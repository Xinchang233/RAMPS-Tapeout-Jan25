
from typing import TYPE_CHECKING, List, Any, Tuple, Union, Optional

if TYPE_CHECKING:
    pass

lpp_type = Tuple[str, str]


class LayerInfo(dict):
    items = ['cad_layer', 'cad_purpose', 'gds_layer', 'gds_purpose', 'color_packet', 'color_props']

    def __init__(self,
                 **kwargs: Any,
                 ) -> None:
        # Check that the kwargs are valid. If not, raise an error
        for key in kwargs:
            if key not in self.items:
                raise ValueError(f'Unknown key: {key}')

        # If key is not specified, content list should have an empty list, not None
        kv_iter = ((key, kwargs.get(key, [])) for key in self.items)
        dict.__init__(self, kv_iter)

    @property
    def cad_layer(self) -> str:
        return self['cad_layer']

    @property
    def cad_purpose(self) -> str:
        return self['cad_purpose']

    @property
    def cad_lpp(self) -> "lpp_type":
        return self['cad_layer'], self['cad_purpose']

    @property
    def gds_layer(self) -> str:
        return self['gds_layer']

    @property
    def gds_purpose(self) -> str:
        return self['gds_purpose']

    @property
    def gds_lpp(self) -> "lpp_type":
        return self['gds_layer'], self['gds_purpose']


class LayerInfoList:
    def __init__(self,
                 info_list: List["LayerInfo"] = None,
                 ):
        self.info_list: List["LayerInfo"] = []
        if info_list is not None:
            self.info_list = info_list

    def has_cad_lpp(self,
                    cad_lpp: "lpp_type",
                    ) -> Union[bool, "lpp_type"]:
        for info in self.info_list:
            if info.cad_lpp == cad_lpp:
                return info.cad_lpp
        return False

    def has_gds_lpp(self,
                    gds_lpp: "lpp_type",
                    ) -> Union[bool, "lpp_type"]:
        for info in self.info_list:
            if info.gds_lpp == gds_lpp:
                return info.gds_lpp, info
        return False

    def append_unique_layerinfo(self,
                                new_info: "LayerInfo",
                                allow_duplicate_gds_overwrite: bool = False,
                                ) -> None:
        if not isinstance(new_info, LayerInfo):
            raise ValueError(f'LayerInfoList.append_unique_layerinfo takes 1 LayerInfo object as an argument.')

        if self.has_cad_lpp(new_info.cad_lpp):
            raise ValueError(f'cad lpp {new_info.cad_lpp} with already exists in LayerInfoList')
        if self.has_gds_lpp(new_info.gds_lpp):
            _, found_info = self.has_gds_lpp(new_info.gds_lpp)
            if not allow_duplicate_gds_overwrite:
                print(found_info)
                raise ValueError(f'gds lpp {new_info.gds_lpp} (with cad lpp {new_info.cad_lpp}) '
                                 f'already used in LayerInfoList')
            else:
                print(f'Overwriting gds lpp {new_info.gds_lpp} which '
                      f'was {found_info.cad_lpp} with cad lpp {new_info.cad_lpp}')
                self.info_list.remove(found_info)
        self.info_list.append(new_info)

    def merge_info_lists(self,
                         new_info_list: "LayerInfoList",
                         allow_duplicate_gds_overwrite: bool = False,
                         ) -> None:
        if not isinstance(new_info_list, LayerInfoList):
            raise ValueError(f'LayerInfoList.append_unique takes 1 LayerInfoList object as an argument.')

        for info in new_info_list.info_list:
            self.append_unique_layerinfo(info,
                                         allow_duplicate_gds_overwrite=allow_duplicate_gds_overwrite)


def parse_layermap(filename: str,
                   ignore_purpose_list: tuple = (),
                   ignore_lpp_list: tuple = (),
                   ) -> "LayerInfoList":
    """
    Parses layermap file into a list of dictionaries for each layer.

    Parameters
    ----------
    filename
    ignore_purpose_list
    ignore_lpp_list

    Returns
    -------

    """
    layer_info_list = LayerInfoList()

    with open(filename, 'r') as f:
        for num, line in enumerate(f):
            line_nocomment = line.split('#')[0]
            values = line_nocomment.split()
            # Ignore blank lines
            if len(values) != 0:
                # Check validity of line
                if not len(values) == 4:
                    raise ValueError(f'layermap invalid. Each line must be 4 words of: '
                                     f'cad_layer, cad_purpose, gds_layer, gds_purpose. '
                                     f'Layermap {filename}, line {num} violates this.')
                if values[1] in ignore_purpose_list:
                    print(f'Ignoring layer (ignore purpose):  {values[0]} {values[1]} {values[2]} {values[3]}')
                elif (values[0], values[1]) in ignore_lpp_list:
                    print(f'Ignoring layer (ignore lpp):  {values[0]} {values[1]} {values[2]} {values[3]}')
                else:
                    layer_info = LayerInfo(
                        cad_layer=values[0],
                        cad_purpose=values[1],
                        gds_layer=values[2],
                        gds_purpose=values[3],
                    )

                    layer_info_list.append_unique_layerinfo(layer_info)

    return layer_info_list


def merge_layermaps(layermap_files: List[str],
                    ignore_lpp_list: tuple = (),
                    ignore_purpose_list: tuple = (),
                    allow_duplicate_gds_overwrite: bool = False,
                    ) -> "LayerInfoList":
    layer_info = LayerInfoList()
    for layermap_file in layermap_files:
        this_info = parse_layermap(layermap_file,
                                   ignore_lpp_list=ignore_lpp_list,
                                   ignore_purpose_list=ignore_purpose_list
                                   )
        layer_info.merge_info_lists(this_info,
                                    allow_duplicate_gds_overwrite=allow_duplicate_gds_overwrite)

    return layer_info


def stream_out_cadence_gds_map(filename: str,
                               layer_info_list: "LayerInfoList",
                               ) -> None:
    with open(filename, 'w') as f:
        # Write header:
        f.write(f'{"#"*80}\n')
        f.write(f'# Cadence stream-out layermap. Generated from GF45RFSOI/Photonics/scripts/make_layermap.py\n')
        f.write(f'{"#"*80}\n\n')
        f.write(f'# {"CAD layer":<23}{"CAD purpose":<25}{"GDS layer":<10}{"GDS purpose"}\n')
        for layer_info in layer_info_list.info_list:
            if len(layer_info.cad_layer) > 25:
                raise ValueError(f'stream_out_cadence_gds_map assumes cad layer name is less than 25 characters. '
                                 f'Layer {layer_info.cad_layer} violates this.')
            if len(layer_info.cad_purpose) > 25:
                raise ValueError(f'stream_out_cadence_gds_map assumes cad purpose name is less than 25 characters. '
                                 f'Layer {layer_info.cad_purpose} violates this.')
            f.write(f'{layer_info.cad_layer:<25}{layer_info.cad_purpose:<25}'
                    f'{layer_info.gds_layer:<10}{layer_info.gds_purpose}\n')


def stream_out_bpg_gds_map(filename: str,
                           layer_info_list: "LayerInfoList",
                           via_info_file: str = None,
                           ) -> None:
    with open(filename, 'w') as f:
        # Write header:
        f.write(f'{"#"*80}\n')
        f.write(f'# BPG stream-out layermap. Generated from GF45RFSOI/Photonics/scripts/make_layermap.py\n')
        f.write(f'{"#"*80}\n\n')

        if via_info_file:
            with open(via_info_file, 'r') as via_file:
                via_lines = via_file.readlines()
                via_lines += f'\n\n'
        else:
            via_lines = [f'via_info:\n\n']

        f.writelines(via_lines)

        f.write(f'layer_map:\n')

        for layer_info in layer_info_list.info_list:
            f.write(f'  !!python/tuple [\'{layer_info.cad_layer}\', \'{layer_info.cad_purpose}\']: '
                    f'[{layer_info.gds_layer}, {layer_info.gds_purpose}]\n')


def generate_layer_maps(layer_maps: List[str],
                        bpg_map_outfile: Optional[str],
                        cadence_map_outfile: Optional[str],
                        via_info_file: str,
                        ignore_lpp_list: tuple = (),
                        ignore_purpose_list: tuple = (),
                        allow_duplicate_gds_overwrite: bool = False,
                        ):
    merged_layerinfo = merge_layermaps(layer_maps,
                                       ignore_purpose_list=ignore_purpose_list,
                                       ignore_lpp_list=ignore_lpp_list,
                                       allow_duplicate_gds_overwrite=allow_duplicate_gds_overwrite,
                                       )
    if bpg_map_outfile is not None:
        stream_out_bpg_gds_map(filename=bpg_map_outfile,
                               layer_info_list=merged_layerinfo,
                               via_info_file=via_info_file)
    if cadence_map_outfile is not None:
        stream_out_cadence_gds_map(filename=cadence_map_outfile,
                                   layer_info_list=merged_layerinfo)


if __name__ == '__main__':
    GF_LAYERMAP = 'gf45spclo/workspace_setup/layermap'
    ABSTRACT_LAYERMAP = 'gf45spclo_photonics/source/abstract_layers.layermap'
    VIA_INFO = 'gf45spclo_photonics/source/via_info_9LM.yaml'

    BPG_MAP_OUT = 'gf45spclo_photonics/gds_map_generated.yaml'
    BPG_MAP_FOUNDRY_ONLY = 'gf45spclo_photonics/gds_map_foundry_layers_generated.yaml'
    CADENCE_MAP_OUT = 'gf45spclo_photonics/gds_map_cadence.layermap'
    CADENCE_MAP_FOUNDRY_ONLY = 'gf45spclo_photonics/gds_map_cadence_foundry_layers.layermap'

    # All matching LPPs in the list below will be ignored (not used for generated layermaps)
    ignore_lpps = ()
    # All layers with these purposes will be ignored (not used for generated layermaps)
    ignore_purposes = ('vdd', 'gnd', )

    # Stream out all layer maps
    generate_layer_maps(layer_maps=[GF_LAYERMAP, ABSTRACT_LAYERMAP],
                        bpg_map_outfile=BPG_MAP_OUT,
                        cadence_map_outfile=CADENCE_MAP_OUT,
                        via_info_file=VIA_INFO,
                        ignore_lpp_list=ignore_lpps,
                        ignore_purpose_list=ignore_purposes,
                        allow_duplicate_gds_overwrite=True,
                        )

    # Stream out foundry (base + supplementary layers)
    generate_layer_maps(layer_maps=[GF_LAYERMAP],
                        bpg_map_outfile=BPG_MAP_FOUNDRY_ONLY,
                        cadence_map_outfile=CADENCE_MAP_FOUNDRY_ONLY,
                        via_info_file=VIA_INFO,
                        ignore_lpp_list=ignore_lpps,
                        ignore_purpose_list=ignore_purposes,
                        allow_duplicate_gds_overwrite=False)

