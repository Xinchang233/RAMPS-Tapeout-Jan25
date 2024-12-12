# Modified by Marc to add the possibility to align both in x and y
# It is also modified so that the origin of the structure corresponds to the bottom
# left corner of the top metal

import BPG
from bag.layout.objects import BBox
from math import ceil


class ViaStack(BPG.PhotonicTemplateBase):
    """
    A class to generate a stack of vias.

    Top and bottom layer are passed, as well as x and y spans of the top and bottom contact regions.

    If center-aligned (side_align_x = False, side_align_y = False, default), the generated via stack is symmetric
    and centered.

    If x side-aligned (side_align_x= True), all enclosure layers are justified to share the same left edge (the
    vias are still centered within the enclosure). The left edge is at x=0, and the via stack is vertically centered.

    If y side-aligned (side_align_y= True), all enclosure layers are justified to share the same bottom edge (the
    vias are still centered within the enclosure). The bottom edge is at y=0, and the via stack is vertically centered.

    The origin of the stack is always located at the bottom left corner of the top metal.

    Intermediate layer sizes are calculated by linear interpolation of the top and bottom contact sizes based
    on the height of each layer.

    If via array is too large and will violate max via array DRC rules, the x span of the via array is restricted.
    If via array is restricted, enclosing metal is still placed at full interpolation y span.
    """

    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)

        # Declare parameters
        self.enclosure_list = []
        self.top_layer_rect = None
        self.bottom_layer_rect = None
        self.side_align_x = None
        self.side_align_y = None
        self.use_top_bbox = None

    @classmethod
    def get_default_param_values(cls):
        return dict(
            side_align_x=False,  # Center align all layers
            side_align_y=False,  # Center align all layers
            use_top_bbox=False,  # Linearly interpolate via array enclosure bbox sizes based on layer height
        )

    @classmethod
    def get_params_info(cls):  # Returns definition of the parameters.
        return dict(
            top_layer='Top layer. Either metal layer name (lpp or layer).',
            bottom_layer='Bottom layer. Either metal layer name (lpp or layer).',
            top_x_span='Top layer contact x span',
            top_y_span='Top layer contact y span',
            bottom_x_span='Bottom layer contact x span',
            bottom_y_span='Bottom layer contact y span',
            side_align_x='True to side-align all layers and vias (so all layer shapes share the same -x coordinate).'
                       'If False, all layers are centered.'
                       'Defaults to False.',
            side_align_y='True to side-align all layers and vias (so all layer shapes share the same -y coordinate).'
                         'If False, all layers are centered.'
                         'Defaults to False.',
            use_top_bbox='True to use top x-span and y-span for all intermediate layer via array enclosure sizes '
                         '(ie all layers except for the bottom most layer).'
                         'False to linearly interpolate array enclosure size based on layer height.'
                         'Defaults to False'
        )

    def check_int_float(self,
                        key: str,
                        ) -> None:
        """
        Checks that the passed parameter key is an int or float.

        Parameters
        ----------
        key : str
            The self.params key to check
        """
        if not (isinstance(self.params[key], float) or isinstance(self.params[key], int)):
            raise ValueError(f'{key} parameter to ViaStack must be int or float. '
                             f'Received {self.params[key]}')

    def round_to_grid(self, value):
        """ Rounds a point to the nearest grid """
        return self.grid.resolution * round(value / self.grid.resolution)

    def round_up_to_even_grid(self, value):
        """ Rounds a distance up to the next even grid layout resolution distance """
        return 2 * self.grid.resolution * ceil((value / self.grid.resolution) / 2)

    def draw_layout(self):
        # Parse the top_layer and bottom layer params
        if isinstance(self.params['top_layer'], tuple):
            # If user passes a LPP
            top_layer_ind = self.grid.tech_info.get_layer_id(self.params['top_layer'][0])
            top_layer_name = self.params['top_layer'][0]
        elif isinstance(self.params['top_layer'], str):
            # If user passes a layer
            top_layer_ind = self.grid.tech_info.get_layer_id(self.params['top_layer'])
            top_layer_name = self.params['top_layer']
        else:
            raise ValueError(f'top_layer parameter to ViaStack must be '
                             f'an LPP, or a layer name.'
                             f'Received value was {self.params["top_layer"]}')

        if isinstance(self.params['bottom_layer'], tuple):
            # If user passes a LPP
            bottom_layer_ind = self.grid.tech_info.get_layer_id(self.params['bottom_layer'][0])
            bottom_layer_name = self.params['bottom_layer'][0]
        elif isinstance(self.params['bottom_layer'], str):
            # If user passes a layer
            bottom_layer_ind = self.grid.tech_info.get_layer_id(self.params['bottom_layer'])
            bottom_layer_name = self.params['bottom_layer']
        else:
            raise ValueError(f'bottom_layer parameter to ViaStack must be '
                             f'an LPP, or a layer name.'
                             f'Received value was {self.params["bottom_layer"]}')

        if bottom_layer_ind >= top_layer_ind:
            raise ValueError(f'bottom_layer must be below top_layer.\n'
                             f'Specified bottom_layer, top_layer were:  {bottom_layer_name}, {top_layer_name}')

        # Parse the lengths and widths
        for key in ['top_x_span', 'top_y_span', 'bottom_x_span', 'bottom_y_span']:
            self.check_int_float(key)
        top_x_span = self.params['top_x_span']
        top_y_span = self.params['top_y_span']
        bottom_x_span = self.params['bottom_x_span']
        bottom_y_span = self.params['bottom_y_span']

        self.side_align_x = self.params['side_align_x']
        self.side_align_y = self.params['side_align_y']
        self.use_top_bbox = self.params['use_top_bbox']

        # Get the height of the top and bottom layers, so interpolation can be performed
        h_top = self.photonic_tech_info.height(top_layer_name)
        h_bot = self.photonic_tech_info.height(bottom_layer_name)

        metal_pairs = self._find_metal_pairs(bot_layer=bottom_layer_name,
                                             top_layer=top_layer_name,
                                             metal_info=self.photonic_tech_info.dataprep_parameters['MetalStack']
                                             )
        # As we iterate over the metal pairs, we only draw the enclosure on the bottom metal.
        # Need to add the top metal with some dummy (None) metal above it in order to draw top metal enclosure
        # and last via.
        metal_pairs.append(
            (metal_pairs[-1][-1], None)
        )
        for bot_metal_name, _ in metal_pairs:
            h = self.photonic_tech_info.height(bot_metal_name)

            # Do not use the top bbox size on the bottom most layer.
            if bot_metal_name == bottom_layer_name or (not self.use_top_bbox):
                # Linearly interpolate based on current layer height
                x_span = top_x_span * (h - h_bot) / (h_top - h_bot) + bottom_x_span * (h_top - h) / (h_top - h_bot)
                y_span = top_y_span * (h - h_bot) / (h_top - h_bot) + bottom_y_span * (h_top - h) / (h_top - h_bot)

                # Round x_span and y_span to res grid and an even size, so that via array can be centered
                x_span = self.round_up_to_even_grid(x_span)
                y_span = self.round_to_grid(y_span)
            else:
                x_span = top_x_span
                y_span = top_y_span

            # Constrain x_span and y_span to be DRC clean (bigger than min width)
            min_w = self.photonic_tech_info.min_width(bot_metal_name)
            x_span = max(min_w, x_span)
            y_span = max(min_w, y_span)

            # Constrain metal enclosure to satsify maximum metal width rules
            max_w = self.photonic_tech_info.max_width(bot_metal_name)
            if x_span > max_w and y_span > max_w:
                x_span = min(max_w, x_span)

            # Draw the enclosure metal layer
            if self.side_align_x and self.side_align_y:
                # Side align so left edge is 0 and bottom edge is also 0
                layer_rect = self.add_rect(
                    layer=(bot_metal_name, 'drawing'),
                    bbox=BBox(
                        bottom=0 + y_off,
                        top=y_span + y_off,
                        left=0 + x_off,
                        right=x_span + x_off,
                        resolution=self.grid.resolution,
                        unit_mode=False,
                    ),
                    unit_mode=False
                )
            elif self.side_align_x and not self.side_align_y:
                # Side align so left edge is 0 and center align in y
                layer_rect = self.add_rect(
                    layer=(bot_metal_name, 'drawing'),
                    bbox=BBox(
                        bottom=top_y_span / 2 - y_span / 2 + y_off,
                        top=top_y_span / 2 + y_span / 2 + y_off,
                        left=0 + x_off,
                        right=x_span + x_off,
                        resolution=self.grid.resolution,
                        unit_mode=False,
                    ),
                    unit_mode=False
                )
            elif not self.side_align_x and self.side_align_y:
                # Center align in x and side align in y so bottom is at 0
                layer_rect = self.add_rect(
                    layer=(bot_metal_name, 'drawing'),
                    bbox=BBox(
                        bottom=0 + y_off,
                        top=y_span + y_off,
                        left=top_x_span / 2 - x_span / 2 + x_off,
                        right=top_x_span / 2 + x_span / 2 + x_off,
                        resolution=self.grid.resolution,
                        unit_mode=False,
                    ),
                    unit_mode=False
                )
            else:
                # Center align
                layer_rect = self.add_rect(
                    layer=(bot_metal_name, 'drawing'),
                    bbox=BBox(
                        bottom=top_y_span / 2 - y_span / 2 + y_off,
                        top=top_y_span / 2 + y_span / 2 + y_off,
                        left=top_x_span / 2 - x_span / 2 + x_off,
                        right=top_x_span / 2 + x_span / 2 + x_off,
                        resolution=self.grid.resolution,
                        unit_mode=False,
                    ),
                    unit_mode=False
                )

            # Append to a enclosure list, so via loop can access the values
            self.enclosure_list.append(dict(x_span=x_span, y_span=y_span, rect=layer_rect))

            # Save the bottom and top rectangles so they can be accessed by higher level cells easily
            if bot_metal_name == bottom_layer_name:
                self.bottom_layer_rect = layer_rect
            if bot_metal_name == top_layer_name:
                self.top_layer_rect = layer_rect

        # Loop over the enclosure rectangles, and add vias within each lower layer
        for ind in range(len(self.enclosure_list) - 1):
            layer_name = self.enclosure_list[ind]['rect'].layer
            x_span = self.enclosure_list[ind]['x_span']
            y_span = self.enclosure_list[ind]['y_span']

            # Constrain x_span and y_span to be DRC clean (bigger than min width)
            min_w = self.photonic_tech_info.min_width(layer_name)

            x_span = max(min_w, x_span)
            y_span = max(min_w, y_span)

            # Constrain metal enclosure for max via array width (y_span is never constrained for a via array)
            max_w = self.photonic_tech_info.via_max_width(layer_name)
            if x_span > max_w and y_span > max_w:
                x_span = min(max_w, x_span)

            # Constrain the via area such that an enclosure on the next layer up will not exceed max width
            max_w_next_layer = self.photonic_tech_info.max_width(self.enclosure_list[ind+1]['rect'].layer)
            if x_span > max_w_next_layer and y_span > max_w_next_layer:
                x_span = min(x_span, max_w_next_layer)

            if self.side_align_x and self.side_align_y:
                # x and y aligned
                if self.enclosure_list[ind]['x_span'] > self.enclosure_list[ind + 1]['x_span']:
                    x_span_enclosure = self.enclosure_list[ind + 1]['x_span']
                else:
                    x_span_enclosure = self.enclosure_list[ind]['x_span']

                if self.enclosure_list[ind]['y_span'] > self.enclosure_list[ind + 1]['y_span']:
                    y_span_enclosure = self.enclosure_list[ind + 1]['y_span']
                else:
                    y_span_enclosure = self.enclosure_list[ind]['y_span']

                offset_x = self.round_to_grid((x_span_enclosure - x_span) / 2)
                offset_y = self.round_to_grid((y_span_enclosure - y_span) / 2)
                bbox = BBox(
                    bottom=offset_y + y_off,
                    top=y_span_enclosure - offset_y + y_off,
                    left=offset_x + x_off,
                    right=x_span_enclosure - offset_x + x_off,
                    resolution=self.grid.resolution,
                    unit_mode=False,
                )
            elif self.side_align_x and not self.side_align_y:
                # Side align centered in the left-justified enclosure
                if self.enclosure_list[ind]['x_span'] > self.enclosure_list[ind + 1]['x_span']:
                    x_span_enclosure = self.enclosure_list[ind + 1]['x_span']
                else:
                    x_span_enclosure = self.enclosure_list[ind]['x_span']

                offset_x = self.round_to_grid((x_span_enclosure - x_span) / 2)
                bbox = BBox(
                    bottom=top_y_span / 2 - y_span / 2 + y_off,
                    top=top_y_span / 2 + y_span / 2 + y_off,
                    left=offset_x + x_off,
                    right=x_span_enclosure - offset_x + x_off,
                    resolution=self.grid.resolution,
                    unit_mode=False,
                )
            elif not self.side_align_x and self.side_align_y:
                # Bottom aligned.
                if self.enclosure_list[ind]['y_span'] > self.enclosure_list[ind + 1]['y_span']:
                    y_span_enclosure = self.enclosure_list[ind + 1]['y_span']
                else:
                    y_span_enclosure = self.enclosure_list[ind]['y_span']

                offset_y = self.round_to_grid((y_span_enclosure - y_span) / 2)
                bbox = BBox(
                    bottom=offset_y+y_off,
                    top=y_span_enclosure - offset_y + y_off,
                    left=top_x_span / 2 - x_span / 2 + x_off,
                    right=top_x_span / 2 + x_span / 2 + x_off,
                    resolution=self.grid.resolution,
                    unit_mode=False,
                )
            else:
                # Center align
                bbox = BBox(
                    bottom=top_y_span / 2 - y_span / 2 + y_off,
                    top=top_y_span / 2 + y_span / 2 + y_off,
                    left=top_x_span / 2 - x_span / 2 + x_off,
                    right=top_x_span / 2 + x_span / 2 + x_off,
                    resolution=self.grid.resolution,
                    unit_mode=False,
                )
            self.add_via(
                bbox=bbox,
                bot_layer=self.enclosure_list[ind]['rect'].layer,
                top_layer=self.enclosure_list[ind + 1]['rect'].layer,
                bot_dir='y',
                extend=False
            )


if __name__ == '__main__':
    spec_file = 'Photonic_Core_Layout/ViaStack/specs/via_stack_specs.yaml'
    plm = BPG.PhotonicLayoutManager(spec_file)
    plm.generate_template()
    plm.generate_content()
    plm.generate_gds()
    plm.generate_flat_content()
    plm.generate_flat_gds()
    plm.dataprep()
    plm.generate_dataprep_gds()
