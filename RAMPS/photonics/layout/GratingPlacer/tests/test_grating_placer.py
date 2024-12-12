import BPG


def test_grating_placer():
    spec_file = 'layout/GratingPlacer/specs/grating_placer.yaml'
    plm = BPG.PhotonicLayoutManager(spec_file)
    plm.generate_content()
    plm.generate_gds()
    # plm.generate_flat_content()
    # plm.generate_flat_gds()


# plm.dataprep_calibre()

if __name__ == "__main__":
    test_grating_placer()
