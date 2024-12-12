#!/usr/bin/env python3

from typing import TYPE_CHECKING, List, Any, Tuple, Union
import re
import os
import string
from pathlib import Path

if TYPE_CHECKING:
    lpp_type = Tuple[str, str]


class LayerInfo(dict):
    items = ['gds_layer', 'gds_purpose', 'color', 'stipple_path', 'stipple', 'name',
             'layer', 'purpose', 'from_layermap']

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
    def gds_layer(self):
        return self['gds_layer']

    @property
    def gds_purpose(self):
        return self['gds_purpose']

    @property
    def gds_lpp(self) -> "lpp_type":
        return self.gds_layer, self.gds_purpose

    @property
    def color(self):
        return self['color']

    @property
    def stipple_path(self):
        return self['stipple_path']

    @property
    def stipple(self):
        return self['stipple']

    @property
    def name(self):
        return self['name']

    @property
    def layer(self):
        return self['layer']

    @property
    def purpose(self):
        return self['purpose']


class LayerInfoList:
    def __init__(self,
                 info_list: List["LayerInfo"] = None,
                 ):
        self.info_list: List["LayerInfo"] = []
        if info_list is not None:
            self.info_list = info_list

    def has_gds_lpp(self,
                    gds_lpp: "lpp_type",
                    ) -> Union[bool, "lpp_type"]:
        for info in self.info_list:
            if info.gds_lpp == gds_lpp:
                return info.gds_lpp
        return False

    def append_unique_layerinfo(self,
                                new_info: "LayerInfo",
                                ) -> None:
        if not isinstance(new_info, LayerInfo):
            raise ValueError(f'LayerInfoList.append_unique_layerinfo takes 1 LayerInfo object as an argument.')

        if self.has_gds_lpp(new_info.gds_lpp):
            print(f'gds lpp {new_info.gds_lpp} already used in LayerInfoList')
        self.info_list.append(new_info)

    def merge_info_lists(self,
                         new_info_list: "LayerInfoList",
                         ) -> None:
        if not isinstance(new_info_list, LayerInfoList):
            raise ValueError(f'LayerInfoList.append_unique takes 1 LayerInfoList object as an argument.')

        for info in new_info_list.info_list:
            self.append_unique_layerinfo(info)


def parse_path_string(path_string):
    """Returns the path_string with any environment variables ($asdf) expanded
    """
    return string.Template(path_string).substitute(os.environ)


def parse_calibre_file(file_name: str,
                       ) -> "LayerInfoList":
    """

    Parameters
    ----------
    file_name

    Returns
    -------

    """

    layer_info_list = LayerInfoList()

    with open(file_name, 'r') as f:
        line_regex = re.compile(r'^(\d+)\.(\d+)\s+(\S+)\s+(\S+)\s+(\w+)\s+\w+\s+\w+')

        for num, line in enumerate(f):
            line_match = re.match(line_regex, line)
            if line_match:
                match = line_match.groups()
                # line goes cad_lay_num.cad_purpose_num  color  @stipplepath  name  visible  valid
                layer_info = LayerInfo(
                    gds_layer=match[0],
                    gds_purpose=match[1],
                    color=match[2],
                    stipple_path=str(Path(parse_path_string(match[3][1:])).expanduser()),
                    stipple=match[3].split('/')[-1][:-4],
                    name=match[4],
                    layer=match[4].split('_')[0],
                    purpose=match[4].split('_')[1] if len(match[4].split('_')) == 2 else 'DRAWING',
                )
                layer_info_list.append_unique_layerinfo(layer_info)

    return layer_info_list


def parse_layermap(file_name: str,
                   layer_info_list: "LayerInfoList"
                   ):

    with open(file_name, 'r') as f:
        for num, line in enumerate(f):
            line_nocomment = line.split('#')[0]
            values = line_nocomment.split()
            # Ignore blank lines
            if len(values) != 0:
                # Check validity of line
                if not len(values) == 4:
                    raise ValueError(f'layermap invalid. Each line must be 4 words of: '
                                     f'cad_layer, cad_purpose, gds_layer, gds_purpose. '
                                     f'Layermap {file_name}, line {num} violates this.')

                layer_info = LayerInfo(
                    cad_layer=values[0],
                    cad_purpose=values[1],
                    gds_layer=values[2],
                    gds_purpose=values[3],
                    from_layermap=True,
                )

                # Only append unique keys
                layer_info_list.append_unique_layerinfo(layer_info)


def get_all_stipples(layer_info_list: LayerInfoList,
                     ) -> List[Tuple[str, str]]:
    """
    Gets a list of all the stipple file paths

    Parameters
    ----------
    layer_info_list

    Returns
    -------

    """
    stipple_paths = []
    for layer in layer_info_list.info_list:
        stipple_paths.extend([(layer.get('stipple_path', []), layer.get('stipple'))])

    return list(set(stipple_paths))     # Return only unique stipples


def parse_stipple_file(file_name: str,
                       ):
    """Parses the stipple file
    """
    out_lines = []
    with open(file_name, 'r') as f:
        line_regex = re.compile(r'^((0x\w\w, )+)')
        for num, line in enumerate(f):
            line_match = re.match(line_regex, line)
            if line_match:
                match = line_match.groups()[0]  # Get full match
                values = match.split(', ')
                outline_list = []
                for value in values[0:-1]:
                    outline_list.append(f'{int(value, 16):0>8b}'.replace('0', '.').replace('1', '*')[::-1])

                lineout = ''.join(outline_list)

                out_lines.append(lineout)

    return out_lines


def find_stipple_ind(stipple_name: str,
                     stipple_paths: List[Tuple[str, str]],
                     ) -> int:
    for ind, (_, stipple) in enumerate(stipple_paths):
        if stipple_name == stipple:
            return ind
    raise ValueError('Stipple was not found. Should never reach here.')


def dump_klayout_layerprops(outfile: str,
                            layer_list: LayerInfoList,
                            stipple_paths: List[Tuple[str, str]],
                            ):
    with open(outfile, 'w') as file:
        file.write(f'<?xml version="1.0" encoding="utf-8"?>\n')
        file.write(f'<layer-properties>\n')
        # Write the layers
        for layer in layer_list.info_list:
            file.write(f' <properties>\n')
            file.write(f'  <frame-color>{layer.color}</frame-color>\n')
            file.write(f'  <fill-color>{layer.color}</fill-color>\n')
            file.write(f'  <frame-brightness>0</frame-brightness>\n')
            file.write(f'  <fill-brightness>0</fill-brightness>\n')
            file.write(f'  <dither-pattern>C{find_stipple_ind(layer.stipple, stipple_paths)}</dither-pattern>\n')		# Dither-pattern must be the index of the custom stipple
            file.write(f'  <valid>true</valid>\n')
            file.write(f'  <visible>true</visible>\n')
            file.write(f'  <transparent>false</transparent>\n')
            file.write(f'  <width>1</width>\n')
            file.write(f'  <marked>false</marked>\n')
            file.write(f'  <animation>0</animation>\n')
            file.write(f'  <name>{layer.layer}.{layer.purpose} - {layer.gds_layer}/{layer.gds_purpose}</name>\n')
            file.write(f'  <source>{layer.gds_layer}/{layer.gds_purpose}@1</source>\n')
            file.write(f' </properties>\n')

        # Write a default display so that all layers will be shown in the layer panel without clicking
        # "Add Other Layer Entries"
        file.write(f' <properties>\n')
        file.write(f'  <source>*/*@*</source>\n')
        file.write(f' </properties>\n')

        file.write(f' <name/>\n')
        # Write the stipples
        for ind, (stipple_path, stipple) in enumerate(stipple_paths):
            stipple_lines = parse_stipple_file(stipple_path)

            file.write(f' <custom-dither-pattern>\n')
            file.write(f'  <pattern>\n')
            for line in stipple_lines[::-1]:
                file.write(f'   <line>{line}</line>\n')
            file.write(f'  </pattern>\n')
            file.write(f'  <order>{ind}</order>\n')
            file.write(f'  <name>{stipple}</name>\n')
            file.write(f' </custom-dither-pattern>\n')

        file.write(f'</layer-properties>\n')


if __name__ == '__main__':
    calibremap = 'gf45spclo_photonics/display/calibreDRV/layerprops'

    # Parse the calibreDRV layermap
    layers_list = parse_calibre_file(calibremap)

    # Get a list of all the stipple files
    stipple_paths = get_all_stipples(layers_list)

    outfile = 'gf45spclo_photonics/display/base_layerprops_generated.lyp'

    dump_klayout_layerprops(outfile=outfile, layer_list=layers_list, stipple_paths=stipple_paths)
