import BPG
from copy import deepcopy
from layout.Y_branch.Y_branch import Y_branch
from Photonic_Core_Layout.AdiabaticPaths.AdiabaticPaths import AdiabaticPaths


class Y_mirror(BPG.PhotonicTemplateBase):
    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)

        self.y_branch_params = deepcopy(self.params['y_branch_params'])
        self.rmin = params['rmin']
       # self.offset = params['offset']

        self.layer = params['y_branch_params']['layer']
        self.port_layer = ('si_full_free', 'port')
        #self.coupling_width = self.params['coupling_width']

    @classmethod
    def get_params_info(cls):
        return dict(
            y_branch_params="None",
            rmin="None",
          #  coupling_width = 'Width of the band in the coupling region',
        )

    @classmethod
    def get_default_param_values(cls):
        return dict(
            y_branch_params="None",
            rmin="None",
            coupling_width = None
        )

    def draw_layout(self) -> None:
        # Template of adiabatic band parameters
        adiabatic_band_params = dict(layer=self.layer, port_layer=self.port_layer, radius_threshold=1.5,
                                     curvature_rate_threshold=0.7, merge_arcs=False)

        size = self.rmin * 2

        offset = (size - (self.y_branch_params['final_width'] - self.y_branch_params['input_width'])) / 2
        self.y_branch_params['offset'] = offset


        y_branch_temp = self.new_template(params=self.y_branch_params, temp_cls=Y_branch)
        y_branch_inst = self.add_instance(master=y_branch_temp, orient='R0')

        self.extract_photonic_ports(inst=y_branch_inst,port_names=['PORT_IN'])


        circular_bend = deepcopy(adiabatic_band_params)
        if self.y_branch_params['offset_bend_width'] == None:
            width = self.y_branch_params['branch_width']
        else:
            width = self.y_branch_params['offset_bend_width']

        circular_bend['arc_params'] = [
            dict(arc_type="180_bend", width=width, turn_left=False, size=size)]

        circular_temp =  self.new_template(params=circular_bend, temp_cls=AdiabaticPaths)
        circular_inst = self.add_instances_port_to_port(inst_master=circular_temp, instance_port_name='PORT_IN',
                                                            self_port=y_branch_inst['PORT_1_OUT'])

def test_taper():
    # 45RF spec file:
    spec_file = 'layout/Mrinmoy_Y_branch/specs/y_mirror.yaml'

    plm = BPG.PhotonicLayoutManager(spec_file)
    plm.generate_content(save_content=False)
    plm.generate_gds()


if __name__ == '__main__':
    test_taper()