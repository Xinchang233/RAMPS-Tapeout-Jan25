import BPG
from BPG.objects import PhotonicPath
import numpy as np


class CosineWaveguide(BPG.PhotonicTemplateBase):
    """
    This class generates a waveguide layout with constant width that follows a cosine bend pattern.

    Parameters
    ----------
    width : float
        width of the waveguide to be drawn
    amplitude: float
        total distance between the top and bottom of the bend shape
    wavelength: float
        length of the cosine shape to be drawn
    start_quarter_angle : float
        starting angle (in PI/2 units) of the cosine
    end_quarter_angle : float
        ending angle (in PI/2 units) of the cosine
    """

    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)

        # Initialize the variables and dictionary of parameters.
        self.width = self.params['width']
        self.amp = self.params['amplitude']
        self.wavelength = self.params['wavelength']
        self.layer = self.params['layer']
        self.start = self.params['start_quarter_angle']
        self.end = self.params['end_quarter_angle']

        # Dynamically default error_tolerance to be the grid/2
        if self.params['error_tolerance'] is None:
            self.error_tolerance = self.grid.resolution / 5
        else:
            self.error_tolerance = self.params['error_tolerance']

        self.path = None
        self.points = None

        # Parameter checking: Make sure parameters are valid type and values
        if any(val <= 0 for val in [self.width, self.amp, self.wavelength]):
            raise ValueError("The width, amplitude, and wavelength cannot be zero or negative")

        if any(not isinstance(val, (int, float)) for val in [self.width, self.amp, self.wavelength]):
            raise ValueError('Width, amplitude, wavelength must be int or float')

    @classmethod
    def get_default_param_values(cls):
        return dict(
            error_tolerance=None,
        )

    @classmethod
    def get_params_info(cls):
        return dict(
            width='width of the waveguide',
            amplitude='Amplitude (0-pk) of the cosine defining this waveguide shape',
            wavelength='Wavelength of the cosine defining this waveguide shape',
            layer='Layer or LPP on which to draw the waveguide',
            start_quarter_angle='Starting angle (in PI/2 units) of the cosine',
            end_quarter_angle='Ending angle (in PI/2 units) of the cosine',
            error_tolerance='Tolerance with which the ideal cosine is approximated. Defaults to self.grid.resolution/2'
        )

    def draw_layout(self) -> None:
        self.create_point_list()
        self.create_path()
        self.create_ports()
        self.add_obj(self.path)

    def create_point_list(self) -> None:
        """
        Defines the points representing the path segments to be drawn
        """
        # If cos(x) \approx 1 - x^2   -->    A*cos(2Pi/lambda * x) \approx A(1 - ((2Pi/lambda) * x)^2
        # The biggest error occurs at the smallest radius of curvature, ie at x=0, at which we want to find
        # dx such that a linear approximation from the ideal cosine deviates by no more than eps
        # A - A(1 - ((2Pi/lambda) * x)^2 = A(2Pi/lambda)^2 x^2 < eps   -->  x < (lambda/2Pi) * sqrt(eps/A)
        dx = (self.wavelength/(2*np.pi)) * np.sqrt(self.error_tolerance/self.amp)

        start = self.start/4 * self.wavelength
        end = self.end/4 * self.wavelength
        num = (end - start )/dx
        # For a linear space
        x = np.linspace(start=start, stop=end, num=num, endpoint=True)
        # Insert points just next to the ends to ensure that the ends are at right angles
        x = np.insert(x, 1, x[0] + (x[1] - x[0])/100)  # self.grid.resolution)
        x = np.insert(x, -1, x[-1] - (x[-1] - x[-2])/100)  # self.grid.resolution)

        y = self.amp * np.cos(2 * np.pi * x / self.wavelength)
        self.points = [(x[ind], y[ind]) for ind in range(x.shape[0])]

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
            show=False,
        )

        self.add_photonic_port(
            name='PORT1',
            center=self.points[-1],
            orient='R180',
            width=self.width,
            layer=self.layer,
            overwrite_purpose=False,
            resolution=self.grid.resolution,
            unit_mode=False,
            show=False,
        )


if __name__ == '__main__':
    spec_file = 'Photonic_Core_Layout/WaveguideBase/specs/cosine_waveguide.yaml'
    plm = BPG.PhotonicLayoutManager(spec_file)
    plm.generate_template()
    plm.generate_content()
    plm.generate_gds()
    plm.generate_flat_content()
    plm.generate_flat_gds()
