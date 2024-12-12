import BPG
from BPG.objects import PhotonicPath
import numpy as np
from bag.layout.util import BBox


class GratingWaveguide(BPG.PhotonicTemplateBase):
    """
    This class generates a straight waveguide with a sidewall or overclad grating

    Parameters
    ----------
    width : float
        Width of waveguide
    teeth_width : float
        Width of grating teeth
    length : float
        Length of waveguide
    period : float
        Pitch of grating teeth
    duty_cycle : float
        Proportion of period occupied by grating teeth
    layer : Union[str, Tuple[str, str]]
        The layer or LPP on which to draw the waveguide
    grating_layer : Union[str, Tuple[str, str]]
        The layer or LPP on which to draw the grating teeth
    box_layers : Tuple [str, str] list
        The layers or LPPs on which to draw surrounding box(es)
    box_ex_width : float
        The extra width surrounding the grating waveguide to be occupied by the box_layers shapes

    """

    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)

        # Initialize the variables and dictionary of parameters.
        self.width = self.params['width']
        self.teeth_width = self.params['teeth_width']
        self.length = self.params['length']
        self.period = self.params['period']
        self.duty_cycle = self.params['duty_cycle']
        self.layer = self.params['layer']
        self.grating_layer = self.params['grating_layer']
        self.box_layers = self.params['box_layers']
        self.box_ex_width = self.params['box_ex_width']

        self.path = None
        self.points = None

        # Parameter checking: Make sure parameters are valid type and values
        if any(val <= 0 for val in [self.width, self.length, self.teeth_width, self.period, self.duty_cycle]):
            raise ValueError('Width, length, teeth_width, period, and duty_cycle must be >0')

        if self.duty_cycle >= 1:
            raise ValueError('duty_cycle must be 0<duty_cycle<1')

    @classmethod
    def get_params_info(cls):
        return dict(
            width = 'Width of waveguide',
            teeth_width = 'Width of grating teeth',
            length = 'Length of waveguide',
            period = 'Pitch of grating teeth',
            duty_cycle = 'Proportion of period occupied by grating teeth',
            layer = 'The layer or LPP on which to draw the waveguide',
            grating_layer = 'The layer or LPP on which to draw the grating teeth',
            box_layers = 'The layers or LPPs on which to draw surrounding box(es)',
            box_ex_width = 'The extra width surrounding the grating waveguide to be occupied by the box_layers shapes'
        )

    @classmethod
    def get_default_params_values(cls):
        return dict(
            width = None,
            teeth_width = None,
            length = None,
            period = None,
            duty_cycle = None,
            layer = None,
            grating_layer = None,
            box_layers = None,
            box_ex_width = None
        )

    def draw_layout(self) -> None:
        self.create_ports()
        rect_list = self.gen_rect_list()
        self.draw_rect_list(rect_list)
        self.draw_box_layers()

    def draw_box_layers(self) -> None:

        box_list = []
        box_list.append({
            'layer': self.box_layers,
            'width': self.width+2*self.box_ex_width,
            'length': self.length+2*self.box_ex_width,
            'left_edge': -self.box_ex_width
        })

        for rect in box_list:
            self.add_rect(layer=rect['layer'],
                          bbox=BBox(left=rect['left_edge'],
                                    bottom=-.5 * rect['width'],
                                    right=rect['length'] + rect['left_edge'],
                                    top=.5 * rect['width'],
                                    resolution=self.grid.resolution))


    def gen_rect_list(self):
        n_teeth = int(np.floor(self.length/self.period))
        current_x = self.length % self.period

        # Grating waveguide rectangle
        rect_list = []
        rect_list.append({
                'layer': self.layer,
                'width': self.width,
                'length': self.length,
                'left_edge': 0.0
            })

        # Add grating teeth
        for count in range(n_teeth):

            rect_list.append({
                'layer': self.grating_layer,
                'width': self.teeth_width,
                'length': self.duty_cycle*self.period,
                'left_edge': current_x
            })
            current_x += self.period

        return rect_list

    def draw_rect_list(self, rect_list):
        for rect in rect_list:
            self.add_rect(layer=rect['layer'],
                          bbox=BBox(left=rect['left_edge'],
                                    bottom=-.5 * rect['width'],
                                    right=rect['length'] + rect['left_edge'],
                                    top=.5 * rect['width'],
                                    resolution=self.grid.resolution))


    def create_ports(self) -> None:
        """
        Place ports at the input and output of the cosine waveguide
        """
        self.add_photonic_port(
            name='PORT0',
            center=(0.0,0.0),
            orient='R0',
            width=self.width,
            layer=self.layer,
            overwrite_purpose=False,
            resolution=self.grid.resolution,
            unit_mode=False,
            show=False
        )


        self.add_photonic_port(
            name='PORT1',
            center=(self.length,0.0),
            orient='R180',
            width=self.width,
            layer=self.layer,
            overwrite_purpose=False,
            resolution=self.grid.resolution,
            unit_mode=False,
            show=False
        )


if __name__ == '__main__':
    spec_file = 'Photonic_Layout_45SPCLO/GratingWaveguide/specs/gratwg.yaml'
    plm = BPG.PhotonicLayoutManager(spec_file)
    plm.generate_content()
    plm.generate_gds()
    plm.generate_flat_content()
    plm.generate_flat_gds()
