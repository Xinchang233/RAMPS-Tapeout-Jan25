import BPG
import importlib
from layout.SinglePhotonSource.SinglePhotonSource import SinglePhotonSource
from layout.Pumpfilter.Pumpfilter_Imbert import Pumpfilter

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
        self.pumpfilter_params=self.params['pumpfilter_params']
        self.grating5_params = self.params['grating5_params']
        self.grating10_params = self.params['grating10_params']
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
                    )

    @classmethod
    def get_default_param_values(cls) -> dict:
        return dict(singlephotonsource_params=None,grating5_params=None,grating10_params=None,
                    pumpfilter_params=None,
         )

    def draw_layout(self) -> None:
        self.create_singlephotonsource()
        self.create_pumpfilter()
        self.place_pumpfilter()
        self.create_greating()
        self.place_gc()

    def create_singlephotonsource(self):
        self.singlephotonsource_master = self.new_template(params=self.singlephotonsource_params, temp_cls=SinglePhotonSource)
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
        self.pumpfilter_master=self.new_template(params=self.pumpfilter_params, temp_cls=Pumpfilter)
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
    # PLM.dataprep_calibre()  # Comment out for faster iteration

    # PLM.generate_flat_content()
    # PLM.generate_lsf()
