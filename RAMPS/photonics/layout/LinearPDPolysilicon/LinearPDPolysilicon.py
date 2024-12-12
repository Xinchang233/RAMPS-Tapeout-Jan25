# Created on 7/29/2020

# This is a linear photodetector in 45RFSOI with an inverse polysilicon ridge waveguide, based on Amir Atabaki's paper

# Notes from Amir meeting 7/30/2020:
#	'i' region improved Q and extinction, but QE barely changed.
#	800nm to 1000nm 'i' region = sweet spot. 800nm responsivity a bit higher (10%) and is reported in paper, but losses also higher
#	Put ZPCUS everywhere to block pre-doping (big improvement in Q)
#	Ohmic contact for transistor gets s/d doping, plus halo doping (n_heavy_sil and p_heavy_sil add BH and BP/BN)
#	BH is halo extension
#	n_inter_phot gives you just BP (n-doping)
# 5 regions (top to bottom):
#	n++ contact (n_heavy_sil = BP with halo)
#	n (n_inter_phot = BP)
#	i (ideally nothing, but actually pre-doped)
#	p (p_inter_phot = BN)
#	p++ contact (p_heavy_sil = BN with halo)
# Actually, the structure above didn't work well because nwell and pwell dopings are too light compare to pre-doping
# Recommend instead to extend n++ and p++ all the way to the "i" (predoped) region

import BPG
from bag.layout.util import BBox
import importlib
from Photonic_Core_Layout_Djordje.ViaStack.ViaStack import ViaStack

class LinearPDPolysilicon( BPG.PhotonicTemplateBase ):

	def __init__( self, temp_db, lib_name, params, used_names, **kwargs ):
		BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)

	@classmethod
	def get_default_param_values( cls ) -> dict:
		return dict(
			pd_params = {
					'length' : 100.000
				},
			Si_params = {
					'layer'	: ( 'si_full_free', 'drawing' ),
					'width'	: 0.600
				},
			polySi_params = {
					'layer'	: ( 'si_poly_free', 'drawing' ),
					'width'	: 4.000
				},
			doping_list = [
					{ 'layer' : ( 'ZPCUS', 'drawing' ), 'top' : 2.000, 'bot' : -2.000 },	# block pre-doping (big improvement in Q -- would still work without it)
					#{ 'layer' : ( 'n_inter_phot', 'drawing' ), 'top' : 2.000, 'bot' : 0.400 },	# n-doping of the photodiode
					#{ 'layer' : ( 'p_inter_phot', 'drawing' ), 'top' : -0.400, 'bot' : -2.400 },# p-doping of the photodiode
					{ 'layer' : ( 'n_heavy_sil', 'drawing' ), 'top' : 2.000, 'bot' : 0.400 },	# n+ contact
					{ 'layer' : ( 'p_heavy_sil', 'drawing' ), 'top' : -0.400, 'bot' : -2.000 },	# p+ contact
				],
			silicide_params = {
					'layer'		: ( 'n_heavy_sil', 'drawing' ),
					'width'		: 0.800,
					'offset_n'	: 1.600,	# 1.2um from the device center
					'offset_p'	: -1.600
				},
			electrode_params = {
					'layer_bot'		: ( 'PC', 'drawing' ), # phot layers don't work for via stacks
					'layer_top'		: ( 'B1', 'drawing' ), # pick a metal layer in the BEOL stack that's high enough for electrical routing (C2 or B1 are OK based on my notes), electrodes are same size as silicide
					'label_pwell'	: 'anode',	# Don't do "_P" and "_N" because it gets confusing when there are also differential signals in the netlist
					'label_nwell'	: 'kathode'
				},
			port_params = {
				'layer'	: ( 'si_full_free', 'drawing' ),
				'width'	: 0.600
				}
		)

	@classmethod
	def get_params_info( cls ) -> dict:
		return dict(
			pd_params = 'Photodiode',
			Si_params = 'Silicon',
			polySi_params = 'Polysilicon',
			doping_list = 'All doping layers',
			silicide_params = 'Silicide',
			electrode_params = 'Contacts',
			port_params = 'Photonic ports',
		)	

	def draw_layout( self ):
		
		# -----------------------------------------------------------------------	
		# Calculate device geometry parameters
		# -----------------------------------------------------------------------

		pd_length = self.params[ 'pd_params' ][ 'length' ]
		pd_left = -0.5 * pd_length
		pd_right = 0.5 * pd_length
		
		# -----------------------------------------------------------------------
		# Draw main device geometry in Si layers
		# -----------------------------------------------------------------------	
		
		# Draw Si inverse waveguide ridge
		self.add_rect(
			layer = self.params[ 'Si_params' ][ 'layer' ],
			bbox = BBox(
					left = pd_left,
					bottom = -0.5 * self.params[ 'Si_params' ][ 'width' ],
					right = pd_right,
					top = 0.5 * self.params[ 'Si_params' ][ 'width' ], 
					resolution = self.grid.resolution,
					unit_mode = False
					)
			)
		
		# Draw polySi device region
		self.add_rect(
			layer = self.params[ 'polySi_params' ][ 'layer' ],
			bbox = BBox(
				left = pd_left,
				bottom = -0.5 * self.params[ 'polySi_params' ][ 'width' ],
				right = pd_right,
				top = 0.5 * self.params[ 'polySi_params' ][ 'width' ],
				resolution = self.grid.resolution,
				unit_mode = False
				)
			)

		# -----------------------------------------------------------------------
		# Draw all layers specified in the doping layer list
		# -----------------------------------------------------------------------	

		for dopant_dict in self.params[ 'doping_list' ]:
			self.add_rect(
				layer = dopant_dict[ 'layer' ],
				bbox = BBox(
					left = pd_left,
					bottom = dopant_dict[ 'bot' ],
					right = pd_right,
					top = dopant_dict[ 'top' ],
					resolution = self.grid.resolution,
					unit_mode = False
					)
				)

		# -----------------------------------------------------------------------
		# Draw silicide
		# -----------------------------------------------------------------------	

		# Load silicide params
		sil_offset_p = self.params[ 'silicide_params' ][ 'offset_p' ]
		sil_offset_n = self.params[ 'silicide_params' ][ 'offset_n' ]
		sil_width = self.params[ 'silicide_params' ][ 'width' ]

		# Add silicide for N contact
		sil_bot_n = sil_offset_n - 0.5 * sil_width
		sil_top_n = sil_offset_n + 0.5 * sil_width
		self.add_rect(
			layer = self.params[ 'silicide_params' ][ 'layer' ],
			bbox = BBox( left = pd_left, bottom = sil_bot_n, right = pd_right, top = sil_top_n, resolution = self.grid.resolution, unit_mode = False )
			)

		# Add silicide for P contact
		sil_bot_p = sil_offset_p - 0.5 * sil_width
		sil_top_p = sil_offset_p + 0.5 * sil_width
		self.add_rect(
			layer = self.params[ 'silicide_params' ][ 'layer' ],
			bbox = BBox( left = pd_left, bottom = sil_bot_p, right = pd_right, top = sil_top_p, resolution = self.grid.resolution, unit_mode = False )
			)
		
		# -----------------------------------------------------------------------
		# Draw electrodes on bottom metal connected by vias to polySi
		# See ringheater.py in Photonic_Core_Layout for an example of via use
		# -----------------------------------------------------------------------

		# Create the electrode via stacks
		via_stack_params = dict(
			top_layer = self.params[ 'electrode_params' ][ 'layer_top' ],
			bottom_layer = self.params[ 'electrode_params' ][ 'layer_bot' ],
			top_x_span = pd_length,
			top_y_span = sil_width,
			bottom_x_span = pd_length,
			bottom_y_span = sil_width,
			side_align = True,
		)

		via_stack_master = self.new_template( params = via_stack_params, temp_cls = ViaStack )

		# Place the via stacks
		pplus_via_stack = self.add_instance(
			master = via_stack_master,
			inst_name = 'pplus_via_stack',
			loc = ( pd_left, sil_offset_p ),
			orient = 'R0',
			unit_mode = False,
		)

		nplus_via_stack = self.add_instance(
			master = via_stack_master,
			inst_name = 'nplus_via_stack',
			loc = ( pd_left, sil_offset_n ),
			orient = 'R0',
			unit_mode = False,
		)		

		# Add electrode contact labels for P&R tools
		self.add_pin_primitive(
			net_name = self.params[ 'electrode_params' ][ 'label_pwell' ],
			layer = self.params[ 'electrode_params' ][ 'layer_top' ][ 0 ],
			bbox = pplus_via_stack.bound_box,
		)

		self.add_pin_primitive(
			net_name = self.params[ 'electrode_params' ][ 'label_nwell' ],
			layer = self.params[ 'electrode_params' ][ 'layer_top' ][ 0 ],
			bbox = nplus_via_stack.bound_box,
		)
					
		# Add photonic ports to the edges of the device
		self.draw_ports( pd_left, pd_right )	
	
	def draw_ports( self, port_xcoord_left, port_xcoord_right ):
	
		self.add_photonic_port(
			name = 'LEFT',
			orient = 'R0',
			center = ( port_xcoord_left, 0 ),
			width = self.params[ 'port_params' ][ 'width' ],
			layer = self.params[ 'port_params' ][ 'layer' ],
			resolution = self.grid.resolution,
			unit_mode = False,
			show = False )
		
		self.add_photonic_port(
			name = 'RIGHT',
			orient = 'R180',
			center = ( port_xcoord_right, 0 ),
			width = self.params[ 'port_params' ][ 'width' ],
			layer = self.params[ 'port_params' ][ 'layer' ],
			resolution = self.grid.resolution,
			unit_mode = False,
			show = False )


if __name__ == '__main__':
    spec_file = 'layout/LinearPDPolysilicon/specs/LinearPDPolysilicon_specs.yaml'
    PLM = BPG.PhotonicLayoutManager( spec_file )
    PLM.generate_content( )
    PLM.generate_gds( )
    PLM.dataprep_calibre( ) # Comment out for faster iteration
    #
    # PLM.generate_flat_content()
    # PLM.generate_lsf( )
    #
    # PLM.generate_flat_gds()
    # PLM.generate_flat_gds(debug=True, generate_gds=True)
    # PLM.dataprep()
