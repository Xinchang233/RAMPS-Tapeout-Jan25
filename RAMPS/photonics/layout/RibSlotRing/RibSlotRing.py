import BPG
import importlib


class RibSlotRing(BPG.PhotonicTemplateBase):
    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)

        # Extracted params
        self.ring_module = params['ring_module']
        self.ring_class = params['ring_class']
        self.ring_params = params['ring_params']
        self.ring_orient = self.params['ring_orient']

        self.wg_width = self.params['wg_width']
        self.gap = params['gap']

        self.layer = self.ring_params['layer'] if 'layer' in self.ring_params.keys() else self.ring_params['ring_params']['layer']
        self.partial_layer = self.ring_params['partial_ring_layer'] if 'partial_ring_layer' in self.ring_params.keys() else self.ring_params['ring_params']['partial_ring_layer']
        self.slot_gap = self.ring_params['gap'] if 'gap' in self.ring_params.keys() else self.ring_params['ring_params']['gap']

    @classmethod
    def get_params_info(cls):
        return dict(
            ring_module=None,
            ring_class=None,
            ring_params=None,
            gap='Gap',
            ring_orient='Orientation at which input/output rings are instantiated',
            wg_width='Waveguide width'
        )

    @classmethod
    def get_default_param_values(cls) -> dict:
        return dict(ring_orient='R0')

    def draw_layout(self) -> None:
        # Import input ring and instantiate it at (0, 0)
        ring_module = importlib.import_module(self.ring_module)
        ring_class = getattr(ring_module, self.ring_class)
        ring_template = self.new_template(params=self.ring_params, temp_cls=ring_class)
        ring_inst = self.add_instance(master=ring_template,
                                      loc=(0, ring_template.bound_box.height / 2 + self.gap + self.wg_width / 2),
                                      orient=self.ring_orient)

        ring_height = ring_inst.bound_box.height
        ring_width = ring_inst.bound_box.width

        # Rib WG with slot
        y_offset = 0
        self.add_rect(
            layer=self.partial_layer,
            coord1=(-ring_width, y_offset + self.wg_width / 2),
            coord2=(ring_width,  y_offset - self.wg_width / 2),
        )
        y_offset -= self.wg_width
        self.add_rect(
            layer=self.layer,
            coord1=(-ring_width, y_offset + self.wg_width / 2),
            coord2=(ring_width,  y_offset - self.wg_width / 2),
        )
        y_offset -= self.wg_width + self.slot_gap
        self.add_rect(
            layer=self.layer,
            coord1=(-ring_width, y_offset + self.wg_width / 2),
            coord2=(ring_width,  y_offset - self.wg_width / 2),
        )
        y_offset -= self.wg_width
        self.add_rect(
            layer=self.partial_layer,
            coord1=(-ring_width, y_offset + self.wg_width / 2),
            coord2=(ring_width,  y_offset - self.wg_width / 2),
        )
