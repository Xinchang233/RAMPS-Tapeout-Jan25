import BPG
import importlib
from layout.FilterArray_size2.FilterArray_size2 import FilterArray_size2
from layout.FilterArray_size2.FilterArray_size2 import FilterArrayCosine_size2
from Photonic_Core_Layout.AdiabaticPaths.AdiabaticPaths import AdiabaticPaths

from copy import deepcopy


class LossRingsCosine(BPG.PhotonicTemplateBase):
    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)
        self.params = deepcopy(params)
        self.filter_params = params['filter_params']
        self.grating_params = params['grating_params']
        self.place_mode_converter = params['place_mode_converter']
        self.taper_params = params['taper_params']

        self.grating_module = importlib.import_module(self.grating_params['package'])
        self.grating_cls = getattr(self.grating_module, self.grating_params['class_name'])

        if self.place_mode_converter:
            self.mode_conv_params = params['mode_converter_params']
            self.mod_conv_module = importlib.import_module(self.mode_conv_params['package'])
            self.mod_conv_cls = getattr(self.mod_conv_module, self.mode_conv_params['class_name'])

        self.template_grating = None
        self.master_grating_in = None
        self.master_grating_out = None

        self.template_filters = None
        self.master_filters = None

        self.template_tapers =None
        self.taper_master =None

        self.mode_conv_template = None
        self.mode_conv_master = None

    @classmethod
    def get_default_param_values(cls) -> dict:
        return dict(
            filter_params=None,
            grating_params=None,
            mode_conv_params=None,
            place_mode_converter=None,
            taper_params=None,

        )

    @classmethod
    def get_params_info(cls) -> dict:
        return dict(
            filter_params="None",
            grating_params='None',
            mode_conv_params="None",
            place_mode_converter='None',
            taper_params="None",
        )

    def draw_layout(self) -> None:
        self.template_filters = self.new_template(params=self.filter_params, temp_cls=FilterArrayCosine_size2)
        self.master_filters = self.add_instance(self.template_filters)

        params1=dict(layer=self.filter_params['class_params'][0]['layer'],
                    port_layer=self.filter_params['class_params'][0]['port_layer'],
                    merge_arcs=False)
        taper_params1 = deepcopy(params1)
        taper_params1['arc_params'] = [
            dict(arc_type="straight_wg", width=[self.taper_params[0]['width'],
                                                self.filter_params['class_params'][0]['input_wg']['width']],
                 length=self.taper_params[0]['length'])]
        self.template_tapers1=self.new_template(params=taper_params1,temp_cls=AdiabaticPaths)

        params2=dict(layer=self.filter_params['class_params'][1]['layer'],
                    port_layer=self.filter_params['class_params'][1]['port_layer'],
                    merge_arcs=False)
        taper_params2 = deepcopy(params2)
        taper_params2['arc_params'] = [
            dict(arc_type="straight_wg", width=[self.taper_params[1]['width'],
                                                self.filter_params['class_params'][1]['input_wg']['width']],
                 length=self.taper_params[1]['length'])]
        self.template_tapers2=self.new_template(params=taper_params2,temp_cls=AdiabaticPaths)

        dummy_params = {'gds_path': 'None'}  # Needed
        self.template_grating = self.new_template(params=dummy_params, temp_cls=self.grating_cls)

        if self.place_mode_converter:
            self.mode_conv_template = self.new_template(params=dummy_params, temp_cls=self.mod_conv_cls)
            # Create a dict for all mode masters so that they are individually addressable.
            self.mode_conv_master = {i: None for i in range(len(self.master_filters._photonic_port_list.keys()))}

            # initialize counter, i, to zero
            i = 0
            for port_name, port in self.master_filters._photonic_port_list.items():
                try:
                    self.mode_conv_master[i] = self.add_instance_port_to_port(inst_master=self.mode_conv_template,
                                                                              instance_port_name='PORT_PARTIAL',
                                                                              self_port=port,
                                                                              reflect=False)
                    master = self.add_instance_port_to_port(inst_master=self.template_grating,
                                                            instance_port_name='PORT_OUT',
                                                            self_port=self.mode_conv_master[i]['PORT_FULL'],
                                                            reflect=False)
                except:
                    self.mode_conv_master[i] = self.add_instance_port_to_port(inst_master=self.mode_conv_template,
                                                                              instance_port_name='PORT_OUT',
                                                                              self_port=port,
                                                                              reflect=False)
                    master = self.add_instance_port_to_port(inst_master=self.template_grating,
                                                            instance_port_name='PORT_OUT',
                                                            self_port=self.mode_conv_master[i]['PORT_IN'],
                                                            reflect=False)
        elif self.taper_params:
            self.taper_master = {i: None for i in range(len(self.master_filters._photonic_port_list.keys()))}
            i=0
            k=0
            for port_name, port in self.master_filters._photonic_port_list.items():
                if k<5:
                    self.taper_master[i] = self.add_instance_port_to_port(inst_master=self.template_tapers1,
                                                            instance_port_name='PORT_OUT',
                                                            self_port=port,
                                                            reflect=False)
                    master = self.add_instance_port_to_port(inst_master=self.template_grating,
                                                            instance_port_name='PORT_OUT',
                                                            self_port=self.taper_master[i]['PORT_IN'],
                                                            reflect=False)
                else:
                    self.taper_master[i] = self.add_instance_port_to_port(inst_master=self.template_tapers2,
                                                            instance_port_name='PORT_OUT',
                                                            self_port=port,
                                                            reflect=False)
                    master = self.add_instance_port_to_port(inst_master=self.template_grating,
                                                            instance_port_name='PORT_OUT',
                                                            self_port=self.taper_master[i]['PORT_IN'],
                                                            reflect=False)
                k+=1
            else:
                for port_name, port in self.master_filters._photonic_port_list.items():
                    master = self.add_instance_port_to_port(inst_master=self.template_grating,
                                                            instance_port_name='PORT_OUT',
                                                            self_port=port,
                                                            reflect=False)


class LossRings(BPG.PhotonicTemplateBase):
    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)
        self.params = deepcopy(params)
        self.filter_params = params['filter_params']
        self.grating_params = params['grating_params']
        self.place_mode_converter = params['place_mode_converter']
        self.taper_params = params['taper_params']

        self.grating_module = importlib.import_module(self.grating_params['package'])
        self.grating_cls = getattr(self.grating_module, self.grating_params['class_name'])

        if self.place_mode_converter:
            self.mode_conv_params = params['mode_converter_params']
            self.mod_conv_module = importlib.import_module(self.mode_conv_params['package'])
            self.mod_conv_cls = getattr(self.mod_conv_module, self.mode_conv_params['class_name'])

        self.template_grating = None
        self.master_grating_in = None
        self.master_grating_out = None

        self.template_filters = None
        self.master_filters = None

        self.template_tapers =None
        self.taper_master =None

        self.mode_conv_template = None
        self.mode_conv_master = None

    @classmethod
    def get_default_param_values(cls) -> dict:
        return dict(
            filter_params=None,
            grating_params=None,
            mode_conv_params=None,
            place_mode_converter=None,
            taper_params=None,

        )

    @classmethod
    def get_params_info(cls) -> dict:
        return dict(
            filter_params="None",
            grating_params='None',
            mode_conv_params="None",
            place_mode_converter='None',
            taper_params='None',
        )

    def draw_layout(self) -> None:
        self.template_filters = self.new_template(params=self.filter_params, temp_cls=FilterArray_size2)
        self.master_filters = self.add_instance(self.template_filters)

        params1=dict(layer=self.filter_params['class_params'][0]['layer'],
                    port_layer=self.filter_params['class_params'][0]['port_layer'],
                    merge_arcs=False)
        taper_params1 = deepcopy(params1)
        taper_params1['arc_params'] = [
            dict(arc_type="straight_wg", width=[self.taper_params[0]['width'],
                                                self.filter_params['class_params'][0]['input_wg']['width']],
                 length=self.taper_params[0]['length'])]
        self.template_tapers1=self.new_template(params=taper_params1,temp_cls=AdiabaticPaths)

        params2=dict(layer=self.filter_params['class_params'][1]['layer'],
                    port_layer=self.filter_params['class_params'][1]['port_layer'],
                    merge_arcs=False)
        taper_params2 = deepcopy(params2)
        taper_params2['arc_params'] = [
            dict(arc_type="straight_wg", width=[self.taper_params[1]['width'],
                                                self.filter_params['class_params'][1]['input_wg']['width']],
                 length=self.taper_params[1]['length'])]
        self.template_tapers2=self.new_template(params=taper_params2,temp_cls=AdiabaticPaths)
        dummy_params = {'gds_path': 'None'}  # Needed
        self.template_grating = self.new_template(params=dummy_params, temp_cls=self.grating_cls)

        if self.place_mode_converter:
            self.mode_conv_template = self.new_template(params=dummy_params, temp_cls=self.mod_conv_cls)
            # Create a dict for all mode masters so that they are individually addressable.
            self.mode_conv_master = {i: None for i in range(len(self.master_filters._photonic_port_list.keys()))}

            # initialize counter, i, to zero
            i = 0
            for port_name, port in self.master_filters._photonic_port_list.items():
                try:
                    self.mode_conv_master[i] = self.add_instance_port_to_port(inst_master=self.mode_conv_template,
                                                                              instance_port_name='PORT_PARTIAL',
                                                                              self_port=port,
                                                                              reflect=False)
                    master = self.add_instance_port_to_port(inst_master=self.template_grating,
                                                            instance_port_name='PORT_OUT',
                                                            self_port=self.mode_conv_master[i]['PORT_FULL'],
                                                            reflect=False)
                except:
                    self.mode_conv_master[i] = self.add_instance_port_to_port(inst_master=self.mode_conv_template,
                                                                              instance_port_name='PORT_OUT',
                                                                              self_port=port,
                                                                              reflect=False)
                    master = self.add_instance_port_to_port(inst_master=self.template_grating,
                                                            instance_port_name='PORT_OUT',
                                                            self_port=self.mode_conv_master[i]['PORT_IN'],
                                                            reflect=False)
        elif self.taper_params:
            self.taper_master = {i: None for i in range(len(self.master_filters._photonic_port_list.keys()))}
            i = 0
            k = 0
            for port_name, port in self.master_filters._photonic_port_list.items():
                if k < 5:
                    self.taper_master[i] = self.add_instance_port_to_port(inst_master=self.template_tapers1,
                                                                          instance_port_name='PORT_OUT',
                                                                          self_port=port,
                                                                          reflect=False)
                    master = self.add_instance_port_to_port(inst_master=self.template_grating,
                                                            instance_port_name='PORT_OUT',
                                                            self_port=self.taper_master[i]['PORT_IN'],
                                                            reflect=False)
                else:
                    self.taper_master[i] = self.add_instance_port_to_port(inst_master=self.template_tapers2,
                                                                          instance_port_name='PORT_OUT',
                                                                          self_port=port,
                                                                          reflect=False)
                    master = self.add_instance_port_to_port(inst_master=self.template_grating,
                                                            instance_port_name='PORT_OUT',
                                                            self_port=self.taper_master[i]['PORT_IN'],
                                                            reflect=False)
                k += 1
            else:
                for port_name, port in self.master_filters._photonic_port_list.items():
                    master = self.add_instance_port_to_port(inst_master=self.template_grating,
                                                            instance_port_name='PORT_OUT',
                                                            self_port=port,
                                                            reflect=False)


