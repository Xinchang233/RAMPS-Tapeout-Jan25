import BPG
from Photonic_Core_Layout.AdiabaticPaths.AdiabaticPaths import AdiabaticPaths
from copy import deepcopy


class General_taper(BPG.PhotonicTemplateBase):
    """
    Port names: PORT_IN, PORT_1_OUT, PORT_2_OUT
    """

    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)
        self.widths = self._listize(self.params['widths'])
        self.straight_sec_len = self._listize(self.params['straight_sec_len'])
        self.taper_len = self._listize(self.params['taper_len'])
        self.path = self._listize(self.params['path'])

        self.layer = self.params['layer']
        self.port_layer = ('si_full_free', 'port')

    @classmethod
    def get_params_info(cls):
        return dict(
            widths='Widths of straight sections. Tapers will connect different width',
            straight_sec_len='Length of straight sections',
            taper_len='Length of tapering sections',
            path='Variable that describes waveguide. E.g. path ["S","U","D" ] corresponds to a waveguide with straight'
                 'section, followed by taper up and then by taper down',
            layer = 'Layer where waveguide will be instantiated'
        )

    @classmethod
    def get_default_param_values(cls):
        return dict(
            taper_len=0,
            straight_sec_len = 0
        )

    def draw_layout(self) -> None:
        # Template of adiabatic band parameters
        adiabatic_band_params = dict(layer=self.layer, port_layer=self.port_layer, radius_threshold=1.5,
                                     curvature_rate_threshold=0.7, merge_arcs=False)
        adiabatic_band_params['arc_params'] = [dict(arc_type="straight_wg", width=5, length=3)]
        # Checking
        # if len(self.widths) != len(self.straight_sec_len):
        #     raise ValueError('Different number of widths and straight section lengths is supplied')
        # if len(self.widths) != len(self.taper_len) or len(self.widths) != len(self.taper_len)-1:
        #     raise ValueError('Wrong number of taper_len parameter is supplied')
        str_count = taper_count = width_count = 0
        for i in range(len(self.path)):
            if self.path[i].capitalize() == 'S':
                # Go straight
                params = deepcopy(adiabatic_band_params)
                params['arc_params'][0]['length'] = self.straight_sec_len[str_count]
                str_count += 1
                params['arc_params'][0]['width'] = self.widths[width_count]  # Dont update width count

                temp = self.new_template(params=params, temp_cls=AdiabaticPaths)
                if 'inst' in vars() or 'inst' in globals():
                    inst = self.add_instances_port_to_port(inst_master=temp, instance_port_name='PORT_IN',
                                                           self_port=inst['PORT_OUT'])
                else:
                    inst = self.add_instance(master=temp)

            elif self.path[i].capitalize() in ['U', 'D']:
                # Taper up or down
                # TODO - check if U corresponds to tapering up (check the widths)
                params = deepcopy(adiabatic_band_params)
                params['arc_params'][0]['length'] = self.taper_len[taper_count]
                taper_count += 1
                params['arc_params'][0]['width'] = [self.widths[width_count],
                                                  self.widths[width_count + 1]]
                width_count += 1

                temp = self.new_template(params=params, temp_cls=AdiabaticPaths)
                if 'inst' in vars() or 'inst' in globals():
                    inst = self.add_instances_port_to_port(inst_master=temp, instance_port_name='PORT_IN',
                                                           self_port=inst['PORT_OUT'])
                else:
                    inst = self.add_instance(master=temp)

            if i == 0:
                self.extract_photonic_ports(inst=inst, port_names=['PORT_IN'])
            if i == len(self.path) - 1:
                self.extract_photonic_ports(inst=inst, port_names=['PORT_OUT'])

    def _listize(self, x):
        """
        if x is a scalar, converts it into a one-element list
        conventient for handling cases when input parameters can be a scalar or a list
        such as width parameter.
        """
        if isinstance(x, list):
            return x
        else:
            return [x]
