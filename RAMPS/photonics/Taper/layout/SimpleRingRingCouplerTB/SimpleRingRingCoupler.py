import BPG
import importlib

""" This class draws 2 arbitrary rings separated by a gap. This is not meant to be used as a layout generator, but
instead as a way to export ring-ring coupler to Lumerical """


class SimpleRingRingCoupler(BPG.PhotonicTemplateBase):
    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)

        # Extracted params
        self.input_ring_module = params['input_ring_module']
        self.input_ring_class = params['input_ring_class']
        self.input_ring_params = params['input_ring_params']

        self.output_ring_module = params['output_ring_module']
        self.output_ring_class = params['output_ring_class']
        self.output_ring_params = params['output_ring_params']

        self.gap = params['gap']
        self.ring_orient = self.params['ring_orient']

    @classmethod
    def get_params_info(cls):
        return dict(
            input_ring_module=None,
            input_ring_class=None,
            input_ring_params=None,
            output_ring_module=None,
            output_ring_class=None,
            output_ring_params=None,
            gap='Gap',
            ring_orient='Orientation at which input/output rings are instantiated'
        )

    @classmethod
    def get_default_param_values(cls) -> dict:
        return dict(ring_orient='R0')

    def draw_layout(self) -> None:
        # Import input ring and instantiate it at (0, 0)
        input_ring_module = importlib.import_module(self.input_ring_module)
        input_ring_class = getattr(input_ring_module, self.input_ring_class)
        input_ring_template = self.new_template(params=self.input_ring_params, temp_cls=input_ring_class)
        input_ring_inst = self.add_instance(master=input_ring_template, loc=(0, 0), orient=self.ring_orient)

        input_ring_height = input_ring_inst.bound_box.height

        # Import output ring and instantiate it above input ring by gap amount
        output_ring_module = importlib.import_module(self.output_ring_module)
        output_ring_class = getattr(output_ring_module, self.output_ring_class)
        output_ring_template = self.new_template(params=self.output_ring_params, temp_cls=output_ring_class)
        output_ring_height = output_ring_template.bound_box.height
        _ = self.add_instance(master=output_ring_template,
                              loc=(0, input_ring_height / 2 + output_ring_height / 2 + self.gap),
                              orient=self.ring_orient)

# Don't add ports, this device isn't meant to be used in layouts
