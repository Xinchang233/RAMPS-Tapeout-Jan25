import BPG

def test_grating_place_holder():
    spec_file = 'Photonic_Layout_45SPCLO/GratingPlacer/specs/grating_place_holder.yaml'
    plm = BPG.PhotonicLayoutManager(spec_file)
    plm.generate_content()
    plm.generate_gds()
    # plm.generate_flat_content()
    # plm.generate_flat_gds()


if __name__ == "__main__":
    test_grating_place_holder()