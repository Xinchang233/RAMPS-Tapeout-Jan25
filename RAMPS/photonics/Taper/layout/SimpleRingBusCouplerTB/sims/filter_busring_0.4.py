from BPG.lumerical.design_manager import LumericalDesignManager
from copy import deepcopy

if __name__ == '__main__':
    spec_file = 'layout/SimpleRingBusCouplerTB/specs/filter_busring_0.4.yaml'
    dsn = LumericalDesignManager(spec_file)

    gap_test_list = [0.05, 0.075, 0.1, 0.15, 0.2, 0.25, 0.3, 0.4]

    for gap in gap_test_list:
        layout_params_modified = deepcopy(dsn.base_layout_params)
        layout_params_modified['gap'] = gap
        tb_params_modified = deepcopy(dsn.base_tb_params)

        if tb_params_modified['simulate'] is False:
            layout_params_modified['ring_params']['layer'] = ('dummy', 'dummy')
            # layout_params_modified['output_ring_params']['layer'] = ('dummy', 'dummy')
            # layout_params_modified['ring_params']['layer'] = ('dummy', 'dummy')

        dsn.add_sweep_point(layout_params=layout_params_modified, tb_params=tb_params_modified)

    dsn.generate_batch(batch_name='gap_sweep')

    print('I AM DONE WOOHOO!!!!!!!!!!!!')




