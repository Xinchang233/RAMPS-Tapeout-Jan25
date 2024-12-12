import BPG
import numpy as np
from bag.layout.util import BBox
from Photonic_Core_Layout.ViaStack.ViaStack import ViaStack
from Photonic_Core_Layout.AdiabaticPaths.AdiabaticPaths import AdiabaticPaths
from ..Single_ring_fullrib.ringheater_fullrib_vertical import RingHeater
from ..Taper.StripToRibTaper import StripToRibTaper
from ..Spoke.SpokeBase_circular_angular import SpokeBase

class RingRibWg(BPG.PhotonicTemplateBase):
    """
    This class generates rib-waveguide ring modulator
    """

    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)

        # Initialize variables and dictionary of parameters
        self.ring_loc = (0, 0)
        self.left_pad_loc = None
        self.right_pad_loc = None
        self.central_pad_loc = None

        self.heaterpad1_loc = None
        self.heaterpad2_loc = None
        self.heaterpad3_loc = None
        self.heaterpad4_loc = None
        self.heaterpad5_loc = None
        self.heaterpad6_loc = None


        self.r_r_gap=self.params['r_r_gap']
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
        self.basic_metal_routing = self.params['basic_metal_routing']

        # Parameters of doping and salicide layers
        # ----------------------------------------
        self.doping_info1 = self.params['doping_info1']

        # Parameters of inner and outer ring electrodes (including SI contact rails)
        # --------------------------------------------------------------------------
        self.inner_electrode_info1 = self.params['inner_electrode_info1']
        self.outer_electrode_info1 = self.params['outer_electrode_info1']
        self.inner_electrode_info3 = self.params['inner_electrode_info3']
        self.outer_electrode_info3 = self.params['outer_electrode_info3']

        # Parameters of vias
        # ------------------
        self.via_info1 = self.params['via_info1']

        self.doping_info2 = self.params['doping_info2']

        # Parameters of inner and outer ring electrodes (including SI contact rails)
        # --------------------------------------------------------------------------
        self.inner_electrode_info2 = self.params['inner_electrode_info2']
        self.outer_electrode_info2 = self.params['outer_electrode_info2']

        # Parameters of vias
        # ------------------
        self.via_info2 = self.params['via_info2']

        # Parameters of gs pads
        # ---------------------
        self.gs_electrodes = self.params['gs_electrodes']
        self.gs_core_dist = self.params['gs_core_dist']
        self.gs_bottom_width = self.params['gs_bottom_width']
        self.gs_bottom_length = self.params['gs_bottom_length']
        self.gs_pad_layer = self.params['gs_pad_layer']
        self.gs_pad_open_layer = self.params['gs_pad_open_layer']
        self.gs_pad_open_inclusion = self.params['gs_pad_open_inclusion']
        self.gs_pad_width = self.params['gs_pad_width']
        self.gs_pad_length = self.params['gs_pad_length']
        self.gs_pad_pitch = self.params['gs_pad_pitch']
        self.gs_pad_to_ring_dist = self.params['gs_pad_to_ring_dist']

        self.access_length = self.params['gs_pad_to_ring_dist']
        self.p_via_radius_offset = self.params['p_via_radius_offset']
        self.n_via_radius_offset = self.params['n_via_radius_offset']
        self.high_doping_rout_offset = self.params['high_doping_rout_offset']
        self.high_doping_rin_offset = self.params['high_doping_rin_offset']
        self.electrode_offset = self.params['electrode_offset']
        self.electrode_width_inner = self.params['electrode_width_inner']
        self.electrode_width_outer = self.params['electrode_width_outer']
        self.drop_taper_length = self.params['drop_taper_length']
        self.salicide_radius_extension = self.params['salicide_radius_extension']
        self.high_doping_n_rin_offset = self.params['high_doping_n_rin_offset']
        self.heater_width = self.params['heater_width']
        self.heater_pad_to_ring_dist = self.params['heater_pad_to_ring_dist']
        self.contact_dist = self.params['contact_dist']
        self.heater_electrode_top_layer = self.params['heater_electrode_top_layer']

        # Parameters of input output tapers
        # ---------------------------------
        self.in_out_taper = self.params['in_out_taper']
        self.in_out_port_width = self.params['in_out_port_width']
        self.taper_length = self.params['taper_length']
        self.taper_layer1 = self.params['taper_layer1']
        # taper_layer1=('si_fullfree', 'drawing'),
        self.taper_layer2 = self.params['taper_layer2']
        self.coup_gap_drop = self.params['coup_gap_drop']
        self.heater_electrode_top_y_span = self.params['heater_electrode_top_y_span']

        self.doping_spoke_info1 = self.params['doping_spoke_info1']
        self.doping_spoke_info2 = self.params['doping_spoke_info2']

    @classmethod
    def get_params_info(cls) -> dict:
        return dict(
            # Parameters of rib-waveguide ring
            # --------------------------------
            r_core_cent='Radius to the center of ring core',
            r_r_gap='Ring to ring gap',
            core_layer='Layer or LPP of ring core',
            core_width='Width of ring core',
            core_slot_width='Width of slot in ring core',

            slab_layer='Layer or LPP of ring slab',
            slab_width='Width of ring slab',
            slab_slot_width='Width of slot in ring slab',
            basic_metal_routing='Option to have only basic metal routings for upper level',

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
            doping_info1='List of doping dictionaries containing: dist0, dist1, angle0, angle1, layer',

            # Parameters of inner and outer ring electrodes (including SI contact rails)
            # --------------------------------------------------------------------------
            inner_electrode_info1='List of electrode dictionaries containing: dist0, dist1, angle0, angle1, layer',
            outer_electrode_info1='List of electrode dictionaries containing: dist0, dist1, angle0, angle1, layer',

            # Parameters of vias
            # ------------------
            via_info1='List of via dictionaries containing: dist, angle0, angle1, azim_dist, layer_top, layer_bottom',

            doping_info2='List of doping dictionaries containing: dist0, dist1, angle0, angle1, layer',

            # Parameters of inner and outer ring electrodes (including SI contact rails)
            # --------------------------------------------------------------------------
            inner_electrode_info2='List of electrode dictionaries containing: dist0, dist1, angle0, angle1, layer',
            outer_electrode_info2='List of electrode dictionaries containing: dist0, dist1, angle0, angle1, layer',
            inner_electrode_info3='List of electrode dictionaries containing: dist0, dist1, angle0, angle1, layer',
            outer_electrode_info3='List of electrode dictionaries containing: dist0, dist1, angle0, angle1, layer',
            # Parameters of vias
            # ------------------
            via_info2='List of via dictionaries containing: dist, angle0, angle1, azim_dist, layer_top, layer_bottom',

            # Parameters of gs pads
            # ---------------------
            gs_electrodes='Boolean variable determines if GS pads are placed or not',
            gs_core_dist='Distance of the corners of GS pads from the center of ring core',
            gs_bottom_width='Width of the bottom layer of GS electrodes',
            gs_bottom_length='Length of the bottom layer of GS electrode',
            gs_pad_layer='Top Layer or LPP of GS pads',
            gs_pad_open_layer='ss',
            gs_pad_open_inclusion='s',
            gs_pad_width='Width of GS pads',
            gs_pad_length='Length of GS pads',
            gs_pad_pitch='Pitch of GS pads',
            gs_pad_to_ring_dist='sdfs',

            # Standard params
            heater_disable='True to not place the heater. Defaults to False (ie heater is present).',
            heater_radius_offset='Offset of outer heater radius from inner ring radius',
            resistance='Resistance target for the heater',
            contact_dist='Distance between two inner edges of the two interior spokes that contact the heater ring.',
            contact_width='Width of interior contact spokes that connect the heater ring to the via stack',
            heater_device_layer='LPP of ring heater device (ie layer of the actual heater)',
            heater_disk_layers='List of additional LPPs on which disks covering the entire ring heater will be drawn',
            heater_electrode_top_layer='LPP of top metal layer of the gs electrode',
            heater_electrode_top_x_span='Electrode x-span on the top electrode metal layer (defaults to 1)',
            heater_electrode_top_y_span='Electrode y-span on the top electrode metal layer (defaults to 1)',
            heater_label='Electrode contact label text [str], or dictionary with keys P: <p_label> and N: <n_label>',
            heater_electrode_bottom_x_span='Electrode x-span on the bottom electrode metal '
                                           'layer (defaults to contact_width)',
            heater_electrode_bottom_y_span='Electrode y-span on the bottom electrode metal '
                                           'layer (defaults to contact_width)',
            # Advanced parameters
            heater_disk_layer_extension='Size by which disk_layers should be drawn beyond outer radius of heater ring',
            # Technology parameter
            heater_electrode_bottom_layer='LPP for the bottom electrode layer in the stack (should be the BAG '
                                          'equivalent layer of device_layer)',
            heater_width='ddsf',
            access_length='d',
            p_via_radius_offset='d',
            n_via_radius_offset='d',
            high_doping_rout_offset='d',
            high_doping_rin_offset='d',
            electrode_offset='d',
            electrode_width_inner='d',
            electrode_width_outer='d',
            drop_taper_length='d',
            salicide_radius_extension='d',
            high_doping_n_rin_offset='d',
            heater_pad_to_ring_dist='ee',
            # Parameters of input output tapers
            # ---------------------------------
            in_out_taper='True',
            in_out_port_width='0.5',
            taper_length='10.2',
            taper_layer1='xvcx',
            # taper_layer1=('si_fullfree', 'drawing'),
            taper_layer2='xcv',
            coup_gap_drop='sds',

            doping_spoke_info2='asf',
            doping_spoke_info1='ad',
        )

    @classmethod
    def get_default_param_values(cls) -> dict:
        """
        Returns default parameters of moscap ring
        """
        return dict(
            r_core_cent=None,
            r_r_gap=None,
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
            doping_info1=None,
            inner_electrode_info1=None,
            outer_electrode_info1=None,

            via_info1=None,

            # Parameters of doping layers
            doping_info2=None,
            inner_electrode_info2=None,
            outer_electrode_info2=None,
            inner_electrode_info3=None,
            outer_electrode_info3=None,
            via_info2=None,

            # Parameters of GS pads
            gs_electrodes=True,
            gs_core_dist=None,
            gs_bottom_width=None,
            gs_bottom_length=None,
            gs_pad_open_layer=None,
            gs_pad_open_inclusion=None,
            gs_pad_layer=None,
            gs_pad_width=None,
            gs_pad_length=None,
            gs_pad_pitch=None,
            gs_pad_to_ring_dist=None,

            heater_disable=None,
            heater_radius_offset=None,
            resistance=None,
            contact_dist=None,
            contact_width=None,
            heater_device_layer=None,
            heater_disk_layers=None,
            heater_electrode_top_layer=None,
            heater_electrode_top_x_span=None,
            heater_electrode_top_y_span=None,
            heater_label=None,
            heater_electrode_bottom_x_span=None,
            heater_electrode_bottom_y_span=None,
            # Advanced parameters
            heater_disk_layer_extension=None,
            heater_electrode_bottom_layer=None,
            heater_width=None,

            access_length=None,
            p_via_radius_offset=None,
            n_via_radius_offset=None,
            high_doping_rout_offset=None,
            high_doping_rin_offset=None,
            electrode_offset=None,
            electrode_width_inner=None,
            electrode_width_outer=None,
            drop_taper_length=None,
            salicide_radius_extension=None,
            high_doping_n_rin_offset=None,
            heater_pad_to_ring_dist=None,
            # Parameters of input output tapers
            # ---------------------------------
            in_out_taper=None,
            in_out_port_width=None,
            taper_length=None,
            taper_layer1=None,
            # taper_layer1=('si_fullfree', 'drawing'),
            taper_layer2=None,
            coup_gap_drop=None,
            doping_spoke_info2=None,
            doping_spoke_info1=None,
        )

    def draw_layout(self):
        """
        Draws all components of rib-waveguide ring modulator
        """
        self.draw_rib_wg_ring1()
        self.draw_rib_wg_ring2()
        self.draw_rib_wg_ring3()
        self.draw_input_wg()
        #self.draw_input_wg_drop()
        self.draw_heater()
        self.draw_concentric_rings1(self.doping_info1)
        self.draw_concentric_rings1(self.inner_electrode_info1)
        self.draw_concentric_rings1(self.outer_electrode_info1)
        self.draw_concentric_rings2(self.doping_info2)
        self.draw_concentric_rings2(self.inner_electrode_info2)
        self.draw_concentric_rings2(self.outer_electrode_info2)
        self.draw_concentric_rings3(self.inner_electrode_info3)
        self.draw_concentric_rings3(self.outer_electrode_info3)
        self.place_circular_via_stack1()
        self.place_circular_via_stack2()
        if self.basic_metal_routing:
            self.place_contact_electrodes_basic()
            self.place_heater_contact_electrodes_basic()
        else:
            self.place_contact_electrodes()
            self.place_heater_contact_electrodes()
            self.place_gs_electrodes()
            self.place_heater_gs_electrodes()
        #self.PHPN1_addition()
        self.mod_addition()
        self.photon_addition()
        # self.draw_KG_pieces() # commented out
        #self.draw_silicon_pieces()
        self.draw_doping_spokes1(self.doping_spoke_info1)
        self.draw_doping_spokes2(self.doping_spoke_info2)

    def draw_silicon_pieces(self):
        #ADD rx PIECE AT INTERSECTION OF RINGS TOWARDS UPP
        self.add_rect(layer=('RX', 'drawing'),
                      bbox=BBox(right=-7.21,
                                bottom=4.3,
                                left=-9.21,
                                top=5,
                                resolution=self.grid.resolution)
                      )
        # ADD rx PIECE AT INTERSECTION OF RINGS TOWARDS DOWN
        self.add_rect(layer=('RX', 'drawing'),
                      bbox=BBox(right=-7.21,
                                bottom=-5,
                                left=-9.21,
                                top=-3.7,
                                resolution=self.grid.resolution)
                      )
        # ADD rx PIECE AT INTERSECTION OF RINGS TOWARDS UPP ,second ring
        self.add_rect(layer=('RX', 'drawing'),
                      bbox=BBox(right=9.21,
                                bottom=4.3,
                                left=7.21,
                                top=5,
                                resolution=self.grid.resolution)
                      )
        # ADD rx PIECE AT INTERSECTION OF RINGS TOWARDS DOWN,second ring
        self.add_rect(layer=('RX', 'drawing'),
                      bbox=BBox(right=9.21,
                                bottom=-5,
                                left=7.21,
                                top=-3.7,
                                resolution=self.grid.resolution)
                      )
        #BUS rx PIEACE TOWARDS RIGHT SIDE
        self.add_rect(layer=('RX', 'drawing'),
                      bbox=BBox(right=-11.56,
                                bottom=-8.7,
                                left=-12.41,
                                top=-7.4,
                                resolution=self.grid.resolution)
                      )
        # BUS rx PIEACE TOWARDS LEFT SIDE
        self.add_rect(layer=('RX', 'drawing'),
                      bbox=BBox(right=-19.51,
                                bottom=-8.7,
                                left=-21.31,
                                top=-7.7,
                                resolution=self.grid.resolution)
                      )

    def draw_KG_pieces(self):
        #self.add_rect(layer=('KG', 'drawing'),bbox=BBox(right=5,bottom=-5,left=-5,top=5,resolution=self.grid.resolution)
        self.add_rect(layer=('KG', 'drawing'),
                      bbox=BBox(right=9.21,
                                bottom=4.0,
                                left=7.21,
                                top=5.0,
                                resolution=self.grid.resolution)
                      )
        self.add_rect(layer=('KG', 'drawing'),
                      bbox=BBox(right=9.21,
                                bottom=-5.0,
                                left=7.21,
                                top=-4.2,
                                resolution=self.grid.resolution)
                      )
        # self.add_rect(layer=('KG', 'drawing'),bbox=BBox(right=5,bottom=-5,left=-5,top=5,resolution=self.grid.resolution)
        self.add_rect(layer=('KG', 'drawing'),
                      bbox=BBox(right=-7.21,
                                bottom=4.3,
                                left=-9.21,
                                top=5.0,
                                resolution=self.grid.resolution)
                      )
        self.add_rect(layer=('KG', 'drawing'),
                      bbox=BBox(right=-7.21,
                                bottom=-5.0,
                                left=-9.21,
                                top=-4.2,
                                resolution=self.grid.resolution)
                      )

        self.add_rect(layer=('KG', 'drawing'),
                      bbox=BBox(right=-10.8,
                                bottom=-8.4,
                                left=-11.8,
                                top=-7.3,
                                resolution=self.grid.resolution)
                      )

        self.add_rect(layer=('KG', 'drawing'),
                      bbox=BBox(right=-21,
                                bottom=-8.4,
                                left=-22,
                                top=-7.3,
                                resolution=self.grid.resolution)
                      )





    def PHPN1_addition(self):
        self.add_rect(layer= ('PHPN1', 'drawing'),
                      bbox=BBox(right=30,
                                bottom=-12,
                                left=-30,
                                top=12,
                                resolution=self.grid.resolution)
                      )

    def mod_addition(self):
        self.add_rect(layer=('mod', 'drawing'),
                      bbox=BBox(right=35,
                                bottom=-15,
                                left=-35,
                                top=15,
                                resolution=self.grid.resolution)
                      )
    def photon_addition(self):
        self.add_rect(layer=('PHOTON', 'drawing'),
                      bbox=BBox(right=35,
                                bottom=-15,
                                left=-35,
                                top=15,
                                resolution=self.grid.resolution)
                      )

    def draw_rib_wg_ring1(self):
        """
        Draws core and slab rings of the first ring rib waveguide for dual ring Oo  (ring O)structure
        """
        # Draw outer portion of core
        core_outer = self.add_round(
            layer=self.core_layer,
            resolution=self.grid.resolution,
            rout=self.r_core_cent + self.core_width / 2,
            rin=self.r_core_cent + self.core_slot_width / 2,
            center=(self.ring_loc[0]-(self.r_r_gap+self.core_width )-2*self.r_core_cent,self.ring_loc[1]))
        self.add_obj(core_outer)

        # Draw inner portion of core
        core_inner = self.add_round(
            layer=self.core_layer,
            resolution=self.grid.resolution,
            rin=self.r_core_cent - self.core_width / 2,
            rout=self.r_core_cent - self.core_slot_width / 2,
            center=(self.ring_loc[0]-(self.r_r_gap+self.core_width )-2*self.r_core_cent,self.ring_loc[1]))
        self.add_obj(core_inner)

        # Draw outer portion of slab
        slab_outer = self.add_round(
            layer=self.slab_layer,
            resolution=self.grid.resolution,
            rout=self.r_core_cent + self.slab_width / 2,
            rin=self.r_core_cent + self.slab_slot_width / 2,
            center=(self.ring_loc[0]-(self.r_r_gap+self.core_width )-2*self.r_core_cent,self.ring_loc[1]))
        self.add_obj(slab_outer)

        # Draw inner portion of slab
        slab_inner = self.add_round(
            layer=self.slab_layer,
            resolution=self.grid.resolution,
            rin=self.r_core_cent - self.slab_width / 2,
            rout=self.r_core_cent - self.slab_slot_width / 2,
            center=(self.ring_loc[0]-(self.r_r_gap+self.core_width )-2*self.r_core_cent,self.ring_loc[1]))
        self.add_obj(slab_inner)

    def draw_rib_wg_ring2(self):
        """
        Draws core and slab rings of the second rib waveguide of dual oO ring(O) structure
        """
        # Draw outer portion of core
        # Draw outer portion of core
        core_outer = self.add_round(
            layer=self.core_layer,
            resolution=self.grid.resolution,
            rout=self.r_core_cent + self.core_width / 2,
            rin=self.r_core_cent + self.core_slot_width / 2,
            center=(self.ring_loc[0]+(self.r_r_gap+self.core_width )+2*self.r_core_cent,self.ring_loc[1]))
        self.add_obj(core_outer)

        # Draw inner portion of core
        core_inner = self.add_round(
            layer=self.core_layer,
            resolution=self.grid.resolution,
            rin=self.r_core_cent - self.core_width / 2,
            rout=self.r_core_cent - self.core_slot_width / 2,
            center=(self.ring_loc[0]+(self.r_r_gap+self.core_width )+2*self.r_core_cent,self.ring_loc[1]))
        self.add_obj(core_inner)

        # Draw outer portion of slab
        slab_outer = self.add_round(
            layer=self.slab_layer,
            resolution=self.grid.resolution,
            rout=self.r_core_cent + self.slab_width / 2,
            rin=self.r_core_cent + self.slab_slot_width / 2,
            center=(self.ring_loc[0]+(self.r_r_gap+self.core_width )+2*self.r_core_cent,self.ring_loc[1]))
        self.add_obj(slab_outer)

        # Draw inner portion of slab
        slab_inner = self.add_round(
            layer=self.slab_layer,
            resolution=self.grid.resolution,
            rin=self.r_core_cent - self.slab_width / 2,
            rout=self.r_core_cent - self.slab_slot_width / 2,
            center=(self.ring_loc[0]+(self.r_r_gap+self.core_width )+ 2*self.r_core_cent,self.ring_loc[1]))
        self.add_obj(slab_inner)

    def draw_rib_wg_ring3(self):
        """
        Draws core and slab rings of the second rib waveguide of dual oO ring(O) structure
        """
        # Draw outer portion of core
        # Draw outer portion of core
        core_outer = self.add_round(
            layer=self.core_layer,
            resolution=self.grid.resolution,
            rout=self.r_core_cent + self.core_width / 2,
            rin=self.r_core_cent + self.core_slot_width / 2,
            center=(self.ring_loc[0],self.ring_loc[1]))
        self.add_obj(core_outer)

        # Draw inner portion of core
        core_inner = self.add_round(
            layer=self.core_layer,
            resolution=self.grid.resolution,
            rin=self.r_core_cent - self.core_width / 2,
            rout=self.r_core_cent - self.core_slot_width / 2,
            center=(self.ring_loc[0],self.ring_loc[1]))
        self.add_obj(core_inner)

        # Draw outer portion of slab
        slab_outer = self.add_round(
            layer=self.slab_layer,
            resolution=self.grid.resolution,
            rout=self.r_core_cent + self.slab_width / 2,
            rin=self.r_core_cent + self.slab_slot_width / 2,
            center=(self.ring_loc[0],self.ring_loc[1]))
        self.add_obj(slab_outer)

        # Draw inner portion of slab
        slab_inner = self.add_round(
            layer=self.slab_layer,
            resolution=self.grid.resolution,
            rin=self.r_core_cent - self.slab_width / 2,
            rout=self.r_core_cent - self.slab_slot_width / 2,
            center=(self.ring_loc[0],self.ring_loc[1]))
        self.add_obj(slab_inner)

    def place_contact_electrodes_basic(self):
        # calculate the corner coordinate of the left (ground) pad
        # calculate the corner coordinate of the left (ground) pad
        dim1 = 11.7
        dim2 = dim1  # 10.722 + 6.72 - 5.812
        self.left_pad_loc = (self.ring_loc[0] - (self.gs_pad_pitch),
                             self.ring_loc[1] - self.gs_pad_to_ring_dist
                             )
        self.central_pad_loc = (self.ring_loc[0],
                                self.ring_loc[1] - self.gs_pad_to_ring_dist
                                )
        # calculate the corner coordinate of the right (signal) pad
        self.right_pad_loc = (self.ring_loc[0] + (self.gs_pad_pitch),
                              self.ring_loc[1] - self.gs_pad_to_ring_dist
                              )
        offset_distance = self.outer_electrode_info1[-1]['dist0']

        # # draw vertical ground wire
        # self.add_rect(layer=self.inner_electrode_info[-1]['layer'],
        #               bbox=BBox(right=self.ring_loc[0],
        #                         bottom=self.left_pad_loc[1] - self.gs_bottom_width,
        #                         left=self.ring_loc[0] - self.gs_bottom_width,
        #                         top=self.ring_loc[1] - self.r_core_cent - self.inner_electrode_info[-1]['dist1'],
        #                         resolution=self.grid.resolution)
        #               )

        # draw left pad wiring
        width=2
        wire1_top = self.ring_loc[1]
        wire1_bottom = wire1_top - width
        wire1_left = -32
        wire1_right = self.ring_loc[0] - (self.r_r_gap/2+self.core_width ) - 2* self.r_core_cent-offset_distance -(self.r_r_gap/2+self.core_width/2 )- self.r_core_cent
        self.add_rect(layer=self.outer_electrode_info1[-1]['layer'],
                      bbox=BBox(right=wire1_right,
                                bottom=wire1_bottom,
                                left=wire1_left,
                                top=wire1_top,
                                resolution=self.grid.resolution)
                      )









        # draw right pad wire
        wire1_top = self.ring_loc[1]
        wire1_bottom = wire1_top - width
        wire1_left = self.ring_loc[0] + (self.r_r_gap/2+self.core_width ) + 2* self.r_core_cent+offset_distance +(self.r_r_gap/2+self.core_width/2 )+self.r_core_cent
        wire1_right = 32
        self.add_rect(layer=self.outer_electrode_info1[-1]['layer'],
                      bbox=BBox(right=wire1_right,
                                bottom=wire1_bottom,
                                left=wire1_left,
                                top=wire1_top,
                                resolution=self.grid.resolution)
                      )



        width=4
        # draw central pad wire(bring from left ring)
        wire1_top = self.ring_loc[1]-self.r_core_cent + offset_distance+1
        wire1_bottom = wire1_top - 6*offset_distance
        wire1_left = self.ring_loc[0] -(self.r_r_gap / 2 + self.core_width) - self.r_core_cent + offset_distance -(self.r_r_gap/2+self.core_width/2 )-self.r_core_cent-2
        wire1_right = wire1_left+ width
        self.add_rect(layer=self.inner_electrode_info1[-1]['layer'],
                      bbox=BBox(right=wire1_right,
                                bottom=wire1_bottom,
                                left=wire1_left,
                                top=wire1_top,
                                resolution=self.grid.resolution)
                      )
        wire2_top = wire1_bottom+width
        wire2_bottom = wire1_bottom
        wire2_left = wire1_left
        wire2_right = 0
        self.add_rect(layer=self.inner_electrode_info1[-1]['layer'],
                      bbox=BBox(right=wire2_right,
                                bottom=wire2_bottom,
                                left=wire2_left,
                                top=wire2_top,
                                resolution=self.grid.resolution)
                      )

        # draw central pad wire(bring from right ring)
        wire1_top = self.ring_loc[1] - self.r_core_cent + offset_distance + 1
        wire1_bottom = wire1_top - 6 * offset_distance
        wire1_right = self.ring_loc[0] + (self.r_r_gap / 2 + self.core_width) + self.r_core_cent - offset_distance  +(self.r_r_gap/2+self.core_width/2 )+self.r_core_cent+2
        wire1_left = wire1_right - width
        self.add_rect(layer=self.inner_electrode_info1[-1]['layer'],
                      bbox=BBox(right=wire1_right,
                                bottom=wire1_bottom,
                                left=wire1_left,
                                top=wire1_top,
                                resolution=self.grid.resolution)
                      )
        wire2_top = wire1_bottom + width
        wire2_bottom = wire1_bottom
        wire2_left = 0
        wire2_right = wire1_right
        self.add_rect(layer=self.inner_electrode_info1[-1]['layer'],
                      bbox=BBox(right=wire2_right,
                                bottom=wire2_bottom,
                                left=wire2_left,
                                top=wire2_top,
                                resolution=self.grid.resolution)
                      )
        # vertical wire upto middle pad




        # lower outer metal contact to the level of higher inner metal contact
        via_stack_master = self.new_template(params=dict(top_layer=self.inner_electrode_info1[-1]['layer'],
                                                         bottom_layer=self.outer_electrode_info1[-1]['layer'],
                                                         top_x_span=self.gs_bottom_width,
                                                         top_y_span=self.gs_bottom_length,
                                                         bottom_x_span=self.gs_bottom_width,
                                                         bottom_y_span=self.gs_bottom_length,
                                                         align='center_align',
                                                         top_bot_offset=0.0),
                                             temp_cls=ViaStack)



    def place_heater_contact_electrodes_basic(self):
        # calculate the corner coordinate of the left (ground) pad
        # calculate the corner coordinate of the left (ground) pad
        dim1 = 11.7
        dim2 = dim1  # 10.722 + 6.72 - 5.812
        self.heaterpad1_loc = (
        self.ring_loc[0] - 5 * (self.gs_pad_pitch) / 2, self.ring_loc[1] + self.heater_pad_to_ring_dist)
        self.heaterpad2_loc = (
        self.ring_loc[0] - 3 * (self.gs_pad_pitch) / 2, self.ring_loc[1] + self.heater_pad_to_ring_dist)
        self.heaterpad3_loc = (
        self.ring_loc[0] - (self.gs_pad_pitch) / 2, self.ring_loc[1] + self.heater_pad_to_ring_dist)
        self.heaterpad4_loc = (
        self.ring_loc[0] + (self.gs_pad_pitch) / 2, self.ring_loc[1] + self.heater_pad_to_ring_dist)
        self.heaterpad5_loc = (
        self.ring_loc[0] + 3 * (self.gs_pad_pitch) / 2, self.ring_loc[1] + self.heater_pad_to_ring_dist)
        self.heaterpad6_loc = (
        self.ring_loc[0] + 5 * (self.gs_pad_pitch) / 2, self.ring_loc[1] + self.heater_pad_to_ring_dist)
        offset_distance = self.outer_electrode_info1[-1]['dist0']

        # # draw vertical ground wire
        # self.add_rect(layer=self.inner_electrode_info[-1]['layer'],
        #               bbox=BBox(right=self.ring_loc[0],
        #                         bottom=self.left_pad_loc[1] - self.gs_bottom_width,
        #                         left=self.ring_loc[0] - self.gs_bottom_width,
        #                         top=self.ring_loc[1] - self.r_core_cent - self.inner_electrode_info[-1]['dist1'],
        #                         resolution=self.grid.resolution)
        #               )

        # heater wiring maximum metal width

        metal_width=4


        # heater wiring to the left upper pad
        wire1_top = 18*offset_distance
        wire1_bottom = -self.heater_electrode_top_y_span/2-0.55
        wire1_left = -self.contact_dist/2 -(self.r_r_gap+self.core_width )-2*self.r_core_cent - metal_width
        wire1_right = wire1_left+ metal_width
        self.add_rect(layer=self.heater_electrode_top_layer,
                      bbox=BBox(right=wire1_right,
                                bottom=wire1_bottom,
                                left=wire1_left,
                                top=wire1_top,
                                resolution=self.grid.resolution)
                      )




        # heater wiring to the left upper pad
        wire1_top = 18 * offset_distance
        wire1_bottom = -self.heater_electrode_top_y_span/2-0.55
        wire1_left = self.contact_dist / 2 - (self.r_r_gap + self.core_width) - 2 * self.r_core_cent
        wire1_right = wire1_left + metal_width
        self.add_rect(layer=self.heater_electrode_top_layer,
                      bbox=BBox(right=wire1_right,
                                bottom=wire1_bottom,
                                left=wire1_left,
                                top=wire1_top,
                                resolution=self.grid.resolution)
                      )



        # heater wiring to the left upper pad
        wire1_top = 18 * offset_distance
        wire1_bottom = -self.heater_electrode_top_y_span/2-0.55
        wire1_left = -self.contact_dist / 2 - metal_width
        wire1_right = wire1_left + metal_width
        self.add_rect(layer=self.heater_electrode_top_layer,
                      bbox=BBox(right=wire1_right,
                                bottom=wire1_bottom,
                                left=wire1_left,
                                top=wire1_top,
                                resolution=self.grid.resolution)
                      )



        # # heater wiring to the right upper pad
        wire1_top = 18*offset_distance
        wire1_bottom = -self.heater_electrode_top_y_span/2-0.55
        wire1_left = self.contact_dist/2 +(self.r_r_gap+self.core_width )+2*self.r_core_cent
        wire1_right = self.contact_dist/2 +(self.r_r_gap+self.core_width )+2*self.r_core_cent + metal_width
        self.add_rect(layer=self.heater_electrode_top_layer,
                      bbox=BBox(right=wire1_right,
                                bottom=wire1_bottom,
                                left=wire1_left,
                                top=wire1_top,
                                resolution=self.grid.resolution)
                      )




        # # heater wiring to the right upper pad
        wire1_top = 18 * offset_distance
        wire1_bottom = -self.heater_electrode_top_y_span/2-0.55
        wire1_left = -self.contact_dist / 2 + (self.r_r_gap + self.core_width) + 2 * self.r_core_cent - metal_width
        wire1_right = -self.contact_dist / 2 + (self.r_r_gap + self.core_width) + 2 * self.r_core_cent
        self.add_rect(layer=self.heater_electrode_top_layer,
                      bbox=BBox(right=wire1_right,
                                bottom=wire1_bottom,
                                left=wire1_left,
                                top=wire1_top,
                                resolution=self.grid.resolution)
                      )



        # # heater wiring to the right upper pad
        wire1_top = 18 * offset_distance
        wire1_bottom = -self.heater_electrode_top_y_span/2-0.55
        wire1_left = self.contact_dist / 2
        wire1_right = self.contact_dist / 2  + metal_width
        self.add_rect(layer=self.heater_electrode_top_layer,
                      bbox=BBox(right=wire1_right,
                                bottom=wire1_bottom,
                                left=wire1_left,
                                top=wire1_top,
                                resolution=self.grid.resolution)
                      )

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
            loc = (self.ring_loc[0] - core_master.arc_list[-1]['x'][-1] / 2 -(self.r_r_gap+self.core_width )-2*self.r_core_cent,
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
            port_renaming={'PORT_IN': 'PORT0',
                           'PORT_OUT': 'PORT1'},
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








        # find the location of bent coupler
        loc = (self.ring_loc[0] - core_master.arc_list[-1]['x'][-1] / 2 -(self.r_r_gap+self.core_width )-2*self.r_core_cent,
               self.ring_loc[1] - max(core_master.arc_list[3]['y']) -
               self.r_core_cent - self.coup_gap - (self.core_width + self.coup_core_width) / 2 - (
               self.core_width + self.coup_core_width) / 2 - self.coup_gap - 0.8)

        # update the coupler parameters with slab parameters
        coup_params['layer'] = ('KG', 'drawing')
        coup_params['arc_params'][0]['w_coupling'] = 0.6
        coup_params['arc_params'][0]['w_in'] = 0.6

        # bent coupler slab master
        coup_slab_master = self.new_template(params=coup_params,
                                             temp_cls=AdiabaticPaths)

        # place the coupler slab to the north of the ring
        self.add_instance(
            master=coup_slab_master,
            inst_name='input_wg',
            loc=loc
        )

        loc = (self.ring_loc[0] - core_master.arc_list[-1]['x'][-1] / 2 -(self.r_r_gap+self.core_width )-2*self.r_core_cent,
               self.ring_loc[1] - max(core_master.arc_list[3]['y']) -
               self.r_core_cent - self.coup_gap - (self.core_width + self.coup_core_width) / 2 + (
                   self.core_width + self.coup_core_width) / 2 + self.coup_gap + 0.8)
        # place the coupler slab to the north of the ring
        self.add_instance(
            master=coup_slab_master,
            inst_name='input_wg',
            loc=loc
        )






        # attach input output tapers
        if self.in_out_taper:
            self.create_in_out_taper()
            taper_in = self.add_instance_port_to_port(inst_master=self.taper_master,
                                                      instance_port_name='PORT1',
                                                      self_port_name='PORT0',
                                                      reflect=False)

            # what i can do is, get the port object, change its position, delete the previous port from self, then add the new port... damn
            # self._photonic_ports['PORT0'].x = 10

            # pdb.set_trace()

            # port1 = self.get_photonic_port('PORT1')
            # self.add_photonic_port( name = 'PORT1',
            #                         center = [port1.x - 0.04, port1.y],
            #                         # orient = port1.orientation,
            #                         orient = 'R0',
            #                         angle = port1.angle,
            #                         width = port1.width,
            #                         layer = port1.layer,
            #                         overwrite = True,
            #                         show = False
            #                         )

            # def add_photonic_port(self,
            #               name: Optional[str] = None,
            #               center: Optional[coord_type] = None,
            #               orient: Optional[str] = None,
            #               angle: Optional[float] = 0.0,
            #               width: Optional[dim_type] = None,
            #               layer: Optional[layer_or_lpp_type] = None,
            #               overwrite_purpose: bool = False,
            #               resolution: Optional[float] = None,
            #               unit_mode: bool = False,
            #               port: Optional[PhotonicPort] = None,
            #               overwrite: bool = False,
            #               show: bool = True
            #               ) -> PhotonicPort:

            # attach input output tapers
            taper_out = self.add_instance_port_to_port(inst_master=self.taper_master,
                                                       instance_port_name='PORT1',
                                                       self_port_name='PORT1',
                                                       reflect=False)
            self.delete_port(['PORT0', 'PORT1'])
            # extract ports from input and output tapers
            self.extract_photonic_ports(
                inst=taper_in,
                port_names='PORT0',
                show=False)

            self.extract_photonic_ports(
                inst=taper_out,
                port_names='PORT0',
                port_renaming={'PORT0': 'PORT1'},
                show=False)


    def draw_input_wg_drop(self):
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
            loc = (self.ring_loc[0] - core_master.arc_list[-1]['x'][-1] / 2 -(self.r_r_gap+self.core_width )-2*self.r_core_cent,
                   self.ring_loc[1] + max(core_master.arc_list[3]['y']) + self.r_core_cent + self.coup_gap_drop + (self.core_width + self.coup_core_width) / 2)

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
                   self.ring_loc[1] + self.r_core_cent + self.coup_gap_drop + (self.core_width + self.coup_core_width) / 2)

            # update the coupler parameters with slab parameters
            coup_params['layer'] = self.slab_layer
            coup_params['arc_params'][0]['width'] = self.slab_width

        # place the coupler core to the north of the ring
        coup_core = self.add_instance(
            master=core_master,
            inst_name='input_wg',
            loc=loc,
            orient='MX',
            )

        # Extract and rename the ports of coupler waveguide
        self.extract_photonic_ports(
            inst=coup_core,
            port_names=['PORT_IN', 'PORT_OUT'],
            port_renaming={'PORT_IN': 'PORT0',
                           'PORT_OUT': 'PORT1'},
            show=False)

        # bent coupler slab master
        coup_slab_master = self.new_template(params=coup_params,
                                             temp_cls=AdiabaticPaths)

        # place the coupler slab to the north of the ring
        self.add_instance(
            master=coup_slab_master,
            inst_name='input_wg',
            loc=loc,
            orient='MX',
        )

        # attach input output tapers
        if self.in_out_taper:
            self.create_in_out_taper()
            taper_in = self.add_instance_port_to_port(inst_master=self.taper_master,
                                                      instance_port_name='PORT1',
                                                      self_port_name='PORT0',
                                                      reflect=False)

            # what i can do is, get the port object, change its position, delete the previous port from self, then add the new port... damn
            # self._photonic_ports['PORT0'].x = 10

            # pdb.set_trace()

            # port1 = self.get_photonic_port('PORT1')
            # self.add_photonic_port( name = 'PORT1',
            #                         center = [port1.x - 0.04, port1.y],
            #                         # orient = port1.orientation,
            #                         orient = 'R0',
            #                         angle = port1.angle,
            #                         width = port1.width,
            #                         layer = port1.layer,
            #                         overwrite = True,
            #                         show = False
            #                         )

            # def add_photonic_port(self,
            #               name: Optional[str] = None,
            #               center: Optional[coord_type] = None,
            #               orient: Optional[str] = None,
            #               angle: Optional[float] = 0.0,
            #               width: Optional[dim_type] = None,
            #               layer: Optional[layer_or_lpp_type] = None,
            #               overwrite_purpose: bool = False,
            #               resolution: Optional[float] = None,
            #               unit_mode: bool = False,
            #               port: Optional[PhotonicPort] = None,
            #               overwrite: bool = False,
            #               show: bool = True
            #               ) -> PhotonicPort:

            # attach input output tapers
            taper_out = self.add_instance_port_to_port(inst_master=self.taper_master,
                                                       instance_port_name='PORT1',
                                                       self_port_name='PORT1',
                                                       reflect=False)
            self.delete_port(['PORT0', 'PORT1'])
            # extract ports from input and output tapers
            self.extract_photonic_ports(
                inst=taper_in,
                port_names='PORT0',
                show=False)

            self.extract_photonic_ports(
                inst=taper_out,
                port_names='PORT0',
                port_renaming={'PORT0': 'PORT1'},
                show=False)

    def draw_heater(self):
        heater_params = dict(
            rout=(self.params['r_core_cent'] - self.params['slab_width']/2 -0.3-1.2
                  ),

            resistance=self.params['resistance'],
            contact_dist=self.params['contact_dist'],
            contact_width=self.params['contact_width'],
            device_layer=self.params['heater_device_layer'],
            disk_layers=self.params['heater_disk_layers'],
            electrode_top_layer=self.params['heater_electrode_top_layer'],
            electrode_top_x_span=self.params['heater_electrode_top_x_span'],
            electrode_top_y_span=self.params['heater_electrode_top_y_span'],
            electrode_label=self.params['heater_label'],
            disk_layer_extension=self.params['heater_disk_layer_extension'],
            electrode_bottom_layer=self.params['heater_electrode_bottom_layer'],
        )
        # Assign dynamic defaults to heater electrode bottom span
        if self.params['heater_electrode_bottom_x_span'] is None:
            heater_params['electrode_bottom_x_span'] = heater_params['contact_width']
        else:

            heater_params['electrode_bottom_x_span'] = self.params['heater_electrode_bottom_x_span']
        if self.params['heater_electrode_bottom_y_span'] is None:
            heater_params['electrode_bottom_y_span'] = heater_params['contact_width']
        else:
            heater_params['electrode_bottom_y_span'] = self.params['heater_electrode_bottom_y_span']

        # Add ring instance
        #ring_master = self.new_template(params=ring_params, temp_cls=RingBase)
        #ring_inst = self.add_instance(master=ring_master)

        # Add the heater if it should be present
        if not self.params['heater_disable']:
            # Compute the width from the heater resistance design function
            # heater_params['width'] = RingHeater.design_heater_width_from_resistance(resistance=heater_params['resistance'],heater_rout=heater_params['rout'],r_square=self.photonic_tech_info.sheet_resistance(heater_params['device_layer']),contact_width=heater_params['contact_width'],contact_dist=heater_params['contact_dist'],)
            heater_params['width'] = 1.6
            #heater_ring_Addition
            heater_master = self.new_template(params=heater_params, temp_cls=RingHeater)
            self.add_instance(master=heater_master,loc=(self.ring_loc[0] + (self.r_r_gap+self.core_width ) + 2*self.r_core_cent, self.ring_loc[1]))
            heater_master = self.new_template(params=heater_params, temp_cls=RingHeater)
            self.add_instance(master=heater_master, loc=(self.ring_loc[0] - (self.r_r_gap  + self.core_width ) - 2*self.r_core_cent, self.ring_loc[1]))
            heater_master = self.new_template(params=heater_params, temp_cls=RingHeater)
            self.add_instance(master=heater_master, loc=(self.ring_loc[0] , self.ring_loc[1]))

    def draw_concentric_rings1(self, ring_info):
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
                center=(self.ring_loc[0]-(self.r_r_gap+self.core_width )-2*self.r_core_cent,self.ring_loc[1])
            )
            self.add_obj(ring)

    def draw_concentric_rings2(self, ring_info):
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
                center=(self.ring_loc[0] +(self.r_r_gap+self.core_width ) + 2*self.r_core_cent, self.ring_loc[1])
            )
            self.add_obj(ring)

    def draw_concentric_rings3(self, ring_info):
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
                center=(self.ring_loc[0], self.ring_loc[1])
            )
            self.add_obj(ring)

    def place_circular_via_stack1(self):
        """
        Draws azimuthally placed via stacks
        """
        for count in range(len(self.via_info1)):
            # calculate angular step from azimuthal distance
            angle_step = (180 / np.pi) * self.via_info1[count]['azim_dist'] / \
                         (self.r_core_cent + self.via_info1[count]['dist'])

            # calculate the number of vias
            via_num = int((self.via_info1[count]['angle1'] - self.via_info1[count]['angle0']) // angle_step)

            # instantiate via stacks
            for via_count in range(via_num):
                delta_phi = np.pi * angle_step / 180
                phi = np.pi * self.via_info1[count]['angle0'] / 180 + via_count * delta_phi
                self.add_via_stack(
                    bot_layer=self.via_info1[count]['layer_bottom'],
                    top_layer=self.via_info1[count]['layer_top'],
                    loc=(self.ring_loc[0] + (self.r_core_cent + self.via_info1[count]['dist']) * np.cos(phi)-(self.r_r_gap+self.core_width )-2*self.r_core_cent,
                         self.ring_loc[1] + (self.r_core_cent + self.via_info1[count]['dist']) * np.sin(phi))
                )

    def place_circular_via_stack2(self):
        """
        Draws azimuthally placed via stacks
        """
        for count in range(len(self.via_info2)):
            # calculate angular step from azimuthal distance
            angle_step = (180 / np.pi) * self.via_info2[count]['azim_dist'] / \
                         (self.r_core_cent + self.via_info2[count]['dist'])

            # calculate the number of vias
            via_num = int((self.via_info2[count]['angle1'] - self.via_info2[count]['angle0']) // angle_step)

            # instantiate via stacks
            for via_count in range(via_num):
                delta_phi = np.pi * angle_step / 180
                phi = np.pi * self.via_info2[count]['angle0'] / 180 + via_count * delta_phi
                self.add_via_stack(
                    bot_layer=self.via_info2[count]['layer_bottom'],
                    top_layer=self.via_info2[count]['layer_top'],
                    loc=(self.ring_loc[0]  + (self.r_r_gap+self.core_width ) + 2*self.r_core_cent + (self.r_core_cent + self.via_info2[count]['dist']) * np.cos(phi),
                         self.ring_loc[1] + (self.r_core_cent + self.via_info2[count]['dist']) * np.sin(phi))
                )

    def draw_doping_spokes1(self,doping_spoke_info):
        """Draw all the doping spokes"""
        if self.doping_spoke_info1:
            for i, doping_spoke_info in enumerate(self.doping_spoke_info1):
                spoke_master = self.new_template(params=doping_spoke_info, temp_cls=SpokeBase)
                self.add_instance(
                    master=spoke_master,
                    inst_name='doping_spokes_' + str(i),
                    loc=(self.ring_loc[0]-(self.r_r_gap+self.core_width )-2*self.r_core_cent,self.ring_loc[1]),
                    orient="R0",
                    unit_mode=False,
                )
    def draw_doping_spokes2(self,doping_spoke_info):
        """Draw all the doping spokes"""
        if self.doping_spoke_info2:
            for i, doping_spoke_info in enumerate(self.doping_spoke_info2):
                spoke_master = self.new_template(params=doping_spoke_info, temp_cls=SpokeBase)
                self.add_instance(
                    master=spoke_master,
                    inst_name='doping_spokes_' + str(i),
                    loc=(self.ring_loc[0] +(self.r_r_gap+self.core_width ) + 2*self.r_core_cent, self.ring_loc[1]),
                    orient="R0",
                    unit_mode=False,
                )

    def place_contact_electrodes(self):
        # calculate the corner coordinate of the left (ground) pad
        # calculate the corner coordinate of the left (ground) pad
        dim1 = 11.7
        dim2 = dim1  # 10.722 + 6.72 - 5.812
        self.left_pad_loc = (self.ring_loc[0] - (self.gs_pad_pitch),
                             self.ring_loc[1] - self.gs_pad_to_ring_dist
                             )
        self.central_pad_loc = (self.ring_loc[0],
                                self.ring_loc[1] - self.gs_pad_to_ring_dist
                                )
        # calculate the corner coordinate of the right (signal) pad
        self.right_pad_loc = (self.ring_loc[0] + (self.gs_pad_pitch),
                              self.ring_loc[1] - self.gs_pad_to_ring_dist
                              )
        offset_distance = self.outer_electrode_info1[-1]['dist0']

        # # draw vertical ground wire
        # self.add_rect(layer=self.inner_electrode_info[-1]['layer'],
        #               bbox=BBox(right=self.ring_loc[0],
        #                         bottom=self.left_pad_loc[1] - self.gs_bottom_width,
        #                         left=self.ring_loc[0] - self.gs_bottom_width,
        #                         top=self.ring_loc[1] - self.r_core_cent - self.inner_electrode_info[-1]['dist1'],
        #                         resolution=self.grid.resolution)
        #               )

        # draw left pad wiring
        width = 2
        wire1_top = self.ring_loc[1]
        wire1_bottom = wire1_top - width
        wire1_left = self.left_pad_loc[0]
        wire1_right = self.ring_loc[0] - (
        self.r_r_gap / 2 + self.core_width) - 2 * self.r_core_cent - offset_distance - (
                      self.r_r_gap / 2 + self.core_width / 2) - self.r_core_cent
        self.add_rect(layer=self.outer_electrode_info1[-1]['layer'],
                      bbox=BBox(right=wire1_right,
                                bottom=wire1_bottom,
                                left=wire1_left,
                                top=wire1_top,
                                resolution=self.grid.resolution)
                      )

        wire2_top = wire1_top
        wire2_bottom = self.left_pad_loc[1] - dim1 / 2
        wire2_left = self.left_pad_loc[0]
        wire2_right = wire2_left + width
        self.add_rect(layer=self.outer_electrode_info1[-1]['layer'],
                      bbox=BBox(right=wire2_right,
                                bottom=wire2_bottom,
                                left=wire2_left,
                                top=wire2_top,
                                resolution=self.grid.resolution)
                      )

        # draw right pad wire
        wire1_top = self.ring_loc[1]
        wire1_bottom = wire1_top - width
        wire1_left = self.ring_loc[0] + (
        self.r_r_gap / 2 + self.core_width) + 2 * self.r_core_cent + offset_distance + (
                     self.r_r_gap / 2 + self.core_width / 2) + self.r_core_cent
        wire1_right = self.right_pad_loc[0]
        self.add_rect(layer=self.outer_electrode_info1[-1]['layer'],
                      bbox=BBox(right=wire1_right,
                                bottom=wire1_bottom,
                                left=wire1_left,
                                top=wire1_top,
                                resolution=self.grid.resolution)
                      )

        wire2_top = wire1_top
        wire2_bottom = self.right_pad_loc[1] - dim1 / 2
        wire2_left = self.right_pad_loc[0] - width
        wire2_right = self.right_pad_loc[0]
        self.add_rect(layer=self.outer_electrode_info1[-1]['layer'],
                      bbox=BBox(right=wire2_right,
                                bottom=wire2_bottom,
                                left=wire2_left,
                                top=wire2_top,
                                resolution=self.grid.resolution)
                      )
        width = 4
        # draw central pad wire(bring from left ring)
        wire1_top = self.ring_loc[1] - self.r_core_cent + offset_distance + 1
        wire1_bottom = wire1_top - 6 * offset_distance
        wire1_left = self.ring_loc[0] - (self.r_r_gap / 2 + self.core_width) - self.r_core_cent + offset_distance - (
        self.r_r_gap / 2 + self.core_width / 2) - self.r_core_cent - 2
        wire1_right = wire1_left + width
        self.add_rect(layer=self.inner_electrode_info1[-1]['layer'],
                      bbox=BBox(right=wire1_right,
                                bottom=wire1_bottom,
                                left=wire1_left,
                                top=wire1_top,
                                resolution=self.grid.resolution)
                      )
        wire2_top = wire1_bottom + width
        wire2_bottom = wire1_bottom
        wire2_left = wire1_left
        wire2_right = 0
        self.add_rect(layer=self.inner_electrode_info1[-1]['layer'],
                      bbox=BBox(right=wire2_right,
                                bottom=wire2_bottom,
                                left=wire2_left,
                                top=wire2_top,
                                resolution=self.grid.resolution)
                      )

        # draw central pad wire(bring from right ring)
        wire1_top = self.ring_loc[1] - self.r_core_cent + offset_distance + 1
        wire1_bottom = wire1_top - 6 * offset_distance
        wire1_right = self.ring_loc[0] + (self.r_r_gap / 2 + self.core_width) + self.r_core_cent - offset_distance + (
        self.r_r_gap / 2 + self.core_width / 2) + self.r_core_cent + 2
        wire1_left = wire1_right - width
        self.add_rect(layer=self.inner_electrode_info1[-1]['layer'],
                      bbox=BBox(right=wire1_right,
                                bottom=wire1_bottom,
                                left=wire1_left,
                                top=wire1_top,
                                resolution=self.grid.resolution)
                      )
        wire2_top = wire1_bottom + width
        wire2_bottom = wire1_bottom
        wire2_left = 0
        wire2_right = wire1_right
        self.add_rect(layer=self.inner_electrode_info1[-1]['layer'],
                      bbox=BBox(right=wire2_right,
                                bottom=wire2_bottom,
                                left=wire2_left,
                                top=wire2_top,
                                resolution=self.grid.resolution)
                      )
        # vertical wire upto middle pad
        wire3_top = wire2_bottom
        wire3_bottom = self.central_pad_loc[1] - dim1 / 2
        wire3_right = width / 2
        wire3_left = - width / 2
        self.add_rect(layer=self.inner_electrode_info1[-1]['layer'],
                      bbox=BBox(right=wire3_right,
                                bottom=wire3_bottom,
                                left=wire3_left,
                                top=wire3_top,
                                resolution=self.grid.resolution)
                      )


        # lower outer metal contact to the level of higher inner metal contact
        via_stack_master = self.new_template(params=dict(top_layer=self.inner_electrode_info1[-1]['layer'],
                                                         bottom_layer=self.outer_electrode_info1[-1]['layer'],
                                                         top_x_span=self.gs_bottom_width,
                                                         top_y_span=self.gs_bottom_length,
                                                         bottom_x_span=self.gs_bottom_width,
                                                         bottom_y_span=self.gs_bottom_length,
                                                         align='center_align',
                                                         top_bot_offset=0.0),
                                             temp_cls=ViaStack)

        self.add_instance(master=via_stack_master,
                          inst_name='S_to_G_layer_via_stack',
                          loc=(self.left_pad_loc[0],self.left_pad_loc[1]-dim1/2),
                          orient='R90')
        self.add_instance(master=via_stack_master,
                          inst_name='S_to_G_layer_via_stack',
                          loc=(self.right_pad_loc[0], self.right_pad_loc[1] - dim1 / 2),
                          orient='R90')

    def place_gs_electrodes(self):
        """
        Draws GS electrodes which are connected to ring electrodes
        """
        # Create GS pad
        gs_electrode_master = self.new_template(params=dict(top_layer=self.gs_pad_layer,
                                                            bottom_layer=self.inner_electrode_info1[-1]['layer'],
                                                            top_x_span=10.0,  # self.gs_pad_width,
                                                            top_y_span=self.gs_pad_length,
                                                            bottom_x_span=self.gs_bottom_width,
                                                            bottom_y_span=self.gs_bottom_length,
                                                            align='center_align',
                                                            top_bot_offset=0.0
                                                            # pad_open_layer=self.gs_pad_open_layer,
                                                            # pad_open_inclusion=self.gs_pad_open_inclusion
                                                            ),
                                                temp_cls=ViaStack)
        # TODO: delete below temporary drc fix
        # from here
        # pad DRC error should be fixed now
        dim1 = 11.7
        dim2 = dim1  # 10.722 + 6.72 - 5.812
        # Place left pad open layer and pad llayer exclusion
        self.left_pad_loc = (self.ring_loc[0] - (self.gs_pad_pitch),
                             self.ring_loc[1] - self.gs_pad_to_ring_dist
                             )
        self.central_pad_loc = (self.ring_loc[0],
                                self.ring_loc[1] - self.gs_pad_to_ring_dist
                                )
        # calculate the corner coordinate of the right (signal) pad
        self.right_pad_loc = (self.ring_loc[0] + (self.gs_pad_pitch),
                              self.ring_loc[1] - self.gs_pad_to_ring_dist
                              )
        self.add_rect(layer=self.gs_pad_layer,
                      bbox=BBox(left=self.left_pad_loc[0] - self.gs_pad_width/2 ,
                                bottom=self.left_pad_loc[1] - self.gs_pad_length - dim1,
                                right=self.left_pad_loc[0] + self.gs_pad_width/2,
                                top=self.left_pad_loc[1],
                                resolution=self.grid.resolution)
                      )
        self.add_rect(layer=self.gs_pad_open_layer,
                      bbox=BBox(left=self.left_pad_loc[0] - self.gs_pad_width/2 + self.gs_pad_open_inclusion,
                                bottom=self.left_pad_loc[1] - self.gs_pad_length-dim1 + self.gs_pad_open_inclusion,
                                right=self.left_pad_loc[0] + self.gs_pad_width/2 -self.gs_pad_open_inclusion,
                                top=self.left_pad_loc[1]-dim1-3,
                                resolution=self.grid.resolution)
                      )
        # Place right pad open layer and pad llayer exclusion
        self.add_rect(layer=self.gs_pad_layer,
                      bbox=BBox(left=self.right_pad_loc[0] - self.gs_pad_width/2,
                                bottom=self.right_pad_loc[1] - self.gs_pad_length-dim1,
                                right=self.right_pad_loc[0] + self.gs_pad_width/2 ,
                                top=self.right_pad_loc[1],
                                resolution=self.grid.resolution)
                      )



        self.add_rect(layer=self.gs_pad_open_layer,
                      bbox=BBox(left=self.right_pad_loc[0] - self.gs_pad_width/2 + self.gs_pad_open_inclusion,
                                bottom=self.left_pad_loc[1] - self.gs_pad_length-dim1 + self.gs_pad_open_inclusion,
                                right=self.right_pad_loc[0] + self.gs_pad_width/2 -self.gs_pad_open_inclusion,
                                top=self.left_pad_loc[1]-dim1-3,
                                resolution=self.grid.resolution)
                      )
        # Place central pad open layer and pad llayer exclusion
        self.add_rect(layer=self.gs_pad_layer,
                      bbox=BBox(left=self.central_pad_loc[0] - self.gs_pad_width / 2,
                                bottom=self.central_pad_loc[1] - self.gs_pad_length - dim1,
                                right=self.central_pad_loc[0] + self.gs_pad_width / 2,
                                top=self.central_pad_loc[1],
                                resolution=self.grid.resolution)
                      )

        self.add_rect(layer=self.gs_pad_open_layer,
                      bbox=BBox(left=self.central_pad_loc[0] - self.gs_pad_width / 2 + self.gs_pad_open_inclusion,
                                bottom=self.central_pad_loc[1] - self.gs_pad_length - dim1 + self.gs_pad_open_inclusion,
                                right=self.central_pad_loc[0] + self.gs_pad_width / 2 - self.gs_pad_open_inclusion,
                                top=self.central_pad_loc[1] - dim1-3,
                                resolution=self.grid.resolution)
                      )


        # Place left pad electrode
        self.add_instance(master=gs_electrode_master,
                          inst_name='G_electrode',
                          loc=(self.left_pad_loc[0],self.left_pad_loc[1]-dim1/2),
                          orient='R90')

        # Place right pad electrode
        self.add_instance(master=gs_electrode_master,
                          inst_name='S_electrode',
                          loc=(self.right_pad_loc[0],self.right_pad_loc[1]-dim1/2),
                          orient='R90')
        # Place central pad electrode
        self.add_instance(master=gs_electrode_master,
                          inst_name='G_electrode',
                          loc=(self.central_pad_loc[0], self.central_pad_loc[1]-dim1/2),
                          orient='R90')

    def place_heater_contact_electrodes(self):
        # calculate the corner coordinate of the left (ground) pad
        # calculate the corner coordinate of the left (ground) pad
        dim1 = 11.7
        dim2 = dim1  # 10.722 + 6.72 - 5.812
        self.heaterpad1_loc = (
        self.ring_loc[0] - 5 * (self.gs_pad_pitch) / 2, self.ring_loc[1] + self.heater_pad_to_ring_dist)
        self.heaterpad2_loc = (
        self.ring_loc[0] - 3 * (self.gs_pad_pitch) / 2, self.ring_loc[1] + self.heater_pad_to_ring_dist)
        self.heaterpad3_loc = (
        self.ring_loc[0] - (self.gs_pad_pitch) / 2, self.ring_loc[1] + self.heater_pad_to_ring_dist)
        self.heaterpad4_loc = (
        self.ring_loc[0] + (self.gs_pad_pitch) / 2, self.ring_loc[1] + self.heater_pad_to_ring_dist)
        self.heaterpad5_loc = (
        self.ring_loc[0] + 3 * (self.gs_pad_pitch) / 2, self.ring_loc[1] + self.heater_pad_to_ring_dist)
        self.heaterpad6_loc = (
        self.ring_loc[0] + 5 * (self.gs_pad_pitch) / 2, self.ring_loc[1] + self.heater_pad_to_ring_dist)
        offset_distance = self.outer_electrode_info1[-1]['dist0']

        # # draw vertical ground wire
        # self.add_rect(layer=self.inner_electrode_info[-1]['layer'],
        #               bbox=BBox(right=self.ring_loc[0],
        #                         bottom=self.left_pad_loc[1] - self.gs_bottom_width,
        #                         left=self.ring_loc[0] - self.gs_bottom_width,
        #                         top=self.ring_loc[1] - self.r_core_cent - self.inner_electrode_info[-1]['dist1'],
        #                         resolution=self.grid.resolution)
        #               )

        # heater wiring maximum metal width

        metal_width = 4

        # heater wiring to the left upper pad
        wire1_top = 6 * offset_distance
        wire1_bottom = -self.heater_electrode_top_y_span / 2
        wire1_left = -self.contact_dist / 2 - (self.r_r_gap + self.core_width) - 2 * self.r_core_cent - metal_width
        wire1_right = wire1_left + metal_width
        self.add_rect(layer=self.heater_electrode_top_layer,
                      bbox=BBox(right=wire1_right,
                                bottom=wire1_bottom,
                                left=wire1_left,
                                top=wire1_top,
                                resolution=self.grid.resolution)
                      )

        wire2_top = wire1_top
        wire2_bottom = wire2_top - metal_width
        wire2_left = self.heaterpad1_loc[0]
        wire2_right = wire1_right
        self.add_rect(layer=self.heater_electrode_top_layer,
                      bbox=BBox(right=wire2_right,
                                bottom=wire2_bottom,
                                left=wire2_left,
                                top=wire2_top,
                                resolution=self.grid.resolution)
                      )

        wire3_top = self.heaterpad1_loc[1] + dim1 / 2
        wire3_bottom = wire2_bottom
        wire3_left = wire2_left
        wire3_right = wire2_left + metal_width
        self.add_rect(layer=self.heater_electrode_top_layer,
                      bbox=BBox(right=wire3_right,
                                bottom=wire3_bottom,
                                left=wire3_left,
                                top=wire3_top,
                                resolution=self.grid.resolution)
                      )

        # heater wiring to the left upper pad
        wire1_top = 12 * offset_distance
        wire1_bottom = -self.heater_electrode_top_y_span / 2
        wire1_left = self.contact_dist / 2 - (self.r_r_gap + self.core_width) - 2 * self.r_core_cent
        wire1_right = wire1_left + metal_width
        self.add_rect(layer=self.heater_electrode_top_layer,
                      bbox=BBox(right=wire1_right,
                                bottom=wire1_bottom,
                                left=wire1_left,
                                top=wire1_top,
                                resolution=self.grid.resolution)
                      )

        wire2_top = wire1_top
        wire2_bottom = wire2_top - metal_width
        wire2_left = self.heaterpad2_loc[0]
        wire2_right = wire1_right
        self.add_rect(layer=self.heater_electrode_top_layer,
                      bbox=BBox(right=wire2_right,
                                bottom=wire2_bottom,
                                left=wire2_left,
                                top=wire2_top,
                                resolution=self.grid.resolution)
                      )

        wire3_top = self.heaterpad1_loc[1] + dim1 / 2
        wire3_bottom = wire2_bottom
        wire3_left = wire2_left
        wire3_right = wire2_left + metal_width
        self.add_rect(layer=self.heater_electrode_top_layer,
                      bbox=BBox(right=wire3_right,
                                bottom=wire3_bottom,
                                left=wire3_left,
                                top=wire3_top,
                                resolution=self.grid.resolution)
                      )

        # heater wiring to the left upper pad
        wire1_top = 18 * offset_distance
        wire1_bottom = -self.heater_electrode_top_y_span / 2
        wire1_left = -self.contact_dist / 2 - metal_width
        wire1_right = wire1_left + metal_width
        self.add_rect(layer=self.heater_electrode_top_layer,
                      bbox=BBox(right=wire1_right,
                                bottom=wire1_bottom,
                                left=wire1_left,
                                top=wire1_top,
                                resolution=self.grid.resolution)
                      )

        wire2_top = wire1_top
        wire2_bottom = wire2_top - metal_width
        wire2_left = self.heaterpad3_loc[0]
        wire2_right = wire1_right
        self.add_rect(layer=self.heater_electrode_top_layer,
                      bbox=BBox(right=wire2_right,
                                bottom=wire2_bottom,
                                left=wire2_left,
                                top=wire2_top,
                                resolution=self.grid.resolution)
                      )

        wire3_top = self.heaterpad1_loc[1] + dim1 / 2
        wire3_bottom = wire2_bottom
        wire3_left = wire2_left
        wire3_right = wire2_left + metal_width
        self.add_rect(layer=self.heater_electrode_top_layer,
                      bbox=BBox(right=wire3_right,
                                bottom=wire3_bottom,
                                left=wire3_left,
                                top=wire3_top,
                                resolution=self.grid.resolution)
                      )

        # # heater wiring to the right upper pad
        wire1_top = 6 * offset_distance
        wire1_bottom = -self.heater_electrode_top_y_span / 2
        wire1_left = self.contact_dist / 2 + (self.r_r_gap + self.core_width) + 2 * self.r_core_cent
        wire1_right = self.contact_dist / 2 + (self.r_r_gap + self.core_width) + 2 * self.r_core_cent + metal_width
        self.add_rect(layer=self.heater_electrode_top_layer,
                      bbox=BBox(right=wire1_right,
                                bottom=wire1_bottom,
                                left=wire1_left,
                                top=wire1_top,
                                resolution=self.grid.resolution)
                      )

        wire2_top = wire1_top
        wire2_bottom = wire1_top - metal_width
        wire2_left = wire1_left
        wire2_right = self.heaterpad6_loc[0]
        self.add_rect(layer=self.heater_electrode_top_layer,
                      bbox=BBox(right=wire2_right,
                                bottom=wire2_bottom,
                                left=wire2_left,
                                top=wire2_top,
                                resolution=self.grid.resolution)
                      )

        wire3_top = self.heaterpad6_loc[1] + dim1 / 2
        wire3_bottom = wire2_bottom
        wire3_left = wire2_right - metal_width
        wire3_right = wire2_right
        self.add_rect(layer=self.heater_electrode_top_layer,
                      bbox=BBox(right=wire3_right,
                                bottom=wire3_bottom,
                                left=wire3_left,
                                top=wire3_top,
                                resolution=self.grid.resolution)
                      )

        # # heater wiring to the right upper pad
        wire1_top = 12 * offset_distance
        wire1_bottom = -self.heater_electrode_top_y_span / 2
        wire1_left = -self.contact_dist / 2 + (self.r_r_gap + self.core_width) + 2 * self.r_core_cent - metal_width
        wire1_right = -self.contact_dist / 2 + (self.r_r_gap + self.core_width) + 2 * self.r_core_cent
        self.add_rect(layer=self.heater_electrode_top_layer,
                      bbox=BBox(right=wire1_right,
                                bottom=wire1_bottom,
                                left=wire1_left,
                                top=wire1_top,
                                resolution=self.grid.resolution)
                      )

        wire2_top = wire1_top
        wire2_bottom = wire1_top - metal_width
        wire2_left = wire1_left
        wire2_right = self.heaterpad5_loc[0]
        self.add_rect(layer=self.heater_electrode_top_layer,
                      bbox=BBox(right=wire2_right,
                                bottom=wire2_bottom,
                                left=wire2_left,
                                top=wire2_top,
                                resolution=self.grid.resolution)
                      )

        wire3_top = self.heaterpad5_loc[1] + dim1 / 2
        wire3_bottom = wire2_bottom
        wire3_left = wire2_right - metal_width
        wire3_right = wire2_right
        self.add_rect(layer=self.heater_electrode_top_layer,
                      bbox=BBox(right=wire3_right,
                                bottom=wire3_bottom,
                                left=wire3_left,
                                top=wire3_top,
                                resolution=self.grid.resolution)
                      )

        # # heater wiring to the right upper pad
        wire1_top = 18 * offset_distance
        wire1_bottom = -self.heater_electrode_top_y_span / 2
        wire1_left = self.contact_dist / 2
        wire1_right = self.contact_dist / 2 + metal_width
        self.add_rect(layer=self.heater_electrode_top_layer,
                      bbox=BBox(right=wire1_right,
                                bottom=wire1_bottom,
                                left=wire1_left,
                                top=wire1_top,
                                resolution=self.grid.resolution)
                      )

        wire2_top = wire1_top
        wire2_bottom = wire1_top - metal_width
        wire2_left = wire1_left
        wire2_right = self.heaterpad4_loc[0]
        self.add_rect(layer=self.heater_electrode_top_layer,
                      bbox=BBox(right=wire2_right,
                                bottom=wire2_bottom,
                                left=wire2_left,
                                top=wire2_top,
                                resolution=self.grid.resolution)
                      )

        wire3_top = self.heaterpad4_loc[1] + dim1 / 2
        wire3_bottom = wire2_bottom
        wire3_left = wire2_right - metal_width
        wire3_right = wire2_right
        self.add_rect(layer=self.heater_electrode_top_layer,
                      bbox=BBox(right=wire3_right,
                                bottom=wire3_bottom,
                                left=wire3_left,
                                top=wire3_top,
                                resolution=self.grid.resolution)
                      )
























    def place_heater_gs_electrodes(self):
        """
        Draws GS electrodes which are connected to ring electrodes
        """
        # Create GS pad
        gs_electrode_master = self.new_template(params=dict(top_layer=self.gs_pad_layer,
                                                            bottom_layer=self.inner_electrode_info1[-1]['layer'],
                                                            top_x_span=10.0,  # self.gs_pad_width,
                                                            top_y_span=self.gs_pad_length,
                                                            bottom_x_span=self.gs_bottom_width,
                                                            bottom_y_span=self.gs_bottom_length,
                                                            align='center_align',
                                                            top_bot_offset=0.0
                                                            # pad_open_layer=self.gs_pad_open_layer,
                                                            # pad_open_inclusion=self.gs_pad_open_inclusion
                                                            ),
                                                temp_cls=ViaStack)
        # TODO: delete below temporary drc fix
        # from here
        # pad DRC error should be fixed now
        dim1 = 11.7
        dim2 = dim1  # 10.722 + 6.72 - 5.812
        self.heaterpad1_loc = (self.ring_loc[0] - 5*(self.gs_pad_pitch )/2 ,  self.ring_loc[1] + self.heater_pad_to_ring_dist)
        self.heaterpad2_loc = (self.ring_loc[0] - 3*(self.gs_pad_pitch)/2, self.ring_loc[1] + self.heater_pad_to_ring_dist)
        self.heaterpad3_loc = (self.ring_loc[0] - (self.gs_pad_pitch)/2, self.ring_loc[1] + self.heater_pad_to_ring_dist)
        self.heaterpad4_loc = (self.ring_loc[0] + (self.gs_pad_pitch)/2, self.ring_loc[1] + self.heater_pad_to_ring_dist)
        self.heaterpad5_loc = (self.ring_loc[0] + 3*(self.gs_pad_pitch)/2, self.ring_loc[1] + self.heater_pad_to_ring_dist)
        self.heaterpad6_loc = (self.ring_loc[0] + 5*(self.gs_pad_pitch )/2 ,  self.ring_loc[1] + self.heater_pad_to_ring_dist)

        # Place heater pad 1

        self.add_rect(layer=self.gs_pad_layer,
                      bbox=BBox(left=self.heaterpad1_loc[0] - self.gs_pad_width/2 ,
                                bottom= self.heaterpad1_loc[1]  ,
                                right=self.heaterpad1_loc[0] + self.gs_pad_width/2,
                                top=self.heaterpad1_loc[1] + self.gs_pad_length + dim1,
                                resolution=self.grid.resolution)
                      )
        self.add_rect(layer=self.gs_pad_open_layer,
                      bbox=BBox(left=self.heaterpad1_loc[0] - self.gs_pad_width/2 + self.gs_pad_open_inclusion,
                                bottom= self.heaterpad1_loc[1]+dim1+3,
                                right=self.heaterpad1_loc[0] + self.gs_pad_width/2 -self.gs_pad_open_inclusion,
                                top= self.heaterpad1_loc[1] + self.gs_pad_length+dim1 - self.gs_pad_open_inclusion ,
                                resolution=self.grid.resolution)
                      )

        # Place heater pad 1
        self.add_rect(layer=self.gs_pad_layer,
                      bbox=BBox(left=self.heaterpad2_loc[0] - self.gs_pad_width / 2,
                                bottom=self.heaterpad2_loc[1],
                                right=self.heaterpad2_loc[0] + self.gs_pad_width / 2,
                                top=self.heaterpad2_loc[1] + self.gs_pad_length + dim1,
                                resolution=self.grid.resolution)
                      )

        self.add_rect(layer=self.gs_pad_open_layer,
                      bbox=BBox(left=self.heaterpad2_loc[0] - self.gs_pad_width / 2 + self.gs_pad_open_inclusion,
                                bottom=self.heaterpad2_loc[1] + dim1+3,
                                right=self.heaterpad2_loc[0] + self.gs_pad_width / 2 - self.gs_pad_open_inclusion,
                                top=self.heaterpad2_loc[1] + self.gs_pad_length + dim1 - self.gs_pad_open_inclusion,
                                resolution=self.grid.resolution)
                      )

        # Place heater pad 1
        self.add_rect(layer=self.gs_pad_layer,
                      bbox=BBox(left=self.heaterpad3_loc[0] - self.gs_pad_width / 2,
                                bottom=self.heaterpad3_loc[1],
                                right=self.heaterpad3_loc[0] + self.gs_pad_width / 2,
                                top=self.heaterpad3_loc[1] + self.gs_pad_length + dim1,
                                resolution=self.grid.resolution)
                      )

        self.add_rect(layer=self.gs_pad_open_layer,
                      bbox=BBox(left=self.heaterpad3_loc[0] - self.gs_pad_width / 2 + self.gs_pad_open_inclusion,
                                bottom=self.heaterpad3_loc[1] + dim1+3,
                                right=self.heaterpad3_loc[0] + self.gs_pad_width / 2 - self.gs_pad_open_inclusion,
                                top=self.heaterpad3_loc[1] + self.gs_pad_length + dim1 - self.gs_pad_open_inclusion,
                                resolution=self.grid.resolution)
                      )

        # Place heater pad 1
        self.add_rect(layer=self.gs_pad_layer,
                      bbox=BBox(left=self.heaterpad4_loc[0] - self.gs_pad_width / 2,
                                bottom=self.heaterpad4_loc[1],
                                right=self.heaterpad4_loc[0] + self.gs_pad_width / 2,
                                top=self.heaterpad4_loc[1] + self.gs_pad_length + dim1,
                                resolution=self.grid.resolution)
                      )

        self.add_rect(layer=self.gs_pad_open_layer,
                      bbox=BBox(left=self.heaterpad4_loc[0] - self.gs_pad_width / 2 + self.gs_pad_open_inclusion,
                                bottom=self.heaterpad4_loc[1] + dim1+3,
                                right=self.heaterpad4_loc[0] + self.gs_pad_width / 2 - self.gs_pad_open_inclusion,
                                top=self.heaterpad4_loc[1] + self.gs_pad_length + dim1 - self.gs_pad_open_inclusion,
                                resolution=self.grid.resolution)
                      )
        # Place heater pad 1
        self.add_rect(layer=self.gs_pad_layer,
                      bbox=BBox(left=self.heaterpad5_loc[0] - self.gs_pad_width / 2,
                                bottom=self.heaterpad5_loc[1],
                                right=self.heaterpad5_loc[0] + self.gs_pad_width / 2,
                                top=self.heaterpad5_loc[1] + self.gs_pad_length + dim1,
                                resolution=self.grid.resolution)
                      )

        self.add_rect(layer=self.gs_pad_open_layer,
                      bbox=BBox(left=self.heaterpad5_loc[0] - self.gs_pad_width / 2 + self.gs_pad_open_inclusion,
                                bottom=self.heaterpad5_loc[1] + dim1+3,
                                right=self.heaterpad5_loc[0] + self.gs_pad_width / 2 - self.gs_pad_open_inclusion,
                                top=self.heaterpad5_loc[1] + self.gs_pad_length + dim1 - self.gs_pad_open_inclusion,
                                resolution=self.grid.resolution)
                      )
        # Place heater pad 1
        self.add_rect(layer=self.gs_pad_layer,
                      bbox=BBox(left=self.heaterpad6_loc[0] - self.gs_pad_width/2,
                                bottom= self.heaterpad6_loc[1],
                                right=self.heaterpad6_loc[0] + self.gs_pad_width/2 ,
                                top= self.heaterpad6_loc[1] + self.gs_pad_length+dim1 ,
                                resolution=self.grid.resolution)
                      )



        self.add_rect(layer=self.gs_pad_open_layer,
                      bbox=BBox(left=self.heaterpad6_loc[0] - self.gs_pad_width/2 + self.gs_pad_open_inclusion,
                                bottom= self.heaterpad1_loc[1]+dim1+3,
                                right=self.heaterpad6_loc[0] + self.gs_pad_width/2 -self.gs_pad_open_inclusion,
                                top= self.heaterpad1_loc[1] + self.gs_pad_length+dim1 - self.gs_pad_open_inclusion ,
                                resolution=self.grid.resolution)
                      )


        # Place heater pad 1
        self.add_instance(master=gs_electrode_master,
                          inst_name='G_electrode',
                          loc=(self.heaterpad1_loc[0],self.heaterpad1_loc[1]+dim1/2),
                          orient='R90')
        # Place heater pad 2
        self.add_instance(master=gs_electrode_master,
                          inst_name='G_electrode',
                          loc=(self.heaterpad2_loc[0], self.heaterpad2_loc[1] + dim1 / 2),
                          orient='R90')

        # Place heater pad 3
        self.add_instance(master=gs_electrode_master,
                          inst_name='G_electrode',
                          loc=(self.heaterpad3_loc[0], self.heaterpad3_loc[1] + dim1 / 2),
                          orient='R90')
        # Place heater pad 4
        self.add_instance(master=gs_electrode_master,
                          inst_name='G_electrode',
                          loc=(self.heaterpad4_loc[0], self.heaterpad4_loc[1] + dim1 / 2),
                          orient='R90')
        # Place heater pad 5 electrode
        self.add_instance(master=gs_electrode_master,
                          inst_name='G_electrode',
                          loc=(self.heaterpad5_loc[0], self.heaterpad5_loc[1] + dim1 / 2),
                          orient='R90')

        # Place heater pad 6 electrode
        self.add_instance(master=gs_electrode_master,
                          inst_name='S_electrode',
                          loc=(self.heaterpad6_loc[0],self.heaterpad6_loc[1]+dim1/2),
                          orient='R90')

    def create_in_out_taper(self):

        taper_params = {'width0': self.in_out_port_width,
                        'width1': self.coup_core_width,
                        'width_partial': self.slab_width,  # hack: here this is supposed to be self.coup_slab_width but it is not working , so self.slab_width
                        'length': self.taper_length}
        self.taper_master = self.new_template(params=taper_params,
                                              temp_cls=StripToRibTaper)


if __name__ == '__main__':
    #spec_file = 'Triple_ring_fullrib/specs/full_rib_horizontal_specs.yaml'
    spec_file = 'Triple_ring_fullrib_point_coupler/specs/full_rib_vertical_specs.yaml'
    PLM = BPG.PhotonicLayoutManager(spec_file)
    PLM.generate_content()
    PLM.generate_gds()
   # PLM.generate_flat_content()
    #PLM.generate_flat_gds()
    PLM.dataprep_calibre()