import BPG


def test_arrayable():
    spec_file = 'Photonic_Layout_45SPCLO/Arrayable/specs/specs.yaml'
    plm = BPG.PhotonicLayoutManager(spec_file)
    plm.generate_content()
    plm.generate_flat_content()
    plm.generate_flat_gds()


test_arrayable()
