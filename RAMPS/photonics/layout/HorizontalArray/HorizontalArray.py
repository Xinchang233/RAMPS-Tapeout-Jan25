import BPG
import importlib
#from Photonic_Core_Layout.DirectionalCoupler.DirectionalCoupler import DirectionalCoupler
from Photonic_Core_Layout.AdiabaticPaths.AdiabaticPaths import AdiabaticPaths
#from Photonic_Core_Layout.Ring.ring import RingBase
#from Photonic_Layout_45SPCLO.GDS_Library_Device.gds_library_device import GDS_Library_Device
from BPG.objects import PhotonicRect
from bag.layout.util import BBox
from math import floor


class HorizontalArray(BPG.PhotonicTemplateBase):
    """
    This class creates
    """

    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)

        self.N_rows = params['N_rows']
        self.N_cols = params['N_cols']
        self.hc = params['hc']
        self.wc = params['wc']
        self.dh1 = params['dh1']
        self.dc_step = params['dc_step']
        self.hm_port = params['hm_port']
        self.spacing_cc = params['spacing_cc']
        self.spacing_cm = params['spacing_cm']
        self.pitch_mm = params['pitch_mm']
        self.spacing_wg = params['spacing_wg']
        self.dr = params['dr']
        self.dl = params['dl']
        self.rmin = params['rmin']
        self.width = params['width']

        self.layer = params['layer']
        self.radius_threshold = params['radius_threshold']
        self.curvature_rate_threshold = params['curvature_rate_threshold']

        self.coupler_top_package = params['coupler_top_package']
        self.coupler_top_class = params['coupler_top_class']
        self.coupler_port_name = params['coupler_port_name']
        self.coupler_params = params['coupler_params']

        self.dut_top_package = params['dut_top_package']
        self.dut_top_class = params['dut_top_class']
        self.dut_port_name_in = params['dut_port_name_in']
        self.dut_port_name_out = params['dut_port_name_out']
        self.dut_rectangle_layer = params['dut_rectangle_layer']
        self.dut_params_list = params['dut_params_list']

        if (len(params['dut_params_list']) != self.N_rows*self.N_cols):
            raise ValueError('Number of entries in the list of device parameters must match the number of devices')


    @classmethod
    def get_params_info(cls) -> dict:

        return dict(
            N_rows='number of coupler rows',
            N_cols='number of coupler columns',
            hc='vertical pitch between couplers (center-to-center)',
            wc='width of the coupler (just for determining the coupler pitch, does not need to be accurate)',
            dh1='spacing between of the bottom of the whole generated cell and the (center of the) bottom-most waveguide',
            dc_step='when going along a column of couplers, a straight waveguide is added to each consecutive coupler to prevent waveguide overlaps; dc_step is the increment of straight waveguide length',
            hm_port='vertical spacing between the input (=output) of the modulator and the bottom of the modulator cell (doesn"t need to be accurate)',
            spacing_cc='horizontal spacing coupler-to-coupler',
            spacing_cm='horizontal spacing coupler-to-modulator',
            pitch_mm='horizontal spacing between modulator centers',
            spacing_wg='vertical spacing between waveguides (center-to-center)',
            dr='length of straight waveguide added to the right port of the modulator',
            dl='length of straight waveguide added to the left port of the modulator',
            rmin='minimum bending radius for adiabatic bends',
            width='waveguide width',
            layer = 'layer used for routing',
            radius_threshold = 'if radius of adiabatic bends drops below this value, an error is generated',
            curvature_rate_threshold = 'if rate of change of curvature of adiabatic bends drops below this value, an error is generated',
            coupler_top_package = 'coupler to be connected to ports, class package',
            coupler_top_class = 'coupler to be connected to ports, class name',
            coupler_port_name = 'coupler to be connected to ports, port name',
            coupler_params = 'coupler to be connected to ports, parameters of the coupler',
            dut_top_package='Package name of device under test',
            dut_top_class='Class name of device under test',
            dut_port_name_in='Name of the input port of the device under test',
            dut_port_name_out='Name of the output port of the device under test',
            dut_rectangle_layer='the device under test (usually modulator) is covered by a rectangle out of this layer',
            dut_params_list='list of N_rows*N_cols values containing parameters of each device'
        )

    @classmethod
    def get_default_param_values(cls) -> dict:
        return dict(
            N_rows=None,
            N_cols=None,
            hc=None,
            wc=None,
            dh1=None,
            dc_step=None,
            hm_port=None,
            spacing_cc=None,
            spacing_cm=None,
            pitch_mm=None,
            spacing_wg=None,
            dr=None,
            dl=None,
            rmin=None,
            width=None,
            layer=None,
            radius_threshold=None,
            curvature_rate_threshold=None,
            dut_top_package=None,
            dut_top_class=None,
            dut_port_name_in=None,
            dut_port_name_out=None,
            dut_params_list=None,
            dut_rectangle_layer=None,
            coupler_top_package=None,
            coupler_top_class=None,
            coupler_port_name=None,
            coupler_params=None,
            input_library_component=None
        )

    def draw_layout(self) -> None:

        N = self.N_rows*self.N_cols

        self.dut_master = [None] * N
        dut_width = [-1] * N
        dut_port_dy = [None] * N
        dut_height = [None] * N
        dut_bottom_y = [None] * N

        for i in range(N):

            dut_lay_module = importlib.import_module(self.dut_top_package)
            template_class_dut = getattr(dut_lay_module, self.dut_top_class)
            self.dut_master[i] = self.new_template(params=self.dut_params_list[i], temp_cls=template_class_dut)

            dut_port_in  = self.dut_master[i].get_photonic_port(self.dut_port_name_in)
            dut_port_out = self.dut_master[i].get_photonic_port(self.dut_port_name_out)

            dut_width[i]   = dut_port_out.center[0] - dut_port_in.center[0]
            dut_port_dy[i] = dut_port_out.center[1] - dut_port_in.center[1]
            dut_height[i] = self.dut_master[i].bound_box.height
            dut_bottom_y[i] = self.dut_master[i].bound_box.bottom - dut_port_in.center[1]

        xb = [0]*N
        yb = [0]*N
        xt = [0]*N
        yt = [0]*N
        xm_in = [0]*N
        ym_in = [0]*N
        ym_out = [0]*N
        xc_in = [0]*N
        yc_in = [0]*N
        xc_out = [0]*N
        yc_out = [0]*N
        len_b = [0]*N
        len_t = [0]*N
        dc_in = [0]*N
        dc_out= [0]*N

        x_max = 2 * self.N_cols * self.wc + 2 * self.spacing_cc * (self.N_cols - 1) + 2 * self.spacing_cm + dut_width[0]/2 + dut_width[-1]/2 + (N - 1) * self.pitch_mm
        y_max = self.N_rows * self.hc + self.spacing_wg * (N - self.N_rows) + self.dh1

        for i in range(N):

            xm_in[i] = self.wc * self.N_cols + self.spacing_cc * (self.N_cols - 1) + self.spacing_cm + dut_width[0]/2 + i * self.pitch_mm - dut_width[i]/2
            ym_in[i] = self.dh1 + self.hm_port + self.params['dut_params_list'][i]['input_gap'] #+ self.spacing_wg * (N - 1 - i)
            ym_out[i] = ym_in[i] + dut_port_dy[i]

            if i > 0:
                yb[i] = self.dh1 + self.spacing_wg * (N - 1 - i)
            else:
                yb[0] = ym_in[0]

            if i <= N-1:
                yt[i] = self.N_rows*self.hc + self.spacing_wg*(N-self.N_rows-i)
            else:
                yt[i] = ym_out[i]

            i_col = self.N_cols - 1 - floor((i+0.01)/self.N_rows)
            i_row = self.N_rows - 1 - (i % self.N_rows)

            if i == 0:
                xc_in[i] = self.wc + (self.spacing_cc + self.wc)*(i_col-1)
                yc_in[i] = self.hc/2 + self.hc * self.N_rows + self.N_rows*self.spacing_wg*(i_col-1)
            else:
                xc_in[i] = self.wc + (self.spacing_cc + self.wc) * i_col
                yc_in[i] = self.hc / 2 + self.hc * i_row + self.N_rows * self.spacing_wg * i_col

            if i_col > 0:
                yc_in[i] += self.dh1

            dc_in[i] = 0.01 + self.dc_step * i_row

            i_col = floor((i+0.01)/self.N_rows)
            i_row = i % self.N_rows
            if i == N-1:
                xc_out[i] = x_max - ( self.wc +(self.spacing_cc + self.wc)*(i_col-1) )
                yc_out[i] = y_max - ( self.hc/2 + self.hc*self.N_rows + self.N_rows*self.spacing_wg*(i_col-1) )
            else:
                xc_out[i] = x_max - ( self.wc +(self.spacing_cc + self.wc)*i_col )
                yc_out[i] = y_max - ( self.hc/2 + self.hc*i_row + self.N_rows*self.spacing_wg*i_col )
            if i_col > 0:
                yc_out[i] -= self.dh1

            dc_out[i] = 0.01 + self.dc_step * i_row

            if i < 1:
                len_b[i] = (xm_in[i] - xc_in[i]) - dc_in[i] - self.offset_x(ym_in[i]-yc_in[i], self.rmin)
            else:
                len_b[i] = (xm_in[i] - xc_in[i]) - dc_in[i] - self.offset_x(yb[i]-yc_in[i], self.rmin) - self.offset_x(ym_in[i]-yb[i], self.rmin) - self.dl

            if i <= N-1:
                len_t[i] = (xc_out[i] - xm_in[i] - dut_width[i]) - self.dr - self.offset_x(yt[i] - ym_out[i], self.rmin) - self.offset_x(yc_out[i] - yt[i], self.rmin) - dc_out[i]
            else:
                len_t[i] = (xc_out[i] - xm_in[i] - dut_width[i]) - self.offset_x(ym_out[i] - yc_out[i], self.rmin) - dc_out[i]

        for i in range(N):
            if len_b[i] < 1e-5:
                raise ValueError('Negative lengths encountered in modulator bank array (bottom waveguides). Give"em more space!')
            if len_t[i]<1e-5:
                raise ValueError('Negative lengths encountered in modulator bank array (top waveguides). Give"em more space!')


        self.paths = []
        self.dut = []

        coupler_lay_module = importlib.import_module(self.coupler_top_package)
        template_class_coupler = getattr(coupler_lay_module, self.coupler_top_class)
        self.coupler_master = self.new_template(params=self.coupler_params, temp_cls=template_class_coupler)

        self.input_coupler = [None] * N
        self.output_coupler = [None] * N

        adiab_params = dict()
        adiab_params['layer'] = self.layer
        adiab_params['port_layer'] = self.layer
        adiab_params['angle_start'] = 0.0
        adiab_params['radius_threshold'] = self.radius_threshold
        adiab_params['curvature_rate_threshold'] = self.curvature_rate_threshold
        adiab_params['merge_arcs'] = False

        for i in range(N):

            self.input_coupler[i] = self.add_instance(self.coupler_master, loc=(xc_in[i], yc_in[i]), orient='R180')

            adiab_params['x_start'] = 0
            adiab_params['y_start'] = 0

            adiab_params['arc_params'] = []
#           adiab_params['arc_params'].append({'arc_type': "straight_wg", 'length': self.wc, 'width': [self.hc, self.width]})
            if i == 0:
                adiab_params['arc_params'].append({'arc_type': "straight_wg", 'length': dc_in[i]+self.wc+self.spacing_cc, 'width': self.width})
            else:
                adiab_params['arc_params'].append({'arc_type': "straight_wg", 'length': dc_in[i], 'width': self.width})

            adiab_params['arc_params'].append({'arc_type': "offset_bend", 'offset': yc_in[i]-yb[i], 'rmin': self.rmin, 'width': self.width})
            if i == 0:
                adiab_params['arc_params'].append({'arc_type': "straight_wg", 'length': len_b[i]-self.wc-self.spacing_cc, 'width': self.width})
            else:
                adiab_params['arc_params'].append({'arc_type': "straight_wg", 'length': len_b[i], 'width': self.width})
            if i > 0:
                adiab_params['arc_params'].append({'arc_type': "offset_bend", 'offset': yb[i]-ym_in[i], 'rmin': self.rmin, 'width': self.width})
                adiab_params['arc_params'].append({'arc_type': "straight_wg", 'length': self.dl, 'width': self.width})

            self.path_master1 = self.new_template(params=adiab_params, temp_cls=AdiabaticPaths)

            self.paths.append(self.add_instance_port_to_port(inst_master=self.path_master1, instance_port_name='PORT_IN', self_port=self.input_coupler[i][self.coupler_port_name], reflect=False))

            # r = self.ring_params()
            # self.ring_master = self.new_template(params=r, temp_cls=RingBase)

            self.dut.append(self.add_instance_port_to_port(inst_master=self.dut_master[i], instance_port_name=self.dut_port_name_in, self_port=self.paths[-1]['PORT_OUT'], reflect=False))

            # poly = PhotonicRect(layer=self.dut_rectangle_layer, bbox=BBox(left=xm_in[i], right=xm_in[i]+dut_width[i], bottom=ym_in[i]+dut_bottom_y[i]-2.1, top=ym_in[i]+dut_bottom_y[i]+dut_height[i]+2.1, resolution=self.grid.resolution))
            # self.add_obj(poly)

            adiab_params['x_start'] = 0
            adiab_params['y_start'] = 0
            adiab_params['arc_params'] = []
            if i <= N-1:
                adiab_params['arc_params'].append({'arc_type': "straight_wg", 'length': self.dr, 'width': self.width})
                adiab_params['arc_params'].append({'arc_type': "offset_bend", 'offset': ym_out[i] - yt[i], 'rmin': self.rmin, 'width': self.width})
            if i == N -1:
                adiab_params['arc_params'].append({'arc_type': "straight_wg", 'length': len_t[i]-self.wc-self.spacing_cc, 'width': self.width})
            else:
                adiab_params['arc_params'].append({'arc_type': "straight_wg", 'length': len_t[i], 'width': self.width})
            adiab_params['arc_params'].append({'arc_type': "offset_bend", 'offset': yt[i] - yc_out[i], 'rmin': self.rmin, 'width': self.width})
            if i == N-1:
                adiab_params['arc_params'].append({'arc_type': "straight_wg", 'length': dc_out[i]+self.wc+self.spacing_cc, 'width': self.width})
            else:
                adiab_params['arc_params'].append({'arc_type': "straight_wg", 'length': dc_out[i], 'width': self.width})
            # adiab_params['arc_params'].append({'arc_type': "straight_wg", 'length': self.wc, 'width': [self.width, self.hc]})

            self.path_master2 = self.new_template(params=adiab_params, temp_cls=AdiabaticPaths)
            self.paths.append(self.add_instance_port_to_port(inst_master=self.path_master2, instance_port_name='PORT_IN', self_port=self.dut[-1][self.dut_port_name_out], reflect=False))

            self.output_coupler[i] = self.add_instance_port_to_port(inst_master=self.coupler_master, instance_port_name=self.coupler_port_name, self_port=self.paths[-1]['PORT_OUT'], reflect=False)

            # # create directional coupler
        # dir_params = dict()
        # dir_params['waveguide_height'] = 0.22
        # dir_params['gap'] = 0.2
        # dir_params['layer'] = ('RX', 'drawing')
        # dir_params['coupl_length'] = 10.0
        # dir_params['width'] = 0.5
        # dir_params['tot_length'] = 20.0
        # dir_params['coupling_height'] = 0.22
        #
        # self.input_dir_coupler_master = self.new_template(params=dir_params, temp_cls=DirectionalCoupler)
        # self.output_dir_coupler_master = self.input_dir_coupler_master
        #
        # # Create phase shifter
        #
        # shifter_params = dict()
        # shifter_params['left_port'] = 'PORT0'
        # shifter_params['right_port'] = 'PORT1'
        # shifter_params['width0'] = 0.5
        # shifter_params['width1'] = 1.5
        # shifter_params['length'] = 20
        # shifter_params['layer'] = ('RX', 'drawing')
        #
        # self.ps_top_master = self.new_template(params=shifter_params, temp_cls=LinearTaper)
        # self.ps_bot_master = self.new_template(params=shifter_params, temp_cls=LinearTaper)
        #
        # # place directional coupler input
        # self.dir_coupler_in = self.add_instance(self.input_dir_coupler_master, loc=(0, 0), orient='R0')
        # self.extract_photonic_ports(inst=self.dir_coupler_in, port_names=['PORT0', 'PORT1'], port_renaming={'PORT0': 'IN_BOT', 'PORT1': 'IN_TOP'}, show=False,)
        #
        # # place phase shifter top and bottom
        # self.ps_top = self.add_instance_port_to_port(inst_master=self.ps_top_master, instance_port_name=shifter_params['left_port'], self_port=self.dir_coupler_in['output_0'], reflect=False)
        # self.ps_bot = self.add_instance_port_to_port(inst_master=self.ps_bot_master, instance_port_name=shifter_params['left_port'], self_port=self.dir_coupler_in['output_1'], reflect=False)
        #
        # # place directional coupler out
        # self.dir_coupler_out = self.add_instance_port_to_port(inst_master=self.output_dir_coupler_master, instance_port_name='input_0', self_port=self.ps_top[shifter_params['right_port']], reflect=False)
        # self.extract_photonic_ports(inst=self.dir_coupler_out, port_names=['PORT3', 'PORT2'], port_renaming={'PORT3': 'OUT_BOT', 'PORT2': 'OUT_TOP'}, show=False,)

    def offset_x(self, offset_y, rmin):

        adiab_params = dict()

        adiab_params['layer'] = ('SXCUT', 'label')
        adiab_params['port_layer'] = ('SXCUT', 'label')
        adiab_params['x_start'] = 0.0
        adiab_params['y_start'] = 0.0
        adiab_params['angle_start'] = 0.0
        adiab_params['merge_arcs'] = False
        adiab_params['show_plot'] = False
        adiab_params['show_plot_labels'] = False

        adiab_params['arc_params'] = []
        adiab_params['arc_params'] = [{'arc_type': "offset_bend", 'offset': offset_y, 'rmin': rmin, 'width': 0.5}]

        off_master = self.new_template(params=adiab_params, temp_cls=AdiabaticPaths)
        delta_x = abs(off_master.arc_list[-1]['x'][-1])

        return delta_x

if __name__ == '__main__':
    spec_file = 'layout/HorizontalArray/specs/moscap_set_01.yaml'
    # spec_file = 'Photonic_Layout_45SPCLO/GDS_Library_Device/specs/gds_library_device.yaml'
    plm = BPG.PhotonicLayoutManager(spec_file)
    plm.generate_content()
    plm.generate_gds()
    # plm.generate_flat_content()
    # plm.generate_flat_gds()
    # plm.generate_lsf()
    # plm.dataprep()
    plm.dataprep_calibre()

