# Runs sourceandfilters for 45RFSOI

import BPG

def test_sourceandfilters():
    # 45RF spec file:
    spec_file = '/projectnb/siphot/imbert/bpg/TO_45RF_2019May/layout/sourceandfilters/specs/sourceandfilters_example_fixed.yaml'

    plm = BPG.PhotonicLayoutManager(spec_file)
    plm.generate_content()
    plm.generate_gds()
    #plm.dataprep_calibre()

if __name__ == '__main__':
    test_sourceandfilters()
