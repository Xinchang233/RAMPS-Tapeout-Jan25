import BPG
from layout.FixedPhotonicPath.FixedPhotonicPath import FixedPhotonicPath


class WireBase(BPG.PhotonicTemplateBase):
    """
    Class that generates an arbitrarily shaped and constant width wire given a list of points

    Parameters
    ----------
    width : float
        width of the waveguide to be drawn
    layer : str
        layer of the waveguide to be drawn
    points : list
        list of (x,y) coordinates denoting the center of the waveguide
    """
    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)

        # Initialize the variables and dictionary of parameters.
        self.width = self.params['width']
        self.layer = self.params['layer']
        self.points = self.params['points']
        self.path = None

        # Parameter checking: Make sure parameters are valid type and values
        if any(val <= 0 for val in [self.width]):
            raise ValueError("The width cannot be zero or negative")

        if any(not isinstance(val, (int, float)) for val in [self.width]):
            raise ValueError('Width must be int or float')

    @classmethod
    def get_params_info(cls) -> dict:
        return dict(
            width='width of the waveguide',
            layer='Layer or LPP on which to draw the waveguide',
            points='List of (x, y) tuples defining the center of the waveguide',
        )

    def draw_layout(self) -> None:
        self.create_path()

    def create_path(self) -> None:
        """
        Generates a PhotonicPath object from the provided list of points and adds it to the db
        """
        self.path = FixedPhotonicPath(
            resolution=self.grid.resolution,
            layer=self.layer,
            width=self.width,
            points=self.points,
            unit_mode=False,
        )
        self.add_obj(self.path)


    # Ports cause problems with dataprep--text not allowed on gds
    # def create_ports(self) -> None:
    #     """
    #     Places ports at the beginning and end of the waveguide
    #     """
    #     self.add_photonic_port(
    #         name='PORT0',
    #         center=self.points[0],
    #         orient='R0',
    #         width=self.width,
    #         layer=self.layer,
    #         resolution=self.grid.resolution,
    #         unit_mode=False,
    #         show=False
    #     )
    #
    #     self.add_photonic_port(
    #         name='PORT1',
    #         center=self.points[-1],
    #         orient='R180',
    #         width=self.width,
    #         layer=self.layer,
    #         resolution=self.grid.resolution,
    #         unit_mode=False,
    #         show=False
    #     )
