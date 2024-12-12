import BPG
from layout.FilterRingArray.FilterRingArray import FilterRingArray
from layout.FilterRingArray.FilterRingArray import FilterRingArrayCosine
from copy import deepcopy
import random


class FilterArrayCosine_size2(BPG.PhotonicTemplateBase):
    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)
        self.params = deepcopy(params)
        self.class_params = params['class_params']
        self.vertical_displacement = params['vertical_displacement']
        self.horizontal_displacement = params['horizontal_displacement']
        try:
            self.additional_wg_layers = params['additional_wg_layers']
        except:
            self.additional_wg_layers = random.randint(1, 1331)

        self.first_array_temp = None
        self.first_array_inst = None
        self.second_array_temp = None
        self.second_array_inst = None

    @classmethod
    def get_default_param_values(cls) -> dict:
        return dict(
            class_params=None,
            vertical_displacement=None,
            horizontal_displacement=None,
            additional_wg_layers=None,
        )

    @classmethod
    def get_params_info(cls) -> dict:
        return dict(
            class_params="None",
            vertical_displacement='NONE',
            horizontal_displacement="None",
            additional_wg_layers="None",
        )

    def draw_layout(self) -> None:

        first_params = deepcopy(self.class_params[0])

        self.first_array_temp = self.new_template(params=first_params, temp_cls=FilterRingArrayCosine)
        box = self.first_array_temp.bound_box

        self.first_array_inst = self.add_instance(self.first_array_temp, loc=(0, 0), orient='R180')
        if isinstance(self.additional_wg_layers, list):
            for i in range(len(self.additional_wg_layers)):
                params = deepcopy(first_params)
                params['layer'] = self.additional_wg_layers[i]['layer']
                params['input_wg']['width'] = self.additional_wg_layers[i]['width']
                params['output_wg']['width'] = self.additional_wg_layers[i]['width']
                for j in range(len(self.class_params[0]['filters'])):
                    params['filters'][j]['in_gap'] = -(
                        self.additional_wg_layers[i]['width'] / 2 - first_params['filters'][j]['in_gap'] -
                        first_params['input_wg']['width'] / 2)

                    params['filters'][j]['out_gap'] = -(
                        self.additional_wg_layers[i]['width'] / 2 - first_params['filters'][j]['out_gap'] -
                        first_params['output_wg']['width'] / 2)
                temp = self.new_template(params=params, temp_cls=FilterRingArrayCosine)
                master = self.add_instance(temp, loc=(0, 0), orient='R180')

        second_params = deepcopy(self.class_params[1])

        a = self.first_array_inst._photonic_port_list['right_down_1'].center[1]
        x_cord = -(box.right + self.horizontal_displacement + self.class_params[0]['input_wg']['width'])
        y_cord = a + self.vertical_displacement - self.class_params[1]['input_length'] - self.class_params[1][
            'input_bend_size'] \
                 + self.class_params[1]['input_wg']['width']
        self.second_array_temp = self.new_template(params=second_params, temp_cls=FilterRingArrayCosine)
        self.second_array_inst = self.add_instance(self.second_array_temp, loc=(x_cord, y_cord), orient='R0')

        if isinstance(self.additional_wg_layers, list):
            for i in range(len(self.additional_wg_layers)):
                params2 = deepcopy(second_params)
                params2['layer'] = self.additional_wg_layers[i]['layer']
                params2['input_wg']['width'] = self.additional_wg_layers[i]['width']
                params2['output_wg']['width'] = self.additional_wg_layers[i]['width']
                for j in range(len(self.class_params[0]['filters'])):
                    params2['filters'][j]['in_gap'] = -(
                        self.additional_wg_layers[i]['width'] / 2 - second_params['filters'][j]['in_gap'] -
                        second_params['input_wg']['width'] / 2)

                    params2['filters'][j]['out_gap'] = -(
                        self.additional_wg_layers[i]['width'] / 2 - second_params['filters'][j]['out_gap'] -
                        second_params['output_wg']['width'] / 2)
                temp = self.new_template(params=params2, temp_cls=FilterRingArrayCosine)
                master = self.add_instance(temp, loc=(x_cord, y_cord), orient='R0')

        self.extract_ports()

    def extract_ports(self):
        # Extracting ports from lower ring array
        self.extract_photonic_ports(
            inst=self.first_array_inst,
            port_names=['PORT_IN', 'PORT_OUT'],
            port_renaming={'PORT_IN': 'PORT_IN_LOWER', 'PORT_OUT': 'PORT_OUT_LOWER'},
            show=False)

        for port_name, port in self.first_array_inst._photonic_port_list.items():
            if 'FILTER' in port_name:
                self.extract_photonic_ports(
                    inst=self.first_array_inst,
                    port_names=[port_name],
                    port_renaming={port_name: '{}_LOWER'.format(port_name)},
                    show=False)

        # Extracting ports from upper ring array
        self.extract_photonic_ports(
            inst=self.second_array_inst,
            port_names=['PORT_IN', 'PORT_OUT'],
            port_renaming={'PORT_IN': 'PORT_IN_UPPER', 'PORT_OUT': 'PORT_OUT_UPPER'},
            show=False)

        for port_name, port in self.second_array_inst._photonic_port_list.items():
            if 'FILTER' in port_name:
                self.extract_photonic_ports(
                    inst=self.second_array_inst,
                    port_names=[port_name],
                    port_renaming={port_name: '{}_UPPER'.format(port_name)},
                    show=False)

class FilterArray_size2(BPG.PhotonicTemplateBase):
    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)
        self.params = deepcopy(params)
        self.class_params = params['class_params']
        self.vertical_displacement = params['vertical_displacement']
        self.horizontal_displacement = params['horizontal_displacement']
        try:
            self.additional_wg_layers = params['additional_wg_layers']
        except:
            self.additional_wg_layers = random.randint(1, 1331)

        self.first_array_temp = None
        self.first_array_inst = None
        self.second_array_temp = None
        self.second_array_inst = None

    @classmethod
    def get_default_param_values(cls) -> dict:
        return dict(
            class_params=None,
            vertical_displacement=None,
            horizontal_displacement=None,
            additional_wg_layers=None,
        )

    @classmethod
    def get_params_info(cls) -> dict:
        return dict(
            class_params="None",
            vertical_displacement='NONE',
            horizontal_displacement="None",
            additional_wg_layers="None",
        )

    def draw_layout(self) -> None:

        first_params = deepcopy(self.class_params[0])

        self.first_array_temp = self.new_template(params=first_params, temp_cls=FilterRingArray)
        box = self.first_array_temp.bound_box

        self.first_array_inst = self.add_instance(self.first_array_temp, loc=(0, 0), orient='R180')
        if isinstance(self.additional_wg_layers, list):
            for i in range(len(self.additional_wg_layers)):
                params = deepcopy(first_params)
                params['layer'] = self.additional_wg_layers[i]['layer']
                params['input_wg']['width'] = self.additional_wg_layers[i]['width']
                params['output_wg']['width'] = self.additional_wg_layers[i]['width']
                for j in range(len(self.class_params[0]['filters'])):
                    params['filters'][j]['in_gap'] = -(
                        self.additional_wg_layers[i]['width'] / 2 - first_params['filters'][j]['in_gap'] -
                        first_params['input_wg']['width'] / 2)

                    params['filters'][j]['out_gap'] = -(
                        self.additional_wg_layers[i]['width'] / 2 - first_params['filters'][j]['out_gap'] -
                        first_params['output_wg']['width'] / 2)
                temp = self.new_template(params=params, temp_cls=FilterRingArray)
                master = self.add_instance(temp, loc=(0, 0), orient='R180')

        second_params = deepcopy(self.class_params[1])

        a = self.first_array_inst._photonic_port_list['right_down_1'].center[1]
        x_cord = -(box.right + self.horizontal_displacement + self.class_params[0]['input_wg']['width'])
        y_cord = a + self.vertical_displacement - self.class_params[1]['input_length'] - self.class_params[1][
            'input_bend_size'] \
                 + self.class_params[1]['input_wg']['width']
        self.second_array_temp = self.new_template(params=second_params, temp_cls=FilterRingArray)
        self.second_array_inst = self.add_instance(self.second_array_temp, loc=(x_cord, y_cord), orient='R0')

        if isinstance(self.additional_wg_layers, list):
            for i in range(len(self.additional_wg_layers)):
                params2 = deepcopy(second_params)
                params2['layer'] = self.additional_wg_layers[i]['layer']
                params2['input_wg']['width'] = self.additional_wg_layers[i]['width']
                params2['output_wg']['width'] = self.additional_wg_layers[i]['width']
                for j in range(len(self.class_params[0]['filters'])):
                    params2['filters'][j]['in_gap'] = -(
                        self.additional_wg_layers[i]['width'] / 2 - second_params['filters'][j]['in_gap'] -
                        second_params['input_wg']['width'] / 2)

                    params2['filters'][j]['out_gap'] = -(
                        self.additional_wg_layers[i]['width'] / 2 - second_params['filters'][j]['out_gap'] -
                        second_params['output_wg']['width'] / 2)
                temp = self.new_template(params=params2, temp_cls=FilterRingArray)
                master = self.add_instance(temp, loc=(x_cord, y_cord), orient='R0')

        self.extract_ports()

    def extract_ports(self):
        # Extracting ports from lower ring array
        self.extract_photonic_ports(
            inst=self.first_array_inst,
            port_names=['PORT_IN', 'PORT_OUT'],
            port_renaming={'PORT_IN': 'PORT_IN_LOWER', 'PORT_OUT': 'PORT_OUT_LOWER'},
            show=False)

        for port_name, port in self.first_array_inst._photonic_port_list.items():
            if 'FILTER' in port_name:
                self.extract_photonic_ports(
                    inst=self.first_array_inst,
                    port_names=[port_name],
                    port_renaming={port_name: '{}_LOWER'.format(port_name)},
                    show=False)

        # Extracting ports from upper ring array
        self.extract_photonic_ports(
            inst=self.second_array_inst,
            port_names=['PORT_IN', 'PORT_OUT'],
            port_renaming={'PORT_IN': 'PORT_IN_UPPER', 'PORT_OUT': 'PORT_OUT_UPPER'},
            show=False)

        for port_name, port in self.second_array_inst._photonic_port_list.items():
            if 'FILTER' in port_name:
                self.extract_photonic_ports(
                    inst=self.second_array_inst,
                    port_names=[port_name],
                    port_renaming={port_name: '{}_UPPER'.format(port_name)},
                    show=False)
