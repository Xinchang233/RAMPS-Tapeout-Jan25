import BPG
from BPG.gds.io import GDSImport


class GcUnidirWl1310nmMfd5000nm(BPG.PhotonicTemplateBase):
    """
    Uidirectional uniform grating (design by Mark Wade)
    Wavelength : 1310nm
    MFD: 5000nm
    Coupling angle : 11 degrees

    Ports:
        'PORT_OUT'
    """

    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)

    @classmethod
    def get_params_info(cls):
        return dict(
            gds_path='Path to .gds file with grating layout'
        )

    @classmethod
    def get_default_param_values(cls):
        return dict(
            gds_path='layout/Importers/GDS_grating_couplers/gc_unidir_wl1310_mfd5000_deg11.gds'
        )

    def draw_layout(self):
        master = self.new_template(params=self.params, temp_cls=GDSImport)
        self.add_instance(master)
        self.add_photonic_port(
            name='PORT_OUT',
            orient='R0',
            center=(0, 0),
            width=0.5,
            layer=('RX', 'port'),
            resolution=self.grid.resolution,
            unit_mode=False,
            show=False)

# spec_file = 'layout/Importers/Gratings/specs/gc_unidir_wl1310nm_mfd5000nm.yaml'

