import BPG

def make_y_branch():
    spec_file = 'layout/Ybranch/specs/ybranch_S3_design_final.yaml'
    plm = BPG.PhotonicLayoutManager(spec_file)
    plm.generate_content()
    plm.generate_gds()
   # plm.dataprep_calibre()


if __name__ == '__main__':
    make_y_branch()

