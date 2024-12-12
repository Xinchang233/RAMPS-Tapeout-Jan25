from BPG import PhotonicTemplateBase
from Photonic_Core_Layout.WaveguideBase.WgRouter import WgRouter
import importlib
import yaml

class SingleRingRowV1(PhotonicTemplateBase):
    """
    Photonic Ports:
    IN = left side
    OUT = right side
    """

    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)
        self.params = params
        # for key, val in self.params.items():
        #     # Automatically unpack variables
        #     # exec( “self.{} = {}“.format( key, val ) )
        #     exec(f”self.{key} = {val!r}” )


        self.port_width = 0.35
        self.wg_port_layer = ('si_full_free', 'port')
        self.wg_routing_layer = ('si_full_free', 'drawing')
        # self.wg_port_layer = ('RX', 'port')
        # self.wg_routing_layer = ('RX', 'drawing')

        self.grating_coupler_module = self.params['grating_coupler_module']
        self.grating_coupler_class = self.params['grating_coupler_class']
        # gc_module = importlib.import_module('gf45spclo_photonics.ph45spclo.iograt')
        gc_module = importlib.import_module(self.grating_coupler_module)
        # gc_class = getattr(gc_module, 'iograt_1311')
        gc_class = getattr(gc_module, self.grating_coupler_class)
        self.gc_master = self.new_template(params=None, temp_cls=gc_class)


        self.package_class_param_list = self.params['package_class_param_list']
        self.yaml_list = self.params['yaml_list']

        self.master_list = []
        self.inst_list = []
        self.site_pitch = self.params['site_pitch']
        self.track_pitch = self.params['track_pitch']

        self.x_coupler_clear = self.params['x_coupler_clear']
        self.y_coupler_clear = self.params['y_coupler_clear']
        self.x_coupler_pitch = self.params['x_coupler_pitch']
        self.y_coupler_pitch = self.params['y_coupler_pitch']

        self.x_port_coupler_in_base = self.params['x_port_coupler_in_base']
        self.x_port_coupler_out_base = self.params['x_port_coupler_out_base']
        self.y_port_coupler_base = self.params['y_port_coupler_base']

        self.dx_inst = self.params['dx_inst']
        self.dy_inst = self.params['dy_inst']
        self.x_instance = self.params['x_instance']
        self.dy_port_inst_bot = self.params['dy_port_inst_bot']
        self.dy_port_inst_top = self.params['dy_port_inst_top']

        self.bend_radius = self.photonic_tech_info.get_default_wg_params(self.wg_routing_layer)['radius']
        self.routing_width = self.photonic_tech_info.get_default_wg_params(self.wg_routing_layer)['width']




    @classmethod
    def get_params_info(cls):
        return dict(
            package_class_param_list='',
            yaml_list='',
            site_pitch='',
            track_pitch='',

            x_coupler_clear='',
            y_coupler_clear='',
            x_coupler_pitch='',
            y_coupler_pitch='',

            x_port_coupler_in_base='',
            x_port_coupler_out_base='',
            y_port_coupler_base='',

            dx_inst='',
            dy_inst='',
            dy_port_inst_bot='',
            dy_port_inst_top='',
            x_instance='',
            param_x='',

            grating_coupler_module='',
            grating_coupler_class='',


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

        # # Instantiate the sites
        # for ind, yaml_file in enumerate(self.yaml_list):
        #     with open(yaml_file, 'r') as f:
        #         yaml_content = yaml.load(f)
        #
        #     lay_module = importlib.import_module('cena_top.RAMPS.photonics.' + yaml_content['layout_package'])
        #     temp_cls = getattr(lay_module, yaml_content['layout_class'])
        #
        #     master = self.new_template(params=yaml_content['layout_params'],
        #                                temp_cls=temp_cls)
        #
        #     self.master_list.append(master)
        #
        #
        # in_port_name = 'PORT0'
        # out_port_name = 'PORT1'
        #
        # for ind, master in enumerate(self.master_list):
        #     master_in_port_loc = master.get_photonic_port(in_port_name).center
        #     self.inst_list.append(
        #         self.add_instance(
        #             master=master,
        #             loc=((ind * self.site_pitch - master_in_port_loc[0]),
        #                  (0 - master_in_port_loc[1])),
        #             # Offset site by location of input port, to put input port at desired location
        #             orient='R0',
        #         )
        #     )
        #
        #
        #
        #
        # num_sites = len(self.master_list)
        #
        # y0_top = max([inst.bound_box.top for inst in self.inst_list]) + 2 * self.track_pitch
        #
        # # inst.bound_box.bot doesn't exist?
        # # WgRouter routability determines "6"
        # y0_bot = min([inst.bound_box.top - inst.bound_box.height for inst in self.inst_list]) - 6 * self.track_pitch
        #
        # x_starts = self.inst_list[0][in_port_name].x - 2 * self.bend_radius
        # x_ends = self.inst_list[-1][out_port_name].x + 2 * self.bend_radius + self.site_pitch/2


        n_site = 5
        #### define coupler port positions
        list_idx_x_port_coupler_in = [0, 0, 2, 1, 1]
        list_idx_x_port_coupler_out = [1, 1, 0, 2, 2]
        list_idx_y_port_coupler_in = [1, 0, 1, 1, 0]
        list_x_port_coupler_in = [
            self.x_port_coupler_in_base + list_idx_x_port_coupler_in[i] * self.x_coupler_pitch for i in range(0, n_site)
        ]
        list_x_port_coupler_out = [
            self.x_port_coupler_out_base + list_idx_x_port_coupler_out[i] * self.x_coupler_pitch for i in range(0, n_site)
        ]
        list_y_port_coupler = [
            self.y_port_coupler_base + list_idx_y_port_coupler_in[i] * self.y_coupler_pitch for i in range(0, n_site)
        ]

        list_x_port_inst_in = [self.x_instance[i] - self.dx_inst / 2 for i in range(0, n_site)]
        list_x_port_inst_out = [self.x_instance[i] + self.dx_inst / 2 for i in range(0, n_site)]

        # 4 long horizontal waveguide tracks on the bottom side of the instances
        list_y_track_bot = [self.track_pitch * (i+1) for i in range(0, 4)]
        # horizontal track the bottom ports of the instances are on
        y_port_inst_bot = list_y_track_bot[-1] + self.track_pitch + self.dy_port_inst_bot

        # check if these positions are appropriate
        if (list_x_port_coupler_in[0] < self.x_coupler_clear):
            raise ValueError('Input Coupler x coordinate is too low')
        if (list_y_port_coupler[0] < list_y_track_bot[1] + self.track_pitch + self.y_coupler_clear / 2):
            raise ValueError('Coupler y coordinate is too low, will conflict with waveguide routing')


        # 7 long horizontal waveguide tracks on the top side of the instances
        y_track_top_min = max(list_y_port_coupler[0] + self.y_coupler_clear / 2 + self.track_pitch * 1,
                              list_y_track_bot[-1] + self.track_pitch + self.dy_inst + self.track_pitch * 0)
        list_y_track_top = [i * self.track_pitch + y_track_top_min for i in range(0, 4)]

        list_y_router_path_in = [list_y_track_top[-1-i] for i in range(0, 2)] + [list_y_track_bot[2-i] for i in range(0, 3)]
        list_y_router_path_out = [list_y_track_top[-1-i] for i in range(0, 4)]

        # gc_module = importlib.import_module(self.gc_module)
        # gc_class = getattr(gc_module, self.gc_class)
        # gc_master = self.new_template(temp_cls=getattr(self.gc_module, self.gc_class))
        #
        #
        list_gc_in = [
            self.add_instance(
                master=self.gc_master,
                loc=(list_x_port_coupler_in[i],
                     list_y_port_coupler[i]),
                # Offset site by location of input port, to put input port at desired location
                orient='R0',
            )
        for i in range(0, n_site)]
        list_gc_out = [
            self.add_instance(
                master=self.gc_master,
                loc=(list_x_port_coupler_out[i],
                     list_y_port_coupler[i]),
                # Offset site by location of input port, to put input port at desired location
                orient='MY',
            )
        for i in range(0, n_site)]

        # # Unpack the package list
        # for packclassparam in self.package_class_param_list:
        #     lay_module = importlib.import_module(packclassparam['package'])
        #     temp_cls = getattr(lay_module, packclassparam['class'])
        #
        #     master = self.new_template(params=packclassparam['params'],
        #                                temp_cls=temp_cls)
        #
        #     self.master_list.append(master)
        #
        #
        # list_inst_gc = []
        #
        # for i in range(0, n_site):
        #
        #     self.inst_list.append(
        #         self.add_instance(
        #             master=self.master_list[0],
        #             loc=(list_x_port_coupler_out[i],
        #                  list_y_port_coupler[i]),
        #             # Offset site by location of input port, to put input port at desired location
        #             orient='R0',
        #         )
        #     )



        list_port_in_main = [
            self.add_photonic_port(
                name=f'IN_MAIN{i}',
                center=(list_x_port_coupler_in[i], list_y_port_coupler[i]),
                orient='R0',
                layer=self.wg_port_layer,
                width=self.routing_width
            )
            for i in range(0, n_site)
        ]

        list_port_out_main = [
            self.add_photonic_port(
                name=f'OUT_MAIN{i}',
                center=(list_x_port_coupler_out[i], list_y_port_coupler[i]),
                orient='R0',
                layer=self.wg_port_layer,
                width=self.routing_width
            )
            for i in range(0, n_site)
        ]



        list_router_in_main = [
            WgRouter(
                self,
                list_port_in_main[i],
                self.wg_routing_layer,
                route_in_port_dir=True
            )
            for i in range(0, n_site)
        ]

        list_router_out_main = [
            WgRouter(
                self,
                list_port_out_main[i],
                self.wg_routing_layer,
                route_in_port_dir=False
            )
            for i in range(0, n_site)
        ]


        for i in range(0, n_site):
            in_router_path = []
            dy_in_bend = self.bend_radius if (i <= 1) else -self.bend_radius
            dx_bend_extra = self.track_pitch * (i == 1 or i == 3)
            in_router_path.extend(
                [
                    (list_x_port_coupler_in[i] + self.bend_radius + dx_bend_extra,
                     list_y_port_coupler[i] + dy_in_bend),
                    (list_x_port_coupler_in[i] + self.bend_radius * 2 + dx_bend_extra,
                     list_y_router_path_in[i]),
                ]
            )
            if i == 0:
                in_router_path.extend(
                    [
                        (list_x_port_inst_in[i] - self.bend_radius,
                         y_port_inst_bot + self.bend_radius),
                        (list_x_port_inst_in[i],
                         y_port_inst_bot),
                    ]
                )
            if i == 1:
                in_router_path.extend(
                    [
                        (list_x_port_inst_in[0] - self.bend_radius * 2,
                         list_y_track_bot[3] + self.bend_radius),
                        (list_x_port_inst_in[0] - self.bend_radius * 1,
                         list_y_track_bot[3]),
                    ]
                )

            if i != 0:
                in_router_path.extend(
                    [
                        (list_x_port_inst_in[i] - self.bend_radius * 3,
                         y_port_inst_bot + self.bend_radius * 1),
                        (list_x_port_inst_in[i] - self.bend_radius * 2,
                         y_port_inst_bot + self.bend_radius * 2),
                        (list_x_port_inst_in[i] - self.bend_radius * 1,
                         y_port_inst_bot + self.bend_radius * 1),
                        (list_x_port_inst_in[i],
                         y_port_inst_bot),
                    ]
                )

            list_router_in_main[i].cardinal_router(in_router_path)


            out_router_path = []
            dy_out_bend = self.bend_radius if (i <= 2) else -self.bend_radius
            dx_bend_extra = self.track_pitch * (i == 1 or i == 3)
            if (i >= 3):
                out_router_path.extend(
                    [
                        (list_x_port_coupler_out[i] - self.bend_radius - dx_bend_extra,
                         list_y_port_coupler[i] - self.bend_radius),
                        (list_x_port_coupler_out[i] - self.bend_radius * 2 - dx_bend_extra,
                         list_y_router_path_in[i] - self.bend_radius),
                     ]
                )
            else:
                out_router_path.extend(
                    [
                        (list_x_port_coupler_out[i] - self.bend_radius - dx_bend_extra,
                         list_y_port_coupler[i] + self.bend_radius),
                        (list_x_port_coupler_out[i] - self.bend_radius * 2 - dx_bend_extra,
                         list_y_router_path_out[i]),
                     ]
                )



            if (i == 4):
                out_router_path.extend(
                    [
                        (list_x_port_inst_out[i] + self.bend_radius * 3,
                         y_port_inst_bot + self.bend_radius * 1),
                        (list_x_port_inst_out[i] + self.bend_radius * 2,
                         y_port_inst_bot + self.bend_radius * 2),
                        (list_x_port_inst_out[i] + self.bend_radius * 1,
                         y_port_inst_bot + self.bend_radius * 1),
                        (list_x_port_inst_out[i],
                         y_port_inst_bot),
                    ]
                )
            if (i == 3):
                out_router_path.extend(
                    [
                        (list_x_port_inst_out[4] + self.bend_radius * 4,
                         list_y_router_path_out[i] - self.bend_radius * 1),
                        (list_x_port_inst_out[i] + self.bend_radius * 3,
                         list_y_router_path_out[i]),
                    ]
                )

            if (i != 4):
                out_router_path.extend(
                    [
                        (list_x_port_inst_out[i] + self.bend_radius,
                         y_port_inst_bot + self.bend_radius),
                        (list_x_port_inst_out[i],
                         y_port_inst_bot),

                    ]
                )


            list_router_out_main[i].cardinal_router(out_router_path)



        # #### site 0
        # idx_now = 0
        #
        # list_router_in_main[idx_now].cardinal_router(
        #     [
        #         (list_x_port_coupler_in[idx_now] + self.bend_radius * 1 + self.track_pitch,
        #          list_y_port_coupler[0] + self.bend_radius * 1),
        #         (list_x_port_inst_in[idx_now] - self.bend_radius * 2,
        #          list_y_track_top[2]),
        #         (list_x_port_inst_in[idx_now] - self.bend_radius * 3 - self.track_pitch,
        #          y_port_inst_bot + self.bend_radius * 1),
        #         (list_x_port_inst_in[idx_now],
        #          y_port_inst_bot),
        #     ]
        # )
        # list_router_in_drop[idx_now].cardinal_router(
        #     [
        #         (list_x_port_coupler_in[idx_now] + self.bend_radius * 1,
        #          list_y_port_coupler[1] + self.bend_radius * 1),
        #         (list_x_port_inst_in[idx_now] - self.bend_radius * 4,
        #          list_y_track_top[3]),
        #         # (list_x_port_inst_in[idx_now] - self.bend_radius * 3,
        #         #  y_port_inst_top - self.bend_radius * 1),
        #         # (list_x_port_inst_in[idx_now] - self.bend_radius * 2,
        #         #  y_port_inst_top - self.bend_radius * 2),
        #         (list_x_port_inst_in[idx_now] - self.bend_radius * 1,
        #          y_port_inst_top + self.bend_radius * 1),
        #         (list_x_port_inst_in[idx_now],
        #          y_port_inst_top),
        #     ]
        # )
        #
        #
        # list_router_out_main[idx_now].cardinal_router(
        #     [
        #         (list_x_port_coupler_out[idx_now] - self.bend_radius * 1 - self.track_pitch,
        #          list_y_port_coupler[0] + self.bend_radius),
        #         (list_x_port_coupler_out[idx_now] - self.bend_radius * 2 - self.track_pitch,
        #          list_y_track_top[2]),
        #         (list_x_port_inst_out[idx_now] + self.bend_radius * 3 + self.track_pitch,
        #          list_y_track_bot[4] + self.bend_radius),
        #         (list_x_port_inst_out[idx_now],
        #          y_port_inst_bot),
        #     ]
        # )
        #
        # router_path = [
        #     (list_x_port_coupler_out[idx_now] - self.bend_radius * 1,
        #      list_y_port_coupler[1] + self.bend_radius),
        #     (list_x_port_coupler_out[idx_now] - self.bend_radius * 2,
        #      list_y_track_top[3]),
        # ] + ([
        #     (list_x_port_inst_out[idx_now] + self.bend_radius * 3,
        #      y_port_inst_top - self.bend_radius * 1),
        #     (list_x_port_inst_out[idx_now] + self.bend_radius * 2,
        #      y_port_inst_top - self.bend_radius * 2),
        #     (list_x_port_inst_out[idx_now] + self.bend_radius * 1,
        #      y_port_inst_top - self.bend_radius * 1),
        #     (list_x_port_inst_out[idx_now],
        #      y_port_inst_top),
        # ] if flag_sp_routing_3 else [
        #     (list_x_port_inst_out[idx_now] + self.bend_radius * 1,
        #      y_port_inst_top + self.bend_radius * 1),
        #     (list_x_port_inst_out[idx_now],
        #      y_port_inst_top),
        # ])
        #
        # list_router_out_drop[idx_now].cardinal_router(router_path)
        #
        #
        #
        # #### site 1
        # idx_now = 1
        #
        # router_path = [
        #     (list_x_port_coupler_in[idx_now] + self.bend_radius * 1 + self.track_pitch,
        #      list_y_port_coupler[0] + self.bend_radius * 1),
        #     (list_x_port_coupler_in[idx_now+1] + self.bend_radius * 3 + self.track_pitch,
        #      list_y_track_top[0]),
        #     (list_x_port_coupler_in[idx_now + 1] + self.bend_radius * 4 + self.track_pitch,
        #      list_y_track_top[0] - self.bend_radius * 1),
        #     (list_x_port_inst_in[idx_now] - self.bend_radius * 4,
        #      list_y_track_bot[2]),
        # ] + ([
        #     (list_x_port_inst_in[idx_now] - self.bend_radius * 3,
        #      y_port_inst_bot + self.bend_radius * 1),
        #     (list_x_port_inst_in[idx_now] - self.bend_radius * 2,
        #      y_port_inst_bot + self.bend_radius * 2),
        #     (list_x_port_inst_in[idx_now] - self.bend_radius * 1,
        #      y_port_inst_bot + self.bend_radius * 1),
        #     (list_x_port_inst_in[idx_now],
        #      y_port_inst_bot),
        # ] if flag_sp_routing_2 else [
        #     (list_x_port_inst_in[idx_now] - self.bend_radius * 1,
        #      y_port_inst_bot - self.bend_radius * 1),
        #     (list_x_port_inst_in[idx_now],
        #      y_port_inst_bot),
        #
        # ])
        #
        # list_router_in_main[idx_now].cardinal_router(router_path)
        #
        #
        # list_router_in_drop[idx_now].cardinal_router(
        #     [
        #         (list_x_port_coupler_in[idx_now] + self.bend_radius * 1,
        #          list_y_port_coupler[1] + self.bend_radius * 1),
        #         (list_x_port_coupler_in[idx_now + 1] + self.bend_radius * 3 + self.track_pitch * 2,
        #          list_y_track_top[1]),
        #         (list_x_port_coupler_in[idx_now + 1] + self.bend_radius * 4 + self.track_pitch * 2,
        #          list_y_track_top[0] - self.bend_radius * 1),
        #         (list_x_port_inst_in[idx_now] - self.bend_radius * 4 - self.track_pitch,
        #          list_y_track_bot[3]),
        #         (list_x_port_inst_in[idx_now] - self.bend_radius * 3 - self.track_pitch,
        #          list_y_track_bot[3] + self.bend_radius),
        #         (list_x_port_inst_in[idx_now],
        #          y_port_inst_top),
        #     ]
        # )
        #
        #
        #
        # list_router_out_main[idx_now].cardinal_router([
        #     (list_x_port_coupler_out[idx_now] - self.bend_radius * 1 - self.track_pitch,
        #      list_y_port_coupler[0] + self.bend_radius),
        #     (list_x_port_coupler_out[idx_now] - self.bend_radius * 2 - self.track_pitch,
        #      list_y_track_top[0]),
        #     (list_x_port_inst_out[idx_now] + self.bend_radius * 3 + self.track_pitch,
        #      list_y_track_bot[4] - self.bend_radius),
        #     (list_x_port_inst_out[idx_now],
        #      y_port_inst_bot),
        # ])
        #
        # router_path = [
        #     (list_x_port_coupler_out[idx_now] - self.bend_radius * 1,
        #      list_y_port_coupler[1] + self.bend_radius),
        #     (list_x_port_coupler_out[idx_now] - self.bend_radius * 2,
        #      list_y_track_top[1]),
        # ] + ([
        #     (list_x_port_inst_out[idx_now] + self.bend_radius * 3,
        #      y_port_inst_top - self.bend_radius * 1),
        #     (list_x_port_inst_out[idx_now] + self.bend_radius * 2,
        #      y_port_inst_top - self.bend_radius * 2),
        #     (list_x_port_inst_out[idx_now] + self.bend_radius * 1,
        #      y_port_inst_top - self.bend_radius * 1),
        #     (list_x_port_inst_out[idx_now],
        #      y_port_inst_top),
        # ] if flag_sp_routing_2 else [
        #     (list_x_port_inst_out[idx_now] + self.bend_radius * 1,
        #      y_port_inst_top + self.bend_radius * 1),
        #     (list_x_port_inst_out[idx_now],
        #      y_port_inst_top),
        # ])
        #
        # list_router_out_drop[idx_now].cardinal_router(router_path)
        #
        # #### site 2
        # idx_now = 2
        #
        # router_path = ([
        #     (list_x_port_coupler_in[idx_now] + self.bend_radius * 1,
        #      list_y_port_coupler[0] + self.bend_radius * 1),
        #     (list_x_port_coupler_in[idx_now] + self.bend_radius * 2,
        #      list_y_port_coupler[0] + self.bend_radius * 2),
        #     (list_x_port_coupler_in[idx_now] + self.bend_radius * 3,
        #      list_y_port_coupler[0] + self.bend_radius * 1),
        # ] if flag_sp_routing_1 else [
        #     (list_x_port_coupler_in[idx_now] + self.bend_radius * 1,
        #      list_y_port_coupler[0] - self.bend_radius * 1),
        # ]) + [
        #     (list_x_port_inst_in[idx_now] - self.bend_radius * 4,
        #      list_y_track_bot[0])
        # ] +  ([
        #     (list_x_port_inst_in[idx_now] - self.bend_radius * 3,
        #      list_y_track_bot[0] + self.bend_radius * 1),
        #     (list_x_port_inst_in[idx_now] - self.bend_radius * 2,
        #      y_port_inst_bot + self.bend_radius * 2),
        #     (list_x_port_inst_in[idx_now] - self.bend_radius * 1,
        #      y_port_inst_bot + self.bend_radius * 1),
        #     (list_x_port_inst_in[idx_now],
        #      y_port_inst_bot),
        # ] if flag_sp_routing_3 else [
        #     (list_x_port_inst_in[idx_now] - self.bend_radius * 1,
        #      y_port_inst_bot - self.bend_radius * 1),
        #     (list_x_port_inst_in[idx_now],
        #      y_port_inst_bot),
        # ])
        #
        # list_router_in_main[idx_now].cardinal_router(router_path)
        #
        #
        # list_router_in_drop[idx_now].cardinal_router(
        #     [
        #         (list_x_port_coupler_in[idx_now] + self.bend_radius * 1 + self.track_pitch,
        #          list_y_port_coupler[0] - self.bend_radius * 1),
        #         (list_x_port_inst_in[idx_now] - self.bend_radius * 4 - self.track_pitch,
        #          list_y_track_bot[1]),
        #         (list_x_port_inst_in[idx_now] - self.bend_radius * 3 - self.track_pitch,
        #          y_port_inst_top - self.bend_radius * 1),
        #         (list_x_port_inst_in[idx_now],
        #          y_port_inst_top),
        #     ]
        # )
        #
        # router_path = ([
        #     (list_x_port_coupler_out[idx_now] - self.bend_radius * 1,
        #      list_y_port_coupler[0] + self.bend_radius * 1),
        #     (list_x_port_coupler_out[idx_now] - self.bend_radius * 2,
        #      list_y_port_coupler[0] + self.bend_radius * 2),
        #     (list_x_port_coupler_out[idx_now] - self.bend_radius * 3,
        #      list_y_port_coupler[0] + self.bend_radius * 1),
        # ] if flag_sp_routing_1 else [
        #     (list_x_port_coupler_out[idx_now] - self.bend_radius * 1,
        #      list_y_port_coupler[0] - self.bend_radius * 1),
        # ]) + [
        #     (list_x_port_inst_out[idx_now] + self.bend_radius * 4,
        #      list_y_track_bot[0])
        # ] +  ([
        #     (list_x_port_inst_out[idx_now] + self.bend_radius * 3,
        #      list_y_track_bot[0] + self.bend_radius * 1),
        #     (list_x_port_inst_out[idx_now] + self.bend_radius * 2,
        #      y_port_inst_bot + self.bend_radius * 2),
        #     (list_x_port_inst_out[idx_now] + self.bend_radius * 1,
        #      y_port_inst_bot + self.bend_radius * 1),
        #     (list_x_port_inst_out[idx_now],
        #      y_port_inst_bot),
        # ] if flag_sp_routing_3 else [
        #     (list_x_port_inst_out[idx_now] + self.bend_radius * 1,
        #      y_port_inst_bot - self.bend_radius),
        #     (list_x_port_inst_out[idx_now],
        #      y_port_inst_bot),
        # ])
        #
        #
        # list_router_out_main[idx_now].cardinal_router(router_path)
        #
        #
        # list_router_out_drop[idx_now].cardinal_router(
        #     [
        #         (list_x_port_coupler_out[idx_now] - self.bend_radius * 1 - self.track_pitch,
        #          list_y_port_coupler[0] - self.bend_radius * 1),
        #         (list_x_port_inst_out[idx_now] + self.bend_radius * 4 + self.track_pitch,
        #          list_y_track_bot[1]),
        #         (list_x_port_inst_out[idx_now] + self.bend_radius * 3 + self.track_pitch,
        #          y_port_inst_top - self.bend_radius * 1),
        #         (list_x_port_inst_out[idx_now],
        #          y_port_inst_top),
        #     ]
        # )


        # router_in_main.cardinal_router(
        #     [(x_instance[idx_now]-dx_inst_port_min/2, y_track_inst_bot)
        #      ]
        # )





        # for ind in range(len(self.inst_list)):
        #
		 #    # Ports define "routing tracks"
        #     start_port = self.add_photonic_port(
        #         name=f'IN{ind}',
        #         center=(x_starts, y0_top + ind * self.track_pitch),
        #         orient='R0',
        #         layer=self.wg_port_layer,
        #         width=self.routing_width
        #     )
        #     end_port = self.add_photonic_port(
        #         name=f'OUT{ind}',
        #         center=(x_ends, y0_bot + ind * self.track_pitch),
        #         orient='R0',
        #         layer=self.wg_port_layer,
        #         width=self.routing_width
        #    )
        #
        #     inst = self.inst_list[ind]
        #
        #     # Route from the start to the site
        #     router = WgRouter(self,
        #                       start_port,
        #                       self.wg_routing_layer,
        #                       route_in_port_dir=True
        #                       )
        #
        #     router.cardinal_router(
        #         [(inst[in_port_name].x - self.bend_radius,
        #           inst[in_port_name].y + self.bend_radius),
        #          (inst[in_port_name].x,
        #           inst[in_port_name].y),
        #         ])
        #
        #     # Route from the output of the site to the end
        #     router_end = WgRouter(self,
        #                         inst[out_port_name],
        #                         self.wg_routing_layer,
        #                         # What is this?
        #                         route_in_port_dir=False
        #                         )
        #
        #     # Better solution?
        #     router_end.cardinal_router(
        #         [(inst[out_port_name].x + self.site_pitch/2.0 - 2*self.bend_radius,
        #         inst[out_port_name].y),
        #         (inst[out_port_name].x + self.site_pitch/2.0 - self.bend_radius,
        #         inst[out_port_name].y - self.bend_radius),
        #         (inst[out_port_name].x + self.site_pitch/2.0 - self.bend_radius,
        #         end_port.y + self.bend_radius),
        #         (inst[out_port_name].x + self.site_pitch/2.0,
        #         end_port.y),
        #         (end_port.x, end_port.y)
        #         ]
        #     )

class SingleRingRow(PhotonicTemplateBase):
    """
    Photonic Ports:
    IN = left side
    OUT = right side
    """

    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)
        self.params = params
        # for key, val in self.params.items():
        #     # Automatically unpack variables
        #     # exec( “self.{} = {}“.format( key, val ) )
        #     exec(f”self.{key} = {val!r}” )


        self.port_width = 0.35
        self.wg_port_layer = ('si_full_free', 'port')
        self.wg_routing_layer = ('si_full_free', 'drawing')
        # self.wg_port_layer = ('RX', 'port')
        # self.wg_routing_layer = ('RX', 'drawing')

        self.grating_coupler_module = self.params['grating_coupler_module']
        self.grating_coupler_class = self.params['grating_coupler_class']
        gc_module = importlib.import_module(self.grating_coupler_module)
        gc_class = getattr(gc_module, self.grating_coupler_class)
        self.gc_master = self.new_template(params=None, temp_cls=gc_class)


        self.package_class_param_list = self.params['package_class_param_list']
        self.yaml_list = self.params['yaml_list']

        self.master_list = []
        self.inst_list = []
        self.site_pitch = self.params['site_pitch']
        self.track_pitch = self.params['track_pitch']

        self.x_coupler_clear = self.params['x_coupler_clear']
        self.y_coupler_clear = self.params['y_coupler_clear']
        self.x_coupler_pitch = self.params['x_coupler_pitch']
        self.y_coupler_pitch = self.params['y_coupler_pitch']

        self.x_port_coupler_in_base = self.params['x_port_coupler_in_base']
        self.x_port_coupler_out_base = self.params['x_port_coupler_out_base']
        self.y_port_coupler_base = self.params['y_port_coupler_base']

        self.dx_inst = self.params['dx_inst']
        self.dy_inst = self.params['dy_inst']
        self.x_instance = self.params['x_instance']
        self.dy_port_inst_bot = self.params['dy_port_inst_bot']
        self.dy_port_inst_top = self.params['dy_port_inst_top']

        self.bend_radius = self.photonic_tech_info.get_default_wg_params(self.wg_routing_layer)['radius']
        self.routing_width = self.photonic_tech_info.get_default_wg_params(self.wg_routing_layer)['width']




    @classmethod
    def get_params_info(cls):
        return dict(
            package_class_param_list='',
            yaml_list='',
            site_pitch='',
            track_pitch='',

            x_coupler_clear='',
            y_coupler_clear='',
            x_coupler_pitch='',
            y_coupler_pitch='',

            x_port_coupler_in_base='',
            x_port_coupler_out_base='',
            y_port_coupler_base='',

            dx_inst='',
            dy_inst='',
            dy_port_inst_bot='',
            dy_port_inst_top='',
            x_instance='',
            param_x='',

            grating_coupler_module='',
            grating_coupler_class='',


        )

    @classmethod
    def get_default_param_values(cls):
        return dict(
        )

    def draw_layout(self):

        # instantiate the ring modulator masters
        list_inst_direction = []
        list_dx_inst = []
        # list_dy_inst = []
        list_x_inst_offset = []
        list_y_inst_offset = []

        in_port_name = 'PORT0'
        out_port_name = 'PORT1'
        for ind, yaml_file in enumerate(self.yaml_list):
            if yaml_file != 'VOID':
                with open(yaml_file, 'r') as f:
                    yaml_content = yaml.load(f)

                lay_module = importlib.import_module(yaml_content['layout_package'])
                temp_cls = getattr(lay_module, yaml_content['layout_class'])

                master = self.new_template(params=yaml_content['layout_params'],
                                           temp_cls=temp_cls)

                self.master_list.append(master)
                master_in_port_loc = master.get_photonic_port(in_port_name).center


                if ((yaml_content['layout_package'] ==
                         'cena_top.RAMPS.photonics.Single_ring_fullrib.ring_rib_wg_vertical') or
                        (yaml_content['layout_package'] ==
                             'cena_top.RAMPS.photonics.Single_ring_fullrib.ring_rib_wg_spoked')):

                    list_inst_direction.append('MXR90')
                    list_dx_inst.append(abs(master_in_port_loc[1] * 2.0))
                    # list_dy_inst.append(abs(master_in_port_loc[0] * 2.0))
                    list_x_inst_offset.append(abs(master_in_port_loc[1] * -1.0))
                    list_y_inst_offset.append(abs(master_in_port_loc[0] * -1.0))
                else:
                    list_inst_direction.append('MX')
                    list_dx_inst.append(abs(master_in_port_loc[0] * 2.0))
                    # list_dy_inst.append(abs(master_in_port_loc[1] * 2.0))
                    list_x_inst_offset.append(abs(master_in_port_loc[0] * -1.0))
                    list_y_inst_offset.append(abs(master_in_port_loc[1] * 1.0))
            else:
                self.master_list.append([])
                list_dx_inst.append(0)
                list_x_inst_offset.append(0)
                list_y_inst_offset.append(0)
                list_inst_direction.append('MX')

        n_site = 5



        #### define coupler port positions
        list_idx_x_port_coupler_in = [0, 1, 2, 3, 4]
        list_idx_x_port_coupler_out = [3, 2, 1, 0, 4]
        list_x_port_coupler_in = [
            self.x_port_coupler_in_base + list_idx_x_port_coupler_in[i] * self.x_coupler_pitch for i in range(0, n_site)
        ]
        list_x_port_coupler_out = [
            self.x_port_coupler_out_base + list_idx_x_port_coupler_out[i] * self.x_coupler_pitch for i in range(0, n_site)
        ]
        y_port_coupler = self.y_port_coupler_base

        list_x_port_inst_in = [self.x_instance[i] - list_dx_inst[i] / 2 for i in range(0, n_site)]
        list_x_port_inst_out = [self.x_instance[i] + list_dx_inst[i] / 2 for i in range(0, n_site)]

        # 4 long horizontal waveguide tracks on the bottom side of the instances
        list_y_track_bot = [self.track_pitch * (i+1) for i in range(0, n_site)]
        # horizontal track the bottom ports of the instances are on
        list_y_port_inst_bot = [list_y_track_bot[-1-i] + self.track_pitch + self.dy_port_inst_bot for i in range(0, n_site)]

        # check if these positions are appropriate
        if (list_x_port_coupler_in[0] < self.x_coupler_clear):
            raise ValueError('Input Coupler x coordinate is too low')
        if (y_port_coupler < list_y_track_bot[1] + self.track_pitch + self.y_coupler_clear / 2):
            raise ValueError('Coupler y coordinate is too low, will conflict with waveguide routing')


        # 7 long horizontal waveguide tracks on the top side of the instances
        y_track_top_min = max(y_port_coupler + max(self.y_coupler_clear / 2 + self.track_pitch * 1, self.bend_radius * 2),
                              list_y_track_bot[-1] + self.bend_radius * 2)
        list_y_track_top = [i * self.track_pitch + y_track_top_min for i in range(0, 4)]

        list_y_router_path_in = [list_y_track_top[-1-i] for i in range(0, 4)] + [list_y_track_bot[0]]
        list_y_router_path_out = [list_y_track_top[-1-i] for i in range(0, 4)] + [list_y_track_bot[0]]


        # instantiate the grating couplers
        list_gc_in = [
            self.add_instance(
                master=self.gc_master,
                loc=(list_x_port_coupler_in[i],
                     y_port_coupler),
                # Offset site by location of input port, to put input port at desired location
                orient='R0',
            )
        for i in range(0, n_site)]
        list_gc_out = [
            self.add_instance(
                master=self.gc_master,
                loc=(list_x_port_coupler_out[i],
                     y_port_coupler),
                # Offset site by location of input port, to put input port at desired location
                orient='MY',
            )
        for i in range(0, n_site)]

        # instantiate the rings
        for i in range(0, n_site):
            if list_dx_inst[i] != 0:
                master_in_port_loc = self.master_list[i].get_photonic_port(in_port_name).center
                self.inst_list.append(
                    self.add_instance(
                        master=self.master_list[i],
                        loc=(list_x_port_inst_in[i] + list_x_inst_offset[i],
                             list_y_port_inst_bot[i] + list_y_inst_offset[i]),
                        orient=list_inst_direction[i],
                    )
                )

        list_port_in_main = [
            self.add_photonic_port(
                name=f'IN_MAIN{i}',
                center=(list_x_port_coupler_in[i], y_port_coupler),
                orient='R0',
                layer=self.wg_port_layer,
                width=self.routing_width
            )
            for i in range(0, n_site)
        ]

        list_port_out_main = [
            self.add_photonic_port(
                name=f'OUT_MAIN{i}',
                center=(list_x_port_coupler_out[i], y_port_coupler),
                orient='R0',
                layer=self.wg_port_layer,
                width=self.routing_width
            )
            for i in range(0, n_site)
        ]



        list_router_in_main = [
            WgRouter(
                self,
                list_port_in_main[i],
                self.wg_routing_layer,
                route_in_port_dir=True
            )
            for i in range(0, n_site)
        ]

        list_router_out_main = [
            WgRouter(
                self,
                list_port_out_main[i],
                self.wg_routing_layer,
                route_in_port_dir=False
            )
            for i in range(0, n_site)
        ]


        for i in range(0, n_site):
            in_router_path = []
            dy_in_bend = self.bend_radius if (i != 4) else -self.bend_radius
            dx_bend_extra = 10
            in_router_path.extend(
                [
                    (list_x_port_coupler_in[i] + self.bend_radius + dx_bend_extra,
                     y_port_coupler + dy_in_bend),
                    (list_x_port_coupler_in[i] + self.bend_radius * 2 + dx_bend_extra,
                     list_y_router_path_in[i]),
                ]
            )
            if (i > 0 and i < 4):
                in_router_path.extend(
                    [
                        (list_x_port_inst_in[0] - self.bend_radius * (i + 1),
                         list_y_track_bot[-1-i] + self.bend_radius),
                        (list_x_port_inst_in[i] - self.bend_radius * 4,
                         list_y_track_bot[-1-i]),
                    ]
                )
            if i == 0:
                in_router_path.extend(
                    [
                        (list_x_port_inst_in[i] - self.bend_radius * 1,
                         list_y_port_inst_bot[i] + self.bend_radius),
                        (list_x_port_inst_in[i],
                         list_y_port_inst_bot[i]),
                    ]
                )
            else:
                in_router_path.extend(
                    [
                        (list_x_port_inst_in[i] - self.bend_radius * 3,
                         list_y_port_inst_bot[i] + self.bend_radius * 1),
                        (list_x_port_inst_in[i] - self.bend_radius * 2,
                         list_y_port_inst_bot[i] + self.bend_radius * 2),
                        (list_x_port_inst_in[i] - self.bend_radius * 1,
                         list_y_port_inst_bot[i] + self.bend_radius * 1),
                        (list_x_port_inst_in[i] - self.bend_radius * 0,
                         list_y_port_inst_bot[i] + self.bend_radius * 0),
                    ]
                )

            list_router_in_main[i].cardinal_router(in_router_path)


            out_router_path = []
            dy_out_bend = self.bend_radius if (i != 4) else -self.bend_radius
            out_router_path.extend(
                [
                    (list_x_port_coupler_out[i] - self.bend_radius - dx_bend_extra,
                     y_port_coupler + dy_out_bend),
                    (list_x_port_coupler_out[i] - self.bend_radius * 2 - dx_bend_extra,
                     list_y_router_path_out[i]),
                ]
            )
            if i == 4:
                out_router_path.extend(
                    [
                        (list_x_port_inst_out[i] + self.bend_radius * 3,
                         list_y_port_inst_bot[i] + self.bend_radius * 1),
                        (list_x_port_inst_out[i] + self.bend_radius * 2,
                         list_y_port_inst_bot[i] + self.bend_radius * 2),
                        (list_x_port_inst_out[i] + self.bend_radius * 1,
                         list_y_port_inst_bot[i] + self.bend_radius * 1),
                        (list_x_port_inst_out[i] - self.bend_radius * 0,
                         list_y_port_inst_bot[i] + self.bend_radius * 0),
                    ]
                )
            else:
                out_router_path.extend(
                    [
                        (list_x_port_inst_out[i] + self.bend_radius * 1,
                         list_y_port_inst_bot[i] + self.bend_radius * 1),
                        (list_x_port_inst_out[i] - self.bend_radius * 0,
                         list_y_port_inst_bot[i] + self.bend_radius * 0),
                    ]
                )
            list_router_out_main[i].cardinal_router(out_router_path)







        # for ind in range(len(self.inst_list)):
        #
		 #    # Ports define "routing tracks"
        #     start_port = self.add_photonic_port(
        #         name=f'IN{ind}',
        #         center=(x_starts, y0_top + ind * self.track_pitch),
        #         orient='R0',
        #         layer=self.wg_port_layer,
        #         width=self.routing_width
        #     )
        #     end_port = self.add_photonic_port(
        #         name=f'OUT{ind}',
        #         center=(x_ends, y0_bot + ind * self.track_pitch),
        #         orient='R0',
        #         layer=self.wg_port_layer,
        #         width=self.routing_width
        #    )
        #
        #     inst = self.inst_list[ind]
        #
        #     # Route from the start to the site
        #     router = WgRouter(self,
        #                       start_port,
        #                       self.wg_routing_layer,
        #                       route_in_port_dir=True
        #                       )
        #
        #     router.cardinal_router(
        #         [(inst[in_port_name].x - self.bend_radius,
        #           inst[in_port_name].y + self.bend_radius),
        #          (inst[in_port_name].x,
        #           inst[in_port_name].y),
        #         ])
        #
        #     # Route from the output of the site to the end
        #     router_end = WgRouter(self,
        #                         inst[out_port_name],
        #                         self.wg_routing_layer,
        #                         # What is this?
        #                         route_in_port_dir=False
        #                         )
        #
        #     # Better solution?
        #     router_end.cardinal_router(
        #         [(inst[out_port_name].x + self.site_pitch/2.0 - 2*self.bend_radius,
        #         inst[out_port_name].y),
        #         (inst[out_port_name].x + self.site_pitch/2.0 - self.bend_radius,
        #         inst[out_port_name].y - self.bend_radius),
        #         (inst[out_port_name].x + self.site_pitch/2.0 - self.bend_radius,
        #         end_port.y + self.bend_radius),
        #         (inst[out_port_name].x + self.site_pitch/2.0,
        #         end_port.y),
        #         (end_port.x, end_port.y)
        #         ]
        #     )

class SingleRingRowArray(PhotonicTemplateBase):
    """
    Photonic Ports:
    IN = left side
    OUT = right side
    """

    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)
        self.params = params
        # for key, val in self.params.items():
        #     # Automatically unpack variables
        #     # exec( “self.{} = {}“.format( key, val ) )
        #     exec(f”self.{key} = {val!r}” )


        self.port_width = 0.35
        self.wg_port_layer = ('si_full_free', 'port')
        self.wg_routing_layer = ('si_full_free', 'drawing')
        # self.wg_port_layer = ('RX', 'port')
        # self.wg_routing_layer = ('RX', 'drawing')

        self.grating_coupler_module = self.params['grating_coupler_module']
        self.grating_coupler_class = self.params['grating_coupler_class']
        gc_module = importlib.import_module(self.grating_coupler_module)
        gc_class = getattr(gc_module, self.grating_coupler_class)
        self.gc_master = self.new_template(params=None, temp_cls=gc_class)


        self.package_class_param_list = self.params['package_class_param_list']
        self.yaml_list = self.params['yaml_list']

        self.master_list = []
        self.inst_list = []
        self.site_pitch = self.params['site_pitch']
        self.track_pitch = self.params['track_pitch']

        self.x_coupler_clear = self.params['x_coupler_clear']
        self.y_coupler_clear = self.params['y_coupler_clear']
        self.x_coupler_pitch = self.params['x_coupler_pitch']
        self.y_coupler_pitch = self.params['y_coupler_pitch']

        self.x_port_coupler_in_base = self.params['x_port_coupler_in_base']
        self.x_port_coupler_out_base = self.params['x_port_coupler_out_base']
        self.y_port_coupler_base = self.params['y_port_coupler_base']

        self.dx_inst = self.params['dx_inst']
        self.dy_inst = self.params['dy_inst']
        self.x_instance = self.params['x_instance']
        self.dy_port_inst_bot = self.params['dy_port_inst_bot']
        self.dy_port_inst_top = self.params['dy_port_inst_top']


        self.n_rowpairs = self.params['n_rowpairs']
        self.y_pitch_rowpairs = self.params['y_pitch_rowpairs']
        self.y_split_in_pair = self.params['y_split_in_pair']

        self.bend_radius = self.photonic_tech_info.get_default_wg_params(self.wg_routing_layer)['radius']
        self.routing_width = self.photonic_tech_info.get_default_wg_params(self.wg_routing_layer)['width']




    @classmethod
    def get_params_info(cls):
        return dict(
            package_class_param_list='',
            yaml_list='',
            site_pitch='',
            track_pitch='',

            x_coupler_clear='',
            y_coupler_clear='',
            x_coupler_pitch='',
            y_coupler_pitch='',

            x_port_coupler_in_base='',
            x_port_coupler_out_base='',
            y_port_coupler_base='',

            dx_inst='',
            dy_inst='',
            dy_port_inst_bot='',
            dy_port_inst_top='',
            x_instance='',
            param_x='',

            grating_coupler_module='',
            grating_coupler_class='',


        )

    @classmethod
    def get_default_param_values(cls):
        return dict(
        )

    def draw_layout(self):


        n_site = 5
        for i in range(0, self.n_rowpairs):
            layout_params_r180 = self.params
            layout_params_r0 = self.params
            yaml_list_mx = self.yaml_list[n_site*(2*i+0):n_site*(2*i+1)]
            yaml_list_r0 = self.yaml_list[n_site*(2*i+1):n_site*(2*i+2)]
            layout_params_r180['yaml_list'] = yaml_list_mx
            layout_params_r0['yaml_list'] = yaml_list_r0

            master_r180 = self.new_template(params=layout_params_r180, temp_cls=SingleRingRow)
            master_r0 = self.new_template(params=layout_params_r0, temp_cls=SingleRingRow)

            #
            dx_inst_r180 = master_r180.bound_box.width
            x_coupler_r180_rightmost = self.x_port_coupler_out_base + \
                                     self.x_coupler_pitch * (n_site-1)
            x_inst_r180 = self.x_port_coupler_in_base + x_coupler_r180_rightmost
            # x_inst_mx = 0
            y_inst_r180 = self.y_pitch_rowpairs * i + \
                          self.y_port_coupler_base * 2 - self.y_coupler_pitch
            x_inst_r0 = 0
            y_inst_r0 = y_inst_r180 + self.y_split_in_pair

            # hfshfs

            self.add_instance(
                master=master_r180,
                loc=(x_inst_r180, y_inst_r180),
                orient='R180',
            )
            self.add_instance(
                master=master_r0,
                loc=(x_inst_r0, y_inst_r0),
                orient='R0',
            )


