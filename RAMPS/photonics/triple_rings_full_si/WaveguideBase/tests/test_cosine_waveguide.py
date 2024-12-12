import BPG
import math
from Photonic_Core_Layout.WaveguideBase.CosineWaveguide import CosineWaveguide


class CosineWaveguideTester(BPG.PhotonicTemplateBase):
    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)

    @classmethod
    def get_params_info(cls):
        return dict(
            cos_waveguide_params_list='list of waveguide parameters',
        )

    def draw_layout(self):
        cos_waveguide_params_list = self.params['cos_waveguide_params_list']

        max_amp = 0
        for cos_wg_params in cos_waveguide_params_list:
            if cos_wg_params['amplitude'] > max_amp:
                max_amp = cos_wg_params['amplitude']

        for i, cos_wg_params in enumerate(cos_waveguide_params_list):
            cos_master = self.new_template(params=cos_wg_params, temp_cls=CosineWaveguide)

            self.add_instance(
                master=cos_master,
                inst_name=f'cos_number_{i}',
                loc=(0, 2.5 * i * max_amp),
                orient='R0',
                unit_mode=False
            )


def test_cosine_waveguide():
    spec_file = 'Photonic_Core_Layout/WaveguideBase/specs/cosine_waveguide.yaml'
    plm = BPG.PhotonicLayoutManager(spec_file)
    plm.generate_template()
    plm.generate_content()
    plm.generate_gds()
    plm.generate_flat_content()
    plm.generate_flat_gds()
    plm.generate_lsf()


def test_cosine_waveguide_class():
    spec_file = 'Photonic_Core_Layout/WaveguideBase/specs/cosine_waveguide_class.yaml'
    plm = BPG.PhotonicLayoutManager(spec_file)
    plm.generate_template()
    plm.generate_content()
    plm.generate_gds()
    plm.generate_flat_content()
    plm.generate_flat_gds()
    plm.generate_lsf()


if __name__ == '__main__':
    test_cosine_waveguide()
    test_cosine_waveguide_class()
