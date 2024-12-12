import BPG
from BPG.gds.io import GDSImport


class gc1550_5mfd(BPG.PhotonicTemplateBase):
    """
    Cale design grating for C band (1550nm)

    Ports:
        'PORT_OUT'
    """

    @classmethod
    def get_params_info(cls):
        return dict(
            gds_path='Path to gds to import'
        )

    def draw_layout(self):
        p = {'gds_path': './layout/gc/gds/gc1550_5mfd.GDS'}
        master = self.new_template(params=p, temp_cls=GDSImport)
        self.add_instance(master)
        self.add_photonic_port(
            name='PORT_OUT',
            orient='R180',
            center=(0, 0),
            width=0.75,
            layer=['si_full_free','port'],
            resolution=self.grid.resolution,
            unit_mode=False,
            show=False)

class gc1550_10mfd(BPG.PhotonicTemplateBase):
    """
    Cale design grating for C band (1550nm)

    Ports:
        'PORT_OUT'
    """

    @classmethod
    def get_params_info(cls):
        return dict(
            gds_path='Path to gds to import'
        )

    def draw_layout(self):
        p = {'gds_path': './layout/gc/gds/gc1550_10mfd.GDS'}
        master = self.new_template(params=p, temp_cls=GDSImport)
        self.add_instance(master)
        self.add_photonic_port(
            name='PORT_OUT',
            orient='R180',
            center=(0.0,0.0),
            width=0.6,
            layer=['si_full_free', 'port'],
            resolution=self.grid.resolution,
            unit_mode=False,
            show=False)

class ngc1550_10mfd(BPG.PhotonicTemplateBase):
    """
    Cale design grating for C band (1550nm)

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
            gds_path='./layout/gc/gds/ngc1550_10mfd.GDS'
        )


    def draw_layout(self):
        p = {'gds_path': './layout/gc/gds/ngc1550_10mfd.GDS'}
        master = self.new_template(params=p, temp_cls=GDSImport)
        self.add_instance(master)
        self.add_photonic_port(
            name='PORT_OUT',
            orient='R180',
            center=(0.0,0.0),
            width=0.6,
            layer=['si_full_free', 'port'],
            resolution=self.grid.resolution,
            unit_mode=False,
            show=False)

class gc_dirbi(BPG.PhotonicTemplateBase):
    """
    Bohan design grating for C band (1550nm) bidirectional

    Ports:
        'PORT_OUT'
    """

    @classmethod
    def get_params_info(cls):
        return dict(
            gds_path='Path to gds to import'
        )

    def draw_layout(self):
        p = {'gds_path': './layout/gc/gds/gc_dirbi_unif_wl1550_mfd5000_deg15_dataprep_calibre.gds'}
        master = self.new_template(params=p, temp_cls=GDSImport)
        self.add_instance(master)
        self.add_photonic_port(
            name='PORT_OUT',
            orient='R0',
            center=(-49.993,0.0),
            width=0.7,
            layer=['si_full_free', 'port'],
            resolution=self.grid.resolution,
            unit_mode=False,
            show=False)