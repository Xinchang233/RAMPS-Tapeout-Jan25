import BPG
from Taper.TaperBase import TaperBase


class LinearTaper(TaperBase):
    """
    This class generates a linear taper from width0 to width1 across a specified length.

    Ports
    -----
    - PORT0: port connected to the left side of the taper. Always set to (0, 0)
    - PORT1: port connected to the right side of the taper

    Parameters
    ----------
    width0 : float
        width of the side of the taper connected to PORT0
    width1: float
        width of the side of the taper connected to PORT1
    length: float
        length of the entire linear taper section
    layer : str
        layer that the taper will be placed on
    """

    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        TaperBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)

    @classmethod
    def get_params_info(cls):
        return dict(
            width0='width of the first photonic port',
            width1='width of the second photonic port',
            length='distance between photonic ports',
            layer='layer on which to draw the taper'
        )

    @classmethod
    def get_default_params_values(cls):
        return dict(
            width0 = None,
            width1 = None,
            length = None,
            layer=  None
        )

    def draw_layout(self):
        self.parameter_bounds_check(w_left=self.params['width0'],
                                    w_right=self.params['width1'],
                                    length=self.params['length'])
        self.create_taper()
        self.create_ports(w_right=self.params['width1'],
                          w_left=self.params['width0'],
                          length=self.params['length'],
                          layer=self.params['layer'])

    def create_taper(self):
        """
        Generate the polygon corresponding to the desired linear taper shape and add it to the db
        """
        self.add_polygon(
            layer=self.params['layer'],
            resolution=self.grid.resolution,
            points=[(0, -self.params['width0'] / 2),
                    (0, self.params['width0'] / 2),
                    (self.params['length'], self.params['width1'] / 2),
                    (self.params['length'], -self.params['width1'] / 2)],
            unit_mode=False,
        )
