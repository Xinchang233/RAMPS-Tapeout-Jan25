import BPG
from layout.Importers.Gratings.GcBidirWl1300nmMfd5000nm import GcBidirWl1300nmMfd5000nm
from Photonic_Core_Layout.AdiabaticPaths.AdiabaticPaths import AdiabaticPaths
from copy import deepcopy


class Str_wg_w_gratings(BPG.PhotonicTemplateBase):
    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)

        self.length = self.params['length']
        self.width = self.params['width']
        self.number_of_turns = self.params['number_of_turns']
        self.r = self.params['r']

    @classmethod
    def get_default_param_values(cls):
        return dict(
            # Standard parameters
            length = 1000,
            width = 0.55,
            number_of_turns = 4,
            r = 5.5
        )

    @classmethod
    def get_params_info(cls):  # Returns definition of the parameters.
        return dict(
            length = 'Length of str wg',
            width = 'Width of Wg',
            number_of_turns = 'NUmber of 180 degree adiabatic bands to be instantiated',
            r = 'Radius of curvature of 180 degree bend'
            )

    def draw_layout(self):
        layer = ('rx3phot', 'drawing')
        wg_params = dict(layer=layer, port_layer=('si_full_free', 'port'),
                           radius_threshold=1,
                           curvature_rate_threshold=0.9, merge_arcs=False)


        wg_params['arc_params'] = [dict(arc_type='straight_wg', length = self.length, width=self.width)]
        bend_180_params = deepcopy(wg_params)
        bend_180_params['arc_params'] = [dict(arc_type = '180_bend', turn_left=True,  width = self.width, rmin = self.r)]

        bend__temp = self.new_template(params=wg_params, temp_cls=AdiabaticPaths)
        bend_180_temp = self.new_template(bend_180_params, AdiabaticPaths)

        grating_temp = self.new_template(params=None, temp_cls=GcBidirWl1300nmMfd5000nm)


        bend_inst = self.add_instance(master=bend__temp)
        self.add_instances_port_to_port(inst_master=grating_temp,
                                        instance_port_name='PORT_OUT',
                                        self_port=bend_inst['PORT_IN'])

        reflect = False
        for i in range(self.number_of_turns):
            bend_inst = self.add_instances_port_to_port(inst_master=bend_180_temp,
                                        instance_port_name='PORT_IN',
                                        self_port=bend_inst['PORT_OUT'], reflect=reflect)
            reflect = not reflect

        self.add_instances_port_to_port(inst_master=grating_temp,
                                        instance_port_name='PORT_OUT',
                                        self_port=bend_inst['PORT_OUT'])



if __name__ == '__main__':
    spec_file = '/projectnb/siphot/djordje/TO_45RF_2019May/layout/Str_wg_w_gratings/specs/str_wg_w_gratings.yaml'
    plm = BPG.PhotonicLayoutManager(spec_file)
    plm.generate_content()
    plm.generate_gds()
    plm.dataprep_calibre()

