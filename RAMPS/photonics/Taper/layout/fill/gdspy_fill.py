"""
author: bohan

loads a .gds adds fill
"""

# -----------------------------------------------------------
# Dependencies

import gdspy

# os
import os
import sys

# for timing code
import time

# python debugger
import pdb
import pprint

# -----------------------------------------------------------
# Methods

def add_fill( gds_filename ):
	"""
	Adds PC fill to gds
	now adds B1, B2, and B3 too
	"""

	starttime = time.time()

	# print(gdspy.__version__)

	# pprint(gdspy.__dir__)

	# load a gds
	gds_filename = '/projectnb/siphot/hayk/BPG_hayk/TO_45RF_2019May/gen_libs/HorizontalArray/data/slot_racetrack_set2_dataprep_calibre.gds'
	gds = gdspy.GdsLibrary( infile=gds_filename )

	# grab the top level cell
	topcell = gds.top_level()[0]

	# get polygons with specified layer
	all_polygons 		= topcell.get_polygons( by_spec = True )
	layer 				= (7, 2) 	# PC exclude
	pcexclude_polygons 	= all_polygons[ layer ] 	# using PC EXCLUDE layer to generate all the fills

	# try scaling it
	add_size = 8.0
	fill_region = gdspy.offset( polygons = pcexclude_polygons, 
												distance = add_size,
												join = 'miter',
												join_first = True,
												layer = 9999,
												datatype = 9999)

	# fill size
	fill_width 	= 100.0;
	fill_height = 2.0;
	fill_space 	= 0.6;

	# get bounding box
	fill_region_box = fill_region.get_bounding_box()

	origin 		= fill_region_box[0]
	end_coord 	= fill_region_box[1]

	# bottom left coordinates of the rectangle
	cur_x = origin[0]
	cur_y = origin[1]

	# fillcell = gdspy.Cell('pc_fill')

	ii = 0
	predicted_rowloops = round( (end_coord[1] - origin[1])/(fill_height+fill_space) )
	while cur_y < end_coord[1]:

		# draw the pc rectangle
		rect = gdspy.Rectangle( point1 		= (cur_x,cur_y), point2 = (cur_x+fill_width, cur_y+fill_height), 
								layer 		= layer[0],
								datatype 	= 0 )

		# check if rectangle should be added
		# if (gdspy.fast_boolean( rect, fill_region, 'and' ) is not None) and (gdspy.fast_boolean( rect, pcexclude_polygons, 'and' ) is None):
		# 	topcell.add( rect )
		if (gdspy.fast_boolean(rect, pcexclude_polygons, 'and') is None):
			topcell.add(rect)

			# draw the rx rectangle
			topcell.add( gdspy.Rectangle( point1 		= (cur_x,cur_y), point2 = (cur_x+fill_width, cur_y+fill_height), 
									layer 		= 2,
									datatype 	= 0 ) )

			# draw the b1 rectangle
			topcell.add( gdspy.Rectangle( point1 		= (cur_x,cur_y), point2 = (cur_x+fill_width, cur_y+fill_height), 
									layer 		= 79,
									datatype 	= 100 ) )

			# draw the b2 rectangle
			topcell.add( gdspy.Rectangle( point1 		= (cur_x,cur_y), point2 = (cur_x+fill_width, cur_y+fill_height), 
									layer 		= 81,
									datatype 	= 100 ) )

			# draw the b3 rectangle
			topcell.add( gdspy.Rectangle( point1 		= (cur_x,cur_y), point2 = (cur_x+fill_width, cur_y+fill_height), 
									layer 		= 83,
									datatype 	= 100 ) )

			# add B1
			# topcell.add( rect )

		# end if
		
		# move x
		cur_x += fill_width + fill_space

		# check if end of row
		if cur_x + fill_width + fill_space > end_coord[0]:
			ii+=1
			cur_x = origin[0]
			cur_y += fill_height + fill_space
			print('loop ' + str(ii) + ' of ' + str(predicted_rowloops))
			print('elapsed time ' + str(time.time() - starttime))

	# end while

	# add fillcell to gds
	# gds.add(fillcell)

	# write to file
	load_filename_dir 	= os.path.split( gds_filename )
	new_filename  		= load_filename_dir[1].replace( '.gds', 'fillgen.gds' )
	save_filename 		= load_filename_dir[0] + '/' + new_filename
	gds.write_gds(save_filename, cells=[topcell])
# end add_fill()

# -----------------------------------------------------------
# Main

if __name__=='__main__':
	"""
	To run from command line, run:
	python gdspy_fill.py your_filename
	"""
	add_fill('')


	# # write a cell and draw it
	# cell = gdspy.Cell('TEST')
	# cell.add(pcexclude_polygons_scaled)
	# gdspy.write_gds('lol.gds')

	# # try a boolean
	# rect 	= gdspy.Rectangle( (-1000,-1000), (-999,-999) )
	# result 	= gdspy.fast_boolean( rect, pcexclude_polygons, 'and' )

	# pprint.pprint(result.polygons)

	# pdb.set_trace()