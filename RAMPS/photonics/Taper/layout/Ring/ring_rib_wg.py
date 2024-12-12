import BPG
import numpy as np
from bag.layout.util import BBox
from Photonic_Core_Layout.ViaStack.ViaStack import ViaStack
from Photonic_Core_Layout.AdiabaticPaths.AdiabaticPaths import AdiabaticPaths


class RingRibWg(BPG.PhotonicTemplateBase):
    """
    This class generates rib-waveguide ring modulator
    """

    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)

        # Initialize variables and dictionary of parameters
        self.ring_loc = (0, 0)
        self.g_pad_loc = None
        self.s_pad_loc = None

        # Parameters of rib-waveguide ring
        # --------------------------------
        self.r_core_cent = self.params['r_core_cent']

        self.core_layer = self.params['core_layer']
        self.core_width = self.params['core_width']
        self.core_slot_width = self.params['core_slot_width']

        self.slab_layer = self.params['slab_layer']
        self.slab_width = self.params['slab_width']
        self.slab_slot_width = self.params['slab_slot_width']

        # Parameters of coupler waveguide
        # -------------------------------
        self.bent_coupler = self.params['bent_coupler']
        self.coup_core_width = self.params['coup_core_width']
        self.coup_slab_width = self.params['coup_slab_width']
        self.coup_length = self.params['coup_length']
        self.coup_gap = self.params['coup_gap']
        self.coup_radius = self.params['coup_radius']
        self.coup_angle = self.params['coup_angle']
        self.curve_rate = self.params['curve_rate']
        self.coup_angle_in = self.params['coup_angle_in']

        # Parameters of doping and salicide layers
        # ----------------------------------------
        self.doping_info = self.params['doping_info']

        # Parameters of inner and outer ring electrodes (including SI contact rails)
        # --------------------------------------------------------------------------
        self.inner_electrode_info = self.params['inner_electrode_info']
        self.outer_electrode_info = self.params['outer_electrode_info']

        # Parameters of vias
        # ------------------
        self.via_info = self.params['via_info']

        # Parameters of gs pads
        # ---------------------
        self.gs_electrodes = self.params['gs_electrodes']
        self.gs_dist = self.params['gs_dist']
        self.gs_bottom_width = self.params['gs_bottom_width']
        self.gs_bottom_length = self.params['gs_bottom_length']
        self.gs_pad_layer = self.params['gs_pad_layer']
        self.gs_pad_width = self.params['gs_pad_width']
        self.gs_pad_length = self.params['gs_pad_length']
        self.gs_pad_pitch = self.params['gs_pad_pitch']

    @classmethod
    def get_params_info(cls) -> dict:
        return dict(
            # Parameters of rib-waveguide ring
            # --------------------------------
            r_core_cent='Radius to the center of ring core',

            core_layer='Layer or LPP of ring core',
            core_width='Width of ring core',
            core_slot_width='Width of slot in ring core',

            slab_layer='Layer or LPP of ring slab',
            slab_width='Width of ring slab',
            slab_slot_width='Width of slot in ring slab',

            # Parameters of coupler waveguide
            # -------------------------------
            bent_coupler='Boolean variable which determines the type of input waveguide (bent or straight)',
            coup_core_width='Width of the core of input coupler waveguide',
            coup_slab_width='Width of the slab of input coupler waveguide',
            coup_length='Length of straight waveguide coupler',
            coup_gap='Coupling gap between the cores of coupler and ring waveguides',
            coup_radius='Radius of the bent coupler core in the coupling region',
            coup_angle='Angular span of constant-radius portion of bent coupler waveguide in coupling region',
            curve_rate='Parameter that sets the upper limit on the rate of change of bent coupler curvature',
            coup_angle_in='Angle at which bent coupler curvature becomes zero',

            # Parameters of doping and salicide layers
            # ----------------------------------------
            doping_info='List of doping dictionaries containing: dist0, dist1, angle0, angle1, layer',

            # Parameters of inner and outer ring electrodes (including SI contact rails)
            # --------------------------------------------------------------------------
            inner_electrode_info='List of electrode dictionaries containing: dist0, dist1, angle0, angle1, layer',
            outer_electrode_info='List of electrode dictionaries containing: dist0, dist1, angle0, angle1, layer',

            # Parameters of vias
            # ------------------
            via_info='List of via dictionaries containing: dist, angle0, angle1, azim_dist, layer_top, layer_bottom',

            # Parameters of gs pads
            # ---------------------
            gs_electrodes='Boolean variable determines if GS pads are placed or not',
            gs_dist='Distance of the corners of GS pads from the center of ring core',
            gs_bottom_width='Width of the bottom layer of GS electrodes',
            gs_bottom_length='Length of the bottom layer of GS electrode',
            gs_pad_layer='Top Layer or LPP of GS pads',
            gs_pad_width='Width of GS pads',
            gs_pad_length='Length of GS pads',
            gs_pad_pitch='Pitch of GS pads',
        )

    @classmethod
    def get_default_param_values(cls) -> dict:
        """
        Returns default parameters of moscap ring
        """
        return dict(
            r_core_cent=None,

            core_layer=None,
            core_width=None,
            core_slot_width=None,

            slab_layer=None,
            slab_width=None,
            slab_slot_width=None,

            bent_coupler=None,
            coup_core_width=None,
            coup_slab_width=None,
            coup_length=None,
            coup_gap=None,
            coup_radius=None,
            coup_anlge=None,
            curve_rate=None,
            coup_angle_in=None,

            # Parameters of doping layers
            doping_info=None,
            inner_electrode_info=None,
            outer_electrode_info=None,

            via_info=None,

            # Parameters of GS pads
            gs_electrodes=True,
            gs_dist=None,
            gs_bottom_width=None,
            gs_bottom_length=None,

            gs_pad_layer=None,
            gs_pad_width=None,
            gs_pad_length=None,
            gs_pad_pitch=None,
        )

    def draw_layout(self):
        """
        Draws all components of rib-waveguide ring modulator
        """
        self.draw_rib_wg_ring()
        self.draw_input_wg()
        self.draw_concentric_rings(self.doping_info)
        self.draw_concentric_rings(self.inner_electrode_info)
        self.draw_concentric_rings(self.outer_electrode_info)

        self.place_circular_via_stack()
        self.place_contact_electrodes()
        if self.gs_electrodes:
            self.place_gs_electrodes()

    def draw_rib_wg_ring(self):
        """
        Draws core and slab rings of the rib waveguide ring structure
        """
        # Draw outer portion of core
        core_outer = self.add_round(
            layer=self.core_layer,
            resolution=self.grid.resolution,
            rout=self.r_core_cent + self.core_width / 2,
            rin=self.r_core_cent + self.core_slot_width / 2,
            center=self.ring_loc)
        self.add_obj(core_outer)

        # Draw inner portion of core
        core_inner = self.add_round(
            layer=self.core_layer,
            resolution=self.grid.resolution,
            rin=self.r_core_cent - self.core_width / 2,
            rout=self.r_core_cent - self.core_slot_width / 2,
            center=self.ring_loc)
        self.add_obj(core_inner)

        # Draw outer portion of slab
        slab_outer = self.add_round(
            layer=self.slab_layer,
            resolution=self.grid.resolution,
            rout=self.r_core_cent + self.slab_width / 2,
            rin=self.r_core_cent + self.slab_slot_width / 2,
            center=self.ring_loc)
        self.add_obj(slab_outer)

        # Draw inner portion of slab
        slab_inner = self.add_round(
            layer=self.slab_layer,
            resolution=self.grid.resolution,
            rin=self.r_core_cent - self.slab_width / 2,
            rout=self.r_core_cent - self.slab_slot_width / 2,
            center=self.ring_loc)
        self.add_obj(slab_inner)

    def draw_input_wg(self):
        """
        Draws input coupler waveguide of the rib-waveguide ring.
        """
        # general parameters to be passed to AdiabaticPaths
        coup_params = {'layer': self.core_layer,
                       'port_layer': self.core_layer,
                       'radius_threshold': self.coup_radius,
                       'curvature_rate_threshold': self.curve_rate,
                       'merge_arcs': False,
                       }
        # parameters of bent coupler
        bent_coup_params = {'arc_params':
                            [{'arc_type': 'wrapped_ring_coupler',
                              'rmin_in': self.coup_radius,
                              'alpha_zero_in': abs(self.coup_angle_in) * np.pi / 180,
                              'w_in': self.coup_core_width,
                              'r_coupling': self.coup_radius,
                              'angle_coupling': abs(self.coup_angle) * np.pi / 180,
                              'w_coupling': self.coup_core_width}
                             ]}
        # parameters of straight coupler
        straight_coup_params = {'arc_params':
                                [{'arc_type': 'straight_wg',
                                  'length': self.coup_length,
                                  'width': self.coup_core_width}
                                 ]}

        if self.bent_coupler:
            # update coupler parameters with bent coupler parameters
            coup_params.update(bent_coup_params)

            # coupler core master
            core_master = self.new_template(params=coup_params,
                                            temp_cls=AdiabaticPaths)

            # find the location of bent coupler
            loc = (self.ring_loc[0] - core_master.arc_list[-1]['x'][-1] / 2,
                   self.ring_loc[1] - max(core_master.arc_list[3]['y']) -
                   self.r_core_cent - self.coup_gap - (self.core_width + self.coup_core_width) / 2)

            # update the coupler parameters with slab parameters
            coup_params['layer'] = self.slab_layer
            coup_params['arc_params'][0]['w_coupling'] = self.slab_width
            coup_params['arc_params'][0]['w_in'] = self.slab_width
        else:
            # update coupler parameters with straight coupler parameters
            coup_params.update(straight_coup_params)

            # coupler core master
            core_master = self.new_template(params=coup_params,
                                            temp_cls=AdiabaticPaths)

            # find the placement location of straight coupler
            loc = (self.ring_loc[0] - self.coup_length / 2,
                   self.ring_loc[1] - self.r_core_cent - self.coup_gap - (self.core_width + self.coup_core_width) / 2)

            # update the coupler parameters with slab parameters
            coup_params['layer'] = self.slab_layer
            coup_params['arc_params'][0]['width'] = self.slab_width

        # place the coupler core to the north of the ring
        coup_core = self.add_instance(
            master=core_master,
            inst_name='input_wg',
            loc=loc
            )

        # Extract and rename the ports of coupler waveguide
        self.extract_photonic_ports(
            inst=coup_core,
            port_names=['PORT_IN', 'PORT_OUT'],
            port_renaming={'PORT_IN': 'PORT_0',
                           'PORT_OUT': 'PORT_1'},
            show=False)

        # bent coupler slab master
        coup_slab_master = self.new_template(params=coup_params,
                                             temp_cls=AdiabaticPaths)

        # place the coupler slab to the north of the ring
        self.add_instance(
            master=coup_slab_master,
            inst_name='input_wg',
            loc=loc
        )

    def draw_concentric_rings(self, ring_info):
        """
        Draws concentric rings corresponding to doping layers, silicon contact rails, salicide layers, ring electrodes
        """
        for ring_count in range(len(ring_info)):
            ring = self.add_round(
                layer=ring_info[ring_count]['layer'],
                resolution=self.grid.resolution,
                rout=self.r_core_cent + max(ring_info[ring_count]['dist0'],
                                            ring_info[ring_count]['dist1']),
                rin=self.r_core_cent + min(ring_info[ring_count]['dist0'],
                                           ring_info[ring_count]['dist1']),
                theta0=ring_info[ring_count]['angle0'],
                theta1=ring_info[ring_count]['angle1'],
                center=self.ring_loc
            )
            self.add_obj(ring)

    def place_circular_via_stack(self):
        """
        Draws azimuthally placed via stacks
        """
        for count in range(len(self.via_info)):
            # calculate angular step from azimuthal distance
            angle_step = (180 / np.pi) * self.via_info[count]['azim_dist'] / \
                         (self.r_core_cent + self.via_info[count]['dist'])

            # calculate the number of vias
            via_num = int((self.via_info[count]['angle1'] - self.via_info[count]['angle0']) // angle_step)

            # instantiate via stacks
            for via_count in range(via_num):
                delta_phi = np.pi * angle_step / 180
                phi = np.pi * self.via_info[count]['angle0'] / 180 + via_count * delta_phi
                self.add_via_stack(
                    bot_layer=self.via_info[count]['layer_bottom'],
                    top_layer=self.via_info[count]['layer_top'],
                    loc=(self.ring_loc[0] + (self.r_core_cent + self.via_info[count]['dist']) * np.cos(phi),
                         self.ring_loc[1] + (self.r_core_cent + self.via_info[count]['dist']) * np.sin(phi))
                )

    def place_contact_electrodes(self):
        # calculate the corner coordinate of the left (ground) pad
        self.g_pad_loc = (self.ring_loc[0] - (self.gs_pad_pitch - self.gs_pad_width) / 2,
                          self.ring_loc[1] - np.sqrt((self.r_core_cent+self.gs_dist)**2 -
                                                     ((self.gs_pad_pitch - self.gs_pad_width) / 2)**2
                                                     )
                          )
        # draw horizontal ground wire
        self.add_rect(layer=self.inner_electrode_info[-1]['layer'],
                      bbox=BBox(right=self.ring_loc[0],
                                bottom=-self.r_core_cent - self.inner_electrode_info[-1]['dist1'] -
                                       self.gs_bottom_width,
                                left=self.g_pad_loc[0] - self.gs_bottom_width,
                                top=-self.r_core_cent - self.inner_electrode_info[-1]['dist1'],
                                resolution=self.grid.resolution)
                      )
        # draw vertical ground wire
        self.add_rect(layer=self.inner_electrode_info[-1]['layer'],
                      bbox=BBox(right=self.g_pad_loc[0],
                                bottom=self.g_pad_loc[1] - self.gs_bottom_width,
                                left=self.g_pad_loc[0] - self.gs_bottom_width,
                                top=-self.r_core_cent - self.inner_electrode_info[-1]['dist1'],
                                resolution=self.grid.resolution)
                      )
        # calculate the corner coordinate of the right (signal) pad
        self.s_pad_loc = (self.ring_loc[0] + (self.gs_pad_pitch - self.gs_pad_width) / 2,
                          self.ring_loc[1] - np.sqrt((self.r_core_cent+self.gs_dist)**2 -
                                                     ((self.gs_pad_pitch - self.gs_pad_width) / 2)**2
                                                     )
                          )
        # draw horizontal signal wire
        self.add_rect(layer=self.outer_electrode_info[-1]['layer'],
                      bbox=BBox(left=self.ring_loc[0],
                                bottom=-self.r_core_cent - self.outer_electrode_info[-1]['dist0'] -
                                       self.gs_bottom_width,
                                right=self.s_pad_loc[0] + self.gs_bottom_width,
                                top=-self.r_core_cent - self.outer_electrode_info[-1]['dist0'],
                                resolution=self.grid.resolution)
                      )
        # draw vertical signal wire
        self.add_rect(layer=self.outer_electrode_info[-1]['layer'],
                      bbox=BBox(left=self.s_pad_loc[0],
                                bottom=self.s_pad_loc[1] - self.gs_bottom_width,
                                right=self.s_pad_loc[0] + self.gs_bottom_width,
                                top=-self.r_core_cent - self.outer_electrode_info[-1]['dist0'],
                                resolution=self.grid.resolution)
                      )

        # lower outer metal contact to the level of higher inner metal contact
        via_stack_master = self.new_template(params=dict(top_layer=self.inner_electrode_info[-1]['layer'],
                                                         bottom_layer=self.outer_electrode_info[-1]['layer'],
                                                         top_x_span=self.gs_bottom_width,
                                                         top_y_span=self.gs_bottom_length,
                                                         bottom_x_span=self.gs_bottom_width,
                                                         bottom_y_span=self.gs_bottom_length,
                                                         align='corner_align',
                                                         top_bot_offset=0.0),
                                             temp_cls=ViaStack)

        self.add_instance(master=via_stack_master,
                          inst_name='S_to_G_layer_via_stack',
                          loc=self.s_pad_loc,
                          orient='R0')

    def place_gs_electrodes(self):
        """
        Draws GS electrodes which are connected to ring electrodes
        """
        # Create GS pad
        gs_electrode_master = self.new_template(params=dict(top_layer=self.gs_pad_layer,
                                                            bottom_layer=self.inner_electrode_info[-1]['layer'],
                                                            top_x_span=self.gs_pad_width,
                                                            top_y_span=self.gs_pad_length,
                                                            bottom_x_span=self.gs_bottom_width,
                                                            bottom_y_span=self.gs_bottom_length,
                                                            align='corner_align',
                                                            top_bot_offset=0.0),
                                                temp_cls=ViaStack)

        # Place ground electrode
        self.add_instance(master=gs_electrode_master,
                          inst_name='G_electrode',
                          loc=self.g_pad_loc,
                          orient='MY')

        # Place signal electrode
        self.add_instance(master=gs_electrode_master,
                          inst_name='S_electrode',
                          loc=self.s_pad_loc,
                          orient='R0')


if __name__ == '__main__':
    spec_file = 'Photonic_Core_Layout/Ring/specs/ring_rib_wg_specs.yaml'
    PLM = BPG.PhotonicLayoutManager(spec_file)
    PLM.generate_content()
    PLM.generate_gds()
    PLM.generate_flat_content()
    PLM.generate_flat_gds()