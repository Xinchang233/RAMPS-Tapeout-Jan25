from BPG import PhotonicTemplateBase
from Photonic_Core_Layout.WaveguideBase.WgRouter import WgRouter
import importlib
import yaml
import numpy as np
from copy import deepcopy, copy


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

        self.bend_radius = self.photonic_tech_info.get_default_wg_params(self.wg_routing_layer)['radius'] + 0.01
        self.routing_width = self.photonic_tech_info.get_default_wg_params(self.wg_routing_layer)['width']




    @classmethod
    def get_params_info(cls):
        return dict(
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


    def adjust_location(self, loc, rotation):
        if rotation == 'R0':
            return ( loc[0],  loc[1])
        elif rotation == 'R90':
            return (-loc[1],  loc[0])
        elif rotation == 'R180':
            return (-loc[0], -loc[1])
        elif rotation == 'R270':
            return ( loc[1], -loc[0])
        elif rotation == 'MX':
            return ( loc[0], -loc[1])
        elif rotation == 'MY':
            return (-loc[0],  loc[1])
        elif rotation == 'MXR90':
            return ( loc[1],  loc[0])
        else:
            return (-loc[1], -loc[0])


    def adjust_rotation_and_location(self, bound_box, loc_in, loc_out):
        loc_center = ((bound_box.left+bound_box.right)/2.0,
                      (bound_box.top+bound_box.bottom)/2.0)
        if loc_out[1] == loc_in[1]:
            # R0, R180, MX or MY
            if loc_out[0] > loc_in[0]:
                # no need to do MY related thing
                loc_in_extend = (bound_box.left, loc_in[1])
                loc_out_extend = (bound_box.right, loc_out[1])
                if loc_out[1] <= loc_center[1]:
                    rotation = 'R0'
                else:
                    rotation = 'MX'
            else:
                # need to MY
                loc_in_extend = (bound_box.right, loc_in[1])
                loc_out_extend = (bound_box.left, loc_out[1])
                if loc_out[1] <= loc_center[1]:
                    rotation = 'MY'
                else:
                    rotation = 'R180'
        else:
            # R90, R270, MXR90 or MYR90
            if loc_out[1] > loc_in[1]:
                loc_in_extend = (loc_in[0], bound_box.bottom)
                loc_out_extend = (loc_out[0], bound_box.top)
                # no need to do MY related thing
                if loc_out[0] >= loc_center[0]:
                    rotation = 'R270'
                else:
                    rotation = 'MXR90'
            else:
                # need to MY
                loc_in_extend = (loc_in[0], bound_box.top)
                loc_out_extend = (loc_out[0], bound_box.bottom)
                if loc_out[0] >= loc_center[0]:
                    rotation = 'MYR90'
                else:
                    rotation = 'R90'
        loc_in_adj = self.adjust_location(loc_in, rotation)
        loc_out_adj = self.adjust_location(loc_out, rotation)
        loc_in_extend_adj = self.adjust_location(loc_in_extend, rotation)
        loc_out_extend_adj = self.adjust_location(loc_out_extend, rotation)
        loc_in_extend_adj = self.adjust_location(loc_in, rotation)
        loc_out_extend_adj = self.adjust_location(loc_out, rotation)
        return rotation, loc_in_adj, loc_out_adj, loc_in_extend_adj, loc_out_extend_adj

    def adjust_rotation_and_location_from_master(self, master, in_port_name, out_port_name):
        port_in = master.get_photonic_port(in_port_name)
        port_out = master.get_photonic_port(out_port_name)
        # gdad
        loc_in = port_in.center
        loc_out = port_out.center
        bound_box = master.bound_box
        loc_center = ((bound_box.left+bound_box.right)/2.0,
                      (bound_box.top+bound_box.bottom)/2.0)
        print(port_in.angle, abs((port_in.angle+180)%180 - 90))
        if (abs(port_in.angle) < 1e-3) or (abs(port_in.angle-np.pi) < 1e-3):
            # R0, R180, MX or MY
            if loc_out[0] > loc_in[0]:
                # no need to do MY related thing
                loc_in_extend = (bound_box.left, loc_in[1])
                loc_out_extend = (bound_box.right, loc_out[1])
                if loc_out[1] <= loc_center[1]:
                    rotation = 'R0'
                else:
                    rotation = 'MX'
            else:
                # need to MY
                loc_in_extend = (bound_box.right, loc_in[1])
                loc_out_extend = (bound_box.left, loc_out[1])
                if loc_out[1] <= loc_center[1]:
                    rotation = 'MY'
                else:
                    rotation = 'R180'
        else:
            # R90, R270, MXR90 or MYR90
            if loc_out[1] > loc_in[1]:
                loc_in_extend = (loc_in[0], bound_box.bottom)
                loc_out_extend = (loc_out[0], bound_box.top)
                # no need to do MY related thing
                if loc_out[0] >= loc_center[0]:
                    rotation = 'R270'
                else:
                    rotation = 'MXR90'
            else:
                # need to MY
                loc_in_extend = (loc_in[0], bound_box.top)
                loc_out_extend = (loc_out[0], bound_box.bottom)
                if loc_out[0] >= loc_center[0]:
                    rotation = 'MYR90'
                else:
                    rotation = 'R90'
        loc_in_adj = self.adjust_location(loc_in, rotation)
        loc_out_adj = self.adjust_location(loc_out, rotation)
        loc_in_extend_adj = self.adjust_location(loc_in_extend, rotation)
        loc_out_extend_adj = self.adjust_location(loc_out_extend, rotation)
        loc_in_extend_adj = self.adjust_location(loc_in, rotation)
        loc_out_extend_adj = self.adjust_location(loc_out, rotation)
        return rotation, loc_in_adj, loc_out_adj, loc_in_extend_adj, loc_out_extend_adj


    def draw_layout(self):

        # instantiate the ring modulator masters
        list_inst_direction = []
        list_dx_inst = []
        # list_dy_inst = []
        list_x_inst_in_offset = []
        list_x_inst_out_offset = []
        list_x_inst_in_extend_offset = []
        list_x_inst_out_extend_offset = []
        list_y_inst_in_offset = []
        list_y_inst_out_offset = []

        in_port_name = 'PORT0'
        out_port_name = 'PORT1'
        for ind, yaml_tuple in enumerate(self.yaml_list):
            yaml_file = yaml_tuple[0]
            yaml_direction = yaml_tuple[1]
            if yaml_file != 'VOID':
                with open(yaml_file, 'r') as f:
                    yaml_content = yaml.load(f)

                lay_module = importlib.import_module(yaml_content['layout_package'])
                temp_cls = getattr(lay_module, yaml_content['layout_class'])

                master = self.new_template(params=yaml_content['layout_params'],
                                           temp_cls=temp_cls)

                master_in_port_loc = master.get_photonic_port(in_port_name).center
                master_out_port_loc = master.get_photonic_port(out_port_name).center

                rotation, loc_in_adj, loc_out_adj, loc_in_extend_adj, loc_out_extend_adj = \
                    self.adjust_rotation_and_location(master.bound_box, master_in_port_loc, master_out_port_loc)
                rotation_old, loc_in_adj_old, loc_out_adj_old, loc_in_extend_adj_old, loc_out_extend_adj_old = \
                    rotation, loc_in_adj, loc_out_adj, loc_in_extend_adj, loc_out_extend_adj

                rotation, loc_in_adj, loc_out_adj, loc_in_extend_adj, loc_out_extend_adj = \
                    self.adjust_rotation_and_location_from_master(master, in_port_name, out_port_name)
                if yaml_direction[0] == 'O':
                    rotation = yaml_direction[1:]
                self.master_list.append(master)
                list_inst_direction.append(rotation)
                list_y_inst_in_offset.append(loc_in_adj[1])
                list_y_inst_out_offset.append(loc_out_adj[1])
                list_x_inst_in_offset.append(loc_in_adj[0])
                list_x_inst_out_offset.append(loc_out_adj[0])
                list_x_inst_in_extend_offset.append(loc_in_extend_adj[0])
                list_x_inst_out_extend_offset.append(loc_out_extend_adj[0])
                list_dx_inst.append(loc_out_extend_adj[0] - loc_in_extend_adj[0])

                if ind==1:
                    print('PRINT', master, rotation, loc_in_adj)
            else:
                self.master_list.append([])
                list_inst_direction.append('R0')
                list_y_inst_in_offset.append(0)
                list_y_inst_out_offset.append(0)
                list_x_inst_in_offset.append(0)
                list_x_inst_out_offset.append(0)
                list_x_inst_in_extend_offset.append(0)
                list_x_inst_out_extend_offset.append(0)
                list_dx_inst.append(0)

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
        y_port_inst_bot = list_y_track_bot[-1] + self.dy_port_inst_bot

        # check if these positions are appropriate
        if (list_x_port_coupler_in[0] < self.x_coupler_clear):
            raise ValueError('Input Coupler x coordinate is too low')
        if (y_port_coupler < list_y_track_bot[1] + self.track_pitch + self.y_coupler_clear / 2):
            raise ValueError('Coupler y coordinate is too low, will conflict with waveguide routing')


        # 7 long horizontal waveguide tracks on the top side of the instances
        y_track_top_min = max(y_port_coupler + max(self.y_coupler_clear / 2 + self.track_pitch * 1, self.bend_radius * 2),
                              list_y_track_bot[-1] + self.bend_radius * 2)
        list_y_track_top = [i * self.track_pitch + y_track_top_min for i in range(0, n_site-1)]

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

        list_y_inst_in = [y_port_inst_bot for i in range(0, n_site)]
        list_y_inst_out = [y_port_inst_bot for i in range(0, n_site)]

        # instantiate the rings
        for i in range(0, n_site):
            if list_dx_inst[i] != 0:
                master_in_port_loc = self.master_list[i].get_photonic_port(in_port_name).center
                y_inst_rotated = (list_y_track_top[-1] + list_y_track_bot[0]) / 2
                if list_y_inst_in_offset[i] == list_y_inst_out_offset[i]:
                    # y_inst = list_y_track_top[1] - self.track_pitch * i - self.bend_radius * 2 - list_y_inst_in_offset[i]
                    y_inst = list_y_track_bot[-1-i] + self.bend_radius * 0.5 - list_y_inst_in_offset[i]
                    list_y_inst_in[i] = y_inst + list_y_inst_in_offset[i]
                    list_y_inst_out[i] = y_inst + list_y_inst_out_offset[i]
                else:
                    # y_inst = list_y_track_bot[2-i] + self.bend_radius * 2 - min(list_y_inst_in_offset[i],list_y_inst_out_offset[i])
                    y_inst = list_y_track_top[1] - self.track_pitch * i - max(list_y_inst_in_offset[i],list_y_inst_out_offset[i])
                    list_y_inst_in[i] = y_inst + list_y_inst_in_offset[i]
                    list_y_inst_out[i] = y_inst + list_y_inst_out_offset[i]
                self.inst_list.append(
                    self.add_instance(
                        master=self.master_list[i],
                        loc=(self.x_instance[i], y_inst),
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
                        (list_x_port_inst_in[0] - self.bend_radius * (i + 3),
                         list_y_track_bot[-1-i] + self.bend_radius),
                        (list_x_port_inst_in[i] - self.bend_radius * 4,
                         list_y_track_bot[-1-i]),
                    ]
                )
            else:
                in_router_path.extend(
                    [
                        (list_x_port_inst_in[i] - self.bend_radius * 4,
                         in_router_path[-1][1]),
                    ]
                )

            list_router_in_main[i].cardinal_router(in_router_path)
            list_router_in_main[i].add_fancy_s_bend(
                shift_left=self.inst_list[i][in_port_name].center[1]-list_router_in_main[i].y,
                length=self.bend_radius*4
            )


            out_router_path = []
            dy_out_bend = self.bend_radius if (i != 4) else -self.bend_radius
            list_router_out_main[i].cardinal_router(
                [(list_x_port_coupler_out[i] - self.bend_radius - dx_bend_extra,
                  y_port_coupler + dy_out_bend),
                 (list_x_port_inst_out[i] + self.bend_radius * 4,
                  list_y_router_path_out[i]),
                 ]
            )
            list_router_out_main[i].add_fancy_s_bend(
                shift_left=-self.inst_list[i][in_port_name].center[1]+list_router_out_main[i].y,
                length=self.bend_radius*4
            )

            # out_router_path.extend(
            #     [
            #         (list_x_port_coupler_out[i] - self.bend_radius - dx_bend_extra,
            #          y_port_coupler + dy_out_bend),
            #         (list_x_port_coupler_out[i] - self.bend_radius * 2 - dx_bend_extra,
            #          list_y_router_path_out[i]),
            #     ]
            # )
            # if i == 4:
            #     out_router_path.extend(
            #         [
            #             (list_x_port_inst_out[i] + self.bend_radius * 3,
            #              list_y_port_inst_bot[i] + self.bend_radius * 1),
            #             (list_x_port_inst_out[i] + self.bend_radius * 2,
            #              list_y_port_inst_bot[i] + self.bend_radius * 2),
            #             (list_x_port_inst_out[i] + self.bend_radius * 1,
            #              list_y_port_inst_bot[i] + self.bend_radius * 1),
            #             (list_x_port_inst_out[i] - self.bend_radius * 0,
            #              list_y_port_inst_bot[i] + self.bend_radius * 0),
            #         ]
            #     )
            # else:
            #     out_router_path.extend(
            #         [
            #             (list_x_port_inst_out[i] + self.bend_radius * 1,
            #              list_y_port_inst_bot[i] + self.bend_radius * 1),
            #             (list_x_port_inst_out[i] - self.bend_radius * 0,
            #              list_y_port_inst_bot[i] + self.bend_radius * 0),
            #         ]
            #     )
            # list_router_out_main[i].cardinal_router(out_router_path)







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


class TripleRingRowV1(PhotonicTemplateBase):
    """
    Photonic Ports:
    IN = left side
    OUT = right side
    """

    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)
        self.params = params

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

        self.bend_radius = self.photonic_tech_info.get_default_wg_params(self.wg_routing_layer)['radius'] + 0.002
        self.routing_width = self.photonic_tech_info.get_default_wg_params(self.wg_routing_layer)['width']

    @classmethod
    def get_params_info(cls):
        return dict(
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


        )

    @classmethod
    def get_default_param_values(cls):
        return dict(
        )

    def adjust_location(self, loc, rotation):
        if rotation == 'R0':
            return ( loc[0],  loc[1])
        elif rotation == 'R90':
            return (-loc[1],  loc[0])
        elif rotation == 'R180':
            return (-loc[0], -loc[1])
        elif rotation == 'R270':
            return ( loc[1], -loc[0])
        elif rotation == 'MX':
            return ( loc[0], -loc[1])
        elif rotation == 'MY':
            return (-loc[0],  loc[1])
        elif rotation == 'MXR90':
            return ( loc[1],  loc[0])
        else:
            return (-loc[1], -loc[0])


    def adjust_rotation_and_location(self, bound_box, loc_in, loc_out):
        loc_center = ((bound_box.left+bound_box.right)/2.0,
                      (bound_box.top+bound_box.bottom)/2.0)
        if loc_out[1] == loc_in[1]:
            # R0, R180, MX or MY
            if loc_out[0] > loc_in[0]:
                # no need to do MY related thing
                loc_in_extend = (bound_box.left, loc_in[1])
                loc_out_extend = (bound_box.right, loc_out[1])
                if loc_out[1] <= loc_center[1]:
                    rotation = 'R0'
                else:
                    rotation = 'MX'
            else:
                # need to MY
                loc_in_extend = (bound_box.right, loc_in[1])
                loc_out_extend = (bound_box.left, loc_out[1])
                if loc_out[1] <= loc_center[1]:
                    rotation = 'MY'
                else:
                    rotation = 'R180'
        else:
            # R90, R270, MXR90 or MYR90
            if loc_out[1] > loc_in[1]:
                loc_in_extend = (loc_in[0], bound_box.bottom)
                loc_out_extend = (loc_out[0], bound_box.top)
                # no need to do MY related thing
                if loc_out[0] >= loc_center[0]:
                    rotation = 'R270'
                else:
                    rotation = 'MXR90'
            else:
                # need to MY
                loc_in_extend = (loc_in[0], bound_box.top)
                loc_out_extend = (loc_out[0], bound_box.bottom)
                if loc_out[0] >= loc_center[0]:
                    rotation = 'MYR90'
                else:
                    rotation = 'R90'
        loc_in_adj = self.adjust_location(loc_in, rotation)
        loc_out_adj = self.adjust_location(loc_out, rotation)
        loc_in_extend_adj = self.adjust_location(loc_in_extend, rotation)
        loc_out_extend_adj = self.adjust_location(loc_out_extend, rotation)
        return rotation, loc_in_adj, loc_out_adj, loc_in_extend_adj, loc_out_extend_adj



    def draw_layout(self):

        # instantiate the ring modulator masters
        list_inst_direction = []
        list_dx_inst = []
        # list_dy_inst = []
        list_x_inst_in_offset = []
        list_x_inst_out_offset = []
        list_x_inst_in_extend_offset = []
        list_x_inst_out_extend_offset = []
        list_y_inst_port_offset = []

        in_port_name = 'PORT0'
        out_port_name = 'PORT1'
        for ind, yaml_tuple in enumerate(self.yaml_list):
            yaml_file = yaml_tuple[0]
            yaml_direction = yaml_tuple[1]
            if yaml_file != 'VOID':
                with open(yaml_file, 'r') as f:
                    yaml_content = yaml.load(f)

                lay_module = importlib.import_module(yaml_content['layout_package'])
                temp_cls = getattr(lay_module, yaml_content['layout_class'])

                master = self.new_template(params=yaml_content['layout_params'],
                                           temp_cls=temp_cls)
                # dsadada


                master_in_port_loc = master.get_photonic_port(in_port_name).center
                master_out_port_loc = master.get_photonic_port(out_port_name).center

                rotation, loc_in_adj, loc_out_adj, loc_in_extend_adj, loc_out_extend_adj = \
                    self.adjust_rotation_and_location(master.bound_box, master_in_port_loc, master_out_port_loc)

                # dx_inst_origin = abs(master_in_port_loc[0] - master_out_port_loc[0])
                # dy_inst_origin = abs(master_in_port_loc[1] - master_out_port_loc[1])

                self.master_list.append(master)
                list_inst_direction.append(rotation)
                list_y_inst_port_offset.append(loc_in_adj[1])
                list_x_inst_in_offset.append(loc_in_adj[0])
                list_x_inst_out_offset.append(loc_out_adj[0])
                list_x_inst_in_extend_offset.append(loc_in_extend_adj[0])
                list_x_inst_out_extend_offset.append(loc_out_extend_adj[0])
                list_dx_inst.append(loc_out_extend_adj[0] - loc_in_extend_adj[0])
                # if (yaml_direction == 'MXR90'):
                #
                #     # list_inst_direction.append('MXR90')
                #     list_dx_inst.append(dy_inst_origin)
                #     list_x_inst_in_offset.append(master_in_port_loc[1] * -1.0)
                #     list_y_inst_port_offset.append(master_in_port_loc[0] * -1.0)
                # elif (yaml_direction == 'MX'):
                #     # list_inst_direction.append('MX')
                #     list_dx_inst.append(dx_inst_origin)
                #     list_x_inst_in_offset.append(master_in_port_loc[0] * 1.0)
                #     list_y_inst_port_offset.append(master_in_port_loc[1] * -1.0)
                # else :
                #     # list_inst_direction.append('R0')
                #     list_dx_inst.append(dx_inst_origin)
                #     list_x_inst_in_offset.append(master_in_port_loc[0] * 1.0)
                #     list_y_inst_port_offset.append(master_in_port_loc[1] * 1.0)

                if ind==1:
                    print('PRINT', master, rotation, loc_in_adj)
            else:
                self.master_list.append([])
                list_inst_direction.append('R0')
                list_y_inst_port_offset.append(0)
                list_x_inst_in_offset.append(0)
                list_x_inst_out_offset.append(0)
                list_x_inst_in_extend_offset.append(0)
                list_x_inst_out_extend_offset.append(0)
                list_dx_inst.append(0)
                # list_dx_inst.append(0)
                # list_x_inst_in_offset.append(0)
                # list_y_inst_port_offset.append(0)
                # list_inst_direction.append('MX')



        n_site = 3
        #### define coupler port positions
        list_idx_port_coupler_in = [0, 1, 2]
        list_idx_port_coupler_out = [1, 0, 2]
        list_x_port_coupler_in = [
            self.x_port_coupler_in_base + list_idx_port_coupler_in[i] * self.x_coupler_pitch for i in range(0, n_site)
        ]
        list_x_port_coupler_out = [
            self.x_port_coupler_out_base + list_idx_port_coupler_out[i] * self.x_coupler_pitch for i in range(0, n_site)
        ]
        list_y_port_coupler = [
            self.y_port_coupler_base + i * self.y_coupler_pitch for i in range(0, 2)
        ]


        # x_coupler_port_in = self.x_coupler_port_in_base + [0, ]
        # y_coupler_port = self.y_coupler_port
        # dx_inst_port_min = self.dx_inst_port_min
        # dy_inst_port_min = self.dy_inst_port_min
        list_x_port_inst_in = [self.x_instance[i] + list_x_inst_in_offset[i] for i in range(0, n_site)]
        list_x_port_inst_out = [self.x_instance[i] + list_x_inst_out_offset[i] for i in range(0, n_site)]
        list_x_port_inst_in_extend = [self.x_instance[i] + list_x_inst_in_extend_offset[i] for i in range(0, n_site)]
        list_x_port_inst_out_extend = [self.x_instance[i] + list_x_inst_out_extend_offset[i] for i in range(0, n_site)]


        # y_track_inst_bot = 3 * self.track_pitch
        # y_track_inst_top_min = y_track_inst_bot + dy_inst_port_min

        # 4 long horizontal waveguide tracks on the bottom side of the instances
        list_y_track_bot = [self.track_pitch * (i+1) for i in range(0, 5)]
        # horizontal track the bottom ports of the instances are on
        y_port_inst_bot = list_y_track_bot[4] + self.dy_port_inst_bot

        # check if these positions are appropriate
        if (list_x_port_coupler_in[0] < self.x_coupler_clear):
            raise ValueError('Input Coupler x coordinate is too low')
        if (list_y_port_coupler[0] < list_y_track_bot[1] + self.track_pitch + self.y_coupler_clear / 2):
            raise ValueError('Coupler y coordinate is too low, will conflict with waveguide routing')


        # 7 long horizontal waveguide tracks on the top side of the instances
        y_track_top_min = max(list_y_port_coupler[1] + self.track_pitch + self.y_coupler_clear / 2,
                              list_y_track_bot[4] + self.dy_inst + self.track_pitch * 1)
        list_y_track_top = [i * self.track_pitch + y_track_top_min for i in range(0, 4)]
        y_port_inst_top = list_y_track_top[3]
        y_port_inst_top = list_y_track_bot[4] + self.dy_port_inst_top


        # flag to trigger special routing because large bend radius
        flag_sp_routing_1 = (list_y_port_coupler[0] - list_y_track_bot[0]) < self.bend_radius * 2
        flag_sp_routing_2 = self.track_pitch * 2 < self.bend_radius * 2
        flag_sp_routing_3 = self.track_pitch * 4 < self.bend_radius * 2

        # instantiate the frating couplers
        list_gc_in_main = [
            self.add_instance(
                master=self.gc_master,
                loc=(list_x_port_coupler_in[i],
                     list_y_port_coupler[0]),
                # Offset site by location of input port, to put input port at desired location
                orient='R0',
            )
        for i in range(0, n_site)]
        list_gc_in_drop = [
            self.add_instance(
                master=self.gc_master,
                loc=(list_x_port_coupler_in[i],
                     list_y_port_coupler[1]),
                # Offset site by location of input port, to put input port at desired location
                orient='R0',
            )
        for i in range(0, n_site)]
        list_gc_out_main = [
            self.add_instance(
                master=self.gc_master,
                loc=(list_x_port_coupler_out[i],
                     list_y_port_coupler[0]),
                # Offset site by location of input port, to put input port at desired location
                orient='MY',
            )
        for i in range(0, n_site)]
        list_gc_out_drop = [
            self.add_instance(
                master=self.gc_master,
                loc=(list_x_port_coupler_out[i],
                     list_y_port_coupler[1]),
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
                        loc=(self.x_instance[i], y_port_inst_bot - list_y_inst_port_offset[i]),
                        orient=list_inst_direction[i],
                    )
                )



        list_port_in_main = [
            self.add_photonic_port(
                name=f'IN_MAIN{i}',
                center=(list_x_port_coupler_in[i], list_y_port_coupler[0]),
                orient='R0',
                layer=self.wg_port_layer,
                width=self.routing_width
            )
            for i in range(0, n_site)
        ]
        list_port_in_drop = [
            self.add_photonic_port(
                name=f'IN_DROP{i}',
                center=(list_x_port_coupler_in[i], list_y_port_coupler[1]),
                orient='R0',
                layer=self.wg_port_layer,
                width=self.routing_width
            )

            for i in range(0, n_site)
        ]
        list_port_out_main = [
            self.add_photonic_port(
                name=f'OUT_MAIN{i}',
                center=(list_x_port_coupler_out[i], list_y_port_coupler[0]),
                orient='R0',
                layer=self.wg_port_layer,
                width=self.routing_width
            )
            for i in range(0, n_site)
        ]
        list_port_out_drop = [
            self.add_photonic_port(
                name=f'OUT_DROP{i}',
                center=(list_x_port_coupler_out[i], list_y_port_coupler[1]),
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
        list_router_in_drop = [
            WgRouter(
                self,
                list_port_in_drop[i],
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
        list_router_out_drop = [
            WgRouter(
                self,
                list_port_out_drop[i],
                self.wg_routing_layer,
                route_in_port_dir=False
            )
            for i in range(0, n_site)
        ]


        #### site 0
        idx_now = 0

        list_router_in_main[idx_now].cardinal_router(
            [
                (list_x_port_coupler_in[idx_now] + self.bend_radius * 1 + self.track_pitch,
                 list_y_port_coupler[0] + self.bend_radius * 1),
                (list_x_port_inst_in_extend[idx_now] - self.bend_radius * 4 - self.track_pitch,
                 list_y_track_top[2]),
                (list_x_port_inst_in_extend[idx_now] - self.bend_radius * 3 - self.track_pitch,
                 y_port_inst_bot + self.bend_radius * 1),
                (list_x_port_inst_in[idx_now],
                 y_port_inst_bot),
            ]
        )
        list_router_in_drop[idx_now].cardinal_router(
            [
                (list_x_port_coupler_in[idx_now] + self.bend_radius * 1,
                 list_y_port_coupler[1] + self.bend_radius * 1),
                (list_x_port_inst_in_extend[idx_now] - self.bend_radius * 4,
                 list_y_track_top[3]),
                # (list_x_port_inst_in[idx_now] - self.bend_radius * 3,
                #  y_port_inst_top - self.bend_radius * 1),
                # (list_x_port_inst_in[idx_now] - self.bend_radius * 2,
                #  y_port_inst_top - self.bend_radius * 2),
                (list_x_port_inst_in_extend[idx_now] - self.bend_radius * 1,
                 y_port_inst_top + self.bend_radius * 1),
                (list_x_port_inst_in[idx_now],
                 y_port_inst_top),
            ]
        )


        list_router_out_main[idx_now].cardinal_router(
            [
                (list_x_port_coupler_out[idx_now] - self.bend_radius * 1 - self.track_pitch,
                 list_y_port_coupler[0] + self.bend_radius),
                (list_x_port_coupler_out[idx_now] - self.bend_radius * 2 - self.track_pitch,
                 list_y_track_top[2]),
                (list_x_port_inst_out_extend[idx_now] + self.bend_radius * 3 + self.track_pitch,
                 list_y_track_bot[4] + self.bend_radius),
                (list_x_port_inst_out[idx_now],
                 y_port_inst_bot),
            ]
        )

        router_path = [
            (list_x_port_coupler_out[idx_now] - self.bend_radius * 1,
             list_y_port_coupler[1] + self.bend_radius),
            (list_x_port_coupler_out[idx_now] - self.bend_radius * 2,
             list_y_track_top[3]),
        ] + ([
            (list_x_port_inst_out_extend[idx_now] + self.bend_radius * 3,
             y_port_inst_top - self.bend_radius * 1),
            (list_x_port_inst_out_extend[idx_now] + self.bend_radius * 2,
             y_port_inst_top - self.bend_radius * 2),
            (list_x_port_inst_out_extend[idx_now] + self.bend_radius * 1,
             y_port_inst_top - self.bend_radius * 1),
            (list_x_port_inst_out_extend[idx_now],
             y_port_inst_top),
        ] if flag_sp_routing_3 else [
            (list_x_port_inst_out_extend[idx_now] + self.bend_radius * 1,
             y_port_inst_top + self.bend_radius * 1),
            (list_x_port_inst_out[idx_now],
             y_port_inst_top),
        ])

        list_router_out_drop[idx_now].cardinal_router(router_path)



        #### site 1
        idx_now = 1

        router_path = [
            (list_x_port_coupler_in[idx_now] + self.bend_radius * 1 + self.track_pitch,
             list_y_port_coupler[0] + self.bend_radius * 1),
            (list_x_port_coupler_in[idx_now+1] + self.bend_radius * 3 + self.track_pitch,
             list_y_track_top[0]),
            (list_x_port_coupler_in[idx_now + 1] + self.bend_radius * 4 + self.track_pitch,
             list_y_track_top[0] - self.bend_radius * 1),
            (list_x_port_inst_in_extend[idx_now] - self.bend_radius * 4,
             list_y_track_bot[2]),
        ] + ([
            (list_x_port_inst_in_extend[idx_now] - self.bend_radius * 3,
             y_port_inst_bot + self.bend_radius * 1),
            (list_x_port_inst_in_extend[idx_now] - self.bend_radius * 2,
             y_port_inst_bot + self.bend_radius * 2),
            (list_x_port_inst_in_extend[idx_now] - self.bend_radius * 1,
             y_port_inst_bot + self.bend_radius * 1),
            (list_x_port_inst_in[idx_now],
             y_port_inst_bot),
        ] if flag_sp_routing_2 else [
            (list_x_port_inst_in_extend[idx_now] - self.bend_radius * 1,
             y_port_inst_bot - self.bend_radius * 1),
            (list_x_port_inst_in[idx_now],
             y_port_inst_bot),

        ])

        list_router_in_main[idx_now].cardinal_router(router_path)


        list_router_in_drop[idx_now].cardinal_router(
            [
                (list_x_port_coupler_in[idx_now] + self.bend_radius * 1,
                 list_y_port_coupler[1] + self.bend_radius * 1),
                (list_x_port_coupler_in[idx_now + 1] + self.bend_radius * 3 + self.track_pitch * 2,
                 list_y_track_top[1]),
                (list_x_port_coupler_in[idx_now + 1] + self.bend_radius * 4 + self.track_pitch * 2,
                 list_y_track_top[0] - self.bend_radius * 1),
                (list_x_port_inst_in_extend[idx_now] - self.bend_radius * 4 - self.track_pitch,
                 list_y_track_bot[3]),
                (list_x_port_inst_in_extend[idx_now] - self.bend_radius * 3 - self.track_pitch,
                 list_y_track_bot[3] + self.bend_radius),
                (list_x_port_inst_in[idx_now],
                 y_port_inst_top),
            ]
        )



        list_router_out_main[idx_now].cardinal_router([
            (list_x_port_coupler_out[idx_now] - self.bend_radius * 1 - self.track_pitch,
             list_y_port_coupler[0] + self.bend_radius),
            (list_x_port_coupler_out[idx_now] - self.bend_radius * 2 - self.track_pitch,
             list_y_track_top[0]),
            (list_x_port_inst_out_extend[idx_now] + self.bend_radius * 3 + self.track_pitch,
             list_y_track_bot[4] - self.bend_radius),
            (list_x_port_inst_out[idx_now],
             y_port_inst_bot),
        ])

        router_path = [
            (list_x_port_coupler_out[idx_now] - self.bend_radius * 1,
             list_y_port_coupler[1] + self.bend_radius),
            (list_x_port_coupler_out[idx_now] - self.bend_radius * 2,
             list_y_track_top[1]),
        ] + ([
            (list_x_port_inst_out_extend[idx_now] + self.bend_radius * 3,
             y_port_inst_top - self.bend_radius * 1),
            (list_x_port_inst_out_extend[idx_now] + self.bend_radius * 2,
             y_port_inst_top - self.bend_radius * 2),
            (list_x_port_inst_out_extend[idx_now] + self.bend_radius * 1,
             y_port_inst_top - self.bend_radius * 1),
            (list_x_port_inst_out[idx_now],
             y_port_inst_top),
        ] if flag_sp_routing_2 else [
            (list_x_port_inst_out_extend[idx_now] + self.bend_radius * 1,
             y_port_inst_top + self.bend_radius * 1),
            (list_x_port_inst_out[idx_now],
             y_port_inst_top),
        ])

        list_router_out_drop[idx_now].cardinal_router(router_path)

        #### site 2
        idx_now = 2

        router_path = ([
            (list_x_port_coupler_in[idx_now] + self.bend_radius * 1,
             list_y_port_coupler[0] + self.bend_radius * 1),
            (list_x_port_coupler_in[idx_now] + self.bend_radius * 2,
             list_y_port_coupler[0] + self.bend_radius * 2),
            (list_x_port_coupler_in[idx_now] + self.bend_radius * 3,
             list_y_port_coupler[0] + self.bend_radius * 1),
        ] if flag_sp_routing_1 else [
            (list_x_port_coupler_in[idx_now] + self.bend_radius * 1,
             list_y_port_coupler[0] - self.bend_radius * 1),
        ]) + [
            (list_x_port_inst_in_extend[idx_now] - self.bend_radius * 4,
             list_y_track_bot[0])
        ] +  ([
            (list_x_port_inst_in_extend[idx_now] - self.bend_radius * 3,
             list_y_track_bot[0] + self.bend_radius * 1),
            (list_x_port_inst_in_extend[idx_now] - self.bend_radius * 2,
             y_port_inst_bot + self.bend_radius * 2),
            (list_x_port_inst_in_extend[idx_now] - self.bend_radius * 1,
             y_port_inst_bot + self.bend_radius * 1),
            (list_x_port_inst_in[idx_now],
             y_port_inst_bot),
        ] if flag_sp_routing_3 else [
            (list_x_port_inst_in_extend[idx_now] - self.bend_radius * 1,
             y_port_inst_bot - self.bend_radius * 1),
            (list_x_port_inst_in[idx_now],
             y_port_inst_bot),
        ])

        list_router_in_main[idx_now].cardinal_router(router_path)


        list_router_in_drop[idx_now].cardinal_router(
            [
                (list_x_port_coupler_in[idx_now] + self.bend_radius * 1 + self.track_pitch,
                 list_y_port_coupler[0] - self.bend_radius * 1),
                (list_x_port_inst_in_extend[idx_now] - self.bend_radius * 4 - self.track_pitch,
                 list_y_track_bot[1]),
                (list_x_port_inst_in_extend[idx_now] - self.bend_radius * 3 - self.track_pitch,
                 y_port_inst_top - self.bend_radius * 1),
                (list_x_port_inst_in[idx_now],
                 y_port_inst_top),
            ]
        )

        router_path = ([
            (list_x_port_coupler_out[idx_now] - self.bend_radius * 1,
             list_y_port_coupler[0] + self.bend_radius * 1),
            (list_x_port_coupler_out[idx_now] - self.bend_radius * 2,
             list_y_port_coupler[0] + self.bend_radius * 2),
            (list_x_port_coupler_out[idx_now] - self.bend_radius * 3,
             list_y_port_coupler[0] + self.bend_radius * 1),
        ] if flag_sp_routing_1 else [
            (list_x_port_coupler_out[idx_now] - self.bend_radius * 1,
             list_y_port_coupler[0] - self.bend_radius * 1),
        ]) + [
            (list_x_port_inst_out_extend[idx_now] + self.bend_radius * 4,
             list_y_track_bot[0])
        ] +  ([
            (list_x_port_inst_out_extend[idx_now] + self.bend_radius * 3,
             list_y_track_bot[0] + self.bend_radius * 1),
            (list_x_port_inst_out_extend[idx_now] + self.bend_radius * 2,
             y_port_inst_bot + self.bend_radius * 2),
            (list_x_port_inst_out_extend[idx_now] + self.bend_radius * 1,
             y_port_inst_bot + self.bend_radius * 1),
            (list_x_port_inst_out[idx_now],
             y_port_inst_bot),
        ] if flag_sp_routing_3 else [
            (list_x_port_inst_out_extend[idx_now] + self.bend_radius * 1,
             y_port_inst_bot - self.bend_radius),
            (list_x_port_inst_out[idx_now],
             y_port_inst_bot),
        ])


        list_router_out_main[idx_now].cardinal_router(router_path)


        list_router_out_drop[idx_now].cardinal_router(
            [
                (list_x_port_coupler_out[idx_now] - self.bend_radius * 1 - self.track_pitch,
                 list_y_port_coupler[0] - self.bend_radius * 1),
                (list_x_port_inst_out_extend[idx_now] + self.bend_radius * 4 + self.track_pitch,
                 list_y_track_bot[1]),
                (list_x_port_inst_out_extend[idx_now] + self.bend_radius * 3 + self.track_pitch,
                 y_port_inst_top - self.bend_radius * 1),
                (list_x_port_inst_out[idx_now],
                 y_port_inst_top),
            ]
        )


class TripleRingRowWithLNA(PhotonicTemplateBase):
    """
    Photonic Ports:
    IN = left side
    OUT = right side
    """

    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)
        self.params = params

        for key, val in self.params.items():  # Automatically unpack variables
            # exec( "self.{} = {}".format( key, val ) )
            exec(f"self.{key} = {val!r}")

        if self.with_drop_ports:
            self.track_pitch_mod = self.track_pitch
            self.y_coupler_pitch_mod = self.y_coupler_pitch
        else:
            self.track_pitch_mod = self.track_pitch / 2
            self.y_coupler_pitch_mod = self.y_coupler_pitch / 2

        # ================================================================
        # Create all templates (may need them to get geometry parameters)
        # ================================================================

        # Create class of each device component
        gc_module = importlib.import_module(self.grating_coupler_module)
        gc_class = getattr(gc_module, self.grating_coupler_class)
        self.gc_master = self.new_template(params=None, temp_cls=gc_class)
        # self.gc_array_inst = [None] * self.grating_coupler_num

        self.bend_radius = self.photonic_tech_info.get_default_wg_params(self.wg_routing_layer)['radius'] + 2
        self.routing_width = self.photonic_tech_info.get_default_wg_params(self.wg_routing_layer)['width']

    @classmethod
    def get_params_info(cls):
        return dict(

            grating_coupler_module=None,
            grating_coupler_class=None,


        )

    @classmethod
    def get_default_param_values(cls):
        return dict(
        )

    def adjust_location(self, loc, rotation):
        if rotation == 'R0':
            return ( loc[0],  loc[1])
        elif rotation == 'R90':
            return (-loc[1],  loc[0])
        elif rotation == 'R180':
            return (-loc[0], -loc[1])
        elif rotation == 'R270':
            return ( loc[1], -loc[0])
        elif rotation == 'MX':
            return ( loc[0], -loc[1])
        elif rotation == 'MY':
            return (-loc[0],  loc[1])
        elif rotation == 'MXR90':
            return ( loc[1],  loc[0])
        else:
            return (-loc[1], -loc[0])


    def adjust_rotation_and_location(self, bound_box, loc_in, loc_out):
        loc_center = ((bound_box.left+bound_box.right)/2.0,
                      (bound_box.top+bound_box.bottom)/2.0)
        if loc_out[1] == loc_in[1]:
            # R0, R180, MX or MY
            if loc_out[0] > loc_in[0]:
                # no need to do MY related thing
                loc_in_extend = (bound_box.left, loc_in[1])
                loc_out_extend = (bound_box.right, loc_out[1])
                if loc_out[1] <= loc_center[1]:
                    rotation = 'R0'
                else:
                    rotation = 'MX'
            else:
                # need to MY
                loc_in_extend = (bound_box.right, loc_in[1])
                loc_out_extend = (bound_box.left, loc_out[1])
                if loc_out[1] <= loc_center[1]:
                    rotation = 'MY'
                else:
                    rotation = 'R180'
        else:
            # R90, R270, MXR90 or MYR90
            if loc_out[1] > loc_in[1]:
                loc_in_extend = (loc_in[0], bound_box.bottom)
                loc_out_extend = (loc_out[0], bound_box.top)
                # no need to do MY related thing
                if loc_out[0] >= loc_center[0]:
                    rotation = 'R270'
                else:
                    rotation = 'MXR90'
            else:
                # need to MY
                loc_in_extend = (loc_in[0], bound_box.top)
                loc_out_extend = (loc_out[0], bound_box.bottom)
                if loc_out[0] >= loc_center[0]:
                    rotation = 'MYR90'
                else:
                    rotation = 'R90'
        loc_in_adj = self.adjust_location(loc_in, rotation)
        loc_out_adj = self.adjust_location(loc_out, rotation)
        loc_in_extend_adj = self.adjust_location(loc_in_extend, rotation)
        loc_out_extend_adj = self.adjust_location(loc_out_extend, rotation)
        loc_in_extend_adj = self.adjust_location(loc_in, rotation)
        loc_out_extend_adj = self.adjust_location(loc_out, rotation)
        return rotation, loc_in_adj, loc_out_adj, loc_in_extend_adj, loc_out_extend_adj

    def adjust_rotation_and_location_from_master(self, master, in_port_name, out_port_name):
        port_in = master.get_photonic_port(in_port_name)
        port_out = master.get_photonic_port(out_port_name)
        # gdad
        loc_in = port_in.center
        loc_out = port_out.center
        bound_box = master.bound_box
        loc_center = ((bound_box.left+bound_box.right)/2.0,
                      (bound_box.top+bound_box.bottom)/2.0)
        print(port_in.angle, abs((port_in.angle+180)%180 - 90))
        if (abs(port_in.angle) < 1e-3) or (abs(port_in.angle-np.pi) < 1e-3):
            # R0, R180, MX or MY
            if loc_out[0] > loc_in[0]:
                # no need to do MY related thing
                loc_in_extend = (bound_box.left, loc_in[1])
                loc_out_extend = (bound_box.right, loc_out[1])
                if loc_out[1] <= loc_center[1]:
                    rotation = 'R0'
                else:
                    rotation = 'MX'
            else:
                # need to MY
                loc_in_extend = (bound_box.right, loc_in[1])
                loc_out_extend = (bound_box.left, loc_out[1])
                if loc_out[1] <= loc_center[1]:
                    rotation = 'MY'
                else:
                    rotation = 'R180'
        else:
            # R90, R270, MXR90 or MYR90
            if loc_out[1] > loc_in[1]:
                loc_in_extend = (loc_in[0], bound_box.bottom)
                loc_out_extend = (loc_out[0], bound_box.top)
                # no need to do MY related thing
                if loc_out[0] >= loc_center[0]:
                    rotation = 'R270'
                else:
                    rotation = 'MXR90'
            else:
                # need to MY
                loc_in_extend = (loc_in[0], bound_box.top)
                loc_out_extend = (loc_out[0], bound_box.bottom)
                if loc_out[0] >= loc_center[0]:
                    rotation = 'MYR90'
                else:
                    rotation = 'R90'
        loc_in_adj = self.adjust_location(loc_in, rotation)
        loc_out_adj = self.adjust_location(loc_out, rotation)
        loc_in_extend_adj = self.adjust_location(loc_in_extend, rotation)
        loc_out_extend_adj = self.adjust_location(loc_out_extend, rotation)
        loc_in_extend_adj = self.adjust_location(loc_in, rotation)
        loc_out_extend_adj = self.adjust_location(loc_out, rotation)
        return rotation, loc_in_adj, loc_out_adj, loc_in_extend_adj, loc_out_extend_adj


    def draw_layout(self):

        self.get_site_specs()
        self.get_inst_and_track_locations()
        self.place_instances()
        self.create_ports()
        self.wg_routing()


    def get_site_specs(self):
        # instantiate the ring modulator masters
        self.list_inst_direction = []
        self.list_dx_inst = []
        # list_dy_inst = []
        self.list_x_inst_in_offset = []
        self.list_x_inst_out_offset = []
        self.list_x_inst_in_extend_offset = []
        self.list_x_inst_out_extend_offset = []
        self.list_y_inst_in_offset = []
        self.list_y_inst_out_offset = []
        self.master_list = []
        self.in_port_name = 'PORT0'
        self.out_port_name = 'PORT1'

        in_port_name = 'PORT0'
        out_port_name = 'PORT1'
        for ind, yaml_tuple in enumerate(self.yaml_list):
            yaml_file = yaml_tuple[0]
            yaml_direction = yaml_tuple[1]
            if yaml_file != 'VOID':
                with open(yaml_file, 'r') as f:
                    yaml_content = yaml.load(f)

                lay_module = importlib.import_module(yaml_content['layout_package'])
                temp_cls = getattr(lay_module, yaml_content['layout_class'])

                master = self.new_template(params=yaml_content['layout_params'],
                                           temp_cls=temp_cls)

                master_in_port_loc = master.get_photonic_port(in_port_name).center
                master_out_port_loc = master.get_photonic_port(out_port_name).center

                rotation, loc_in_adj, loc_out_adj, loc_in_extend_adj, loc_out_extend_adj = \
                    self.adjust_rotation_and_location(master.bound_box, master_in_port_loc, master_out_port_loc)
                rotation_old, loc_in_adj_old, loc_out_adj_old, loc_in_extend_adj_old, loc_out_extend_adj_old = \
                    rotation, loc_in_adj, loc_out_adj, loc_in_extend_adj, loc_out_extend_adj

                rotation, loc_in_adj, loc_out_adj, loc_in_extend_adj, loc_out_extend_adj = \
                    self.adjust_rotation_and_location_from_master(master, in_port_name, out_port_name)
                print('COMPARE (old):', ind, rotation_old, loc_in_adj_old, loc_out_adj_old, loc_in_extend_adj_old, loc_out_extend_adj_old)

                print('COMPARE (new):', ind, rotation, loc_in_adj, loc_out_adj, loc_in_extend_adj, loc_out_extend_adj)
                self.master_list.append(master)
                self.list_inst_direction.append(rotation)
                self.list_y_inst_in_offset.append(loc_in_adj[1])
                self.list_y_inst_out_offset.append(loc_out_adj[1])
                self.list_x_inst_in_offset.append(loc_in_adj[0])
                self.list_x_inst_out_offset.append(loc_out_adj[0])
                self.list_x_inst_in_extend_offset.append(loc_in_extend_adj[0])
                self.list_x_inst_out_extend_offset.append(loc_out_extend_adj[0])
                self.list_dx_inst.append(loc_out_extend_adj[0] - loc_in_extend_adj[0])

                if ind==1:
                    print('PRINT', master, rotation, loc_in_adj)
            else:
                self.master_list.append([])
                self.list_inst_direction.append('R0')
                self.list_y_inst_in_offset.append(0)
                self.list_y_inst_out_offset.append(0)
                self.list_x_inst_in_offset.append(0)
                self.list_x_inst_out_offset.append(0)
                self.list_x_inst_in_extend_offset.append(0)
                self.list_x_inst_out_extend_offset.append(0)
                self.list_dx_inst.append(0)

    def get_inst_and_track_locations(self):

        self.n_site = 9
        x_port_coupler_in_base = self.x_port_coupler_in_base
        x_port_coupler_out_base = self.dx_design - x_port_coupler_in_base - self.x_coupler_pitch * 2

        #### define index of coupler port positions from left to right, the i-th element is
        #### the index of coupler port position of the i-th site
        list_idx_x_port_coupler_in = [0, 0, 1, 1, 2, 2, 0, 1, 2]
        list_idx_x_port_coupler_out = [1, 1, 0, 0, 2, 2, 1, 0, 2]
        list_idx_y_port_coupler = [1, 0, 0, 1, 0, 1, 0, 0, 0]

        # define coupler port coordinates
        self.list_x_port_coupler_in = [
            x_port_coupler_in_base +
            list_idx_x_port_coupler_in[i] * self.x_coupler_pitch for i in range(0, self.n_site)
        ]
        self.list_x_port_coupler_out = [
            x_port_coupler_out_base +
            list_idx_x_port_coupler_out[i] * self.x_coupler_pitch for i in range(0, self.n_site)
        ]
        self.list_y_port_coupler_main = [
            (self.y_port_coupler_base[0] if (i <= 5) else self.y_port_coupler_base[1]) +
            list_idx_y_port_coupler[i] * self.y_coupler_pitch_mod * 2 for i in range(0, self.n_site)
        ]
        self.list_y_port_coupler_drop = [
            self.list_y_port_coupler_main[i] + self.y_coupler_pitch_mod for i in range(0, self.n_site)
        ]


        #### define port locations for modulators
        # self.list_x_port_inst_in = [self.x_instance[i] - self.list_dx_inst[i] / 2 for i in range(0, self.n_site)]
        # self.list_x_port_inst_out = [self.x_instance[i] + self.list_dx_inst[i] / 2 for i in range(0, self.n_site)]

        self.list_x_port_inst_in = [self.x_instance[i] + self.list_x_inst_in_offset[i] for i in range(0, self.n_site)]
        self.list_x_port_inst_out = [self.x_instance[i] + self.list_x_inst_out_offset[i] for i in range(0, self.n_site)]
        self.list_x_port_inst_in_extend = [self.x_instance[i] + self.list_x_inst_in_extend_offset[i] for i in range(0, self.n_site)]
        self.list_x_port_inst_out_extend = [self.x_instance[i] + self.list_x_inst_out_extend_offset[i] for i in range(0, self.n_site)]
        # fsfsfesfse

        # TODO: modify
        # self.y_port_inst_bot_group2_base = 460
        self.y_port_inst_bot_group2 = self.y_port_inst_bot_group2_base + self.track_pitch_mod + self.dy_port_inst_bot
        self.y_port_inst_top_group2 = self.y_port_inst_bot_group2_base + self.track_pitch_mod + self.dy_port_inst_top


        # 10 long horizontal waveguide tracks on the bottom side of the group 0 instances
        self.list_y_track_bot_group1 = [self.y_track_bot_group1_min + self.track_pitch_mod * i for i in range(0, 10)]

        y_track_bot_group2_min = self.y_port_coupler_base[1] - self.y_coupler_clear / 2 - \
                                 self.track_pitch_mod * 2 - self.track_pitch
        self.list_y_track_bot_group2 = [y_track_bot_group2_min,
                                        y_track_bot_group2_min + self.track_pitch_mod]
        self.list_y_track_mid_group2 = [self.y_port_coupler_base[-1] + (self.y_coupler_pitch if self.with_drop_ports else 0) +
                                        self.y_coupler_clear / 2 + self.track_pitch + self.track_pitch_mod * i
                                        for i in range(0, 6)]

        # the horizontal track that the bottom ports of the instances are on
        self.y_port_inst_bot_group1 = self.list_y_track_bot_group1[-1] + self.track_pitch + self.dy_port_inst_bot
        self.y_port_inst_top_group1 = self.list_y_track_bot_group1[-1] + self.track_pitch + self.dy_port_inst_top


        # check if these positions are appropriate
        if (self.list_x_port_coupler_in[0] < self.x_coupler_clear):
            raise ValueError('Input Coupler x coordinate is too low')
        if (self.y_port_coupler_base[0] < self.list_y_track_bot_group1[-5] +
            self.track_pitch + self.y_coupler_clear / 2):
            raise ValueError('Coupler y coordinate is too low, will conflict with waveguide routing')


        # 10 long horizontal waveguide tracks on the top side of the instances
        y_track_top_group1_min = max((self.list_y_port_coupler_drop[5] if self.with_drop_ports else self.list_y_port_coupler_main[5]) +
                                      self.track_pitch + self.y_coupler_clear / 2 -
                                      self.track_pitch_mod * 6,
                                      self.list_y_track_bot_group1[-1] + self.dy_inst + self.track_pitch * 1)
        self.list_y_track_top_group1 = [i * self.track_pitch_mod + y_track_top_group1_min for i in range(0, 10)]

        self.list_y_track_top_group2 = [self.y_port_inst_bot_group2 + self.dy_inst +
                                        self.track_pitch_mod * i + self.track_pitch
                                        for i in range(0, 4)]

    def place_instances(self):
        # instantiate the grating couplers
        self.list_gc_in_main = [
            self.add_instance(
                master=self.gc_master,
                loc=(self.list_x_port_coupler_in[i],
                     self.list_y_port_coupler_main[i]),
                # Offset site by location of input port, to put input port at desired location
                orient='R0',
            )
        for i in range(0, self.n_site)]
        self.list_gc_out_main = [
            self.add_instance(
                master=self.gc_master,
                loc=(self.list_x_port_coupler_out[i],
                     self.list_y_port_coupler_main[i]),
                # Offset site by location of input port, to put input port at desired location
                orient='MY',
            )
        for i in range(0, self.n_site)]
        if self.with_drop_ports:
            self.list_gc_in_drop = [
                self.add_instance(
                    master=self.gc_master,
                    loc=(self.list_x_port_coupler_in[i],
                         self.list_y_port_coupler_drop[i]),
                    # Offset site by location of input port, to put input port at desired location
                    orient='R0',
                )
            for i in range(0, self.n_site)]
            self.list_gc_out_drop = [
                self.add_instance(
                    master=self.gc_master,
                    loc=(self.list_x_port_coupler_out[i],
                         self.list_y_port_coupler_drop[i]),
                    # Offset site by location of input port, to put input port at desired location
                    orient='MY',
                )
            for i in range(0, self.n_site)]


        in_port_name = 'PORT0'
        out_port_name = 'PORT1'
        list_y_inst_in = [0 for i in range(0, self.n_site)]
        list_y_inst_out = [0 for i in range(0, self.n_site)]


        # instantiate the rings
        for i in range(0, self.n_site):
            if i < 6:
                y_port_inst_bot = self.y_port_inst_bot_group1
                list_y_track_top = self.list_y_track_top_group1
                list_y_track_mid = self.list_y_track_bot_group1
            else:
                y_port_inst_bot = self.y_port_inst_bot_group2
                list_y_track_top = self.list_y_track_top_group2
                list_y_track_mid = self.list_y_track_mid_group2

            if self.list_dx_inst[i] != 0:
                master_in_port_loc = self.master_list[i].get_photonic_port(in_port_name).center
                y_inst_rotated = (list_y_track_top[-1] + list_y_track_mid[0]) / 2
                if self.list_y_inst_in_offset[i] == self.list_y_inst_out_offset[i]:
                    # y_inst = list_y_track_top[1] - self.track_pitch * i - self.bend_radius * 2 - list_y_inst_in_offset[i]
                    y_inst = list_y_track_mid[-1-(i%6)] + self.bend_radius * 2 - self.list_y_inst_in_offset[i%6]
                    list_y_inst_in[i] = y_inst + self.list_y_inst_in_offset[i]
                    list_y_inst_out[i] = y_inst + self.list_y_inst_out_offset[i]
                else:
                    # y_inst = list_y_track_bot[2-i] + self.bend_radius * 2 - min(list_y_inst_in_offset[i],list_y_inst_out_offset[i])
                    y_inst = list_y_track_top[1] - self.track_pitch * (i%6) - max(self.list_y_inst_in_offset[i],self.list_y_inst_out_offset[i])
                    list_y_inst_in[i] = y_inst + self.list_y_inst_in_offset[i]
                    list_y_inst_out[i] = y_inst + self.list_y_inst_out_offset[i]
                # if i==8:
                #     kdkd
                # print('i=', i, y_inst)
                y_inst = self.y_instance[0] if i < 6 else  self.y_instance[1]
                self.inst_list.append(
                    self.add_instance(
                        master=self.master_list[i],
                        # loc=(self.x_instance[i], y_port_inst_bot - list_y_inst_port_offset[i]),
                        loc=(self.x_instance[i], y_inst),
                        orient=self.list_inst_direction[i],
                    )

                )


    def create_ports(self):

        self.list_port_in_main = [
            self.add_photonic_port(
                name=f'IN_MAIN{i}',
                center=(self.list_x_port_coupler_in[i], self.list_y_port_coupler_main[i]),
                orient='R0',
                layer=self.wg_port_layer,
                width=self.routing_width
            )
            for i in range(0, self.n_site)
        ]
        self.list_port_out_main = [
            self.add_photonic_port(
                name=f'OUT_MAIN{i}',
                center=(self.list_x_port_coupler_out[i], self.list_y_port_coupler_main[i]),
                orient='R0',
                layer=self.wg_port_layer,
                width=self.routing_width
            )
            for i in range(0, self.n_site)
        ]
        if self.with_drop_ports:
            self.list_port_in_drop = [
                self.add_photonic_port(
                    name=f'IN_DROP{i}',
                    center=(self.list_x_port_coupler_in[i], self.list_y_port_coupler_drop[i]),
                    orient='R0',
                    layer=self.wg_port_layer,
                    width=self.routing_width
                )

                for i in range(0, self.n_site)
            ]
            self.list_port_out_drop = [
                self.add_photonic_port(
                    name=f'OUT_DROP{i}',
                    center=(self.list_x_port_coupler_out[i], self.list_y_port_coupler_drop[i]),
                    orient='R0',
                    layer=self.wg_port_layer,
                    width=self.routing_width
                )
                for i in range(0, self.n_site)
            ]

    def wg_routing(self):


        in_port_name = 'PORT0'
        out_port_name = 'PORT1'
        #### group 1
        list_router_in_main = [
            WgRouter(
                self,
                self.list_port_in_main[i],
                self.wg_routing_layer,
                route_in_port_dir=True
            )
            for i in range(0, self.n_site)
        ]
        list_router_out_main = [
            WgRouter(
                self,
                self.list_port_out_main[i],
                self.wg_routing_layer,
                route_in_port_dir=False
            )
            for i in range(0, self.n_site)
        ]

        if self.with_drop_ports:
            list_router_in_drop = [
                WgRouter(
                    self,
                    self.list_port_in_drop[i],
                    self.wg_routing_layer,
                    route_in_port_dir=True
                )
                for i in range(0, self.n_site)
            ]
            list_router_out_drop = [
                WgRouter(
                    self,
                    self.list_port_out_drop[i],
                    self.wg_routing_layer,
                    route_in_port_dir=False
                )
                for i in range(0, self.n_site)
            ]

        # list_idx_wg[idx] = val means port of the idx-th ring get routed to the val-th track
        list_idx_wg_main_bot = [2, 0, 4, 6, 8, 0, 0, 0, 0]
        list_idx_wg_main_top = [0, 0, 2, 4, 6, 8, 2, 0, 0]
        list_idx_wg_main_mid = [0, 0, 0, 0, 0, 0, 4, 2, 0]
        list_idx_wg_drop_bot = [(idx_wg_main_bot + 1) for idx_wg_main_bot in list_idx_wg_main_bot]
        list_idx_wg_drop_top = [(idx_wg_main_top + 1) for idx_wg_main_top in list_idx_wg_main_top]
        list_idx_wg_drop_mid = [(idx_wg_main_mid + 1) for idx_wg_main_mid in list_idx_wg_main_mid]

        # direction of the first bend, counting from the coupler
        list_first_bend_dir = [-1, -1, -1, -1, 1, 1, 1, 1, -1]
        list_1st_bend_extra_dx_in_main = [self.track_pitch_mod * 2, 0,
                                          0, self.track_pitch_mod * 2,
                                          self.track_pitch_mod * 3, self.track_pitch_mod,
                                          self.track_pitch_mod, self.track_pitch_mod, self.track_pitch_mod]
        list_1st_bend_extra_dx_in_drop = [self.track_pitch_mod * 3, self.track_pitch_mod * 1,
                                          self.track_pitch_mod * 1, self.track_pitch_mod * 3,
                                          self.track_pitch_mod * 2, 0,
                                          0, 0, 0]
        list_1st_bend_extra_dx_out_main = [self.track_pitch_mod * 2, 0,
                                           0, self.track_pitch_mod * 2,
                                           self.track_pitch_mod * 3, self.track_pitch_mod,
                                           self.track_pitch_mod, self.track_pitch_mod, 0]
        list_1st_bend_extra_dx_out_drop = [self.track_pitch_mod * 3, self.track_pitch_mod * 1,
                                           self.track_pitch_mod * 1, self.track_pitch_mod * 3,
                                           self.track_pitch_mod * 2, 0,
                                           0, 0, self.track_pitch_mod]
        list_int_bend_x_in_main = [0, 0,
                                   self.list_x_port_coupler_in[2] + self.x_coupler_pitch + self.bend_radius + self.track_pitch_mod * 7,
                                   self.list_x_port_coupler_in[3] + self.x_coupler_pitch + self.bend_radius + self.track_pitch_mod * 5,
                                   0, 0, 0, 0, 0]
        list_int_bend_x_in_drop = [0, 0,
                                   self.list_x_port_coupler_in[2] + self.x_coupler_pitch + self.bend_radius + self.track_pitch_mod * 6,
                                   self.list_x_port_coupler_in[2] + self.x_coupler_pitch + self.bend_radius + self.track_pitch_mod * 4,
                                   0, 0, 0, 0, 0]

        list_int_bend_x_out_main = [(self.x_instance[1] + self.x_instance[2]) / 2, 0, 0, 0,
                                    self.list_x_port_coupler_out[5] - self.x_coupler_pitch * 2 - self.bend_radius - self.track_pitch_mod * 4,
                                    self.list_x_port_coupler_out[5] - self.x_coupler_pitch * 2 - self.bend_radius - self.track_pitch_mod * 6,
                                    self.x_instance[8] + self.dx_LNA / 2 + self.bend_radius + self.track_pitch_mod * 4,
                                    self.x_instance[8] + self.dx_LNA / 2 + self.bend_radius + self.track_pitch_mod * 2,
                                    self.list_x_port_coupler_out[7] - self.bend_radius - self.track_pitch_mod * 3]
        list_int_bend_x_out_drop = [(self.x_instance[1] + self.x_instance[2]) / 2 + self.track_pitch, 0, 0, 0,
                                    self.list_x_port_coupler_out[5] - self.x_coupler_pitch * 2 - self.bend_radius - self.track_pitch_mod * 5,
                                    self.list_x_port_coupler_out[5] - self.x_coupler_pitch * 2 - self.bend_radius - self.track_pitch_mod * 7,
                                    self.x_instance[8] + self.dx_LNA / 2 + self.bend_radius + self.track_pitch_mod * 5,
                                    self.x_instance[8] + self.dx_LNA / 2 + self.bend_radius + self.track_pitch_mod * 3,
                                    self.list_x_port_coupler_out[7] - self.bend_radius - self.track_pitch_mod * 2]



        list_lst_bend_extra_dx_in_main  = [0, 0, self.track_pitch_mod, self.track_pitch_mod, self.track_pitch_mod, self.track_pitch_mod,
                                           0, 0, 0]
        list_lst_bend_extra_dx_in_drop  = [self.track_pitch_mod, self.track_pitch_mod, 0, 0, 0, 0,
                                           self.track_pitch_mod, self.track_pitch_mod, self.track_pitch_mod]
        list_lst_bend_extra_dx_out_main = [self.track_pitch_mod, 0, 0, 0, 0, self.track_pitch_mod,
                                           self.track_pitch_mod, self.track_pitch_mod, 0]
        list_lst_bend_extra_dx_out_drop = [0, self.track_pitch_mod, self.track_pitch_mod, self.track_pitch_mod, self.track_pitch_mod, 0,
                                           0, 0, self.track_pitch_mod]

        #### group 1, 6 sites
        # main ports
        for idx_ring in range(0, 6):
            # first_bend
            list_router_in_main[idx_ring].cardinal_router(
                [
                    (self.list_x_port_coupler_in[idx_ring] + self.bend_radius + list_1st_bend_extra_dx_in_main[idx_ring],
                     self.list_y_track_bot_group1[list_idx_wg_main_bot[idx_ring]] + self.bend_radius if (idx_ring < 4) else
                     self.list_y_track_top_group1[list_idx_wg_main_top[idx_ring]] - self.bend_radius),
                ]
            )

            # intermadiate two bends
            if idx_ring == 2 or idx_ring == 3:
                list_router_in_main[idx_ring].cardinal_router(
                    [
                        (list_int_bend_x_in_main[idx_ring] - self.bend_radius,
                         self.list_y_track_bot_group1[list_idx_wg_main_bot[idx_ring]] if (idx_ring < 4) else
                         self.list_y_track_top_group1[list_idx_wg_main_top[idx_ring]]),

                        (list_int_bend_x_in_main[idx_ring],
                         self.list_y_track_top_group1[list_idx_wg_main_top[idx_ring]] - self.bend_radius),
                    ]
                )

            # input waveguide final three bends to the ring modulator
            list_router_in_main[idx_ring].cardinal_router(
                [

                    (min(self.list_x_port_inst_in[idx_ring], self.x_instance[idx_ring] - self.dx_LNA / 2) -
                     self.bend_radius * 2 - list_lst_bend_extra_dx_in_main[idx_ring],
                     self.list_y_track_bot_group1[list_idx_wg_main_bot[idx_ring]] if (idx_ring < 2) else
                     self.list_y_track_top_group1[list_idx_wg_main_top[idx_ring]]),

                    (min(self.inst_list[idx_ring][in_port_name].center[0], self.x_instance[idx_ring] - self.dx_LNA / 2) -
                     self.bend_radius * 1 - list_lst_bend_extra_dx_in_main[idx_ring],
                     self.inst_list[idx_ring][in_port_name].center[1]),

                     self.inst_list[idx_ring][in_port_name].center,



                ]
            )


            list_router_out_main[idx_ring].cardinal_router(
                [
                    (self.list_x_port_coupler_out[idx_ring] - self.bend_radius - list_1st_bend_extra_dx_out_main[idx_ring],
                     self.list_y_track_bot_group1[list_idx_wg_main_bot[idx_ring]] + self.bend_radius if (idx_ring < 4) else
                     self.list_y_track_top_group1[list_idx_wg_main_top[idx_ring]] - self.bend_radius),
                ]
            )

            # intermadiate two bends
            if idx_ring == 4 or idx_ring == 0:
                list_router_out_main[idx_ring].cardinal_router(
                    [
                        (list_int_bend_x_out_main[idx_ring] + self.bend_radius,
                         self.list_y_track_bot_group1[list_idx_wg_main_bot[idx_ring]] if (idx_ring < 4) else
                         self.list_y_track_top_group1[list_idx_wg_main_top[idx_ring]]),

                        (list_int_bend_x_out_main[idx_ring],
                         (self.list_y_track_top_group1[list_idx_wg_main_top[idx_ring]] - self.bend_radius) if (idx_ring == 4) else
                         (self.list_y_track_bot_group1[list_idx_wg_main_bot[idx_ring]] + self.bend_radius)),
                    ]
                )



            # input waveguide final three bends to the ring modulator
            list_router_out_main[idx_ring].cardinal_router(
                [

                    (max(self.list_x_port_inst_out[idx_ring], self.x_instance[idx_ring] + self.dx_LNA / 2) +
                     self.bend_radius * 2 + list_lst_bend_extra_dx_out_main[idx_ring],
                     self.list_y_track_bot_group1[list_idx_wg_main_bot[idx_ring]] if (idx_ring != 0 and idx_ring != 5) else
                     self.list_y_track_top_group1[list_idx_wg_main_top[idx_ring]]),

                ]
            )

            list_router_out_main[idx_ring].add_fancy_s_bend(
                shift_left = ((self.list_y_track_bot_group1[list_idx_wg_main_bot[idx_ring]] - self.inst_list[idx_ring][out_port_name].center[1])
                             if (idx_ring != 0 and idx_ring != 5) else
                              (self.list_y_track_top_group1[list_idx_wg_main_top[idx_ring]] - self.inst_list[idx_ring][out_port_name].center[1])),
            )

            list_router_out_main[idx_ring].cardinal_router(
                [self.inst_list[idx_ring][out_port_name].center]
            )

        # drop ports
            if self.with_drop_ports:
                list_router_in_drop[idx_ring].cardinal_router(
                    [
                        (self.list_x_port_coupler_in[idx_ring] + self.bend_radius + list_1st_bend_extra_dx_in_drop[idx_ring],
                         self.list_y_track_bot_group1[list_idx_wg_drop_bot[idx_ring]] + self.bend_radius if (
                         idx_ring < 4) else
                         self.list_y_track_top_group1[list_idx_wg_drop_top[idx_ring]] - self.bend_radius),
                    ]
                )

            # intermadiate two bends
                if idx_ring == 2 or idx_ring == 3:
                    list_router_in_drop[idx_ring].cardinal_router(
                        [
                            (list_int_bend_x_in_drop[idx_ring] - self.bend_radius,
                             self.list_y_track_bot_group1[list_idx_wg_drop_bot[idx_ring]] if (idx_ring < 4) else
                             self.list_y_track_top_group1[list_idx_wg_drop_top[idx_ring]]),

                            (list_int_bend_x_in_drop[idx_ring],
                             self.list_y_track_top_group1[list_idx_wg_drop_top[idx_ring]] - self.bend_radius),
                        ]
                    )

                # input waveguide final three bends to the ring modulator

                list_router_in_drop[idx_ring].cardinal_router(
                    [

                        (min(self.list_x_port_inst_in[idx_ring], self.x_instance[idx_ring] - self.dx_LNA / 2) -
                         self.bend_radius * 2 - list_lst_bend_extra_dx_in_drop[idx_ring],
                         self.list_y_track_bot_group1[list_idx_wg_drop_bot[idx_ring]] if (idx_ring < 2) else
                         self.list_y_track_top_group1[list_idx_wg_drop_top[idx_ring]]),

                        (min(self.list_x_port_inst_in[idx_ring], self.x_instance[idx_ring] - self.dx_LNA / 2) -
                         self.bend_radius * 1 - list_lst_bend_extra_dx_in_drop[idx_ring],
                         self.y_port_inst_top_group1 - self.bend_radius if (idx_ring < 2) else
                         self.y_port_inst_top_group1 + self.bend_radius),

                        (self.list_x_port_inst_in[idx_ring],
                         self.y_port_inst_top_group1),

                    ]
                )



                list_router_out_drop[idx_ring].cardinal_router(
                    [
                        (self.list_x_port_coupler_out[idx_ring] - self.bend_radius - list_1st_bend_extra_dx_out_drop[idx_ring],
                         self.list_y_track_bot_group1[list_idx_wg_drop_bot[idx_ring]] + self.bend_radius if (idx_ring < 4) else
                         self.list_y_track_top_group1[list_idx_wg_drop_top[idx_ring]] - self.bend_radius),
                    ]
                )

                # intermadiate two bends

                if idx_ring == 4 or idx_ring == 0:
                    list_router_out_drop[idx_ring].cardinal_router(
                        [
                            (list_int_bend_x_out_drop[idx_ring] + self.bend_radius,
                             self.list_y_track_bot_group1[list_idx_wg_drop_bot[idx_ring]] if (idx_ring < 4) else
                             self.list_y_track_top_group1[list_idx_wg_drop_top[idx_ring]]),

                            (list_int_bend_x_out_drop[idx_ring],
                             (self.list_y_track_top_group1[list_idx_wg_drop_top[idx_ring]] - self.bend_radius) if (idx_ring == 4) else
                             (self.list_y_track_bot_group1[list_idx_wg_drop_bot[idx_ring]] + self.bend_radius)),
                        ]
                    )



                # input waveguide final three bends to the ring modulator
                list_router_out_drop[idx_ring].cardinal_router(
                    [

                        (max(self.list_x_port_inst_out[idx_ring], self.x_instance[idx_ring] + self.dx_LNA / 2) +
                         self.bend_radius * 2 + list_lst_bend_extra_dx_out_drop[idx_ring],
                         self.list_y_track_bot_group1[list_idx_wg_drop_bot[idx_ring]] if (idx_ring != 0 and idx_ring != 5) else
                         self.list_y_track_top_group1[list_idx_wg_drop_top[idx_ring]]),

                    ]
                )

                list_router_out_drop[idx_ring].add_fancy_s_bend(
                    shift_left = ((self.list_y_track_bot_group1[list_idx_wg_drop_bot[idx_ring]] - self.y_port_inst_top_group1)
                                 if (idx_ring != 0 and idx_ring != 5) else
                                  (self.list_y_track_top_group1[list_idx_wg_drop_top[idx_ring]] - self.y_port_inst_top_group1)),
                )

                list_router_out_drop[idx_ring].cardinal_router(
                    [(self.list_x_port_inst_out[idx_ring],self.y_port_inst_top_group1),]
                )




        ### group 2, 3 sites
        for idx_ring in range(6, 9):


            list_router_in_main[idx_ring].cardinal_router(
                [
                    (self.list_x_port_coupler_in[idx_ring] + self.bend_radius + list_1st_bend_extra_dx_in_main[idx_ring],
                     self.list_y_port_coupler_main[idx_ring] + self.bend_radius),

                    (self.list_x_port_coupler_in[idx_ring] + self.bend_radius * 2 + list_1st_bend_extra_dx_in_main[idx_ring],
                     self.list_y_track_mid_group2[list_idx_wg_main_mid[idx_ring]]),

                    (min(self.list_x_port_inst_in[idx_ring], self.x_instance[idx_ring] - self.dx_LNA / 2) -
                     self.bend_radius - list_lst_bend_extra_dx_in_main[idx_ring],
                     self.inst_list[idx_ring][in_port_name].center[1] - self.bend_radius),

                    self.inst_list[idx_ring][in_port_name].center,
                ]
            )

            list_router_out_main[idx_ring].cardinal_router(
                [
                    (self.list_x_port_coupler_out[idx_ring] - self.bend_radius * 1 - list_1st_bend_extra_dx_out_main[idx_ring],
                     self.list_y_port_coupler_main[idx_ring] - self.bend_radius * ((idx_ring == 8) * 2 - 1)),

                    (self.list_x_port_coupler_out[idx_ring] - self.bend_radius * 2 - list_1st_bend_extra_dx_out_main[idx_ring],
                     self.list_y_track_bot_group2[list_idx_wg_main_bot[idx_ring]] if (idx_ring == 8) else
                     self.list_y_track_mid_group2[list_idx_wg_main_mid[idx_ring]]),

                    (list_int_bend_x_out_main[idx_ring],
                     (self.list_y_track_mid_group2[list_idx_wg_main_mid[idx_ring]] if (idx_ring == 8) else
                     self.list_y_track_top_group2[list_idx_wg_main_top[idx_ring]]) - self.bend_radius),

                    (list_int_bend_x_out_main[idx_ring] - self.bend_radius,
                     (self.list_y_track_mid_group2[list_idx_wg_main_mid[idx_ring]] if (idx_ring == 8) else
                      self.list_y_track_top_group2[list_idx_wg_main_top[idx_ring]])),

                    (self.x_instance[idx_ring] + self.dx_LNA / 2 + list_lst_bend_extra_dx_out_main[idx_ring]
                     + self.bend_radius,
                     self.inst_list[idx_ring][out_port_name].center[1] - self.bend_radius * ((idx_ring == 8) * 2 - 1)),

                    self.inst_list[idx_ring][out_port_name].center,

                    ]
            )


            if self.with_drop_ports:
                list_router_in_drop[idx_ring].cardinal_router(
                    [
                        (self.list_x_port_coupler_in[idx_ring] + self.bend_radius + list_1st_bend_extra_dx_in_drop[idx_ring],
                         self.list_y_port_coupler_drop[idx_ring] + self.bend_radius),

                        (self.list_x_port_coupler_in[idx_ring] + self.bend_radius * 2 + list_1st_bend_extra_dx_in_drop[idx_ring],
                         self.list_y_track_mid_group2[list_idx_wg_drop_mid[idx_ring]]),

                        (min(self.list_x_port_inst_in[idx_ring], self.x_instance[idx_ring] - self.dx_LNA / 2) -
                         self.bend_radius - list_lst_bend_extra_dx_in_drop[idx_ring],
                         self.y_port_inst_top_group2 - self.bend_radius),

                        (self.list_x_port_inst_in[idx_ring],
                         self.y_port_inst_top_group2),
                    ]
                )

                list_router_out_drop[idx_ring].cardinal_router(
                    [
                        (self.list_x_port_coupler_out[idx_ring] - self.bend_radius * 1 - list_1st_bend_extra_dx_out_drop[
                            idx_ring],
                         self.list_y_port_coupler_drop[idx_ring] - self.bend_radius * ((idx_ring == 8) * 2 - 1)),

                        (self.list_x_port_coupler_out[idx_ring] - self.bend_radius * 2 - list_1st_bend_extra_dx_out_drop[
                            idx_ring],
                         self.list_y_track_bot_group2[list_idx_wg_drop_bot[idx_ring]] if (idx_ring == 8) else
                         self.list_y_track_mid_group2[list_idx_wg_drop_mid[idx_ring]]),

                        (list_int_bend_x_out_drop[idx_ring],
                         (self.list_y_track_mid_group2[list_idx_wg_drop_mid[idx_ring]] if (idx_ring == 8) else
                          self.list_y_track_top_group2[list_idx_wg_drop_top[idx_ring]]) - self.bend_radius),

                        (list_int_bend_x_out_drop[idx_ring] - self.bend_radius,
                         (self.list_y_track_mid_group2[list_idx_wg_drop_mid[idx_ring]] if (idx_ring == 8) else
                          self.list_y_track_top_group2[list_idx_wg_drop_top[idx_ring]])),

                        (self.x_instance[idx_ring] + self.dx_LNA / 2 + list_lst_bend_extra_dx_out_drop[idx_ring]
                         + self.bend_radius,
                         self.y_port_inst_top_group2 - self.bend_radius * ((idx_ring == 8) * 2 - 1)),

                        (self.list_x_port_inst_out[idx_ring],
                         self.y_port_inst_top_group2),

                    ]
                )


class TripleRingRowWithLNANoDropForceRouting(PhotonicTemplateBase):
    """
    Photonic Ports:
    IN = left side
    OUT = right side
    """

    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)
        self.params = params

        for key, val in self.params.items():  # Automatically unpack variables
            # exec( "self.{} = {}".format( key, val ) )
            exec(f"self.{key} = {val!r}")

        if self.with_drop_ports:
            self.track_pitch_mod = self.track_pitch
            self.y_coupler_pitch_mod = self.y_coupler_pitch
        else:
            self.track_pitch_mod = self.track_pitch / 2
            self.y_coupler_pitch_mod = self.y_coupler_pitch / 2

        # ================================================================
        # Create all templates (may need them to get geometry parameters)
        # ================================================================

        # Create class of each device component
        gc_module = importlib.import_module(self.grating_coupler_module)
        gc_class = getattr(gc_module, self.grating_coupler_class)
        self.gc_master = self.new_template(params=None, temp_cls=gc_class)
        # self.gc_array_inst = [None] * self.grating_coupler_num

        self.bend_radius = self.photonic_tech_info.get_default_wg_params(self.wg_routing_layer)['radius'] + 0.1
        self.routing_width = self.photonic_tech_info.get_default_wg_params(self.wg_routing_layer)['width']

    @classmethod
    def get_params_info(cls):
        return dict(

            grating_coupler_module=None,
            grating_coupler_class=None,


        )

    @classmethod
    def get_default_param_values(cls):
        return dict(
        )

    def adjust_location(self, loc, rotation):
        if rotation == 'R0':
            return ( loc[0],  loc[1])
        elif rotation == 'R90':
            return (-loc[1],  loc[0])
        elif rotation == 'R180':
            return (-loc[0], -loc[1])
        elif rotation == 'R270':
            return ( loc[1], -loc[0])
        elif rotation == 'MX':
            return ( loc[0], -loc[1])
        elif rotation == 'MY':
            return (-loc[0],  loc[1])
        elif rotation == 'MXR90':
            return ( loc[1],  loc[0])
        else:
            return (-loc[1], -loc[0])


    def adjust_rotation_and_location(self, bound_box, loc_in, loc_out):
        loc_center = ((bound_box.left+bound_box.right)/2.0,
                      (bound_box.top+bound_box.bottom)/2.0)
        if loc_out[1] == loc_in[1]:
            # R0, R180, MX or MY
            if loc_out[0] > loc_in[0]:
                # no need to do MY related thing
                loc_in_extend = (bound_box.left, loc_in[1])
                loc_out_extend = (bound_box.right, loc_out[1])
                if loc_out[1] <= loc_center[1]:
                    rotation = 'R0'
                else:
                    rotation = 'MX'
            else:
                # need to MY
                loc_in_extend = (bound_box.right, loc_in[1])
                loc_out_extend = (bound_box.left, loc_out[1])
                if loc_out[1] <= loc_center[1]:
                    rotation = 'MY'
                else:
                    rotation = 'R180'
        else:
            # R90, R270, MXR90 or MYR90
            if loc_out[1] > loc_in[1]:
                loc_in_extend = (loc_in[0], bound_box.bottom)
                loc_out_extend = (loc_out[0], bound_box.top)
                # no need to do MY related thing
                if loc_out[0] >= loc_center[0]:
                    rotation = 'R270'
                else:
                    rotation = 'MXR90'
            else:
                # need to MY
                loc_in_extend = (loc_in[0], bound_box.top)
                loc_out_extend = (loc_out[0], bound_box.bottom)
                if loc_out[0] >= loc_center[0]:
                    rotation = 'MYR90'
                else:
                    rotation = 'R90'
        loc_in_adj = self.adjust_location(loc_in, rotation)
        loc_out_adj = self.adjust_location(loc_out, rotation)
        loc_in_extend_adj = self.adjust_location(loc_in_extend, rotation)
        loc_out_extend_adj = self.adjust_location(loc_out_extend, rotation)
        loc_in_extend_adj = self.adjust_location(loc_in, rotation)
        loc_out_extend_adj = self.adjust_location(loc_out, rotation)
        return rotation, loc_in_adj, loc_out_adj, loc_in_extend_adj, loc_out_extend_adj

    def adjust_rotation_and_location_from_master(self, master, in_port_name, out_port_name):
        port_in = master.get_photonic_port(in_port_name)
        port_out = master.get_photonic_port(out_port_name)
        # gdad
        loc_in = port_in.center
        loc_out = port_out.center
        bound_box = master.bound_box
        loc_center = ((bound_box.left+bound_box.right)/2.0,
                      (bound_box.top+bound_box.bottom)/2.0)
        print(port_in.angle, abs((port_in.angle+180)%180 - 90))
        if (abs(port_in.angle) < 1e-3) or (abs(port_in.angle-np.pi) < 1e-3):
            # R0, R180, MX or MY
            if loc_out[0] > loc_in[0]:
                # no need to do MY related thing
                loc_in_extend = (bound_box.left, loc_in[1])
                loc_out_extend = (bound_box.right, loc_out[1])
                if loc_out[1] <= loc_center[1]:
                    rotation = 'R0'
                else:
                    rotation = 'MX'
            else:
                # need to MY
                loc_in_extend = (bound_box.right, loc_in[1])
                loc_out_extend = (bound_box.left, loc_out[1])
                if loc_out[1] <= loc_center[1]:
                    rotation = 'MY'
                else:
                    rotation = 'R180'
        else:
            # R90, R270, MXR90 or MYR90
            if loc_out[1] > loc_in[1]:
                loc_in_extend = (loc_in[0], bound_box.bottom)
                loc_out_extend = (loc_out[0], bound_box.top)
                # no need to do MY related thing
                if loc_out[0] >= loc_center[0]:
                    rotation = 'R270'
                else:
                    rotation = 'MXR90'
            else:
                # need to MY
                loc_in_extend = (loc_in[0], bound_box.top)
                loc_out_extend = (loc_out[0], bound_box.bottom)
                if loc_out[0] >= loc_center[0]:
                    rotation = 'MYR90'
                else:
                    rotation = 'R90'
        loc_in_adj = self.adjust_location(loc_in, rotation)
        loc_out_adj = self.adjust_location(loc_out, rotation)
        loc_in_extend_adj = self.adjust_location(loc_in_extend, rotation)
        loc_out_extend_adj = self.adjust_location(loc_out_extend, rotation)
        loc_in_extend_adj = self.adjust_location(loc_in, rotation)
        loc_out_extend_adj = self.adjust_location(loc_out, rotation)
        return rotation, loc_in_adj, loc_out_adj, loc_in_extend_adj, loc_out_extend_adj

    def get_inst_and_track_locations(self):

        self.n_site = 9
        x_port_coupler_in_base = self.x_port_coupler_in_base
        x_port_coupler_out_base = self.dx_design - x_port_coupler_in_base - self.x_coupler_pitch * 2

        #### define index of coupler port positions from left to right, the i-th element is
        #### the index of coupler port position of the i-th site
        list_idx_x_port_coupler_in = [0, 0, 1, 1, 2, 2, 0, 1, 2]
        list_idx_x_port_coupler_out = [1, 1, 0, 0, 2, 2, 1, 0, 2]
        list_idx_y_port_coupler = [1, 0, 0, 1, 0, 1, 0, 0, 0]

        # define coupler port coordinates
        self.list_x_port_coupler_in = [
            x_port_coupler_in_base +
            list_idx_x_port_coupler_in[i] * self.x_coupler_pitch for i in range(0, self.n_site)
        ]
        self.list_x_port_coupler_out = [
            x_port_coupler_out_base +
            list_idx_x_port_coupler_out[i] * self.x_coupler_pitch for i in range(0, self.n_site)
        ]
        self.list_y_port_coupler_main = [
            (self.y_port_coupler_base[0] if (i <= 5) else self.y_port_coupler_base[1]) +
            list_idx_y_port_coupler[i] * self.y_coupler_pitch_mod * 2 for i in range(0, self.n_site)
        ]
        self.list_y_port_coupler_drop = [
            self.list_y_port_coupler_main[i] + self.y_coupler_pitch_mod for i in range(0, self.n_site)
        ]





    def draw_layout(self):

        # print(self.yaml_list)
        self.get_site_specs()
        self.get_inst_and_track_locations()
        self.place_instances()
        self.create_ports()
        self.wg_routing()


    def get_site_specs(self):
        # instantiate the ring modulator masters
        self.list_inst_direction = []
        self.list_dx_inst = []
        # list_dy_inst = []
        self.list_x_inst_in_offset = []
        self.list_x_inst_out_offset = []
        self.list_x_inst_in_extend_offset = []
        self.list_x_inst_out_extend_offset = []
        self.list_y_inst_in_offset = []
        self.list_y_inst_out_offset = []
        self.master_list = []
        self.in_port_name = 'PORT0'
        self.out_port_name = 'PORT1'

        in_port_name = 'PORT0'
        out_port_name = 'PORT1'
        for ind, yaml_tuple in enumerate(self.yaml_list):
            yaml_file = yaml_tuple[0]
            yaml_rotation = yaml_tuple[1]
            if yaml_file != 'VOID':
                with open(yaml_file, 'r') as f:
                    yaml_content = yaml.load(f)

                lay_module = importlib.import_module(yaml_content['layout_package'])
                temp_cls = getattr(lay_module, yaml_content['layout_class'])

                master = self.new_template(params=yaml_content['layout_params'],
                                           temp_cls=temp_cls)

                master_in_port_loc = master.get_photonic_port(in_port_name).center
                master_out_port_loc = master.get_photonic_port(out_port_name).center

                rotation, loc_in_adj, loc_out_adj, loc_in_extend_adj, loc_out_extend_adj = \
                    self.adjust_rotation_and_location(master.bound_box, master_in_port_loc, master_out_port_loc)
                rotation_old, loc_in_adj_old, loc_out_adj_old, loc_in_extend_adj_old, loc_out_extend_adj_old = \
                    rotation, loc_in_adj, loc_out_adj, loc_in_extend_adj, loc_out_extend_adj

                rotation, loc_in_adj, loc_out_adj, loc_in_extend_adj, loc_out_extend_adj = \
                    self.adjust_rotation_and_location_from_master(master, in_port_name, out_port_name)
                # print('COMPARE (old):', ind, rotation_old, loc_in_adj_old, loc_out_adj_old, loc_in_extend_adj_old, loc_out_extend_adj_old)
                #
                # print('COMPARE (new):', ind, rotation, loc_in_adj, loc_out_adj, loc_in_extend_adj, loc_out_extend_adj)
                self.master_list.append(master)
                rotation_override = yaml_rotation[1:] if yaml_rotation[0] == 'O' else rotation
                self.list_inst_direction.append(rotation_override)
                self.list_y_inst_in_offset.append(loc_in_adj[1])
                self.list_y_inst_out_offset.append(loc_out_adj[1])
                self.list_x_inst_in_offset.append(loc_in_adj[0])
                self.list_x_inst_out_offset.append(loc_out_adj[0])
                self.list_x_inst_in_extend_offset.append(loc_in_extend_adj[0])
                self.list_x_inst_out_extend_offset.append(loc_out_extend_adj[0])
                self.list_dx_inst.append(loc_out_extend_adj[0] - loc_in_extend_adj[0])

                # if ind==1:
                #     print('PRINT', master, rotation, loc_in_adj)
            else:
                self.master_list.append([])
                self.list_inst_direction.append('R0')
                self.list_y_inst_in_offset.append(0)
                self.list_y_inst_out_offset.append(0)
                self.list_x_inst_in_offset.append(0)
                self.list_x_inst_out_offset.append(0)
                self.list_x_inst_in_extend_offset.append(0)
                self.list_x_inst_out_extend_offset.append(0)
                self.list_dx_inst.append(0)


    def place_instances(self):
        # instantiate the grating couplers
        self.list_gc_in_main = [
            self.add_instance(
                master=self.gc_master,
                loc=(self.list_x_port_coupler_in[i],
                     self.list_y_port_coupler_main[i]),
                # Offset site by location of input port, to put input port at desired location
                orient='R0',
            )
        for i in range(0, self.n_site)]
        self.list_gc_out_main = [
            self.add_instance(
                master=self.gc_master,
                loc=(self.list_x_port_coupler_out[i],
                     self.list_y_port_coupler_main[i]),
                # Offset site by location of input port, to put input port at desired location
                orient='MY',
            )
        for i in range(0, self.n_site)]


        # instantiate the rings
        for i in range(0, self.n_site):

            y_inst = self.y_instance[0] if i < 6 else  self.y_instance[1]
            self.inst_list.append(
                self.add_instance(
                    master=self.master_list[i],
                    loc=(self.x_instance[i], y_inst),
                    orient=self.list_inst_direction[i],
                )

            )


    def create_ports(self):

        self.list_port_in_main = [
            self.add_photonic_port(
                name=f'IN_MAIN{i}',
                center=(self.list_x_port_coupler_in[i], self.list_y_port_coupler_main[i]),
                orient='R0',
                layer=self.wg_port_layer,
                width=self.routing_width
            )
            for i in range(0, self.n_site)
        ]
        self.list_port_out_main = [
            self.add_photonic_port(
                name=f'OUT_MAIN{i}',
                center=(self.list_x_port_coupler_out[i], self.list_y_port_coupler_main[i]),
                orient='R0',
                layer=self.wg_port_layer,
                width=self.routing_width
            )
            for i in range(0, self.n_site)
        ]


    def wg_routing(self):


        in_port_name = 'PORT0'
        out_port_name = 'PORT1'
        #### group 1
        list_router_in_main = [
            WgRouter(
                self,
                self.list_port_in_main[i],
                self.wg_routing_layer,
                route_in_port_dir=True
            )
            for i in range(0, self.n_site)
        ]
        list_router_out_main = [
            WgRouter(
                self,
                self.list_port_out_main[i],
                self.wg_routing_layer,
                route_in_port_dir=False
            )
            for i in range(0, self.n_site)
        ]

        list_in_router_path = self.in_path
        list_out_router_path = self.out_path



        #### group 1, 6 sites
        # main ports
        list_center_left = [(self.inst_list[idx_ring][in_port_name].center if
                            self.inst_list[idx_ring][in_port_name].center[0] < self.inst_list[idx_ring][out_port_name].center[0]
                            else self.inst_list[idx_ring][out_port_name].center) for idx_ring in range(0, 9)]
        list_center_right = [(self.inst_list[idx_ring][out_port_name].center if
                            self.inst_list[idx_ring][in_port_name].center[0] < self.inst_list[idx_ring][out_port_name].center[0]
                            else self.inst_list[idx_ring][in_port_name].center) for idx_ring in range(0, 9)]


        for idx_ring in range(0, 6):

            list_router_out_main[idx_ring].cardinal_router(
                list_out_router_path[idx_ring],
                # [self.inst_list[idx_ring][out_port_name].center]
            )

            list_router_out_main[idx_ring].add_fancy_s_bend(
                shift_left=-list_center_right[idx_ring][1]+list_out_router_path[idx_ring][-1][1],
                length=-list_center_right[idx_ring][0]+list_out_router_path[idx_ring][-1][0]
            )

        for idx_ring in [0, 1, 2]:
            list_router_in_main[idx_ring].cardinal_router(
                list_in_router_path[idx_ring],
            )

            list_router_in_main[idx_ring].add_fancy_s_bend(
                shift_left=list_center_left[idx_ring][1]-list_in_router_path[idx_ring][-1][1],
                length=list_center_left[idx_ring][0]-list_in_router_path[idx_ring][-1][0]
            )


        for idx_ring in [3, 4, 5]:
            list_router_in_main[idx_ring].cardinal_router(
                list_in_router_path[idx_ring]
                +
                [list_center_left[idx_ring]],
            )

        for idx_ring in [6, 7, 8]:
            list_router_in_main[idx_ring].cardinal_router(
                list_in_router_path[idx_ring] +
                [list_center_left[idx_ring]],
            )

            list_router_out_main[idx_ring].cardinal_router(
                list_out_router_path[idx_ring] +
                [list_center_right[idx_ring]]
            )

        # for idx_ring in [7, 8]:
        #     list_router_in_main[idx_ring].cardinal_router(
        #         list_in_router_path[idx_ring]
        #         +
        #         [self.inst_list[idx_ring][in_port_name].center],
        #     )
        #
        #     list_router_out_main[idx_ring].cardinal_router(
        #         list_out_router_path[idx_ring]
        #         +
        #         [self.inst_list[idx_ring][out_port_name].center]
        #     )
class TripleRingRowWithLNANoDropForceRouting1(PhotonicTemplateBase):
    """
    Photonic Ports:
    IN = left side
    OUT = right side
    """

    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)
        self.params = params

        for key, val in self.params.items():  # Automatically unpack variables
            # exec( "self.{} = {}".format( key, val ) )
            exec(f"self.{key} = {val!r}")

        if self.with_drop_ports:
            self.track_pitch_mod = self.track_pitch
            self.y_coupler_pitch_mod = self.y_coupler_pitch
        else:
            self.track_pitch_mod = self.track_pitch / 2
            self.y_coupler_pitch_mod = self.y_coupler_pitch / 2

        # ================================================================
        # Create all templates (may need them to get geometry parameters)
        # ================================================================

        # Create class of each device component
        gc_module = importlib.import_module(self.grating_coupler_module)
        gc_class = getattr(gc_module, self.grating_coupler_class)
        self.gc_master = self.new_template(params=None, temp_cls=gc_class)
        # self.gc_array_inst = [None] * self.grating_coupler_num

        self.bend_radius = self.photonic_tech_info.get_default_wg_params(self.wg_routing_layer)['radius'] + 0.1
        self.routing_width = self.photonic_tech_info.get_default_wg_params(self.wg_routing_layer)['width']

    @classmethod
    def get_params_info(cls):
        return dict(

            grating_coupler_module=None,
            grating_coupler_class=None,


        )

    @classmethod
    def get_default_param_values(cls):
        return dict(
        )

    def adjust_location(self, loc, rotation):
        if rotation == 'R0':
            return ( loc[0],  loc[1])
        elif rotation == 'R90':
            return (-loc[1],  loc[0])
        elif rotation == 'R180':
            return (-loc[0], -loc[1])
        elif rotation == 'R270':
            return ( loc[1], -loc[0])
        elif rotation == 'MX':
            return ( loc[0], -loc[1])
        elif rotation == 'MY':
            return (-loc[0],  loc[1])
        elif rotation == 'MXR90':
            return ( loc[1],  loc[0])
        else:
            return (-loc[1], -loc[0])


    def adjust_rotation_and_location(self, bound_box, loc_in, loc_out):
        loc_center = ((bound_box.left+bound_box.right)/2.0,
                      (bound_box.top+bound_box.bottom)/2.0)
        if loc_out[1] == loc_in[1]:
            # R0, R180, MX or MY
            if loc_out[0] > loc_in[0]:
                # no need to do MY related thing
                loc_in_extend = (bound_box.left, loc_in[1])
                loc_out_extend = (bound_box.right, loc_out[1])
                if loc_out[1] <= loc_center[1]:
                    rotation = 'R0'
                else:
                    rotation = 'MX'
            else:
                # need to MY
                loc_in_extend = (bound_box.right, loc_in[1])
                loc_out_extend = (bound_box.left, loc_out[1])
                if loc_out[1] <= loc_center[1]:
                    rotation = 'MY'
                else:
                    rotation = 'R180'
        else:
            # R90, R270, MXR90 or MYR90
            if loc_out[1] > loc_in[1]:
                loc_in_extend = (loc_in[0], bound_box.bottom)
                loc_out_extend = (loc_out[0], bound_box.top)
                # no need to do MY related thing
                if loc_out[0] >= loc_center[0]:
                    rotation = 'R270'
                else:
                    rotation = 'MXR90'
            else:
                # need to MY
                loc_in_extend = (loc_in[0], bound_box.top)
                loc_out_extend = (loc_out[0], bound_box.bottom)
                if loc_out[0] >= loc_center[0]:
                    rotation = 'MYR90'
                else:
                    rotation = 'R90'
        loc_in_adj = self.adjust_location(loc_in, rotation)
        loc_out_adj = self.adjust_location(loc_out, rotation)
        loc_in_extend_adj = self.adjust_location(loc_in_extend, rotation)
        loc_out_extend_adj = self.adjust_location(loc_out_extend, rotation)
        loc_in_extend_adj = self.adjust_location(loc_in, rotation)
        loc_out_extend_adj = self.adjust_location(loc_out, rotation)
        return rotation, loc_in_adj, loc_out_adj, loc_in_extend_adj, loc_out_extend_adj

    def adjust_rotation_and_location_from_master(self, master, in_port_name, out_port_name):
        port_in = master.get_photonic_port(in_port_name)
        port_out = master.get_photonic_port(out_port_name)
        # gdad
        loc_in = port_in.center
        loc_out = port_out.center
        bound_box = master.bound_box
        loc_center = ((bound_box.left+bound_box.right)/2.0,
                      (bound_box.top+bound_box.bottom)/2.0)
        print(port_in.angle, abs((port_in.angle+180)%180 - 90))
        if (abs(port_in.angle) < 1e-3) or (abs(port_in.angle-np.pi) < 1e-3):
            # R0, R180, MX or MY
            if loc_out[0] > loc_in[0]:
                # no need to do MY related thing
                loc_in_extend = (bound_box.left, loc_in[1])
                loc_out_extend = (bound_box.right, loc_out[1])
                if loc_out[1] <= loc_center[1]:
                    rotation = 'R0'
                else:
                    rotation = 'MX'
            else:
                # need to MY
                loc_in_extend = (bound_box.right, loc_in[1])
                loc_out_extend = (bound_box.left, loc_out[1])
                if loc_out[1] <= loc_center[1]:
                    rotation = 'MY'
                else:
                    rotation = 'R180'
        else:
            # R90, R270, MXR90 or MYR90
            if loc_out[1] > loc_in[1]:
                loc_in_extend = (loc_in[0], bound_box.bottom)
                loc_out_extend = (loc_out[0], bound_box.top)
                # no need to do MY related thing
                if loc_out[0] >= loc_center[0]:
                    rotation = 'R270'
                else:
                    rotation = 'MXR90'
            else:
                # need to MY
                loc_in_extend = (loc_in[0], bound_box.top)
                loc_out_extend = (loc_out[0], bound_box.bottom)
                if loc_out[0] >= loc_center[0]:
                    rotation = 'MYR90'
                else:
                    rotation = 'R90'
        loc_in_adj = self.adjust_location(loc_in, rotation)
        loc_out_adj = self.adjust_location(loc_out, rotation)
        loc_in_extend_adj = self.adjust_location(loc_in_extend, rotation)
        loc_out_extend_adj = self.adjust_location(loc_out_extend, rotation)
        loc_in_extend_adj = self.adjust_location(loc_in, rotation)
        loc_out_extend_adj = self.adjust_location(loc_out, rotation)
        return rotation, loc_in_adj, loc_out_adj, loc_in_extend_adj, loc_out_extend_adj

    def get_inst_and_track_locations(self):

        self.n_site = 9
        x_port_coupler_in_base = self.x_port_coupler_in_base
        x_port_coupler_out_base = self.dx_design - x_port_coupler_in_base - self.x_coupler_pitch * 2

        #### define index of coupler port positions from left to right, the i-th element is
        #### the index of coupler port position of the i-th site
        list_idx_x_port_coupler_in = [0, 0, 1, 1, 2, 2, 0, 1, 2]
        list_idx_x_port_coupler_out = [1, 1, 0, 0, 2, 2, 1, 0, 2]
        list_idx_y_port_coupler = [1, 0, 0, 1, 0, 1, 0, 0, 0]

        # define coupler port coordinates
        self.list_x_port_coupler_in = [
            x_port_coupler_in_base +
            list_idx_x_port_coupler_in[i] * self.x_coupler_pitch for i in range(0, self.n_site)
        ]
        self.list_x_port_coupler_out = [
            x_port_coupler_out_base +
            list_idx_x_port_coupler_out[i] * self.x_coupler_pitch for i in range(0, self.n_site)
        ]
        self.list_y_port_coupler_main = [
            (self.y_port_coupler_base[0] if (i <= 5) else self.y_port_coupler_base[1]) +
            list_idx_y_port_coupler[i] * self.y_coupler_pitch_mod * 2 for i in range(0, self.n_site)
        ]
        self.list_y_port_coupler_drop = [
            self.list_y_port_coupler_main[i] + self.y_coupler_pitch_mod for i in range(0, self.n_site)
        ]





    def draw_layout(self):

        # print(self.yaml_list)
        self.get_site_specs()
        self.get_inst_and_track_locations()
        self.place_instances()
        self.create_ports()
        self.wg_routing()


    def get_site_specs(self):
        # instantiate the ring modulator masters
        self.list_inst_direction = []
        self.list_dx_inst = []
        # list_dy_inst = []
        self.list_x_inst_in_offset = []
        self.list_x_inst_out_offset = []
        self.list_x_inst_in_extend_offset = []
        self.list_x_inst_out_extend_offset = []
        self.list_y_inst_in_offset = []
        self.list_y_inst_out_offset = []
        self.master_list = []
        self.in_port_name = 'PORT0'
        self.out_port_name = 'PORT1'

        in_port_name = 'PORT0'
        out_port_name = 'PORT1'
        for ind, yaml_tuple in enumerate(self.yaml_list):
            yaml_file = yaml_tuple[0]
            yaml_rotation = yaml_tuple[1]
            if yaml_file != 'VOID':
                with open(yaml_file, 'r') as f:
                    yaml_content = yaml.load(f)

                lay_module = importlib.import_module(yaml_content['layout_package'])
                temp_cls = getattr(lay_module, yaml_content['layout_class'])

                master = self.new_template(params=yaml_content['layout_params'],
                                           temp_cls=temp_cls)

                master_in_port_loc = master.get_photonic_port(in_port_name).center
                master_out_port_loc = master.get_photonic_port(out_port_name).center

                rotation, loc_in_adj, loc_out_adj, loc_in_extend_adj, loc_out_extend_adj = \
                    self.adjust_rotation_and_location(master.bound_box, master_in_port_loc, master_out_port_loc)
                rotation_old, loc_in_adj_old, loc_out_adj_old, loc_in_extend_adj_old, loc_out_extend_adj_old = \
                    rotation, loc_in_adj, loc_out_adj, loc_in_extend_adj, loc_out_extend_adj

                rotation, loc_in_adj, loc_out_adj, loc_in_extend_adj, loc_out_extend_adj = \
                    self.adjust_rotation_and_location_from_master(master, in_port_name, out_port_name)
                # print('COMPARE (old):', ind, rotation_old, loc_in_adj_old, loc_out_adj_old, loc_in_extend_adj_old, loc_out_extend_adj_old)
                #
                # print('COMPARE (new):', ind, rotation, loc_in_adj, loc_out_adj, loc_in_extend_adj, loc_out_extend_adj)
                self.master_list.append(master)
                rotation_override = yaml_rotation[1:] if yaml_rotation[0] == 'O' else rotation
                self.list_inst_direction.append(rotation_override)
                self.list_y_inst_in_offset.append(loc_in_adj[1])
                self.list_y_inst_out_offset.append(loc_out_adj[1])
                self.list_x_inst_in_offset.append(loc_in_adj[0])
                self.list_x_inst_out_offset.append(loc_out_adj[0])
                self.list_x_inst_in_extend_offset.append(loc_in_extend_adj[0])
                self.list_x_inst_out_extend_offset.append(loc_out_extend_adj[0])
                self.list_dx_inst.append(loc_out_extend_adj[0] - loc_in_extend_adj[0])

                # if ind==1:
                #     print('PRINT', master, rotation, loc_in_adj)
            else:
                self.master_list.append([])
                self.list_inst_direction.append('R0')
                self.list_y_inst_in_offset.append(0)
                self.list_y_inst_out_offset.append(0)
                self.list_x_inst_in_offset.append(0)
                self.list_x_inst_out_offset.append(0)
                self.list_x_inst_in_extend_offset.append(0)
                self.list_x_inst_out_extend_offset.append(0)
                self.list_dx_inst.append(0)


    def place_instances(self):
        # instantiate the grating couplers
        self.list_gc_in_main = [
            self.add_instance(
                master=self.gc_master,
                loc=(self.list_x_port_coupler_in[i],
                     self.list_y_port_coupler_main[i]),
                # Offset site by location of input port, to put input port at desired location
                orient='R0',
            )
        for i in range(0, self.n_site)]
        self.list_gc_out_main = [
            self.add_instance(
                master=self.gc_master,
                loc=(self.list_x_port_coupler_out[i],
                     self.list_y_port_coupler_main[i]),
                # Offset site by location of input port, to put input port at desired location
                orient='MY',
            )
        for i in range(0, self.n_site)]


        # instantiate the rings
        for i in range(0, self.n_site):

            y_inst = self.y_instance[0] if i < 6 else  self.y_instance[1]
            self.inst_list.append(
                self.add_instance(
                    master=self.master_list[i],
                    loc=(self.x_instance[i], y_inst),
                    orient=self.list_inst_direction[i],
                )

            )


    def create_ports(self):

        self.list_port_in_main = [
            self.add_photonic_port(
                name=f'IN_MAIN{i}',
                center=(self.list_x_port_coupler_in[i], self.list_y_port_coupler_main[i]),
                orient='R0',
                layer=self.wg_port_layer,
                width=self.routing_width
            )
            for i in range(0, self.n_site)
        ]
        self.list_port_out_main = [
            self.add_photonic_port(
                name=f'OUT_MAIN{i}',
                center=(self.list_x_port_coupler_out[i], self.list_y_port_coupler_main[i]),
                orient='R0',
                layer=self.wg_port_layer,
                width=self.routing_width
            )
            for i in range(0, self.n_site)
        ]


    def wg_routing(self):


        in_port_name = 'PORT0'
        out_port_name = 'PORT1'
        #### group 1
        list_router_in_main = [
            WgRouter(
                self,
                self.list_port_in_main[i],
                self.wg_routing_layer,
                route_in_port_dir=True
            )
            for i in range(0, self.n_site)
        ]
        list_router_out_main = [
            WgRouter(
                self,
                self.list_port_out_main[i],
                self.wg_routing_layer,
                route_in_port_dir=False
            )
            for i in range(0, self.n_site)
        ]

        list_in_router_path = self.in_path
        list_out_router_path = self.out_path



        #### group 1, 6 sites
        # main ports
        list_center_left = [(self.inst_list[idx_ring][in_port_name].center if
                            self.inst_list[idx_ring][in_port_name].center[0] < self.inst_list[idx_ring][out_port_name].center[0]
                            else self.inst_list[idx_ring][out_port_name].center) for idx_ring in range(0, 9)]
        list_center_right = [(self.inst_list[idx_ring][out_port_name].center if
                            self.inst_list[idx_ring][in_port_name].center[0] < self.inst_list[idx_ring][out_port_name].center[0]
                            else self.inst_list[idx_ring][in_port_name].center) for idx_ring in range(0, 9)]


        for idx_ring in range(0, 6):

            list_router_out_main[idx_ring].cardinal_router(
                list_out_router_path[idx_ring],
                # [self.inst_list[idx_ring][out_port_name].center]
            )

            list_router_out_main[idx_ring].add_fancy_s_bend(
                shift_left=-list_center_right[idx_ring][1]+list_out_router_path[idx_ring][-1][1],
                length=-list_center_right[idx_ring][0]+list_out_router_path[idx_ring][-1][0]
            )

        for idx_ring in [0, 1, 2]:
            list_router_in_main[idx_ring].cardinal_router(
                list_in_router_path[idx_ring],
            )

            list_router_in_main[idx_ring].add_fancy_s_bend(
                shift_left=list_center_left[idx_ring][1]-list_in_router_path[idx_ring][-1][1],
                length=list_center_left[idx_ring][0]-list_in_router_path[idx_ring][-1][0]
            )


        for idx_ring in [3, 4, 5]:
            list_router_in_main[idx_ring].cardinal_router(
                list_in_router_path[idx_ring]
                +
                [list_center_left[idx_ring]],
            )

        for idx_ring in [6, 7, 8]:
            list_router_in_main[idx_ring].cardinal_router(
                list_in_router_path[idx_ring] +
                [list_center_left[idx_ring]],
            )

            list_router_out_main[idx_ring].cardinal_router(
                list_out_router_path[idx_ring] +
                [list_center_right[idx_ring]]
            )

        # for idx_ring in [7, 8]:
        #     list_router_in_main[idx_ring].cardinal_router(
        #         list_in_router_path[idx_ring]
        #         +
        #         [self.inst_list[idx_ring][in_port_name].center],
        #     )
        #
        #     list_router_out_main[idx_ring].cardinal_router(
        #         list_out_router_path[idx_ring]
        #         +
        #         [self.inst_list[idx_ring][out_port_name].center]
        #     )
class TripleRingRowWithLNANoDropForceRouting2(PhotonicTemplateBase):
    """
    Photonic Ports:
    IN = left side
    OUT = right side
    """

    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)
        self.params = params

        for key, val in self.params.items():  # Automatically unpack variables
            # exec( "self.{} = {}".format( key, val ) )
            exec(f"self.{key} = {val!r}")

        if self.with_drop_ports:
            self.track_pitch_mod = self.track_pitch
            self.y_coupler_pitch_mod = self.y_coupler_pitch
        else:
            self.track_pitch_mod = self.track_pitch / 2
            self.y_coupler_pitch_mod = self.y_coupler_pitch / 2

        # ================================================================
        # Create all templates (may need them to get geometry parameters)
        # ================================================================

        # Create class of each device component
        gc_module = importlib.import_module(self.grating_coupler_module)
        gc_class = getattr(gc_module, self.grating_coupler_class)
        self.gc_master = self.new_template(params=None, temp_cls=gc_class)
        # self.gc_array_inst = [None] * self.grating_coupler_num

        self.bend_radius = self.photonic_tech_info.get_default_wg_params(self.wg_routing_layer)['radius'] + 0.1
        self.routing_width = self.photonic_tech_info.get_default_wg_params(self.wg_routing_layer)['width']

    @classmethod
    def get_params_info(cls):
        return dict(

            grating_coupler_module=None,
            grating_coupler_class=None,


        )

    @classmethod
    def get_default_param_values(cls):
        return dict(
        )

    def adjust_location(self, loc, rotation):
        if rotation == 'R0':
            return ( loc[0],  loc[1])
        elif rotation == 'R90':
            return (-loc[1],  loc[0])
        elif rotation == 'R180':
            return (-loc[0], -loc[1])
        elif rotation == 'R270':
            return ( loc[1], -loc[0])
        elif rotation == 'MX':
            return ( loc[0], -loc[1])
        elif rotation == 'MY':
            return (-loc[0],  loc[1])
        elif rotation == 'MXR90':
            return ( loc[1],  loc[0])
        else:
            return (-loc[1], -loc[0])


    def adjust_rotation_and_location(self, bound_box, loc_in, loc_out):
        loc_center = ((bound_box.left+bound_box.right)/2.0,
                      (bound_box.top+bound_box.bottom)/2.0)
        if loc_out[1] == loc_in[1]:
            # R0, R180, MX or MY
            if loc_out[0] > loc_in[0]:
                # no need to do MY related thing
                loc_in_extend = (bound_box.left, loc_in[1])
                loc_out_extend = (bound_box.right, loc_out[1])
                if loc_out[1] <= loc_center[1]:
                    rotation = 'R0'
                else:
                    rotation = 'MX'
            else:
                # need to MY
                loc_in_extend = (bound_box.right, loc_in[1])
                loc_out_extend = (bound_box.left, loc_out[1])
                if loc_out[1] <= loc_center[1]:
                    rotation = 'MY'
                else:
                    rotation = 'R180'
        else:
            # R90, R270, MXR90 or MYR90
            if loc_out[1] > loc_in[1]:
                loc_in_extend = (loc_in[0], bound_box.bottom)
                loc_out_extend = (loc_out[0], bound_box.top)
                # no need to do MY related thing
                if loc_out[0] >= loc_center[0]:
                    rotation = 'R270'
                else:
                    rotation = 'MXR90'
            else:
                # need to MY
                loc_in_extend = (loc_in[0], bound_box.top)
                loc_out_extend = (loc_out[0], bound_box.bottom)
                if loc_out[0] >= loc_center[0]:
                    rotation = 'MYR90'
                else:
                    rotation = 'R90'
        loc_in_adj = self.adjust_location(loc_in, rotation)
        loc_out_adj = self.adjust_location(loc_out, rotation)
        loc_in_extend_adj = self.adjust_location(loc_in_extend, rotation)
        loc_out_extend_adj = self.adjust_location(loc_out_extend, rotation)
        loc_in_extend_adj = self.adjust_location(loc_in, rotation)
        loc_out_extend_adj = self.adjust_location(loc_out, rotation)
        return rotation, loc_in_adj, loc_out_adj, loc_in_extend_adj, loc_out_extend_adj

    def adjust_rotation_and_location_from_master(self, master, in_port_name, out_port_name):
        port_in = master.get_photonic_port(in_port_name)
        port_out = master.get_photonic_port(out_port_name)
        # gdad
        loc_in = port_in.center
        loc_out = port_out.center
        bound_box = master.bound_box
        loc_center = ((bound_box.left+bound_box.right)/2.0,
                      (bound_box.top+bound_box.bottom)/2.0)
        print(port_in.angle, abs((port_in.angle+180)%180 - 90))
        if (abs(port_in.angle) < 1e-3) or (abs(port_in.angle-np.pi) < 1e-3):
            # R0, R180, MX or MY
            if loc_out[0] > loc_in[0]:
                # no need to do MY related thing
                loc_in_extend = (bound_box.left, loc_in[1])
                loc_out_extend = (bound_box.right, loc_out[1])
                if loc_out[1] <= loc_center[1]:
                    rotation = 'R0'
                else:
                    rotation = 'MX'
            else:
                # need to MY
                loc_in_extend = (bound_box.right, loc_in[1])
                loc_out_extend = (bound_box.left, loc_out[1])
                if loc_out[1] <= loc_center[1]:
                    rotation = 'MY'
                else:
                    rotation = 'R180'
        else:
            # R90, R270, MXR90 or MYR90
            if loc_out[1] > loc_in[1]:
                loc_in_extend = (loc_in[0], bound_box.bottom)
                loc_out_extend = (loc_out[0], bound_box.top)
                # no need to do MY related thing
                if loc_out[0] >= loc_center[0]:
                    rotation = 'R270'
                else:
                    rotation = 'MXR90'
            else:
                # need to MY
                loc_in_extend = (loc_in[0], bound_box.top)
                loc_out_extend = (loc_out[0], bound_box.bottom)
                if loc_out[0] >= loc_center[0]:
                    rotation = 'MYR90'
                else:
                    rotation = 'R90'
        loc_in_adj = self.adjust_location(loc_in, rotation)
        loc_out_adj = self.adjust_location(loc_out, rotation)
        loc_in_extend_adj = self.adjust_location(loc_in_extend, rotation)
        loc_out_extend_adj = self.adjust_location(loc_out_extend, rotation)
        loc_in_extend_adj = self.adjust_location(loc_in, rotation)
        loc_out_extend_adj = self.adjust_location(loc_out, rotation)
        return rotation, loc_in_adj, loc_out_adj, loc_in_extend_adj, loc_out_extend_adj

    def get_inst_and_track_locations(self):

        self.n_site = 9
        x_port_coupler_in_base = self.x_port_coupler_in_base
        x_port_coupler_out_base = self.dx_design - x_port_coupler_in_base - self.x_coupler_pitch * 2

        #### define index of coupler port positions from left to right, the i-th element is
        #### the index of coupler port position of the i-th site
        list_idx_x_port_coupler_in = [0, 0, 1, 1, 2, 2, 0, 1, 2]
        list_idx_x_port_coupler_out = [1, 1, 0, 0, 2, 2, 1, 0, 2]
        list_idx_y_port_coupler = [1, 0, 0, 1, 0, 1, 0, 0, 0]

        # define coupler port coordinates
        self.list_x_port_coupler_in = [
            x_port_coupler_in_base +
            list_idx_x_port_coupler_in[i] * self.x_coupler_pitch for i in range(0, self.n_site)
        ]
        self.list_x_port_coupler_out = [
            x_port_coupler_out_base +
            list_idx_x_port_coupler_out[i] * self.x_coupler_pitch for i in range(0, self.n_site)
        ]
        self.list_y_port_coupler_main = [
            (self.y_port_coupler_base[0] if (i <= 5) else self.y_port_coupler_base[1]) +
            list_idx_y_port_coupler[i] * self.y_coupler_pitch_mod * 2 for i in range(0, self.n_site)
        ]
        self.list_y_port_coupler_drop = [
            self.list_y_port_coupler_main[i] + self.y_coupler_pitch_mod for i in range(0, self.n_site)
        ]





    def draw_layout(self):

        # print(self.yaml_list)
        self.get_site_specs()
        self.get_inst_and_track_locations()
        self.place_instances()
        self.create_ports()
        self.wg_routing()


    def get_site_specs(self):
        # instantiate the ring modulator masters
        self.list_inst_direction = []
        self.list_dx_inst = []
        # list_dy_inst = []
        self.list_x_inst_in_offset = []
        self.list_x_inst_out_offset = []
        self.list_x_inst_in_extend_offset = []
        self.list_x_inst_out_extend_offset = []
        self.list_y_inst_in_offset = []
        self.list_y_inst_out_offset = []
        self.master_list = []
        self.in_port_name = 'PORT0'
        self.out_port_name = 'PORT1'

        in_port_name = 'PORT0'
        out_port_name = 'PORT1'
        for ind, yaml_tuple in enumerate(self.yaml_list):
            yaml_file = yaml_tuple[0]
            yaml_rotation = yaml_tuple[1]
            if yaml_file != 'VOID':
                with open(yaml_file, 'r') as f:
                    yaml_content = yaml.load(f)

                lay_module = importlib.import_module(yaml_content['layout_package'])
                temp_cls = getattr(lay_module, yaml_content['layout_class'])

                master = self.new_template(params=yaml_content['layout_params'],
                                           temp_cls=temp_cls)

                master_in_port_loc = master.get_photonic_port(in_port_name).center
                master_out_port_loc = master.get_photonic_port(out_port_name).center

                rotation, loc_in_adj, loc_out_adj, loc_in_extend_adj, loc_out_extend_adj = \
                    self.adjust_rotation_and_location(master.bound_box, master_in_port_loc, master_out_port_loc)
                rotation_old, loc_in_adj_old, loc_out_adj_old, loc_in_extend_adj_old, loc_out_extend_adj_old = \
                    rotation, loc_in_adj, loc_out_adj, loc_in_extend_adj, loc_out_extend_adj

                rotation, loc_in_adj, loc_out_adj, loc_in_extend_adj, loc_out_extend_adj = \
                    self.adjust_rotation_and_location_from_master(master, in_port_name, out_port_name)
                # print('COMPARE (old):', ind, rotation_old, loc_in_adj_old, loc_out_adj_old, loc_in_extend_adj_old, loc_out_extend_adj_old)
                #
                # print('COMPARE (new):', ind, rotation, loc_in_adj, loc_out_adj, loc_in_extend_adj, loc_out_extend_adj)
                self.master_list.append(master)
                rotation_override = yaml_rotation[1:] if yaml_rotation[0] == 'O' else rotation
                self.list_inst_direction.append(rotation_override)
                self.list_y_inst_in_offset.append(loc_in_adj[1])
                self.list_y_inst_out_offset.append(loc_out_adj[1])
                self.list_x_inst_in_offset.append(loc_in_adj[0])
                self.list_x_inst_out_offset.append(loc_out_adj[0])
                self.list_x_inst_in_extend_offset.append(loc_in_extend_adj[0])
                self.list_x_inst_out_extend_offset.append(loc_out_extend_adj[0])
                self.list_dx_inst.append(loc_out_extend_adj[0] - loc_in_extend_adj[0])

                # if ind==1:
                #     print('PRINT', master, rotation, loc_in_adj)
            else:
                self.master_list.append([])
                self.list_inst_direction.append('R0')
                self.list_y_inst_in_offset.append(0)
                self.list_y_inst_out_offset.append(0)
                self.list_x_inst_in_offset.append(0)
                self.list_x_inst_out_offset.append(0)
                self.list_x_inst_in_extend_offset.append(0)
                self.list_x_inst_out_extend_offset.append(0)
                self.list_dx_inst.append(0)


    def place_instances(self):
        # instantiate the grating couplers
        self.list_gc_in_main = [
            self.add_instance(
                master=self.gc_master,
                loc=(self.list_x_port_coupler_in[i],
                     self.list_y_port_coupler_main[i]),
                # Offset site by location of input port, to put input port at desired location
                orient='R0',
            )
        for i in range(0, self.n_site)]
        self.list_gc_out_main = [
            self.add_instance(
                master=self.gc_master,
                loc=(self.list_x_port_coupler_out[i],
                     self.list_y_port_coupler_main[i]),
                # Offset site by location of input port, to put input port at desired location
                orient='MY',
            )
        for i in range(0, self.n_site)]


        # instantiate the rings
        for i in range(0, self.n_site):

            y_inst = self.y_instance[0] if i < 6 else  self.y_instance[1]
            self.inst_list.append(
                self.add_instance(
                    master=self.master_list[i],
                    loc=(self.x_instance[i], y_inst),
                    orient=self.list_inst_direction[i],
                )

            )


    def create_ports(self):

        self.list_port_in_main = [
            self.add_photonic_port(
                name=f'IN_MAIN{i}',
                center=(self.list_x_port_coupler_in[i], self.list_y_port_coupler_main[i]),
                orient='R0',
                layer=self.wg_port_layer,
                width=self.routing_width
            )
            for i in range(0, self.n_site)
        ]
        self.list_port_out_main = [
            self.add_photonic_port(
                name=f'OUT_MAIN{i}',
                center=(self.list_x_port_coupler_out[i], self.list_y_port_coupler_main[i]),
                orient='R0',
                layer=self.wg_port_layer,
                width=self.routing_width
            )
            for i in range(0, self.n_site)
        ]


    def wg_routing(self):


        in_port_name = 'PORT0'
        out_port_name = 'PORT1'
        #### group 1
        list_router_in_main = [
            WgRouter(
                self,
                self.list_port_in_main[i],
                self.wg_routing_layer,
                route_in_port_dir=True
            )
            for i in range(0, self.n_site)
        ]
        list_router_out_main = [
            WgRouter(
                self,
                self.list_port_out_main[i],
                self.wg_routing_layer,
                route_in_port_dir=False
            )
            for i in range(0, self.n_site)
        ]

        list_in_router_path = self.in_path
        list_out_router_path = self.out_path



        #### group 1, 6 sites
        # main ports
        list_center_left = [(self.inst_list[idx_ring][in_port_name].center if
                            self.inst_list[idx_ring][in_port_name].center[0] < self.inst_list[idx_ring][out_port_name].center[0]
                            else self.inst_list[idx_ring][out_port_name].center) for idx_ring in range(0, 9)]
        list_center_right = [(self.inst_list[idx_ring][out_port_name].center if
                            self.inst_list[idx_ring][in_port_name].center[0] < self.inst_list[idx_ring][out_port_name].center[0]
                            else self.inst_list[idx_ring][in_port_name].center) for idx_ring in range(0, 9)]


        for idx_ring in range(0, 6):

            list_router_out_main[idx_ring].cardinal_router(
                list_out_router_path[idx_ring],
                # [self.inst_list[idx_ring][out_port_name].center]
            )

            list_router_out_main[idx_ring].add_fancy_s_bend(
                shift_left=-list_center_right[idx_ring][1]+list_out_router_path[idx_ring][-1][1],
                length=-list_center_right[idx_ring][0]+list_out_router_path[idx_ring][-1][0]
            )

        for idx_ring in [0, 1, 2]:
            list_router_in_main[idx_ring].cardinal_router(
                list_in_router_path[idx_ring],
            )

            list_router_in_main[idx_ring].add_fancy_s_bend(
                shift_left=list_center_left[idx_ring][1]-list_in_router_path[idx_ring][-1][1],
                length=list_center_left[idx_ring][0]-list_in_router_path[idx_ring][-1][0]
            )


        for idx_ring in [3, 4, 5]:
            list_router_in_main[idx_ring].cardinal_router(
                list_in_router_path[idx_ring]
                +
                [list_center_left[idx_ring]],
            )

        for idx_ring in [6, 7, 8]:
            list_router_in_main[idx_ring].cardinal_router(
                list_in_router_path[idx_ring] +
                [list_center_left[idx_ring]],
            )

            list_router_out_main[idx_ring].cardinal_router(
                list_out_router_path[idx_ring] +
                [list_center_right[idx_ring]]
            )

        # for idx_ring in [7, 8]:
        #     list_router_in_main[idx_ring].cardinal_router(
        #         list_in_router_path[idx_ring]
        #         +
        #         [self.inst_list[idx_ring][in_port_name].center],
        #     )
        #
        #     list_router_out_main[idx_ring].cardinal_router(
        #         list_out_router_path[idx_ring]
        #         +
        #         [self.inst_list[idx_ring][out_port_name].center]
        #     )





class TripleRingRowNoDropOld(PhotonicTemplateBase):
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
        # self.wg_port_layer = ('RX', 'port')
        # self.wg_routing_layer = ('RX', 'drawing')

        # self.package_class_param_list = self.params['package_class_param_list']
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

        self.bend_radius = self.photonic_tech_info.get_default_wg_params(self.wg_routing_layer)['radius']
        self.routing_width = self.photonic_tech_info.get_default_wg_params(self.wg_routing_layer)['width']

    @classmethod
    def get_params_info(cls):
        return dict(
            # package_class_param_list='',
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
            x_instance='',


        )

    @classmethod
    def get_default_param_values(cls):
        return dict(
        )

    def draw_layout(self):


        n_site = 3
        #### define coupler port positions
        list_idx_port_coupler_in = [0, 1, 2]
        list_idx_port_coupler_out = [1, 0, 2]
        list_x_port_coupler_in = [
            self.x_port_coupler_in_base + list_idx_port_coupler_in[i] * self.x_coupler_pitch for i in range(0, n_site)
        ]
        list_x_port_coupler_out = [
            self.x_port_coupler_out_base + list_idx_port_coupler_out[i] * self.x_coupler_pitch for i in range(0, n_site)
        ]
        list_y_port_coupler = [self.y_port_coupler_base]


        list_x_port_inst_in = [self.x_instance[i] - self.dx_inst / 2 for i in range(0, n_site)]
        list_x_port_inst_out = [self.x_instance[i] + self.dx_inst / 2 for i in range(0, n_site)]


        # 4 long horizontal waveguide tracks on the bottom side of the instances
        list_y_track_bot = [self.track_pitch * (i+1) for i in range(0, 3)]
        # horizontal track the bottom ports of the instances are on
        y_port_inst_bot = list_y_track_bot[-1] + self.track_pitch + self.dy_port_inst_bot

        # check if these positions are appropriate
        if (list_x_port_coupler_in[0] < self.x_coupler_clear):
            raise ValueError('Input Coupler x coordinate is too low')
        if (list_y_port_coupler[0] < list_y_track_bot[0] + self.track_pitch + self.y_coupler_clear / 2):
            raise ValueError('Coupler y coordinate is too low, will conflict with waveguide routing')


        # 7 long horizontal waveguide tracks on the top side of the instances
        y_track_top_min = max(list_y_port_coupler[-1] + self.track_pitch + self.y_coupler_clear / 2,
                              list_y_track_bot[-1] + self.track_pitch * 2 + self.dy_inst)
        list_y_track_top = [i * self.track_pitch + y_track_top_min for i in range(0, 2)]



        # flag to trigger special routing because large bend radius
        flag_sp_routing_1 = (list_y_port_coupler[0] - list_y_track_bot[0]) < self.bend_radius * 2
        flag_sp_routing_2 = self.track_pitch * 2 < self.bend_radius * 2
        flag_sp_routing_3 = self.track_pitch * 4 < self.bend_radius * 2





        list_port_in_main = [
            self.add_photonic_port(
                name=f'IN_MAIN{i}',
                center=(list_x_port_coupler_in[i], list_y_port_coupler[0]),
                orient='R0',
                layer=self.wg_port_layer,
                width=self.routing_width
            )
            for i in range(0, n_site)
        ]

        list_port_out_main = [
            self.add_photonic_port(
                name=f'OUT_MAIN{i}',
                center=(list_x_port_coupler_out[i], list_y_port_coupler[0]),
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



        #### site 0
        idx_now = 0

        list_router_in_main[idx_now].cardinal_router(
            [
                (list_x_port_coupler_in[idx_now] + self.bend_radius * 1,
                 list_y_port_coupler[0] + self.bend_radius * 1),
                (list_x_port_inst_in[idx_now] - self.bend_radius * 2,
                 list_y_track_top[1]),
                (list_x_port_inst_in[idx_now] - self.bend_radius * 3,
                 y_port_inst_bot + self.bend_radius * 1),
                (list_x_port_inst_in[idx_now],
                 y_port_inst_bot),
            ]
        )



        list_router_out_main[idx_now].cardinal_router(
            [
                (list_x_port_coupler_out[idx_now] - self.bend_radius * 1,
                 list_y_port_coupler[0] + self.bend_radius),
                (list_x_port_coupler_out[idx_now] - self.bend_radius * 2,
                 list_y_track_top[1]),
                (list_x_port_inst_out[idx_now] + self.bend_radius * 3,
                 list_y_track_bot[2] + self.bend_radius),
                (list_x_port_inst_out[idx_now],
                 y_port_inst_bot),
            ]
        )





        #### site 1
        idx_now = 1

        router_path = [
            (list_x_port_coupler_in[idx_now] + self.bend_radius * 1,
             list_y_port_coupler[0] + self.bend_radius * 1),
            (list_x_port_coupler_in[idx_now+1] + self.bend_radius * 3,
             list_y_track_top[0]),
            (list_x_port_coupler_in[idx_now + 1] + self.bend_radius * 4,
             list_y_track_top[0] - self.bend_radius * 1),
            (list_x_port_inst_in[idx_now] - self.bend_radius * 4,
             list_y_track_bot[2]),
        ] + ([
            (list_x_port_inst_in[idx_now] - self.bend_radius * 3,
             y_port_inst_bot + self.bend_radius * 1),
            (list_x_port_inst_in[idx_now] - self.bend_radius * 2,
             y_port_inst_bot + self.bend_radius * 2),
            (list_x_port_inst_in[idx_now] - self.bend_radius * 1,
             y_port_inst_bot + self.bend_radius * 1),
            (list_x_port_inst_in[idx_now],
             y_port_inst_bot),
        ] if flag_sp_routing_2 else [
            (list_x_port_inst_in[idx_now] - self.bend_radius * 1,
             y_port_inst_bot - self.bend_radius * 1),
            (list_x_port_inst_in[idx_now],
             y_port_inst_bot),

        ])

        list_router_in_main[idx_now].cardinal_router(router_path)




        list_router_out_main[idx_now].cardinal_router([
            (list_x_port_coupler_out[idx_now] - self.bend_radius * 1,
             list_y_port_coupler[0] + self.bend_radius),
            (list_x_port_coupler_out[idx_now] - self.bend_radius * 2,
             list_y_track_top[0]),
            (list_x_port_inst_out[idx_now] + self.bend_radius * 3,
             list_y_track_bot[1] - self.bend_radius),
            (list_x_port_inst_out[idx_now],
             y_port_inst_bot),
        ])


        #### site 2
        idx_now = 2

        router_path = ([
            (list_x_port_coupler_in[idx_now] + self.bend_radius * 1,
             list_y_port_coupler[0] + self.bend_radius * 1),
            (list_x_port_coupler_in[idx_now] + self.bend_radius * 2,
             list_y_port_coupler[0] + self.bend_radius * 2),
            (list_x_port_coupler_in[idx_now] + self.bend_radius * 3,
             list_y_port_coupler[0] + self.bend_radius * 1),
        ] if flag_sp_routing_1 else [
            (list_x_port_coupler_in[idx_now] + self.bend_radius * 1,
             list_y_port_coupler[0] - self.bend_radius * 1),
        ]) + [
            (list_x_port_inst_in[idx_now] - self.bend_radius * 4,
             list_y_track_bot[0])
        ] +  ([
            (list_x_port_inst_in[idx_now] - self.bend_radius * 3,
             list_y_track_bot[0] + self.bend_radius * 1),
            (list_x_port_inst_in[idx_now] - self.bend_radius * 2,
             y_port_inst_bot + self.bend_radius * 2),
            (list_x_port_inst_in[idx_now] - self.bend_radius * 1,
             y_port_inst_bot + self.bend_radius * 1),
            (list_x_port_inst_in[idx_now],
             y_port_inst_bot),
        ] if flag_sp_routing_3 else [
            (list_x_port_inst_in[idx_now] - self.bend_radius * 1,
             y_port_inst_bot - self.bend_radius * 1),
            (list_x_port_inst_in[idx_now],
             y_port_inst_bot),
        ])

        list_router_in_main[idx_now].cardinal_router(router_path)


        router_path = ([
            (list_x_port_coupler_out[idx_now] - self.bend_radius * 1,
             list_y_port_coupler[0] + self.bend_radius * 1),
            (list_x_port_coupler_out[idx_now] - self.bend_radius * 2,
             list_y_port_coupler[0] + self.bend_radius * 2),
            (list_x_port_coupler_out[idx_now] - self.bend_radius * 3,
             list_y_port_coupler[0] + self.bend_radius * 1),
        ] if flag_sp_routing_1 else [
            (list_x_port_coupler_out[idx_now] - self.bend_radius * 1,
             list_y_port_coupler[0] - self.bend_radius * 1),
        ]) + [
            (list_x_port_inst_out[idx_now] + self.bend_radius * 4,
             list_y_track_bot[0])
        ] +  ([
            (list_x_port_inst_out[idx_now] + self.bend_radius * 3,
             list_y_track_bot[0] + self.bend_radius * 1),
            (list_x_port_inst_out[idx_now] + self.bend_radius * 2,
             y_port_inst_bot + self.bend_radius * 2),
            (list_x_port_inst_out[idx_now] + self.bend_radius * 1,
             y_port_inst_bot + self.bend_radius * 1),
            (list_x_port_inst_out[idx_now],
             y_port_inst_bot),
        ] if flag_sp_routing_3 else [
            (list_x_port_inst_out[idx_now] + self.bend_radius * 1,
             y_port_inst_bot - self.bend_radius),
            (list_x_port_inst_out[idx_now],
             y_port_inst_bot),
        ])


        list_router_out_main[idx_now].cardinal_router(router_path)


class TripleRingRowNoDrop(PhotonicTemplateBase):
    """
    Photonic Ports:
    IN = left side
    OUT = right side
    """

    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)
        self.params = params

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

        self.bend_radius = self.photonic_tech_info.get_default_wg_params(self.wg_routing_layer)['radius'] + 0.002
        self.routing_width = self.photonic_tech_info.get_default_wg_params(self.wg_routing_layer)['width']

    @classmethod
    def get_params_info(cls):
        return dict(
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


        )

    @classmethod
    def get_default_param_values(cls):
        return dict(
        )

    def adjust_location(self, loc, rotation):
        if rotation == 'R0':
            return ( loc[0],  loc[1])
        elif rotation == 'R90':
            return (-loc[1],  loc[0])
        elif rotation == 'R180':
            return (-loc[0], -loc[1])
        elif rotation == 'R270':
            return ( loc[1], -loc[0])
        elif rotation == 'MX':
            return ( loc[0], -loc[1])
        elif rotation == 'MY':
            return (-loc[0],  loc[1])
        elif rotation == 'MXR90':
            return ( loc[1],  loc[0])
        else:
            return (-loc[1], -loc[0])


    def adjust_rotation_and_location(self, bound_box, loc_in, loc_out):
        loc_center = ((bound_box.left+bound_box.right)/2.0,
                      (bound_box.top+bound_box.bottom)/2.0)
        if loc_out[1] == loc_in[1]:
            # R0, R180, MX or MY
            if loc_out[0] > loc_in[0]:
                # no need to do MY related thing
                loc_in_extend = (bound_box.left, loc_in[1])
                loc_out_extend = (bound_box.right, loc_out[1])
                if loc_out[1] <= loc_center[1]:
                    rotation = 'R0'
                else:
                    rotation = 'MX'
            else:
                # need to MY
                loc_in_extend = (bound_box.right, loc_in[1])
                loc_out_extend = (bound_box.left, loc_out[1])
                if loc_out[1] <= loc_center[1]:
                    rotation = 'MY'
                else:
                    rotation = 'R180'
        else:
            # R90, R270, MXR90 or MYR90
            if loc_out[1] > loc_in[1]:
                loc_in_extend = (loc_in[0], bound_box.bottom)
                loc_out_extend = (loc_out[0], bound_box.top)
                # no need to do MY related thing
                if loc_out[0] >= loc_center[0]:
                    rotation = 'R270'
                else:
                    rotation = 'MXR90'
            else:
                # need to MY
                loc_in_extend = (loc_in[0], bound_box.top)
                loc_out_extend = (loc_out[0], bound_box.bottom)
                if loc_out[0] >= loc_center[0]:
                    rotation = 'MYR90'
                else:
                    rotation = 'R90'
        loc_in_adj = self.adjust_location(loc_in, rotation)
        loc_out_adj = self.adjust_location(loc_out, rotation)
        loc_in_extend_adj = self.adjust_location(loc_in_extend, rotation)
        loc_out_extend_adj = self.adjust_location(loc_out_extend, rotation)
        loc_in_extend_adj = self.adjust_location(loc_in, rotation)
        loc_out_extend_adj = self.adjust_location(loc_out, rotation)
        return rotation, loc_in_adj, loc_out_adj, loc_in_extend_adj, loc_out_extend_adj

    def adjust_rotation_and_location_from_master(self, master, in_port_name, out_port_name):
        port_in = master.get_photonic_port(in_port_name)
        port_out = master.get_photonic_port(out_port_name)
        # gdad
        loc_in = port_in.center
        loc_out = port_out.center
        bound_box = master.bound_box
        loc_center = ((bound_box.left+bound_box.right)/2.0,
                      (bound_box.top+bound_box.bottom)/2.0)
        # print(port_in.angle, abs((port_in.angle+180)%180 - 90))
        if (abs(port_in.angle) < 1e-3) or (abs(port_in.angle-np.pi) < 1e-3):
            # R0, R180, MX or MY
            if loc_out[0] > loc_in[0]:
                # no need to do MY related thing
                loc_in_extend = (bound_box.left, loc_in[1])
                loc_out_extend = (bound_box.right, loc_out[1])
                if loc_out[1] <= loc_center[1]:
                    rotation = 'R0'
                else:
                    rotation = 'MX'
            else:
                # need to MY
                loc_in_extend = (bound_box.right, loc_in[1])
                loc_out_extend = (bound_box.left, loc_out[1])
                if loc_out[1] <= loc_center[1]:
                    rotation = 'MY'
                else:
                    rotation = 'R180'
        else:
            # R90, R270, MXR90 or MYR90
            if loc_out[1] > loc_in[1]:
                loc_in_extend = (loc_in[0], bound_box.bottom)
                loc_out_extend = (loc_out[0], bound_box.top)
                # no need to do MY related thing
                if loc_out[0] >= loc_center[0]:
                    rotation = 'R270'
                else:
                    rotation = 'MXR90'
            else:
                # need to MY
                loc_in_extend = (loc_in[0], bound_box.top)
                loc_out_extend = (loc_out[0], bound_box.bottom)
                if loc_out[0] >= loc_center[0]:
                    rotation = 'MYR90'
                else:
                    rotation = 'R90'
        loc_in_adj = self.adjust_location(loc_in, rotation)
        loc_out_adj = self.adjust_location(loc_out, rotation)
        loc_in_extend_adj = self.adjust_location(loc_in_extend, rotation)
        loc_out_extend_adj = self.adjust_location(loc_out_extend, rotation)
        loc_in_extend_adj = self.adjust_location(loc_in, rotation)
        loc_out_extend_adj = self.adjust_location(loc_out, rotation)
        return rotation, loc_in_adj, loc_out_adj, loc_in_extend_adj, loc_out_extend_adj

    def draw_layout(self):

        # instantiate the ring modulator masters
        list_inst_direction = []
        list_dx_inst = []
        # list_dy_inst = []
        list_x_inst_in_offset = []
        list_x_inst_out_offset = []
        list_x_inst_in_extend_offset = []
        list_x_inst_out_extend_offset = []
        list_y_inst_in_offset = []
        list_y_inst_out_offset = []

        in_port_name = 'PORT0'
        out_port_name = 'PORT1'
        for ind, yaml_tuple in enumerate(self.yaml_list):
            yaml_file = yaml_tuple[0]
            yaml_direction = yaml_tuple[1]
            if yaml_file != 'VOID':
                with open(yaml_file, 'r') as f:
                    yaml_content = yaml.load(f)

                lay_module = importlib.import_module(yaml_content['layout_package'])
                temp_cls = getattr(lay_module, yaml_content['layout_class'])

                master = self.new_template(params=yaml_content['layout_params'],
                                           temp_cls=temp_cls)

                master_in_port_loc = master.get_photonic_port(in_port_name).center
                master_out_port_loc = master.get_photonic_port(out_port_name).center

                rotation, loc_in_adj, loc_out_adj, loc_in_extend_adj, loc_out_extend_adj = \
                    self.adjust_rotation_and_location(master.bound_box, master_in_port_loc, master_out_port_loc)
                rotation_old, loc_in_adj_old, loc_out_adj_old, loc_in_extend_adj_old, loc_out_extend_adj_old = \
                    rotation, loc_in_adj, loc_out_adj, loc_in_extend_adj, loc_out_extend_adj

                rotation, loc_in_adj, loc_out_adj, loc_in_extend_adj, loc_out_extend_adj = \
                    self.adjust_rotation_and_location_from_master(master, in_port_name, out_port_name)
                print('COMPARE (old):', ind, rotation_old, loc_in_adj_old, loc_out_adj_old, loc_in_extend_adj_old, loc_out_extend_adj_old)

                print('COMPARE (new):', ind, rotation, loc_in_adj, loc_out_adj, loc_in_extend_adj, loc_out_extend_adj)
                self.master_list.append(master)
                list_inst_direction.append(rotation)
                list_y_inst_in_offset.append(loc_in_adj[1])
                list_y_inst_out_offset.append(loc_out_adj[1])
                list_x_inst_in_offset.append(loc_in_adj[0])
                list_x_inst_out_offset.append(loc_out_adj[0])
                list_x_inst_in_extend_offset.append(loc_in_extend_adj[0])
                list_x_inst_out_extend_offset.append(loc_out_extend_adj[0])
                list_dx_inst.append(loc_out_extend_adj[0] - loc_in_extend_adj[0])

                if ind==1:
                    print('PRINT', master, rotation, loc_in_adj)
            else:
                self.master_list.append([])
                list_inst_direction.append('R0')
                list_y_inst_in_offset.append(0)
                list_y_inst_out_offset.append(0)
                list_x_inst_in_offset.append(0)
                list_x_inst_out_offset.append(0)
                list_x_inst_in_extend_offset.append(0)
                list_x_inst_out_extend_offset.append(0)
                list_dx_inst.append(0)


        n_site = 3
        #### define coupler port positions
        list_idx_port_coupler_in = [0, 1, 2]
        list_idx_port_coupler_out = [1, 0, 2]
        list_x_port_coupler_in = [
            self.x_port_coupler_in_base + list_idx_port_coupler_in[i] * self.x_coupler_pitch for i in range(0, n_site)
        ]
        list_x_port_coupler_out = [
            self.x_port_coupler_out_base + list_idx_port_coupler_out[i] * self.x_coupler_pitch for i in range(0, n_site)
        ]
        list_y_port_coupler = [
            self.y_port_coupler_base + i * self.y_coupler_pitch for i in range(0, 2)
        ]


        list_x_port_inst_in = [self.x_instance[i] + list_x_inst_in_offset[i] for i in range(0, n_site)]
        list_x_port_inst_out = [self.x_instance[i] + list_x_inst_out_offset[i] for i in range(0, n_site)]
        list_x_port_inst_in_extend = [self.x_instance[i] + list_x_inst_in_extend_offset[i] for i in range(0, n_site)]
        list_x_port_inst_out_extend = [self.x_instance[i] + list_x_inst_out_extend_offset[i] for i in range(0, n_site)]


        # y_track_inst_bot = 3 * self.track_pitch
        # y_track_inst_top_min = y_track_inst_bot + dy_inst_port_min

        # 4 long horizontal waveguide tracks on the bottom side of the instances
        list_y_track_bot = [self.track_pitch * (i+1) for i in range(0, 5)]
        # horizontal track the bottom ports of the instances are on
        y_port_inst_bot = list_y_track_bot[-1] + self.dy_port_inst_bot

        # check if these positions are appropriate
        if (list_x_port_coupler_in[0] < self.x_coupler_clear):
            raise ValueError('Input Coupler x coordinate is too low')
        if (list_y_port_coupler[0] < list_y_track_bot[1] + self.track_pitch + self.y_coupler_clear / 2):
            raise ValueError('Coupler y coordinate is too low, will conflict with waveguide routing')


        # 7 long horizontal waveguide tracks on the top side of the instances
        y_track_top_min = max(list_y_port_coupler[1] + self.track_pitch + self.y_coupler_clear / 2,
                              list_y_track_bot[4] + self.dy_inst + self.track_pitch * 1)
        list_y_track_top = [i * self.track_pitch + y_track_top_min for i in range(0, 4)]
        y_port_inst_top = list_y_track_top[3]
        y_port_inst_top = list_y_track_bot[4] + self.dy_port_inst_top


        # flag to trigger special routing because large bend radius
        flag_sp_routing_1 = (list_y_port_coupler[0] - list_y_track_bot[0]) < self.bend_radius * 2
        flag_sp_routing_2 = self.track_pitch * 2 < self.bend_radius * 2
        flag_sp_routing_3 = self.track_pitch * 4 < self.bend_radius * 2

        # instantiate the frating couplers
        list_gc_in_main = [
            self.add_instance(
                master=self.gc_master,
                loc=(list_x_port_coupler_in[i],
                     list_y_port_coupler[0]),
                # Offset site by location of input port, to put input port at desired location
                orient='R0',
            )
        for i in range(0, n_site)]

        list_gc_out_main = [
            self.add_instance(
                master=self.gc_master,
                loc=(list_x_port_coupler_out[i],
                     list_y_port_coupler[0]),
                # Offset site by location of input port, to put input port at desired location
                orient='MY',
            )
        for i in range(0, n_site)]

        list_y_inst_in = [y_port_inst_bot for i in range(0, n_site)]
        list_y_inst_out = [y_port_inst_bot for i in range(0, n_site)]

        # instantiate the rings
        for i in range(0, n_site):
            if list_dx_inst[i] != 0:
                master_in_port_loc = self.master_list[i].get_photonic_port(in_port_name).center
                y_inst_rotated = (list_y_track_top[-1] + list_y_track_bot[0]) / 2
                if list_y_inst_in_offset[i] == list_y_inst_out_offset[i]:
                    # y_inst = list_y_track_top[1] - self.track_pitch * i - self.bend_radius * 2 - list_y_inst_in_offset[i]
                    y_inst = list_y_track_bot[2-i] + self.bend_radius * 2 - list_y_inst_in_offset[i]
                    list_y_inst_in[i] = y_inst + list_y_inst_in_offset[i]
                    list_y_inst_out[i] = y_inst + list_y_inst_out_offset[i]
                else:
                    # y_inst = list_y_track_bot[2-i] + self.bend_radius * 2 - min(list_y_inst_in_offset[i],list_y_inst_out_offset[i])
                    y_inst = list_y_track_top[1] - self.track_pitch * i - max(list_y_inst_in_offset[i],list_y_inst_out_offset[i])
                    list_y_inst_in[i] = y_inst + list_y_inst_in_offset[i]
                    list_y_inst_out[i] = y_inst + list_y_inst_out_offset[i]

                self.inst_list.append(
                    self.add_instance(
                        master=self.master_list[i],
                        # loc=(self.x_instance[i], y_port_inst_bot - list_y_inst_port_offset[i]),
                        loc=(self.x_instance[i], y_inst),
                        orient=list_inst_direction[i],
                    )
                )



        list_port_in_main = [
            self.add_photonic_port(
                name=f'IN_MAIN{i}',
                center=(list_x_port_coupler_in[i], list_y_port_coupler[0]),
                orient='R0',
                layer=self.wg_port_layer,
                width=self.routing_width
            )
            for i in range(0, n_site)
        ]

        list_port_out_main = [
            self.add_photonic_port(
                name=f'OUT_MAIN{i}',
                center=(list_x_port_coupler_out[i], list_y_port_coupler[0]),
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



        for idx_now in range(0, n_site):

            y_track_in_1st = list_y_track_top[1] if idx_now==0 else (list_y_track_top[0] if idx_now==1 else list_y_track_bot[0])
            y_track_out_1st = list_y_track_top[1] if idx_now==0 else (list_y_track_top[0] if idx_now==1 else list_y_track_bot[0])
            y_track_in_fin = list_y_track_top[1] if idx_now==0 else (list_y_track_bot[1] if idx_now==1 else list_y_track_bot[0])


            list_router_in_main[idx_now].add_fancy_s_bend(shift_left=(y_track_in_1st - list_y_port_coupler[0]))
            list_router_out_main[idx_now].add_fancy_s_bend(shift_left=-(y_track_out_1st - list_y_port_coupler[0]))

            list_router_in_main[idx_now].cardinal_router(
                [(list_x_port_inst_in_extend[idx_now] - self.bend_radius * 3, y_track_in_1st)
                 if idx_now != 1 else
                 (list_x_port_inst_in_extend[0] - self.bend_radius * 5, y_track_in_1st)]
            )

            list_router_out_main[idx_now].cardinal_router(
                [(list_x_port_inst_out_extend[idx_now] + self.bend_radius * 4, y_track_out_1st)]
            )

            if (idx_now == 1):
                list_router_in_main[idx_now].add_fancy_s_bend(shift_left=(list_y_track_bot[1] - y_track_in_1st))

                list_router_in_main[idx_now].cardinal_router(
                    [(list_x_port_inst_in_extend[idx_now] - self.bend_radius * 4, list_y_track_bot[1])]
                )



            list_router_in_main[idx_now].add_fancy_s_bend(shift_left=(list_y_inst_in[idx_now] - y_track_in_fin))
            list_router_out_main[idx_now].add_fancy_s_bend(shift_left=-(list_y_inst_out[idx_now] - y_track_out_1st))

            list_router_in_main[idx_now].cardinal_router(
                [(list_x_port_inst_in[idx_now], list_y_inst_in[idx_now])]
            )

            list_router_out_main[idx_now].cardinal_router(
                [(list_x_port_inst_out[idx_now], list_y_inst_out[idx_now])]
            )


class TripleRingRow(PhotonicTemplateBase):
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
        # self.wg_port_layer = ('RX', 'port')
        # self.wg_routing_layer = ('RX', 'drawing')

        # self.package_class_param_list = self.params['package_class_param_list']
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
        self.dy_port_inst_bot = self.params['dy_port_inst_bot']
        self.x_instance = self.params['x_instance']

        self.bend_radius = self.photonic_tech_info.get_default_wg_params(self.wg_routing_layer)['radius']
        self.routing_width = self.photonic_tech_info.get_default_wg_params(self.wg_routing_layer)['width']

    @classmethod
    def get_params_info(cls):
        return dict(
            # package_class_param_list='',
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
            x_instance='',


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


        n_site = 3
        #### define coupler port positions
        list_idx = [0, 2, 1]
        list_x_port_coupler_in = [
            self.x_port_coupler_in_base + list_idx[i] * self.x_coupler_pitch for i in range(0, n_site)
        ]
        list_x_port_coupler_out = [
            self.x_port_coupler_out_base + list_idx[i] * self.x_coupler_pitch for i in range(0, n_site)
        ]
        list_y_port_coupler = [
            self.y_port_coupler_base + i * self.y_coupler_pitch for i in range(0, 2)
        ]

        # x_coupler_port_in = self.x_coupler_port_in_base + [0, ]
        # y_coupler_port = self.y_coupler_port
        # dx_inst_port_min = self.dx_inst_port_min
        # dy_inst_port_min = self.dy_inst_port_min
        list_x_port_inst_in = [self.x_instance[i] - self.dx_inst / 2 for i in range(0, n_site)]
        list_x_port_inst_out = [self.x_instance[i] + self.dx_inst / 2 for i in range(0, n_site)]


        # y_track_inst_bot = 3 * self.track_pitch
        # y_track_inst_top_min = y_track_inst_bot + dy_inst_port_min

        # 4 long horizontal waveguide tracks on the bottom side of the instances
        list_y_track_bot = [self.track_pitch * (i+1) for i in range(0, 4)]
        # horizontal track the bottom ports of the instances are on
        # list_y_port_inst_bot = [list_y_track_bot[2], list_y_track_bot[0], list_y_track_bot[2]]
        # list_y_port_inst_top = [
        #     self.dy_inst + y_port_inst_bot for y_port_inst_bot in list_y_port_inst_bot
        # ]
        list_y_port_inst_bot = [list_y_track_bot[2] + self.dy_port_inst_bot for i in range(0, 3)]
        list_y_port_inst_top = [list_y_track_bot[2] + self.dy_inst for i in range(0, 3)]

        # TODO: check if these positions are appropriate
        if (list_x_port_coupler_in[0] < self.track_pitch * 3 + self.x_coupler_clear):
            raise ValueError('Input Coupler x coordinate is too low')
        if (list_y_port_coupler[0] < list_y_track_bot[-1] + self.track_pitch + self.y_coupler_clear / 2):
            raise ValueError('Coupler y coordinate is too low, will conflict with waveguide routing')

        # 7 long horizontal waveguide tracks on the top side of the instances
        list_y_track_top = [
            i * self.track_pitch + list_y_track_bot[2] + self.dy_inst for i in range(0, 7)
        ]

        if list_y_track_top[1] <= list_y_port_coupler[0]:
            y_track_temp = list_y_port_coupler[0]
        else:
            y_track_temp = max(list_y_track_top[1], list_y_port_coupler[0] + self.bend_radius * 2)
        list_y_track_top[1:] = [(y_track_temp - list_y_track_top[1]) + element for element in list_y_track_top[1:]]

        if list_y_track_top[2] <= list_y_port_coupler[1]:
            y_track_temp = list_y_port_coupler[1]
        else:
            y_track_temp = max(list_y_track_top[2], list_y_port_coupler[1] + self.bend_radius * 2)
        list_y_track_top[2:] = [(y_track_temp - list_y_track_top[2]) + element for element in list_y_track_top[2:]]

        y_track_temp = max(list_y_track_top[3],
                           list_y_port_coupler[0] + self.bend_radius * 2,
                           list_y_port_coupler[1] + self.y_coupler_clear / 2 + self.bend_radius)
        list_y_track_top[3:] = [(y_track_temp - list_y_track_top[3]) + element for element in list_y_track_top[3:]]

        y_track_temp = max(list_y_port_coupler[1] + self.bend_radius * 2, list_y_track_top[4])
        list_y_track_top[4:] = [(y_track_temp - list_y_track_top[4]) + element for element in list_y_track_top[4:]]

        # y_track_temp = max(list_y_port_coupler[1] + self.y_coupler_clear / 2 + self.bend_radius, list_y_track_top[5])
        # list_y_track_top[5:] = [(y_track_temp - list_y_track_top[5]) + element for element in list_y_track_top[5:]]


        # horizontal track the top ports of the instances are on
        # list_y_port_inst_top = [list_y_port_inst_bot[i] + self.dy_inst for i in range(0, n_site)]




        #
        # if y_track_inst_top_min <= y_coupler_port[1]:
        #     y_track_inst_top = y_coupler_port[1]
        # else:
        #     y_track_inst_top = y_coupler_port[1] + self.bend_radius * 2
        #
        # y_track_site1_top = max(y_track_inst_top, y_coupler_port[1]) + self.bend_radius * 2



        list_port_in_main = [
            self.add_photonic_port(
                name=f'IN_MAIN{i}',
                center=(list_x_port_coupler_in[i], list_y_port_coupler[0]),
                orient='R0',
                layer=self.wg_port_layer,
                width=self.routing_width
            )
            for i in range(0, n_site)
        ]
        list_port_in_drop = [
            self.add_photonic_port(
                name=f'IN_DROP{i}',
                center=(list_x_port_coupler_in[i], list_y_port_coupler[1]),
                orient='R0',
                layer=self.wg_port_layer,
                width=self.routing_width
            )

            for i in range(0, n_site)
        ]
        list_port_out_main = [
            self.add_photonic_port(
                name=f'OUT_MAIN{i}',
                center=(list_x_port_coupler_out[i], list_y_port_coupler[0]),
                orient='R0',
                layer=self.wg_port_layer,
                width=self.routing_width
            )
            for i in range(0, n_site)
        ]
        list_port_out_drop = [
            self.add_photonic_port(
                name=f'OUT_DROP{i}',
                center=(list_x_port_coupler_out[i], list_y_port_coupler[1]),
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
        list_router_in_drop = [
            WgRouter(
                self,
                list_port_in_drop[i],
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
        list_router_out_drop = [
            WgRouter(
                self,
                list_port_out_drop[i],
                self.wg_routing_layer,
                route_in_port_dir=False
            )
            for i in range(0, n_site)
        ]


        #### site 0
        idx_now = 0

        list_router_in_main[idx_now].cardinal_router(
            [
                (list_x_port_coupler_in[idx_now] + self.bend_radius * 1,
                 list_y_port_coupler[0] - self.bend_radius * 1),
                (list_x_port_inst_in[idx_now] - self.bend_radius * 4,
                 list_y_track_bot[2]),
                (list_x_port_inst_in[idx_now] - self.bend_radius * 3,
                 list_y_port_inst_bot[idx_now] + self.bend_radius * 1),
                (list_x_port_inst_in[idx_now] - self.bend_radius * 2,
                 list_y_port_inst_bot[idx_now] + self.bend_radius * 2),
                (list_x_port_inst_in[idx_now] - self.bend_radius * 1,
                 list_y_port_inst_bot[idx_now] + self.bend_radius * 1),
                (list_x_port_inst_in[idx_now],
                 list_y_port_inst_bot[idx_now])
            ]
        )
        list_router_in_drop[idx_now].cardinal_router(
            [
                (list_x_port_coupler_in[idx_now] + self.bend_radius * 1 + self.track_pitch,
                 list_y_port_coupler[1] - self.bend_radius * 1),
                (list_x_port_inst_in[idx_now] - self.bend_radius * 4 - self.track_pitch,
                 list_y_track_bot[3]),
                (list_x_port_inst_in[idx_now] - self.bend_radius * 3 - self.track_pitch,
                 list_y_port_inst_top[idx_now] - self.bend_radius * 1),
                (list_x_port_inst_in[idx_now],
                 list_y_port_inst_top[idx_now]),
            ]
        )

        list_router_out_main[idx_now].cardinal_router(
            [
                (list_x_port_coupler_out[idx_now] - self.bend_radius * 1 - self.track_pitch,
                 list_y_port_coupler[0] + self.bend_radius),
                (self.track_pitch * 2 + self.bend_radius,
                 list_y_track_top[-2]),
                (self.track_pitch * 2,
                 list_y_track_bot[1] + self.bend_radius),
                (list_x_port_inst_out[idx_now] + self.bend_radius * 2,
                 list_y_track_bot[1]),
                (list_x_port_inst_out[idx_now] + self.bend_radius * 3,
                 list_y_track_bot[1] + self.bend_radius * 1),
                (list_x_port_inst_out[idx_now] + self.bend_radius * 2,
                 list_y_port_inst_bot[idx_now] + self.bend_radius * 2),
                (list_x_port_inst_out[idx_now] + self.bend_radius * 1,
                 list_y_port_inst_bot[idx_now] + self.bend_radius * 1),
                (list_x_port_inst_out[idx_now],
                 list_y_port_inst_bot[idx_now]),
            ]
        )

        list_router_out_drop[idx_now].cardinal_router(
            [
                (list_x_port_coupler_out[idx_now] - self.bend_radius * 1,
                 list_y_port_coupler[1] + self.bend_radius),
                (self.track_pitch * 1 + self.bend_radius,
                 list_y_track_top[-1]),
                (self.track_pitch * 1,
                 list_y_track_bot[0] + self.bend_radius),
                (self.track_pitch * 1 + self.bend_radius,
                 list_y_track_bot[0]),
                (list_x_port_inst_out[idx_now] + self.bend_radius * 3 + self.track_pitch,
                 list_y_port_inst_top[idx_now] - self.bend_radius * 1),
                (list_x_port_inst_out[idx_now],
                 list_y_port_inst_top[idx_now]),
            ]
        )



        #### site 1
        idx_now = 1

        router_path = [
            (list_x_port_inst_in[idx_now] - self.bend_radius * 3 - self.track_pitch,
             list_y_port_inst_bot[idx_now] + self.bend_radius * 1),
            (list_x_port_inst_in[idx_now],
             list_y_port_inst_bot[idx_now]),
        ]
        if list_y_track_top[1] > list_y_port_coupler[0]:
            router_path = [
                (list_x_port_coupler_in[idx_now] + self.bend_radius * 1 + self.track_pitch,
                 list_y_port_coupler[0] + self.bend_radius * 1),
                (list_x_port_inst_in[idx_now] - self.bend_radius * 3 - self.track_pitch,
                 list_y_track_top[1]),
            ] + router_path

        list_router_in_main[idx_now].cardinal_router(
            router_path
        )

        if (list_y_track_top[2] - list_y_port_inst_top[idx_now] < self.bend_radius * 2):
            # list_y_port_inst_top[idx_now] = list_y_track_top[2]
            router_path = [
                (list_x_port_inst_in[idx_now] - self.bend_radius * 3,
                 list_y_port_inst_top[idx_now] - self.bend_radius * 1),
                (list_x_port_inst_in[idx_now] - self.bend_radius * 2,
                 list_y_port_inst_top[idx_now] - self.bend_radius * 2),
                (list_x_port_inst_in[idx_now] - self.bend_radius * 1,
                 list_y_port_inst_top[idx_now] - self.bend_radius * 1),
                (list_x_port_inst_in[idx_now],
                 list_y_port_inst_top[idx_now]),
            ]
        else:
            router_path = [
                (list_x_port_inst_in[idx_now] - self.bend_radius * 1,
                 list_y_port_inst_top[idx_now] + self.bend_radius * 1),
                (list_x_port_inst_in[idx_now],
                 list_y_port_inst_top[idx_now])
            ]

        if list_y_track_top[2] > list_y_port_coupler[1]:
            router_path = [
                (list_x_port_coupler_in[idx_now] + self.bend_radius * 1,
                 list_y_port_coupler[1] + self.bend_radius * 1),
                (list_x_port_coupler_in[idx_now] + self.bend_radius * 2,
                 list_y_track_top[2]),
            ] + router_path

        list_router_in_drop[idx_now].cardinal_router(
            router_path
        )
        list_router_out_main[idx_now].cardinal_router(
            [
                (list_x_port_coupler_out[idx_now] - self.bend_radius * 1,
                 list_y_port_coupler[0] - self.bend_radius * 1),
                (list_x_port_inst_out[idx_now] + self.bend_radius * 4,
                 list_y_track_bot[0]),
                (list_x_port_inst_out[idx_now] + self.bend_radius * 3,
                 list_y_port_inst_bot[idx_now] + self.bend_radius * 1),
                (list_x_port_inst_out[idx_now] + self.bend_radius * 2,
                 list_y_port_inst_bot[idx_now] + self.bend_radius * 2),
                (list_x_port_inst_out[idx_now] + self.bend_radius * 1,
                 list_y_port_inst_bot[idx_now] + self.bend_radius * 1),
                (list_x_port_inst_out[idx_now],
                 list_y_port_inst_bot[idx_now]),
            ]
        )
        list_router_out_drop[idx_now].cardinal_router(
            [
                (list_x_port_coupler_out[idx_now] - self.bend_radius * 1 - self.track_pitch,
                 list_y_port_coupler[1] - self.bend_radius * 1),
                (list_x_port_inst_out[idx_now] + self.bend_radius * 4 + self.track_pitch,
                 list_y_track_bot[1]),
                (list_x_port_inst_out[idx_now] + self.bend_radius * 3 + self.track_pitch,
                 list_y_port_inst_top[idx_now] - self.bend_radius),
                (list_x_port_inst_out[idx_now],
                 list_y_port_inst_top[idx_now]),
            ]
        )

        #### site 2
        idx_now = 2

        list_router_in_main[idx_now].cardinal_router(
            [
                (list_x_port_coupler_in[idx_now] + self.bend_radius * 1 + self.track_pitch,
                 list_y_port_coupler[0] + self.bend_radius * 1),
                (list_x_port_inst_in[idx_now] - self.bend_radius * 2 - self.track_pitch,
                 list_y_track_top[3]),
                (list_x_port_inst_in[idx_now] - self.bend_radius * 1 - self.track_pitch,
                 list_y_port_inst_bot[idx_now] + self.bend_radius * 1),
                (list_x_port_inst_in[idx_now],
                 list_y_port_inst_bot[idx_now]),
            ]
        )

        list_router_in_drop[idx_now].cardinal_router(
            [
                (list_x_port_coupler_in[idx_now] + self.bend_radius * 1,
                 list_y_port_coupler[1] + self.bend_radius * 1),
                (list_x_port_inst_in[idx_now] - self.bend_radius * 2,
                 list_y_track_top[4]),
                (list_x_port_inst_in[idx_now] - self.bend_radius * 1,
                 list_y_port_inst_top[idx_now] + self.bend_radius * 1),
                (list_x_port_inst_in[idx_now],
                 list_y_port_inst_top[idx_now]),
            ]
        )
        list_router_out_main[idx_now].cardinal_router(
            [
                (list_x_port_coupler_out[idx_now] - self.bend_radius * 1,
                 list_y_port_coupler[0] - self.bend_radius * 1),
                (list_x_port_inst_out[idx_now] + self.bend_radius * 4,
                 list_y_track_bot[2]),
                (list_x_port_inst_out[idx_now] + self.bend_radius * 3,
                 list_y_port_inst_bot[idx_now] + self.bend_radius * 1),
                (list_x_port_inst_out[idx_now] + self.bend_radius * 2,
                 list_y_port_inst_bot[idx_now] + self.bend_radius * 2),
                (list_x_port_inst_out[idx_now] + self.bend_radius * 1,
                 list_y_port_inst_bot[idx_now] + self.bend_radius * 1),
                (list_x_port_inst_out[idx_now],
                 list_y_port_inst_bot[idx_now]),
            ]
        )
        list_router_out_drop[idx_now].cardinal_router(
            [
                (list_x_port_coupler_out[idx_now] - self.bend_radius * 1 - self.track_pitch,
                 list_y_port_coupler[1] - self.bend_radius * 1),
                (list_x_port_inst_out[idx_now] + self.bend_radius * 4 + self.track_pitch,
                 list_y_track_bot[3]),
                (list_x_port_inst_out[idx_now] + self.bend_radius * 3 + self.track_pitch,
                 list_y_port_inst_top[idx_now] - self.bend_radius),
                (list_x_port_inst_out[idx_now],
                 list_y_port_inst_top[idx_now]),
            ]
        )


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


class TripleRingRowArray(PhotonicTemplateBase):
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


        n_site = 3
        for i in range(0, self.n_rowpairs):
            layout_params_r180 = deepcopy(self.params)
            layout_params_r0 = deepcopy(self.params)
            yaml_list_mx = self.yaml_list[n_site*(2*i+0):n_site*(2*i+1)]
            yaml_list_r0 = self.yaml_list[n_site*(2*i+1):n_site*(2*i+2)]
            # layout_params_r180.update({'yaml_list', yaml_list_mx})
            # layout_params_r0.update({'yaml_list', yaml_list_r0})
            layout_params_r180['yaml_list'] = yaml_list_mx
            layout_params_r0['yaml_list'] = yaml_list_r0
            if i == 0:
                print('YAML LIST')
                print(yaml_list_mx)
                print(layout_params_r180['yaml_list'])
            # print(i, self.yaml_list[n_site*(2*i+0):n_site*(2*i+1)], self.yaml_list[n_site*(2*i+1):n_site*(2*i+2)])

            master_r180 = self.new_template(params=layout_params_r180, temp_cls=TripleRingRowNoDrop)
            master_r0 = self.new_template(params=layout_params_r0, temp_cls=TripleRingRowNoDrop)

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


class TxHybridRowArray(PhotonicTemplateBase):
    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)
        self.params = params
        # print(params, '\n')
        # print(self.params, '\n')

        for key, val in self.params.items():  # Automatically unpack variables
            # print(key, val, '\n')
            # exec( "self.{} = {}".format( key, val ) )
            exec(f"self.{key} = {val!r}")
        # print(params, '\n')
        # print(self.params, '\n')

        # ================================================================
        # Create all templates (may need them to get geometry parameters)
        # ================================================================

        self.bend_radius = self.photonic_tech_info.get_default_wg_params(self.wg_routing_layer)['radius']
        self.routing_width = self.photonic_tech_info.get_default_wg_params(self.wg_routing_layer)['width']


    # ================================================================
    # Common geometry parameters
    # ================================================================

    # Pad-related
    # self.num_pads = 4
    # self.x_start_pads = -1.0 * self.pad_params[ 'pitch' ] * ( self.num_pads - 1.0 ) / 2.0
    #
    # self.pad_locs = [ ]
    # for i in range( self.num_pads ):
    # 	loc = ( self.x_start_pads + i * self.pad_params[ 'pitch' ], 0.0 )
    # 	self.pad_locs.append( loc )

    #
    # self.pad_via_stacks = [ ]

    @classmethod
    def get_default_param_values(cls) -> dict:
        return dict(
            photonic_spec_file=None,
            photonic_module_name=None,
            photonic_class_name=None,
            wg_routing_layer=None,

        )

    @classmethod
    def get_params_info(cls) -> dict:
        return dict(
            photonic_spec_file='TODO',
            photonic_module_name='TODO',
            photonic_class_name='TODO',
            wg_routing_layer='TODO',

        )

    def draw_layout(self):
        self.place_instances()

    def place_instances(self):

        list_master_single_r180 = []
        list_master_single_r0 = []
        list_master_triple_r180 = []
        list_master_triple_r0 = []

        for i in range(0, self.n_rowpairs_single):
            n_site = 5
            layout_params_single    = self.params['params_single_ring_row_array'].copy()


            layout_params_r180  = layout_params_single.copy()
            layout_params_r0    = layout_params_single.copy()
            yaml_list_r180      = layout_params_single['yaml_list'][n_site*(2*i+0):n_site*(2*i+1)]
            yaml_list_r0        = layout_params_single['yaml_list'][n_site*(2*i+1):n_site*(2*i+2)]
            layout_params_r180['yaml_list'] = yaml_list_r180
            layout_params_r0['yaml_list']   = yaml_list_r0

            list_master_single_r180.append(self.new_template(params=layout_params_r180,
                                         temp_cls=SingleRingRow))
            list_master_single_r0.append(self.new_template(params=layout_params_r0,
                                                           temp_cls=SingleRingRow))

        for i in range(0, self.n_rowpairs_triple):
            n_site = 3
            layout_params_triple    = self.params['params_triple_ring_row_array'].copy()

            layout_params_r180  = layout_params_triple.copy()
            layout_params_r0    = layout_params_triple.copy()
            yaml_list_r180      = layout_params_triple['yaml_list'][n_site*(2*i+0):n_site*(2*i+1)]
            yaml_list_r0        = layout_params_triple['yaml_list'][n_site*(2*i+1):n_site*(2*i+2)]
            layout_params_r180['yaml_list'] = yaml_list_r180
            layout_params_r0['yaml_list']   = yaml_list_r0

            list_master_triple_r180.append(self.new_template(params=layout_params_r180,
                                                             temp_cls=TripleRingRowNoDrop))
            list_master_triple_r0.append(self.new_template(params=layout_params_r0,
                                                           temp_cls=TripleRingRowNoDrop))


        idx_single = 0
        idx_triple = 0
        for i in range(0, self.n_rowpairs_single + self.n_rowpairs_triple):
            y_rowpair_base = sum(self.list_pitch_row_pair[:i+1])
            print(i, y_rowpair_base)

            if self.list_seq_pitch_row_pair[i] == 'triple':
                params_shared   = self.params['params_triple_ring_row_array']
                master_r180     = list_master_triple_r180[idx_triple]
                master_r0       = list_master_triple_r0[idx_triple]
                n_site          = 3
                idx_triple      += 1
            elif self.list_seq_pitch_row_pair[i] == 'single':
                params_shared   = self.params['params_single_ring_row_array']
                master_r180     = list_master_single_r180[idx_single]
                master_r0       = list_master_single_r0[idx_single]
                n_site          = 5
                idx_single      += 1
            else:
                raise ValueError("Wrong row type, must be either single or triple")

            print(master_r180.bound_box, master_r0.bound_box)

            dx_inst_r180                = master_r180.bound_box.width
            x_coupler_r180_rightmost    = params_shared['x_port_coupler_out_base']  + \
                                          params_shared['x_coupler_pitch'] * (n_site - 1)

            x_inst_r180                 = params_shared['x_port_coupler_in_base'] + \
                                          x_coupler_r180_rightmost
            x_inst_r0                   = 0

            y_inst_r180                 = y_rowpair_base + params_shared['y_port_coupler_base'] * 2 - \
                                          params_shared['y_coupler_pitch']

            y_inst_r0                   = y_inst_r180 + params_shared['y_split_in_pair']

            # y_inst_r0                   = y_rowpair_base - master_r180.bound_box.bottom
            # y_inst_r180                 = y_inst_r0 - params_shared['y_split_in_pair']

            # hfshfs

            self.add_instance(
                master=master_r0,
                loc=(x_inst_r0, y_inst_r0),
                orient='R0',
            )
            self.add_instance(
                master=master_r180,
                loc=(x_inst_r180, y_inst_r180),
                orient='R180',
            )




    # ================================================================
    # Helper methods
    # ================================================================

    def create_template(self, photonic_spec_file, photonic_module_name, photonic_class_name):
        # Load params from the specified yaml file
        with open(photonic_spec_file) as spec_file:
            yaml_file = yaml.load(spec_file)
        yaml_params = deepcopy(yaml_file['layout_params'])

        # Load the module and class for the instance, then create the template
        temp_cls = getattr(importlib.import_module(photonic_module_name), photonic_class_name)
        return self.new_template(params=yaml_params, temp_cls=temp_cls)

    def create_straight_wg_template(self, width, length, layer, port_layer):
        arc_params = [
            dict(
                arc_type='straight_wg',
                width=width,
                length=length,
            )
        ]

        offset_params = dict(
            layer=layer,
            port_layer=port_layer,
            x_start=0.0,
            y_start=0.0,
            angle_start=0.0,
            radius_threshold=0.0,
            curvature_rate_threshold=0.7,
            merge_arcs=False,
            show_plot=False,
            show_plot_labels=False,
            arc_params=arc_params
        )

        return self.new_template(params=offset_params, temp_cls=AdiabaticPaths)


class TripleRingRowArrayWithLNA(PhotonicTemplateBase):
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

        self.package_class_param_list = self.params['package_class_param_list']
        self.yaml_list = self.params['yaml_list']

        self.master_list = []
        self.inst_list = []



        self.n_rows = self.params['n_rows']
        self.y_pitch_row = self.params['y_pitch_row']

        self.bend_radius = self.photonic_tech_info.get_default_wg_params(self.wg_routing_layer)['radius']
        self.routing_width = self.photonic_tech_info.get_default_wg_params(self.wg_routing_layer)['width']




    @classmethod
    def get_params_info(cls):
        return dict(
            package_class_param_list='',
            yaml_list='',
            site_pitch='',
            track_pitch='',
            grating_coupler_module='',
            grating_coupler_class='',


        )

    @classmethod
    def get_default_param_values(cls):
        return dict(
        )

    def draw_layout(self):

        master_row = []
        n_site = 9
        # for i in range(0, self.n_rows):

        layout_params0 = deepcopy(self.params)
        layout_params1 = deepcopy(self.params)
        layout_params2 = deepcopy(self.params)
        yaml_list0 = self.yaml_list[0:9]
        yaml_list1 = self.yaml_list[9:18]
        yaml_list2 = self.yaml_list[18:27]
        layout_params0['yaml_list'] = yaml_list0
        master0 = self.new_template(params=layout_params0, temp_cls=TripleRingRowWithLNANoDropForceRouting)
        layout_params1['yaml_list'] = yaml_list1
        master1 = self.new_template(params=layout_params1, temp_cls=TripleRingRowWithLNANoDropForceRouting1)
        layout_params2['yaml_list'] = yaml_list2
        master2 = self.new_template(params=layout_params2, temp_cls=TripleRingRowWithLNANoDropForceRouting2)
        # print(layout_params0)
        # print(layout_params1)
        # print(layout_params2)


        print(master_row)
        x_inst = 0
        y_inst = self.y_pitch_row

        self.add_instance(
            master=master0,
            loc=(x_inst, -self.y_pitch_row * 0),
            orient='R0',
        )
        self.add_instance(
            master=master1,
            loc=(x_inst, self.y_pitch_row * 1),
            orient='R0',
        )
        self.add_instance(
            master=master2,
            loc=(x_inst, self.y_pitch_row * 2),
            orient='R0',
        )

