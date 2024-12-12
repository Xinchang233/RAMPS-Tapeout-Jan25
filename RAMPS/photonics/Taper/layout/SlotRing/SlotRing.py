import BPG
from layout.Round.Round import Round
from layout.AdiabaticRouter.AdiabaticRouter import AdiabaticRouter
from layout.Couplers.StraightBusCoupler import StraightBusCoupler


class SlotRing(BPG.PhotonicTemplateBase):
    """ A ring with a slot in the middle.
    Ports:
        PORT_IN
        PORT_THROUGH
    """
    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)
        
        self.ring_params = self.params['ring_params']
        self.coupler_in_through_params = self.params['coupler_in_through_params']

    @classmethod
    def get_default_param_values(cls):
        return dict(
            coupler_in_through_params=None  # None or dict with params to be passed to StraightBusCoupler class
        )

    @classmethod
    def get_params_info(cls):  # Returns definition of the parameters.
        return dict(
            # Standard parameters
            ring_params='All parameters needed to specify the ring',
            coupler_in_through_params='Optional in-through bus coupler parameters'
        )
    
    def draw_layout(self):
        self.draw_slot_ring()

        if self.coupler_in_through_params is not None:
            self.draw_in_through_coupler()
            
    def draw_slot_ring(self):
        """ Draw the outer ring """
        outer_ring_params = dict(layer=self.ring_params['layer'], r_out=self.ring_params['outer_rout'],
                                 ring_width=self.ring_params['outer_ring_width'], resolution=0.001)

        outer_ring_temp = self.new_template(params=outer_ring_params, temp_cls=Round)
        self.add_instance(master=outer_ring_temp, loc=(0, 0), orient="R0", unit_mode=False, )

        """ Draw the inner ring """
        rout = self.ring_params['outer_rout'] - self.ring_params['outer_ring_width'] - self.ring_params['gap']
        inner_ring_params = dict(layer=self.ring_params['layer'], r_out=rout,
                                 ring_width=self.ring_params['inner_ring_width'], resolution=0.001)

        inner_ring_temp = self.new_template(params=inner_ring_params, temp_cls=Round)
        self.add_instance(master=inner_ring_temp, loc=(0, 0), orient="R0", unit_mode=False, )


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
            coupler_params = dict(layer=self.ring_params['layer'], width=self.coupler_in_through_params['width'],
                                  length=self.coupler_in_through_params['length'])

            coupler_master = self.new_template(params=coupler_params, temp_cls=StraightBusCoupler)
            self.coupler_inst_in = self.add_instance(master=coupler_master,
                                                     loc=(0,
                                                          -self.ring_params['rout'] - self.coupler_in_through_params[
                                                              'gap'] - self.coupler_in_through_params['width'] / 2))

            self.extract_photonic_ports(
                inst=self.coupler_inst_in,
                port_names=['PORT_IN', 'PORT_OUT'],
                port_renaming={'PORT_IN': 'PORT_IN', 'PORT_OUT': 'PORT_THROUGH'},
                show=False)

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
        Wg.add_wrapped_ring_coupler(rmin_in=self.coupler_in_through_params['rmin'], alpha_zero_in=np.pi / 5,
                                    r_coupling=r_coupling, angle_coupling=np.pi / 3, w_coupling=width)
        coupler_height = Wg.inst[1].bound_box.height
        coupler_length = Wg.inst[1].bound_box.width

        Wg.add_straight_wg(length=length / 2)

        translation_vector = [length / 2 + coupler_length / 2, -r_coupling + coupler_height - width]
        self.move_object(Wg, translation_vector)

        self.add_photonic_port(name='PORT_IN',
                               center=(-translation_vector[0], translation_vector[1]),
                               orient='R0', width=width, layer=('RX', 'port'))

        self.add_photonic_port(name='PORT_THROUGH',
                               center=(translation_vector[0], Wg.port.center[1] + translation_vector[1]),
                               orient='R180', width=width, layer=('RX', 'port'))


    @staticmethod
    def move_object(object, direction):
        for i in range(len(object.inst)):
            object.inst[i]._origin.center = object.inst[i].location + direction
