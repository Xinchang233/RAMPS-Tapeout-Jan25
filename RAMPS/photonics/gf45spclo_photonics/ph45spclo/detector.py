from .foundry_import import FoundryImport
from bag.layout.util import BBox


class detector_0p6u(FoundryImport):
    """
    BPG wrapper around GF45spclo detector cell
    """

    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        FoundryImport.__init__(self, temp_db, lib_name, params, used_names, **kwargs)

        self.wg_port_layer = ('si_full_free', 'port')
        self.port_width = 0.35

    @classmethod
    def get_params_info(cls):
        params = FoundryImport.get_params_info()
        return params

    @classmethod
    def get_default_param_values(cls):
        default_params = FoundryImport.get_default_param_values()
        default_params.update(
            dict(input_gds_filename='detector_0p6u.gds')
        )
        return default_params

    def draw_layout(self):
        self.add_gds_layout()

        self.add_photonic_port(
            name='IN',
            center=(0, 0),
            orient='R0',
            angle=0.0,
            width=self.port_width,
            layer=self.wg_port_layer
        )

        self.add_rect(
            layer=('no_dataprep', 'no_dataprep'),
            coord1=(0, -6),
            coord2=(49, 6)
        )


        self.add_pin_primitive(
            net_name = 'CATHODE',
            label = 'CATHODE',
            layer = ('M3', 'label'),
            bbox = BBox(
                left = 30.0,
                bottom = 1.73,
                right = 45.72, 
                top = 3.73,
                resolution = self.grid.resolution,
                unit_mode = False   
            )
        )

        self.add_pin_primitive(
            net_name = 'ANODE',
            label = 'ANODE',
            layer = ('M3', 'label'),
            bbox = BBox(
                left = 30.0,
                bottom = -3.73,
                right = 45.72, 
                top = -1.73,
                resolution = self.grid.resolution,
                unit_mode = False   
            )
        )


class detector_0p7u(FoundryImport):
    """
    BPG wrapper around GF45spclo detector cell
    """

    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        FoundryImport.__init__(self, temp_db, lib_name, params, used_names, **kwargs)

        self.wg_port_layer = ('si_full_free', 'port')
        self.port_width = 0.35

    @classmethod
    def get_params_info(cls):
        params = FoundryImport.get_params_info()
        return params

    @classmethod
    def get_default_param_values(cls):
        default_params = FoundryImport.get_default_param_values()
        default_params.update(
            dict(input_gds_filename='detector_0p7u.gds')
        )
        return default_params

    def draw_layout(self):
        self.add_gds_layout()

        self.add_photonic_port(
            name='IN',
            center=(0, 0),
            orient='R0',
            angle=0.0,
            width=self.port_width,
            layer=self.wg_port_layer
        )

        self.add_rect(
            layer=('no_dataprep', 'no_dataprep'),
            coord1=(0, -6),
            coord2=(49, 6)
        )


        self.add_pin_primitive(
            net_name = 'CATHODE',
            label = 'CATHODE',
            layer = ('M3', 'label'),
            bbox = BBox(
                left = 30.0,
                bottom = 1.78,
                right = 45.72, 
                top = 3.78,
                resolution = self.grid.resolution,
                unit_mode = False   
            )
        )

        self.add_pin_primitive(
            net_name = 'ANODE',
            label = 'ANODE',
            layer = ('M3', 'label'),
            bbox = BBox(
                left = 30.0,
                bottom = -3.78,
                right = 45.72, 
                top = -1.78,
                resolution = self.grid.resolution,
                unit_mode = False   
            )

        )
        self.add_rect(
            layer = ('PHOTON', 'drawing'),
            coord1 = (self.gds_instance.bound_box.left, self.gds_instance.bound_box.bottom),
            coord2 = (self.gds_instance.bound_box.right, self.gds_instance.bound_box.top),
            #unit_mode=False
        )

class detectorc_0p6u(FoundryImport):
    """
    BPG wrapper around GF45spclo detectorc cell
    """

    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        FoundryImport.__init__(self, temp_db, lib_name, params, used_names, **kwargs)

        self.wg_port_layer = ('si_full_free', 'port')
        self.port_width = 0.5

    @classmethod
    def get_params_info(cls):
        params = FoundryImport.get_params_info()
        return params

    @classmethod
    def get_default_param_values(cls):
        default_params = FoundryImport.get_default_param_values()
        default_params.update(
            dict(input_gds_filename='detectorc_0p6u.gds')
        )
        return default_params

    def draw_layout(self):
        self.add_gds_layout()

        self.add_photonic_port(
            name='IN',
            center=(0, 0),
            orient='R0',
            angle=0.0,
            width=self.port_width,
            layer=self.wg_port_layer
        )

        self.add_rect(
            layer=('no_dataprep', 'no_dataprep'),
            coord1=(0, -6),
            coord2=(49, 6)
        )


        self.add_pin_primitive(
            net_name = 'CATHODE',
            label = 'CATHODE',
            layer = ('M3', 'label'),
            bbox = BBox(
                left = 30.0,
                bottom = 1.73,
                right = 45.72,
                top = 3.73,
                resolution = self.grid.resolution,
                unit_mode = False
            )
        )

        self.add_pin_primitive(
            net_name = 'ANODE',
            label = 'ANODE',
            layer = ('M3', 'label'),
            bbox = BBox(
                left = 30.0,
                bottom = -3.73,
                right = 45.72,
                top = -1.73,
                resolution = self.grid.resolution,
                unit_mode = False
            )
        )


class detectorc_0p7u(FoundryImport):
    """
    BPG wrapper around GF45spclo detectorcx cell
    """

    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        FoundryImport.__init__(self, temp_db, lib_name, params, used_names, **kwargs)

        self.wg_port_layer = ('si_full_free', 'port')
        self.port_width = 0.5

    @classmethod
    def get_params_info(cls):
        params = FoundryImport.get_params_info()
        return params

    @classmethod
    def get_default_param_values(cls):
        default_params = FoundryImport.get_default_param_values()
        default_params.update(
            dict(input_gds_filename='detectorc_0p7u.gds')
        )
        return default_params

    def draw_layout(self):
        self.add_gds_layout()

        self.add_photonic_port(
            name='IN',
            center=(0, 0),
            orient='R0',
            angle=0.0,
            width=self.port_width,
            layer=self.wg_port_layer
        )

        self.add_rect(
            layer=('no_dataprep', 'no_dataprep'),
            coord1=(0, -6),
            coord2=(59, 6)
        )


        self.add_pin_primitive(
            net_name = 'CATHODE',
            label = 'CATHODE',
            layer = ('M3', 'label'),
            bbox = BBox(
                left = 30.0,
                bottom = 1.78,
                right = 45.72,
                top = 3.78,
                resolution = self.grid.resolution,
                unit_mode = False
            )
        )

        self.add_pin_primitive(
            net_name = 'ANODE',
            label = 'ANODE',
            layer = ('M3', 'label'),
            bbox = BBox(
                left = 30.0,
                bottom = -3.78,
                right = 45.72,
                top = -1.78,
                resolution = self.grid.resolution,
                unit_mode = False
            )

        )

        self.add_rect(
            layer = ('PHOTON', 'drawing'),
            coord1 = (self.gds_instance.bound_box.left, self.gds_instance.bound_box.bottom),
            coord2 = (self.gds_instance.bound_box.right, self.gds_instance.bound_box.top),
            #unit_mode=False
        )

