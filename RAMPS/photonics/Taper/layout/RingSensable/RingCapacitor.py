import BPG
from Photonic_Core_Layout.ViaStack_test.ViaStack import ViaStack
from BPG.objects import PhotonicRound

class RingCapacitor(BPG.PhotonicTemplateBase):
    """This class creates nothing. It just serves as an template for what a real code might look like.
    -------------
    Template parameters: None
    """
    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)
        self.capacitor_params = self.params["capacitor_params"]
        self.via_stack_params = self.params["via_stack_params"]

        #Master declaration
        self.capacitor_master = dict()
        self.via_stack_master = dict()

        #Instances declaration
        self.capacitor = dict()
        self.via_stacks = dict()

    @classmethod
    def get_params_info(cls):
        return dict(
            capacitor_params='This is a blurb that describes what component 1 does',
            via_stack_params='This is a blurb that describes what component 2 does',
                    )

    @classmethod
    def get_default_param_values(cls):
        return dict(
            capacitor_params=None,
            via_stack_params=None,
        )

    def draw_layout(self) -> None:
        self.create_capacitor()
        self.create_via_stacks()
        self.place_via_stacks() #order has to be correct, so place must be after create

    def create_capacitor(self):
        self.add_obj(PhotonicRound(
            layer=self.capacitor_params['layer'],
            resolution=self.grid.resolution,
            center=(0,0),
            rout=self.capacitor_params['rCenter']+self.capacitor_params['width']/2,
            rin = self.capacitor_params['rCenter']-self.capacitor_params['width']/2,
            theta0=self.capacitor_params['start_angle'],
            theta1=self.capacitor_params['stop_angle'],
            unit_mode=False
            ))
        self.add_obj(PhotonicRound(
            layer=self.capacitor_params['layer'],
            resolution=self.grid.resolution,
            center=(0,0),
            rout=self.capacitor_params['rCenter'] + self.capacitor_params['width'] / 2,
            rin=self.capacitor_params['rCenter'] - self.capacitor_params['width'] / 2,
            theta0=self.capacitor_params['start_angle']+180,
            theta1=self.capacitor_params['stop_angle']+180,
            unit_mode=False
            ))


    def create_via_stacks(self):
        self.via_stack_master['via_stack_1'] = self.new_template(params=self.via_stack_params,
                                                                 temp_cls=ViaStack)
        self.via_stack_master['via_stack_2'] = self.new_template(params=self.via_stack_params,
                                                                 temp_cls=ViaStack)

    def place_via_stacks(self):
        rCenter = self.capacitor_params['rCenter']
        via_stack_left = (-rCenter,0)
        via_stack_right = (rCenter,0)
        self.via_stacks['via_stack_1'] = self.add_instance(self.via_stack_master['via_stack_1'],
                                                 loc=via_stack_left,
                                                 orient='R0')
        self.via_stacks['via_stack_2'] = self.add_instance(self.via_stack_master['via_stack_2'],
                                                 loc=via_stack_right,
                                                 orient='R0')

        self.add_photonic_port(
            name='via_stack_left',
            center=via_stack_left,
            orient='R180',
            width=self.via_stack_params['top_x_span'],
            layer=('si_full_free','port'),
            overwrite_purpose=False,
            resolution=self.grid.resolution,
            unit_mode=False,
            show=False,
        )
        self.add_photonic_port(
            name='via_stack_right',
            center=via_stack_right,
            orient='R180',
            width=self.via_stack_params['top_x_span'],
            layer=('si_full_free','port'),
            overwrite_purpose=False,
            resolution=self.grid.resolution,
            unit_mode=False,
            show=False,
        )