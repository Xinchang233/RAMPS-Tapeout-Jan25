import BPG
import importlib
from Photonic_Core_Layout.Template1.Template1 import Template1
#from Photonic_Core_Layout.AdiabaticPaths.AdiabaticPaths import AdiabaticPaths
from layout.Template2.Template2 import Template2
#from layout.ArbitraryOrderRingFilter.ArbitraryOrderRingFilter import ArbitraryOrderRingFilter
from copy import deepcopy

class Template(BPG.PhotonicTemplateBase):
    """This class creates nothing. It just serves as an template for what a real code might look like.
    -------------
    Template parameters: None
    """
    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)
        self.component1_params = self.params["component1_params_as_shown_in_yaml_file"]
        self.component2_params = self.params["component2_params_as_shown_in_yaml_file"]

        #Master declaration
        self.components_master = dict()

        #Instances declaration
        self.components = dict()

    @classmethod
    def get_params_info(cls):
        return dict(
            component1_params='This is a blurb that describes what component 1 does',
            component2_params='This is a blurb that describes what component 2 does',
            any_other_params='This is a blub that describes what any_other_params are for', #note that the order must be
            # correct, so component2_params can't use values from any_other_params, for instance.
                    )

    @classmethod
    def get_default_param_values(cls):
        return dict(
            component1_params=None,
            component2_params=None,
            any_other_params=3.0, #whatever value you might want to hard-code in the .py file rather than the .yaml file
        )

    def draw_layout(self) -> None:
        self.create_component1()
        self.create_component2()
        self.place_component1()
        self.place_component2() #order has to be correct, so place must be after create

    def create_component1(self):
        self.components_master['component1'] = self.new_template(params=self.component1_params,
                                                                   temp_cls=Template1)

    def create_component2(self):
        self.components_master['component2'] = self.new_template(params=self.component2_params,
                                                                 temp_cls=Template2)

    def place_component1(self):
        self.components['component1'] = self.add_instance_port_to_port(inst_master=self.components_master['component1'],
                                       instance_port_name='PORT_IN',
                                       self_port=self.components['component1']['PORT_THROUGH'],
                                       reflect=False)

    def place_component2(self):
        self.components['component2'] = self.add_instance(self.components_master['component2'],
                                                 loc=(0, 0),
                                                 orient='R0')







