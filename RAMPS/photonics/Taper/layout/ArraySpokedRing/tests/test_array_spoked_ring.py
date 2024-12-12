import BPG

if __name__ == '__main__':
    spec_file = '/projectnb/siphot/djordje/TO_45RF_2019May/layout/ArraySpokedRing/specs/array_spoked_ring2.yaml'
    plm = BPG.PhotonicLayoutManager(spec_file)
    plm.generate_content()
    plm.generate_gds()
    plm.dataprep_calibre()