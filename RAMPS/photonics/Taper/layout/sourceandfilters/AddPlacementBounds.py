import BPG

class AddPlacementBounds(BPG.PhotonicTemplateBase):
    """
    Adds PHOTON_A rectangles to a layout in order to prevent circuits from being drawn there

    """

    @staticmethod
    def design_heater_width_from_resistance(resistance,
                                            heater_rout,
                                            r_square,
                                            contact_width,
                                            contact_dist,
                                            ):
