from BPG.photonic_core import PhotonicTechInfo
from BPG.bpg_custom_types import *
from typing import Union, Tuple
from math import pi


class PhotonicTechInfo45SPCLO(PhotonicTechInfo):
    def __init__(self, photonic_tech_params, resolution, layout_unit):
        PhotonicTechInfo.__init__(self, photonic_tech_params, resolution, layout_unit)

    def min_width_unit(self,
                       layer,  # type: Union[str, Tuple[str, str]]
                       ):
        # type: (...) -> int
        """
        Returns the minimum width (in resolution units) for a given layer.

        Parameters
        ----------
        layer : Union[str, Tuple[str, str]]
            The layer name or LPP of the layer.

        Returns
        -------
        min_width_unit : float
            The minimum width in resolution units for shapes on the layer
        """
        # If a tuple, look only at the layer of the LPP
        if isinstance(layer, tuple):
            layer = layer[0]

        layer_values = self.dataprep_parameters['MinWidth']
        if layer not in layer_values:
            raise ValueError('Layer {layer} not present in parameters for MinWidth'.format(layer=layer))

        return int(round(layer_values[layer] / self._resolution))

    def min_width(self,
                  layer,  # type: Union[str, Tuple[str, str]]
                  ):
        # type: (...) -> float
        """
        Returns the minimum width (in layout units) for a given layer.

        Parameters
        ----------
        layer : Union[str, Tuple[str, str]]
            The layer name or LPP of the layer.

        Returns
        -------
        min_width : float
            The minimum width for shapes on the layer
        """

        return self.min_width_unit(layer) * self._resolution

    def min_space_unit(self,
                       layer,  # type: Union[str, Tuple[str, str]]
                       ):
        # type: (...) -> int
        """
        Returns the minimum space (in resolution units) for a given layer.

        Parameters
        ----------
        layer : Union[str, Tuple[str, str]]
            The layer name or LPP of the layer.

        Returns
        -------
        min_space_unit : float
            The minimum space in resolution units for shapes on the layer
        """
        # If a tuple, look only at the layer of the LPP
        if isinstance(layer, tuple):
            layer = layer[0]

        layer_values = self.dataprep_parameters['MinSpace']
        if layer not in layer_values:
            raise ValueError('Layer {layer} not present in parameters for MinSpace'.format(layer=layer))

        return int(round(layer_values[layer] / self._resolution))

    def min_space(self,
                  layer,  # type: Union[str, Tuple[str, str]]
                  ):
        # type: (...) -> float
        """
        Returns the minimum space (in layout units) for a given layer.

        Parameters
        ----------
        layer : Union[str, Tuple[str, str]]
            The layer name or LPP of the layer.

        Returns
        -------
        min_space : float
            The minimum space for shapes on the layer
        """

        return self.min_space_unit(layer) * self._resolution

    def max_width_unit(self,
                       layer,  # type: Union[str, Tuple[str, str]]
                       ):
        # type: (...) -> int
        """
        Returns the maximum width (in resolution units) for a given layer.

        Parameters
        ----------
        layer : Union[str, Tuple[str, str]]
            The layer name or LPP of the layer.

        Returns
        -------
        max_width_unit : float
            The maximum width in resolution units for shapes on the layer
        """
        # If a tuple, look only at the layer of the LPP
        if isinstance(layer, tuple):
            layer = layer[0]

        layer_values = self.dataprep_parameters['MaxWidth']
        if layer not in layer_values:
            raise ValueError('Layer {layer} not present in parameters for MaxWidth'.format(layer=layer))

        return int(round(layer_values[layer] / self._resolution))

    def max_width(self,
                  layer,  # type: Union[str, Tuple[str, str]]
                  ):
        # type: (...) -> float
        """
        Returns the maximum width (in layout units) for a given layer.

        Parameters
        ----------
        layer : Union[str, Tuple[str, str]]
            The layer name or LPP of the layer.

        Returns
        -------
        max_width : float
            The maximum width for shapes on the layer
        """

        return self.max_width_unit(layer) * self._resolution

    def min_area_unit(self,
                      layer,  # type: Union[str, Tuple[str, str]]
                      ):
        # type: (...) -> int
        """
        Returns the minimum area (in resolution units) for a given layer.

        Parameters
        ----------
        layer : Union[str, Tuple[str, str]]
            The layer name or LPP of the layer.

        Returns
        -------
        min_area_unit : float
            The minimum area in resolution units for shapes on the layer
        """
        # If a tuple, look only at the layer of the LPP
        if isinstance(layer, tuple):
            layer = layer[0]

        layer_values = self.dataprep_parameters['MinArea']
        if layer not in layer_values:
            raise ValueError('Layer {layer} not present in parameters for MinArea'.format(layer=layer))

        return int(round(layer_values[layer] / (self._resolution * self._resolution)))

    def min_area(self,
                 layer,  # type: Union[str, Tuple[str, str]]
                 ):
        # type: (...) -> float
        """
        Returns the minimum area (in layout units) for a given layer.

        Parameters
        ----------
        layer : Union[str, Tuple[str, str]]
            The layer name or LPP of the layer.

        Returns
        -------
        min_area : float
            The minimum area for shapes on the layer
        """

        return self.min_area_unit(layer) * self._resolution * self._resolution

    def min_edge_length_unit(self,
                             layer: Union[str, Tuple[str, str]],
                             ):
        # type: (...) -> int
        """
        Returns the minimum edge length (in resolution units) for a given layer.

        Parameters
        ----------
        layer : Union[str, Tuple[str, str]]
            The layer name or LPP of the layer.

        Returns
        -------
        min_edge_length : float
            The minimum edge length in resolution units for shapes on the layer
        """
        # If a tuple, look only at the layer of the LPP
        if isinstance(layer, tuple):
            layer = layer[0]

        layer_values = self.dataprep_parameters['MinEdgeLength']
        if layer not in layer_values:
            raise ValueError(f'Layer {layer} not present in parameters for MinEdgeLength')

        return int(round(layer_values[layer] / self._resolution))

    def min_edge_length(self,
                        layer: Union[str, Tuple[str, str]],
                        ):
        # type: (...) -> float
        """
        Returns the minimum edge length (in layout units) for a given layer.

        Parameters
        ----------
        layer : Union[str, Tuple[str, str]]
            The layer name or LPP of the layer.

        Returns
        -------
        min_edge_length : float
            The minimum edge length for shapes on the layer
        """

        return self.min_edge_length_unit(layer) * self._resolution

    def height_unit(self,
                    layer,  # type: Union[str, Tuple[str, str]]
                    ):
        # type: (...) -> int
        """
        Returns the height from the top of the silicon region (defined as 0) to the bottom surface of the given
        layer, in resolution units.

        Parameters
        ----------
        layer : Union[str, Tuple[str, str]]
            The layer name or LPP of the layer.

        Returns
        -------
        height_unit : float
            The height of the bottom surface in resolution units for shapes on the layer
        """
        # If a tuple, look only at the layer of the LPP
        if isinstance(layer, tuple):
            layer = layer[0]

        layer_values = self.dataprep_parameters['Height']
        if layer not in layer_values:
            raise ValueError('Layer {layer} not present in parameters for Height'.format(layer=layer))

        return int(round(layer_values[layer] / self._resolution))

    def height(self,
               layer,  # type: Union[str, Tuple[str, str]]
               ):
        # type: (...) -> float
        """
        Returns the height from the top of the silicon region (defined as 0) to the bottom surface of the given
        layer, in layout units.

        Parameters
        ----------
        layer : Union[str, Tuple[str, str]]
            The layer name or LPP of the layer.

        Returns
        -------
        height : float
            The height of the bottom surface for shapes on the layer
        """

        return self.height_unit(layer) * self._resolution

    def thickness_unit(self,
                       layer,  # type: Union[str, Tuple[str, str]]
                       ):
        # type: (...) -> int
        """
        Returns the thickness of the layer, in resolution units

        Parameters
        ----------
        layer : Union[str, Tuple[str, str]]
            The layer name or LPP of the layer.

        Returns
        -------
        thickness_unit : float
            The thickness in resolution units for shapes on the layer
        """
        # If a tuple, look only at the layer of the LPP
        if isinstance(layer, tuple):
            layer = layer[0]

        layer_values = self.dataprep_parameters['Thickness']
        if layer not in layer_values:
            raise ValueError('Layer {layer} not present in parameters for Thickness'.format(layer=layer))

        return int(round(layer_values[layer] / self._resolution))

    def thickness(self,
                  layer,  # type: Union[str, Tuple[str, str]]
                  ):
        # type: (...) -> float
        """
        Returns the thickness of the layer, in layout units.

        Parameters
        ----------
        layer : Union[str, Tuple[str, str]]
            The layer name or LPP of the layer.

        Returns
        -------
        thickness : float
            The thickness of shapes on the layer
        """

        return self.thickness_unit(layer) * self._resolution

    def sheet_resistance(self,
                         layer  # type: Union[str, Tuple[str, str]]
                         ):
        # type: (...) -> float
        """
        Returns the sheet resistance of the layer, in Ohm/sq.

        Parameters
        ----------
        layer : Union[str, Tuple[str, str]]
            The layer name or LPP of the layer.

        Returns
        -------
        rs : float
            The sheet resistance of the layer in Ohm/sq
        """
        # If a tuple, look only at the layer of the LPP
        if isinstance(layer, tuple):
            layer = layer[0]
        if isinstance(layer, list):
            layer = layer[0]

        rs_values = self.dataprep_parameters['Rs']
        if layer not in rs_values:
            raise ValueError('Layer {layer} not present in parameters for sheet resistance (Rs)'.format(layer=layer))

        return rs_values[layer]

    def via_max_width_unit(self,
                           layer: Union[str, Tuple[str, str]],
                           ) -> int:
        """
        Returns the metal width corresponding to minimum metal enclosure for a max width via array.
        IE, a larger metal would satisfy via enclosure rules, but the via array cannot grow any larger.

        So for BPG's via stack, the biggest enclosure width allowed to be passed into bag's add_via function is this
        width, because bag does not check for this rule.

        Parameters
        ----------
        layer : Union[str, Tuple[str, str]]
            The layer name or LPP of the layer.

        Returns
        -------
        max_width_unit : int
            The max width
        """
        # If a tuple, look only at the layer of the LPP
        if isinstance(layer, tuple):
            layer = layer[0]

        layer_values = self.dataprep_parameters['ViaMaxWidth']
        if layer not in layer_values:
            raise ValueError('Layer {layer} not present in parameters for ViaMaxWidth'.format(layer=layer))

        return int(round(layer_values[layer] / self._resolution))

    def via_max_width(self,
                      layer: Union[str, Tuple[str, str]],
                      ) -> float:
        """
        Returns the metal width corresponding to minimum metal enclosure for a max width via array.
        IE, a larger metal would satisfy via enclosure rules, but the via array cannot grow any larger.

        So for BPG's via stack, the biggest enclosure width allowed to be passed into bag's add_via function is this
        width, because bag does not check for this rule.

        Parameters
        ----------
        layer : Union[str, Tuple[str, str]]
            The layer name or LPP of the layer.

        Returns
        -------
        max_width : float
            The max width
        """

        return self.via_max_width_unit(layer) * self._resolution

    # #
    # @property
    # def waveguide_layer(self) -> layer_or_lpp_type:
    #     """ Default layer to be used for waveguide routing """
    #     return 'rx1phot', 'drawing'
    #
    # @property
    # def waveguide_width(self) -> float:
    #     """ Default waveguide width """
    #     return .418

    @staticmethod
    def default_layer_table():
        return {
            'Routing': ('si_full_free', 'drawing'),
            'nitride': ('si_full_free', 'drawing'),
        }

    def layer_lookup(self, purpose):
        return self.default_layer_table()[purpose]

    @staticmethod
    def get_default_wg_params(layer=None,
                              ) -> dict:
        # Define default waeguide parameters for each waveguide type

        default_wg_params = dict(
            bend_type='trajECE',
            AngleTurnEuler=0.14 * pi
        )

        # Full height silicon waveguide
        if layer[0] == 'si_full' or layer[0] == 'si_full_free':
            default_wg_params['radius'] = 10
            default_wg_params['width'] = 0.350

        elif layer[0] == 'si_tm':
            default_wg_params['radius'] = 40.0
            default_wg_params['width'] = 0.350

        elif layer[0] == 'sin_free' or layer[0] == 'sin':
            default_wg_params['radius'] = 50
            default_wg_params['width'] = 0.8

        return default_wg_params

    def get_edge_length(self) -> float:
        # Edge length used in some round shape drawing
        return 0.015
