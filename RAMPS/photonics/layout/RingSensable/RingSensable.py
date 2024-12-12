import BPG
import importlib
from layout.Ring.ring import RingBase
from Photonic_Core_Layout.AdiabaticPaths.AdiabaticPaths import AdiabaticPaths
from layout.SimpleRing.SimpleRing import SimpleRing
from layout.RingSensable.RingCapacitor import RingCapacitor
from layout.RingTunable.RingHeater import RingHeater
from Photonic_Core_Layout.ViaStack_test.ViaStack import ViaStack
from bag.layout.util import BBox
from numpy import pi
from math import sqrt
from copy import deepcopy

class RingSensable(BPG.PhotonicTemplateBase):
    """
    Ring with integrated photodiode to sense light in ring--Script class
    """

    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)
        # Hard coded params
        self.ring_loc = (0, 0)
        # Parameters parsed from spec file
        self.spoked_ring_params = self.params["spoked_ring_params"]
        self.heater_params = self.params["heater_params"]
        self.via_stack_params = self.params["via_stack_params"]

        # Master declaration
        self.spoked_ring_master = dict()
        self.heater_master = dict()
        self.via_stack_master = dict()

        # Instances declaration
        self.spoked_ring = dict()
        self.heater = dict()
        self.via_stacks = dict()

    @classmethod
    def get_params_info(cls):
        return dict(
            spoked_ring_params='Parameters for the modulator-like spoked ring',
            heater_params='Parameters for the ring heater',
            via_stack_params='via stacks that connects electrode rings to wires',
            ring_heater_gap='Gap between outer radius of ring and heater',
            label_p = 'name for p contact label',
            label_n = 'name for n contact label',
        )

    @classmethod
    def get_default_param_values(cls):
        return dict(
            spoked_ring_params=None,
            heater_params=None,
            via_stack_params=None,
            ring_heater_gap=1.42,
            label_p = 'P_Contact',
            label_n = 'N_Contact',
            # whatever value you might want to hard-code in the .py file rather than the .yaml file
        )

    def draw_layout(self) -> None:
        self.create_spoked_ring()
        if self.via_stack_params:
            self.create_via_stacks()
        if self.heater_params:
            self.create_heater()

        self.place_spoked_ring()
        if self.heater_params:
            self.place_heater()  # order has to be correct, so place must be after create
        if self.via_stack_params:
            self.place_via_stacks()

    def create_spoked_ring(self):
        spoked_ring_params = deepcopy(self.spoked_ring_params)
        spoked_ring_params['coupling_slot'] = 0
        spoked_ring_params['drop_slot'] = 0
        spoked_ring_params['wg_width'] = 0
        spoked_ring_params['access_length'] = 0
        spoked_ring_params['drop_taper_length'] = 0
        self.spoked_ring_master = self.new_template(params=spoked_ring_params,
                                                                 temp_cls=RingBase)

    def create_via_stacks(self):
        self.via_stack_master = self.new_template(params=self.via_stack_params,
                                                                 temp_cls=ViaStack)

    def create_heater(self):
        # Extract values
        self.heater_params['ring_params']['r_out'] = self.spoked_ring_params['rout'] - \
                                                     self.spoked_ring_params['ring_width'] - \
                                                     self.params['ring_heater_gap']
        self.heater_master = self.new_template(params=self.heater_params,
                                                                 temp_cls=RingHeater)

    def place_spoked_ring(self):
        self.spoked_ring = self.add_instance(self.spoked_ring_master,
                                             loc=self.ring_loc,
                                             orient='R0')
        # Extract the ports
        self.extract_photonic_ports(
            inst=self.spoked_ring,
        )


    def place_heater(self):
        self.heater = self.add_instance(self.heater_master,
                                        loc=self.ring_loc,
                                        orient='R0')

    def place_via_stacks(self):
        silicon_ring_rin = self.spoked_ring_params['rout'] - self.spoked_ring_params['ring_width']
        # p-electrode position
        p_via_radius = silicon_ring_rin - self.spoked_ring_params['p_via_radius_offset']
        p_electrode_rin = p_via_radius + self.spoked_ring_params['electrode_offset']
        p_electrode_rout = p_electrode_rin + self.spoked_ring_params['electrode_width_outer']
        p_electrode_rcenter = (p_electrode_rout + p_electrode_rin)/2
        # n-electrode position
        n_via_radius = silicon_ring_rin - self.spoked_ring_params['n_via_radius_offset']
        n_electrode_rout = n_via_radius - self.spoked_ring_params['electrode_offset']
        n_electrode_rin = n_electrode_rout - self.spoked_ring_params['electrode_width_inner']
        n_electrode_rcenter = (n_electrode_rout+n_electrode_rin)/2

        via_stack_position_p = (p_electrode_rcenter,0)
        via_stack_position_n = (-n_electrode_rcenter,0)
        self.via_stacks['via_stack_p']=self.add_instance(master=self.via_stack_master, loc=via_stack_position_p,
                                                         orient='R0', unit_mode=False)
        self.via_stacks['via_stack_n'] = self.add_instance(master=self.via_stack_master, loc=via_stack_position_n,
                                                           orient='R0',
                                                           unit_mode=False)
        ################################################################################
        # Process the ring electrode layers
        ################################################################################
        self.outer_electrode_ring_layer_inds = []
        self.outer_electrode_ring_layers = self.spoked_ring_params['outer_electrode_ring_layers']
        if not isinstance(self.outer_electrode_ring_layers, list):
            self.outer_electrode_ring_layers = [self.outer_electrode_ring_layers]
        for lpp in self.outer_electrode_ring_layers:
            self.outer_electrode_ring_layer_inds.append(self.grid.tech_info.get_layer_id(lpp[0]))
        self.outer_electrode_ring_layer_inds.sort()

        self.inner_electrode_ring_layer_inds = []
        self.inner_electrode_ring_layers = self.spoked_ring_params['inner_electrode_ring_layers']
        if not isinstance(self.inner_electrode_ring_layers, list):
            self.inner_electrode_ring_layers = [self.inner_electrode_ring_layers]
        for lpp in self.inner_electrode_ring_layers:
            self.inner_electrode_ring_layer_inds.append(self.grid.tech_info.get_layer_id(lpp[0]))
        self.inner_electrode_ring_layer_inds.sort()

        # outer electrode is p, inner electrode is n
        self.p_electrode_layer_ind_list = self.outer_electrode_ring_layer_inds
        self.n_electrode_layer_ind_list = self.inner_electrode_ring_layer_inds

        # p contact label
        bbox = BBox(
            top=self.via_stacks['via_stack_p'].bound_box.top,
            bottom=self.via_stacks['via_stack_p'].bound_box.bottom,
            left=self.via_stacks['via_stack_p'].bound_box.left,
            right=self.via_stacks['via_stack_p'].bound_box.right,
            resolution=self.grid.resolution
        )
        # contact_label_layer = self.grid.tech_info.get_layer_name(max(self.p_electrode_layer_ind_list))
        # self.add_label(label=self.params['label_p'], layer=(contact_label_layer, "label"), bbox=bbox)

        contact_label_layer = self.grid.tech_info.get_layer_name(max(self.p_electrode_layer_ind_list)+1)
        self.add_pin_primitive(net_name=self.params['label_p'], layer=(contact_label_layer, "label"), bbox=bbox)

        # n contact label
        bbox = BBox(
            top=self.via_stacks['via_stack_n'].bound_box.top,
            bottom=self.via_stacks['via_stack_n'].bound_box.bottom,
            left=self.via_stacks['via_stack_n'].bound_box.left,
            right=self.via_stacks['via_stack_n'].bound_box.right,
            resolution=self.grid.resolution
        )
        # contact_label_layer = self.grid.tech_info.get_layer_name(max(self.n_electrode_layer_ind_list))
        # self.add_label(label=self.params['label_n'], layer=(contact_label_layer, "label"), bbox=bbox)

        contact_label_layer = self.grid.tech_info.get_layer_name(max(self.n_electrode_layer_ind_list)+1)
        self.add_pin_primitive(net_name=self.params['label_n'], layer=(contact_label_layer, "label"), bbox=bbox)

class RingSensableWithCosine(BPG.PhotonicTemplateBase):
    """
    Ring with integrated photodiode to sense light in ring--Script class
    """

    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)
        # Hard coded params
        self.ring_loc = (0, 0)
        # Parameters parsed from spec file
        self.spoked_ring_params = self.params["spoked_ring_params"]
        self.heater_params = self.params["heater_params"]
        self.via_stack_params = self.params["via_stack_params"]

        # Master declaration
        self.spoked_ring_master = dict()
        self.heater_master = dict()
        self.via_stack_master = dict()

        # Instances declaration
        self.spoked_ring = dict()
        self.heater = dict()
        self.via_stacks = dict()

    @classmethod
    def get_params_info(cls):
        return dict(
            spoked_ring_params='Parameters for the modulator-like spoked ring',
            heater_params='Parameters for the ring heater',
            via_stack_params='via stacks that connects electrode rings to wires',
            ring_heater_gap='Gap between outer radius of ring and heater',
            label_p='name for p contact label',
            label_n='name for n contact label',
        )

    @classmethod
    def get_default_param_values(cls):
        return dict(
            spoked_ring_params=None,
            heater_params=None,
            via_stack_params=None,
            ring_heater_gap=1.42,
            label_p='P_Contact',
            label_n='N_Contact',
            # whatever value you might want to hard-code in the .py file rather than the .yaml file
        )

    def draw_layout(self) -> None:
        self.create_spoked_ring()
        if self.via_stack_params:
            self.create_via_stacks()
        if self.heater_params:
            self.create_heater()

        self.place_spoked_ring()
        if self.heater_params:
            self.place_heater()  # order has to be correct, so place must be after create
        if self.via_stack_params:
            self.place_via_stacks()

    def create_spoked_ring(self):
        spoked_ring_params = deepcopy(self.spoked_ring_params)
        # spoked_ring_params['coupling_slot'] = 3.0
        r_out = spoked_ring_params['rout']
        amplitude = 0.5 * r_out
        access_length = 2 * pi * sqrt(r_out * amplitude)
        spoked_ring_params['drop_slot'] = 0
        spoked_ring_params['access_length'] = access_length
        spoked_ring_params['drop_taper_length'] = 0
        self.spoked_ring_master = self.new_template(params=spoked_ring_params,
                                                    temp_cls=RingBase)

    def create_via_stacks(self):
        self.via_stack_master = self.new_template(params=self.via_stack_params,
                                                  temp_cls=ViaStack)

    def create_heater(self):
        # Extract values
        self.heater_params['ring_params']['r_out'] = self.spoked_ring_params['rout'] - \
                                                     self.spoked_ring_params['ring_width'] - \
                                                     self.params['ring_heater_gap']
        self.heater_master = self.new_template(params=self.heater_params,
                                               temp_cls=RingHeater)

    def place_spoked_ring(self):
        self.spoked_ring = self.add_instance(self.spoked_ring_master,
                                             loc=self.ring_loc,
                                             orient='R0')
        # Extract the ports
        self.extract_photonic_ports(
            inst=self.spoked_ring,
        )

    def place_heater(self):
        self.heater = self.add_instance(self.heater_master,
                                        loc=self.ring_loc,
                                        orient='R0')

    def place_via_stacks(self):
        silicon_ring_rin = self.spoked_ring_params['rout'] - self.spoked_ring_params['ring_width']
        # p-electrode position
        p_via_radius = silicon_ring_rin - self.spoked_ring_params['p_via_radius_offset']
        p_electrode_rin = p_via_radius + self.spoked_ring_params['electrode_offset']
        p_electrode_rout = p_electrode_rin + self.spoked_ring_params['electrode_width_outer']
        p_electrode_rcenter = (p_electrode_rout + p_electrode_rin) / 2
        # n-electrode position
        n_via_radius = silicon_ring_rin - self.spoked_ring_params['n_via_radius_offset']
        n_electrode_rout = n_via_radius - self.spoked_ring_params['electrode_offset']
        n_electrode_rin = n_electrode_rout - self.spoked_ring_params['electrode_width_inner']
        n_electrode_rcenter = (n_electrode_rout + n_electrode_rin) / 2

        via_stack_position_p = (p_electrode_rcenter, 0)
        via_stack_position_n = (-n_electrode_rcenter, 0)
        self.via_stacks['via_stack_p'] = self.add_instance(master=self.via_stack_master, loc=via_stack_position_p,
                                                           orient='R0', unit_mode=False)
        self.via_stacks['via_stack_n'] = self.add_instance(master=self.via_stack_master, loc=via_stack_position_n,
                                                           orient='R0',
                                                           unit_mode=False)
        ################################################################################
        # Process the ring electrode layers
        ################################################################################
        self.outer_electrode_ring_layer_inds = []
        self.outer_electrode_ring_layers = self.spoked_ring_params['outer_electrode_ring_layers']
        if not isinstance(self.outer_electrode_ring_layers, list):
            self.outer_electrode_ring_layers = [self.outer_electrode_ring_layers]
        for lpp in self.outer_electrode_ring_layers:
            self.outer_electrode_ring_layer_inds.append(self.grid.tech_info.get_layer_id(lpp[0]))
        self.outer_electrode_ring_layer_inds.sort()

        self.inner_electrode_ring_layer_inds = []
        self.inner_electrode_ring_layers = self.spoked_ring_params['inner_electrode_ring_layers']
        if not isinstance(self.inner_electrode_ring_layers, list):
            self.inner_electrode_ring_layers = [self.inner_electrode_ring_layers]
        for lpp in self.inner_electrode_ring_layers:
            self.inner_electrode_ring_layer_inds.append(self.grid.tech_info.get_layer_id(lpp[0]))
        self.inner_electrode_ring_layer_inds.sort()

        # outer electrode is p, inner electrode is n
        self.p_electrode_layer_ind_list = self.outer_electrode_ring_layer_inds
        self.n_electrode_layer_ind_list = self.inner_electrode_ring_layer_inds

        # p contact label
        bbox = BBox(
            top=self.via_stacks['via_stack_p'].bound_box.top,
            bottom=self.via_stacks['via_stack_p'].bound_box.bottom,
            left=self.via_stacks['via_stack_p'].bound_box.left,
            right=self.via_stacks['via_stack_p'].bound_box.right,
            resolution=self.grid.resolution
        )
        # contact_label_layer = self.grid.tech_info.get_layer_name(max(self.p_electrode_layer_ind_list))
        # self.add_label(label=self.params['label_p'], layer=(contact_label_layer, "label"), bbox=bbox)

        contact_label_layer = self.grid.tech_info.get_layer_name(max(self.p_electrode_layer_ind_list)+1)
        self.add_pin_primitive(net_name=self.params['label_p'], layer=(contact_label_layer, "label"), bbox=bbox)

        # n contact label
        bbox = BBox(
            top=self.via_stacks['via_stack_n'].bound_box.top,
            bottom=self.via_stacks['via_stack_n'].bound_box.bottom,
            left=self.via_stacks['via_stack_n'].bound_box.left,
            right=self.via_stacks['via_stack_n'].bound_box.right,
            resolution=self.grid.resolution
        )
        # contact_label_layer = self.grid.tech_info.get_layer_name(max(self.n_electrode_layer_ind_list))
        # self.add_label(label=self.params['label_n'], layer=(contact_label_layer, "label"), bbox=bbox)

        contact_label_layer = self.grid.tech_info.get_layer_name(max(self.n_electrode_layer_ind_list)+1)
        self.add_pin_primitive(net_name=self.params['label_n'], layer=(contact_label_layer, "label"), bbox=bbox)
# def test_ringsensable_dummy():
#     # 45RF spec file:
#     spec_file = 'layout/RingSensable/specs/ring_sensable_dummy.yaml'
#
#     plm = BPG.PhotonicLayoutManager(spec_file)
#     plm.generate_content()
#     plm.generate_gds()
#     plm.dataprep_calibre()
#
#
# if __name__ == '__main__':
#     test_ringsensable_dummy()

class RingSensableWithCosinegc(BPG.PhotonicTemplateBase):
    """
    Ring with integrated photodiode to sense light in ring--Script class
    """

    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)
        # Hard coded params
        self.ring_loc = (0, 0)
        # Parameters parsed from spec file
        self.spoked_ring_params = self.params["spoked_ring_params"]
        self.heater_params = self.params["heater_params"]
        self.via_stack_params = self.params["via_stack_params"]
        self.grating5_params = self.params['grating5_params']
        self.grating10_params = self.params['grating10_params']

        # Master declaration
        self.spoked_ring_master = dict()
        self.heater_master = dict()
        self.via_stack_master = dict()
        self.wgs_master = dict()

        # Instances declaration
        self.spoked_ring = dict()
        self.heater = dict()
        self.via_stacks = dict()
        self.gc = dict()
        self.wgs = dict()

    @classmethod
    def get_params_info(cls):
        return dict(grating5_params='5mfd gc',grating10_params='10mfd gc',
            spoked_ring_params='Parameters for the modulator-like spoked ring',
            heater_params='Parameters for the ring heater',
            via_stack_params='via stacks that connects electrode rings to wires',
            ring_heater_gap='Gap between outer radius of ring and heater',
            label_p='name for p contact label',
            label_n='name for n contact label',
        )

    @classmethod
    def get_default_param_values(cls):
        return dict(grating5_params=None,grating10_params=None,
            spoked_ring_params=None,
            heater_params=None,
            via_stack_params=None,
            ring_heater_gap=1.42,
            label_p='P_Contact',
            label_n='N_Contact',
            # whatever value you might want to hard-code in the .py file rather than the .yaml file
        )

    def draw_layout(self) -> None:
        self.create_spoked_ring()
        if self.via_stack_params:
            self.create_via_stacks()
        if self.heater_params:
            self.create_heater()

        self.place_spoked_ring()
        if self.heater_params:
            self.place_heater()  # order has to be correct, so place must be after create
        if self.via_stack_params:
            self.place_via_stacks()

        self.create_greating()
        self.place_gc()

    def create_spoked_ring(self):
        spoked_ring_params = deepcopy(self.spoked_ring_params)
        # spoked_ring_params['coupling_slot'] = 3.0
        r_out = spoked_ring_params['rout']
        amplitude = 0.5 * r_out
        access_length = 2 * pi * sqrt(r_out * amplitude)
        spoked_ring_params['drop_slot'] = 0
        spoked_ring_params['access_length'] = access_length
        spoked_ring_params['drop_taper_length'] = 0
        self.spoked_ring_master = self.new_template(params=spoked_ring_params,
                                                    temp_cls=RingBase)

    def create_via_stacks(self):
        self.via_stack_master = self.new_template(params=self.via_stack_params,
                                                  temp_cls=ViaStack)

    def create_heater(self):
        # Extract values
        self.heater_params['ring_params']['r_out'] = self.spoked_ring_params['rout'] - \
                                                     self.spoked_ring_params['ring_width'] - \
                                                     self.params['ring_heater_gap']
        self.heater_master = self.new_template(params=self.heater_params,
                                               temp_cls=RingHeater)

    def place_spoked_ring(self):
        self.spoked_ring = self.add_instance(self.spoked_ring_master,
                                             loc=self.ring_loc,
                                             orient='R0')
        # Extract the ports
        self.extract_photonic_ports(
            inst=self.spoked_ring,
        )

    def place_heater(self):
        self.heater = self.add_instance(self.heater_master,
                                        loc=self.ring_loc,
                                        orient='R0')

    def place_via_stacks(self):
        silicon_ring_rin = self.spoked_ring_params['rout'] - self.spoked_ring_params['ring_width']
        # p-electrode position
        p_via_radius = silicon_ring_rin - self.spoked_ring_params['p_via_radius_offset']
        p_electrode_rin = p_via_radius + self.spoked_ring_params['electrode_offset']
        p_electrode_rout = p_electrode_rin + self.spoked_ring_params['electrode_width_outer']
        p_electrode_rcenter = (p_electrode_rout + p_electrode_rin) / 2
        # n-electrode position
        n_via_radius = silicon_ring_rin - self.spoked_ring_params['n_via_radius_offset']
        n_electrode_rout = n_via_radius - self.spoked_ring_params['electrode_offset']
        n_electrode_rin = n_electrode_rout - self.spoked_ring_params['electrode_width_inner']
        n_electrode_rcenter = (n_electrode_rout + n_electrode_rin) / 2

        via_stack_position_p = (p_electrode_rcenter, 0)
        via_stack_position_n = (-n_electrode_rcenter, 0)
        self.via_stacks['via_stack_p'] = self.add_instance(master=self.via_stack_master, loc=via_stack_position_p,
                                                           orient='R0', unit_mode=False)
        self.via_stacks['via_stack_n'] = self.add_instance(master=self.via_stack_master, loc=via_stack_position_n,
                                                           orient='R0',
                                                           unit_mode=False)
        ################################################################################
        # Process the ring electrode layers
        ################################################################################
        self.outer_electrode_ring_layer_inds = []
        self.outer_electrode_ring_layers = self.spoked_ring_params['outer_electrode_ring_layers']
        if not isinstance(self.outer_electrode_ring_layers, list):
            self.outer_electrode_ring_layers = [self.outer_electrode_ring_layers]
        for lpp in self.outer_electrode_ring_layers:
            self.outer_electrode_ring_layer_inds.append(self.grid.tech_info.get_layer_id(lpp[0]))
        self.outer_electrode_ring_layer_inds.sort()

        self.inner_electrode_ring_layer_inds = []
        self.inner_electrode_ring_layers = self.spoked_ring_params['inner_electrode_ring_layers']
        if not isinstance(self.inner_electrode_ring_layers, list):
            self.inner_electrode_ring_layers = [self.inner_electrode_ring_layers]
        for lpp in self.inner_electrode_ring_layers:
            self.inner_electrode_ring_layer_inds.append(self.grid.tech_info.get_layer_id(lpp[0]))
        self.inner_electrode_ring_layer_inds.sort()

        # outer electrode is p, inner electrode is n
        self.p_electrode_layer_ind_list = self.outer_electrode_ring_layer_inds
        self.n_electrode_layer_ind_list = self.inner_electrode_ring_layer_inds

        # p contact label
        bbox = BBox(
            top=self.via_stacks['via_stack_p'].bound_box.top,
            bottom=self.via_stacks['via_stack_p'].bound_box.bottom,
            left=self.via_stacks['via_stack_p'].bound_box.left,
            right=self.via_stacks['via_stack_p'].bound_box.right,
            resolution=self.grid.resolution
        )
        # contact_label_layer = self.grid.tech_info.get_layer_name(max(self.p_electrode_layer_ind_list))
        # self.add_label(label=self.params['label_p'], layer=(contact_label_layer, "label"), bbox=bbox)

        contact_label_layer = self.grid.tech_info.get_layer_name(max(self.p_electrode_layer_ind_list)+1)
        self.add_pin_primitive(net_name=self.params['label_p'], layer=(contact_label_layer, "label"), bbox=bbox)

        # n contact label
        bbox = BBox(
            top=self.via_stacks['via_stack_n'].bound_box.top,
            bottom=self.via_stacks['via_stack_n'].bound_box.bottom,
            left=self.via_stacks['via_stack_n'].bound_box.left,
            right=self.via_stacks['via_stack_n'].bound_box.right,
            resolution=self.grid.resolution
        )
        # contact_label_layer = self.grid.tech_info.get_layer_name(max(self.n_electrode_layer_ind_list))
        # self.add_label(label=self.params['label_n'], layer=(contact_label_layer, "label"), bbox=bbox)

        contact_label_layer = self.grid.tech_info.get_layer_name(max(self.n_electrode_layer_ind_list)+1)
        self.add_pin_primitive(net_name=self.params['label_n'], layer=(contact_label_layer, "label"), bbox=bbox)
    def create_greating(self) -> None:
        grating_module = importlib.import_module(self.grating5_params['package'])
        grating_class = getattr(grating_module, self.grating5_params['class'])
        self.grating_master5 = self.new_template(params={'gds_path': 'dummy'},
                                                 temp_cls=grating_class)
        grating_module = importlib.import_module(self.grating10_params['package'])
        grating_class = getattr(grating_module, self.grating10_params['class'])
        self.grating_master10 = self.new_template(params={'gds_path': 'dummy'},
                                                  temp_cls=grating_class)
        params = dict(layer=self.spoked_ring_params['layer'],
                      port_layer=self.spoked_ring_params['port_layer'],
                      merge_arcs=False)
        arc_params = [
            dict(arc_type='straight_wg', width=self.spoked_ring_params['wg_width'],
                 )]
        params['arc_params'] = arc_params
        # Set parameters for input and output tapers
        taper_params = deepcopy(params)
        taper_params['arc_params'] = [
            dict(arc_type="straight_wg", width=[self.grating5_params['width'],
                                                self.spoked_ring_params['wg_width']],
                 length=15)]
        self.wgs_master['taper_in'] = self.new_template(params=taper_params, temp_cls=AdiabaticPaths)



    def place_gc(self) -> None:
        self.wgs['in'] = self.add_instance_port_to_port(inst_master=self.wgs_master['taper_in'],
                                                       instance_port_name='PORT_OUT',
                                                       self_port=self.spoked_ring['PORT0'],
                                                       reflect=False)
        self.gc['in'] = self.add_instance_port_to_port(inst_master=self.grating_master5,
                                                             instance_port_name='PORT_OUT',
                                                             self_port=self.wgs['in']['PORT_IN'],
                                                             reflect=False)
        self.wgs['out'] = self.add_instance_port_to_port(inst_master=self.wgs_master['taper_in'],
                                                        instance_port_name='PORT_OUT',
                                                        self_port=self.spoked_ring['PORT1'],
                                                        reflect=False)
        self.gc['out'] = self.add_instance_port_to_port(inst_master=self.grating_master5,
                                                             instance_port_name='PORT_OUT',
                                                             self_port=self.wgs['out']['PORT_IN'],
                                                             reflect=False)



class RingSensableCLIPP(BPG.PhotonicTemplateBase):
    """
    Photosensing Ring using CLIPP probe with Heater Script class
    """

    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)

        self.ring_params = self.params['ring_params']
        self.heater_params = self.params['heater_params']
        self.capacitor_params = self.params['capacitor_params']
        self.capacitor_orientation = self.capacitor_params['orientation']

        # Master declaration
        self.ring_master = dict()
        self.heater_master = dict()
        self.capacitor_master = dict()

        # Instances declaration
        self.ring = dict()
        self.heater = dict()
        self.capacitor = dict()

    @classmethod
    def get_params_info(cls):
        return dict(
            ring_params='This is the ring that is to be tuned',
            heater_params='This is the heater for the ring that tunes it',
            capacitor_params='This is the CLIPP capacitor above the ring',
            capacitor_orientation='This allows you to rotate the capacitor',
            ring_heater_gap = 'This is the gap between the heater and the ring',
            ring_orientation = 'This is the orientation (e.g R0,R90) of the heater ring',
        )

    @classmethod
    def get_default_param_values(cls):
        return dict(
            ring_params=None,
            heater_params=None,
            capacitor_params=None,
            capacitor_orientation='R90',
            ring_heater_gap = 1.42,
            ring_orientation = 'R0',
            # whatever value you might want to hard-code in the .py file rather than the .yaml file
        )

    def draw_layout(self) -> None:
        # Create layouts
        self.create_ring()
        if self.heater_params:
            self.create_heater()
        self.create_capacitor()
        # Place layouts
        self.place_ring()
        if self.heater_params:
            self.place_heater()
        self.place_capacitor()

    def create_ring(self):
        self.ring_master = self.new_template(params=self.ring_params, temp_cls=SimpleRing)

    def create_heater(self):
        # Extract values
        self.heater_params['ring_params']['r_out'] = self.ring_params['r_out'] - \
                                                     self.ring_params['ring_width'] - \
                                                     self.params['ring_heater_gap']
        # Create instance
        self.heater_master = self.new_template(params=self.heater_params, temp_cls=RingHeater)

    def create_capacitor(self):
        rCenter = self.ring_params['r_out'] - self.ring_params['ring_width'] / 2
        self.capacitor_params['capacitor_params']['rCenter'] = rCenter
        distance = self.capacitor_params['capacitor_params']['capacitor_distance']
        phi = 180*distance/(pi*rCenter)
        theta = 180-phi
        self.capacitor_params['capacitor_params']['start_angle'] = -theta/2
        self.capacitor_params['capacitor_params']['stop_angle'] = theta/2
        self.capacitor_params['via_stack_params']['bottom_layer'] = self.capacitor_params['capacitor_params']['layer']
        self.capacitor_master = self.new_template(params=self.capacitor_params, temp_cls=RingCapacitor)

    def place_ring(self):
        self.ring=self.add_instance(master=self.ring_master, loc=(0, 0), orient='R0', unit_mode=False)

    def place_heater(self):
        self.ring_orientation=self.params['ring_orientation']
        self.heater=self.add_instance(master=self.heater_master, loc=(0,0), orient=self.ring_orientation, unit_mode=False)

    def place_capacitor(self):
        self.capacitor=self.add_instance(master=self.capacitor_master, loc=(0,0), orient=self.capacitor_orientation, unit_mode=False)
        self.extract_photonic_ports(
            inst=self.capacitor,
            port_names=['via_stack_left', 'via_stack_right'],
            show=False,)



