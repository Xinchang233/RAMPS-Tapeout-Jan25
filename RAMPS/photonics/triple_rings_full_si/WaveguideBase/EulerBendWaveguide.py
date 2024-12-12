import BPG
from BPG.objects import PhotonicPath
import numpy as np
from scipy.special import fresnel


class EulerBendWaveguide(BPG.PhotonicTemplateBase):
    """
    This class generates a waveguide bend layout with parameterized Euler-circular-Euler bend.

    Parameters
    ----------
    width : float
        width of the waveguide to be drawn
    radius : float
        Effective radius of the euler-circular-euler bend
    theta_deg : float
        The angle (in degrees) that the bend will span
    euler_percent : float
        Percentage of bend length that is an Euler curve. Must be 0 <= euler_percent <= 1
    layer : Union[str, Tuple[str, str]]
        The layer or LPP on which to draw the bend

    Optional Parameters
    -------------------
    num : int
        Number of points that will be used to approximate the bend. Defaults to radial accuracy of 10*grid resolution
    num_iterations: int
        Number of iterations used to find the ideal Euler bend. Defaults to 10
    error_tolerance : float
        Tolerance below which two bends in the iteration are considered to be the same. Defaults to 0.01 (1%)
    """

    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)

        # Initialize the variables and dictionary of parameters.
        self.width = self.params['width']
        self.radius = self.params['radius']
        self.layer = self.params['layer']
        self.theta_deg = self.params['theta_deg']
        self.theta = self.theta_deg * np.pi/180
        self.euler_percent = self.params['euler_percent']

        self.num = self.params['num']

        self.error_tolerance = self.params['error_tolerance']
        self.num_iterations = self.params['num_iterations']

        # Clean up euler_percent to avoid divide by 0
        if self.euler_percent == 0:
            self.euler_percent = np.finfo(float).eps
        self.gamma = 1 / (1 - 0.5 * self.euler_percent)

        # Dynamically default the number of points so that points are separated by at least 10 grid resolutions
        if self.num is None:
            self.num = round(self.radius * self.theta / (10 * self.grid.resolution))

        self.path = None
        self.points = None

        # Parameter checking: Make sure parameters are valid type and values
        if any(val <= 0 for val in [self.width, self.radius, self.theta]):
            raise ValueError('The width, radius, theta cannot be zero or negative')

        if 0.5*self.width > self.radius:
            raise ValueError(f'Width over two must be less than the bend radius to avoid self-intersecting path.')

        if not np.isclose(self.theta_deg, 90):
            raise ValueError(f'Only 90 degree Euler-Circle-Euler bends are currently supported')

    @classmethod
    def get_default_param_values(cls):
        return dict(
            num=None,
            error_tolerance=0.01,
            num_iterations=10,
        )

    @classmethod
    def get_params_info(cls):
        return dict(
            width='width of the waveguide to be drawn',
            radius='Effective radius of the euler-circular-euler bend',
            theta_deg='The angle (in degrees) that the bend will span',
            euler_percent='Percentage of bend length that is an Euler curve. Must be 0 <= euler_percent <= 1',
            layer='The layer or LPP on which to draw the bend',
            num='Number of points that will be used to approximate the bend. Defaults to radial accuracy of 10*grid '
                'resolution',
            num_iterations='Number of iterations used to find the ideal Euler bend. Defaults to 10',
            error_tolerance='Tolerance below which two bends in the iteration are considered to be the same. '
                            'Defaults to 0.01 (1%)',
        )

    def draw_layout(self) -> None:
        self.create_point_list()
        self.create_path()
        self.create_ports()
        self.add_obj(self.path)

    def create_point_list(self):
        x, y = self.iterate_bend_coords()

        # Insert points adjacent to the ends to ensure that the port is angled properly.
        x = np.insert(x, 1, (x[1] - x[0]) / 100)
        y = np.insert(y, 1, 0)

        # TODO: When any angle is supported, calculate the vector here.
        x = np.insert(x, -1, x[-1])
        y = np.insert(y, -1, y[-1] - (y[-1] - y[-2]) / 100)

        self.points = [(x[ind], y[ind]) for ind in range(x.shape[0])]

    def iterate_bend_coords(self):
        """
        Derived from:
        R. N. and F. H. Peters, “Bends in the Plane with Variable Curvature,”
        Bull. Irish Math. Soc., vol. 78, no. 78, pp. 61–80, 2016.
        Parameters
        ----------
        theta
        num
        tol

        Returns
        -------

        """
        x_points = None
        y_points = None

        n_iter = 0

        bend_length = self.radius * self.theta
        x_end = self.radius * np.sin(self.theta)
        y_end = self.radius * (1 - np.cos(self.theta))


        while n_iter < self.num_iterations:
            bend_length_old = bend_length

            x_points, y_points = self.define_bend_coords(bend_length_target=bend_length)
            x_scale = x_end / x_points[-1]
            y_scale = y_end / y_points[-1]

            x_points = x_scale * x_points
            y_points = y_scale * y_points

            bend_length = self.calculate_euclidean_dist(x_points, y_points)

            if (bend_length - bend_length_old)/bend_length_old < self.error_tolerance:
                break
            else:
                n_iter += 1

        return x_points, y_points

    def define_bend_coords(self,
                           bend_length_target,
                           ):
        """
        Derived from:
        R. N. and F. H. Peters, “Bends in the Plane with Variable Curvature,”
        Bull. Irish Math. Soc., vol. 78, no. 78, pp. 61–80, 2016.

        Parameters
        ----------
        bend_length_target

        Returns
        -------

        """

        radius_effective = bend_length_target / self.theta
        k_t = self.gamma / radius_effective

        alpha_t = k_t ** 2 / (k_t * bend_length_target - self.theta)
        s_points = np.linspace(0, bend_length_target, num=self.num)

        x_points = np.zeros(np.size(s_points))
        y_points = np.zeros(np.size(s_points))

        # Position parameters
        sigma = k_t / alpha_t
        nu = bend_length_target - sigma

        # S regions for the Euler, circular, and Euler sections
        s_region_euler1 = s_points <= sigma
        s_region_euler2 = s_points >= nu
        s_region_circular = np.logical_not(np.logical_or(s_region_euler1, s_region_euler2))

        d1 = np.sqrt(np.pi / alpha_t)
        d2 = k_t / np.sqrt(np.pi * alpha_t)
        d3 = k_t * bend_length_target - np.power(k_t, 2) / alpha_t
        d4 = k_t * bend_length_target - (3 * np.power(k_t, 2) / (2 * alpha_t))

        # Fresnel cos and sin
        fres_sin__s_d1, fres_cos__s_d1 = fresnel(s_points / d1)

        # Fresnel cos and sin at d2
        fres_sin_d2, fres_cos_d2 = fresnel(d2)

        # Fresnel cos and sin of (s - L_tc)/d1
        fres_sin_q, fres_cos_q = fresnel((s_points - bend_length_target) / d1)

        p_x = (2 / k_t * np.sin(0.5 * (k_t * s_points - (np.power(k_t, 2) / alpha_t))) * np.cos(0.5 * k_t * s_points)
               + d1 * fres_cos_d2)

        q_x = (d1 * (np.cos(d3) * (fres_cos_q + fres_cos_d2) + np.sin(d3) * (fres_sin_q + fres_sin_d2))
               + 1 / k_t * np.sin(d4) - 1 / k_t * np.sin(np.power(k_t, 2) / (2 * alpha_t)) + d1 * fres_cos_d2)

        p_y = (2 / k_t * np.sin(0.5 * (k_t * s_points - (np.power(k_t, 2) / alpha_t))) * np.sin(0.5 * k_t * s_points)
               + d1 * fres_sin_d2)

        q_y = (d1 * (np.sin(d3) * (fres_cos_q + fres_cos_d2) - np.cos(d3) * (fres_sin_q + fres_sin_d2))
               - 1 / k_t * np.cos(d4) + 1 / k_t * np.cos(np.power(k_t, 2) / (2 * alpha_t)) + d1 * fres_sin_d2)

        x_points[s_region_euler1] = d1 * fres_cos__s_d1[s_region_euler1]
        y_points[s_region_euler1] = d1 * fres_sin__s_d1[s_region_euler1]

        x_points[s_region_euler2] = q_x[s_region_euler2]
        y_points[s_region_euler2] = q_y[s_region_euler2]

        x_points[s_region_circular] = p_x[s_region_circular]
        y_points[s_region_circular] = p_y[s_region_circular]

        return x_points, y_points

    @staticmethod
    def calculate_euclidean_dist(x_points, y_points):
        return np.sum(np.sqrt(np.power(np.diff(x_points), 2) + np.power(np.diff(y_points), 2)))

    def create_path(self) -> None:
        """
        Takes the list of points and generates a PhotonicPath shape
        """
        self.path = PhotonicPath(
            resolution=self.grid.resolution,
            layer=self.layer,
            width=self.width,
            points=self.points,
            unit_mode=False,
            eps=self.grid.resolution/10,
        )

    def create_ports(self) -> None:
        """
        Place ports at the input and output of the cosine waveguide
        """
        self.add_photonic_port(
            name='PORT0',
            center=self.points[0],
            orient='R0',
            width=self.width,
            layer=self.layer,
            overwrite_purpose=False,
            resolution=self.grid.resolution,
            unit_mode=False,
            show=True,
        )

        # TODO: Change this when anyangle is supported
        self.add_photonic_port(
            name='PORT1',
            center=self.points[-1],
            orient='R270',
            width=self.width,
            layer=self.layer,
            overwrite_purpose=False,
            resolution=self.grid.resolution,
            unit_mode=False,
            show=True,
        )


if __name__ == '__main__':
    spec_file = 'Photonic_Core_Layout/WaveguideBase/specs/euler.yaml'
    plm = BPG.PhotonicLayoutManager(spec_file)
    plm.generate_template()
    plm.generate_content()
    plm.generate_gds()
    plm.generate_flat_content()
    plm.generate_flat_gds()
