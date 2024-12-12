# Last updated 5/29/2019

import BPG
from bag.layout.util import BBox
import importlib
from Photonic_Core_Layout.ViaStack.ViaStack import ViaStack

class ProbePads( BPG.PhotonicTemplateBase ):

	def __init__( self, temp_db, lib_name, params, used_names, **kwargs ):
		BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)

	@classmethod
	def get_default_param_values( cls ) -> dict:
		return dict(				
			probe_pitch = 50.000,
			pad_to_pad_spacing = 10.000,
			num_pads = 2, # minimum = 1
			pad_labels = [ 'probe_pad_left', 'probe_pad_right' ],
			pad_metal_layer = ( 'LB', 'drawing' ), 
			pad_opening_layer = ( 'LV', 'drawing' ),
			draw_pad_opening = True
		)

	@classmethod
	def get_params_info( cls ) -> dict:
		return dict(
			probe_pitch = 'Pitch between probe tips (typically 50, 100, or 150um)',
			pad_to_pad_spacing = 'Clearance between pads, this along with pitch sets the pad edge length, since we use square pads',
			num_pads = 'number of pads in the array (GS is 2, GSG is 3, etc)',
			pad_labels = 'names of the pads from left to right',
			pad_metal_layer = 'layer of top metal that the pads are on',
			pad_opening_layer = 'layer used to draw the passivation opening over the pad',
			draw_pad_opening = 'determines whether a pad opening should be drawn -- might want it False if you want to manually remove passivation over test structures and otherwise solder flip-chip'
		)	

	def draw_layout( self ):
		
		# -----------------------------------------------------------------------	
		# Calculate device geometry parameters
		# -----------------------------------------------------------------------

		probe_pitch = self.params[ 'probe_pitch' ]
		num_pads = self.params[ 'num_pads' ]

		pad_edge = probe_pitch - self.params[ 'pad_to_pad_spacing' ]
		
		# Set pad center locations so that origin is at the centeroid of the pad array
		pad_x_locs = list( )
		pad_x_start = -1 * probe_pitch * ( num_pads - 1 ) / 2
		for index in range( num_pads ):
			pad_x_locs.append( pad_x_start + index * probe_pitch )
		
		# -----------------------------------------------------------------------
		# Draw main device geometry
		# -----------------------------------------------------------------------
		
		pad_metal_layer = self.params[ 'pad_metal_layer' ]
		pad_opening_layer = self.params[ 'pad_opening_layer' ]

		for index in range( num_pads ):
			print( index )
			x_loc = pad_x_locs[ index ]
			
			# draw metal pad
			pad_inst = self.add_rect(
				layer = pad_metal_layer,
				bbox = BBox(
					left 		= x_loc - pad_edge / 2,
					bottom 		= -1 * pad_edge / 2,
                	right 		= x_loc + pad_edge / 2,
                	top 		= pad_edge / 2,
                	resolution 	= self.grid.resolution,
                	unit_mode 	= False
				)
			)

			# New way: add pin primitive for desired connection point (top/middle of electrode)
			self.add_pin_primitive(
				net_name = self.params[ 'pad_labels' ][ index ],
				layer = pad_metal_layer[ 0 ],
				bbox = BBox(
					left 		= x_loc - pad_edge / 4,
					bottom 		= pad_edge / 4,
                	right 		= x_loc + pad_edge / 4,
                	top 		= pad_edge / 2,
                	resolution 	= self.grid.resolution,
                	unit_mode 	= False
				)
			)

			# Old way: add electrode contact label
			#self.add_label(
			#	label = self.params[ 'pad_labels' ][ index ],
			#	layer = pad_metal_layer[0],
			#	bbox = pad_inst.bound_box,
			#)

			# draw pad opening
			opening_inst = self.add_rect( layer = pad_opening_layer,
				bbox = BBox( left = x_loc - pad_edge / 2,
					bottom = -1 * pad_edge / 2,
                	                right = x_loc + pad_edge / 2,
                	                top = pad_edge / 2, 
                	                resolution = self.grid.resolution,
                	                unit_mode = False )
			)


if __name__ == '__main__':
    spec_file = 'quantum_photon_pair_generator/photonics/ProbePads/specs/ProbePads_specs.yaml'
    PLM = BPG.PhotonicLayoutManager( spec_file )
    PLM.generate_content( )
    PLM.generate_gds( )
    #PLM.dataprep_calibre( ) # Comment out for faster iteration
    
    PLM.generate_flat_content()
    PLM.generate_lsf( )
    
    # PLM.generate_flat_gds()
    # PLM.generate_flat_gds(debug=True, generate_gds=True)
    # PLM.dataprep()
