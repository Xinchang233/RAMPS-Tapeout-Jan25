import BPG
import numpy as np
from bag.layout.util import BBox
from Photonic_Core_Layout.Taper.LinearTaper import LinearTaper
from Photonic_Core_Layout.ViaStack_test.ViaStack import ViaStack
from layout.Importers.Gratings.GcUnidirWl1310nmMfd5000nm import GcUnidirWl1310nmMfd5000nm
from copy import deepcopy
from Photonic_Core_Layout.AdiabaticPaths.AdiabaticPaths import AdiabaticPaths

class RingMoscap(BPG.PhotonicTemplateBase):
    """
    This class generates moscap ring modulator

    """

    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)

        # Initialize variables and dictionary of parameters
        # Hard coded params
        self.ring_loc = (0, 0)

        # Parameters of c_Si (body) ring and input/drop waveguides

        self.body_layer = self.params['body_layer']
        self.body_ring_rout = self.params['body_ring_rout']
        self.body_ring_width = self.params['body_ring_width']

        self.input_wg_cosine = self.params['input_wg_cosine']
        self.input_wg_width = self.params['input_wg_width']
        self.input_wg_length = self.params['input_wg_length']
        self.input_gap = self.params['input_gap']

        self.drop_wg = self.params['drop_wg']
        self.drop_wg_length = self.params['drop_wg_length']
        self.drop_wg_width = self.params['drop_wg_width']
        self.drop_gap = self.params['drop_gap']
        self.drop_wg_taper_length = self.params['drop_wg_taper_length']

        # Parameters of c_Si partial thickness (if available in the technology)
        self.body_thin = self.params['body_thin']
        self.body_thin_layer = self.params['body_thin_layer']
        self.body_thin_rout = self.params['body_thin_rout']
        self.body_thin_width = self.params['body_thin_width']

        # Parameters of p_Si (gate) ring
        self.gate_layer = self.params['gate_layer']
        self.gate_ring_rout = self.params['gate_ring_rout']
        self.gate_ring_width = self.params['gate_ring_width']

        # Parameters of doping layers
        self.body_doping_info = self.params['body_doping_info']
        self.gate_doping_info = self.params['gate_doping_info']

        # Parameters of metal vias and ring electrodes
        self.body_via_radius = self.params['body_via_radius']
        self.body_via_number = self.params['body_via_number']
        self.gate_via_radius = self.params['gate_via_radius']
        self.gate_via_number = self.params['gate_via_number']

        self.body_electrode_ring_layer = self.params['body_electrode_ring_layer']
        self.body_electrode_ring_width = self.params['body_electrode_ring_width']
        self.gate_electrode_ring_layer = self.params['gate_electrode_ring_layer']
        self.gate_electrode_ring_width = self.params['gate_electrode_ring_width']

        self.label_body_electrode = self.params['label_body_electrode']
        self.label_gate_electrode = self.params['label_gate_electrode']

        # Parameters of GS electrodes
        self.gs_electrodes = self.params['gs_electrodes']

        self.g_bottom_width = self.params['g_bottom_width']
        self.g_bottom_length = self.params['g_bottom_length']

        self.s_bottom_width = self.params['s_bottom_width']
        self.s_bottom_length = self.params['s_bottom_length']

        self.pad_layer = self.params['pad_layer']
        self.pad_width = self.params['pad_width']
        self.pad_length = self.params['pad_length']
        self.pad_pitch = self.params['pad_pitch']
        self.gs_pad_open_layer = self.params['gs_pad_open_layer']
        self.gs_pad_open_inclusion = self.params['gs_pad_open_inclusion']

        # Parameters of auxiliary layers such as exclusion layer
        self.aux_layer_info = self.params['aux_layer_info']

        self.place_grating = self.params['place_grating']

    @classmethod
    def get_params_info(cls) -> dict:
        return dict(
            # Parameters of c_Si (body) ring and input/drop waveguides
            body_layer='Layer or LPP of body ring and input/drop waveguides of moscap resonator',
            body_ring_rout='Outer radius of body ring of moscap resonator',
            body_ring_width='Width of body ring of moscap resonator',

            input_wg_cosine='Boolean variable which determines the type of input waveguide (cosine or straight)',
            input_wg_width='Width of input waveguide of moscap resonator',
            input_wg_length='Length of input waveguide of moscap resonator',
            input_gap='Coupling gap between input waveguide and body ring of moscap resonator',

            drop_wg='Boolean variable which determines if drop waveguide is placed or not',
            drop_wg_width='Width of drop waveguide of moscap resoantor',
            drop_wg_length='Length of the drop waveguide of moscap resonator',
            drop_gap='Coupling gap between drop waveguide and body ring of moscap resonator',
            drop_wg_taper_length='Length of the radiating inverse taper of the drop waveguide',

            # Parameters of c_Si partial thickness (if available in the technology)
            body_thin='Boolean variable which determines if partial etch of body ring is placed',
            body_thin_layer='Layer or LPP that produces partially etched thin body layer of moscap resonator',
            body_thin_rout='Outer radius of partially etched thin body ring of moscap resonator',
            body_thin_width='Width of the partially etched thin body ring of moscap resonator',

            # Parameters of p_Si (gate) ring
            gate_layer='Layer or LPP of gate ring of moscap resonator',
            gate_ring_rout='Outer radius of gate ring of moscap resonator',
            gate_ring_width='Width of gate ring of moscap resoantor',

            # Parameters of doping layers
            body_doping_info='List of doping dictionaries for body ring containing: rout, rin, layer',
            gate_doping_info='List of doping dictionaries for gate ring containing: rout, rin, layer',

            # Parameters of metal electrodes
            body_via_radius='Distance between the center of moscap resonator and'
                            'centers of vias azimuthally placed on body ring',
            body_via_number='Number of vias azimuthally placed on body ring of moscap resonator',
            gate_via_radius='Distance between the center of moscap resonator and'
                            'centers of vias azimuthally placed on gate ring',
            gate_via_number='Number of vias azimuthally placed on gate ring of moscap resonator',
            body_electrode_ring_layer='List of metal layers or LPPs ordered from bottom to top'
                                      'on which ring electrode is drawn',
            body_electrode_ring_width='Width of the metal electrode which is connected to body ring through via stack',
            gate_electrode_ring_layer='List of metal layers or LPPs ordered from bottom to top'
                                      'on which ring electrode is drawn',
            gate_electrode_ring_width='Width of the metal electrode which is connected to gate ring through via stack',
            label_body_electrode='Label attached to electrode which is connected to body ring',
            label_gate_electrode='Label attached to electrode which is connected to gate ring',

            # Parameters of GS electrodes
            gs_electrodes='Boolean variable determines if GS pads are placed or not',

            g_bottom_width='Width of the bottom layer of ground electrode',
            g_bottom_length='Length of the bottom layer of ground electrode',

            s_bottom_width='Width of the bottom layer of signal electrode',
            s_bottom_length='Length of the bottom layer of signal electrode',

            pad_layer='Top Layer or LPP of GS pads',
            pad_width='Width of GS pads',
            pad_length='Length of GS pads',
            pad_pitch='Pitch of GS pads',

            gs_pad_open_layer='Passivation opening layer',
            gs_pad_open_inclusion='Inclusion width of passivation opening layer within metal pad',

            # Parameters of auxiliary layers such as exclusion layer
            aux_layer_info='List of dictionaries containing parameters width, length, and layer of aux layer',
            place_grating= 'Bolean determening if grating is placed'
        )

    @classmethod
    def get_default_param_values(cls) -> dict:
        """
        Returns default parameters of moscap ring
        """
        return dict(
            body_layer=('rx3phot', 'drawing'),
            body_ring_rout=2.61,
            body_ring_width=2.61,

            input_wg_cosine=False,
            input_wg_width=0.6,
            input_wg_length=5.0,
            input_gap=0.125,

            drop_wg=False,
            drop_wg_width=0.4,
            drop_wg_length=10.0,
            drop_gap=0.2,
            drop_wg_taper_length=5.0,

            # Parameters of c_Si partial thickness (if available in the technology)
            body_thin=False,
            body_thin_layer=('rx3phot', 'drawing'),
            body_thin_rout=1.8,
            body_thin_width=1.23,

            # Parameters of p_Si (gate) ring
            gate_layer=tuple(['pc3phot', 'drawing']),
            gate_ring_rout=2.5,
            gate_ring_width=1.7,

            # Parameters of doping layers
            body_doping_info=[{'rout': 2.5, 'rin': 0.0, 'layer': ('nw4phot', 'drawing')},
                              {'rout': 2.5, 'rin': 0.0, 'layer': ('nw3phot', 'drawing')},
                              {'rout': 1.2, 'rin': 0.0, 'layer': ('nw2phot', 'drawing')},
                              {'rout': 0.7, 'rin': 0.0, 'layer': ('n_inter_phot', 'drawing')},
                              {'rout': 1.2, 'rin': 0.0, 'layer': ('n_heavy_sil', 'drawing')}],
            gate_doping_info=[{'rout': 2.5, 'rin': 0.9, 'layer': ('RP', 'drawing')},
                              {'rout': 1.15, 'rin': 0.88, 'layer': ('p_inter_phot', 'drawing')}],

            # Parameters of metal electrodes
            body_via_radius=0.5,
            body_via_number=9,
            gate_via_radius=1.0,
            gate_via_number=20,
            body_electrode_ring_layer=('B1', 'drawing'),
            body_electrode_ring_width=0.2,
            gate_electrode_ring_layer=('C2', 'drawing'),
            gate_electrode_ring_width=0.2,
            label_body_electrode='BODY',
            label_gate_electrode='GATE',

            # Parameters of GS pads
            gs_electrodes=False,

            g_bottom_width=2.3,
            g_bottom_length=0.7,

            s_bottom_width=2.3,
            s_bottom_length=0.7,

            pad_layer=('LB', 'drawing'),
            pad_width=43.0,
            pad_length=65,
            pad_pitch=47.0,
            gs_pad_open_layer=('DV', 'drawing'),
            gs_pad_open_inclusion=2.0,

            # Parameters of auxiliary layers such as exclusion layer
            aux_layer_info=[{'width': 10.0, 'length': 10.0, 'layer': ('DG', 'drawing')}],

            place_grating = True)

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
        if self.gs_electrodes:
            self.draw_gs_electrodes()
        self.draw_auxiliary_layers()
        
        if self.place_grating:
            self.add_gratings()

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
    def add_gratings(self):
        grating_band_radius = 5
        grating_distance = 127
        access_length = 15
        wg_width = 0.5
        layer = ('rx3phot', 'drawing')
        reflect = True
        pad = (grating_distance - access_length) / 2
        adiabatic_band_params = dict(layer=layer, port_layer=['si_full_free', 'port'], radius_threshold=1.5,
                                     curvature_rate_threshold=0.7, merge_arcs=False)
        if grating_band_radius == 0:
            adiabatic_band_params['arc_params'] = [
                dict(arc_type="straight_wg", width=wg_width, length=pad)]
            temp_wg = self.new_template(params=adiabatic_band_params, temp_cls=AdiabaticPaths)
            right_wg_inst = self.add_instance_port_to_port(inst_master=temp_wg,
                                                           instance_port_name='PORT_IN',
                                                           self_port_name='PORT1')

            left_wg_inst = self.add_instance_port_to_port(inst_master=temp_wg,
                                                          instance_port_name='PORT_IN',
                                                          self_port_name='PORT0')
            temp = self.new_template(params=None, temp_cls=GcUnidirWl1310nmMfd5000nm)
            right_inst = self.add_instance_port_to_port(inst_master=temp,
                                                        instance_port_name='PORT_OUT',
                                                        self_port=right_wg_inst['PORT_OUT'])
            left_inst = self.add_instance_port_to_port(inst_master=temp,
                                                       instance_port_name='PORT_OUT',
                                                       self_port=left_wg_inst['PORT_OUT'])
        else:
            adiabatic_band_params['arc_params'] = [
                dict(arc_type="straight_wg", width=wg_width,
                     length=pad - grating_band_radius * 1.8700958466)]
            temp_wg = self.new_template(params=adiabatic_band_params, temp_cls=AdiabaticPaths)
            right_wg_inst = self.add_instance_port_to_port(inst_master=temp_wg,
                                                           instance_port_name='PORT_IN',
                                                           self_port_name='THRU')

            left_wg_inst = self.add_instance_port_to_port(inst_master=temp_wg,
                                                          instance_port_name='PORT_IN',
                                                          self_port_name='INPUT')
            bend90_params = deepcopy(adiabatic_band_params)
            bend90_params['arc_params'] = [
                dict(arc_type="90_bend", rmin=grating_band_radius, turn_left=False, width=wg_width)]

            temp_90_right = self.new_template(params=bend90_params, temp_cls=AdiabaticPaths)
            inst_90_right = self.add_instance_port_to_port(inst_master=temp_90_right,
                                                           instance_port_name='PORT_IN',
                                                           self_port=right_wg_inst['PORT_OUT'],
                                                           reflect=reflect)

            bend90_params_left = deepcopy(bend90_params)
            bend90_params_left['arc_params'][0]['turn_left'] = True
            temp_90_left = self.new_template(params=bend90_params_left, temp_cls=AdiabaticPaths)
            inst_90_left = self.add_instance_port_to_port(inst_master=temp_90_left,
                                                          instance_port_name='PORT_IN',
                                                          self_port=left_wg_inst['PORT_OUT'],
                                                          reflect=reflect)

            temp = self.new_template(params=None, temp_cls=GcUnidirWl1310nmMfd5000nm)
            right_inst = self.add_instance_port_to_port(inst_master=temp,
                                                        instance_port_name='PORT_OUT',
                                                        self_port=inst_90_right['PORT_OUT'])
            left_inst = self.add_instance_port_to_port(inst_master=temp,
                                                       instance_port_name='PORT_OUT',
                                                       self_port=inst_90_left['PORT_OUT'])
    
    
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
