import BPG
from BPG.gds.io import GDSImport


class YBranch_CBand_with_bends(BPG.PhotonicTemplateBase):
    """
    3 dB splitter
    Wavelength : 1550nm
    Input wg width: 600
    Output wg width: 600nm

    Ports:
        'PORT_IN'
        'PORT_OUT1'
        'PORT_OUT2'
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
            gds_path='layout/Importers/YBranch/gds/Y_splitter_C_band_with_bends.gds'
        )

    def draw_layout(self):
        master = self.new_template(params=self.params, temp_cls=GDSImport)
        self.add_instance(master)
        self.add_photonic_port(
            name='PORT_IN',
            orient='R0',
            center=(0, 0),
            width=0.6,
            layer=('RX', 'port'),
            resolution=self.grid.resolution,
            unit_mode=False,
            show=False)

        self.add_photonic_port(
            name='PORT_OUT1',
            orient='R180',
            center=(23.6, 1.2),
            width=0.6,
            layer=('RX', 'port'),
            resolution=self.grid.resolution,
            unit_mode=False,
            show=False)

        self.add_photonic_port(
            name='PORT_OUT2',
            orient='R180',
            center=(23.6, -1.2),
            width=0.6,
            layer=('RX', 'port'),
            resolution=self.grid.resolution,
            unit_mode=False,
            show=False)
