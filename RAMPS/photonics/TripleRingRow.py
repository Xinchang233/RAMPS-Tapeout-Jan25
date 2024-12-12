# from BPG import PhotonicTemplateBase
# from Photonic_Core_Layout.WaveguideBase.WgRouter import WgRouter
# import importlib
# import yaml
#
# class TripleRingRowV1(PhotonicTemplateBase):
#     """
#     Photonic Ports:
#     IN = left side
#     OUT = right side
#     """
#
#     def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
#         PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)
#         self.params = params
#
#         self.port_width = 0.35
#         self.wg_port_layer = ('si_full_free', 'port')
#         self.wg_routing_layer = ('si_full_free', 'drawing')
#         # self.wg_port_layer = ('RX', 'port')
#         # self.wg_routing_layer = ('RX', 'drawing')
#
#
#         self.grating_coupler_module = self.params['grating_coupler_module']
#         self.grating_coupler_class = self.params['grating_coupler_class']
#         gc_module = importlib.import_module(self.grating_coupler_module)
#         gc_class = getattr(gc_module, self.grating_coupler_class)
#         self.gc_master = self.new_template(params=None, temp_cls=gc_class)
#
#         self.package_class_param_list = self.params['package_class_param_list']
#         self.yaml_list = self.params['yaml_list']
#
#         self.master_list = []
#         self.inst_list = []
#         self.site_pitch = self.params['site_pitch']
#         self.track_pitch = self.params['track_pitch']
#
#         self.x_coupler_clear = self.params['x_coupler_clear']
#         self.y_coupler_clear = self.params['y_coupler_clear']
#         self.x_coupler_pitch = self.params['x_coupler_pitch']
#         self.y_coupler_pitch = self.params['y_coupler_pitch']
#
#         self.x_port_coupler_in_base = self.params['x_port_coupler_in_base']
#         self.x_port_coupler_out_base = self.params['x_port_coupler_out_base']
#         self.y_port_coupler_base = self.params['y_port_coupler_base']
#
#         self.dx_inst = self.params['dx_inst']
#         self.dy_inst = self.params['dy_inst']
#         self.x_instance = self.params['x_instance']
#         self.dy_port_inst_bot = self.params['dy_port_inst_bot']
#         self.dy_port_inst_top = self.params['dy_port_inst_top']
#
#         self.bend_radius = self.photonic_tech_info.get_default_wg_params(self.wg_routing_layer)['radius'] + 0.02
#         self.routing_width = self.photonic_tech_info.get_default_wg_params(self.wg_routing_layer)['width']
#
#     @classmethod
#     def get_params_info(cls):
#         return dict(
#             package_class_param_list='',
#             yaml_list='',
#             site_pitch='',
#             track_pitch='',
#
#             x_coupler_clear='',
#             y_coupler_clear='',
#             x_coupler_pitch='',
#             y_coupler_pitch='',
#
#             x_port_coupler_in_base='',
#             x_port_coupler_out_base='',
#             y_port_coupler_base='',
#
#             dx_inst='',
#             dy_inst='',
#             dy_port_inst_bot='',
#             dy_port_inst_top='',
#             x_instance='',
#
#
#         )
#
#     @classmethod
#     def get_default_param_values(cls):
#         return dict(
#         )
#
#     def draw_layout(self):
#
#         # instantiate the ring modulator masters
#         list_inst_direction = []
#         list_dx_inst = []
#         # list_dy_inst = []
#         list_x_inst_offset = []
#         list_y_inst_offset = []
#
#         in_port_name = 'PORT0'
#         out_port_name = 'PORT1'
#         for ind, yaml_file in enumerate(self.yaml_list):
#             if yaml_file != 'VOID':
#                 with open(yaml_file, 'r') as f:
#                     yaml_content = yaml.load(f)
#
#                 lay_module = importlib.import_module(yaml_content['layout_package'])
#                 temp_cls = getattr(lay_module, yaml_content['layout_class'])
#
#                 master = self.new_template(params=yaml_content['layout_params'],
#                                            temp_cls=temp_cls)
#
#                 self.master_list.append(master)
#                 master_in_port_loc = master.get_photonic_port(in_port_name).center
#                 # master_in_port_loc = (0, 0)
#
#
#                 if (1):
#
#                     list_inst_direction.append('MXR90')
#                     list_dx_inst.append(abs(master_in_port_loc[1] * 2.0))
#                     list_x_inst_offset.append(abs(master_in_port_loc[1] * -1.0))
#                     list_y_inst_offset.append(abs(master_in_port_loc[0] * -1.0))
#                 else:
#                     list_inst_direction.append('MX')
#                     list_dx_inst.append(abs(master_in_port_loc[0] * 2.0))
#                     list_x_inst_offset.append(abs(master_in_port_loc[0] * -1.0))
#                     list_y_inst_offset.append(abs(master_in_port_loc[1] * 1.0))
#             else:
#                 self.master_list.append([])
#                 list_dx_inst.append(0)
#                 list_x_inst_offset.append(0)
#                 list_y_inst_offset.append(0)
#                 list_inst_direction.append('MX')
#
#
#
#         n_site = 3
#         #### define coupler port positions
#         list_idx_port_coupler_in = [0, 1, 2]
#         list_idx_port_coupler_out = [1, 0, 2]
#         list_x_port_coupler_in = [
#             self.x_port_coupler_in_base + list_idx_port_coupler_in[i] * self.x_coupler_pitch for i in range(0, n_site)
#         ]
#         list_x_port_coupler_out = [
#             self.x_port_coupler_out_base + list_idx_port_coupler_out[i] * self.x_coupler_pitch for i in range(0, n_site)
#         ]
#         list_y_port_coupler = [
#             self.y_port_coupler_base + i * self.y_coupler_pitch for i in range(0, 2)
#         ]
#
#
#         # x_coupler_port_in = self.x_coupler_port_in_base + [0, ]
#         # y_coupler_port = self.y_coupler_port
#         # dx_inst_port_min = self.dx_inst_port_min
#         # dy_inst_port_min = self.dy_inst_port_min
#         list_x_port_inst_in = [self.x_instance[i] - list_dx_inst[i] / 2 for i in range(0, n_site)]
#         list_x_port_inst_out = [self.x_instance[i] + list_dx_inst[i] / 2 for i in range(0, n_site)]
#
#
#         # y_track_inst_bot = 3 * self.track_pitch
#         # y_track_inst_top_min = y_track_inst_bot + dy_inst_port_min
#
#         # 4 long horizontal waveguide tracks on the bottom side of the instances
#         list_y_track_bot = [self.track_pitch * (i+1) for i in range(0, 5)]
#         # horizontal track the bottom ports of the instances are on
#         y_port_inst_bot = list_y_track_bot[4] + self.dy_port_inst_bot
#
#         # check if these positions are appropriate
#         if (list_x_port_coupler_in[0] < self.x_coupler_clear):
#             raise ValueError('Input Coupler x coordinate is too low')
#         if (list_y_port_coupler[0] < list_y_track_bot[1] + self.track_pitch + self.y_coupler_clear / 2):
#             raise ValueError('Coupler y coordinate is too low, will conflict with waveguide routing')
#
#
#         # 7 long horizontal waveguide tracks on the top side of the instances
#         y_track_top_min = max(list_y_port_coupler[1] + self.track_pitch + self.y_coupler_clear / 2,
#                               list_y_track_bot[4] + self.dy_inst + self.track_pitch * 1)
#         list_y_track_top = [i * self.track_pitch + y_track_top_min for i in range(0, 4)]
#         y_port_inst_top = list_y_track_top[3]
#         y_port_inst_top = list_y_track_bot[4] + self.dy_port_inst_top
#
#
#         # flag to trigger special routing because large bend radius
#         flag_sp_routing_1 = (list_y_port_coupler[0] - list_y_track_bot[0]) < self.bend_radius * 2
#         flag_sp_routing_2 = self.track_pitch * 2 < self.bend_radius * 2
#         flag_sp_routing_3 = self.track_pitch * 4 < self.bend_radius * 2
#
#         # instantiate the frating couplers
#         list_gc_in_main = [
#             self.add_instance(
#                 master=self.gc_master,
#                 loc=(list_x_port_coupler_in[i],
#                      list_y_port_coupler[0]),
#                 # Offset site by location of input port, to put input port at desired location
#                 orient='R0',
#             )
#         for i in range(0, n_site)]
#         list_gc_in_drop = [
#             self.add_instance(
#                 master=self.gc_master,
#                 loc=(list_x_port_coupler_in[i],
#                      list_y_port_coupler[1]),
#                 # Offset site by location of input port, to put input port at desired location
#                 orient='R0',
#             )
#         for i in range(0, n_site)]
#         list_gc_out_main = [
#             self.add_instance(
#                 master=self.gc_master,
#                 loc=(list_x_port_coupler_out[i],
#                      list_y_port_coupler[0]),
#                 # Offset site by location of input port, to put input port at desired location
#                 orient='MY',
#             )
#         for i in range(0, n_site)]
#         list_gc_out_drop = [
#             self.add_instance(
#                 master=self.gc_master,
#                 loc=(list_x_port_coupler_out[i],
#                      list_y_port_coupler[1]),
#                 # Offset site by location of input port, to put input port at desired location
#                 orient='MY',
#             )
#         for i in range(0, n_site)]
#
#         # instantiate the rings
#         for i in range(0, n_site):
#             if list_dx_inst[i] != 0:
#                 master_in_port_loc = self.master_list[i].get_photonic_port(in_port_name).center
#
#                 # master_in_port_loc = (0, 0)
#                 self.inst_list.append(
#                     self.add_instance(
#                         master=self.master_list[i],
#                         loc=(list_x_port_inst_in[i] + list_x_inst_offset[i],
#                              y_port_inst_bot + list_y_inst_offset[i]),
#                         orient=list_inst_direction[i],
#                     )
#                 )
#
#
#
#         list_port_in_main = [
#             self.add_photonic_port(
#                 name=f'IN_MAIN{i}',
#                 center=(list_x_port_coupler_in[i], list_y_port_coupler[0]),
#                 orient='R0',
#                 layer=self.wg_port_layer,
#                 width=self.routing_width
#             )
#             for i in range(0, n_site)
#         ]
#         list_port_in_drop = [
#             self.add_photonic_port(
#                 name=f'IN_DROP{i}',
#                 center=(list_x_port_coupler_in[i], list_y_port_coupler[1]),
#                 orient='R0',
#                 layer=self.wg_port_layer,
#                 width=self.routing_width
#             )
#
#             for i in range(0, n_site)
#         ]
#         list_port_out_main = [
#             self.add_photonic_port(
#                 name=f'OUT_MAIN{i}',
#                 center=(list_x_port_coupler_out[i], list_y_port_coupler[0]),
#                 orient='R0',
#                 layer=self.wg_port_layer,
#                 width=self.routing_width
#             )
#             for i in range(0, n_site)
#         ]
#         list_port_out_drop = [
#             self.add_photonic_port(
#                 name=f'OUT_DROP{i}',
#                 center=(list_x_port_coupler_out[i], list_y_port_coupler[1]),
#                 orient='R0',
#                 layer=self.wg_port_layer,
#                 width=self.routing_width
#             )
#             for i in range(0, n_site)
#         ]
#
#
#
#         list_router_in_main = [
#             WgRouter(
#                 self,
#                 list_port_in_main[i],
#                 self.wg_routing_layer,
#                 route_in_port_dir=True
#             )
#             for i in range(0, n_site)
#         ]
#         list_router_in_drop = [
#             WgRouter(
#                 self,
#                 list_port_in_drop[i],
#                 self.wg_routing_layer,
#                 route_in_port_dir=True
#             )
#             for i in range(0, n_site)
#         ]
#         list_router_out_main = [
#             WgRouter(
#                 self,
#                 list_port_out_main[i],
#                 self.wg_routing_layer,
#                 route_in_port_dir=False
#             )
#             for i in range(0, n_site)
#         ]
#         list_router_out_drop = [
#             WgRouter(
#                 self,
#                 list_port_out_drop[i],
#                 self.wg_routing_layer,
#                 route_in_port_dir=False
#             )
#             for i in range(0, n_site)
#         ]
#
#
#         #### site 0
#         idx_now = 0
#
#         list_router_in_main[idx_now].cardinal_router(
#             [
#                 (list_x_port_coupler_in[idx_now] + self.bend_radius * 1 + self.track_pitch,
#                  list_y_port_coupler[0] + self.bend_radius * 1),
#                 (list_x_port_inst_in[idx_now] - self.bend_radius * 2,
#                  list_y_track_top[2]),
#                 (list_x_port_inst_in[idx_now] - self.bend_radius * 3 - self.track_pitch,
#                  y_port_inst_bot + self.bend_radius * 1),
#                 (list_x_port_inst_in[idx_now],
#                  y_port_inst_bot),
#             ]
#         )
#         list_router_in_drop[idx_now].cardinal_router(
#             [
#                 (list_x_port_coupler_in[idx_now] + self.bend_radius * 1,
#                  list_y_port_coupler[1] + self.bend_radius * 1),
#                 (list_x_port_inst_in[idx_now] - self.bend_radius * 4,
#                  list_y_track_top[3]),
#                 # (list_x_port_inst_in[idx_now] - self.bend_radius * 3,
#                 #  y_port_inst_top - self.bend_radius * 1),
#                 # (list_x_port_inst_in[idx_now] - self.bend_radius * 2,
#                 #  y_port_inst_top - self.bend_radius * 2),
#                 (list_x_port_inst_in[idx_now] - self.bend_radius * 1,
#                  y_port_inst_top + self.bend_radius * 1),
#                 (list_x_port_inst_in[idx_now],
#                  y_port_inst_top),
#             ]
#         )
#
#
#         list_router_out_main[idx_now].cardinal_router(
#             [
#                 (list_x_port_coupler_out[idx_now] - self.bend_radius * 1 - self.track_pitch,
#                  list_y_port_coupler[0] + self.bend_radius),
#                 (list_x_port_coupler_out[idx_now] - self.bend_radius * 2 - self.track_pitch,
#                  list_y_track_top[2]),
#                 (list_x_port_inst_out[idx_now] + self.bend_radius * 3 + self.track_pitch,
#                  list_y_track_bot[4] + self.bend_radius),
#                 (list_x_port_inst_out[idx_now],
#                  y_port_inst_bot),
#             ]
#         )
#
#         router_path = [
#             (list_x_port_coupler_out[idx_now] - self.bend_radius * 1,
#              list_y_port_coupler[1] + self.bend_radius),
#             (list_x_port_coupler_out[idx_now] - self.bend_radius * 2,
#              list_y_track_top[3]),
#         ] + ([
#             (list_x_port_inst_out[idx_now] + self.bend_radius * 3,
#              y_port_inst_top - self.bend_radius * 1),
#             (list_x_port_inst_out[idx_now] + self.bend_radius * 2,
#              y_port_inst_top - self.bend_radius * 2),
#             (list_x_port_inst_out[idx_now] + self.bend_radius * 1,
#              y_port_inst_top - self.bend_radius * 1),
#             (list_x_port_inst_out[idx_now],
#              y_port_inst_top),
#         ] if flag_sp_routing_3 else [
#             (list_x_port_inst_out[idx_now] + self.bend_radius * 1,
#              y_port_inst_top + self.bend_radius * 1),
#             (list_x_port_inst_out[idx_now],
#              y_port_inst_top),
#         ])
#
#         list_router_out_drop[idx_now].cardinal_router(router_path)
#
#
#
#         #### site 1
#         idx_now = 1
#
#         router_path = [
#             (list_x_port_coupler_in[idx_now] + self.bend_radius * 1 + self.track_pitch,
#              list_y_port_coupler[0] + self.bend_radius * 1),
#             (list_x_port_coupler_in[idx_now+1] + self.bend_radius * 3 + self.track_pitch,
#              list_y_track_top[0]),
#             (list_x_port_coupler_in[idx_now + 1] + self.bend_radius * 4 + self.track_pitch,
#              list_y_track_top[0] - self.bend_radius * 1),
#             (list_x_port_inst_in[idx_now] - self.bend_radius * 4,
#              list_y_track_bot[2]),
#         ] + ([
#             (list_x_port_inst_in[idx_now] - self.bend_radius * 3,
#              y_port_inst_bot + self.bend_radius * 1),
#             (list_x_port_inst_in[idx_now] - self.bend_radius * 2,
#              y_port_inst_bot + self.bend_radius * 2),
#             (list_x_port_inst_in[idx_now] - self.bend_radius * 1,
#              y_port_inst_bot + self.bend_radius * 1),
#             (list_x_port_inst_in[idx_now],
#              y_port_inst_bot),
#         ] if flag_sp_routing_2 else [
#             (list_x_port_inst_in[idx_now] - self.bend_radius * 1,
#              y_port_inst_bot - self.bend_radius * 1),
#             (list_x_port_inst_in[idx_now],
#              y_port_inst_bot),
#
#         ])
#
#         list_router_in_main[idx_now].cardinal_router(router_path)
#
#
#         list_router_in_drop[idx_now].cardinal_router(
#             [
#                 (list_x_port_coupler_in[idx_now] + self.bend_radius * 1,
#                  list_y_port_coupler[1] + self.bend_radius * 1),
#                 (list_x_port_coupler_in[idx_now + 1] + self.bend_radius * 3 + self.track_pitch * 2,
#                  list_y_track_top[1]),
#                 (list_x_port_coupler_in[idx_now + 1] + self.bend_radius * 4 + self.track_pitch * 2,
#                  list_y_track_top[0] - self.bend_radius * 1),
#                 (list_x_port_inst_in[idx_now] - self.bend_radius * 4 - self.track_pitch,
#                  list_y_track_bot[3]),
#                 (list_x_port_inst_in[idx_now] - self.bend_radius * 3 - self.track_pitch,
#                  list_y_track_bot[3] + self.bend_radius),
#                 (list_x_port_inst_in[idx_now],
#                  y_port_inst_top),
#             ]
#         )
#
#
#
#         list_router_out_main[idx_now].cardinal_router([
#             (list_x_port_coupler_out[idx_now] - self.bend_radius * 1 - self.track_pitch,
#              list_y_port_coupler[0] + self.bend_radius),
#             (list_x_port_coupler_out[idx_now] - self.bend_radius * 2 - self.track_pitch,
#              list_y_track_top[0]),
#             (list_x_port_inst_out[idx_now] + self.bend_radius * 3 + self.track_pitch,
#              list_y_track_bot[4] - self.bend_radius),
#             (list_x_port_inst_out[idx_now],
#              y_port_inst_bot),
#         ])
#
#         router_path = [
#             (list_x_port_coupler_out[idx_now] - self.bend_radius * 1,
#              list_y_port_coupler[1] + self.bend_radius),
#             (list_x_port_coupler_out[idx_now] - self.bend_radius * 2,
#              list_y_track_top[1]),
#         ] + ([
#             (list_x_port_inst_out[idx_now] + self.bend_radius * 3,
#              y_port_inst_top - self.bend_radius * 1),
#             (list_x_port_inst_out[idx_now] + self.bend_radius * 2,
#              y_port_inst_top - self.bend_radius * 2),
#             (list_x_port_inst_out[idx_now] + self.bend_radius * 1,
#              y_port_inst_top - self.bend_radius * 1),
#             (list_x_port_inst_out[idx_now],
#              y_port_inst_top),
#         ] if flag_sp_routing_2 else [
#             (list_x_port_inst_out[idx_now] + self.bend_radius * 1,
#              y_port_inst_top + self.bend_radius * 1),
#             (list_x_port_inst_out[idx_now],
#              y_port_inst_top),
#         ])
#
#         list_router_out_drop[idx_now].cardinal_router(router_path)
#
#         #### site 2
#         idx_now = 2
#
#         router_path = ([
#             (list_x_port_coupler_in[idx_now] + self.bend_radius * 1,
#              list_y_port_coupler[0] + self.bend_radius * 1),
#             (list_x_port_coupler_in[idx_now] + self.bend_radius * 2,
#              list_y_port_coupler[0] + self.bend_radius * 2),
#             (list_x_port_coupler_in[idx_now] + self.bend_radius * 3,
#              list_y_port_coupler[0] + self.bend_radius * 1),
#         ] if flag_sp_routing_1 else [
#             (list_x_port_coupler_in[idx_now] + self.bend_radius * 1,
#              list_y_port_coupler[0] - self.bend_radius * 1),
#         ]) + [
#             (list_x_port_inst_in[idx_now] - self.bend_radius * 4,
#              list_y_track_bot[0])
#         ] +  ([
#             (list_x_port_inst_in[idx_now] - self.bend_radius * 3,
#              list_y_track_bot[0] + self.bend_radius * 1),
#             (list_x_port_inst_in[idx_now] - self.bend_radius * 2,
#              y_port_inst_bot + self.bend_radius * 2),
#             (list_x_port_inst_in[idx_now] - self.bend_radius * 1,
#              y_port_inst_bot + self.bend_radius * 1),
#             (list_x_port_inst_in[idx_now],
#              y_port_inst_bot),
#         ] if flag_sp_routing_3 else [
#             (list_x_port_inst_in[idx_now] - self.bend_radius * 1,
#              y_port_inst_bot - self.bend_radius * 1),
#             (list_x_port_inst_in[idx_now],
#              y_port_inst_bot),
#         ])
#
#         list_router_in_main[idx_now].cardinal_router(router_path)
#
#
#         list_router_in_drop[idx_now].cardinal_router(
#             [
#                 (list_x_port_coupler_in[idx_now] + self.bend_radius * 1 + self.track_pitch,
#                  list_y_port_coupler[0] - self.bend_radius * 1),
#                 (list_x_port_inst_in[idx_now] - self.bend_radius * 4 - self.track_pitch,
#                  list_y_track_bot[1]),
#                 (list_x_port_inst_in[idx_now] - self.bend_radius * 3 - self.track_pitch,
#                  y_port_inst_top - self.bend_radius * 1),
#                 (list_x_port_inst_in[idx_now],
#                  y_port_inst_top),
#             ]
#         )
#
#         router_path = ([
#             (list_x_port_coupler_out[idx_now] - self.bend_radius * 1,
#              list_y_port_coupler[0] + self.bend_radius * 1),
#             (list_x_port_coupler_out[idx_now] - self.bend_radius * 2,
#              list_y_port_coupler[0] + self.bend_radius * 2),
#             (list_x_port_coupler_out[idx_now] - self.bend_radius * 3,
#              list_y_port_coupler[0] + self.bend_radius * 1),
#         ] if flag_sp_routing_1 else [
#             (list_x_port_coupler_out[idx_now] - self.bend_radius * 1,
#              list_y_port_coupler[0] - self.bend_radius * 1),
#         ]) + [
#             (list_x_port_inst_out[idx_now] + self.bend_radius * 4,
#              list_y_track_bot[0])
#         ] +  ([
#             (list_x_port_inst_out[idx_now] + self.bend_radius * 3,
#              list_y_track_bot[0] + self.bend_radius * 1),
#             (list_x_port_inst_out[idx_now] + self.bend_radius * 2,
#              y_port_inst_bot + self.bend_radius * 2),
#             (list_x_port_inst_out[idx_now] + self.bend_radius * 1,
#              y_port_inst_bot + self.bend_radius * 1),
#             (list_x_port_inst_out[idx_now],
#              y_port_inst_bot),
#         ] if flag_sp_routing_3 else [
#             (list_x_port_inst_out[idx_now] + self.bend_radius * 1,
#              y_port_inst_bot - self.bend_radius),
#             (list_x_port_inst_out[idx_now],
#              y_port_inst_bot),
#         ])
#
#
#         list_router_out_main[idx_now].cardinal_router(router_path)
#
#
#         list_router_out_drop[idx_now].cardinal_router(
#             [
#                 (list_x_port_coupler_out[idx_now] - self.bend_radius * 1 - self.track_pitch,
#                  list_y_port_coupler[0] - self.bend_radius * 1),
#                 (list_x_port_inst_out[idx_now] + self.bend_radius * 4 + self.track_pitch,
#                  list_y_track_bot[1]),
#                 (list_x_port_inst_out[idx_now] + self.bend_radius * 3 + self.track_pitch,
#                  y_port_inst_top - self.bend_radius * 1),
#                 (list_x_port_inst_out[idx_now],
#                  y_port_inst_top),
#             ]
#         )
#
#
#
#
#
# class TripleRingRowNoDrop(PhotonicTemplateBase):
#     """
#     Photonic Ports:
#     IN = left side
#     OUT = right side
#     """
#
#     def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
#         PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)
#
#         self.port_width = 0.35
#         self.wg_port_layer = ('si_full_free', 'port')
#         self.wg_routing_layer = ('si_full_free', 'drawing')
#         # self.wg_port_layer = ('RX', 'port')
#         # self.wg_routing_layer = ('RX', 'drawing')
#
#         # self.package_class_param_list = self.params['package_class_param_list']
#         self.yaml_list = self.params['yaml_list']
#
#         self.master_list = []
#         self.inst_list = []
#         self.site_pitch = self.params['site_pitch']
#         self.track_pitch = self.params['track_pitch']
#
#         self.x_coupler_clear = self.params['x_coupler_clear']
#         self.y_coupler_clear = self.params['y_coupler_clear']
#         self.x_coupler_pitch = self.params['x_coupler_pitch']
#         self.y_coupler_pitch = self.params['y_coupler_pitch']
#
#         self.x_port_coupler_in_base = self.params['x_port_coupler_in_base']
#         self.x_port_coupler_out_base = self.params['x_port_coupler_out_base']
#         self.y_port_coupler_base = self.params['y_port_coupler_base']
#
#         self.dx_inst = self.params['dx_inst']
#         self.dy_inst = self.params['dy_inst']
#         self.x_instance = self.params['x_instance']
#         self.dy_port_inst_bot = self.params['dy_port_inst_bot']
#
#         self.bend_radius = self.photonic_tech_info.get_default_wg_params(self.wg_routing_layer)['radius']
#         self.routing_width = self.photonic_tech_info.get_default_wg_params(self.wg_routing_layer)['width']
#
#     @classmethod
#     def get_params_info(cls):
#         return dict(
#             # package_class_param_list='',
#             yaml_list='',
#             site_pitch='',
#             track_pitch='',
#
#             x_coupler_clear='',
#             y_coupler_clear='',
#             x_coupler_pitch='',
#             y_coupler_pitch='',
#
#             x_port_coupler_in_base='',
#             x_port_coupler_out_base='',
#             y_port_coupler_base='',
#
#             dx_inst='',
#             dy_inst='',
#             dy_port_inst_bot='',
#             x_instance='',
#
#
#         )
#
#     @classmethod
#     def get_default_param_values(cls):
#         return dict(
#         )
#
#     def draw_layout(self):
#
#
#         n_site = 3
#         #### define coupler port positions
#         list_idx_port_coupler_in = [0, 1, 2]
#         list_idx_port_coupler_out = [1, 0, 2]
#         list_x_port_coupler_in = [
#             self.x_port_coupler_in_base + list_idx_port_coupler_in[i] * self.x_coupler_pitch for i in range(0, n_site)
#         ]
#         list_x_port_coupler_out = [
#             self.x_port_coupler_out_base + list_idx_port_coupler_out[i] * self.x_coupler_pitch for i in range(0, n_site)
#         ]
#         list_y_port_coupler = [self.y_port_coupler_base]
#
#
#         list_x_port_inst_in = [self.x_instance[i] - self.dx_inst / 2 for i in range(0, n_site)]
#         list_x_port_inst_out = [self.x_instance[i] + self.dx_inst / 2 for i in range(0, n_site)]
#
#
#         # 4 long horizontal waveguide tracks on the bottom side of the instances
#         list_y_track_bot = [self.track_pitch * (i+1) for i in range(0, 3)]
#         # horizontal track the bottom ports of the instances are on
#         y_port_inst_bot = list_y_track_bot[-1] + self.track_pitch + self.dy_port_inst_bot
#
#         # check if these positions are appropriate
#         if (list_x_port_coupler_in[0] < self.x_coupler_clear):
#             raise ValueError('Input Coupler x coordinate is too low')
#         if (list_y_port_coupler[0] < list_y_track_bot[0] + self.track_pitch + self.y_coupler_clear / 2):
#             raise ValueError('Coupler y coordinate is too low, will conflict with waveguide routing')
#
#
#         # 7 long horizontal waveguide tracks on the top side of the instances
#         y_track_top_min = max(list_y_port_coupler[-1] + self.track_pitch + self.y_coupler_clear / 2,
#                               list_y_track_bot[-1] + self.track_pitch * 2 + self.dy_inst)
#         list_y_track_top = [i * self.track_pitch + y_track_top_min for i in range(0, 2)]
#
#
#
#         # flag to trigger special routing because large bend radius
#         flag_sp_routing_1 = (list_y_port_coupler[0] - list_y_track_bot[0]) < self.bend_radius * 2
#         flag_sp_routing_2 = self.track_pitch * 2 < self.bend_radius * 2
#         flag_sp_routing_3 = self.track_pitch * 4 < self.bend_radius * 2
#
#
#
#
#
#         list_port_in_main = [
#             self.add_photonic_port(
#                 name=f'IN_MAIN{i}',
#                 center=(list_x_port_coupler_in[i], list_y_port_coupler[0]),
#                 orient='R0',
#                 layer=self.wg_port_layer,
#                 width=self.routing_width
#             )
#             for i in range(0, n_site)
#         ]
#
#         list_port_out_main = [
#             self.add_photonic_port(
#                 name=f'OUT_MAIN{i}',
#                 center=(list_x_port_coupler_out[i], list_y_port_coupler[0]),
#                 orient='R0',
#                 layer=self.wg_port_layer,
#                 width=self.routing_width
#             )
#             for i in range(0, n_site)
#         ]
#
#
#
#         list_router_in_main = [
#             WgRouter(
#                 self,
#                 list_port_in_main[i],
#                 self.wg_routing_layer,
#                 route_in_port_dir=True
#             )
#             for i in range(0, n_site)
#         ]
#
#         list_router_out_main = [
#             WgRouter(
#                 self,
#                 list_port_out_main[i],
#                 self.wg_routing_layer,
#                 route_in_port_dir=False
#             )
#             for i in range(0, n_site)
#         ]
#
#
#
#         #### site 0
#         idx_now = 0
#
#         list_router_in_main[idx_now].cardinal_router(
#             [
#                 (list_x_port_coupler_in[idx_now] + self.bend_radius * 1,
#                  list_y_port_coupler[0] + self.bend_radius * 1),
#                 (list_x_port_inst_in[idx_now] - self.bend_radius * 2,
#                  list_y_track_top[1]),
#                 (list_x_port_inst_in[idx_now] - self.bend_radius * 3,
#                  y_port_inst_bot + self.bend_radius * 1),
#                 (list_x_port_inst_in[idx_now],
#                  y_port_inst_bot),
#             ]
#         )
#
#
#
#         list_router_out_main[idx_now].cardinal_router(
#             [
#                 (list_x_port_coupler_out[idx_now] - self.bend_radius * 1,
#                  list_y_port_coupler[0] + self.bend_radius),
#                 (list_x_port_coupler_out[idx_now] - self.bend_radius * 2,
#                  list_y_track_top[1]),
#                 (list_x_port_inst_out[idx_now] + self.bend_radius * 3,
#                  list_y_track_bot[2] + self.bend_radius),
#                 (list_x_port_inst_out[idx_now],
#                  y_port_inst_bot),
#             ]
#         )
#
#
#
#
#
#         #### site 1
#         idx_now = 1
#
#         router_path = [
#             (list_x_port_coupler_in[idx_now] + self.bend_radius * 1,
#              list_y_port_coupler[0] + self.bend_radius * 1),
#             (list_x_port_coupler_in[idx_now+1] + self.bend_radius * 3,
#              list_y_track_top[0]),
#             (list_x_port_coupler_in[idx_now + 1] + self.bend_radius * 4,
#              list_y_track_top[0] - self.bend_radius * 1),
#             (list_x_port_inst_in[idx_now] - self.bend_radius * 4,
#              list_y_track_bot[2]),
#         ] + ([
#             (list_x_port_inst_in[idx_now] - self.bend_radius * 3,
#              y_port_inst_bot + self.bend_radius * 1),
#             (list_x_port_inst_in[idx_now] - self.bend_radius * 2,
#              y_port_inst_bot + self.bend_radius * 2),
#             (list_x_port_inst_in[idx_now] - self.bend_radius * 1,
#              y_port_inst_bot + self.bend_radius * 1),
#             (list_x_port_inst_in[idx_now],
#              y_port_inst_bot),
#         ] if flag_sp_routing_2 else [
#             (list_x_port_inst_in[idx_now] - self.bend_radius * 1,
#              y_port_inst_bot - self.bend_radius * 1),
#             (list_x_port_inst_in[idx_now],
#              y_port_inst_bot),
#
#         ])
#
#         list_router_in_main[idx_now].cardinal_router(router_path)
#
#
#
#
#         list_router_out_main[idx_now].cardinal_router([
#             (list_x_port_coupler_out[idx_now] - self.bend_radius * 1,
#              list_y_port_coupler[0] + self.bend_radius),
#             (list_x_port_coupler_out[idx_now] - self.bend_radius * 2,
#              list_y_track_top[0]),
#             (list_x_port_inst_out[idx_now] + self.bend_radius * 3,
#              list_y_track_bot[1] - self.bend_radius),
#             (list_x_port_inst_out[idx_now],
#              y_port_inst_bot),
#         ])
#
#
#         #### site 2
#         idx_now = 2
#
#         router_path = ([
#             (list_x_port_coupler_in[idx_now] + self.bend_radius * 1,
#              list_y_port_coupler[0] + self.bend_radius * 1),
#             (list_x_port_coupler_in[idx_now] + self.bend_radius * 2,
#              list_y_port_coupler[0] + self.bend_radius * 2),
#             (list_x_port_coupler_in[idx_now] + self.bend_radius * 3,
#              list_y_port_coupler[0] + self.bend_radius * 1),
#         ] if flag_sp_routing_1 else [
#             (list_x_port_coupler_in[idx_now] + self.bend_radius * 1,
#              list_y_port_coupler[0] - self.bend_radius * 1),
#         ]) + [
#             (list_x_port_inst_in[idx_now] - self.bend_radius * 4,
#              list_y_track_bot[0])
#         ] +  ([
#             (list_x_port_inst_in[idx_now] - self.bend_radius * 3,
#              list_y_track_bot[0] + self.bend_radius * 1),
#             (list_x_port_inst_in[idx_now] - self.bend_radius * 2,
#              y_port_inst_bot + self.bend_radius * 2),
#             (list_x_port_inst_in[idx_now] - self.bend_radius * 1,
#              y_port_inst_bot + self.bend_radius * 1),
#             (list_x_port_inst_in[idx_now],
#              y_port_inst_bot),
#         ] if flag_sp_routing_3 else [
#             (list_x_port_inst_in[idx_now] - self.bend_radius * 1,
#              y_port_inst_bot - self.bend_radius * 1),
#             (list_x_port_inst_in[idx_now],
#              y_port_inst_bot),
#         ])
#
#         list_router_in_main[idx_now].cardinal_router(router_path)
#
#
#         router_path = ([
#             (list_x_port_coupler_out[idx_now] - self.bend_radius * 1,
#              list_y_port_coupler[0] + self.bend_radius * 1),
#             (list_x_port_coupler_out[idx_now] - self.bend_radius * 2,
#              list_y_port_coupler[0] + self.bend_radius * 2),
#             (list_x_port_coupler_out[idx_now] - self.bend_radius * 3,
#              list_y_port_coupler[0] + self.bend_radius * 1),
#         ] if flag_sp_routing_1 else [
#             (list_x_port_coupler_out[idx_now] - self.bend_radius * 1,
#              list_y_port_coupler[0] - self.bend_radius * 1),
#         ]) + [
#             (list_x_port_inst_out[idx_now] + self.bend_radius * 4,
#              list_y_track_bot[0])
#         ] +  ([
#             (list_x_port_inst_out[idx_now] + self.bend_radius * 3,
#              list_y_track_bot[0] + self.bend_radius * 1),
#             (list_x_port_inst_out[idx_now] + self.bend_radius * 2,
#              y_port_inst_bot + self.bend_radius * 2),
#             (list_x_port_inst_out[idx_now] + self.bend_radius * 1,
#              y_port_inst_bot + self.bend_radius * 1),
#             (list_x_port_inst_out[idx_now],
#              y_port_inst_bot),
#         ] if flag_sp_routing_3 else [
#             (list_x_port_inst_out[idx_now] + self.bend_radius * 1,
#              y_port_inst_bot - self.bend_radius),
#             (list_x_port_inst_out[idx_now],
#              y_port_inst_bot),
#         ])
#
#
#         list_router_out_main[idx_now].cardinal_router(router_path)
#
#
#
#
#
# class TripleRingRow(PhotonicTemplateBase):
#     """
#     Photonic Ports:
#     IN = left side
#     OUT = right side
#     """
#
#     def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
#         PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)
#
#         self.port_width = 0.35
#         self.wg_port_layer = ('si_full_free', 'port')
#         self.wg_routing_layer = ('si_full_free', 'drawing')
#         # self.wg_port_layer = ('RX', 'port')
#         # self.wg_routing_layer = ('RX', 'drawing')
#
#         # self.package_class_param_list = self.params['package_class_param_list']
#         self.yaml_list = self.params['yaml_list']
#
#         self.master_list = []
#         self.inst_list = []
#         self.site_pitch = self.params['site_pitch']
#         self.track_pitch = self.params['track_pitch']
#
#         self.x_coupler_clear = self.params['x_coupler_clear']
#         self.y_coupler_clear = self.params['y_coupler_clear']
#         self.x_coupler_pitch = self.params['x_coupler_pitch']
#         self.y_coupler_pitch = self.params['y_coupler_pitch']
#
#         self.x_port_coupler_in_base = self.params['x_port_coupler_in_base']
#         self.x_port_coupler_out_base = self.params['x_port_coupler_out_base']
#         self.y_port_coupler_base = self.params['y_port_coupler_base']
#
#         self.dx_inst = self.params['dx_inst']
#         self.dy_inst = self.params['dy_inst']
#         self.dy_port_inst_bot = self.params['dy_port_inst_bot']
#         self.x_instance = self.params['x_instance']
#
#         self.bend_radius = self.photonic_tech_info.get_default_wg_params(self.wg_routing_layer)['radius']
#         self.routing_width = self.photonic_tech_info.get_default_wg_params(self.wg_routing_layer)['width']
#
#     @classmethod
#     def get_params_info(cls):
#         return dict(
#             # package_class_param_list='',
#             yaml_list='',
#             site_pitch='',
#             track_pitch='',
#
#             x_coupler_clear='',
#             y_coupler_clear='',
#             x_coupler_pitch='',
#             y_coupler_pitch='',
#
#             x_port_coupler_in_base='',
#             x_port_coupler_out_base='',
#             y_port_coupler_base='',
#
#             dx_inst='',
#             dy_inst='',
#             dy_port_inst_bot='',
#             x_instance='',
#
#
#         )
#
#     @classmethod
#     def get_default_param_values(cls):
#         return dict(
#         )
#
#     def draw_layout(self):
#
#         # # Unpack the package list
#         # for packclassparam in self.package_class_param_list:
#         #     lay_module = importlib.import_module(packclassparam['package'])
#         #     temp_cls = getattr(lay_module, packclassparam['class'])
#         #
#         #     master = self.new_template(params=packclassparam['params'],
#         #                                temp_cls=temp_cls)
#         #
#         #     self.master_list.append(master)
#
#         # # Instantiate the sites
#         # for ind, yaml_file in enumerate(self.yaml_list):
#         #     with open(yaml_file, 'r') as f:
#         #         yaml_content = yaml.load(f)
#         #
#         #     lay_module = importlib.import_module('cena_top.RAMPS.photonics.' + yaml_content['layout_package'])
#         #     temp_cls = getattr(lay_module, yaml_content['layout_class'])
#         #
#         #     master = self.new_template(params=yaml_content['layout_params'],
#         #                                temp_cls=temp_cls)
#         #
#         #     self.master_list.append(master)
#         #
#         #
#         # in_port_name = 'PORT0'
#         # out_port_name = 'PORT1'
#         #
#         # for ind, master in enumerate(self.master_list):
#         #     master_in_port_loc = master.get_photonic_port(in_port_name).center
#         #     self.inst_list.append(
#         #         self.add_instance(
#         #             master=master,
#         #             loc=((ind * self.site_pitch - master_in_port_loc[0]),
#         #                  (0 - master_in_port_loc[1])),
#         #             # Offset site by location of input port, to put input port at desired location
#         #             orient='R0',
#         #         )
#         #     )
#         #
#         #
#         #
#         #
#         # num_sites = len(self.master_list)
#         #
#         # y0_top = max([inst.bound_box.top for inst in self.inst_list]) + 2 * self.track_pitch
#         #
#         # # inst.bound_box.bot doesn't exist?
#         # # WgRouter routability determines "6"
#         # y0_bot = min([inst.bound_box.top - inst.bound_box.height for inst in self.inst_list]) - 6 * self.track_pitch
#         #
#         # x_starts = self.inst_list[0][in_port_name].x - 2 * self.bend_radius
#         # x_ends = self.inst_list[-1][out_port_name].x + 2 * self.bend_radius + self.site_pitch/2
#
#
#         n_site = 3
#         #### define coupler port positions
#         list_idx = [0, 2, 1]
#         list_x_port_coupler_in = [
#             self.x_port_coupler_in_base + list_idx[i] * self.x_coupler_pitch for i in range(0, n_site)
#         ]
#         list_x_port_coupler_out = [
#             self.x_port_coupler_out_base + list_idx[i] * self.x_coupler_pitch for i in range(0, n_site)
#         ]
#         list_y_port_coupler = [
#             self.y_port_coupler_base + i * self.y_coupler_pitch for i in range(0, 2)
#         ]
#
#         # x_coupler_port_in = self.x_coupler_port_in_base + [0, ]
#         # y_coupler_port = self.y_coupler_port
#         # dx_inst_port_min = self.dx_inst_port_min
#         # dy_inst_port_min = self.dy_inst_port_min
#         list_x_port_inst_in = [self.x_instance[i] - self.dx_inst / 2 for i in range(0, n_site)]
#         list_x_port_inst_out = [self.x_instance[i] + self.dx_inst / 2 for i in range(0, n_site)]
#
#
#         # y_track_inst_bot = 3 * self.track_pitch
#         # y_track_inst_top_min = y_track_inst_bot + dy_inst_port_min
#
#         # 4 long horizontal waveguide tracks on the bottom side of the instances
#         list_y_track_bot = [self.track_pitch * (i+1) for i in range(0, 4)]
#         # horizontal track the bottom ports of the instances are on
#         # list_y_port_inst_bot = [list_y_track_bot[2], list_y_track_bot[0], list_y_track_bot[2]]
#         # list_y_port_inst_top = [
#         #     self.dy_inst + y_port_inst_bot for y_port_inst_bot in list_y_port_inst_bot
#         # ]
#         list_y_port_inst_bot = [list_y_track_bot[2] + self.dy_port_inst_bot for i in range(0, 3)]
#         list_y_port_inst_top = [list_y_track_bot[2] + self.dy_inst for i in range(0, 3)]
#
#         # TODO: check if these positions are appropriate
#         if (list_x_port_coupler_in[0] < self.track_pitch * 3 + self.x_coupler_clear):
#             raise ValueError('Input Coupler x coordinate is too low')
#         if (list_y_port_coupler[0] < list_y_track_bot[-1] + self.track_pitch + self.y_coupler_clear / 2):
#             raise ValueError('Coupler y coordinate is too low, will conflict with waveguide routing')
#
#         # 7 long horizontal waveguide tracks on the top side of the instances
#         list_y_track_top = [
#             i * self.track_pitch + list_y_track_bot[2] + self.dy_inst for i in range(0, 7)
#         ]
#
#         if list_y_track_top[1] <= list_y_port_coupler[0]:
#             y_track_temp = list_y_port_coupler[0]
#         else:
#             y_track_temp = max(list_y_track_top[1], list_y_port_coupler[0] + self.bend_radius * 2)
#         list_y_track_top[1:] = [(y_track_temp - list_y_track_top[1]) + element for element in list_y_track_top[1:]]
#
#         if list_y_track_top[2] <= list_y_port_coupler[1]:
#             y_track_temp = list_y_port_coupler[1]
#         else:
#             y_track_temp = max(list_y_track_top[2], list_y_port_coupler[1] + self.bend_radius * 2)
#         list_y_track_top[2:] = [(y_track_temp - list_y_track_top[2]) + element for element in list_y_track_top[2:]]
#
#         y_track_temp = max(list_y_track_top[3],
#                            list_y_port_coupler[0] + self.bend_radius * 2,
#                            list_y_port_coupler[1] + self.y_coupler_clear / 2 + self.bend_radius)
#         list_y_track_top[3:] = [(y_track_temp - list_y_track_top[3]) + element for element in list_y_track_top[3:]]
#
#         y_track_temp = max(list_y_port_coupler[1] + self.bend_radius * 2, list_y_track_top[4])
#         list_y_track_top[4:] = [(y_track_temp - list_y_track_top[4]) + element for element in list_y_track_top[4:]]
#
#         # y_track_temp = max(list_y_port_coupler[1] + self.y_coupler_clear / 2 + self.bend_radius, list_y_track_top[5])
#         # list_y_track_top[5:] = [(y_track_temp - list_y_track_top[5]) + element for element in list_y_track_top[5:]]
#
#
#         # horizontal track the top ports of the instances are on
#         # list_y_port_inst_top = [list_y_port_inst_bot[i] + self.dy_inst for i in range(0, n_site)]
#
#
#
#
#         #
#         # if y_track_inst_top_min <= y_coupler_port[1]:
#         #     y_track_inst_top = y_coupler_port[1]
#         # else:
#         #     y_track_inst_top = y_coupler_port[1] + self.bend_radius * 2
#         #
#         # y_track_site1_top = max(y_track_inst_top, y_coupler_port[1]) + self.bend_radius * 2
#
#
#
#         list_port_in_main = [
#             self.add_photonic_port(
#                 name=f'IN_MAIN{i}',
#                 center=(list_x_port_coupler_in[i], list_y_port_coupler[0]),
#                 orient='R0',
#                 layer=self.wg_port_layer,
#                 width=self.routing_width
#             )
#             for i in range(0, n_site)
#         ]
#         list_port_in_drop = [
#             self.add_photonic_port(
#                 name=f'IN_DROP{i}',
#                 center=(list_x_port_coupler_in[i], list_y_port_coupler[1]),
#                 orient='R0',
#                 layer=self.wg_port_layer,
#                 width=self.routing_width
#             )
#
#             for i in range(0, n_site)
#         ]
#         list_port_out_main = [
#             self.add_photonic_port(
#                 name=f'OUT_MAIN{i}',
#                 center=(list_x_port_coupler_out[i], list_y_port_coupler[0]),
#                 orient='R0',
#                 layer=self.wg_port_layer,
#                 width=self.routing_width
#             )
#             for i in range(0, n_site)
#         ]
#         list_port_out_drop = [
#             self.add_photonic_port(
#                 name=f'OUT_DROP{i}',
#                 center=(list_x_port_coupler_out[i], list_y_port_coupler[1]),
#                 orient='R0',
#                 layer=self.wg_port_layer,
#                 width=self.routing_width
#             )
#             for i in range(0, n_site)
#         ]
#
#
#
#         list_router_in_main = [
#             WgRouter(
#                 self,
#                 list_port_in_main[i],
#                 self.wg_routing_layer,
#                 route_in_port_dir=True
#             )
#             for i in range(0, n_site)
#         ]
#         list_router_in_drop = [
#             WgRouter(
#                 self,
#                 list_port_in_drop[i],
#                 self.wg_routing_layer,
#                 route_in_port_dir=True
#             )
#             for i in range(0, n_site)
#         ]
#         list_router_out_main = [
#             WgRouter(
#                 self,
#                 list_port_out_main[i],
#                 self.wg_routing_layer,
#                 route_in_port_dir=False
#             )
#             for i in range(0, n_site)
#         ]
#         list_router_out_drop = [
#             WgRouter(
#                 self,
#                 list_port_out_drop[i],
#                 self.wg_routing_layer,
#                 route_in_port_dir=False
#             )
#             for i in range(0, n_site)
#         ]
#
#
#         #### site 0
#         idx_now = 0
#
#         list_router_in_main[idx_now].cardinal_router(
#             [
#                 (list_x_port_coupler_in[idx_now] + self.bend_radius * 1,
#                  list_y_port_coupler[0] - self.bend_radius * 1),
#                 (list_x_port_inst_in[idx_now] - self.bend_radius * 4,
#                  list_y_track_bot[2]),
#                 (list_x_port_inst_in[idx_now] - self.bend_radius * 3,
#                  list_y_port_inst_bot[idx_now] + self.bend_radius * 1),
#                 (list_x_port_inst_in[idx_now] - self.bend_radius * 2,
#                  list_y_port_inst_bot[idx_now] + self.bend_radius * 2),
#                 (list_x_port_inst_in[idx_now] - self.bend_radius * 1,
#                  list_y_port_inst_bot[idx_now] + self.bend_radius * 1),
#                 (list_x_port_inst_in[idx_now],
#                  list_y_port_inst_bot[idx_now])
#             ]
#         )
#         list_router_in_drop[idx_now].cardinal_router(
#             [
#                 (list_x_port_coupler_in[idx_now] + self.bend_radius * 1 + self.track_pitch,
#                  list_y_port_coupler[1] - self.bend_radius * 1),
#                 (list_x_port_inst_in[idx_now] - self.bend_radius * 4 - self.track_pitch,
#                  list_y_track_bot[3]),
#                 (list_x_port_inst_in[idx_now] - self.bend_radius * 3 - self.track_pitch,
#                  list_y_port_inst_top[idx_now] - self.bend_radius * 1),
#                 (list_x_port_inst_in[idx_now],
#                  list_y_port_inst_top[idx_now]),
#             ]
#         )
#
#         list_router_out_main[idx_now].cardinal_router(
#             [
#                 (list_x_port_coupler_out[idx_now] - self.bend_radius * 1 - self.track_pitch,
#                  list_y_port_coupler[0] + self.bend_radius),
#                 (self.track_pitch * 2 + self.bend_radius,
#                  list_y_track_top[-2]),
#                 (self.track_pitch * 2,
#                  list_y_track_bot[1] + self.bend_radius),
#                 (list_x_port_inst_out[idx_now] + self.bend_radius * 2,
#                  list_y_track_bot[1]),
#                 (list_x_port_inst_out[idx_now] + self.bend_radius * 3,
#                  list_y_track_bot[1] + self.bend_radius * 1),
#                 (list_x_port_inst_out[idx_now] + self.bend_radius * 2,
#                  list_y_port_inst_bot[idx_now] + self.bend_radius * 2),
#                 (list_x_port_inst_out[idx_now] + self.bend_radius * 1,
#                  list_y_port_inst_bot[idx_now] + self.bend_radius * 1),
#                 (list_x_port_inst_out[idx_now],
#                  list_y_port_inst_bot[idx_now]),
#             ]
#         )
#
#         list_router_out_drop[idx_now].cardinal_router(
#             [
#                 (list_x_port_coupler_out[idx_now] - self.bend_radius * 1,
#                  list_y_port_coupler[1] + self.bend_radius),
#                 (self.track_pitch * 1 + self.bend_radius,
#                  list_y_track_top[-1]),
#                 (self.track_pitch * 1,
#                  list_y_track_bot[0] + self.bend_radius),
#                 (self.track_pitch * 1 + self.bend_radius,
#                  list_y_track_bot[0]),
#                 (list_x_port_inst_out[idx_now] + self.bend_radius * 3 + self.track_pitch,
#                  list_y_port_inst_top[idx_now] - self.bend_radius * 1),
#                 (list_x_port_inst_out[idx_now],
#                  list_y_port_inst_top[idx_now]),
#             ]
#         )
#
#
#
#         #### site 1
#         idx_now = 1
#
#         router_path = [
#             (list_x_port_inst_in[idx_now] - self.bend_radius * 3 - self.track_pitch,
#              list_y_port_inst_bot[idx_now] + self.bend_radius * 1),
#             (list_x_port_inst_in[idx_now],
#              list_y_port_inst_bot[idx_now]),
#         ]
#         if list_y_track_top[1] > list_y_port_coupler[0]:
#             router_path = [
#                 (list_x_port_coupler_in[idx_now] + self.bend_radius * 1 + self.track_pitch,
#                  list_y_port_coupler[0] + self.bend_radius * 1),
#                 (list_x_port_inst_in[idx_now] - self.bend_radius * 3 - self.track_pitch,
#                  list_y_track_top[1]),
#             ] + router_path
#
#         list_router_in_main[idx_now].cardinal_router(
#             router_path
#         )
#
#         if (list_y_track_top[2] - list_y_port_inst_top[idx_now] < self.bend_radius * 2):
#             # list_y_port_inst_top[idx_now] = list_y_track_top[2]
#             router_path = [
#                 (list_x_port_inst_in[idx_now] - self.bend_radius * 3,
#                  list_y_port_inst_top[idx_now] - self.bend_radius * 1),
#                 (list_x_port_inst_in[idx_now] - self.bend_radius * 2,
#                  list_y_port_inst_top[idx_now] - self.bend_radius * 2),
#                 (list_x_port_inst_in[idx_now] - self.bend_radius * 1,
#                  list_y_port_inst_top[idx_now] - self.bend_radius * 1),
#                 (list_x_port_inst_in[idx_now],
#                  list_y_port_inst_top[idx_now]),
#             ]
#         else:
#             router_path = [
#                 (list_x_port_inst_in[idx_now] - self.bend_radius * 1,
#                  list_y_port_inst_top[idx_now] + self.bend_radius * 1),
#                 (list_x_port_inst_in[idx_now],
#                  list_y_port_inst_top[idx_now])
#             ]
#
#         if list_y_track_top[2] > list_y_port_coupler[1]:
#             router_path = [
#                 (list_x_port_coupler_in[idx_now] + self.bend_radius * 1,
#                  list_y_port_coupler[1] + self.bend_radius * 1),
#                 (list_x_port_coupler_in[idx_now] + self.bend_radius * 2,
#                  list_y_track_top[2]),
#             ] + router_path
#
#         list_router_in_drop[idx_now].cardinal_router(
#             router_path
#         )
#         list_router_out_main[idx_now].cardinal_router(
#             [
#                 (list_x_port_coupler_out[idx_now] - self.bend_radius * 1,
#                  list_y_port_coupler[0] - self.bend_radius * 1),
#                 (list_x_port_inst_out[idx_now] + self.bend_radius * 4,
#                  list_y_track_bot[0]),
#                 (list_x_port_inst_out[idx_now] + self.bend_radius * 3,
#                  list_y_port_inst_bot[idx_now] + self.bend_radius * 1),
#                 (list_x_port_inst_out[idx_now] + self.bend_radius * 2,
#                  list_y_port_inst_bot[idx_now] + self.bend_radius * 2),
#                 (list_x_port_inst_out[idx_now] + self.bend_radius * 1,
#                  list_y_port_inst_bot[idx_now] + self.bend_radius * 1),
#                 (list_x_port_inst_out[idx_now],
#                  list_y_port_inst_bot[idx_now]),
#             ]
#         )
#         list_router_out_drop[idx_now].cardinal_router(
#             [
#                 (list_x_port_coupler_out[idx_now] - self.bend_radius * 1 - self.track_pitch,
#                  list_y_port_coupler[1] - self.bend_radius * 1),
#                 (list_x_port_inst_out[idx_now] + self.bend_radius * 4 + self.track_pitch,
#                  list_y_track_bot[1]),
#                 (list_x_port_inst_out[idx_now] + self.bend_radius * 3 + self.track_pitch,
#                  list_y_port_inst_top[idx_now] - self.bend_radius),
#                 (list_x_port_inst_out[idx_now],
#                  list_y_port_inst_top[idx_now]),
#             ]
#         )
#
#         #### site 2
#         idx_now = 2
#
#         list_router_in_main[idx_now].cardinal_router(
#             [
#                 (list_x_port_coupler_in[idx_now] + self.bend_radius * 1 + self.track_pitch,
#                  list_y_port_coupler[0] + self.bend_radius * 1),
#                 (list_x_port_inst_in[idx_now] - self.bend_radius * 2 - self.track_pitch,
#                  list_y_track_top[3]),
#                 (list_x_port_inst_in[idx_now] - self.bend_radius * 1 - self.track_pitch,
#                  list_y_port_inst_bot[idx_now] + self.bend_radius * 1),
#                 (list_x_port_inst_in[idx_now],
#                  list_y_port_inst_bot[idx_now]),
#             ]
#         )
#
#         list_router_in_drop[idx_now].cardinal_router(
#             [
#                 (list_x_port_coupler_in[idx_now] + self.bend_radius * 1,
#                  list_y_port_coupler[1] + self.bend_radius * 1),
#                 (list_x_port_inst_in[idx_now] - self.bend_radius * 2,
#                  list_y_track_top[4]),
#                 (list_x_port_inst_in[idx_now] - self.bend_radius * 1,
#                  list_y_port_inst_top[idx_now] + self.bend_radius * 1),
#                 (list_x_port_inst_in[idx_now],
#                  list_y_port_inst_top[idx_now]),
#             ]
#         )
#         list_router_out_main[idx_now].cardinal_router(
#             [
#                 (list_x_port_coupler_out[idx_now] - self.bend_radius * 1,
#                  list_y_port_coupler[0] - self.bend_radius * 1),
#                 (list_x_port_inst_out[idx_now] + self.bend_radius * 4,
#                  list_y_track_bot[2]),
#                 (list_x_port_inst_out[idx_now] + self.bend_radius * 3,
#                  list_y_port_inst_bot[idx_now] + self.bend_radius * 1),
#                 (list_x_port_inst_out[idx_now] + self.bend_radius * 2,
#                  list_y_port_inst_bot[idx_now] + self.bend_radius * 2),
#                 (list_x_port_inst_out[idx_now] + self.bend_radius * 1,
#                  list_y_port_inst_bot[idx_now] + self.bend_radius * 1),
#                 (list_x_port_inst_out[idx_now],
#                  list_y_port_inst_bot[idx_now]),
#             ]
#         )
#         list_router_out_drop[idx_now].cardinal_router(
#             [
#                 (list_x_port_coupler_out[idx_now] - self.bend_radius * 1 - self.track_pitch,
#                  list_y_port_coupler[1] - self.bend_radius * 1),
#                 (list_x_port_inst_out[idx_now] + self.bend_radius * 4 + self.track_pitch,
#                  list_y_track_bot[3]),
#                 (list_x_port_inst_out[idx_now] + self.bend_radius * 3 + self.track_pitch,
#                  list_y_port_inst_top[idx_now] - self.bend_radius),
#                 (list_x_port_inst_out[idx_now],
#                  list_y_port_inst_top[idx_now]),
#             ]
#         )
#
#
#         # router_in_main.cardinal_router(
#         #     [(x_instance[idx_now]-dx_inst_port_min/2, y_track_inst_bot)
#         #      ]
#         # )
#
#
#
#
#
#         # for ind in range(len(self.inst_list)):
#         #
# 		 #    # Ports define "routing tracks"
#         #     start_port = self.add_photonic_port(
#         #         name=f'IN{ind}',
#         #         center=(x_starts, y0_top + ind * self.track_pitch),
#         #         orient='R0',
#         #         layer=self.wg_port_layer,
#         #         width=self.routing_width
#         #     )
#         #     end_port = self.add_photonic_port(
#         #         name=f'OUT{ind}',
#         #         center=(x_ends, y0_bot + ind * self.track_pitch),
#         #         orient='R0',
#         #         layer=self.wg_port_layer,
#         #         width=self.routing_width
#         #    )
#         #
#         #     inst = self.inst_list[ind]
#         #
#         #     # Route from the start to the site
#         #     router = WgRouter(self,
#         #                       start_port,
#         #                       self.wg_routing_layer,
#         #                       route_in_port_dir=True
#         #                       )
#         #
#         #     router.cardinal_router(
#         #         [(inst[in_port_name].x - self.bend_radius,
#         #           inst[in_port_name].y + self.bend_radius),
#         #          (inst[in_port_name].x,
#         #           inst[in_port_name].y),
#         #         ])
#         #
#         #     # Route from the output of the site to the end
#         #     router_end = WgRouter(self,
#         #                         inst[out_port_name],
#         #                         self.wg_routing_layer,
#         #                         # What is this?
#         #                         route_in_port_dir=False
#         #                         )
#         #
#         #     # Better solution?
#         #     router_end.cardinal_router(
#         #         [(inst[out_port_name].x + self.site_pitch/2.0 - 2*self.bend_radius,
#         #         inst[out_port_name].y),
#         #         (inst[out_port_name].x + self.site_pitch/2.0 - self.bend_radius,
#         #         inst[out_port_name].y - self.bend_radius),
#         #         (inst[out_port_name].x + self.site_pitch/2.0 - self.bend_radius,
#         #         end_port.y + self.bend_radius),
#         #         (inst[out_port_name].x + self.site_pitch/2.0,
#         #         end_port.y),
#         #         (end_port.x, end_port.y)
#         #         ]
#         #     )
#
#
#
# class DummySite(PhotonicTemplateBase):
#     """
#     Photonic Ports:
#     IN = left side
#     OUT = right side
#     """
#
#     def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
#         PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)
#
#         self.port_width = 0.35
#         self.wg_port_layer = ('si_full_free', 'port')
#         self.wg_routing_layer = ('si_full_free', 'drawing')
#         self.length = self.params['length']
#
#     @classmethod
#     def get_params_info(cls):
#         return dict(
#             length=''
#         )
#
#     @classmethod
#     def get_default_param_values(cls):
#         return dict(
#             length=15
#         )
#
#     def draw_layout(self):
#
#         start_port = self.add_photonic_port(
#             name='IN',
#             center=(0, 0),
#             orient='R0',
#             angle=0.0,
#             width=self.port_width,
#             layer=self.wg_port_layer
#         )
#
#         router = WgRouter(self,
#                           start_port,
#                           self.wg_routing_layer,
#                           route_in_port_dir=True
#                           )
#
#
#         router.add_straight_wg(self.length)
#
#         port = router.port
#         port.name = 'OUT'
#
#         self.add_photonic_port(port=port)
#
#         self.add_round(
#             layer=self.wg_routing_layer,
#             resolution=self.grid.resolution,
#             rout=5,
#             center=(0.5 * self.length, 5 + 0.1 + 0.5 * self.port_width),
#             rin=4
#         )
#
#
# class TripleRingRowArray(PhotonicTemplateBase):
#     """
#     Photonic Ports:
#     IN = left side
#     OUT = right side
#     """
#
#     def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
#         PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)
#         self.params = params
#         # for key, val in self.params.items():
#         #     # Automatically unpack variables
#         #     # exec( “self.{} = {}“.format( key, val ) )
#         #     exec(f”self.{key} = {val!r}” )
#
#
#         self.port_width = 0.35
#         self.wg_port_layer = ('si_full_free', 'port')
#         self.wg_routing_layer = ('si_full_free', 'drawing')
#         # self.wg_port_layer = ('RX', 'port')
#         # self.wg_routing_layer = ('RX', 'drawing')
#
#         self.grating_coupler_module = self.params['grating_coupler_module']
#         self.grating_coupler_class = self.params['grating_coupler_class']
#         gc_module = importlib.import_module(self.grating_coupler_module)
#         gc_class = getattr(gc_module, self.grating_coupler_class)
#         self.gc_master = self.new_template(params=None, temp_cls=gc_class)
#
#
#         self.package_class_param_list = self.params['package_class_param_list']
#         self.yaml_list = self.params['yaml_list']
#
#         self.master_list = []
#         self.inst_list = []
#         self.site_pitch = self.params['site_pitch']
#         self.track_pitch = self.params['track_pitch']
#
#         self.x_coupler_clear = self.params['x_coupler_clear']
#         self.y_coupler_clear = self.params['y_coupler_clear']
#         self.x_coupler_pitch = self.params['x_coupler_pitch']
#         self.y_coupler_pitch = self.params['y_coupler_pitch']
#
#         self.x_port_coupler_in_base = self.params['x_port_coupler_in_base']
#         self.x_port_coupler_out_base = self.params['x_port_coupler_out_base']
#         self.y_port_coupler_base = self.params['y_port_coupler_base']
#
#         self.dx_inst = self.params['dx_inst']
#         self.dy_inst = self.params['dy_inst']
#         self.x_instance = self.params['x_instance']
#         self.dy_port_inst_bot = self.params['dy_port_inst_bot']
#         self.dy_port_inst_top = self.params['dy_port_inst_top']
#
#
#         self.n_rowpairs = self.params['n_rowpairs']
#         self.y_pitch_rowpairs = self.params['y_pitch_rowpairs']
#         self.y_split_in_pair = self.params['y_split_in_pair']
#
#         self.bend_radius = self.photonic_tech_info.get_default_wg_params(self.wg_routing_layer)['radius']
#         self.routing_width = self.photonic_tech_info.get_default_wg_params(self.wg_routing_layer)['width']
#
#
#
#
#     @classmethod
#     def get_params_info(cls):
#         return dict(
#             package_class_param_list='',
#             yaml_list='',
#             site_pitch='',
#             track_pitch='',
#
#             x_coupler_clear='',
#             y_coupler_clear='',
#             x_coupler_pitch='',
#             y_coupler_pitch='',
#
#             x_port_coupler_in_base='',
#             x_port_coupler_out_base='',
#             y_port_coupler_base='',
#
#             dx_inst='',
#             dy_inst='',
#             dy_port_inst_bot='',
#             dy_port_inst_top='',
#             x_instance='',
#             param_x='',
#
#             grating_coupler_module='',
#             grating_coupler_class='',
#
#
#         )
#
#     @classmethod
#     def get_default_param_values(cls):
#         return dict(
#         )
#
#     def draw_layout(self):
#
#
#         n_site = 3
#         for i in range(0, self.n_rowpairs):
#             layout_params_r180 = self.params
#             layout_params_r0 = self.params
#             yaml_list_mx = self.yaml_list[n_site*(2*i+0):n_site*(2*i+1)]
#             yaml_list_r0 = self.yaml_list[n_site*(2*i+1):n_site*(2*i+2)]
#             layout_params_r180['yaml_list'] = yaml_list_mx
#             layout_params_r0['yaml_list'] = yaml_list_r0
#
#             master_r180 = self.new_template(params=layout_params_r180, temp_cls=TripleRingRowV1)
#             master_r0 = self.new_template(params=layout_params_r0, temp_cls=TripleRingRowV1)
#
#             #
#             dx_inst_r180 = master_r180.bound_box.width
#             x_coupler_r180_rightmost = self.x_port_coupler_out_base + \
#                                      self.x_coupler_pitch * (n_site-1)
#             x_inst_r180 = self.x_port_coupler_in_base + x_coupler_r180_rightmost
#             # x_inst_mx = 0
#             y_inst_r180 = self.y_pitch_rowpairs * i + \
#                           self.y_port_coupler_base * 2 - self.y_coupler_pitch
#             x_inst_r0 = 0
#             y_inst_r0 = y_inst_r180 + self.y_split_in_pair
#
#             # hfshfs
#
#             self.add_instance(
#                 master=master_r180,
#                 loc=(x_inst_r180, y_inst_r180),
#                 orient='R180',
#             )
#             self.add_instance(
#                 master=master_r0,
#                 loc=(x_inst_r0, y_inst_r0),
#                 orient='R0',
#             )