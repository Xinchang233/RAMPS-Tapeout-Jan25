import BPG
from BPG.objects import PhotonicPolygon
from bag.layout.util import BBox


class SimpleTaper(BPG.PhotonicTemplateBase):
    """
    Class that generates a straight waveguide with fixed width

    Parameters
    ----------
    length : float
        length of the waveguide to be drawn
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
        self.length = self.params['length']
        self.widthI = self.params['widthI']
        self.widthO = self.params['widthO']
        self.layer = self.params['layer']
        self.port_layer = self.params['port_layer']


    @classmethod
    def get_params_info(cls) -> dict:
        return dict(
            length='length of the waveguide to be drawn',
            widthI='inport width of the waveguide to be drawn',
            widthO='outport width of the waveguide to be drawn',
            layer='Layer or LPP on which to draw the waveguide',
            port_layer='Layer or LPP on which to draw the ports'
        )

    def draw_layout(self) -> None:
        self.draw_tp()
        self.create_ports()

    def draw_tp(self) -> None:
        """ Draws the taper """
        plg = PhotonicPolygon(resolution=self.grid.resolution, layer = self.layer, points = [(0, self.widthI / 2), (0, -self.widthI / 2), (self.length, -self.widthO / 2), (self.length, self.widthO / 2)])
        self.add_obj(plg)

    def create_ports(self) -> None:
        """
        Places ports at the beginning and end of the waveguide
        """
        self.add_photonic_port(
            name='PORT_IN',
            center=(0, 0),
            orient='R0',
            width=self.widthI,
            layer=self.port_layer,
            resolution=self.grid.resolution,
            unit_mode=False,
            show=True
        )

        self.add_photonic_port(
            name='PORT_OUT',
            center=(self.length, 0),
            orient='R180',
            width=self.widthO,
            layer=self.port_layer,
            resolution=self.grid.resolution,
            unit_mode=False,
            show=True
        )
