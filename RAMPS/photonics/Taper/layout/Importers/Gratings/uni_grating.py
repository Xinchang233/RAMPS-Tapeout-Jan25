import BPG
from BPG.gds.io import GDSImport


class GcBidirWl1300nmMfd9200nmCurved(BPG.PhotonicTemplateBase):
    """
    Bidirectional uniform grating
    Wavelength : 1300nm
    MFD: 9200nm
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
            gds_path='/cena_top/RAMPS/photonics/layout/Importers/Gratings/GcBidirWl1300nmMfd5000nmPortw700nm.py'
        )

    def draw_layout(self):
        master = self.new_template(params=self.params, temp_cls=GDSImport)
        self.add_instance(master)
        self.add_photonic_port(
            name='PORT_OUT',
            orient='R0',
            center=(-5, 0),
            width=0.5,
            layer=('rx1phot', 'port'),
            resolution=self.grid.resolution,
            unit_mode=False,
            show=False)

