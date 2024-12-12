import BPG
from BPG.objects import PhotonicPath
import numpy as np


class PathWaveguide(BPG.PhotonicTemplateBase):
    """
    Abstract class for waveguides with coordinates defined in create_point_list.
    """

    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)

        # Initialize the variables and dictionary of parameters.
        self.width = self.params['width']
        self.layer = self.params['layer']

        self.path = None
        self.points = None

        # Parameter checking: Make sure parameters are valid type and values
        if any(val <= 0 for val in [self.width]):
            raise ValueError("The width, amplitude, and wavelength cannot be zero or negative")
        if any(not isinstance(val, (int, float)) for val in [self.width]):
            raise ValueError('Width, amplitude, wavelength must be int or float')

    @classmethod
    def get_default_param_values(cls):
        pass

    def draw_layout(self) -> None:
        self.create_point_list()
        self.create_path()
        self.create_ports()
        self.add_obj(self.path)

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
        )

        # print('In PathWaveguide: ')
        # print([p[0] for p in self.path._polygon_points_unit])

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

        self.add_photonic_port(
            name='PORT1',
            center=self.points[-1],
            orient='R180',
            width=self.width,
            layer=self.layer,
            overwrite_purpose=False,
            resolution=self.grid.resolution,
            unit_mode=False,
            show=True,
        )
