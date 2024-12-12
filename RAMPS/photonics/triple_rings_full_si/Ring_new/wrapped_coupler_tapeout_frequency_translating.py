### FIX for improper rotation by arbitrary angle was to comment out self.move_by function call in geometry.mirror_rotate_translate
import BPG
from ...triple_rings_full_si.Ring_new.AdiabaticRouter import AdiabaticRouter
from ...triple_rings_full_si.BasicElements.SimpleRing.SimpleRing import SimpleRing
from ...triple_rings_full_si.utils.adiabatic_bends import compute_arc_length
from ...triple_rings_full_si.utils.adiabatic_bends import compute_arc_length
from ...triple_rings_full_si.utils.adiabatic_bends_x_y import compute_arc_length1
from ...triple_rings_full_si.utils.adiabatic_bends_x_y_2nd import compute_arc_length2
from ...triple_rings_full_si.BasicElements.SimpleRing.SimpleRing import SimpleRing
from ...triple_rings_full_si.AdiabaticRouter.SimpleRound.SimpleRound import SimpleRound
from BPG.objects import PhotonicPolygon
import math
import numpy as np
import numpy as np
from ...triple_rings_full_si.Ring.ringheater_theta2 import RingHeater

class adiabatic_coupler_cena(BPG.PhotonicTemplateBase):
    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)
        self.layer = self.params['layer'],
        self.layer1 = params['layer1'],
        self.w = self.params['w']
        self.y = self.params['y']
        self.x = self.params['x']
        self.gap = self.params['gap']
        self.wg180_radius = self.params['wg180_radius']
        self.r_core_cent=self.params['r_core_cent']
        self.coup_core_width=self.params['coup_core_width']
        self.rmin_in = self.params['rmin_in']
        self.alpha_zero_in = self.params['alpha_zero_in']
        self.angle_coupling = self.params['angle_coupling']
        self.core_width= self.params['core_width']
        self.coup_gap=self.params['coup_gap']
        self.r_r_gap=self.params['r_r_gap']



    @classmethod
    def get_params_info(cls):
        return dict(
            layer='sfds',
            layer1='shj',
            w='dsfsd',
            x='xx',
            y='sd',
            gap='asd',
            wg180_radius='asda',
            coup_core_width='asdas',
            r_core_cent='asdas',
            rmin_in='asd',
            alpha_zero_in='asdas',
            angle_coupling='dsafas',
            core_width='sf',
            coup_gap='asd',
            r_r_gap='safa',


        )

    @classmethod
    def get_default_param_values(cls):
        return dict(

        )
#(5+5*math.sin(pi/6)+5.6*math.sin(pi/5), 5.6-(5.6-5.6*math.cos(pi/5)+5-5*math.cos(pi/5)))
    def draw_layout(self) -> None:
        pi=np.pi
        init_port = self.add_photonic_port(name='init_port', center=(0, -(self.r_core_cent + self.coup_core_width/2 + self.gap - self.y)),
                                           orient='R180',
                                           width=self.coup_core_width, layer=self.layer)
        # init_port = self.add_photonic_port(name='init_port', center=(0,0), orient='R0',width=w, layer=('RX', 'port'))
        # (27.6/2,5.6-2.4275919117522138)
        print(self.layer1)
        Wg = AdiabaticRouter(gen_cls=self,
                             init_port=init_port,
                             layer=self.layer1[0], # this line creates problem
                             name='init_port')
        Wg.add_straight_wg(length=7)
        Wg.add_bend_90(size=10)


        self.extract_photonic_ports(
            inst=Wg.inst[list(Wg.inst)[-1]],
            port_names=['PORT_IN', 'PORT_OUT'],
            port_renaming={'PORT_IN': 'PORT_IN',
                           'PORT_OUT': 'PORT_OUT_FINAL',
                           },
            show=True)


        Wg.add_bend_180(size=2*( 3*self.r_core_cent +  self.coup_core_width / 2 + self.coup_gap+self.r_r_gap ),turn_left=False)

        Wg.add_bend_90(size=10)

        #self.layer1[0]
        # Wg.add_wrapped_ring_coupler(rmin_in=5, alpha_zero_in=pi / 6,
        #                             r_coupling=5 + 0.2 + self.gap,
        #                             angle_coupling=pi / 5, w_coupling=self.w)



        #Wg.add_wrapped_ring_coupler_centport(rmin_in=10, alpha_zero_in=pi / 6,
        #                                     r_coupling=6 + 0.4 / 2 + 0.1,
        #                                     angle_coupling=pi / 5, w_coupling=self.coup_core_width)


        # a = compute_arc_length(Wg.inst[1].master.arc_list)
        # [X, Y] = compute_arc_length1(Wg.inst[1].master.arc_list)

        # print(a, X, Y)



        self.extract_photonic_ports(
            inst=Wg.inst[list(Wg.inst)[-1]],
            port_names=['PORT_IN', 'PORT_OUT'],
            port_renaming={'PORT_IN': 'PORT_180LEFT_BOT',
                           'PORT_OUT': 'PORT_OUT'
                           },
            show=True)

        Wg.add_straight_wg(length=7)

        # a5 = compute_arc_length(Wg.inst[3].master.arc_list)
        # [X1, Y1] = compute_arc_length2(Wg.inst[3].master.arc_list)
        # print(a5, Y1)
        # placer = -(2 * (5 + self.gap + 0.2) - 2 * self.y + Y1)
        # Wg.add_straight_wg(length=7)
        # Wg.add_bend_180(rmin=self.wg180_radius, turn_left='true') #important
        # a = compute_arc_length(Wg.inst[0].master.arc_list) + compute_arc_length(
        #     Wg.inst[1].master.arc_list) + compute_arc_length(Wg.inst[2].master.arc_list) + compute_arc_length(
        #     Wg.inst[3].master.arc_list)
        # b = a + compute_arc_length(Wg.inst[4].master.arc_list) + compute_arc_length(
        #     Wg.inst[5].master.arc_list) + compute_arc_length(Wg.inst[6].master.arc_list) + compute_arc_length(
        #     Wg.inst[7].master.arc_list)

        # a5 = compute_arc_length(Wg.inst[4].master.arc_list)
        # [X1, Y1] = compute_arc_length2(Wg.inst[4].master.arc_list)
        # print(a5, Y1)
        # placer = -(2 * (5 + self.gap + 0.2) - 2 * self.y + Y1)




def test_taper():
    # 45RF spec file:
    spec_file = 'layout/AdiabaticRouter/specs/test_adiabatic_router.yaml'
    plm = BPG.PhotonicLayoutManager(spec_file)
    plm.generate_content()
    plm.generate_gds()
    #plm.dataprep_calibre()


if __name__ == '__main__':
    test_taper()
