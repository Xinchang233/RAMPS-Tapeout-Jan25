import BPG


def test_generic_mzi_site():
    spec_file = 'layout/Pumpfilter/specs/pumpfilters_example_twosourceandfilters.yaml'
    plm = BPG.PhotonicLayoutManager(spec_file)
    plm.generate_content()
    plm.generate_gds()
    #plm.generate_flat_content()
    #plm.generate_flat_gds()
    #plm.dataprep_calibre()
    #plm.generate_lsf()


if __name__ == '__main__':
    test_generic_mzi_site()
