import BPG
from BPG.gds.io import GDSImport


class FullEtchToFullRib_Cband(BPG.PhotonicTemplateBase):
    """
    Mode converter between fundamental modes of full etch and rib waveguide.
    Input width of the full etch wg is 0.5um.
    Output width of rib wg is: 0.5um of full thickness silicon, 4um of partial etch silicon (1.75um on each side)

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
            gds_path='layout/Importers/ModeConverters/gds/FullEtchToRibWg_Cband.GDS'
        )

    def draw_layout(self):
        master = self.new_template(params=self.params, temp_cls=GDSImport)
        self.add_instance(master)
        self.add_photonic_port(
            name='PORT_IN',
            orient='R0',
            center=(0, 0),
            width=0.5,
            layer=('RX', 'port'),
            resolution=self.grid.resolution,
            unit_mode=False,
            show=False)

        self.add_photonic_port(
            name='PORT_OUT',
            orient='R180',
            center=(22.2, 0),
            width=0.5,
            layer=('RX', 'port'),
            resolution=self.grid.resolution,
            unit_mode=False,
            show=False)


#################################### Generation code ##################################

     # init_port = self.add_photonic_port(name='init_port', center=(0, 0),
     #                                       orient='R0', width=0.5, layer=(full_etch_layer[0], 'port'))

    # full_etch_sil_inst = AdiabaticRouter(gen_cls=self, init_port=init_port, layer=full_etch_layer, name='init_port')
    # full_etch_sil_inst.add_straight_wg(length=1)
    # full_etch_sil_inst.add_straight_wg(length=5, width=1)
    # full_etch_sil_inst.add_straight_wg(length=10.2)
    # full_etch_sil_inst.add_straight_wg(length=5, width=0.5)
    #
    # full_etch_sil_inst.add_straight_wg(length=1) # just a wg extension (not a part of converter)
    #
    # init_port1 = self.add_photonic_port(name='init_port1', center=(0, 0),
    #                                    orient='R0', width=4, layer=(full_etch_layer[0], 'port'))
    #
    # partial_etch_sil_inst = AdiabaticRouter(gen_cls=self, init_port=init_port1, layer=partial_etch_layer, name='init_port1')
    # partial_etch_sil_inst.add_straight_wg(length=1)
    # partial_etch_sil_inst.add_straight_wg(length=5)
    # partial_etch_sil_inst.add_straight_wg(length=10, width=1.4)