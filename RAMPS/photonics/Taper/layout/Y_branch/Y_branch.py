import BPG
import importlib
from BPG.objects import PhotonicPolygon
from Photonic_Core_Layout.AdiabaticPaths.AdiabaticPaths import AdiabaticPaths
from numpy import pi
from copy import deepcopy
import numpy as np


class Y_branch(BPG.PhotonicTemplateBase):
    """
    Port names: PORT_IN, PORT_1_OUT, PORT_2_OUT
    """

    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)

        self.input_width = params['input_width']
        self.init_taper_len = params['init_taper_len']
        self.final_taper_len = params['final_taper_len']

        self.w_temp_width = params['w_temp_width']
        self.w_temp_len = params['w_temp_len']
        self.final_width = params['final_width']
        self.branch_width = params['branch_width']
        self.branch_length = params['branch_length']

        self.final_wg_len = params['final_wg_len']
        # self.grating_module = importlib.import_module(self.grating_params['package'])
        # self.grating_cls = getattr(self.grating_module, self.grating_params['class_name'])

        self.layer = params['layer']
        self.port_layer = ['si_full_free', 'port']

        self.spoke_size = params['spoke_size']
        self.num_spokes = params['num_spokes']
        self.add_offset = params['add_offset']
        self.offset = params['offset']
        self.rmin = params['rmin']

        self.add_triangles_boolean = self.params['add_triangles_boolean']
        self.triangle_vertices = self.params['triangle_vertices']

        self.offset_bend_width = self.params['offset_bend_width']

    @classmethod
    def get_params_info(cls):
        return dict(
            grating_params="None",
            input_width="None",
            w_temp_width="None",
            w_temp_len="None",
            final_width="None",
            branch_width="None",
            layer="None",
            init_taper_len="None",
            final_taper_len="None",
            final_wg_len="None",
            branch_length="None",
            spoke_size="None",
            num_spokes="None",
            add_offset="None",
            offset='None',
            rmin = 'None',
            add_triangles_boolean = "None",
            triangle_vertices = "None",
            offset_bend_width = 'None or a number. It is the width at the end of the offset bend'
        )

    @classmethod
    def get_default_param_values(cls):
        return dict(
            grating_params="None",
            input_width="None",
            w_temp_width="None",
            w_temp_len="None",
            final_width="None",
            branch_width="None",
            layer="None",
            init_taper_len="None",
            final_taper_len="None",
            final_wg_len="None",
            branch_length="None",
            spoke_size=0.1,
            num_spokes=3,
            add_offset=True,
            rmin = 5,
            offset = 1,

            add_triangles_boolean = False,
            triangle_vertices = 0,
            offset_bend_width = None
        )

    def draw_layout(self) -> None:
        # Template of adiabatic band parameters
        adiabatic_band_params = dict(layer=self.layer, port_layer=self.port_layer, radius_threshold=1.5,
                                     curvature_rate_threshold=0.7, merge_arcs=False)

        # Declare and instantiate fundamental mode width waveguide that is insertion point of Y branch
        in_wg_params = deepcopy(adiabatic_band_params)
        in_wg_params['arc_params'] = [dict(arc_type="straight_wg", width=self.input_width, length=1)]

        self.input_wg_temp = self.new_template(params=in_wg_params, temp_cls=AdiabaticPaths)
        self.input_wg_inst = self.add_instance(self.input_wg_temp, loc=(0, 0), orient='R0', reflect=False)

        self.extract_photonic_ports(inst=self.input_wg_inst, port_names=['PORT_IN'], show=False)

        # Declare and instantiate first taper that will excite modes 1 and 3 in proper ratio
        taper1_params = deepcopy(adiabatic_band_params)
        taper1_params['arc_params'] = [
            dict(arc_type="straight_wg", width=[self.input_width, self.w_temp_width], length=self.init_taper_len)]
        self.taper1_temp = self.new_template(params=taper1_params, temp_cls=AdiabaticPaths)
        self.taper1_inst = self.add_instance_port_to_port(inst_master=self.taper1_temp,
                                                          instance_port_name='PORT_IN',
                                                          self_port=self.input_wg_inst['PORT_OUT'])

        # Declare and instantiate middle (wider) wg which will propagate modes 1 and 3 until they are put of phase
        wide_wg_params = deepcopy(adiabatic_band_params)
        wide_wg_params['arc_params'] = [
            dict(arc_type="straight_wg", width=self.w_temp_width, length=self.w_temp_len)]
        self.wide_wg_temp = self.new_template(params=wide_wg_params, temp_cls=AdiabaticPaths)
        self.wide_wg_inst = self.add_instance_port_to_port(inst_master=self.wide_wg_temp,
                                                           instance_port_name='PORT_IN',
                                                           self_port=self.taper1_inst['PORT_OUT'])

        # Declare and instantiate second taper which will taper down to final Y branch width
        taper2_params = deepcopy(adiabatic_band_params)
        taper2_params['arc_params'] = [
            dict(arc_type="straight_wg", width=[self.w_temp_width, self.final_width], length=self.final_taper_len)]
        self.taper2_temp = self.new_template(params=taper2_params, temp_cls=AdiabaticPaths)
        self.taper2_inst = self.add_instance_port_to_port(inst_master=self.taper2_temp,
                                                          instance_port_name='PORT_IN',
                                                          self_port=self.wide_wg_inst['PORT_OUT'])

        # Declare and instantiate final wg which will propagate modes 1 and 3 until they are put of phase, before the split
        final_wg_params = deepcopy(adiabatic_band_params)
        final_wg_params['arc_params'] = [
            dict(arc_type="straight_wg", width=self.final_width, length=self.final_wg_len)]
        self.wide_wg_temp = self.new_template(params=final_wg_params, temp_cls=AdiabaticPaths)
        self.wide_wg_inst = self.add_instance_port_to_port(inst_master=self.wide_wg_temp,
                                                           instance_port_name='PORT_IN',
                                                           self_port=self.taper2_inst['PORT_OUT'])
        # compute the coordinates of top right corner of final waveguide to be able to place branches properly
        x_cor_of_final_wg = self.wide_wg_inst.bound_box.right
        y_cor_of_final_wg = self.wide_wg_inst.bound_box.top

        # Declare and instantiate top branch
        top_branch_params = deepcopy(adiabatic_band_params)
        top_branch_params['arc_params'] = [
            dict(arc_type="straight_wg", width=self.branch_width, length=self.branch_length)]
        self.top_branch_temp = self.new_template(params=top_branch_params, temp_cls=AdiabaticPaths)
        self.top_branch_inst = self.add_instance(self.top_branch_temp,
                                                 loc=(x_cor_of_final_wg, y_cor_of_final_wg - self.branch_width / 2),
                                                 orient='R0', reflect=False)

        y = self.top_branch_inst.bound_box.bottom
        self.add_spokes(x=x_cor_of_final_wg, y=y - self.spoke_size / 2, spoke_size=self.spoke_size,
                        num_spokes=self.num_spokes)

        self.bottom_branch_inst = self.add_instance(self.top_branch_temp,
                                                    loc=(x_cor_of_final_wg,
                                                         y_cor_of_final_wg + self.branch_width / 2 - self.final_width),
                                                    orient='R0', reflect=False)

        y = self.bottom_branch_inst.bound_box.top

        self.add_spokes(x=x_cor_of_final_wg, y=y + self.spoke_size / 2, spoke_size=self.spoke_size,
                        num_spokes=self.num_spokes)
        if self.add_triangles_boolean:
            self.add_triangles()

        if self.add_offset:
            self.add_offset_bend()
        else:
            self.extract_photonic_ports(inst=self.top_branch_inst, port_names=['PORT_OUT'],
                                        port_renaming={'PORT_OUT': 'PORT_1_OUT'}, show=False)
            self.extract_photonic_ports(inst=self.bottom_branch_inst, port_names=['PORT_OUT'],
                                        port_renaming={'PORT_OUT': 'PORT_2_OUT'}, show=False)


    def add_triangles(self):
        gap=0.0847*2

        x = self.wide_wg_inst.bound_box.right
        y1 = self.top_branch_inst.bound_box.bottom - np.max(self.triangle_vertices, axis=0)[1]+gap/2
        translation = np.array([x, y1])
        points = translation+np.array(self.triangle_vertices)
        P1 = PhotonicPolygon(resolution=self.grid.resolution, layer=self.layer, points=points)
        self.add_obj(P1)

        #Flip across x axis
        ver = np.array(self.triangle_vertices)
        for point in ver:
            point[1] *= -1
        y2 = self.bottom_branch_inst.bound_box.top + np.max(self.triangle_vertices, axis=0)[1] - gap/2
        translation = np.array([x, y2])
        points = translation + ver
        P2 = PhotonicPolygon(resolution=self.grid.resolution, layer=self.layer, points=points)
        self.add_obj(P2)

    def add_spokes(self, x, y, spoke_size, num_spokes):
        adiabatic_band_params = dict(layer=self.layer, port_layer=self.port_layer, radius_threshold=1.5,
                                     curvature_rate_threshold=0.7, merge_arcs=False)
        adiabatic_band_params['arc_params'] = [
            dict(arc_type="straight_wg", width=spoke_size, length=spoke_size)]

        temp = self.new_template(params=adiabatic_band_params, temp_cls=AdiabaticPaths)
        for i in range(num_spokes):
            self.add_instance(master=temp, loc=(x + 2 * i * spoke_size, y))

    def add_offset_bend(self):
        adiabatic_band_params = dict(layer=self.layer, port_layer=self.port_layer, radius_threshold=1.5,
                                     curvature_rate_threshold=0.7, merge_arcs=False)
        #Determine what is the width profile of the offset bend
        if self.offset_bend_width == None:
            width = self.branch_width
        else:
            width = [self.branch_width, self.offset_bend_width]
        adiabatic_band_params['arc_params'] = [
            dict(arc_type="offset_bend", width=width, offset=self.offset, rmin=self.rmin)]

        temp = self.new_template(params=adiabatic_band_params, temp_cls=AdiabaticPaths)

        inst1 = self.add_instances_port_to_port(inst_master=temp, instance_port_name='PORT_IN',
                                                self_port=self.top_branch_inst['PORT_OUT'], reflect=True)
        inst2 = self.add_instances_port_to_port(inst_master=temp, instance_port_name='PORT_IN',
                                                self_port=self.bottom_branch_inst['PORT_OUT'])

        self.extract_photonic_ports(inst=inst1, port_names=['PORT_OUT'],
                                    port_renaming={'PORT_OUT': 'PORT_1_OUT'}, show=False)
        self.extract_photonic_ports(inst=inst2, port_names=['PORT_OUT'],
                                    port_renaming={'PORT_OUT': 'PORT_2_OUT'}, show=False)