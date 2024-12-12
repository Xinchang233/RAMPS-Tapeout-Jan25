import BPG

def test():
    spec_file = 'layout/FilterArray_size2/specs/filter_array_cosine_size_2.yaml'
    plm = BPG.PhotonicLayoutManager(spec_file)
    plm.generate_content()
    plm.generate_gds()
    #plm.generate_flat_content()
    #plm.generate_flat_gds()
    #plm.dataprep()
    #plm.generate_dataprep_gds()
    #plm.generate_lsf()

if __name__ == '__main__':
    test()