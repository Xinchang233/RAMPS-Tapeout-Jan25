"""
An example of how to load custom grating couplers into your design
"""

import BPG

# Import the grating class you want to use
# lambda = 1300nm, MFD = 9.2 um, output angle = +15 deg, uniform bidirectional body interfacing grating
from Photonic_Layout_45SPCLO.GratingCoupler.WorkhorseGratings import GC_WL1300_MFD9200nm_15DEG

# linear taper for wg
from Photonic_Core_Layout.Taper.LinearTaper import LinearTaper

# python debugger
import pdb

class example_grating_usage( BPG.PhotonicTemplateBase ):
	"""
	Draws a simple waveguide, connects a grating cell (cell = grating + taper) to it
	"""

	def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
		BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)


	def draw_layout(self):

		# add the grating
		# notice that params is empty
		self.grating_template = self.new_template( params = {}, temp_cls = GC_WL1300_MFD9200nm_15DEG )
		self.grating_instance = self.add_instance( self.grating_template, loc=(0.0, 0.0) )

		# get the output port from the grating
		self.extract_photonic_ports(
            inst = self.grating_instance,
            show = False,
            port_names = [ 'PORT_OUT' ],
        )

		# connect a waveguide
		wg_params 	= { 'layer': ( 'si_full', 'drawing' ),
						'width0': self.grating_instance['PORT_OUT'].width,
						'width1': self.grating_instance['PORT_OUT'].width,
						'length': 100.0 }
        wg_template = self.new_template( params = wg_params, temp_cls = LinearTaper )
        self.wg 	= self.add_instances_port_to_port(inst_master=wg_template,
                                                   instance_port_name='PORT0',
                                                   self_port_name='PORT_OUT'
                                                   )

	# end draw_layout()

# end class example_grating_usage


# Main
if __name__ == '__main__':
	
	# generate stuff
    plm = BPG.PhotonicLayoutManager(spec_file)
    plm.generate_content()
    plm.generate_gds()