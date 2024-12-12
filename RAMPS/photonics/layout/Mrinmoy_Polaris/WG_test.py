import BPG
from layout.AdiabaticRouter.AdiabaticRouter import AdiabaticRouter
from layout.Importers.Gratings.PDK_grating_Cband import PDK_grating_Cband
from layout.Importers.YBranch.YBranch_C_band_with_bends import YBranch_CBand_with_bends
from layout.WaveguideBase.SimpleWaveguide import SimpleWaveguide


class BalancedMZI(BPG.PhotonicTemplateBase):
    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)

        self.input_width = params['input_width']
        self.layer = params['layer']
        # self.port_layer = self.port_layer = ['si_full_free', 'port']
        self.port_layer = params['port_layer']

        self.rmin = 5

    @classmethod
    def get_params_info(cls):
        return dict(
            input_width="Initial width of the router",
            layer="layer where device are drawn",
            port_layer="layer where port is drawn"
        )

    def draw_layout(self):
        # init_port = self.add_photonic_port(name='init_port',center=(0,0), orient='R0', width=self.input_width, layer=self.port_layer)
        #
        # wg= AdiabaticRouter(gen_cls=self, init_port=init_port, layer=self.layer)
        #
        # wg.add_straight_wg(length=5)
        # wg.add_offset_bend(offset=10, rmin=2)
        # wg.add_offset_bend(offset=-10, rmin=2)
        # wg.add_straight_wg(length=10)
        # wg.add_bend_90(size=2, turn_left= True)
        # wg.add_bend_180(size=4, turn_left=False)
        #
        # self.grating_temp=self.new_template(params=None, temp_cls=PDK_grating_Cband)
        # self.grating_inst=self.add_instance_port_to_port(inst_master=self.grating_temp,instance_port_name='PORT_IN',self_port=self.wg.add_straight_wg['PORT_IN'])

        #####################################################################
        grating_temp = self.new_template(temp_cls=PDK_grating_Cband)
        y_branch_temp = self.new_template(temp_cls=YBranch_CBand_with_bends)

        slot_wg_params = dict(length=50, width=1, layer=self.layer, port_layer=self.port_layer)
        slot_wg_temp = self.new_template(params=slot_wg_params, temp_cls=SimpleWaveguide)

        #adding grating coupler
        grating_inst = self.add_instance(master=grating_temp)

        #adding WG connecting Grating_coupler and Y-branch
        wg = AdiabaticRouter(gen_cls=self, init_port=grating_inst['PORT_OUT'], layer=self.layer)
        wg.add_straight_wg(length=20, width=y_branch_temp._photonic_ports['PORT_IN'].width)

        #adding Y-branch/splitter
        y_branch_inst = self.add_instance_port_to_port(inst_master=y_branch_temp,
                                                       instance_port_name='PORT_IN',
                                                       self_port=wg.port)

        #adding off_set_bends in Y-branch BOTTOM arms
        wg_router_bottom = AdiabaticRouter(gen_cls=self, init_port=y_branch_inst['PORT_OUT1'], layer=self.layer)
        wg_router_bottom.add_offset_bend(rmin=self.rmin,
                                         offset=20,
                                         # width=slot_wg_temp._photonic_ports['PORT_IN'].width
                                         )
        wg_router_bottom.add_straight_wg(length=5, width=slot_wg_temp._photonic_ports['PORT_IN'].width)

        # replace it with SLOT section
        slot_wg_inst_bot = self.add_instance_port_to_port(inst_master=slot_wg_temp,
                                                          instance_port_name='PORT_IN',
                                                          self_port=wg_router_bottom.port)
        # adding off_set_bends in Y-branch TOP arms
        wg_router_top = AdiabaticRouter(gen_cls=self, init_port=y_branch_inst['PORT_OUT2'], layer=self.layer)
        wg_router_top.add_offset_bend(rmin=self.rmin,
                                      offset=-20,
                                      # width=slot_wg_temp._photonic_ports['PORT_IN'].width
                                      )
        wg_router_top.add_straight_wg(length=5, width=slot_wg_temp._photonic_ports['PORT_IN'].width)

        #replace it with SLOT section
        slot_wg_inst_top = self.add_instance_port_to_port(inst_master=slot_wg_temp,
                                                          instance_port_name='PORT_IN',
                                                          self_port=wg_router_top.port)
######################



        #other side arm
        wg_router_bottom2=AdiabaticRouter(gen_cls=self, init_port=slot_wg_inst_bot['PORT_OUT'],layer=self.layer)
        wg_router_bottom2.add_straight_wg(length=5, width=y_branch_inst['PORT_OUT1'].width)

        wg_router_bottom2.add_offset_bend(rmin=self.rmin, offset=-20)



        wg_router_top2=AdiabaticRouter(gen_cls=self, init_port=slot_wg_inst_top['PORT_OUT'],layer=self.layer)
        wg_router_top2.add_straight_wg(length=5, width=y_branch_inst['PORT_OUT2'].width)

        wg_router_top2.add_offset_bend(rmin=self.rmin, offset=20 )

        y_branch_temp2 = self.new_template(temp_cls=YBranch_CBand_with_bends, orient='R0')
        y_branch_inst2 = self.add_instance_port_to_port(inst_master=y_branch_temp,
                                                       instance_port_name=['PORT_OUT1','PORT_OUT2'],
                                                       self_port=[wg_router_top2.port, wg_router_bottom2.port])



        # def test_taper():
        #     # 45RF spec file:
        #     spec_file = 'layout/Mrinmoy_Polaris/specs/WG_specs.yaml'
        #     plm = BPG.PhotonicLayoutManager(spec_file)
        #     plm.generate_content(save_content=False)
        #     plm.generate_gds()
        #
        #
        # if __name__ == '__main__':
        #     test_taper()
