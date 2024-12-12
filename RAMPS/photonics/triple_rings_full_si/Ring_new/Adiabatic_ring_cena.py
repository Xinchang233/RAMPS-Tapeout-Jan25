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

class adiabatic_ring_tapeout(BPG.PhotonicTemplateBase):
    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)
        self.layer=self.params['layer'],
        self.layer1 = params['layer1'],
        self.w = self.params['w']
        self.y = self.params['y']
        self.x = self.params['x']
        self.gap = self.params['gap']
        self.wg180_radius = self.params['wg180_radius']
        self.r_core_cent = self.params['r_core_cent']
        self.middle_rmin_in = self.params['middle_rmin_in']
        self.middle_alpha_zero_in = self.params['middle_alpha_zero_in']
        self.middle_angle_coupling = self.params['middle_angle_coupling']

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
            r_core_cent='asdas',
            middle_rmin_in='asd',
            middle_alpha_zero_in='asdas',
            middle_angle_coupling='dsafas',
        )

    @classmethod
    def get_default_param_values(cls):
        return dict(

        )
#(5+5*math.sin(pi/6)+5.6*math.sin(pi/5), 5.6-(5.6-5.6*math.cos(pi/5)+5-5*math.cos(pi/5)))
    def draw_layout(self) -> None:
        pi=np.pi
        init_port = self.add_photonic_port(name='init_port', center=((self.x + 14) / 2, -(self.r_core_cent + self.w/2 + self.gap - self.y)),
                                           orient='R0',
                                           width=self.w, layer=self.layer)
        # init_port = self.add_photonic_port(name='init_port', center=(0,0), orient='R0',width=w, layer=('RX', 'port'))
        # (27.6/2,5.6-2.4275919117522138)
        print(self.layer1)
        Wg = AdiabaticRouter(gen_cls=self,
                             init_port=init_port,
                             layer=self.layer1[0], # this line creates problem
                             name='init_port')
        Wg.add_straight_wg(length=7)
        #self.layer1[0]
        # Wg.add_wrapped_ring_coupler(middle_rmin_in=5, middle_alpha_zero_in=pi / 6,
        #                             r_coupling=5 + 0.2 + self.gap,
        #                             middle_angle_coupling=pi / 5, w_coupling=self.w)

        Wg.add_wrapped_ring_coupler_centport(rmin_in=self.middle_rmin_in, alpha_zero_in=self.middle_alpha_zero_in* np.pi/180,
                                             r_coupling=self.r_core_cent + self.w/2 + self.gap,
                                             angle_coupling=self.middle_angle_coupling*np.pi/180, w_coupling=self.w)
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
        init_port1 = self.add_photonic_port(name='init_port1',
                                            center=(0, 0),
                                            orient='R0',
                                            width=self.w,
                                            layer=self.layer)
        Wg1 = AdiabaticRouter(gen_cls=self,
                              init_port=init_port1,
                              layer=self.layer1[0],
                              name='init_port')
        Wg.add_bend_180(rmin=self.wg180_radius, turn_left='true')  #important

        self.extract_photonic_ports(
            inst=Wg.inst[list(Wg.inst)[-1]],
            port_names=['PORT_IN', 'PORT_OUT'],
            port_renaming={'PORT_IN': 'PORT_180LEFT_BOT',
                           'PORT_OUT': 'PORT_180LEFT_TOP'
                           },
            show=True)

        # ubend_span =
        ubend_span = abs(Wg.inst[list(Wg.inst)[-1]].get_photonic_port('PORT_OUT').y - Wg.inst[list(Wg.inst)[-1]].get_photonic_port('PORT_IN').y)

        Wg.add_straight_wg(length=7)
        # Wg.add_wrapped_ring_coupler(middle_rmin_in=5, middle_alpha_zero_in=pi / 6,
        #                             r_coupling=5 + 0.2 + self.gap,
        #                             middle_angle_coupling=pi / 5, w_coupling=self.w)
        Wg.add_wrapped_ring_coupler_centport(rmin_in=self.middle_rmin_in, alpha_zero_in=self.middle_alpha_zero_in* np.pi/180,
                                             r_coupling=self.r_core_cent + self.w/2 + self.gap,
                                             angle_coupling=self.middle_angle_coupling*np.pi/180, w_coupling=self.w)

        # Wg.inst[-2]

        # self.extract_photonic_ports(
        #     inst=Wg.inst[6],
        #     port_names = 'PORT_IN',
        #     # port_renaming = dict('PORT_CENTER','PORT_OUT')
        #     port_renaming = {'PORT_IN','PORT_CENTER'}
        # )

        self.extract_photonic_ports(
                inst= Wg.inst[list(Wg.inst)[-1]],
                port_names= ['PORT_OUT'],
                port_renaming={'PORT_OUT': 'PORT_CENTER2'
                               },
                show=True)


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
        Wg.add_straight_wg(length=7)
        Wg.add_bend_180(rmin=self.wg180_radius, turn_left='true')

        self.extract_photonic_ports(
            inst=Wg.inst[list(Wg.inst)[-1]],
            port_names=['PORT_IN','PORT_OUT'],
            port_renaming={'PORT_IN': 'PORT_180RIGHT_TOP',
                           'PORT_OUT':'PORT_180RIGHT_BOT'
                           },
            show=True)

        # important
        # a = compute_arc_length(Wg.inst[0].master.arc_list) + compute_arc_length(
        #     Wg.inst[1].master.arc_list) + compute_arc_length(Wg.inst[2].master.arc_list) + compute_arc_length(
        #     Wg.inst[3].master.arc_list)
        # b = a + compute_arc_length(Wg.inst[4].master.arc_list) + compute_arc_length(
        #     Wg.inst[5].master.arc_list) + compute_arc_length(Wg.inst[6].master.arc_list) + compute_arc_length(
        #     Wg.inst[7].master.arc_list) + compute_arc_length(
        #     Wg.inst[8].master.arc_list)
        # print(b, placer)
        self.place_heater_ring(ubend_span)

    def place_heater_ring(self,ubend_span):
        # heater parameters
        heater_radius_offset = 1.3  # 0.5 #0.45 # distance from top bottom of peanut u-bend
        resistance = 200
        contact_dist = 2
        contact_width = 2  # 1.5
        heater_device_layer = ('si_full_free', 'drawing')
        heater_device_layer_RX = ('si_full_free', 'drawing')
        # heater_disk_layers = ('nw1phot', 'drawing')
        heater_disk_layers = [('n_heavy_sil', 'drawing')]

        heater_electrode_top_layer = ('BA', 'drawing')
        heater_electrode_top_x_span = 2  # 0.6
        heater_electrode_top_y_span = 6  # 1.2
        # Either heater label format is acceptable 1.2 ,1.2,1,1
        heater_label = dict(P='HEATER', N='HEATER_N')
        #  heater_label: 'HEATER'
        heater_electrode_bottom_x_span = 2  # 0.6
        heater_electrode_bottom_y_span = 6
        # Advanced parameters
        heater_disk_layer_extension = 0.1
        # Technology parameter
        heater_electrode_bottom_layer = ('RX', 'drawing')

        heater_params = dict(
            rout=( ubend_span/2 - self.w/2 - #self.wg180_radius -
                  heater_radius_offset),
            resistance=resistance,
            contact_dist=contact_dist,
            contact_width=contact_width,
            device_layer=heater_device_layer,
            disk_layers=heater_disk_layers,
            electrode_top_layer=heater_electrode_top_layer,
            electrode_top_x_span=heater_electrode_top_x_span,
            electrode_top_y_span=heater_electrode_top_y_span,
            electrode_label=heater_label,
            disk_layer_extension=heater_disk_layer_extension,
            electrode_bottom_layer=heater_electrode_bottom_layer,
        )

        # Assign dynamic defaults to heater electrode bottom span
        if heater_electrode_bottom_x_span is None:
            heater_params['electrode_bottom_x_span'] = heater_params['contact_width']
        else:

            heater_params['electrode_bottom_x_span'] = heater_electrode_bottom_x_span
        if heater_electrode_bottom_y_span is None:
            heater_params['electrode_bottom_y_span'] = heater_params['contact_width']
        else:
            heater_params['electrode_bottom_y_span'] = heater_electrode_bottom_y_span

            # Compute the width from the heater resistance design function
            heater_params['width'] = 2.5 # heater width 0.8
            heater_temp = self.new_template(params=heater_params, temp_cls=RingHeater)

            right_180_top = self.get_photonic_port('PORT_180RIGHT_TOP').center
            right_180_bot = self.get_photonic_port('PORT_180RIGHT_BOT').center
            right_h_cent = [right_180_top[0] , right_180_bot[1] + (right_180_top[1] - right_180_bot[1])/2]

            # trans_vec_ring2 = right_180_top - right_180_bot - np.array([0, y_shift_ring2])

            heater_master = self.add_instance(master=heater_temp, orient='R270', loc=(0,0))
            # trans_vec_heatr =  np.array(right_h_cent) + self.wg180_radius
            heater_master.move_by(dx=right_h_cent[0]+1 , dy=right_h_cent[1], unit_mode=False)

            self.extract_photonic_ports(
                inst=heater_master,
                port_names=['PORT_IN', 'PORT_OUT'],
                port_renaming={'PORT_IN': 'PORT_HT_R1',
                               'PORT_OUT': 'PORT_HT_R2'
                               },
                show=True)

            left_180_top = self.get_photonic_port('PORT_180LEFT_TOP').center
            left_180_bot = self.get_photonic_port('PORT_180LEFT_BOT').center
            left_h_cent = [left_180_top[0]-1, left_180_bot[1] + (left_180_top[1] - left_180_bot[1]) / 2]

            # trans_vec_ring2 = right_180_top - right_180_bot - np.array([0, y_shift_ring2])

            heater_master2 = self.add_instance(master=heater_temp, orient='R90', loc=(0, 0))
            # trans_vec_heatr =  np.array(right_h_cent) + self.wg180_radius
            heater_master2.move_by(dx=left_h_cent[0], dy=left_h_cent[1], unit_mode=False)

            self.extract_photonic_ports(
                inst=heater_master2,
                port_names=['PORT_IN', 'PORT_OUT'],
                port_renaming={'PORT_IN': 'PORT_HT_L2',
                               'PORT_OUT': 'PORT_HT_L1'
                               },
                show=True)

            contact_points = [right_180_bot,
                              left_180_bot,
                              left_180_top,
                              right_180_top
                              ]

            polygon = PhotonicPolygon(
                resolution=self.grid.resolution,
                layer=('si_full_free', 'drawing'),
                points=contact_points,
                unit_mode=False
            )
            #self.add_obj(polygon)

def test_taper():
    # 45RF spec file:
    spec_file = 'layout/AdiabaticRouter/specs/test_adiabatic_router.yaml'
    plm = BPG.PhotonicLayoutManager(spec_file)
    plm.generate_content()
    plm.generate_gds()
    #plm.dataprep_calibre()


if __name__ == '__main__':
    test_taper()
