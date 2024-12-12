import BPG
import importlib
from Photonic_Core_Layout_Djordje.Ring.ring_2020_gsbox_heater_ports import RingBase
from layout.Ring_new.Test_Adiabatic_router_heaterB1 import adiabatic_ring # peanut
from Photonic_Core_Layout_Djordje.AdiabaticPaths.AdiabaticPaths import AdiabaticPaths
from layout.LNAwiring.LNAwiring_wpeanut import LNAwiring


# from layout.Importers.Gratings.higheff1300lm5um.GcUnidirWl1300nmMfd5000nmApodDown_fromAL11A_nobend import GcUnidirWl1300nmMfd5000nmApodDown_fromAL11A_nobend
# layout/Importers/Gratings/unidirectional/GcUniWl1300nmMfd5000nm.py
from layout.Importers.Gratings.unidirectional.GcUniWl1300nmMfd5000nm import GcUniWl1300nmMfd5000nm
from bag.layout.util import BBox
from BPG.objects import PhotonicPolygon, PhotonicRound, PhotonicRect

import numpy as np


from copy import deepcopy

class DualRing(BPG.PhotonicTemplateBase):
    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)
        self.params = deepcopy(params)
        self.spoked_peanut_gap = params['spoked_peanut_gap']
        self.ring_bus_gap = params['ring_bus_gap']
        self.ring_bus_gap_drop = params['ring_bus_gap']
        self.spoked_list_params = params['spoked_list_params']

    @classmethod
    def get_default_param_values(cls) -> dict:
        return dict(
            spoked_peanut_gap=None,
            ring_bus_gap=None,
            ring_bus_gap_drop=None,
            spoked_list_params=None,

        )

    @classmethod
    def get_params_info(cls) -> dict:
        return dict(
            spoked_peanut_gap='None',
            ring_bus_gap='None',
            ring_bus_gap_drop='None',
            spoked_list_params='None',
        )

    def draw_layout(self) -> None:


        position_ring1 = (0, 50)
        ring_bus_gap = self.ring_bus_gap  # 0.500
        ring_bus_gap_drop = self.ring_bus_gap_drop  # 0.500
        spoked_peanut_gap = self.spoked_peanut_gap  # 0.300
        peanut_width = 0.4

        template_rings = []
        master_rings = []
        ring_acces_wds = []

        # ring top
        ringpa = deepcopy(self.spoked_list_params[0])
        ringpa['coupling_slot'] = ring_bus_gap
        ringpa['use_adiabatic_access_wg'] = True
        template_rings.append(self.new_template(params=ringpa, temp_cls=RingBase))
        # ring_acces_wds.append(template_rings[0].access_length)


        # rign bottom
        ringpa = deepcopy(self.spoked_list_params[0])
        ringpa['coupling_slot'] = ring_bus_gap_drop
        ringpa['use_adiabatic_access_wg'] = True
        template_rings.append(self.new_template(params=ringpa, temp_cls=RingBase))
        # ring_acces_wds.append(template_rings[1].access_length)


        # ring_acces_wds.append(template_rings[irng].access_length)

        master_rings.append(self.add_instance(template_rings[0], orient='R180', loc=position_ring1)) # coupler on top
        ring_acces_wds.append(abs(master_rings[0]['PORT0'].x - master_rings[0]['PORT1'].x))

        # ring_loc: (0, 0)  # 555nm 68-71 ghz
        # ring_loc_2: (0, 0)
        # heater_middle: 21  # contact to the ring
        # adiabaticplacer: -19.9452807482
        # w: 0.4
        # x: 17.81272164955083
        # y: 2.6665182149334257
        # gap: 0.555
        # wg180_radius: 5

        middle_ring_params = dict(
            layer='rxphot_noopc',
            layer1=('rxphot_noopc', 'drawing'),
            w=peanut_width,
            x=0,
            y=0,
            gap=0,
            wg180_radius=10,
        )


        temp_peanut = self.new_template(params=middle_ring_params, temp_cls=adiabatic_ring)
        master_peanut = self.add_instance(temp_peanut, orient='R0', loc=(0, 0))

        ring1_bot_port = master_rings[0].get_photonic_port('PORT_RING_TOP')
        peanut_top_port = master_peanut.get_photonic_port('PORT_CENTER1')
        peanut_bot_port = master_peanut.get_photonic_port('PORT_CENTER2')
        # ring2_top_port = master_rings[1].get_photonic_port('PORT_RING_TOP')

        trans_vec_peanut = ring1_bot_port.center - peanut_top_port.center - np.array([0, peanut_width/2 + spoked_peanut_gap] )
        master_peanut.move_by(dx=trans_vec_peanut[0], dy=trans_vec_peanut[1], unit_mode=False)


        span_y_peanut = peanut_top_port.center[1] - peanut_bot_port.center[1]

        y_shift_ring2 = span_y_peanut + spoked_peanut_gap*2 + peanut_width
        # master_rings.append(self.add_instance(template_rings[1], orient='R0', loc=(position_ring1[0], position_ring1[1] - y_shift_ring2)))

        master_rings.append(self.add_instance(template_rings[1], orient='R0', loc=(0,0)))
        ring2_top_port = master_rings[1].get_photonic_port('PORT_RING_TOP')

        trans_vec_ring2 = ring1_bot_port.center - ring2_top_port.center - np.array([0, y_shift_ring2])
        master_rings[1].move_by(dx=trans_vec_ring2[0], dy=trans_vec_ring2[1], unit_mode=False)

        r1_nport = master_rings[1].get_photonic_port(name='PORT_OUTER_PIN')
        r1_pport = master_rings[1].get_photonic_port(name='PORT_INNER_PIN')
        r2_nport = master_rings[0].get_photonic_port(name='PORT_OUTER_PIN')
        r2_pport = master_rings[0].get_photonic_port(name='PORT_INNER_PIN')

        # r1_nport = master_rings[1].get_photonic_port(name='PORT_OUTER_PIN')
        # r1_pport = master_rings[1].get_photonic_port(name='PORT_INNER_PIN')
        # r2_nport = master_rings[0].get_photonic_port(name='PORT_OUTER_PIN')
        # r2_pport = master_rings[0].get_photonic_port(name='PORT_INNER_PIN')

        pnhR1 = master_peanut.get_photonic_port(name='PORT_HT_R1')
        pnhR2 = master_peanut.get_photonic_port(name='PORT_HT_R2')
        pnhL1 = master_peanut.get_photonic_port(name='PORT_HT_L2')
        pnhL2 = master_peanut.get_photonic_port(name='PORT_HT_L1')

        wire_params = dict(
            n1_portcent=list(r1_nport.center),
            p1_portcent=list(r1_pport.center),
            n2_portcent=list(r2_nport.center),
            p2_portcent=list(r2_pport.center),
            pnhR1_portcent=list(pnhR1.center),
            pnhR2_portcent=list(pnhR2.center),
            pnhL1_portcent=list(pnhL1.center),
            pnhL2_portcent=list(pnhL2.center),
        )

        temp_wires = self.new_template(params=wire_params, temp_cls=LNAwiring)
        master_wires = self.add_instance(temp_wires, orient='R0', loc=(0, 0))

        self.extract_photonic_ports(
            inst=master_rings[0],
            port_names=['PORT0', 'PORT1'],
            port_renaming={'PORT0': 'RING0_P0',
                           'PORT1': 'RING0_P1'
                           },
            show=True)

        self.extract_photonic_ports(
            inst=master_rings[1],
            port_names=['PORT0', 'PORT1'],
            port_renaming={'PORT0': 'RING1_P0',
                           'PORT1': 'RING1_P1'
                           },
            show=True)

       ########################
        #########3
        #####

        dist_grat_grat = 127  # 127/2
        draw_grats1 = False
        draw_grats2 = False
        grating_bend_radius = 10
        # mod_y_loc = 25
        # mod_y_loc1 = 55

        # mod_y_diff = mod_y_loc1 - mod_y_loc
        # mod_y_diff = master_rings[0]['PORT0'].y - master_rings[1]['PORT0'].y
        # abs(master_rings[0].get_photonic_port('PORT_OUT').y - master_rings[1]].get_photonic_port('PORT_OUT').y)
        mod_y_diff = master_rings[0]['PORT0'].y - master_rings[1]['PORT0'].y

        wg_width = 0.4  # template_rings[0].wg_width
        wg_layer = ('rx3phot', 'drawing')  # template_rings[0].layer

        adiabatic_band_params = dict(layer=wg_layer, port_layer=['RX', 'port'], radius_threshold=1.5,
                                     curvature_rate_threshold=0.7, merge_arcs=False)
        adiabatic_band_params['arc_params'] = [dict(arc_type="straight_wg", width=wg_width, length=0)]

        dx_grat_lines = 8
        len_mod_to_grats_y = 310 - 20 + 38 + 25  # 450

        if draw_grats1:
            dist_grat_grat1 = dist_grat_grat * 3
            grat_wg_wd = 0.5
            bend_strlen = grating_bend_radius * 1.8700958466
            x_grat_max_right = 120

            mod1_gratlines_diff = dx_grat_lines * 3  # 40

            left_temps = []
            # left
            # 0
            pad_left_len = 50  # (dist_grat_grat / 2) - (ring_acces_wds[0] / 2) - bend_strlen  # dist_mod_grat_first - bend_strlen
            padwg_params_left = deepcopy(adiabatic_band_params)
            padwg_params_left['arc_params'][0]['length'] = pad_left_len
            padwg_params_left['arc_params'][0]['width'] = [wg_width, grat_wg_wd]
            left_temps.append(self.new_template(params=padwg_params_left, temp_cls=AdiabaticPaths))

            # #1
            # bend90_params_left = deepcopy(adiabatic_band_params)
            # bend90_params_left['arc_params'] = [ dict(arc_type="90_bend", rmin=grating_bend_radius, turn_left=False, width= [wg_width, grat_wg_wd])]
            # left_temps.append(self.new_template(params=bend90_params_left, temp_cls=AdiabaticPaths))

            # bend180_params_left = deepcopy(adiabatic_band_params)
            # # bend90_params_left['arc_params'] = [ dict(arc_type="90_bend", rmin=grating_bend_radius, turn_left=False, width=[wg_width, 0.5])]
            # bend180_params_left['arc_params'] = [
            #     # dict(arc_type="180_bend", rmin=grating_bend_radius, turn_left=False, width=[wg_width, grat_wg_wd])]
            #     # dict(arc_type="180_bend", rmin=grating_bend_radius, turn_left=False, width=[wg_width])]
            #     dict(arc_type="180_bend", size=100, turn_left=False, width=[grat_wg_wd])]
            # left_temps.append( self.new_template(params=bend180_params_left, temp_cls=AdiabaticPaths))
            # ubend_dist_left = abs(left_temps[-1].get_photonic_port('PORT_OUT').y - left_temps[-1].get_photonic_port('PORT_IN').y)

            bend180_params_left = deepcopy(adiabatic_band_params)
            # bend90_params_left['arc_params'] = [ dict(arc_type="90_bend", rmin=grating_bend_radius, turn_left=False, width=[wg_width, 0.5])]
            bend180_params_left['arc_params'] = [
                # dict(arc_type="180_bend", rmin=grating_bend_radius, turn_left=False, width=[wg_width, grat_wg_wd])]
                dict(arc_type="90bends_uturn", rmin=grating_bend_radius, turn_left=False, width=[grat_wg_wd], length=25)]
            # dict(arc_type="90bends_uturn", size=10, turn_left=False, width=[wg_width], length=35)]
            # dict(arc_type="180_bend", size=[100, 20, 100], turn_left=False, width=[grat_wg_wd])]
            left_temps.append(self.new_template(params=bend180_params_left, temp_cls=AdiabaticPaths))
            ubend_dist_left = abs(
                left_temps[-1].get_photonic_port('PORT_OUT').y - left_temps[-1].get_photonic_port('PORT_IN').y)

            # 1.2
            padx_left_len = pad_left_len + ring_acces_wds[0] + x_grat_max_right - mod1_gratlines_diff  # 80 #len_mod_to_grats_y
            padwgx_params_leftu = deepcopy(adiabatic_band_params)
            padwgx_params_leftu['arc_params'][0]['length'] = padx_left_len
            padwgx_params_leftu['arc_params'][0]['width'] = [grat_wg_wd]
            left_temps.append(self.new_template(params=padwgx_params_leftu, temp_cls=AdiabaticPaths))

            # 1.3
            bend90_params_left = deepcopy(adiabatic_band_params)
            bend90_params_left['arc_params'] = [
                dict(arc_type="90_bend", rmin=grating_bend_radius, turn_left=True, width=grat_wg_wd)]
            left_temps.append(self.new_template(params=bend90_params_left, temp_cls=AdiabaticPaths))

            # 2
            pady_left_len = len_mod_to_grats_y
            padwg_params_leftu = deepcopy(adiabatic_band_params)
            padwg_params_leftu['arc_params'][0]['length'] = pady_left_len
            padwg_params_leftu['arc_params'][0]['width'] = grat_wg_wd
            left_temps.append(self.new_template(params=padwg_params_leftu, temp_cls=AdiabaticPaths))

            # 3
            bend90_params_left2 = deepcopy(adiabatic_band_params)
            bend90_params_left2['arc_params'] = [
                dict(arc_type="90_bend", rmin=grating_bend_radius, turn_left=True, width=grat_wg_wd)]
            left_temps.append(self.new_template(params=bend90_params_left2, temp_cls=AdiabaticPaths))

            # # 1.2
            # padx_left_len2 = 10
            # padwgx_params_left2 = deepcopy(adiabatic_band_params)
            # padwgx_params_left2['arc_params'][0]['length'] = padx_left_len2
            # padwgx_params_left2['arc_params'][0]['width'] = [grat_wg_wd]
            # left_temps.append(self.new_template(params=padwgx_params_left2, temp_cls=AdiabaticPaths))

            m1_padxxx = 40
            # 1.2
            padxxxl = m1_padxxx - dx_grat_lines * 3
            padxxxl_par = deepcopy(adiabatic_band_params)
            padxxxl_par['arc_params'][0]['length'] = padxxxl
            padxxxl_par['arc_params'][0]['width'] = [grat_wg_wd]
            left_temps.append(self.new_template(params=padxxxl_par, temp_cls=AdiabaticPaths))

            right_temps = []
            # right
            # 0
            pad_right_len = x_grat_max_right  # 100 #(dist_grat_grat / 2) - (ring_acces_wds[0] / 2) - bend_strlen  # dist_mod_grat_first - bend_strlen
            padwg_params_right = deepcopy(adiabatic_band_params)
            padwg_params_right['arc_params'][0]['length'] = pad_right_len
            right_temps.append(self.new_template(params=padwg_params_right, temp_cls=AdiabaticPaths))

            # 1
            bend90_params_right = deepcopy(adiabatic_band_params)
            bend90_params_right['arc_params'] = [
                dict(arc_type="90_bend", rmin=grating_bend_radius, turn_left=True, width=[wg_width, grat_wg_wd])]
            right_temps.append(self.new_template(params=bend90_params_right, temp_cls=AdiabaticPaths))

            # 2
            pady_right_len = len_mod_to_grats_y + ubend_dist_left + dist_grat_grat1
            padwg_params_right = deepcopy(adiabatic_band_params)
            padwg_params_right['arc_params'][0]['length'] = pady_right_len
            padwg_params_right['arc_params'][0]['width'] = grat_wg_wd
            right_temps.append(self.new_template(params=padwg_params_right, temp_cls=AdiabaticPaths))

            # 3
            bend90_params_right2 = deepcopy(adiabatic_band_params)
            bend90_params_right2['arc_params'] = [
                dict(arc_type="90_bend", rmin=grating_bend_radius, turn_left=True, width=[grat_wg_wd])]
            right_temps.append(self.new_template(params=bend90_params_right2, temp_cls=AdiabaticPaths))

            # #4
            # pad_right_len2 = mod1_gratlines_diff + 10  # 100 #(dist_grat_grat / 2) - (ring_acces_wds[0] / 2) - bend_strlen  # dist_mod_grat_first - bend_strlen
            # padwg_params_right2 = deepcopy(adiabatic_band_params)
            # padwg_params_right2['arc_params'][0]['length'] = pad_right_len2
            # padwg_params_right2['arc_params'][0]['width'] = grat_wg_wd
            # right_temps.append(self.new_template(params=padwg_params_right2, temp_cls=AdiabaticPaths))

            # 1.2
            padxxxr = m1_padxxx  # - dx_grat_lines * 3
            padxxxr_par = deepcopy(adiabatic_band_params)
            padxxxr_par['arc_params'][0]['length'] = padxxxr
            padxxxr_par['arc_params'][0]['width'] = [grat_wg_wd]
            right_temps.append(self.new_template(params=padxxxr_par, temp_cls=AdiabaticPaths))

            leftinsts = []
            leftinsts.append(self.add_instance_port_to_port(inst_master=left_temps[0],
                                                            instance_port_name='PORT_IN',
                                                            self_port=master_rings[1]['PORT0']))
            # self_port=self.master_rings[0]['PORT0']))
            for ii in range(1, len(left_temps)):
                leftinsts.append(self.add_instance_port_to_port(inst_master=left_temps[ii],
                                                                instance_port_name='PORT_IN',
                                                                self_port=leftinsts[-1]['PORT_OUT']))

            # leftinsts.append(self.add_instance_port_to_port(inst_master=left_temps[2],
            #                                                 instance_port_name='PORT_IN',
            #                                                 self_port=leftinsts[-1]['PORT_OUT']))

            rightinsts = []
            rightinsts.append(self.add_instance_port_to_port(inst_master=right_temps[0],
                                                             instance_port_name='PORT_IN',
                                                             self_port=master_rings[1]['PORT1']))
            # self_port=self.master_rings[0]['PORT1']))
            for ii in range(1, len(right_temps)):
                rightinsts.append(self.add_instance_port_to_port(inst_master=right_temps[ii],
                                                                 instance_port_name='PORT_IN',
                                                                 self_port=rightinsts[-1]['PORT_OUT']))

            # rightinsts.append(self.add_instance_port_to_port(inst_master=right_temps[2],
            #                                                 instance_port_name='PORT_IN',
            #                                                 self_port=rightinsts[-1]['PORT_OUT']))


            temp_grat_left = self.new_template(params=None,
                                               temp_cls=GcUniWl1300nmMfd5000nm)  # GcUnidirWl1300nmMfd5000nmApodDown_fromAL11A)
            temp_grat_right = self.new_template(params=None,
                                                temp_cls=GcUniWl1300nmMfd5000nm)

            leftinsts.append(self.add_instance_port_to_port(inst_master=temp_grat_left,
                                                            instance_port_name='PORT_OUT',
                                                            self_port=leftinsts[-1]['PORT_OUT']))
            rightinsts.append(self.add_instance_port_to_port(inst_master=temp_grat_right,
                                                             instance_port_name='PORT_OUT',
                                                             self_port=rightinsts[-1]['PORT_OUT']))

        if draw_grats2:

            grat_wg_wd = 0.5
            bend_strlen = grating_bend_radius * 1.8700958466
            # len_mod_to_grats_y = 450
            m1x_grat_max_right = pad_right_len - dx_grat_lines  # + ring_acces_wds[0] #padx_left_len + ring_acces_wds[0] - dx_grat_lines # x_grat_max_right - dist_grat_grat #112
            m1_endturn_len = 160
            # dist_grat_grat2 = dist_grat_grat

            mod2_gratlines_diff = dx_grat_lines  # 6
            mod2_gratline_diffy = dist_grat_grat  # 60

            m1_pady1_len = pady_right_len - abs(mod_y_diff) - mod2_gratline_diffy  # - bend_strlen #dist_grat_grat*2#140

            m1left_temps = []
            # left
            # 0
            m1pad_left_len = 30  # (dist_grat_grat / 2) - (ring_acces_wds[0] / 2) - bend_strlen  # dist_mod_grat_first - bend_strlen
            m1padwg_params_left = deepcopy(adiabatic_band_params)
            m1padwg_params_left['arc_params'][0]['length'] = m1pad_left_len
            m1padwg_params_left['arc_params'][0]['width'] = [wg_width, grat_wg_wd]
            m1left_temps.append(self.new_template(params=m1padwg_params_left, temp_cls=AdiabaticPaths))

            # #1
            # m1bend90_params_left = deepcopy(adiabatic_band_params)
            # m1bend90_params_left['arc_params'] = [ dict(arc_type="90_bend", rmin=grating_bend_radius, turn_left=False, width= [wg_width, grat_wg_wd])]
            # m1left_temps.append(self.new_template(params=m1bend90_params_left, temp_cls=AdiabaticPaths))

            m1bend180_params_left = deepcopy(adiabatic_band_params)
            # m1bend90_params_left['arc_params'] = [ dict(arc_type="90_bend", rmin=grating_bend_radius, turn_left=False, width=[wg_width, 0.5])]
            m1bend180_params_left['arc_params'] = [
                # dict(arc_type="180_bend", rmin=grating_bend_radius, turn_left=False, width=[wg_width, grat_wg_wd])]
                dict(arc_type="180_bend", rmin=grating_bend_radius, turn_left=False, width=[grat_wg_wd])]
            # dict(arc_type="180_bend", size=60, turn_left=False, width=[grat_wg_wd])]
            m1left_temps.append(self.new_template(params=m1bend180_params_left, temp_cls=AdiabaticPaths))
            m1ubend_dist_left = abs(
                m1left_temps[-1].get_photonic_port('PORT_OUT').y - m1left_temps[-1].get_photonic_port('PORT_IN').y)

            # 1.2
            m1padx_left_len = m1pad_left_len + ring_acces_wds[
                0] + m1x_grat_max_right - mod2_gratlines_diff  # 80 #len_mod_to_grats_y
            m1padwgx_params_leftu = deepcopy(adiabatic_band_params)
            m1padwgx_params_leftu['arc_params'][0]['length'] = m1padx_left_len
            m1padwgx_params_leftu['arc_params'][0]['width'] = [grat_wg_wd]
            m1left_temps.append(self.new_template(params=m1padwgx_params_leftu, temp_cls=AdiabaticPaths))

            # 1.3
            m1bend90_params_left = deepcopy(adiabatic_band_params)
            m1bend90_params_left['arc_params'] = [
                dict(arc_type="90_bend", rmin=grating_bend_radius, turn_left=True, width=grat_wg_wd)]
            m1left_temps.append(self.new_template(params=m1bend90_params_left, temp_cls=AdiabaticPaths))

            # 2
            m1pady_left_len = m1_pady1_len - mod2_gratline_diffy - m1ubend_dist_left  # len_mod_to_grats_y + m1_pady1_len - mod2_gratline_diffy
            m1padwg_params_leftu = deepcopy(adiabatic_band_params)
            m1padwg_params_leftu['arc_params'][0]['length'] = m1pady_left_len
            m1padwg_params_leftu['arc_params'][0]['width'] = grat_wg_wd
            m1left_temps.append(self.new_template(params=m1padwg_params_leftu, temp_cls=AdiabaticPaths))

            # 3
            m1bend90_params_left2 = deepcopy(adiabatic_band_params)
            m1bend90_params_left2['arc_params'] = [
                dict(arc_type="90_bend", rmin=grating_bend_radius, turn_left=True, width=grat_wg_wd)]
            m1left_temps.append(self.new_template(params=m1bend90_params_left2, temp_cls=AdiabaticPaths))

            # 1.2
            m1padxxxl = m1_padxxx - dx_grat_lines * 2
            m1padxxxl_par = deepcopy(adiabatic_band_params)
            m1padxxxl_par['arc_params'][0]['length'] = m1padxxxl
            m1padxxxl_par['arc_params'][0]['width'] = [grat_wg_wd]
            m1left_temps.append(self.new_template(params=m1padxxxl_par, temp_cls=AdiabaticPaths))

            #             # 4
            #             m1padx_left_len2 = m1_endturn_len
            #             m1padwgx_params_left2 = deepcopy(adiabatic_band_params)

            ####
            m1right_temps = []
            # right
            # 0
            m1pad_right_len = m1x_grat_max_right  # 100 #(dist_grat_grat / 2) - (ring_acces_wds[0] / 2) - bend_strlen  # dist_mod_grat_first - bend_strlen
            m1padwg_params_right = deepcopy(adiabatic_band_params)
            m1padwg_params_right['arc_params'][0]['length'] = m1pad_right_len
            m1right_temps.append(self.new_template(params=m1padwg_params_right, temp_cls=AdiabaticPaths))

            # 1
            m1bend90_params_right = deepcopy(adiabatic_band_params)
            m1bend90_params_right['arc_params'] = [
                dict(arc_type="90_bend", rmin=grating_bend_radius, turn_left=True, width=[wg_width, grat_wg_wd])]
            m1right_temps.append(self.new_template(params=m1bend90_params_right, temp_cls=AdiabaticPaths))

            # 2
            m1pady_right_len = m1_pady1_len  # len_mod_to_grats_y + m1ubend_dist_left + m1_pady1_len #dist_grat_grat
            m1padwg_params_right = deepcopy(adiabatic_band_params)
            m1padwg_params_right['arc_params'][0]['length'] = m1pady_right_len
            m1padwg_params_right['arc_params'][0]['width'] = grat_wg_wd
            m1right_temps.append(self.new_template(params=m1padwg_params_right, temp_cls=AdiabaticPaths))

            # 3
            m1bend90_params_right2 = deepcopy(adiabatic_band_params)
            m1bend90_params_right2['arc_params'] = [
                dict(arc_type="90_bend", rmin=grating_bend_radius, turn_left=True, width=[grat_wg_wd])]
            m1right_temps.append(self.new_template(params=m1bend90_params_right2, temp_cls=AdiabaticPaths))

            # 1.2
            m1padxxxr = m1_padxxx - dx_grat_lines * 1
            m1padxxxr_par = deepcopy(adiabatic_band_params)
            m1padxxxr_par['arc_params'][0]['length'] = m1padxxxr
            m1padxxxr_par['arc_params'][0]['width'] = [grat_wg_wd]
            m1right_temps.append(self.new_template(params=m1padxxxr_par, temp_cls=AdiabaticPaths))

            # # 4

            #     m1right_temps[-1].get_photonic_port('PORT_OUT').y - m1left_temps[-1].get_photonic_port('PORT_IN').y)




            m1leftinsts = []
            m1leftinsts.append(self.add_instance_port_to_port(inst_master=m1left_temps[0],
                                                              instance_port_name='PORT_IN',
                                                              self_port=master_rings[0]['PORT1']))
            # self_port=self.master_rings[1]['PORT1']))

            for ii in range(1, len(m1left_temps)):
                m1leftinsts.append(self.add_instance_port_to_port(inst_master=m1left_temps[ii],
                                                                  instance_port_name='PORT_IN',
                                                                  self_port=m1leftinsts[-1]['PORT_OUT']))

            # m1leftinsts.append(self.add_instance_port_to_port(inst_master=m1left_temps[2],
            #                                                 instance_port_name='PORT_IN',
            #                                                 self_port=m1leftinsts[-1]['PORT_OUT']))

            m1rightinsts = []
            m1rightinsts.append(self.add_instance_port_to_port(inst_master=m1right_temps[0],
                                                               instance_port_name='PORT_IN',
                                                               self_port=master_rings[0]['PORT0']))
            # self_port=self.master_rings[1]['PORT0']))
            for ii in range(1, len(m1right_temps)):
                m1rightinsts.append(self.add_instance_port_to_port(inst_master=m1right_temps[ii],
                                                                   instance_port_name='PORT_IN',
                                                                   self_port=m1rightinsts[-1]['PORT_OUT']))

            # m1rightinsts.append(self.add_instance_port_to_port(inst_master=m1right_temps[2],
            #                                                 instance_port_name='PORT_IN',
            #                                                 self_port=m1rightinsts[-1]['PORT_OUT']))


            m1temp_grat_left = self.new_template(params=None,
                                                 temp_cls=GcUniWl1300nmMfd5000nm)  # GcUnidirWl1300nmMfd5000nmApodDown_fromAL11A)
            m1temp_grat_right = self.new_template(params=None,
                                                  temp_cls=GcUniWl1300nmMfd5000nm)

            m1leftinsts.append(self.add_instance_port_to_port(inst_master=m1temp_grat_left,
                                                              instance_port_name='PORT_OUT',
                                                              self_port=m1leftinsts[-1]['PORT_OUT']))
            m1rightinsts.append(self.add_instance_port_to_port(inst_master=m1temp_grat_right,
                                                               instance_port_name='PORT_OUT',
                                                               self_port=m1rightinsts[-1]['PORT_OUT']))
            # template_rings[0].place_gs_boxesonly()
            # band_params_metal = dict(layer=['RX', 'drawing'], port_layer=['RX', 'port'], radius_threshold=0.01,
            #                              curvature_rate_threshold=float('Inf'), merge_arcs=True)
            # N1_temps = []
            # pad_len_N1 = 20
            # pad_params_N1 = deepcopy(band_params_metal)
            # bend90_params_left['arc_params'] = [ dict(arc_type="90_bend", rmin=grating_bend_radius, turn_left=False, width= [wg_width, grat_wg_wd])]

            # pad_params_N1['arc_params'] = [dict(arc_type="90_bend", rmin=0.5, turn_left=True, width=10)]
            # # pad_params_N1['arc_params'][0]['length'] = pad_len_N1
            # # pad_params_N1['layer'] = ['B1', 'drawing']
            # # port_layer = ['RX', 'port']
            # N1_temps.append(self.new_template(params=pad_params_N1, temp_cls=AdiabaticPaths))
            #
            # N1insts = []
            # N1insts.append(self.add_instance_port_to_port(inst_master=N1_temps[0],
            #                                                  instance_port_name='PORT_IN',
            #                                                  self_port=master_rings[0]['PORT_OUTER_PIN']))




            # # place first ring
            # locsstart = (0,50)
            # y_shift_loc = -30 #[(0,50) , (0, 20)]
            # for ii in range(len(self.spoked_list_params)):
            #     print('weweewewew\n')
            #     master_rings.append(self.add_instance(template_rings[ii],orient='R0',loc= (locsstart[0], locsstart[1] + ii*y_shift_loc)))
            # wg_width = template_rings[0].wg_width
            # wg_layer = template_rings[0].layer
            #
            # adiabatic_band_params = dict(layer=wg_layer, port_layer=['RX', 'port'], radius_threshold=1.5, curvature_rate_threshold=0.7, merge_arcs=False)
            # adiabatic_band_params['arc_params'] = [dict(arc_type="straight_wg", width=wg_width, length=0)]


if __name__ == '__main__':
    spec_file = 'layout/DualRing/specs/dual_ring2_wireduniup.yaml'
    plm = BPG.PhotonicLayoutManager(spec_file)
    plm.generate_content()
    plm.generate_gds()
    plm.dataprep_calibre()