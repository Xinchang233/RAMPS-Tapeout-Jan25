import BPG


def test_taper():
    # 45RF spec file:
    spec_file = 'layout/Y_branch/specs/y_mirror.yaml'

    plm = BPG.PhotonicLayoutManager(spec_file)
    plm.generate_content(save_content=False)
    plm.generate_gds()

    # plm = BPG.PhotonicLayoutManager(spec_file)
    # plm.generate_content()
    # plm.generate_gds()
    # plm.dataprep_calibre()


if __name__ == '__main__':
    test_taper()
