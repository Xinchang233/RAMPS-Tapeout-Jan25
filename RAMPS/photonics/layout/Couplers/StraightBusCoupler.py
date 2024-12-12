import BPG


class StraightBusCoupler(BPG.PhotonicTemplateBase):
    """
    """

    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)

        self.layer = self.params['layer']
        self.width = self.params['width']
        self.length = self.params['length']

    @classmethod
    def get_default_param_values(cls):
        return dict(
        )

    @classmethod
    def get_params_info(cls):  # Returns definition of the parameters.
        return dict(
            layer='',
            width='',
            length='coupler length '
        )

    def draw_layout(self):
        # place coupler
        self.add_rect(
            layer=self.layer,
            coord1=(-self.length / 2, -self.width / 2),
            coord2=(self.length / 2, self.width / 2))

        # add port at the input
        self.add_photonic_port(
            name='PORT_IN',
            orient='R0',
            center=(-self.length / 2, 0),
            width=self.width,
            layer=(self.layer[0], 'port'),
            resolution=self.grid.resolution,
            unit_mode=False,
            show=False)

        # add port at the output
        self.add_photonic_port(
            name='PORT_OUT',
            orient='R180',
            center=(self.length / 2, 0),
            width=self.width,
            layer=(self.layer[0], 'port'),
            resolution=self.grid.resolution,
            unit_mode=False,
            show=False)

        # add port at the coupling point
        self.add_photonic_port(
            name='PORT_COUPLE',
            orient='R0',
            center=(0, self.width / 2),
            width=self.width,
            layer=(self.layer[0], 'port'),
            resolution=self.grid.resolution,
            unit_mode=False,
            show=False)
