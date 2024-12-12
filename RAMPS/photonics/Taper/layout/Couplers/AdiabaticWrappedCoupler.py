import BPG
import numpy as np
import random, string
from ..AdiabaticRouter.AdiabaticRouter import AdiabaticRouter


class AdiabaticWrappedCoupler(BPG.PhotonicTemplateBase):
    """
    """

    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)

        self.layer = self.params['layer']
        self.width = self.params['width']
        self.length = self.params['length']
        self.r_coupling = self.params['r_coupling']
        self.rmin_in = self.params['rmin_in']
        self.alpha_zero_in = self.params['alpha_zero_in']
        self.angle_coupling = self.params['angle_coupling']

    @classmethod
    def get_default_param_values(cls):
        return dict(
            rmin_in=5,
            alpha_zero_in=np.pi / 5,
            angle_coupling=np.pi / 3
        )

    @classmethod
    def get_params_info(cls):  # Returns definition of the parameters.
        return dict(
            layer='Layer where coupler is drawn',
            width='Width of the coupler - could be a single value or a list with 3 values',
            length='Total length of the straight waveguide added to the wrapped coupler. length/2 is added to each side',
            r_coupling='Circular radius at the coupling point',
            rmin_in='Min radius of curvature of the input/output adiabatic bend',
            alpha_zero_in='Starting angle from which the coupler is drawn. Must be >= 2xangle_coupling',
            angle_coupling='Angle over which the bus and the ring form coupling region',

        )

    def draw_layout(self):

        if isinstance(self.width, list):
            input_port_width = self.width[0]
            coupling_port_width = self.width[1]
        else:
            input_port_width = self.width
            coupling_port_width = self.width

        init_port = self.add_photonic_port(
            name='PORT_IN',
            center=(0, 0),
            orient='R0', width=input_port_width, layer=(self.layer[0], 'port'))

        Wg = AdiabaticRouter(gen_cls=self, init_port=init_port, layer=self.layer, name='init_port')
        Wg.add_straight_wg(length=self.length / 2)
        Wg.add_wrapped_ring_coupler(rmin_in=self.rmin_in, alpha_zero_in=self.alpha_zero_in,
                                    r_coupling=self.r_coupling, angle_coupling=self.angle_coupling,
                                    w_coupling=self.width)


        if self.alpha_zero_in > 0:
            coupler_port_loc_y = Wg.inst[1].bound_box.bottom + coupling_port_width
        else:
            coupler_port_loc_y = Wg.inst[1].bound_box.top - coupling_port_width

        coupler_length = Wg.inst[1].bound_box.width
        Wg.add_straight_wg(length=self.length / 2)
        coupler_port_loc_x = -self.length / 2 - coupler_length / 2

        coupling_port_loc = [coupler_port_loc_x, coupler_port_loc_y]

        # add port at the coupling point
        self.add_photonic_port(
            name='PORT_COUPLE',
            orient='R0',
            center=coupling_port_loc,
            width=coupling_port_width,
            layer=(self.layer[0], 'port'),
            resolution=self.grid.resolution,
            unit_mode=False,
            show=True)

        # add output port
        self.add_photonic_port(
            name='PORT_OUT',
            orient='R180',
            center=tuple(Wg.port.center),
            width=input_port_width,
            layer=(self.layer[0], 'port'),
            resolution=self.grid.resolution,
            unit_mode=False,
            show=True)

