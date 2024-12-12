import abc
import BPG


class TaperBase(BPG.PhotonicTemplateBase, metaclass=abc.ABCMeta):
    """
    Base class for tapers. It holds the common baseline parameters and methods that all tapers
    should inherit. The class itself is just a placeholder - it does not actually draw a layout.
    Use this class as a template for creating generic testbenches.

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
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)

    @classmethod
    def get_params_info(cls):
        return dict(
            width0='width of the first photonic port',
            width1='width of the second photonic port',
            length='distance between the photonics ports',
            layer='layer on which to draw the taper'
        )

    @abc.abstractmethod
    def draw_layout(self):
        pass

    def create_ports(self, w_left, w_right, length, layer):
        """
        Add PORT0 to the left edge and add PORT1 to the right edge
        """
        self.add_photonic_port(
            name='PORT0',
            center=(0, 0),
            orient='R0',
            width=w_left,
            layer=layer,
            resolution=self.grid.resolution,
            unit_mode=False,
            show=False
        )

        self.add_photonic_port(
            name='PORT1',
            center=(length, 0),
            orient='R180',
            width=w_right,
            layer=layer,
            resolution=self.grid.resolution,
            unit_mode=False,
            show=False
        )

        # also calculate length
        self.length = abs( self.get_photonic_port(port_name='PORT1').center[1] - self.get_photonic_port(port_name='PORT0').center[0] )

    # end create_ports()


    def parameter_bounds_check(self, w_left, w_right, length):
        """ Given the widths and lengths of the taper, determine if a valid design can be drawn """
        if any(val <= 0 for val in [w_left, w_right, length]):
            raise ValueError("The widths, distance between ports or the number of tapers can not "
                             "be zero or negative!")

        for val in [w_left, w_right, length]:
            if not isinstance(val, (int, float)):
                raise ValueError('Origin, widths, and length must be int or float')
