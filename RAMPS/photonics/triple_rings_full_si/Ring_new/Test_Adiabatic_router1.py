### FIX for improper rotation by arbitrary angle was to comment out self.move_by function call in geometry.mirror_rotate_translate
import BPG
from layout.Ring_new.AdiabaticRouter import AdiabaticRouter
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
import numpy as np

class adiabatic_ring1(BPG.PhotonicTemplateBase):
    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)
        self.layer=self.params['layer'],
        self.layer1 = params['layer1'],
        self.w = self.params['w']
        self.y = self.params['y']
        self.x = self.params['x']
        self.gap = self.params['gap']
        self.wg180_radius = self.params['wg180_radius']
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
        )

    @classmethod
    def get_default_param_values(cls):
        return dict(

        )
#(5+5*math.sin(pi/6)+5.6*math.sin(pi/5), 5.6-(5.6-5.6*math.cos(pi/5)+5-5*math.cos(pi/5)))
    def draw_layout(self) -> None:
        pi=np.pi
        init_port = self.add_photonic_port(name='init_port', center=((self.x + 10) / 2, -(5 + 0.2 + self.gap - self.y)),
                                           orient='R0',
                                           width=self.w, layer=self.layer)
        # init_port = self.add_photonic_port(name='init_port', center=(0,0), orient='R0',width=w, layer=('RX', 'port'))
        # (27.6/2,5.6-2.4275919117522138)
        print(self.layer1)
        Wg = AdiabaticRouter(gen_cls=self,
                             init_port=init_port,
                             layer=self.layer1[0], # this line creates problem
                             name='init_port')
        Wg.add_straight_wg(length=5)

        Wg.add_wrapped_ring_coupler(rmin_in=5, alpha_zero_in=pi / 6,
                                    r_coupling=5 + 0.2 + self.gap,
                                    angle_coupling=pi / 5, w_coupling=self.w)
        a = compute_arc_length(Wg.inst[1].master.arc_list)
        [X, Y] = compute_arc_length1(Wg.inst[1].master.arc_list)

        print(a, X, Y)
        Wg.add_straight_wg(length=5)
        init_port1 = self.add_photonic_port(name='init_port1',
                                            center=(0, 0),
                                            orient='R0',
                                            width=0.6,
                                            layer=self.layer)
        Wg1 = AdiabaticRouter(gen_cls=self,
                              init_port=init_port1,
                              layer=self.layer1[0],
                              name='init_port')
        Wg.add_arb_bend(angle=[pi/10], curvature=pi)  #important

        Wg.add_straight_wg(length=5)
        Wg.add_wrapped_ring_coupler(rmin_in=5, alpha_zero_in=pi / 6,
                                    r_coupling=5 + 0.2 + self.gap,
                                    angle_coupling=pi / 5, w_coupling=self.w)
        a5 = compute_arc_length(Wg.inst[3].master.arc_list)
        [X1, Y1] = compute_arc_length2(Wg.inst[3].master.arc_list)
        print(a5, Y1)
        placer = -(2 * (5 + self.gap + 0.2) - 2 * self.y + Y1)
        Wg.add_straight_wg(length=5)
        Wg.add_arb_bend(angle=[pi/10],curvature=pi,w_coupling=self.w)
        
def test_taper():
    # 45RF spec file:
    spec_file = 'layout/AdiabaticRouter/specs/test_adiabatic_router.yaml'
    plm = BPG.PhotonicLayoutManager(spec_file)
    plm.generate_content()
    plm.generate_gds()
    #plm.dataprep_calibre()


if __name__ == '__main__':
    test_taper()
