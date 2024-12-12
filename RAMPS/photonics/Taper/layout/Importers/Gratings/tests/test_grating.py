import BPG


def test_grating_wl1300nm_mfd5000nm():
    spec_file = 'layout/Importers/Gratings/specs/gc_bidir_wl1300nm_mfd5000nm.yaml'
    plm = BPG.PhotonicLayoutManager(spec_file)
    plm.generate_content()
    plm.generate_gds()


def test_grating_wl1300nm_mfd9200nm():
    spec_file = 'layout/Importers/Gratings/specs/gc_bidir_wl1300nm_mfd9200nm.yaml'
    plm = BPG.PhotonicLayoutManager(spec_file)
    plm.generate_content()
    plm.generate_gds()


def test_grating_wl1550nm_mfd5000nm():
    spec_file = 'layout/Importers/Gratings/specs/gc_bidir_wl1550nm_mfd5000nm.yaml'
    plm = BPG.PhotonicLayoutManager(spec_file)
    plm.generate_content()
    plm.generate_gds()


def test_grating_wl1550nm_mfd10400nm():
    spec_file = 'layout/Importers/Gratings/specs/gc_bidir_wl1550nm_mfd10400nm.yaml'
    plm = BPG.PhotonicLayoutManager(spec_file)
    plm.generate_content()
    plm.generate_gds()

if __name__ == '__main__':
    test_grating_wl1300nm_mfd5000nm()
    test_grating_wl1300nm_mfd9200nm()
    test_grating_wl1550nm_mfd5000nm()
    test_grating_wl1550nm_mfd10400nm()