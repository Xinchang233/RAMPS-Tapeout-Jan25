import BPG
from BPG.gds.io import GDSImport
from bag.layout.util import BBox


class ThermalPhaseShifter(BPG.PhotonicTemplateBase):
    """
    PDK component
    Ports:
        'PORT_IN'
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
            gds_path='layout/Importers/gds/phasethermc_short_with_mode_convertor.GDS'
        )

    def draw_layout(self):
        master = self.new_template(params=self.params, temp_cls=GDSImport)
        self.add_instance(master)
        self.add_photonic_port(
            name='PORT_IN',
            orient='R0',
            center=(-22.2, 0),
            width=0.5,
            layer=('RX', 'port'),
            resolution=self.grid.resolution,
            unit_mode=False,
            show=False)

        self.add_photonic_port(
            name='PORT_OUT',
            orient='R180',
            center=(222.2, 0),
            width=0.5,
            layer=('RX', 'port'),
            resolution=self.grid.resolution,
            unit_mode=False,
            show=False)

        # add pins where LB routing wires should be initialized

        self.add_pin_primitive(
            net_name='PIN_VDD',
            label='PIN_VDD',
            layer=('LB', 'pin'),
            bbox=BBox(
                top=-7 + 2,
                bottom=-7 - 2,
                left=100 - 2,
                right=100 + 2,
                resolution=self.grid.resolution
            )
        )

        self.add_pin_primitive(
            net_name='PIN_GND',
            label='PIN_GND',
            layer=('LB', 'pin'),
            bbox=BBox(
                top=11.75 + 2,
                bottom=11.75 - 2,
                left=55.3 - 2,
                right=55.3 + 2,
                resolution=self.grid.resolution
            )
        )
