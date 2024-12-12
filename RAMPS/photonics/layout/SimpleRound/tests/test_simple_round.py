import BPG


def test_simple_round():
    spec_file = 'Photonic_Layout_45SPCLO/SimpleRound/specs/simple_round.yaml'
    plm = BPG.PhotonicLayoutManager(spec_file)
    plm.generate_content()
    plm.generate_gds()


test_simple_round()
