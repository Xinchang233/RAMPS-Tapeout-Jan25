import BPG
from numpy import pi, sin, cos, deg2rad
import numpy as np
from BPG.objects import PhotonicPolygon


class Round(BPG.PhotonicTemplateBase):
    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)
        self.layer = params['layer']
        self.r_out = params['r_out']
        self.ring_width = params['ring_width']
        self.theta_in = self.params['theta_in']
        self.theta_out = self.params['theta_out']
        self.resolution = self.params['resolution']
        self.port_layer = self.params['port_layer']

    @classmethod
    def get_params_info(cls):
        return dict(
            layer='None',
            r_out='None',
            ring_width='None',
            theta_in='Start angle',
            theta_out='End angle',
            resolution='Angular resolution in radians',
            port_layer='port layer'
        )

    @classmethod
    def get_default_param_values(cls):
        return dict(
            theta_in=0,
            theta_out=360,
            resolution=0.001,
            port_layer=('si_full', 'port')
        )

    def draw_layout(self) -> None:
        rout = self.r_out
        rin = self.r_out - self.ring_width

        delta_theta_out = max(self.resolution, 0.01)
        delta_theta_in = max(self.resolution, 0.01)

        theta_out = np.arange(deg2rad(self.theta_in), deg2rad(self.theta_out), delta_theta_out)
        theta_in = np.arange(deg2rad(self.theta_in), deg2rad(self.theta_out), delta_theta_in)

        points_out = []
        points_in = []

        for t in theta_out:
            p1 = (cos(t) * rout, sin(t) * rout)
            points_out.append(p1)

        if (self.theta_out - self.theta_in) > 359:  points_out.append((rout, 0))
        points_out.reverse()

        for t in theta_in:
            p2 = (cos(t) * rin, sin(t) * rin)
            points_in.append(p2)

        if (self.theta_out - self.theta_in) > 359: points_in.append((rin, 0))

        points = points_in + points_out

        polygon = PhotonicPolygon(resolution=self.grid.resolution,
                                  layer=self.layer,
                                  points=points)

        self.add_obj(polygon)

        self.add_photonic_port(
            name='PORT_IN',
            center=(cos(deg2rad(self.theta_in)) * (self.r_out - self.ring_width / 2),
                    sin(deg2rad(self.theta_in)) * (self.r_out - self.ring_width / 2)),
            orient='R0',
            width=self.ring_width,
            layer=self.port_layer,
            angle=np.deg2rad(self.theta_in) + pi / 2,
        )

        self.add_photonic_port(
            name='PORT_OUT',
            center=(cos(deg2rad(self.theta_out)) * (self.r_out - self.ring_width / 2),
                    sin(deg2rad(self.theta_out)) * (self.r_out - self.ring_width / 2)),
            orient='R180',
            width=self.ring_width,
            layer=self.port_layer,
            angle=np.deg2rad(self.theta_out) + pi / 2,
        )
