import BPG
import numpy as np
from scipy.interpolate import interp1d


class SplineBend(BPG.PhotonicTemplateBase):
    port_layer = ('RX', 'port')
    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)
        self.layer = self.params['layer']
        self.gap_out = self.params['gap_out']
        self.gap_in = self.params['gap_in']
        self.s = self.params['s']

        self.w_in_section = self.params['w_in_section']
        self.dx = self.params['dx']
        self.w_out_section = self.params['w_out_section']
        self.length = self.params['length']

    @classmethod
    def get_params_info(cls):
        return dict(
            layer='Layer',
            gap_out='Output gap',
            gap_in='Input gap',
            s='spline parameter determening the spline rate of change',
            w_in_section='input width of the wg',
            dx='dx',
            w_out_section='output width of the wg',
            length='Length of the spline bend'

        )

    @classmethod
    def get_default_param_values(cls):
        return dict(
            dx=0.1,
            s=0.01
        )

    def draw_layout(self):
        G = abs(self.gap_out)
        wout = self.w_in_section
        dx = self.dx
        w = self.w_out_section
        g = self.gap_in  # last crossection gap
        s = self.s  # %distance between spline points
        s1 = s
        offset = 0  # ; %if you need an offser for your bends on y direction
        L = self.length

        xout = np.arange(0, L + dx, dx)  # xmax:dx:xmax+L;
        dd = offset - g / 2 - w
        du = offset - g / 2
        ud = offset + g / 2
        uu = offset + g / 2 + w  # % last crossection positions
        yt1 = np.zeros((4, 1))
        yt1[3] = 0.5 * (du + ud) - G / 2 - wout
        yt1[2] = yt1[3]
        yt1[1] = dd
        yt1[0] = dd
        XX = np.array([xout[0] - s, xout[0], xout[-1], xout[-1] + s1])
        yt1 = yt1.transpose()
        ddyaout = interp1d(XX, yt1, kind='cubic')(xout)

        yt1 = np.zeros((4, 1))
        yt1[3] = 0.5 * (du + ud) - G / 2
        yt1[2] = yt1[3]
        yt1[1] = du
        yt1[0] = du
        XX = np.array([xout[0] - s, xout[0], xout[-1], xout[-1] + s1])
        yt1 = yt1.transpose()
        duyaout = interp1d(XX, yt1, kind='cubic')(xout)

        yt1 = np.zeros((4, 1))
        yt1[3] = 0.5 * (du + ud) + G / 2
        yt1[2] = yt1[3]
        yt1[1] = ud
        yt1[0] = ud
        XX = np.array([xout[0] - s, xout[0], xout[-1], xout[-1] + s1])
        yt1 = yt1.transpose()
        udyaout = interp1d(XX, yt1, kind='cubic')(xout)

        yt1 = np.zeros((4, 1))
        yt1[3] = 0.5 * (du + ud) + G / 2 + wout
        yt1[2] = yt1[3]
        yt1[1] = uu
        yt1[0] = uu
        XX = np.array([xout[0] - s, xout[0], xout[-1], xout[-1] + s1])
        yt1 = yt1.transpose()
        uuyaout = interp1d(XX, yt1, kind='cubic')(xout)


        xl = list(xout) + list(np.flip(xout))
        yl = list(ddyaout[0]) + list(np.flip(duyaout[0]))
        bv = list(zip(xl, yl))

        xu = list(xout) + list(np.flip(xout))
        yu = list(udyaout[0]) + list(np.flip(uuyaout[0]))
        tv = list(zip(xu, yu))

        if self.gap_out > 0:
            self.add_polygon(layer=self.layer,
                             resolution=self.grid.resolution,
                             points=tv,
                             unit_mode=False,
                             )

            self.add_photonic_port(
                name='PORT_IN', orient='R0', center=(xout[0], (yu[0] + yu[-1]) / 2), width=wout,
                layer=self.port_layer, resolution=self.grid.resolution, unit_mode=False, show=False)

            self.add_photonic_port(
                name='PORT_OUT', orient='R180', center=(xout[-1], (udyaout[0][-1] + uuyaout[0][-1]) / 2), width=w,
                layer=self.port_layer, resolution=self.grid.resolution, unit_mode=False, show=False)

        else:
            self.add_polygon(layer=self.layer,
                             resolution=self.grid.resolution,
                             points=bv,
                             unit_mode=False,
                             )

            self.add_photonic_port(
                name='PORT_IN', orient='R0', center=(xout[0], (yl[0] + yl[-1]) / 2), width=wout,
                layer=self.port_layer, resolution=self.grid.resolution, unit_mode=False, show=False)

            self.add_photonic_port(
                name='PORT_OUT', orient='R180', center=(xout[-1], (ddyaout[0][-1] + duyaout[0][-1]) / 2), width=w,
                layer=self.port_layer, resolution=self.grid.resolution, unit_mode=False, show=False)

#
# def test_taper():
#     # 45RF spec file:
#     spec_file = 'layout/BasicElements/SplineBend/specs/development.yaml'
#     plm = BPG.PhotonicLayoutManager(spec_file)
#     plm.generate_content()
#     plm.generate_gds()
# plm.dataprep_calibre()


#
# if __name__ == '__main__':
#     test_taper()
