# Runs linear taper with the 45RF layers

import BPG
from Photonic_Core_Layout.Taper.LinearTaper import LinearTaper


def test_taper():
    # 45RF spec file:
    spec_file = 'layout/Taper/specs/linear_taper_45rf.yaml'
    
    plm = BPG.PhotonicLayoutManager(spec_file)
    plm.generate_content()
    plm.generate_gds()
    plm.dataprep_calibre()


if __name__ == '__main__':
    test_taper()
