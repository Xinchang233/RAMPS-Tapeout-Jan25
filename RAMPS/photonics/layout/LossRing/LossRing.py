import BPG
import numpy as np
from bag.layout.util import BBox
from Photonic_Core_Layout.Taper.LinearTaper import LinearTaper
from Photonic_Core_Layout.ViaStack_test.ViaStack import ViaStack


class LossRing(BPG.PhotonicTemplateBase):
    """
    This class generates loss ring set

    """

    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)

        # Initialize variables and dictionary of parameters
        # Hard coded params
        self.bus_start = (0, 0)

        # ring parameters
        self.ring_params = self.params['ring_params']
        self.radius_increment = self.params['radius_increment']

        # bus parameters
        self.bus_layer = self.params['bus_layer']
        self.bus_width = self.params['bus_width']
        self.bus_length = self.params['bus_length']
        self.routing_width = self.params['routing_width']
        self.taper_length = self.params['taper_length']
        self.drop_bend_rmin = self.params['drop_bend_rmin']
        self.rad_taper_min_width = self.params['rad_taper_min_width']

        # coupling gap params
        self.coupling_gap_list = self.params['coupling_gap_list']

        # Parameters of auxiliary layers such as exclusion layer
        self.aux_layer_info = self.params['aux_layer_info']

        # grating parameters
        self.gc_package = self.params['gc_package']
        self.gc_class = self.params['gc_class']
        self.gc_params = self.params['gc_params']


    @classmethod
    def get_params_info(cls) -> dict:
        return dict(
            # ring parameters
            ring_params='',
            radius_increment='',

            # bus parameters
            bus_layer='',
            bus_width='',
            bus_length='',
            routing_width='',
            taper_length='',
            drop_bend_rmin='',
            rad_taper_min_width='',

            # coupling gap params
            coupling_gap_list='',

            # Parameters of auxiliary layers such as exclusion layer
            aux_layer_info='',

            # grating parameters
            gc_package='',
            gc_class='',
            gc_params='',
        )

    @classmethod
    def get_default_param_values(cls) -> dict:
        """
        Returns default parameters of moscap ring
        """
        return dict(
            # ring parameters
            ring_params=[{'rout': 3.0, 'width': 0.5, 'layer': ('pc3phot', 'drawing')},
                         {'rout': 3.0, 'width': 0.5, 'layer': ('pc3phot', 'drawing')}],
            radius_increment=0.01,

            # bus parameters
            bus_layer=('rx3phot', 'drawing'),
            bus_width=0.5,
            bus_length=5,
            routing_width=0.5,
            taper_length=3,
            drop_bend_rmin=3,
            rad_taper_min_width=0.1,

            # coupling gap params
            coupling_gap_list=[0.1, 0.2, 0.3, 0.4],

            # Parameters of auxiliary layers such as exclusion layer
            aux_layer_info=[{'width': 10.0, 'length': 10.0, 'layer': ('DG', 'drawing')}],

            # grating parameters
            gc_package='layout.Importers.Gratings.GcBidirWl1550nmMfd5000nm',
            gc_class='GcBidirWl1550nmMfd5000nm',
            gc_port='PORT_OUT',
            gc_params={'gds_path': 'layout/Importers/GDS_grating_couplers/\
                        gc_dirbi_unif_wl1550_mfd5000_deg15_dataprep_calibre.gds'},
        )

    def draw_layout(self):
        """
        Draws all components of moscap ring resonator with doped body and gate and electrical contacts
        """
        # Draw basic moscap ring
        self.draw_body_and_gate_rings()

        if self.body_thin:
            # Add partial etch to body ring
            self.draw_thin_body_ring()

        if not self.input_wg_cosine:
            # Draw straight input waveguide
            self.draw_input_or_drop_straight_wg(type_input=True,
                                                width=self.input_wg_width,
                                                length=self.input_wg_length,
                                                gap=self.input_gap)
        if self.drop_wg:
            # Draw straight drop waveguide
            self.draw_input_or_drop_straight_wg(type_input=False,
                                                width=self.drop_wg_width,
                                                length=self.drop_wg_length,
                                                gap=self.drop_gap)
            self.draw_drop_wg_taper()

        # Draw doping layers on body ring
        self.draw_doping_ring(doping_info=self.body_doping_info)

        # Draw circular via stack attached to body ring
        self.draw_circular_via_stack(via_radius=self.body_via_radius,
                                     via_number=self.body_via_number,
                                     bot_layer=('RX', 'drawing'),
                                     top_layer=self.body_electrode_ring_layer)

        # self.draw_circular_via_stack(via_radius=self.body_via_radius*2,
        #                              via_number=self.body_via_number,
        #                              bot_layer=('B2', 'drawing'),
        #                              top_layer=self.body_electrode_ring_layer)

        # Draw electrode ring connected to body ring through via stack
        self.draw_salicide_or_electrode_ring(rout=self.body_via_radius+self.body_electrode_ring_width / 2,
                                             rin=self.body_via_radius - self.body_electrode_ring_width / 2,
                                             layer=('M1', 'drawing'))
        self.draw_salicide_or_electrode_ring(rout=self.body_via_radius+self.body_electrode_ring_width / 2,
                                             rin=self.body_via_radius - self.body_electrode_ring_width / 2,
                                             layer=('M2', 'drawing'))
        self.draw_salicide_or_electrode_ring(rout=self.body_via_radius+self.body_electrode_ring_width / 2,
                                             rin=self.body_via_radius - self.body_electrode_ring_width / 2,
                                             layer=('M3', 'drawing'))
        self.draw_salicide_or_electrode_ring(rout=self.body_via_radius+self.body_electrode_ring_width / 2,
                                             rin=self.body_via_radius - self.body_electrode_ring_width / 2,
                                             layer=('C1', 'drawing'))
        self.draw_salicide_or_electrode_ring(rout=self.body_via_radius+self.body_electrode_ring_width / 2,
                                             rin=self.body_via_radius - self.body_electrode_ring_width / 2,
                                             layer=('C2', 'drawing'))
        self.draw_salicide_or_electrode_ring(rout=self.body_via_radius+self.body_electrode_ring_width / 2,
                                             rin=self.body_via_radius - self.body_electrode_ring_width / 2,
                                             layer=self.body_electrode_ring_layer)

        # Draw doping layer on gate ring
        self.draw_doping_ring(doping_info=self.gate_doping_info)

        # Draw circular via stack attached to gate ring
        self.draw_circular_via_stack(via_radius=self.gate_via_radius,
                                     via_number=self.gate_via_number,
                                     bot_layer=('RX', 'drawing'),
                                     top_layer=self.gate_electrode_ring_layer)

        # Draw electrode ring connected to gate ring through via stack
        self.draw_salicide_or_electrode_ring(rout=self.gate_via_radius+self.gate_electrode_ring_width / 2,
                                             rin=self.gate_via_radius - self.gate_electrode_ring_width / 2,
                                             layer=('M1', 'drawing'))
        self.draw_salicide_or_electrode_ring(rout=self.gate_via_radius+self.gate_electrode_ring_width / 2,
                                             rin=self.gate_via_radius - self.gate_electrode_ring_width / 2,
                                             layer=('M2', 'drawing'))
        self.draw_salicide_or_electrode_ring(rout=self.gate_via_radius+self.gate_electrode_ring_width / 2,
                                             rin=self.gate_via_radius - self.gate_electrode_ring_width / 2,
                                             layer=('M3', 'drawing'))
        self.draw_salicide_or_electrode_ring(rout=self.gate_via_radius+self.gate_electrode_ring_width / 2,
                                             rin=self.gate_via_radius - self.gate_electrode_ring_width / 2,
                                             layer=('C1', 'drawing'))
        self.draw_salicide_or_electrode_ring(rout=self.gate_via_radius+self.gate_electrode_ring_width / 2,
                                             rin=self.gate_via_radius - self.gate_electrode_ring_width / 2,
                                             layer=('C1', 'drawing'))
        self.draw_salicide_or_electrode_ring(rout=self.gate_via_radius+self.gate_electrode_ring_width / 2,
                                             rin=self.gate_via_radius - self.gate_electrode_ring_width / 2,
                                             layer=self.gate_electrode_ring_layer)

        # Draw GS electrodes which will be connected to ring electrodes
        self.draw_gs_electrodes()
        self.draw_auxiliary_layers()

    def draw_body_and_gate_rings(self):
        """
        Draws body and gate concentric rings of moscap resonator
        """
        # Draw body ring
        body_ring=self.add_round(
            layer=self.body_layer,
            resolution=self.grid.resolution,
            rout=self.body_ring_rout,
            rin=self.body_ring_rout-self.body_ring_width,
            center=self.ring_loc)
        self.add_obj(body_ring)

        # Draw gate ring
        gate_ring=self.add_round(
            layer=self.gate_layer,
            resolution=self.grid.resolution,
            rout=self.gate_ring_rout,
            rin=self.gate_ring_rout-self.gate_ring_width,
            center=self.ring_loc)
        self.add_obj(gate_ring)

    def draw_thin_body_ring(self):
        """
        Draws partial etch ring that produces thin body region on body ring
        """
        thin_ring=self.add_round(
            layer=self.body_thin_layer,
            resolution=self.grid.resolution,
            rout=self.body_thin_rout,
            rin=self.body_thin_rout-self.body_thin_width,
            center=self.ring_loc)
        self.add_obj(thin_ring)

    def draw_input_or_drop_straight_wg(self,
                                       type_input: bool,
                                       width: float,
                                       length: float,
                                       gap: float
                                       ):
        """
        Draws straight input or drop waveguide of moscap resonator.

        Parameters
        ----------
        width: float
            Width of the straight waveguide.
        length: float
            Length of the straight waveguide.
        gap:
            Coupling gap between body ring and the straight waveguide.
        """
        straight_wg_master = self.new_template(params=dict(width0=width,
                                                           width1=width,
                                                           length=length,
                                                           layer=self.body_layer),
                                               temp_cls=LinearTaper)
        # TODO a hack from here
        if self.body_ring_rout < 2.2:
            port_width = 0.5
        else:
            port_width = 0.7
        taper_master = self.new_template(params=dict(width0=port_width,
                                                     width1=self.input_wg_width,
                                                     length=5.0,
                                                     layer=self.body_layer),
                                         temp_cls=LinearTaper)
        # TODO to here

        if type_input:
            straight_wg = self.add_instance(
                master=straight_wg_master,
                inst_name='input_wg',
                loc=(self.ring_loc[0] - length / 2,
                     self.ring_loc[1]+self.body_ring_rout+gap+width / 2)
            )

            # Extract ports
            self.extract_photonic_ports(
                inst=straight_wg,
                #port_renaming={'PORT0': 'INPUT', 'PORT1': 'THRU'},
                show=False)

            in_taper = self.add_instance_port_to_port(inst_master=taper_master,
                                                      instance_port_name='PORT1',
                                                      self_port_name='PORT0',
                                                      reflect=False)

            self.delete_port('PORT0')

            # Extract ports
            self.extract_photonic_ports(
                inst=in_taper,
                port_names='PORT0',
                port_renaming={'PORT0': 'INPUT'},
                show=False)

            out_taper = self.add_instance_port_to_port(inst_master=taper_master,
                                                       instance_port_name='PORT1',
                                                       self_port_name='PORT1',
                                                       reflect=False)
            self.delete_port('PORT1')

            # Extract ports
            self.extract_photonic_ports(
                inst=out_taper,
                port_names='PORT0',
                port_renaming={'PORT0': 'THRU'},
                show=False)
        else:
            straight_wg = self.add_instance(
                master=straight_wg_master,
                inst_name='drop_wg',
                loc=(self.ring_loc[0] - length / 2,
                     self.ring_loc[1]-self.body_ring_rout-gap-width / 2)
            )
            # Extract ports
            self.extract_photonic_ports(
                inst=straight_wg,
                port_renaming={'PORT0': 'DROP', 'PORT1': 'ADD'},
                show=False)

    def draw_drop_wg_taper(self):
        """
        Draws radiating inverse taper on the drop waveguide
        """
        taper_master = self.new_template(params=dict(width0=self.drop_wg_width,
                                                     width1=self.photonic_tech_info.min_width(self.body_layer),
                                                     length=self.drop_wg_taper_length,
                                                     layer=self.body_layer),
                                         temp_cls=LinearTaper)
        self.add_instance_port_to_port(inst_master=taper_master,
                                       instance_port_name='PORT0',
                                       self_port_name='ADD',
                                       reflect=False)

    def draw_doping_ring(self, doping_info: list):
        """
        Draws concentric doping rings of moscap resonator
        """
        for doping_count in range(len(doping_info)):
            doping_ring=self.add_round(
                layer=doping_info[doping_count]['layer'],
                resolution=self.grid.resolution,
                rout=doping_info[doping_count]['rout'],
                rin=doping_info[doping_count]['rin'],
                center=self.ring_loc
            )
            self.add_obj(doping_ring)

    def draw_circular_via_stack(self,
                                via_radius: float,
                                via_number: int,
                                bot_layer: "layer_or_lpp_type",
                                top_layer: "layer_or_lpp_type",
                                ):
        """
        Draws azimuthally placed via stacks

        Parameters
        ----------
        via_radius: float
            Radius of via placement, i.e. distance between center of moscap ring and centers of via stacks
        via_number: int
            Number of via stacks uniformly distributed over 2pi angle
        bot_layer: layer_or_lpp_type
            Bottom layer or LPP of the circular via stack
        bot_layer: layer_or_lpp_type
            Top layer or LPP of the circular via stack
        """
        delta_phi = 2*np.pi/via_number
        for via_count in range(via_number):
            phi = np.pi/4 + via_count * delta_phi
            self.add_via_stack(
                bot_layer=bot_layer,
                top_layer=top_layer,
                loc=(np.cos(phi) * via_radius + self.ring_loc[0],
                     np.sin(phi) * via_radius + self.ring_loc[1])
            )

    def draw_salicide_or_electrode_ring(self,
                                        rout: float,
                                        rin: float,
                                        layer: "layer_or_lpp_type"
                                        ):
        """
        Draws ring electrode

        Parameters
        ----------
        rout: float
            Outer radius of ring salicide/electrode
        rout: float
            Inner radius of ring salicide/electrode
        layer: layer_or_lpp_type
            Layer or LPP of ring salicide/electrode
        """
        electrode_ring = self.add_round(
            layer=layer,
            resolution=self.grid.resolution,
            rout=rout,
            rin=rin,
            center=self.ring_loc)
        self.add_obj(electrode_ring)

    def draw_gs_electrodes(self):
        """
        Draws GS electrodes which are connected to ring electrodes
        """
        # Calculate contact offset length
        offset_length = (self.pad_pitch - self.pad_width -
                         self.gate_via_radius - self.body_via_radius +
                         self.gate_electrode_ring_width / 2 + self.body_electrode_ring_width / 2) / 2

        # Create rectangular extension which connects body ring electrode to ground electrode
        self.add_rect(layer=self.body_electrode_ring_layer,
                      bbox=BBox(left=self.ring_loc[0] - self.body_via_radius +
                                     self.body_electrode_ring_width/2 - offset_length,
                                bottom=self.ring_loc[1] - self.g_bottom_length/2,
                                right=self.ring_loc[0] - self.body_via_radius + self.body_electrode_ring_width/2,
                                top=self.ring_loc[1] + self.g_bottom_length / 2,
                                resolution=self.grid.resolution)
                      )

        # Create ground electrode master
        g_electrode_master = self.new_template(params=dict(top_layer=self.pad_layer,
                                                           bottom_layer=self.body_electrode_ring_layer,
                                                           top_x_span=self.pad_length,
                                                           top_y_span=self.pad_width,
                                                           bottom_x_span=self.g_bottom_width,
                                                           bottom_y_span=self.g_bottom_length,
                                                           align='corner_align',
                                                           top_bot_offset=0.0,
                                                           pad_open_layer=self.gs_pad_open_layer,
                                                           pad_open_inclusion=self.gs_pad_open_inclusion
                                                           ),
                                               temp_cls=ViaStack)

        # Place ground electrode
        self.add_instance(master=g_electrode_master,
                          inst_name='G_electrode',
                          loc=(self.ring_loc[0]-self.body_via_radius +
                               self.body_electrode_ring_width/2 - offset_length,
                               self.ring_loc[1] + self.g_bottom_length / 2),
                          orient='R270')

        # Create rectangular extension which connects gate ring electrode to signal electrode
        self.add_rect(layer=self.gate_electrode_ring_layer,
                      bbox=BBox(right=self.ring_loc[0] + self.gate_via_radius -
                                      self.gate_electrode_ring_width/2 + offset_length,
                                bottom=self.ring_loc[1] - self.s_bottom_length/2,
                                left=self.ring_loc[0] + self.gate_via_radius -
                                     self.gate_electrode_ring_width/2,
                                top=self.ring_loc[1] + self.s_bottom_length / 2,
                                resolution=self.grid.resolution)
                      )

        # Raise the ground (body) electrode from lower metal layer to the layer of signal (gate) electrode
        s_lift_master = self.new_template(params=dict(top_layer=self.body_electrode_ring_layer,
                                                      bottom_layer=self.gate_electrode_ring_layer,
                                                      top_x_span=self.s_bottom_width,
                                                      top_y_span=self.s_bottom_length,
                                                      bottom_x_span=self.s_bottom_width,
                                                      bottom_y_span=self.s_bottom_length,
                                                      align='corner_align',
                                                      top_bot_offset=0.0),
                                          temp_cls=ViaStack)

        self.add_instance(master=s_lift_master,
                          loc=(self.ring_loc[0] + self.gate_via_radius -
                               self.gate_electrode_ring_width/2 + offset_length,
                               self.ring_loc[1] + self.s_bottom_length/2),
                          orient='MYR90')

        # Create signal electrode master
        s_electrode_master = self.new_template(params=dict(top_layer=self.pad_layer,
                                                           bottom_layer=self.body_electrode_ring_layer,
                                                           top_x_span=self.pad_length,
                                                           top_y_span=self.pad_width,
                                                           bottom_x_span=self.s_bottom_width,
                                                           bottom_y_span=self.s_bottom_length,
                                                           align='corner_align',
                                                           top_bot_offset=0.0,
                                                           pad_open_layer=self.gs_pad_open_layer,
                                                           pad_open_inclusion=self.gs_pad_open_inclusion
                                                           ),
                                               temp_cls=ViaStack)

        # Place ground electrode
        self.add_instance(master=s_electrode_master,
                          inst_name='S_electrode',
                          loc=(self.ring_loc[0] + self.gate_via_radius -
                               self.gate_electrode_ring_width/2 + offset_length,
                               self.ring_loc[1] + self.s_bottom_length/2),
                          orient='MYR90')

    def draw_auxiliary_layers(self):
        """
        Draw auxiliary layers (such as exclusion layers)
        """
        for count in range(len(self.aux_layer_info)):
            self.add_rect(layer=self.aux_layer_info[count]['layer'],
                          bbox=BBox(left=self.ring_loc[0] - self.aux_layer_info[count]['width'] / 2,
                                    bottom=self.ring_loc[1] - self.aux_layer_info[count]['length'] / 2,
                                    right=self.ring_loc[0] + self.aux_layer_info[count]['width'] / 2,
                                    top=self.ring_loc[1] + self.aux_layer_info[count]['length'] / 2,
                                    resolution=self.grid.resolution)
                          )

if __name__ == '__main__':
    spec_file = 'layout/MoscapModulator/specs/ring_moscap_specs.yaml'
    PLM = BPG.PhotonicLayoutManager(spec_file)
    PLM.generate_content()
    PLM.generate_gds()
    # PLM.generate_flat_content()
    # PLM.generate_flat_gds()
    # dataprep
    # PLM.dataprep()
    PLM.dataprep_calibre()
