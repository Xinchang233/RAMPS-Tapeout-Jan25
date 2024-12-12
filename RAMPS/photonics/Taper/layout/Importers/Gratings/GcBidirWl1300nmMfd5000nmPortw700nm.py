import BPG
from BPG.gds.io import GDSImport


class GcBidirWl1300nmMfd5000nmPortw700nm(BPG.PhotonicTemplateBase):
    """
    Bidirectional uniform grating
    Wavelength : 1300nm
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
            gds_path='/projectnb/siphot/zhangxc/code/TO_45CLO_2023March/cena_top/RAMPS/photonics/workhorse/gc_TE_lambda1300_deg15_mfd10um_workhorse.gds'
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

spec_file = '/projectnb/siphot/zhangxc/code/TO_45CLO_2023March/cena_top/RAMPS/photonics/layout/Importers/Gratings/specs/gc_bidir_wl1300nm_mfd5000nm_portw700nm.yaml'
plm = BPG.PhotonicLayoutManager(spec_file)
plm.generate_content()
plm.generate_gds()
plm.dataprep_calibre()
