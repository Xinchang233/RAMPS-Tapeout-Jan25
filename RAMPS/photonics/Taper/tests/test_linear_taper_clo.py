# Runs linear taper with the 45RF layers

import os
print(os.getcwd())

import BPG
#from Photonic_Core_Layout.Taper.LinearTaper import LinearTaper

# DEBUG importing os
import os

def test_taper():
    # CLO spec file:
    spec_file = 'Photonic_Layout_45SPCLO/Taper/specs/linear_taper_clo.yaml'
    
    # everything else is the same
    plm = BPG.PhotonicLayoutManager(spec_file)
    plm.generate_content()
    plm.generate_gds()
    plm.generate_flat_content()
    plm.generate_flat_gds()
    plm.dataprep()
    plm.generate_dataprep_gds()
    plm.generate_lsf()

    # generate dataprep'd gds
    plm.dataprep()
    plm.generate_dataprep_gds()

if __name__ == '__main__':
    test_taper()

    print(os.getcwd())
