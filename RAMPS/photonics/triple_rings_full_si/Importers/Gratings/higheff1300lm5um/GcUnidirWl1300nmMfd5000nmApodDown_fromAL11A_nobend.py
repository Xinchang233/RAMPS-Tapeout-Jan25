import BPG
from BPG.gds.io import GDSImport


class GcUnidirWl1300nmMfd5000nmApodDown_fromAL11A_nobend(BPG.PhotonicTemplateBase):
    """
    Undirectional, apodized grating
    Wavelength : 1300nm
    MFD: 5000nm
    Coupling angle : -15 degrees (-20 deg measured, coupling into air)
    Coupling direction: downwards
    Taper: mine

    no bend version

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
            gds_path='layout/Importers/Gratings/higheff1300lm5um/gds/gc_diruni_apod_lam1300_mfd5000_neg15down_air_al11a_nobend_dataprep_calibre.gds'
        )

    def draw_layout(self):
        master = self.new_template(params=self.params, temp_cls=GDSImport)
        self.add_instance(master)
        self.add_photonic_port(
            name='PORT_OUT',
            orient='R0',
            center=(-93.98300, 0.0),
            width=0.5,
            layer=('RX', 'port'),
            resolution=self.grid.resolution,
            unit_mode=False,
            show=False)

# end class GcUnidirWl1300nmMfd9200nmApodDownJtaper
