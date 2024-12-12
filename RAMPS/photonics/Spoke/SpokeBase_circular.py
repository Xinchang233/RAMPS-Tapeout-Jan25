import BPG
import warnings
import math


class SpokeBase(BPG.PhotonicTemplateBase):
    """
    This class generates a series of radially symmetric spokes.
    The spokes are straight-edged.
    Inner radius and outer radius are calculated at the angular boundaries of the spoke.
    The center of the tangent-to-a-circle edges of the spoke will be closer to the center of the circle.

    Parameters
    ----------
    rout : float
        Outer radius of spoke [um]
    rin : float
        Inner radius of spoke [um]
    num : int
        Number of spokes in a complete circle
    spoke_width_percentage : float
        Duty cycle of spoke within each radial slice. spoke_width_percentage of 1.0 fills half the spoke
        (ie, you will get a fully closed box with spoke_width_percentage = 2.0)
    spoke_offset : float
        offset angle of the center of the first spoke in fractions of 2PI/num radians
    layer : str
        layer to draw the spoke on
    """
    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)
        self.rout = self.params['rout']
        self.rin = self.params['rin']
        self.num = self.params['num']
        self.spk_wdth_pct = self.params['spoke_width_percentage']
        self.spk_offset = self.params['spoke_offset']
        self.layer = self.params['layer']

        # Check parameter validity
        if self.rout < self.rin:
            raise ValueError('Outer radius must be larger than inner radius')

        if self.rin < 0:
            warnings.warn("Inner radius is specified less than 0. Setting to rin=0", SyntaxWarning)
            self.rin = 0

    @classmethod
    def get_params_info(cls):  # Returns definition of the parameters.
        return dict(
            rout='Outer radius of spoke [um]',
            rin='Inner radius of spoke [um]',
            num='Number of spokes in a complete circle [int]',
            spoke_width_percentage='Percentage of uniformly divided width that spoke should occupy',
            spoke_offset='Offset angle of center of the first spoke, in fractions of 2pi/num radians.'
                         'Ex) spoke_offset=1.0 is equivalent to spoke_offset=0.'
                         'Ex) spoke_offset=0.5 will offset the spokes half-way to the next original spoke.',
            layer='Layer / LPP to draw spokes on',
        )

    def draw_layout(self):
        delta_theta = math.pi * 2 / self.num

        for i in range(self.num):
            theta0 = delta_theta * (i + self.spk_offset)
            theta_min = (theta0 - 0.25 * delta_theta * self.spk_wdth_pct)*180/math.pi
            theta_max = (theta0 + 0.25 * delta_theta * self.spk_wdth_pct)*180/math.pi

            ring = self.add_round(
                layer=self.layer,
                resolution=self.grid.resolution,
                rout=self.rout,
                rin=self.rin,
                theta0=theta_min,
                theta1=theta_max,
            )
            self.add_obj(ring)
