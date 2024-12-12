import BPG
import importlib
from Photonic_Core_Layout.AdiabaticPaths.AdiabaticPaths import AdiabaticPaths
from Photonic_Core_Layout.WaveguideBase.WaveguideBase import WaveguideBase

# changed "layout" -> "quantum_photon_pair_generator.github.equip01.EquipRow_v1_BWRC"
from layout.ArbitraryOrderRingFilter.ArbitraryOrderRingFilter import ArbitraryOrderRingFilter
from layout.Pumpfilter.Pumpfilter import Pumpfilter
from layout.asefilter.asefilter import asefilter
from layout.RingSensable.RingSensable import RingSensable

from Photonic_Core_Layout.Taper.LinearTaper import LinearTaper
from copy import deepcopy

class sourceandfilters2(BPG.PhotonicTemplateBase):
    """
    This class creates an unbalanced MZI with an input and output rac coupler.
    Parameters
    ----------
    rac_params : dict
        dict of parameters to be sent to the directional coupler master

    """

    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)
        self.pumpfilter_params=self.params['pumpfilters_params']
        self.asefilter_params = self.params['asefilters_params']
        self.source_params = self.params['source_params']
        self.grating5_params = self.params['grating5_params']
        self.grating10_params = self.params['grating10_params']
        self.taper_length = self.params['taper_length']
        # Master declaration

        self.filters_master = dict()
        self.wgs_master = dict()
        self.grating_master5=None
        self.grating_master10=None
        self.taper_master=None
        # Instances declaration
        self.filters = dict()
        self.wgs = dict()
        self.gc = dict()
        self.taper = dict()


    @classmethod
    def get_params_info(cls) -> dict:
        return dict(taper_length='taper length connecting soruce and filters',grating5_params='gc params 5mfd',grating10_params='gc params 10mfd',source_params='source_params', pumpfilters_params='pumpfilter params',
                     asefilters_params='idler filter params filter')

    @classmethod
    def get_default_param_values(cls) -> dict:
        return dict(taper_length=None,grating5_params=None,grating10_params=None,
        source_params=None,
                    pumpfilters_params=None,
                    asefilters_params=None
         )

    def draw_layout(self) -> None:
        self.create_ase_filter()
        self.place_ase_filter()
        self.create_taper()
        self.create_source()
        self.place_source()
        self.create_pump_filter()
        self.place_pump_filter()
        self.create_greating()
        self.place_input_gc()
        self.place_output_gc()

    def create_greating(self) -> None:
        grating_module = importlib.import_module(self.grating5_params['package'])
        grating_class = getattr(grating_module, self.grating5_params['class'])
        self.grating_master5 = self.new_template(params={'gds_path': 'dummy'},
                                                           temp_cls=grating_class)
        grating_module = importlib.import_module(self.grating10_params['package'])
        grating_class = getattr(grating_module, self.grating10_params['class'])
        self.grating_master10 = self.new_template(params={'gds_path': 'dummy'},
                                                 temp_cls=grating_class)

    def create_pump_filter(self) -> None:
        self.filters_master['pump'] = self.new_template(params=self.pumpfilter_params,
                                                                   temp_cls=Pumpfilter)

    def create_ase_filter(self) -> None:
        self.filters_master['ase'] = self.new_template(params=self.asefilter_params,
                                                          temp_cls=asefilter)

    def create_taper(self) -> None:
        taperparam = dict(port_layer=self.source_params['spoked_ring_params']['port_layer'], width0=self.asefilter_params['ase_filter_params']['arb_ring_params']['wg_out_params']['width'], width1=self.source_params['spoked_ring_params']['wg_width'],
                      length=self.taper_length, layer=self.source_params['spoked_ring_params']['layer'])
        self.taper_master = self.new_template(params=taperparam, temp_cls=LinearTaper)

    def create_source(self) -> None:
        self.filters_master['source'] = self.new_template(params=self.source_params,
                                                          temp_cls=RingSensable)

    def place_pump_filter(self) -> None:
        self.filters['pump'] = self.add_instance_port_to_port(inst_master=self.filters_master['pump'],
                                       instance_port_name='PORT_IN',
                                       self_port=self.taper['out']['PORT0'],
                                       reflect=False)
    # ##delete this when finished troubleshooting
    # def place_pump_filter(self) -> None:
    #     self.filters['pump'] = self.add_instance_port_to_port(inst_master=self.filters_master['pump'],
    #                                    instance_port_name='PORT_IN',
    #                                    self_port=self.filters['ase']['PORT_DROP'],
    #                                    reflect=False)
    # ##delete above when finished troubleshooting

    def place_ase_filter(self) -> None:
        self.filters['ase'] = self.add_instance(self.filters_master['ase'],
                                                 loc=(0, 0),
                                                 orient='R0')

    def place_source(self) -> None:
        self.taper['in'] = self.add_instance_port_to_port(inst_master=self.taper_master,
                                                                instance_port_name='PORT0',
                                                                self_port=self.filters['ase']['PORT_DROP'],
                                                                reflect=False)
        self.filters['source']=self.add_instance_port_to_port(inst_master=self.filters_master['source'],
                                       instance_port_name='PORT0',
                                       self_port=self.taper['in']['PORT1'],
                                       reflect=False)
        self.taper['out'] = self.add_instance_port_to_port(inst_master=self.taper_master,
                                                                instance_port_name='PORT1',
                                                                self_port=self.filters['source']['PORT1'],
                                                                reflect=False)

    def place_input_gc(self) -> None:
        self.gc['in_pump'] = self.add_instance_port_to_port(inst_master=self.grating_master10,
                                       instance_port_name='PORT_OUT',
                                       self_port=self.filters['ase']['PORT_IN'],
                                       reflect=False)

        self.gc['in_test'] = self.add_instance_port_to_port(inst_master=self.grating_master10,
                                                            instance_port_name='PORT_OUT',
                                                            self_port=self.filters['ase']['PORT_TEST'],
                                                            reflect=False)


    def place_output_gc(self) -> None:
        self.gc['out_signal'] = self.add_instance_port_to_port(inst_master=self.grating_master10,
                                       instance_port_name='PORT_OUT',
                                       self_port=self.filters['pump']['PORT_OUT_S'],
                                       reflect=False)

        self.gc['out_pump'] = self.add_instance_port_to_port(inst_master=self.grating_master10,
                                                            instance_port_name='PORT_OUT',
                                                            self_port=self.filters['pump']['PORT_OUT_P'],
                                                            reflect=False)
        self.gc['out_idler'] = self.add_instance_port_to_port(inst_master=self.grating_master10,
                                                              instance_port_name='PORT_OUT',
                                                              self_port=self.filters['pump']['PORT_OUT_I'],
                                                              reflect=False)
        self.gc['out_ase_test'] = self.add_instance_port_to_port(inst_master=self.grating_master5,
                                                            instance_port_name='PORT_OUT',
                                                            self_port=self.filters['ase']['PORT_THROUGH'],
                                                            reflect=False)

class sourceandfilters(BPG.PhotonicTemplateBase):
    """
    This class creates an unbalanced MZI with an input and output rac coupler.
    Parameters
    ----------
    rac_params : dict
        dict of parameters to be sent to the directional coupler master

    """

    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)
        self.pumpfilter_params=self.params['pumpfilters_params']
        self.asefilter_params = self.params['asefilters_params']
        self.source_params = self.params['source_params']
        self.grating5_params = self.params['grating5_params']
        self.grating10_params = self.params['grating10_params']
        self.taper_length = self.params['taper_length']
        # Master declaration

        self.filters_master = dict()
        self.wgs_master = dict()
        self.grating_master5=None
        self.grating_master10=None
        self.taper_master=None
        # Instances declaration
        self.filters = dict()
        self.wgs = dict()
        self.gc = dict()
        self.taper = dict()


    @classmethod
    def get_params_info(cls) -> dict:
        return dict(taper_length='taper length connecting soruce and filters',grating5_params='gc params 5mfd',grating10_params='gc params 10mfd',source_params='source_params', pumpfilters_params='pumpfilter params',
                     asefilters_params='idler filter params filter')

    @classmethod
    def get_default_param_values(cls) -> dict:
        return dict(taper_length=None,grating5_params=None,grating10_params=None,
        source_params=None,
                    pumpfilters_params=None,
                    asefilters_params=None
         )

    def draw_layout(self) -> None:
        self.create_ase_filter()
        self.place_ase_filter()
        self.create_taper()
        self.create_source()
        self.place_source()
        self.create_pump_filter()
        self.place_pump_filter()
        self.create_greating()
        self.place_input_gc()
        self.place_output_gc()

    def create_greating(self) -> None:
        grating_module = importlib.import_module(self.grating5_params['package'])
        grating_class = getattr(grating_module, self.grating5_params['class'])
        self.grating_master5 = self.new_template(params={'gds_path': 'dummy'},
                                                           temp_cls=grating_class)
        grating_module = importlib.import_module(self.grating10_params['package'])
        grating_class = getattr(grating_module, self.grating10_params['class'])
        self.grating_master10 = self.new_template(params={'gds_path': 'dummy'},
                                                 temp_cls=grating_class)

    def create_pump_filter(self) -> None:
        self.filters_master['pump'] = self.new_template(params=self.pumpfilter_params,
                                                                   temp_cls=Pumpfilter)

    def create_ase_filter(self) -> None:
        self.filters_master['ase'] = self.new_template(params=self.asefilter_params,
                                                          temp_cls=asefilter)

    def create_taper(self) -> None:
        taperparam = dict(port_layer=self.source_params['spoked_ring_params']['port_layer'], width0=self.asefilter_params['ase_filter_params']['arb_ring_params']['wg_out_params']['width'], width1=self.source_params['spoked_ring_params']['wg_width'],
                      length=self.taper_length, layer=self.source_params['spoked_ring_params']['layer'])
        self.taper_master = self.new_template(params=taperparam, temp_cls=LinearTaper)

    def create_source(self) -> None:
        self.filters_master['source'] = self.new_template(params=self.source_params,
                                                          temp_cls=RingSensable)

    def place_pump_filter(self) -> None:
        self.filters['pump'] = self.add_instance_port_to_port(inst_master=self.filters_master['pump'],
                                       instance_port_name='PORT_IN',
                                       self_port=self.taper['out']['PORT0'],
                                       reflect=False)
    # ##delete this when finished troubleshooting
    # def place_pump_filter(self) -> None:
    #     self.filters['pump'] = self.add_instance_port_to_port(inst_master=self.filters_master['pump'],
    #                                    instance_port_name='PORT_IN',
    #                                    self_port=self.filters['ase']['PORT_DROP'],
    #                                    reflect=False)
    # ##delete above when finished troubleshooting

    def place_ase_filter(self) -> None:
        self.filters['ase'] = self.add_instance(self.filters_master['ase'],
                                                 loc=(0, 0),
                                                 orient='R0')

    def place_source(self) -> None:
        self.taper['in'] = self.add_instance_port_to_port(inst_master=self.taper_master,
                                                                instance_port_name='PORT0',
                                                                self_port=self.filters['ase']['PORT_DROP'],
                                                                reflect=False)
        self.filters['source']=self.add_instance_port_to_port(inst_master=self.filters_master['source'],
                                       instance_port_name='PORT0',
                                       self_port=self.taper['in']['PORT1'],
                                       reflect=False)
        self.taper['out'] = self.add_instance_port_to_port(inst_master=self.taper_master,
                                                                instance_port_name='PORT1',
                                                                self_port=self.filters['source']['PORT1'],
                                                                reflect=False)

    def place_input_gc(self) -> None:
        self.gc['in_pump'] = self.add_instance_port_to_port(inst_master=self.grating_master5,
                                       instance_port_name='PORT_OUT',
                                       self_port=self.filters['ase']['PORT_IN'],
                                       reflect=False)

        self.gc['in_test'] = self.add_instance_port_to_port(inst_master=self.grating_master5,
                                                            instance_port_name='PORT_OUT',
                                                            self_port=self.filters['ase']['PORT_THROUGH'],
                                                            reflect=False)


    def place_output_gc(self) -> None:
        self.gc['out_signal'] = self.add_instance_port_to_port(inst_master=self.grating_master10,
                                       instance_port_name='PORT_OUT',
                                       self_port=self.filters['pump']['PORT_OUT_S'],
                                       reflect=False)
        layersi = self.pumpfilter_params['signal_filter_params']['arb_ring_params']['wg_in_params']['layer']
        buswgwidth = self.pumpfilter_params['signal_filter_params']['arb_ring_params']['wg_in_params']['width']
        yf = self.filters['ase']._photonic_port_list['PORT_TEST'].center[1]
        yf2 = self.filters['pump']._photonic_port_list['PORT_OUT_P'].center[1]
        wgparams = dict(layer=layersi,
                        width=buswgwidth, points=[(0.0, 0.0), (abs(yf-yf2), 0.0)])
        self.wgs_master['outextratest'] = self.new_template(params=wgparams, temp_cls=WaveguideBase)

        self.wgs['outextratest'] = self.add_instance_port_to_port(inst_master=self.wgs_master['outextratest'],
                                                             instance_port_name='PORT0',
                                                             self_port=self.filters['ase']['PORT_TEST'],
                                                             reflect=False)

        self.gc['out_pump'] = self.add_instance_port_to_port(inst_master=self.grating_master5,
                                                            instance_port_name='PORT_OUT',
                                                            self_port=self.filters['pump']['PORT_OUT_P'],
                                                            reflect=False)
        self.gc['out_idler'] = self.add_instance_port_to_port(inst_master=self.grating_master10,
                                                              instance_port_name='PORT_OUT',
                                                              self_port=self.filters['pump']['PORT_OUT_I'],
                                                              reflect=False)
        self.gc['out_ase_test'] = self.add_instance_port_to_port(inst_master=self.grating_master5,
                                                            instance_port_name='PORT_OUT',
                                                            self_port=self.wgs['outextratest']['PORT1'],
                                                           reflect=False)