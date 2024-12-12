# Runs RingHeater for 45RFSOI

import BPG

def test_ringtunable():
    # 45RF spec file:
    spec_file = 'layout/RingTunable/specs/ringtunable.yaml'

    plm = BPG.PhotonicLayoutManager(spec_file)
    plm.generate_content()
    plm.generate_gds()
    plm.dataprep_calibre()


if __name__ == '__main__':
    test_ringtunable()