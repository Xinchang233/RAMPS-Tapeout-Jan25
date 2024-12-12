import BPG


def test_loss_rings():
    spec_file = 'layout/LossRings/specs/lossring_variant7gc.yaml'  # parameter gds path in the spec file can be set to arbitrary value
    plm = BPG.PhotonicLayoutManager(spec_file)
    plm.generate_content()
    plm.generate_gds()
    # plm.generate_flat_content()
    # plm.generate_flat_gds()
    # plm.dataprep()
    # plm.generate_dataprep_gds()


if __name__ == '__main__':
    test_loss_rings()
