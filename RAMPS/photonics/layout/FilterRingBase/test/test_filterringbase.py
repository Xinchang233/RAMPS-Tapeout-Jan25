import BPG

def test():
    spec_file = 'layout/FilterRingBase/specs/specs.yaml'
    plm = BPG.PhotonicLayoutManager(spec_file)
    plm.generate_content()
    plm.generate_gds()
    #plm.generate_flat_content()
    #plm.generate_flat_gds()
    #plm.generate_lsf()

if __name__ == '__main__':
    test()
