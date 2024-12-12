# Runs RingHeater for 45RFSOI

import BPG

def test_ring_moscap():
    # 45RF spec file:
    spec_file = 'layout/Ring/specs/ring_moscap_specs.yaml'

    plm = BPG.PhotonicLayoutManager(spec_file)
    plm.generate_content()
    plm.generate_gds()
    plm.dataprep_calibre()


if __name__ == '__main__':
    test_ring_moscap()