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
        self.slab_width=self.params['slab_width']
        self.slab_layer=self.params['slab_layer']


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
            slab_width='sdf',
            slab_layer='asd'
        )

    @classmethod
    def get_default_param_values(cls):
        return dict(

        )
#(5+5*math.sin(pi/6)+5.6*math.sin(pi/5), 5.6-(5.6-5.6*math.cos(pi/5)+5-5*math.cos(pi/5)))
    def draw_layout(self) -> None:
        pi=np.pi
        init_port = self.add_photonic_port(name='init_port', center=((self.x + 14) / 2, -(self.r_core_cent + self.coup_core_width/2 + self.gap - self.y)),
                                           orient='R0',
                                           width=self.coup_core_width, layer=self.layer)
        # init_port = self.add_photonic_port(name='init_port', center=(0,0), orient='R0',width=w, layer=('RX', 'port'))
        # (27.6/2,5.6-2.4275919117522138)
        print(self.layer1)
        Wg = AdiabaticRouter(gen_cls=self,
                             init_port=init_port,
                             layer=self.layer1[0], # this line creates problem
                             name='init_port')
        Wg.add_straight_wg(length=7)

        self.extract_photonic_ports(
            inst=Wg.inst[list(Wg.inst)[-1]],
            port_names=['PORT_IN', 'PORT_OUT'],
            port_renaming={'PORT_IN': 'PORT_IN',
                           },
            show=True)
        #self.layer1[0]
        # Wg.add_wrapped_ring_coupler(rmin_in=5, alpha_zero_in=pi / 6,
        #                             r_coupling=5 + 0.2 + self.gap,
        #                             angle_coupling=pi / 5, w_coupling=self.w)



        #Wg.add_wrapped_ring_coupler_centport(rmin_in=10, alpha_zero_in=pi / 6,
        #                                     r_coupling=6 + 0.4 / 2 + 0.1,
        #                                     angle_coupling=pi / 5, w_coupling=self.coup_core_width)
        Wg.add_wrapped_ring_coupler_centport(rmin_in=self.rmin_in, alpha_zero_in=self.alpha_zero_in* np.pi/180,
                                             r_coupling=self.r_core_cent + self.coup_core_width/2 + self.gap,
                                             angle_coupling=self.angle_coupling*np.pi/180, w_coupling=self.coup_core_width)
        a = len(Wg.inst)
        self.extract_photonic_ports(
            inst=Wg.inst[list(Wg.inst)[-1]],
            port_names=['PORT_OUT'],
            port_renaming={'PORT_OUT': 'PORT_CENTER1'
                           },
            show=True)

        # a = compute_arc_length(Wg.inst[1].master.arc_list)
        # [X, Y] = compute_arc_length1(Wg.inst[1].master.arc_list)

        # print(a, X, Y)
        Wg.add_straight_wg(length=7)


        self.extract_photonic_ports(
            inst=Wg.inst[list(Wg.inst)[-1]],
            port_names=['PORT_IN', 'PORT_OUT'],
            port_renaming={'PORT_IN': 'PORT_180LEFT_BOT',
                           'PORT_OUT': 'PORT_OUT_wg'
                           },
            show=True)


# slab coupler placement begins from here


        init_port1 = self.add_photonic_port(name='init_port1', center=((self.x + 14) / 2, -(self.r_core_cent + self.coup_core_width/2 + self.gap - self.y)),
                                           orient='R0',
                                           width=self.slab_width, layer=self.slab_layer)
        # init_port = self.add_photonic_port(name='init_port', center=(0,0), orient='R0',width=w, layer=('RX', 'port'))
        # (27.6/2,5.6-2.4275919117522138)
        print(self.layer1)
        Wg1 = AdiabaticRouter(gen_cls=self,
                             init_port=init_port1,
                             layer=self.slab_layer, # this line creates problem  self.layer1[0]
                             name='init_port1')
        Wg1.add_straight_wg(length=7)

        self.extract_photonic_ports(
            inst=Wg1.inst[list(Wg1.inst)[-1]],
            port_names=['PORT_IN', 'PORT_OUT'],
            port_renaming={'PORT_IN': 'PORT_IN_slab',
                           },
            show=True)
        #self.layer1[0]
        # Wg.add_wrapped_ring_coupler(rmin_in=5, alpha_zero_in=pi / 6,
        #                             r_coupling=5 + 0.2 + self.gap,
        #                             angle_coupling=pi / 5, w_coupling=self.w)



        #Wg.add_wrapped_ring_coupler_centport(rmin_in=10, alpha_zero_in=pi / 6,
        #                                     r_coupling=6 + 0.4 / 2 + 0.1,
        #                                     angle_coupling=pi / 5, w_coupling=self.coup_core_width)
        Wg1.add_wrapped_ring_coupler_centport(rmin_in=self.rmin_in, alpha_zero_in=self.alpha_zero_in* np.pi/180,
                                             r_coupling=self.r_core_cent + self.coup_core_width/2 + self.gap,
                                             angle_coupling=self.angle_coupling*np.pi/180, w_coupling=self.slab_width)
        a = len(Wg1.inst)
        self.extract_photonic_ports(
            inst=Wg1.inst[list(Wg1.inst)[-1]],
            port_names=['PORT_OUT'],
            port_renaming={'PORT_OUT': 'PORT_CENTER1_slab'
                           },
            show=True)

        # a = compute_arc_length(Wg.inst[1].master.arc_list)
        # [X, Y] = compute_arc_length1(Wg.inst[1].master.arc_list)

        # print(a, X, Y)
        Wg1.add_straight_wg(length=7)


        self.extract_photonic_ports(
            inst=Wg1.inst[list(Wg1.inst)[-1]],
            port_names=['PORT_IN', 'PORT_OUT'],
            port_renaming={'PORT_IN': 'PORT_180LEFT_BOT_slab',
                           'PORT_OUT': 'PORT_OUT_slab'
                           },
            show=True)


# KG layer begins from here


        init_port2 = self.add_photonic_port(name='init_port2', center=((self.x + 14) / 2, -(self.r_core_cent + self.coup_core_width/2 + self.gap - self.y)),
                                           orient='R0',
                                           width=2.9, layer=('KG','drawing'))
        # init_port = self.add_photonic_port(name='init_port', center=(0,0), orient='R0',width=w, layer=('RX', 'port'))
        # (27.6/2,5.6-2.4275919117522138)
        print(self.layer1)
        Wg2 = AdiabaticRouter(gen_cls=self,
                             init_port=init_port2,
                             layer=('KG','drawing'), # this line creates problem  self.layer1[0]
                             name='init_port1')
        Wg2.add_straight_wg(length=7)

        self.extract_photonic_ports(
            inst=Wg2.inst[list(Wg2.inst)[-1]],
            port_names=['PORT_IN', 'PORT_OUT'],
            port_renaming={'PORT_IN': 'PORT_IN_kg',
                           },
            show=True)
        #self.layer1[0]
        # Wg.add_wrapped_ring_coupler(rmin_in=5, alpha_zero_in=pi / 6,
        #                             r_coupling=5 + 0.2 + self.gap,
        #                             angle_coupling=pi / 5, w_coupling=self.w)



        #Wg.add_wrapped_ring_coupler_centport(rmin_in=10, alpha_zero_in=pi / 6,
        #                                     r_coupling=6 + 0.4 / 2 + 0.1,
        #                                     angle_coupling=pi / 5, w_coupling=self.coup_core_width)
        Wg2.add_wrapped_ring_coupler_centport(rmin_in=self.rmin_in, alpha_zero_in=self.alpha_zero_in* np.pi/180,
                                             r_coupling=self.r_core_cent + self.coup_core_width/2 + self.gap,
                                             angle_coupling=self.angle_coupling*np.pi/180, w_coupling=2.9)
        a = len(Wg2.inst)
        self.extract_photonic_ports(
            inst=Wg2.inst[list(Wg2.inst)[-1]],
            port_names=['PORT_OUT'],
            port_renaming={'PORT_OUT': 'PORT_CENTER1_kg'
                           },
            show=True)

        # a = compute_arc_length(Wg.inst[1].master.arc_list)
        # [X, Y] = compute_arc_length1(Wg.inst[1].master.arc_list)

        # print(a, X, Y)
        Wg2.add_straight_wg(length=7)


        self.extract_photonic_ports(
            inst=Wg2.inst[list(Wg2.inst)[-1]],
            port_names=['PORT_IN', 'PORT_OUT'],
            port_renaming={'PORT_IN': 'PORT_180LEFT_BOT_kg',
                           'PORT_OUT': 'PORT_OUT1'
                           },
            show=True)



def test_taper():
    # 45RF spec file:
    spec_file = 'layout/AdiabaticRouter/specs/test_adiabatic_router.yaml'
    plm = BPG.PhotonicLayoutManager(spec_file)
    plm.generate_content()
    plm.generate_gds()
    #plm.dataprep_calibre()


if __name__ == '__main__':
    test_taper()
