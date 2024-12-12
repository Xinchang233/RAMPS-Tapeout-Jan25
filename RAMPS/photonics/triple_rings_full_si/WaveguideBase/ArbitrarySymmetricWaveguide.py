import BPG
import importlib
from Photonic_Core_Layout.WaveguideBase.WgRouter import WgRouter


class ArbitrarySymmetricWaveguide(BPG.PhotonicTemplateBase):
    """
    This Class generates an arbitrary symmetric waveguide structure consisting of components listed in comp_list.
    First the components are placed and connected to each other in the same order they appear in the comp_list.
    Then they are flipped and connected in reverse order.
    This Class is particularly useful for creating unit cells for paperclip and taperclip waveguides and waveguide phase
    shifters with complex geometries.

    Parameters
    ----------
    comp_package : list
        List of packages used for building arbitrary symmetric waveguide
    comp_class : list
        List of classes used for building arbitrary symmetric waveguide
    comp_ports : list
        List of input and output ports of the components
    comp_params : list
        List of parameter dictionaries of the components
    flip_last : Bool
        Bool variable which determines if a flipped copy of the last component is added to the structure or not
    """

    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)

        # Initialize the variables and dictionary of parameters.
        self.comp_package = self.params['comp_package']
        self.comp_class = self.params['comp_class']
        self.comp_ports = self.params['comp_ports']
        self.comp_params = self.params['comp_params']
        self.flip_last = self.params['flip_last']

    @classmethod
    def get_params_info(cls) -> dict:
        return dict(
            comp_package='List of packages used for building arbitrary symmetric waveguide',
            comp_class='List of classes used for building arbitrary symmetric waveguide',
            comp_ports='List of input and output ports of the components',
            comp_params='List of parameter dictionaries of the components',
            flip_last='Bool variable which determines if a flipped copy of the last component'
                      ' is added to the structure or not'
        )

    def draw_layout(self):
        self.create_symmetric_wg()

    def create_symmetric_wg(self):
        """
        Creates symmetric waveguide structure
        """
        # place the first component and make its input port as the input port of the symmetric waveguide
        lay_module = importlib.import_module(self.comp_package[0])
        temp_cls = getattr(lay_module, self.comp_class[0])

        # create template of the first component
        comp1_master = self.new_template(temp_cls=temp_cls,
                                         params=self.comp_params[0])

        # instantiate the first component
        comp1_inst = self.add_instance(comp1_master,
                                       loc=(0, 0),
                                       orient='R0')

        # extract input and output ports of the first component
        self.extract_photonic_ports(inst=comp1_inst,
                                    port_names=[self.comp_ports[0][0], self.comp_ports[0][1]],
                                    port_renaming={self.comp_ports[0][0]: 'PORT0',
                                                   self.comp_ports[0][1]: 'PORT1'},
                                    show=False
                                    )
        # Pass the output port of the first component to WgRouter function
        router = WgRouter(gen_cls=self,
                          init_port=self.get_photonic_port('PORT1'),
                          layer=self.get_photonic_port('PORT1').layer)

        # Output port of the first component can now be deleted
        self.delete_port('PORT1')

        # Place the remaining components
        num_comp = len(self.comp_class)
        for count in range(1, num_comp, 1):
            lay_module = importlib.import_module(self.comp_package[count])
            temp_cls = getattr(lay_module, self.comp_class[count])
            router.add_component(temp_cls=temp_cls,
                                 params=self.comp_params[count],
                                 input_port_name=self.comp_ports[count][0],
                                 output_port_name=self.comp_ports[count][1],
                                 reflect=False)

        if not self.flip_last:
            num_comp -= 1

        for count in range(num_comp-1, -1, -1):
            lay_module = importlib.import_module(self.comp_package[count])
            temp_cls = getattr(lay_module, self.comp_class[count])
            router.add_component(temp_cls=temp_cls,
                                 params=self.comp_params[count],
                                 input_port_name=self.comp_ports[count][1],
                                 output_port_name=self.comp_ports[count][0],
                                 reflect=True
                                 )

        # Extract the input port of the last instance and make it the output port of the symmetric waveguide
        self.extract_photonic_ports(inst=router.inst,
                                    port_names=self.comp_ports[0][0],
                                    port_renaming={self.comp_ports[0][0]: 'PORT1'},
                                    show=False
                                    )
