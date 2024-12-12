from BPG.lumerical.testbench import LumericalTB
from BPG.lumerical.design_manager import LumericalDesignManager

from copy import deepcopy

class SimpleRingRingCouplerFDTD(LumericalTB):
    """
    Runs a 3D FDTD simulation with a Mode source to find the coupling from straight WG to simple round ring
    """

    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        LumericalTB.__init__(self, temp_db, lib_name, params, used_names, **kwargs)
        for key, val in self.tb_params.items():  # Automatically unpack variables, tb_params created by line above
            exec(f"self.{key} = {val!r}")

    def construct_tb(self):
        # ----------------------------------------------------------------------------------------
        # Add an FDTD simulation
        # ----------------------------------------------------------------------------------------

        # get the size of DUT
        dut_width = self.dut_inst.bound_box.width * 1.0e-6

        # get the size of ring radii
        input_ring_radius  = self._get_ring_radius_from_params(input_ring=True)  * 1.0e-6
        output_ring_radius = self._get_ring_radius_from_params(input_ring=False) * 1.0e-6

        # get gap between rings
        gap = self.layout_params['gap'] * 1.0e-6

        if self.simulate:
            fdtd = self.add_code_obj()
            fdtd.add_code('addfdtd')

            fdtd['dimension'] = "3D"
            fdtd['mesh accuracy'] = self.mesh_accuracy

            " Setup the FDTD simulation volume so that it only includes the bottom half of the ring "

            fdtd['x min'] = -1 * (dut_width / 2 + self.tb_params['sim_margin'])
            fdtd['x max'] = dut_width / 2 + self.tb_params['sim_margin']

            fdtd['y min'] = -self.monitor_offset_m
            fdtd['y max'] = input_ring_radius + output_ring_radius + gap + self.monitor_offset_m

            fdtd['z span'] = self.tb_params['z_span']
            fdtd['z'] = 0

            # Set the boundary conditions
            fdtd['x min bc'] = self.bc_type
            fdtd['x max bc'] = self.bc_type

            fdtd['y min bc'] = self.bc_type
            fdtd['y max bc'] = self.bc_type

            fdtd['z min bc'] = self.bc_type
            fdtd['z max bc'] = self.bc_type

            # find y-coordinates of the mesh that is closest to desired monitors' position
            mesh = self.add_code_obj()
            mesh.add_code("drop_port_y = {}".format(input_ring_radius + output_ring_radius + gap))
            mesh.add_code("""fdtd_y = getresult('FDTD', 'y');
    
    # find point closest to 0
    pointI = min(abs(fdtd_y));
    pointI_index = find(fdtd_y==pointI);
     if (pointI_index == 0) {pointI_index = find(fdtd_y==-pointI);}
     
     # find point closest to desired drop port postion
     
     temp = find(fdtd_y > drop_port_y);
     pointD_index = temp(1)-1 """)

            # ----------------------------------------------------------------------------------------
            # Add a mode source to the coupler region on the left side of the ring
            # ----------------------------------------------------------------------------------------

            mode_source = self.add_code_obj()
            mode_source.add_code('addmode')

            mode_source['name'] = 'mode_source'

            # "General" tab
            mode_source['injection axis'] = 'y-axis'
            mode_source['direction'] = 'forward'
            mode_source['amplitude'] = 1
            mode_source['phase'] = 0

            mode_source['bent waveguide'] = 1
            mode_source['bend radius'] = input_ring_radius
            mode_source['bend orientation'] = 90

            # "Geometry" tab
            mode_source['x'] = input_ring_radius
            mode_source['x span'] = self.tb_params['monitor_size']
            mode_source.add_code("set('y', fdtd_y(pointI_index))")
            mode_source['z'] = fdtd['z']
            mode_source['z span'] = fdtd['z span']

            # "Frequency/Wavelength" tab
            mode_source['center wavelength'] = self.tb_params['wavelength']
            mode_source['wavelength span'] = self.tb_params['wavelength_span']

            # Now calculate the fundamental mode
            mode_source['mode selection'] = self.mode_selection
            if self.mode_selection == 'user select':
                # update the outer BC to be PML
                mode_source.add_code("seteigensolver('override default boundaries', 1)")
                mode_source.add_code("seteigensolver('x max bc', 'PML')")

                mode_source.add_code('updatesourcemode(1)')
                mode_source['auto update'] = 0  # stop auto update of the source mode.

            else:
                mode_source.add_code('updatesourcemode')

            # ----------------------------------------------------------------------------------------
            # Add a mode profile field and power monitor directly after the mode source to check injection efficiency
            # ----------------------------------------------------------------------------------------

            input_monitor, input_EME_monitor = self.add_eme_monitor(
                name='input_monitor',
                EME_name='input_EME_monitor',
                monitor_type='2D Y-normal',
                x=input_ring_radius,
                x_span=self.tb_params['monitor_size'],
                y=self.monitor_offset_m,
                y_span=None,
                z=fdtd['z'],
                z_span=fdtd['z span'],
                bent_waveguide=1,
                bend_radius=input_ring_radius,
                bend_orientation=90
            )

            # ----------------------------------------------------------------------------------------
            # Add a mode profile field and power monitor on the through port
            # ----------------------------------------------------------------------------------------

            through_monitor, through_EME_monitor = self.add_eme_monitor(
                name='through_monitor',
                EME_name='through_EME_monitor',
                monitor_type='2D Y-normal',
                x=-1 * input_ring_radius,
                x_span=self.tb_params['monitor_size'],
                y=self.monitor_offset_m,
                y_span=None,
                z=fdtd['z'],
                z_span=fdtd['z span'],
                bent_waveguide=1,
                bend_radius=input_ring_radius,
                bend_orientation=270
            )

            # ----------------------------------------------------------------------------------------
            # Add a mode profile field and power monitor to measure the mode coupled into the ring in the desired direction
            # ----------------------------------------------------------------------------------------

            drop_monitor, drop_EME_monitor = self.add_eme_monitor(
                name='drop_monitor',
                EME_name='drop_EME_monitor',
                monitor_type='2D Y-normal',
                x=-1 * output_ring_radius,
                x_span=self.tb_params['monitor_size'],
                y=input_ring_radius + output_ring_radius + gap,
                y_span=None,
                z=fdtd['z'],
                z_span=fdtd['z span'],
                bent_waveguide=1,
                bend_radius=output_ring_radius,
                bend_orientation=270
            )

            # ----------------------------------------------------------------------------------------
            # Add a mode profile field and power monitor to measure the mode coupled into the ring in the reflected direction
            # ----------------------------------------------------------------------------------------

            reflection_monitor, reflection_EME_monitor = self.add_eme_monitor(
                name='reflection_monitor',
                EME_name='reflection_EME_monitor',
                monitor_type='2D Y-normal',
                x=output_ring_radius,
                x_span=self.tb_params['monitor_size'],
                y=input_ring_radius + output_ring_radius + gap,
                y_span=None,
                z=fdtd['z'],
                z_span=fdtd['z span'],
                bent_waveguide=1,
                bend_radius=output_ring_radius,
                bend_orientation=90
            )

            # ----------------------------------------------------------------------------------------
            # Add a field and power monitor slicing through the ring to make sure the mode is propagating as we expect
            # ----------------------------------------------------------------------------------------
            ring_top_view_monitor = self.add_code_obj()
            ring_top_view_monitor.add_code('addprofile')

            ring_top_view_monitor['name'] = 'ring_top_view_monitor'

            ring_top_view_monitor['monitor type'] = '2D Z-normal'

            ring_top_view_monitor['z'] = 80e-9
            ring_top_view_monitor['x min'] = fdtd['x min']
            ring_top_view_monitor['x max'] = fdtd['x max']

            ring_top_view_monitor['y min'] = fdtd['y min']
            ring_top_view_monitor['y max'] = fdtd['y max']

            # ----------------------------------------------------------------------------------------
            # Run the simulation and calculate the transmission
            # ----------------------------------------------------------------------------------------

            file_name = "input_radius_{:.3f}um_out_radius_{:.3f}um_gap_{:.3f}um".format(input_ring_radius * 1e6,
                                                                                        output_ring_radius * 1e6,
                                                                                        gap * 1e6)
            sim_cmds = self.add_code_obj()
            sim_cmds.add_code("setglobalmonitor('frequency points',{})".format(self.number_of_frequency_points))
            sim_cmds.add_code("save('{}.fsp')".format(file_name))

        else:

            file_name = "input_radius_{:.3f}um_out_radius_{:.3f}um_gap_{:.3f}um".format(input_ring_radius * 1e6,
                                                                                        output_ring_radius * 1e6,
                                                                                        gap * 1e6)
            sim_cmds = self.add_code_obj()

            # save variable names
            sim_cmds.add_code("load('{}.fsp')".format(file_name))
            sim_cmds.add_code("input_ring_radius= {}".format(input_ring_radius * 1e6))
            sim_cmds.add_code("gap= {}".format(gap * 1e6))
            sim_cmds.add_code("output_ring_radius= {}".format(output_ring_radius * 1e6))

            # do expansion
            sim_cmds.add_code("""expansion_drop = getresult("drop_EME_monitor","expansion for In")""")
            sim_cmds.add_code("""expansion_thru = getresult("through_EME_monitor","expansion for In")""")
            sim_cmds.add_code("""expansion_in= getresult("input_EME_monitor","expansion for In")""")

            sim_cmds.add_code("""N_in = expansion_in.N""")
            sim_cmds.add_code("""N_drop = expansion_drop.N""")
            sim_cmds.add_code("""N_thru = expansion_thru.N""")

            sim_cmds.add_code("""a_in = expansion_in.a""")
            sim_cmds.add_code("""a_drop = expansion_drop.a""")
            sim_cmds.add_code("""b_thru = expansion_thru.b""")

            sim_cmds.add_code("""d = a_drop/a_in * sqrt(N_drop/N_in)""")
            sim_cmds.add_code("""t = b_thru/a_in * sqrt(N_thru/N_in)""")
            sim_cmds.add_code("""?D = abs(d)^2""")
            sim_cmds.add_code("""?T = abs(t)^2""")
            sim_cmds.add_code("""?Loss = 1-T-D""")
            sim_cmds.add_code("""matlabsave("{:s}.mat")""".format(file_name))

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
            # update the outer BC to be PML
            EME_monitor.add_code("seteigensolver('override default boundaries', 1)")
            if bend_orientation == 90:
                EME_monitor.add_code("seteigensolver('x max bc', 'PML')")
            else:
                EME_monitor.add_code("seteigensolver('x min bc', 'PML')")

            EME_monitor.add_code('updatemodes(1)')
            EME_monitor['auto update'] = 0  # stop auto update of the source mode.
        else:
            EME_monitor.add_code('updatemodes')

        EME_monitor.add_code("setexpansion('In', '{}')".format(name))

        return monitor, EME_monitor

    def _get_ring_radius_from_params(self, input_ring):
        """ Function returns outer ring radius
        Params:
            input_ring: Boolean value which determines if radius of input or output ring is returned"""
        if input_ring:
            if self.layout_params['input_ring_class'] == 'SimpleRing':
                return self.layout_params['input_ring_params']['r_out']

            elif self.layout_params['input_ring_class'] == 'RingConstantRout':
                return self.layout_params['input_ring_params']['rout']

            elif self.layout_params['input_ring_class'] == 'SimpleAdiabaticRing':
                return self.layout_params['input_ring_params']['ring_params']['outer_ring_radius']

        else:
            if self.layout_params['output_ring_class'] == 'SimpleRing':
                return self.layout_params['output_ring_params']['r_out']

            elif self.layout_params['output_ring_class'] == 'RingConstantRout':
                return self.layout_params['output_ring_params']['rout']

            elif self.layout_params['output_ring_class'] == 'SimpleAdiabaticRing':
                return self.layout_params['output_ring_params']['ring_params']['outer_ring_radius']
