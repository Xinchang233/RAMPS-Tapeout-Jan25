import BPG
from copy import deepcopy

from Photonic_Core_Layout_Djordje.Arrayable.Arrayable import Arrayable


class Arrayed_Moscap(BPG.PhotonicTemplateBase):
    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)

        self.spoked_ring_params = params['spoked_ring_params']
        self.arrayable_params = params['arrayable_params']

    @classmethod
    def get_default_param_values(cls):
        return dict(
            # Standard parameters
            spoked_ring_params=None,
            arrayable_params=None
        )

    @classmethod
    def get_params_info(cls):  # Returns definition of the parameters.
        return dict(
            # Standard parameters
            spoked_ring_params="None",
            arrayable_params="None", )

    def draw_layout(self):
        self.arrayable_params['class_params'] = deepcopy(self.spoked_ring_params)

        temp = self.new_template(params=self.arrayable_params, temp_cls=Arrayable)
        inst = self.add_instance(master=temp, loc=(0, 0), orient="R270", unit_mode=False, )
