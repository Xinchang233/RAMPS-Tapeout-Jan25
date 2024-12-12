import BPG

def test_dual_layer_contacted_slot_waveguide():
    spec_file = 'layout/WaveguidePhaseShifter/specs/waveguide_phase_shifter.yaml'
    plm = BPG.PhotonicLayoutManager(spec_file)
    plm.generate_content()
    plm.generate_gds()
    plm.generate_flat_content()
    plm.generate_flat_gds()
    # plm.generate_lsf()

if __name__ == '__main__':
    test_dual_layer_contacted_slot_waveguide()