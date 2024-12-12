import BPG
from copy import deepcopy
import numpy as np
from layout.GratingWaveguide.DualGratingWaveguide import DualGratingWaveguide
from Photonic_Core_Layout.WaveguideBase.WaveguideBase import WaveguideBase
from Photonic_Core_Layout.AdiabaticPaths.AdiabaticPaths import AdiabaticPaths
from layout.Taper.ParabolicTaper import ParabolicTaper

class SerpentineDualGrating(BPG.PhotonicTemplateBase):
    """
    This class creates a serpentine with dual layer gratings
    """
    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)

        # Overall serpentine parameters
        self.nrows = self.params['nrows']
        self.input_offset = self.params['input_offset']
        self.output_offset = self.params['output_offset']

        # Serpentine component parameters
        self.grating_params = self.params['grating_params']
        self.flyback_params = self.params['flyback_params']
        self.bend_params = self.params['bend_params']
        self.grat_taper_params = self.params['grat_taper_params']
        self.fly_taper_params = self.params['fly_taper_params']

        # Serpentine component templates
        self.grating_wg = None
        self.flyback_wg = None
        self.bend = None
        self.grat_taper = None
        self.fly_taper = None
        self.wg_in = None
        self.wg_out = None

        # Instances
        self.grating_insts = {i: None for i in range(self.nrows)}
        self.flyback_insts = {i: None for i in range(self.nrows - 1)}
        self.west_bend_insts = {i: None for i in range(self.nrows - 1)}
        self.west_grat_taper_insts = {i: None for i in range(self.nrows)}
        self.west_fly_taper_insts = {i: None for i in range(self.nrows - 1)}
        self.east_bend_insts = {i: None for i in range(self.nrows - 1)}
        self.east_grat_taper_insts = {i: None for i in range(self.nrows)}
        self.east_fly_taper_insts = {i: None for i in range(self.nrows - 1)}
        self.wg_insts = {i: None for i in range(2)}

    @classmethod
    def get_params_info(cls):
        return dict(
            nrows = 'Integer setting the number of grating waveguides to write',
            input_offset = 'Float setting the distance between the serpentine input and input coupler',
            output_offset = 'Float setting the distance between the serpentine output and output coupler',

            grating_params = 'Dict of parameters for grating waveguide',
            flyback_params = 'Dict of parameters for flyback waveguide',
            bend_params = 'Dict of parameters for bends',
            grat_taper_params = 'Dict of parameters for taper between the bends and grating waveguides',
            fly_taper_params = 'Dict of parameters for the taper between the bends and flyback waveguide'
        )

    @classmethod
    def get_default_params_values(cls):
        return dict(
            nrows = 30,
            input_offset = 10.0,
            output_offset = 10.0,
            grating_params = None,
            flyback_params = None,
            bend_params = None,
            grat_taper_params = None,
            fly_taper_params = None,
        )

    def draw_layout(self):
        self.create_serp_components()
        self.place_serp_components()
        self.place_io_wgs()

    def create_serp_components(self):
        """
        Generates templates for each component of the serpentine
        """
        self.grating_wg = self.new_template(params=self.grating_params,
                                            temp_cls=DualGratingWaveguide,
                                            temp_name='DualGratingWaveguide')

        self.flyback_wg = self.new_template(params=self.flyback_params,
                                            temp_cls=WaveguideBase,
                                            temp_name='Flyback')

        self.bend = self.new_template(params=self.bend_params,
                                      temp_cls=AdiabaticPaths,
                                      temp_name='Bend')

        self.grat_taper = self.new_template(params=self.grat_taper_params,
                                            temp_cls=ParabolicTaper,
                                            temp_name='GratingTaper')

        self.fly_taper = self.new_template(params=self.fly_taper_params,
                                           temp_cls=ParabolicTaper,
                                           temp_name='FlybackTaper')

        # Input/output waveguides
        wg_params = dict(
            width=self.grat_taper_params['width0'],
            layer=self.grat_taper_params['layer'])
        wg_in_params = deepcopy(wg_params)
        wg_out_params = deepcopy(wg_params)
        wg_in_params['points'] = [(0.0, 0.0), (self.input_offset, 0.0)]
        wg_out_params['points'] = [(0.0, 0.0), (self.output_offset, 0.0)]
        self.wg_in = self.new_template(params=wg_in_params,
                                       temp_cls=WaveguideBase,
                                       temp_name='WgIn')
        self.wg_out = self.new_template(params=wg_out_params,
                                        temp_cls=WaveguideBase,
                                        temp_name='WgOut')

    def place_serp_components(self):
        """
        Places serpentine components row by row.
        A single row consists of a grating waveguide, a flyback waveguide, tapers, and bends.
        """
        for row in range(self.nrows):
            # West (left) grating taper
            if row is 0:
                # Starting point at the origin
                self.west_grat_taper_insts[0] = self.add_instance(
                    master = self.grat_taper,
                    loc = (0,0),
                    orient = 'R0',
                    inst_name = 'WestGratingTaper' + str(row)
                )

            else:
                self.west_grat_taper_insts[row] = self.add_instance_port_to_port(
                    inst_master = self.grat_taper,
                    instance_port_name = 'PORT0',
                    self_port = self.west_bend_insts[row-1]['PORT_OUT'],
                    reflect = False,
                    instance_name = 'WestGratingTaper' + str(row)
                )

            # Grating waveguide
            self.grating_insts[row] = self.add_instance_port_to_port(
                inst_master = self.grating_wg,
                instance_port_name = 'PORT0',
                self_port = self.west_grat_taper_insts[row]['PORT1'],
                reflect = False,
                instance_name = 'GratingWaveguide' + str(row)
            )

            # East grating taper
            self.east_grat_taper_insts[row] = self.add_instance_port_to_port(
                inst_master=self.grat_taper,
                instance_port_name='PORT1',
                self_port=self.grating_insts[row]['PORT1'],
                reflect=False,
                instance_name='EastGratingTaper' + str(row)
            )

            # Exclude last row
            if row < (self.nrows - 1):

                # East bend
                self.east_bend_insts[row] = self.add_instance_port_to_port(
                    inst_master=self.bend,
                    instance_port_name='PORT_IN',
                    self_port=self.east_grat_taper_insts[row]['PORT0'],
                    reflect=False,
                    instance_name='EastBend' + str(row)
                )

                # East flyback taper
                self.east_fly_taper_insts[row] = self.add_instance_port_to_port(
                    inst_master=self.fly_taper,
                    instance_port_name='PORT0',
                    self_port=self.east_bend_insts[row]['PORT_OUT'],
                    reflect=False,
                    instance_name='EastFlybackWaveguide' + str(row)
                )

                # Flyback Waveguide
                self.flyback_insts[row] = self.add_instance_port_to_port(
                    inst_master=self.flyback_wg,
                    instance_port_name='PORT0',
                    self_port=self.east_fly_taper_insts[row]['PORT1'],
                    reflect=False,
                    instance_name='FlybackWaveguide' + str(row)
                )

                # West flyback taper
                self.west_fly_taper_insts[row] = self.add_instance_port_to_port(
                    inst_master=self.fly_taper,
                    instance_port_name='PORT1',
                    self_port=self.flyback_insts[row]['PORT1'],
                    reflect=False,
                    instance_name='WestFlybackTaper' + str(row)
                )

                # West bend
                self.west_bend_insts[row] = self.add_instance_port_to_port(
                    inst_master=self.bend,
                    instance_port_name='PORT_IN',
                    self_port=self.west_fly_taper_insts[row]['PORT0'],
                    reflect=True,
                    instance_name='WestBend' + str(row)
                )

    def place_io_wgs(self):
        """
        Draws input and output waveguides
        """
        # Input
        self.wg_insts[0] = self.add_instance_port_to_port(
            inst_master=self.wg_in,
            instance_port_name='PORT0',
            self_port=self.west_grat_taper_insts[0]['PORT0'],
            reflect=False,
            instance_name='InputWaveguide'
        )

        # Output
        self.wg_insts[1] = self.add_instance_port_to_port(
            inst_master=self.wg_out,
            instance_port_name='PORT0',
            self_port=self.east_grat_taper_insts[self.nrows - 1]['PORT0'],
            reflect=False,
            instance_name='OutputWaveguide'
        )





