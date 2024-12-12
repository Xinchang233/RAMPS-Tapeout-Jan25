from ...triple_rings_full_si.ViaStack.ViaStack import ViaStack
from ...triple_rings_full_si.WaveguideBase.WaveguideBase import WaveguideBase

from BPG.port import PhotonicPort
import random
import string


class RectalinearRouter:

    def __init__(self, gen_cls, init_port, layer, **kwargs):

        self.gen_cls = gen_cls
        self.layer = layer
        self.init_port = init_port
        self.inst = dict()
        self.port = self.init_port

        self.port_layer = ('RX', 'port')

    def route(self, length: float, direction: str, width=None, override_width=False):
        # Process the width
        if not override_width:
            if width is None or width == self.port.width:
                width = self.port.width
            else:
                width = width
        else:
            width = width

        # Process the direction
        if direction.upper() == "S":
            orient = self.port.orientation
            # disp_correction_x = 0
            # disp_correction_y = 0
            if self.port.orientation == 'R0':
                disp_correction_x = -width / 2
                disp_correction_y = 0
            elif self.port.orientation == 'R90':
                disp_correction_x = 0
                disp_correction_y = -width / 2

            elif self.port.orientation == 'R180':
                disp_correction_x = width / 2
                disp_correction_y = 0

            elif self.port.orientation == 'R270':
                disp_correction_x = 0
                disp_correction_y = width / 2

        elif direction.upper() == "R":
            if self.port.orientation == 'R0':
                orient = 'R270'
                disp_correction_x = width / 2
                disp_correction_y = width / 2
            elif self.port.orientation == 'R90':
                orient = 'R0'
                disp_correction_x = width / 2
                disp_correction_y = -width / 2

            elif self.port.orientation == 'R180':
                orient = 'R90'
                disp_correction_x = width / 2
                disp_correction_y = width / 2
            elif self.port.orientation == 'R270':
                orient = 'R180'
                disp_correction_x = -width / 2
                disp_correction_y = width / 2

        elif direction.upper() == "L":
            if self.port.orientation == 'R0':
                orient = 'R90'
                disp_correction_x = width / 2
                disp_correction_y = -width / 2

            elif self.port.orientation == 'R90':
                orient = 'R180'
                disp_correction_x = -width / 2
                disp_correction_y = -width / 2

            elif self.port.orientation == 'R180':
                orient = 'R270'
                disp_correction_x = -width / 2
                disp_correction_y = width / 2

            elif self.port.orientation == 'R270':
                orient = 'R0'
                disp_correction_x = -width / 2
                disp_correction_y = -width / 2

        elif direction.upper() == "C":
            self.go_to_layer(layer=(length,
                                    'drawing'))  # this is a hacky way to do it, but implementing it otherwise would take complete refactor of the code
            return

        # Process the length
        points = [(0, 0), (length, 0)]
        wg_params = dict(width=width,
                         layer=self.layer,
                         points=points)
        temp = self.gen_cls.new_template(params=wg_params, temp_cls=WaveguideBase)

        port = PhotonicPort(
            name=self.port.name + ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10)),
            center=(self.port.center[0] - disp_correction_x, self.port.center[1] - disp_correction_y),
            orient=orient,
            width=self.port.width,
            layer=self.port_layer,
            resolution=self.gen_cls.grid.resolution
        )
        self.gen_cls.add_photonic_port(
            port=port
        )
        self.port = port

        index = len(self.inst)
        self.inst[index] = self.gen_cls.add_instance_port_to_port(inst_master=temp, instance_port_name='PORT_IN',
                                                                  self_port=self.port)
        self.port = self.inst[index]['PORT_OUT']

    def go_to_layer(self, layer, width=None):
        if width is None:
            width = self.port.width

        top_layer_ind = self.gen_cls.grid.tech_info.get_layer_id(layer[0])
        bottom_layer_ind = self.gen_cls.grid.tech_info.get_layer_id(self.layer[0])

        if bottom_layer_ind > top_layer_ind:
            params = dict(top_layer=self.layer,
                          bottom_layer=layer,
                          top_x_span=self.port.width,
                          top_y_span=self.port.width,
                          bottom_x_span=width,
                          bottom_y_span=width,
                          align='center_align')
        elif bottom_layer_ind < top_layer_ind:
            params = dict(top_layer=layer,
                          bottom_layer=self.layer,
                          top_x_span=width,
                          top_y_span=width,
                          bottom_x_span=self.port.width,
                          bottom_y_span=self.port.width,
                          align='center_align')
        else:
            return

        self.layer = layer

        via_stack_master = self.gen_cls.new_template(params=params, temp_cls=ViaStack)
        self.gen_cls.add_instance(master=via_stack_master, loc=self.port.center)

        port = PhotonicPort(
            name=self.port.name + ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10)),
            center=self.port.center,
            orient=self.port.orientation,
            width=self.port.width,
            layer=(layer[0], 'label'),
            resolution=self.gen_cls.grid.resolution)

        self.gen_cls.add_photonic_port(port=port)
        self.port = port

    def auto_route(self, final_cord, x_offset=0, y_offset=0, priority_x=True):
        # final_cord -  tuple/list with final coordinate where router needs to go
        # x_offset - offset in x direction with respect to final coordinate
        # y_offset - offset in y direction with respect to final coordinate
        # priority_x - Boolean flag which determines if auto-route first routes in x or y direction
        current_cord = self.port.center

        dx = final_cord[0] - current_cord[0] + x_offset
        dy = final_cord[1] - current_cord[1] + y_offset

        # dx += (-1) ** (dx < 0) * self.port.width
        # dy += (-1) ** (dy < 0) * self.port.width

        if priority_x:
            if dx > 1e-10:  # Go right
                # Check port orientation and based on it go right
                if self.port.orientation == 'R180':
                    self.route(length=abs(dx), direction="S")
                elif self.port.orientation == 'R90':
                    self.route(length=abs(dx), direction="L")
                elif self.port.orientation == 'R270':
                    self.route(length=abs(dx), direction="R")
                else:
                    raise ValueError("This configuration cannot be router properly at this moment")

            else:  # Go left
                # Check port orientation and based on it go right
                if self.port.orientation == 'R0':
                    self.route(length=abs(dx), direction="S")
                elif self.port.orientation == 'R90':
                    self.route(length=abs(dx), direction="R")
                elif self.port.orientation == 'R270':
                    self.route(length=abs(dx), direction="L")
                else:
                    raise ValueError("This configuration cannot be router properly at this moment")

            if dy > 1e-10:  # Go up
                # Check port orientation and based on it go right
                if self.port.orientation == 'R0':
                    self.route(length=abs(dy), direction="R")
                elif self.port.orientation == 'R270':
                    self.route(length=abs(dy), direction="S")
                elif self.port.orientation == 'R180':
                    self.route(length=abs(dy), direction="L")
                else:
                    raise ValueError("This configuration cannot be router properly at this moment")

            else:  # Go down
                # Check port orientation and based on it go right
                if self.port.orientation == 'R180':
                    self.route(length=abs(dy), direction="R")
                elif self.port.orientation == 'R0':
                    self.route(length=abs(dy), direction="L")
                elif self.port.orientation == 'R90':
                    self.route(length=abs(dy), direction="S")
                else:
                    raise ValueError("This configuration cannot be router properly at this moment")
        else:
            if dy > 1e-10:  # Go up
                # Check port orientation and based on it go right
                if self.port.orientation == 'R0':
                    self.route(length=abs(dy), direction="R")
                elif self.port.orientation == 'R270':
                    self.route(length=abs(dy), direction="S")
                elif self.port.orientation == 'R180':
                    self.route(length=abs(dy), direction="L")
                else:
                    raise ValueError("This configuration cannot be router properly at this moment")

            else:  # Go down
                # Check port orientation and based on it go right
                if self.port.orientation == 'R180':
                    self.route(length=abs(dy), direction="R")
                elif self.port.orientation == 'R0':
                    self.route(length=abs(dy), direction="L")
                elif self.port.orientation == 'R90':
                    self.route(length=abs(dy), direction="S")
                else:
                    raise ValueError("This configuration cannot be router properly at this moment")

            if dx > 1e-10:  # Go right
                # Check port orientation and based on it go right
                if self.port.orientation == 'R180':
                    self.route(length=abs(dx), direction="S")
                elif self.port.orientation == 'R90':
                    self.route(length=abs(dx), direction="L")
                elif self.port.orientation == 'R270':
                    self.route(length=abs(dx), direction="R")
                else:
                    raise ValueError("This configuration cannot be router properly at this moment")

            else:  # Go left
                # Check port orientation and based on it go right
                if self.port.orientation == 'R0':
                    self.route(length=abs(dx), direction="S")
                elif self.port.orientation == 'R90':
                    self.route(length=abs(dx), direction="R")
                elif self.port.orientation == 'R270':
                    self.route(length=abs(dx), direction="L")
                else:
                    raise ValueError("This configuration cannot be router properly at this moment")

    #
    # @staticmethod
    # def _listize(x):
    #     """
    #     if x is a scalar, converts it into a one-element list
    #     conventient for handling cases when input parameters can be a scalar or a list
    #     such as width parameter.
    #     """
    #     if isinstance(x, list):
    #         return x
    #     else:
    #         return [x]
