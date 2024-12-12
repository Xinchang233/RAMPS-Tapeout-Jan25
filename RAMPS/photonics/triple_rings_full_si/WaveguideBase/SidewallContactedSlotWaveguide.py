import BPG
import warnings
import numpy as np
from bag.layout.util import BBox


class SidewallContactedSlotWaveguide(BPG.PhotonicTemplateBase):
    """
    This Class generates a straight section of slot waveguide with sidewall contacts

    Parameters
    ----------
    length : float
        length of the waveguide to be drawn
    core_width_in : float
        width of the core (the slot and the two rails on each side) at the input of the waveguide to be drawn
    core_width_out : float
        width of the core (the slot and the two rails on each side) at the output of the waveguide to be drawn
    slot_width_in : float
        width of the slot (gap between the two rails) on the input of the waveguide to be drawn
    slot_width_out : float
        width of the slot (gap between the two rails) on the output of the waveguide to be drawn
    draw_contact : bool
        determines if sidewall contacts are drawn or not
    contact_length_in : float
        length of the sidewall contacts on the input of the waveguide to be drawn
    contact_length_out : float
        length of the sidewall contacts on the output of the waveguide to be drawn
    contact_width : float
        width of the sidewall contats along the length of the waveguide to be drawn
    contact_period : float
        period of the sidewall contacts along the length of the waveguide to be drawn
    layer : str
        layer of the waveguide to be drawn
    """

    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)

        # Initialize the variables and dictionary of parameters.
        self.length = self.params['length']
        self.core_width_in = self.params['core_width_in']
        self.core_width_out = self.params['core_width_out']
        self.slot_width_in = self.params['slot_width_in']
        self.slot_width_out = self.params['slot_width_out']
        self.draw_contact = self.params['draw_contact']
        self.contact_length_in = self.params['contact_length_in']
        self.contact_length_out = self.params['contact_length_out']
        self.contact_linear = self.params['contact_linear']
        self.logorlin = self.params['logorlin']
        self.contact_width = self.params['contact_width']
        self.contact_period = self.params['contact_period']
        self.layer = self.params['layer']

        # Parameter checking: Make sure parameters are valid type and values
        if any(not isinstance(val, (int, float)) for val in [self.length, self.core_width_in, self.core_width_out,
                                                             self.slot_width_in, self.slot_width_out,
                                                             self.contact_length_in, self.contact_length_out,
                                                             self.contact_width, self.contact_period]):
            raise ValueError('Waveguide dimensions must be int or float')

        if self.length <= 0.0:
            raise ValueError("Length of the slot waveguide must be a positive number")

        if any([self.core_width_in < self.slot_width_in, self.core_width_out < self.slot_width_out]):
            raise ValueError("Width of the core of the waveguide must be larger than the slot width")

        if self.draw_contact and any([self.contact_length_in <= 0.0,
                                      self.contact_length_out <= 0.0,
                                      self.contact_width <= 0.0]):
            raise ValueError("Dimensions of the sidewall contacts must be positive.",
                             "Use option draw_contact = False if no sidewall contacts are needed")

        if self.draw_contact and self.contact_width > self.contact_period:
            raise ValueError("Width of the sidewall contacts must be less than or equal to contact period")

        if self.draw_contact and round(self.length / self.grid.resolution) \
                % round(self.contact_period / self.grid.resolution) != 0:
            warnings.warn("Length of the slot waveguide must be a multiple of contact period."
                          "Setting length = (length // contact_period + 1) * contact_period")
            self.length = (
                    (round(self.params['length'] / self.grid.resolution)
                     // round(self.params['contact_period'] / self.grid.resolution) + 1.0
                     ) * self.contact_period
            )

        # if self.draw_contact and self.core_width_in != self.core_width_out:
        #     warnings.warn("Sidewall contacts with tapered core are not supported. Setting draw_contact=False")
        #     self.draw_contact = False

        if self.slot_width_in < 0.0:
            warnings.warn("Slot width is specified less than 0. Setting slot_width_in = 0")
            self.slot_width_in = 0.0

        if self.slot_width_out < 0.0:
            warnings.warn("Slot width is specified less than 0. Setting slot_width_out = 0")
            self.slot_width_out = 0.0

    @classmethod
    def get_params_info(cls) -> dict:
        return dict(
            length='length of the sidewall contacted slot waveguide',
            core_width_in='width of the core of the sidewall contacted slot waveguide at the input',
            core_width_out='width of the core of the sidewall contacted slot waveguide at the output',
            slot_width_in='width of the slot at the input of the sidewall contacted slot waveguide',
            slot_width_out='width of the slot at the output of the sidewall contacted slot waveguide',
            draw_contact='boolean variable which turns on/off the sidewall contacts of the slot waveguide',
            contact_length_in='length of the contacts of the sidewall contacted slot waveguide',
            contact_length_out='length of the contacts of the sidewall contacted slot waveguide',
            contact_linear='"log" or "linear" tapering of the sidewall contacts',
            logorlin='parameter which determines how logarithmic or linear the taper is',
            contact_width='width of the contacts of the sidewall contacted slot waveguide',
            contact_period='period of the contacts of the sidewall contacted slot waveguide',
            layer='Layer or LPP on which to draw the waveguide',
        )

    def get_default_param_values(cls) -> dict:
        """
                Returns default parameters of moscap ring
                """
        return dict(
            contact_linear=True,
            logorlin=0.5,
        )

    def draw_layout(self) -> None:
        self.create_wg_rail()

        if self.draw_contact:
            self.create_tapered_contacts()

        self.create_ports()

    def create_wg_rail(self) -> None:
        """
        Create the rails of the slot waveguide
        """
        # add the top rail
        self.add_polygon(layer=self.layer,
                         points=[(0.0, self.slot_width_in / 2),
                                 (0.0, self.core_width_in / 2),
                                 (self.length, self.core_width_out / 2),
                                 (self.length, self.slot_width_out / 2),
                                 ],
                         resolution=self.grid.resolution)
        # add the bottom rail
        self.add_polygon(layer=self.layer,
                         points=[(0.0, -self.slot_width_in / 2),
                                 (0.0, -self.core_width_in / 2),
                                 (self.length, -self.core_width_out / 2),
                                 (self.length, -self.slot_width_out / 2),
                                 ],
                         resolution=self.grid.resolution)

    def create_tapered_contacts(self) -> None:
        """
        Create tapered array of sidewall contacts
        """
        num_contact = round(self.length / self.grid.resolution) // round(self.contact_period / self.grid.resolution)
        core_width = min(self.core_width_in, self.core_width_out)

        if self.core_width_in > self.core_width_out:
            self.contact_length_in = self.contact_length_in + (self.core_width_in - self.core_width_out)/2
        elif self.core_width_in < self.core_width_out:
            self.contact_length_out = self.contact_length_out + (self.core_width_out - self.core_width_in)/2

        if self.contact_linear:
            contact_length_list = list(np.linspace(self.contact_length_in, self.contact_length_out, num_contact))
        else:
            B = np.exp((self.contact_length_out-self.contact_length_in)/self.logorlin)/self.length
            z = np.linspace(0, self.length, num_contact)
            contact_length_list = self.contact_length_out - self.logorlin*np.log(B*(self.length-z)+1)
        count = 0

        for contact_length in contact_length_list:
            self.add_rect(layer=self.layer,
                          bbox=BBox(left=(count + 0.5) * self.contact_period - self.contact_width / 2,
                                    right=(count + 0.5) * self.contact_period + self.contact_width / 2,
                                    bottom=-core_width / 2 - contact_length,
                                    top=-core_width / 2,
                                    resolution=self.grid.resolution),
                          )
            self.add_rect(layer=self.layer,
                          bbox=BBox(left=(count + 0.5) * self.contact_period - self.contact_width / 2,
                                    right=(count + 0.5) * self.contact_period + self.contact_width / 2,
                                    top=core_width / 2 + contact_length,
                                    bottom=core_width / 2,
                                    resolution=self.grid.resolution),
                          )
            count += 1

    def create_ports(self) -> None:
        """
        Places ports at the beginning and end of the waveguide
        """
        self.add_photonic_port(
            name='PORT0',
            center=(0, 0),
            orient='R0',
            width=self.core_width_in,
            layer=self.layer,
            resolution=self.grid.resolution,
            unit_mode=False,
            show=False
        )

        self.add_photonic_port(
            name='PORT1',
            center=(self.length, 0),
            orient='R180',
            width=self.core_width_out,
            layer=self.layer,
            resolution=self.grid.resolution,
            unit_mode=False,
            show=False
        )
