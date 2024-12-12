import numpy as np
from copy import deepcopy
import BPG
from bag.layout.util import BBox
from ..Spoke.SpokeBase import SpokeBase
from ..Round.Round import Round
from ..RingHeater.RingHeater import RingHeater
from ..AdiabaticRouter.AdiabaticRouter import AdiabaticRouter
from Photonic_Core_Layout.ViaStack.ViaStack import ViaStack

from typing import TYPE_CHECKING, List, Union, Optional

if TYPE_CHECKING:
    from BPG.bpg_custom_types import layer_or_lpp_type


class FullEtchRing(BPG.PhotonicTemplateBase):
    """
    Ring class with interdigitated PIN junction, integrated heater (with optional undercut) and input coupler

    Ring is described by ring_params:
        layer - silicon layer
        ring_width - ring width
        rout - outer radius

    Coupler params determine the coupler type and shape

    """

    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)

        self.ring_params = self.params['ring_params']
        self.coupler_in_through_params = self.params['coupler_in_through_params']

    @classmethod
    def get_default_param_values(cls):
        return dict(
        )

    @classmethod
    def get_params_info(cls):  # Returns definition of the parameters.
        return dict(
            # Standard parameters
            ring_params='All parameters needed to specify the ring',
            coupler_in_through_params='Optional in-through bus coupler parameters'
        )

    def draw_layout(self):
        self.draw_si_ring()
        self.draw_in_through_coupler()

    def draw_si_ring(self):
        """ parse parameters from ring_params dictionary """
        # si ring params
        layer = self.ring_params['layer']
        ring_width = self.ring_params['ring_width']
        ring_rout = self.ring_params['rout']

        """ Draw the silicon ring """
        ring_params = dict(layer=layer, r_out=ring_rout, ring_width=ring_width, resolution=0.005)
        si_ring_temp = self.new_template(params=ring_params, temp_cls=Round)
        self.add_instance(master=si_ring_temp, loc=(0, 0), orient="R0", unit_mode=False)

    def draw_in_through_coupler(self):
        # draw adiabatic coupler
        if self.coupler_in_through_params['coupler_type'] == 'adiabatic':
            self.draw_adiabatic_access_waveguide(width=self.coupler_in_through_params['width'],
                                                 layer=self.ring_params['layer'],
                                                 length=self.coupler_in_through_params['length'])

        # draw MZI coupler
        elif self.coupler_in_through_params['coupler_type'] == 'MZI':
            self.draw_MZI_access_waveguide(width=self.coupler_in_through_params['width'],
                                           layer=self.ring_params['layer'],
                                           rout=self.coupler_in_through_params['rout'],
                                           gap=self.coupler_in_through_params['gap'])

        elif self.coupler_in_through_params['coupler_type'] == 'straight':
            init_port = self.add_photonic_port(name='PORT_IN',
                                               center=(self.coupler_in_through_params['length'] / 2,
                                                       -self.ring_params['rout'] - self.coupler_in_through_params[
                                                           'gap'] -
                                                       self.coupler_in_through_params['width'] / 2),
                                               orient='R0', width=self.coupler_in_through_params['width'],
                                               layer=('RX', 'port'))

            Wg = AdiabaticRouter(gen_cls=self, init_port=init_port, layer=self.ring_params['layer'], name='init_port')

            Wg.add_straight_wg(length=self.coupler_in_through_params['length'])

            self.add_photonic_port(name='PORT_THROUGH',
                                   center=(self.coupler_in_through_params['length'] / 2,
                                           -self.ring_params['rout'] - self.coupler_in_through_params['gap'] -
                                           self.coupler_in_through_params['width'] / 2),
                                   orient='R180', width=self.coupler_in_through_params['width'], layer=('RX', 'port'))

        else:
            raise ValueError("Coupler type {} is not supported".format(self.coupler_in_through_params['coupler_type']))

    def draw_MZI_access_waveguide(self, width, layer, rout, gap):
        straight_length = 1

        R = rout + gap + self.ring_params['rout']
        X = 2 * (rout - width / 2)
        Y = np.sqrt(R ** 2 - X ** 2)

        input_port_x = X + straight_length
        input_port_y = -Y + rout - width / 2

        init_port = self.add_photonic_port(name='ppt',
                                           center=(-input_port_x, input_port_y),
                                           orient='R180', width=width, layer=('RX', 'port'))

        Wg = AdiabaticRouter(gen_cls=self, init_port=init_port, layer=layer, name='init_port')

        Wg.add_straight_wg(length=straight_length)
        Wg.port.orientation = 'R0'
        Wg.add_circular_bend(rout=rout, width=width, theta_in=0, theta_out=-90)
        Wg.port.orientation = 'R90'
        Wg.add_circular_bend(rout=rout, width=width, theta_in=0, theta_out=180)
        Wg.port.orientation = 'R90'
        Wg.add_circular_bend(rout=rout, width=width, theta_in=180, theta_out=90)
        Wg.port.orientation = 'R180'
        Wg.add_straight_wg(length=straight_length)
        #
        self.add_photonic_port(name='PORT_THROUGH',
                               center=(input_port_x, input_port_y),
                               orient='R180', width=width, layer=('RX', 'port'))

        self.add_photonic_port(name='PORT_IN',
                               center=(-input_port_x, input_port_y),
                               orient='R0', width=width, layer=('RX', 'port'))

    def draw_adiabatic_access_waveguide(self, width, layer, length):

        r_coupling = self.ring_params['rout'] + self.coupler_in_through_params['gap'] + width / 2

        init_port = self.add_photonic_port(name='ppt',
                                           center=(0, 0),
                                           orient='R0', width=width, layer=('RX', 'port'))

        Wg = AdiabaticRouter(gen_cls=self, init_port=init_port, layer=layer, name='init_port')
        Wg.add_straight_wg(length=length / 2)
        Wg.add_wrapped_ring_coupler(rmin_in=5, alpha_zero_in=np.pi / 6,
                                    r_coupling=r_coupling, angle_coupling=np.pi / 5, w_coupling=width)
        coupler_height = Wg.inst[1].bound_box.height
        coupler_length = Wg.inst[1].bound_box.width

        Wg.add_straight_wg(length=length / 2)

        translation_vector = [length/2+coupler_length/2, -r_coupling+coupler_height-width]
        self.move_object(Wg, translation_vector)

    @staticmethod
    def move_object(object, direction):
        for i in range(len(object.inst)):
            object.inst[i]._origin.center = object.inst[i].location + direction