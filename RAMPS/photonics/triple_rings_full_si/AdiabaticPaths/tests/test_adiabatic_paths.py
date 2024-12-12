import BPG


def test_adaiabatic_paths():
    spec_file = 'Photonic_Core_Layout/AdiabaticPaths/specs/specs.yaml'
    plm = BPG.PhotonicLayoutManager(spec_file)
    plm.generate_content()
    plm.generate_gds()
    plm.generate_flat_content()
    plm.generate_flat_gds()


test_adaiabatic_paths()
