import BPG
import importlib
from Photonic_Core_Layout_Djordje.Ring.ring_2020_gsbox_heater_ports import RingBase
from layout.Ring_new.Test_Adiabatic_router_heaterB1 import adiabatic_ring # peanut
from Photonic_Core_Layout_Djordje.AdiabaticPaths.AdiabaticPaths import AdiabaticPaths
from layout.LNAwiring.LNAwiring_wpeanut import LNAwiring


from layout.Importers.Gratings.higheff1300lm5um.GcUnidirWl1300nmMfd5000nmApodDown_fromAL11A_nobend import GcUnidirWl1300nmMfd5000nmApodDown_fromAL11A_nobend
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
        # ring_acces_wds = []

        # ring top
        ringpa = deepcopy(self.spoked_list_params[0])
        ringpa['coupling_slot'] = ring_bus_gap
        ringpa['use_adiabatic_access_wg'] = True
        template_rings.append(self.new_template(params=ringpa, temp_cls=RingBase))

        # rign bottom
        ringpa = deepcopy(self.spoked_list_params[0])
        ringpa['coupling_slot'] = ring_bus_gap_drop
        ringpa['use_adiabatic_access_wg'] = True
        template_rings.append(self.new_template(params=ringpa, temp_cls=RingBase))


        #ring_acces_wds.append(template_rings[irng].access_length)

        master_rings.append(self.add_instance(template_rings[0], orient='R180', loc=position_ring1)) # coupler on top

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
            wg180_radius=5,
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

        # / projectnb / siphot / deniz / RFDec2020 / TO_45RF_2020June / layout / DualRing / DualRing_wired.py



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
    spec_file = 'layout/DualRing/specs/dual_ring_wired.yaml'
    plm = BPG.PhotonicLayoutManager(spec_file)
    plm.generate_content()
    plm.generate_gds()
    plm.dataprep_calibre()