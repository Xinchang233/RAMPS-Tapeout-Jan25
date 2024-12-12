import BPG
import importlib
from Photonic_Core_Layout_Djordje.Ring.ring_2020_gsbox_heater_ports import RingBase
from layout.Ring_new.Test_Adiabatic_router import adiabatic_ring # peanut
from Photonic_Core_Layout_Djordje.AdiabaticPaths.AdiabaticPaths import AdiabaticPaths


from layout.Importers.Gratings.higheff1300lm5um.GcUnidirWl1300nmMfd5000nmApodDown_fromAL11A_nobend import GcUnidirWl1300nmMfd5000nmApodDown_fromAL11A_nobend
from bag.layout.util import BBox
from BPG.objects import PhotonicPolygon, PhotonicRound, PhotonicRect

import numpy as np


from copy import deepcopy

class DualRing(BPG.PhotonicTemplateBase):
    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)
        self.params = deepcopy(params)
        self.grating_params = params['grating_params']
        self.spoked_list_params = params['spoked_list_params']

    @classmethod
    def get_default_param_values(cls) -> dict:
        return dict(
            grating_params=None,
            spoked_list_params=None,

        )

    @classmethod
    def get_params_info(cls) -> dict:
        return dict(
            grating_params='None',
            spoked_list_params='None',
        )

    def draw_layout(self) -> None:

        position_ring1 =  (0,50)
        ring_bus_gap = 0.500
        spoked_peanut_gap = 0.300
        peanut_width = 0.4


        template_rings = []
        master_rings = []
        # ring_acces_wds = []

        # ring top
        ringpa = deepcopy(self.spoked_list_params[0])
        ringpa['coupling_slot'] = ring_bus_gap
        template_rings.append(self.new_template(params=ringpa, temp_cls=RingBase))

        # rign bottom
        ringpa = deepcopy(self.spoked_list_params[0])
        ringpa['coupling_slot'] = ring_bus_gap
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
        # master_peanut.move_by(dx=trans_vec_peanut[0], dy=trans_vec_peanut[1], unit_mode=True)

        # master_peanut = self.add_instance(temp_peanut, orient='R0', loc=(0,0))

        # master_rings.append(self.add_instance(template_rings[1], orient='R0', loc=(position_ring1[0], position_ring1[1] - y_shift_ring2)))

        #temp_peanut = self.new_template(params=ringpa, temp_cls=adiabatic_ring)



        span_y_peanut = peanut_top_port.center[1] - peanut_bot_port.center[1]

        y_shift_ring2 = span_y_peanut + spoked_peanut_gap*2 + peanut_width
        # master_rings.append(self.add_instance(template_rings[1], orient='R0', loc=(position_ring1[0], position_ring1[1] - y_shift_ring2)))

        master_rings.append(self.add_instance(template_rings[1], orient='R0', loc=(0,0)))
        ring2_top_port = master_rings[1].get_photonic_port('PORT_RING_TOP')

        trans_vec_ring2 = ring1_bot_port.center - ring2_top_port.center - np.array([0, y_shift_ring2])
        master_rings[1].move_by(dx=trans_vec_ring2[0], dy=trans_vec_ring2[1], unit_mode=False)


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
    spec_file = 'layout/DualRing/specs/dual_ring_test.yaml'
    plm = BPG.PhotonicLayoutManager(spec_file)
    plm.generate_content()
    plm.generate_gds()
    plm.dataprep_calibre()