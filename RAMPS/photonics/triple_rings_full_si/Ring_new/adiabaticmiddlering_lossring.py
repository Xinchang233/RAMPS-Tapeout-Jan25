import BPG
from layout.Ring_new.ring import RingBase
from layout.Ring_new.ringheater import RingHeater
import importlib
from layout.Ring_new.ringheater_middle import RingHeater_middle
from layout.Ring_new.ringheater1 import RingHeater1
from layout.Ring_new.adiabaticsinglemiddlering import RingBase1
from layout.Ring_new.ring2 import RingBase2
from layout.Ring_new.AdiabaticRouter import AdiabaticRouter
from layout.Ring_new.Test_Adiabatic_router1 import adiabatic_ring1
from layout.Ring_new.Test_Adiabatic_router import adiabatic_ring
from layout.Ring_new.GS_pads import GSPads
from layout.Ring_new.GS_pads1 import GSPads1
from layout.Ring_new.GS_pads2 import GSPads2
from layout.Ring_new.GS_pads3 import GSPads3
from layout.Ring_new.GS_pads4 import GSPads4
from layout.Ring_new.ViaStack.ViaStack import ViaStack
from layout.Ring_new.ViaStack import ViaStack
from layout.BasicElements.SimpleRing.SimpleRing import SimpleRing
from utils.adiabatic_bends import compute_arc_length
from utils.adiabatic_bends import compute_arc_length
from utils.adiabatic_bends_x_y import compute_arc_length1
from utils.adiabatic_bends_x_y_2nd import compute_arc_length2
from layout.BasicElements.SimpleRing.SimpleRing import SimpleRing
from layout.AdiabaticRouter.SimpleRound.SimpleRound import SimpleRound
from BPG.objects import PhotonicPolygon
import math
import numpy as np
from bag.layout.util import BBox



class RingWithHeaterBase(BPG.PhotonicTemplateBase):
    """
    Ring-heater Design Script class
    """

    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)

        self.x_slot = None
        self.y_offset = None
        self.right_pad_master = None
        self.left_pad_master = None
        self.right_pad_master1 = None
        self.left_pad_master1 = None
        self.left_pad = None
        self.right_pad = None
        self.psr_parts_master = dict()
        # Declare access length so it can be accessed by higher level scripts
        self.access_length = None
        self.w=self.params['w']
        self.y = self.params['y']
        self.x = self.params['x']
        self.gap = self.params['gap']
        self.wg180_radius = self.params['wg180_radius']
        self.coupling_slot_drop=self.params['coupling_slot_drop']
        self.wg_width=self.params['wg_width']
        self.placer = self.params['placer']
        self.adiabaticplacer = self.params['adiabaticplacer']
        self.psr_parts = dict()


    @classmethod
    def get_default_param_values(cls):
        return dict(
            drop_slot=-1,  # Do not have a drop port by default
            bottom_electrode_label_layer=None,  # Do not place a label on the bottom metal layer
            heater_electrode_bottom_x_span=None,
            heater_electrode_bottom_y_span=None,
            ring_label='Contact',
            heater_label='Heat',
            heater_disable=False,
            heater_disable1=False,
            x_slot=10.0,
            y_offset=0,
            right_pad_params=None,
            left_pad_params=None,
            right_pad_params1=None,
            left_pad_params1=None,
            right_pad_params2=None,
            left_pad_params2=None,
            right_pad_params3=None,
            left_pad_params3=None,
            right_pad_params4=None,
            left_pad_params4=None,
            right_pad_params5=None,
            left_pad_params5=None,
            right_pad_label=None,
            left_pad_label=None,
            te_1300grating_params=None,
            adiabaticmiddle_params=None,
        )

    @classmethod
    def get_params_info(cls):  # Returns definition of the parameters.
        return dict(
            # Ring params
            # Standard parameters
            te_1300grating_params='DD',
            adiabaticmiddle_params='dfdf',
            ring_loc='first',
            ring_loc_2='second',
            heater_middle='xzc',
            placer='fhgfgh',
            adiabaticplacer='fhgfgh',
            rout='Outer radius of ring',
            ring_width='Ring width',
            layer='Layer or LPP of the main ring and spokes',
            doping_spoke_info='List of spoke doping dictionaries containing: rout, rin, num, layer, '
                              'spoke_width_percentage, spoke_offset',
            extra_ring_info='List of extra ring dictionaries containing: rout, ring_width, layer',
            spoke_num='Number of n or p spokes (total spoke number is 2x this value',
            coupling_slot='Ring to access waveguide gap.',
            coupling_slot_drop='Ring to access waveguide gap.',
            drop_slot='Ring to drop port gap',
            wg_width='Width of the access waveguide.',
            ring_label='Ring contact label text [str], or dictionary with keys P: <p_label> and N: <n_label>',

            outer_electrode_ring_layers='Ordered list of LPPs (bot to top) on which outer electrode ring is drawn.',
            inner_electrode_ring_layers='Ordered list of LPPs (bot to top) on which inner electrode ring is drawn.',

            # Advanced parameters: can change between designs per technology, but not recommended for standard users
            access_length='Length of the cosine-curved access wavelength',
            p_via_radius_offset='P via radius offset of ring device. If p_via_radius_offset > n_via_radius_offset, '
                                'inner electrode will be P, and the P silicon spokes will be longer.',
            n_via_radius_offset='N via radius offset of ring device. If p_via_radius_offset > n_via_radius_offset, '
                                'inner electrode will be P, and the P silicon spokes will be longer.',
            high_doping_rout_offset='Offset of outer high doping radius (distance from ring inner radius to outer '
                                    'high doping radius). Positive offset decreases outer radius.',
            high_doping_rin_offset='Offset of the inner high doping radius (radius of the inner edge of the high '
                                   'doping region). Positive offset decreases inner radius.',
            electrode_offset='Electrode offset away from the via locations',
            electrode_width_inner='Width of the inner electrode ring',
            electrode_width_outer='Width of the outer electrode ring',
            drop_taper_length='Length of the tapers on the drop port',
            salicide_radius_extension='Extra amount that should be added to the salicide disk covering the center of '
                                      'the ring (spoke tips).',
            high_doping_n_rin_offset='Offset of the inner radius high n doping region around the silicon contact '
                                     'spokes. Positive value makes rin of this doping larger (further from ring '
                                     'center). Used to space high n doping of spoke from high n doping of any central '
                                     'heater.',

            # Advanced tech params: should not need to change between designs in a given technology
            high_p_doping_layer='LPP for the high p doping silicon contacts',
            high_n_doping_layer='LPP for the high n doping silicon contacts',
            salicide_lpp='LPP for the salicide region for making low resistance silicon contacts',
            bottom_metal_electrode_layer='LPP for the bottom electrode layer in the stack (should be the BAG '
                                         'equivalent metal layer of the layer parameter).',
            bottom_electrode_label_layer='LPP for the layer on which an electrode label should be placed. '
                                         'If not provided, no bottom label is drawn.',

            # Heater params
            # Standard params
            heater_disable='True to not place the heater. Defaults to False (ie heater is present).',
            heater_disable1='True to not place the heater. Defaults to False (ie heater is present).',
            heater_radius_offset='Offset of outer heater radius from inner ring radius',
            resistance='Resistance target for the heater',
            contact_dist='Distance between two inner edges of the two interior spokes that contact the heater ring.',
            contact_width='Width of interior contact spokes that connect the heater ring to the via stack',
            heater_device_layer='LPP of ring heater device (ie layer of the actual heater)',
            heater_device_layer_RX='LPP of ring heater device (ie layer of the actual heater)',
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
            w='dsfsd',
            x='xx',
            y='sd',
            gap='asd',
            wg180_radius='asda',
            x_slot='Slot in the x direction between the two pads',
            y_offset='y offset between the two opads',
            right_pad_params='Parameters for the ViaStack template corresponding to the right pad',
            left_pad_params='Parameters for the ViaStack template corresponding to the left pad',
            right_pad_params1='Parameters for the ViaStack template corresponding to the right pad',
            left_pad_params1='Parameters for the ViaStack template corresponding to the left pad',
            right_pad_params2='Parameters for the ViaStack template corresponding to the right pad',
            left_pad_params2='Parameters for the ViaStack template corresponding to the left pad',
            right_pad_params3='Parameters for the ViaStack template corresponding to the right pad',
            left_pad_params3='Parameters for the ViaStack template corresponding to the left pad',
            right_pad_params4='Parameters for the ViaStack template corresponding to the right pad',
            left_pad_params4='Parameters for the ViaStack template corresponding to the left pad',
            right_pad_params5='Parameters for the ViaStack template corresponding to the right pad',
            left_pad_params5='Parameters for the ViaStack template corresponding to the left pad',
            right_pad_label='Optional dict containing label params for the right pad',
            left_pad_label='Optional dict containing label params for the left pad',

        )

    def draw_layout(self):
        # Set the ring parameters
        ring_params = dict(
            # Standard parameters
            ring_loc=self.params['ring_loc'],
            rout=self.params['rout'],
            ring_width=self.params['ring_width'],
            layer=self.params['layer'],
            doping_spoke_info=self.params['doping_spoke_info'],
            extra_ring_info=self.params['extra_ring_info'],
            spoke_num=self.params['spoke_num'],
            coupling_slot=self.params['coupling_slot'],
            drop_slot=self.params['drop_slot'],
            wg_width=self.params['wg_width'],
            label=self.params['ring_label'],

            outer_electrode_ring_layers=self.params['outer_electrode_ring_layers'],
            inner_electrode_ring_layers=self.params['inner_electrode_ring_layers'],

            # Advanced parameters: can change between designs per technology, but not recommended for standard users
            access_length=self.params['access_length'],
            p_via_radius_offset=self.params['p_via_radius_offset'],
            n_via_radius_offset=self.params['n_via_radius_offset'],
            high_doping_rout_offset=self.params['high_doping_rout_offset'],
            high_doping_rin_offset=self.params['high_doping_rin_offset'],
            electrode_offset=self.params['electrode_offset'],
            electrode_width_inner=self.params['electrode_width_inner'],
            electrode_width_outer=self.params['electrode_width_outer'],
            drop_taper_length=self.params['drop_taper_length'],
            salicide_radius_extension=self.params['salicide_radius_extension'],
            high_doping_n_rin_offset=self.params['high_doping_n_rin_offset'],


            # Advanced tech params: should not need to change between designs in a given technology
            high_p_doping_layer=self.params['high_p_doping_layer'],
            high_n_doping_layer=self.params['high_n_doping_layer'],
            salicide_lpp=self.params['salicide_lpp'],
            bottom_metal_electrode_layer=self.params['bottom_metal_electrode_layer'],
            bottom_electrode_label_layer=self.params['bottom_electrode_label_layer'],


        )
        ring_params = dict(
            # Standard parameters
            placer=0-self.params['placer']/2,
            ring_loc=self.params['ring_loc_2'],
            rout=self.params['rout'],
            ring_width=self.params['ring_width'],
            layer=self.params['layer'],
            doping_spoke_info=self.params['doping_spoke_info'],
            extra_ring_info=self.params['extra_ring_info'],
            spoke_num=self.params['spoke_num'],
            coupling_slot=self.params['coupling_slot'],
            coupling_slot_drop=self.params['coupling_slot_drop'],
            drop_slot=self.params['drop_slot'],
            wg_width=self.params['wg_width'],
            label=self.params['ring_label'],

            outer_electrode_ring_layers=self.params['outer_electrode_ring_layers'],
            inner_electrode_ring_layers=self.params['inner_electrode_ring_layers'],

            # Advanced parameters: can change between designs per technology, but not recommended for standard users
            access_length=self.params['access_length'],
            p_via_radius_offset=self.params['p_via_radius_offset'],
            n_via_radius_offset=self.params['n_via_radius_offset'],
            high_doping_rout_offset=self.params['high_doping_rout_offset'],
            high_doping_rin_offset=self.params['high_doping_rin_offset'],
            electrode_offset=self.params['electrode_offset'],
            electrode_width_inner=self.params['electrode_width_inner'],
            electrode_width_outer=self.params['electrode_width_outer'],
            drop_taper_length=self.params['drop_taper_length'],
            salicide_radius_extension=self.params['salicide_radius_extension'],
            high_doping_n_rin_offset=self.params['high_doping_n_rin_offset'],

            # Advanced tech params: should not need to change between designs in a given technology
            high_p_doping_layer=self.params['high_p_doping_layer'],
            high_n_doping_layer=self.params['high_n_doping_layer'],
            salicide_lpp=self.params['salicide_lpp'],
            bottom_metal_electrode_layer=self.params['bottom_metal_electrode_layer'],
            bottom_electrode_label_layer=self.params['bottom_electrode_label_layer'],
        )
        ring_params1 = dict(
            # Standard parameters
            placer=self.params['placer']-self.params['placer']/2,
            ring_loc=self.params['ring_loc_2'],
            rout=self.params['rout'],
            ring_width=self.params['ring_width'],
            layer=self.params['layer'],
            doping_spoke_info=self.params['doping_spoke_info'],
            extra_ring_info=self.params['extra_ring_info'],
            spoke_num=self.params['spoke_num'],
            coupling_slot=self.params['coupling_slot'],
            drop_slot=self.params['drop_slot'],
            wg_width=self.params['wg_width'],
            label=self.params['ring_label'],

            outer_electrode_ring_layers=self.params['outer_electrode_ring_layers'],
            inner_electrode_ring_layers=self.params['inner_electrode_ring_layers'],

            # Advanced parameters: can change between designs per technology, but not recommended for standard users
            access_length=self.params['access_length'],
            p_via_radius_offset=self.params['p_via_radius_offset'],
            n_via_radius_offset=self.params['n_via_radius_offset'],
            high_doping_rout_offset=self.params['high_doping_rout_offset'],
            high_doping_rin_offset=self.params['high_doping_rin_offset'],
            electrode_offset=self.params['electrode_offset'],
            electrode_width_inner=self.params['electrode_width_inner'],
            electrode_width_outer=self.params['electrode_width_outer'],
            drop_taper_length=self.params['drop_taper_length'],
            salicide_radius_extension=self.params['salicide_radius_extension'],
            high_doping_n_rin_offset=self.params['high_doping_n_rin_offset'],

            # Advanced tech params: should not need to change between designs in a given technology
            high_p_doping_layer=self.params['high_p_doping_layer'],
            high_n_doping_layer=self.params['high_n_doping_layer'],
            salicide_lpp=self.params['salicide_lpp'],
            bottom_metal_electrode_layer=self.params['bottom_metal_electrode_layer'],
            bottom_electrode_label_layer=self.params['bottom_electrode_label_layer'],
        )

        heater_params = dict(
            heater_middle=self.params['heater_middle'],
            placer=self.params['placer'],
            rout=(self.params['rout'] - self.params['ring_width'] -
                  max(self.params['p_via_radius_offset'], self.params['n_via_radius_offset']) -
                  self.params['heater_radius_offset']),
            resistance=self.params['resistance'],
            contact_dist=self.params['contact_dist'],
            contact_width=self.params['contact_width'],
            device_layer=self.params['heater_device_layer'],
            device_layer_RX=self.params['heater_device_layer_RX'],
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
        ring_master1 = self.new_template(params=ring_params, temp_cls=RingBase1)
        #ring_inst1 = self.add_instance(master=ring_master1)
        ring_master = self.new_template(params=ring_params1, temp_cls=RingBase2)
        #ring_inst = self.add_instance(master=ring_master)
        # Add the heater if it should be present



        if not self.params['heater_disable']:
            # Compute the width from the heater resistance design function
            heater_params['width'] = RingHeater.design_heater_width_from_resistance(
                resistance=heater_params['resistance'],
                heater_rout=heater_params['rout'],
                r_square=self.photonic_tech_info.sheet_resistance(heater_params['device_layer_RX']),
                contact_width=heater_params['contact_width'],
                contact_dist=heater_params['contact_dist'],
            )
            heater_master = self.new_template(params=heater_params, temp_cls=RingHeater)
            #self.add_instance(master=heater_master)


        wg180_radius_final = self.params['wg180_radius']
        middle_ring_params = dict(
            layer='rxphot_noopc',
            layer1 = ('rxphot_noopc','drawing'),
            w=self.params['w'],
            x=self.params['x'],
            y=self.params['y']-self.params['adiabaticplacer']/2,
            gap=self.params['gap'],
            wg180_radius=wg180_radius_final,
        )
        ring_master11 = self.new_template(params=middle_ring_params, temp_cls=adiabatic_ring)
        #ring_inst11 = self.add_instance(master=ring_master11)

        wg180_radius_final = self.params['wg180_radius']-2.1 #0.55
        y_placer = self.params['y'] - 2.9 - self.params['placer'] / 2
        middle_ring_params = dict(
            layer='rxphot_noopc',
            layer1=('rxphot_noopc', 'drawing'),
            w=self.params['w'],
            x=self.params['x'],
            y=y_placer, #0.7
            gap=self.params['gap'],
            wg180_radius=wg180_radius_final,
        )
        ring_master11 = self.new_template(params=middle_ring_params, temp_cls=adiabatic_ring)
        #ring_inst11 = self.add_instance(master=ring_master11)


        middle_ring_params = dict(
            layer='rxphot_noopc',
            layer1=('nnphot', 'drawing'),
            w=self.params['w'],
            x=self.params['x'],
            y=y_placer,
            gap=self.params['gap'],
            wg180_radius=wg180_radius_final,
        )
        ring_master11 = self.new_template(params=middle_ring_params, temp_cls=adiabatic_ring)
        #ring_inst11 = self.add_instance(master=ring_master11)


        middle_ring_params = dict(
            layer='rxphot_noopc',
            layer1=('sldphot', 'drawing'),
            w=self.params['w'],
            x=self.params['x'],
            y=y_placer,
            gap=self.params['gap'],
            wg180_radius=wg180_radius_final,
        )
        ring_master11 = self.new_template(params=middle_ring_params, temp_cls=adiabatic_ring)
        #ring_inst11 = self.add_instance(master=ring_master11)



        gs_params = dict(
            placer=self.params['placer'],
            x_slot=self.params['x_slot'],
            y_offset=self.params['y_offset'],
            right_pad_params=self.params['right_pad_params'],
            left_pad_params=self.params['left_pad_params'],
            right_pad_label=self.params['right_pad_label'],
            left_pad_label=self.params['left_pad_label'],
        )
        gs_probes = self.new_template(params=gs_params, temp_cls=GSPads)
        #ring_inst11 = self.add_instance(master=gs_probes)

        gs_params = dict(
            placer=self.params['placer'],
            x_slot=self.params['x_slot'],
            y_offset=self.params['y_offset'],
            right_pad_params=self.params['right_pad_params1'],
            left_pad_params=self.params['left_pad_params1'],
            right_pad_label=self.params['right_pad_label'],
            left_pad_label=self.params['left_pad_label'],
        )
        gs_probes = self.new_template(params=gs_params, temp_cls=GSPads)
        #ring_inst11 = self.add_instance(master=gs_probes)

        gs_params = dict(
            placer=self.params['placer'],
            x_slot=self.params['x_slot'],
            y_offset=self.params['y_offset'],
            right_pad_params=self.params['right_pad_params2'],
            left_pad_params=self.params['left_pad_params2'],
            right_pad_label=self.params['right_pad_label'],
            left_pad_label=self.params['left_pad_label'],
        )
        gs_probes = self.new_template(params=gs_params, temp_cls=GSPads)
        #ring_inst11 = self.add_instance(master=gs_probes)

        gs_params = dict(
            placer=self.params['placer'],
            contact_dist=self.params['contact_dist'],
            electrode_bottom_x_span=self.params['heater_electrode_bottom_x_span'],
            electrode_bottom_y_span=self.params['heater_electrode_top_y_span'],
            x_slot=self.params['x_slot'],
            y_offset=self.params['y_offset'],
            right_pad_params=self.params['right_pad_params'],
            left_pad_params=self.params['left_pad_params'],
            right_pad_params1=self.params['right_pad_params1'],
            left_pad_params1=self.params['left_pad_params1'],
            right_pad_params2=self.params['right_pad_params2'],
            left_pad_params2=self.params['left_pad_params2'],
            right_pad_label=self.params['right_pad_label'],
            left_pad_label=self.params['left_pad_label'],
        )
        gs_probes = self.new_template(params=gs_params, temp_cls=GSPads1)
        #ring_inst11 = self.add_instance(master=gs_probes)





        gs_params = dict(
            electrode_width_inner=self.params['electrode_width_inner'],
            electrode_width_outer=self.params['electrode_width_outer'],
            radius_b1=self.params['rout']-self.params['ring_width']+self.params['p_via_radius_offset'],
            radius_b2 =self.params['rout']-self.params['ring_width']-self.params['n_via_radius_offset']-self.params['electrode_offset'],
            placer=self.params['placer'],
            contact_dist=self.params['contact_dist'],
            electrode_bottom_x_span=self.params['heater_electrode_bottom_x_span'],
            electrode_bottom_y_span=self.params['heater_electrode_top_y_span'],
            x_slot=self.params['x_slot'],
            y_offset=self.params['y_offset'],
            right_pad_params=self.params['right_pad_params3'],
            left_pad_params=self.params['left_pad_params3'],
            right_pad_label=self.params['right_pad_label'],
            left_pad_label=self.params['left_pad_label'],
        )
        #gs_probes = self.new_template(params=gs_params, temp_cls=GSPads2)
        gs_probes = self.new_template(params=gs_params, temp_cls=GSPads4)
        #ring_inst11 = self.add_instance(master=gs_probes)

        gs_params = dict(
            electrode_width_inner=self.params['electrode_width_inner'],
            electrode_width_outer=self.params['electrode_width_outer'],
            radius_b1=self.params['rout'] - self.params['ring_width'] + self.params['p_via_radius_offset'],
            radius_b2=self.params['rout'] - self.params['ring_width'] - self.params['n_via_radius_offset'] -
                      self.params['electrode_offset'],
            placer=self.params['placer'],
            contact_dist=self.params['contact_dist'],
            electrode_bottom_x_span=self.params['heater_electrode_bottom_x_span'],
            electrode_bottom_y_span=self.params['heater_electrode_top_y_span'],
            x_slot=self.params['x_slot'],
            y_offset=self.params['y_offset'],
            right_pad_params=self.params['right_pad_params4'],
            left_pad_params=self.params['left_pad_params4'],
            right_pad_label=self.params['right_pad_label'],
            left_pad_label=self.params['left_pad_label'],
        )
        gs_probes = self.new_template(params=gs_params, temp_cls=GSPads2)
        #ring_inst11 = self.add_instance(master=gs_probes)
        # gs_params = dict(
        #     placer=self.params['placer'],
        #     x_slot=self.params['x_slot'],
        #     y_offset=self.params['y_offset'],
        #     right_pad_params=self.params['right_pad_params4'],
        #     left_pad_params=self.params['left_pad_params4'],
        #     right_pad_label=self.params['right_pad_label'],
        #     left_pad_label=self.params['left_pad_label'],
        # )
        # gs_probes = self.new_template(params=gs_params, temp_cls=GSPads)
        # ring_inst11 = self.add_instance(master=gs_probes)

        # gs_params = dict(
        #     placer=self.params['placer'],
        #     x_slot=self.params['x_slot'],
        #     y_offset=self.params['y_offset'],
        #     right_pad_params=self.params['right_pad_params4'],
        #     left_pad_params=self.params['left_pad_params4'],
        #     right_pad_label=self.params['right_pad_label'],
        #     left_pad_label=self.params['left_pad_label'],
        # )
        # gs_probes = self.new_template(params=gs_params, temp_cls=GSPads)
        # ring_inst11 = self.add_instance(master=gs_probes)
        #
        # gs_params = dict(
        #     placer=self.params['placer'],
        #     x_slot=self.params['x_slot'],
        #     y_offset=self.params['y_offset'],
        #     right_pad_params=self.params['right_pad_params5'],
        #     left_pad_params=self.params['left_pad_params5'],
        #     right_pad_label=self.params['right_pad_label'],
        #     left_pad_label=self.params['left_pad_label'],
        # )
        # gs_probes = self.new_template(params=gs_params, temp_cls=GSPads)
        # ring_inst11 = self.add_instance(master=gs_probes)





        # Extract


        self.access_length = ring_master.access_length

        #add middle ring


        pi = np.pi

        # (x+10)/2,-(5+0.2+gap-y)
        # 520 18.857874497357543 17.76478811775237 2.6583930707547307
        # 530  18.87253520818853 17.778483412551928 2.6607145405200714
        # 540 18.887195919019526 17.792178707351493 2.6630360102854143
        # 550 18.901856629850517 17.80587400215105 2.665357480050755
        # 560 18.91651734068151 17.81956929695061 2.667678949816096
        # 570 18.931178051512504 17.833264591750176 2.6700004195814384
        # 580 18.945838762343495 17.846959886549737 2.6723218893467795
        # 590 18.960499473174487 17.860655181349294 2.674643359112121
        # 600 NM 18.975161012683216 17.874350476148855 2.6772863308249972
        # 610 18.989821724942967 17.888045770948416 2.6796083549040404
        # 620 19.00448243720271 17.901741065747977 2.6819303789830857
        # 630 19.019143149462458 17.915436360547538 2.6842524030621293
        # 640 19.03380386172221 17.9291316553471 2.6865744271411742
        # 650 19.048465107928276 17.942826950146664 2.6888964512202174
        # 660 19.063125821100748 17.95652224494622 2.691218475299262
        # 680 19.092447247445698 17.983912834545343 2.6958625234573503
        # 670 19.077786534273223 17.970217539745782 2.693540499378306
        # 545 18.894526274435023 17.799026354751273 2.664196745168084
        # 555 18.90918698526601 17.81272164955083 2.6665182149334257
        # 565 18.923847696097003 17.82641694435039 2.668839684698767
        # 575 18.938508406927998 17.840112239149956 2.6711611544641087
        # 595 18.967830656553346 17.867502828749075 2.676125318785475
        # 585 18.95316911775899 17.853807533949514 2.6734826242294503
        # 635 19.02647350559233 17.92228400794732 2.685413415101651
        # 645 19.041134217852083 17.935979302746883 2.6877354391806962 120 um, placer= -20.082846299739252(20gh, 5um straight,length)
        # 655 19.05579546451451 17.94967459754644 2.6900574632597394
        # 665 19.070456177686985 17.963369892346 2.6923794873387843
        # 675 19.085116890859464 17.977065187145563 2.6947015114178283
        # 685 19.09977760403194 17.990760481945124 2.6970235354968723
        # (x+10)/2,-(5+0.2+gap-y)+0.004 100NM 18.242119392272954 17.189585736170816 2.557192128151484
        # (x+10)/2,-(5+0.2+gap-y)+0.002 200NM  18.38872802250795 17.326538684166426 2.5817258011272206
        # (x+10)/2,-(5+0.2+gap-y)+0.001 300NM   18.535335999321507 17.463491632162032 2.6059852722695087
        # (x+10)/2,-(5+0.2+gap-y)+0.001) 400NM 18.681944562881018 17.600444580157642 2.6299880313443076
        #   500 NM 18.828553075695556 17.73739752815325 2.6537501312240472
        # (x+10)/2,-(5+0.2+gap-y) 600 NM 18.975161012683216 17.874350476148855 2.6772863308249972
        # (x+10)/2,-(5+0.2+gap-y) 700 NM 19.12176867379065 18.011303424144465 2.7005065716154384
        # (x+10)/2,-(5+0.2+gap-y)  800 NM 19.268376615585566 18.14825637214007 2.7238322190506272
        # (x+10)/2,-(5+0.2+gap-y) 900 NM 19.41498505211373 18.285209320135678 2.7469547051752468
        # 1000 NM 19.561593448387917 18.422162268131288 2.7698859660654778
        # (x+10)/2,-(5+0.2+gap-y) 1100 19.708201356757574 18.559115216126894 2.7926370332067423


        # 595 18.967830656553346 17.867502828749075 2.676125318785475
        # 560 18.91651734068151 17.81956929695061 2.667678949816096




        mt_module = importlib.import_module(self.params['te_1300grating_params']['package'])
        mt_class = getattr(mt_module, self.params['te_1300grating_params']['class'])
        self.psr_parts_master['te_1300grating'] = self.new_template(params=self.params['te_1300grating_params'],
                                                                    temp_cls=mt_class)

# add waveguide
#         x = 17.463491632162032
#         y = 2.6059852722695087
#         gap = 0.3
#         wg180_radius = 5
#         init_port11 = self.add_photonic_port(name='init_port11', center=(
#         -self.params['rout'] + self.params['wg_width'] / 2, -self.placer / 2), orient='R270',
#                                              width=self.w, layer=('rxphot_noopc', 'port'))
#         #         # init_port = self.add_photonic_port(name='init_port', center=(0,0), orient='R0',width=w, layer=('RX', 'port'))
#         #         # (27.6/2,5.6-2.4275919117522138)
#         Wg = AdiabaticRouter(gen_cls=self,
#                              init_port=init_port11,
#                              layer=('rxphot_noopc', 'drawing'),
#                              name='init_port11')
#         Wg.add_bend_90(size=20)
#         Wg.add_straight_wg(length=30, width=0.5)
#         # Wg.add_offset_bend(offset=-40, rmin=10)
#
#         mt_module = importlib.import_module(self.params['te_1300grating_params']['package'])
#         mt_class = getattr(mt_module, self.params['te_1300grating_params']['class'])
#         self.psr_parts_master['te_1300grating'] = self.new_template(params=self.params['te_1300grating_params'],
#                                                                     temp_cls=mt_class)
#
#         self.psr_parts['te_1300grating'] = self.add_instance_port_to_port(
#             inst_master=self.psr_parts_master['te_1300grating'],
#             instance_port_name='PORT_OUT',
#             self_port=Wg.port,
#             reflect=False)
#
#         init_port111 = self.add_photonic_port(name='init_port111', center=(
#         self.params['rout'] - self.params['wg_width'] / 2, -self.placer / 2), orient='R270',
#                                               width=self.w, layer=('rxphot_noopc', 'port'))
#         #         # init_port = self.add_photonic_port(name='init_port', center=(0,0), orient='R0',width=w, layer=('RX', 'port'))
#         #         # (27.6/2,5.6-2.4275919117522138)
#         Wg = AdiabaticRouter(gen_cls=self,
#                              init_port=init_port111,
#                              layer=('rxphot_noopc', 'drawing'),
#                              name='init_port111')
#         Wg.add_bend_90(size=20, turn_left=False)
#         Wg.add_straight_wg(length=30, width=0.5)
#         # Wg.add_offset_bend(offset=40, rmin=10)
#
#         mt_module = importlib.import_module(self.params['te_1300grating_params']['package'])
#         mt_class = getattr(mt_module, self.params['te_1300grating_params']['class'])
#         self.psr_parts_master['te_1300grating'] = self.new_template(params=self.params['te_1300grating_params'],
#                                                                     temp_cls=mt_class)
#
#         self.psr_parts['te_1300grating'] = self.add_instance_port_to_port(
#             inst_master=self.psr_parts_master['te_1300grating'],
#             instance_port_name='PORT_OUT',
#             self_port=Wg.port,
#             reflect=False)
#         ring = self.new_template(params={'layer': ('rxphot_noopc', 'drawing'),
#                                          'r_out': 5,
#                                          'r_width': 0.4,
#                                          'r_step': 0.04,
#                                          'theta0': 180,
#                                          'theta1': 360},
#                                  temp_cls=SimpleRound)
#         self.add_instance(master=ring, loc=[0, -self.placer / 2], inst_name='ring')






        x_spacing=110
        add = 56.793/2+0.2
        gap = 0.375

        init_port1111 = self.add_photonic_port(name='init_port1111', center=(0,-gap), orient='R270',
                                             width=self.w, layer=('rxphot_noopc', 'port'))
        #         # init_port = self.add_photonic_port(name='init_port', center=(0,0), orient='R0',width=w, layer=('RX', 'port'))
        #         # (27.6/2,5.6-2.4275919117522138)


        mt_module = importlib.import_module(self.params['adiabaticmiddle_params']['package'])
        mt_class = getattr(mt_module, self.params['adiabaticmiddle_params']['class'])
        self.psr_parts_master['te1_1300grating'] = self.new_template(params=self.params['adiabaticmiddle_params'],
                                                                    temp_cls=mt_class)

        self.psr_parts['te1_1300grating'] = self.add_instance_port_to_port(
            inst_master=self.psr_parts_master['te1_1300grating'],
            instance_port_name='PORT_OUT',
            self_port=init_port1111,
            reflect=False)

        # init_port9 = self.add_photonic_port(name='init_port9', center=(x_spacing, -2*gap), orient='R270',
        #                                        width=self.w, layer=('rxphot_noopc', 'port'))
        # #         # init_port = self.add_photonic_port(name='init_port', center=(0,0), orient='R0',width=w, layer=('RX', 'port'))
        # #         # (27.6/2,5.6-2.4275919117522138)
        #
        #
        # mt_module = importlib.import_module(self.params['adiabaticmiddle_params']['package'])
        # mt_class = getattr(mt_module, self.params['adiabaticmiddle_params']['class'])
        # self.psr_parts_master['te1_1300grating'] = self.new_template(params=self.params['adiabaticmiddle_params'],
        #                                                              temp_cls=mt_class)
        #
        # self.psr_parts['te1_1300grating'] = self.add_instance_port_to_port(
        #     inst_master=self.psr_parts_master['te1_1300grating'],
        #     instance_port_name='PORT_OUT',
        #     self_port=init_port9,
        #     reflect=False)
        #
        # init_port7 = self.add_photonic_port(name='init_port7', center=(2*x_spacing, -3*gap), orient='R270',
        #                                     width=self.w, layer=('rxphot_noopc', 'port'))
        # #         # init_port = self.add_photonic_port(name='init_port', center=(0,0), orient='R0',width=w, layer=('RX', 'port'))
        # #         # (27.6/2,5.6-2.4275919117522138)
        #
        #
        # mt_module = importlib.import_module(self.params['adiabaticmiddle_params']['package'])
        # mt_class = getattr(mt_module, self.params['adiabaticmiddle_params']['class'])
        # self.psr_parts_master['te1_1300grating'] = self.new_template(params=self.params['adiabaticmiddle_params'],
        #                                                              temp_cls=mt_class)
        #
        # self.psr_parts['te1_1300grating'] = self.add_instance_port_to_port(
        #     inst_master=self.psr_parts_master['te1_1300grating'],
        #     instance_port_name='PORT_OUT',
        #     self_port=init_port7,
        #     reflect=False)
        #
        # init_port8 = self.add_photonic_port(name='init_port5', center=(3 * x_spacing, -4 * gap), orient='R270',
        #                                     width=self.w, layer=('rxphot_noopc', 'port'))
        # #         # init_port = self.add_photonic_port(name='init_port', center=(0,0), orient='R0',width=w, layer=('RX', 'port'))
        # #         # (27.6/2,5.6-2.4275919117522138)
        #
        #
        # mt_module = importlib.import_module(self.params['adiabaticmiddle_params']['package'])
        # mt_class = getattr(mt_module, self.params['adiabaticmiddle_params']['class'])
        # self.psr_parts_master['te1_1300grating'] = self.new_template(params=self.params['adiabaticmiddle_params'],
        #                                                              temp_cls=mt_class)
        #
        # self.psr_parts['te1_1300grating'] = self.add_instance_port_to_port(
        #     inst_master=self.psr_parts_master['te1_1300grating'],
        #     instance_port_name='PORT_OUT',
        #     self_port=init_port8,
        #     reflect=False)




        init_port11 = self.add_photonic_port(name='init_port11', center=(
            0,add), orient='R180',
                                             width=self.w, layer=('rxphot_noopc', 'port'))
        #         # init_port = self.add_photonic_port(name='init_port', center=(0,0), orient='R0',width=w, layer=('RX', 'port'))
        #         # (27.6/2,5.6-2.4275919117522138)
        Wg = AdiabaticRouter(gen_cls=self,
                             init_port=init_port11,
                             layer=('rxphot_noopc', 'drawing'),
                             name='init_port11')
        Wg.add_straight_wg(length=40)
        Wg.add_straight_wg(length=30, width=0.5)
        # Wg.add_offset_bend(offset=-40, rmin=10)

        mt_module = importlib.import_module(self.params['te_1300grating_params']['package'])
        mt_class = getattr(mt_module, self.params['te_1300grating_params']['class'])
        self.psr_parts_master['te_1300grating'] = self.new_template(params=self.params['te_1300grating_params'],
                                                                    temp_cls=mt_class)

        self.psr_parts['te_1300grating'] = self.add_instance_port_to_port(
            inst_master=self.psr_parts_master['te_1300grating'],
            instance_port_name='PORT_OUT',
            self_port=Wg.port,
            reflect=False)

        init_port6 = self.add_photonic_port(name='init_port6', center=(
            0, add), orient='R0',
                                             width=self.w, layer=('rxphot_noopc', 'port'))
        #         # init_port = self.add_photonic_port(name='init_port', center=(0,0), orient='R0',width=w, layer=('RX', 'port'))
        #         # (27.6/2,5.6-2.4275919117522138)
        Wg = AdiabaticRouter(gen_cls=self,
                             init_port=init_port6,
                             layer=('rxphot_noopc', 'drawing'),
                             name='init_port6')
        Wg.add_straight_wg(length=20)
        Wg.add_straight_wg(length=30, width=0.5)
        # Wg.add_offset_bend(offset=-40, rmin=10)

        mt_module = importlib.import_module(self.params['te_1300grating_params']['package'])
        mt_class = getattr(mt_module, self.params['te_1300grating_params']['class'])
        self.psr_parts_master['te_1300grating'] = self.new_template(params=self.params['te_1300grating_params'],
                                                                    temp_cls=mt_class)

        self.psr_parts['te_1300grating'] = self.add_instance_port_to_port(
            inst_master=self.psr_parts_master['te_1300grating'],
            instance_port_name='PORT_OUT',
            self_port=Wg.port,
            reflect=False)

        init_port14 = self.add_photonic_port(name='init_port14', center=(0+5, -add-2*gap), orient='R0',width=self.w, layer=('rxphot_noopc', 'port'))
        #         # init_port = self.add_photonic_port(name='init_port', center=(0,0), orient='R0',width=w, layer=('RX', 'port'))
        #         # (27.6/2,5.6-2.4275919117522138)
        Wg = AdiabaticRouter(gen_cls=self,
                             init_port=init_port14,
                             layer=('rxphot_noopc', 'drawing'),
                             name='init_port14')
        Wg.add_straight_wg(length=20)
        Wg.add_bend_180(rmin=20, turn_left=True, width=0.4)
        Wg.add_straight_wg(length=30, width=0.5)


        mt_module = importlib.import_module(self.params['te_1300grating_params']['package'])
        mt_class = getattr(mt_module, self.params['te_1300grating_params']['class'])
        self.psr_parts_master['te_1300grating'] = self.new_template(params=self.params['te_1300grating_params'],
                                                                    temp_cls=mt_class)
        self.psr_parts_master['te_1300grating'] = self.new_template(params=self.params['te_1300grating_params'],
                                                                    temp_cls=mt_class)

        self.psr_parts['te_1300grating'] = self.add_instance_port_to_port(
            inst_master=self.psr_parts_master['te_1300grating'],
            instance_port_name='PORT_OUT',
            self_port=Wg.port,
            reflect=False)

        # init_port15 = self.add_photonic_port(name='init_port15', center=(x_spacing + 5, -add-4*gap), orient='R0', width=self.w,
        #                                      layer=('rxphot_noopc', 'port'))
        # #         # init_port = self.add_photonic_port(name='init_port', center=(0,0), orient='R0',width=w, layer=('RX', 'port'))
        # #         # (27.6/2,5.6-2.4275919117522138)
        # Wg = AdiabaticRouter(gen_cls=self,
        #                      init_port=init_port15,
        #                      layer=('rxphot_noopc', 'drawing'),
        #                      name='init_port15')
        # Wg.add_straight_wg(length=20)
        # Wg.add_bend_180(rmin=5, turn_left=True, width=0.4)
        # Wg.add_straight_wg(length=30, width=0.5)
        #
        # mt_module = importlib.import_module(self.params['te_1300grating_params']['package'])
        # mt_class = getattr(mt_module, self.params['te_1300grating_params']['class'])
        # self.psr_parts_master['te_1300grating'] = self.new_template(params=self.params['te_1300grating_params'],
        #                                                             temp_cls=mt_class)
        # self.psr_parts_master['te_1300grating'] = self.new_template(params=self.params['te_1300grating_params'],
        #                                                             temp_cls=mt_class)
        #
        # self.psr_parts['te_1300grating'] = self.add_instance_port_to_port(
        #     inst_master=self.psr_parts_master['te_1300grating'],
        #     instance_port_name='PORT_OUT',
        #     self_port=Wg.port,
        #     reflect=False)
        #
        # init_port16 = self.add_photonic_port(name='init_port16', center=(2*x_spacing + 5, -add - 6*gap), orient='R0',
        #                                      width=self.w,
        #                                      layer=('rxphot_noopc', 'port'))
        # #         # init_port = self.add_photonic_port(name='init_port', center=(0,0), orient='R0',width=w, layer=('RX', 'port'))
        # #         # (27.6/2,5.6-2.4275919117522138)
        # Wg = AdiabaticRouter(gen_cls=self,
        #                      init_port=init_port16,
        #                      layer=('rxphot_noopc', 'drawing'),
        #                      name='init_port16')
        # Wg.add_straight_wg(length=20)
        # Wg.add_bend_180(rmin=5, turn_left=True, width=0.4)
        # Wg.add_straight_wg(length=30, width=0.5)
        #
        # mt_module = importlib.import_module(self.params['te_1300grating_params']['package'])
        # mt_class = getattr(mt_module, self.params['te_1300grating_params']['class'])
        # self.psr_parts_master['te_1300grating'] = self.new_template(params=self.params['te_1300grating_params'],
        #                                                             temp_cls=mt_class)
        # self.psr_parts_master['te_1300grating'] = self.new_template(params=self.params['te_1300grating_params'],
        #                                                             temp_cls=mt_class)
        #
        # self.psr_parts['te_1300grating'] = self.add_instance_port_to_port(
        #     inst_master=self.psr_parts_master['te_1300grating'],
        #     instance_port_name='PORT_OUT',
        #     self_port=Wg.port,
        #     reflect=False)
        #
        # init_port18 = self.add_photonic_port(name='init_port18', center=(3 * x_spacing + 5, -add - 8* gap),
        #                                      orient='R0',
        #                                      width=self.w,
        #                                      layer=('rxphot_noopc', 'port'))
        # #         # init_port = self.add_photonic_port(name='init_port', center=(0,0), orient='R0',width=w, layer=('RX', 'port'))
        # #         # (27.6/2,5.6-2.4275919117522138)
        # Wg = AdiabaticRouter(gen_cls=self,
        #                      init_port=init_port18,
        #                      layer=('rxphot_noopc', 'drawing'),
        #                      name='init_port18')
        # Wg.add_straight_wg(length=20)
        # Wg.add_bend_180(rmin=5, turn_left=True, width=0.4)
        # Wg.add_straight_wg(length=30, width=0.5)
        #
        # mt_module = importlib.import_module(self.params['te_1300grating_params']['package'])
        # mt_class = getattr(mt_module, self.params['te_1300grating_params']['class'])
        # self.psr_parts_master['te_1300grating'] = self.new_template(params=self.params['te_1300grating_params'],
        #                                                             temp_cls=mt_class)
        # self.psr_parts_master['te_1300grating'] = self.new_template(params=self.params['te_1300grating_params'],
        #                                                             temp_cls=mt_class)
        #
        # self.psr_parts['te_1300grating'] = self.add_instance_port_to_port(
        #     inst_master=self.psr_parts_master['te_1300grating'],
        #     instance_port_name='PORT_OUT',
        #     self_port=Wg.port,
        #     reflect=False)













        #salicide box in middle ring (self.params['y']+y_placer- self.params['placer'] / 2)

        # self.add_rect(layer=('sldphot', 'drawing'),
        #               bbox=BBox(left=-(self.params['heater_middle']+1),
        #                         bottom=-4,
        #                         right=-4,
        #                         top=4,
        #                         resolution=self.grid.resolution)
        #               )
        # self.add_rect(layer=('sldphot', 'drawing'),
        #               bbox=BBox(left=4,
        #                         bottom=-4,
        #                         right=(self.params['heater_middle']+1),
        #                         top=4,
        #                         resolution=self.grid.resolution)
        #               )
        # self.add_rect(layer=('sldphot', 'drawing'),
        #               bbox=BBox(left=-5,
        #                         bottom=-3,
        #                         right=5,
        #                         top=3,
        #                         resolution=self.grid.resolution)
        #               )



        # ring = self.new_template(params={'layer': ('rxphot_noopc', 'drawing'),
        #                                  'r_out': 5.6,
        #                                  'r_width': 0.6,
        #                                  'r_step': 0.04,
        #                                  'theta0': -90,
        #                                  'theta1': 90},
        #                          temp_cls=SimpleRound)
        # self.add_instance(master=ring, loc=[19, 0], inst_name='ring')
        #
        # ring = self.new_template(params={'layer': ('rxphot_noopc', 'drawing'),
        #                                  'r_out': 5.6,
        #                                  'r_width': 0.6,
        #                                  'r_step': 0.04,
        #                                  'theta0': 90,
        #                                  'theta1': 270},
        #                          temp_cls=SimpleRound)
        # self.add_instance(master=ring, loc=[-19, 0], inst_name='ring')
        #
        # ring = self.new_template(params={'layer': ('sldphot', 'drawing'),
        #                                  'r_out': 5.6,
        #                                  'r_width': 5.6,
        #                                  'r_step': 0.04},
        #                          temp_cls=SimpleRound)
        # self.add_instance(master=ring, loc=[19, 0], inst_name='ring')
        #
        # ring = self.new_template(params={'layer': ('sldphot', 'drawing'),
        #                                  'r_out': 5.6,
        #                                  'r_width': 5.6,
        #                                  'r_step': 0.04},
        #                          temp_cls=SimpleRound)
        # self.add_instance(master=ring, loc=[-19, 0], inst_name='ring')
        #
        # ring = self.new_template(params={'layer': ('nnphot', 'drawing'),
        #                                  'r_out': 5.6,
        #                                  'r_width': 5.6,
        #                                  'r_step': 0.04},
        #                          temp_cls=SimpleRound)
        # self.add_instance(master=ring, loc=[19, 0], inst_name='ring')
        #
        # ring = self.new_template(params={'layer': ('nnphot', 'drawing'),
        #                                  'r_out': 5.6,
        #                                  'r_width': 5.6,
        #                                  'r_step': 0.04},
        #                          temp_cls=SimpleRound)
        # self.add_instance(master=ring, loc=[-19, 0], inst_name='ring')











if __name__ == '__main__':
    spec_file = 'layout/Ring/specs/ring_with_heater_specs.yaml'
    plm = BPG.PhotonicLayoutManager(spec_file)
    plm.generate_content()
    plm.generate_gds()
    plm.generate_flat_content()
    plm.generate_flat_gds()
