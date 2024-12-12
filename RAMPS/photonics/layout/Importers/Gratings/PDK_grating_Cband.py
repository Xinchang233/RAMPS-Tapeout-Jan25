import BPG
from BPG.gds.io import GDSImport


class PDK_grating_Cband(BPG.PhotonicTemplateBase):
    """
    PDK Library grating for C band (1550nm)

    Ports:
        'PORT_OUT'
    """

    @classmethod
    def get_params_info(cls):
        return dict(
            gds_path='Path to gds to import'
        )
    @classmethod
    def get_default_param_values(cls):
        return dict(
            gds_path='layout/Importers/GDS_grating_couplers/iogratc.gds'
        )

    def draw_layout(self):
        p = {'gds_path': 'layout/Importers/GDS_grating_couplers/iogratc.gds'}
        master = self.new_template(params=p, temp_cls=GDSImport)
        self.add_instance(master)
        self.add_photonic_port(
            name='PORT_OUT',
            orient='R180',
            center=(0, 0),
            width=0.5,
            layer=['RX', 'port'],
            resolution=self.grid.resolution,
            unit_mode=False,
            show=False)
        

