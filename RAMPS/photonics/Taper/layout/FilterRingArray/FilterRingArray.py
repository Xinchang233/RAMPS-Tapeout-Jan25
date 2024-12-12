import BPG
from layout.FilterRingBase.FilterRingBase import FilterRingBase
from layout.FilterRingBase.FilterRingBase import FilterRingBaseCosine
from Photonic_Core_Layout.AdiabaticPaths.AdiabaticPaths import AdiabaticPaths
import numpy as np
from copy import deepcopy
import random
"""This class instantiates array of loss/ filter rings. Rings are made out of FilterRingBase.
   
   NOTE: In theory one can instantiate any number of rings, but odd number of rings gives nicer layout.
   
      Parameters
    ----------        
     filters : list
        List of parameters that describe ring with two wg's on the side: r_out, width, in_gap, out_gap
     port_layer : tuple
        Layer where port will be specified
     layer : tuple
        Layer where entire layout will be specified
     input_bend_size : float
        Size of the input bend that determines curvature of the 90deg bend. input_bend_size ~ bend radius * 1.8 
     size_out : float
        Size of the output bend that determines curvature of the 90deg bend. output_bend_size ~ bend radius * 1.8 
     input_wg : list
        List of parameters that describe input wg: [width, length]. Length might be deprecated 
     output_wg= : list
        List of parameters that describe output wg: [width, length]. Length might be deprecated
     spacing= : float
        Spacing between ring centers
     total_size : float
        Total (vertical) size of the layout. If above parameters give structure which has height smaller than
        total_size, straight wg will be placed to make up the height. However, if layout's size is bigger than
        total_size, error will be raised
     input_length : float
        The length of straight part of input wg. This parameter and total_size offer full control over sizes
        of different parts of layout
     additional_layers : list
        This parameter offers a way to place doping layers over rings AND rings only.
        List contains the following parameter:
            layer: tuple
            width: float or list
            r_out: float or list or None. When r_out is not specified, doping additional ring will be placed
                         over primary ring with respect to the middle line of the ring (r_out - width/2)                 
"""

class FilterRingArray(BPG.PhotonicTemplateBase):
    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)
        self.params = deepcopy(params)
        self.layer = self.params['layer']
        self.port_layer = self.params['port_layer']
        self.input_wg = self.params['input_wg']
        self.output_wg = self.params['output_wg']
        self.center = (0, 0)
        self.height = 0
        self.in_width = self.input_wg['width']
        self.out_width = self.output_wg['width']
        self.input_bend_size = self.params['input_bend_size']
        self.size_out = self.params['size_out']
        self.filters = self.params['filters']
        self.spacing = self.params['spacing']
        self.total_size = self.params['total_size']
        self.input_length = self.params['input_length']

        self.in_wg_temp = None
        self.in_wg_inst = None

        self.input_wg_temp = None
        self.input_wg_inst = None

        self.Filters_temp = {i: "" for i in range(len(self.filters))}
        self.Filters_inst = {i: "" for i in range(len(self.filters))}

        self.arcs_temp = {i: "" for i in range(2 * len(self.filters))}
        self.arcs_inst = {i: "" for i in range(2 * len(self.filters))}

        self._90_temp = None
        self._90_inst = None

        self.offset_temp = None
        self.offset_inst = None
        try:
            self.additional_layers = self.params['additional_layers']
        except:
            self.additional_layers = random.randint(1, 1331)

    @classmethod
    def get_default_param_values(cls) -> dict:
        return dict(
            filters=None,
            port_layer=None,
            layer=None,
            input_bend_size=None,
            size_out=None,
            input_wg=None,
            output_wg=None,
            spacing=None,
            total_size=None,
            input_length=None,
            additional_layers=None,

        )

    @classmethod
    def get_params_info(cls) -> dict:
        return dict(
            filters="List of parameters that describe ring with two wg's on the side: r_out, width, in_gap, out_gap",
            port_layer='Layer where port will be specified',
            layer="Layer where entire layout will be specified",
            input_bend_size="Size of the input bend that determines curvature of the 90deg bend. input_bend_size ~ bend radius * 1.8 ",
            size_out="Size of the output bend that determines curvature of the 90deg bend. output_bend_size ~ bend radius * 1.8 ",
            input_wg="List of parameters that describe input wg: [width, length]. Length might be deprecated",
            output_wg="List of parameters that describe output wg: [width, length]. Length might be deprecated",
            spacing="Spacing between ring centers",
            total_size='The length of straight part of input wg. This parameter and total_size offer full control over sizes of different parts of layout',
            input_length='The length of straight part of input wg. This parameter and total_size offer full control over sizesof different parts of layout',
            additional_layers="""List contains the following parameter:
            layer: tuple
            width: float or list
            r_out: float or list or None. When r_out is not specified, doping additional ring will be placed
                         over primary ring with respect to the middle line of the ring (r_out - width/2) """

        )

    def draw_layout(self) -> None:
        input_wg_params = dict(layer=self.layer, port_layer=self.port_layer, merge_arcs=False)
        arc_params = [dict(arc_type="straight_wg", width=self.out_width, length=self.input_length)]
        input_wg_params['arc_params'] = arc_params

        self.in_wg_temp = self.new_template(params=input_wg_params, temp_cls=AdiabaticPaths)
        self.in_wg_inst = self.add_instance(self.in_wg_temp, loc=(0, 0), orient='R90', angle=0)

        self.extract_photonic_ports(
            inst=self.in_wg_inst,
            port_names=['PORT_IN'],
            show=False)

        arc_params = [dict(arc_type="90_bend", size=self.input_bend_size, turn_left=False, width=self.in_width)]
        input_wg_params['arc_params'] = arc_params
        self.input_wg_temp = self.new_template(params=input_wg_params, temp_cls=AdiabaticPaths)
        self.input_wg_inst = self.add_instance_port_to_port(inst_master=self.input_wg_temp,
                                                            instance_port_name='PORT_IN',
                                                            self_port=self.in_wg_inst['PORT_OUT'],
                                                            reflect=False)

        self.place_filters()
        self.place_arcs()
        self.place_height_compensators()
        self.place_input_wg_terminator()

    def place_input_wg_terminator(self):

        end_coordinates = self.Filters_inst[len(self.Filters_inst) - 1]._photonic_port_list[
            'right_down'].center  # 137, 10
        last_arc_cords = self.arcs_inst[len(self.arcs_inst) / 2 - 1]._photonic_port_list['PORT_OUT'].center

        if isinstance(self.additional_layers, list):  # and 'IM' in self.additional_layers[0]:
            a = end_coordinates[0] + self.size_out - last_arc_cords[0]
            b = self.spacing

        if end_coordinates[0] + self.size_out - last_arc_cords[0] < self.spacing:
            size = self.spacing - (end_coordinates[0] - last_arc_cords[0])
            bend_params = dict(layer=self.layer, port_layer=self.port_layer,  merge_arcs=False)
            arc_90_params = [dict(arc_type="90_bend", size=size, turn_left=True, width=self.in_width)]
            bend_params['arc_params'] = arc_90_params

            self._90_temp = self.new_template(params=bend_params, temp_cls=AdiabaticPaths)
            self._90_inst = self.add_instance_port_to_port(inst_master=self._90_temp,
                                                           instance_port_name='PORT_IN',
                                                           self_port=self.Filters_inst[len(self.filters) - 1][
                                                               'right_down'],
                                                           reflect=False)

            # Placing height compensator to output waveguide
            height = self._90_inst._photonic_port_list['PORT_OUT'].center[1]

            if self.total_size > height:
                arc_params = [dict(arc_type="straight_wg", width=self.out_width, length=self.total_size - height)]
                wg_params = dict(layer=self.layer, port_layer=self.port_layer, x_start=0.0, y_start=0.0,
                                 angle_start=0.0, radius_threshold=1.5, curvature_rate_threshold=0.7,
                                 merge_arcs=False,
                                 show_plot=False, show_plot_labels=False)
                wg_params['arc_params'] = arc_params
                wg_temp = self.new_template(params=wg_params, temp_cls=AdiabaticPaths)
                wg_inst = self.add_instance_port_to_port(inst_master=wg_temp,
                                                         instance_port_name='PORT_IN',
                                                         self_port=self._90_inst['PORT_OUT'],
                                                         reflect=False)
                self.extract_photonic_ports(
                    inst=wg_inst,
                    port_names=['PORT_OUT'],
                    show=False, )
            else:
                self.extract_photonic_ports(
                    inst=self._90_inst,
                    port_names=['PORT_OUT'],
                    show=False, )

        else:
            bend_params = dict(layer=self.layer, port_layer=self.port_layer, x_start=0.0, y_start=0.0,
                               angle_start=0.0, radius_threshold=1.5, curvature_rate_threshold=0.7, merge_arcs=False,
                               show_plot=False, show_plot_labels=False)
            arc_90_params = [dict(arc_type="90_bend", size=self.size_out, turn_left=True, width=self.in_width)]
            bend_params['arc_params'] = arc_90_params

            self._90_temp = self.new_template(params=bend_params, temp_cls=AdiabaticPaths)
            self._90_inst = self.add_instance_port_to_port(inst_master=self._90_temp,
                                                           instance_port_name='PORT_IN',
                                                           self_port=self.Filters_inst[len(self.filters) - 1][
                                                               'right_down'],
                                                           reflect=False)
            offset = self.spacing - (end_coordinates[0] + self.size_out - last_arc_cords[0])

            offset_params = dict(layer=self.layer, port_layer=self.port_layer,  merge_arcs=False,)
            arc_offset_params = [dict(arc_type="offset_bend", offset=offset, rmin=self.size_out/1.7, width=self.in_width)]
            offset_params['arc_params'] = arc_offset_params
            self.offset_temp = self.new_template(params=offset_params, temp_cls=AdiabaticPaths)
            self.offset_inst = self.add_instance_port_to_port(inst_master=self.offset_temp,
                                                              instance_port_name='PORT_IN',
                                                              self_port=self._90_inst['PORT_OUT'],
                                                              reflect=False)

            # Placing height compensator to output waveguide
            height = self.offset_inst._photonic_port_list['PORT_OUT'].center[1]
            if self.total_size > height:
                arc_params = [dict(arc_type="straight_wg", width=self.out_width, length=self.total_size - height)]
                offset_params['arc_params'] = arc_params
                wg_temp = self.new_template(params=offset_params, temp_cls=AdiabaticPaths)
                wg_inst = self.add_instance_port_to_port(inst_master=wg_temp,
                                                         instance_port_name='PORT_IN',
                                                         self_port=self.offset_inst['PORT_OUT'],
                                                         reflect=False)
                self.extract_photonic_ports(
                    inst=wg_inst,
                    port_names=['PORT_OUT'],
                    show=False, )
            else:
                self.extract_photonic_ports(
                    inst=self.offset_inst,
                    port_names=['PORT_OUT'],
                    show=False, )

    def place_height_compensators(self):
        heights = self.find_heights()
        max_height = self.total_size
        dummy_list = [i for i in heights if i > max_height]
        if len(dummy_list) > 0:
            raise ValueError('Too small value for total_size was specified. Max height is {}'.format(max(heights)))
        input_wg_params = dict(layer=self.layer, port_layer=self.port_layer, x_start=0.0, y_start=0.0,
                               angle_start=0.0, radius_threshold=1.5, curvature_rate_threshold=0.7, merge_arcs=False,
                               show_plot=False, show_plot_labels=False)

        for i in range(len(self.filters)):
            # must be range of filters and not arcs, since there are twice as many arcs as there are filters
            if heights[i] < max_height:
                arc_params = [dict(arc_type="straight_wg", width=self.out_width, length=max_height - heights[i])]
                input_wg_params['arc_params'] = arc_params
                wg_temp = self.input_wg_temp = self.new_template(params=input_wg_params, temp_cls=AdiabaticPaths)
                wg_inst = self.add_instance_port_to_port(inst_master=wg_temp,
                                                         instance_port_name='PORT_IN',
                                                         self_port=self.arcs_inst[i]['PORT_OUT'],
                                                         reflect=False)
                self.extract_photonic_ports(
                    inst=wg_inst,
                    port_names=['PORT_OUT'],
                    port_renaming={'PORT_OUT': 'FILTER_{}'.format(i)},
                    show=False, )
            else:
                self.extract_photonic_ports(
                    inst=self.arcs_inst[i],
                    port_names=['PORT_OUT'],
                    port_renaming={'PORT_OUT': 'FILTER_{}'.format(i)},
                    show=False, )

    def place_filters(self):
        i = 0
        for filter in self.filters:
            if i == 0:
                l = self.output_wg['length']
            elif i == 1:
                l = self.spacing * 2 - self.output_wg['length']
            else:
                l = 2 * self.spacing - l

            try:  # The error that breaks the code is non existance of self.params['additional_layers']
                a = self.params['additional_layers']  # breaker

                flag = True
                for add_lay in a:
                    if isinstance(add_lay['width'], list) or (
                                    'r_out' in add_lay.keys() and isinstance(add_lay['r_out'], list)):
                        flag = False
                        break

                if flag:
                    params2 = dict(layer=self.layer,
                                   port_layer=self.port_layer,
                                   additional_layers=self.params['additional_layers'],  # sec_copy
                                   radius=filter['r_out'],
                                   ring_width=filter['width'],
                                   input_wg=dict(length=l, width=self.in_width, gap=filter['in_gap']),
                                   place_output_wg=True,
                                   output_wg=dict(length=self.output_wg['length'], width=self.out_width,
                                                  gap=filter['out_gap']))
                else:
                    add_layers = []
                    for j in range(len(a)):
                        if isinstance(a[j]['width'], list) and (
                                        'r_out' in a[j].keys() and isinstance(a[j]['r_out'], list)):
                            assert len(a[j]['width']) == len(a[j]['r_out']) == 5, "width and r_out have to be pf the same length"

                            D = dict(layer= a[j]['layer'], r_out=a[j]['r_out'][i], width=a[j]['width'][i])
                        elif isinstance(a[j]['width'], list):
                            assert len(a[j]['width']) == 5, "When width is a list it must contain 5 elements"
                            D = dict(layer=a[j]['layer'], r_out=a[j]['r_out'], width=a[j]['width'][i])
                        elif 'r_out' in a[j].keys() and isinstance(a[j]['r_out'], list):
                            assert len(a[j]['r_out']) == 5, "When width is a list it must contain 5 elements"
                            D = dict(layer=a[j]['layer'], r_out=a[j]['r_out'][i], width=a[j]['width'])
                        else:
                            D = dict(layer=a[j]['layer'], r_out=a[j]['r_out'], width=a[j]['width'])

                        add_layers.append(D)

                    params2 = dict(layer=self.layer,
                                   port_layer=self.port_layer,
                                   additional_layers=add_layers,
                                   radius=filter['r_out'],
                                   ring_width=filter['width'],
                                   input_wg=dict(length=l, width=self.in_width, gap=filter['in_gap']),
                                   place_output_wg=True,
                                   output_wg=dict(length=self.output_wg['length'], width=self.out_width,
                                                  gap=filter['out_gap']))



           # Now that all add_layers which have r_out and width as lists are located
           # create all possible combinations of the dicts and pass them as additional layers param"""

            except:
                params2 = dict(layer=self.layer,
                               port_layer=self.port_layer,
                               radius=filter['r_out'],
                               ring_width=filter['width'],
                               input_wg=dict(length=l, width=self.in_width, gap=filter['in_gap']),
                               place_output_wg=True,
                               output_wg=dict(length=self.output_wg['length'], width=self.out_width,
                                              gap=filter['out_gap']))

            self.Filters_temp[i] = self.new_template(params=params2, temp_cls=FilterRingBase)
            if i == 0:
                port = self.input_wg_inst['PORT_OUT']
            else:
                port = self.Filters_inst[i - 1]['right_down']
            self.Filters_inst[i] = self.add_instance_port_to_port(inst_master=self.Filters_temp[i],
                                                                  instance_port_name='left_down',
                                                                  self_port=port,
                                                                  reflect=False)
            self.extract_photonic_ports(
                inst=self.Filters_inst[i],
                port_names=['right_down'],
                port_renaming={'rigth_down': 'right_down{}'.format(i)},
                show=False, )
            i += 1

    def place_arcs(self):
        l = len(self.filters)
        for i in range(len(self.filters)):
            input_params = dict(layer=self.layer, port_layer=self.port_layer, merge_arcs=False)
            arc_params = [dict(arc_type="90_bend", size=self.input_bend_size, turn_left=False, width=self.out_width)]
            input_params['arc_params'] = arc_params

            self.arcs_temp[i] = self.new_template(params=input_params, temp_cls=AdiabaticPaths)
            self.arcs_inst[i] = self.add_instance_port_to_port(inst_master=self.arcs_temp[i],
                                                               instance_port_name='PORT_IN',
                                                               self_port=self.Filters_inst[i]['left_up'],
                                                               reflect=False)

            input_params = dict(layer=self.layer, port_layer=self.port_layer, merge_arcs=False)
            arc_params = [dict(arc_type="arbitrary_arc", angle=[0, np.pi / 8, np.pi / 4], curvature=[0, -1 / 4, 0],
                               width=[self.out_width, self.out_width / 2, 0.1])]
            input_params['arc_params'] = arc_params
            self.arcs_temp[i + l] = self.new_template(params=input_params, temp_cls=AdiabaticPaths)
            self.arcs_inst[i + l] = self.add_instance_port_to_port(inst_master=self.arcs_temp[i + l],
                                                                   instance_port_name='PORT_IN',
                                                                   self_port=self.Filters_inst[i]['right_up'],
                                                                   reflect=False)
            # Hack used to remove wg terminators

            # if self.out_width > 5.4:
            #     width = [self.out_width, self.out_width / 2, 0.2]
            #     arc_params = [dict(arc_type="arbitrary_arc", angle=[0, np.pi / 8, np.pi / 4], curvature=[0, -1 / 4, 0],
            #                        width=width)]
            #     input_params['arc_params'] = arc_params
            #
            #     self.arcs_temp[i + l] = self.new_template(params=input_params, temp_cls=AdiabaticPaths)
            #     self.arcs_inst[i + l] = self.add_instance_port_to_port(inst_master=self.arcs_temp[i + l],
            #                                                            instance_port_name='PORT_IN',
            #                                                            self_port=self.Filters_inst[i]['right_up'],
            #                                                            reflect=False)
            # else:
            #     width = [self.out_width, 0.275, 0.2]



    def find_heights(self):
        L = []
        for i in range(
                len(self.filters)):  # Must be self.filters because there are twice as many arcs as there are filter
            # And we only want the height of the first half of arcs since those are the ones
            # that are output arcs
            f = self.arcs_inst[i]._photonic_port_list['PORT_OUT'].center[1]
            L.append(f)
        return L

class FilterRingArrayCosine(BPG.PhotonicTemplateBase):
    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)
        self.params = deepcopy(params)
        self.layer = self.params['layer']
        self.port_layer = self.params['port_layer']
        self.input_wg = self.params['input_wg']
        self.output_wg = self.params['output_wg']
        self.center = (0, 0)
        self.height = 0
        self.in_width = self.input_wg['width']
        self.out_width = self.output_wg['width']
        self.input_bend_size = self.params['input_bend_size']
        self.size_out = self.params['size_out']
        self.filters = self.params['filters']
        self.spacing = self.params['spacing']
        self.total_size = self.params['total_size']
        self.input_length = self.params['input_length']

        self.in_wg_temp = None
        self.in_wg_inst = None

        self.input_wg_temp = None
        self.input_wg_inst = None

        self.Filters_temp = {i: "" for i in range(len(self.filters))}
        self.Filters_inst = {i: "" for i in range(len(self.filters))}

        self.period_wg = {i: "" for i in range(len(self.filters))}
        self.period_wg_inst = {i: "" for i in range(len(self.filters))}

        self.arcs_temp = {i: "" for i in range(2 * len(self.filters))}
        self.arcs_inst = {i: "" for i in range(2 * len(self.filters))}

        self._90_temp = None
        self._90_inst = None

        self.offset_temp = None
        self.offset_inst = None
        try:
            self.additional_layers = self.params['additional_layers']
        except:
            self.additional_layers = random.randint(1, 1331)

    @classmethod
    def get_default_param_values(cls) -> dict:
        return dict(
            filters=None,
            port_layer=None,
            layer=None,
            input_bend_size=None,
            size_out=None,
            input_wg=None,
            output_wg=None,
            spacing=None,
            total_size=None,
            input_length=None,
            additional_layers=None,

        )

    @classmethod
    def get_params_info(cls) -> dict:
        return dict(
            filters="List of parameters that describe ring with two wg's on the side: r_out, width, in_gap, out_gap",
            port_layer='Layer where port will be specified',
            layer="Layer where entire layout will be specified",
            input_bend_size="Size of the input bend that determines curvature of the 90deg bend. input_bend_size ~ bend radius * 1.8 ",
            size_out="Size of the output bend that determines curvature of the 90deg bend. output_bend_size ~ bend radius * 1.8 ",
            input_wg="List of parameters that describe input wg: [width, length]. Length might be deprecated",
            output_wg="List of parameters that describe output wg: [width, length]. Length might be deprecated",
            spacing="Spacing between ring centers",
            total_size='The length of straight part of input wg. This parameter and total_size offer full control over sizes of different parts of layout',
            input_length='The length of straight part of input wg. This parameter and total_size offer full control over sizesof different parts of layout',
            additional_layers="""List contains the following parameter:
            layer: tuple
            width: float or list
            r_out: float or list or None. When r_out is not specified, doping additional ring will be placed
                         over primary ring with respect to the middle line of the ring (r_out - width/2) """

        )

    def draw_layout(self) -> None:
        input_wg_params = dict(layer=self.layer, port_layer=self.port_layer, merge_arcs=False)
        arc_params = [dict(arc_type="straight_wg", width=self.out_width, length=self.input_length)]
        input_wg_params['arc_params'] = arc_params

        self.in_wg_temp = self.new_template(params=input_wg_params, temp_cls=AdiabaticPaths)
        self.in_wg_inst = self.add_instance(self.in_wg_temp, loc=(0, 0), orient='R90', angle=0)

        self.extract_photonic_ports(
            inst=self.in_wg_inst,
            port_names=['PORT_IN'],
            show=False)

        arc_params = [dict(arc_type="90_bend", size=self.input_bend_size, turn_left=False, width=self.in_width)]
        input_wg_params['arc_params'] = arc_params
        self.input_wg_temp = self.new_template(params=input_wg_params, temp_cls=AdiabaticPaths)
        self.input_wg_inst = self.add_instance_port_to_port(inst_master=self.input_wg_temp,
                                                            instance_port_name='PORT_IN',
                                                            self_port=self.in_wg_inst['PORT_OUT'],
                                                            reflect=False)

        self.place_filters()
        self.place_arcs()
        self.place_height_compensators()
        self.place_input_wg_terminator()

    def place_input_wg_terminator(self):

        end_coordinates = self.Filters_inst[len(self.Filters_inst) - 1]._photonic_port_list[
            'right_down'].center  # 137, 10
        last_arc_cords = self.arcs_inst[len(self.arcs_inst) / 2 - 1]._photonic_port_list['PORT_OUT'].center

        if isinstance(self.additional_layers, list):  # and 'IM' in self.additional_layers[0]:
            a = end_coordinates[0] + self.size_out - last_arc_cords[0]
            b = self.spacing

        if end_coordinates[0] + self.size_out - last_arc_cords[0] < self.spacing:
            size = self.spacing - (end_coordinates[0] - last_arc_cords[0])
            bend_params = dict(layer=self.layer, port_layer=self.port_layer,  merge_arcs=False)
            arc_90_params = [dict(arc_type="90_bend", size=size, turn_left=True, width=self.in_width)]
            bend_params['arc_params'] = arc_90_params

            self._90_temp = self.new_template(params=bend_params, temp_cls=AdiabaticPaths)
            self._90_inst = self.add_instance_port_to_port(inst_master=self._90_temp,
                                                           instance_port_name='PORT_IN',
                                                           self_port=self.period_wg_inst[len(self.filters) - 1][
                                                               'PORT_OUT'],
                                                           reflect=False)

            # Placing height compensator to output waveguide
            height = self._90_inst._photonic_port_list['PORT_OUT'].center[1]

            if self.total_size > height:
                arc_params = [dict(arc_type="straight_wg", width=self.out_width, length=self.total_size - height)]
                wg_params = dict(layer=self.layer, port_layer=self.port_layer, x_start=0.0, y_start=0.0,
                                 angle_start=0.0, radius_threshold=1.5, curvature_rate_threshold=0.7,
                                 merge_arcs=False,
                                 show_plot=False, show_plot_labels=False)
                wg_params['arc_params'] = arc_params
                wg_temp = self.new_template(params=wg_params, temp_cls=AdiabaticPaths)
                wg_inst = self.add_instance_port_to_port(inst_master=wg_temp,
                                                         instance_port_name='PORT_IN',
                                                         self_port=self._90_inst['PORT_OUT'],
                                                         reflect=False)
                self.extract_photonic_ports(
                    inst=wg_inst,
                    port_names=['PORT_OUT'],
                    show=False, )
            else:
                self.extract_photonic_ports(
                    inst=self._90_inst,
                    port_names=['PORT_OUT'],
                    show=False, )

        else:
            bend_params = dict(layer=self.layer, port_layer=self.port_layer, x_start=0.0, y_start=0.0,
                               angle_start=0.0, radius_threshold=1.5, curvature_rate_threshold=0.7, merge_arcs=False,
                               show_plot=False, show_plot_labels=False)
            arc_90_params = [dict(arc_type="90_bend", size=self.size_out, turn_left=True, width=self.in_width)]
            bend_params['arc_params'] = arc_90_params

            self._90_temp = self.new_template(params=bend_params, temp_cls=AdiabaticPaths)
            self._90_inst = self.add_instance_port_to_port(inst_master=self._90_temp,
                                                           instance_port_name='PORT_IN',
                                                           self_port=self.period_wg_inst[len(self.filters) - 1][
                                                               'PORT_OUT'],
                                                           reflect=False)
            offset = self.spacing - (end_coordinates[0] + self.size_out - last_arc_cords[0])

            offset_params = dict(layer=self.layer, port_layer=self.port_layer,  merge_arcs=False,)
            arc_offset_params = [dict(arc_type="offset_bend", offset=offset, rmin=self.size_out/1.7, width=self.in_width)]
            offset_params['arc_params'] = arc_offset_params
            self.offset_temp = self.new_template(params=offset_params, temp_cls=AdiabaticPaths)
            self.offset_inst = self.add_instance_port_to_port(inst_master=self.offset_temp,
                                                              instance_port_name='PORT_IN',
                                                              self_port=self._90_inst['PORT_OUT'],
                                                              reflect=False)

            # Placing height compensator to output waveguide
            height = self.offset_inst._photonic_port_list['PORT_OUT'].center[1]
            if self.total_size > height:
                arc_params = [dict(arc_type="straight_wg", width=self.out_width, length=self.total_size - height)]
                offset_params['arc_params'] = arc_params
                wg_temp = self.new_template(params=offset_params, temp_cls=AdiabaticPaths)
                wg_inst = self.add_instance_port_to_port(inst_master=wg_temp,
                                                         instance_port_name='PORT_IN',
                                                         self_port=self.offset_inst['PORT_OUT'],
                                                         reflect=False)
                self.extract_photonic_ports(
                    inst=wg_inst,
                    port_names=['PORT_OUT'],
                    show=False, )
            else:
                self.extract_photonic_ports(
                    inst=self.offset_inst,
                    port_names=['PORT_OUT'],
                    show=False, )

    def place_height_compensators(self):
        heights = self.find_heights()
        max_height = self.total_size
        dummy_list = [i for i in heights if i > max_height]
        if len(dummy_list) > 0:
            raise ValueError('Too small value for total_size was specified. Max height is {}'.format(max(heights)))
        input_wg_params = dict(layer=self.layer, port_layer=self.port_layer, x_start=0.0, y_start=0.0,
                               angle_start=0.0, radius_threshold=1.5, curvature_rate_threshold=0.7, merge_arcs=False,
                               show_plot=False, show_plot_labels=False)

        for i in range(len(self.filters)):
            # must be range of filters and not arcs, since there are twice as many arcs as there are filters
            if heights[i] < max_height:
                arc_params = [dict(arc_type="straight_wg", width=self.out_width, length=max_height - heights[i])]
                input_wg_params['arc_params'] = arc_params
                wg_temp = self.input_wg_temp = self.new_template(params=input_wg_params, temp_cls=AdiabaticPaths)
                wg_inst = self.add_instance_port_to_port(inst_master=wg_temp,
                                                         instance_port_name='PORT_IN',
                                                         self_port=self.arcs_inst[i]['PORT_OUT'],
                                                         reflect=False)
                self.extract_photonic_ports(
                    inst=wg_inst,
                    port_names=['PORT_OUT'],
                    port_renaming={'PORT_OUT': 'FILTER_{}'.format(i)},
                    show=False, )
            else:
                self.extract_photonic_ports(
                    inst=self.arcs_inst[i],
                    port_names=['PORT_OUT'],
                    port_renaming={'PORT_OUT': 'FILTER_{}'.format(i)},
                    show=False, )

    def place_filters(self):
        i = 0
        for filter in self.filters:
            if i == 0:
                l = self.output_wg['length']
            elif i == 1:
                l = self.spacing * 2 - self.output_wg['length']
            else:
                l = 2 * self.spacing - l

            try:  # The error that breaks the code is non existance of self.params['additional_layers']
                a = self.params['additional_layers']  # breaker

                flag = True
                for add_lay in a:
                    if isinstance(add_lay['width'], list) or (
                                    'r_out' in add_lay.keys() and isinstance(add_lay['r_out'], list)):
                        flag = False
                        break

                if flag:
                    params2 = dict(layer=self.layer,
                                   port_layer=self.port_layer,
                                   additional_layers=self.params['additional_layers'],  # sec_copy
                                   radius=filter['r_out'],
                                   ring_width=filter['width'],
                                   input_wg=dict(length=l, width=self.in_width, gap=filter['in_gap']),
                                   place_output_wg=True,
                                   output_wg=dict(length=self.output_wg['length'], width=self.out_width,
                                                  gap=filter['out_gap']))
                else:
                    add_layers = []
                    for j in range(len(a)):
                        if isinstance(a[j]['width'], list) and (
                                        'r_out' in a[j].keys() and isinstance(a[j]['r_out'], list)):
                            assert len(a[j]['width']) == len(a[j]['r_out']) == 5, "width and r_out have to be pf the same length"

                            D = dict(layer= a[j]['layer'], r_out=a[j]['r_out'][i], width=a[j]['width'][i])
                        elif isinstance(a[j]['width'], list):
                            assert len(a[j]['width']) == 5, "When width is a list it must contain 5 elements"
                            D = dict(layer=a[j]['layer'], r_out=a[j]['r_out'], width=a[j]['width'][i])
                        elif 'r_out' in a[j].keys() and isinstance(a[j]['r_out'], list):
                            assert len(a[j]['r_out']) == 5, "When width is a list it must contain 5 elements"
                            D = dict(layer=a[j]['layer'], r_out=a[j]['r_out'][i], width=a[j]['width'])
                        else:
                            D = dict(layer=a[j]['layer'], r_out=a[j]['r_out'], width=a[j]['width'])

                        add_layers.append(D)

                    params2 = dict(layer=self.layer,
                                   port_layer=self.port_layer,
                                   additional_layers=add_layers,
                                   radius=filter['r_out'],
                                   ring_width=filter['width'],
                                   input_wg=dict(length=l, width=self.in_width, gap=filter['in_gap']),
                                   place_output_wg=True,
                                   output_wg=dict(length=self.output_wg['length'], width=self.out_width,
                                                  gap=filter['out_gap']))



           # Now that all add_layers which have r_out and width as lists are located
           # create all possible combinations of the dicts and pass them as additional layers param"""

            except:
                params2 = dict(layer=self.layer,
                               port_layer=self.port_layer,
                               radius=filter['r_out'],
                               ring_width=filter['width'],
                               input_wg=dict(length=l, width=self.in_width, gap=filter['in_gap']),
                               place_output_wg=True,
                               output_wg=dict(length=self.output_wg['length'], width=self.out_width,
                                              gap=filter['out_gap']))

            self.Filters_temp[i] = self.new_template(params=params2, temp_cls=FilterRingBaseCosine)

            params_period = dict(layer=self.layer, port_layer=self.port_layer,merge_arcs=False)
            params_period['arc_params'] = [
                dict(arc_type="straight_wg", width=self.in_width, length=self.spacing,)
            ]

            self.period_wg[i] = self.new_template(params= params_period, temp_cls = AdiabaticPaths)
            if i == 0:
                port = self.input_wg_inst['PORT_OUT']
            else:
                port = self.period_wg_inst[i - 1]['PORT_OUT']
            self.Filters_inst[i] = self.add_instance_port_to_port(inst_master=self.Filters_temp[i],
                                                                  instance_port_name='left_down',
                                                                  self_port=port,
                                                                  reflect=False)
            self.period_wg_inst[i] = self.add_instance_port_to_port(inst_master=self.period_wg[i],
                                                                    instance_port_name='PORT_IN',
                                                                    self_port=self.Filters_inst[i]['right_down'],
                                                                    reflect=False)
            self.extract_photonic_ports(
                inst=self.Filters_inst[i],
                port_names=['right_down'],
                port_renaming={'rigth_down': 'right_down{}'.format(i)},
                show=False, )
            i += 1

    def place_arcs(self):
        l = len(self.filters)
        for i in range(len(self.filters)):
            input_params = dict(layer=self.layer, port_layer=self.port_layer, merge_arcs=False)
            arc_params = [dict(arc_type="90_bend", size=self.input_bend_size, turn_left=False, width=self.out_width)]
            input_params['arc_params'] = arc_params

            self.arcs_temp[i] = self.new_template(params=input_params, temp_cls=AdiabaticPaths)
            self.arcs_inst[i] = self.add_instance_port_to_port(inst_master=self.arcs_temp[i],
                                                               instance_port_name='PORT_IN',
                                                               self_port=self.Filters_inst[i]['left_up'],
                                                               reflect=False)

            input_params = dict(layer=self.layer, port_layer=self.port_layer, merge_arcs=False)
            arc_params = [dict(arc_type="arbitrary_arc", angle=[0, np.pi / 8, np.pi / 4], curvature=[0, -1 / 4, 0],
                               width=[self.out_width, self.out_width / 2, 0.1])]
            input_params['arc_params'] = arc_params
            self.arcs_temp[i + l] = self.new_template(params=input_params, temp_cls=AdiabaticPaths)
            self.arcs_inst[i + l] = self.add_instance_port_to_port(inst_master=self.arcs_temp[i + l],
                                                                   instance_port_name='PORT_IN',
                                                                   self_port=self.Filters_inst[i]['right_up'],
                                                                   reflect=False)
            # Hack used to remove wg terminators

            # if self.out_width > 5.4:
            #     width = [self.out_width, self.out_width / 2, 0.2]
            #     arc_params = [dict(arc_type="arbitrary_arc", angle=[0, np.pi / 8, np.pi / 4], curvature=[0, -1 / 4, 0],
            #                        width=width)]
            #     input_params['arc_params'] = arc_params
            #
            #     self.arcs_temp[i + l] = self.new_template(params=input_params, temp_cls=AdiabaticPaths)
            #     self.arcs_inst[i + l] = self.add_instance_port_to_port(inst_master=self.arcs_temp[i + l],
            #                                                            instance_port_name='PORT_IN',
            #                                                            self_port=self.Filters_inst[i]['right_up'],
            #                                                            reflect=False)
            # else:
            #     width = [self.out_width, 0.275, 0.2]



    def find_heights(self):
        L = []
        for i in range(
                len(self.filters)):  # Must be self.filters because there are twice as many arcs as there are filter
            # And we only want the height of the first half of arcs since those are the ones
            # that are output arcs
            f = self.arcs_inst[i]._photonic_port_list['PORT_OUT'].center[1]
            L.append(f)
        return L
