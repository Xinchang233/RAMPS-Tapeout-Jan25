from BPG import PhotonicTemplateBase
from Photonic_Core_Layout.WaveguideBase.WgRouter import WgRouter
import importlib
import yaml


class TestSiteArray(PhotonicTemplateBase):
    """
    Photonic Ports:
    IN = left side
    OUT = right side
    """

    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)

        self.port_width = 0.35
        self.wg_port_layer = ('si_full_free', 'port')
        self.wg_routing_layer = ('si_full_free', 'drawing')

        self.package_class_param_list = self.params['package_class_param_list']
        self.yaml_list = self.params['yaml_list']

        self.master_list = []
        self.inst_list = []
        self.site_pitch = self.params['site_pitch']
        self.track_pitch = self.params['track_pitch']

        self.bend_radius = self.photonic_tech_info.get_default_wg_params(self.wg_routing_layer)['radius']
        self.routing_width = self.photonic_tech_info.get_default_wg_params(self.wg_routing_layer)['width']

    @classmethod
    def get_params_info(cls):
        return dict(
            package_class_param_list='',
            yaml_list='',
            site_pitch='',
            track_pitch='',


        )

    @classmethod
    def get_default_param_values(cls):
        return dict(
        )

    def draw_layout(self):

        # # Unpack the package list
        # for packclassparam in self.package_class_param_list:
        #     lay_module = importlib.import_module(packclassparam['package'])
        #     temp_cls = getattr(lay_module, packclassparam['class'])
        #
        #     master = self.new_template(params=packclassparam['params'],
        #                                temp_cls=temp_cls)
        #
        #     self.master_list.append(master)

        # # Unpack the package list
        # for packclassparam in self.package_class_param_list:
        #     lay_module = importlib.import_module(packclassparam['package'])
        #     temp_cls = getattr(lay_module, packclassparam['class'])
        #
        #     master = self.new_template(params=packclassparam['params'],
        #                                temp_cls=temp_cls)
        #
        #     self.master_list.append(master)

        # Instantiate the sites
        for ind, yaml_file in enumerate(self.yaml_list):
            with open(yaml_file, 'r') as f:
                yaml_content = yaml.load(f)

            lay_module = importlib.import_module(yaml_content['layout_package'])
            # lay_module = importlib.import_module(yaml_content['layout_package'])
            temp_cls = getattr(lay_module, yaml_content['layout_class'])

            master = self.new_template(params=yaml_content['layout_params'],
                                       temp_cls=temp_cls)

            self.master_list.append(master)
        # Instantiate the sites

        in_port_name = 'PORT0'
        out_port_name = 'PORT1'

        for ind, master in enumerate(self.master_list):
            master_in_port_loc = master.get_photonic_port(in_port_name).center
            self.inst_list.append(
                self.add_instance(
                    master=master,
                    loc=((ind * self.site_pitch - master_in_port_loc[0]),
                         (0 - master_in_port_loc[1])),
                    # Offset site by location of input port, to put input port at desired location
                    orient='R0',
                )
            )




        num_sites = len(self.master_list)

        y0_top = max([inst.bound_box.top for inst in self.inst_list]) + 2 * self.track_pitch
		
		# inst.bound_box.bot doesn't exist?
		# WgRouter routability determines "6"
        y0_bot = min([inst.bound_box.top - inst.bound_box.height for inst in self.inst_list]) - 6 * self.track_pitch

        x_starts = self.inst_list[0][in_port_name].x - 2 * self.bend_radius
        x_ends = self.inst_list[-1][out_port_name].x + 2 * self.bend_radius + self.site_pitch/2

        for ind in range(len(self.inst_list)):

		    # Ports define "routing tracks"
            start_port = self.add_photonic_port(
                name=f'IN{ind}',
                center=(x_starts, y0_top + ind * self.track_pitch),
                orient='R0',
                layer=self.wg_port_layer,
                width=self.routing_width
            )
            end_port = self.add_photonic_port(
                name=f'OUT{ind}',
                center=(x_ends, y0_bot + ind * self.track_pitch),
                orient='R0',
                layer=self.wg_port_layer,
                width=self.routing_width
           )

            inst = self.inst_list[ind]

            # Route from the start to the site
            router = WgRouter(self,
                              start_port,
                              self.wg_routing_layer,
                              route_in_port_dir=True
                              )

            router.cardinal_router(
                [(inst[in_port_name].x - self.bend_radius,
                  inst[in_port_name].y + self.bend_radius),
                 (inst[in_port_name].x,
                  inst[in_port_name].y),
                ])

            # Route from the output of the site to the end
            router_end = WgRouter(self,
                                inst[out_port_name],
                                self.wg_routing_layer,
                                # What is this?
                                route_in_port_dir=False
                                )

            # Better solution?
            router_end.cardinal_router(
                [(inst[out_port_name].x + self.site_pitch/2.0 - 2*self.bend_radius, 
                inst[out_port_name].y),
                (inst[out_port_name].x + self.site_pitch/2.0 - self.bend_radius,
                inst[out_port_name].y - self.bend_radius),
                (inst[out_port_name].x + self.site_pitch/2.0 - self.bend_radius,
                end_port.y + self.bend_radius),
                (inst[out_port_name].x + self.site_pitch/2.0,
                end_port.y),
                (end_port.x, end_port.y)
                ]
            )



class DummySite(PhotonicTemplateBase):
    """
    Photonic Ports:
    IN = left side
    OUT = right side
    """

    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)

        self.port_width = 0.35
        self.wg_port_layer = ('si_full_free', 'port')
        self.wg_routing_layer = ('si_full_free', 'drawing')
        self.length = self.params['length']

    @classmethod
    def get_params_info(cls):
        return dict(
            length=''
        )

    @classmethod
    def get_default_param_values(cls):
        return dict(
            length=15
        )

    def draw_layout(self):

        start_port = self.add_photonic_port(
            name='IN',
            center=(0, 0),
            orient='R0',
            angle=0.0,
            width=self.port_width,
            layer=self.wg_port_layer
        )

        router = WgRouter(self,
                          start_port,
                          self.wg_routing_layer,
                          route_in_port_dir=True
                          )


        router.add_straight_wg(self.length)

        port = router.port
        port.name = 'OUT'

        self.add_photonic_port(port=port)

        self.add_round(
            layer=self.wg_routing_layer,
            resolution=self.grid.resolution,
            rout=5,
            center=(0.5 * self.length, 5 + 0.1 + 0.5 * self.port_width),
            rin=4
        )
