import BPG
import numpy as np
from bag.layout.util import BBox
from Photonic_Core_Layout.ViaStack.ViaStack import ViaStack
from Photonic_Core_Layout.AdiabaticPaths.AdiabaticPaths import AdiabaticPaths
from ..Single_ring_fullrib.ringheater_halfrib_spoked import RingHeater
from ..Dual_ring_halfrib_point_coupler.ring_rib_wg_spoked import RingRibWg
from ..Taper.StripToRibTaper import StripToRibTaper
from ..Spoke.SpokeBase import SpokeBase
from typing import TYPE_CHECKING, List, Union, Optional
from BPG.objects import PhotonicPolygon, PhotonicRound, PhotonicRect
from importlib import import_module


from typing import TYPE_CHECKING, List, Union, Optional
from BPG.objects import PhotonicPolygon, PhotonicRound, PhotonicRect
from ..Single_ring_halfrib_dep.ring_rib_wg import RingRibWg_sr
from ..triple_rings_full_si.Ring_new.wrapped_coupler_tapeout import adiabatic_coupler_cena
from ..triple_rings_full_si.Ring_new.AdiabaticRouter import AdiabaticRouter

class Standalone_and_WDM(BPG.PhotonicTemplateBase):
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
        self.left_heaterpad_loc = None
        self.right_heaterpad_loc = None
        self.central_heaterpad_loc = None
        self.r_r_gap=self.params['r_r_gap']
        # Parameters of rib-waveguide ring
        # --------------------------------
        self.r_core_cent = self.params['r_core_cent']
        self.drop_core_width = 0.35
        self.pad_width = 40
        self.pad_length = 60
        self.pad_open_width = 36
        self.pad_open_length = 52
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
        self.basic_metal_routing = self.params['basic_metal_routing']

        # Parameters of input output tapers
        # ---------------------------------
        self.in_out_taper = self.params['in_out_taper']
        self.in_out_port_width = self.params['in_out_port_width']
        self.taper_length = self.params['taper_length']
        self.taper_layer1 = self.params['taper_layer1']
        # taper_layer1=('si_fullfree', 'drawing'),
        self.taper_layer2 = self.params['taper_layer2']

        # ring_spoked doping info bitches!

        self.doping_spoke_info = self.params['doping_spoke_info']

        # Get additional ring information. Handle no extra rings properly
        self.extra_ring_info = self.params['extra_ring_info']
        self.spoke_num = self.params['spoke_num']
        self.label = self.params['label']

        # Advanced parameters: can change between designs per technology, but not recommended for standard users
        self.p_via_radius_offset = self.params['p_via_radius_offset']
        self.n_via_radius_offset = self.params['n_via_radius_offset']
        self.high_doping_rin_offset = self.params['high_doping_rin_offset']
        self.high_doping_rout_offset = self.params['high_doping_rout_offset']

        self.electrode_offset = self.params['electrode_offset']
        self.electrode_width_inner = self.params['electrode_width_inner']
        self.electrode_width_outer = self.params['electrode_width_outer']
        self.access_length = self.params['access_length']

        self.outer_electrode_ring_layers = self.params['outer_electrode_ring_layers']
        self.inner_electrode_ring_layers = self.params['inner_electrode_ring_layers']

        self.drop_taper_length = self.params['drop_taper_length']
        self.salicide_radius_extension = self.params['salicide_radius_extension']
        self.high_doping_n_rin_offset = self.params['high_doping_n_rin_offset']

        # Advanced tech parameters
        self.high_n_doping_layer = self.params['high_n_doping_layer']
        self.high_p_doping_layer = self.params['high_p_doping_layer']
        self.salicide_lpp = self.params['salicide_lpp']
        self.bottom_metal_electrode_layer = self.params['bottom_metal_electrode_layer']
        self.bottom_electrode_label_layer = self.params['bottom_electrode_label_layer']
        self.outer_electrode_ring_layer_inds = self.params['outer_electrode_ring_layer_inds']
        self.inner_electrode_ring_layer_inds = self.params['inner_electrode_ring_layer_inds']
        self.n_contact_offset = self.params['n_contact_offset']  # n spoke is aligned on the +x axis
        self.p_contact_offset = self.params['p_contact_offset']  # p spoke is offset
        self.layer = self.params['layer']
        self.si_spoke_offset_percentage = self.params['si_spoke_offset_percentage']
        self.rmin_in = self.params['rmin_in']
        self.alpha_zero_in = self.params['alpha_zero_in']
        self.angle_coupling = self.params['angle_coupling']
        self.coup_gap_drop = self.params['coup_gap_drop']
        self.heater_electrode_top_y_span = self.params['heater_electrode_top_y_span']

    @classmethod
    def get_params_info(cls) -> dict:
        return dict(
            # Parameters of rib-waveguide ring
            # --------------------------------
            r_core_cent='Radius to the center of ring core',
            drop_gap = 'Gap in drop port',

            r_r_gap='Ring to ring gap',
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
            access_length ='d',
            p_via_radius_offset ='d',
            n_via_radius_offset  ='d',
            high_doping_rout_offset ='d',
            high_doping_rin_offset ='d',
            electrode_offset ='d',
            electrode_width_inner ='d',
            electrode_width_outer ='d',
            basic_metal_routing='Option to have only basic metal routings for upper level',
            drop_taper_length ='d',
            salicide_radius_extension ='d',
            high_doping_n_rin_offset ='d',
            heater_pad_to_ring_dist='ee',
            in_out_taper='True',
            in_out_port_width='0.5',
            taper_length='10.2',
            taper_layer1='xvcx',
            taper_layer2='xcv',
            doping_spoke_info='xcv',
            extra_ring_info='xcv',
            spoke_num='xcv',
            label='xcv',
            outer_electrode_ring_layers='xcv',
            inner_electrode_ring_layers='xcv',
            high_n_doping_layer='xcv',
            high_p_doping_layer='xcv',
            salicide_lpp='xcv',
            bottom_metal_electrode_layer='xcv',
            bottom_electrode_label_layer='xcv',
            outer_electrode_ring_layer_inds='xcv',
            inner_electrode_ring_layer_inds='xcv',
            p_contact_offset='v',
            n_contact_offset='c',
            layer='hjkh',
            si_spoke_offset_percentage='fhg',
            rmin_in='fhf',
            alpha_zero_in='dfgd',
            angle_coupling='fghf',
            coup_gap_drop='sds',
        )

    @classmethod
    def get_default_param_values(cls) -> dict:
        """
        Returns default parameters of moscap ring
        """
        return dict(
            r_core_cent=None,
            r_r_gap=None,
            drop_gap = None,
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
            heater_disk_layer_extension=None,
            heater_electrode_bottom_layer=None,
            heater_width=None,
            access_length=None,
            p_via_radius_offset=None,
            n_via_radius_offset =None,
            high_doping_rout_offset=None,
            high_doping_rin_offset =None,
            electrode_offset =None,
            electrode_width_inner =None,
            electrode_width_outer =None,
            drop_taper_length =None,
            salicide_radius_extension =None,
            high_doping_n_rin_offset =None,
            heater_pad_to_ring_dist=None,
            in_out_taper=None,
            in_out_port_width=None,
            taper_length=None,
            taper_layer1=None,
            taper_layer2=None,
            doping_spoke_info=None,
            extra_ring_info=None,
            spoke_num=None,
            label=None,
            outer_electrode_ring_layers=None,
            inner_electrode_ring_layers=None,
            high_n_doping_layer=None,
            high_p_doping_layer=None,
            salicide_lpp=None,
            bottom_metal_electrode_layer=None,
            bottom_electrode_label_layer=None,
            outer_electrode_ring_layer_inds=None,
            inner_electrode_ring_layer_inds=None,
            p_contact_offset=None,
            n_contact_offset=None,
            layer=None,
            si_spoke_offset_percentage=None,
            rmin_in=None,
            alpha_zero_in=None,
            angle_coupling=None,
            coup_gap_drop=None,
        )

    def draw_layout(self):
        self.y_offset = 7.709-0.266
        """
        Draws all components of rib-waveguide ring modulator
        """
        self.draw_pad_array()
        
        # Row 1
        row = 1
        yB = 560
        yA = 640
        self.yA=yA
        self.yB=yB
        
        self.row_y_centre = 0.5*(yA+yB)
        
        self.radius_A = [6,6.01,6.02]
        self.ring_bus_A = [0.15,0.15,0.15]
        self.ring_ring_A = [0.175,0.175,0.175]
        
        self.radius_B = [6,6,6.031]
        self.ring_bus_B = [0.15,0.14,0.15]
        self.ring_ring_B= [0.15,0.15,0.175]
        
        self.device_ID=f"test{row}B0"
        self.draw_one_unit(rf_orientation="down",modu_centre=[-275,yB], ring_bus=self.ring_bus_B[0],  ring_ring=self.ring_ring_B[0],  radius=self.radius_B[0])
        self.device_ID=f"test{row}A0"
        self.draw_one_unit(rf_orientation="up",modu_centre=[-325,yA],   ring_bus=self.ring_bus_A[0],  ring_ring=self.ring_ring_A[0],  radius=self.radius_A[0])
        self.device_ID=f"test{row}B1"
        self.draw_one_unit(rf_orientation="down",modu_centre=[25,yB],   ring_bus=self.ring_bus_B[1],  ring_ring=self.ring_ring_B[1],  radius=self.radius_B[1])
        self.device_ID=f"test{row}A1"
        self.draw_one_unit(rf_orientation="up",modu_centre=[-25,yA],    ring_bus=self.ring_bus_A[1],  ring_ring=self.ring_ring_A[1],  radius=self.radius_A[1])
        self.device_ID=f"test{row}B2"
        self.draw_one_unit(rf_orientation="down",modu_centre=[325,yB],  ring_bus=self.ring_bus_B[2],  ring_ring=self.ring_ring_B[2],  radius=self.radius_B[2])
        self.device_ID=f"test{row}A2"
        self.draw_one_unit(rf_orientation="up",modu_centre=[275,yA],    ring_bus=self.ring_bus_A[2],  ring_ring=self.ring_ring_A[2],  radius=self.radius_A[2])
        self.put_gratings(number=3,gc_x=-600,gc_y=0.5*(yA+yB))
        self.put_gratings(number=3,gc_x=600,gc_y=0.5*(yA+yB))
        self.route_WDM_and_standalone(row=row,device="A0")

        
        # Row 2
        row=2
        yB = yB-240
        yA = yA-240
        self.yA=yA
        self.yB=yB
        
        self.row_y_centre = 0.5*(yA+yB)
        
        self.radius_A = [6,6.01,6.02]
        self.ring_bus_A = [0.13,0.13,0.13]
        self.ring_ring_A = [0.205,0.205,0.205]
        
        self.radius_B = [6,6,6.031]
        self.ring_bus_B = [0.15,0.14,0.13]
        self.ring_ring_B= [0.17,0.17,0.205]
        
        self.device_ID=f"test{row}B0"
        self.draw_one_unit(rf_orientation="down",modu_centre=[-275,yB], ring_bus=self.ring_bus_B[0],  ring_ring=self.ring_ring_B[0],  radius=self.radius_B[0])
        self.device_ID=f"test{row}A0"
        self.draw_one_unit(rf_orientation="up",modu_centre=[-325,yA],   ring_bus=self.ring_bus_A[0],  ring_ring=self.ring_ring_A[0],  radius=self.radius_A[0])
        self.device_ID=f"test{row}B1"
        self.draw_one_unit(rf_orientation="down",modu_centre=[25,yB],   ring_bus=self.ring_bus_B[1],  ring_ring=self.ring_ring_B[1],  radius=self.radius_B[1])
        self.device_ID=f"test{row}A1"
        self.draw_one_unit(rf_orientation="up",modu_centre=[-25,yA],    ring_bus=self.ring_bus_A[1],  ring_ring=self.ring_ring_A[1],  radius=self.radius_A[1])
        self.device_ID=f"test{row}B2"
        self.draw_one_unit(rf_orientation="down",modu_centre=[325,yB],  ring_bus=self.ring_bus_B[2],  ring_ring=self.ring_ring_B[2],  radius=self.radius_B[2])
        self.device_ID=f"test{row}A2"
        self.draw_one_unit(rf_orientation="up",modu_centre=[275,yA],    ring_bus=self.ring_bus_A[2],  ring_ring=self.ring_ring_A[2],  radius=self.radius_A[2])
        self.put_gratings(number=3,gc_x=-600,gc_y=0.5*(yA+yB))
        self.put_gratings(number=3,gc_x=600,gc_y=0.5*(yA+yB))
        self.route_WDM_and_standalone(row=row,device="A0")
        
        
        # Row 3
        row = 3
        yB = yB-240
        yA = yA-240
        self.yA=yA
        self.yB=yB
        
        self.row_y_centre = 0.5*(yA+yB)
        
        self.radius_A = [6,6.01,6.02]
        self.ring_bus_A = [0.12,0.12,0.12]
        self.ring_ring_A = [0.175,0.175,0.175]
        
        self.radius_B = [6,6,6.031]
        self.ring_bus_B = [0.15,0.14,0.12]
        self.ring_ring_B= [0.19,0.19,0.175]
        
        self.device_ID=f"test{row}B0"
        self.draw_one_unit(rf_orientation="down",modu_centre=[-275,yB], ring_bus=self.ring_bus_B[0],  ring_ring=self.ring_ring_B[0],  radius=self.radius_B[0])
        self.device_ID=f"test{row}A0"
        self.draw_one_unit(rf_orientation="up",modu_centre=[-325,yA],   ring_bus=self.ring_bus_A[0],  ring_ring=self.ring_ring_A[0],  radius=self.radius_A[0])
        self.device_ID=f"test{row}B1"
        self.draw_one_unit(rf_orientation="down",modu_centre=[25,yB],   ring_bus=self.ring_bus_B[1],  ring_ring=self.ring_ring_B[1],  radius=self.radius_B[1])
        self.device_ID=f"test{row}A1"
        self.draw_one_unit(rf_orientation="up",modu_centre=[-25,yA],    ring_bus=self.ring_bus_A[1],  ring_ring=self.ring_ring_A[1],  radius=self.radius_A[1])
        self.device_ID=f"test{row}B2"
        self.draw_one_unit(rf_orientation="down",modu_centre=[325,yB],  ring_bus=self.ring_bus_B[2],  ring_ring=self.ring_ring_B[2],  radius=self.radius_B[2])
        self.device_ID=f"test{row}A2"
        self.draw_one_unit(rf_orientation="up",modu_centre=[275,yA],    ring_bus=self.ring_bus_A[2],  ring_ring=self.ring_ring_A[2],  radius=self.radius_A[2])
        self.put_gratings(number=3,gc_x=-600,gc_y=0.5*(yA+yB))
        self.put_gratings(number=3,gc_x=600,gc_y=0.5*(yA+yB))
        self.route_WDM_and_standalone(row=row,device="A0")
        
        
        # Row 4
        row = 4
        yB = yB-240
        yA = yA-240
        self.yA=yA
        self.yB=yB
        
        self.row_y_centre = 0.5*(yA+yB)
        
        self.radius_A = [6,6.01,6.02]
        self.ring_bus_A = [0.15,0.15,0.15]
        self.ring_ring_A = [0.205,0.205,0.205]
        
        self.radius_B = [6,6,6.031]
        self.ring_bus_B = [0.13,0.12,0.15]
        self.ring_ring_B= [0.15,0.15,0.205]
        
        self.device_ID=f"test{row}B0"
        self.draw_one_unit(rf_orientation="down",modu_centre=[-275,yB], ring_bus=self.ring_bus_B[0],  ring_ring=self.ring_ring_B[0],  radius=self.radius_B[0])
        self.device_ID=f"test{row}A0"
        self.draw_one_unit(rf_orientation="up",modu_centre=[-325,yA],   ring_bus=self.ring_bus_A[0],  ring_ring=self.ring_ring_A[0],  radius=self.radius_A[0])
        self.device_ID=f"test{row}B1"
        self.draw_one_unit(rf_orientation="down",modu_centre=[25,yB],   ring_bus=self.ring_bus_B[1],  ring_ring=self.ring_ring_B[1],  radius=self.radius_B[1])
        self.device_ID=f"test{row}A1"
        self.draw_one_unit(rf_orientation="up",modu_centre=[-25,yA],    ring_bus=self.ring_bus_A[1],  ring_ring=self.ring_ring_A[1],  radius=self.radius_A[1])
        self.device_ID=f"test{row}B2"
        self.draw_one_unit(rf_orientation="down",modu_centre=[325,yB],  ring_bus=self.ring_bus_B[2],  ring_ring=self.ring_ring_B[2],  radius=self.radius_B[2])
        self.device_ID=f"test{row}A2"
        self.draw_one_unit(rf_orientation="up",modu_centre=[275,yA],    ring_bus=self.ring_bus_A[2],  ring_ring=self.ring_ring_A[2],  radius=self.radius_A[2])
        self.put_gratings(number=3,gc_x=-600,gc_y=0.5*(yA+yB))
        self.put_gratings(number=3,gc_x=600,gc_y=0.5*(yA+yB))
        self.route_WDM_and_standalone(row=row,device="A0")
        # Row 5
        row = 5
        yB = yB-240
        yA = yA-240
        self.yA=yA
        self.yB=yB
        
        self.row_y_centre = 0.5*(yA+yB)
        
        self.radius_A = [6,6.01,6.02]
        self.ring_bus_A = [0.13,0.13,0.13]
        self.ring_ring_A = [0.175,0.175,0.175]
        
        self.radius_B = [6,6,6.031]
        self.ring_bus_B = [0.13,0.12,0.13]
        self.ring_ring_B= [0.17,0.17,0.175]
        
        self.device_ID=f"test{row}B0"
        self.draw_one_unit(rf_orientation="down",modu_centre=[-275,yB], ring_bus=self.ring_bus_B[0],  ring_ring=self.ring_ring_B[0],  radius=self.radius_B[0])
        self.device_ID=f"test{row}A0"
        self.draw_one_unit(rf_orientation="up",modu_centre=[-325,yA],   ring_bus=self.ring_bus_A[0],  ring_ring=self.ring_ring_A[0],  radius=self.radius_A[0])
        self.device_ID=f"test{row}B1"
        self.draw_one_unit(rf_orientation="down",modu_centre=[25,yB],   ring_bus=self.ring_bus_B[1],  ring_ring=self.ring_ring_B[1],  radius=self.radius_B[1])
        self.device_ID=f"test{row}A1"
        self.draw_one_unit(rf_orientation="up",modu_centre=[-25,yA],    ring_bus=self.ring_bus_A[1],  ring_ring=self.ring_ring_A[1],  radius=self.radius_A[1])
        self.device_ID=f"test{row}B2"
        self.draw_one_unit(rf_orientation="down",modu_centre=[325,yB],  ring_bus=self.ring_bus_B[2],  ring_ring=self.ring_ring_B[2],  radius=self.radius_B[2])
        self.device_ID=f"test{row}A2"
        self.draw_one_unit(rf_orientation="up",modu_centre=[275,yA],    ring_bus=self.ring_bus_A[2],  ring_ring=self.ring_ring_A[2],  radius=self.radius_A[2])
        self.put_gratings(number=3,gc_x=-600,gc_y=0.5*(yA+yB))
        self.put_gratings(number=3,gc_x=600,gc_y=0.5*(yA+yB))
        self.route_WDM_and_standalone(row=row,device="A0")
        
        
        # Row 6
        row = 6
        yB = yB-240
        yA = yA-240
        self.yA=yA
        self.yB=yB
        
        self.row_y_centre = 0.5*(yA+yB)
        
        self.radius_A = [6,6.01,6.02]
        self.ring_bus_A = [0.12,0.12,0.12]
        self.ring_ring_A = [0.205,0.205,0.205]
        
        self.radius_B = [6,6,6.031]
        self.ring_bus_B = [0.13,0.12,0.12]
        self.ring_ring_B= [0.19,0.19,0.205]
        
        self.device_ID=f"test{row}B0"
        self.draw_one_unit(rf_orientation="down",modu_centre=[-275,yB], ring_bus=self.ring_bus_B[0],  ring_ring=self.ring_ring_B[0],  radius=self.radius_B[0])
        self.device_ID=f"test{row}A0"
        self.draw_one_unit(rf_orientation="up",modu_centre=[-325,yA],   ring_bus=self.ring_bus_A[0],  ring_ring=self.ring_ring_A[0],  radius=self.radius_A[0])
        self.device_ID=f"test{row}B1"
        self.draw_one_unit(rf_orientation="down",modu_centre=[25,yB],   ring_bus=self.ring_bus_B[1],  ring_ring=self.ring_ring_B[1],  radius=self.radius_B[1])
        self.device_ID=f"test{row}A1"
        self.draw_one_unit(rf_orientation="up",modu_centre=[-25,yA],    ring_bus=self.ring_bus_A[1],  ring_ring=self.ring_ring_A[1],  radius=self.radius_A[1])
        self.device_ID=f"test{row}B2"
        self.draw_one_unit(rf_orientation="down",modu_centre=[325,yB],  ring_bus=self.ring_bus_B[2],  ring_ring=self.ring_ring_B[2],  radius=self.radius_B[2])
        self.device_ID=f"test{row}A2"
        self.draw_one_unit(rf_orientation="up",modu_centre=[275,yA],    ring_bus=self.ring_bus_A[2],  ring_ring=self.ring_ring_A[2],  radius=self.radius_A[2])
        self.put_gratings(number=3,gc_x=-600,gc_y=0.5*(yA+yB))
        self.put_gratings(number=3,gc_x=600,gc_y=0.5*(yA+yB))
        self.route_WDM_and_standalone(row=row,device="A0")
        # self.route_WDM_special()

    def route_WDM_special(self,row=6):
        relative_y_0 = -self.ring_bus_A[0]-self.radius_A[0]
        relative_y_1 = -self.ring_bus_A[1]-self.radius_A[1]
        relative_y_B0 = -self.radius_B[0]-self.ring_bus_B[0]
        relative_y_B1 = -self.radius_B[1]-self.ring_bus_B[1]
        offset_to_left_gc = (0+self.row_y_centre)-(self.yA+relative_y_0)+self.y_offset
        offset_to_right_gc = (0+self.row_y_centre)-(self.yA+relative_y_B1)+self.y_offset+abs(self.yA-self.yB)
        start_device_ID = f"test{row}A0"
         # ring xA0
        Wg_A0L = AdiabaticRouter(gen_cls=self, init_port=self.get_photonic_port(f'{start_device_ID}_PORT_IN'),
                             layer=('si_full_free', 'drawing'), name='init_port')

        Wg_A0L.add_straight_wg(length=20, width= 0.35)
        Wg_A0L.add_straight_wg(length=60, width= 0.35)
        Wg_A0L.add_offset_bend(offset=offset_to_left_gc,rmin=10,width=0.35)
        Wg_A0L.add_straight_wg(length=150, width= 0.35)
        Wg_A0R = AdiabaticRouter(gen_cls=self, init_port=self.get_photonic_port(f'{start_device_ID}_PORT_OUT'),
                             layer=('si_full_free', 'drawing'), name='init_port')

        Wg_A0R.add_straight_wg(length=20, width= 0.35)
        Wg_A0R.add_offset_bend(offset=-relative_y_1+relative_y_0,rmin=10,width=0.35)
        Wg_A0R.add_straight_wg(length=233, width= 0.35)
        
        # ring xA1
        second_device_ID = f"test{row}A1"
        Wg_A1L = AdiabaticRouter(gen_cls=self, init_port=self.get_photonic_port(f'{second_device_ID}_PORT_IN'),
                             layer=('si_full_free', 'drawing'), name='init_port')

        Wg_A1L.add_straight_wg(length=20, width= 0.35)
        Wg_A1R = AdiabaticRouter(gen_cls=self, init_port=self.get_photonic_port(f'{second_device_ID}_PORT_OUT'),
                             layer=('si_full_free', 'drawing'), name='init_port')

        Wg_A1R.add_straight_wg(length=10, width= 0.35)
        Wg_A1R.add_bend_90(rmin=10,size=10,turn_left=False,width=0.35)
        Wg_A1R.add_straight_wg(length=10, width= 0.35)
        Wg_A1R.add_bend_90(rmin=10,size=10,turn_left=False,width=0.35)
        Wg_A1R.add_straight_wg(length=40+50+300, width= 0.35)
        Wg_A1R.add_bend_90(rmin=10,size=10,turn_left=True,width=0.35)
        Wg_A1R.add_straight_wg(length=abs(self.yA-self.yB)-10-10-10-10-10+15, width= 0.35)
        Wg_A1R.add_bend_90(rmin=10,size=10,turn_left=True,width=0.35)
        Wg_A1R.add_straight_wg(length=10, width= 0.35)
        Wg_A1R.add_offset_bend(offset=-relative_y_B0+relative_y_1-15,rmin=10,width=0.35)
        Wg_A1R.add_straight_wg(length=40, width= 0.35)
        
        # ring xB0
        third_device_ID=f"test{row}B0"
        Wg_B0L = AdiabaticRouter(gen_cls=self, init_port=self.get_photonic_port(f'{third_device_ID}_PORT_IN'),
                             layer=('si_full_free', 'drawing'), name='init_port')
        Wg_B0L.add_straight_wg(length=20, width= 0.35)
        
        Wg_B0R = AdiabaticRouter(gen_cls=self, init_port=self.get_photonic_port(f'{third_device_ID}_PORT_OUT'),
                             layer=('si_full_free', 'drawing'), name='init_port')
        Wg_B0R.add_straight_wg(length=10, width= 0.35)
        Wg_B0R.add_offset_bend(offset=15,rmin=10,width=0.35)
        Wg_B0R.add_straight_wg(length=160, width= 0.35)
        Wg_B0R.add_offset_bend(offset=-relative_y_B1+relative_y_B0-15,rmin=10,width=0.35)
        
        # ring xB1
        fourth_device_ID=f"test{row}B0"
        Wg_B0L = AdiabaticRouter(gen_cls=self, init_port=self.get_photonic_port(f'{fourth_device_ID}_PORT_IN'),
                             layer=('si_full_free', 'drawing'), name='init_port')
        Wg_B0L.add_straight_wg(length=20, width= 0.35)
        Wg_B2R = AdiabaticRouter(gen_cls=self, init_port=self.get_photonic_port(f'{fourth_device_ID}_PORT_OUT'),
                             layer=('si_full_free', 'drawing'), name='init_port')

        Wg_B2R.add_straight_wg(length=20, width= 0.35)
        Wg_B2R.add_offset_bend(offset=15,rmin=10,width=0.35)

        Wg_B2R.add_straight_wg(length=20+60, width= 0.35)
        Wg_B2R.add_offset_bend(offset=-offset_to_right_gc-15,rmin=10,width=0.35)
        Wg_B2R.add_straight_wg(length=150, width= 0.35)





          
    def route_WDM_and_standalone(self,row=1,device="A0"):
        relative_y_0 = -self.ring_bus_A[0]-self.radius_A[0]
        relative_y_1 = -self.ring_bus_A[1]-self.radius_A[1]
        relative_y_2 = -self.ring_bus_A[2]-self.radius_A[2]
        relative_y_3 = -self.ring_bus_B[2]-self.radius_B[2]
        offset_to_left_gc = (90+self.row_y_centre)-(self.yA+relative_y_0)+self.y_offset
        offset_to_right_gc = (90+self.row_y_centre)-(self.yA+relative_y_3)+self.y_offset+abs(self.yA-self.yB)
        start_device_ID = f"test{row}{device}"
        # ring xA0
        Wg_A0L = AdiabaticRouter(gen_cls=self, init_port=self.get_photonic_port(f'{start_device_ID}_PORT_IN'),
                             layer=('si_full_free', 'drawing'), name='init_port')

        Wg_A0L.add_straight_wg(length=20, width= 0.35)
        Wg_A0L.add_straight_wg(length=60, width= 0.35)
        Wg_A0L.add_offset_bend(offset=offset_to_left_gc,rmin=10,width=0.35)
        Wg_A0L.add_straight_wg(length=150, width= 0.35)
        
        Wg_A0R = AdiabaticRouter(gen_cls=self, init_port=self.get_photonic_port(f'{start_device_ID}_PORT_OUT'),
                             layer=('si_full_free', 'drawing'), name='init_port')

        Wg_A0R.add_straight_wg(length=20, width= 0.35)
        Wg_A0R.add_offset_bend(offset=-relative_y_1+relative_y_0,rmin=10,width=0.35)
        Wg_A0R.add_straight_wg(length=233, width= 0.35)
        
        # ring xA1
        second_device_ID = f"test{row}A1"
        Wg_A1L = AdiabaticRouter(gen_cls=self, init_port=self.get_photonic_port(f'{second_device_ID}_PORT_IN'),
                             layer=('si_full_free', 'drawing'), name='init_port')

        Wg_A1L.add_straight_wg(length=20, width= 0.35)
        
        Wg_A1R = AdiabaticRouter(gen_cls=self, init_port=self.get_photonic_port(f'{second_device_ID}_PORT_OUT'),
                             layer=('si_full_free', 'drawing'), name='init_port')

        Wg_A1R.add_straight_wg(length=20, width= 0.35)
        Wg_A1R.add_offset_bend(offset=-relative_y_2+relative_y_1,rmin=10,width=0.35)
        Wg_A1R.add_straight_wg(length=233, width= 0.35)
        
        #ring xA2
        third_device_ID = f"test{row}A2"
        Wg_A2L = AdiabaticRouter(gen_cls=self, init_port=self.get_photonic_port(f'{third_device_ID}_PORT_IN'),
                             layer=('si_full_free', 'drawing'), name='init_port')

        Wg_A2L.add_straight_wg(length=20, width= 0.35)

        Wg_A2R = AdiabaticRouter(gen_cls=self, init_port=self.get_photonic_port(f'{third_device_ID}_PORT_OUT'),
                             layer=('si_full_free', 'drawing'), name='init_port')

        Wg_A2R.add_straight_wg(length=10, width= 0.35)
        Wg_A2R.add_bend_90(rmin=10,size=10,turn_left=False,width=0.35)
        Wg_A2R.add_straight_wg(length=10, width= 0.35)
        Wg_A2R.add_bend_90(rmin=10,size=10,turn_left=False,width=0.35)
        Wg_A2R.add_straight_wg(length=40+50, width= 0.35)
        Wg_A2R.add_bend_90(rmin=10,size=10,turn_left=True,width=0.35)
        Wg_A2R.add_straight_wg(length=abs(self.yA-self.yB)-10-10-10-10-10+15, width= 0.35)
        Wg_A2R.add_bend_90(rmin=10,size=10,turn_left=True,width=0.35)
        Wg_A2R.add_straight_wg(length=5, width= 0.35)
        Wg_A2R.add_offset_bend(offset=-relative_y_3+relative_y_2-15,rmin=10,width=0.35)
        Wg_A2R.add_straight_wg(length=15+23, width= 0.35)


        
        #ring xB2
        fourth_device_ID = f"test{row}B2"
        Wg_B2L = AdiabaticRouter(gen_cls=self, init_port=self.get_photonic_port(f'{fourth_device_ID}_PORT_IN'),
                             layer=('si_full_free', 'drawing'), name='init_port')

        Wg_B2L.add_straight_wg(length=20, width= 0.35)

        Wg_B2R = AdiabaticRouter(gen_cls=self, init_port=self.get_photonic_port(f'{fourth_device_ID}_PORT_OUT'),
                             layer=('si_full_free', 'drawing'), name='init_port')

        Wg_B2R.add_straight_wg(length=20, width= 0.35)
        Wg_B2R.add_offset_bend(offset=15,rmin=10,width=0.35)

        Wg_B2R.add_straight_wg(length=20+30, width= 0.35)
        Wg_B2R.add_offset_bend(offset=-offset_to_right_gc-15,rmin=10,width=0.35)
        Wg_B2R.add_straight_wg(length=150, width= 0.35)
        
        """Start to do standalone"""
        relative_y_B0 = -self.radius_B[0]-self.ring_bus_B[0]
        relative_y_B1 = -self.radius_B[1]-self.ring_bus_B[1]
        B0_to_gc_offset_y = (-90+self.row_y_centre)-(self.yB+relative_y_B0)+self.y_offset
        B1_to_gc_offset_y = (0+self.row_y_centre)-(self.yB+relative_y_B1)+self.y_offset

        fifth_device_ID = f"test{row}B0"
        Wg_B0L = AdiabaticRouter(gen_cls=self, init_port=self.get_photonic_port(f'{fifth_device_ID}_PORT_IN'),
                             layer=('si_full_free', 'drawing'), name='init_port')

        Wg_B0L.add_straight_wg(length=10, width= 0.35)
        Wg_B0L.add_offset_bend(offset=B0_to_gc_offset_y,rmin=10,width=0.35)
        Wg_B0L.add_straight_wg(length=250, width= 0.35)
        
        Wg_B0R = AdiabaticRouter(gen_cls=self, init_port=self.get_photonic_port(f'{fifth_device_ID}_PORT_OUT'),
                             layer=('si_full_free', 'drawing'), name='init_port')

        Wg_B0R.add_straight_wg(length=10, width= 0.35)
        Wg_B0R.add_offset_bend(offset=24,rmin=10,width=0.35)
        Wg_B0R.add_straight_wg(length=680, width= 0.35)
        Wg_B0R.add_offset_bend(offset=-B0_to_gc_offset_y-24,rmin=10,width=0.35)
        Wg_B0R.add_straight_wg(length=120, width= 0.35)

        six_device_ID = f"test{row}B1"
        Wg_B1L = AdiabaticRouter(gen_cls=self, init_port=self.get_photonic_port(f'{six_device_ID}_PORT_IN'),
                             layer=('si_full_free', 'drawing'), name='init_port')

        Wg_B1L.add_straight_wg(length=10, width= 0.35)
        Wg_B1L.add_offset_bend(offset=-20,rmin=10,width=0.35)
        Wg_B1L.add_straight_wg(length=60, width= 0.35)
        Wg_B1L.add_offset_bend(offset=B1_to_gc_offset_y+20,rmin=10,width=0.35)
        Wg_B1L.add_straight_wg(length=470, width= 0.35)
        
        Wg_B1R = AdiabaticRouter(gen_cls=self, init_port=self.get_photonic_port(f'{six_device_ID}_PORT_OUT'),
                             layer=('si_full_free', 'drawing'), name='init_port')

        Wg_B1R.add_straight_wg(length=10, width= 0.35)
        Wg_B1R.add_offset_bend(offset=20,rmin=10,width=0.35)
        Wg_B1R.add_straight_wg(length=380, width= 0.35)
        Wg_B1R.add_offset_bend(offset=-B1_to_gc_offset_y-20,rmin=10,width=0.35)
        Wg_B1R.add_straight_wg(length=120, width= 0.35)









        


        
            # offset_to_left_gc = (90+self.row_y_centre)-(self.yA+relative_y_0)+self.y_offset

        
        
        
        
        
        
        

        
    def draw_pad_array(self):
        for M in range(6):
            if M>=0:
                for N in range(18):
                    self.draw_single_pad("up",[50*N-425,240*M-685])
                    self.draw_single_pad("down",[50*N-425,240*M-685+170])
            else:
                for N in range(12):
                    self.draw_single_pad("up",[50*N-425,240*M-685])
                    self.draw_single_pad("down",[50*N-425,240*M-685+170])
                    
    
    def draw_single_pad(self,oreintation=str,centre=[0,0]):
        
            self.add_rect(layer=['LB', 'drawing'],
                      bbox=BBox(right=centre[0]+0.5*self.pad_width,
                                bottom=centre[1]-0.5*self.pad_length,
                                left=centre[0]-0.5*self.pad_width,
                                top=centre[1]+0.5*self.pad_length,
                                resolution=self.grid.resolution)
                      )
    
            self.add_rect(layer=['DV', 'drawing'],
                      bbox=BBox(right=centre[0]+0.5*self.pad_open_width,
                                bottom=centre[1]-0.5*self.pad_open_length,
                                left=centre[0]-0.5*self.pad_open_width,
                                top=centre[1]+0.5*self.pad_open_length,
                                resolution=self.grid.resolution)
                      )
            if oreintation.lower() == "up":
                self.add_rect(layer=['LB', 'drawing'],
                      bbox=BBox(right=centre[0]+0.5*14.6,
                                bottom=centre[1]+0.5*self.pad_length,
                                left=centre[0]-0.5*14.6,
                                top=centre[1]+0.5*self.pad_length+8.1,
                                resolution=self.grid.resolution)
                      )
            else:
                self.add_rect(layer=['LB', 'drawing'],
                      bbox=BBox(right=centre[0]+0.5*14.6,
                                bottom=centre[1]-0.5*self.pad_length-8.1,
                                left=centre[0]-0.5*14.6,
                                top=centre[1]-0.5*self.pad_length,
                                resolution=self.grid.resolution)
                      )
                
            
    # Modulator Unit
    def draw_one_unit(self,rf_orientation=str,modu_centre=[0,0],ring_ring=0.4,ring_bus=0.4,radius=6):
        self.r_r_gap = ring_ring
        self.r_core_cent = radius
        self.coup_gap = ring_bus
        
        self.modu_centre = modu_centre
        if rf_orientation.lower() == "down":
            self.draw_input_wg()
            self.draw_heater()
            self.draw_spoked_rings()
            # self.draw_drop_to_PD()

            if self.basic_metal_routing:
                self.place_contact_electrodes_basic()
                self.place_heater_contact_electrodes_basic()
            else:
                self.place_contact_electrodes()
                self.place_heater_contact_electrodes()
                self.place_gs_electrodes()
                self.place_heater_gs_electrodes()

            self.mod_addition()
            self.photon_addition()

        if rf_orientation.lower() == "up":
            self.draw_spoked_rings()
            self.draw_heater()
            self.draw_input_wg()
            self.place_contact_electrodes_basic_up()
            self.place_heater_contact_electrodes_basic_up()
         
                
            self.mod_addition()
            self.photon_addition()
        
        
    def PHPN1_addition(self):
        self.add_rect(layer= ('PHPN1', 'drawing'),
                      bbox=BBox(right=16,
                                bottom=-15,
                                left=-16,
                                top=15,
                                resolution=self.grid.resolution)
                      )

    def mod_addition(self):
        self.add_rect(layer=('PHOTON', 'drawing'),
                      bbox=BBox(right=self.modu_centre[0]+16,
                                bottom=self.modu_centre[1]-15,
                                left=self.modu_centre[0]-16,
                                top=self.modu_centre[1]+15,
                                resolution=self.grid.resolution)
                      )
    def photon_addition(self):
        self.add_rect(layer=('mod', 'drawing'),
                      bbox=BBox(right=self.modu_centre[0]+16,
                                bottom=self.modu_centre[1]-15,
                                left=self.modu_centre[0]-16,
                                top=self.modu_centre[1]+15,
                                resolution=self.grid.resolution)
                      )
        # self.add_rect(layer=('IH', 'drawing'),
        #               bbox=BBox(right=self.modu_centre[0]+16,
        #                         bottom=self.modu_centre[1]-15,
        #                         left=self.modu_centre[0]-16,
        #                         top=self.modu_centre[1]+15,
        #                         resolution=self.grid.resolution)
        #               )
        
        self.add_rect(layer=('IH', 'drawing'),
                      bbox=BBox(right=self.modu_centre[0]+0.5*self.r_r_gap+0.08,
                                bottom=self.modu_centre[1]-1.3,
                                left=self.modu_centre[0]-0.5*self.r_r_gap-0.08,
                                top=self.modu_centre[1]+1.3,
                                resolution=self.grid.resolution)
                      )

    def draw_spoked_rings(self):
        spoke_params = dict(
            # This class could have been sent as a dict under name spoked_params and that would have shorten the code
            # But that will need changes in variables used in seperate functions like metal routings,etc which will break code
            ring_loc = (0, 0),
            g_pad_loc = None,
            s_pad_loc = None,
            heaterpad1_loc = None,
            heaterpad2_loc = None,
            r_core_cent = self.r_core_cent,
            drop_gap = self.params['drop_gap'],
            core_layer = self.params['core_layer'],
            core_width = self.params['core_width'],
            core_slot_width = self.params['core_slot_width'],
            slab_layer = self.params['slab_layer'],
            slab_width = self.params['slab_width'],
            slab_slot_width = self.params['slab_slot_width'],
            bent_coupler = self.params['bent_coupler'],
            coup_core_width = self.params['coup_core_width'],
            coup_slab_width = self.params['coup_slab_width'],
            coup_length = self.params['coup_length'],
            coup_gap = self.coup_gap,
            coup_radius = self.params['coup_radius'],
            coup_angle = self.params['coup_angle'],
            curve_rate = self.params['curve_rate'],
            coup_angle_in = self.params['coup_angle_in'],
            gs_electrodes = self.params['gs_electrodes'],
            gs_core_dist = self.params['gs_core_dist'],
            gs_bottom_width = self.params['gs_bottom_width'],
            gs_bottom_length = self.params['gs_bottom_length'],
            gs_pad_layer = self.params['gs_pad_layer'],
            gs_pad_open_layer = self.params['gs_pad_open_layer'],
            gs_pad_open_inclusion = self.params['gs_pad_open_inclusion'],
            gs_pad_width = self.params['gs_pad_width'],
            gs_pad_length = self.params['gs_pad_length'],
            gs_pad_pitch = self.params['gs_pad_pitch'],
            gs_pad_to_ring_dist = self.params['gs_pad_to_ring_dist'],
            access_length = self.params['gs_pad_to_ring_dist'],
            p_via_radius_offset = self.params['p_via_radius_offset'],
            n_via_radius_offset = self.params['n_via_radius_offset'],
            high_doping_rout_offset = self.params['high_doping_rout_offset'],
            high_doping_rin_offset = self.params['high_doping_rin_offset'],
            electrode_offset = self.params['electrode_offset'],
            electrode_width_inner = self.params['electrode_width_inner'],
            electrode_width_outer = self.params['electrode_width_outer'],
            drop_taper_length = self.params['drop_taper_length'],
            salicide_radius_extension = self.params['salicide_radius_extension'],
            high_doping_n_rin_offset = self.params['high_doping_n_rin_offset'],
            heater_width = self.params['heater_width'],
            heater_pad_to_ring_dist = self.params['heater_pad_to_ring_dist'],
            contact_dist = self.params['contact_dist'],
            heater_electrode_top_layer = self.params['heater_electrode_top_layer'],
            in_out_taper = self.params['in_out_taper'],
            in_out_port_width = self.params['in_out_port_width'],
            taper_length = self.params['taper_length'],
            taper_layer1 = self.params['taper_layer1'],
            taper_layer2 = self.params['taper_layer2'],
            doping_spoke_info = self.params['doping_spoke_info'],
            extra_ring_info = self.params['extra_ring_info'],
            spoke_num = self.params['spoke_num'],
            label = self.params['label'],
            outer_electrode_ring_layers = self.params['outer_electrode_ring_layers'],
            inner_electrode_ring_layers = self.params['inner_electrode_ring_layers'],
            high_n_doping_layer = self.params['high_n_doping_layer'],
            high_p_doping_layer = self.params['high_p_doping_layer'],
            salicide_lpp = self.params['salicide_lpp'],
            bottom_metal_electrode_layer = self.params['bottom_metal_electrode_layer'],
            bottom_electrode_label_layer = self.params['bottom_electrode_label_layer'],
            outer_electrode_ring_layer_inds = self.params['outer_electrode_ring_layer_inds'],
            inner_electrode_ring_layer_inds = self.params['inner_electrode_ring_layer_inds'],
            n_contact_offset = self.params['n_contact_offset'],  # n spoke is aligned on the +x axis
            p_contact_offset = self.params['p_contact_offset'],  # p spoke is offset
            layer = self.params['layer'],
            si_spoke_offset_percentage=self.params['si_spoke_offset_percentage'],
        )
        heater_master = self.new_template(params=spoke_params, temp_cls=RingRibWg_sr)
        self.add_instance(master=heater_master, loc=(self.modu_centre[0] + (self.r_r_gap/2+self.core_width / 2) + self.r_core_cent, self.modu_centre[1]))
        heater_master = self.new_template(params=spoke_params, temp_cls=RingRibWg_sr)
        self.add_instance(master=heater_master, loc=(self.modu_centre[0] - (self.r_r_gap / 2 + self.core_width / 2) - self.r_core_cent, self.modu_centre[1]))

    def draw_heater(self):
        rout = self.r_core_cent + self.core_width / 2
        ring_width = self.core_width / 2 + self.slab_width / 2
        rin = rout - ring_width
        p_via_radius = rin - self.p_via_radius_offset
        n_via_radius = rin - self.n_via_radius_offset
        if p_via_radius < n_via_radius:
            # inner electrode is p, outer is n

            electrode_width_p = self.electrode_width_inner
            electrode_rout_p = p_via_radius - self.electrode_offset
            inner_pn_radius = electrode_rout_p - electrode_width_p

            electrode_width_n = self.electrode_width_outer
            electrode_rin_n = n_via_radius + self.electrode_offset
            outer_pn_radius = electrode_rin_n + electrode_width_n
            heater_radius = inner_pn_radius + electrode_width_p
        else:

            p_electrode_layer_ind_list = self.outer_electrode_ring_layer_inds
            electrode_width_p = self.electrode_width_outer
            electrode_rin_p = p_via_radius + self.electrode_offset
            outer_pn_radius = electrode_rin_p + electrode_width_p

            electrode_width_n = self.electrode_width_inner
            electrode_rout_n = n_via_radius - self.electrode_offset
            inner_pn_radius = electrode_rout_n - electrode_width_n
            heater_radius = inner_pn_radius + electrode_width_n
        offset_distance = outer_pn_radius


        heater_params = dict(
            rout=heater_radius-0.2,

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

        if not self.params['heater_disable']:
            # Compute the width from the heater resistance design function
            heater_params['width'] = 1.2
            heater_master = self.new_template(params=heater_params, temp_cls=RingHeater)
            self.add_instance(master=heater_master,loc=(self.modu_centre[0] + (self.r_r_gap/2+self.core_width / 2) + self.r_core_cent, self.modu_centre[1]))
            heater_master = self.new_template(params=heater_params, temp_cls=RingHeater)
            self.add_instance(master=heater_master, loc=(self.modu_centre[0] - (self.r_r_gap / 2 + self.core_width / 2) - self.r_core_cent, self.modu_centre[1]))

    def draw_heater_up(self):
        rout = self.r_core_cent + self.core_width / 2
        ring_width = self.core_width / 2 + self.slab_width / 2
        rin = rout - ring_width
        p_via_radius = rin - self.p_via_radius_offset
        n_via_radius = rin - self.n_via_radius_offset
        if p_via_radius < n_via_radius:
            # inner electrode is p, outer is n

            electrode_width_p = self.electrode_width_inner
            electrode_rout_p = p_via_radius - self.electrode_offset
            inner_pn_radius = electrode_rout_p - electrode_width_p

            electrode_width_n = self.electrode_width_outer
            electrode_rin_n = n_via_radius + self.electrode_offset
            outer_pn_radius = electrode_rin_n + electrode_width_n
            heater_radius = inner_pn_radius + electrode_width_p
        else:

            p_electrode_layer_ind_list = self.outer_electrode_ring_layer_inds
            electrode_width_p = self.electrode_width_outer
            electrode_rin_p = p_via_radius + self.electrode_offset
            outer_pn_radius = electrode_rin_p + electrode_width_p

            electrode_width_n = self.electrode_width_inner
            electrode_rout_n = n_via_radius - self.electrode_offset
            inner_pn_radius = electrode_rout_n - electrode_width_n
            heater_radius = inner_pn_radius + electrode_width_n
        offset_distance = outer_pn_radius


        heater_params = dict(
            rout=heater_radius-0.2,

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

        if not self.params['heater_disable']:
            # Compute the width from the heater resistance design function
            heater_params['width'] = 1.2
            heater_master = self.new_template(params=heater_params, temp_cls=RingHeater)
            self.add_instance(master=heater_master,loc=(self.modu_centre[0] + (self.r_r_gap/2+self.core_width / 2) + self.r_core_cent, self.modu_centre[1]))
            heater_master = self.new_template(params=heater_params, temp_cls=RingHeater)
            self.add_instance(master=heater_master, loc=(self.modu_centre[0] - (self.r_r_gap / 2 + self.core_width / 2) - self.r_core_cent, self.modu_centre[1]))

    def draw_input_wg_cena(self):
        """
        Draws input coupler waveguide of the rib-waveguide ring.
        """
        position_ring1 = (0, 0)
        ring_bus_gap = self.coup_gap  # 0.500


        peanut_width = 0.4

        coupler_params = dict(
            layer='si_full_free',
            layer1=('si_full_free', 'drawing'),
            w=peanut_width,
            x=0,
            y=0,
            gap=self.params['coup_gap'],
            wg180_radius=10,
            r_core_cent=self.params['r_core_cent']+self.params['core_width']/2,
            coup_core_width=self.params['coup_core_width'],
            rmin_in=self.params['rmin_in'],
            alpha_zero_in=self.params['alpha_zero_in'],
            angle_coupling=self.params['angle_coupling'],
        )
        temp_peanut = self.new_template(params=coupler_params, temp_cls=adiabatic_coupler_cena)
        master_peanut = self.add_instance(temp_peanut, orient='R270', loc=(0, 0))
        peanut_top_port = master_peanut.get_photonic_port('PORT_CENTER1')

        trans_vec_peanut = - peanut_top_port.center
        master_peanut.move_by(dx=trans_vec_peanut[0]-2*self.r_core_cent-self.core_width-self.params['coup_core_width']/2-self.coup_gap-self.r_r_gap/2,
                              dy=trans_vec_peanut[1],
                              unit_mode=False)
#+self.coup_gap+self.r_core_cent+self.params['coup_core_width']/2+self.core_width/2
        print("Peanut y transform is {}".format(trans_vec_peanut[1]))



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
            loc = (self.modu_centre[0] - core_master.arc_list[-1]['x'][-1] / 2 -(self.r_r_gap/2+self.core_width / 2)-self.r_core_cent,
                   self.modu_centre[1] - max(core_master.arc_list[3]['y']) -
                   self.r_core_cent - self.coup_gap - (self.core_width + self.coup_core_width) / 2)
            self.ring_1_centre = [self.modu_centre[0]  -(self.r_r_gap/2+self.core_width / 2)-self.r_core_cent,
                                  self.modu_centre[1]]

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
            loc = (self.modu_centre[0] - self.coup_length / 2,
                   self.modu_centre[1] - self.r_core_cent - self.coup_gap - (self.core_width + self.coup_core_width) / 2)

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
            port_renaming={'PORT_IN': f'{self.device_ID}_PORT_IN',
                           'PORT_OUT': f'{self.device_ID}_PORT_OUT'},
            show=False)

        # Wg = AdiabaticRouter(gen_cls=self, init_port=self.get_photonic_port(f'{self.device_ID}_PORT_IN'),
        #                      layer=('si_full_free', 'drawing'), name='init_port')

        # Wg.add_straight_wg(length=20, width= 0.35)

        # self.extract_photonic_ports(
        #     inst=Wg.inst[list(Wg.inst)[-1]],
        #     port_names=['PORT_IN', 'PORT_OUT'],
        #     port_renaming={'PORT_IN': 'PORT_IN',
        #                    'PORT_OUT': 'PORT0',
        #                    },
        #     show=True)

        # Wg1 = AdiabaticRouter(gen_cls=self, init_port=self.get_photonic_port(f'{self.device_ID}_PORT_OUT'),
        #                       layer=('si_full_free', 'drawing'), name='init_port')

        # Wg1.add_straight_wg(length=20, width= 0.35)

        # self.extract_photonic_ports(
        #     inst=Wg1.inst[list(Wg1.inst)[-1]],
        #     port_names=['PORT_IN', 'PORT_OUT'],
        #     port_renaming={'PORT_IN': 'PORT_IN',
        #                    'PORT_OUT': 'PORT1',
        #                    },
        #     show=True)

        # attach input output tapers
        if self.in_out_taper:
            self.create_in_out_taper()
            taper_in = self.add_instance_port_to_port(inst_master=self.taper_master,
                                                      instance_port_name='PORT1',
                                                      self_port_name='PORT0',
                                                      reflect=False)



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
            
       
    def draw_drop_to_PD(self):
        """
        Draw output port to terminator and PD.
        """
        
        """Parameters"""
        coupling_region_length = 6
        bend90_size = 4
        terminator_effective_size = 11
        terminator_end_width = 0.05
        drop_gap = 0.4
        
        # PD L
        self.add_photonic_port(name='terminator_L_end', center=(self.ring_1_centre[0]-self.r_core_cent-0.5*self.core_width-drop_gap-0.5*self.drop_core_width+terminator_effective_size, self.ring_1_centre[1]+0.5*coupling_region_length+terminator_effective_size),
                               orient='R0', width=terminator_end_width, layer=self.core_layer)
        Wg = AdiabaticRouter(gen_cls=self, init_port=self.get_photonic_port('terminator_L_end'),
                            layer=self.core_layer, name='test_port1')
        # Wg.add_straight_wg(length=5)
        Wg.add_bend_90(rmin=3, size=terminator_effective_size, turn_left=True,width=self.drop_core_width)
        Wg.add_straight_wg(length=coupling_region_length,width=self.drop_core_width)
        Wg.add_bend_90(rmin=2, size=bend90_size, turn_left=False, width=self.drop_core_width)
        Wg.add_straight_wg(length=2,width=self.drop_core_width)
        Wg.add_offset_bend(offset=bend90_size+0.5*coupling_region_length, rmin=2)
        Wg.add_straight_wg(length=2,width=self.drop_core_width)
        # PD R
        self.add_photonic_port(name='terminator_R_end', center=(self.ring_1_centre[0]+2*self.r_core_cent+self.core_width+self.r_r_gap+self.r_core_cent+0.5*self.core_width+drop_gap+0.5*self.drop_core_width-terminator_effective_size, self.ring_1_centre[1]+0.5*coupling_region_length+terminator_effective_size),
                               orient='R180', width=terminator_end_width, layer=self.core_layer)
        Wg = AdiabaticRouter(gen_cls=self, init_port=self.get_photonic_port('terminator_R_end'),
                            layer=self.core_layer, name='test_port1')
        # Wg.add_straight_wg(length=5)
        Wg.add_bend_90(rmin=3, size=terminator_effective_size, turn_left=False,width=self.drop_core_width)
        Wg.add_straight_wg(length=coupling_region_length,width=self.drop_core_width)
        Wg.add_bend_90(rmin=2, size=bend90_size, turn_left=True, width=self.drop_core_width)
        Wg.add_straight_wg(length=2,width=self.drop_core_width)
        Wg.add_offset_bend(offset=-(bend90_size+0.5*coupling_region_length), rmin=2)
        Wg.add_straight_wg(length=2,width=self.drop_core_width)


    
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
            loc = (self.modu_centre[0] - core_master.arc_list[-1]['x'][-1] / 2 -(self.r_r_gap/2+self.core_width / 2)-self.r_core_cent,
                   self.modu_centre[1] + max(core_master.arc_list[3]['y']) +
                   self.r_core_cent + self.coup_gap_drop + (self.core_width + self.coup_core_width) / 2)

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
            loc = (self.modu_centre[0] - self.coup_length / 2,
                   self.modu_centre[1] + self.r_core_cent + self.coup_gap_drop + (self.core_width + self.coup_core_width) / 2)

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

        # attach input output tapers
        if self.in_out_taper:
            self.create_in_out_taper()
            taper_in = self.add_instance_port_to_port(inst_master=self.taper_master,
                                                      instance_port_name='PORT1',
                                                      self_port_name='PORT0',
                                                      reflect=False)



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


    

    def place_contact_electrodes(self):
        # calculate the corner coordinate of the left (ground) pad
        # calculate the corner coordinate of the left (ground) pad

        rout = self.r_core_cent + self.core_width / 2
        ring_width = self.core_width / 2 + self.slab_width / 2
        rin = rout - ring_width
        p_via_radius = rin - self.p_via_radius_offset
        n_via_radius = rin - self.n_via_radius_offset
        if p_via_radius < n_via_radius:
            # inner electrode is p, outer is n

            electrode_width_p = self.electrode_width_inner
            electrode_rout_p = p_via_radius - self.electrode_offset
            inner_pn_radius = electrode_rout_p - electrode_width_p

            electrode_width_n = self.electrode_width_outer
            electrode_rin_n = n_via_radius + self.electrode_offset
            outer_pn_radius = electrode_rin_n + electrode_width_n

        else:

            p_electrode_layer_ind_list = self.outer_electrode_ring_layer_inds
            electrode_width_p = self.electrode_width_outer
            electrode_rin_p = p_via_radius + self.electrode_offset
            outer_pn_radius = electrode_rin_p + electrode_width_p

            electrode_width_n = self.electrode_width_inner
            electrode_rout_n = n_via_radius - self.electrode_offset
            inner_pn_radius = electrode_rout_n - electrode_width_n

        dim1 = 11.7
        dim2 = dim1  # 10.722 + 6.72 - 5.812
        self.left_pad_loc = (self.modu_centre[0] - (self.gs_pad_pitch ) ,
                          self.modu_centre[1] - self.gs_pad_to_ring_dist
                          )
        self.central_pad_loc = (self.modu_centre[0] ,
                                self.modu_centre[1] - self.gs_pad_to_ring_dist
                             )
        # calculate the corner coordinate of the right (signal) pad
        self.right_pad_loc = (self.modu_centre[0] + (self.gs_pad_pitch),
                              self.modu_centre[1] - self.gs_pad_to_ring_dist
                              )
        offset_distance = outer_pn_radius
        width=2
        # draw left pad wiring
        wire1_top = self.modu_centre[1]
        wire1_bottom = wire1_top - width
        wire1_left = self.left_pad_loc[0]
        wire1_right = self.modu_centre[0] - (self.r_r_gap/2+self.core_width/2 ) -  self.r_core_cent-offset_distance
        self.add_rect(layer=self.outer_electrode_ring_layers[-1],
                      bbox=BBox(right=wire1_right,
                                bottom=wire1_bottom,
                                left=wire1_left,
                                top=wire1_top,
                                resolution=self.grid.resolution)
                      )


        wire2_top = wire1_top
        wire2_bottom = self.left_pad_loc[1]-dim1/2
        wire2_left = self.left_pad_loc[0]
        wire2_right = wire2_left + width
        self.add_rect(layer=self.outer_electrode_ring_layers[-1],
                      bbox=BBox(right=wire2_right,
                                bottom=wire2_bottom,
                                left=wire2_left,
                                top=wire2_top,
                                resolution=self.grid.resolution)
                      )
        # draw right pad wire
        wire1_top = self.modu_centre[1]
        wire1_bottom = wire1_top - width
        wire1_left = self.modu_centre[0] + (self.r_r_gap/2+self.core_width/2 ) + self.r_core_cent+offset_distance
        wire1_right = self.right_pad_loc[0]
        self.add_rect(layer=self.outer_electrode_ring_layers[-1],
                      bbox=BBox(right=wire1_right,
                                bottom=wire1_bottom,
                                left=wire1_left,
                                top=wire1_top,
                                resolution=self.grid.resolution)
                      )
        wire2_top = wire1_top
        wire2_bottom = self.right_pad_loc[1]-dim1/2
        wire2_left = self.right_pad_loc[0]-width
        wire2_right = self.right_pad_loc[0]
        self.add_rect(layer=self.outer_electrode_ring_layers[-1],
                      bbox=BBox(right=wire2_right,
                                bottom=wire2_bottom,
                                left=wire2_left,
                                top=wire2_top,
                                resolution=self.grid.resolution)
                      )
        width=4
        # draw central pad wire(bring from left ring)
        wire1_top = -3.5
        wire1_bottom = -4
        wire1_left = self.modu_centre[0] -(self.r_r_gap / 2 ) - self.r_core_cent-0.3
        wire1_right = self.modu_centre[0] + (self.r_r_gap / 2 ) + self.r_core_cent+0.3
        self.add_rect(layer=self.inner_electrode_ring_layers[-1],
                      bbox=BBox(right=wire1_right,
                                bottom=wire1_bottom,
                                left=wire1_left,
                                top=wire1_top,
                                resolution=self.grid.resolution)
                      )

        wire1_top = -3
        wire1_bottom = -3.5
        wire1_left = self.modu_centre[0] - (self.r_r_gap / 2) - self.r_core_cent +1
        wire1_right = self.modu_centre[0] + (self.r_r_gap / 2) + self.r_core_cent -1
        self.add_rect(layer=self.inner_electrode_ring_layers[-1],
                      bbox=BBox(right=wire1_right,
                                bottom=wire1_bottom,
                                left=wire1_left,
                                top=wire1_top,
                                resolution=self.grid.resolution)
                      )

        wire1_top = -2
        wire1_bottom = -3
        wire1_left = self.modu_centre[0] - (self.r_r_gap / 2) - self.r_core_cent+2.4
        wire1_right = self.modu_centre[0] + (self.r_r_gap / 2) + self.r_core_cent -2.4
        self.add_rect(layer=self.inner_electrode_ring_layers[-1],
                      bbox=BBox(right=wire1_right,
                                bottom=wire1_bottom,
                                left=wire1_left,
                                top=wire1_top,
                                resolution=self.grid.resolution)
                      )

        wire1_top = -1
        wire1_bottom = -2
        wire1_left = self.modu_centre[0] - (self.r_r_gap / 2) - self.r_core_cent + 2.85
        wire1_right = self.modu_centre[0] + (self.r_r_gap / 2) + self.r_core_cent - 2.85
        self.add_rect(layer=self.inner_electrode_ring_layers[-1],
                      bbox=BBox(right=wire1_right,
                                bottom=wire1_bottom,
                                left=wire1_left,
                                top=wire1_top,
                                resolution=self.grid.resolution)
                      )

        wire1_top = 0
        wire1_bottom = -1
        wire1_left = self.modu_centre[0] - (self.r_r_gap / 2) - self.r_core_cent + 3.1
        wire1_right = self.modu_centre[0] + (self.r_r_gap / 2) + self.r_core_cent - 3.1
        self.add_rect(layer=self.inner_electrode_ring_layers[-1],
                      bbox=BBox(right=wire1_right,
                                bottom=wire1_bottom,
                                left=wire1_left,
                                top=wire1_top,
                                resolution=self.grid.resolution)
                      )
        # vertical wire upto middle pad
        wire3_top = -4
        wire3_bottom = self.central_pad_loc[1]-dim1/2
        wire3_right = width/2
        wire3_left = - width/2
        self.add_rect(layer=self.inner_electrode_ring_layers[-1],
                      bbox=BBox(right=wire3_right,
                                bottom=wire3_bottom,
                                left=wire3_left,
                                top=wire3_top,
                                resolution=self.grid.resolution)
                      )

        wire1_top = 1
        wire1_bottom = -1
        wire1_left = 6.1/2
        wire1_right = 6.4/2
        self.add_rect(layer=self.inner_electrode_ring_layers[-1],
                      bbox=BBox(right=wire1_right,
                                bottom=wire1_bottom,
                                left=wire1_left,
                                top=wire1_top,
                                resolution=self.grid.resolution)
                      )

        wire1_top = 1
        wire1_bottom = -1
        wire1_left = -6.4 / 2
        wire1_right = -6.1 / 2
        self.add_rect(layer=self.inner_electrode_ring_layers[-1],
                      bbox=BBox(right=wire1_right,
                                bottom=wire1_bottom,
                                left=wire1_left,
                                top=wire1_top,
                                resolution=self.grid.resolution)
                      )

    def place_gs_electrodes(self):
        """
        Draws GS electrodes which are connected to ring electrodes
        """
        # Create GS pad
        gs_electrode_master = self.new_template(params=dict(top_layer=self.gs_pad_layer,
                                                            bottom_layer=self.inner_electrode_ring_layers[-1],
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

    def place_heater_contact_electrodes_basic(self):
        # calculate the corner coordinate of the left (ground) pad
        # calculate the corner coordinate of the left (ground) pad
        dim1 = 11.7
        dim2 = dim1  # 10.722 + 6.72 - 5.812
        self.left_heaterpad_loc = (self.modu_centre[0] - (self.gs_pad_pitch ) ,
                          self.modu_centre[1] + self.heater_pad_to_ring_dist
                          )
        self.central_heaterpad_loc = (self.modu_centre[0] ,
                                self.modu_centre[1] + self.heater_pad_to_ring_dist
                             )
        # calculate the corner coordinate of the right (signal) pad
        self.right_heaterpad_loc = (self.modu_centre[0] + (self.gs_pad_pitch),
                              self.modu_centre[1] + self.heater_pad_to_ring_dist
                              )

        rout = self.r_core_cent + self.core_width / 2
        ring_width = self.core_width / 2 + self.slab_width / 2
        rin = rout - ring_width
        p_via_radius = rin - self.p_via_radius_offset
        n_via_radius = rin - self.n_via_radius_offset
        if p_via_radius < n_via_radius:
            # inner electrode is p, outer is n

            electrode_width_p = self.electrode_width_inner
            electrode_rout_p = p_via_radius - self.electrode_offset
            inner_pn_radius = electrode_rout_p - electrode_width_p

            electrode_width_n = self.electrode_width_outer
            electrode_rin_n = n_via_radius + self.electrode_offset
            outer_pn_radius = electrode_rin_n + electrode_width_n

        else:

            p_electrode_layer_ind_list = self.outer_electrode_ring_layer_inds
            electrode_width_p = self.electrode_width_outer
            electrode_rin_p = p_via_radius + self.electrode_offset
            outer_pn_radius = electrode_rin_p + electrode_width_p

            electrode_width_n = self.electrode_width_inner
            electrode_rout_n = n_via_radius - self.electrode_offset
            inner_pn_radius = electrode_rout_n - electrode_width_n

        offset_distance = outer_pn_radius

        metal_width = 2
        # heater wiring to the left upper pad
        # D Wires
        # D0
        wire1_top = 30+self.modu_centre[1]
        wire1_bottom = -self.heater_electrode_top_y_span / 2-0.5+self.modu_centre[1]
        wire1_left = -self.contact_dist / 2 - (self.r_r_gap / 2 + self.core_width / 2) - self.r_core_cent - metal_width+self.modu_centre[0]
        wire1_right = wire1_left + metal_width
        self.add_rect(layer=self.heater_electrode_top_layer,
                      bbox=BBox(right=wire1_right,
                                bottom=wire1_bottom,
                                left=wire1_left,
                                top=wire1_top,
                                resolution=self.grid.resolution)
                      )
        
        # D1
        wire1_top =30+self.modu_centre[1]+1*metal_width
        wire1_bottom = 30+self.modu_centre[1]
        wire1_left = -self.contact_dist / 2 - (self.r_r_gap / 2 + self.core_width / 2) - self.r_core_cent - metal_width+self.modu_centre[0]
        wire1_right = self.modu_centre[0]+70
        self.add_rect(layer=self.heater_electrode_top_layer,
                    bbox=BBox(right=wire1_right,
                                bottom=wire1_bottom,
                                left=wire1_left,
                                top=wire1_top,
                                resolution=self.grid.resolution)
                    )
        # D2
        wire1_top =self.modu_centre[1]+150
        wire1_bottom = 30+self.modu_centre[1]
        wire1_left = self.modu_centre[0]+70
        wire1_right = self.modu_centre[0]+70+metal_width
        self.add_rect(layer=self.heater_electrode_top_layer,
                    bbox=BBox(right=wire1_right,
                                bottom=wire1_bottom,
                                left=wire1_left,
                                top=wire1_top,
                                resolution=self.grid.resolution)
                    )
        #D3
        wire1_top = self.modu_centre[1]+150
        wire1_bottom = self.modu_centre[1]+150-metal_width
        wire1_left = self.modu_centre[0]+20
        wire1_right = self.modu_centre[0]+70+metal_width
        self.add_rect(layer=self.heater_electrode_top_layer,
                    bbox=BBox(right=wire1_right,
                                bottom=wire1_bottom,
                                left=wire1_left,
                                top=wire1_top,
                                resolution=self.grid.resolution)
                    )
        #D4
        wire1_top = self.modu_centre[1]+150
        wire1_bottom = self.modu_centre[1]+90.5
        wire1_right = self.modu_centre[0]+20+metal_width
        wire1_left = self.modu_centre[0]+20

        self.add_rect(layer=self.heater_electrode_top_layer,
                    bbox=BBox(right=wire1_right,
                                bottom=wire1_bottom,
                                left=wire1_left,
                                top=wire1_top,
                                resolution=self.grid.resolution)
                    )
        
        #D5
        wire1_top = self.modu_centre[1]+90.5+0.5*metal_width
        wire1_bottom = self.modu_centre[1]+90.5-0.5*metal_width
        wire1_right = self.modu_centre[0]+20+metal_width
        wire1_left = self.modu_centre[0]

        self.add_rect(layer=self.heater_electrode_top_layer,
                    bbox=BBox(right=wire1_right,
                                bottom=wire1_bottom,
                                left=wire1_left,
                                top=wire1_top,
                                resolution=self.grid.resolution)
                    )
        
        via_stack_master = self.new_template(params=dict(top_layer=('LB', 'drawing'),
                                                         bottom_layer=('UA', 'drawing'),
                                                         top_x_span=14.6,
                                                         top_y_span=8.1,
                                                         bottom_x_span=14.6,
                                                         bottom_y_span=8.1,
                                                         align='center_align',
                                                         top_bot_offset=0.0),
                                             temp_cls=ViaStack)

        self.add_instance(master=via_stack_master,
                          inst_name='test_via_stack',
                          loc=(self.modu_centre[0]-100,self.modu_centre[1]+90.95),
                          orient='R0')
        self.add_instance(master=via_stack_master,
                          inst_name='test_via_stack',
                          loc=(self.modu_centre[0]+100,self.modu_centre[1]+90.95),
                          orient='R0')
        self.add_instance(master=via_stack_master,
                          inst_name='test_via_stack',
                          loc=(self.modu_centre[0],self.modu_centre[1]+90.95),
                          orient='R0')




        # # heater wiring to the right upper pad
        # A wire
        #A0
        wire1_top = 20+self.modu_centre[1]
        wire1_bottom = -self.heater_electrode_top_y_span / 2-0.5+self.modu_centre[1]
        wire1_left = self.contact_dist / 2 + (self.r_r_gap / 2 + self.core_width / 2) + self.r_core_cent+self.modu_centre[0]
        wire1_right = self.contact_dist / 2 + (self.r_r_gap / 2 + self.core_width / 2) + self.r_core_cent + metal_width+self.modu_centre[0]
        self.add_rect(layer=self.heater_electrode_top_layer,
                      bbox=BBox(right=wire1_right,
                                bottom=wire1_bottom,
                                left=wire1_left,
                                top=wire1_top,
                                resolution=self.grid.resolution)
                      )
        # A1
        wire1_top = 20+self.modu_centre[1]+0.5*metal_width
        wire1_bottom = 20+self.modu_centre[1]-0.5*metal_width
        wire1_left = self.contact_dist / 2 + (self.r_r_gap / 2 + self.core_width / 2) + self.r_core_cent+self.modu_centre[0]
        wire1_right = self.modu_centre[0]+100
        self.add_rect(layer=self.heater_electrode_top_layer,
                      bbox=BBox(right=wire1_right,
                                bottom=wire1_bottom,
                                left=wire1_left,
                                top=wire1_top,
                                resolution=self.grid.resolution)
                      )
        # A2
        wire1_top = self.modu_centre[1]+95
        wire1_bottom = 20+self.modu_centre[1]-0.5*metal_width
        wire1_left = self.modu_centre[0]+100-0.5*metal_width
        wire1_right = self.modu_centre[0]+100+0.5*metal_width
        self.add_rect(layer=self.heater_electrode_top_layer,
                      bbox=BBox(right=wire1_right,
                                bottom=wire1_bottom,
                                left=wire1_left,
                                top=wire1_top,
                                resolution=self.grid.resolution)
                      )
        
        

        # draw central upper pad wire(bring from left ring)
        # B WIRES C WIRES
        wire1_top = 3 * offset_distance+self.modu_centre[1]
        wire1_bottom = -self.heater_electrode_top_y_span / 2-0.5+self.modu_centre[1]
        wire1_left = self.contact_dist / 2 - (self.r_r_gap / 2 + self.core_width / 2) - self.r_core_cent+self.modu_centre[0]
        wire1_right = wire1_left + metal_width
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
        wire2_right = self.modu_centre[0]
        self.add_rect(layer=self.heater_electrode_top_layer,
                      bbox=BBox(right=wire2_right,
                                bottom=wire2_bottom,
                                left=wire2_left,
                                top=wire2_top,
                                resolution=self.grid.resolution)
                      )
        # C1
        wire_verticl_middle_bottom = wire1_top
        wire_verticl_middle_top = self.modu_centre[1]+26
        wire_verticl_middle_left = self.modu_centre[0]-metal_width/2
        wire_verticl_middle_right = self.modu_centre[0]+metal_width/2
        self.add_rect(layer=self.heater_electrode_top_layer,
                      bbox=BBox(right=wire_verticl_middle_right,
                                bottom=wire_verticl_middle_bottom,
                                left=wire_verticl_middle_left,
                                top=wire_verticl_middle_top,
                                resolution=self.grid.resolution)
                      )
        #C2
        wire_verticl_middle_bottom = self.modu_centre[1]+26-metal_width
        wire_verticl_middle_top = self.modu_centre[1]+26
        wire_verticl_middle_left = self.modu_centre[0]+metal_width/2
        wire_verticl_middle_right = self.modu_centre[0]+80
        self.add_rect(layer=self.heater_electrode_top_layer,
                      bbox=BBox(right=wire_verticl_middle_right,
                                bottom=wire_verticl_middle_bottom,
                                left=wire_verticl_middle_left,
                                top=wire_verticl_middle_top,
                                resolution=self.grid.resolution)
                      )
        #C3
        wire_verticl_middle_bottom = self.modu_centre[1]+26-metal_width
        wire_verticl_middle_top = self.modu_centre[1]+155
        wire_verticl_middle_left = self.modu_centre[0]+80-metal_width
        wire_verticl_middle_right = self.modu_centre[0]+80
        self.add_rect(layer=self.heater_electrode_top_layer,
                      bbox=BBox(right=wire_verticl_middle_right,
                                bottom=wire_verticl_middle_bottom,
                                left=wire_verticl_middle_left,
                                top=wire_verticl_middle_top,
                                resolution=self.grid.resolution)
                      )
        #C4
        wire_verticl_middle_bottom = self.modu_centre[1]+155
        wire_verticl_middle_top = self.modu_centre[1]+155+metal_width
        wire_verticl_middle_left = self.modu_centre[0]-100+20
        wire_verticl_middle_right = self.modu_centre[0]+80
        self.add_rect(layer=self.heater_electrode_top_layer,
                      bbox=BBox(right=wire_verticl_middle_right,
                                bottom=wire_verticl_middle_bottom,
                                left=wire_verticl_middle_left,
                                top=wire_verticl_middle_top,
                                resolution=self.grid.resolution)
                      )
        #C5
        wire_verticl_middle_bottom = self.modu_centre[1]+90.5
        wire_verticl_middle_top = self.modu_centre[1]+155+metal_width
        wire_verticl_middle_left = self.modu_centre[0]-100+20
        wire_verticl_middle_right = self.modu_centre[0]-100+20+metal_width
        self.add_rect(layer=self.heater_electrode_top_layer,
                      bbox=BBox(right=wire_verticl_middle_right,
                                bottom=wire_verticl_middle_bottom,
                                left=wire_verticl_middle_left,
                                top=wire_verticl_middle_top,
                                resolution=self.grid.resolution)
                      )
        
        #C6
        wire_verticl_middle_bottom = self.modu_centre[1]+90.5
        wire_verticl_middle_top = self.modu_centre[1]+90.5+metal_width
        wire_verticl_middle_left = self.modu_centre[0]-100
        wire_verticl_middle_right = self.modu_centre[0]-100+20+metal_width
        self.add_rect(layer=self.heater_electrode_top_layer,
                      bbox=BBox(right=wire_verticl_middle_right,
                                bottom=wire_verticl_middle_bottom,
                                left=wire_verticl_middle_left,
                                top=wire_verticl_middle_top,
                                resolution=self.grid.resolution)
                      )

        # draw central upper pad wire(bring from right ring)
        wire1_top = 3 * offset_distance+self.modu_centre[1]
        wire1_bottom = -self.heater_electrode_top_y_span / 2-0.5+self.modu_centre[1]
        wire1_right = -self.contact_dist / 2 + (self.r_r_gap / 2 + self.core_width / 2) + self.r_core_cent+self.modu_centre[0]
        wire1_left = wire1_right - metal_width
        self.add_rect(layer=self.heater_electrode_top_layer,
                      bbox=BBox(right=wire1_right,
                                bottom=wire1_bottom,
                                left=wire1_left,
                                top=wire1_top,
                                resolution=self.grid.resolution)
                      )
        wire2_top = wire1_top
        wire2_bottom = wire1_top - metal_width
        wire2_left = self.modu_centre[0]
        wire2_right = wire1_right
        self.add_rect(layer=self.heater_electrode_top_layer,
                      bbox=BBox(right=wire2_right,
                                bottom=wire2_bottom,
                                left=wire2_left,
                                top=wire2_top,
                                resolution=self.grid.resolution)
                      )

        
        
        
        
    def place_heater_contact_electrodes_basic_up(self):
        # calculate the corner coordinate of the left (ground) pad
        # calculate the corner coordinate of the left (ground) pad
        dim1 = 11.7
        dim2 = dim1  # 10.722 + 6.72 - 5.812
        self.left_heaterpad_loc = (self.modu_centre[0] - (self.gs_pad_pitch ) ,
                        self.modu_centre[1] + self.heater_pad_to_ring_dist
                        )
        self.central_heaterpad_loc = (self.modu_centre[0] ,
                                self.modu_centre[1] + self.heater_pad_to_ring_dist
                            )
        # calculate the corner coordinate of the right (signal) pad
        self.right_heaterpad_loc = (self.modu_centre[0] + (self.gs_pad_pitch),
                            self.modu_centre[1] + self.heater_pad_to_ring_dist
                            )

        rout = self.r_core_cent + self.core_width / 2
        ring_width = self.core_width / 2 + self.slab_width / 2
        rin = rout - ring_width
        p_via_radius = rin - self.p_via_radius_offset
        n_via_radius = rin - self.n_via_radius_offset
        if p_via_radius < n_via_radius:
            # inner electrode is p, outer is n

            electrode_width_p = self.electrode_width_inner
            electrode_rout_p = p_via_radius - self.electrode_offset
            inner_pn_radius = electrode_rout_p - electrode_width_p

            electrode_width_n = self.electrode_width_outer
            electrode_rin_n = n_via_radius + self.electrode_offset
            outer_pn_radius = electrode_rin_n + electrode_width_n

        else:

            p_electrode_layer_ind_list = self.outer_electrode_ring_layer_inds
            electrode_width_p = self.electrode_width_outer
            electrode_rin_p = p_via_radius + self.electrode_offset
            outer_pn_radius = electrode_rin_p + electrode_width_p

            electrode_width_n = self.electrode_width_inner
            electrode_rout_n = n_via_radius - self.electrode_offset
            inner_pn_radius = electrode_rout_n - electrode_width_n

        offset_distance = outer_pn_radius

        metal_width = 2
        # heater wiring to the left upper pad
        # A wires
        #A0
        wire1_bottom = -20+self.modu_centre[1]
        wire1_top = self.heater_electrode_top_y_span / 2+self.modu_centre[1]
        wire1_left = -self.contact_dist / 2 - (self.r_r_gap / 2 + self.core_width / 2) - self.r_core_cent - metal_width+self.modu_centre[0]
        wire1_right = wire1_left + metal_width
        self.add_rect(layer=self.heater_electrode_top_layer,
                    bbox=BBox(right=wire1_right,
                                bottom=wire1_bottom,
                                left=wire1_left,
                                top=wire1_top,
                                resolution=self.grid.resolution)
                    )
        #A1
        wire1_top = -20+self.modu_centre[1]+0.5*metal_width
        wire1_bottom = -20+self.modu_centre[1]-0.5*metal_width
        wire1_left = self.modu_centre[0]-100-0.5*metal_width
        wire1_right =  -self.contact_dist / 2 - (self.r_r_gap / 2 + self.core_width / 2) - self.r_core_cent - metal_width+self.modu_centre[0]+metal_width
        self.add_rect(layer=self.heater_electrode_top_layer,
                      bbox=BBox(right=wire1_right,
                                bottom=wire1_bottom,
                                left=wire1_left,
                                top=wire1_top,
                                resolution=self.grid.resolution)
                      )
        #A2
        wire1_top = -20+self.modu_centre[1]+0.5*metal_width
        wire1_bottom = self.modu_centre[1]-95
        wire1_left = self.modu_centre[0]-100-0.5*metal_width
        wire1_right = self.modu_centre[0]-100+0.5*metal_width
        self.add_rect(layer=self.heater_electrode_top_layer,
                      bbox=BBox(right=wire1_right,
                                bottom=wire1_bottom,
                                left=wire1_left,
                                top=wire1_top,
                                resolution=self.grid.resolution)
                      )
        
        
        
        via_stack_master = self.new_template(params=dict(top_layer=('LB', 'drawing'),
                                                         bottom_layer=('UA', 'drawing'),
                                                         top_x_span=14.6,
                                                         top_y_span=8.1,
                                                         bottom_x_span=14.6,
                                                         bottom_y_span=8.1,
                                                         align='center_align',
                                                         top_bot_offset=0.0),
                                             temp_cls=ViaStack)

        self.add_instance(master=via_stack_master,
                          inst_name='test_via_stack',
                          loc=(self.modu_centre[0]-100,self.modu_centre[1]-90.95),
                          orient='R0')
        self.add_instance(master=via_stack_master,
                          inst_name='test_via_stack',
                          loc=(self.modu_centre[0]+100,self.modu_centre[1]-90.95),
                          orient='R0')
        self.add_instance(master=via_stack_master,
                          inst_name='test_via_stack',
                          loc=(self.modu_centre[0],self.modu_centre[1]-90.95),
                          orient='R0')




        # # heater wiring to the right upper pad Wire D
        # D0
        wire1_top = self.heater_electrode_top_y_span / 2+self.modu_centre[1]
        wire1_bottom = -30+self.modu_centre[1]
        wire1_left = self.contact_dist / 2 + (self.r_r_gap / 2 + self.core_width / 2) + self.r_core_cent+self.modu_centre[0]
        wire1_right = self.contact_dist / 2 + (self.r_r_gap / 2 + self.core_width / 2) + self.r_core_cent + metal_width+self.modu_centre[0]
        self.add_rect(layer=self.heater_electrode_top_layer,
                    bbox=BBox(right=wire1_right,
                                bottom=wire1_bottom,
                                left=wire1_left,
                                top=wire1_top,
                                resolution=self.grid.resolution)
                    )
        # D1
        wire1_top =-30+self.modu_centre[1]
        wire1_bottom = -30+self.modu_centre[1]-1*metal_width
        wire1_left = self.modu_centre[0]-70
        wire1_right = self.contact_dist / 2 + (self.r_r_gap / 2 + self.core_width / 2) + self.r_core_cent + metal_width+self.modu_centre[0]
        self.add_rect(layer=self.heater_electrode_top_layer,
                    bbox=BBox(right=wire1_right,
                                bottom=wire1_bottom,
                                left=wire1_left,
                                top=wire1_top,
                                resolution=self.grid.resolution)
                    )
        # D2
        wire1_top =-30+self.modu_centre[1]
        wire1_bottom = self.modu_centre[1]-150
        wire1_left = self.modu_centre[0]-70-metal_width
        wire1_right = self.modu_centre[0]-70
        self.add_rect(layer=self.heater_electrode_top_layer,
                    bbox=BBox(right=wire1_right,
                                bottom=wire1_bottom,
                                left=wire1_left,
                                top=wire1_top,
                                resolution=self.grid.resolution)
                    )
        #D3
        wire1_top = self.modu_centre[1]-150+metal_width
        wire1_bottom = self.modu_centre[1]-150
        wire1_left = self.modu_centre[0]-70-metal_width
        wire1_right = self.modu_centre[0]-20
        self.add_rect(layer=self.heater_electrode_top_layer,
                    bbox=BBox(right=wire1_right,
                                bottom=wire1_bottom,
                                left=wire1_left,
                                top=wire1_top,
                                resolution=self.grid.resolution)
                    )
        #D4
        wire1_top = self.modu_centre[1]-90.5
        wire1_bottom = self.modu_centre[1]-150
        wire1_left = self.modu_centre[0]-20-metal_width
        wire1_right = self.modu_centre[0]-20
        self.add_rect(layer=self.heater_electrode_top_layer,
                    bbox=BBox(right=wire1_right,
                                bottom=wire1_bottom,
                                left=wire1_left,
                                top=wire1_top,
                                resolution=self.grid.resolution)
                    )
        
        #D5
        wire1_top = self.modu_centre[1]-90.5+0.5*metal_width
        wire1_bottom = self.modu_centre[1]-90.5-0.5*metal_width
        wire1_left = self.modu_centre[0]-20-metal_width
        wire1_right = self.modu_centre[0]
        self.add_rect(layer=self.heater_electrode_top_layer,
                    bbox=BBox(right=wire1_right,
                                bottom=wire1_bottom,
                                left=wire1_left,
                                top=wire1_top,
                                resolution=self.grid.resolution)
                    )
   


        # draw central upper pad wire(bring from left ring)
        wire1_top = self.heater_electrode_top_y_span / 2+self.modu_centre[1]
        wire1_bottom = -3 * offset_distance+self.modu_centre[1]
        wire1_left = self.contact_dist / 2 - (self.r_r_gap / 2 + self.core_width / 2) - self.r_core_cent+self.modu_centre[0]
        wire1_right = wire1_left + metal_width
        self.add_rect(layer=self.heater_electrode_top_layer,
                    bbox=BBox(right=wire1_right,
                                bottom=wire1_bottom,
                                left=wire1_left,
                                top=wire1_top,
                                resolution=self.grid.resolution)
                    )
        wire2_top = wire1_bottom+metal_width
        wire2_bottom = wire1_bottom
        wire2_left = wire1_left
        wire2_right = self.modu_centre[0]
        self.add_rect(layer=self.heater_electrode_top_layer,
                    bbox=BBox(right=wire2_right,
                                bottom=wire2_bottom,
                                left=wire2_left,
                                top=wire2_top,
                                resolution=self.grid.resolution)
                    )

        # draw central upper pad wire(bring from right ring)
        # B Wire C Wire
        wire1_top = self.heater_electrode_top_y_span / 2+self.modu_centre[1]
        wire1_bottom = -3 * offset_distance+self.modu_centre[1]
        wire1_right = -self.contact_dist / 2 + (self.r_r_gap / 2 + self.core_width / 2) + self.r_core_cent+self.modu_centre[0]
        wire1_left = wire1_right - metal_width
        self.add_rect(layer=self.heater_electrode_top_layer,
                    bbox=BBox(right=wire1_right,
                                bottom=wire1_bottom,
                                left=wire1_left,
                                top=wire1_top,
                                resolution=self.grid.resolution)
                    )
        wire2_top = wire1_bottom+metal_width
        wire2_bottom = wire1_bottom
        wire2_left = self.modu_centre[0]
        wire2_right = wire1_right
        self.add_rect(layer=self.heater_electrode_top_layer,
                    bbox=BBox(right=wire2_right,
                                bottom=wire2_bottom,
                                left=wire2_left,
                                top=wire2_top,
                                resolution=self.grid.resolution)
                    )
        # C1
        wire_verticl_middle_bottom = self.modu_centre[1]-26
        wire_verticl_middle_top = wire1_bottom 
        wire_verticl_middle_left = self.modu_centre[0]-metal_width/2
        wire_verticl_middle_right = self.modu_centre[0]+metal_width/2
        self.add_rect(layer=self.heater_electrode_top_layer,
                      bbox=BBox(right=wire_verticl_middle_right,
                                bottom=wire_verticl_middle_bottom,
                                left=wire_verticl_middle_left,
                                top=wire_verticl_middle_top,
                                resolution=self.grid.resolution)
                      )
        #C2
        wire_verticl_middle_bottom = self.modu_centre[1]-26
        wire_verticl_middle_top = wire_verticl_middle_bottom+metal_width
        wire_verticl_middle_left = self.modu_centre[0]-80
        wire_verticl_middle_right = self.modu_centre[0]+metal_width/2
        self.add_rect(layer=self.heater_electrode_top_layer,
                      bbox=BBox(right=wire_verticl_middle_right,
                                bottom=wire_verticl_middle_bottom,
                                left=wire_verticl_middle_left,
                                top=wire_verticl_middle_top,
                                resolution=self.grid.resolution)
                      )
        #C3
        wire_verticl_middle_bottom = self.modu_centre[1]-155-metal_width
        wire_verticl_middle_top = self.modu_centre[1]-26+metal_width
        wire_verticl_middle_left = self.modu_centre[0]-80
        wire_verticl_middle_right = self.modu_centre[0]-80+metal_width
        self.add_rect(layer=self.heater_electrode_top_layer,
                      bbox=BBox(right=wire_verticl_middle_right,
                                bottom=wire_verticl_middle_bottom,
                                left=wire_verticl_middle_left,
                                top=wire_verticl_middle_top,
                                resolution=self.grid.resolution)
                      )
        #C4
        wire_verticl_middle_bottom = self.modu_centre[1]-155-metal_width
        wire_verticl_middle_top = self.modu_centre[1]-155
        wire_verticl_middle_left = self.modu_centre[0]-80
        wire_verticl_middle_right = self.modu_centre[0]+100-20
        self.add_rect(layer=self.heater_electrode_top_layer,
                      bbox=BBox(right=wire_verticl_middle_right,
                                bottom=wire_verticl_middle_bottom,
                                left=wire_verticl_middle_left,
                                top=wire_verticl_middle_top,
                                resolution=self.grid.resolution)
                      )
        #C5
        wire_verticl_middle_bottom = self.modu_centre[1]-155-metal_width
        wire_verticl_middle_top = self.modu_centre[1]-90.5
        wire_verticl_middle_left = self.modu_centre[0]+100-20-metal_width
        wire_verticl_middle_right = self.modu_centre[0]+100-20
        self.add_rect(layer=self.heater_electrode_top_layer,
                      bbox=BBox(right=wire_verticl_middle_right,
                                bottom=wire_verticl_middle_bottom,
                                left=wire_verticl_middle_left,
                                top=wire_verticl_middle_top,
                                resolution=self.grid.resolution)
                      )
        
        #C6
        wire_verticl_middle_bottom = self.modu_centre[1]-90.5-0.5*metal_width
        wire_verticl_middle_top = self.modu_centre[1]-90.5+0.5*metal_width
        wire_verticl_middle_left = self.modu_centre[0]+100-20-metal_width
        wire_verticl_middle_right = self.modu_centre[0]+100
        self.add_rect(layer=self.heater_electrode_top_layer,
                      bbox=BBox(right=wire_verticl_middle_right,
                                bottom=wire_verticl_middle_bottom,
                                left=wire_verticl_middle_left,
                                top=wire_verticl_middle_top,
                                resolution=self.grid.resolution)
                      )
        
    
        
        
    # vertical wire upto upto middle pad
    def place_contact_electrodes_basic_up(self):
        # calculate the corner coordinate of the left (ground) pad
        # calculate the corner coordinate of the left (ground) pad

        rout = self.r_core_cent + self.core_width / 2
        ring_width = self.core_width / 2 + self.slab_width / 2
        rin = rout - ring_width
        p_via_radius = rin - self.p_via_radius_offset
        n_via_radius = rin - self.n_via_radius_offset
        if p_via_radius < n_via_radius:
            # inner electrode is p, outer is n

            electrode_width_p = self.electrode_width_inner
            electrode_rout_p = p_via_radius - self.electrode_offset
            inner_pn_radius = electrode_rout_p - electrode_width_p

            electrode_width_n = self.electrode_width_outer
            electrode_rin_n = n_via_radius + self.electrode_offset
            outer_pn_radius = electrode_rin_n + electrode_width_n

        else:

            p_electrode_layer_ind_list = self.outer_electrode_ring_layer_inds
            electrode_width_p = self.electrode_width_outer
            electrode_rin_p = p_via_radius + self.electrode_offset
            outer_pn_radius = electrode_rin_p + electrode_width_p

            electrode_width_n = self.electrode_width_inner
            electrode_rout_n = n_via_radius - self.electrode_offset
            inner_pn_radius = electrode_rout_n - electrode_width_n

        dim1 = 11.7
        dim2 = dim1  # 10.722 + 6.72 - 5.812
        self.left_pad_loc = (self.modu_centre[0] - (self.gs_pad_pitch ) ,
                          self.modu_centre[1] - self.gs_pad_to_ring_dist
                          )
        self.central_pad_loc = (self.modu_centre[0] ,
                                self.modu_centre[1] - self.gs_pad_to_ring_dist
                             )
        # calculate the corner coordinate of the right (signal) pad
        self.right_pad_loc = (self.modu_centre[0] + (self.gs_pad_pitch),
                              self.modu_centre[1] - self.gs_pad_to_ring_dist
                              )
        offset_distance = outer_pn_radius

        width = 2
        # draw left pad wiring
        # y WIRES
        # y0
        wire1_bottom = self.modu_centre[1]-0.5*width
        wire1_top = self.modu_centre[1] + 0.5*width
        wire1_left = -100+self.modu_centre[0]-width/2
        wire1_right = self.modu_centre[0] - (self.r_r_gap / 2 + self.core_width / 2) - self.r_core_cent - offset_distance+0.35
        self.add_rect(layer=self.outer_electrode_ring_layers[-1],
                      bbox=BBox(right=wire1_right,
                                bottom=wire1_bottom,
                                left=wire1_left,
                                top=wire1_top,
                                resolution=self.grid.resolution)
                      )
        # y0 patch
        wire1_bottom = self.modu_centre[1]-0.5*width-0.91
        wire1_top = self.modu_centre[1] + 0.5*width+0.91
        wire1_right = self.modu_centre[0] - (self.r_r_gap / 2 + self.core_width / 2) - self.r_core_cent - offset_distance+0.35
        wire1_left = wire1_right-0.5*width

        self.add_rect(layer=self.outer_electrode_ring_layers[-1],
                      bbox=BBox(right=wire1_right,
                                bottom=wire1_bottom,
                                left=wire1_left,
                                top=wire1_top,
                                resolution=self.grid.resolution)
                      )
        #y1
        wire1_bottom = self.modu_centre[1]
        wire1_top = self.modu_centre[1]+15
        wire1_left = -100+self.modu_centre[0]-width/2
        wire1_right = wire1_left+width
        self.add_rect(layer=self.outer_electrode_ring_layers[-1],
                      bbox=BBox(right=wire1_right,
                                bottom=wire1_bottom,
                                left=wire1_left,
                                top=wire1_top,
                                resolution=self.grid.resolution)
                      )
        

        # draw right pad wire
        # z wires
        # z0
        wire1_top = self.modu_centre[1]+0.5*width
        wire1_bottom = self.modu_centre[1]-0.5*width
        wire1_left = self.modu_centre[0] + (self.r_r_gap / 2 + self.core_width / 2) + self.r_core_cent + offset_distance-0.35
        wire1_right = width/2+100+self.modu_centre[0]
        self.add_rect(layer=self.outer_electrode_ring_layers[-1],
                      bbox=BBox(right=wire1_right,
                                bottom=wire1_bottom,
                                left=wire1_left,
                                top=wire1_top,
                                resolution=self.grid.resolution)
                      )
        
        # z0 patch
        wire1_bottom = self.modu_centre[1]-0.5*width-0.91
        wire1_top = self.modu_centre[1] + 0.5*width+0.91
        wire1_left = self.modu_centre[0] + (self.r_r_gap / 2 + self.core_width / 2) + self.r_core_cent + offset_distance-0.35
        wire1_right = wire1_left+0.5*width
        self.add_rect(layer=self.outer_electrode_ring_layers[-1],
                bbox=BBox(right=wire1_right,
                        bottom=wire1_bottom,
                        left=wire1_left,
                        top=wire1_top,
                        resolution=self.grid.resolution)
                )

        # z1
        wire1_bottom = self.modu_centre[1]
        wire1_top = wire1_bottom+15
        wire1_right = 100+self.modu_centre[0]+width/2
        wire1_left = wire1_right-width
        self.add_rect(layer=self.outer_electrode_ring_layers[-1],
                      bbox=BBox(right=wire1_right,
                                bottom=wire1_bottom,
                                left=wire1_left,
                                top=wire1_top,
                                resolution=self.grid.resolution)
                      )
        
        
        width = 4
        
        wire1_bottom = 3.5 + self.modu_centre[1]
        wire1_top = 4+ self.modu_centre[1]
        wire1_left = self.modu_centre[0] - (self.r_r_gap / 2) - self.r_core_cent - 0.3
        wire1_right = self.modu_centre[0] + (self.r_r_gap / 2) + self.r_core_cent + 0.3
        self.add_rect(layer=self.inner_electrode_ring_layers[-1],
                      bbox=BBox(right=wire1_right,
                                bottom=wire1_bottom,
                                left=wire1_left,
                                top=wire1_top,
                                resolution=self.grid.resolution)
                      )

        wire1_bottom = 3+ self.modu_centre[1]
        wire1_top = 3.5+ self.modu_centre[1]
        wire1_left = self.modu_centre[0] - (self.r_r_gap / 2) - self.r_core_cent + 0.2
        wire1_right = self.modu_centre[0] + (self.r_r_gap / 2) + self.r_core_cent - 0.2
        self.add_rect(layer=self.inner_electrode_ring_layers[-1],
                      bbox=BBox(right=wire1_right,
                                bottom=wire1_bottom,
                                left=wire1_left,
                                top=wire1_top,
                                resolution=self.grid.resolution)
                      )
        
        wire1_bottom = 2.5+ self.modu_centre[1]
        wire1_top = 3+ self.modu_centre[1]
        wire1_left = self.modu_centre[0] - (self.r_r_gap / 2) - self.r_core_cent + 1.6
        wire1_right = self.modu_centre[0] + (self.r_r_gap / 2) + self.r_core_cent - 1.6
        self.add_rect(layer=self.inner_electrode_ring_layers[-1],
                      bbox=BBox(right=wire1_right,
                                bottom=wire1_bottom,
                                left=wire1_left,
                                top=wire1_top,
                                resolution=self.grid.resolution)
                      )

        wire1_bottom = 2+ self.modu_centre[1]
        wire1_top = 2.5+ self.modu_centre[1]
        wire1_left = self.modu_centre[0] - (self.r_r_gap / 2) - self.r_core_cent + 2
        wire1_right = self.modu_centre[0] + (self.r_r_gap / 2) + self.r_core_cent - 2
        self.add_rect(layer=self.inner_electrode_ring_layers[-1],
                      bbox=BBox(right=wire1_right,
                                bottom=wire1_bottom,
                                left=wire1_left,
                                top=wire1_top,
                                resolution=self.grid.resolution)
                      )

        wire1_bottom = 1+ self.modu_centre[1]
        wire1_top = 2+ self.modu_centre[1]
        wire1_left = self.modu_centre[0] - (self.r_r_gap / 2) - self.r_core_cent + 2.65
        wire1_right = self.modu_centre[0] + (self.r_r_gap / 2) + self.r_core_cent - 2.65
        self.add_rect(layer=self.inner_electrode_ring_layers[-1],
                      bbox=BBox(right=wire1_right,
                                bottom=wire1_bottom,
                                left=wire1_left,
                                top=wire1_top,
                                resolution=self.grid.resolution)
                      )

        wire1_bottom = 0+ self.modu_centre[1]
        wire1_top = 1+ self.modu_centre[1]
        wire1_left = self.modu_centre[0] - (self.r_r_gap / 2) - self.r_core_cent + 2.5
        wire1_right = self.modu_centre[0] + (self.r_r_gap / 2) + self.r_core_cent - 2.5
        self.add_rect(layer=self.inner_electrode_ring_layers[-1],
                      bbox=BBox(right=wire1_right,
                                bottom=wire1_bottom,
                                left=wire1_left,
                                top=wire1_top,
                                resolution=self.grid.resolution)
                      )
        wire1_top = 1+ self.modu_centre[1]
        wire1_bottom = -1+ self.modu_centre[1]
        wire1_left = self.modu_centre[0] - (self.r_r_gap / 2) - self.r_core_cent + 2.5
        wire1_right = self.modu_centre[0] - (self.r_r_gap / 2) - self.r_core_cent + 2.8
        self.add_rect(layer=self.inner_electrode_ring_layers[-1],
                      bbox=BBox(right=wire1_right,
                                bottom=wire1_bottom,
                                left=wire1_left,
                                top=wire1_top,
                                resolution=self.grid.resolution)
                      )
        wire1_top = 1+ self.modu_centre[1]
        wire1_bottom = -1+ self.modu_centre[1]
        wire1_left = self.modu_centre[0] + (self.r_r_gap / 2) + self.r_core_cent - 2.8
        wire1_right = self.modu_centre[0] + (self.r_r_gap / 2) + self.r_core_cent - 2.5
        self.add_rect(layer=self.inner_electrode_ring_layers[-1],
                      bbox=BBox(right=wire1_right,
                                bottom=wire1_bottom,
                                left=wire1_left,
                                top=wire1_top,
                                resolution=self.grid.resolution)
                      )
        # vertical wire upto middle pad
        wire3_bottom = 4+ self.modu_centre[1]
        wire3_top = 15+ self.modu_centre[1] #self.central_pad_loc[1] - dim1 / 2
        wire3_right = width / 2+ self.modu_centre[0]
        wire3_left = - width / 2+ self.modu_centre[0]
        self.add_rect(layer=self.inner_electrode_ring_layers[-1],
                      bbox=BBox(right=wire3_right,
                                bottom=wire3_bottom,
                                left=wire3_left,
                                top=wire3_top,
                                resolution=self.grid.resolution)
                      )
        
    

        wire1_top = 1+ self.modu_centre[1]
        wire1_bottom = -1+ self.modu_centre[1]
        wire1_left = 6.1 / 2+ self.modu_centre[0]
        wire1_right = 6.4 / 2+ self.modu_centre[0]
        self.add_rect(layer=self.inner_electrode_ring_layers[-1],
                      bbox=BBox(right=wire1_right,
                                bottom=wire1_bottom,
                                left=wire1_left,
                                top=wire1_top,
                                resolution=self.grid.resolution)
                      )

        wire1_top = 1+ self.modu_centre[1]
        wire1_bottom = -1+ self.modu_centre[1]
        wire1_left = -6.4 / 2+ self.modu_centre[0]
        wire1_right = -6.1 / 2+ self.modu_centre[0]
        self.add_rect(layer=self.inner_electrode_ring_layers[-1],
                      bbox=BBox(right=wire1_right,
                                bottom=wire1_bottom,
                                left=wire1_left,
                                top=wire1_top,
                                resolution=self.grid.resolution)
                      )
        
        via_stack_master = self.new_template(params=dict(top_layer=('LB', 'drawing'),
                                                         bottom_layer=('M5', 'drawing'),
                                                         top_x_span=14.6,
                                                         top_y_span=8.1,
                                                         bottom_x_span=14.6,
                                                         bottom_y_span=8.1,
                                                         align='center_align',
                                                         top_bot_offset=0.0),
                                             temp_cls=ViaStack)
        middle_via_stack_master = self.new_template(params=dict(top_layer=('LB', 'drawing'),
                                                         bottom_layer=('BA', 'drawing'),
                                                         top_x_span=14.6,
                                                         top_y_span=8.1,
                                                         bottom_x_span=14.6,
                                                         bottom_y_span=8.1,
                                                         align='center_align',
                                                         top_bot_offset=0.0),
                                             temp_cls=ViaStack)

        self.add_instance(master=middle_via_stack_master,
                          inst_name='test_via_stack',
                          loc=(self.modu_centre[0],self.modu_centre[1]+10.95),
                          orient='R0')
        self.add_instance(master=via_stack_master,
                          inst_name='test_via_stack',
                          loc=(self.modu_centre[0]-100,self.modu_centre[1]+10.95),
                          orient='R0')
        self.add_instance(master=via_stack_master,
                          inst_name='test_via_stack',
                          loc=(self.modu_centre[0]+100,self.modu_centre[1]+10.95),
                          orient='R0')
        
        
    def place_contact_electrodes_basic(self):
        # calculate the corner coordinate of the left (ground) pad
        # calculate the corner coordinate of the left (ground) pad

        rout = self.r_core_cent + self.core_width / 2
        ring_width = self.core_width / 2 + self.slab_width / 2
        rin = rout - ring_width
        p_via_radius = rin - self.p_via_radius_offset
        n_via_radius = rin - self.n_via_radius_offset
        if p_via_radius < n_via_radius:
            # inner electrode is p, outer is n

            electrode_width_p = self.electrode_width_inner
            electrode_rout_p = p_via_radius - self.electrode_offset
            inner_pn_radius = electrode_rout_p - electrode_width_p

            electrode_width_n = self.electrode_width_outer
            electrode_rin_n = n_via_radius + self.electrode_offset
            outer_pn_radius = electrode_rin_n + electrode_width_n

        else:

            p_electrode_layer_ind_list = self.outer_electrode_ring_layer_inds
            electrode_width_p = self.electrode_width_outer
            electrode_rin_p = p_via_radius + self.electrode_offset
            outer_pn_radius = electrode_rin_p + electrode_width_p

            electrode_width_n = self.electrode_width_inner
            electrode_rout_n = n_via_radius - self.electrode_offset
            inner_pn_radius = electrode_rout_n - electrode_width_n

        dim1 = 11.7
        dim2 = dim1  # 10.722 + 6.72 - 5.812
        self.left_pad_loc = (self.modu_centre[0] - (self.gs_pad_pitch ) ,
                          self.modu_centre[1] - self.gs_pad_to_ring_dist
                          )
        self.central_pad_loc = (self.modu_centre[0] ,
                                self.modu_centre[1] - self.gs_pad_to_ring_dist
                             )
        # calculate the corner coordinate of the right (signal) pad
        self.right_pad_loc = (self.modu_centre[0] + (self.gs_pad_pitch),
                              self.modu_centre[1] - self.gs_pad_to_ring_dist
                              )
        offset_distance = outer_pn_radius

        width = 2
        # draw left pad wiring
        # Z wires
        # z0
        wire1_top = self.modu_centre[1]+0.5*width
        wire1_bottom = self.modu_centre[1] - 0.5*width
        wire1_left = -100+self.modu_centre[0]-width/2
        wire1_right = self.modu_centre[0] - (self.r_r_gap / 2 + self.core_width / 2) - self.r_core_cent - offset_distance+0.35
        self.add_rect(layer=self.outer_electrode_ring_layers[-1],
                      bbox=BBox(right=wire1_right,
                                bottom=wire1_bottom,
                                left=wire1_left,
                                top=wire1_top,
                                resolution=self.grid.resolution)
                      )
        # z0 patch
        wire1_bottom = self.modu_centre[1]-0.5*width-0.91
        wire1_top = self.modu_centre[1] + 0.5*width+0.91
        wire1_right = self.modu_centre[0] - (self.r_r_gap / 2 + self.core_width / 2) - self.r_core_cent - offset_distance+0.35
        wire1_left = wire1_right-0.5*width

        self.add_rect(layer=self.outer_electrode_ring_layers[-1],
                      bbox=BBox(right=wire1_right,
                                bottom=wire1_bottom,
                                left=wire1_left,
                                top=wire1_top,
                                resolution=self.grid.resolution)
                      )
        # z1
        wire1_top = self.modu_centre[1]
        wire1_bottom = self.modu_centre[1]-15
        wire1_left = -100+self.modu_centre[0]-width/2
        wire1_right = wire1_left+width
        self.add_rect(layer=self.outer_electrode_ring_layers[-1],
                      bbox=BBox(right=wire1_right,
                                bottom=wire1_bottom,
                                left=wire1_left,
                                top=wire1_top,
                                resolution=self.grid.resolution)
                      )


        # draw right pad wire
        # Y wires
        # y0
        wire1_top = self.modu_centre[1]+0.5*width
        wire1_bottom = self.modu_centre[1] - 0.5*width
        wire1_left = self.modu_centre[0] + (self.r_r_gap / 2 + self.core_width / 2) + self.r_core_cent + offset_distance-0.35
        wire1_right = 100+self.modu_centre[0]+width/2
        self.add_rect(layer=self.outer_electrode_ring_layers[-1],
                      bbox=BBox(right=wire1_right,
                                bottom=wire1_bottom,
                                left=wire1_left,
                                top=wire1_top,
                                resolution=self.grid.resolution)
                      )
        # y0 patch
        wire1_bottom = self.modu_centre[1]-0.5*width-0.91
        wire1_top = self.modu_centre[1] + 0.5*width+0.91
        wire1_left = self.modu_centre[0] +(self.r_r_gap / 2 + self.core_width / 2) + self.r_core_cent + offset_distance - 0.35
        wire1_right = wire1_left+0.5*width

        self.add_rect(layer=self.outer_electrode_ring_layers[-1],
                      bbox=BBox(right=wire1_right,
                                bottom=wire1_bottom,
                                left=wire1_left,
                                top=wire1_top,
                                resolution=self.grid.resolution)
                      )
        
        # y1
        wire1_top = self.modu_centre[1]
        wire1_bottom = self.modu_centre[1]-15
        wire1_right = 100+self.modu_centre[0]+width/2
        wire1_left = wire1_right-width
        self.add_rect(layer=self.outer_electrode_ring_layers[-1],
                      bbox=BBox(right=wire1_right,
                                bottom=wire1_bottom,
                                left=wire1_left,
                                top=wire1_top,
                                resolution=self.grid.resolution)
                      )
        
        
        width = 4
        # draw central pad wire(bring from left ring)
        wire1_top = -3.5 + self.modu_centre[1]
        wire1_bottom = -4+ self.modu_centre[1]
        wire1_left = self.modu_centre[0] - (self.r_r_gap / 2) - self.r_core_cent - 0.3
        wire1_right = self.modu_centre[0] + (self.r_r_gap / 2) + self.r_core_cent + 0.3
        self.add_rect(layer=self.inner_electrode_ring_layers[-1],
                      bbox=BBox(right=wire1_right,
                                bottom=wire1_bottom,
                                left=wire1_left,
                                top=wire1_top,
                                resolution=self.grid.resolution)
                      )

        wire1_top = -3+ self.modu_centre[1]
        wire1_bottom = -3.5+ self.modu_centre[1]
        wire1_left = self.modu_centre[0] - (self.r_r_gap / 2) - self.r_core_cent + 0.2
        wire1_right = self.modu_centre[0] + (self.r_r_gap / 2) + self.r_core_cent - 0.2
        self.add_rect(layer=self.inner_electrode_ring_layers[-1],
                      bbox=BBox(right=wire1_right,
                                bottom=wire1_bottom,
                                left=wire1_left,
                                top=wire1_top,
                                resolution=self.grid.resolution)
                      )

        wire1_top = -2.5+ self.modu_centre[1]
        wire1_bottom = -3+ self.modu_centre[1]
        wire1_left = self.modu_centre[0] - (self.r_r_gap / 2) - self.r_core_cent + 1.6
        wire1_right = self.modu_centre[0] + (self.r_r_gap / 2) + self.r_core_cent - 1.6
        self.add_rect(layer=self.inner_electrode_ring_layers[-1],
                      bbox=BBox(right=wire1_right,
                                bottom=wire1_bottom,
                                left=wire1_left,
                                top=wire1_top,
                                resolution=self.grid.resolution)
                      )
        
        wire1_top = -2+ self.modu_centre[1]
        wire1_bottom = -2.5+ self.modu_centre[1]
        wire1_left = self.modu_centre[0] - (self.r_r_gap / 2) - self.r_core_cent + 2
        wire1_right = self.modu_centre[0] + (self.r_r_gap / 2) + self.r_core_cent - 2
        self.add_rect(layer=self.inner_electrode_ring_layers[-1],
                      bbox=BBox(right=wire1_right,
                                bottom=wire1_bottom,
                                left=wire1_left,
                                top=wire1_top,
                                resolution=self.grid.resolution)
                      )

        wire1_top = -1+ self.modu_centre[1]
        wire1_bottom = -2+ self.modu_centre[1]
        wire1_left = self.modu_centre[0] - (self.r_r_gap / 2) - self.r_core_cent + 2.65
        wire1_right = self.modu_centre[0] + (self.r_r_gap / 2) + self.r_core_cent - 2.65
        self.add_rect(layer=self.inner_electrode_ring_layers[-1],
                      bbox=BBox(right=wire1_right,
                                bottom=wire1_bottom,
                                left=wire1_left,
                                top=wire1_top,
                                resolution=self.grid.resolution)
                      )

        wire1_top = 0+ self.modu_centre[1]
        wire1_bottom = -1+ self.modu_centre[1]
        wire1_left = self.modu_centre[0] - (self.r_r_gap / 2) - self.r_core_cent + 2.5
        wire1_right = self.modu_centre[0] + (self.r_r_gap / 2) + self.r_core_cent - 2.5
        self.add_rect(layer=self.inner_electrode_ring_layers[-1],
                      bbox=BBox(right=wire1_right,
                                bottom=wire1_bottom,
                                left=wire1_left,
                                top=wire1_top,
                                resolution=self.grid.resolution)
                      )
        wire1_top = 1+ self.modu_centre[1]
        wire1_bottom = -1+ self.modu_centre[1]
        wire1_left = self.modu_centre[0] - (self.r_r_gap / 2) - self.r_core_cent + 2.5
        wire1_right = self.modu_centre[0] - (self.r_r_gap / 2) - self.r_core_cent + 2.8
        self.add_rect(layer=self.inner_electrode_ring_layers[-1],
                      bbox=BBox(right=wire1_right,
                                bottom=wire1_bottom,
                                left=wire1_left,
                                top=wire1_top,
                                resolution=self.grid.resolution)
                      )
        wire1_top = 1+ self.modu_centre[1]
        wire1_bottom = -1+ self.modu_centre[1]
        wire1_left = self.modu_centre[0] + (self.r_r_gap / 2) + self.r_core_cent - 2.8
        wire1_right = self.modu_centre[0] + (self.r_r_gap / 2) + self.r_core_cent - 2.5
        self.add_rect(layer=self.inner_electrode_ring_layers[-1],
                      bbox=BBox(right=wire1_right,
                                bottom=wire1_bottom,
                                left=wire1_left,
                                top=wire1_top,
                                resolution=self.grid.resolution)
                      )
        # vertical wire upto middle pad
        #x0 x wires
        wire3_top = -4+ self.modu_centre[1]
        wire3_bottom = -10.95+ self.modu_centre[1] #self.central_pad_loc[1] - dim1 / 2
        wire3_right = width / 2+ self.modu_centre[0]
        wire3_left = - width / 2+ self.modu_centre[0]
        self.add_rect(layer=self.inner_electrode_ring_layers[-1],
                      bbox=BBox(right=wire3_right,
                                bottom=wire3_bottom,
                                left=wire3_left,
                                top=wire3_top,
                                resolution=self.grid.resolution)
                      )

        wire1_top = 1+ self.modu_centre[1]
        wire1_bottom = -1+ self.modu_centre[1]
        wire1_left = 6.1 / 2+ self.modu_centre[0]
        wire1_right = 6.4 / 2+ self.modu_centre[0]
        self.add_rect(layer=self.inner_electrode_ring_layers[-1],
                      bbox=BBox(right=wire1_right,
                                bottom=wire1_bottom,
                                left=wire1_left,
                                top=wire1_top,
                                resolution=self.grid.resolution)
                      )

        wire1_top = 1+ self.modu_centre[1]
        wire1_bottom = -1+ self.modu_centre[1]
        wire1_left = -6.4 / 2+ self.modu_centre[0]
        wire1_right = -6.1 / 2+ self.modu_centre[0]
        self.add_rect(layer=self.inner_electrode_ring_layers[-1],
                      bbox=BBox(right=wire1_right,
                                bottom=wire1_bottom,
                                left=wire1_left,
                                top=wire1_top,
                                resolution=self.grid.resolution)
                      )
        
        via_stack_master = self.new_template(params=dict(top_layer=('LB', 'drawing'),
                                                         bottom_layer=('M5', 'drawing'),
                                                         top_x_span=14.6,
                                                         top_y_span=8.1,
                                                         bottom_x_span=14.6,
                                                         bottom_y_span=8.1,
                                                         align='center_align',
                                                         top_bot_offset=0.0),
                                             temp_cls=ViaStack)
        middle_via_stack_master = self.new_template(params=dict(top_layer=('LB', 'drawing'),
                                                         bottom_layer=('BA', 'drawing'),
                                                         top_x_span=14.6,
                                                         top_y_span=8.1,
                                                         bottom_x_span=14.6,
                                                         bottom_y_span=8.1,
                                                         align='center_align',
                                                         top_bot_offset=0.0),
                                             temp_cls=ViaStack)

        self.add_instance(master=middle_via_stack_master,
                          inst_name='test_via_stack',
                          loc=(self.modu_centre[0],self.modu_centre[1]-10.95),
                          orient='R0')
        self.add_instance(master=via_stack_master,
                          inst_name='test_via_stack',
                          loc=(self.modu_centre[0]-100,self.modu_centre[1]-10.95),
                          orient='R0')
        self.add_instance(master=via_stack_master,
                          inst_name='test_via_stack',
                          loc=(self.modu_centre[0]+100,self.modu_centre[1]-10.95),
                          orient='R0')
        
    
    def place_heater_contact_electrodes(self):
        # calculate the corner coordinate of the left (ground) pad
        # calculate the corner coordinate of the left (ground) pad
        dim1 = 11.7
        dim2 = dim1  # 10.722 + 6.72 - 5.812
        self.left_heaterpad_loc = (self.modu_centre[0] - (self.gs_pad_pitch ) ,
                          self.modu_centre[1] + self.heater_pad_to_ring_dist
                          )
        self.central_heaterpad_loc = (self.modu_centre[0] ,
                                self.modu_centre[1] + self.heater_pad_to_ring_dist
                             )
        # calculate the corner coordinate of the right (signal) pad
        self.right_heaterpad_loc = (self.modu_centre[0] + (self.gs_pad_pitch),
                              self.modu_centre[1] + self.heater_pad_to_ring_dist
                              )

        rout = self.r_core_cent + self.core_width / 2
        ring_width = self.core_width / 2 + self.slab_width / 2
        rin = rout - ring_width
        p_via_radius = rin - self.p_via_radius_offset
        n_via_radius = rin - self.n_via_radius_offset
        if p_via_radius < n_via_radius:
            # inner electrode is p, outer is n

            electrode_width_p = self.electrode_width_inner
            electrode_rout_p = p_via_radius - self.electrode_offset
            inner_pn_radius = electrode_rout_p - electrode_width_p

            electrode_width_n = self.electrode_width_outer
            electrode_rin_n = n_via_radius + self.electrode_offset
            outer_pn_radius = electrode_rin_n + electrode_width_n

        else:

            p_electrode_layer_ind_list = self.outer_electrode_ring_layer_inds
            electrode_width_p = self.electrode_width_outer
            electrode_rin_p = p_via_radius + self.electrode_offset
            outer_pn_radius = electrode_rin_p + electrode_width_p

            electrode_width_n = self.electrode_width_inner
            electrode_rout_n = n_via_radius - self.electrode_offset
            inner_pn_radius = electrode_rout_n - electrode_width_n

        offset_distance = outer_pn_radius

        metal_width=2
        # heater wiring to the left upper pad
        wire1_top = 3*offset_distance
        wire1_bottom = -self.heater_electrode_top_y_span/2
        wire1_left = -self.contact_dist/2 -(self.r_r_gap/2+self.core_width / 2)-self.r_core_cent -metal_width
        wire1_right = wire1_left+ metal_width
        self.add_rect(layer=self.heater_electrode_top_layer,
                      bbox=BBox(right=wire1_right,
                                bottom=wire1_bottom,
                                left=wire1_left,
                                top=wire1_top,
                                resolution=self.grid.resolution)
                      )


        wire2_top = wire1_top
        wire2_bottom = wire2_top-metal_width
        wire2_left = self.left_heaterpad_loc[0]
        wire2_right = wire1_right
        self.add_rect(layer=self.heater_electrode_top_layer,
                      bbox=BBox(right=wire2_right,
                                bottom=wire2_bottom,
                                left=wire2_left,
                                top=wire2_top,
                                resolution=self.grid.resolution)
                      )

        wire3_top = self.left_heaterpad_loc[1]+dim1/2
        wire3_bottom = wire2_bottom
        wire3_left = wire2_left
        wire3_right = wire2_left+metal_width
        self.add_rect(layer=self.heater_electrode_top_layer,
                      bbox=BBox(right=wire3_right,
                                bottom=wire3_bottom,
                                left=wire3_left,
                                top=wire3_top,
                                resolution=self.grid.resolution)
                      )





        # # heater wiring to the right upper pad
        wire1_top = 3*offset_distance
        wire1_bottom = -self.heater_electrode_top_y_span/2
        wire1_left = self.contact_dist/2 +(self.r_r_gap/2+self.core_width / 2)+self.r_core_cent
        wire1_right = self.contact_dist/2 +(self.r_r_gap/2+self.core_width / 2)+self.r_core_cent +metal_width
        self.add_rect(layer=self.heater_electrode_top_layer,
                      bbox=BBox(right=wire1_right,
                                bottom=wire1_bottom,
                                left=wire1_left,
                                top=wire1_top,
                                resolution=self.grid.resolution)
                      )


        wire2_top = wire1_top
        wire2_bottom = wire1_top-metal_width
        wire2_left = wire1_left
        wire2_right = self.right_heaterpad_loc[0]
        self.add_rect(layer=self.heater_electrode_top_layer,
                      bbox=BBox(right=wire2_right,
                                bottom=wire2_bottom,
                                left=wire2_left,
                                top=wire2_top,
                                resolution=self.grid.resolution)
                      )

        wire3_top = self.right_heaterpad_loc[1]+dim1/2
        wire3_bottom = wire2_bottom
        wire3_left = wire2_right-metal_width
        wire3_right = wire2_right
        self.add_rect(layer=self.heater_electrode_top_layer,
                      bbox=BBox(right=wire3_right,
                                bottom=wire3_bottom,
                                left=wire3_left,
                                top=wire3_top,
                                resolution=self.grid.resolution)
                      )
        # draw central upper pad wire(bring from left ring)
        wire1_top = 3*offset_distance
        wire1_bottom = -self.heater_electrode_top_y_span/2
        wire1_left = self.contact_dist/2 -(self.r_r_gap/2+self.core_width / 2)-self.r_core_cent
        wire1_right = wire1_left+metal_width
        self.add_rect(layer=self.heater_electrode_top_layer,
                      bbox=BBox(right=wire1_right,
                                bottom=wire1_bottom,
                                left=wire1_left,
                                top=wire1_top,
                                resolution=self.grid.resolution)
                      )
        wire2_top = wire1_top
        wire2_bottom = wire1_top-metal_width
        wire2_left = wire1_left
        wire2_right = 0
        self.add_rect(layer=self.heater_electrode_top_layer,
                      bbox=BBox(right=wire2_right,
                                bottom=wire2_bottom,
                                left=wire2_left,
                                top=wire2_top,
                                resolution=self.grid.resolution)
                      )

        # draw central upper pad wire(bring from right ring)
        wire1_top = 3*offset_distance
        wire1_bottom = -self.heater_electrode_top_y_span/2
        wire1_right = -self.contact_dist/2 +(self.r_r_gap/2+self.core_width / 2)+self.r_core_cent
        wire1_left = wire1_right - metal_width
        self.add_rect(layer=self.heater_electrode_top_layer,
                      bbox=BBox(right=wire1_right,
                                bottom=wire1_bottom,
                                left=wire1_left,
                                top=wire1_top,
                                resolution=self.grid.resolution)
                      )
        wire2_top = wire1_top
        wire2_bottom = wire1_top-metal_width
        wire2_left = 0
        wire2_right = wire1_right
        self.add_rect(layer=self.heater_electrode_top_layer,
                      bbox=BBox(right=wire2_right,
                                bottom=wire2_bottom,
                                left=wire2_left,
                                top=wire2_top,
                                resolution=self.grid.resolution)
                      )
        # vertical wire upto upto middle pad
        wire3_top = self.central_heaterpad_loc[1]+dim1/2
        wire3_bottom = wire2_bottom
        wire3_right = metal_width/2
        wire3_left = -metal_width/2
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
                                                            bottom_layer=self.inner_electrode_ring_layers[-1],
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
        self.left_heaterpad_loc = (self.modu_centre[0] - (self.gs_pad_pitch ) ,  self.modu_centre[1] + self.heater_pad_to_ring_dist)
        self.central_heaterpad_loc = (self.modu_centre[0]  ,  self.modu_centre[1] + self.heater_pad_to_ring_dist)
        self.right_heaterpad_loc = (self.modu_centre[0] + (self.gs_pad_pitch ) ,  self.modu_centre[1] + self.heater_pad_to_ring_dist)

        # Place left pad open layer and pad llayer exclusion for heater

        self.add_rect(layer=self.gs_pad_layer,
                      bbox=BBox(left=self.left_heaterpad_loc[0] - self.gs_pad_width/2 ,
                                bottom= self.left_heaterpad_loc[1]  ,
                                right=self.left_heaterpad_loc[0] + self.gs_pad_width/2,
                                top=self.left_heaterpad_loc[1] + self.gs_pad_length + dim1,
                                resolution=self.grid.resolution)
                      )
        self.add_rect(layer=self.gs_pad_open_layer,
                      bbox=BBox(left=self.left_heaterpad_loc[0] - self.gs_pad_width/2 + self.gs_pad_open_inclusion,
                                bottom= self.left_heaterpad_loc[1]+dim1+3,
                                right=self.left_heaterpad_loc[0] + self.gs_pad_width/2 -self.gs_pad_open_inclusion,
                                top= self.left_heaterpad_loc[1] + self.gs_pad_length+dim1 - self.gs_pad_open_inclusion ,
                                resolution=self.grid.resolution)
                      )
        # Place right pad open layer and pad llayer exclusion for heater
        self.add_rect(layer=self.gs_pad_layer,
                      bbox=BBox(left=self.right_heaterpad_loc[0] - self.gs_pad_width/2,
                                bottom= self.right_heaterpad_loc[1],
                                right=self.right_heaterpad_loc[0] + self.gs_pad_width/2 ,
                                top= self.right_heaterpad_loc[1] + self.gs_pad_length+dim1 ,
                                resolution=self.grid.resolution)
                      )



        self.add_rect(layer=self.gs_pad_open_layer,
                      bbox=BBox(left=self.right_heaterpad_loc[0] - self.gs_pad_width/2 + self.gs_pad_open_inclusion,
                                bottom= self.left_heaterpad_loc[1]+dim1+3,
                                right=self.right_heaterpad_loc[0] + self.gs_pad_width/2 -self.gs_pad_open_inclusion,
                                top= self.left_heaterpad_loc[1] + self.gs_pad_length+dim1 - self.gs_pad_open_inclusion ,
                                resolution=self.grid.resolution)
                      )
        # Place central pad open layer and pad llayer exclusion for heater
        self.add_rect(layer=self.gs_pad_layer,
                      bbox=BBox(left=self.central_heaterpad_loc[0] - self.gs_pad_width / 2,
                                bottom=self.central_heaterpad_loc[1],
                                right=self.central_heaterpad_loc[0] + self.gs_pad_width / 2,
                                top= self.central_heaterpad_loc[1] + self.gs_pad_length + dim1 ,
                                resolution=self.grid.resolution)
                      )

        self.add_rect(layer=self.gs_pad_open_layer,
                      bbox=BBox(left=self.central_heaterpad_loc[0] - self.gs_pad_width / 2 + self.gs_pad_open_inclusion,
                                bottom= self.central_heaterpad_loc[1] + dim1+3,
                                right = self.central_heaterpad_loc[0] + self.gs_pad_width / 2 - self.gs_pad_open_inclusion,
                                top= self.central_heaterpad_loc[1] + self.gs_pad_length + dim1 - self.gs_pad_open_inclusion,
                                resolution=self.grid.resolution)
                      )


        # Place left upper pad electrode
        self.add_instance(master=gs_electrode_master,
                          inst_name='G_electrode',
                          loc=(self.left_heaterpad_loc[0],self.left_heaterpad_loc[1]+dim1/2),
                          orient='R90')

        # Place right upper pad electrode
        self.add_instance(master=gs_electrode_master,
                          inst_name='S_electrode',
                          loc=(self.right_heaterpad_loc[0],self.right_heaterpad_loc[1]+dim1/2),
                          orient='R90')
        # Place central upper pad electrode
        self.add_instance(master=gs_electrode_master,
                          inst_name='G_electrode',
                          loc=(self.central_heaterpad_loc[0], self.central_heaterpad_loc[1]+dim1/2),
                          orient='R90')

    def create_in_out_taper(self):

        taper_params = {'width0': self.in_out_port_width,
                        'width1': self.coup_core_width,
                        'width_partial': self.slab_width,  # hack: here this is supposed to be self.coup_slab_width but it is not working , so self.slab_width
                        'length': self.taper_length}
        self.taper_master = self.new_template(params=taper_params,
                                              temp_cls=StripToRibTaper)
        
    def put_gratings(self,number=3,gc_x=float,gc_y=float):
        self.grating_coupler_module = 'RAMPS-Tapeout-Jan25.RAMPS.photonics.gf45spclo_photonics.ph45spclo.iograt'
        self.grating_coupler_class = 'iograt_1311'
        gc_module = import_module(self.grating_coupler_module)
        gc_class = getattr(gc_module, self.grating_coupler_class)
        self.gc_master = self.new_template(params=None, temp_cls=gc_class)
        if gc_x < 0:
            orient = "R0"
            if number == 2:
                y = [90+gc_y, -90+gc_y]
                
                grating_L0 = self.add_instance(
                    master=self.gc_master,
                    loc=(gc_x,y[0]),
                    orient=orient,
                )
                self.extract_photonic_ports(inst=grating_L0,port_names="IN",port_renaming="GC_L0",show = True)
                Wg1 = AdiabaticRouter(gen_cls=self, init_port=self.get_photonic_port('IN'),
                              layer=('si_full_free', 'drawing'), name='init_port')

                Wg1.add_straight_wg(length=20, width= 0.35)
                
                
                grating_L1 = self.add_instance(
                    master=self.gc_master,
                    loc=(gc_x,y[1]),
                    orient=orient,
                )
                self.add_photonic_port(name='grating_L1', orient='R180',
                                    center=(gc_x,y[1]), width = 0.35,
                                    layer=('RX', 'port'), resolution=self.grid.resolution, unit_mode=False, show=False)
                
                grating_L2 = self.add_instance(
                    master=self.gc_master,
                    loc=(gc_x,y[2]),
                    orient=orient,
                )
                self.add_photonic_port(name='grating_L1', orient='R180',
                                    center=(gc_x,y[2]), width = 0.35,
                                    layer=('RX', 'port'), resolution=self.grid.resolution, unit_mode=False, show=False)
                
                
            if number == 3:
                y = [90+gc_y, gc_y, -90+gc_y]
                for i in range(len(y)):
                    self.add_instance(
                        master=self.gc_master,
                        loc=(gc_x,y[i]),
                        orient=orient,
                    )
                    
            if number == 1:
                y = [gc_y]
                for i in range(len(y)):
                    self.add_instance(
                        master=self.gc_master,
                        loc=(gc_x,y[i]),
                        orient=orient,
                    )
            if number == 4:
                y = [100+gc_y, 50+gc_y, -50+gc_y,-100+gc_y]
                for i in range(len(y)):
                    self.add_instance(
                        master=self.gc_master,
                        loc=(gc_x,y[i]),
                        orient=orient,
                    )
        else:
            orient = "R180"
                
            
        if number == 2:
            y = [90+gc_y, -90+gc_y]
            for i in range(len(y)):
                self.add_instance(
                    master=self.gc_master,
                    loc=(gc_x,y[i]),
                    orient=orient,
                )
        if number == 3:
            y = [90+gc_y, gc_y, -90+gc_y]
            for i in range(len(y)):
                self.add_instance(
                    master=self.gc_master,
                    loc=(gc_x,y[i]),
                    orient=orient,
                )
                
        if number == 1:
            y = [gc_y]
            for i in range(len(y)):
                self.add_instance(
                    master=self.gc_master,
                    loc=(gc_x,y[i]),
                    orient=orient,
                )
        if number == 4:
            y = [100+gc_y, 50+gc_y, -50+gc_y,-100+gc_y]
            for i in range(len(y)):
                self.add_instance(
                    master=self.gc_master,
                    loc=(gc_x,y[i]),
                    orient=orient,
                )




if __name__ == '__main__':
    spec_file = 'Dual_ring_halfrib_point_coupler/specs/halfrib_dual_ring_spoked.yaml'
    PLM = BPG.PhotonicLayoutManager(spec_file)
    PLM.generate_content()
    PLM.generate_gds()
   # PLM.generate_flat_content()
    #PLM.generate_flat_gds()
    PLM.dataprep_calibre()