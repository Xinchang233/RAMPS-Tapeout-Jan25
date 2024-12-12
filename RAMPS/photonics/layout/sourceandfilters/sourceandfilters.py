import BPG
import importlib
#from layout.SinglePhotonSource.SinglePhotonSource import SinglePhotonSource
#from layout.Pumpfilter.Pumpfilter import Pumpfilter
from copy import deepcopy
from bag.layout.util import BBox

class sourceandfilters4r(BPG.PhotonicTemplateBase):
    """
    This class creates an unbalanced MZI with an input and output rac coupler.
    Parameters
    ----------
    rac_params : dict
        dict of parameters to be sent to the directional coupler master

    """

    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)

        self.singlephotonsource_params=self.params['singlephotonsource_params']
        device_module = importlib.import_module(self.singlephotonsource_params['package'])
        self.SinglePhotonSource = getattr(device_module, self.singlephotonsource_params['class'])

        self.pumpfilter_params = self.params['pumpfilter_params']
        device_module = importlib.import_module(self.pumpfilter_params['package'])
        self.Pumpfilter = getattr(device_module, self.pumpfilter_params['class'])

        self.grating5_params = self.params['grating5_params']
        self.grating10_params = self.params['grating10_params']
        self.pin_labels = self.params['pin_labels']
        self.array_index = self.params['array_index']
        # Master declaration
        self.singlephotonsource_master = None
        self.pumpfilter_master = None
        self.grating_master5=None
        self.grating_master10=None
        # Instances declaration
        self.singlephotonsource = None
        self.pumpfilter = None
        self.gc = dict()

    @classmethod
    def get_params_info(cls) -> dict:
        return dict(singlephotonsource_params='parameters for the single photon source',
                    pumpfilter_params='parameters for the pump filter',grating5_params='5mfd gc',grating10_params='10mfd gc',
                    pin_labels='names of the labels',array_index='index in array',
                    )

    @classmethod
    def get_default_param_values(cls) -> dict:
        return dict(singlephotonsource_params=None,grating5_params=None,grating10_params=None,
                    pumpfilter_params=None, pin_labels=None,array_index=None,
         )

    def draw_layout(self) -> None:
        self.create_singlephotonsource()
        self.create_pumpfilter()
        self.place_pumpfilter()
        self.create_greating()
        self.place_gc()

    def create_singlephotonsource(self):
        singlephotonsource_params=deepcopy(self.singlephotonsource_params)
        singlephotonsource_params['pin_labels']=self.pin_labels['singlephotonsource_labels']
        singlephotonsource_params['array_index']=self.array_index
        self.singlephotonsource_master = self.new_template(params=singlephotonsource_params, temp_cls=self.SinglePhotonSource)
        self.singlephotonsource=self.add_instance(master=self.singlephotonsource_master,
                          loc=(0,0),
                          orient='R0'
                          )

    def create_greating(self) -> None:
        grating_module = importlib.import_module(self.grating5_params['package'])
        grating_class = getattr(grating_module, self.grating5_params['class'])
        self.grating_master5 = self.new_template(params={'gds_path': 'dummy'},
                                                 temp_cls=grating_class)
        grating_module = importlib.import_module(self.grating10_params['package'])
        grating_class = getattr(grating_module, self.grating10_params['class'])
        self.grating_master10 = self.new_template(params={'gds_path': 'dummy'},
                                                  temp_cls=grating_class)

    def create_pumpfilter(self):
        pumpfilter_params=deepcopy(self.pumpfilter_params)
        idler = dict()
        idler['0'] = (78.5, -63.13)
        idler['1'] = (78.5, -64.6)
        idler['2'] = (78.5, -83.5)
        idler['3'] = (78.5, -85)
        signal = dict()
        signal['0'] = (153.5, -63.13)
        signal['1'] = (153.5, -64.6)
        signal['2'] = (153.5, -83.5)
        signal['3'] = (153.5, -85)
        for i in signal:
            # heater contact label 1
            bbox = BBox(
                top=signal[str(i)][1]+0.5,
                bottom=signal[str(i)][1]-0.5,
                left=signal[str(i)][0]-0.5,
                right=signal[str(i)][0]+0.5,
                resolution=self.grid.resolution
            )
            if (int(i) % 2)==0:
                heater_label = self.pin_labels['signal_filter_labels']['heater_label_1']
            else:
                heater_label = self.pin_labels['signal_filter_labels']['heater_label_2'] + '_Site' + str(
                    self.array_index) + '[' + str(int((int(i)-1)/2)) + ']'
            # Add labels to via stacks
            self.heater_contact_layers_inds = []
            self.heater_contact_layers = pumpfilter_params['signal_filter_params']['arb_ring_params']['ring_params'][0]['heater_params'][
                'via_stack_params']['top_layer']
            if not isinstance(self.heater_contact_layers, list):
                self.heater_contact_layers = [self.heater_contact_layers]
            for lpp in self.heater_contact_layers:
                self.heater_contact_layers_inds.append(self.grid.tech_info.get_layer_id(lpp[0]))
            self.heater_contact_layers_inds.sort()
            contact_label_layer = self.grid.tech_info.get_layer_name(max(self.heater_contact_layers_inds))
            self.add_pin_primitive(net_name=heater_label, layer=(contact_label_layer, "label"), bbox=bbox)
        for i in idler:
            # heater contact label 1
            bbox = BBox(
                top=idler[str(i)][1] + 0.5,
                bottom=idler[str(i)][1] - 0.5,
                left=idler[str(i)][0] - 0.5,
                right=idler[str(i)][0] + 0.5,
                resolution=self.grid.resolution
            )
            if (int(i) % 2) == 0:
                heater_label = self.pin_labels['idler_filter_labels']['heater_label_1']
            else:
                heater_label = self.pin_labels['idler_filter_labels']['heater_label_2'] + '_Site' + str(
                    self.array_index) + '[' + str(int((int(i) - 1) / 2)) + ']'
            # Add labels to via stacks
            self.heater_contact_layers_inds = []
            self.heater_contact_layers = \
            pumpfilter_params['idler_filter_params']['arb_ring_params']['ring_params'][0]['heater_params'][
                'via_stack_params']['top_layer']
            if not isinstance(self.heater_contact_layers, list):
                self.heater_contact_layers = [self.heater_contact_layers]
            for lpp in self.heater_contact_layers:
                self.heater_contact_layers_inds.append(self.grid.tech_info.get_layer_id(lpp[0]))
            self.heater_contact_layers_inds.sort()
            contact_label_layer = self.grid.tech_info.get_layer_name(max(self.heater_contact_layers_inds))
            self.add_pin_primitive(net_name=heater_label, layer=(contact_label_layer, "label"), bbox=bbox)
        i=2
        for ring in self.pumpfilter_params['signal_filter_params']['arb_ring_params']['ring_params']:
            pumpfilter_params['signal_filter_params']['arb_ring_params']['ring_params'][i-2]['heater_params'][
                'heater_label_1']=self.pin_labels['signal_filter_labels']['heater_label_1']
            pumpfilter_params['signal_filter_params']['arb_ring_params']['ring_params'][i-2]['heater_params'][
                'heater_label_2']=self.pin_labels['signal_filter_labels']['heater_label_2']+'_Site'+str(self.array_index)+'['+str(i)+']'
            i+=1
        i=2
        for ring in self.pumpfilter_params['idler_filter_params']['arb_ring_params']['ring_params']:
            pumpfilter_params['idler_filter_params']['arb_ring_params']['ring_params'][i-2]['heater_params'][
                'heater_label_1']=self.pin_labels['idler_filter_labels']['heater_label_1']
            pumpfilter_params['idler_filter_params']['arb_ring_params']['ring_params'][i-2]['heater_params'][
                'heater_label_2']=self.pin_labels['idler_filter_labels']['heater_label_2']+'_Site'+str(self.array_index)+'['+str(i)+']'
            i+=1
        self.pumpfilter_master=self.new_template(params=pumpfilter_params, temp_cls=self.Pumpfilter)
    def place_pumpfilter(self):
        self.pumpfilter=self.add_instance_port_to_port(inst_master=self.pumpfilter_master,
                                                       instance_port_name='PORT_FILTER',
                                                       self_port=self.singlephotonsource['PORT_SOURCE'],
                                                       reflect=False)
    def place_gc(self) -> None:
        self.gc['out_signal'] = self.add_instance_port_to_port(inst_master=self.grating_master10,
                                                             instance_port_name='PORT_OUT',
                                                            self_port=self.pumpfilter['PORT_OUT_S'],
                                                             reflect=False)
        self.gc['out_idler'] = self.add_instance_port_to_port(inst_master=self.grating_master10,
                                                             instance_port_name='PORT_OUT',
                                                             self_port=self.pumpfilter['PORT_OUT_I'],
                                                             reflect=False)
        self.gc['out_pump'] = self.add_instance_port_to_port(inst_master=self.grating_master5,
                                                             instance_port_name='PORT_OUT',
                                                             self_port=self.singlephotonsource['PORT_OUT_P'],
                                                             reflect=False)
        self.gc['in'] = self.add_instance_port_to_port(inst_master=self.grating_master5,
                                                             instance_port_name='PORT_OUT',
                                                             self_port=self.singlephotonsource['PORT_IN_P'],
                                                             reflect=False)
        self.gc['in_test'] = self.add_instance_port_to_port(inst_master=self.grating_master5,
                                                             instance_port_name='PORT_OUT',
                                                             self_port=self.singlephotonsource['PORT_IN_TEST'],
                                                             reflect=False)
        self.gc['out_ase_test'] = self.add_instance_port_to_port(inst_master=self.grating_master5,
                                                            instance_port_name='PORT_OUT',
                                                            self_port=self.singlephotonsource['PORT_OUT_ASE_TEST'],
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

        self.singlephotonsource_params=self.params['singlephotonsource_params']
        device_module = importlib.import_module(self.singlephotonsource_params['package'])
        self.SinglePhotonSource = getattr(device_module, self.singlephotonsource_params['class'])

        self.pumpfilter_params = self.params['pumpfilter_params']
        device_module = importlib.import_module(self.pumpfilter_params['package'])
        self.Pumpfilter = getattr(device_module, self.pumpfilter_params['class'])

        self.grating5_params = self.params['grating5_params']
        self.grating10_params = self.params['grating10_params']
        self.pin_labels = self.params['pin_labels']
        self.array_index = self.params['array_index']
        # Master declaration
        self.singlephotonsource_master = None
        self.pumpfilter_master = None
        self.grating_master5=None
        self.grating_master10=None
        # Instances declaration
        self.singlephotonsource = None
        self.pumpfilter = None
        self.gc = dict()

    @classmethod
    def get_params_info(cls) -> dict:
        return dict(singlephotonsource_params='parameters for the single photon source',
                    pumpfilter_params='parameters for the pump filter',grating5_params='5mfd gc',grating10_params='10mfd gc',
                    pin_labels='names of the labels',array_index='index in array',
                    )

    @classmethod
    def get_default_param_values(cls) -> dict:
        return dict(singlephotonsource_params=None,grating5_params=None,grating10_params=None,
                    pumpfilter_params=None, pin_labels=None,array_index=None,
         )

    def draw_layout(self) -> None:
        self.create_singlephotonsource()
        self.create_pumpfilter()
        self.place_pumpfilter()
        self.create_greating()
        self.place_gc()

    def create_singlephotonsource(self):
        singlephotonsource_params=deepcopy(self.singlephotonsource_params)
        singlephotonsource_params['pin_labels']=self.pin_labels['singlephotonsource_labels']
        singlephotonsource_params['array_index']=self.array_index
        self.singlephotonsource_master = self.new_template(params=singlephotonsource_params, temp_cls=self.SinglePhotonSource)
        self.singlephotonsource=self.add_instance(master=self.singlephotonsource_master,
                          loc=(0,0),
                          orient='R0'
                          )

    def create_greating(self) -> None:
        grating_module = importlib.import_module(self.grating5_params['package'])
        grating_class = getattr(grating_module, self.grating5_params['class'])
        self.grating_master5 = self.new_template(params={'gds_path': 'dummy'},
                                                 temp_cls=grating_class)
        grating_module = importlib.import_module(self.grating10_params['package'])
        grating_class = getattr(grating_module, self.grating10_params['class'])
        self.grating_master10 = self.new_template(params={'gds_path': 'dummy'},
                                                  temp_cls=grating_class)

    def create_pumpfilter(self):
        pumpfilter_params=deepcopy(self.pumpfilter_params)
        i=0
        for ring in self.pumpfilter_params['signal_filter_params']['arb_ring_params']['ring_params']:
            pumpfilter_params['signal_filter_params']['arb_ring_params']['ring_params'][i]['heater_params'][
                'heater_label_1']=self.pin_labels['signal_filter_labels']['heater_label_1']
            pumpfilter_params['signal_filter_params']['arb_ring_params']['ring_params'][i]['heater_params'][
                'heater_label_2']=self.pin_labels['signal_filter_labels']['heater_label_2']+'_Site'+str(self.array_index)+'['+str(i)+']'
            i+=1
        i=0
        for ring in self.pumpfilter_params['idler_filter_params']['arb_ring_params']['ring_params']:
            pumpfilter_params['idler_filter_params']['arb_ring_params']['ring_params'][i]['heater_params'][
                'heater_label_1']=self.pin_labels['idler_filter_labels']['heater_label_1']
            pumpfilter_params['idler_filter_params']['arb_ring_params']['ring_params'][i]['heater_params'][
                'heater_label_2']=self.pin_labels['idler_filter_labels']['heater_label_2']+'_Site'+str(self.array_index)+'['+str(i)+']'
            i+=1
        self.pumpfilter_master=self.new_template(params=pumpfilter_params, temp_cls=self.Pumpfilter)
    def place_pumpfilter(self):
        self.pumpfilter=self.add_instance_port_to_port(inst_master=self.pumpfilter_master,
                                                       instance_port_name='PORT_FILTER',
                                                       self_port=self.singlephotonsource['PORT_SOURCE'],
                                                       reflect=False)
    def place_gc(self) -> None:
        self.gc['out_signal'] = self.add_instance_port_to_port(inst_master=self.grating_master10,
                                                             instance_port_name='PORT_OUT',
                                                            self_port=self.pumpfilter['PORT_OUT_S'],
                                                             reflect=False)
        self.gc['out_idler'] = self.add_instance_port_to_port(inst_master=self.grating_master10,
                                                             instance_port_name='PORT_OUT',
                                                             self_port=self.pumpfilter['PORT_OUT_I'],
                                                             reflect=False)
        self.gc['out_pump'] = self.add_instance_port_to_port(inst_master=self.grating_master5,
                                                             instance_port_name='PORT_OUT',
                                                             self_port=self.singlephotonsource['PORT_OUT_P'],
                                                             reflect=False)
        self.gc['in'] = self.add_instance_port_to_port(inst_master=self.grating_master5,
                                                             instance_port_name='PORT_OUT',
                                                             self_port=self.singlephotonsource['PORT_IN_P'],
                                                             reflect=False)
        self.gc['in_test'] = self.add_instance_port_to_port(inst_master=self.grating_master5,
                                                             instance_port_name='PORT_OUT',
                                                             self_port=self.singlephotonsource['PORT_IN_TEST'],
                                                             reflect=False)
        self.gc['out_ase_test'] = self.add_instance_port_to_port(inst_master=self.grating_master5,
                                                            instance_port_name='PORT_OUT',
                                                            self_port=self.singlephotonsource['PORT_OUT_ASE_TEST'],
                                                            reflect=False)


if __name__ == '__main__':
    spec_file = 'layout/sourceandfilters/specs/sourceandfilters_imbert.yaml'
    PLM = BPG.PhotonicLayoutManager(spec_file)
    PLM.generate_content()
    PLM.generate_gds()
    PLM.dataprep_calibre()  # Comment out for faster iteration

    # PLM.generate_flat_content()
    # PLM.generate_lsf()
