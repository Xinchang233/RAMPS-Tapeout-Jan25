import BPG
import importlib
from ...triple_rings_full_si.Ring.ring_2020_gsbox_heater_ports import RingBase
from ...triple_rings_full_si.Ring_new.Test_Adiabatic_router_heater import adiabatic_ring
from ...triple_rings_full_si.AdiabaticPaths.AdiabaticPaths import AdiabaticPaths

# from layout.Importers.Gratings.unidirectional.GcUnidirWl1300nmMfd9200nmApodDownJtaper import GcUnidirWl1300nmMfd9200nmApodDownJtaper
from ...triple_rings_full_si.Importers.Gratings.Manuj.bidirectional.uni_grating import GcBidirWl1300nmMfd9200nmCurved
from bag.layout.util import BBox
from BPG.objects import PhotonicPolygon, PhotonicRound, PhotonicRect
from ...triple_rings_full_si.AdiabaticRouter.AdiabaticRouter import AdiabaticRouter
from ...triple_rings_full_si.RectalinearRouter.RectalinearRouter import RectalinearRouter
from ...triple_rings_full_si.ProbePads.ProbePads import ProbePads

import numpy as np

from copy import deepcopy


class DualRing(BPG.PhotonicTemplateBase):
    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)
        self.params = deepcopy(params)
        self.spoked_peanut_gap = params['spoked_peanut_gap']

        self.spoked_list_params = params['spoked_list_params']
        self.ring_bus_gap = params['ring_bus_gap']
        self.ring_bus_gap_drop = params['ring_bus_gap_drop']

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
        position_ring1 = (0, 0)
        ring_bus_gap = self.ring_bus_gap  # 0.500
        ring_bus_gap_drop = self.ring_bus_gap_drop
        spoked_peanut_gap = self.spoked_peanut_gap  # 0.300
        peanut_width = 0.4

        template_rings = []
        master_rings = []
        # ring_acces_wds = []

        # ring top
        print(ring_bus_gap)
        ringpa = deepcopy(self.spoked_list_params[0])
        ringpa['coupling_slot'] = ring_bus_gap
        ringpa['use_adiabatic_access_wg'] = True
        template_rings.append(self.new_template(params=ringpa, temp_cls=RingBase))

        # rign bottom

        ringpa = deepcopy(self.spoked_list_params[0])
        ringpa['coupling_slot'] = ring_bus_gap_drop
        ringpa['use_adiabatic_access_wg'] = True
        template_rings.append(self.new_template(params=ringpa, temp_cls=RingBase))

        # ring_acces_wds.append(template_rings[irng].access_length)

        master_rings.append(self.add_instance(template_rings[0], orient='R180', loc=position_ring1))  # coupler on top

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
        # Grating temp
        grating_temp = self.new_template(params=None, temp_cls=GcBidirWl1300nmMfd9200nmCurved)
        top_pad_params = dict(
            probe_pitch=90.000,
            pad_to_pad_spacing=26.000,
            num_pads=6,  # minimum = 1
            pad_labels=['probe_pad_left', 'probe_pad_right', 'probe_pad_more_right', 'probe_pad_even_more_right',
                        'you_see_where_this_is_going', 'last_one'],
            pad_metal_layer=('LB', 'drawing'),
            pad_opening_layer=('LV', 'drawing'),
            draw_pad_opening=True
        )
        pad_size = top_pad_params['probe_pitch'] - top_pad_params['pad_to_pad_spacing']
        top_pad_temp = self.new_template(params=top_pad_params, temp_cls=ProbePads)

        bottom_pad_params = dict(
            probe_pitch=90.000,
            pad_to_pad_spacing=26.000,
            num_pads=3,  # minimum = 1
            pad_labels=['probe_pad_left1', 'probe_pad_right1', 'probe_pad_more_right1'],
            pad_metal_layer=('LB', 'drawing'),
            pad_opening_layer=('LV', 'drawing'),
            draw_pad_opening=True
        )
        bottom_pad_temp = self.new_template(params=bottom_pad_params, temp_cls=ProbePads)

        temp_peanut = self.new_template(params=middle_ring_params, temp_cls=adiabatic_ring)
        master_peanut = self.add_instance(temp_peanut, orient='R0', loc=(0, 0))

        ring1_bot_port = master_rings[0].get_photonic_port('PORT_RING_TOP')
        peanut_top_port = master_peanut.get_photonic_port('PORT_CENTER1')
        peanut_bot_port = master_peanut.get_photonic_port('PORT_CENTER2')
        # ring2_top_port = master_rings[1].get_photonic_port('PORT_RING_TOP')

        trans_vec_peanut = ring1_bot_port.center - peanut_top_port.center - np.array(
            [0, peanut_width / 2 + spoked_peanut_gap])
        master_peanut.move_by(dx=trans_vec_peanut[0], dy=trans_vec_peanut[1], unit_mode=False)
        print("Peanut y transform is {}".format(trans_vec_peanut[1]))
        # master_peanut.move_by(dx=trans_vec_peanut[0], dy=trans_vec_peanut[1], unit_mode=True)

        # master_peanut = self.add_instance(temp_peanut, orient='R0', loc=(0,0))

        # master_rings.append(self.add_instance(template_rings[1], orient='R0', loc=(position_ring1[0], position_ring1[1] - y_shift_ring2)))

        # temp_peanut = self.new_template(params=ringpa, temp_cls=adiabatic_ring)



        span_y_peanut = peanut_top_port.center[1] - peanut_bot_port.center[1]

        y_shift_ring2 = span_y_peanut + spoked_peanut_gap * 2 + peanut_width
        # master_rings.append(self.add_instance(template_rings[1], orient='R0', loc=(position_ring1[0], position_ring1[1] - y_shift_ring2)))

        master_rings.append(self.add_instance(template_rings[1], orient='R0', loc=(0, 0)))
        ring2_top_port = master_rings[1].get_photonic_port('PORT_RING_TOP')

        trans_vec_ring2 = ring1_bot_port.center - ring2_top_port.center - np.array([0, y_shift_ring2])
        master_rings[1].move_by(dx=trans_vec_ring2[0], dy=trans_vec_ring2[1], unit_mode=False)

        print("ring 2 y trans = {}".format(trans_vec_ring2[1]))

        self.extract_photonic_ports(inst=master_rings[0], port_names=['PORT0', 'PORT1'],
                                    port_renaming={'PORT0': 'PORT_DROP', 'PORT1': 'PORT_RED'})

        self.extract_photonic_ports(inst=master_rings[1], port_names=['PORT0', 'PORT1'],
                                    port_renaming={'PORT0': 'PORT_IN', 'PORT1': 'PORT_THROUGH'})

        ############################################ Route gratings ###################################################

        router_in = AdiabaticRouter(gen_cls=self, init_port=self._photonic_ports['PORT_IN'],
                                    layer=self.spoked_list_params[0]['layer'], name='init_port')
        router_in.add_straight_wg(length=60)
        router_in.add_bend_180(rmin=10, turn_left=True)

        router_in.add_straight_wg(length=10, width=grating_temp._photonic_ports['PORT_OUT'].width)
        router_in.add_offset_bend(rmin=10, offset=70)
        router_in.add_straight_wg(length=400)
        self.add_instance_port_to_port(inst_master=grating_temp, self_port=router_in.port,
                                       instance_port_name='PORT_OUT')

        # router_through = AdiabaticRouter(gen_cls=self, init_port=self._photonic_ports['PORT_THROUGH'],
        #                                  layer=self.spoked_list_params[0]['layer'], name='init_port2')
        # router_through.add_straight_wg(length=50)
        # router_through.add_offset_bend(offset=-100, rmin=10)
        # router_through.add_straight_wg(length=297, width=grating_temp._photonic_ports['PORT_OUT'].width)
        # self.add_instance_port_to_port(inst_master=grating_temp, self_port=router_through.port,
        #                                instance_port_name='PORT_OUT')

        offset_bend = 85
        router_drop = AdiabaticRouter(gen_cls=self, init_port=self._photonic_ports['PORT_DROP'],
                                      layer=self.spoked_list_params[0]['layer'], name='init_port3')
        router_drop.add_straight_wg(length=10)
        router_drop.add_offset_bend(offset=-offset_bend, rmin=10)
        router_drop.add_straight_wg(length=307, width=grating_temp._photonic_ports['PORT_OUT'].width)
        self.add_instance_port_to_port(inst_master=grating_temp, self_port=router_drop.port,
                                       instance_port_name='PORT_OUT')

        router_red = AdiabaticRouter(gen_cls=self, init_port=self._photonic_ports['PORT_RED'],
                                     layer=self.spoked_list_params[0]['layer'], name='init_port3')
        router_red.add_straight_wg(length=10)
        router_red.add_offset_bend(offset=offset_bend, rmin=10)
        router_red.add_straight_wg(length=290, width=grating_temp._photonic_ports['PORT_OUT'].width)
        self.add_instance_port_to_port(inst_master=grating_temp, self_port=router_red.port,
                                       instance_port_name='PORT_OUT')

        ########################################## WIRE ROUTING ##################################

        # Add pads
        self.add_instance(master=top_pad_temp, loc=(0, -40 - pad_size / 2))
        self.add_instance(master=bottom_pad_temp, loc=(0, 10 + pad_size / 2))

        # Route lower ring heater
        cord = (1.9, trans_vec_ring2[1])
        init_port = self.add_photonic_port(name='pin_port_{}'.format(cord), center=cord,
                                           orient='R180', width=2.8,
                                           layer=('RX', 'port'))
        bottom_ring_heater_right = RectalinearRouter(gen_cls=self, init_port=init_port,
                                                     layer=('B3', 'drawing'), name='init_port3')
        bottom_ring_heater_right.route(direction='S', length=35.5)
        bottom_ring_heater_right.route(direction='R', length=55 - 2.8)
        bottom_ring_heater_right.go_to_layer(layer=('LB', 'drawing'), width=10)

        cord = (-1.9, trans_vec_ring2[1])
        init_port = self.add_photonic_port(name='pin_port_{}'.format(cord), center=cord,
                                           orient='R0', width=2.8,
                                           layer=('RX', 'port'))
        bottom_ring_heater_left = RectalinearRouter(gen_cls=self, init_port=init_port,
                                                    layer=('B3', 'drawing'), name='init_port3')
        bottom_ring_heater_left.route(direction='S', length=35.5 - 2.8)
        bottom_ring_heater_left.route(direction='L', length=55)
        bottom_ring_heater_left.go_to_layer(layer=('LB', 'drawing'), width=10)

        # Route peanut heater
        ref_cord = master_peanut.get_photonic_port('PORT_180RIGHT_BOT')
        cord = (24, -middle_ring_params['wg180_radius'] * 2.753663435620129 / 2 + ref_cord.center[1] + 2.5)
        init_port = self.add_photonic_port(name='pin_port_{}'.format(cord), center=cord,
                                           orient='R0', width=2.8,
                                           layer=('RX', 'port'))
        middle_ring_heater_conn = RectalinearRouter(gen_cls=self, init_port=init_port,
                                                    layer=('B3', 'drawing'), name='init_port3')
        middle_ring_heater_conn.route(direction='S', length=50)

        # Route left
        cord = (17, -middle_ring_params['wg180_radius'] * 2.753663435620129 / 2 + ref_cord.center[1] - 2.5)
        init_port = self.add_photonic_port(name='pin_port_{}'.format(cord), center=cord,
                                           orient='R180', width=2.8,
                                           layer=('RX', 'port'))
        middle_ring_heater_left = RectalinearRouter(gen_cls=self, init_port=init_port,
                                                    layer=('B3', 'drawing'), name='init_port3')
        middle_ring_heater_left.route(direction='S', length=120)
        middle_ring_heater_left.route(direction='R', length=72)
        middle_ring_heater_left.go_to_layer(layer=('LB', 'drawing'), width=10)

        # Route right
        cord = (-17, -middle_ring_params['wg180_radius'] * 2.753663435620129 / 2 + +  ref_cord.center[1] - 2.5)

        init_port = self.add_photonic_port(name='pin_port_{}'.format(cord), center=cord,
                                           orient='R0', width=2.8,
                                           layer=('RX', 'port'))
        middle_ring_heater_right = RectalinearRouter(gen_cls=self, init_port=init_port,
                                                     layer=('B3', 'drawing'), name='init_port3')
        middle_ring_heater_right.route(direction='S', length=120)
        middle_ring_heater_right.route(direction='L', length=72)
        middle_ring_heater_right.go_to_layer(layer=('LB', 'drawing'), width=10)

        # Route upper ring heater
        cord = (1.9, 0)
        init_port = self.add_photonic_port(name='pin_port_{}'.format(cord), center=cord,
                                           orient='R180', width=2.8,
                                           layer=('RX', 'port'))
        top_ring_heater_right = RectalinearRouter(gen_cls=self, init_port=init_port,
                                                  layer=('B3', 'drawing'), name='init_port3')
        top_ring_heater_right.route(direction='S', length=150)
        top_ring_heater_right.route(direction='R', length=85)
        top_ring_heater_right.route(direction='L', length=70)
        top_ring_heater_right.route(direction='L', length=5)
        top_ring_heater_right.go_to_layer(layer=('LB', 'drawing'), width=10)

        cord = (-1.9, 0)
        init_port = self.add_photonic_port(name='pin_port_{}'.format(cord), center=cord,
                                           orient='R0', width=2.8,
                                           layer=('RX', 'port'))
        top_ring_heater_left = RectalinearRouter(gen_cls=self, init_port=init_port,
                                                 layer=('B3', 'drawing'), name='init_port3')
        top_ring_heater_left.route(direction='S', length=150)
        top_ring_heater_left.route(direction='L', length=85)
        top_ring_heater_left.route(direction='R', length=70)
        top_ring_heater_left.route(direction='L', length=5)
        top_ring_heater_left.go_to_layer(layer=('LB', 'drawing'), width=10)

        # Route Anodes
        # top anode
        cord = (4.1, 0)
        init_port = self.add_photonic_port(name='pin_port_{}'.format(cord), center=cord,
                                           orient='R180', width=2,
                                           layer=('RX', 'port'))
        top_anode = RectalinearRouter(gen_cls=self, init_port=init_port,
                                      layer=('B2', 'drawing'), name='init_port3')
        top_anode.route(direction='S', length=2)
        top_anode.route(direction='L', length=10)
        top_anode.route(direction='L', length=6)
        top_anode.route(direction='R', length=30)
        top_anode.go_to_layer(layer=('LB', 'drawing'), width=10)

        # bottom anode
        cord = (-5.1, trans_vec_ring2[1])
        init_port = self.add_photonic_port(name='pin_port_{}'.format(cord), center=cord,
                                           orient='R0', width=2,
                                           layer=('RX', 'port'))
        bottom_anode = RectalinearRouter(gen_cls=self, init_port=init_port,
                                         layer=('B2', 'drawing'), name='init_port3')
        bottom_anode.route(direction='S', length=6)
        bottom_anode.route(direction='R', length=50)
        bottom_anode.route(direction='R', length=11)

        ####### Route cathodes
        # Top cathode
        cord = (-6.1, 0)
        init_port = self.add_photonic_port(name='pin_port_{}'.format(cord), center=cord,
                                           orient='R0', width=2,
                                           layer=('RX', 'port'))
        top_cathode = RectalinearRouter(gen_cls=self, init_port=init_port,
                                        layer=('B1', 'drawing'), name='init_port3')
        top_cathode.route(direction='S', length=82)
        top_cathode.route(direction='R', length=52)
        top_cathode.go_to_layer(layer=('LB', 'drawing'), width=10)

        # bottom cathode
        cord = (6.1, trans_vec_ring2[1])
        init_port = self.add_photonic_port(name='pin_port_{}'.format(cord), center=cord,
                                           orient='R180', width=2,
                                           layer=('RX', 'port'))
        bottom_cathode = RectalinearRouter(gen_cls=self, init_port=init_port,
                                           layer=('B1', 'drawing'), name='init_port3')
        bottom_cathode.route(direction='S', length=82)
        bottom_cathode.route(direction='L', length=70)
        bottom_cathode.go_to_layer(layer=('LB', 'drawing'), width=10)


        #   bottom_anode.route(direction='L', length=50)
        # bottom_anode.go_to_layer(layer=('LB', 'drawing'), width=10)




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
    #spec_file = 'layout/DualRing/vars_manuj/mod5/dual_ring_mod5v1.yaml'
    #spec_file = 'layout/DualRing/vars_manuj/mod5/dual_ring_mod5v2.yaml'
    #spec_file = 'layout/DualRing/vars_manuj/mod5/dual_ring_mod5v3.yaml'
    #spec_file = 'layout/DualRing/vars_manuj/mod5/dual_ring_mod5v4.yaml'
    #spec_file = 'layout/DualRing/vars_manuj/mod5/dual_ring_mod5v5.yaml'
    #spec_file = 'layout/DualRing/vars_manuj/mod5/dual_ring_mod5v6.yaml'
    #spec_file = 'layout/DualRing/vars_manuj/mod10/dual_ring_mod10v1.yaml'
    #spec_file = 'layout/DualRing/vars_manuj/mod10/dual_ring_mod10v2.yaml'
    #spec_file = 'layout/DualRing/vars_manuj/mod10/dual_ring_mod10v3.yaml'
    #spec_file = 'layout/DualRing/vars_manuj/mod10/dual_ring_mod10v4.yaml'
    #spec_file = 'layout/DualRing/vars_manuj/mod10/dual_ring_mod10v5.yaml'
    #spec_file = 'layout/DualRing/vars_manuj/mod10/dual_ring_mod10v6.yaml'




    #spec_file = 'layout/DualRing/vars_manuj/mod20/dual_ring_mod20v1.yaml'
    #spec_file = 'layout/DualRing/vars_manuj/mod20/dual_ring_mod20v2.yaml'
    #spec_file = 'layout/DualRing/vars_manuj/mod20/dual_ring_mod20v3.yaml'
    #spec_file = 'layout/DualRing/vars_manuj/mod20/dual_ring_mod20v4.yaml'
    #spec_file = 'layout/DualRing/vars_manuj/mod20/dual_ring_mod20v5.yaml'
    #spec_file = 'layout/DualRing/vars_manuj/mod20/dual_ring_mod20v6.yaml'
    #spec_file = 'layout/DualRing/vars_manuj/mod40/dual_ring_mod40v1.yaml'
    #spec_file = 'layout/DualRing/vars_manuj/mod40/dual_ring_mod40v2.yaml'
    spec_file = 'triple_rings_full_si/DualRing/vars_manuj/mod40/dual_ring_mod40v3.yaml'
    #spec_file = 'layout/DualRing/vars_manuj/mod40/dual_ring_mod40v4.yaml'
    #spec_file = 'layout/DualRing/vars_manuj/mod40/dual_ring_mod40v5.yaml'
    #spec_file = 'layout/DualRing/vars_manuj/mod40/dual_ring_mod40v6.yaml'
    plm = BPG.PhotonicLayoutManager(spec_file)
    plm.generate_content()
    plm.generate_gds()
    plm.dataprep_calibre()
