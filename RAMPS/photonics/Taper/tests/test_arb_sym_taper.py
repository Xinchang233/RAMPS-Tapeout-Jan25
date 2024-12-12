"""
Arbitrary symmetric taper test cases

authors: bohan zhang
"""
import BPG

def test_arb_taper():
    """ Generate an arbitrary symmetric taper"""
    # points inside spec file
#    spec_file = 'Photonic_Core_Layout/Taper/specs/symmetric_taper.yaml'

    # load points from .mat file
    spec_file = 'Photonic_Layout_45SPCLO/Taper/specs/symmetric_taper_matfile.yaml'

    # generate gds and stuff
    plm = BPG.PhotonicLayoutManager(spec_file)
    plm.generate_content()
    plm.generate_gds()
#    plm.generate_flat_content()
#    plm.generate_flat_gds()
#    plm.generate_lsf()
    # end test_arb_taper()

if __name__ == '__main__':
    test_arb_taper()

