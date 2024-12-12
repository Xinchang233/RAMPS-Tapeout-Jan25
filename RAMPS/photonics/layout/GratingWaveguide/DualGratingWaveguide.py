import BPG
import numpy as np
from bag.layout.util import BBox

class DualGratingWaveguide(BPG.PhotonicTemplateBase):
    """
    This class generates a straight waveguide with dual layer gratings.

    The gratings directly above the waveguide are referred to as the first gratings.
    The gratings above the first gratings are referred to as the second gratings.

    Along the waveguide, the gratings are organized into cells, with each cell
    consisting of the waveguide and a single tooth from each grating.

    Parameters
    ----------
    length: float
        Length of the straight waveguide
    period: float
        Pitch of the cells
    first_grat: boolean
        True if the first gratings exist
    second_grat: boolean
        True if the second gratings exist

    wg_width: float
        Width of the straight waveguide

    """
    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)

        # Initialize the variables and dictionary of parameters.
        self.length = self.params['length']
        self.period = self.params['period']

        self.box_layers = self.params['box_layers']
        self.box_ex_width = self.params['box_ex_width']

        # Waveguide parameters
        self.wg_layer = self.params['wg_layer']
        self.wg_width = self.params['wg_width']

        # First grating parameters, if the layer exists
        self.first_grat = self.params['first_grat']
        self.first_grat_layer = self.params['first_grat_layer']
        self.first_grat_width = self.params['first_grat_width']
        self.first_duty_cycle = self.params['first_duty_cycle']
        self.first_offset_ratio = self.params['first_offset_ratio']
        if not 0 <= self.first_duty_cycle <= 1:
            raise ValueError('Duty cycle must be between 0 and 1')

        if not -1 <= self.first_offset_ratio <= 1:
            raise ValueError('Offset ratio must be between -1 and 1')

        if (self.first_offset_ratio + self.first_duty_cycle)*self.period > self.period:
            raise ValueError('Offset ratio is too high')

        # Second grating parameters, if the layer exists
        self.second_grat = self.params['second_grat']
        self.second_grat_layer = self.params['second_grat_layer']
        self.second_grat_width = self.params['second_grat_width']
        self.second_duty_cycle = self.params['second_duty_cycle']
        self.second_offset_ratio = self.params['second_offset_ratio']
        if not 0 <= self.second_duty_cycle <= 1:
            raise ValueError('Duty cycle must be between 0 and 1')

        if not -1 <= self.second_offset_ratio <= 1:
            raise ValueError('Offset ratio must be between -1 and 1')

        if (self.second_offset_ratio + self.second_duty_cycle) * self.period > self.period:
            raise ValueError('Offset ratio is too high')

        # Parameter checking: Make sure parameters are valid type and values
        if any(val <= 0 for val in [ self.length,
                                     self.period,
                                     self.wg_width,
                                     self.first_grat_width,
                                     self. second_grat_width]):
            raise ValueError('Width, length, teeth_width, period, and duty_cycle must be >0')

    @classmethod
    def get_params_info(cls):
        return dict(
            length = 'Length of waveguide',
            period = 'Pitch of grating teeth',

            box_layers = 'Layers for surrounding box(es)',
            box_ex_width = 'Extra width surrounding the grating waveguide to be occupied by the box layer shapes',

            wg_layer = 'Layer for the waveguide',
            wg_width = 'Width of waveguide',

            first_grat='Boolean setting whether to add first grating layer',
            first_grat_layer= 'Layer for the first grating teeth',
            first_grat_width = 'Width of first grating teeth',
            first_duty_cycle = 'Proportion of the period occupied by first grating teeth',
            first_offset_ratio = 'RRatio of the first grating tooth offset from the left edge of the cell to the period',

            second_grat='Boolean setting whether to add second grating layer',
            second_grat_layer = 'Layer for the second grating teeth',
            second_grat_width = 'Width of the second grating teeth',
            second_duty_cycle = 'Proportion of the period occupied by second grating teeth',
            second_offset_ratio = 'Ratio of the second grating tooth offset from the left edge of the cell to the period'
        )

    @classmethod
    def get_default_params_values(cls):
        return dict(
            length = None,
            period = None,

            box_layers = None,
            box_ex_width = None,

            wg_layer = None,
            wg_width = None,

            first_grat=None,
            first_grat_layer = None,
            first_grat_width = None,
            first_duty_cycle = None,
            first_offset_ratio = None,

            second_grat=None,
            second_grat_layer = None,
            second_grat_width = None,
            second_duty_cycle = None,
            second_offset_ratio = None
        )

    def draw_layout(self):
        self.create_ports()
        self.draw_waveguide()

        if self.first_grat:
            self.draw_gratings(layer = self.first_grat_layer,
                               width = self.first_grat_width,
                               duty_cycle = self.first_duty_cycle,
                               offset_ratio = self.first_offset_ratio)

        if self.second_grat:
            self.draw_gratings(layer = self.second_grat_layer,
                               width = self.second_grat_width,
                               duty_cycle = self.second_duty_cycle,
                               offset_ratio = self.second_offset_ratio)

        self.draw_box_layers()


    def create_ports(self) -> None:
        """
        Place ports at the input and output of the cosine waveguide
        """
        self.add_photonic_port(
            name='PORT0',
            center=(0.0, 0.0),
            orient='R0',
            width=self.wg_width,
            layer=self.wg_layer,
            overwrite_purpose=False,
            resolution=self.grid.resolution,
            unit_mode=False,
            show=False
        )

        self.add_photonic_port(
            name='PORT1',
            center=(self.length, 0.0),
            orient='R180',
            width=self.wg_width,
            layer=self.wg_layer,
            overwrite_purpose=False,
            resolution=self.grid.resolution,
            unit_mode=False,
            show=False
        )

    def draw_waveguide(self):
        self.add_rect(layer = self.wg_layer,
                      bbox = BBox(left = 0.0,
                                  bottom = -0.5 * self.wg_width,
                                  right = self.length,
                                  top = 0.5 * self.wg_width,
                                  resolution = self.grid.resolution))

    def draw_gratings(self, layer, width, duty_cycle, offset_ratio):
        n_teeth = int(np.floor(self.length / self.period))
        current_x = self.length % self.period

        tooth_length = duty_cycle * self.period
        offset = offset_ratio * self.period

        for tooth in range(n_teeth):
            self.add_rect(layer = layer,
                          bbox = BBox(left = current_x + offset,
                                      bottom = -0.5 * width,
                                      right = tooth_length + current_x + offset,
                                      top = 0.5 * width,
                                      resolution = self.grid.resolution))
            current_x += self.period


    def draw_box_layers(self):

        box_list = []
        box_list.append({
            'layer': self.box_layers,
            'width': self.wg_width + 2*self.box_ex_width,
            'length': self.length + 2*self.box_ex_width,
            'left_edge': -self.box_ex_width
        })

        for rect in box_list:
            self.add_rect(layer = rect['layer'],
                          bbox = BBox(left = rect['left_edge'],
                                      bottom = -0.5 * rect['width'],
                                      right = rect['length'] + rect['left_edge'],
                                      top = 0.5 * rect['width'],
                                      resolution = self.grid.resolution))
