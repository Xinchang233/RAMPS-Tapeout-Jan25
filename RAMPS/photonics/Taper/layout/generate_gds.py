"""
A simple function that will run any spec file

You can call this from the command line, with the name of the spec file as the argument,
OR you can load the generate_gds() function into your own python code

@author: bohan
"""


# Dependencies

# BPG
import BPG

import sys

def generate_gds( spec_file ):
    """
    Given a spec file, generates gds files
    """   

    custom_dataprep_file = '/projectnb/siphot/chips/45RF_2019May/TO_45RF_2019May_infrastructure/GF45RFSOI/Photonics/dataprep_routine_custom.yaml'
    
    # generate stuff
    plm = BPG.PhotonicLayoutManager(spec_file)

    plm.generate_content()

    plm.generate_gds()
    plm.photonic_tech_info.dataprep_routine_filepath = custom_dataprep_file
    # plm.generate_flat_content()
    # plm.generate_flat_gds()

#    # generate dataprep'd gds
#    plm.dataprep()
#    plm.generate_dataprep_gds()


    plm.dataprep_calibre()

# end generate_gds()

if __name__=='__main__':

    generate_gds( sys.argv[1] )
    # generate_gds( '/projectnb/siphot/bz/git/TO_45RF_2019May/layout/Taper/specs/linear_taper_45rf.yaml' )
