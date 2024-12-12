import BPG
def test_loss_ring_array():
    spec_file = 'Photonic_Layout_45SPCLO/SimpleRing/specs/simple_ring.yaml'
    plm = BPG.PhotonicLayoutManager(spec_file)
    plm.generate_content()
    plm.generate_gds()
    plm.generate_flat_content()
    plm.generate_flat_gds()
    #plm.dataprep()
    #plm.generate_dataprep_gds()
    plm.dataprep_calibre()
test_loss_ring_array()

