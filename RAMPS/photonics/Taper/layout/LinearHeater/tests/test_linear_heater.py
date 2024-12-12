import BPG

def test_linear_heater():
    spec_file = 'layout/LinearHeater/specs/linear_heater.yaml'
    plm = BPG.PhotonicLayoutManager(spec_file)
    plm.generate_content()
    plm.generate_gds()
    plm.dataprep_calibre()

if __name__ == '__main__':
    test_linear_heater()