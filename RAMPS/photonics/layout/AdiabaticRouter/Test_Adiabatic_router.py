### FIX for improper rotation by arbitrary angle was to comment out self.move_by function call in geometry.mirror_rotate_translate
import BPG
from layout.AdiabaticRouter.AdiabaticRouter import AdiabaticRouter
from layout.Importers.YBranch.YBranch_O_band_no_bends import YBranch_OBand_no_bends
from numpy import pi
from layout.Importers.Gratings.PDK_grating_Oband import PDK_grating_Oband
import numpy as np
from bag.layout.util import BBox


class Test(BPG.PhotonicTemplateBase):
    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)

    @classmethod
    def get_params_info(cls):
        return dict(

        )

    @classmethod
    def get_default_param_values(cls):
        return dict(

        )

    def draw_layout(self) -> None:

        # gc_master = self.new_template(params=None, temp_cls=PDK_grating_Oband)
        # gc_inst = self.add_instance(master=gc_master)
        init_port = self.add_photonic_port(
            name='PORT_IN',
            center=(0, 0),
            orient='R0', width=0.5, layer=('si_full_free', 'port'))

        Wg = AdiabaticRouter(gen_cls=self, init_port=init_port, layer=('si_full_free', 'drawing'), name='p')

        Wg.add_wrapped_ring_coupler(w_coupling=0.5, rmin_in=5, r_coupling=6, angle_coupling=np.pi/6.2, alpha_zero_in=-np.pi/3)
        # turn_left = True
        # for i in range(4):
        #     Wg.add_straight_wg(length=100)
        #     Wg.add_bend_180(rmin=4, turn_left=turn_left)
        #     turn_left = not turn_left
        #
        # Wg.add_straight_wg(length=100)
        # self.add_instance_port_to_port(inst_master=gc_master, instance_port_name='PORT_OUT', self_port=Wg.port)
        # # radius = 10
        # init_port = self.add_photonic_port(name='init_port2', center=(0, 0), orient='R0', width=0.45,
        #                                     layer=('RX', 'port'))
        # Wg = AdiabaticRouter(gen_cls=self,
        #                       init_port=init_port,
        #                       layer=('si_full_free', 'drawing'),
        #                       name='init_port2')
        # 
        # for i in range(2):
        #     Wg.add_arb_bend(angle=[0, -pi / 8, -pi/4, -pi / 2,  -3 * pi / 4, -7*pi/8 , - pi],
        #                      curvature=[1 / (1*radius), 1 / (1*radius), 1 / (1*radius), 1 / radius, 1 / (1*radius), 1 / (1*radius), 1 / (1*radius)],
        #                      width=[0.45, 0.7, 0.9, 1.4, 0.9, 0.7, 0.45], override_width=True)

        # radius = 8
        # init_port = self.add_photonic_port(name='init_port2', center=(0, 0), orient='R0', width=0.45,   layer=('RX', 'port'))
        # Wg = AdiabaticRouter(gen_cls=self, init_port=init_port, layer=('si_full_free', 'drawing'), name='init_port2')
        # curvature = -1.0 / radius

        # for i in range(2):
        #     Wg.add_arb_bend(angle=[0, pi/2,  pi],
        #                     curvature=[curvature,
        #                                curvature,
        #                                curvature,],
        #                     width=[0.45, 1.5, 0.45],
        #                     override_width=True)

        # for i in range(2):
        #     Wg.add_arb_bend(angle=[0, pi / 12, pi / 4, 3 * pi / 8,
        #                            pi / 2,
        #                            5 * pi / 8, 3 * pi / 4, 11 * pi / 12, pi],
        #                     curvature=[curvature, curvature, curvature, curvature,
        #                                curvature,
        #                                curvature, curvature, curvature, curvature],
        #                     width=[0.45, 0.55, 1, 1., 1., 1., 1, 0.55, 0.45],
        #                     override_width=True)
        #
        #
        # temp = self.new_template(params=None, temp_cls=YBranch_OBand_no_bends)
        # master = self.add_instance(master=temp, loc=(20, 0))
        #
        # Wg_in = AdiabaticRouter(gen_cls=self, init_port=master['PORT_IN'], layer=('si_full_free', 'drawing'), name='init1')
        # Wg_in.add_straight_wg(length=5)
        #
        # Wg_out1 =  AdiabaticRouter(gen_cls=self, init_port=master['PORT_OUT1'], layer=('si_full_free', 'drawing'), name='init2')
        # Wg_out1.add_straight_wg(length=6)



        # [0.45, 0.9, 1.4, 0.9, 0.45]
        # Wg1.add_arb_bend(angle=[0, -pi / 2, -pi], curvature=[0, +1 / radius, 0], width=[1.45, 0.5])

        # Wg1.add_bend_90(rmin=10, turn_left=False, width=[1.45, 0.45])
        # Wg1.add_bend_180(rmin=10, turn_left=False, width=[1.45, 0.45])

        # b = compute_arc_length(Wg1.inst[0].master.arc_list)
        # print(b)

        # Wg.add_straight_wg(length=5)

        # Wg.add_parabolic_polygon(wout=1.45, length=1.5)
        # Wg.add_straight_wg(length=1.2)
        # Wg.add_straight_wg(length=0.7, width=1.3)
        # Wg.add_straight_wg(length=1.2)
        # Wg.add_straight_wg(length=0.5, width=1.35)
        # Wg.add_straight_wg(length=1.36)
        #
        #
        # init_port1 = self.add_photonic_port(name='init_port1',
        #                                    center=(6.96, 0.365),
        #                                    orient='R180',
        #                                    width=0.62,
        #                                    layer=('RX', 'port'))
        # Wg1 = AdiabaticRouter(gen_cls=self,
        #                      init_port=init_port1,
        #                      layer=('rx3phot', 'drawing'),
        #                      name='init_port')
        # Wg1.add_parabolic_polygon(wout=0.48, length=1.4)
        # Wg1.add_straight_wg(length=0.7)
        # # Wg1.add_straight_wg(length=1.5, width=0.38)
        # # Wg1.add_spline_bend(gap_out=1.9, gap_in=0.25, s=0.1, w_in_section=0.38, dx=0.1, w_out_section=0.38, length=6.5)
        # # Wg1.add_straight_wg(length=2.5)
        #
        #
        # init_port2 = self.add_photonic_port(name='init_port2',
        #                                     center=(6.96, -0.365),
        #                                     orient='R180',
        #                                     width=0.62,
        #                                     layer=('RX', 'port'))
        # Wg2= AdiabaticRouter(gen_cls=self,
        #                       init_port=init_port2,
        #                       layer=('rx3phot', 'drawing'),
        #                       name='init_port')
        # Wg2.add_parabolic_polygon(wout=0.48, length=1.4)
        # Wg2.add_straight_wg(length=0.7)
        # # Wg2.add_straight_wg(length=1.5, width=0.38)
        # # Wg2.add_spline_bend(gap_out=-1.9, gap_in=0.25, s=0.1, w_in_section=0.38, dx=0.1, w_out_section=0.38, length=6.5)
        # # Wg2.add_straight_wg(length=2.5)
        #
        #
        # # self.add_instances_port_to_port(inst_master=grating_temp, instance_port_name='PORT_OUT', self_port=Wg.port)

        bbox = BBox(
            top=2,
            bottom=-2,
            left=-2,
            right=2,
            resolution=self.grid.resolution
        )
        # self.add_label(label=self.ring_params['via_stack']['label']['P'],
        #                layer=(top_layer[0], "label"),
        #                bbox=bbox)
        self.add_pin_primitive(
            net_name='test',
            label='test2',
            layer=('RX', "label"),
            bbox=bbox
        )
