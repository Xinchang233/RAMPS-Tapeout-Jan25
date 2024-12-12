import BPG
from BPG.gds.io import GDSImport


class GcBidirWl1550nmMfd5000nm(BPG.PhotonicTemplateBase):
    """
    Bidirectional uniform grating
    Wavelength : 1550nm
    MFD: 5000nm
    Coupling angle : 15 degrees

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
            gds_path='layout/Importers/GDS_grating_couplers/gc_dirbi_unif_wl1550_mfd5000_deg15_dataprep_calibre.gds'
        )

    def draw_layout(self):
        master = self.new_template(params=self.params, temp_cls=GDSImport)
        self.add_instance(master)
        self.add_photonic_port(
            name='PORT_OUT',
            orient='R0',
            center=(0, 0),
            width=0.7,
            layer=('RX', 'port'),
            resolution=self.grid.resolution,
            unit_mode=False,
            show=False)

spec_file = 'layout/Importers/Gratings/specs/gc_bidir_wl1550nm_mfd5000nm.yaml'
plm = BPG.PhotonicLayoutManager(spec_file)
plm.generate_content()
plm.generate_gds()
plm.dataprep_calibre()
