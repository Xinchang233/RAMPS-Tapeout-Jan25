import BPG
from Photonic_Core_Layout.ViaStack.ViaStack import ViaStack
def test_viastack():
    spec_file = 'layout/RingTunable/specs/via_stack_specs.yaml'
    plm = BPG.PhotonicLayoutManager(spec_file)
    plm.generate_content()
    plm.generate_gds()
    #plm.generate_flat_content()
    #plm.generate_flat_gds()
    plm.dataprep_calibre()
test_viastack()