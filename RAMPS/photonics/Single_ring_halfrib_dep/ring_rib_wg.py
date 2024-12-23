import BPG
import numpy as np
from bag.layout.util import BBox
from Photonic_Core_Layout.ViaStack.ViaStack import ViaStack
from Photonic_Core_Layout.AdiabaticPaths.AdiabaticPaths import AdiabaticPaths
from ..Single_ring_fullrib.ringheater import RingHeater
from ..Taper.StripToRibTaper import StripToRibTaper
from ..Spoke.SpokeBase_circular import SpokeBase
from typing import TYPE_CHECKING, List, Union, Optional
from BPG.objects import PhotonicPolygon, PhotonicRound, PhotonicRect


class RingRibWg_sr(BPG.PhotonicTemplateBase):
    """
    This class generates rib-waveguide ring modulator
    """

    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)

        # Initialize variables and dictionary of parameters
        self.ring_loc = (0, 0)
        self.g_pad_loc = None
        self.s_pad_loc = None

        self.heaterpad1_loc = None
        self.heaterpad2_loc = None
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
        self.si_spoke_offset_percentage=self.params['si_spoke_offset_percentage']

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
            # ring_spoked doping info bitches!

            doping_spoke_info='xcv',

            # Get additional ring information. Handle no extra rings properly
            extra_ring_info='xcv',
            spoke_num='xcv',
            label='xcv',

            outer_electrode_ring_layers='xcv',
            inner_electrode_ring_layers='xcv',

            # Advanced tech parameters
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
            si_spoke_offset_percentage='gjf',

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

            # ring_spoked doping info bitches!

            doping_spoke_info=None,

            # Get additional ring information. Handle no extra rings properly
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

        )

    def draw_layout(self):

        self.draw_halfrib_wg_ring()

        self.draw_Spokes(self.doping_spoke_info)


    def draw_Spokes(self, doping_spoke_info):
        rout = self.r_core_cent + self.core_width / 2
        ring_width = self.core_width / 2 + self.slab_width / 2
        rin = rout - ring_width
        p_via_radius = rin - self.p_via_radius_offset
        n_via_radius = rin - self.n_via_radius_offset

        self.outer_electrode_ring_layer_inds = []
        if not isinstance(self.outer_electrode_ring_layers, list):
            self.outer_electrode_ring_layers = [self.outer_electrode_ring_layers]
        for lpp in self.outer_electrode_ring_layers:
            self.outer_electrode_ring_layer_inds.append(self.grid.tech_info.get_layer_id(lpp[0]))
        self.outer_electrode_ring_layer_inds.sort()
        if self.outer_electrode_ring_layer_inds != list(range(min(self.outer_electrode_ring_layer_inds),
                                                              max(self.outer_electrode_ring_layer_inds) + 1)):
            raise ValueError(f'List of provided outer_electrode_ring_layers must be consecutive from bottom to top. '
                             f'Intermediate layer is missing.')

        self.inner_electrode_ring_layer_inds = []
        if not isinstance(self.inner_electrode_ring_layers, list):
            self.inner_electrode_ring_layers = [self.inner_electrode_ring_layers]
        for lpp in self.inner_electrode_ring_layers:
            self.inner_electrode_ring_layer_inds.append(self.grid.tech_info.get_layer_id(lpp[0]))
        self.inner_electrode_ring_layer_inds.sort()
        if self.inner_electrode_ring_layer_inds != list(range(min(self.inner_electrode_ring_layer_inds),
                                                              max(self.inner_electrode_ring_layer_inds) + 1)):
            raise ValueError(f'List of provided inner_electrode_ring_layers must be consecutive from bottom to top. '
                             f'Intermediate layer is missing.')

        if isinstance(self.label, str):
            label_p = self.label + '_P'
            label_n = self.label + '_N'
        elif isinstance(self.label, dict):
            if not ('P' in self.label.keys() and 'N' in self.label.keys()):
                raise ValueError(f'If specifying labels as a dictionary, must pass a '
                                 f'P and N key for the P and N labels')
            label_p = self.label['P']
            label_n = self.label['N']
        else:
            raise ValueError(f'parameter "label" must be of type string or dict with "P" and "N" entries.')

        if p_via_radius < n_via_radius:
            # inner electrode is p, outer is n
            p_electrode_layer_ind_list = self.inner_electrode_ring_layer_inds
            electrode_width_p = self.electrode_width_inner
            electrode_rout_p = p_via_radius - self.electrode_offset
            electrode_rin_p = electrode_rout_p - electrode_width_p

            n_electrode_layer_ind_list = self.outer_electrode_ring_layer_inds
            electrode_width_n = self.electrode_width_outer
            electrode_rin_n = n_via_radius + self.electrode_offset
            electrode_rout_n = electrode_rin_n + electrode_width_n

        else:
            # outer electrode is p, inner electrode is n
            p_electrode_layer_ind_list = self.outer_electrode_ring_layer_inds
            electrode_width_p = self.electrode_width_outer
            electrode_rin_p = p_via_radius + self.electrode_offset
            electrode_rout_p = electrode_rin_p + electrode_width_p

            n_electrode_layer_ind_list = self.inner_electrode_ring_layer_inds
            electrode_width_n = self.electrode_width_inner
            electrode_rout_n = n_via_radius - self.electrode_offset
            electrode_rin_n = electrode_rout_n - electrode_width_n

        high_doping_rout = rout - ring_width - self.high_doping_rout_offset
        high_doping_rin = min(p_via_radius, n_via_radius) - self.high_doping_rin_offset

        # Salicide ring:  Draw salicide ring if present in params
        if self.salicide_lpp:
            sld_rout = max(p_via_radius, n_via_radius) + self.salicide_radius_extension

            salicide_ring = PhotonicRound(
                layer=self.salicide_lpp,
                resolution=self.grid.resolution,
                center=self.ring_loc,
                rout=sld_rout + 1,
                unit_mode=False
            )
            self.add_obj(salicide_ring)

        # Draw the doping spokes and the extra ring information
        self.draw_doping_spokes(doping_spoke_info)
        self.draw_extra_rings(self.extra_ring_info)

        # Draw p silicon spokes and via stacks.  Via stack goes to the bottom-most electrode layer
        self.draw_contact_spokes_and_via_stack(
            r_via=p_via_radius,
            spoke_num=self.spoke_num,
            offset=self.p_contact_offset,
            bot_layer=self.bottom_metal_electrode_layer,
            top_layer=self.grid.tech_info.get_layer_name(max(p_electrode_layer_ind_list)),
            # top_layer=[self.grid.tech_info.get_layer_name(max(p_electrode_layer_ind_list))],
            label=label_p,
        )

        # Draw n silicon spokes and via stacks.  Via stack goes to the bottom-most electrode layer
        self.draw_contact_spokes_and_via_stack(
            r_via=n_via_radius,
            spoke_num=self.spoke_num,
            offset=self.n_contact_offset,
            bot_layer=self.bottom_metal_electrode_layer,
            top_layer=self.grid.tech_info.get_layer_name(max(p_electrode_layer_ind_list)),
            # top_layer=('BA','drawing'),
            label=label_n,
        )

        # p+ region around the p spokes for low resistance
        spoke_info_p = dict(
            rout=high_doping_rout,
            rin=high_doping_rin,
            num=self.spoke_num,
            spoke_width_percentage=1,
            spoke_offset=self.p_contact_offset,
            layer=self.high_p_doping_layer,
        )
        spoke_master_p = self.new_template(params=spoke_info_p, temp_cls=SpokeBase)
        #self.add_instance(  master=spoke_master_p,inst_name='high_p_doping',loc=self.ring_loc,orient="R0",unit_mode=False,)

        # n+ region around the n spokes for low resistance
        spoke_info_n = dict(
            rout=high_doping_rout,
            rin=high_doping_rin + self.high_doping_n_rin_offset,
            num=self.spoke_num,
            spoke_width_percentage=1,
            spoke_offset=self.n_contact_offset,
            layer=self.high_n_doping_layer,
        )
        spoke_master_n = self.new_template(params=spoke_info_n, temp_cls=SpokeBase)
        #self.add_instance(  master=spoke_master_n,inst_name='high_n_doping',loc=self.ring_loc,orient="R0",unit_mode=False,)

        # p contact rings. Spokes to the contact via stacks are only on the bottom most layer
        self.draw_electrode_ring_and_spokes(
            ring_layer_indices=[5],
            spoke_layer_indices=[5],
            electrode_rout=electrode_rout_p+0.4,
            electrode_rin=electrode_rin_p,
            via_radius=p_via_radius,
            spoke_num=self.spoke_num,
            offset=self.p_contact_offset,
        )

        # n contact rings. Spokes to the contact via stacks are only on the bottom most layer
        self.draw_electrode_ring_and_spokes(
            ring_layer_indices=[6],
            spoke_layer_indices=[6],
            electrode_rout=electrode_rout_n,
            electrode_rin=electrode_rin_n-0.4,
            via_radius=n_via_radius,
            spoke_num=self.spoke_num,
            offset=self.n_contact_offset,
        )

    def draw_halfrib_wg_ring(self):
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

        # Draw inner portion of slab
        slab_inner = self.add_round(
            layer=self.slab_layer,
            resolution=self.grid.resolution,
            rin=self.r_core_cent - self.slab_width / 2-0.08,
            rout=self.r_core_cent - self.slab_slot_width / 2,
            center=self.ring_loc)
        self.add_obj(slab_inner)

        # Draw inner portion of core
        core_inner = self.add_round(
            layer=self.core_layer,
            resolution=self.grid.resolution,
            rin=self.r_core_cent - self.slab_width / 2,
            rout=self.r_core_cent - self.slab_width / 2 + 0.1,
            center=self.ring_loc)
        #self.add_obj(core_inner)

    def draw_heater(self):

        if self.params['n_via_radius_offset'] < self.params['p_via_radius_offset']:
            t = self.params['p_via_radius_offset']
        else:
            t = self.params['n_via_radius_offset']

        heater_params = dict(
            rout=(self.params['r_core_cent'] - self.params['slab_width'] / 2 - 0.3 - t
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
        # ring_master = self.new_template(params=ring_params, temp_cls=RingBase)
        # ring_inst = self.add_instance(master=ring_master)

        # Add the heater if it should be present
        if not self.params['heater_disable']:
            # Compute the width from the heater resistance design function
            heater_params['width'] = RingHeater.design_heater_width_from_resistance(
                resistance=heater_params['resistance'],
                heater_rout=heater_params['rout'],
                r_square=self.photonic_tech_info.sheet_resistance(heater_params['device_layer']),
                contact_width=heater_params['contact_width'],
                contact_dist=heater_params['contact_dist'],
            )
            # heater_ring_Addition

            heater_master = self.new_template(params=heater_params, temp_cls=RingHeater)
            self.add_instance(master=heater_master, loc=(self.ring_loc[0], self.ring_loc[1]))

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
            port_renaming={'PORT_IN': 'PORT0',
                           'PORT_OUT': 'PORT1'},
            show=False)

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
        self.left_pad_loc = (self.ring_loc[0] - (self.gs_pad_pitch) / 2,
                             self.ring_loc[1] - self.gs_pad_to_ring_dist
                             )

        # calculate the corner coordinate of the right (signal) pad
        self.right_pad_loc = (self.ring_loc[0] + (self.gs_pad_pitch) / 2,
                              self.ring_loc[1] - self.gs_pad_to_ring_dist
                              )
        offset_distance = outer_pn_radius

        # draw left pad wiring
        wire1_top = self.ring_loc[1]
        wire1_bottom = wire1_top - self.gs_bottom_width
        wire1_left = self.left_pad_loc[0]
        wire1_right = -offset_distance
        self.add_rect(layer=self.outer_electrode_ring_layers[-1],
                      bbox=BBox(right=wire1_right,
                                bottom=wire1_bottom,
                                left=wire1_left,
                                top=wire1_top,
                                resolution=self.grid.resolution)
                      )

        wire2_top = wire1_top
        wire2_bottom = self.left_pad_loc[1] - dim1 / 2
        wire2_left = self.left_pad_loc[0]
        wire2_right = wire2_left + self.gs_bottom_width
        self.add_rect(layer=self.outer_electrode_ring_layers[-1],
                      bbox=BBox(right=wire2_right,
                                bottom=wire2_bottom,
                                left=wire2_left,
                                top=wire2_top,
                                resolution=self.grid.resolution)
                      )

        # draw right pad wiring
        wire1_top = -(inner_pn_radius)
        wire1_bottom = -12 * offset_distance
        wire1_left = -self.gs_bottom_width / 2
        wire1_right = self.gs_bottom_width / 2
        self.add_rect(layer=self.inner_electrode_ring_layers[-1],
                      bbox=BBox(right=wire1_right,
                                bottom=wire1_bottom,
                                left=wire1_left,
                                top=wire1_top,
                                resolution=self.grid.resolution)
                      )

        wire2_top = wire1_bottom + self.gs_bottom_width
        wire2_bottom = wire1_bottom
        wire2_left = wire1_left
        wire2_right = self.right_pad_loc[0] + self.gs_bottom_width / 2
        self.add_rect(layer=self.inner_electrode_ring_layers[-1],
                      bbox=BBox(right=wire2_right,
                                bottom=wire2_bottom,
                                left=wire2_left,
                                top=wire2_top,
                                resolution=self.grid.resolution)
                      )

        wire3_top = wire2_top
        wire3_bottom = self.right_pad_loc[1] - dim1 / 2
        wire3_left = wire2_right - self.gs_bottom_width / 2
        wire3_right = wire2_right + self.gs_bottom_width / 2
        self.add_rect(layer=self.inner_electrode_ring_layers[-1],
                      bbox=BBox(right=wire3_right,
                                bottom=wire3_bottom,
                                left=wire3_left,
                                top=wire3_top,
                                resolution=self.grid.resolution)
                      )

        # lower outer metal contact to the level of higher inner metal contact
        via_stack_master = self.new_template(params=dict(top_layer=self.inner_electrode_ring_layers[-1],
                                                         bottom_layer=self.outer_electrode_ring_layers[-1],
                                                         top_x_span=self.gs_bottom_width,
                                                         top_y_span=self.gs_bottom_length,
                                                         bottom_x_span=self.gs_bottom_width,
                                                         bottom_y_span=self.gs_bottom_length,
                                                         align='center_align',
                                                         top_bot_offset=0.0),
                                             temp_cls=ViaStack)

        self.add_instance(master=via_stack_master,
                          inst_name='S_to_G_layer_via_stack',
                          loc=(self.left_pad_loc[0], self.left_pad_loc[1] - dim1 / 2),
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
        self.left_pad_loc = (self.ring_loc[0] - (self.gs_pad_pitch) / 2,
                             self.ring_loc[1] - self.gs_pad_to_ring_dist
                             )

        # calculate the corner coordinate of the right (signal) pad
        self.right_pad_loc = (self.ring_loc[0] + (self.gs_pad_pitch) / 2,
                              self.ring_loc[1] - self.gs_pad_to_ring_dist
                              )
        self.add_rect(layer=self.gs_pad_layer,
                      bbox=BBox(left=self.left_pad_loc[0] - self.gs_pad_width / 2,
                                bottom=self.left_pad_loc[1] - self.gs_pad_length - dim1,
                                right=self.left_pad_loc[0] + self.gs_pad_width / 2,
                                top=self.left_pad_loc[1],
                                resolution=self.grid.resolution)
                      )
        self.add_rect(layer=self.gs_pad_open_layer,
                      bbox=BBox(left=self.left_pad_loc[0] - self.gs_pad_width / 2 + self.gs_pad_open_inclusion,
                                bottom=self.left_pad_loc[1] - self.gs_pad_length - dim1 + self.gs_pad_open_inclusion,
                                right=self.left_pad_loc[0] + self.gs_pad_width / 2 - self.gs_pad_open_inclusion,
                                top=self.left_pad_loc[1] - dim1,
                                resolution=self.grid.resolution)
                      )
        # Place right pad open layer and pad llayer exclusion
        self.add_rect(layer=self.gs_pad_layer,
                      bbox=BBox(left=self.right_pad_loc[0] - self.gs_pad_width / 2,
                                bottom=self.right_pad_loc[1] - self.gs_pad_length - dim1,
                                right=self.right_pad_loc[0] + self.gs_pad_width / 2,
                                top=self.right_pad_loc[1],
                                resolution=self.grid.resolution)
                      )

        self.add_rect(layer=self.gs_pad_open_layer,
                      bbox=BBox(left=self.right_pad_loc[0] - self.gs_pad_width / 2 + self.gs_pad_open_inclusion,
                                bottom=self.left_pad_loc[1] - self.gs_pad_length - dim1 + self.gs_pad_open_inclusion,
                                right=self.right_pad_loc[0] + self.gs_pad_width / 2 - self.gs_pad_open_inclusion,
                                top=self.left_pad_loc[1] - dim1,
                                resolution=self.grid.resolution)
                      )

        # Place left pad electrode
        self.add_instance(master=gs_electrode_master,
                          inst_name='G_electrode',
                          loc=(self.left_pad_loc[0], self.left_pad_loc[1] - dim1 / 2),
                          orient='R90')

        # Place right pad electrode
        self.add_instance(master=gs_electrode_master,
                          inst_name='S_electrode',
                          loc=(self.right_pad_loc[0], self.right_pad_loc[1] - dim1 / 2),
                          orient='R90')

    def place_heater_contact_electrodes(self):
        # calculate the corner coordinate of the left (ground) pad
        # calculate the corner coordinate of the left (ground) pad
        dim1 = 11.7
        dim2 = dim1  # 10.722 + 6.72 - 5.812
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
        self.left_pad_loc = (self.ring_loc[0] - (self.gs_pad_pitch) / 2,
                             self.ring_loc[1] - self.gs_pad_to_ring_dist
                             )

        # calculate the corner coordinate of the right (signal) pad
        self.right_pad_loc = (self.ring_loc[0] + (self.gs_pad_pitch) / 2,
                              self.ring_loc[1] - self.gs_pad_to_ring_dist
                              )
        offset_distance = outer_pn_radius
        self.heaterpad1_loc = (
            self.ring_loc[0] - (self.gs_pad_pitch) / 2, self.ring_loc[1] + self.heater_pad_to_ring_dist)
        self.heaterpad2_loc = (
            self.ring_loc[0] + (self.gs_pad_pitch) / 2, self.ring_loc[1] + self.heater_pad_to_ring_dist)

        metal_width = 1.6

        # heater wiring to the left upper pad
        wire1_top = 6 * offset_distance
        wire1_bottom = 0
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

        # # heater wiring to the right upper pad
        wire1_top = 6 * offset_distance
        wire1_bottom = 0
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
        wire2_right = self.heaterpad2_loc[0]
        self.add_rect(layer=self.heater_electrode_top_layer,
                      bbox=BBox(right=wire2_right,
                                bottom=wire2_bottom,
                                left=wire2_left,
                                top=wire2_top,
                                resolution=self.grid.resolution)
                      )

        wire3_top = self.heaterpad2_loc[1] + dim1 / 2
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

        self.heaterpad1_loc = (
        self.ring_loc[0] - (self.gs_pad_pitch) / 2, self.ring_loc[1] + self.heater_pad_to_ring_dist)
        self.heaterpad2_loc = (
        self.ring_loc[0] + (self.gs_pad_pitch) / 2, self.ring_loc[1] + self.heater_pad_to_ring_dist)

        # Place heater pad 1
        self.add_rect(layer=self.gs_pad_layer,
                      bbox=BBox(left=self.heaterpad1_loc[0] - self.gs_pad_width / 2,
                                bottom=self.heaterpad1_loc[1],
                                right=self.heaterpad1_loc[0] + self.gs_pad_width / 2,
                                top=self.heaterpad1_loc[1] + self.gs_pad_length + dim1,
                                resolution=self.grid.resolution)
                      )

        self.add_rect(layer=self.gs_pad_open_layer,
                      bbox=BBox(left=self.heaterpad1_loc[0] - self.gs_pad_width / 2 + self.gs_pad_open_inclusion,
                                bottom=self.heaterpad1_loc[1] + dim1,
                                right=self.heaterpad1_loc[0] + self.gs_pad_width / 2 - self.gs_pad_open_inclusion,
                                top=self.heaterpad1_loc[1] + self.gs_pad_length + dim1 - self.gs_pad_open_inclusion,
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
                                bottom=self.heaterpad2_loc[1] + dim1,
                                right=self.heaterpad2_loc[0] + self.gs_pad_width / 2 - self.gs_pad_open_inclusion,
                                top=self.heaterpad2_loc[1] + self.gs_pad_length + dim1 - self.gs_pad_open_inclusion,
                                resolution=self.grid.resolution)
                      )
        # Place heater pad 1




        # Place heater pad 3
        self.add_instance(master=gs_electrode_master,
                          inst_name='G_electrode',
                          loc=(self.heaterpad1_loc[0], self.heaterpad1_loc[1] + dim1 / 2),
                          orient='R90')
        # Place heater pad 4
        self.add_instance(master=gs_electrode_master,
                          inst_name='G_electrode',
                          loc=(self.heaterpad2_loc[0], self.heaterpad2_loc[1] + dim1 / 2),
                          orient='R90')

    def draw_doping_spokes(self, doping_spoke_info):
        """Draw all the doping spokes"""
        if self.doping_spoke_info:
            for i, doping_spoke_info in enumerate(self.doping_spoke_info):
                spoke_master = self.new_template(params=doping_spoke_info, temp_cls=SpokeBase)
                self.add_instance(
                    master=spoke_master,
                    inst_name='doping_spokes_' + str(i),
                    loc=self.ring_loc,
                    orient="R0",
                    unit_mode=False,
                )

    def draw_extra_rings(self, extra_ring_info):
        """Draw any extra rings in the design. May be present for SiGe or counter doping"""
        if self.extra_ring_info:
            for i, extra_ring_info in enumerate(self.extra_ring_info):
                ring = PhotonicRound(
                    layer=extra_ring_info['layer'],
                    resolution=self.grid.resolution,
                    center=self.ring_loc,
                    rout=extra_ring_info['rout'],
                    rin=extra_ring_info['rout'] - extra_ring_info['ring_width'],
                    unit_mode=False,
                )
                self.add_obj(ring)

    def draw_electrode_ring_and_spokes(self,
                                       ring_layer_indices: Union[int, List[int]],
                                       spoke_layer_indices: Union[int, List[int]],
                                       electrode_rout: float,
                                       electrode_rin: float,
                                       via_radius: float,
                                       spoke_num: int,
                                       offset: float,
                                       ) -> None:
        """
        Draws the electrode ring stack and the spokes to the via stack going to the silicon contacts.
        Spokes are drawn to be 2*min_width at the via location. If spoke goes radially inward, it will get more narrow.
        If spoke goes radially outward, it will get wider.

        Parameters
        ----------
        ring_layer_indices : Union[int, List[int]]
            A layer index or list of layer indices on which the ring electrodes should be drawn.
        spoke_layer_indices : Union[int, List[int]]
            A layer index or list of layer indices on which the metal spokes to the contact via stack should be drawn.
        electrode_rout : float
            Outer radius of the ring electrode
        electrode_rin : float
            Inner radius of the ring electrode
        via_radius : float
            Radius at which the silicon contact via stack are located. Can be inside or outside the ring electrode
        spoke_num : int
            Number of spokes in the design
        offset : float
            Offset angle of the spoke, in units of 2pi/spoke_num radians. Should most likely be 0 or 0.5.

        Returns
        -------

        """
        # Draw the electrode rings and vias between them
        self.draw_electrode_ring_stack(ring_layer_indices, electrode_rout, electrode_rin)

        if not isinstance(spoke_layer_indices, list):
            spoke_layer_indices = [spoke_layer_indices]

        # Draw the spokes to the contact via stacks
        for layer_ind in spoke_layer_indices:
            # Check to make sure valid spoke layer
            if layer_ind not in ring_layer_indices:
                raise ValueError(f'Spoke layer index {layer_ind} not in "ring_layer_indices"')

            # Calculate the width of the spokes based on the min with of the current layer and the number of spokes
            # Calculation here is = 2*min_width / (arc_length of 100% spoke at the desired radius radius)
            if max(ring_layer_indices) == 5:
                ratio = 8
            
            if max(ring_layer_indices) == 6:
                ratio = 1
            spoke_width_percentage = ratio*2 * self.photonic_tech_info.min_width(
                self.grid.tech_info.get_layer_name(layer_ind)
            ) / (np.pi * via_radius / spoke_num)

            # Initialize and place the spokes
            spoke_info = dict(
                rout=via_radius + 0.1 if via_radius > electrode_rout + 0.1 else electrode_rin,
                rin=via_radius-0.1 if via_radius < electrode_rin else electrode_rout,
                num=spoke_num,
                spoke_width_percentage=spoke_width_percentage,
                spoke_offset=offset,
                # get_layer name returns only layer, hardcode 'drawing' purpose as this is a metal
                layer=(self.grid.tech_info.get_layer_name(layer_ind), 'drawing'),
            )
            spoke_master = self.new_template(params=spoke_info, temp_cls=SpokeBase)
            self.add_instance(
                master=spoke_master,
                inst_name='electrode_spokes',
                loc=self.ring_loc,
                orient="R0",
                unit_mode=False,
            )

    def draw_contact_spokes_and_via_stack(self,
                                          r_via: float,
                                          spoke_num: int,
                                          offset: float,
                                          bot_layer: "layer_or_lpp_type",
                                          top_layer: "layer_or_lpp_type",
                                          label: Optional[str] = None,
                                          ):

        # def draw_heater_ring(self):
        """
        Draws the silicon spokes and contact vias to contact the doped n and p regions.
        Draws a via stack up to the top_layer param
        Adds a contact label to the bottom_electrode_label_layer for each via, if bottom_electrode_label_layer is not
        none.

        Parameters
        ----------
        r_via : float
            Radius at which the vias should be placed
        spoke_num : int
            Number of spokes in the design
        offset : float
            Offset angle of the spoke, in units of 2pi/spoke_num radians. Should most likely be 0 or 0.5.
        bot_layer : Union[str, Tuple[str, str]]
            Layer or LPP of the bottom layer to which the via stacks should be drawn
        top_layer : Union[str, Tuple[str, str]]
            Layer or LPP of the top layer to which the via stacks should be drawn
        label : str
            Text label to be placed on the bottom electrode label layer

        """
        # Place vias for each spoke
        delta_theta = 2 * np.pi / spoke_num
        offset_theta = offset * delta_theta

        rout = self.r_core_cent + self.core_width / 2
        ring_width = self.core_width / 2 + self.slab_width / 2
        rin = rout - ring_width
        for i in range(spoke_num):
            theta = i * delta_theta + offset_theta
            via_loc = (np.cos(theta) * r_via + self.ring_loc[0], np.sin(theta) * r_via + self.ring_loc[1])
            self.add_via_stack(
                bot_layer=bot_layer,
                top_layer=top_layer,
                loc=via_loc
            )
            if offset == 0:
                metal_ring_vias = self.new_template(params=dict(top_layer=('BA','drawing'),
                                                                bottom_layer=('M1','drawing'),
                                                                top_x_span=0.25,  # self.gs_pad_width,
                                                                top_y_span=0.25,
                                                                bottom_x_span=0.25,
                                                                bottom_y_span=0.25,
                                                                align='center_align',
                                                                top_bot_offset=0.0
                                                                # pad_open_layer=self.gs_pad_open_layer,
                                                                # pad_open_inclusion=self.gs_pad_open_inclusion
                                                                ),
                                                    temp_cls=ViaStack)
                self.add_instance(master=metal_ring_vias,
                                inst_name='test_metal_ring_vias',
                                loc=via_loc,
                                orient='R90')
                if i == 2:#or i==6 or i==10 or i==14:
                    patch_width = 0.2
                    num_of_patch = 150
                    delta_theta_pacth = 2*3.1415/150
                    theta_patch = i * delta_theta
                    change_y_bottom = 0
                    change_x_left = 0
                    for j in range(num_of_patch):
                        if j >=0:
                            if j == 95 or j == 18:
                                change_in_x = 0.5
                            else:
                                change_in_x=0
                                
                            if j == 132 or j == 55:
                                change_in_y = 0.5
                            else:
                                change_in_y=0
                                
                            if j == 130:
                                change_y_bottom = -0.5
                                
                            if j == 20:
                                change_x_left = -0.5
                            k = j-num_of_patch//2
                            centre_offset = 0.63
                            patch_centre = (np.cos(theta_patch+k*delta_theta_pacth) * (r_via+centre_offset) + self.ring_loc[0], np.sin(theta_patch+k*delta_theta_pacth) * (centre_offset+r_via) + self.ring_loc[1])
                            self.add_rect(layer=('M5','drawing'),
                                bbox=BBox(right=patch_centre[0]+0.5*patch_width+change_in_x,
                                        bottom=patch_centre[1]-0.5*patch_width+change_y_bottom,
                                        left=patch_centre[0]-0.5*patch_width+change_x_left,
                                        top=patch_centre[1]+0.5*patch_width+change_in_y,
                                        resolution=self.grid.resolution)
                                
                            )
                    delta_theta_pacth_out = 0.035
                    num_of_patch_out = 27
                    for j in range(num_of_patch_out):
                        k = j-num_of_patch_out//2
                        theta_patch = i * delta_theta
                        centre_offset = 0.44+1.45
                        patch_centre = (np.cos(theta_patch+k*delta_theta_pacth_out) * (r_via+centre_offset) + self.ring_loc[0], np.sin(theta_patch+k*delta_theta_pacth_out) *(r_via+centre_offset) + self.ring_loc[1])
                        self.add_rect(layer=('M5','drawing'),
                            bbox=BBox(right=patch_centre[0]+0.5*patch_width,
                                    bottom=patch_centre[1]-0.5*patch_width,
                                    left=patch_centre[0]-0.5*patch_width,
                                    top=patch_centre[1]+0.5*patch_width,
                                    resolution=self.grid.resolution)
                            
                        )
                        
                if i == 6 or i==10 or i==14:
                    patch_width = 0.2
                    num_of_patch = 150
                    delta_theta_pacth = 2*3.1415/150
                    theta_patch = i * delta_theta
                    
                    delta_theta_pacth_out = 0.035
                    num_of_patch_out = 27
                    for j in range(num_of_patch_out):
                        k = j-num_of_patch_out//2
                        theta_patch = i * delta_theta
                        centre_offset = 0.44+1.45
                        patch_centre = (np.cos(theta_patch+k*delta_theta_pacth_out) * (r_via+centre_offset) + self.ring_loc[0], np.sin(theta_patch+k*delta_theta_pacth_out) *(r_via+centre_offset) + self.ring_loc[1])
                        self.add_rect(layer=('M5','drawing'),
                            bbox=BBox(right=patch_centre[0]+0.5*patch_width,
                                    bottom=patch_centre[1]-0.5*patch_width,
                                    left=patch_centre[0]-0.5*patch_width,
                                    top=patch_centre[1]+0.5*patch_width,
                                    resolution=self.grid.resolution)
                            
                        )
                
                if offset == 0.5:
                    metal_ring_vias = self.new_template(params=dict(top_layer=('M5','drawing'),
                                                                    bottom_layer=('M1','drawing'),
                                                                    top_x_span=0.25,  # self.gs_pad_width,
                                                                    top_y_span=0.25,
                                                                    bottom_x_span=0.25,
                                                                    bottom_y_span=0.25,
                                                                    align='center_align',
                                                                    top_bot_offset=0.0
                                                                    # pad_open_layer=self.gs_pad_open_layer,
                                                                    # pad_open_inclusion=self.gs_pad_open_inclusion
                                                                    ),
                                                        temp_cls=ViaStack)
                    self.add_instance(master=metal_ring_vias,
                                    inst_name='test_metal_ring_vias',
                                    loc=via_loc,
                                    orient='R90')
                
        
            

            # Add p and n contact labels if label layer and label string are passed
            if self.bottom_electrode_label_layer and label:
                label_bbox = BBox(left=via_loc[0],
                                  bottom=via_loc[1],
                                  right=via_loc[0] + self.grid.resolution,
                                  top=via_loc[1] + self.grid.resolution,
                                  resolution=self.grid.resolution,
                                  unit_mode=False
                                  )
                self.add_label(label=label,
                               layer=(self.bottom_electrode_label_layer[0], "label"),
                               bbox=label_bbox
                               )

        # Calculate the width of the spokes, based on the min width of the silicon layer and the number of spokes
        spoke_width_percentage = 2 * self.photonic_tech_info.min_width(self.layer) / (
            np.pi * rin / spoke_num) + self.si_spoke_offset_percentage

        # Initialize and place the spokes
        spoke_info = dict(
            rout=rin,
            rin=r_via-0.15, # to push the spokes inward and cover the square
            num=spoke_num,
            spoke_width_percentage=spoke_width_percentage,
            spoke_offset=offset,
            layer=self.layer,
        )
        spoke_master = self.new_template(params=spoke_info, temp_cls=SpokeBase)
        self.add_instance(
            master=spoke_master,
            inst_name='via_spokes',
            loc=self.ring_loc,
            orient="R0",
            unit_mode=False,
        )

    def draw_electrode_ring_stack(self,
                                  layer_indices: Union[int, List[int]],
                                  rout: float,
                                  rin: float,
                                  ) -> None:
        """
        Draw the electrode ring on the list of layers provided, and connect by uniformly spaced vias.

        Parameters
        ----------
        layer_indices : Union[int, List[int]]
            A layer index or list of layer indices on which the electrode ring should be drawn.
        rout : float
            The outer radius of the electrode ring.
        rin : float
            The inner radius of the electrode ring.

        """
        # For each layer, place an electrode ring
        for layer_ind in layer_indices:
            ring = PhotonicRound(
                # get_layer name returns only layer, hardcode 'drawing' purpose as this is a metal
                layer=(self.grid.tech_info.get_layer_name(layer_ind), 'drawing'),
                resolution=self.grid.resolution,
                center=self.ring_loc,
                rout=rout,
                rin=rin,
                unit_mode=False
            )
            self.add_obj(ring)

        # Get top layer of via stack
        top_layer_ind = max(layer_indices)

        # Place vias in the center radius of the electrode ring. They are spaced based on the maximum
        via_radius = (rout + rin) / 2
        via_spacing = 3 * self.photonic_tech_info.min_width(
            self.grid.tech_info.get_layer_name(top_layer_ind)
        )
        num_vias = int(2 * np.pi * via_radius // via_spacing)
        via_theta = 2 * np.pi / num_vias

        for i in range(num_vias):
            self.add_via_stack_by_ind(
                bot_layer_ind=min(layer_indices),
                top_layer_ind=top_layer_ind,
                loc=(via_radius * np.cos(via_theta * i), via_radius * np.sin(via_theta * i)),
                min_area_on_bot_top_layer=False,
                unit_mode=False,

            )


if __name__ == '__main__':
    spec_file = 'Single_ring_halfrib_dep/specs/ring_rib_wg_specs.yaml'
    PLM = BPG.PhotonicLayoutManager(spec_file)
    PLM.generate_content()
    PLM.generate_gds()
    # PLM.generate_flat_content()
    # PLM.generate_flat_gds()
    PLM.dataprep_calibre()