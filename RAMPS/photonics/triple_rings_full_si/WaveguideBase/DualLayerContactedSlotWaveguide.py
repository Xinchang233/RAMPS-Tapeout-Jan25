import BPG
from Photonic_Core_Layout.WaveguideBase.SidewallContactedSlotWaveguide import SidewallContactedSlotWaveguide


class DualLayerContactedSlotWaveguide(BPG.PhotonicTemplateBase):
    """
    This Class generates a section of contacted dual-layer slot waveguide
    (e.g. layer1: body, layer2: gate or layer1: full_etch, layer2: partial_etch)

    Parameters
    ----------
    layer1_wg_params : dict
        parameters of the layer1 of the dual-layer slot waveguide
    layer2_wg_params : dict
        parameters of the layer2 of the dual-layer slot waveguide
    """

    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)

        # Master declaration
        self.layer1_wg_master = None
        self.layer2_wg_master = None
        self.layer1_wg_inst = None
        self.layer2_wg_inst = None

        # Initialize the variables and dictionary of parameters.
        self.layer1_wg_params = self.params['layer1_wg_params']
        self.layer2_wg_params = self.params['layer2_wg_params']

        # Parameter checking: Make sure parameters are valid type and values
        if any(not isinstance(val, (dict, type(None))) for val in [self.layer1_wg_params,
                                                                   self.layer2_wg_params]):
            raise ValueError('waveguide parameters of the layer1 and layer2 must be given as dict')

    @classmethod
    def get_params_info(cls) -> dict:
        return dict(
            layer1_wg_params='parameters of the layer1 of the dual-layer slot waveguide',
            layer2_wg_params='parameters of the layer2 of the dual-layer slot waveguide',
        )

    def draw_layout(self) -> None:
        self.create_wg_layers()
        self.place_wg_layers()

    def create_wg_layers(self) -> None:
        """
        Create the layers 1 and 2 of the slot waveguide
        """
        if self.layer1_wg_params is not None:
            self.layer1_wg_master = self.new_template(params=self.layer1_wg_params,
                                                      temp_cls=SidewallContactedSlotWaveguide)
        if self.layer2_wg_params is not None:
            self.layer2_wg_master = self.new_template(params=self.layer2_wg_params,
                                                      temp_cls=SidewallContactedSlotWaveguide)

    def place_wg_layers(self) -> None:
        """
        Place the layers 1 and 2 of the slot waveguide
        """
        if self.layer1_wg_params is not None:
            self.layer1_wg_inst = self.add_instance(self.layer1_wg_master,
                                                    loc=(0, 0),
                                                    orient='R0')
        if self.layer2_wg_params is not None:
            self.layer2_wg_inst = self.add_instance(self.layer2_wg_master,
                                                    loc=(0, 0),
                                                    orient='R0')
        # Extract photonic ports from one of the layers of the dual-layer dlot waveguide
        self.extract_photonic_ports(
            inst=self.layer1_wg_inst,
            show=False,
        )
