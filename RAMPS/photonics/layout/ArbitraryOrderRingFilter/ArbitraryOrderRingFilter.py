import BPG
import importlib
from Photonic_Core_Layout.AdiabaticPaths.AdiabaticPaths import AdiabaticPaths
from layout.BasicElements.SimpleRing.SimpleRing import SimpleRing


class ArbitraryOrderRingFilter(BPG.PhotonicTemplateBase):
    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)
        self.ring_params = params['ring_params']
        self.ring_module = importlib.import_module(params['ring_module'])
        self.ring_class = getattr(self.ring_module, params['ring_class'])
        self.wg_in_params = self.params['wg_in_params']
        self.wg_out_params = self.params['wg_out_params']
        self.side_coupler_params = self.params['side_coupler_params']

        try:
            self.hor_disp = params['hor_disp']
        except:
            self.hor_disp = 0.5
        self._accumulated_height = 0

        # templates
        self.wg_in_template = None
        self.wg_out_template = None
        self.ring_template = dict()

        # instances
        self.wg_in_inst = None
        self.wg_out_inst = None
        self.ring_inst = dict()

    @classmethod
    def get_params_info(cls):
        return dict(
            ring_params='Information about n rings: radius, distance between outer edges',
            ring_module='None',
            ring_class='None',
            wg_in_params='None',
            wg_out_params='None',
            hor_disp='Horizontal displacement of center of the ring with the respect to the start of the input wg',
            side_coupler_params = 'Parameters that are passed to SimpleRing in order to create circular side coupler'
        )

    @classmethod
    def get_default_param_values(cls):
        return dict(
            hor_disp=0.5,
            side_coupler_params = 2
        )

    def draw_layout(self) -> None:
        self.draw_in_wg()
        self.create_rings()
        self.place_rings()
        self.draw_out_wg()

    def draw_in_wg(self):
        if self.wg_in_params:
            offset_params = dict(layer=self.wg_in_params['layer'], port_layer=self.wg_in_params['port_layer'],
                                 x_start=0.0, y_start=0.0,
                                 angle_start=0.0, radius_threshold=1.5, curvature_rate_threshold=0.7, merge_arcs=False,
                                 show_plot=False, show_plot_labels=False)

            arc_params = [
                dict(arc_type="straight_wg", width=self.wg_in_params['width'], length=self.wg_in_params['length'])]
            offset_params['arc_params'] = arc_params

            self.wg_in_template = self.new_template(params=offset_params, temp_cls=AdiabaticPaths)
            self.wg_in_inst = self.add_instance(master=self.wg_in_template,
                                                loc=(0, 0),
                                                orient='R0',
                                                unit_mode=False)

            self.extract_photonic_ports(
                inst=self.wg_in_inst,
                port_names=['PORT_IN', 'PORT_OUT'],
                port_renaming={'PORT_IN': 'PORT_IN', 'PORT_OUT': 'PORT_THROUGH'},
                show=False)

            self._accumulated_height += self.wg_in_params['width'] / 2 + self.wg_in_params['gap']

    def create_rings(self) -> None:
        """
        Creates a PhotonicRound shape of specified outer radius and width, then places it at given gap value relative
        to the created waveguide
        """

        for i in range(len(self.ring_params['r_out'])):
            # Create a dict with properly parsed params
            ring = dict(layer = self.ring_params['layer'],
                        port_layer=self.ring_params['port_layer'],
                        r_out = self.ring_params['r_out'][i],
                        ring_width= self.ring_params['ring_width'][i],
                        gap = self.ring_params['gap'][i])


            ring_temp = self.new_template(params=ring, temp_cls=self.ring_class)
            if self.params['ring_class'] == 'RingSensableCLIPP':
                ring_height = 2 * ring['ring_params']['r_out']
            else:
                ring_height = ring_temp.bound_box.height
            ring_center = self._accumulated_height + ring_height / 2
            self._accumulated_height += ring_height + ring['gap']
            self.ring_template[ring_center] = ring_temp

    def place_rings(self):
        self.displacement = []
        place_half_rings = True
        rr = 8
        gap = 0.2
        left = False

        # ring_params = dict(layer=['si_full_free', 'drawing'],
        #                    port_layer=['si_full_free', 'port'],
        #                    r_out=8,
        #                    ring_width=0.6,
        #                    theta_in=-90,
        #                    theta_out=90)
        #
        # ring_temp = self.new_template(params=ring_params, temp_cls=SimpleRing)
        keys = [*self.ring_template.keys()]
        values = [*self.ring_template.values()]

        for i in range(len(self.ring_template)):
            key = keys[i]
            value = values[i]

            if self.params['ring_class'] == 'RingTunable':
                self.ring_inst[key] = self.add_instance(master=value,
                                                        loc=(self.wg_in_params['length'] * self.hor_disp, key),
                                                        orient='R90',
                                                        unit_mode=False)

            elif self.params['ring_class'] == 'RingSensableCLIPP':
                self.ring_inst[key] = self.add_instance(master=value,
                                                        loc=(self.wg_in_params['length'] * self.hor_disp, key),
                                                        orient='R0',
                                                        unit_mode=False)
                self.extract_photonic_ports(
                    inst=self.ring_inst[key],
                    port_names=['via_stack_left', 'via_stack_right'],
                    show=False)

            else:
                self.ring_inst[key] = self.add_instance(master=value,
                                                        loc=(self.wg_in_params['length'] * self.hor_disp, key),
                                                        orient='R0',
                                                        unit_mode=False)
                if 'side_coupler' in self.ring_params.keys() and self.ring_params['side_coupler']['place'][i]:
                    if self.ring_params['side_coupler']['left'][i]:
                        dd = -self.ring_params['side_coupler']['r_out'][i]-self.ring_params['side_coupler']['gap'][i]-self.ring_params['r_out'][i]
                    else:
                        dd = self.ring_params['side_coupler']['r_out'][i]+self.ring_params['side_coupler']['gap'][i]+self.ring_params['r_out'][i]

                    coupler_params = dict(r_out=self.ring_params['side_coupler']['r_out'][i],
                                          ring_width=self.ring_params['side_coupler']['ring_width'][i],
                                          theta_in=self.ring_params['side_coupler']['theta_in'][i],
                                          theta_out = self.ring_params['side_coupler']['theta_out'][i],
                                          gap=self.ring_params['side_coupler']['gap'][i])

                    coupler_temp = self.new_template(params=coupler_params , temp_cls=SimpleRing)
                    hr = self.add_instance(master=coupler_temp, loc=(self.wg_in_params['length'] * self.hor_disp+dd, key))
                    self.extract_photonic_ports(inst=hr,port_names=['PORT_IN', 'PORT_OUT'],
                                                port_renaming={'PORT_IN':"PORT_IN_{}".format(i),
                                                               'PORT_OUT':"PORT_OUT_{}".format(i)})


                # TODO: see if there can be a better definition of the port displacement

                # rout = self.ring_params[i]['r_out']
                # displacement = rout* 0.1125
                # self.displacement.append(displacement)
                # gap = 0.2
                # width = 0.6
                #
                # self.add_photonic_port(name='PORT_RING_LEFT_UP_{}'.format(i),
                #                        layer=self.wg_out_params['port_layer'],
                #                        center=(self.wg_in_params['length'] * self.hor_disp - rout-gap-width/2, key + displacement),
                #                        orient='R90', width=0.5)
                #
                # self.add_photonic_port(name='PORT_RING_RIGHT_UP_{}'.format(i),
                #                        layer=self.wg_out_params['port_layer'],
                #                        center=(self.wg_in_params['length'] * self.hor_disp + rout+gap+width/2, key + displacement),
                #                        orient='R90',
                #                        width=0.5)
                #
                # self.add_photonic_port(name='PORT_RING_LEFT_DOWN_{}'.format(i),
                #                        layer=self.wg_out_params['port_layer'],
                #                        center=(self.wg_in_params['length'] * self.hor_disp - rout-gap-width/2, key - displacement),
                #                        orient='R270',
                #                        width=0.5)
                #
                # self.add_photonic_port(name='PORT_RING_RIGHT_DOWN_{}'.format(i),
                #                        layer=self.wg_out_params['port_layer'],
                #                        center=(self.wg_in_params['length'] * self.hor_disp + rout+gap+width/2, key - displacement),
                #                        orient='R270',
                #                        width=0.5)


    def draw_out_wg(self):
        if self.wg_out_params:
            offset_params = dict(layer=self.wg_out_params['layer'], port_layer=self.wg_out_params['port_layer'],
                                 x_start=0.0, y_start=0.0,
                                 angle_start=0.0, radius_threshold=1.5, curvature_rate_threshold=0.7, merge_arcs=False,
                                 show_plot=False, show_plot_labels=False)

            arc_params = [
                dict(arc_type="straight_wg", width=self.wg_out_params['width'], length=self.wg_out_params['length'])]
            offset_params['arc_params'] = arc_params

            self.wg_out_template = self.new_template(params=offset_params, temp_cls=AdiabaticPaths)
            self.wg_out_inst = self.add_instance(master=self.wg_out_template,
                                                 loc=(0, self._accumulated_height + self.wg_out_params['width'] / 2),
                                                 orient='R0',
                                                 unit_mode=False)
            a = self._accumulated_height + self.wg_out_params['width'] / 2
            self.extract_photonic_ports(
                inst=self.wg_out_inst,
                port_names=['PORT_IN', 'PORT_OUT'],
                port_renaming={'PORT_IN': 'PORT_DROP', 'PORT_OUT': 'PORT_RED'},
                show=False)
