import BPG
import timeit


def gen_moscap_set():
    for count in range(1, 3):
        spec_file = 'layout/HorizontalArray/specs/moscap_set_0'+str(count)+'.yaml'
        plm = BPG.PhotonicLayoutManager(spec_file)
        plm.generate_content()
        plm.generate_gds()
        plm.dataprep_calibre()

start = timeit.default_timer()
gen_moscap_set()
stop = timeit.default_timer()

print('Time: ', stop - start)
