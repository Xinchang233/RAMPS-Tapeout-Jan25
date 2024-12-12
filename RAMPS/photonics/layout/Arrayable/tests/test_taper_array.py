import BPG

def test_grating_array():
    # CLO spec file:
    spec_file = 'Photonic_Layout_45SPCLO/Arrayable/specs/grating_array.yaml'
    plm = BPG.PhotonicLayoutManager(spec_file)
    plm.generate_content()
    plm.generate_gds()
    plm.generate_flat_content()
    plm.generate_flat_gds()
    plm.generate_lsf()


if __name__ == '__main__':
    test_grating_array()
