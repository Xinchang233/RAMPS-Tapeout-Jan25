import BPG
from BPG.objects import PhotonicPolygon
import numpy as np
from numpy import pi
from copy import deepcopy


class SimpleRound(BPG.PhotonicTemplateBase):
    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)
        self.layer = self.params['layer']
        self.r_out = self.params['r_out']
        self.ring_width = self.params['r_width']
        self.r_step = self.params['r_step']
        self.theta0 = self.params['theta0']
        self.theta1 = self.params['theta1']

    @classmethod
    def get_params_info(cls):
        return dict(
            layer='None',
            r_out='None',
            r_width='None',
            r_step='Distance between adjacent points defining a polygon',
            theta0='Start angle in deg',
            theta1='End angle in deg'
        )

    @classmethod
    def get_default_param_values(cls):
        return dict(
            layer=None,
            r_out=None,
            r_width=None,
            r_step=0.01,
            theta0=0.0,
            theta1=360.0
        )

    def draw_layout(self) -> None:

        theta0_rad = self.theta0 * pi / 180
        theta1_rad = self.theta1 * pi / 180

        alpha_step = self.r_step / self.r_out
        number_of_points = int(abs((theta1_rad-theta0_rad)) / alpha_step)

        # Generating outer_radius points
        alpha = np.linspace(theta0_rad, theta1_rad, number_of_points)
        x = self.r_out * np.cos(alpha)
        y = self.r_out * np.sin(alpha)
        outer_radius_points = [(x[i], y[i]) for i in range(len(x))]

        # Generating inner radius points
        r_in = self.r_out - self.ring_width
        # assert r_in >= 0, "Width of the ring is larger than outer radius. This is not physical."
        if r_in>0:
            alpha = np.linspace(theta1_rad, theta0_rad, number_of_points)
            x = r_in * np.cos(alpha)
            y = r_in * np.sin(alpha)
            inner_radius_points = [(x[i], y[i]) for i in range(len(x))]
        else:
            inner_radius_points = []

        all_points = inner_radius_points + outer_radius_points  #

        polygon = PhotonicPolygon(resolution=self.grid.resolution, layer=self.layer, points=all_points)

        self.add_obj(polygon)


def test_simple_round():
    spec_file = 'Photonic_Layout_45SPCLO/SimpleRound/specs/simple_round.yaml'
    plm = BPG.PhotonicLayoutManager(spec_file)
    plm.generate_content()
    plm.generate_gds()
