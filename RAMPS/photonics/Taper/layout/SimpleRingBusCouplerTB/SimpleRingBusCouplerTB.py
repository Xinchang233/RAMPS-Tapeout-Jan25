import BPG
from BPG.lumerical.testbench import LumericalTB
from BPG.lumerical.design_manager import LumericalDesignManager
from BPG.geometry import CoordBase

from copy import deepcopy


class SimpleRingBusCouplerFDTD(LumericalTB):
    """
    Runs a 3D FDTD simulation with a Mode source to find the coupling from straight WG to simple round ring
    """

    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        LumericalTB.__init__(self, temp_db, lib_name, params, used_names, **kwargs)

        for key, val in self.tb_params.items():  # Automatically unpack variables, tb_params created by line above
            exec(f"self.{key} = {val!r}")

    def construct_tb(self):
        # ----------------------------------------------------------------------------------------
        # Create a filename based on the geometry parameters
        # ----------------------------------------------------------------------------------------
        self.rout = self.get_radius()  # outer radius
        self.ring_width = self.get_ring_width()
        self.wg_width = 1e-6 * self.layout_params['wg_width']
        self.gap = 1e-6 * self.layout_params['gap']
        self.simulate = self.tb_params['simulate']

        # define number of frequency points
        self.number_of_frequency_points = self.tb_params[
            'number_of_frequency_points'] if 'number_of_frequency_points' in self.tb_params.keys() else 11

        filename = '{:s}__mesh_{:d}__rout_{:.0f}nm__gap_{:.0f}nm__wgwidthring_{:.0f}nm__wgwidthbus_{:.0f}nm'.format(
            self.filename_base,
            self.mesh_accuracy,
            1e9 * self.rout,
            1e9 * self.gap,
            1e9 * self.ring_width,
            1e9 * self.wg_width
        )

        print('Generating lsf for file: ' + filename)

        # ----------------------------------------------------------------------------------------
        # Add an FDTD simulation
        # ----------------------------------------------------------------------------------------
        if self.simulate:
            fdtd = self.add_code_obj()
            fdtd.add_code('addfdtd')

            fdtd['dimension'] = "3D"
            fdtd['mesh accuracy'] = self.mesh_accuracy

            # Setup the FDTD simulation volume so that it only includes the bottom half of the ring
            # Note: these units are all meters in lsf, but um in BPG! Need to convert using CoordBase

            # Derived parameters
            mode_delta_y = 10 * self.wg_width

            # need the waveguide to go through the entire PML to ensure there are no reflections
            # fdtd[ 'x min' ] =  self.layout_params[ 'bus_wg_start_x' ] + 1
            # fdtd[ 'x max' ] =  self.layout_params[ 'bus_wg_end_x' ] - 1

            fdtd['x min'] = -1 * (self.rout + mode_delta_y / 2)
            fdtd['x max'] = self.rout + mode_delta_y / 2

            fdtd['y min'] = -1 * self.wg_width / 2 - mode_delta_y / 2
            fdtd['y max'] = self.wg_width / 2 + self.gap + self.rout  # ring_center_y

            fdtd['z span'] = self.z_span
            fdtd['z'] = 0

            # Set the boundary conditions
            fdtd['x min bc'] = self.bc_type
            fdtd['x max bc'] = self.bc_type

            fdtd['y min bc'] = self.bc_type
            fdtd['y max bc'] = self.bc_type

            fdtd['z min bc'] = self.bc_type
            fdtd['z max bc'] = self.bc_type

            # ----------------------------------------------------------------------------------------
            # Add a mode source to the coupler region on the left side of the ring
            # ----------------------------------------------------------------------------------------

            mode_source = self.add_code_obj()
            mode_source.add_code('addmode')

            mode_source['name'] = 'mode_source'

            # "General" tab
            mode_source['injection axis'] = 'x-axis'
            mode_source['direction'] = 'forward'
            mode_source['amplitude'] = 1
            mode_source['phase'] = 0

            mode_source['bent waveguide'] = 0  # set = 1 to check, 0 to uncheck

            # "Geometry" tab
            # mode_source[ 'x' ] = -1 * mode_source[ 'bend radius' ]
            # mode_source[ 'x span' ] =  10 * ring_params[ 'wg_width_couplers' ]
            mode_source['x'] = fdtd['x min'] + self.monitor_offset_m  # Mode source can't overlap PML boundary
            # no x-span for 2D source

            mode_source['y'] = 0
            mode_source['y span'] = mode_delta_y

            mode_source['z'] = fdtd['z']
            mode_source['z span'] = fdtd['z span']

            # "Frequency/Wavelength" tab
            mode_source['center wavelength'] = self.wavelength
            mode_source['wavelength span'] = self.wavelength_span
            mode_source['optimize for short pulse'] = 0

            # Now calculate the fundamental mode
            mode_source['mode selection'] = self.mode_selection
            if self.mode_selection == 'user select':
                mode_source.add_code('updatesourcemode(1)')
                mode_source['auto update'] = 0  # stop auto update of the source mode.
            else:
                mode_source.add_code('updatesourcemode')

            # Helper variables
            bend_radius = self.rout - self.ring_width / 2

            mode_source.add_code("""save("{:s}.fsp")""".format(filename))  # save geometry

            # ----------------------------------------------------------------------------------------
            # Add a mode profile field and power monitor directly after the mode source to check injection efficiency
            # ----------------------------------------------------------------------------------------

            input_monitor, input_EME_monitor = self.add_eme_monitor(
                name='input_monitor',
                EME_name='input_EME_monitor',
                monitor_type='2D X-normal',
                x=mode_source['x'] + self.monitor_offset_m,
                x_span=None,
                y=mode_source['y'],
                y_span=mode_source['y span'],
                z=fdtd['z'],
                z_span=fdtd['z span'],
                bent_waveguide=0,
                bend_radius=None,
                bend_orientation=None
            )

            # ----------------------------------------------------------------------------------------
            # Add a mode profile field and power monitor on the through port
            # ----------------------------------------------------------------------------------------

            through_monitor, through_EME_monitor = self.add_eme_monitor(
                name='through_monitor',
                EME_name='through_EME_monitor',
                monitor_type='2D X-normal',
                x=fdtd['x max'] - 2 * self.monitor_offset_m,
                x_span=None,
                y=mode_source['y'],
                y_span=mode_source['y span'],
                z=fdtd['z'],
                z_span=fdtd['z span'],
                bent_waveguide=0,
                bend_radius=None,
                bend_orientation=None
            )

            # ----------------------------------------------------------------------------------------
            # Add a mode profile field and power monitor to measure the mode coupled into the ring in the desired direction
            # ----------------------------------------------------------------------------------------

            output_monitor, output_EME_monitor = self.add_eme_monitor(
                name='output_monitor',
                EME_name='output_EME_monitor',
                monitor_type='2D Y-normal',
                x=bend_radius,
                x_span=mode_source['y span'],
                y=fdtd['y max'] - self.monitor_offset_m,
                y_span=None,
                z=fdtd['z'],
                z_span=fdtd['z span'],
                bent_waveguide=1,
                bend_radius=bend_radius,
                bend_orientation=90
            )

            # ----------------------------------------------------------------------------------------
            # Add a mode profile field and power monitor to measure the mode coupled into the ring in the reflected direction
            # ----------------------------------------------------------------------------------------

            reflection_monitor, reflection_EME_monitor = self.add_eme_monitor(
                name='reflection_monitor',
                EME_name='reflection_EME_monitor',
                monitor_type='2D Y-normal',
                x=-1 * bend_radius,
                x_span=mode_source['y span'],
                y=fdtd['y max'] - self.monitor_offset_m,
                y_span=None,
                z=fdtd['z'],
                z_span=fdtd['z span'],
                bent_waveguide=1,
                bend_radius=bend_radius,
                bend_orientation=270
            )

            # ----------------------------------------------------------------------------------------
            # Add a field and power monitor slicing through the ring to make sure the mode is propagating as we expect
            # ----------------------------------------------------------------------------------------
            ring_top_view_monitor = self.add_code_obj()
            ring_top_view_monitor.add_code('addprofile')

            ring_top_view_monitor['name'] = 'ring_top_view_monitor'

            ring_top_view_monitor['monitor type'] = '2D Z-normal'

            ring_top_view_monitor['z'] = 0.080e-6  # hardcoded to half the WG height

            ring_top_view_monitor['x min'] = fdtd['x min']
            ring_top_view_monitor['x max'] = fdtd['x max']

            ring_top_view_monitor['y min'] = fdtd['y min']
            ring_top_view_monitor['y max'] = fdtd['y max']

            # ----------------------------------------------------------------------------------------
            # Run the simulation and calculate the transmission
            # ----------------------------------------------------------------------------------------

            sim_cmds = self.add_code_obj()
            sim_cmds.add_code("setglobalmonitor('frequency points',{})".format(self.number_of_frequency_points))
            sim_cmds.add_code('save')
        else:

            sim_cmds = self.add_code_obj()
            sim_cmds.add_code("load('{:s}.fsp')".format(filename))
            sim_cmds.add_code("""expansion_drop = getresult("output_EME_monitor","expansion for port")""")
            sim_cmds.add_code("""expansion_thru = getresult("through_EME_monitor","expansion for port")""")
            sim_cmds.add_code("""expansion_in= getresult("input_EME_monitor","expansion for port")""")

            sim_cmds.add_code("""N_in = expansion_in.N""")
            sim_cmds.add_code("""N_drop = expansion_drop.N""")
            sim_cmds.add_code("""N_thru = expansion_thru.N""")

            sim_cmds.add_code("""a_in = expansion_in.a""")
            sim_cmds.add_code("""a_drop = expansion_drop.a""")
            sim_cmds.add_code("""a_thru = expansion_thru.a""")

            sim_cmds.add_code("""d = a_drop/a_in * sqrt(N_drop/N_in)""")
            sim_cmds.add_code("""t = a_thru/a_in * sqrt(N_thru/N_in)""")
            sim_cmds.add_code("""?D = abs(d)^2""")
            sim_cmds.add_code("""?T = abs(t)^2""")
            sim_cmds.add_code("""?Loss = 1-T-D""")

            # save variable names
            sim_cmds.add_code("rout= {}".format(self.rout * 1e6))
            sim_cmds.add_code("ring_width= {}".format(self.ring_width * 1e6))
            sim_cmds.add_code("gap= {}".format(self.gap * 1e6))
            sim_cmds.add_code("wg_width= {}".format(self.wg_width * 1e6))

            sim_cmds.add_code("""matlabsave("{:s}")""".format(filename))
        # sim_cmds.add_code('save')

    def add_eme_monitor(self, name, EME_name, monitor_type, x, x_span, y, y_span, z, z_span, bent_waveguide,
                        bend_radius=None, bend_orientation=None):  # Eigenmode expanstion mode monitor (2D)
        assert (monitor_type == '2D Y-normal' or monitor_type == '2D X-normal')

        monitor = self.add_code_obj()
        monitor.add_code('addpower')
        monitor['name'] = name

        # "Geometry" tab
        monitor['monitor type'] = monitor_type

        monitor['x'] = x
        monitor['y'] = y

        if monitor_type == '2D Y-normal':
            monitor['x span'] = x_span
        elif monitor_type == '2D X-normal':
            monitor['y span'] = y_span

        monitor['z'] = z
        monitor['z span'] = z_span

        # 'Mode expansion" tab
        EME_monitor = self.add_code_obj()
        EME_monitor.add_code('addmodeexpansion')
        EME_monitor['name'] = EME_name

        # "Geometry" tab
        EME_monitor['monitor type'] = monitor_type

        EME_monitor['x'] = x
        EME_monitor['y'] = y

        if monitor_type == '2D Y-normal':
            EME_monitor['x span'] = x_span
        elif monitor_type == '2D X-normal':
            EME_monitor['y span'] = y_span

        EME_monitor['z'] = z
        EME_monitor['z span'] = z_span

        EME_monitor['align to frequency monitor center'] = 1

        # Bend parameters
        if bent_waveguide == 1:
            EME_monitor['bent waveguide'] = 1  # set = 1 to check, 0 to uncheck
            EME_monitor['bend radius'] = bend_radius
            EME_monitor['bend orientation'] = bend_orientation
        else:
            EME_monitor['bent waveguide'] = 0

        # Now calculate the fundamental mode
        EME_monitor['mode selection'] = self.mode_selection
        if self.mode_selection == 'user select':
            if bent_waveguide == 1:
                EME_monitor.add_code("seteigensolver('override default boundaries', 1)")
                if bend_orientation == 90:
                    EME_monitor.add_code("seteigensolver('x max bc', 'PML')")
                else:
                    EME_monitor.add_code("seteigensolver('x min bc', 'PML')")

            EME_monitor.add_code('updatemodes(1)')
            EME_monitor['auto update'] = 0  # stop auto update of the source mode.
        else:
            EME_monitor.add_code('updatemodes')

        EME_monitor.add_code("setexpansion('port', '{}')".format(name))

        return monitor, EME_monitor

    def get_radius(self):
        """ Function returns outer ring radius
                Params:
                    input_ring: Boolean value which determines if radius of input or output ring is returned"""
        if self.layout_params['ring_class'] == 'SimpleRound':
            return 1e-6 * self.layout_params['ring_params']['r_out']

        elif self.layout_params['ring_class'] == 'SimpleRoundWithPartialEtch':
            return 1e-6 * self.layout_params['ring_params']['ring_params']['r_out']

        elif self.layout_params['ring_class'] == 'SlotRing':
            return 1e-6 * self.layout_params['ring_params']['ring_params']['rout']

    def get_ring_width(self):
        """ Function returns ring width
            Params:
                input_ring: Boolean value which determines if radius of input or output ring is returned"""
        if self.layout_params['ring_class'] == 'SimpleRound':
            return 1e-6 * self.layout_params['ring_params']['r_width']

        elif self.layout_params['ring_class'] == 'SimpleRoundWithPartialEtch':
            return 1e-6 * self.layout_params['ring_params']['ring_params']['r_width']

        elif self.layout_params['ring_class'] == 'SlotRing':
            return 1e-6 * self.layout_params['ring_params']['ring_params']['outer_ring_width']
