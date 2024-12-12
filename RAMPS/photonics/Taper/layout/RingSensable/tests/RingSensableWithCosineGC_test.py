# Runs RingHeater for 45RFSOI

import BPG

def test_ringsensable_dummy():
    # 45RF spec file:
    #spec_file = 'layout/RingSensable/specs/ring_sensable.yaml'
    spec_file='layout/RingSensable/specs/sourcering_variant3gc.yaml'

    plm = BPG.PhotonicLayoutManager(spec_file)
    plm.generate_content()
    plm.generate_gds()
    plm.dataprep_calibre()
    #plm.generate_flat_content()
    #plm.generate_lsf()

if __name__ == '__main__':
    test_ringsensable_dummy()