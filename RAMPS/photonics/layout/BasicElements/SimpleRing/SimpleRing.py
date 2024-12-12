import BPG
from numpy import pi, sin, cos, deg2rad

class SimpleRing(BPG.PhotonicTemplateBase):
    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)
        self.layer = self.params['layer']
        self.port_layer = self.params['port_layer']
        self.r_out = self.params['r_out']
        self.ring_width = self.params['ring_width']
        self.theta_in = self.params['theta_in']
        self.theta_out = self.params['theta_out']

    @classmethod
    def get_params_info(cls):
        return dict(
            layer='None',
            port_layer='None',
            r_out='None',
            ring_width='None',
            theta_in='Start angle',
            theta_out='End angle'
        )

    @classmethod
    def get_default_param_values(cls):
        return dict(
            layer=['si_full_free', 'drawing'],
            port_layer=['si_full_free', 'port'],
            theta_in=0,
            theta_out=360
        )

    def draw_layout(self) -> None:
        self.add_round(layer=self.layer,
                       resolution=self.grid.resolution,
                       center=(0, 0),
                       rin=self.r_out - self.ring_width,
                       rout=self.r_out,
                       theta0=self.theta_in,
                       theta1=self.theta_out)

        theta0 = deg2rad(self.theta_in)
        theta1 = deg2rad(self.theta_out)

        R = self.r_out-self.ring_width/2

# TODO: orient angle of the port properly

        self.add_photonic_port(
            name='PORT_IN', orient='R90', center=(R*cos(theta0), R*sin(theta0)), width=self.ring_width,
            layer=self.port_layer, resolution=self.grid.resolution, unit_mode=False, show=False, angle=theta0)

        self.add_photonic_port(
            name='PORT_OUT', orient='R270', center=(R*cos(theta1), R*sin(theta1)), width=self.ring_width,
            layer=self.port_layer, resolution=self.grid.resolution, unit_mode=False, show=False,angle=theta1)