import BPG
import numpy as np

class DesignHeater(BPG.PhotonicTemplateBase):
    """
    Base ring-heater class

    """

    @staticmethod
    def design_heater_width_from_resistance(resistance,
                                            heater_rout,
                                            r_square,
                                            contact_width,
                                            contact_dist,
                                            ):
        """
        Calculates the required heater width for a given resistance, outer radius, r_square, contact width, and contact
        distance.

        Values must be passed in in units of microns and ohm/um^2

        Parameters
        ----------
        resistance : float
            The target resistance
        heater_rout : float
            The outer radius of the heater ring
        r_square : float
            The sheet resistance
        contact_width : float
            The width of the contacts that connect the heater ring to the via stack
        contact_dist : float
            The separation between the ends of the two contacts

        Returns
        -------
        ring_width : float
            The width of the heater ring required to achieve the target resistance for the specified geometry
        """
        # If you integrate across the radius to find effective resistance per 'pie-slice' of the annulus, and then
        # integrate over theta, one finds:
        # ring_width = rout - np.exp((4*resistance*np.log(rout) - rsq*np.pi^2) / 4*resistance)
        # This formula is with 10% of the magic code below. It does not include effects of the contacts

        # Magic formula from legacy designs
        ring_width = \
            1 / (16 * r_square) * (
                -8 * contact_dist * r_square + 8 * heater_rout * r_square - 4 * resistance * contact_width -
                np.pi * r_square * contact_width +
                np.sqrt(
                    64 * np.pi * heater_rout * r_square ** 2 * contact_width +
                    (
                        8 * contact_dist * r_square - 8 * heater_rout * r_square +
                        4 * resistance * contact_width + np.pi * r_square * contact_width
                    ) ** 2
                )
            )
        return ring_width
