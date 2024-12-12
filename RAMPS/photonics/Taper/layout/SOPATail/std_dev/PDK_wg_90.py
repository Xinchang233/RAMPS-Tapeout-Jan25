import BPG
from BPG.gds.io import GDSImport


class PDK_wg_90(BPG.PhotonicTemplateBase):
    """
    90 degrees bend, 5µm radius

    Ports:
        'IN' 'OUT'
    """

    @classmethod
    def get_params_info(cls):
        return dict(
            gds_path='Path to gds to import'
        )
    @classmethod
    def get_default_param_values(cls):
        return dict(
            gds_path='layout/SOPATail/std_dev/GDS/Si_WG_90.GDS'
        )

    def draw_layout(self):
        p = {'gds_path': 'layout/SOPATail/std_dev/GDS/Si_WG_90.GDS'}
        master = self.new_template(params=p, temp_cls=GDSImport)
        self.add_instance(master)
        self.add_photonic_port(
            name='IN',
            orient='R0',
            center=(0, -5),
            width=0.48,
            layer=['port'],
            resolution=self.grid.resolution,
            unit_mode=False,
            show=False)
        
        self.add_photonic_port(
            name='THR',
            orient='R180',
            center=(15, -5),
            width=0.48,
            layer=['port'],
            resolution=self.grid.resolution,
            unit_mode=False,
            show=False)
        
        self.add_photonic_port(
            name='ADD',
            orient='R0',
            center=(0, 5),
            width=0.48,
            layer=['port'],
            resolution=self.grid.resolution,
            unit_mode=False,
            show=False)
        
        self.add_photonic_port(
            name='DRP',
            orient='R180',
            center=(15, 5),
            width=0.48,
            layer=['port'],
            resolution=self.grid.resolution,
            unit_mode=False,
            show=False)
        

