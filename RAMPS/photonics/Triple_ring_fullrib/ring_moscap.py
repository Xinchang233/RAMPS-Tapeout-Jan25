import BPG
import numpy as np
from bag.layout.util import BBox
from Photonic_Core_Layout.Taper.LinearTaper import LinearTaper
from Photonic_Core_Layout.ViaStack.ViaStack import ViaStack


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

        self.salicide_ring_layer = self.params['salicide_ring_layer']
        self.salicide_ring_width = self.params['salicide_ring_width']

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
            salicide_ring_layer='Layer or LPP of salicide',
            salicide_ring_width='Width of salicide rings',
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
        )

    @classmethod
    def get_default_param_values(cls) -> dict:
        """
        Returns default parameters of moscap ring
        """
        return dict(
            body_layer=None,
            body_ring_rout=None,
            body_ring_width=None,

            input_wg_cosine=False,
            input_wg_width=0.45,
            input_wg_length=10.0,
            input_gap=None,

            drop_wg=False,
            drop_wg_width=0.45,
            drop_wg_length=10.0,
            drop_gap=0.2,
            drop_wg_taper_length=5.0,

            # Parameters of c_Si partial thickness (if available in the technology)
            body_thin=None,
            body_thin_layer=None,
            body_thin_rout=None,
            body_thin_width=None,

            # Parameters of p_Si (gate) ring
            gate_layer=None,
            gate_ring_rout=None,
            gate_ring_width=None,

            # Parameters of doping layers
            body_doping_info=None,
            gate_doping_info=None,

            # Parameters of metal electrodes
            body_via_radius=None,
            body_via_number=None,
            gate_via_radius=None,
            gate_via_number=None,
            salicide_ring_layer=None,
            salicide_ring_width=None,
            body_electrode_ring_layer=None,
            body_electrode_ring_width=None,
            gate_electrode_ring_layer=None,
            gate_electrode_ring_width=None,
            label_body_electrode='BODY',
            label_gate_electrode='GATE',

            # Parameters of GS pads
            gs_electrodes=True,

            g_bottom_width=0.5,
            g_bottom_length=0.5,

            s_bottom_width=0.5,
            s_bottom_length=0.5,

            pad_layer=None,
            pad_width=38.0,
            pad_length=50,
            pad_pitch=42.0,
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

        # Draw salicide ring in the region of body ring where circular via stack is placed
        self.draw_salicide_or_electrode_ring(rout=self.body_via_radius + self.salicide_ring_width / 2,
                                             rin=self.body_via_radius - self.salicide_ring_width / 2,
                                             layer=self.salicide_ring_layer)

        # Draw circular via stack attached to body ring
        self.draw_circular_via_stack(via_radius=self.body_via_radius,
                                     via_number=self.body_via_number,
                                     bot_layer=self.body_layer,
                                     top_layer=self.body_electrode_ring_layer)

        # Draw electrode ring connected to body ring through via stack
        self.draw_salicide_or_electrode_ring(rout=self.body_via_radius+self.body_electrode_ring_width / 2,
                                             rin=self.body_via_radius - self.body_electrode_ring_width / 2,
                                             layer=self.body_electrode_ring_layer)

        # Draw doping layer on gate ring
        self.draw_doping_ring(doping_info=self.gate_doping_info)

        # Draw salicide ring in the region of gate ring where circular via stack is placed
        self.draw_salicide_or_electrode_ring(rout=self.gate_via_radius + self.salicide_ring_width / 2,
                                             rin=self.gate_via_radius - self.salicide_ring_width / 2,
                                             layer=self.salicide_ring_layer)

        # Draw circular via stack attached to gate ring
        self.draw_circular_via_stack(via_radius=self.gate_via_radius,
                                     via_number=self.gate_via_number,
                                     bot_layer=self.body_layer,
                                     top_layer=self.gate_electrode_ring_layer)

        # Draw electrode ring connected to gate ring through via stack
        self.draw_salicide_or_electrode_ring(rout=self.gate_via_radius+self.gate_electrode_ring_width / 2,
                                             rin=self.gate_via_radius - self.gate_electrode_ring_width / 2,
                                             layer=self.gate_electrode_ring_layer)

        # Draw GS electrodes which will be connected to ring electrodes
        self.draw_gs_electrodes()

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
                port_renaming={'PORT0': 'INPUT', 'PORT1': 'THRU'},
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
        self.add_instances_port_to_port(inst_master=taper_master,
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
            phi = via_count * delta_phi
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
                                                           top_x_span=self.pad_width,
                                                           top_y_span=self.pad_length,
                                                           bottom_x_span=self.g_bottom_width,
                                                           bottom_y_span=self.g_bottom_length,
                                                           side_align=True),
                                               temp_cls=ViaStack)

        # Place ground electrode
        self.add_instance(master=g_electrode_master,
                          inst_name='G_electrode',
                          loc=(self.ring_loc[0]-self.body_via_radius +
                               self.body_electrode_ring_width/2 - offset_length,
                               self.ring_loc[1]),
                          orient='R180')

        # Create rectangular extension which connects gate ring electrode to signal electrode
        self.add_rect(layer=self.gate_electrode_ring_layer,
                      bbox=BBox(right=self.ring_loc[0] + self.gate_via_radius -
                                      self.body_electrode_ring_width/2 + offset_length,
                                bottom=self.ring_loc[1] - self.s_bottom_length/2,
                                left=self.ring_loc[0] + self.gate_via_radius -
                                     self.body_electrode_ring_width/2,
                                top=self.ring_loc[1] + self.s_bottom_length / 2,
                                resolution=self.grid.resolution)
                      )

        # Raise the ground (body) electrode from lower metal layer to the layer of signal (gate) electrode
        g_lift_master = self.new_template(params=dict(top_layer=self.body_electrode_ring_layer,
                                                      bottom_layer=self.gate_electrode_ring_layer,
                                                      top_x_span=self.g_bottom_width,
                                                      top_y_span=self.g_bottom_length,
                                                      bottom_x_span=self.g_bottom_width,
                                                      bottom_y_span=self.g_bottom_length,
                                                      side_align=True),
                                          temp_cls=ViaStack)

        self.add_instance(master=g_lift_master,
                          inst_name='G_electrode',
                          loc=(self.ring_loc[0]-self.body_via_radius +
                               self.body_electrode_ring_width/2 - offset_length,
                               self.ring_loc[1]),
                          orient='R180')

        # Create signal electrode master
        s_electrode_master = self.new_template(params=dict(top_layer=self.pad_layer,
                                                           bottom_layer=self.body_electrode_ring_layer,
                                                           top_x_span=self.pad_width,
                                                           top_y_span=self.pad_length,
                                                           bottom_x_span=self.s_bottom_width,
                                                           bottom_y_span=self.s_bottom_length,
                                                           side_align=True),
                                               temp_cls=ViaStack)

        # Place ground electrode
        self.add_instance(master=s_electrode_master,
                          inst_name='S_electrode',
                          loc=(self.ring_loc[0] + self.gate_via_radius -
                               self.gate_electrode_ring_width/2 + offset_length,
                               self.ring_loc[1]),
                          orient='R0')

if __name__ == '__main__':
    spec_file = 'Photonic_Core_Layout/Ring/specs/ring_moscap_specs.yaml'
    PLM = BPG.PhotonicLayoutManager(spec_file)
    PLM.generate_content()
    PLM.generate_gds()
    PLM.generate_flat_content()
    PLM.generate_flat_gds()