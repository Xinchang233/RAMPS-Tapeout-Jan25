import BPG
from bag.layout.util import BBox
from BPG.objects import PhotonicRound
from copy import deepcopy
import random
from layout.SimpleRound.SimpleRound import SimpleRound
from Photonic_Core_Layout.WaveguideBase.CosineWaveguide import CosineWaveguide
from numpy import pi
from math import sqrt


class FilterRingBase(BPG.PhotonicTemplateBase):
    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)
        self.params = deepcopy(params)
        self.radius = self.params['radius']
        self.layer = self.params['layer']
        self.ring_width = self.params['ring_width']
        self.input_wg = self.params['input_wg']
        self.place_output_wg = self.params['place_output_wg']
        if self.place_output_wg:
            self.output_wg = self.params['output_wg']
        self.center = (0, 0)
        self.height = 0
        self.output_wg_port_center = None

        self.port_layer = self.params['port_layer']
        try:
            self.additional_layers = self.params['additional_layers']
            a = self.params['additional_layers']
            self.add_layers_present = True

        except:
            self.additional_layers = random.randint(1,1023)
            self.add_layers_present = False

    @classmethod
    def get_default_param_values(cls) -> dict:
        return dict(
            layer=None,
            port_layer=None,
            radius=None,
            ring_width=None,
            input_wg=None,
            output_wg=None,
            place_output_wg=None,
            additional_layers=None,
        )

    @classmethod
    def get_params_info(cls) -> dict:
        return dict(
            layer='Layer',
            port_layer="None",
            radius="Outer radius of the ring",
            ring_width="Width of the ring. Inner radius = Outer_radius - width",
            input_wg="Parameter dict for input waveguide. Dict contains length, width and gap to the ring",
            output_wg="Parameter dict for output waveguide. Dict contains length, width and gap to the ring",
            place_output_wg="Boolian value which specifies if output waveguide is created",
            additional_layers='Layer - width pair that will be placed over the ring'
        )

    def draw_layout(self) -> None:
        self.draw_input_wg()
        self.draw_ring()
        if self.place_output_wg:
            self.draw_output_wg()
        self.draw_ports()

    def draw_input_wg(self) -> None:
        layer = self.params['layer']
        self.add_rect(layer=layer,
                      bbox=BBox(left=0,
                                bottom=0,
                                right=self.input_wg['length'],
                                top=self.input_wg['width'],
                                resolution=self.grid.resolution,
                                unit_mode=False))
        x_cor = self.input_wg['length'] / 2
        y_cor = self.input_wg['width'] + self.input_wg['gap'] + self.radius
        self.center = (x_cor, y_cor)

    def draw_ring(self) -> None:
        r_out = self.radius
        distance = self.input_wg['gap']
        width = self.ring_width
        layer = self.layer
        self.height = distance + r_out + self.input_wg['width']
        params = dict(layer=layer,
                      r_out=r_out,
                      r_width=width,
                      r_step= 0.02)
        ring_temp = self.new_template(params=params, temp_cls=SimpleRound)
        ring_inst = self.add_instance(master=ring_temp, loc=self.center)
        # P = PhotonicRound(layer=layer,
        #                   resolution=self.grid.resolution,
        #                   center=self.center,
        #                   rout=r_out,
        #                   rin=r_out - width)
        # self.add_obj(P)

        center_of_circle = r_out - width / 2
        if self.add_layers_present:

            for i in range(len(self.additional_layers)):
                try:
                    rout = self.additional_layers[i]['r_out']
                except:
                    rout = center_of_circle + self.additional_layers[i]['width'] / 2

                params = dict(layer=self.additional_layers[i]['layer'],
                              r_out=rout,
                              r_width=self.additional_layers[i]['width'],
                              r_step=0.02)
                ring_temp = self.new_template(params=params, temp_cls=SimpleRound)
                ring_inst = self.add_instance(master=ring_temp, loc=self.center)

                # B = PhotonicRound(layer=self.additional_layers[i]['layer'],
                #                   resolution=self.grid.resolution,
                #                   center=self.center,
                #                   rout=center_of_circle + self.additional_layers[i]['width'] / 2,
                #                   rin=center_of_circle - self.additional_layers[i]['width'] / 2)
                # self.add_obj(B)

    def draw_output_wg(self) -> None:
        length = self.output_wg['length']
        width = self.output_wg['width']
        layer = self.layer
        x_start = (self.input_wg['length'] - length) / 2
        x_end = x_start + length

        y_start = self.height + self.radius + self.output_wg['gap']
        y_end = y_start + width
        self.add_rect(layer=layer,
                      bbox=BBox(left=x_start,
                                bottom=y_start,
                                right=x_end,
                                top=y_end,
                                resolution=self.grid.resolution,
                                unit_mode=False))
        self.output_wg_port_center = (x_start, (y_end + y_start) / 2)

    def draw_ports(self):
        self.add_photonic_port(
            name='left_down',
            orient='R0',
            center=(0, self.input_wg['width'] / 2),
            width=self.input_wg['width'],
            layer=self.port_layer,
            resolution=self.grid.resolution,
            unit_mode=False,
            show=False)

        self.add_photonic_port(
            name='right_down',
            orient='R180',
            center=(self.input_wg['length'], self.input_wg['width'] / 2),
            width=self.input_wg['width'],
            layer=self.port_layer,
            resolution=self.grid.resolution,
            unit_mode=False,
            show=False)

        if self.place_output_wg:
            self.add_photonic_port(
                name='left_up',
                orient='R0',
                center=self.output_wg_port_center,
                width=self.input_wg['width'],
                layer=self.port_layer,
                resolution=self.grid.resolution,
                unit_mode=False,
                show=False)

            self.add_photonic_port(
                name='right_up',
                orient='R180',
                center=(self.output_wg_port_center[0] + self.output_wg['length'], self.output_wg_port_center[1]),
                width=self.input_wg['width'],
                layer=self.port_layer,
                resolution=self.grid.resolution,
                unit_mode=False,
                show=False)

class FilterRingBaseCosine(BPG.PhotonicTemplateBase):
    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)
        self.params = deepcopy(params)
        self.radius = self.params['radius']
        self.layer = self.params['layer']
        self.ring_width = self.params['ring_width']
        self.input_wg = self.params['input_wg']
        self.place_output_wg = self.params['place_output_wg']
        if self.place_output_wg:
            self.output_wg = self.params['output_wg']
        self.center = (0, 0)
        self.height = 0
        self.output_wg_port_center = None

        self.port_layer = self.params['port_layer']
        try:
            self.additional_layers = self.params['additional_layers']
            a = self.params['additional_layers']
            self.add_layers_present = True

        except:
            self.additional_layers = random.randint(1,1023)
            self.add_layers_present = False

    @classmethod
    def get_default_param_values(cls) -> dict:
        return dict(
            layer=None,
            port_layer=None,
            radius=None,
            ring_width=None,
            input_wg=None,
            output_wg=None,
            place_output_wg=None,
            additional_layers=None,
        )

    @classmethod
    def get_params_info(cls) -> dict:
        return dict(
            layer='Layer',
            port_layer="None",
            radius="Outer radius of the ring",
            ring_width="Width of the ring. Inner radius = Outer_radius - width",
            input_wg="Parameter dict for input waveguide. Dict contains length, width and gap to the ring",
            output_wg="Parameter dict for output waveguide. Dict contains length, width and gap to the ring",
            place_output_wg="Boolian value which specifies if output waveguide is created",
            additional_layers='Layer - width pair that will be placed over the ring'
        )

    def draw_layout(self) -> None:
        self.draw_input_wg()
        self.draw_ring()
        if self.place_output_wg:
            self.draw_output_wg()
        self.draw_ports()

    def draw_input_wg(self) -> None:
        layer = self.params['layer']
        # self.add_rect(layer=layer,
        #               bbox=BBox(left=0,
        #                         bottom=0,
        #                         right=self.input_wg['length'],
        #                         top=self.input_wg['width'],
        #                         resolution=self.grid.resolution,
        #                         unit_mode=False))
        r_out = self.radius
        amplitude = 0.25*r_out
        self.access_length = 2 * pi * sqrt(r_out * amplitude)
        self.draw_access_waveguide(
            cosine_amplitude=amplitude,
            cosine_length=self.access_length,
            wg_width=self.input_wg['width'],
            layer=layer,
            loc=(0,-amplitude+0.5*self.input_wg['width']),
            orient='R0',
        )
        x_cor = self.access_length / 2
        y_cor = 0.5*self.input_wg['width'] + self.input_wg['gap'] + self.radius-2*amplitude+0.5*self.input_wg['width']
        self.center = (x_cor, y_cor)

    def draw_ring(self) -> None:
        r_out = self.radius
        distance = self.input_wg['gap']
        width = self.ring_width
        layer = self.layer
        self.height = distance + r_out + self.input_wg['width']
        params = dict(layer=layer,
                      r_out=r_out,
                      r_width=width,
                      r_step= 0.02)
        ring_temp = self.new_template(params=params, temp_cls=SimpleRound)
        ring_inst = self.add_instance(master=ring_temp, loc=self.center)
        # P = PhotonicRound(layer=layer,
        #                   resolution=self.grid.resolution,
        #                   center=self.center,
        #                   rout=r_out,
        #                   rin=r_out - width)
        # self.add_obj(P)

        center_of_circle = r_out - width / 2
        if self.add_layers_present:

            for i in range(len(self.additional_layers)):
                try:
                    rout = self.additional_layers[i]['r_out']
                except:
                    rout = center_of_circle + self.additional_layers[i]['width'] / 2

                params = dict(layer=self.additional_layers[i]['layer'],
                              r_out=rout,
                              r_width=self.additional_layers[i]['width'],
                              r_step=0.02)
                ring_temp = self.new_template(params=params, temp_cls=SimpleRound)
                ring_inst = self.add_instance(master=ring_temp, loc=self.center)

                # B = PhotonicRound(layer=self.additional_layers[i]['layer'],
                #                   resolution=self.grid.resolution,
                #                   center=self.center,
                #                   rout=center_of_circle + self.additional_layers[i]['width'] / 2,
                #                   rin=center_of_circle - self.additional_layers[i]['width'] / 2)
                # self.add_obj(B)

    def draw_output_wg(self) -> None:
        # length = self.output_wg['length']
        # width = self.output_wg['width']
        # layer = self.layer
        # x_start = (self.input_wg['length'] - length) / 2
        # x_end = x_start + length
        #
        # y_start = self.height + self.radius + self.output_wg['gap']
        # y_end = y_start + width
        # self.add_rect(layer=layer,
        #               bbox=BBox(left=x_start,
        #                         bottom=y_start,
        #                         right=x_end,
        #                         top=y_end,
        #                         resolution=self.grid.resolution,
        #                         unit_mode=False))
        layer = self.params['layer']
        r_out = self.radius
        self.amplitude = 0.25*r_out
        self.access_length = 2 * pi * sqrt(r_out * self.amplitude)
        self.draw_access_waveguide(
            cosine_amplitude=self.amplitude,
            cosine_length=self.access_length,
            wg_width=self.output_wg['width'],
            layer=layer,
            loc=(self.access_length,self.center[1]+self.radius+self.output_wg['gap']-self.amplitude+self.output_wg['width']/2),
            orient='R180',
        )
        #self.output_wg_port_center = (x_start, (y_end + y_start) / 2)

    def draw_ports(self):
        self.add_photonic_port(
            name='left_down',
            orient='R0',
            center=(0, self.input_wg['width'] / 2),
            width=self.input_wg['width'],
            layer=self.port_layer,
            resolution=self.grid.resolution,
            unit_mode=False,
            show=False)

        self.add_photonic_port(
            name='right_down',
            orient='R180',
            center=(self.access_length, self.input_wg['width'] / 2),
            width=self.input_wg['width'],
            layer=self.port_layer,
            resolution=self.grid.resolution,
            unit_mode=False,
            show=False)

        if self.place_output_wg:
            self.add_photonic_port(
                name='left_up',
                orient='R0',
                center=(0,self.center[1]+self.radius+self.output_wg['gap']-2*self.amplitude+self.output_wg['width']/2),
                width=self.output_wg['width'],
                layer=self.port_layer,
                resolution=self.grid.resolution,
                unit_mode=False,
                show=False)

            self.add_photonic_port(
                name='right_up',
                orient='R180',
                center=(self.access_length,self.center[1]+self.radius+self.output_wg['gap']-2*self.amplitude+self.output_wg['width']/2),
                width=self.output_wg['width'],
                layer=self.port_layer,
                resolution=self.grid.resolution,
                unit_mode=False,
                show=False)

    def draw_access_waveguide(self,
                              cosine_amplitude: float,
                              cosine_length: float,
                              wg_width: float,
                              layer: "layer_or_lpp_type",
                              loc: tuple,
                              orient: str,
                              ) -> None:
        """
        Draws the acccess waveguide. Assumed Cosine waveguide shape. Extracts the ports to this hierarchy.

        """
        params = dict(
            width=wg_width,
            amplitude=cosine_amplitude,
            wavelength=cosine_length,
            layer=layer,
            start_quarter_angle=0,
            end_quarter_angle=4
        )

        wg_master = self.new_template(params=params, temp_cls=CosineWaveguide)
        access_wg = self.add_instance(
            master=wg_master,
            inst_name='access_waveguide',
            loc=loc,
            orient=orient,
        )