import BPG
import importlib
from copy import deepcopy

class twosourceandfilters(BPG.PhotonicTemplateBase):
    """
    This class creates an unbalanced MZI with an input and output rac coupler.
    Parameters
    ----------
    rac_params : dict
        dict of parameters to be sent to the directional coupler master

    """

    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)

        self.s1=self.params['system1']
        self.s2 = self.params['system2']
        self.pin_labels = self.params['pin_labels']
        self.array_index=self.params['array_index']

        # Master declaration
        self.system_master = dict()

        # Instances declaration
        self.system = dict()


    @classmethod
    def get_params_info(cls) -> dict:
        return dict(offsetx='offset x', offsety='offset y', system1='system 1 param',system2='system 2 param',
                    pin_labels='labels for pins for wires', array_index='index of array'
                    )

    @classmethod
    def get_default_param_values(cls) -> dict:
        return dict(offsetx=None, offsety=None, system1=None, system2=None, pin_labels=None, array_index=None
         )

    def draw_layout(self) -> None:
        self.create_system()

    def create_system(self):
        s1=deepcopy(self.s1)
        device_module = importlib.import_module(s1['package_source'])
        sourceandfilters1 = getattr(device_module, s1['class_source'])
        s1['pin_labels']=self.pin_labels
        s1['array_index']=self.array_index+1
        self.system_master['s1'] = self.new_template(params=s1, temp_cls=sourceandfilters1)
        s2=deepcopy(self.s2)
        device_module = importlib.import_module(s2['package_source'])
        sourceandfilters2 = getattr(device_module, s2['class_source'])
        s2['pin_labels'] = self.pin_labels
        s2['array_index']=self.array_index
        self.system_master['s2'] = self.new_template(params=s2, temp_cls=sourceandfilters2)

        self.system['s1']=self.add_instance(master=self.system_master['s1'],
                          loc=(0,0),
                          orient='R0'
                          )
        self.system['s2'] = self.add_instance(master=self.system_master['s2'],
                                              loc=(self.params['offsetx'], self.params['offsety']),
                                              orient='R180'
                                              )




if __name__ == '__main__':
    spec_file = 'layout/twosourceandfilters/specs/twosourceandfilters_gaptest.yaml'
    PLM = BPG.PhotonicLayoutManager(spec_file)
    PLM.generate_content()
    PLM.generate_gds()
    #PLM.dataprep_calibre()  # Comment out for faster iteration

    # PLM.generate_flat_content()
    # PLM.generate_lsf()
