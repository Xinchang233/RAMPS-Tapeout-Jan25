import BPG
from Photonic_Core_Layout.WaveguideBase.WaveguideBase import WaveguideBase


class WaveguideBaseTester(BPG.PhotonicTemplateBase):
    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)

    @classmethod
    def get_params_info(cls):
        return dict(
            gen_waveguide_params='Waveguide parameters',
            gen_waveguide2_params='Waveguide parameters',
        )

    def draw_layout(self):
        waveguide_params = self.params['gen_waveguide_params']
        waveguide2_params = self.params['gen_waveguide2_params']

        waveguide_master = self.new_template(params=waveguide_params, temp_cls=WaveguideBase)
        waveguide2_master = self.new_template(params=waveguide2_params, temp_cls=WaveguideBase)

        waveguide1 = self.add_instance(
            master=waveguide_master,
            loc=(0, 0),
            orient='R90',
            unit_mode=False,
        )

        waveguide2 = self.add_instance(
            master=waveguide2_master,
            loc=(10, 0),
            orient='R270',
            unit_mode=False,
        )

        # Extracts and renames ports that will be used to do back-to-back port addition.
        self.extract_photonic_ports(
            inst=waveguide1,
            port_names='PORT0',
            port_renaming={'PORT0': 'NEWPORT'}
        )

        self.extract_photonic_ports(
            inst=waveguide2,
            port_names='PORT1',
            port_renaming={'PORT1': 'NEWPORT_2'}
        )

        # Generates a new instance of a given port template and connects it to one of the extracted ports.
        self.add_instances_port_to_port(
            inst_master=waveguide_master,
            instance_port_name='PORT1',
            self_port_name='NEWPORT',
            instance_name='NEW_GEN_WAVEGUIDE_1',
            reflect=True,
        )

        self.add_instances_port_to_port(
            inst_master=waveguide2_master,
            instance_port_name='PORT0',
            self_port_name='NEWPORT_2',
            instance_name='NEW_GEN_WAVEGUIDE_2',
            reflect=True,
        )


def test_wg_base():
    spec_file = 'Photonic_Core_Layout/WaveguideBase/specs/waveguide_base.yaml'
    plm = BPG.PhotonicLayoutManager(spec_file)
    plm.generate_content()
    plm.generate_gds()
    plm.generate_flat_content()
    plm.generate_flat_gds()
    plm.generate_lsf()


def test_wg_base_class():
    spec_file = 'Photonic_Core_Layout/WaveguideBase/specs/waveguide_base_class.yaml'
    plm = BPG.PhotonicLayoutManager(spec_file)
    plm.generate_content()
    plm.generate_gds()
    plm.generate_flat_content()
    plm.generate_flat_gds()
    plm.generate_lsf()


if __name__ == '__main__':
    test_wg_base()
    test_wg_base_class()
