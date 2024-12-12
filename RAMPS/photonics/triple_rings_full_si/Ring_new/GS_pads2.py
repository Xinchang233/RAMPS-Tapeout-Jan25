import BPG
from layout.Ring_new.ViaStack1 import ViaStack1
from bag.layout.util import BBox


class GSPads2(BPG.PhotonicTemplateBase):
    """
    A class to generate a pair of pads (for example for a GS pair. It is based on
    instantiating the ViaStack class of Photonic Core Layout, which generates a single pad from
    the specified parameters.

    We can either specify the parameters of each pad (through right_pad_params, left_pad_params) or
    only one set of parameters for both pads (through pad_params). If all are specified, we will use the
    specific parameters in right_pad_params and left_pad_params.

    The slot between the two pads is given by the x_slot parameter. If for any reason a y offset between the
    two pads is needed, it can be given in the parameter y_offset.

    The center of the cell is at the midpoint between the pads in both x and y

    The left pad is mirrored!
    """

    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)

        # Call the parent class constructor
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)
        self.params = params
        self.electrode_bottom_y_span=None,
        self.right_pad_master = None
        self.left_pad_master = None
        self.left_pad = None
        self.right_pad = None

    @classmethod
    def get_default_param_values(cls):
        return dict(
            electrode_width_inner=None,
            electrode_width_outer=None,
            radius_b1=None,
            radius_b2=None,
            placer=None,
            contact_dist=None,
            electrode_bottom_x_span=None,
            electrode_bottom_y_span=None,
            x_slot=10.0,
            y_offset=0,
            right_pad_params=None,
            left_pad_params=None,
            right_pad_label=None,
            left_pad_label=None,
        )

    @classmethod
    def get_params_info(cls):  # Returns definition of the parameters.
        return dict(
            electrode_width_inner='fh',
            electrode_width_outer='fh',
            radius_b1='fhjg',
            radius_b2='fhg',
            placer='sd',
            contact_dist='dfg',
            electrode_bottom_x_span='GHJG',
            electrode_bottom_y_span='JGHJ',
            x_slot='Slot in the x direction between the two pads',
            y_offset='y offset between the two opads',
            right_pad_params='Parameters for the ViaStack template corresponding to the right pad',
            left_pad_params='Parameters for the ViaStack template corresponding to the left pad',
            right_pad_label='Optional dict containing label params for the right pad',
            left_pad_label='Optional dict containing label params for the left pad',
        )

    def draw_layout(self) -> None:
        self.draw_pads()
        self.add_labels()
        self.draw_lv()
        self.metal_routing()

    def metal_routing(self) -> None:

        # self.add_rect(layer=('B2', 'drawing'),
        #               bbox=BBox(left=-36,
        #                         bottom=-self.params['electrode_bottom_y_span'] / 2 - self.params['placer'] / 2,
        #                         right=-self.params['radius_b2'] + self.params['electrode_width_inner'],
        #                         top=self.params['electrode_bottom_y_span'] / 2 - self.params['placer'] / 2,
        #                         resolution=self.grid.resolution)
        #               )
        # self.add_rect(layer=('B2', 'drawing'),
        #               bbox=BBox(left=-36,
        #                         bottom=-self.params['electrode_bottom_y_span'] / 2 + self.params['placer'] -
        #                                self.params['placer'] / 2,
        #                         right=-self.params['radius_b2'] + self.params['electrode_width_inner'],
        #                         top=self.params['electrode_bottom_y_span'] / 2 + self.params['placer'] - self.params[
        #                                                                                                      'placer'] / 2,
        #                         resolution=self.grid.resolution)
        #               )
        # self.add_rect(layer=('B2', 'drawing'),
        #               bbox=BBox(left=-36,
        #                         bottom=-self.params['left_pad_params']['y_off'] - 20,
        #                         right=-36 + self.params['electrode_bottom_y_span'],
        #                         top=self.params['electrode_bottom_y_span'] / 2 - self.params['placer'] / 2,
        #                         resolution=self.grid.resolution)
        #               )
        #
        #
        #
        # self.add_rect(layer=('B2', 'drawing'),
        #               bbox=BBox(left=-(self.params['left_pad_params']['x_off'])/2,
        #                         bottom=-self.params['electrode_bottom_y_span']/2-self.params['placer']/2,
        #                         right=-self.params['radius_b2']+self.params['electrode_width_inner'],
        #                         top=self.params['electrode_bottom_y_span']/2-self.params['placer']/2,
        #                         resolution=self.grid.resolution)
        #               )
        # self.add_rect(layer=('B2', 'drawing'),
        #               bbox=BBox(left=-(self.params['left_pad_params']['x_off']) / 2,
        #                         bottom=-self.params['electrode_bottom_y_span'] / 2+self.params['placer']-self.params['placer']/2,
        #                         right=-self.params['radius_b2'] + self.params['electrode_width_inner'],
        #                         top=self.params['electrode_bottom_y_span'] / 2+self.params['placer']-self.params['placer']/2,
        #                         resolution=self.grid.resolution)
        #               )
        # self.add_rect(layer=('B2', 'drawing'),
        #               bbox=BBox(left=-(self.params['left_pad_params']['x_off']) / 2,
        #                         bottom=self.params['left_pad_params']['y_off']-self.params['placer']/2,
        #                         right=-(self.params['left_pad_params']['x_off']) / 2+self.params['electrode_bottom_y_span'],
        #                         top=self.params['electrode_bottom_y_span'] / 2-self.params['placer']/2,
        #                         resolution=self.grid.resolution)
        #               )
        # self.add_rect(layer=('B2', 'drawing'),
        #               bbox=BBox(left=-(self.params['left_pad_params']['x_off']+self.params['left_pad_params']['bottom_x_span']),
        #                         bottom=self.params['left_pad_params']['y_off']-self.params['placer']/2,
        #                         right=-(self.params['left_pad_params']['x_off']) / 2+self.params['electrode_bottom_y_span'],
        #                         top=self.params['left_pad_params']['y_off']+self.params['electrode_bottom_y_span']-self.params['placer']/2,
        #                         resolution=self.grid.resolution)
        #               )
        self.add_rect(layer=('B1', 'drawing'),
                      bbox=BBox(left=-62-self.params['electrode_bottom_y_span'],
                                bottom=-self.params['electrode_bottom_y_span']/2-self.params['placer']/2,
                                right=-self.params['radius_b1']+self.params['electrode_width_outer'],
                                top=self.params['electrode_bottom_y_span']/2-self.params['placer']/2,
                                resolution=self.grid.resolution)
                      )
        self.add_rect(layer=('B1', 'drawing'),
                      bbox=BBox(left=-62-self.params['electrode_bottom_y_span'],
                                bottom=-self.params['left_pad_params']['y_off'],
                                right=-62,
                                top=self.params['electrode_bottom_y_span']/2-self.params['placer']/2,
                                resolution=self.grid.resolution)
                      )
        # self.add_rect(layer=('B1', 'drawing'),
        #               bbox=BBox(left=-(self.params['left_pad_params']['x_off']) - 103,
        #                         bottom=self.params['left_pad_params']['y_off']-self.params['placer']/2,
        #                         right=-(self.params['left_pad_params']['x_off']) - 80+self.params['electrode_bottom_y_span'],
        #                         top=self.params['left_pad_params']['y_off']+self.params['electrode_bottom_y_span']-self.params['placer']/2,
        #                         resolution=self.grid.resolution)
        #               )
        self.add_rect(layer=('B1', 'drawing'),
                      bbox=BBox(left=(self.params['radius_b1'] - self.params['electrode_width_outer']),
                                bottom=-self.params['electrode_bottom_y_span']/2+self.params['placer']-self.params['placer']/2,
                                right=66.8,
                                top=self.params['electrode_bottom_y_span']/2+self.params['placer']-self.params['placer']/2,
                                resolution=self.grid.resolution)
                      )
        self.add_rect(layer=('B1', 'drawing'),
                      bbox=BBox(left=66.8-self.params['electrode_bottom_y_span'],
                                bottom=-self.params['left_pad_params']['y_off'],
                                right=66.8,
                                top=self.params['electrode_bottom_y_span']/2+self.params['placer']/2,
                                resolution=self.grid.resolution)
                      )
        # self.add_rect(layer=('B1', 'drawing'),
        #               bbox=BBox(
        #                   left=(self.params['left_pad_params']['x_off']) / 2 - self.params['electrode_bottom_y_span'],
        #                   bottom=self.params['left_pad_params']['y_off']-self.params['placer']/2,
        #                   right=(self.params['left_pad_params']['x_off']+self.params['left_pad_params']['bottom_x_span']),
        #                   top=self.params['left_pad_params']['y_off']+self.params['electrode_bottom_y_span']-self.params['placer']/2,
        #                   resolution=self.grid.resolution)
        #               )


    def draw_lv(self) -> None:

        self.add_rect(layer=('LV', 'drawing'),
                      bbox=BBox(left=100-26+2,
                                bottom=-self.params['left_pad_params']['y_off'] - self.params['left_pad_params'][
                                    'top_y_span'] + 5,
                                right=100+24+2,
                                top=-self.params['left_pad_params']['y_off'] - 5,
                                resolution=self.grid.resolution)
                      )

        self.add_rect(layer=('LV', 'drawing'),
                      bbox=BBox(left=-100 - 24,
                                bottom=-self.params['left_pad_params']['y_off'] - self.params['left_pad_params'][
                                    'top_y_span'] + 5,
                                right=-100 + 26,
                                top=-self.params['left_pad_params']['y_off'] - 5,
                                resolution=self.grid.resolution)
                      )
        # self.add_rect(layer=('LV', 'drawing'),
        #               bbox=BBox(left=200 - 26+2,
        #                         bottom=-self.params['left_pad_params']['y_off'] - self.params['left_pad_params'][
        #                             'top_y_span'] + 5,
        #                         right=200 + 24+2,
        #                         top=-self.params['left_pad_params']['y_off'] - 5,
        #                         resolution=self.grid.resolution)
        #               )
        #
        # self.add_rect(layer=('LV', 'drawing'),
        #               bbox=BBox(left=-200 - 24,
        #                         bottom=-self.params['left_pad_params']['y_off'] - self.params['left_pad_params'][
        #                             'top_y_span'] + 5,
        #                         right=-200 + 26,
        #                         top=-self.params['left_pad_params']['y_off'] - 5,
        #                         resolution=self.grid.resolution)
        #               )
        #addpads_here
        # self.add_rect(layer=('LV', 'drawing'),
        #               bbox=BBox(left=300 - 26+2,
        #                         bottom=-self.params['left_pad_params']['y_off'] - self.params['left_pad_params'][
        #                             'top_y_span'] + 5,
        #                         right=300 + 24+2,
        #                         top=-self.params['left_pad_params']['y_off'] - 5,
        #                         resolution=self.grid.resolution)
        #               )
        #
        # self.add_rect(layer=('LV', 'drawing'),
        #               bbox=BBox(left=-300 - 24,
        #                         bottom=-self.params['left_pad_params']['y_off'] - self.params['left_pad_params'][
        #                             'top_y_span'] + 5,
        #                         right=-300 + 26,
        #                         top=-self.params['left_pad_params']['y_off'] - 5,
        #                         resolution=self.grid.resolution)
        #               )



    def draw_pads(self) -> None:
        """ Draws the two pads by the instantiation of the ViaStack with the
        correct parameters. It spaces both pads according to the spec file.
        """

        # First see if we were specified joint parameters or different paremeters per pad
        if 'left_pad_params' in self.params and 'right_pad_params' in self.params:
            self.right_pad_master = self.new_template(params=self.params['right_pad_params'],
                                                      temp_cls=ViaStack1)
            self.left_pad_master = self.new_template(params=self.params['right_pad_params'],
                                                     temp_cls=ViaStack1)

        elif 'pad_params' in self.params:
            self.right_pad_master = self.new_template(params=self.params['pad_params'],
                                                      temp_cls=ViaStack1)
            self.left_pad_master = self.new_template(params=self.params['pad_params'],
                                                     temp_cls=ViaStack1)
        else:
            raise ValueError(f'Pad parameters not specified correctly. Check there is either '
                             f'a <pad_params> key or both <left_pad_params> and <right_pad_params> ')

        # Draw right pad
        self.right_pad = self.add_instance(self.right_pad_master,
                                           loc=(2, 0),
                                           orient='MX')  # No rotation
        # Draw left pad
        self.left_pad = self.add_instance(self.left_pad_master,
                                          loc=(0, 0),
                                          orient='MY',
                                          reflect=True,
                                          )  # Mirror the pad so everything is symmetric
        # self.right_pad = self.add_instance(self.right_pad_master,
        #                                    loc=(100+2, 0),
        #                                    orient='MX')  # No rotation
        # Draw left pad
        # self.left_pad = self.add_instance(self.left_pad_master,
        #                                   loc=(-100, 0),
        #                                   orient='MY',
        #                                   reflect=True,
        #                                   )  # Mirror the pad so everything is symmetric
        # self.right_pad = self.add_instance(self.right_pad_master,
        #                                    loc=(200+2, 0),
        #                                    orient='MX')  # No rotation
        # Draw left pad
        # self.left_pad = self.add_instance(self.left_pad_master,
        #                                   loc=(-50, 0),
        #                                   orient='MY',
        #                                   reflect=True,
        #                                   )  # Mirror the pad so everything is symmetric

    def add_labels(self) -> None:
        """
        Adds a label for the left and right pads in the specified layers (if specified)
        """

        if 'left_pad_label' in self.params:
            l_label_bbox = BBox(left=-self.params['x_slot'] / 2 - self.grid.resolution,
                                bottom=-self.params['y_offset'] / 2-self.params['placer']/2,
                                right=-self.params['x_slot'] / 2,
                                top=-self.params['y_offset'] / 2 + self.grid.resolution-self.params['placer']/2,
                                resolution=self.grid.resolution,
                                unit_mode=False
                                )
            self.add_label(label=self.params['left_pad_label']['label'],
                           layer=self.params['left_pad_label']['lpp'],
                           bbox=l_label_bbox
                           )

        if 'right_pad_label' in self.params:
            r_label_bbox = BBox(left=self.params['x_slot'] / 2,
                                bottom=self.params['y_offset'] / 2-self.params['placer']/2,
                                right=self.params['x_slot'] / 2 + self.grid.resolution,
                                top=self.params['y_offset'] / 2 + self.grid.resolution-self.params['placer']/2,
                                resolution=self.grid.resolution,
                                unit_mode=False
                                )

            self.add_label(label=self.params['right_pad_label']['label'],
                           layer=self.params['right_pad_label']['lpp'],
                           bbox=r_label_bbox)


if __name__ == '__main__':
    spec_file = 'ice1_scripts/Pads/specs/GS_pads_specs.yaml'
    plm = BPG.PhotonicLayoutManager(spec_file)
    plm.generate_content()
    plm.generate_gds()
    # plm.generate_flat_content()
    # plm.generate_flat_gds()
    plm.dataprep_calibre()











