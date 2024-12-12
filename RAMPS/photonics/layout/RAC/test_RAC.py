import BPG
import os

def test_rac():
    spec_file = 'layout/RAC/rac_test.yaml'

    plm = BPG.PhotonicLayoutManager(spec_file)
    plm.generate_content()
    plm.generate_gds()
    #plm.dataprep_calibre()


if __name__ == '__main__':
    test_rac()

