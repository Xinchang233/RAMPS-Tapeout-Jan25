import BPG
import numpy as np
from bag.layout.util import BBox
from Photonic_Core_Layout.ViaStack_test.ViaStack import ViaStack
from Photonic_Core_Layout.AdiabaticPaths.AdiabaticPaths import AdiabaticPaths
from Photonic_Core_Layout.WaveguideBase.ArbitrarySymmetricWaveguide import ArbitrarySymmetricWaveguide
from layout.LinearHeater.LinearHeater import LinearHeater
from layout.Importers.Gratings.GcUnidirWl1310nmMfd5000nm import GcUnidirWl1310nmMfd5000nm
from copy import deepcopy

class SlotRacetrackModulator(BPG.PhotonicTemplateBase):
    """
    This class generates racetrack-shaped slot modulator with subwavelength contacts
    """

    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)

        # Initialize variables and dictionary of parameters
        self.bus_loc = (0, 0)
        self.cont1_loc = None
        self.cont2_loc = None
        self.ps1_center = None
        self.ps2_center = None
        self.heater_master = None
        self.slot_extension_master = None
        self.bend_master = None
        self.slot_master = None

        # Parameters of the optical structure of the waveguide phase shifter
        # ------------------------------------------------------------------
        self.ps_layer = self.params['ps_layer']
        self.ps_length = self.params['ps_length']
        self.ps_core_width = self.params['ps_core_width']
        self.ps_slot_width = self.params['ps_slot_width']
        self.ps_contact_width = self.params['ps_contact_width']
        self.ps_contact_length = self.params['ps_contact_length']
        self.ps_contact_width = self.params['ps_contact_width']
        self.ps_contact_period = self.params['ps_contact_period']

        # Parameters of the taper
        # -----------------------
        self.taper_length = self.params['taper_length']
        self.taper_core_width_in = self.params['taper_core_width_in']
        self.taper_core_width_out = self.params['taper_core_width_out']
        self.taper_slot_width_in = self.params['taper_slot_width_in']
        self.taper_slot_width_out = self.params['taper_slot_width_out']
        self.taper_contact_length_in = self.params['taper_contact_length_in']
        self.taper_contact_length_out = self.params['taper_contact_length_out']
        self.taper_linear = self.params['taper_linear']
        self.logorlin = self.params['logorlin']

        # Parameters of racetrack bends
        # -----------------------------
        self.bend_width = self.params['bend_width']
        self.bend_port_width = self.params['bend_port_width']
        self.bend_layer = self.params['bend_layer']
        self.bend_slot_width = self.params['bend_slot_width']
        self.bend_slot_offset = self.params['bend_slot_offset']
        self.bend_slot_layer = self.params['bend_slot_layer']
        self.bend_rmin = self.params['bend_rmin']
        self.bend_curve_rate = self.params['bend_curve_rate']

        # Parameters of bus waveguide
        # ---------------------------
        self.bus_length = self.params['bus_length']
        self.bus_width = self.params['bus_width']
        self.bus_ring_gap = self.params['bus_ring_gap']
        self.bus_layer = self.params['bus_layer']
        self.bus_taper_length = self.params['bus_taper_length']
        self.bus_port_width = self.params['bus_port_width']

        # Parameters of doping and salicide layers
        # ----------------------------------------
        self.doping_info = self.params['doping_info']
        self.doping_length_extend = self.params['doping_length_extend']

        # Parameters of metal electrodes
        # ------------------------------
        self.lin_electrode_bottom_layer = self.params['lin_electrode_bottom_layer']
        self.lin_electrode_length_extend = self.params['lin_electrode_length_extend']
        self.lin_electrode_bottom_width = self.params['lin_electrode_bottom_width']
        self.lin_electrode_top_layer1 = self.params['lin_electrode_top_layer1']
        self.lin_electrode_top_width1 = self.params['lin_electrode_top_width1']
        self.lin_electrode_top_layer2 = self.params['lin_electrode_top_layer2']
        self.lin_electrode_top_width2 = self.params['lin_electrode_top_width2']

        # Parameters of auxiliary layers (such as exclusion layers)
        # --------------------------------------------------------
        self.aux_info = self.params['aux_info']

        # Parameters of metal electrodes
        # ------------------------------
        self.electrode_bridge_width = self.params['electrode_bridge_width']
        self.electrode_bridge_dist = self.params['electrode_bridge_dist']
        self.electrode_contact_width = self.params['electrode_contact_width']
        self.electrode_contact_length = self.params['electrode_contact_length']
        self.electrode_contact_dist = self.params['electrode_contact_dist']

        # Parameters of gs pads
        # ---------------------
        self.gs_electrodes = self.params['gs_electrodes']
        self.gs_pad_layer = self.params['gs_pad_layer']
        self.gs_pad_width = self.params['gs_pad_width']
        self.gs_pad_length = self.params['gs_pad_length']
        self.gs_pad_open_layer = self.params['gs_pad_open_layer']
        self.gs_pad_open_inclusion = self.params['gs_pad_open_inclusion']

        # Parameters heaters
        # ------------------
        self.heaters = self.params['heaters']
        self.heater_params = self.params['heater_params']

        # Parameters of heater pads
        # ------------------
        self.heater_pads = self.params['heater_pads']
        self.heater_wiring_width = self.params['heater_wiring_width']
        self.heater_pad_width = self.params['heater_pad_width']
        self.heater_pad_length = self.params['heater_pad_length']
        self.heater_pad_pitch = self.params['heater_pad_pitch']
        self.heater_gs_pad_dist = self.params['heater_gs_pad_dist']

        self.place_grating = self.params['place_grating']

    @classmethod
    def get_params_info(cls) -> dict:
        return dict(
            # Parameters of the optical structure of the waveguide phase shifter
            # ------------------------------------------------------------------
            ps_layer='Layer on which optical sturecture of the phase shifter is drawn',
            ps_length='Length of waveguide phase shifter',
            ps_core_width='Width of slot waveguide phase shifter',
            ps_slot_width='Slot width of slot waveguide phase shifter',
            ps_contact_length='Length of subwavelength contacts of slot waveguide phase shifter',
            ps_contact_width='Width of subwavelength contacts of slot waveguide phase shifter',
            ps_contact_period='Period of placement of subwavelength contacts on slot waveguide phase shifter',

            # Parameters of the taper
            # -----------------------
            taper_length='Length of the taper from slot waveguide bend to slot waveguide phase shifter',
            taper_core_width_in='Input width of the core of slot waveguide taper',
            taper_core_width_out='Output width of the core of slot waveguide taper',
            taper_slot_width_in='Width of the slot of slot waveguide taper at the input',
            taper_slot_width_out='Width of the slot of slot waveguide taper at the output',
            taper_contact_length_in='Length of subwavelength contacts of slot waveguide taper at its input',
            taper_contact_length_out='Length of subwavelength contacts of slot waveguide taper at its output',
            taper_linear='True: linear taper, False: logarithmic taper',
            logorlin='Determines how logarithmic the taper is',

            # Parameters of bus waveguide
            # ---------------------------
            bus_length='Bus waveguide length',
            bus_width='Bus waveguide width',
            bus_ring_gap='Gap between bus waveguide and racetrack bend',
            bus_layer='Layer on which bus waveguide is drawn',
            bus_taper_length='Length of tapers on bus waveguide',
            bus_port_width='Widths of input/output ports of bus waveguide',

            # Parameters of racetrack bends
            # -----------------------------
            bend_width='Total width of the bent slot waveguides',
            bend_port_width='Width of waveguide band at its input and output',
            bend_layer='Layer on which waveguide bend is drawn',
            bend_slot_width='Width of the slot of bent slot waveguide',
            bend_slot_offset='Offset of the slot of bent slot waveguide from the center of the waveguide',
            bend_slot_layer='Layer on which the slot of waveguide bend is drawn',
            bend_rmin='min bend radius along the length of adiabatic bent slot waveguide',
            bend_curve_rate='Threshold curvature change rate of bent slot waveguide',

            # parameters of doping layers
            doping_length_extend='',
            doping_info='List of doping dictionaries containing distances dist0, dist1 from the center of the waveguide'
                        'and doping layer',

            # parameters of via stack on either side of the waveguide
            lin_electrode_bottom_layer='Bottom layer of the electrode of slot waveguide phase shifter',
            lin_electrode_length_extend='',
            lin_electrode_bottom_width='Bottom layer width of the electrode of slot waveguide phase shifter',
            lin_electrode_top_layer1='Top layer of the electrode of slot waveguide phase shifter',
            lin_electrode_top_width1='Top layer width of the electrode of slot waveguide phase shifter',
            lin_electrode_top_layer2='Top layer of the electrode of slot waveguide phase shifter',
            lin_electrode_top_width2='Top layer width of the electrode of slot waveguide phase shifter',

            # Parameters of auxiliary layers (such as exclusion layers)
            aux_info='',

            # Parameters of metal electrodes
            # ------------------------------
            electrode_bridge_width='Width of metal strips connecting matching polarities of slot wg phase shifters',
            electrode_bridge_dist='Distance between metal strips connecting matching polarities of wg phase shifters',
            electrode_contact_width='Width of anode/cathode contacts of modulator',
            electrode_contact_length='Length of anode/cathode contacts of modulator',
            electrode_contact_dist='Distance between anode and cathode of modulator',

            # Parameters of gs pads
            # ---------------------
            gs_electrodes='Boolean variable determines if GS pads are placed or not',
            gs_pad_layer='Top Layer or LPP of GS pads',
            gs_pad_width='Width of GS pads',
            gs_pad_length='Length of GS pads',
            gs_pad_open_layer='Layer for passivation opening',
            gs_pad_open_inclusion='Inclusion of passivation opening layer inside pad layer',

            # Parameters heaters
            # ------------------
            heaters='Bool variable determines if heaters are place on racetrack',
            heater_params='Dictionary containing heater parameters',

            # Parameters of heater pads
            # ------------------
            heater_pads='Bool variable determines if heaters pads are placed',
            heater_wiring_width='Width of the wiring between the heaters on two arms and from heater to pads',
            heater_pad_width='Width of heater pads',
            heater_pad_length='length of heater pads',
            heater_pad_pitch='Pitch of heater pads',
            heater_gs_pad_dist='Distance between heater pads and gs pads',
            place_grating = 'Boolean that determines if gratings are placed'
        )

    @classmethod
    def get_default_param_values(cls) -> dict:
        """
        Returns default parameters of moscap ring
        """
        return dict(
            # Parameters of the optical structure of the waveguide phase shifter
            # ------------------------------------------------------------------
            ps_layer=('rx3phot', 'drawing'),
            ps_length=30,
            ps_core_width=0.65,
            ps_slot_width=0.1,
            ps_contact_length=1.4,
            ps_contact_width=0.08,
            ps_contact_period=0.28,

            # Parameters of the taper
            # -----------------------
            taper_length=10.0,
            taper_core_width_in=0.792,
            taper_core_width_out=0.65,
            taper_slot_width_in=0.092,
            taper_slot_width_out=0.1,
            taper_contact_length_in=0.005,
            taper_contact_length_out=1.4,
            taper_linear=False,
            logorlin=0.6,

            # Parameters of bus waveguide
            # ---------------------------
            bus_length=20.0,
            bus_width=0.5,
            bus_ring_gap=0.3,
            bus_layer=('rx3phot', 'drawing'),
            bus_taper_length=5.0,
            bus_port_width=0.7,

            # Parameters of racetrack bends
            # -----------------------------
            bend_width=0.942,
            bend_port_width=0.792,
            bend_layer=('rx3phot', 'drawing'),
            bend_slot_width=0.092,
            bend_slot_offset=0.0,
            bend_slot_layer=('rx2phot', 'drawing'),
            bend_rmin=10.0,
            bend_curve_rate=1,

            # parameters of doping layers
            doping_info=[{'dist0': 0.0, 'dist1': 2.185, 'layer': ('nw2phot', 'drawing')},
                         {'dist0': 0.0, 'dist1': 2.185, 'layer': ('nw3phot', 'drawing')},
                         {'dist0': 0.0, 'dist1': 2.185, 'layer': ('nw4phot', 'drawing')},
                         {'dist0': 1.565, 'dist1': 2.185, 'layer': ('n_inter_phot', 'drawing')},
                         {'dist0': 1.565, 'dist1': 2.185,  'layer': ('n_heavy_sil', 'drawing')},
                         {'dist0': -0.0, 'dist1': -2.185, 'layer': ('pw5phot', 'drawing')},
                         {'dist0': -0.0, 'dist1': -2.185, 'layer': ('pw8phot', 'drawing')},
                         {'dist0': -0.0, 'dist1': -2.185, 'layer': ('p_mod_phot', 'drawing')},
                         {'dist0': -0.0, 'dist1': -2.185, 'layer': ('pw3phot', 'drawing')},
                         {'dist0': -0.0, 'dist1': -2.185, 'layer': ('pw4phot', 'drawing')},
                         {'dist0': -0.0, 'dist1': -2.185, 'layer': ('pw6phot', 'drawing')},
                         {'dist0': -1.565, 'dist1': -2.185,  'layer': ('p_inter_phot', 'drawing')},
                         {'dist0': -1.565, 'dist1': -2.185,  'layer': ('n_heavy_sil', 'drawing')}
                         ],
            doping_length_extend=0.2,

            # parameters of via stack on either side of the waveguide
            lin_electrode_bottom_layer=('RX', 'drawing'),
            lin_electrode_length_extend=0.5,
            lin_electrode_bottom_width=0.3,
            lin_electrode_top_layer1=('B1', 'drawing'),
            lin_electrode_top_width1=1.0,
            lin_electrode_top_layer2=('B2', 'drawing'),
            lin_electrode_top_width2=1.2,

            # Parameters of auxiliary layers (such as exclusion layers)
            aux_info=None,

            # Parameters of metal electrodes
            # ------------------------------
            electrode_bridge_width=2.0,
            electrode_bridge_dist=5.0,
            electrode_contact_width=2.0,
            electrode_contact_length=3.0,
            electrode_contact_dist=4.0,

            # Parameters of GS pads
            gs_electrodes=False,
            gs_pad_layer=('LB', 'drawing'),
            gs_pad_width=43.0,
            gs_pad_length=65.0,
            gs_pad_open_layer=('LV', 'drawing'),
            gs_pad_open_inclusion=2.0,

            # Parameters of heaters
            # ------------------
            heaters=True,
            heater_params={'heat_layer': ('si_full_free', 'drawing'),
                           'heat_length': 40.0,
                           'heat_width': 1.9,
                           'heat_dist': 6.0,
                           'doping_info': [{'width': 2.3, 'layer': ('n_heavy_sil', 'drawing')},
                                           {'width': 2.3, 'layer': ('n_heavy_sil', 'drawing')}],
                           'contact_bottom_layer': ('RX', 'drawing'),
                           'contact_bottom_width': 1,
                           'contact_bottom_length': 2.5,
                           'contact_top_layer': ('B2', 'drawing'),
                           'contact_top_width': 1,
                           'contact_top_length': 2.5,
                           'contact_doping_extend': 0.5,
                           'contact_doping_info': [('n_heavy_sil', 'drawing'),
                                                   ('n_heavy_sil', 'drawing'),
                                                   ('BFCUS', 'drawing')]
                           },

            # Parameters of heater pads
            # ------------------
            heater_pads=False,
            heater_wiring_width=2.7,
            heater_pad_width=50,
            heater_pad_length=70,
            heater_pad_pitch=80,
            heater_gs_pad_dist=40,

            place_grating=True
        )

    def draw_layout(self):
        """
        Draws all components of rib-waveguide ring modulator
        """
        self.draw_input_wg()
        self.draw_top_slot_waveguide_bend()
        self.create_slot_wg_ps()
        self.draw_bottom_slot_waveguide_bend()
        self.place_contact_electrodes()
        if self.gs_electrodes:
            self.place_gs_electrodes()
        if self.heaters:
            self.place_heaters()
        if self.heater_pads:
            self.place_heater_pads()
        if self.place_grating:
            self.place_gratings()


    def create_slot_wg_ps(self):
        """
        Create and place waveguide phase shifters
        """
        # create a dict with taper params to be passed to arbitrary symmetric waveguide
        taper_params = {'layer1_wg_params': {'length': self.taper_length,
                                             'core_width_in': self.taper_core_width_in,
                                             'core_width_out': self.taper_core_width_out,
                                             'slot_width_in': self.taper_slot_width_in,
                                             'slot_width_out': self.taper_slot_width_out,
                                             'draw_contact': True,
                                             'contact_length_in': self.taper_contact_length_in,
                                             'contact_length_out': self.taper_contact_length_out,
                                             'contact_linear': self.taper_linear,
                                             'logorlin': self.logorlin,
                                             'contact_width': self.ps_contact_width,
                                             'contact_period': self.ps_contact_period,
                                             'layer': self.ps_layer,
                                             },
                        'layer2_wg_params': None
                        }

        # create a dict with parameters of the optical structure of the phase shifter
        ps_wg_params = {'layer1_wg_params': {'length': self.ps_length,
                                             'core_width_in': self.ps_core_width,
                                             'core_width_out': self.ps_core_width,
                                             'slot_width_in': self.ps_slot_width,
                                             'slot_width_out': self.ps_slot_width,
                                             'draw_contact': True,
                                             'contact_length_in': self.ps_contact_length,
                                             'contact_length_out': self.ps_contact_length,
                                             'contact_width': self.ps_contact_width,
                                             'contact_period': self.ps_contact_period,
                                             'layer': self.ps_layer,
                                             },
                        'layer2_wg_params': None
                        }

        # create a dict with phase shifter params to be passed to arbitrary symmetric waveguide
        ps_params = {'wg_params': ps_wg_params,
                     'doping_info': self.doping_info,
                     'doping_length_extend': self.doping_length_extend,
                     'lin_electrode_bottom_layer': self.lin_electrode_bottom_layer,
                     'lin_electrode_length_extend': self.lin_electrode_length_extend,
                     'lin_electrode_bottom_width': self.lin_electrode_bottom_width,
                     'lin_electrode_top_layer1': self.lin_electrode_top_layer1,
                     'lin_electrode_top_width1': self.lin_electrode_top_width1,
                     'lin_electrode_top_layer2': self.lin_electrode_top_layer2,
                     'lin_electrode_top_width2': self.lin_electrode_top_width2,
                     'lin_electrode_bot_dist': self.ps_core_width/2 + self.ps_contact_length,
                     'lin_electrode_top_dist': self.ps_core_width/2 + self.ps_contact_length,
                     'aux_info': self.aux_info,
                     }

        # parameters of the arbitrary symmetric waveguide
        arb_symm_wg_params = {'flip_last': False,
                              'comp_package': ['Photonic_Core_Layout.WaveguideBase.DualLayerContactedSlotWaveguide',
                                               'layout.WaveguidePhaseShifter.WaveguidePhaseShifter'],
                              'comp_class': ['DualLayerContactedSlotWaveguide',
                                             'WaveguidePhaseShifter'],
                              'comp_ports': [['PORT0', 'PORT1'],
                                             ['PORT0', 'PORT1']],
                              'comp_params': [taper_params, ps_params]
                              }

        # create a phase shifter with tapers on each side
        arb_symm_wg_master = self.new_template(params=arb_symm_wg_params, temp_cls=ArbitrarySymmetricWaveguide)

        # attach the phase shifters to slot waveguide bends
        left_ps = self.add_instance_port_to_port(inst_master=arb_symm_wg_master,
                                                 instance_port_name='PORT0',
                                                 self_port_name='PORT00',
                                                 reflect=False
                                                 )
        self.add_instance_port_to_port(inst_master=arb_symm_wg_master,
                                       instance_port_name='PORT0',
                                       self_port_name='PORT01',
                                       reflect=True
                                       )

        # Extract photonic port of the left ps which will be used for placing bottom slot bend
        self.extract_photonic_ports(inst=left_ps,
                                    port_names='PORT1',
                                    port_renaming={'PORT1': 'PORT_PS'},
                                    show=False)

    def draw_input_wg(self):
        """
        Draws input coupler waveguide of racetrack ring.
        """
        # general parameters to be passed to AdiabaticPaths
        coup_params = {'layer': self.bus_layer,
                       'port_layer': self.bus_layer,
                       'radius_threshold': 3.0,
                       'curvature_rate_threshold': 0.7,
                       'merge_arcs': False,
                       }
        straight_coup_params = {'arc_params':
                                [{'arc_type': 'straight_wg',
                                  'length': self.bus_length,
                                  'width': self.bus_width}
                                 ]}

        # update coupler parameters with straight coupler parameters
        coup_params.update(straight_coup_params)

        # coupler core master
        core_master = self.new_template(params=coup_params,
                                        temp_cls=AdiabaticPaths)

        # place center of the input waveguide at bus_loc
        coup_core = self.add_instance(
            master=core_master,
            inst_name='input_wg',
            loc=(self.bus_loc[0]-self.bus_length/2, self.bus_loc[1])
            )

        # Extract and rename the ports of coupler waveguide to be used to connect tapers below
        self.extract_photonic_ports(
            inst=coup_core,
            port_names=['PORT_IN', 'PORT_OUT'],
            port_renaming={'PORT_IN': 'PORT0',
                           'PORT_OUT': 'PORT1'},
            show=False)

        coup_params['arc_params'][0]['width'] = [self.bus_port_width, self.bus_width]
        coup_params['arc_params'][0]['length'] = self.bus_taper_length

        taper_master = self.new_template(params=coup_params,
                                         temp_cls=AdiabaticPaths)
        taper_in = self.add_instance_port_to_port(inst_master=taper_master,
                                                  self_port_name='PORT0',
                                                  instance_port_name='PORT_OUT',
                                                  reflect=False)

        taper_out = self.add_instance_port_to_port(inst_master=taper_master,
                                                   self_port_name='PORT1',
                                                   instance_port_name='PORT_OUT',
                                                   reflect=False)
        # delete bus ports
        self.delete_port(['PORT0', 'PORT1'])

        # extract taper ports
        self.extract_photonic_ports(inst=taper_in,
                                    port_names='PORT_IN',
                                    port_renaming={'PORT_IN': 'PORT0'},
                                    show=False)

        self.extract_photonic_ports(inst=taper_out,
                                    port_names='PORT_IN',
                                    port_renaming={'PORT_IN': 'PORT1'},
                                    show=False)

    def draw_top_slot_waveguide_bend(self):
        """
        Draws slot waveguide bend_1 adjacent to the coupler
        """
        # general parameters to be passed to AdiabaticPaths
        magic_number = 2.753663435620129
        wavgeguide_bend_params = {'layer': self.bend_layer,
                                  'port_layer': self.bend_layer,
                                  'x_start': self.bus_loc[0],
                                  'y_start': self.bus_loc[1],
                                  'angle_start': np.pi/2,
                                  'radius_threshold': self.bend_rmin,
                                  'curvature_rate_threshold': self.bend_curve_rate,
                                  'merge_arcs': False,
                                  }
        bend_params = {'arc_params':
                       [{'arc_type': '180_bend',
                         'size': self.bend_rmin * magic_number,
                         'turn_left': False,
                         'width': [self.bend_port_width, self.bend_width, self.bend_port_width]}
                        ]}

        wavgeguide_bend_params.update(bend_params)

        # define bend master
        self.bend_master = self.new_template(params=wavgeguide_bend_params,
                                             temp_cls=AdiabaticPaths)

        # place the bend under the coupler
        bend_loc = (self.bus_loc[0] - self.bend_rmin * magic_number/2,
                    self.bus_loc[1] - max(self.bend_master.arc_list[0]['y']) -
                        self.bend_width/2 - self.bus_width/2 - self.bus_ring_gap)

        # place top slot waveguide bend
        bend_inst = self.add_instance(
            master=self.bend_master,
            inst_name='wg_bend',
            loc=bend_loc,
            orient='R0'
            )

        # update adiabatic path parameters with slot parameters
        wavgeguide_bend_params['layer'] = self.bend_slot_layer
        wavgeguide_bend_params['arc_params'][0]['width'] = self.bend_slot_width

        # define slot master
        self.slot_master = self.new_template(params=wavgeguide_bend_params,
                                             temp_cls=AdiabaticPaths)

        # place top waveguide bend slot
        slot_loc = (bend_loc[0], bend_loc[1]+self.bend_slot_offset)
        slot_inst = self.add_instance(
            master=self.slot_master,
            inst_name='wg_bend_slot',
            loc=slot_loc,
            orient='R0'
            )

        # Extract and rename the ports of the slot of waveguide bend
        self.extract_photonic_ports(
            inst=slot_inst,
            port_names=['PORT_IN', 'PORT_OUT'],
            port_renaming={'PORT_IN': 'PORT00',
                           'PORT_OUT': 'PORT01'},
            show=False)

        # add straight waveguide extensions to the slot on the terminals
        slot_extension_params = {'arc_params':
                                 [{'arc_type': 'straight_wg',
                                   'length': self.bend_slot_offset,
                                   'width': self.bend_slot_width}
                                  ]}

        wavgeguide_bend_params.update(slot_extension_params)

        # create slot extensions
        self.slot_extension_master = self.new_template(params=wavgeguide_bend_params,
                                                       temp_cls=AdiabaticPaths)

        if self.bend_slot_offset != 0:
            # place slot extension one on each side
            self.add_instance_port_to_port(inst_master=self.slot_extension_master,
                                           instance_port_name='PORT_IN',
                                           self_port_name='PORT00')

            self.add_instance_port_to_port(inst_master=self.slot_extension_master,
                                           instance_port_name='PORT_IN',
                                           self_port_name='PORT01')

        self.delete_port(['PORT00', 'PORT01'])

        # Extract and rename the ports of waveguide bend
        self.extract_photonic_ports(
            inst=bend_inst,
            port_names=['PORT_IN', 'PORT_OUT'],
            port_renaming={'PORT_IN': 'PORT00',
                           'PORT_OUT': 'PORT01'},
            show=False)

    def draw_bottom_slot_waveguide_bend(self):
        """
        Draws bottom slot waveguide bend
        """
        # Find where the phase shifter bottom port is
        bend_loc = self.get_photonic_port(port_name='PORT_PS').center
        # place bottom slot waveguide bend
        self.add_instance(
            master=self.bend_master,
            inst_name='bottom_bend',
            loc=bend_loc,
            orient='MX'
            )

        # place bottom waveguide bend slot
        slot_inst = self.add_instance(
            master=self.slot_master,
            inst_name='wg_bend_slot',
            loc=(bend_loc[0], bend_loc[1] - self.bend_slot_offset),
            orient='MX'
            )

        if self.bend_slot_offset != 0:
            # Extract and rename the ports of of the slot of waveguide bend
            self.extract_photonic_ports(
                inst=slot_inst,
                port_names=['PORT_IN', 'PORT_OUT'],
                port_renaming={'PORT_IN': 'PORT10',
                               'PORT_OUT': 'PORT11'},
                show=False)
            # place slot extension one on each side
            self.add_instance_port_to_port(inst_master=self.slot_extension_master,
                                           instance_port_name='PORT_IN',
                                           self_port_name='PORT10')

            self.add_instance_port_to_port(inst_master=self.slot_extension_master,
                                           instance_port_name='PORT_IN',
                                           self_port_name='PORT11')

            self.delete_port(['PORT10', 'PORT11'])

    def place_contact_electrodes(self):

        self.ps1_center = (self.get_photonic_port('PORT00').center[0],
                           self.get_photonic_port('PORT00').center[1]-self.taper_length-self.ps_length/2)
        self.ps2_center = (self.get_photonic_port('PORT01').center[0],
                           self.get_photonic_port('PORT01').center[1]-self.taper_length-self.ps_length/2)

        # draw horizontal wire between inner ps contacts
        self.add_rect(layer=self.lin_electrode_top_layer1,
                      bbox=BBox(left=self.ps1_center[0] + self.ps_core_width/2 + self.ps_contact_length,
                                bottom=self.ps1_center[1]+ self.electrode_bridge_dist/2,
                                right=self.ps2_center[0] - (self.ps_core_width/2 + self.ps_contact_length),
                                top=self.ps2_center[1] + self.electrode_bridge_dist/2 + self.electrode_bridge_width,
                                resolution=self.grid.resolution)
                      )

        # draw vertical contact connected to the top bridge between inner contacts
        self.add_rect(layer=self.lin_electrode_top_layer1,
                      bbox=BBox(left=self.bus_loc[0] - self.electrode_contact_dist/2 - self.electrode_contact_width,
                                bottom=self.ps1_center[1] + self.electrode_bridge_dist/2 - self.electrode_contact_length,
                                right=self.bus_loc[0] - self.electrode_contact_dist/2,
                                top=self.ps2_center[1] + self.electrode_bridge_dist/2,
                                resolution=self.grid.resolution)
                      )

        # raise lower contact to the level of higher contact
        via_stack_master = self.new_template(params=dict(top_layer=self.lin_electrode_top_layer2,
                                                         bottom_layer=self.lin_electrode_top_layer1,
                                                         top_x_span=2*self.electrode_contact_length -
                                                                    self.electrode_bridge_dist,
                                                         top_y_span=self.electrode_contact_width,
                                                         bottom_x_span=2*self.electrode_contact_length -
                                                                       self.electrode_bridge_dist,
                                                         bottom_y_span=self.electrode_contact_width,
                                                         align='corner_align',
                                                         top_bot_offset=0.0),
                                             temp_cls=ViaStack)

        self.cont1_loc = (self.bus_loc[0] - self.electrode_contact_dist/2, self.ps1_center[1])
        self.cont2_loc = (self.bus_loc[0] + self.electrode_contact_dist/2, self.ps2_center[1])

        self.add_instance(master=via_stack_master,
                          loc=(self.cont1_loc[0], self.cont1_loc[1] -
                               self.electrode_contact_length + self.electrode_bridge_dist/2),
                          orient='MXR90')

        # draw horizontal wire between outer ps contacts
        self.add_rect(layer=self.lin_electrode_top_layer2,
                      bbox=BBox(left=self.ps1_center[0] - (self.ps_core_width/2 + self.ps_contact_length),
                                bottom=self.ps1_center[1] - (self.electrode_bridge_dist/2 + self.electrode_bridge_width),
                                right=self.ps2_center[0] + (self.ps_core_width/2 + self.ps_contact_length),
                                top=self.ps2_center[1] - self.electrode_bridge_dist/2,
                                resolution=self.grid.resolution)
                      )

        # draw vertical contact connected to the top bridge between inner contacts
        self.add_rect(layer=self.lin_electrode_top_layer2,
                      bbox=BBox(left=self.bus_loc[0] + self.electrode_contact_dist/2,
                                bottom=self.ps2_center[1] - self.electrode_bridge_dist/2,
                                right=self.bus_loc[0] + self.electrode_contact_dist/2 + self.electrode_contact_width,
                                top=self.ps2_center[1] - self.electrode_bridge_dist/2 + self.electrode_contact_length,
                                resolution=self.grid.resolution)
                      )

    def place_gs_electrodes(self):
        """
        Draws GS electrodes which are connected to ring electrodes
        """
        # Create GS pad
        gs_electrode_master = self.new_template(params=dict(top_layer=self.gs_pad_layer,
                                                            bottom_layer=self.lin_electrode_top_layer2,
                                                            top_x_span=self.gs_pad_length,
                                                            top_y_span=self.gs_pad_width,
                                                            bottom_x_span=2*self.electrode_contact_length -
                                                                          self.electrode_bridge_dist,
                                                            bottom_y_span=self.electrode_contact_width,
                                                            align='corner_align',
                                                            top_bot_offset=0.0,
                                                            pad_open_layer=self.gs_pad_open_layer,
                                                            pad_open_inclusion=self.gs_pad_open_inclusion),
                                                temp_cls=ViaStack)
        print(self.cont1_loc)
        print(self.cont2_loc)
        # Place ground electrode
        self.add_instance(master=gs_electrode_master,
                          inst_name='G_electrode',
                          loc=(self.cont1_loc[0], self.cont1_loc[1] -
                               self.electrode_contact_length + self.electrode_bridge_dist/2),
                          orient='MXR90')

        # Place signal electrode
        self.add_instance(master=gs_electrode_master,
                          inst_name='S_electrode',
                          loc=(self.cont2_loc[0], self.cont2_loc[1] -
                               self.electrode_contact_length + self.electrode_bridge_dist/2),
                          orient='R90')

    def place_heaters(self):
        """
        Place a heater on the arms of racetrack
        """
        # Create heaters
        self.heater_master = self.new_template(params=self.heater_params, temp_cls=LinearHeater)

        # Place heater on left arm
        self.add_instance(master=self.heater_master,
                          inst_name='left_heater',
                          loc=self.ps1_center,
                          orient='R0')

        # Place heater on left arm
        self.add_instance(master=self.heater_master,
                          inst_name='right_heater',
                          loc=self.ps2_center,
                          orient='R0')

        # Connect top contacts of heaters
        self.add_rect(layer=self.heater_params['contact_top_layer'],
                      bbox=BBox(left=self.ps1_center[0] - self.heater_params['heat_dist']/2 -
                                     self.heater_params['heat_width']/2 - self.heater_params['contact_top_width'] / 2,
                                right=self.ps2_center[0] + self.heater_params['heat_dist'] / 2 +
                                      self.heater_params['heat_width'] / 2 + self.heater_params['contact_top_width'] / 2,
                                bottom=self.ps1_center[1] + self.heater_params['heat_length'] / 2 +
                                       self.heater_params['contact_bottom_length'] / 2 -
                                       self.heater_params['contact_top_length'] / 2,
                                top=self.ps1_center[1] + self.heater_params['heat_length'] / 2 +
                                    self.heater_params['contact_bottom_length'] / 2 -
                                    self.heater_params['contact_top_length'] / 2 + self.heater_wiring_width,
                                resolution=self.grid.resolution)
                      )

    def place_heater_pads(self):
        """
        Places pads for heaters
        """
        # Create a pad
        heater_pad_master = self.new_template(params=dict(top_layer=self.gs_pad_layer,
                                                          bottom_layer=self.heater_params['contact_top_layer'],
                                                          top_x_span=self.heater_pad_length,
                                                          top_y_span=self.heater_pad_width,
                                                          bottom_x_span=self.heater_wiring_width,
                                                          bottom_y_span=self.heater_wiring_width,
                                                          align='corner_align',
                                                          top_bot_offset=0.0,
                                                          pad_open_layer=self.gs_pad_open_layer,
                                                          pad_open_inclusion=self.gs_pad_open_inclusion),
                                                temp_cls=ViaStack)

        # Place left pad
        self.add_instance(master=heater_pad_master,
                          inst_name='heater_pad_left',
                          loc=((self.ps1_center[0]+self.ps2_center[0])/2-(self.heater_pad_pitch-self.heater_pad_width)/2,
                               self.ps1_center[1] - self.heater_gs_pad_dist),
                          orient='R270')

        # Place right pad
        self.add_instance(master=heater_pad_master,
                          inst_name='heater_right_left',
                          loc=((self.ps1_center[0]+self.ps2_center[0])/2+(self.heater_pad_pitch-self.heater_pad_width)/2,
                               self.ps1_center[1] - self.heater_gs_pad_dist),
                          orient='MYR90')

        # Wire heaters to pads
        # left heater horizontal wire
        left = min(self.ps1_center[0],
                   (self.ps1_center[0] + self.ps2_center[0]) / 2 - (self.heater_pad_pitch - self.heater_pad_width) / 2)

        right = max(self.ps1_center[0],
                    (self.ps1_center[0] + self.ps2_center[0]) / 2 - (self.heater_pad_pitch - self.heater_pad_width) / 2)

        self.add_rect(layer=self.heater_params['contact_top_layer'],
                      bbox=BBox(left=left,
                                right=right,
                                top=self.ps1_center[1] - self.heater_params['heat_length'] / 2 -
                                       self.heater_params['contact_bottom_length'] / 2 +
                                       self.heater_params['contact_top_length'] / 2,
                                bottom=self.ps1_center[1] - self.heater_params['heat_length'] / 2 -
                                    self.heater_params['contact_bottom_length'] / 2 +
                                    self.heater_params['contact_top_length'] / 2 - self.heater_wiring_width,
                                resolution=self.grid.resolution)
                      )
        # left heater vertical wire
        bottom = min(self.ps1_center[1] - self.heater_gs_pad_dist,
                     self.ps1_center[1] - self.heater_params['heat_length'] / 2 -
                     self.heater_params['contact_bottom_length'] / 2 + self.heater_params['contact_top_length'] / 2)

        top = max(self.ps1_center[1] - self.heater_gs_pad_dist,
                  self.ps1_center[1] - self.heater_params['heat_length'] / 2 -
                  self.heater_params['contact_bottom_length'] / 2 + self.heater_params['contact_top_length'] / 2)

        if abs(self.ps1_center[0] - self.ps2_center[0]) > self.heater_pad_pitch-self.heater_pad_width:
            left = right - self.heater_wiring_width
            right = right
        else:
            right = left
            left = left - self.heater_wiring_width

        self.add_rect(layer=self.heater_params['contact_top_layer'],
                      bbox=BBox(left=left,
                                right=right,
                                top=top,
                                bottom=bottom,
                                resolution=self.grid.resolution)
                      )

        # right heater horizontal wire
        left = min((self.ps1_center[0]+self.ps2_center[0])/2 +
                   (self.heater_pad_pitch-self.heater_pad_width)/2,
                   self.ps2_center[0])
        right = max((self.ps1_center[0]+self.ps2_center[0])/2 +
                    (self.heater_pad_pitch-self.heater_pad_width)/2,
                    self.ps2_center[0])

        self.add_rect(layer=self.heater_params['contact_top_layer'],
                      bbox=BBox(left=left,
                                right=right,
                                top=self.ps1_center[1] - self.heater_params['heat_length'] / 2 -
                                       self.heater_params['contact_bottom_length'] / 2 +
                                       self.heater_params['contact_top_length'] / 2,
                                bottom=self.ps1_center[1] - self.heater_params['heat_length'] / 2 -
                                    self.heater_params['contact_bottom_length'] / 2 +
                                    self.heater_params['contact_top_length'] / 2 - self.heater_wiring_width,
                                resolution=self.grid.resolution)
                      )

        # right heater vertical wire
        bottom = min(self.ps2_center[1] - self.heater_gs_pad_dist,
                     self.ps2_center[1] - self.heater_params['heat_length'] / 2 -
                     self.heater_params['contact_bottom_length'] / 2 + self.heater_params['contact_top_length'] / 2)

        top = max(self.ps2_center[1] - self.heater_gs_pad_dist,
                  self.ps2_center[1] - self.heater_params['heat_length'] / 2 -
                  self.heater_params['contact_bottom_length'] / 2 + self.heater_params['contact_top_length'] / 2)

        if abs(self.ps1_center[0] - self.ps2_center[0]) > self.heater_pad_pitch-self.heater_pad_width:
            right = left + self.heater_wiring_width
            left = left
        else:
            left = right
            right = right + self.heater_wiring_width

        self.add_rect(layer=self.heater_params['contact_top_layer'],
                      bbox=BBox(left=left,
                                right=right,
                                top=top,
                                bottom=bottom,
                                resolution=self.grid.resolution)
                      )

    def place_gratings(self):
        grating_band_radius = 5
        grating_distance = 127
        access_length = 30
        wg_width = 0.7
        layer = ('rx3phot', 'drawing')
        reflect = False

        add_taper = True
        taper_len = 5
        taper_width = 0.5

        pad = (grating_distance - access_length) / 2
        adiabatic_band_params = dict(layer=layer, port_layer=['si_full_free', 'port'], radius_threshold=1.5,
                                     curvature_rate_threshold=0.7, merge_arcs=False)
        if grating_band_radius == 0:
            adiabatic_band_params['arc_params'] = [
                dict(arc_type="straight_wg", width=wg_width, length=pad)]
            temp_wg = self.new_template(params=adiabatic_band_params, temp_cls=AdiabaticPaths)
            right_wg_inst = self.add_instance_port_to_port(inst_master=temp_wg,
                                                           instance_port_name='PORT_IN',
                                                           self_port_name='PORT1')

            left_wg_inst = self.add_instance_port_to_port(inst_master=temp_wg, instance_port_name='PORT_IN',
                                                          self_port_name='PORT0')
            temp = self.new_template(params=None, temp_cls=GcUnidirWl1310nmMfd5000nm)
            right_inst = self.add_instance_port_to_port(inst_master=temp, instance_port_name='PORT_OUT',
                                                        self_port=right_wg_inst['PORT_OUT'])
            left_inst = self.add_instance_port_to_port(inst_master=temp, instance_port_name='PORT_OUT',
                                                       self_port=left_wg_inst['PORT_OUT'])
        else:
            adiabatic_band_params['arc_params'] = [
                dict(arc_type="straight_wg", width=wg_width,
                     length=pad - grating_band_radius * 1.8700958466)]
            temp_wg = self.new_template(params=adiabatic_band_params, temp_cls=AdiabaticPaths)
            right_wg_inst = self.add_instance_port_to_port(inst_master=temp_wg,instance_port_name='PORT_IN',
                                                           self_port_name='PORT1')

            left_wg_inst = self.add_instance_port_to_port(inst_master=temp_wg,instance_port_name='PORT_IN',
                                                          self_port_name='PORT0')
            bend90_params = deepcopy(adiabatic_band_params)
            bend90_params['arc_params'] = [
                dict(arc_type="90_bend", rmin=grating_band_radius, turn_left=False, width=wg_width)]

            temp_90_right = self.new_template(params=bend90_params, temp_cls=AdiabaticPaths)
            inst_90_right = self.add_instance_port_to_port(inst_master=temp_90_right,instance_port_name='PORT_IN',
                                                           self_port=right_wg_inst['PORT_OUT'], reflect=reflect)

            bend90_params_left = deepcopy(bend90_params)
            bend90_params_left['arc_params'][0]['turn_left'] = True
            temp_90_left = self.new_template(params=bend90_params_left, temp_cls=AdiabaticPaths)
            inst_90_left = self.add_instance_port_to_port(inst_master=temp_90_left, instance_port_name='PORT_IN',
                                                          self_port=left_wg_inst['PORT_OUT'], reflect=reflect)

            temp = self.new_template(params=None, temp_cls=GcUnidirWl1310nmMfd5000nm)

            if add_taper:
                taper_params = deepcopy(adiabatic_band_params)
                taper_params['arc_params'] = [
                    dict(arc_type="straight_wg", width=[wg_width, taper_width], length = taper_len)]

                taper_temp = self.new_template(params=taper_params, temp_cls=AdiabaticPaths)
                taper_right_inst = self.add_instance_port_to_port(inst_master=taper_temp,instance_port_name='PORT_IN',
                                                            self_port=inst_90_right['PORT_OUT'])
                taper_left_inst = self.add_instance_port_to_port(inst_master=taper_temp, instance_port_name='PORT_IN',
                                                                  self_port=inst_90_left['PORT_OUT'])

                right_inst = self.add_instance_port_to_port(inst_master=temp, instance_port_name='PORT_OUT',
                                                            self_port=taper_right_inst['PORT_OUT'])
                left_inst = self.add_instance_port_to_port(inst_master=temp, instance_port_name='PORT_OUT',
                                                           self_port=taper_left_inst['PORT_OUT'])

            else:
                right_inst = self.add_instance_port_to_port(inst_master=temp,instance_port_name='PORT_OUT',
                                                            self_port=inst_90_right['PORT_OUT'])
                left_inst = self.add_instance_port_to_port(inst_master=temp, instance_port_name='PORT_OUT',
                                                           self_port=inst_90_left['PORT_OUT'])


# if __name__ == '__main__':
#     spec_file = 'layout/SlotRacetrackModulator/specs/slot_racetrack_modulator_specs.yaml'
#     PLM = BPG.PhotonicLayoutManager(spec_file)
#     PLM.generate_content()
#     PLM.generate_gds()
#     PLM.dataprep_calibre()