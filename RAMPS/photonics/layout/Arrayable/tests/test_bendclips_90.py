import BPG
def test_loss_ring_array():
    spec_file = 'Photonic_Layout_45SPCLO/Arrayable/specs/bend_90.yaml'
    plm = BPG.PhotonicLayoutManager(spec_file)
    plm.generate_content()
    plm.generate_gds()



test_loss_ring_array()

