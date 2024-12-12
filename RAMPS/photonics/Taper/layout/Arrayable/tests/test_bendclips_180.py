import BPG
def test_loss_ring_array():
    spec_file = 'Photonic_Layout_45SPCLO/Arrayable/specs/bend_180.yaml'
    plm = BPG.PhotonicLayoutManager(spec_file)
    plm.generate_content()
    plm.generate_gds()
    # plm.generate_flat_content()
    # plm.generate_flat_gds()
    # plm.dataprep()
    # plm.generate_dataprep_gds()


test_loss_ring_array()

