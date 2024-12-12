from .foundry_import import FoundryImport


class iograt_1311(FoundryImport):
    """
    BPG wrapper around GF45spclo iograt cell
    """

    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        FoundryImport.__init__(self, temp_db, lib_name, params, used_names, **kwargs)

        self.wg_port_layer = ('si_full_free', 'port')
        self.port_width = 0.35
        self.beam_center = (-24.0, 0)

    @classmethod
    def get_params_info(cls):
        params = FoundryImport.get_params_info()
        return params

    @classmethod
    def get_default_param_values(cls):
        default_params = FoundryImport.get_default_param_values()
        default_params.update(
            dict(input_gds_filename='iograt_1311.gds')
        )
        return default_params

    def draw_layout(self):
        self.add_gds_layout()

        self.add_photonic_port(
            name='IN',
            center=(0, 0),
            orient='R180',
            angle=0.0,
            width=self.port_width,
            layer=self.wg_port_layer
        )

        self.add_rect(
            layer=('no_dataprep', 'no_dataprep'),
            coord1=(-39, -15),
            coord2=(0, 15)
        )


class iograt_1331(FoundryImport):
    """
    BPG wrapper around GF45spclo iograt cell
    """

    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        FoundryImport.__init__(self, temp_db, lib_name, params, used_names, **kwargs)

        self.wg_port_layer = ('si_full_free', 'port')
        self.port_width = 0.35
        self.beam_center = (-24.0, 0)

    @classmethod
    def get_params_info(cls):
        params = FoundryImport.get_params_info()
        return params

    @classmethod
    def get_default_param_values(cls):
        default_params = FoundryImport.get_default_param_values()
        default_params.update(
            dict(input_gds_filename='iograt_1331.gds')
        )
        return default_params

    def draw_layout(self):
        self.add_gds_layout()

        self.add_photonic_port(
            name='IN',
            center=(0, 0),
            orient='R180',
            angle=0.0,
            width=self.port_width,
            layer=self.wg_port_layer
        )

        self.add_rect(
            layer=('no_dataprep', 'no_dataprep'),
            coord1=(-39, -15),
            coord2=(0, 15)
        )


class iograt_1291(FoundryImport):
    """
    BPG wrapper around GF45spclo iograt cell
    """

    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        FoundryImport.__init__(self, temp_db, lib_name, params, used_names, **kwargs)

        self.wg_port_layer = ('si_full_free', 'port')
        self.port_width = 0.35
        self.beam_center = (-24.0, 0)

    @classmethod
    def get_params_info(cls):
        params = FoundryImport.get_params_info()
        return params

    @classmethod
    def get_default_param_values(cls):
        default_params = FoundryImport.get_default_param_values()
        default_params.update(
            dict(input_gds_filename='iograt_1291.gds')
        )
        return default_params

    def draw_layout(self):
        self.add_gds_layout()

        self.add_photonic_port(
            name='IN',
            center=(0, 0),
            orient='R180',
            angle=0.0,
            width=self.port_width,
            layer=self.wg_port_layer
        )

        self.add_rect(
            layer=('no_dataprep', 'no_dataprep'),
            coord1=(-39, -15),
            coord2=(0, 15)
        )


class iograt_1271(FoundryImport):
    """
    BPG wrapper around GF45spclo iograt cell
    """

    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        FoundryImport.__init__(self, temp_db, lib_name, params, used_names, **kwargs)

        self.wg_port_layer = ('si_full_free', 'port')
        self.port_width = 0.35
        self.beam_center = (-24.0, 0)

    @classmethod
    def get_params_info(cls):
        params = FoundryImport.get_params_info()
        return params

    @classmethod
    def get_default_param_values(cls):
        default_params = FoundryImport.get_default_param_values()
        default_params.update(
            dict(input_gds_filename='iograt_1271.gds')
        )
        return default_params

    def draw_layout(self):
        self.add_gds_layout()

        self.add_photonic_port(
            name='IN',
            center=(0, 0),
            orient='R180',
            angle=0.0,
            width=self.port_width,
            layer=self.wg_port_layer
        )

        self.add_rect(
            layer=('no_dataprep', 'no_dataprep'),
            coord1=(-39, -15),
            coord2=(0, 15)
        )
