import BPG

def test_taper():
    # 45RF spec file:
    spec_file = 'layout/General_taper/specs/general_taper.yaml'

    plm = BPG.PhotonicLayoutManager(spec_file)
    plm.generate_content()
    plm.generate_gds()
    plm.dataprep_calibre()


if __name__ == '__main__':
    test_taper()
