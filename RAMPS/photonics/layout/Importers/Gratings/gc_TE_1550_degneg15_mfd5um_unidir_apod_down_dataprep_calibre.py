import BPG
from BPG.gds.io import GDSImport


class GcUnidirBackWl1550nmMfd5000nmDown(BPG.PhotonicTemplateBase):
    """
    Unidirectional appodized grating that couples light out towards the pads
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
            gds_path='layout/Importers/GDS_grating_couplers/gc_TE_1550_degneg15_mfd5um_unidir_apod_down_curved_dataprep_calibre.gds'
        )

    def draw_layout(self):
        master = self.new_template(params=self.params, temp_cls=GDSImport)
        self.add_instance(master)
        self.add_photonic_port(
            name='PORT_OUT',
            orient='R0',
            center=(0, -20),
            width=0.5,
            layer=('RX', 'port'),
            resolution=self.grid.resolution,
            unit_mode=False,
            show=False)

# spec_file = 'layout/Importers/Gratings/specs/gc_unidirback_wl1550nm_mfd5000nm.yaml'
# plm = BPG.PhotonicLayoutManager(spec_file)
# plm.generate_content()
# plm.generate_gds()
#
