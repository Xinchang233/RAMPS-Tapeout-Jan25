import BPG
from Photonic_Core_Layout.Spoke.SpokeBase import SpokeBase


class SpokeTestBase(BPG.PhotonicTemplateBase):
    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)

    @classmethod
    def get_params_info(cls):  # Returns definition of the parameters.
        return dict(
            spokes='List of spoke params',
        )

    def draw_layout(self):
        for spoke in self.params['spokes']:
            spoke_master = self.new_template(params=spoke, temp_cls=SpokeBase)
            self.add_instance(
                master=spoke_master,
                loc=(0, 0)
            )


def test_spoke_vertical():
    spec_file = 'Photonic_Core_Layout_Djordje/Ring/specs/ring_specs_vertical.yaml'
    plm = BPG.PhotonicLayoutManager(spec_file)
    plm.generate_content()
    plm.generate_gds()
    plm.dataprep_calibre()


if __name__ == '__main__':
    test_spoke_vertical()
    # test_spoke_class()
