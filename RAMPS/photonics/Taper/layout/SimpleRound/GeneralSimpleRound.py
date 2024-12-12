import BPG
from ..SimpleRound.SimpleRound import SimpleRound
import importlib
from Photonic_Core_Layout.WaveguideBase.WaveguideBase import WaveguideBase


class GeneralSimpleRound(BPG.PhotonicTemplateBase):
    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)
        self.ring_params = self.params['ring_params']
        self.UT_params = self.params['UT_params']
        self.heater_params = self.params['heater_params']

    @classmethod
    def get_params_info(cls):
        return dict(
            ring_params='Params passed to SimpleRound to create a desired ring',
            UT_params='Params passed to self.draw_UT_shapes that will create desired undercut',
            heater_params='Module, class and paramerers used to draw a heater'
        )

    @classmethod
    def get_default_param_values(cls):
        return dict(
            UT_params=None,
            heater_params=None,
        )

    def draw_layout(self) -> None:
        # Instantiate a SimpleRound
        ring_master = self.new_template(params=self.ring_params, temp_cls=SimpleRound)
        ring_inst = self.add_instance(master=ring_master, loc=(0, 0))

        # add UT shapes
        if self.UT_params is not None:
            self.draw_ut_shapes()

        if self.heater_params is not None:
            self.draw_heater()

    def void(self):
        pass

    def draw_ut_shapes(self):
        WaveguideBase.create_ports = self.void  # overwrite create_ports function to resolve error with port layer
        # iterate over the list of the parameters
        for ut_params in self.UT_params:
            # extract parameters used to determine the number and size of the circular spokes
            ut_length = ut_params['length']
            ut_width = ut_params['width']
            ut_distance = ut_params['distance']
            ut_layer = ut_params['layer']

            # add left UT shape
            points_left = [(-ut_distance - ut_width / 2, -ut_length / 2), (-ut_distance - ut_width / 2, ut_length / 2)]

            left_params = dict(width=ut_width,
                               layer=ut_layer,
                               points=points_left)
            lest_master = self.new_template(params=left_params, temp_cls=WaveguideBase)
            left_inst = self.add_instance(master=lest_master, loc=(0, 0))

            # add right UT shape
            points_right = [(ut_distance + ut_width / 2, -ut_length / 2), (ut_distance + ut_width / 2, ut_length / 2)]

            right_params = dict(width=ut_width,
                                layer=ut_layer,
                                points=points_right)
            lest_master = self.new_template(params=right_params, temp_cls=WaveguideBase)
            right_inst = self.add_instance(master=lest_master, loc=(0, 0))



    def draw_heater(self):
        heater_module = importlib.import_module(self.heater_params['module'])
        heater_class = getattr(heater_module, self.heater_params['class'])
        heater_params = self.heater_params['params']

        heater_master = self.new_template(params=heater_params, temp_cls=heater_class)
        heater_inst = self.add_instance(master=heater_master,
                                        loc=(0, 0),
                                        orient='R0',
                                        unit_mode=False)
        # extract pins
        self.extract_pins_from_inst(inst=heater_inst, pin_names=['Heat_P', 'Heat_N'])
