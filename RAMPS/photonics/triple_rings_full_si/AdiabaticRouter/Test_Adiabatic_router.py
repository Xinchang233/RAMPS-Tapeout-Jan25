### FIX for improper rotation by arbitrary angle was to comment out self.move_by function call in geometry.mirror_rotate_translate
import BPG
from layout.AdiabaticRouter.AdiabaticRouter import AdiabaticRouter
from layout.EQUIP.BasicElements.SimpleRing.SimpleRing import SimpleRing
from utils.adiabatic_bends import compute_arc_length
from numpy import pi
from layout.EQUIP.RectalinearRouter.RectalinearRouter import RectalinearRouter
from Photonic_Core_Layout_Djordje.Spoke.SpokeBase import SpokeBase

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

        # t = self.new_template(params=None, temp_cls=YBranch_CBand_with_bends)
        # self.add_instance(master=t, loc=(0, 6))
        init_port = self.add_photonic_port(name='init_port',
                               center=(0, 0),
                               orient='R270',
                               width=0.7,
                               layer=('RX', 'port'))

      #   Wg = RectalinearRouter(gen_cls=self,
      #                         init_port= init_port ,
      #                         layer=('M1', 'drawing'),
      #                        name = 'init_port')
      #   Wg.route(length=5, direction="S", width=2)
      # #  Wg.route(length=7, direction="S", width=2)
      #   Wg.route(length=5, direction="R", width=2)
      #   Wg.route(length=5, direction="S", width=2)
      #   Wg.route(length=5, direction="L", width=2)
      #   Wg.route(length=5, direction="S", width=2)
      #   Wg.route(length=5, direction="L", width=2)
      #   Wg.route(length=15, direction="S", width=2)
      #
      #   Wg.route(length=5, direction="L", width=2)
      #   Wg.route(length=5, direction="L", width=2)
      #   Wg.route(length=5, direction="R", width=2)
      #   Wg.route(length=5, direction="R", width=2)
      #
      #   Wg.route(length=5, direction="S", width=2)
      #   Wg.route(length=5, direction="R", width=2)
      #   Wg.route(length=2, direction="R", width=2)
      #   Wg.auto_route(final_cord=(-25, -20))

        # spoke_info_n = dict(
        #     rout=12.2,
        #     rin=11.7,
        #     num=180,
        #     spoke_width_percentage=0.5,
        #     spoke_offset=0,
        #     layer=('nw4phot', 'drawing'),
        # )
        # spoke_master_n = self.new_template(params=spoke_info_n, temp_cls=SpokeBase)
        # self.add_instance(
        #     master=spoke_master_n,
        #     inst_name='high_p_doping',
        #     loc=(40,30),
        #     orient="R0",
        #     unit_mode=False,
        # )
        #
        # spoke_info_p = dict(
        #     rout=12.2,
        #     rin=11.7,
        #     num=180,
        #     spoke_width_percentage=0.5,
        #     spoke_offset=0.5,
        #     layer=('pw4phot', 'drawing'),
        # )
        # spoke_master_p = self.new_template(params=spoke_info_p, temp_cls=SpokeBase)
        # self.add_instance(
        #     master=spoke_master_p,
        #     inst_name='high_p_doping',
        #     loc=(40, 30),
        #     orient="R0",
        #     unit_mode=False,
        # )
#
        Wg = AdiabaticRouter(gen_cls=self,
                              init_port= init_port ,
                              layer=('rx3phot', 'drawing'),
                             name = 'init_port')

        Wg.add_straight_wg(length=5)
        Wg.add_bend_180(rmin=3, turn_left=False, width=[0.7, 1.1, 0.7])
        Wg.add_straight_wg(length=5)
        a=compute_arc_length(Wg.inst[1].master.arc_list)
        print(a)
        # b=Wg.port.center
        # c = Wg.port.orientation
        # init_port1 = self.add_photonic_port(name='init_port1',
        #                                    center=(10, 5),
        #                                    orient='R0',
        #                                    width=0.6,
        #                                    layer=('RX', 'port'))
        #
        # Wg1 = AdiabaticRouter(gen_cls=self,
        #                      init_port=init_port1,
        #                      layer=('rx3phot', 'drawing'),
        #                      name='init_port1')
        # # Wg.add_straight_wg(length=5)
        # Wg1.add_bend_90(size=10, turn_left=False, width=0.8)
        # Wg1.add_bend_90(size=10, turn_left=False, width=0.6)
        # Wg1.add_bend_90(size=10, turn_left=False, width=0.8)
        # Wg1.add_bend_90(size=10, turn_left=False, width=0.6)
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



def test_taper():
    # 45RF spec file:
    spec_file = 'layout/AdiabaticRouter/specs/test_adiabatic_router.yaml'
    plm = BPG.PhotonicLayoutManager(spec_file)
    plm.generate_content()
    plm.generate_gds()
    # plm.generate_flat_content()
    # plm.generate_flat_gds()
   # plm.dataprep_calibre()


if __name__ == '__main__':
    test_taper()

