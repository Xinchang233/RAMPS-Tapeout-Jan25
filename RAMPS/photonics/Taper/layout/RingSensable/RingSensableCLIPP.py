import BPG
from layout.SimpleRing.SimpleRing import SimpleRing
from layout.RingTunable.RingHeater import RingHeater
from layout.RingSensable.RingCapacitor import RingCapacitor
from numpy import pi


class RingSensableCLIPP(BPG.PhotonicTemplateBase):
    """
    Photosensing Ring using CLIPP probe with Heater Script class
    """

    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)

        self.ring_params = self.params['ring_params']
        self.heater_params = self.params['heater_params']
        self.capacitor_params = self.params['capacitor_params']
        self.capacitor_orientation = self.capacitor_params['orientation']

        # Master declaration
        self.ring_master = dict()
        self.heater_master = dict()
        self.capacitor_master = dict()

        # Instances declaration
        self.ring = dict()
        self.heater = dict()
        self.capacitor = dict()

    @classmethod
    def get_params_info(cls):
        return dict(
            ring_params='This is the ring that is to be tuned',
            heater_params='This is the heater for the ring that tunes it',
            capacitor_params='This is the CLIPP capacitor above the ring',
            capacitor_orientation='This allows you to rotate the capacitor',
            ring_heater_gap = 'This is the gap between the heater and the ring',
            ring_orientation = 'This is the orientation (e.g R0,R90) of the heater ring',
        )

    @classmethod
    def get_default_param_values(cls):
        return dict(
            ring_params=None,
            heater_params=None,
            capacitor_params=None,
            capacitor_orientation='R90',
            ring_heater_gap = 1.42,
            ring_orientation = 'R0',
            # whatever value you might want to hard-code in the .py file rather than the .yaml file
        )

    def draw_layout(self) -> None:
        # Create layouts
        self.create_ring()
        if self.heater_params:
            self.create_heater()
        self.create_capacitor()
        # Place layouts
        self.place_ring()
        if self.heater_params:
            self.place_heater()
        self.place_capacitor()

    def create_ring(self):
        self.ring_master = self.new_template(params=self.ring_params, temp_cls=SimpleRing)

    def create_heater(self):
        # Extract values
        self.heater_params['ring_params']['r_out'] = self.ring_params['r_out'] - \
                                                     self.ring_params['ring_width'] - \
                                                     self.params['ring_heater_gap']
        # Create instance
        self.heater_master = self.new_template(params=self.heater_params, temp_cls=RingHeater)

    def create_capacitor(self):
        rCenter = self.ring_params['r_out'] - self.ring_params['ring_width'] / 2
        self.capacitor_params['capacitor_params']['rCenter'] = rCenter
        distance = self.capacitor_params['capacitor_params']['capacitor_distance']
        phi = 180*distance/(pi*rCenter)
        theta = 180-phi
        self.capacitor_params['capacitor_params']['start_angle'] = -theta/2
        self.capacitor_params['capacitor_params']['stop_angle'] = theta/2
        self.capacitor_params['via_stack_params']['bottom_layer'] = self.capacitor_params['capacitor_params']['layer']
        self.capacitor_master = self.new_template(params=self.capacitor_params, temp_cls=RingCapacitor)

    def place_ring(self):
        self.ring=self.add_instance(master=self.ring_master, loc=(0, 0), orient='R0', unit_mode=False)

    def place_heater(self):
        self.ring_orientation=self.params['ring_orientation']
        self.heater=self.add_instance(master=self.heater_master, loc=(0,0), orient=self.ring_orientation, unit_mode=False)

    def place_capacitor(self):
        self.capacitor=self.add_instance(master=self.capacitor_master, loc=(0,0), orient=self.capacitor_orientation, unit_mode=False)




