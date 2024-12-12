import BPG
from BPG.lumerical.testbench import LumericalTB
from BPG.lumerical.design_manager import LumericalDesignManager
from BPG.geometry import CoordBase

from copy import deepcopy


class AdiabaticRingBusCouplerTB(LumericalTB):
    """
    Runs a 3D FDTD simulation with a Mode source to find the coupling from straight WG to simple round ring
    """

    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        LumericalTB.__init__(self, temp_db, lib_name, params, used_names, **kwargs)

        for key, val in self.tb_params.items():  # Automatically unpack variables, tb_params created by line above
            exec(f"self.{key} = {val!r}")

        # create short name variables
        self.gap = self.layout_params['bus_wg_params']['in_through_gap']
        self.bus_width = self.layout_params['bus_wg_params']['in_through_width']
        self.rout = self.layout_params['ring_params']['outer_ring_radius']
        self.ring_width_couple = self.layout_params['ring_params']['wg_width_couplers']
        self.ring_width_contact = self.layout_params['ring_params']['wg_width_contacts']

        self.extra_FDTD_size = 2.3e-6

    def construct_tb(self):
        # ----------------------------------------------------------------------------------------
        # Create a filename based on the geometry parameters
        # ----------------------------------------------------------------------------------------
        filename = '{:s}__mesh_{:d}__rout_{:.0f}nm__gap_{:.0f}nm__wg_in_{:.0f}nm__wg_mid_{:.0f}nm_bus_{:.0f}nm'.format(
            self.filename_base,
            self.mesh_accuracy,
            1e3 * self.rout,
            1e3 * self.gap,
            1e3 * self.ring_width_couple,
            1e3 * self.ring_width_contact,
            1e3 * self.bus_width
        )

        save_params = self.add_code_obj()
        save_params.add_code('param_mesh = {:d}'.format(self.mesh_accuracy))
        save_params.add_code('param_rout = {:.0f}'.format(1e3 * self.rout))
        save_params.add_code('param_gap = {:.0f}'.format(1e3 * self.gap))
        save_params.add_code('param_ring_width_couple  = {:.0f}'.format(1e3 * self.ring_width_couple))
        save_params.add_code('param_ring_width_contact = {:.0f}'.format(1e3 * self.ring_width_contact))
        save_params.add_code('param_wg_width_bus = {:.0f}'.format(1e3 * self.bus_width))

        print('Generating lsf for file: ' + filename)

        # ----------------------------------------------------------------------------------------
        # Add an FDTD simulation
        # ----------------------------------------------------------------------------------------

        fdtd = self.add_code_obj()
        fdtd.add_code('addfdtd')

        fdtd['dimension'] = "3D"
        fdtd['mesh accuracy'] = self.mesh_accuracy

        # Setup the FDTD simulation volume so that it only includes the bottom half of the ring
        # Note: these units are all meters in lsf, but um in BPG! Need to convert using CoordBase

        # Derived parameters
        mode_delta_y = CoordBase(self.bus_width + self.gap).meters + self.extra_FDTD_size
        y_max = CoordBase(self.rout).meters
        
        # need the waveguide to go through the entire PML to ensure there are no reflections
        # fdtd[ 'x min' ] = CoordBase( self.layout_params[ 'bus_wg_start_x' ] + 1 ).meters
        # fdtd[ 'x max' ] = CoordBase( self.layout_params[ 'bus_wg_end_x' ] - 1 ).meters

        fdtd['x min'] = -1 * (CoordBase(self.rout).meters + mode_delta_y)
        fdtd['x max'] = self.monitor_offset_m

        fdtd['y min'] = -1 * (CoordBase(self.rout).meters + self.extra_FDTD_size)
        fdtd['y max'] = y_max

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
        mode_source['injection axis'] = 'y-axis'
        mode_source['direction'] = 'backward'
        mode_source['amplitude'] = 1
        mode_source['phase'] = 0

        mode_source['bent waveguide'] = 0  # set = 1 to check, 0 to uncheck

        # "Geometry" tab
        # mode_source[ 'x' ] = -1 * mode_source[ 'bend radius' ]
        # mode_source[ 'x span' ] = CoordBase( 10 * ring_params[ 'wg_width_couplers' ] ).meters
        mode_source['x'] = -1 * (CoordBase(self.rout + self.gap + self.bus_width / 2).meters)
        mode_source['x span'] = 2 * self.extra_FDTD_size

        mode_source['y'] = y_max - self.monitor_offset_m

        mode_source['z'] = fdtd['z']
        mode_source['z span'] = fdtd['z span']

        # "Frequency/Wavelength" tab
        mode_source['center wavelength'] = self.wavelength
        mode_source['wavelength span'] = self.wavelength_span

        # Now calculate the fundamental mode
        mode_source['mode selection'] = self.mode_selection
        if self.mode_selection == 'user select':
            mode_source.add_code('updatesourcemode(1)')
            mode_source['auto update'] = 0  # stop auto update of the source mode.
        else:
            mode_source.add_code('updatesourcemode')

        # Helper variables
        bend_radius = CoordBase(self.rout - self.ring_width_contact / 2).meters

        mode_source.add_code("""save("{:s}")""".format(filename))  # save geometry

        # ----------------------------------------------------------------------------------------
        # Add a mode profile field and power monitor directly after the mode source to check injection efficiency
        # ----------------------------------------------------------------------------------------

        input_monitor, input_EME_monitor = self.add_eme_monitor(
            name='input_monitor',
            EME_name='input_EME_monitor',
            monitor_type='2D Y-normal',
            x=mode_source['x'],
            x_span=mode_source['x span'],
            y=mode_source['y'] - self.monitor_offset_m,
            y_span=None,
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
            monitor_type='2D Y-normal',
            x=mode_source['x'],
            x_span=mode_source['x span'],
            y=fdtd['y min'] + 2 * self.monitor_offset_m,
            y_span=None,
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
            monitor_type='2D X-normal',
            x=0,
            x_span=None,
            y=-bend_radius,
            y_span=mode_source['x span'],
            z=fdtd['z'],
            z_span=fdtd['z span'],
            bent_waveguide=1,
            bend_radius=bend_radius,
            bend_orientation=180
        )

        # ----------------------------------------------------------------------------------------
        # Add a mode profile field and power monitor to measure the mode coupled into the ring in the reflected direction
        # ----------------------------------------------------------------------------------------

        # reflection_monitor, reflection_EME_monitor = self.add_eme_monitor(
        # 	name='reflection_monitor',
        # 	EME_name='reflection_EME_monitor',
        # 	monitor_type='2D Y-normal',
        # 	x=-1 * bend_radius,
        # 	x_span=mode_source['y span'],
        # 	y=fdtd['y max'] - self.monitor_offset_m,
        # 	y_span=None,
        # 	z=fdtd['z'],
        # 	z_span=fdtd['z span'],
        # 	bent_waveguide=1,
        # 	bend_radius=bend_radius,
        # 	bend_orientation=270
        # )

        # ----------------------------------------------------------------------------------------
        # Add a field and power monitor slicing through the ring to make sure the mode is propagating as we expect
        # ----------------------------------------------------------------------------------------
        ring_top_view_monitor = self.add_code_obj()
        ring_top_view_monitor.add_code('addprofile')

        ring_top_view_monitor['name'] = 'ring_top_view_monitor'

        ring_top_view_monitor['monitor type'] = '2D Z-normal'

        ring_top_view_monitor['z'] = CoordBase(
            0.080).meters  # hardcoded to half the WG height (=40nm for RF, 80nm for CLO)

        ring_top_view_monitor['x min'] = fdtd['x min']
        ring_top_view_monitor['x max'] = fdtd['x max']

        ring_top_view_monitor['y min'] = fdtd['y min']
        ring_top_view_monitor['y max'] = fdtd['y max']

        # ----------------------------------------------------------------------------------------
        # Run the simulation and calculate the transmission
        # ----------------------------------------------------------------------------------------

        sim_cmds = self.add_code_obj()
        sim_cmds.add_code('save')
#         sim_cmds.add_code('run')
#         sim_cmds.add_code('save')
#
#         sim_cmds.add_code("""expansion_drop = getresult("output_EME_monitor","expansion for port");
# expansion_thru = getresult("through_EME_monitor","expansion for port");
# expansion_in= getresult("input_EME_monitor","expansion for port");
#
# N_in = expansion_in.N;
# N_drop = expansion_drop.N;
# N_thru = expansion_thru.N;
#
# a_in = expansion_in.b;
# a_drop = expansion_drop.a;
# a_thru = expansion_thru.b;
#
# d = a_drop/a_in * sqrt(N_drop/N_in);
# t = a_thru/a_in * sqrt(N_thru/N_in);
#
# ?D = abs(d)^2;
# ?T = abs(t)^2;
# ?Loss = 1-T-D""")

        # sim_cmds.add_code("""matlabsave("{:s}.mat")""".format(filename))
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
            EME_monitor.add_code('updatemodes(1)')
            EME_monitor['auto update'] = 0  # stop auto update of the source mode.
        else:
            EME_monitor.add_code('updatemodes')

        EME_monitor.add_code("setexpansion('port', '{}')".format(name))

        return monitor, EME_monitor


if __name__ == '__main__':
    spec_file = 'layout/SimpleRingBusCouplerTB/specs/SimpleRingBusCouplerTB_Cband_specs.yaml'
    dsn = LumericalDesignManager(spec_file)

    mesh_accuracy_test_list = [4]
    r_out_test_list = [5, 7.5, 10]  # Create a sweep that varies the ring radius
    gap_test_list = [0.100, 0.140, 0.180, 0.220]  # Create a sweep that varies the coupling gap

    for mesh_accuracy in mesh_accuracy_test_list:
        for r_out in r_out_test_list:
            for gap in gap_test_list:
                layout_params_modified = deepcopy(dsn.base_layout_params)
                layout_params_modified['gap'] = gap
                layout_params_modified['r_out'] = r_out

                tb_params_modified = deepcopy(dsn.base_tb_params)
                tb_params_modified['mesh_accuracy'] = mesh_accuracy

                dsn.add_sweep_point(layout_params=layout_params_modified, tb_params=tb_params_modified)

    # dsn.generate_batch( batch_name = 'sweep__mesh_{:d}__rout_{:.0f}nm'.format( mesh_accuracy, 1e3 * rout ) )

    dsn.generate_batch(batch_name='SimpleRingBusCoupler_tb_CBand_45CLO')

    print('I AM DONE WOOHOO!!!!!!!!!!!!')
