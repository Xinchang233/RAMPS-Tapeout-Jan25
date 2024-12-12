import BPG
from BPG.gds.io import GDSImport


class GcUniWl1300nmMfd5000nm(BPG.PhotonicTemplateBase):
    """
    Unidirectional Upwards
    Wavelength : 1300nm
    MFD: 5000nm
    Coupling angle : 15 degrees

    Curved version, for AL11B

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
            gds_path='layout/Importers/Gratings/unidirectional/gds/gc_diruni_unif_lam1300_mfd5000_15degup_air_201210125816_dataprep_calibre.gds'
        )

    def draw_layout(self):
        master = self.new_template(params=self.params, temp_cls=GDSImport)
        self.add_instance(master)
        self.add_photonic_port(
            name='PORT_OUT',
            orient='R0',
            center=(-55.164, 0),
            width=0.5,
            layer=('RX', 'port'),
            resolution=self.grid.resolution,
            unit_mode=False,
            show=False)

