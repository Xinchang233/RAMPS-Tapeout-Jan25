import BPG

if __name__ == '__main__':
    spec_file = '/projectnb/siphot/djordje/TO_45RF_2019May/layout/Arrayed_Moscap/specs/Arrayed_Moscap.yaml'
    plm = BPG.PhotonicLayoutManager(spec_file)
    plm.generate_content()
    plm.generate_gds()
    plm.dataprep_calibre()
