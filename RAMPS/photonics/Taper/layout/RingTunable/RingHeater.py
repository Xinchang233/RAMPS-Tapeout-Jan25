import BPG
from Photonic_Core_Layout.ViaStack_test.ViaStack import ViaStack
from layout.SimpleRing.SimpleRing import SimpleRing
from layout.RingTunable.DesignHeater import DesignHeater
from BPG.objects import PhotonicRect, PhotonicRound
from bag.layout.util import BBox


class RingHeater(BPG.PhotonicTemplateBase):
    """This class creates a heater for a ring.
    -------------
    Template parameters:
    ViaStack: -top layer, bottom layer
            top_x_span, top_y_span, bottom_x_span, bottom_y_span
    Spoke: via_stack_spacing_from_heater, spoke_width
    Ring: heater_rOut, heater_width, heater_layer
    """

    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)
        self.ring_params = self.params['ring_params']
        self.contact_params = self.params["contact_params"]
        self.via_stack_params = self.params["via_stack_params"]
        self.doping_disk_params = self.params["doping_disk_params"]

        # Master declaration
        self.ring_master = dict()
        self.via_stack_master = dict()

        # Instances declaration
        self.ring = dict()
        self.via_stacks = dict()

    @classmethod
    def get_params_info(cls):
        return dict(
            ring_params='This is the doped ring that acts like a metal, heating the ring',
            contact_params='These are the rectangles that protrude radially inwards to keep the metals a suitable'
                         'distance from the silicon ring that the heater is heating, so as to prevent absorption of'
                         'the field by the metal',
            via_stack_params='These are the contacts that connect the silicon spokes of the heater ring to the'
                             'metal wires above',
            doping_margin='How much outside the heater ring the doping layer extrends',
            doping_disk_params='This is the gds layer that is deleted in dataprep that shows which areas should not be'
                                'excluded from doping',
            heater_label_1='This is what you call the left heater contact',
            heater_label_2='This is what you call the right heater contact',
        )

    @classmethod
    def get_default_param_values(cls):
        return dict(
            ring_params=None,
            contact_params=None,
            via_stack_params=None,
            doping_margin=0.1,
            doping_disk_params=None,
            heater_label_1 = 'HeaterLabelLeft',
            heater_label_2 = 'HeaterLabelRight'
            # whatever value you might want to hard-code in the .py file rather than the .yaml file
        )

    def draw_layout(self) -> None:
        # Create layouts
        self.create_ring()
        self.create_contacts()
        self.create_via_stacks()
        self.create_doping_disk()
        # Place layouts
        self.place_ring()
        self.place_via_stacks()

    def create_ring(self):
        if self.ring_params['resistance']:
            self.ring_params['ring_width'] = DesignHeater.design_heater_width_from_resistance(
                resistance=self.ring_params['resistance'],
                heater_rout=self.ring_params['r_out'],
                r_square=self.photonic_tech_info.sheet_resistance(self.ring_params['layer']),
                contact_width=self.contact_params['contact_width'],
                contact_dist=self.contact_params['contact_distance'],
            )
        self.ring_master = self.new_template(params=self.ring_params, temp_cls=SimpleRing)

    def create_contacts(self):
        #Extract values
        self.ring_layer = self.ring_params['layer']
        self.ring_rout = self.ring_params['r_out']
        self.ring_width = self.ring_params['ring_width']
        self.half_contact_distance = self.contact_params['contact_distance']/2
        self.contact_width = self.contact_params['contact_width']

        self.add_obj(PhotonicRect(layer=self.ring_layer,
                                  bbox=BBox(left=-self.ring_rout+self.ring_width, right=-self.half_contact_distance,
                                            top=self.contact_width/2,
                                            bottom=-self.contact_width/2, resolution=self.grid.resolution)))

        self.add_obj(PhotonicRect(layer=self.ring_layer,
                                  bbox=BBox(left=self.half_contact_distance, right=self.ring_rout-self.ring_width,
                                            top=self.contact_width/2,
                                            bottom=-self.contact_width/2, resolution=self.grid.resolution)))

    def create_via_stacks(self):
        self.via_stack_master = self.new_template(params=self.via_stack_params,
                                                                 temp_cls=ViaStack)


    def create_doping_disk(self):
        for disk in self.doping_disk_params:
            self.add_obj(PhotonicRound(
                layer=disk['doping_layer'],
                resolution=self.grid.resolution,
                center=(0,0),
                rout=self.ring_params['r_out']+self.params['doping_margin'],
                unit_mode=False
            ))



    def place_ring(self):
        self.ring=self.add_instance(master=self.ring_master, loc=(0, 0), orient='R0', unit_mode=False)

    def place_via_stacks(self):
        self.via_stacks['via_stack_1']=self.add_instance(master=self.via_stack_master, loc=(-self.half_contact_distance-self.via_stack_params['bottom_x_span']/2,0), orient='R0', unit_mode=False)
        self.via_stacks['via_stack_2'] = self.add_instance(master=self.via_stack_master, loc=(self.half_contact_distance+self.via_stack_params['bottom_x_span']/2,0), orient='R0',
                                             unit_mode=False)
        # Add labels to via stacks
        self.heater_contact_layers_inds = []
        self.heater_contact_layers = self.via_stack_params['top_layer']
        if not isinstance(self.heater_contact_layers, list):
            self.heater_contact_layers = [self.heater_contact_layers]
        for lpp in self.heater_contact_layers:
            self.heater_contact_layers_inds.append(self.grid.tech_info.get_layer_id(lpp[0]))
        self.heater_contact_layers_inds.sort()
        # heater contact label 1
        bbox = BBox(
            top=self.via_stacks['via_stack_1'].bound_box.top,
            bottom=self.via_stacks['via_stack_1'].bound_box.bottom,
            left=self.via_stacks['via_stack_1'].bound_box.left,
            right=self.via_stacks['via_stack_1'].bound_box.right,
            resolution=self.grid.resolution
        )
        contact_label_layer = self.grid.tech_info.get_layer_name(max(self.heater_contact_layers_inds))
        # self.add_label(label=self.params['heater_label_1'], layer=(contact_label_layer, "label"), bbox=bbox)
        if self.params['heater_label_1']:
            self.add_pin_primitive(net_name=self.params['heater_label_1'], layer=(contact_label_layer, "label"), bbox=bbox)

        # heater contact label 2
        bbox = BBox(
            top=self.via_stacks['via_stack_2'].bound_box.top,
            bottom=self.via_stacks['via_stack_2'].bound_box.bottom,
            left=self.via_stacks['via_stack_2'].bound_box.left,
            right=self.via_stacks['via_stack_2'].bound_box.right,
            resolution=self.grid.resolution
        )
        contact_label_layer = self.grid.tech_info.get_layer_name(max(self.heater_contact_layers_inds))
        # self.add_label(label=self.params['heater_label_2'], layer=(contact_label_layer, "label"), bbox=bbox)
        if self.params['heater_label_2']:
            self.add_pin_primitive(net_name=self.params['heater_label_2'], layer=(contact_label_layer, "label"), bbox=bbox)
            # self.add_label(
            #     label=self.params['heater_label_2'],
            #     layer=(contact_label_layer, "label"),
            #     bbox=bbox
            #     )







