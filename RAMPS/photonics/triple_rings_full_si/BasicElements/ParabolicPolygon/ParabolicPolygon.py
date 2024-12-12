import BPG
import numpy as np


class ParabolicPolygon(BPG.PhotonicTemplateBase):
    port_layer = ('RX', 'port')
    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)
        self.win = self.params['win']
        self.wout = self.params['wout']
        self.length = self.params['length']
        self.layer = self.params['layer']

    @classmethod
    def get_params_info(cls):
        return dict(
            win='Input width',
            wout='Output width',
            length='Length of the PP',
            layer = 'Layer'
        )

    def draw_layout(self):
        num_points = int(self.length * 1e2)
        x1 = np.linspace(0, self.length, num=num_points)
        constant = (self.wout - self.win) / self.length ** 2

        if constant > 0:
            y1 = constant / 2 * (x1 ** 2) + self.win / 2

            center = (0, 0)
            p1 = list(zip(-x1 + center[0], y1 + center[1]))
            p2 = list(zip(np.flip(-x1 + center[0], axis=0), np.flip(y1 * -1 + center[1], axis=0)))
            points = p1 + p2
        else:
            y1 = -constant / 2 * (x1 ** 2) + self.wout / 2
            y1=y1[::-1] # Reverse order of y coordinates
            center = (0, 0)
            p1 = list(zip(-x1 + center[0], y1 + center[1]))
            p2 = list(zip(np.flip(-x1 + center[0], axis=0), np.flip(y1 * -1 + center[1], axis=0)))
            points = p1+ p2

        self.add_polygon(layer=self.layer,
                         resolution=self.grid.resolution,
                         points=points,
                         unit_mode=False,
                         )

        self.add_photonic_port(
            name='PORT_OUT', orient='R0', center=(center[0] - self.length, center[1]), width=self.wout,
            layer=self.port_layer, resolution=self.grid.resolution, unit_mode=False, show=False)

        self.add_photonic_port(
            name='PORT_IN', orient='R180', center=(center[0], center[1]), width=self.win,
            layer=self.port_layer, resolution=self.grid.resolution, unit_mode=False, show=False)
#
# def test_taper():
#     # 45RF spec file:
#     spec_file = 'layout/BasicElements/ParabolicPolygon/specs/ParabolicPolygon.yaml'
#     plm = BPG.PhotonicLayoutManager(spec_file)
#     plm.generate_content()
#     plm.generate_gds()
#     # plm.dataprep_calibre()

#
# if __name__ == '__main__':
#     test_taper()