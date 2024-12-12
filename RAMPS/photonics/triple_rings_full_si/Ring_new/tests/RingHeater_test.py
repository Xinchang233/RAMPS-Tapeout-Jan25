# Runs RingHeater for 45RFSOI

import BPG

def test_ringheater():
    # 45RF spec file:
    spec_file = 'layout/Ring_new/specs/ring_with_heater_specs.yaml'

    plm = BPG.PhotonicLayoutManager(spec_file)
    plm.generate_content()
    plm.generate_gds()
    plm.dataprep_calibre()


if __name__ == '__main__':
    test_ringheater()