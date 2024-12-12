import BPG
from Photonic_Core_Layout.WaveguideBase.DualLayerContactedSlotWaveguide import DualLayerContactedSlotWaveguide


class TestDualLayerContactedSlotWaveguideClass(BPG.PhotonicTemplateBase):
    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)

    @classmethod
    def get_params_info(cls) -> dict:
        return dict(
            slot_params_list='',
        )

    def draw_layout(self) -> None:
        """
        Draw waveguide paperclip components
        """
        slot_params_list = self.params['slot_params_list']

        allowed_orients = ['R0', 'R90', 'R180', 'R270', 'MX', 'MY', 'MXR90', 'MYR90']

        for reflect_ind, reflect in enumerate([True, False]):
            for ind, orient in enumerate(allowed_orients):
                slot_master = self.new_template(params=slot_params_list[0], temp_cls=DualLayerContactedSlotWaveguide)

                slot_loc = ((0 if ind < 4 else 20) + 40 * reflect_ind, 20 * (ind % 4))

                myport = self.add_photonic_port(
                    name=f'PORT{ind}_ref{reflect_ind}',
                    center=slot_loc,
                    orient=orient,
                    width=0.4,
                    layer=('SI', 'drawing'),
                    resolution=self.grid.resolution,
                    unit_mode=False
                )

                self.add_instance_port_to_port(
                    inst_master=slot_master,
                    instance_port_name='PORT0',
                    self_port=myport,
                    reflect=reflect
                )


def test_dual_layer_contacted_slot_waveguide():
    spec_file = 'Photonic_Core_Layout/WaveguideBase/specs/dual_layer_contacted_slot_waveguide.yaml'
    plm = BPG.PhotonicLayoutManager(spec_file)
    plm.generate_content()
    plm.generate_flat_content()
    plm.generate_flat_gds()
    # plm.generate_lsf()


def test_dual_layer_contacted_slot_waveguide_class():
    spec_file = 'Photonic_Core_Layout/WaveguideBase/specs/dual_layer_contacted_slot_waveguide_class.yaml'
    plm = BPG.PhotonicLayoutManager(spec_file)
    plm.generate_content()
    plm.generate_gds()
    plm.generate_flat_content()
    plm.generate_flat_gds()


if __name__ == '__main__':
    test_dual_layer_contacted_slot_waveguide()
    test_dual_layer_contacted_slot_waveguide_class()