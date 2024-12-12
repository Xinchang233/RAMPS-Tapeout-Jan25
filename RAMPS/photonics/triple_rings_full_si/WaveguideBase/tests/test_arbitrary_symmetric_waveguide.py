import BPG


def test_ridge_arbitrary_ridge_waveguide():
    spec_file = 'Photonic_Core_Layout/WaveguideBase/specs/arbitrary_symmetric_waveguide.yaml'
    plm = BPG.PhotonicLayoutManager(spec_file)
    plm.generate_content()
    plm.generate_flat_content()
    plm.generate_flat_gds()
    # plm.generate_lsf()


if __name__ == '__main__':
    test_ridge_arbitrary_ridge_waveguide()