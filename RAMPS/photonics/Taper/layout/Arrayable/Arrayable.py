import BPG
import importlib
import numpy as np
from copy import deepcopy

""" This class is used to create array of layout class specified in yaml file.
    Instances of class are placed in row with horizontal distance between them.
    Every row will hold inst_per_row instances.
    When inst_per_row is reached, next instances will be placed in the next row.
    Rows are separated by vertical_distance. Also, adjacent rows can be horizontally displaced
    by amount horizontal_offset.     
    """


class Arrayable(BPG.PhotonicTemplateBase):
    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)
        self.params = deepcopy(params)
        self.package = self.params['package']
        self.class_name = params['class_name']
        self.class_params = params['class_params']
        self.module = importlib.import_module(self.package)

        self.horizontal_distance = params['horizontal_distance']
        self.vertical_distance = params['vertical_distance']
        self.horizontal_offset = params['horizontal_offset']
        self.inst_per_row = params['instances_per_row']

        self.pack_params = params['pack_params']
        if self.pack_params:
            self.params_per_cell = params['params_per_cell']

        self.templates = []
        self.placed = []
        self.cords = (0, 0)
        self.temp_cls = None

    @classmethod
    def get_default_param_values(cls) -> dict:
        return dict(
            class_name=None,
            class_params=None,
            left_top_port=None,
            horizontal_distance=None,
            vertical_distance=None,
            horizontal_offset=None,
            instances_per_row=None,
            pack_params=None,
            params_per_cell=None
        )

    @classmethod
    def get_params_info(cls) -> dict:
        return dict(
            package='Path to the class',
            class_name="Name of the class to be instantiated",
            class_params="List of parameters to be passed to the desired class",
            horizontal_distance="Distance between adjacent instances in the row",
            vertical_distance='Distances between the rows of instances',
            horizontal_offset='Offset between adjacent rows',
            instances_per_row="Number of instances per row",
            pack_params='If user has a wrapper class that places same instances of parent class so to minimaze '
                        'footprint you can pack n dicts of parameters  and pass them to your wrapper class. '
                        'Usually set to False.',
            params_per_cell='If pack_params is set to True then packing of parameters will be done with params_per_cell'
        )

    def draw_layout(self) -> None:
        self.create_all_instances()
        self.place_all_instances()

    def create_all_instances(self) -> None:
        # Get class
        cls = getattr(self.module, self.class_name)
        if self.pack_params:
            i = 0

            while i < len(self.class_params):
                try:
                    params = dict()
                    params['layer'] = self.class_params[0]['layer']
                    params['port_layer'] = self.class_params[0]['port_layer']
                    params['vertical_displacement'] = self.vertical_distance
                    params['horizontal_displacement'] = self.horizontal_distance
                    params['class_params'] = [self.class_params[i], self.class_params[i + 1]]

                    template = self.new_template(params=params, temp_cls=cls)
                    self.templates.append((template, self.class_params[i]))
                    i += 2
                except:
                    raise ValueError('Odd number of cells present')
        else:
            for i in range(len(self.class_params)):
                template = self.new_template(params=self.class_params[i], temp_cls=cls)
                self.templates.append((template, self.class_params[i]))

    def place_all_instances(self) -> None:
        # Initialize instance counter to 0
        counter = 0
        y_displacement = 0
        for i in range(len(self.templates)):
            if i == 0:
                placed = self.add_instance(self.templates[i][0], loc=(
                    self.cords[0], abs(self.templates[0][0].bound_box.bottom) + self.vertical_distance), orient='R0')
                self.placed.append(placed)
                counter += 1
                max_height = 0
                current = self.templates[i][0].bound_box
                previous = self.templates[i][0].bound_box
            else:
                current = self.templates[i][
                    0].bound_box  # Get info for the next instance to be placed, in order not to overlap with it
                previous = placed.bound_box

                if counter == self.inst_per_row:
                    counter = 0
                    y_displacement = max_height
                    self.cords = (self.horizontal_offset, y_displacement + abs(current.bottom) + self.vertical_distance)

                    if self.horizontal_offset == self.params['horizontal_offset']:
                        self.horizontal_offset = 0
                    else:
                        self.horizontal_offset = self.params['horizontal_offset']
                else:
                    self.cords = (previous.right - current.left + self.horizontal_distance,
                                  y_displacement + abs(current.bottom) + self.vertical_distance)

                placed = self.add_instance(self.templates[i][0], loc=self.cords, orient='R0')
                self.placed.append(placed)
                max_height = max(max_height, placed.bound_box.top)
                counter += 1

    def place_ports(self) -> None:
        self.add_photonic_port(
            name='PORT_L',
            orient='R0',
            center=(0, 0),
            width=1,
            layer=['SI', 'port'],
            resolution=self.grid.resolution,
            unit_mode=False,
            show=False)
