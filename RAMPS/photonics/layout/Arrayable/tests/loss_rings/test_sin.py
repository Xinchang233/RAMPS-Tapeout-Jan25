import BPG

def test_loss_ring_array():
    spec_file = 'Photonic_Layout_45SPCLO/Arrayable/specs/loss_rings/sin.yaml'
    plm = BPG.PhotonicLayoutManager(spec_file)
    plm.generate_content()
    plm.generate_gds()
    #plm.generate_flat_content()
    #plm.generate_flat_gds()
    plm.dataprep_calibre()

if __name__ == "__main__":
    test_loss_ring_array()
