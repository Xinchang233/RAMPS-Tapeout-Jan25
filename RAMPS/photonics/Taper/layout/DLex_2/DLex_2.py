# DL exercise 2: take 2 of arbitrary single structures and put them onto designed positions

import BPG
import importlib

class DLex_2(BPG.PhotonicTemplateBase):
    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)

        self.xcoord = params['x_coord']
        self.ycoord = params['y_coord']

        # Extracted params
        self.module1 = params['module1']
        self.class1 = params['class1']
        self.params1 = params['params1']

        self.module2 = params['module2']
        self.class2 = params['class2']
        self.params2 = params['params2']

        self.layer1 = self.params1['layer'] if 'layer' in self.params1.keys() else self.params1['params1']['layer']
        self.layer2 = self.params2['layer'] if 'layer' in self.params2.keys() else self.params2['params2']['layer']

    @classmethod
    def get_default_param_values(cls):
        return dict(
        )

    @classmethod
    def get_params_info(cls):  # Returns definition of the parameters.
        return dict(
            )

    def draw_layout(self):
        # specify which two structures is wanted and their locations on chip

        # Import the first structure and instantiate it at (0, 0)

        module1 = importlib.import_module(self.module1)
        class1 = getattr(module1, self.class1)
        template1 = self.new_template(params=self.params1, temp_cls=class1)
        inst1 = self.add_instance(master=template1,
                                      loc=(0, 0))

        module2 = importlib.import_module(self.module2)
        class2 = getattr(module2, self.class2)
        template2 = self.new_template(params=self.params2, temp_cls=class2)
        inst2 = self.add_instance(master=template2,
                                      loc=(self.xcoord, self.ycoord))
