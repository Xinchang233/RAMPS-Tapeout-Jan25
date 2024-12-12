import BPG
from bag.layout.objects import BBox
from math import ceil


class ViaStack(BPG.PhotonicTemplateBase):
    """
    A class to generate a stack of vias.

    Top and bottom layer are passed, as well as x and y spans of the top and bottom contact regions.

    If center-aligned (side_align = False, default), the origin is in the center of the via array, and the generated
    via stack is symmetric and centered.

    If side-aligned (side_align = True), all enclosure layers are left-justified to share the same left edge (the
    vias are still centered within the enclosure). The left edge is at x=0, and the via stack is vertically centered
    about the x-axis (origin is on center of left edge).

    Intermediate layer sizes are calculated by linear interpolation of the top and bottom contact sizes based
    on the height of each layer.

    If via array is too large and will violate max via array DRC rules, the x span of the via array is restricted.
    If via array is restricted, enclosing metal is still placed at full interpolation y span.
    """

    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)

        # Declare parameters
        self.enclosure_list = []
        self.stair_offset_list =[]
        self.top_layer_rect = None
        self.bottom_layer_rect = None
        self.align = None
        self.top_bot_offset = None
        self.pad_open_layer = None
        self.pad_open_inclusion = None

    @classmethod
    def get_default_param_values(cls):
        return dict(
            align='center_align',  # Center align all layers
            top_bot_offset=0,
            pad_open_layer=None,
            pad_open_inclusion=None
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
            align='If side_align all layers and vias share the same -x coordinate.'
                  'If corner_align all layers and vias share the same -x and +y coordinates.'
                  'Otherwise center_align, default: center align',
            top_bot_offset='Offset between top and bottom layers on x axis',
            pad_open_layer='Passivation opening if the top metal layer of via stack is used as bond or G/S pad',
            pad_open_inclusion='Inclusion width of the passivation opening within the top metal layer',

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

        # Parse the lengths and widths
        for key in ['top_x_span', 'top_y_span', 'bottom_x_span', 'bottom_y_span']:
            self.check_int_float(key)
        top_x_span = self.params['top_x_span']
        top_y_span = self.params['top_y_span']
        bottom_x_span = self.params['bottom_x_span']
        bottom_y_span = self.params['bottom_y_span']

        self.align = self.params['align']
        self.top_bot_offset = self.params['top_bot_offset']

        # Get the height of the top and bottom layers, so interpolation can be performed
        h_top = self.photonic_tech_info.height(top_layer_name)
        h_bot = self.photonic_tech_info.height(bottom_layer_name)

        for layer_ind in range(bottom_layer_ind, top_layer_ind + 1):
            layer_name = self.grid.tech_info.get_layer_name(layer_ind)

            # As both SI and POLY have the same layer number, layer_name will be a list
            # In this case, because SI/POLY must be the lowest layer of the stack, use bottom_layer_name instead
            if isinstance(layer_name, list):
                layer_name = bottom_layer_name

            h = self.photonic_tech_info.height(layer_name)

            # Linearly interpolate based on current layer height
            x_span = top_x_span * (h - h_bot) / (h_top - h_bot) + bottom_x_span * (h_top - h) / (h_top - h_bot)
            y_span = top_y_span * (h - h_bot) / (h_top - h_bot) + bottom_y_span * (h_top - h) / (h_top - h_bot)

            # Round x_span and y_span to res grid and an even size, so that via array can be centered
            x_span = self.round_up_to_even_grid(x_span)
            y_span = self.round_to_grid(y_span)

            # Constrain x_span and y_span to be DRC clean (bigger than min width)
            min_w = self.photonic_tech_info.min_width(layer_name)

            x_span = max(min_w, x_span)
            y_span = max(min_w, y_span)

            # Constrain metal enclosure to satsify maximum metal width rules
            max_w = self.photonic_tech_info.max_width(layer_name)
            if x_span > max_w and y_span > max_w:
                x_span = min(max_w, x_span)

            stair_offset = self.top_bot_offset * (h - h_bot) / (h_top - h_bot)
            self.stair_offset_list.append(stair_offset)

            # Draw the enclosure metal layer
            if self.align == 'side_align':
                # Side align so left edge is 0
                layer_rect = self.add_rect(
                    layer=(layer_name, 'drawing'),
                    bbox=BBox(
                        bottom=-y_span / 2,
                        top=y_span / 2,
                        left=stair_offset,
                        right=stair_offset + x_span,
                        resolution=self.grid.resolution,
                        unit_mode=False,
                    ),
                    unit_mode=False
                )
            elif self.align == 'corner_align':
                # Align to the left top corner
                layer_rect = self.add_rect(
                    layer=(layer_name, 'drawing'),
                    bbox=BBox(
                        bottom=-y_span,
                        top=0.0,
                        left=stair_offset,
                        right=stair_offset + x_span,
                        resolution=self.grid.resolution,
                        unit_mode=False,
                    ),
                    unit_mode=False
                )
            else:
                # Center align
                layer_rect = self.add_rect(
                    layer=(layer_name, 'drawing'),
                    bbox=BBox(
                        bottom=-y_span / 2,
                        top=y_span / 2,
                        left=-x_span / 2,
                        right=x_span / 2,
                        resolution=self.grid.resolution,
                        unit_mode=False,
                    ),
                    unit_mode=False
                )

            # Append to a enclosure list, so via loop can access the values
            self.enclosure_list.append(dict(x_span=x_span, y_span=y_span, rect=layer_rect))

            # Save the bottom and top rectangles so they can be accessed by higher level cells easily
            if layer_ind == bottom_layer_ind:
                self.bottom_layer_rect = layer_rect
            if layer_ind == top_layer_ind:
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

            if self.align == 'side_align':
                # Side align centered in the left-justified enclosure
                x_span_enclosure = self.enclosure_list[ind]['x_span']
                offset = self.round_to_grid((x_span_enclosure - x_span) / 2)
                bbox = BBox(
                    bottom=-y_span / 2,
                    top=y_span / 2,
                    left=offset + self.stair_offset_list[ind+1],
                    right=x_span_enclosure - offset,
                    resolution=self.grid.resolution,
                    unit_mode=False,
                )
            elif self.align == 'corner_align':
                # corner align centered in the left-justified enclosure
                x_span_enclosure = self.enclosure_list[ind]['x_span']
                offset = self.round_to_grid((x_span_enclosure - x_span) / 2)
                bbox = BBox(
                    bottom=-y_span,
                    top=0.0,
                    left=offset + self.stair_offset_list[ind+1],
                    right=x_span_enclosure - offset,
                    resolution=self.grid.resolution,
                    unit_mode=False,
                )
            else:
                # Center align
                bbox = BBox(
                    bottom=-y_span / 2,
                    top=y_span / 2,
                    left=-x_span / 2,
                    right=x_span / 2,
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

        # Draw passivation opening layer

        if self.params['pad_open_layer'] is not None:

            if self.align == 'side_align':
                # Side align or corner align
                pad_open = self.add_rect(
                    layer=self.params['pad_open_layer'],
                    bbox=BBox(
                        bottom=-top_y_span / 2 + self.params['pad_open_inclusion'],
                        top=top_y_span / 2 - self.params['pad_open_inclusion'],
                        left=self.top_bot_offset + self.params['pad_open_inclusion'] + 10.5,
                        right=self.top_bot_offset + top_x_span - self.params['pad_open_inclusion'],
                        resolution=self.grid.resolution,
                    ),
                )
                self.add_obj(pad_open)
            elif self.align == 'corner_align':
                # Side align or corner align
                pad_open = self.add_rect(
                    layer=self.params['pad_open_layer'],
                    bbox=BBox(
                        bottom=-top_y_span + self.params['pad_open_inclusion'],
                        top=-self.params['pad_open_inclusion'],
                        left=self.top_bot_offset + self.params['pad_open_inclusion'] + 10.5,
                        right=self.top_bot_offset + top_x_span - self.params['pad_open_inclusion'],
                        resolution=self.grid.resolution,
                    ),
                )
                self.add_obj(pad_open)
            else:
                # Side align or corner align
                pad_open = self.add_rect(
                    layer=self.pad_open_layer,
                    bbox=BBox(
                        bottom=-top_y_span / 2 + self.params['pad_open_inclusion'],
                        top=top_y_span / 2 - self.params['pad_open_inclusion'],
                        left=-top_x_span / 2 + self.params['pad_open_inclusion'],
                        right=top_x_span / 2 - self.params['pad_open_inclusion'],
                        resolution=self.grid.resolution,
                    ),
                )
                self.add_obj(pad_open)

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
