import BPG
from BPG.gds.io import GDSImport
from bag.layout.util import BBox


class ThermalPhaseShifterOBand(BPG.PhotonicTemplateBase):
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
            gds_path='layout/Importers/gds/phasethermsld.gds'
        )

    def draw_layout(self):
        master = self.new_template(params=self.params, temp_cls=GDSImport)
        self.add_instance(master)
        self.add_photonic_port(
            name='PORT_IN',
            orient='R90',
            center=(0, 0),
            width=0.4,
            layer=('RX', 'port'),
            resolution=self.grid.resolution,
            unit_mode=False,
            show=False)

        self.add_photonic_port(
            name='PORT_OUT',
            orient='90',
            center=(50, 0),
            width=0.4,
            layer=('RX', 'port'),
            resolution=self.grid.resolution,
            unit_mode=False,
            show=False)

        # add pins for UA as UB should be used for top-level power routing. And the horizontal UA layer is deleted in
        # phase shifter layout to avoid collision.

        self.add_pin_primitive(
            net_name='PIN_VDD',
            label='PIN_VDD',
            layer=('UA', 'pin'),
            bbox=BBox(
                top=1,
                bottom=0,
                left=40.26,
                right=44.26,
                resolution=self.grid.resolution
            )
        )

        self.add_pin_primitive(
            net_name='PIN_GND',
            label='PIN_GND',
            layer=('UB', 'pin'),
            bbox=BBox(
                top=1,
                bottom=0,
                left=-9.74,
                right=-5.74,
                resolution=self.grid.resolution
            )
        )
