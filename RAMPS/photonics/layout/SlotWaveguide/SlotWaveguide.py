import BPG
from BPG.objects import PhotonicRect
from bag.layout.util import BBox


class SlotWaveguide(BPG.PhotonicTemplateBase):
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
        self.slot_width =self.params['slot_width']
        self.rail_width = self.params['rail_width']
        self.strip_width = self.params['strip_width']
        self.base_width = self.params['base_width']
        self.length = self.params['length']
        self.width = self.params['width']
        self.layer = self.params['layer']
        self.port_layer = self.params['port_layer']


    @classmethod
    def get_params_info(cls) -> dict:
        return dict(
            slot_width='',
            rail_width='',
            strip_width='',
            base_width='',
            length='length of the waveguide to be drawn',
            width='width of the waveguide to be drawn',
            layer='Layer or LPP on which to draw the waveguide',
            port_layer='Layer or LPP on which to draw the ports'
        )

    def draw_layout(self) -> None:
        self.draw_wg()
        self.create_ports()

    def draw_wg(self) -> None:
        """ Draws the waveguide """
        rect = PhotonicRect(layer=self.layer,
                            bbox=BBox(left=0, right=self.length, bottom=self.slot_width/2, top=self.slot_width/2+self.rail_width,
                                      resolution=self.grid.resolution))


        self.add_obj(rect)

        rect1 = PhotonicRect(layer=self.layer,
                            bbox=BBox(left=0, right=self.length, bottom=-(self.slot_width/2+self.rail_width), top=-self.slot_width/2,
                                      resolution=self.grid.resolution))

        self.add_obj(rect1)


    def create_ports(self) -> None:
        """
        Places ports at the beginning and end of the waveguide
        """
        self.add_photonic_port(
            name='PORT_IN',
            center=(0, self.width/2),
            orient='R0',
            width=self.width,
            layer=self.port_layer,
            resolution=self.grid.resolution,
            unit_mode=False,
            show=True
        )

        self.add_photonic_port(
            name='PORT_OUT',
            center=(self.length, self.width/2),
            orient='R180',
            width=self.width,
            layer=self.port_layer,
            resolution=self.grid.resolution,
            unit_mode=False,
            show=True
        )
