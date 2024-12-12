# Last updated 11/03/2021

# This is a BPG script used to generate photonic top (Cryo TX and Coherent RX) gds for 45SPCLO Nov2021 tapeout

import BPG

from numpy import sqrt, pi, linspace, sin, cos
import numpy as np
from BPG.objects import PhotonicPolygon, PhotonicRound
from BPG.port import PhotonicPort

from copy import deepcopy
import yaml
import importlib

from Photonic_Core_Layout.AdiabaticPaths.AdiabaticPaths import AdiabaticPaths
from Photonic_Core_Layout.WaveguideBase.WgRouter import WgRouter
from Photonic_Core_Layout.ViaStack.ViaStack import ViaStack


class CoherentLink(BPG.PhotonicTemplateBase):
    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)
        self.params = params
        for key, val in self.params.items():  # Automatically unpack variables
            # exec( "self.{} = {}".format( key, val ) )
            exec(f"self.{key} = {val!r}")

        # ================================================================
        # Create all templates (may need them to get geometry parameters)
        # ================================================================

        # Create class of each device component
        gc_module = importlib.import_module(self.grating_coupler_module)
        gc_class = getattr(gc_module, self.grating_coupler_class)
        self.gc_master = self.new_template(params=None, temp_cls=gc_class)
        self.gc_array_inst = [None] * self.grating_coupler_num

        pd_module = importlib.import_module(self.pd_module)
        pd_class = getattr(pd_module, self.pd_class)
        self.pd_master = self.new_template(params=None, temp_cls=pd_class)

        ps_module = importlib.import_module(self.phase_shifter_module)
        ps_cls = getattr(ps_module, self.phase_shifter_class)
        self.ps_master = self.new_template(params=self.phase_shifter_params, temp_cls=ps_cls)


        self.rac_template = self.create_template(
            photonic_spec_file=self.rac_spec_file,
            photonic_module_name=self.rac_module,
            photonic_class_name=self.rac_class,
        )

        self.bend_radius = self.photonic_tech_info.get_default_wg_params(self.wg_routing_layer)['radius'] + 0.1
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
            grating_coupler_module=None,
            grating_coupler_class=None,
            grating_coupler_spec_file=None,
            grating_coupler_loc_offset=[127, 127],
            grating_coupler_pitch=127.0,
            grating_coupler_num=0,
            rac_module=None,
            rac_class=None,
            rac_spec_file=None,
            pd_module=None,
            pd_class=None,
            pd_spec_file=None,
            photonic_spec_file=None,
            photonic_module_name=None,
            photonic_class_name=None,
            wg_routing_layer=None,

        )

    @classmethod
    def get_params_info(cls) -> dict:
        return dict(
            grating_coupler_module='TODO',
            grating_coupler_class='TODO',
            grating_coupler_spec_file='TODO',
            grating_coupler_loc_offset='TODO',
            grating_coupler_pitch='TODO',
            grating_coupler_num='TODO',
            rac_module='TODO',
            rac_class='TODO',
            rac_spec_file='TODO',
            pd_module='TODO',
            pd_class='TODO',
            pd_spec_file='TODO',
            photonic_spec_file='TODO',
            photonic_module_name='TODO',
            photonic_class_name='TODO',
            wg_routing_layer='TODO',

        )

    def draw_layout(self):
        # Draw pads and fixed photonic devices relative to pad locs
        # self.draw_pads( )

        # self.draw_source_ring( )
        # self.draw_bus_wg( )




        self.place_instances()
        self.wg_routing()
        self.add_ports()



    def place_instances(self):

        rac_port_bl_loc     = self.rac_template.get_photonic_port('IN_BOT').center
        rac_port_tl_loc     = self.rac_template.get_photonic_port('IN_TOP').center
        rac_port_br_loc     = self.rac_template.get_photonic_port('OUTPUT_BOT').center
        rac_port_tr_loc     = self.rac_template.get_photonic_port('OUTPUT_TOP').center

        w_rac   = rac_port_tr_loc[0] - rac_port_bl_loc[0]
        h_rac   = max(rac_port_tr_loc[1] - rac_port_bl_loc[1], rac_port_tl_loc[1] - rac_port_br_loc[1])
        w_ps    = self.ps_master.bound_box.width
        w_pd    = self.pd_master.bound_box.width
        h_pd    = self.pd_master.bound_box.height

        x_rac           = self.bend_radius * 2
        y_rac           = h_rac + (self.bend_radius + self.r_extra) * 2 + h_pd
        x_pd            = x_rac + max(w_rac + (self.bend_radius + self.r_extra) * 2, w_ps) + \
                          self.dx_pd_extra
        x_pd_dum        = x_pd + self.dx_pd_dummy


        self.inst_rac = self.add_instance(
            master=self.rac_template,
            loc=(x_rac, y_rac),
            orient='R0'
        )


        self.inst_pd_bot = self.add_instance(
            master=self.pd_master,
            loc=(x_pd, self.inst_rac['OUTPUT_BOT'].center[1] - (self.bend_radius + self.r_extra) * 2),
            orient='R0'
        )
        self.inst_pd_top = self.add_instance(
            master=self.pd_master,
            loc=(x_pd, self.inst_rac['OUTPUT_TOP'].center[1] + (self.bend_radius + self.r_extra) * 2),
            orient='R0'
        )

        self.inst_pd_bot_dum = self.add_instance(
            master=self.pd_master,
            loc=(x_pd_dum, self.inst_rac['OUTPUT_BOT'].center[1] - (self.bend_radius + self.r_extra) * 2 + self.dy_pd_dummy),
            orient='R0'
        )
        self.inst_pd_top_dum = self.add_instance(
            master=self.pd_master,
            loc=(x_pd_dum, self.inst_rac['OUTPUT_TOP'].center[1] + (self.bend_radius + self.r_extra) * 2 - self.dy_pd_dummy),
            orient='R0'
        )


        x_ps            = self.bend_radius * 2 + self.ps_master.get_photonic_port('PORT_OUT').center[0]
        y_ps            = self.inst_rac['OUTPUT_TOP'].center[1] + (self.bend_radius + self.r_extra) * 2 - \
                          self.ps_master.bound_box.bottom

        self.inst_ps = self.add_instance(
            master=self.ps_master,
            loc=(x_ps, y_ps),
            orient='MY'
        )



    def wg_routing(self):

        router_in_bot = WgRouter(
            gen_cls=self,
            init_port=self.inst_rac['IN_BOT'],
            layer=self.wg_routing_layer,
            name='wg_in_bot'
        )
        router_in_bot.cardinal_router(
            points=[
                self.inst_rac['IN_BOT'].center,
                [0, self.inst_rac['IN_BOT'].center[1]],
            ],
            bend_params=None,
            relative_coords=False
        )

        router_mid_top = WgRouter(
            gen_cls=self,
            init_port=self.inst_rac['IN_TOP'],
            layer=self.wg_routing_layer,
            name='wg_mid_top'
        )
        router_mid_top.cardinal_router(
            points=[
                self.inst_rac['IN_TOP'].center + [-self.bend_radius * 1, self.bend_radius * 1],
                self.inst_ps['PORT_OUT'].center,
            ],
            bend_params=None,
            relative_coords=False
        )
        router_in_top = WgRouter(
            gen_cls=self,
            init_port=self.inst_ps['PORT_IN'],
            layer=self.wg_routing_layer,
            name='wg_in_top'
        )
        router_in_top.cardinal_router(
            points=[
                self.inst_ps['PORT_IN'].center,
                # self.inst_ps['PORT_IN'].center + [self.bend_radius, self.bend_radius],
                # (max(self.inst_rac['IN_TOP'].center[0] + self.w_ps, self.inst_pd_top.bound_box.right),
                #  self.inst_ps['PORT_IN'].center[1]),
            ],
            bend_params=None,
            relative_coords=False
        )

        router_out_bot = WgRouter(
            gen_cls=self,
            init_port=self.inst_rac['OUTPUT_BOT'],
            layer=self.wg_routing_layer,
            name='wg_out_bot'
        )
        router_out_bot.cardinal_router(
            points=[self.inst_rac['OUTPUT_BOT'].center,
                    self.inst_rac['OUTPUT_BOT'].center + [self.bend_radius, -self.bend_radius],
                    self.inst_pd_bot['IN'].center],
            bend_params=None,
            relative_coords=False
        )

        router_out_top = WgRouter(
            gen_cls=self,
            init_port=self.inst_rac['OUTPUT_TOP'],
            layer=self.wg_routing_layer,
            name='wg_out_top'
        )
        router_out_top.cardinal_router(
            points=[self.inst_rac['OUTPUT_TOP'].center,
                    self.inst_rac['OUTPUT_TOP'].center + [self.bend_radius, self.bend_radius],
                    self.inst_pd_top['IN'].center],
            bend_params=None,
            relative_coords=False
        )
        ## fix drc for dummy PDs
        for inst_pd in [self.inst_pd_bot_dum, self.inst_pd_top_dum]:
            router_drc = WgRouter(
                gen_cls=self,
                init_port=inst_pd['IN'],
                layer=self.wg_routing_layer,
                name='wg_drc',
            )
            router_drc.cardinal_router(
            points=[inst_pd['IN'].center + [-0.1, 0]],
            bend_params=None,
            relative_coords=False
        )


    def add_ports(self):


        self.add_photonic_port(
            name='IN_LEFT',
            center=(0, self.inst_rac['IN_BOT'].center[1]),
            orient=self.inst_rac['IN_BOT'].orientation,
            width=self.inst_rac['IN_BOT'].width,
            layer=self.inst_rac['IN_BOT'].layer,
            resolution=self.inst_rac['IN_BOT'].resolution,
            angle=self.inst_rac['IN_BOT'].mod_angle,
        )

        self.add_photonic_port(
            name='IN_RIGHT',
            # center=(max(self.inst_rac['IN_TOP'].center[0] + self.w_ps, self.inst_pd_top.bound_box.right),
            #         self.inst_ps['PORT_IN'].center[1]),
            center=(self.inst_ps['PORT_IN'].center[0], self.inst_ps['PORT_IN'].center[1]),
            orient=self.inst_ps['PORT_IN'].orientation,
            width=self.inst_ps['PORT_IN'].width,
            layer=self.inst_ps['PORT_IN'].layer,
            resolution=self.inst_ps['PORT_IN'].resolution,
            angle=self.inst_ps['PORT_IN'].mod_angle,
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


class Hybrid90(BPG.PhotonicTemplateBase):
    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)
        self.params = params
        for key, val in self.params.items():  # Automatically unpack variables
            # exec( "self.{} = {}".format( key, val ) )
            exec(f"self.{key} = {val!r}")

        # ================================================================
        # Create all templates (may need them to get geometry parameters)
        # ================================================================

        # Create class of each device component
        gc_module = importlib.import_module(self.grating_coupler_module)
        gc_class = getattr(gc_module, self.grating_coupler_class)
        self.gc_master = self.new_template(params=None, temp_cls=gc_class)
        self.gc_array_inst = [None] * self.grating_coupler_num

        pd_module = importlib.import_module(self.pd_module)
        pd_class = getattr(pd_module, self.pd_class)
        self.pd_master = self.new_template(params=None, temp_cls=pd_class)

        self.rac_template = self.create_template(
            photonic_spec_file=self.rac_spec_file,
            photonic_module_name=self.rac_module,
            photonic_class_name=self.rac_class,
        )

        ps_module = importlib.import_module(self.phase_shifter_module)
        ps_cls = getattr(ps_module, self.phase_shifter_class)
        self.ps_master = self.new_template(params=self.phase_shifter_params, temp_cls=ps_cls)

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
            grating_coupler_module=None,
            grating_coupler_class=None,
            grating_coupler_spec_file=None,
            grating_coupler_loc_offset=[127, 127],
            grating_coupler_pitch=127.0,
            grating_coupler_num=0,
            rac_module=None,
            rac_class=None,
            rac_spec_file=None,
            pd_module=None,
            pd_class=None,
            pd_spec_file=None,
            photonic_spec_file=None,
            photonic_module_name=None,
            photonic_class_name=None,
            wg_routing_layer=None,

        )

    @classmethod
    def get_params_info(cls) -> dict:
        return dict(
            grating_coupler_module='TODO',
            grating_coupler_class='TODO',
            grating_coupler_spec_file='TODO',
            grating_coupler_loc_offset='TODO',
            grating_coupler_pitch='TODO',
            grating_coupler_num='TODO',
            rac_module='TODO',
            rac_class='TODO',
            rac_spec_file='TODO',
            pd_module='TODO',
            pd_class='TODO',
            pd_spec_file='TODO',
            photonic_spec_file='TODO',
            photonic_module_name='TODO',
            photonic_class_name='TODO',
            wg_routing_layer='TODO',

        )

    def draw_layout(self):
        # Draw pads and fixed photonic devices relative to pad locs
        # self.draw_pads( )

        # self.draw_source_ring( )
        # self.draw_bus_wg( )




        self.place_instances()
        self.wg_routing()
        self.add_ports()



    def place_instances(self):

        rac_port_bl_loc     = self.rac_template.get_photonic_port('IN_BOT').center
        rac_port_tl_loc     = self.rac_template.get_photonic_port('IN_TOP').center
        rac_port_br_loc     = self.rac_template.get_photonic_port('OUTPUT_BOT').center
        rac_port_tr_loc     = self.rac_template.get_photonic_port('OUTPUT_TOP').center

        w_rac   = rac_port_tr_loc[0] - rac_port_bl_loc[0]
        h_rac   = max(rac_port_tr_loc[1] - rac_port_bl_loc[1], rac_port_tl_loc[1] - rac_port_br_loc[1])
        w_ps    = self.ps_master.bound_box.width
        w_pd    = self.pd_master.bound_box.width
        h_pd    = self.pd_master.bound_box.height
        # x_iso   = -40

        x_ps            = w_rac + self.x_iso - self.ps_master.get_photonic_port('PORT_IN').center[0]
        list_x_rac      = [0, x_ps + w_ps]
        list_y_rac      = [(h_rac + self.bend_radius * 2 + h_pd) * i for i in range(0, 3)]
        list_y_ps       = [h_rac, list_y_rac[2]]
        x_pd            = list_x_rac[1] + w_rac
        x_pd_dum        = x_pd - self.dx_pd_dummy


        self.inst_rac_left    = self.add_instance(
            master=self.rac_template,
            loc=(list_x_rac[0], list_y_rac[1]),
            orient='R0'
        )

        self.inst_rac_right    = self.add_instance(
            master=self.rac_template,
            loc=(list_x_rac[1] + w_rac, list_y_rac[1]),
            orient='MY'
        )


        self.inst_rac_i    = self.add_instance(
            master=self.rac_template,
            loc=(list_x_rac[1], list_y_rac[0]),
            orient='R0'
        )

        self.inst_rac_q    = self.add_instance(
            master=self.rac_template,
            loc=(list_x_rac[1], list_y_rac[2] + h_rac),
            orient='MX'
        )


        self.inst_ps_i = self.add_instance(
            master=self.ps_master,
            loc=(x_ps, self.inst_rac_i['IN_BOT'].center[1] - self.ps_master.get_photonic_port('PORT_OUT').center[1]),
            orient='MX'
        )
        self.inst_ps_q = self.add_instance(
            master=self.ps_master,
            loc=(x_ps, self.inst_rac_q['IN_BOT'].center[1] + self.ps_master.get_photonic_port('PORT_OUT').center[1]),
            orient='R0'
        )


        self.inst_pd_i_bot = self.add_instance(
            master=self.pd_master,
            loc=(x_pd, self.inst_rac_i['OUTPUT_BOT'].center[1] - (self.bend_radius+self.r_extra) * 2),
            orient='MY'
        )
        self.inst_pd_i_top = self.add_instance(
            master=self.pd_master,
            loc=(x_pd, self.inst_rac_i['OUTPUT_TOP'].center[1] + (self.bend_radius+self.r_extra) * 2),
            orient='MY'
        )
        self.inst_pd_q_bot = self.add_instance(
            master=self.pd_master,
            loc=(x_pd, self.inst_rac_q['OUTPUT_TOP'].center[1] - (self.bend_radius+self.r_extra) * 2),
            orient='R180'
        )
        self.inst_pd_q_top = self.add_instance(
            master=self.pd_master,
            loc=(x_pd, self.inst_rac_q['OUTPUT_BOT'].center[1] + (self.bend_radius+self.r_extra) * 2),
            orient='R180'
        )
        self.inst_pd_i_bot_dum = self.add_instance(
            master=self.pd_master,
            loc=(x_pd_dum, self.inst_rac_i['OUTPUT_BOT'].center[1] - (self.bend_radius+self.r_extra) * 2 + self.dy_pd_dummy),
            orient='MY'
        )
        self.inst_pd_i_top_dum = self.add_instance(
            master=self.pd_master,
            loc=(x_pd_dum, self.inst_rac_i['OUTPUT_TOP'].center[1] + (self.bend_radius+self.r_extra) * 2 - self.dy_pd_dummy),
            orient='MY'
        )
        self.inst_pd_q_bot_dum = self.add_instance(
            master=self.pd_master,
            loc=(x_pd_dum, self.inst_rac_q['OUTPUT_TOP'].center[1] - (self.bend_radius+self.r_extra) * 2 + self.dy_pd_dummy),
            orient='R180'
        )
        self.inst_pd_q_top_dum = self.add_instance(
            master=self.pd_master,
            loc=(x_pd_dum, self.inst_rac_q['OUTPUT_BOT'].center[1] + (self.bend_radius+self.r_extra) * 2 - self.dy_pd_dummy),
            orient='R180'
        )



    def wg_routing(self):
        router_i_left = WgRouter(
            gen_cls=self,
            init_port=self.inst_rac_left['OUTPUT_BOT'],
            layer=self.wg_routing_layer,
            name='wg_i_left'
        )
        router_i_left.cardinal_router(
            points=[self.inst_rac_left['OUTPUT_BOT'].center + [self.bend_radius, -self.bend_radius],
                    self.inst_rac_left['OUTPUT_BOT'].center + [0, -self.bend_radius*2]],
            bend_params=None,
            relative_coords=False
        )
        router_i_left.add_fancy_s_bend((self.inst_rac_left['OUTPUT_BOT'].center[1] -
                                        self.inst_ps_i['PORT_IN'].center[1] - self.bend_radius*4),
                                       -self.x_iso)
        router_i_left.cardinal_router(
            points=[self.inst_ps_i['PORT_IN'].center + [-self.bend_radius, self.bend_radius],
                    self.inst_ps_i['PORT_IN'].center],
            bend_params=None,
            relative_coords=False
        )

        router_q_left = WgRouter(
            gen_cls=self,
            init_port=self.inst_rac_left['OUTPUT_TOP'],
            layer=self.wg_routing_layer,
            name='wg_q_left'
        )
        router_q_left.cardinal_router(
            points=[self.inst_rac_left['OUTPUT_TOP'].center + [self.bend_radius, self.bend_radius],
                    self.inst_rac_left['OUTPUT_TOP'].center + [0, self.bend_radius*2]],
            bend_params=None,
            relative_coords=False
        )
        router_q_left.add_fancy_s_bend((self.bend_radius*4 + self.inst_rac_left['OUTPUT_TOP'].center[1] -
                                        self.inst_ps_q['PORT_IN'].center[1]),
                                       -self.x_iso)
        router_q_left.cardinal_router(
            points=[self.inst_ps_q['PORT_IN'].center + [-self.bend_radius, -self.bend_radius],
                    self.inst_ps_q['PORT_IN'].center],
            bend_params=None,
            relative_coords=False
        )


        router_i_mid = WgRouter(
            gen_cls=self,
            init_port=self.inst_ps_i['PORT_OUT'],
            layer=self.wg_routing_layer,
            name='wg_i_mid'
        )
        router_i_mid.cardinal_router(
            [self.inst_rac_i['IN_BOT'].center],
        )
        router_q_mid = WgRouter(
            gen_cls=self,
            init_port=self.inst_ps_q['PORT_OUT'],
            layer=self.wg_routing_layer,
            name='wg_q_mid'
        )
        router_q_mid.cardinal_router(
            [self.inst_rac_q['IN_BOT'].center],
        )

        router_i_right = WgRouter(
            gen_cls=self,
            init_port=self.inst_rac_right['OUTPUT_BOT'],
            layer=self.wg_routing_layer,
            name='wg_i_right'
        )
        router_i_right.cardinal_router(
            points=[self.inst_rac_right['OUTPUT_BOT'].center,
                    self.inst_rac_right['OUTPUT_BOT'].center + [-self.bend_radius, -self.bend_radius],
                    self.inst_rac_i['IN_TOP'].center],
            bend_params=None,
            relative_coords=False
        )

        router_q_right = WgRouter(
            gen_cls=self,
            init_port=self.inst_rac_right['OUTPUT_TOP'],
            layer=self.wg_routing_layer,
            name='wg_q_right'
        )
        router_q_right.cardinal_router(
            points=[self.inst_rac_right['OUTPUT_TOP'].center,
                    self.inst_rac_right['OUTPUT_TOP'].center + [-self.bend_radius, self.bend_radius],
                    self.inst_rac_q['IN_TOP'].center],
            bend_params=None,
            relative_coords=False
        )


        router_i_bot = WgRouter(
            gen_cls=self,
            init_port=self.inst_rac_i['OUTPUT_BOT'],
            layer=self.wg_routing_layer,
            name='wg_i_bot'
        )
        router_i_bot.cardinal_router(
            points=[self.inst_rac_i['OUTPUT_BOT'].center,
                    self.inst_rac_i['OUTPUT_BOT'].center + [self.bend_radius+self.r_extra, -self.bend_radius-+self.r_extra],
                    self.inst_pd_i_bot['IN'].center],
            bend_params=None,
            relative_coords=False
        )

        router_i_top = WgRouter(
            gen_cls=self,
            init_port=self.inst_rac_i['OUTPUT_TOP'],
            layer=self.wg_routing_layer,
            name='wg_i_top'
        )
        router_i_top.cardinal_router(
            points=[self.inst_rac_i['OUTPUT_TOP'].center,
                    self.inst_rac_i['OUTPUT_TOP'].center + [self.bend_radius+self.r_extra, self.bend_radius+self.r_extra],
                    self.inst_pd_i_top['IN'].center],
            bend_params=None,
            relative_coords=False
        )

        router_q_bot = WgRouter(
            gen_cls=self,
            init_port=self.inst_rac_q['OUTPUT_TOP'],
            layer=self.wg_routing_layer,
            name='wg_q_bot'
        )
        router_q_bot.cardinal_router(
            points=[self.inst_rac_q['OUTPUT_TOP'].center,
                    self.inst_rac_q['OUTPUT_TOP'].center + [self.bend_radius+self.r_extra, -self.bend_radius-self.r_extra],
                    self.inst_pd_q_bot['IN'].center],
            bend_params=None,
            relative_coords=False
        )

        router_q_top = WgRouter(
            gen_cls=self,
            init_port=self.inst_rac_q['OUTPUT_BOT'],
            layer=self.wg_routing_layer,
            name='wg_q_top'
        )
        router_q_top.cardinal_router(
            points=[self.inst_rac_q['OUTPUT_BOT'].center,
                    self.inst_rac_q['OUTPUT_BOT'].center + [self.bend_radius+self.r_extra, self.bend_radius+self.r_extra],
                    self.inst_pd_q_top['IN'].center],
            bend_params=None,
            relative_coords=False
        )



        router_in_right = WgRouter(
            gen_cls=self,
            init_port=self.inst_rac_right['IN_BOT'],
            layer=self.wg_routing_layer,
            name='wg_in_right',
        )
        router_in_right.cardinal_router(
            points=[self.inst_rac_right['IN_BOT'].center,
                    self.inst_rac_right['IN_BOT'].center + [self.bend_radius*2, 0],
                   ],
            bend_params=None,
            relative_coords=False
        )

        ## fix drc for dummy PDs
        for inst_pd in [self.inst_pd_i_bot_dum, self.inst_pd_i_top_dum,
                        self.inst_pd_q_bot_dum, self.inst_pd_q_top_dum]:
            router_drc = WgRouter(
                gen_cls=self,
                init_port=inst_pd['IN'],
                layer=self.wg_routing_layer,
                name='wg_drc',
            )
            router_drc.cardinal_router(
            points=[inst_pd['IN'].center + [0.1, 0]],
            bend_params=None,
            relative_coords=False
        )

    def add_ports(self):


        self.add_photonic_port(
            name='IN_LEFT',
            center=(self.inst_rac_left['IN_BOT'].center[0],
                    self.inst_rac_left['IN_BOT'].center[1]),
            orient=self.inst_rac_left['IN_BOT'].orientation,
            width=self.inst_rac_left['IN_BOT'].width,
            layer=self.inst_rac_left['IN_BOT'].layer,
            resolution=self.inst_rac_left['IN_BOT'].resolution,
            angle=self.inst_rac_left['IN_BOT'].mod_angle,
        )

        self.add_photonic_port(
            name='IN_RIGHT',
            center=(self.inst_rac_right['IN_BOT'].center[0] + self.bend_radius*2,
                    self.inst_rac_right['IN_BOT'].center[1]),
            orient=self.inst_rac_right['IN_BOT'].orientation,
            width=self.inst_rac_right['IN_BOT'].width,
            layer=self.inst_rac_right['IN_BOT'].layer,
            resolution=self.inst_rac_right['IN_BOT'].resolution,
            angle=self.inst_rac_right['IN_BOT'].mod_angle,
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


class RxRowSingle(BPG.PhotonicTemplateBase):
    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)
        self.params = params
        for key, val in self.params.items():  # Automatically unpack variables
            # exec( "self.{} = {}".format( key, val ) )
            exec(f"self.{key} = {val!r}")

        # ================================================================
        # Create all templates (may need them to get geometry parameters)
        # ================================================================

        # Create class of each device component
        gc_module = importlib.import_module(self.grating_coupler_module)
        gc_class = getattr(gc_module, self.grating_coupler_class)
        self.gc_master = self.new_template(params=None, temp_cls=gc_class)
        self.gc_array_inst = [None] * self.grating_coupler_num

        pd_module = importlib.import_module(self.pd_module)
        pd_class = getattr(pd_module, self.pd_class)
        self.pd_master = self.new_template(params=None, temp_cls=pd_class)

        self.rac_template = self.create_template(
            photonic_spec_file=self.rac_spec_file,
            photonic_module_name=self.rac_module,
            photonic_class_name=self.rac_class,
        )

        self.bend_radius = self.photonic_tech_info.get_default_wg_params(self.wg_routing_layer)['radius'] + 0.1
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
            grating_coupler_module=None,
            grating_coupler_class=None,
            grating_coupler_spec_file=None,
            grating_coupler_loc_offset=[127, 127],
            grating_coupler_pitch=127.0,
            grating_coupler_num=0,
            rac_module=None,
            rac_class=None,
            rac_spec_file=None,
            pd_module=None,
            pd_class=None,
            pd_spec_file=None,
            photonic_spec_file=None,
            photonic_module_name=None,
            photonic_class_name=None,
            wg_routing_layer=None,

        )

    @classmethod
    def get_params_info(cls) -> dict:
        return dict(
            grating_coupler_module='TODO',
            grating_coupler_class='TODO',
            grating_coupler_spec_file='TODO',
            grating_coupler_loc_offset='TODO',
            grating_coupler_pitch='TODO',
            grating_coupler_num='TODO',
            rac_module='TODO',
            rac_class='TODO',
            rac_spec_file='TODO',
            pd_module='TODO',
            pd_class='TODO',
            pd_spec_file='TODO',
            photonic_spec_file='TODO',
            photonic_module_name='TODO',
            photonic_class_name='TODO',
            wg_routing_layer='TODO',

        )

    def draw_layout(self):
        # Draw pads and fixed photonic devices relative to pad locs

        self.place_instances()
        self.wg_routing()


    def place_instances(self):

        n_sites = 2

        # left & right refer to the relative location to the R0-oriented filter & hybrid,
        # if they are placed with direction MY, 'left' coupler refers to the coupler
        # on their right in the layout floorplan

        self.dict_x_coupler = {
            'LEFT': [self.x_inst_coupler_base,
                     self.x_span - self.x_inst_coupler_base],
            'RIGHT': [self.x_span - self.x_inst_coupler_base - self.x_coupler_pitch,
                      self.x_inst_coupler_base + self.x_coupler_pitch,]
        }
        list_y_coupler_lh = [(self.y_span - self.y_coupler_pitch) / 2, (self.y_span + self.y_coupler_pitch) / 2]
        list_y_coupler_hl = [(self.y_span + self.y_coupler_pitch) / 2, (self.y_span - self.y_coupler_pitch) / 2]
        self.dict_y_coupler = {
            ('LEFT', 'IN'): list_y_coupler_hl,
            ('RIGHT', 'IN'): list_y_coupler_lh,
            ('LEFT', 'OUT'): list_y_coupler_lh,
            ('RIGHT', 'OUT'): list_y_coupler_hl,
        }
        self.dict_orient_coupler = {
            'LEFT': ['R0', 'MY'],
            'RIGHT': ['MY', 'R0'],
        }
        self.dict_orient_filter = {
            'LEFT': ['R270', 'R90'],
            'RIGHT': ['R90', 'R270'],
        }
        self.list_x_cohlink = [self.x_inst_cohlink_base,
                              self.x_span - self.x_inst_cohlink_base]
        self.list_orient_site = ['R0', 'MY']

        self.master_cohlink = self.new_template(
            params=self.params,
            temp_cls=CoherentLink
        )

        # self.list_x_filter = [self.x_inst_filter_base,
        #                       self.x_span - self.x_inst_filter_base]
        self.dict_x_filter = {
            'LEFT': [0, 0],
            'RIGHT': [0, 0],
        }

        with open(self.yaml_filter, 'r') as f:
            yaml_content = yaml.load(f)

        lay_module = importlib.import_module(yaml_content['layout_package'])
        temp_cls = getattr(lay_module, yaml_content['layout_class'])
        self.master_filter = self.new_template(params=yaml_content['layout_params'],
                                          temp_cls=temp_cls)


        y_cohlink = self.y_inst_cohlink_base
        list_y_filter = [self.y_inst_filter_base, self.y_span - self.y_inst_filter_base]


        self.list_inst_cohlink = [0, 0]
        self.list_dict_inst_filter = [{}, {}]
        self.list_dict_inst_gc = [{}, {}]

        self.list_dict_x_filter_ports = [{}, {}]
        self.list_dict_y_filter_ports = [{}, {}]
        self.list_dict_loc_filter_ports = [{}, {}]

        # index of the Rx site
        for i in range(0, 2):

            self.list_inst_cohlink[i] = self.add_instance(
                master=self.master_cohlink,
                loc=(self.list_x_cohlink[i], y_cohlink),
                orient=self.list_orient_site[i],
            )

            self.dict_x_filter['LEFT'][0] = self.x_inst_filter_base
            self.dict_x_filter['LEFT'][1] = self.x_span - self.x_inst_filter_base
            self.dict_x_filter['RIGHT'][0] = self.x_span - self.x_inst_filter_base
            self.dict_x_filter['RIGHT'][1] = self.x_inst_filter_base


            # key of the input port for each site
            for key_dict_x, val_dict_x in self.dict_x_coupler.items():

                self.list_dict_inst_filter[i][key_dict_x] = self.add_instance(
                    master=self.master_filter,
                    loc=(self.dict_x_filter[key_dict_x][i], list_y_filter[i]),
                    orient=self.dict_orient_filter[key_dict_x][i],
                )

                # TODO: replace this part with real ports of the ring filter

                self.list_dict_x_filter_ports[i][key_dict_x] = {
                    'IN': self.list_dict_inst_filter[i][key_dict_x]['PORT_IN'].center[0],
                    'THRU': self.list_dict_inst_filter[i][key_dict_x]['PORT_THROUGH'].center[0],
                    'DROP': self.list_dict_inst_filter[i][key_dict_x]['PORT_DROP'].center[0],
                }

                self.list_dict_y_filter_ports[i][key_dict_x] = {
                    'IN': self.list_dict_inst_filter[i][key_dict_x]['PORT_IN'].center[1],
                    'THRU': self.list_dict_inst_filter[i][key_dict_x]['PORT_THROUGH'].center[1],
                    'DROP': self.list_dict_inst_filter[i][key_dict_x]['PORT_DROP'].center[1],
                }

                self.list_dict_loc_filter_ports[i][key_dict_x] = {}
                for key_port in ['IN', 'THRU', 'DROP']:

                    self.list_dict_loc_filter_ports[i][key_dict_x][key_port] = (
                        self.list_dict_x_filter_ports[i][key_dict_x][key_port],
                        self.list_dict_y_filter_ports[i][key_dict_x][key_port]
                    )




            for key_dict_y, val_dict_y in self.dict_y_coupler.items():
                # key_dict_inst_gc = (key_dict_x, key_dict_y)
                key_dict_inst_gc = key_dict_y
                key_dict_x = key_dict_y[0]

                self.list_dict_inst_gc[i][key_dict_inst_gc] = self.add_instance(
                    master=self.gc_master,
                    loc=(self.dict_x_coupler[key_dict_x][i], val_dict_y[i]),
                    orient=self.dict_orient_coupler[key_dict_x][i],
                )

    def wg_routing(self):

        dict_list_wg_bend_dx = {
            'LEFT': [1, -1],
            'RIGHT': [-1, 1],
        }

        for i in range(0, 2):
            for key_dict_x, val_dict_x in self.dict_x_coupler.items():
                router_drop =  WgRouter(
                    gen_cls=self,
                    init_port=self.list_inst_cohlink[i]['IN_' + key_dict_x],
                    layer=self.wg_routing_layer,
                )
                if key_dict_x == 'LEFT':
                    router_drop.cardinal_router(
                        points=[
                            self.list_inst_cohlink[i]['IN_' + key_dict_x].center,
                            (self.list_inst_cohlink[i]['IN_' + key_dict_x].center[0] - self.bend_radius * dict_list_wg_bend_dx[key_dict_x][i],
                             self.list_inst_cohlink[i]['IN_' + key_dict_x].center[1] - self.bend_radius * 1),
                            self.list_dict_loc_filter_ports[i][key_dict_x]['DROP'],
                        ],
                        bend_params=None,
                        relative_coords=False
                    )
                else:
                    y_wg = (self.y_span - self.track_pitch) if i == 0 else self.track_pitch
                    dy_bend = 1 if i == 0 else -1
                    if i == 1:

                        # router_drop.add_fancy_s_bend(shift_left=self.list_inst_cohlink[i]['IN_' + key_dict_x].center[1]-)
                        router_drop.cardinal_router(
                            points=[
                                (self.list_inst_cohlink[i]['IN_' + key_dict_x].center[0] - self.bend_radius,
                                 self.list_inst_cohlink[i]['IN_' + key_dict_x].center[1] + self.bend_radius),
                                (self.list_inst_cohlink[i].bound_box.left,
                                 self.list_inst_cohlink[i]['IN_' + key_dict_x].center[1] + self.bend_radius * 2),
                            ],
                            bend_params=None,
                            relative_coords=False
                        )
                    router_drop.cardinal_router(
                        points=[
                            (router_drop.x - self.bend_radius * dict_list_wg_bend_dx[key_dict_x][i],
                             router_drop.y + self.bend_radius * dy_bend),
                            (router_drop.x + self.bend_radius * dict_list_wg_bend_dx[key_dict_x][i] * 2,
                             y_wg),
                            (self.list_dict_loc_filter_ports[i][key_dict_x]['DROP'][0] + self.bend_radius * dict_list_wg_bend_dx[key_dict_x][i] * 1,
                             self.list_dict_loc_filter_ports[i][key_dict_x]['DROP'][1] + self.bend_radius * dy_bend),
                            self.list_dict_loc_filter_ports[i][key_dict_x]['DROP']
                        ],
                        bend_params=None,
                        relative_coords=False
                    )

            # wg bending direction in y-coordinate out of devices
            list_wg_bend_dy = [1, -1]
            dict_list_y_track = {
                'IN': [self.y_span - self.track_pitch * 2, self.track_pitch],
                'OUT': [self.y_span - self.track_pitch * 1, self.track_pitch * 2],
            }
            dict_shift_left_1st = {
                ('LEFT', 'IN'): self.y_span - self.track_pitch - self.list_dict_inst_gc[0][('LEFT', 'IN')]['IN'].center[1],
                ('RIGHT', 'IN'): self.list_dict_loc_filter_ports[1]['RIGHT']['IN'][1] + self.bend_radius * 2 -
                                  self.list_dict_inst_gc[1][('RIGHT', 'IN')]['IN'].center[1],
                ('LEFT', 'OUT'): self.y_span - self.track_pitch * 2 - self.list_dict_inst_gc[0][('LEFT', 'OUT')]['IN'].center[1],
                ('RIGHT', 'OUT'): self.list_dict_loc_filter_ports[1]['RIGHT']['THRU'][1] -
                                  self.list_dict_inst_gc[1][('RIGHT', 'OUT')]['IN'].center[1],
            }


            for key_dict_y, val_dict_y in self.dict_y_coupler.items():

                key_dict_inst_gc = key_dict_y
                dx_in = -1 if ((i==0) == (key_dict_y[0] == 'LEFT')) else 1

                print(key_dict_y, self.list_dict_inst_gc[i][key_dict_inst_gc]['IN'])

                router_in = WgRouter(
                    gen_cls=self,
                    init_port=self.list_dict_inst_gc[i][key_dict_inst_gc]['IN'],
                    layer=self.wg_routing_layer,
                )
                if key_dict_y == ('LEFT', 'OUT'):
                    router_in.add_fancy_s_bend(0, self.track_pitch)
                router_in.add_fancy_s_bend(dict_shift_left_1st[key_dict_y], self.bend_radius*3)

                if key_dict_y == ('RIGHT', 'OUT'):
                    router_in.add_fancy_s_bend(0, self.list_dict_x_filter_ports[1]['RIGHT']['THRU'] -
                                               self.list_dict_inst_gc[1][key_dict_inst_gc]['IN'].center[0] - self.bend_radius*2)
                # elif key_dict_y == ('RIGHT', 'OUT'):
                elif key_dict_y[1] == 'IN':
                    router_in.cardinal_router([
                        (self.list_dict_x_filter_ports[i][key_dict_y[0]]['IN'] - self.bend_radius * dx_in,
                         self.list_dict_y_filter_ports[i][key_dict_y[0]]['IN'] - self.bend_radius * dx_in),
                        (self.list_dict_x_filter_ports[i][key_dict_y[0]]['IN'],
                         self.list_dict_y_filter_ports[i][key_dict_y[0]]['IN']),
                    ])
                else:
                    router_in.cardinal_router([
                        (self.list_dict_x_filter_ports[i][key_dict_y[0]]['THRU'] + self.bend_radius * dx_in,
                         self.list_dict_y_filter_ports[i][key_dict_y[0]]['THRU'] - self.bend_radius * dx_in),
                        (self.list_dict_x_filter_ports[i][key_dict_y[0]]['THRU'],
                         self.list_dict_y_filter_ports[i][key_dict_y[0]]['THRU']),
                    ])

    def add_ports(self):


        self.add_photonic_port(
            name='IN_LEFT',
            center=(self.inst_rac_left['IN_BOT'].center[0],
                    self.inst_rac_left['IN_BOT'].center[1]),
            orient=self.inst_rac_left['IN_BOT'].orientation,
            width=self.inst_rac_left['IN_BOT'].width,
            layer=self.inst_rac_left['IN_BOT'].layer,
            resolution=self.inst_rac_left['IN_BOT'].resolution,
            angle=self.inst_rac_left['IN_BOT'].mod_angle,
        )

        self.add_photonic_port(
            name='IN_RIGHT',
            center=(self.inst_pd_i_bot['IN'].center[0] + self.pd_master.bound_box.width,
                    self.inst_rac_right['IN_BOT'].center[1]),
            orient=self.inst_rac_right['IN_BOT'].orientation,
            width=self.inst_rac_right['IN_BOT'].width,
            layer=self.inst_rac_right['IN_BOT'].layer,
            resolution=self.inst_rac_right['IN_BOT'].resolution,
            angle=self.inst_rac_right['IN_BOT'].mod_angle,
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


class RxRowIQ(BPG.PhotonicTemplateBase):
    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)
        self.params = params
        for key, val in self.params.items():  # Automatically unpack variables
            # exec( "self.{} = {}".format( key, val ) )
            exec(f"self.{key} = {val!r}")

        # ================================================================
        # Create all templates (may need them to get geometry parameters)
        # ================================================================

        # Create class of each device component
        gc_module = importlib.import_module(self.grating_coupler_module)
        gc_class = getattr(gc_module, self.grating_coupler_class)
        self.gc_master = self.new_template(params=None, temp_cls=gc_class)
        self.gc_array_inst = [None] * self.grating_coupler_num

        pd_module = importlib.import_module(self.pd_module)
        pd_class = getattr(pd_module, self.pd_class)
        self.pd_master = self.new_template(params=None, temp_cls=pd_class)

        self.rac_template = self.create_template(
            photonic_spec_file=self.rac_spec_file,
            photonic_module_name=self.rac_module,
            photonic_class_name=self.rac_class,
        )

        self.bend_radius = self.photonic_tech_info.get_default_wg_params(self.wg_routing_layer)['radius'] + 0.1
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
            grating_coupler_module=None,
            grating_coupler_class=None,
            grating_coupler_spec_file=None,
            grating_coupler_loc_offset=[127, 127],
            grating_coupler_pitch=127.0,
            grating_coupler_num=0,
            rac_module=None,
            rac_class=None,
            rac_spec_file=None,
            pd_module=None,
            pd_class=None,
            pd_spec_file=None,
            photonic_spec_file=None,
            photonic_module_name=None,
            photonic_class_name=None,
            wg_routing_layer=None,

        )

    @classmethod
    def get_params_info(cls) -> dict:
        return dict(
            grating_coupler_module='TODO',
            grating_coupler_class='TODO',
            grating_coupler_spec_file='TODO',
            grating_coupler_loc_offset='TODO',
            grating_coupler_pitch='TODO',
            grating_coupler_num='TODO',
            rac_module='TODO',
            rac_class='TODO',
            rac_spec_file='TODO',
            pd_module='TODO',
            pd_class='TODO',
            pd_spec_file='TODO',
            photonic_spec_file='TODO',
            photonic_module_name='TODO',
            photonic_class_name='TODO',
            wg_routing_layer='TODO',

        )

    def draw_layout(self):
        # Draw pads and fixed photonic devices relative to pad locs
        self.place_instances()
        self.wg_routing()




    def place_instances(self):

        n_sites = 2

        # left & right refer to the relative location to the R0-oriented filter & hybrid,
        # if they are placed with direction MY, 'left' coupler refers to the coupler
        # on their right in the layout floorplan

        self.dict_x_coupler = {
            'LEFT': [self.x_inst_coupler_base,
                     self.x_span - self.x_inst_coupler_base],
            'RIGHT': [self.x_span - self.x_inst_coupler_base - self.x_coupler_pitch,
                      self.x_inst_coupler_base + self.x_coupler_pitch,]
        }
        list_y_coupler_lh = [(self.y_span - self.y_coupler_pitch) / 2, (self.y_span + self.y_coupler_pitch) / 2]
        list_y_coupler_hl = [(self.y_span + self.y_coupler_pitch) / 2, (self.y_span - self.y_coupler_pitch) / 2]
        self.dict_y_coupler = {
            ('LEFT', 'IN'): list_y_coupler_hl,
            ('RIGHT', 'IN'): list_y_coupler_lh,
            ('LEFT', 'OUT'): list_y_coupler_lh,
            ('RIGHT', 'OUT'): list_y_coupler_hl,
        }
        self.dict_orient_coupler = {
            'LEFT': ['R0', 'MY'],
            'RIGHT': ['MY', 'R0'],
        }
        self.dict_orient_filter = {
            'LEFT': ['R270', 'R90'],
            'RIGHT': ['R90', 'R270'],
        }
        self.list_x_hybrid = [self.x_inst_hybrid_base,
                              self.x_span - self.x_inst_hybrid_base]
        self.list_orient_site = ['R0', 'MY']

        self.master_hybrid = self.new_template(
            params=self.params,
            temp_cls=Hybrid90
        )

        # self.list_x_filter = [self.x_inst_filter_base,
        #                       self.x_span - self.x_inst_filter_base]
        self.dict_x_filter = {
            'LEFT': [0, 0],
            'RIGHT': [0, 0],
        }

        with open(self.yaml_filter, 'r') as f:
            yaml_content = yaml.load(f)

        lay_module = importlib.import_module(yaml_content['layout_package'])
        temp_cls = getattr(lay_module, yaml_content['layout_class'])
        self.master_filter = self.new_template(params=yaml_content['layout_params'],
                                          temp_cls=temp_cls)

        y_hybrid = self.y_inst_hybrid_base
        list_y_filter = [self.y_inst_filter_base, self.y_span - self.y_inst_filter_base]

        self.list_inst_hybrid = [0, 0]
        self.list_dict_inst_filter = [{}, {}]
        self.list_dict_inst_gc = [{}, {}]

        self.list_dict_x_filter_ports = [{}, {}]
        self.list_dict_y_filter_ports = [{}, {}]
        self.list_dict_loc_filter_ports = [{}, {}]

        # index of the Rx site
        for i in range(0, 2):

            self.list_inst_hybrid[i] = self.add_instance(
                master=self.master_hybrid,
                loc=(self.list_x_hybrid[i], y_hybrid),
                orient=self.list_orient_site[i],
            )

            self.dict_x_filter['LEFT'][0] = self.x_inst_filter_base
            self.dict_x_filter['LEFT'][1] = self.x_span - self.x_inst_filter_base
            self.dict_x_filter['RIGHT'][0] = self.x_span - self.x_inst_filter_base
            self.dict_x_filter['RIGHT'][1] = self.x_inst_filter_base


            # key of the input port for each site
            for key_dict_x, val_dict_x in self.dict_x_coupler.items():

                self.list_dict_inst_filter[i][key_dict_x] = self.add_instance(
                    master=self.master_filter,
                    loc=(self.dict_x_filter[key_dict_x][i], list_y_filter[i]),
                    orient=self.dict_orient_filter[key_dict_x][i],
                )

                # TODO: replace this part with real ports of the ring filter

                self.list_dict_x_filter_ports[i][key_dict_x] = {
                    'IN': self.list_dict_inst_filter[i][key_dict_x]['PORT_IN'].center[0],
                    'THRU': self.list_dict_inst_filter[i][key_dict_x]['PORT_THROUGH'].center[0],
                    'DROP': self.list_dict_inst_filter[i][key_dict_x]['PORT_DROP'].center[0],
                }

                self.list_dict_y_filter_ports[i][key_dict_x] = {
                    'IN': self.list_dict_inst_filter[i][key_dict_x]['PORT_IN'].center[1],
                    'THRU': self.list_dict_inst_filter[i][key_dict_x]['PORT_THROUGH'].center[1],
                    'DROP': self.list_dict_inst_filter[i][key_dict_x]['PORT_DROP'].center[1],
                }

                self.list_dict_loc_filter_ports[i][key_dict_x] = {}
                for key_port in ['IN', 'THRU', 'DROP']:

                    self.list_dict_loc_filter_ports[i][key_dict_x][key_port] = (
                        self.list_dict_x_filter_ports[i][key_dict_x][key_port],
                        self.list_dict_y_filter_ports[i][key_dict_x][key_port]
                    )




            for key_dict_y, val_dict_y in self.dict_y_coupler.items():
                # key_dict_inst_gc = (key_dict_x, key_dict_y)
                key_dict_inst_gc = key_dict_y
                key_dict_x = key_dict_y[0]

                self.list_dict_inst_gc[i][key_dict_inst_gc] = self.add_instance(
                    master=self.gc_master,
                    loc=(self.dict_x_coupler[key_dict_x][i], val_dict_y[i]),
                    orient=self.dict_orient_coupler[key_dict_x][i],
                )


    def wg_routing(self):

        dict_list_wg_bend_dx = {
            'LEFT': [1, -1],
            'RIGHT': [-1, 1],
        }

        for i in range(0, 2):
            for key_dict_x, val_dict_x in self.dict_x_coupler.items():
                router_drop =  WgRouter(
                    gen_cls=self,
                    init_port=self.list_inst_hybrid[i]['IN_' + key_dict_x],
                    layer=self.wg_routing_layer,
                )
                if key_dict_x == 'LEFT':
                    # router_drop.add_fancy_s_bend(
                    #     self.list_inst_hybrid[0]['IN_' + key_dict_x].center[1] -
                    #     self.list_dict_loc_filter_ports[i][key_dict_x]['DROP'][1],
                    #     self.list_inst_hybrid[0]['IN_' + key_dict_x].center[0] -
                    #     self.list_dict_loc_filter_ports[0][key_dict_x]['DROP'][0]
                    # )
                    router_drop.cardinal_router(
                        points=[
                            self.list_inst_hybrid[i]['IN_' + key_dict_x].center,
                            (self.list_inst_hybrid[i]['IN_' + key_dict_x].center[0] - self.bend_radius * dict_list_wg_bend_dx[key_dict_x][i],
                             self.list_inst_hybrid[i]['IN_' + key_dict_x].center[1] - self.bend_radius * 1),
                            self.list_dict_loc_filter_ports[i][key_dict_x]['DROP'],
                        ],
                        bend_params=None,
                        relative_coords=False
                    )
                else:
                    y_wg = (self.y_span - self.track_pitch) if i == 0 else self.track_pitch
                    dy_bend = 1 if i == 0 else -1
                    router_drop.cardinal_router(
                        points=[
                            self.list_inst_hybrid[i]['IN_' + key_dict_x].center,
                            (self.list_inst_hybrid[i]['IN_' + key_dict_x].center[0] - self.bend_radius * dict_list_wg_bend_dx[key_dict_x][i],
                             self.list_inst_hybrid[i]['IN_' + key_dict_x].center[1] + self.bend_radius * dy_bend),
                            (self.list_dict_loc_filter_ports[i][key_dict_x]['DROP'][0] + self.bend_radius * dict_list_wg_bend_dx[key_dict_x][i] * 2,
                             y_wg),
                            (self.list_dict_loc_filter_ports[i][key_dict_x]['DROP'][0] + self.bend_radius * dict_list_wg_bend_dx[key_dict_x][i] * 1,
                             self.list_dict_loc_filter_ports[i][key_dict_x]['DROP'][1] + self.bend_radius * dy_bend),
                            self.list_dict_loc_filter_ports[i][key_dict_x]['DROP']
                        ],
                        bend_params=None,
                        relative_coords=False
                    )

            # wg bending direction in y-coordinate out of devices
            list_wg_bend_dy = [1, -1]
            dict_list_y_track = {
                'IN': [self.y_span - self.track_pitch * 2, self.track_pitch],
                'OUT': [self.y_span - self.track_pitch * 1, self.track_pitch * 2],
            }
            dict_shift_left_1st = {
                ('LEFT', 'IN'): self.y_span - self.track_pitch - self.list_dict_inst_gc[0][('LEFT', 'IN')]['IN'].center[1],
                ('RIGHT', 'IN'): self.list_dict_loc_filter_ports[1]['RIGHT']['IN'][1] + self.bend_radius * 2 -
                                  self.list_dict_inst_gc[1][('RIGHT', 'IN')]['IN'].center[1],
                ('LEFT', 'OUT'): self.y_span - self.track_pitch * 2 - self.list_dict_inst_gc[0][('LEFT', 'OUT')]['IN'].center[1],
                ('RIGHT', 'OUT'): self.list_dict_loc_filter_ports[1]['RIGHT']['THRU'][1] -
                                  self.list_dict_inst_gc[1][('RIGHT', 'OUT')]['IN'].center[1],
            }


            for key_dict_y, val_dict_y in self.dict_y_coupler.items():

                key_dict_inst_gc = key_dict_y
                dx_in = -1 if ((i==0) == (key_dict_y[0] == 'LEFT')) else 1

                print(key_dict_y, self.list_dict_inst_gc[i][key_dict_inst_gc]['IN'])

                router_in = WgRouter(
                    gen_cls=self,
                    init_port=self.list_dict_inst_gc[i][key_dict_inst_gc]['IN'],
                    layer=self.wg_routing_layer,
                )
                if key_dict_y == ('LEFT', 'OUT'):
                    router_in.add_fancy_s_bend(0, self.track_pitch)
                router_in.add_fancy_s_bend(dict_shift_left_1st[key_dict_y], self.bend_radius*3)

                if key_dict_y == ('RIGHT', 'OUT'):
                    router_in.add_fancy_s_bend(0, self.list_dict_x_filter_ports[1]['RIGHT']['THRU'] -
                                               self.list_dict_inst_gc[1][key_dict_inst_gc]['IN'].center[0] - self.bend_radius*2)
                # elif key_dict_y == ('RIGHT', 'OUT'):
                elif key_dict_y[1] == 'IN':
                    router_in.cardinal_router([
                        (self.list_dict_x_filter_ports[i][key_dict_y[0]]['IN'] - self.bend_radius * dx_in,
                         self.list_dict_y_filter_ports[i][key_dict_y[0]]['IN'] - self.bend_radius * dx_in),
                        (self.list_dict_x_filter_ports[i][key_dict_y[0]]['IN'],
                         self.list_dict_y_filter_ports[i][key_dict_y[0]]['IN']),
                    ])
                else:
                    router_in.cardinal_router([
                        (self.list_dict_x_filter_ports[i][key_dict_y[0]]['THRU'] + self.bend_radius * dx_in,
                         self.list_dict_y_filter_ports[i][key_dict_y[0]]['THRU'] - self.bend_radius * dx_in),
                        (self.list_dict_x_filter_ports[i][key_dict_y[0]]['THRU'],
                         self.list_dict_y_filter_ports[i][key_dict_y[0]]['THRU']),
                    ])





    def add_ports(self):


        self.add_photonic_port(
            name='IN_LEFT',
            center=(self.inst_rac_left['IN_BOT'].center[0],
                    self.inst_rac_left['IN_BOT'].center[1]),
            orient=self.inst_rac_left['IN_BOT'].orientation,
            width=self.inst_rac_left['IN_BOT'].width,
            layer=self.inst_rac_left['IN_BOT'].layer,
            resolution=self.inst_rac_left['IN_BOT'].resolution,
            angle=self.inst_rac_left['IN_BOT'].mod_angle,
        )

        self.add_photonic_port(
            name='IN_RIGHT',
            center=(self.inst_pd_i_bot['IN'].center[0] + self.pd_master.bound_box.width,
                    self.inst_rac_right['IN_BOT'].center[1]),
            orient=self.inst_rac_right['IN_BOT'].orientation,
            width=self.inst_rac_right['IN_BOT'].width,
            layer=self.inst_rac_right['IN_BOT'].layer,
            resolution=self.inst_rac_right['IN_BOT'].resolution,
            angle=self.inst_rac_right['IN_BOT'].mod_angle,
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


