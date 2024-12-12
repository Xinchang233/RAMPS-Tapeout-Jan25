# this is the symmetric case of the other WgBend
import BPG
from BPG.objects import PhotonicPolygon
import numpy as np
from numpy import pi
from copy import deepcopy


class SimpleWgBend2(BPG.PhotonicTemplateBase):
    """
    Class that generates a bent waveguide with fixed width (in the 1st quadrant?)

    Parameters
    ----------
    r : float
        radius of the waveguide to be drawn
    width : float
        width of the waveguide to be drawn
    layer : str
        layer of the waveguide to be drawn
    port_layer : str
        layer of the port to be drawn
    """
    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)

        # Assign parameters
        self.r = self.params['r']
        self.width = self.params['width']
        self.layer = self.params['layer']
        self.port_layer = self.params['port_layer']


    @classmethod
    def get_params_info(cls) -> dict:
        return dict(
            r='radius for the bend',
            width='width of the waveguide to be drawn',
            layer='Layer or LPP on which to draw the waveguide',
            port_layer='Layer or LPP on which to draw the ports'
        )

    def draw_layout(self) -> None:
        self.draw_bend()
        self.create_ports()

    def draw_bend(self) -> None:
        """ copied from layout/SimpleRound """
        theta0_rad = 180.0 * pi / 180
        theta1_rad = 270.0 * pi / 180

        # alpha_step = self.r_step / self.r_out
        alpha_step = 0.01 / self.r
        number_of_points = int(abs((theta1_rad-theta0_rad)) / alpha_step)

        # Generating outer_radius points
        alpha = np.linspace(theta0_rad, theta1_rad, number_of_points)
        x = self.r * np.cos(alpha)
        y = self.r * np.sin(alpha)
        outer_radius_points = [(x[i], y[i]) for i in range(len(x))]

        # Generating inner radius points
        r_in = self.r - self.width
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

    def create_ports(self) -> None:
        """
        Places ports at the beginning and end of the waveguide
        """
        self.add_photonic_port(
            name='PORT_IN',
            center=(-self.r + self.width/2, 0),
            orient='R270',
            width=self.width,
            layer=self.port_layer,
            resolution=self.grid.resolution,
            unit_mode=False,
            show=True
        )

        self.add_photonic_port(
            name='PORT_OUT',
            center=(0, -self.r + self.width/2),
            orient='R180',
            width=self.width,
            layer=self.port_layer,
            resolution=self.grid.resolution,
            unit_mode=False,
            show=True
        )
