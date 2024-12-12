import BPG
import importlib
from Photonic_Core_Layout.WaveguideBase.WaveguideBase import WaveguideBase
from BPG.objects import PhotonicPolygon, PhotonicRect
from bag.layout.objects import BBox
from copy import deepcopy
import numpy as np

class SerpentineGrating(BPG.PhotonicTemplateBase):
    """
    This class creates a serpentine grating

    Parameters
    ----------
    Serpentine parameters
    ----------
    nrows : integer
        number of gratings to write (total 2*nrows-1 waveguides)
    input_mod : boolean
        True to include a modulator at input to serpentine


    Component parameters
    ----------
    mod_class : class
        Class to use for input modulator if input_mod == True
    grating_params : dict
        dict of parameters to be sent to the grating waveguide
    flyback_params : dict
        dict of parameters to be sent to the flyback waveguide
    bend_params: dict
        dict of parameters to be sent to bend
    grat_taper_params: dict
        dict of paramters to be sent to the taper going from the bend into the grating waveguide
    fly_taper_params: dict
        dict of paramters to be sent to the taper going from the bend into the flyback waveguide
    mod_taper_params: dict
        dict of parameters to be sent to the taper going into/out of the input modulator
    mod_params: dict
        dict of parameters to be sent to the input modulator
    """

    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)

        # Import serpentine overall parameters
        self.nrows = self.params['nrows']
        self.input_offset = self.params['input_offset']
        self.output_offset = self.params['output_offset']
        self.input_mod = self.params['input_mod']
        self.add_coupler = self.params['add_coupler']
        if self.input_mod:
            self.mod_length = self.params['mod_length']
            self.pad_loc = self.params['pad_loc']

        # Import parameter values
        self.grating_params = self.params['grating_params']
        self.flyback_params = self.params['flyback_params']
        self.bend_params = self.params['bend_params']
        self.grat_taper_params = self.params['grat_taper_params']
        self.fly_taper_params = self.params['fly_taper_params']
        if self.input_mod:
            self.mod_params = self.params['mod_params']
            self.mod_taper_params = self.params['mod_taper_params']
            self.pad_params = self.params['pad_params']
            self.wiring_params = self.params['wiring_params']
        if self.add_coupler:
            self.input_coupler_params = self.params['input_coupler_params']
            self.output_coupler_params = self.params['output_coupler_params']
            self.input_coupler_taper_params = self.params['input_coupler_taper_params']
            self.output_coupler_taper_params = self.params['output_coupler_taper_params']

        # Instances
        self.grating_insts = {i: None for i in range(self.nrows)}
        self.flyback_insts = {i: None for i in range(self.nrows-1)}
        self.west_bend_insts = {i: None for i in range(self.nrows-1)}
        self.west_grat_taper_insts = {i: None for i in range(self.nrows)}
        self.west_fly_taper_insts = {i: None for i in range(self.nrows-1)}
        self.east_bend_insts = {i: None for i in range(self.nrows - 1)}
        self.east_grat_taper_insts = {i: None for i in range(self.nrows)}
        self.east_fly_taper_insts = {i: None for i in range(self.nrows - 1)}
        self.wg_insts = {i: None for i in range(2)}
        if self.input_mod:
            self.n_mods = int(np.floor(self.mod_length/self.mod_params['mod_length']))
            self.act_mod_length = self.n_mods*self.mod_params['mod_length']
            self.mod_insts = {i: None for i in range(self.n_mods)}
            self.mod_gap_insts = {i: None for i in range(self.n_mods-1)}
            self.mod_gap_slab_insts = {i: None for i in range(self.n_mods - 1)}
            self.mod_gap_block_insts = {i: None for i in range(self.n_mods - 1)}
            self.mod_rout_taper_insts = {i: None for i in range(2)}
            self.mod_input_taper_insts = {i: None for i in range(2)}
            self.wiring_inst = None
            self.pad_insts = {i: None for i in range(3)}
        if self.add_coupler:
            self.coupler_insts= {0: None,
                               1: None}
            self.coupler_taper_insts = {0: None,
                                  1: None}

        # Templates
        self.grating = None
        self.flyback = None
        self.bend = None
        self.grat_taper = None
        self.fly_taper = None
        self.wg_in = None
        self.wg_out = None
        if self.input_mod:
            self.mod_rout_taper = None
            self.mod_input_taper = None
            self.mod = None
            self.mod_gap = None
            self.gap_length = 1.0
            self.mod_gap_slab = None
            self.mod_gap_block = None
            self.wiring = None
            self.pad = None
        if self.add_coupler:
            self.input_coupler = None
            self.output_coupler = None
            self.input_coupler_taper = None
            self.output_coupler_taper = None

    @classmethod
    def get_params_info(cls) -> dict:
        return dict(
            nrows='integer setting the number of gratings to write',
            input_offset='float setting the distance between the serpentine input (including modulator if input_mod) and input coupler',
            output_offset='float setting the distance between the serpentine output and output coupler',
            input_mod='boolean setting whether to add input modulator',
            add_coupler='boolean to add input/output couplers',
            mod_length='float setting desired length of modulator',
            pad_loc='tuple setting center location of pads relative to modulator input',
            grating_params='dict of parameters for the grating waveguide',
            flyback_params='dict of parameters for the flyback waveguide',
            bend_params='dict of parameters for the bends',
            grat_taper_params='dict of parameters for the taper between the bends and the grating waveguide',
            fly_taper_params='dict of parameters for the taper between the bends and the flyback waveguide',
            mod_taper_params='dict of parameters for the tapers into and out of the input modulator if input_mod==True',
            mod_params='dict of parameters for the input modulator if input_mod==True',
            pad_params='dict of parameters for the pads if input_mod==True',
            wiring_params='dict of parameters for modulator wiring if input_mod==True',
            input_coupler_params='dict of parameters for input coupler',
            output_coupler_params='dict of parameters for output coupler',
            input_coupler_taper_params='dict of parameters for tapers into input coupler',
            output_coupler_taper_params='dict of parameters for tapers into output coupler',

        )

    @classmethod
    def get_default_param_values(cls) -> dict:
        return dict(
            nrows = 30,
            input_offset=10.0,
            output_offset=10.0,
            input_mod = False,
            add_coupler = True,
            mod_length=1000.0,
            pad_loc=(0.0,100.0),
            grating_params = None,
            flyback_params = None,
            bend_params = None,
            grat_taper_params = None,
            fly_taper_params = None,
            mod_taper_params = None,
            mod_params = None,
            pad_params = None,
            wiring_params = None,
            input_coupler_params = None,
            output_coupler_params=None,
            input_coupler_taper_params=None,
            output_coupler_taper_params=None,
        )

    def draw_layout(self) -> None:
        self.create_serp_components()
        self.place_serp_components()
        if self.input_mod:
            self.route_wiring()
            self.create_mod_components()
            self.place_mod_components()
        self.place_io_wgs()
        if self.add_coupler:
            self.create_coupler_components()
            self.place_coupler_components()

        self.add_ports()
        #if not self.add_coupler:
        #    self.add_ports()

    def create_serp_components(self) -> None:
        """
        Generate templates for each component in serpentine
        """
        grating_module = importlib.import_module(self.grating_params['module'])
        grating_class = getattr(grating_module, self.grating_params['class'])
        self.grating = self.new_template(params=self.grating_params,
                                         temp_cls=grating_class,
                                         temp_name = 'GratingWaveguide')

        flyback_module = importlib.import_module(self.flyback_params['module'])
        flyback_class = getattr(flyback_module, self.flyback_params['class'])
        self.flyback = self.new_template(params=self.flyback_params,
                                         temp_cls=flyback_class,
                                         temp_name='Flyback')

        bend_module = importlib.import_module(self.bend_params['module'])
        bend_class = getattr(bend_module, self.bend_params['class'])
        self.bend = self.new_template(params=self.bend_params,
                                      temp_cls=bend_class,
                                      temp_name='Bend')

        grat_taper_module = importlib.import_module(self.grat_taper_params['module'])
        grat_taper_class = getattr(grat_taper_module, self.grat_taper_params['class'])
        self.grat_taper = self.new_template(params=self.grat_taper_params,
                                         temp_cls=grat_taper_class,
                                            temp_name='GratingTaper')
        fly_taper_module = importlib.import_module(self.fly_taper_params['module'])
        fly_taper_class = getattr(fly_taper_module, self.fly_taper_params['class'])
        self.fly_taper = self.new_template(params=self.fly_taper_params,
                                         temp_cls=fly_taper_class,
                                           temp_name='FlybackTaper')

        #Input/output waveguides
        wg_params = dict(
            width = self.grat_taper_params['width0'],
            layer = self.grat_taper_params['layer'])
        wg_in_params = deepcopy(wg_params)
        wg_out_params = deepcopy(wg_params)
        wg_in_params['points'] = [(0.0,0.0),(self.input_offset,0.0)]
        wg_out_params['points'] = [(0.0, 0.0), (self.output_offset, 0.0)]
        self.wg_in = self.new_template(params=wg_in_params,
                                           temp_cls=WaveguideBase,
                                           temp_name='WgIn')
        self.wg_out = self.new_template(params=wg_out_params,
                                       temp_cls=WaveguideBase,
                                       temp_name='WgOut')

    def route_wiring(self):
        min_route = self.wiring_params['seps'] / 2 + self.wiring_params['widths'][0]
        if self.pad_loc[0]>(-min_route):
            raise ValueError('Pads too close to modulator input, move to the left')
        direction = np.sign(self.pad_loc[1])
        """
        #No bend code
        wire_route = [(0.0, self.wiring_params['signal_offset'])]
        wire_route.append((self.pad_loc[0],wire_route[-1][1]))
        wire_route.append((self.pad_loc[0], self.pad_loc[1]-direction*(self.wiring_params['fan_out_length']+self.pad_params['height']/2)))
        self.wiring_params['points'] = wire_route
        """

        #With bend
        bend_rad = self.pad_loc[0]
        #Draw wires over length of modulator for covering drc gaps
        #wire_route = [(-self.act_mod_length, self.wiring_params['signal_offset'])]
        wire_route = []
        wire_route.append((0.0, self.wiring_params['signal_offset']))
        for ii in range(1,90):
            wire_route.append((wire_route[0][0]+bend_rad*np.sin(np.pi/180*ii),wire_route[0][1]-bend_rad*(1-np.cos(np.pi/180*ii))))
        wire_route.append((self.pad_loc[0], self.pad_loc[1] - direction * (
        self.wiring_params['fan_out_length'] + self.pad_params['height'] / 2)))
        self.wiring_params['points'] = wire_route






    def create_mod_components(self):
        """
        Create modulator components
        """
        mod_taper_module = importlib.import_module(self.mod_taper_params['module'])
        mod_taper_class = getattr(mod_taper_module, self.mod_taper_params['class'])
        self.mod_rout_taper = self.new_template(params=self.mod_taper_params,
                                     temp_cls=mod_taper_class,
                                     temp_name='ModulatorRoutingTaper')
        mod_module = importlib.import_module(self.mod_params['module'])
        mod_class = getattr(mod_module, self.mod_params['class'])
        self.mod = self.new_template(params=self.mod_params,
                                       temp_cls=mod_class,
                                       temp_name='Modulator')
        mod_input_taper_module = importlib.import_module(self.mod_params['taper_module'])
        mod_input_taper_class = getattr(mod_input_taper_module, self.mod_params['taper_class'])
        self.mod_input_taper = self.new_template(params=self.mod_params,
                                     temp_cls=mod_input_taper_class,
                                     temp_name='ModulatorInputTaper')
        wiring_module = importlib.import_module(self.wiring_params['module'])
        wiring_class = getattr(wiring_module, self.wiring_params['class'])
        self.wiring = self.new_template(params=self.wiring_params,
                                                temp_cls=wiring_class,
                                                temp_name='Wiring')
        #Modulator gap waveguide
        wg_width = .32
        mod_gap_params = dict(
            width=wg_width,
            layer=self.grat_taper_params['layer'],
            points = [(0.0, 0.0), (self.gap_length, 0.0)])
        mod_slab_params = dict(
            width=3.32,
            layer=('si_partial','drawing'),
            points = [(0.0, 0.0), (self.gap_length, 0.0)])
        mod_block_params = dict(
            width=9.32,
            layer=('mod','drawing'),
            points=[(0.0, 0.0), (self.gap_length, 0.0)])
        self.mod_gap = self.new_template(params=mod_gap_params,
                                       temp_cls=WaveguideBase,
                                       temp_name='ModGapWg')
        self.mod_gap_slab = self.new_template(params=mod_slab_params,
                                         temp_cls=WaveguideBase,
                                         temp_name='ModGapSlab')

        #Parse pad parameters
        self.pad_params['top_x_span'] = self.pad_params['width']
        self.pad_params['bottom_x_span'] = self.pad_params['width']
        self.pad_params['top_y_span'] = self.pad_params['height']
        self.pad_params['bottom_y_span'] = self.pad_params['height']
        self.pad_params['top_bot_offset'] = 0.0


        '''
        #Manually draw pad, ViaStack doesn't work for only one layer
        pad_module = importlib.import_module(self.pad_params['module'])
        pad_class = getattr(pad_module, self.pad_params['class'])
        self.pad = self.new_template(params=self.pad_params,
                                                temp_cls=pad_class,
                                                temp_name='Pad')
        '''

    def create_coupler_components(self):
        """
        Create coupler components
        """
        input_coupler_taper_module = importlib.import_module(self.input_coupler_taper_params['module'])
        input_coupler_taper_class = getattr(input_coupler_taper_module, self.input_coupler_taper_params['class'])
        self.input_coupler_taper = self.new_template(params=self.input_coupler_taper_params,
                                           temp_cls=input_coupler_taper_class,
                                           temp_name='InputCouplerTaper')
        output_coupler_taper_module = importlib.import_module(self.output_coupler_taper_params['module'])
        output_coupler_taper_class = getattr(output_coupler_taper_module, self.output_coupler_taper_params['class'])
        self.output_coupler_taper = self.new_template(params=self.output_coupler_taper_params,
                                                     temp_cls=output_coupler_taper_class,
                                                     temp_name='OutputCouplerTaper')
        input_coupler_module = importlib.import_module(self.input_coupler_params['module'])
        input_coupler_class = getattr(input_coupler_module, self.input_coupler_params['class'])
        self.input_coupler = self.new_template(params=self.input_coupler_params,
                                     temp_cls=input_coupler_class,
                                     temp_name='InputCoupler')
        output_coupler_module = importlib.import_module(self.output_coupler_params['module'])
        output_coupler_class = getattr(output_coupler_module, self.output_coupler_params['class'])
        self.output_coupler = self.new_template(params=self.output_coupler_params,
                                               temp_cls=output_coupler_class,
                                               temp_name='OutputCoupler')


    def place_serp_components(self) -> None:

        #Make serpentine grating
        #West grating taper
        for ii in range(self.nrows):
            if ii == 0:
                #Place at origin
                self.west_grat_taper_insts[0] = self.add_instance(master = self.grat_taper,
                                                        loc=(0, 0),
                                                        orient='R0',
                                                        inst_name='WestGratingTaper'+str(ii))
            else:
                self.west_grat_taper_insts[ii] = self.add_instance_port_to_port(inst_master=self.grat_taper,
                                                                                instance_port_name='PORT0',
                                                                                self_port=self.west_bend_insts[ii-1]['PORT_OUT'],
                                                                                reflect = False,
                                                                                instance_name = 'WestGratingTaper'+str(ii))

            #Grating waveguide
            self.grating_insts[ii] = self.add_instance_port_to_port(inst_master=self.grating,
                                                        instance_port_name='PORT0',
                                                        self_port=self.west_grat_taper_insts[ii]['PORT1'],
                                                        reflect=False,
                                                       instance_name='GratingWaveguide' + str(ii))

            #East grating taper
            self.east_grat_taper_insts[ii] = self.add_instance_port_to_port(inst_master=self.grat_taper,
                                                    instance_port_name='PORT1',
                                                    self_port=self.grating_insts[ii]['PORT1'],
                                                    reflect=False,
                                                    instance_name='EastGratingTaper' + str(ii))

            if ii<(self.nrows-1):
                #Not last row, add flyback routing
                #East bend
                self.east_bend_insts[ii] = self.add_instance_port_to_port(inst_master=self.bend,
                                                        instance_port_name='PORT_IN',
                                                        self_port=self.east_grat_taper_insts[ii]['PORT0'],
                                                        reflect=False,
                                                        instance_name='EastBend' + str(ii))

                # East flyback taper
                self.east_fly_taper_insts[ii] = self.add_instance_port_to_port(inst_master=self.fly_taper,
                                                        instance_port_name='PORT0',
                                                        self_port=self.east_bend_insts[ii]['PORT_OUT'],
                                                        reflect=False)
                # Flyback
                self.flyback_insts[ii] = self.add_instance_port_to_port(inst_master=self.flyback,
                                                        instance_port_name='PORT0',
                                                        self_port=self.east_fly_taper_insts[ii]['PORT1'],
                                                        reflect=False)
                # West flyback taper
                self.west_fly_taper_insts[ii] = self.add_instance_port_to_port(inst_master=self.fly_taper,
                                                        instance_port_name='PORT1',
                                                        self_port=self.flyback_insts[ii]['PORT1'],
                                                        reflect=False,
                                                        instance_name='WestFlybackTaper' + str(ii))
                # West bend
                self.west_bend_insts[ii] = self.add_instance_port_to_port(inst_master=self.bend,
                                                        instance_port_name='PORT_IN',
                                                        self_port=self.west_fly_taper_insts[ii]['PORT0'],
                                                        reflect=True,
                                                        instance_name='WestBend' + str(ii))


    def place_mod_components(self) -> None:
        #Working backwards from array input
        # Add input modulator and couplers
        self.mod_rout_taper_insts[1] = self.add_instance_port_to_port(inst_master=self.mod_rout_taper,
                                                                 instance_port_name='PORT0',
                                                                 self_port=self.west_grat_taper_insts[0]['PORT0'],
                                                                 reflect=False,
                                                                 instance_name='RoutingModulatorTaper1')
        self.mod_input_taper_insts[1] = self.add_instance_port_to_port(inst_master=self.mod_input_taper,
                                                                      instance_port_name='PORT0',
                                                                      self_port=self.mod_rout_taper_insts[1]['PORT1'],
                                                                      reflect=False,
                                                                      instance_name='InputModulatorTaper1')
        for ii in range(self.n_mods):
            # Add mod block over entire modulator section
            self.add_obj(PhotonicRect(
                layer=('mod','drawing'),
                bbox=BBox(
                    bottom=-9.32/2,
                    top=9.32/2,
                    left=-self.act_mod_length-25.0 -self.gap_length*(self.n_mods-1),
                    right=-25.0,
                    resolution=self.grid.resolution,
                )))
            if ii==0:
                #First section, add to input taper
                self.mod_insts[ii] = self.add_instance_port_to_port(inst_master=self.mod,
                                                               instance_port_name='PORT1',
                                                               self_port=self.mod_input_taper_insts[1]['PORT1'],
                                                               reflect=False,
                                                               instance_name='ModulatorSection'+str(self.n_mods-1-ii))
            else:
                #Add gap waveguide and slabs
                self.mod_gap_insts[ii-1] = self.add_instance_port_to_port(inst_master=self.mod_gap,
                                                                    instance_port_name='PORT1',
                                                                    self_port=self.mod_insts[ii - 1]['PORT0'],
                                                                    reflect=False,
                                                                    instance_name='ModulatorGapWg' + str(
                                                                        self.n_mods - 2 - ii))
                self.mod_gap_slab_insts[ii - 1] = self.add_instance_port_to_port(inst_master=self.mod_gap_slab,
                                                                            instance_port_name='PORT1',
                                                                            self_port=self.mod_insts[ii - 1]['PORT0'],
                                                                            reflect=False,
                                                                            instance_name='ModulatorGapSlab' + str(
                                                                                self.n_mods - 2 - ii))
                self.mod_insts[ii] = self.add_instance_port_to_port(inst_master=self.mod,
                                                                    instance_port_name='PORT1',
                                                                    self_port=self.mod_gap_insts[ii-1]['PORT0'],
                                                                    reflect=False,
                                                                    instance_name='ModulatorSection' + str(
                                                                        self.n_mods - 1 - ii))

        self.mod_input_taper_insts[0] = self.add_instance_port_to_port(inst_master=self.mod_input_taper,
                                                                 instance_port_name='PORT1',
                                                                 self_port=self.mod_insts[self.n_mods - 1]['PORT0'],
                                                                 reflect=False,
                                                                 instance_name='InputModulatorTaper0')
        self.mod_rout_taper_insts[0] = self.add_instance_port_to_port(inst_master=self.mod_rout_taper,
                                                                       instance_port_name='PORT1',
                                                                       self_port=self.mod_input_taper_insts[0]['PORT0'],
                                                                       reflect=False,
                                                                       instance_name='RoutingModulatorTaper0')
        #Add wiring
        #Get modulator input location
        input_loc = self.mod_insts[ii]._photonic_port_list['PORT0'].center
        pad_loc = (self.pad_loc[0] + input_loc[0], self.pad_loc[1] + input_loc[1])
        self.wiring_inst = self.add_instance(master=self.wiring,
                                                   loc=input_loc,
                                                   orient='R0',
                                                   inst_name='Wiring')

        # Add fan out to pads
        x1_left = [-self.wiring_params['seps'] - self.wiring_params['widths'][0] / 2,
                   -self.wiring_params['seps'] + self.wiring_params['widths'][0] / 2]
        x1_mid = [- self.wiring_params['widths'][1] / 2, self.wiring_params['widths'][1] / 2]
        x1_right = [x1_left[0] + 2 * self.wiring_params['seps'], x1_left[1] + 2 * self.wiring_params['seps']]
        x2_left = [-self.pad_params['pitch'] - self.pad_params['width'] / 2,
                   -self.pad_params['pitch'] + self.pad_params['width'] / 2]
        x2_mid = [x2_left[0] + self.pad_params['pitch'], x2_left[1] + self.pad_params['pitch']]
        x2_right = [x2_mid[0] + self.pad_params['pitch'], x2_mid[1] + self.pad_params['pitch']]
        y1 = -self.wiring_params['fan_out_length']
        y2 = 0.0

        #Adjust points to match pad location
        x1_left = [x1_left[0] + pad_loc[0], x1_left[1] + pad_loc[0]]
        x1_mid = [x1_mid[0] + pad_loc[0], x1_mid[1] + pad_loc[0]]
        x1_right = [x1_right[0] + pad_loc[0], x1_right[1] + pad_loc[0]]
        x2_left = [x2_left[0] + pad_loc[0], x2_left[1] + pad_loc[0]]
        x2_mid = [x2_mid[0] + pad_loc[0], x2_mid[1] + pad_loc[0]]
        x2_right = [x2_right[0] + pad_loc[0], x2_right[1] + pad_loc[0]]

        y1 += pad_loc[1]-self.pad_params['height']/2
        y2 += pad_loc[1]-self.pad_params['height']/2

        self.add_obj(PhotonicPolygon(layer=self.wiring_params['layer'],
                                     points=[(x1_left[0], y1), (x1_left[1],y1), (x2_left[1], y2), (x2_left[0],y2)],
                                     resolution=self.grid.resolution,
                                     unit_mode=False))
        self.add_obj(PhotonicPolygon(layer=self.wiring_params['layer'],
                                     points=[(x1_mid[0], y1), (x1_mid[1],y1), (x2_mid[1], y2), (x2_mid[0],y2)],
                                     resolution=self.grid.resolution,
                                     unit_mode=False))
        self.add_obj(PhotonicPolygon(layer=self.wiring_params['layer'],
                                     points=[(x1_right[0], y1), (x1_right[1], y1), (x2_right[1], y2), (x2_right[0], y2)],
                                     resolution=self.grid.resolution,
                                     unit_mode=False))
        
        # Add pads
        #ViaStack aligns to side not center
        dummy_pad_offset = 10.0
        names = {0: 'LeftGroundPad',
                 1: 'SignalPad',
                 2: 'RightGroundPad'}
        for ii in range(3):
            name = names[ii]
            #Pad location
            pad_center = (pad_loc[0] + (ii-1)* self.pad_params['pitch'],pad_loc[1])
            # Open layer
            self.add_obj(PhotonicRect(
                layer=self.pad_params['pad_open_layer'],
                bbox=BBox(
                    bottom=pad_center[1] - self.pad_params['height'] / 2 + self.pad_params['pad_open_inclusion'],
                    top=pad_center[1] + self.pad_params['height'] / 2 - self.pad_params['pad_open_inclusion'],
                    left=pad_center[0] - self.pad_params['width'] / 2 + self.pad_params['pad_open_inclusion'],
                    right=pad_center[0] + self.pad_params['width'] / 2 - self.pad_params['pad_open_inclusion'],
                    resolution=self.grid.resolution,
                )))
            # Pad metal layer
            self.add_obj(PhotonicRect(
                layer=self.pad_params['top_layer'],
                bbox=BBox(
                    bottom=pad_center[1] - self.pad_params['height'] / 2,
                    top=pad_center[1] + self.pad_params['height'] / 2,
                    left=pad_center[0] - self.pad_params['width'] / 2,
                    right=pad_center[0] + self.pad_params['width'] / 2,
                    resolution=self.grid.resolution,
                )))

    def place_io_wgs(self) -> None:
        #Add input and output waveguides
        if self.input_mod:
            self.wg_insts[0] = self.add_instance_port_to_port(inst_master=self.wg_in,
                                                                          instance_port_name='PORT0',
                                                                          self_port=self.mod_rout_taper_insts[0][
                                                                              'PORT0'],
                                                                          reflect=False,
                                                                          instance_name='InputWaveguide')
        else:
            self.wg_insts[0] = self.add_instance_port_to_port(inst_master=self.wg_in,
                                                              instance_port_name='PORT0',
                                                              self_port=self.west_grat_taper_insts[0][
                                                                  'PORT0'],
                                                              reflect=False,
                                                              instance_name='InputWaveguide')
        self.wg_insts[1] = self.add_instance_port_to_port(inst_master=self.wg_out,
                                                          instance_port_name='PORT0',
                                                          self_port=self.east_grat_taper_insts[self.nrows-1][
                                                              'PORT0'],
                                                          reflect=False,
                                                          instance_name='OutputWaveguide')



    def place_coupler_components(self) -> None:
        #Add taper to input coupler
        self.coupler_taper_insts[0] = self.add_instance_port_to_port(inst_master=self.input_coupler_taper,
                                                                 instance_port_name='PORT0',
                                                                 self_port=self.wg_insts[0]['PORT1'],
                                                                 reflect=False,
                                                                 instance_name='InputCouplerTaper')
        #Add input coupler
        #self.coupler_insts[0] = self.add_instance_port_to_port(inst_master=self.input_coupler,
        #                                                             instance_port_name='PORT_OUT',
        #                                                             self_port=self.coupler_taper_insts[0]['PORT1'],
        #                                                             reflect=False,
        #                                                             instance_name='InputCoupler')
        # Add taper to output coupler
        self.coupler_taper_insts[1] = self.add_instance_port_to_port(inst_master=self.output_coupler_taper,
                                                                     instance_port_name='PORT0',
                                                                     self_port=self.wg_insts[1]['PORT1'],
                                                                     reflect=False,
                                                                     instance_name='OutputCouplerTaper')
        # Add output coupler
        self.coupler_insts[1] = self.add_instance_port_to_port(inst_master=self.output_coupler,
                                                               instance_port_name='PORT_OUT',
                                                               self_port=self.coupler_taper_insts[1]['PORT1'],
                                                               reflect=False,
                                                               instance_name='OutputCoupler')

    def add_ports(self) -> None:
        # Get input port
        self.extract_photonic_ports(
                inst=self.wg_insts[0],
                port_names=['PORT1'],
                port_renaming={'PORT1': 'PORT0'},
                show=False,
            )
        # Get output port
        self.extract_photonic_ports(
            inst=self.wg_insts[1],
            port_names=['PORT1'],
            show=False,
        )




# if __name__ == '__main__':
#     spec_file = 'specs/serpgrating.yaml'
#     plm = BPG.PhotonicLayoutManager(spec_file)
#     plm.generate_content()
#     plm.generate_gds()
#     plm.generate_flat_content()
#     plm.generate_flat_gds()
#     plm.dataprep_calibre()
