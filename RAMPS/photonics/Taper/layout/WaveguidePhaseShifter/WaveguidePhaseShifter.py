import BPG
from bag.layout.util import BBox
from Photonic_Core_Layout.ViaStack_test.ViaStack import ViaStack
from Photonic_Core_Layout.WaveguideBase.DualLayerContactedSlotWaveguide import DualLayerContactedSlotWaveguide


class WaveguidePhaseShifter(BPG.PhotonicTemplateBase):
    """
    This Class can be used for generating waveguide phase shifters with different waveguide geometries
    (e.g. rib, subwavelength, slot and combinations of these geometries) and laterally placed doping layers.

    """

    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)

        # Master declaration
        self.wg_master = None
        self.wg_inst = None
        self.via_stack_master = None
        self.lin_electrode_master1 = None
        self.lin_electrode_master2 = None

        # Hard coded params
        self.wg_loc = (0, 0)

        # Initialize the variables and dictionary of parameters.

        # parameters of waveguide structure
        self.wg_params = self.params['wg_params']

        # parameters of doping layers
        self.doping_info = self.params['doping_info']
        self.doping_length_extend = self.params['doping_length_extend']

        # parameters of electrodes (including Si contact rails and salicide)
        self.lin_electrode_bottom_layer = self.params['lin_electrode_bottom_layer']
        self.lin_electrode_length_extend = self.params['lin_electrode_length_extend']
        self.lin_electrode_bottom_width = self.params['lin_electrode_bottom_width']
        self.lin_electrode_top_layer1 = self.params['lin_electrode_top_layer1']
        self.lin_electrode_top_width1 = self.params['lin_electrode_top_width1']
        self.lin_electrode_top_layer2 = self.params['lin_electrode_top_layer2']
        self.lin_electrode_top_width2 = self.params['lin_electrode_top_width2']
        self.lin_electrode_bot_dist = self.params['lin_electrode_bot_dist']
        self.lin_electrode_top_dist = self.params['lin_electrode_top_dist']

        # Parameters of auxiliary layers (such as exclusion layers)
        self.aux_info = self.params['aux_info']

    @classmethod
    def get_params_info(cls) -> dict:
        return dict(
            # parameters of waveguide structure
            wg_params='parameters of the waveguide structure of the waveguide phase shifter',

            # parameters of doping layers
            doping_info='List of doping dictionaries containing distances dist0, dist1 from the center of the waveguide'
                        'and doping layer',
            doping_length_extend='',

            # parameters of via stack on either side of the waveguide
            lin_electrode_bottom_layer='',
            lin_electrode_length_extend='',
            lin_electrode_bottom_width='',
            lin_electrode_top_layer1='',
            lin_electrode_top_width1='',
            lin_electrode_top_layer2='',
            lin_electrode_top_width2='',
            lin_electrode_bot_dist='',
            lin_electrode_top_dist='',

            # Parameters of auxiliary layers (such as exclusion layers)
            aux_info=''
        )

    def draw_layout(self) -> None:
        self.place_wg_structure()
        self.draw_doping_layers()
        self.draw_electrodes()
        self.draw_aux_layers()

    def place_wg_structure(self) -> None:
        """
        Creates straight waveguide structure
        """
        # Create the template
        self.wg_master = self.new_template(params=self.wg_params,
                                           temp_cls=DualLayerContactedSlotWaveguide)

        # Instantiate the waveguide structure
        self.wg_inst = self.add_instance(self.wg_master,
                                         loc=self.wg_loc,
                                         orient='R0')

        # Extract input/output ports of the waveguide and make it the ports of the phase shifter
        self.extract_photonic_ports(
            inst=self.wg_inst,
            show=False,
        )

    def draw_doping_layers(self):
        """
        Draws doping layers on the waveguide structure using the information given in doping_info
        """
        for count in range(len(self.doping_info)):
            self.add_rect(layer=self.doping_info[count]['layer'],
                          bbox=BBox(left=self.wg_loc[0] -self.lin_electrode_length_extend - self.doping_length_extend,
                                    bottom=self.wg_loc[1] +
                                           min(self.doping_info[count]['dist0'], self.doping_info[count]['dist1']),
                                    right=self.wg_loc[0] + self.wg_params['layer1_wg_params']['length'] +
                                          self.lin_electrode_length_extend + self.doping_length_extend,
                                    top=self.wg_loc[1] + max(self.doping_info[count]['dist0'],
                                                             self.doping_info[count]['dist1']),
                                    resolution=self.grid.resolution)
                          )

    def draw_electrodes(self):
        """
        Draws metal electrodes as well as Si contact rails and salicide layers on either side of the waveguide
        """
        self.lin_electrode_master1 = \
            self.new_template(params={'top_layer': self.lin_electrode_top_layer1,
                                      'bottom_layer': self.lin_electrode_bottom_layer,
                                      'top_y_span': self.wg_params['layer1_wg_params']['length'] +
                                                    2*self.lin_electrode_length_extend,
                                      'top_x_span': self.lin_electrode_top_width1,
                                      'bottom_y_span': self.wg_params['layer1_wg_params']['length'] +
                                                       2*self.lin_electrode_length_extend,
                                      'bottom_x_span': self.lin_electrode_bottom_width,
                                      'align': 'side_align',
                                      'top_bot_offset': self.lin_electrode_top_dist-self.lin_electrode_bot_dist
                                      },
                              temp_cls=ViaStack)
        # place an electrode to the north of the waveguide
        self.add_instance(self.lin_electrode_master1,
                          loc=(self.wg_loc[0] + self.wg_params['layer1_wg_params']['length'] / 2,
                               self.wg_loc[1] + self.lin_electrode_bot_dist),
                          orient='R90')

        self.lin_electrode_master2 = \
            self.new_template(params={'top_layer': self.lin_electrode_top_layer2,
                                      'bottom_layer': self.lin_electrode_bottom_layer,
                                      'top_y_span': self.wg_params['layer1_wg_params']['length'] +
                                                    2*self.lin_electrode_length_extend,
                                      'top_x_span': self.lin_electrode_top_width2,
                                      'bottom_y_span': self.wg_params['layer1_wg_params']['length'] +
                                                       2*self.lin_electrode_length_extend,
                                      'bottom_x_span': self.lin_electrode_bottom_width,
                                      'align': 'side_align',
                                      'top_bot_offset': self.lin_electrode_top_dist-self.lin_electrode_bot_dist
                                      },
                              temp_cls=ViaStack)

        # place an electrode to the south of the waveguide
        self.add_instance(self.lin_electrode_master2,
                          loc=(self.wg_loc[0] + self.wg_params['layer1_wg_params']['length'] / 2,
                               self.wg_loc[1] - self.lin_electrode_bot_dist),
                          orient='R270')

    def draw_aux_layers(self):
        """
        Draws auxiliary layers (such as exclusion layers) which are centered at the waveguide core
        """
        if self.aux_info is not None:
            for count in range(len(self.aux_info)):
                self.add_rect(layer=self.aux_info[count]['layer'],
                              bbox=BBox(left=self.wg_loc[0],
                                        bottom=self.wg_loc[1] - self.aux_info[count]['width'] / 2,
                                        right=self.wg_loc[0] + self.wg_params['layer1_wg_params']['length'],
                                        top=self.wg_loc[1] + self.aux_info[count]['width'] / 2,
                                        resolution=self.grid.resolution)
                              )
