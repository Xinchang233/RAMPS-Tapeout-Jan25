import BPG
import timeit

start = timeit.default_timer()

def gen_slot_set():
    for count in range(1, 7):
        spec_file = 'layout/HorizontalArray/specs/slot_racetrack_set'+str(count)+'.yaml'
        plm = BPG.PhotonicLayoutManager(spec_file)
        plm.generate_content()
        plm.generate_gds()
        plm.dataprep_calibre()

gen_slot_set()

stop = timeit.default_timer()

print('Time: ', stop - start)
