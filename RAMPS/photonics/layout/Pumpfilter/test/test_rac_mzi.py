import BPG


def test_generic_mzi_site():
    spec_file = 'Photonic_Layout_45SPCLO/RACMZI/specs/rac_mzi.yaml'
    plm = BPG.PhotonicLayoutManager(spec_file)
    plm.generate_content()
    plm.generate_gds()
    #plm.generate_flat_content()
    #plm.generate_flat_gds()
    #plm.dataprep_calibre()
    #plm.generate_lsf()


if __name__ == '__main__':
    test_generic_mzi_site()
