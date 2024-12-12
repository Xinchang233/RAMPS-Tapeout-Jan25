# DL exercise 1: single structure containing grating coupler + wg + taper (if needed)

import BPG
import importlib

from layout.Importers.Gratings.PDK_grating_Cband import PDK_grating_Cband
from layout.WaveguideBase.SimpleWaveguide import SimpleWaveguide
from layout.DL_TaperBase.SimpleTaper import SimpleTaper
from layout.DL_WGBendBase.SimpleWgBend import SimpleWgBend

class DLex_1(BPG.PhotonicTemplateBase):
    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)

        self.layer = params['layer'] # I currently have no idea what this should be
        self.port_layer = params['port_layer']
        self.length = self.params['length'] # length L draw in picture
        self.tlength = self.params['tlength'] # length for taper, self-defined
        self.width = self.params['width'] # width of wg, if needed
        self.turn_radius = self.params['turn_radius'] # turning radius R for bend wg drawn in picture

    @classmethod
    def get_default_param_values(cls):
        return dict(
            layer = None,
            port_layer = None,
            # Default values for parameters L, R, width
            length = 500,
            tlength = 50,
            width = 0.55,
            turn_radius = 5.5
        )

    @classmethod
    def get_params_info(cls):  # Returns definition of the parameters.
        return dict(
            layer = 'None',
            port_layer = 'None',
            length = 'Length of str wg (length L draw in picture)',
            tlength = 'Length of taper',
            width = 'Width of Wg',
            turn_radius = 'Radius of curvature of bend (turning radius R for bend wg drawn in picture)'
            )

    def draw_layout(self):
        # need a grating coupler, straight wg, bend eg, then everything symmetric

        grating_temp = self.new_template(temp_cls = PDK_grating_Cband)
        grating_inst = self.add_instance(master = grating_temp, loc = (0,0))

        taper_params = dict(layer = self.layer, port_layer = self.port_layer, length = self.tlength, widthI = 0.5, widthO = self.width)
        taper_template = self.new_template(params = taper_params, temp_cls = SimpleTaper)

        wg_params = dict(layer = self.layer, port_layer = self.port_layer, length = self.length, width = self.width)
        wg_template = self.new_template(params = wg_params, temp_cls = SimpleWaveguide)

        bend_params = dict(layer = self.layer, port_layer = self.port_layer, r = self.turn_radius, width = self.width)
        bend_template = self.new_template(params = bend_params, temp_cls = SimpleWgBend)

        # add taper to grating coupler
        Structinst = self.add_instances_port_to_port(inst_master = taper_template,
                                        instance_port_name = 'PORT_IN',
                                        self_port = grating_inst['PORT_OUT'])

        # add straight wg to the previous outcome struct
        Structinst = self.add_instances_port_to_port(inst_master = wg_template,
                                        instance_port_name = 'PORT_IN',
                                        self_port = Structinst['PORT_OUT'])

        # add bend to the previous outcome struct
        Structinst = self.add_instances_port_to_port(inst_master = bend_template,
                                        instance_port_name = 'PORT_IN',
                                        self_port = Structinst['PORT_OUT'])

        # add another bend to the previous outcome struct
        Structinst = self.add_instances_port_to_port(inst_master = bend_template,
                                        instance_port_name = 'PORT_OUT',
                                        self_port = Structinst['PORT_OUT'])

        # add another straight wg to the previous outcome struct
        Structinst = self.add_instances_port_to_port(inst_master = wg_template,
                                        instance_port_name = 'PORT_IN',
                                        self_port = Structinst['PORT_IN'])

        # add another taper to previous outcome struct
        Structinst = self.add_instances_port_to_port(inst_master = taper_template,
                                        instance_port_name = 'PORT_OUT', # NOTICE
                                        self_port = Structinst['PORT_OUT'])

        # add another grating coupler to previous outcome struct
        Structinst = self.add_instances_port_to_port(inst_master = grating_temp,
                                        instance_port_name = 'PORT_OUT', # NOTICE
                                        self_port = Structinst['PORT_IN'])
