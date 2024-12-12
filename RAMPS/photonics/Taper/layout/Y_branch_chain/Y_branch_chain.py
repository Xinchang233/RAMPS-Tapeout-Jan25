import BPG
from layout.Y_branch.Y_branch import Y_branch
from layout.Importers.Gratings.GcBidirWl1300nmMfd5000nm import GcBidirWl1300nmMfd5000nm
from Photonic_Core_Layout.AdiabaticPaths.AdiabaticPaths import AdiabaticPaths


class Y_branch_chain(BPG.PhotonicTemplateBase):
    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)

        self.y_branch_params = params['y_branch_params']
        self.num_inst = params['num_inst']

    @classmethod
    def get_default_param_values(cls):
        return dict(
            # Standard parameters
            y_branch_params=None,
            num_inst=None
        )

    @classmethod
    def get_params_info(cls):  # Returns definition of the parameters.
        return dict(
            # Standard parameters
            y_branch_params="None",
            num_inst="None", )

    def draw_layout(self):
        zaokret = 48
        rmin = 5.5
        additional_num_of_180_bends = 0
        bend_params = dict(layer=self.y_branch_params['layer'], port_layer=('si_full_free', 'port'),
                           radius_threshold=1,
                           curvature_rate_threshold=0.9, merge_arcs=False)

        width = self.y_branch_params['branch_width']

        bend_params['arc_params'] = [dict(arc_type='180_bend', rmin=rmin, turn_left=False, width=width)]
        bend_180_temp = self.new_template(params=bend_params, temp_cls=AdiabaticPaths)

        y_branch_temp = self.new_template(params=self.y_branch_params, temp_cls=Y_branch)
        grating_temp = self.new_template(params=None, temp_cls=GcBidirWl1300nmMfd5000nm)

        y_branch_inst = self.add_instance(master=y_branch_temp)
        self.add_instances_port_to_port(inst_master=grating_temp,
                                        instance_port_name='PORT_OUT',
                                        self_port=y_branch_inst['PORT_IN'])

        # When orient is 1, add branches to branches, otherwise add roots to roots
        orient = 1
        reflect = False
        for i in range(1, int(self.num_inst)):
            if i % zaokret == 0:
                y_branch_inst = self.add_instances_port_to_port(inst_master=bend_180_temp,
                                                                instance_port_name='PORT_OUT',
                                                                self_port=y_branch_inst['PORT_IN'], reflect=reflect)
                reflect =  not reflect
            if orient:
                orient = 0
                y_branch_inst = self.add_instances_port_to_port(inst_master=y_branch_temp,
                                                                instance_port_name='PORT_1_OUT',
                                                                self_port=y_branch_inst['PORT_1_OUT'], reflect=True)
            else:
                orient = 1
                y_branch_inst = self.add_instances_port_to_port(inst_master=y_branch_temp,
                                                                instance_port_name='PORT_IN',
                                                                self_port=y_branch_inst['PORT_IN'])
           # if i == self.num_inst - 1:
                # if i % 2 == 1:
                #     self.add_instances_port_to_port(inst_master=grating_temp,
                #                                     instance_port_name='PORT_OUT',
                #                                     self_port=y_branch_inst['PORT_IN'])
                # else:
                #     self.add_instances_port_to_port(inst_master=grating_temp,
                #                                    instance_port_name='PORT_OUT',
                #                                    self_port=y_branch_inst['PORT_2_OUT'])
                #     bend180_inst =  self.add_instances_port_to_port(inst_master=bend_180_temp,
                #                                    instance_port_name='PORT_IN',
                #                                    self_port=y_branch_inst['PORT_1_OUT'], reflect=True)
                #     self.add_instances_port_to_port(inst_master=grating_temp,
                #                                     instance_port_name='PORT_OUT',
                #                                     self_port=bend180_inst ['PORT_OUT'])

        for i in range(additional_num_of_180_bends):
            y_branch_inst = self.add_instances_port_to_port(inst_master=bend_180_temp,
                                                            instance_port_name='PORT_OUT',
                                                            self_port=y_branch_inst['PORT_IN'], reflect=reflect)
            reflect = not reflect
        self.add_instances_port_to_port(inst_master=grating_temp,
                                            instance_port_name='PORT_OUT',
                                            self_port=y_branch_inst['PORT_IN'])