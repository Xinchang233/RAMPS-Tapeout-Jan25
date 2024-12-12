# Runs RingHeater for 45RFSOI

import BPG

def test_ringsensableclipp():
    # 45RF spec file:
    spec_file = 'layout/RingSensable/specs/ringsensable_clipp.yaml'

    plm = BPG.PhotonicLayoutManager(spec_file)
    plm.generate_content()
    plm.generate_gds()
    plm.dataprep_calibre()
    # plm.generate_flat_content()
    # plm.generate_lsf()

if __name__ == '__main__':
    test_ringsensableclipp()