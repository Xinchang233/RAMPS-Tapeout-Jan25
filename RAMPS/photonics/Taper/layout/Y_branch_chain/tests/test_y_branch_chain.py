import BPG

def test_taper():
    # 45RF spec file:
    spec_file = 'layout/Y_branch_chain/specs/y_branch_chain.yaml'

    plm = BPG.PhotonicLayoutManager(spec_file)
    plm.generate_content()
    plm.generate_gds()
    plm.dataprep_calibre()


if __name__ == '__main__':
    test_taper()
