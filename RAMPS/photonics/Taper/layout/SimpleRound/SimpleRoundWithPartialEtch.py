import BPG
from ..SimpleRound.SimpleRound import SimpleRound
from ..Round.Round import Round
import importlib


class SimpleRoundWithPartialEtch(BPG.PhotonicTemplateBase):
    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)
        self.ring_params = self.params['ring_params']
        self.partial_etch_params = self.params['partial_etch_params']


    @classmethod
    def get_params_info(cls):
        return dict(
            ring_params='Params passed to SimpleRound to create a desired ring on full thickness layer',
            partial_etch_params = 'Params passed to SimpleRound to create a desired ring on partial etch layer'
        )

    @classmethod
    def get_default_param_values(cls):
        return dict(

        )

    def draw_layout(self) -> None:
        # Instantiate a SimpleRound
        full_thickness_ring_master = self.new_template(params=self.ring_params, temp_cls=SimpleRound)
        ring_inst = self.add_instance(master=full_thickness_ring_master, loc=(0, 0))

        partial_thickness_ring_master = self.new_template(params=self.partial_etch_params, temp_cls=SimpleRound)
        ring_inst = self.add_instance(master=partial_thickness_ring_master, loc=(0, 0))
