# Runs sourceandfilters for 45RFSOI

import BPG

def test_sourceandfilters6thorder_ringsensable():
    # 45RF spec file:
    spec_file = '/projectnb/siphot/imbert/bpg/TO_45RF_2019May/layout/sourceandfilters/specs/sourceandfilter6thorder_ringsensable.yaml'

    plm = BPG.PhotonicLayoutManager(spec_file)
    plm.generate_content()
    plm.generate_gds()
    plm.dataprep_calibre()

if __name__ == '__main__':
    test_sourceandfilters6thorder_ringsensable()
