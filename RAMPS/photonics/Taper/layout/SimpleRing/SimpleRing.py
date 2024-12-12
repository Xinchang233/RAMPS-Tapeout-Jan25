import BPG



class SimpleRing(BPG.PhotonicTemplateBase):
    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)
        self.layer = params['layer']
        self.port_layer = params['port_layer']
        self.r_out = params['r_out']
        self.ring_width = params['ring_width']

    @classmethod
    def get_params_info(cls):
        return dict(
            layer='None',
            port_layer='None',
            r_out='None',
            ring_width='None'
        )

    @classmethod
    def get_default_param_values(cls):
        return dict(
            layer=None,
            port_layer=None,
            r_out=None,
            ring_width=None
        )

    def draw_layout(self) -> None:
        self.add_round(layer=self.layer,
                       resolution=self.grid.resolution,
                       center=(0, 0),
                       rin=self.r_out - self.ring_width,
                       rout=self.r_out)




