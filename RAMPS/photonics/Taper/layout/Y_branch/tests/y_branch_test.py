# Runs linear taper with the 45RF layers

import BPG
from layout.Y_branch.Y_branch import Y_branch


def test_taper():
    # 45RF spec file:
    spec_file = 'layout/Y_branch/specs/y_branch_specs.yaml'

    plm = BPG.PhotonicLayoutManager(spec_file)
    plm.generate_content()
    plm.generate_gds()
    plm.dataprep_calibre()


if __name__ == '__main__':
    test_taper()
