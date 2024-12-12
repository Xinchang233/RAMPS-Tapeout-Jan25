# Last updated 5/29/2019

# This is a simple linear photodetector with SiGe implant in GF45RFSOI
# This class is written in a process-specific way, since we are taking advantage of the specific SiGe layer

# the default parameters are from kramnik's EE232 LinearPD design, modified from Luca Aloatti's 2015 APL paper to reduce contact losses and improve confinement factor in SiGe
# since the device width has been increased from 4um to 5um, the bandwidth may be reduced due to higher access resistance
# Todo: make the well dopings a layer list and have the layout script iterate over multiple layers -- we need to combine well dopings to get high doping for low access resistance

import BPG
from bag.layout.util import BBox
import importlib
from Photonic_Core_Layout.ViaStack_test.ViaStack import ViaStack

class LinearPD( BPG.PhotonicTemplateBase ):

	def __init__( self, temp_db, lib_name, params, used_names, **kwargs ):
		BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)

	@classmethod
	def get_default_param_values( cls ) -> dict:
		return dict(				
			device_centered_on_sige = False,
			pd_length = 100.000,
			pd_width = 5.000, # changed from 5
			silicide_width = 0.500, # changed from 0.5
			nplus_sd_width = 1.000,
			pplus_sd_width = 1.000,
			sige_width = 0.300,
			pn_junction_offset_from_sige = 0.000,
			polysi_width = 0.130,
			active_si_layer = ( 'si_full_free', 'drawing' ), # put everywhere you want crystalline body silicon instead of oxide
			silicide_layer = ( 'n_heavy_sil', 'drawing' ), # this is the inverse of SBLK, so put it where you want contacts
			nplus_sd_layer = ( 'n_heavy_sil', 'drawing' ), # guess, it's highest n-doping in spreadsheet
			pplus_sd_layer = ( 'p_heavy_sil', 'drawing' ), # guess, it's highest p-doping in spreadsheet
			sige_layer = ( 'tjphot', 'drawing' ), # this draws directly on the derived SiGe layer (TJ)
			polysi_layer = ( 'si_poly_free', 'drawing' ), # polysilicon (not sure if it's just predoped, or if it gets other dopings too)
			nwell_layer_list = [ ( 'n_inter_phot', 'drawing' ), ( 'nw2phot', 'drawing' ), ( 'nw3phot', 'drawing' ), ( 'nw4phot', 'drawing' ) ], # just a guess for now, see doping spreadsheet, CONFIRM BEFORE TAPING OUT
			pwell_layer_list = [ ( 'p_inter_phot', 'drawing' ), ( 'pw4phot', 'drawing' ), ( 'pw5phot', 'drawing' ), ( 'pw6phot', 'drawing' ), ( 'pw8phot', 'drawing' ) ], # just a guess for now, see doping spreadsheet, CONFIRM BEFORE TAPING OUT
			electrode_layer_top = ( 'B1', 'drawing' ), # pick a metal layer in the BEOL stack that's high enough for electrical routing (C2 or B1 are OK based on my notes), electrodes are same size as silicide
			electrode_label_pwell = 'anode', # Don't do "_P" and "_N" because it gets confusing when there are also differential signals in the netlist
			electrode_label_nwell = 'kathode',
			io_port_layer = ( 'si_full_free', 'drawing' ), # got this from the FilterRingBase yaml
			io_wg_width = 0.400, # in the future, this should be a waveguide parameter dict instead
			io_draw_tapers_on_both_ends = True, # useful for characterization
			io_taper_end_width = 1.600, # width chosen to optimize overlap between mode at the end of taper and mode in pSi ridge waveguide
			io_taper_length = 10.000 # 4um is the min
		)

	@classmethod
	def get_params_info( cls ) -> dict:
		return dict(
			device_centered_on_sige = 'Set true to center on SiGe (Like Luca paper), set false to center on polySi',
			pd_length = 'Total length (x-direction) of linear PD SiGe waveguide',	
			pd_width = 'Total width (y-direction) of linear PD and contacts',
			silicide_width = 'Width (y-direction) of silicide over P/N contacts',
			nplus_sd_width = 'Width (y-direction) of n+ contact implant in n-well',
			pplus_sd_width = 'Width (y-direction) of p+ contact implant in p-well',
			sige_width = 'Width (y-direction) of SiGe epitaxy to the side of polySi core',
			pn_junction_offset_from_sige = 'Offset (+y-direction) of p/n well junction from middle of SiGe',
			polysi_width = 'Width (y-direction) of polysilicon waveguide core',
			active_si_layer = '(Positive) active Si region in the device (as opposed to oxide)',
			silicide_layer = '(Positive) silicide formation layer',
			nplus_sd_layer = '(Positive) n++ layer',
			pplus_sd_layer = '(Positive) p++ layer',
			sige_layer = '(Positive) SiGe layer',
			polysi_layer = '(Positive) polySi layer',
			nwell_layer_list = 'list of (Positive) n-well layers',
			pwell_layer_list = 'list of (Positive) p-well layers',
			electrode_layer_top = '(Positive) top layer of metal that via stack goes to',
			electrode_label_pwell = 'Label for p+/p-well electrode (anode)',
			electrode_label_nwell = 'Label for n+/n-well electrode (kathode)',
			io_port_layer = 'Input/output cSi waveguide layer',
			io_wg_width = 'Input/output cSi waveguide layer (switch to waveguide dict later)',
			io_draw_tapers_on_both_ends = 'Set true to draw two tapers, set false to draw taper only on left (entry) side',
			io_taper_end_width = 'Final expansion width of input/output cSi adiabatic taper',
			io_taper_length = 'Length of input/output cSi adiabatic taper'
		)	

	def draw_layout( self ):
		
		# -----------------------------------------------------------------------	
		# Calculate device geometry parameters
		# -----------------------------------------------------------------------

		if( self.params[ 'device_centered_on_sige' ] ):
			sige_top = 0.5 * self.params[ 'sige_width' ]
			sige_bot = -0.5 * self.params[ 'sige_width' ]

			poly_top = sige_top + self.params[ 'polysi_width' ]
			poly_bot = sige_top
		else:		
			poly_top = 0.5 * self.params[ 'polysi_width' ]
			poly_bot = -0.5 * self.params[ 'polysi_width' ]

			sige_top = poly_bot
			sige_bot = poly_bot - self.params[ 'sige_width' ]
		
		sige_center = ( sige_top + sige_bot ) / 2
	
		pd_top = 0.5 * self.params[ 'pd_width' ]
		pd_bot = -0.5 * self.params[ 'pd_width' ]

		# this centers the device on the middle of the PD waveguide
		input_taper_left = -1 * self.params[ 'pd_length' ] / 2 - self.params[ 'io_taper_length' ]
		input_taper_right = input_taper_left + self.params[ 'io_taper_length' ] 

		pd_left = input_taper_right
		pd_right = input_taper_right + self.params[ 'pd_length' ]

		output_taper_left = pd_right
		output_taper_right = output_taper_left + self.params[ 'io_taper_length' ]
		
		# -----------------------------------------------------------------------
		# Draw main device geometry in Si layers
		# -----------------------------------------------------------------------	
		
		# Draw Si device region
		layer = self.params[ 'active_si_layer' ]
		self.add_rect( layer = layer,
			bbox = BBox( left = pd_left,
				bottom = pd_bot,
                                right = pd_right,
                                top = pd_top, 
                                resolution = self.grid.resolution,
                                unit_mode = False )
			)	
		
		# Draw SiGe heteroepitaxy		
		layer = self.params[ 'sige_layer' ]
		self.add_rect( layer = layer,
			bbox = BBox( left = pd_left,
				bottom = sige_bot,
                                right = pd_right,
                                top = sige_top,
                                resolution = self.grid.resolution,
                                unit_mode = False )
			)	
		
		# Draw polySi waveguide ridge
		layer = self.params[ 'polysi_layer' ]
		self.add_rect( layer = layer,
			bbox = BBox( left = pd_left,
				bottom = poly_bot,
                                right = pd_right,
                                top = poly_top,
                                resolution = self.grid.resolution,
                                unit_mode = False )
			)
		
		# Draw n-well dopings on bottom (-y) side of PD
		nwell_layer_list = self.params[ 'nwell_layer_list' ]
		for lpp in nwell_layer_list:
			self.add_rect( layer = lpp,
				bbox = BBox( left = pd_left,
					bottom = pd_bot,
                        	        right = pd_right,
                        	        top = sige_center + self.params[ 'pn_junction_offset_from_sige' ], 
                        	        resolution = self.grid.resolution,
                        	        unit_mode = False )
				)
		
		# Draw p-well dopings on top (+y) side of PD
		pwell_layer_list = self.params[ 'pwell_layer_list' ]
		for lpp in pwell_layer_list:
			self.add_rect( layer = lpp,
				bbox = BBox( left = pd_left,
					bottom = sige_center + self.params[ 'pn_junction_offset_from_sige' ],
                	                right = pd_right,
                	                top = pd_top,
                	                resolution = self.grid.resolution,
                	                unit_mode = False )
				)
			
		# Draw n+ source/drain implant
		layer = self.params[ 'nplus_sd_layer' ]
		self.add_rect( layer = layer,
			bbox = BBox( left = pd_left,
				bottom = pd_bot,
                                right = pd_right,
                                top = pd_bot + self.params[ 'nplus_sd_width' ], 
                                resolution = self.grid.resolution,
                                unit_mode = False )
			)

		# Draw p+ source/drain implant
		layer = self.params[ 'pplus_sd_layer' ]
		self.add_rect( layer = layer,
			bbox = BBox( left = pd_left,
				bottom = pd_top - self.params[ 'pplus_sd_width' ],
                                right = pd_right,
                                top = pd_top,
                                resolution = self.grid.resolution,
                                unit_mode = False )
			)	

		# Draw silicide over n+ contact
		layer = self.params[ 'silicide_layer' ]
		self.add_rect( layer = layer,
			bbox = BBox( left = pd_left,
				bottom = pd_bot,
                                right = pd_right,
                                top = pd_bot + self.params[ 'silicide_width' ], 
                                resolution = self.grid.resolution,
                                unit_mode = False )
			)	
			
		# Draw silicide over p+ contact
		layer = self.params[ 'silicide_layer' ]
		self.add_rect( layer = layer,
			bbox = BBox( left = pd_left,
				bottom = pd_top - self.params[ 'silicide_width' ],
                                right = pd_right,
                                top = pd_top,
                                resolution = self.grid.resolution,
                                unit_mode = False )
			)	
		
		# -----------------------------------------------------------------------
		# Draw electrodes on bottom metal connected by vias to active Si
		# See ringheater.py in Photonic_Core_Layout for an example of via use
		# -----------------------------------------------------------------------
		
		# Create the electrode via stacks
		via_stack_params = dict(
			top_layer = self.params[ 'electrode_layer_top' ],
			bottom_layer = ( 'RX', 'drawing' ), # need to hardcode this because 'si_full_free' won't work
			top_x_span = self.params[ 'pd_length' ],
			top_y_span = self.params[ 'silicide_width' ],
			bottom_x_span = self.params[ 'pd_length' ],
			bottom_y_span = self.params[ 'silicide_width' ],
			side_align = True,
		)

		via_stack_master = self.new_template( params = via_stack_params, temp_cls = ViaStack )

		# Place the via stacks
		pplus_via_stack_loc = ( pd_left, pd_top - 0.5 * self.params[ 'silicide_width' ] )
		pplus_via_stack = self.add_instance(
			master = via_stack_master,
			inst_name = 'pplus_via_stack',
			loc = pplus_via_stack_loc,
			orient = 'R0',
			unit_mode = False,
		)

		nplus_via_stack_loc = ( pd_left, pd_bot + 0.5 * self.params[ 'silicide_width' ] )
		nplus_via_stack = self.add_instance(
			master = via_stack_master,
			inst_name = 'nplus_via_stack',
			loc = nplus_via_stack_loc,
			orient = 'R0',
			unit_mode = False,
		)		

		# Add electrode contact labels for P&R tools
		self.add_pin_primitive(
			net_name = self.params[ 'electrode_label_pwell' ],
			layer = self.params[ 'electrode_layer_top' ][ 0 ],
			bbox = pplus_via_stack.bound_box,
		)

		self.add_pin_primitive(
			net_name = self.params[ 'electrode_label_nwell' ],
			layer = self.params[ 'electrode_layer_top' ][ 0 ],
			bbox = nplus_via_stack.bound_box,
		)

		# Old way: just add labels (can't be accessed for each class instance, unlike ports)
		#self.add_label(
		#	label = self.params[ 'electrode_label_pwell' ],
		#	layer = self.params[ 'electrode_layer_top' ][0],
		#	bbox = pplus_via_stack.bound_box,
		#)

		#self.add_label(
		#	label = self.params[ 'electrode_label_nwell' ],
		#	layer = self.params[ 'electrode_layer_top' ][0],
		#	bbox = nplus_via_stack.bound_box,
		#)
		
		# -----------------------------------------------------------------------
		# Draw input and output tapers
		# -----------------------------------------------------------------------
		
		# Draw a linear taper on the left side between the PD and input WG
		layer_taper = self.params[ 'active_si_layer' ]
		self.add_polygon( layer = layer_taper,
			resolution = self.grid.resolution,
			points = [ ( input_taper_left, -1 * self.params[ 'io_wg_width' ] / 2 ),
				( input_taper_left, self.params[ 'io_wg_width' ] / 2 ),
				( input_taper_right, self.params[ 'io_taper_end_width' ] / 2 ),
				( input_taper_right, -1 * self.params[ 'io_taper_end_width' ] / 2 ) ],
			unit_mode = False
		)

		port_xcoord_left = input_taper_left

		# If specified, draw another identical linear taper on the right side between PD and output WG
		if( self.params[ 'io_draw_tapers_on_both_ends' ] ):
			self.add_polygon( layer = layer_taper,
				resolution = self.grid.resolution,
				points = [ ( output_taper_left, -1 * self.params[ 'io_taper_end_width' ] / 2 ),
					( output_taper_left, self.params[ 'io_taper_end_width' ] / 2 ),
					( output_taper_right, self.params[ 'io_wg_width' ] / 2 ),
					( output_taper_right, -1 * self.params[ 'io_wg_width' ] / 2 ) ],
				unit_mode = False
			)
			port_xcoord_right = output_taper_right
		else:
			port_xcoord_right = pd_right	
					
		# Add photonic ports to the edges of the device
		self.draw_ports( port_xcoord_left, port_xcoord_right )	
	
	def draw_ports( self, port_xcoord_left, port_xcoord_right ):
	
		self.add_photonic_port(
			name = 'LEFT',
			orient = 'R0',
			center = ( port_xcoord_left, 0 ),
			width = self.params[ 'io_wg_width' ],
			layer = self.params[ 'io_port_layer' ],
			resolution = self.grid.resolution,
			unit_mode = False,
			show = False )
		
		self.add_photonic_port(
			name = 'RIGHT',
			orient = 'R180',
			center = ( port_xcoord_right, 0 ),
			width = self.params[ 'io_wg_width' ],
			layer = self.params[ 'io_port_layer' ],
			resolution = self.grid.resolution,
			unit_mode = False,
			show = False )


if __name__ == '__main__':
    spec_file = 'layout/LinearPD/LinearPD/specs/LinearPD_specs.yaml'
    PLM = BPG.PhotonicLayoutManager( spec_file )
    PLM.generate_content( )
    PLM.generate_gds( )
    # PLM.dataprep_calibre( ) # Comment out for faster iteration
    #
    # PLM.generate_flat_content()
    # PLM.generate_lsf( )
    
    # PLM.generate_flat_gds()
    # PLM.generate_flat_gds(debug=True, generate_gds=True)
    # PLM.dataprep()
