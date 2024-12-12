import BPG
from Photonic_Core_Layout.WaveguideBase.EulerBendWaveguide import EulerBendWaveguide


class EulerBendTester(BPG.PhotonicTemplateBase):
    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)

    @classmethod
    def get_params_info(cls):
        return dict(
            euler_bend_param_list='list of waveguide parameters',
        )

    def draw_layout(self):
        euler_param_list = self.params['euler_bend_param_list']

        for euler_params in euler_param_list:
            euler_master = self.new_template(params=euler_params, temp_cls=EulerBendWaveguide)

            self.add_instance(
                master=euler_master,
                inst_name=f'euler_percent__{euler_params["euler_percent"]}',
                loc=(0, 0),
                orient='R0',
                unit_mode=False
            )


def test_euler_bend():
    spec_file = 'Photonic_Core_Layout/WaveguideBase/specs/euler.yaml'
    plm = BPG.PhotonicLayoutManager(spec_file)
    plm.generate_content()
    plm.generate_gds()
    plm.generate_flat_content()
    plm.generate_flat_gds()
    plm.generate_lsf()


def test_euler_bend_class():
    spec_file = 'Photonic_Core_Layout/WaveguideBase/specs/euler_class.yaml'
    plm = BPG.PhotonicLayoutManager(spec_file)
    plm.generate_content()
    plm.generate_gds()
    plm.generate_flat_content()
    plm.generate_flat_gds()
    plm.generate_lsf()


if __name__ == '__main__':
    test_euler_bend()
    test_euler_bend_class()
