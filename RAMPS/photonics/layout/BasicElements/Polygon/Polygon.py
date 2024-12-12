import BPG

class  Polygon(BPG.PhotonicTemplateBase):

    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)
        self.points = self.params['points']
        self.layer = self.params['layer']

    @classmethod
    def get_params_info(cls):
        return dict(
            points='Polygon points',
            layer = 'Layer'
        )

    def draw_layout(self):

        self.add_polygon(layer=self.layer,
                         resolution=self.grid.resolution,
                         points=self.points,
                         unit_mode=False,
                         )