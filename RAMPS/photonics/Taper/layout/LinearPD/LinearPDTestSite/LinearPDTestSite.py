# This is a simple linear photodetector with SiGe implant in GF45RFSOI
# This class is written in a process-specific way, since we are taking advantage of the specific SiGe geometry

import BPG
from bag.layout.util import BBox
import importlib

# import subcomponents

from layout.GratingPlacer.GratingPlaceHolder import GratingPlaceHolder

from Photonic_Core_Layout.WaveguideBase.WgRouter import WgRouter
from layout.EQUIP.ViaStack.ViaStack import ViaStack

from layout.LinearPD.LinearPD.LinearPD import LinearPD
from layout.ProbePads.ProbePads import ProbePads

class LinearPDTestSite( BPG.PhotonicTemplateBase ):

	def __init__( self, temp_db, lib_name, params, used_names, **kwargs ):
		BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)

	@classmethod
	def get_default_param_values( cls ) -> dict:
		return dict(
			draw_pad_opening = True,
			pad_to_device_routing_layer = ( 'B3', 'drawing' )
		)

	@classmethod
	def get_params_info( cls ) -> dict:
		return dict(
			draw_pad_opening = 'passed to ProbePads, set to False if you want to remove the passivation yourself when you get the chip',
			pad_to_device_routing_layer = 'layer for routing from PDs to pads, must be above the top electrode layer of the PDs!'
		)

	def draw_layout( self ): # All WGs are 0.400um wide by default

		probepads_params = dict( # 50um GS probe pads			
			probe_pitch = 50.000,
			pad_to_pad_spacing = 10.000,
			num_pads = 2, # minimum = 1
			pad_labels = [ 'probe_pad_left', 'probe_pad_right' ],
			pad_metal_layer = ( 'LB', 'drawing' ), 
			pad_opening_layer = ( 'LV', 'drawing' ),
			draw_pad_opening = self.params[ 'draw_pad_opening' ]
		)

		linearpd_params = LinearPD.get_default_param_values( )
		
		linearpd_master = self.new_template( params = linearpd_params, temp_cls = LinearPD )
		grating_master = self.new_template( temp_cls = GratingPlaceHolder )
		probepads_master = self.new_template( params = probepads_params, temp_cls = ProbePads )
	
		# ----------------------------------------------------------------------
		# Create photonic test site for default geometry LinearPD
		# ----------------------------------------------------------------------
		
		# Draw a LinearPD with default geometry settings
		linearpd_inst = self.add_instance( 
			master = linearpd_master,
			loc = ( 0, 0 ),
			orient = 'R0'
		)

		# Add a grating coupler to the entry waveguide
		linearpd_grating_left_inst = self.add_instance_port_to_port(
			inst_master = grating_master,
			instance_port_name = 'PORT_OUT',
			self_port = linearpd_inst[ 'LEFT' ],
			reflect = False
		)

		# Add a grating coupler to the exit waveguide
		linearpd_grating_right_inst = self.add_instance_port_to_port(
			inst_master = grating_master,
			instance_port_name = 'PORT_OUT',
			self_port = linearpd_inst[ 'RIGHT' ],
			reflect = False
		)

		# ----------------------------------------------------------------------
		# Place GS probe pads below LinearPD
		# ----------------------------------------------------------------------

		# Add GS probe pads
		linearpd_inst_loc_x = linearpd_inst.location[0]
		linearpd_inst_loc_y = linearpd_inst.location[1]

		linearpd_probepads = self.add_instance(
			master = probepads_master,
			loc = [ linearpd_inst_loc_x, linearpd_inst_loc_y - 0.5 * probepads_params[ 'probe_pitch' ] ],
			orient = 'R0'
		)

		pad_via_bottom_layer = self.params[ 'pad_to_device_routing_layer' ]
		pad_via_top_layer = probepads_params[ 'pad_metal_layer' ]

		linearpd_via_bottom_layer = linearpd_params[ 'electrode_layer_top' ]
		linearpd_via_top_layer = pad_via_bottom_layer

		# ----------------------------------------------------------------------
		# Wire the left probe pad (G) to the anode (pwell contact)
		# ----------------------------------------------------------------------

		# Find the bbox of the pad's pin_primitive and set the via stack dimensions accordingly
		pad_port_left = linearpd_probepads.get_port( 'probe_pad_left' )
		pad_bbox_left = pad_port_left.get_bounding_box( self.grid.resolution )

		via_stack_pad_left_params = dict(
			top_layer = pad_via_top_layer,
			bottom_layer = pad_via_bottom_layer,
			top_x_span = pad_bbox_left.width,
			top_y_span = pad_bbox_left.height,
			bottom_x_span = pad_bbox_left.width,
			bottom_y_span = pad_bbox_left.height,
			side_align = False, # center align
		)

		via_stack_pad_left_master = self.new_template( params = via_stack_pad_left_params, temp_cls = ViaStack )

		via_stack_pad_left_loc = [ pad_bbox_left.left + pad_bbox_left.width / 2, pad_bbox_left.bottom + pad_bbox_left.height / 2 ]  # is there a more-elegant way?

		via_stack_pad_left_inst = self.add_instance(
			master=via_stack_pad_left_master,
			inst_name='pad_right_via_stack',
			loc=via_stack_pad_left_loc,
			orient='R0',
			unit_mode=False,
		)

		# Find the bbox of the linearpd's pin_primitive and set the via stack dimensions accordingly
		linearpd_port_anode = linearpd_inst.get_port( 'anode' )
		linearpd_bbox_anode = linearpd_port_anode.get_bounding_box( self.grid.resolution )

		linearpd_anode_loc = [ linearpd_bbox_anode.left + linearpd_bbox_anode.width / 2, linearpd_bbox_anode.bottom + linearpd_bbox_anode.height / 2 ] # is there a more-elegant way?

		via_stack_linearpd_anode_params = dict(
			top_layer = linearpd_via_top_layer,
			bottom_layer = linearpd_via_bottom_layer,
			top_x_span = linearpd_bbox_anode.width / 4,
			top_y_span = linearpd_bbox_anode.height,
			bottom_x_span = linearpd_bbox_anode.width / 4,
			bottom_y_span = linearpd_bbox_anode.height,
			side_align = False, # center align
		)

		via_stack_linearpd_anode_master = self.new_template( params = via_stack_linearpd_anode_params, temp_cls = ViaStack )

		via_stack_linearpd_anode_loc = [ via_stack_pad_left_loc[ 0 ], linearpd_anode_loc[ 1 ] ]

		via_stack_linearpd_anode_inst = self.add_instance(
			master = via_stack_linearpd_anode_master,
			inst_name = 'linearpd_anode_via_stack',
			loc = via_stack_linearpd_anode_loc,
			orient = 'R0',
			unit_mode = False
		)

		# Set the wire x-dimensions based on the actual size of the bottom rectangle in the via stack (which is automatically set based on the design rules)
		wire_anode = self.add_rect(
			layer = self.params[ 'pad_to_device_routing_layer' ],
			bbox = BBox(
				left 		= via_stack_pad_left_master.enclosure_list[ 0 ][ 'rect' ].bbox.left + via_stack_pad_left_loc[ 0 ], #pad_bbox_left.left,
				bottom 		= pad_bbox_left.bottom,
                right 		= via_stack_pad_left_master.enclosure_list[ 0 ][ 'rect' ].bbox.right + via_stack_pad_left_loc[ 0 ], #pad_bbox_left.right,
                top 		= linearpd_bbox_anode.top,
                resolution 	= self.grid.resolution,
                unit_mode 	= False
			)
		)

		# ----------------------------------------------------------------------
		# Wire the right probe pad (S) to the kathode (nwell contact)
		# ----------------------------------------------------------------------

		# Find the bbox of the pin_primitive of the pad and set the via stack dimensions accordingly
		pad_port_right = linearpd_probepads.get_port( 'probe_pad_right' )
		pad_bbox_right = pad_port_right.get_bounding_box( self.grid.resolution )

		via_stack_pad_right_params = dict(
			top_layer = pad_via_top_layer,
			bottom_layer = pad_via_bottom_layer,
			top_x_span = pad_bbox_right.width,
			top_y_span = pad_bbox_right.height,
			bottom_x_span = pad_bbox_right.width,
			bottom_y_span = pad_bbox_right.height,
			side_align = False,
		)

		via_stack_pad_right_master = self.new_template( params = via_stack_pad_right_params, temp_cls = ViaStack )

		via_stack_pad_right_loc = [ pad_bbox_right.left + pad_bbox_right.width / 2, pad_bbox_right.bottom + pad_bbox_right.height / 2 ] # is there a more-elegant way?

		via_stack_pad_right_inst = self.add_instance(
			master = via_stack_pad_right_master,
			inst_name = 'pad_right_via_stack',
			loc = via_stack_pad_right_loc,
			orient = 'R0',
			unit_mode = False,
		)

		# Find the bbox of the linearpd's pin_primitive and set the via stack dimensions accordingly
		linearpd_port_kathode = linearpd_inst.get_port( 'kathode' )
		linearpd_bbox_kathode = linearpd_port_kathode.get_bounding_box( self.grid.resolution )

		linearpd_kathode_loc = [linearpd_bbox_kathode.left + linearpd_bbox_kathode.width / 2, linearpd_bbox_kathode.bottom + linearpd_bbox_kathode.height / 2]  # is there a more-elegant way?

		via_stack_linearpd_kathode_params = dict(
			top_layer = linearpd_via_top_layer,
			bottom_layer = linearpd_via_bottom_layer,
			top_x_span = linearpd_bbox_anode.width / 4,
			top_y_span = linearpd_bbox_anode.height,
			bottom_x_span = linearpd_bbox_anode.width / 4,
			bottom_y_span = linearpd_bbox_anode.height,
			side_align = False,  # center align
		)

		via_stack_linearpd_kathode_master = self.new_template( params = via_stack_linearpd_kathode_params, temp_cls = ViaStack )

		via_stack_linearpd_kathode_loc = [ via_stack_pad_right_loc[ 0 ], linearpd_kathode_loc[ 1 ] ]

		via_stack_linearpd_kathode_inst = self.add_instance(
			master = via_stack_linearpd_kathode_master,
			inst_name = 'linearpd_kathode_via_stack',
			loc = via_stack_linearpd_kathode_loc,
			orient = 'R0',
			unit_mode = False
		)

		# Set the wire x-dimensions based on the actual size of the bottom rectangle in the via stack (which is automatically set based on the design rules)
		wire_kathode = self.add_rect(
			layer = self.params['pad_to_device_routing_layer'],
			bbox = BBox(
				left 		= via_stack_pad_right_master.enclosure_list[ 0 ][ 'rect' ].bbox.left + via_stack_pad_right_loc[ 0 ], #pad_bbox_right.left,
				bottom 		= pad_bbox_right.bottom,
				right 		= via_stack_pad_left_master.enclosure_list[ 0 ][ 'rect' ].bbox.right + via_stack_pad_right_loc[ 0 ], #pad_bbox_right.right,
				top 		= linearpd_bbox_kathode.top,
				resolution 	= self.grid.resolution,
				unit_mode 	= False
			)
		)

		# ----------------------------------------------------------------------
		# Cut-back test waveguides and gratings (commented out and moved to separate file)
		# ----------------------------------------------------------------------

		# left_grating_xcoord = linearpd_grating_left_inst.location[0]
		#
		# cutback_test_lengths = [ 100, 70, 40 ]
		# cutback_test_vert_spacing = 15
		#
		# for index in range( len( cutback_test_lengths ) ):
		# 	# Add cut-back test left grating
		# 	cutback_grating_left_inst = self.add_instance(
		# 		master = grating_master,
		# 		loc = ( left_grating_xcoord, ( index + 1 ) * cutback_test_vert_spacing ),
		# 		orient = 'R180'
		# 	)
		#
		# 	# Route cut-back test WG
		# 	router_start_port = cutback_grating_left_inst[ 'INPUT' ]
		#
		# 	cutback_router = WgRouter( gen_cls = self,
		# 		init_port = router_start_port,
		# 		layer = ( router_start_port.layer[ 0 ], 'drawing' )
		# 	)
		#
		# 	cutback_router.add_straight_wg( length = cutback_test_lengths[ index ] )
		#
		# 	# Add the right grating to the end of the WG
		# 	cutback_grating_right_inst = self.add_instances_port_to_port(
		# 		inst_master = grating_master,
		# 		instance_port_name = 'INPUT',
		# 		self_port = cutback_router.port
		# 	)
		
		

if __name__ == '__main__':
    spec_file = 'layout/LinearPD/LinearPDTestSite/specs/LinearPDTestSite_specs.yaml'
    PLM = BPG.PhotonicLayoutManager( spec_file )
    PLM.generate_content( )
    PLM.generate_gds( )
    PLM.dataprep_calibre( ) # Comment out for faster iteration
    
    PLM.generate_flat_content()
    PLM.generate_lsf( )
    
    # PLM.generate_flat_gds()
    # PLM.generate_flat_gds(debug=True, generate_gds=True)
    # PLM.dataprep()
