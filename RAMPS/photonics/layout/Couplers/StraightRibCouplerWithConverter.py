import BPG
from ..Importers.ModeConverters.FullEtchToFullRib_Cband import FullEtchToFullRib_Cband


class StraightRibCouplerWithConverter(BPG.PhotonicTemplateBase):
    """
    """

    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)

        self.full_thickness_si_layer = self.params['full_thickness_si_layer']
        self.partial_thickness_si_layer = self.params['partial_thickness_si_layer']

        self.full_thickness_si_width = self.params['full_thickness_si_width']
        self.partial_thickness_si_width = self.params['partial_thickness_si_width']

        self.length = self.params['length']

    @classmethod
    def get_default_param_values(cls):
        return dict(
        )

    @classmethod
    def get_params_info(cls):  # Returns definition of the parameters.
        return dict(
            full_thickness_si_layer='',
            partial_thickness_si_layer='',
            full_thickness_si_width='',
            partial_thickness_si_width='',
            length='coupler length '
        )

    def draw_layout(self):
        # place full thickness silicon
        self.add_rect(
            layer=self.full_thickness_si_layer,
            coord1=(-self.length / 2, -self.full_thickness_si_width / 2),
            coord2=(self.length / 2, self.full_thickness_si_width / 2))

        # place partial etch silicon
        self.add_rect(
            layer=self.partial_thickness_si_layer,
            coord1=(-self.length / 2, -self.partial_thickness_si_width / 2),
            coord2=(self.length / 2, self.partial_thickness_si_width / 2))

        # add port at the coupling point
        self.add_photonic_port(
            name='PORT_COUPLE',
            orient='R0',
            center=(0, self.full_thickness_si_width / 2),
            width=self.full_thickness_si_width,
            layer=(self.full_thickness_si_layer[0], 'port'),
            resolution=self.grid.resolution,
            unit_mode=False,
            show=False)

        # place mode convertors on both sides
        mode_conv_template = self.new_template(params=None, temp_cls=FullEtchToFullRib_Cband)
        mode_conv_width = mode_conv_template.bound_box.width
        mode_conv_inst_left = self.add_instance(master=mode_conv_template,
                                                loc=(-self.length / 2 - mode_conv_width, 0), orient='R0')
        mode_conv_inst_right = self.add_instance(master=mode_conv_template,
                                                 loc=(self.length / 2 + mode_conv_width, 0), orient='R180')

        # extract ports
        self.extract_photonic_ports(inst=mode_conv_inst_left, port_names=['PORT_IN'])
        self.extract_photonic_ports(inst=mode_conv_inst_right, port_names=['PORT_IN'],
                                    port_renaming={'PORT_IN': 'PORT_OUT'})
