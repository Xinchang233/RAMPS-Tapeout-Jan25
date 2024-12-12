import BPG



class GratingPlaceHolder(BPG.PhotonicTemplateBase):
    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)
        self.box_width = self.params['box_width']
        self.box_height = self.params['box_height']

    @classmethod
    def get_params_info(cls):
        return dict(
            box_width='Width of PHOTONIC box',
            box_height='Height of Photonic Box',
        )

    @classmethod
    def get_default_param_values(cls) -> dict:
        return dict(
            box_width=76,
            box_height=20,
        )

    def draw_layout(self):


        left = -self.box_width / 2
        right = self.box_width / 2
        bottom = -self.box_height / 2
        top = self.box_height / 2

        box_points = [[left, bottom], [right, bottom], [right, top], [left, top]]

        box_points = list(box_points)
        self.add_polygon(layer=('PhotGrating', 'photmarker'),
                         points=box_points,
                         resolution=self.grid.resolution,
                         )
        # self.add_polygon(layer=('lib_component', 'drawing'),
        #                  points=box_points,
        #                  resolution=self.grid.resolution,
        #                  )

        points = [[self.box_width / 2, -0.0100], [self.box_width / 2, 0.01], [self.box_width / 2 - 0.01, 0]]

        points = list(points)
        self.add_polygon(layer=('grating_place_holder', 'drawing'),
                         points=points,
                         resolution=self.grid.resolution,
                         )
        center = ((points[0][0] + points[1][0]) / 2, points[2][1])
        self.add_photonic_port(name='PORT_OUT', center=center, orient='R180', width=1, layer=('si_full_free', 'port'),
                               resolution=self.grid.resolution)



