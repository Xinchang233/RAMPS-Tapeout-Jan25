# mostly for testing custom partial etch wg in clo dataprep

# annoying python path imports
import sys
import os
sys.path.insert( 0, os.getcwd() + '/BPG' )

import BPG

def test_taper():
    # CLO spec file:
    spec_file = 'Photonic_Layout_45SPCLO/Taper/specs/linear_taper_clo_paretch.yaml'
    
    # everything else is the same
    plm = BPG.PhotonicLayoutManager(spec_file)
    plm.generate_content()
    plm.generate_gds()
    plm.generate_flat_content()
    plm.generate_flat_gds()
    plm.generate_lsf()

    # generate dataprep'd gds
    plm.dataprep()
    plm.generate_dataprep_gds()

if __name__ == '__main__':
    test_taper()
