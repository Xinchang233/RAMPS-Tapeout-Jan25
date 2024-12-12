import numpy as np
from copy import deepcopy
import BPG
from BPG.objects import PhotonicPolygon, PhotonicRound, PhotonicRect
from bag.layout.util import BBox

from Photonic_Core_Layout_Djordje.Spoke.SpokeBase import SpokeBase
from Photonic_Core_Layout_Djordje.WaveguideBase.CosineWaveguide import CosineWaveguide

from typing import TYPE_CHECKING, List, Union, Optional
from Photonic_Core_Layout.ViaStack_test.ViaStack import ViaStack
from layout.Importers.Gratings.higheff1300lm5um.GcUnidirWl1300nmMfd5000nmApodDown_fromAL11A import GcUnidirWl1300nmMfd5000nmApodDown_fromAL11A
# layout/Importers/Gratings/1300_high_eff_5um/GcUnidirWl1300nmMfd5000nmApodDown_fromAL11A.py
# from layout.Importers.Gratings.bidirectional.GcBidirWl1300nmMfd9200nm import GcBidirWl1300nmMfd9200nmCurved
# layout/Importers/Gratings/bidirectional/GcBidirWl1300nmMfd9200nm.py
from Photonic_Core_Layout.AdiabaticPaths.AdiabaticPaths import AdiabaticPaths

if TYPE_CHECKING:
    from BPG.bpg_custom_types import layer_or_lpp_type


class RingBase(BPG.PhotonicTemplateBase):
    """
    Base ring class

    For contact electrodes:
        inner_electrode_ring_layers: layers on which the inner electrode ring is drawn
        outer_electrode_ring_layers: layers on which the outer electrode ring is drawn

        The spokes from the electrode ring to the via stack going to the silicon layer are drawn only on the lowest
        electrode layer for each of the outer and inner rings.

        The contact labels are placed on the top layer for each of the outer and inner rings.

    n contact spokes are hardcoded as being on the +x axis.

    The inner electrode will belong to the n/p that has the shorter offset (n_via_radius_offset vs p_via_radius_offset)
    if n_via_radius_offset < p_via_radius_offset:
        p contact is inside, n contact is outside


    """

    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)

        # Hard coded params
        self.ring_loc = (0, 0)
        self.n_contact_offset = 0  # n spoke is aligned on the +x axis
        self.p_contact_offset = 0.5  # p spoke is offset

        # Standard parameters: can change between designs in a technology.
        self.rout = None
        self.ring_width = None
        self.layer = None
        self.doping_spoke_info = None
        self.extra_ring_info = None
        self.spoke_num = None
        self.coupling_slot = None
        self.drop_slot = None
        self.wg_width = None
        self.label = None
        self.label_p = None
        self.label_n = None

        self.outer_electrode_ring_layers = None
        self.inner_electrode_ring_layers = None

        # Advanced parameters: can change between designs per technology, but not recommended for standard users
        self.p_via_radius_offset = None
        self.n_via_radius_offset = None
        self.high_doping_rin_offset = None
        self.high_doping_rout_offset = None
        self.electrode_offset = None
        self.electrode_width_inner = None
        self.electrode_width_outer = None
        self.access_length = None
        self.drop_taper_length = None
        self.salicide_radius_extension = None
        self.high_doping_n_rin_offset = None

        # Advanced tech params: should not need to change between designs in a given technology
        self.high_n_doping_layer = None
        self.high_p_doping_layer = None
        self.salicide_lpp = None
        self.bottom_metal_electrode_layer = None
        self.bottom_electrode_label_layer = None

        # Derived parameters
        self.rin = None
        self.p_via_radius = None
        self.n_via_radius = None
        self.high_doping_rout = None
        self.high_doping_rin = None
        self.sld_rout = None
        self.p_electrode_layer_ind_list = None
        self.n_electrode_layer_ind_list = None
        self.inner_electrode_ring_layer_inds = None
        self.outer_electrode_ring_layer_inds = None

        self.gs_electrod_params = params['gs_electrod_params']
        self.add_grating_left = params['add_grating_left']
        self.add_grating_right = params['add_grating_right']
        self.grating_distance = params['grating_distance']
        self.grating_band_radius = params['grating_band_radius']
        self.draw_pads = params['draw_pads']
        self.reflect = params['reflect']

    @classmethod
    def get_default_param_values(cls):
        return dict(
            # Standard parameters
            drop_slot=-1,  # Do not have a drop port
            bottom_electrode_label_layer=None,  # Do not place a label on the bottom metal layer
        )

    @classmethod
    def get_params_info(cls):  # Returns definition of the parameters.
        return dict(
            # Standard parameters
            rout='Outer radius of ring',
            ring_width='Ring width',
            layer='Layer or LPP of the main ring and spokes',
            doping_spoke_info='List of spoke doping dictionaries containing: rout, rin, num, layer, '
                              'spoke_width_percentage, spoke_offset',
            extra_ring_info='List of extra ring dictionaries containing: rout, ring_width, layer',
            spoke_num='Number of n or p spokes (total spoke number is 2x this value',
            coupling_slot='Ring to access waveguide gap.',
            drop_slot='Ring to drop port gap',
            wg_width='Width of the access waveguide.',
            label='Ring contact label text [str], or dictionary with keys P: <p_label> and N: <n_label>',

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
            gs_electrod_params='Parameters needed to create a gs elector pads',
            add_grating_left='Boolian value used to determined if grating is placed on the left end of the access wg',
            add_grating_right='Boolean value used to determined if grating is placed on the right end of the access wg',
            grating_distance='Horizontal distance between the gratings, if both gratings are placed. If one grating is'
                             'placed, then this is the padded RX added to the waveguide before the grating',
            grating_band_radius='Radius of the bend. When zero, straight waveguide is generated of len grating_distance',
            draw_pads='Boolean determining if GS pads are instantiated',
            reflect = 'Boolean determining orientation of grating coupler'
        )

    @staticmethod
    def check_lpp_entry(lpp_entry, lpp_entry_name):
        if not ((lpp_entry is None) or (isinstance(lpp_entry, tuple) and len(lpp_entry) == 2
                                        and isinstance(lpp_entry[0], str) and isinstance(lpp_entry[1], str))):
            raise ValueError(f'LPP entry "{lpp_entry_name}" must be a tuple of two strings. Received {lpp_entry}')

    def draw_layout(self):
        ################################################################################
        # Check parameter validity
        ################################################################################
        # Standard parameters
        self.rout = self.params['rout']
        self.ring_width = self.params['ring_width']
        self.layer = self.params['layer']
        # Get doping spoke information. Handle no doping properly
        self.doping_spoke_info = self.params['doping_spoke_info']
        if self.doping_spoke_info is not None:
            if not isinstance(self.doping_spoke_info, list):
                self.doping_spoke_info = [self.doping_spoke_info]
        # Get additional ring information. Handle no extra rings properly
        self.extra_ring_info = self.params['extra_ring_info']
        if self.extra_ring_info is not None:
            if not isinstance(self.extra_ring_info, list):
                self.extra_ring_info = [self.extra_ring_info]

        self.spoke_num = self.params['spoke_num']
        self.coupling_slot = self.params['coupling_slot']
        self.drop_slot = self.params['drop_slot']
        self.wg_width = self.params['wg_width']

        self.label = self.params['label']
        if isinstance(self.label, str):
            self.label_p = self.label + '_P'
            self.label_n = self.label + '_N'
        elif isinstance(self.label, dict):
            if not ('P' in self.label.keys() and 'N' in self.label.keys()):
                raise ValueError(f'If specifying labels as a dictionary, must pass a '
                                 f'P and N key for the P and N labels')
            self.label_p = self.label['P']
            self.label_n = self.label['N']
        else:
            raise ValueError(f'parameter "label" must be of type string or dict with "P" and "N" entries.')

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

        # Check LPP validity
        check_lpps_list = ['high_n_doping_layer', 'high_p_doping_layer',
                           'salicide_lpp', 'bottom_electrode_label_layer']
        for lpp in check_lpps_list:
            self.check_lpp_entry(self.params[lpp], lpp)

        ################################################################################
        # Process the ring electrode layers
        ################################################################################
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

        ################################################################################
        # Drawing ring and spokes
        ################################################################################
        # Derived parameters:
        self.rin = self.rout - self.ring_width
        self.p_via_radius = self.rin - self.p_via_radius_offset
        self.n_via_radius = self.rin - self.n_via_radius_offset
        if self.p_via_radius < self.n_via_radius:
            # inner electrode is p, outer is n
            self.p_electrode_layer_ind_list = self.inner_electrode_ring_layer_inds
            electrode_width_p = self.electrode_width_inner
            electrode_rout_p = self.p_via_radius - self.electrode_offset
            electrode_rin_p = electrode_rout_p - electrode_width_p

            self.n_electrode_layer_ind_list = self.outer_electrode_ring_layer_inds
            electrode_width_n = self.electrode_width_outer
            electrode_rin_n = self.n_via_radius + self.electrode_offset
            electrode_rout_n = electrode_rin_n + electrode_width_n

        else:
            # outer electrode is p, inner electrode is n
            self.p_electrode_layer_ind_list = self.outer_electrode_ring_layer_inds
            electrode_width_p = self.electrode_width_outer
            electrode_rin_p = self.p_via_radius + self.electrode_offset
            electrode_rout_p = electrode_rin_p + electrode_width_p

            self.n_electrode_layer_ind_list = self.inner_electrode_ring_layer_inds
            electrode_width_n = self.electrode_width_inner
            electrode_rout_n = self.n_via_radius - self.electrode_offset
            electrode_rin_n = electrode_rout_n - electrode_width_n

        self.high_doping_rout = self.rout - self.ring_width - self.high_doping_rout_offset
        self.high_doping_rin = min(self.p_via_radius, self.n_via_radius) - self.high_doping_rin_offset

        # Draw silicon ring
        self.create_silicon_ring()

        # Salicide ring:  Draw salicide ring if present in params
        if self.salicide_lpp:
            self.sld_rout = max(self.p_via_radius, self.n_via_radius) + self.salicide_radius_extension

            salicide_ring = PhotonicRound(
                layer=self.salicide_lpp,
                resolution=self.grid.resolution,
                center=self.ring_loc,
                rout=self.sld_rout + 1,
                unit_mode=False
            )
            self.add_obj(salicide_ring)

        # Draw the doping spokes and the extra ring information
        self.draw_doping_spokes()
        self.draw_extra_rings()

        # Draw p silicon spokes and via stacks.  Via stack goes to the bottom-most electrode layer
        self.draw_contact_spokes_and_via_stack(
            r_via=self.p_via_radius,
            spoke_num=self.spoke_num,
            offset=self.p_contact_offset,
            bot_layer=self.bottom_metal_electrode_layer,
            top_layer=self.grid.tech_info.get_layer_name(min(self.p_electrode_layer_ind_list)),
            label=self.label_p,
        )

        # Draw p silicon spokes and via stacks.  Via stack goes to the bottom-most electrode layer
        self.draw_contact_spokes_and_via_stack(
            r_via=self.n_via_radius,
            spoke_num=self.spoke_num,
            offset=self.n_contact_offset,
            bot_layer=self.bottom_metal_electrode_layer,
            top_layer=self.grid.tech_info.get_layer_name(min(self.n_electrode_layer_ind_list)),
            label=self.label_n,
        )

        # p+ region around the p spokes for low resistance
        spoke_info_p = dict(
            rout=self.high_doping_rout,
            rin=self.high_doping_rin,
            num=self.spoke_num,
            spoke_width_percentage=1,
            spoke_offset=self.p_contact_offset,
            layer=self.high_p_doping_layer,
        )
        spoke_master_p = self.new_template(params=spoke_info_p, temp_cls=SpokeBase)
        self.add_instance(
            master=spoke_master_p,
            inst_name='high_p_doping',
            loc=self.ring_loc,
            orient="R0",
            unit_mode=False,
        )

        # n+ region around the n spokes for low resistance
        spoke_info_n = dict(
            rout=self.high_doping_rout,
            rin=self.high_doping_rin + self.high_doping_n_rin_offset,
            num=self.spoke_num,
            spoke_width_percentage=1,
            spoke_offset=self.n_contact_offset,
            layer=self.high_n_doping_layer,
        )
        spoke_master_n = self.new_template(params=spoke_info_n, temp_cls=SpokeBase)
        self.add_instance(
            master=spoke_master_n,
            inst_name='high_n_doping',
            loc=self.ring_loc,
            orient="R0",
            unit_mode=False,
        )

        # p contact rings. Spokes to the contact via stacks are only on the bottom most layer
        self.draw_electrode_ring_and_spokes(
            ring_layer_indices=self.p_electrode_layer_ind_list,
            spoke_layer_indices=min(self.p_electrode_layer_ind_list),
            electrode_rout=electrode_rout_p,
            electrode_rin=electrode_rin_p,
            via_radius=self.p_via_radius,
            spoke_num=self.spoke_num,
            offset=self.p_contact_offset,
        )

        # Changed by Djordje to enable second ring with spokes to make my design work
        # n contact rings. Spokes to the contact via stacks are only on the bottom most layer
        self.draw_electrode_ring_and_spokes(
            ring_layer_indices=self.n_electrode_layer_ind_list,
            spoke_layer_indices=sorted(self.n_electrode_layer_ind_list)[0:2],
            electrode_rout=electrode_rout_n,
            electrode_rin=electrode_rin_n,
            via_radius=self.n_via_radius,
            spoke_num=self.spoke_num,
            offset=self.n_contact_offset,
        )

        # p contact label
        bbox = BBox(
            top=electrode_rout_p - electrode_width_p / 4,
            bottom=electrode_rin_p + electrode_width_p / 4,
            left=-(electrode_width_p / 2),
            right=(electrode_width_p / 2),
            resolution=self.grid.resolution
        )
        contact_label_layer = self.grid.tech_info.get_layer_name(max(self.p_electrode_layer_ind_list))
        self.add_label(label=self.label_p, layer=(contact_label_layer, "label"), bbox=bbox)

        # n contact label
        bbox = BBox(
            top=electrode_rout_n - electrode_width_n / 4,
            bottom=electrode_rin_n + electrode_width_n / 4,
            left=-(electrode_width_n / 2),
            right=(electrode_width_n / 2),
            resolution=self.grid.resolution
        )
        contact_label_layer = self.grid.tech_info.get_layer_name(max(self.n_electrode_layer_ind_list))
        self.add_label(label=self.label_n, layer=(contact_label_layer, "label"), bbox=bbox)

        # Draw the access waveguide
        Amp = self.rout + self.coupling_slot + self.wg_width
        CosAmp = Amp / 2

        self.access_length = 2 * np.pi * np.sqrt(Amp * CosAmp)
        self.draw_access_waveguide(
            cosine_amplitude=0.5 * self.rout,
            cosine_length=self.access_length,
            wg_width=self.wg_width,
            layer=self.layer
        )

        if self.drop_slot and self.drop_slot > 0:
            self.draw_drop_waveguide(taper_length=self.drop_taper_length,
                                     wg_width=self.wg_width,
                                     layer=self.layer
                                     )

        # Added by Djordje
        self.create_sldphot_ring()
        if self.draw_pads:
            self.place_gs_electrodes()
        #if self.draw_gsbox:
            #self.place_gs_boxesonly()
        self.place_gratings()

    def create_silicon_ring(self):
        """Draw the silicon ring"""
        ring = PhotonicRound(
            layer=self.layer,
            resolution=self.grid.resolution,
            rout=self.rout,
            center=self.ring_loc,
            rin=self.rin,
            unit_mode=False
        )
        self.add_obj(ring)

    # Added by Djordje ['sldphot', 'drawing'] has to cover silicide layer to enable proper functionality of device
    def create_sldphot_ring(self):
        """Draw the silicon ring"""
        ring = PhotonicRound(
            layer=['sldphot', 'drawing'],
            resolution=self.grid.resolution,
            rout=3.7,
            center=self.ring_loc,
            rin=1.5,
            unit_mode=False
        )
        self.add_obj(ring)

    def draw_doping_spokes(self):
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

    def draw_extra_rings(self):
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

    def draw_contact_spokes_and_via_stack(self,
                                          r_via: float,
                                          spoke_num: int,
                                          offset: float,
                                          bot_layer: "layer_or_lpp_type",
                                          top_layer: "layer_or_lpp_type",
                                          label: Optional[str] = None,
                                          ):
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

        for i in range(spoke_num):
            theta = i * delta_theta + offset_theta
            via_loc = (np.cos(theta) * r_via + self.ring_loc[0], np.sin(theta) * r_via + self.ring_loc[1])
            self.add_via_stack(
                bot_layer=bot_layer,
                top_layer=top_layer,
                loc=via_loc
            )

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
            np.pi * self.rin / spoke_num) + 0.05

        # Initialize and place the spokes
        spoke_info = dict(
            rout=self.rin,
            rin=r_via,
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
            spoke_width_percentage = 2 * self.photonic_tech_info.min_width(
                self.grid.tech_info.get_layer_name(layer_ind)
            ) / (np.pi * via_radius / spoke_num)

            # Initialize and place the spokes
            spoke_info = dict(
                rout=via_radius + 0.1 if via_radius > electrode_rout + 0.1 else electrode_rin,
                rin=via_radius if via_radius < electrode_rin else electrode_rout,
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

    def draw_access_waveguide(self,
                              cosine_amplitude: float,
                              cosine_length: float,
                              wg_width: float,
                              layer: "layer_or_lpp_type",
                              ) -> None:
        """
        Draws the acccess waveguide. Assumed Cosine waveguide shape. Extracts the ports to this hierarchy.

        """
        params = dict(
            width=wg_width,
            amplitude=cosine_amplitude,
            wavelength=cosine_length,
            layer=layer,
            start_quarter_angle=0,
            end_quarter_angle=4
        )

        wg_master = self.new_template(params=params, temp_cls=CosineWaveguide)
        access_wg = self.add_instance(
            master=wg_master,
            inst_name='access_waveguide',
            loc=(-cosine_length / 2.0, -0.5 * self.rout - self.coupling_slot - wg_width / 2)
        )

        # Extract the ports
        self.extract_photonic_ports(
            inst=access_wg,
        )

    def draw_drop_waveguide(self,
                            taper_length: float,
                            wg_width: float,
                            layer: "layer_or_lpp_type",
                            ) -> None:
        """
        Draw the drop port waveguide and tapers. The tapers are drawn to a point. Assumes that dataprep will clean to
        avoid min width DRC.

        Parameters
        ----------
        taper_length : float
            The length of the taper
        wg_width : float
            The width at the start of the taper
        layer : Union[str, Tuple[str, str]]
            The layer on which to draw the taper

        """

        drop_y = self.rout + self.drop_slot + wg_width / 2

        points = [(-taper_length / 2, drop_y),
                  (-self.rout, drop_y + wg_width / 2),
                  (self.rout, drop_y + wg_width / 2),
                  (taper_length / 2, drop_y),
                  (self.rout, drop_y - wg_width / 2),
                  (-self.rout, drop_y - wg_width / 2),
                  ]

        polygon = PhotonicPolygon(
            resolution=self.grid.resolution,
            layer=layer,
            points=points,
            unit_mode=False
        )
        self.add_obj(polygon)

    def place_gs_boxesonly(self):
        """
        Draws GS electrodes which are connected to ring electrodes
        """
        # Create GS pad
        pad_size = 2
        pad_offset = 1

        self.n_electrode_layer_ind_list = self.inner_electrode_ring_layer_inds
        electrode_rin_n = self.n_via_radius - self.electrode_offset - self.electrode_width_outer

        box = BBox(left=electrode_rin_n - pad_size, bottom=-self.rout / 4, right=electrode_rin_n,
                   top=self.rout / 4, resolution=self.grid.resolution, unit_mode=False)

        Rect_inner = PhotonicRect(layer=['B1', 'drawing'], bbox=box)
        self.add_obj(Rect_inner)

        box1 = BBox(left=electrode_rin_n * np.sqrt(2) / 1.75 - 0.4, bottom=-self.rout / 4,
                    right=electrode_rin_n * np.sqrt(2) / 1.75,
                    top=self.rout / 4 + 0.5, resolution=self.grid.resolution, unit_mode=False)

        Rect_inner1 = PhotonicRect(layer=['B1', 'drawing'], bbox=box1)
        self.add_obj(Rect_inner1)

        box2 = BBox(left=electrode_rin_n * np.sqrt(2) / 1.75 - 0.4, bottom=-self.rout / 4 - 0.5,
                    right=electrode_rin_n * np.sqrt(2) / 1.75,
                    top=-self.rout / 4, resolution=self.grid.resolution, unit_mode=False)

        Rect_inner2 = PhotonicRect(layer=['B1', 'drawing'], bbox=box2)
        self.add_obj(Rect_inner2)

        electrode_rin_p = self.p_via_radius + self.electrode_offset
        box3 = BBox(left=electrode_rin_p, bottom=-self.rout / 4, right=electrode_rin_p + pad_size,
                    top=self.rout / 4, resolution=self.grid.resolution, unit_mode=False)

        Rect_outer = PhotonicRect(layer=['B1', 'drawing'], bbox=box3)
        self.add_obj(Rect_outer)

    def place_gs_electrodes(self):
        """
        Draws GS electrodes which are connected to ring electrodes
        """
        # Create GS pad
        pad_size = 2
        pad_offset = 1

        self.n_electrode_layer_ind_list = self.inner_electrode_ring_layer_inds
        electrode_rin_n = self.n_via_radius - self.electrode_offset - self.electrode_width_outer

        box = BBox(left=electrode_rin_n - pad_size, bottom=-self.rout / 4, right=electrode_rin_n,
                   top=self.rout / 4, resolution=self.grid.resolution, unit_mode=False)

        Rect_inner = PhotonicRect(layer=['B1', 'drawing'], bbox=box)
        self.add_obj(Rect_inner)

        box1 = BBox(left=electrode_rin_n * np.sqrt(2) / 1.75 - 0.4, bottom=-self.rout / 4,
                    right=electrode_rin_n * np.sqrt(2) / 1.75,
                    top=self.rout / 4 + 0.5, resolution=self.grid.resolution, unit_mode=False)

        Rect_inner1 = PhotonicRect(layer=['B1', 'drawing'], bbox=box1)
        self.add_obj(Rect_inner1)

        box2 = BBox(left=electrode_rin_n * np.sqrt(2) / 1.75 - 0.4, bottom=-self.rout / 4 - 0.5,
                    right=electrode_rin_n * np.sqrt(2) / 1.75,
                    top=-self.rout / 4, resolution=self.grid.resolution, unit_mode=False)

        Rect_inner2 = PhotonicRect(layer=['B1', 'drawing'], bbox=box2)
        self.add_obj(Rect_inner2)

        electrode_rin_p = self.p_via_radius + self.electrode_offset
        box3 = BBox(left=electrode_rin_p, bottom=-self.rout / 4, right=electrode_rin_p + pad_size,
                    top=self.rout / 4, resolution=self.grid.resolution, unit_mode=False)

        Rect_outer = PhotonicRect(layer=['B1', 'drawing'], bbox=box3)
        self.add_obj(Rect_outer)

        gs_electrode_master = self.new_template(params=dict(top_layer=self.gs_electrod_params['gs_pad_layer'],

                                                            bottom_layer=('B1', 'drawing'),

                                                            top_x_span=self.gs_electrod_params['gs_pad_length'],
                                                            top_y_span=self.gs_electrod_params['gs_pad_width'],

                                                            bottom_x_span=self.rout / 2,
                                                            bottom_y_span=pad_size - 0.5,
                                                            align='corner_align',
                                                            top_bot_offset=0.0,
                                                            pad_open_layer=self.gs_electrod_params['gs_pad_open_layer'],
                                                            pad_open_inclusion=self.gs_electrod_params[
                                                                'gs_pad_open_inclusion']),
                                                temp_cls=ViaStack)

        # Place ground electrode
        self.add_instance(master=gs_electrode_master,
                          inst_name='G_electrode',
                          loc=(electrode_rin_n - pad_size / 2, -self.rout / 4),
                          orient='MXR90')

        # Place signal electrode
        self.add_instance(master=gs_electrode_master,
                          inst_name='S_electrode',
                          loc=(electrode_rin_p + pad_offset + pad_size / 2 - 0.5, -self.rout / 4),
                          orient='R90')

    def place_gratings(self):
        if self.add_grating_left and self.add_grating_right:
            pad = (self.grating_distance - self.access_length) / 2
            adiabatic_band_params = dict(layer=self.layer, port_layer=['RX', 'port'], radius_threshold=1.5,
                                         curvature_rate_threshold=0.7, merge_arcs=False)
            if self.grating_band_radius == 0:
                adiabatic_band_params['arc_params'] = [
                    dict(arc_type="straight_wg", width=self.wg_width, length=pad)]
                temp_wg = self.new_template(params=adiabatic_band_params, temp_cls=AdiabaticPaths)
                right_wg_inst = self.add_instance_port_to_port(inst_master=temp_wg,
                                                               instance_port_name='PORT_IN',
                                                               self_port_name='PORT1')

                left_wg_inst = self.add_instance_port_to_port(inst_master=temp_wg,
                                                              instance_port_name='PORT_IN',
                                                              self_port_name='PORT0')
                temp = self.new_template(params=None, temp_cls=GcUnidirWl1300nmMfd5000nmApodDown_fromAL11A)
                right_inst = self.add_instance_port_to_port(inst_master=temp,
                                                            instance_port_name='PORT_OUT',
                                                            self_port=right_wg_inst['PORT_OUT'])
                left_inst = self.add_instance_port_to_port(inst_master=temp,
                                                           instance_port_name='PORT_OUT',
                                                           self_port=left_wg_inst['PORT_OUT'])
            else:
                adiabatic_band_params['arc_params'] = [
                    dict(arc_type="straight_wg", width=self.wg_width,
                         length=pad - self.grating_band_radius * 1.8700958466)]
                temp_wg = self.new_template(params=adiabatic_band_params, temp_cls=AdiabaticPaths)
                right_wg_inst = self.add_instance_port_to_port(inst_master=temp_wg,
                                                               instance_port_name='PORT_IN',
                                                               self_port_name='PORT1')

                left_wg_inst = self.add_instance_port_to_port(inst_master=temp_wg,
                                                              instance_port_name='PORT_IN',
                                                              self_port_name='PORT0')
                bend90_params = deepcopy(adiabatic_band_params)
                bend90_params['arc_params'] = [
                    dict(arc_type="90_bend", rmin=self.grating_band_radius, turn_left=False, width=[self.wg_width, 0.5])]

                temp_90_right = self.new_template(params=bend90_params, temp_cls=AdiabaticPaths)
                inst_90_right = self.add_instance_port_to_port(inst_master=temp_90_right,
                                                               instance_port_name='PORT_IN',
                                                               self_port=right_wg_inst['PORT_OUT'],
                                                               reflect=self.reflect)

                bend90_params_left = deepcopy(bend90_params)
                bend90_params_left['arc_params'][0]['turn_left'] = True
                temp_90_left = self.new_template(params=bend90_params_left, temp_cls=AdiabaticPaths)
                inst_90_left = self.add_instance_port_to_port(inst_master=temp_90_left,
                                                              instance_port_name='PORT_IN',
                                                              self_port=left_wg_inst['PORT_OUT'],
                                                              reflect=self.reflect)

                temp = self.new_template(params=None, temp_cls=GcUnidirWl1300nmMfd5000nmApodDown_fromAL11A)
                right_inst = self.add_instance_port_to_port(inst_master=temp,
                                                            instance_port_name='PORT_OUT',
                                                            self_port=inst_90_right['PORT_OUT'])
                left_inst = self.add_instance_port_to_port(inst_master=temp,
                                                           instance_port_name='PORT_OUT',
                                                           self_port=inst_90_left['PORT_OUT'])

# if __name__ == '__main__':
#     spec_file = '/projectnb/siphot/djordje/TO_45RF_2019May/Photonic_Core_Layout_Djordje/Ring/specs/ring_specs.yaml'
#     plm = BPG.PhotonicLayoutManager(spec_file)
#     plm.generate_content()
#     plm.generate_gds()
#     plm.dataprep_calibre()
#     plm.generate_flat_content()
#     plm.generate_flat_gds()
