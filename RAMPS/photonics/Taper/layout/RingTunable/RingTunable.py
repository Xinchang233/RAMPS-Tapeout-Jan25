import BPG
from layout.SimpleRing.SimpleRing import SimpleRing
from layout.RingTunable.RingHeater import RingHeater


class RingTunable(BPG.PhotonicTemplateBase):
    """
    Ring with Heater Script class
    """

    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)

        self.ring_params = self.params['ring_params']
        self.heater_params = self.params['heater_params']

        # Master declaration
        self.ring_master = dict()
        self.heater_master = dict()

        # Instances declaration
        self.ring = dict()
        self.heater = dict()

    @classmethod
    def get_params_info(cls):
        return dict(
            ring_params='This is the ring that is to be tuned',
            heater_params='This is the heater for the ring that tunes it',
            ring_heater_gap = 'This is the gap between the heater and the ring',
            ring_orientation = 'This is the orientation (e.g R0,R90) of the heater ring',
        )

    @classmethod
    def get_default_param_values(cls):
        return dict(
            ring_params=None,
            heater_params=None,
            ring_heater_gap = 1.42,
            ring_orientation = 'R0',
            # whatever value you might want to hard-code in the .py file rather than the .yaml file
        )

    def draw_layout(self) -> None:
        # Create layouts
        self.create_ring()
        self.create_heater()
        # Place layouts
        self.place_ring()
        self.place_heater()
       # temp=self.heater.master._layout._pin_list
      #  self.extract_photonic_ports(inst=self.heater, port_names=['PORT_OUT'])
        self.extract_pins_from_inst(inst=self.heater, pins=self.heater_params['heater_label_1'])
        self.extract_pins_from_inst(inst=self.heater, pins=self.heater_params['heater_label_2'])


    def create_ring(self):
        self.ring_master = self.new_template(params=self.ring_params, temp_cls=SimpleRing)

    def create_heater(self):
        # Extract values
        self.heater_params['ring_params']['r_out'] = self.ring_params['r_out'] - \
                                                     self.ring_params['ring_width'] - \
                                                     self.params['ring_heater_gap']
        self.heater_master = self.new_template(params=self.heater_params, temp_cls=RingHeater)

    def place_ring(self):
        self.ring=self.add_instance(master=self.ring_master, loc=(0, 0), orient='R0', unit_mode=False)

    def place_heater(self):
        self.ring_orientation=self.params['ring_orientation']
        self.heater=self.add_instance(master=self.heater_master, loc=(0,0), orient=self.ring_orientation, unit_mode=False)




