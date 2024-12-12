import numpy as np
import importlib
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


class FullRibRing(BPG.PhotonicTemplateBase):
    """
    Rib ring class with interdigitated PIN junction, integrated heater (with optional undercut) and input coupler

    """

    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)

        self.ring_params = self.params['ring_params']

        self.coupler_in_through_params = self.params['coupler_in_through_params']

    @classmethod
    def get_default_param_values(cls):
        return dict(
            coupler_in_through_params=None
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
        if self.coupler_in_through_params is not None:
            self.draw_in_through_coupler()

    def draw_si_ring(self):
        """ parse parameters from ring_params dictionary """
        # si ring params
        layer = self.ring_params['layer']
        ring_width = self.ring_params['ring_width']
        ring_rout = self.ring_params['rout']

        """ Draw the silicon ring """
        ring_params = dict(layer=layer, r_out=ring_rout, ring_width=ring_width, resolution=0.02)
        si_ring_temp = self.new_template(params=ring_params, temp_cls=Round)
        self.add_instance(master=si_ring_temp, loc=(0, 0), orient="R0", unit_mode=False)

        rout_partial = self.ring_params['rout_partial']
        rwidth_partial = self.ring_params['rwidth_partial']

        partial_etch_ring_params = dict(
            layer=self.ring_params['partial_ring_layer'],
            r_out=rout_partial,
            ring_width=rwidth_partial,
            resolution=0.02
        )

        partial_ring_temp = self.new_template(params=partial_etch_ring_params, temp_cls=Round)
        self.add_instance(
            master=partial_ring_temp,
            loc=(0, 0),
            orient="R0",
            unit_mode=False
        )

    def draw_in_through_coupler(self):
        # Import mode converter
        mode_converter_module = importlib.import_module(self.params['coupler_in_through_params']['module'])
        mode_converter_module_class = getattr(mode_converter_module, self.params['coupler_in_through_params']['class'])
        mode_converter_master = self.new_template(params=None, temp_cls=mode_converter_module_class)

        coupler_x_start = -self.coupler_in_through_params['length'] / 2 - mode_converter_master.bound_box.width
        coupler_y_start = -self.ring_params['rout'] - self.coupler_in_through_params['gap'] - self.coupler_in_through_params[
            'width'] / 2

        mode_converter_inst1 = self.add_instance(
            master=mode_converter_master,
            loc=(coupler_x_start, coupler_y_start)
        )

        self.extract_photonic_ports(inst=mode_converter_inst1, port_names=['PORT_IN'])

        coupler_inst_full_etch = AdiabaticRouter(
            gen_cls=self,
            init_port=mode_converter_inst1['PORT_OUT'],
            layer=self.ring_params['layer'],
            name='init_port'
        )
        coupler_inst_full_etch.add_straight_wg(length=self.coupler_in_through_params['length'])

        coupler_inst_part_etch = AdiabaticRouter(
            gen_cls=self,
            init_port=mode_converter_inst1['PORT_OUT'],
            layer=self.ring_params['partial_ring_layer'],
            name='init_port'
        )
        coupler_inst_part_etch.add_straight_wg(
            length=self.coupler_in_through_params['length'],
            width=self.coupler_in_through_params['partial_wg_width'], override_width=True
        )

        mode_converter_inst12 = self.add_instance_port_to_port(
            inst_master=mode_converter_master,
            instance_port_name='PORT_OUT',
            self_port=coupler_inst_full_etch.port
        )

        self.extract_photonic_ports(
            inst=mode_converter_inst12,
            port_names=['PORT_IN'],
            port_renaming={'PORT_IN': 'PORT_THROUGH'}
        )
