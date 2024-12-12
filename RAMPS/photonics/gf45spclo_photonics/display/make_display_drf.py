from typing import TYPE_CHECKING, List, Any, Tuple, Union
import re

if TYPE_CHECKING:
    pass

lpp_type = Tuple[str, str]


class LayerInfo(dict):
    items = ['cad_layer', 'cad_purpose', 'gds_layer', 'gds_purpose', 'display_packet', 'color_props']

    def __init__(self,
                 **kwargs: Any,
                 ) -> None:
        # Check that the kwargs are valid. If not, raise an error
        for key in kwargs:
            if key not in self.items:
                raise ValueError(f'Unknown key: {key}')

        # If key is not specified, content list should have an empty list, not None
        kv_iter = ((key, kwargs.get(key)) for key in self.items)
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

    @property
    def display_packet(self) -> str:
        return self['display_packet']

    @property
    def color_props(self) -> Tuple:
        return self['color_props']

    @color_props.setter
    def color_props(self,
                    new_color_props: Tuple) -> None:
        self['color_props'] = new_color_props


class LayerInfoList:
    def __init__(self,
                 info_list: List["LayerInfo"] = None,
                 color_dict: dict = None,
                 stipple_dict: dict = None,
                 line_dict: dict = None,
                 ):
        self.info_list: List["LayerInfo"] = []
        if info_list is not None:
            self.info_list = info_list

        self.color_dict = {}
        if color_dict is not None:
            self.color_dict = color_dict

        self.stipple_dict = {}
        if stipple_dict is not None:
            self.stipple_dict = stipple_dict

        self.line_dict = {}
        if line_dict is not None:
            self.line_dict = line_dict

    def has_cad_lpp(self,
                    cad_lpp: "lpp_type",
                    ) -> Union["LayerInfo", None]:
        for info in self.info_list:
            if info.cad_lpp == cad_lpp:
                return info
        return None

    def has_gds_lpp(self,
                    gds_lpp: "lpp_type",
                    ) -> Union["LayerInfo", None]:
        for info in self.info_list:
            if info.gds_lpp == gds_lpp:
                return info
        return None

    def has_display_packet(self,
                           display_packet: str,
                           ) -> Union["LayerInfo", None]:
        ret_val = []
        for info in self.info_list:
            if info.display_packet == display_packet:
                ret_val.append(info)
        return ret_val

    def append_unique_layerinfo(self,
                                new_info: "LayerInfo",
                                ) -> None:
        if not isinstance(new_info, LayerInfo):
            raise ValueError(f'LayerInfoList.append_unique_layerinfo takes 1 LayerInfo object as an argument.')

        if (new_info.cad_lpp != (None, None)) and self.has_cad_lpp(new_info.cad_lpp):
            print(f'cad lpp {new_info.cad_lpp} with already exists in LayerInfoList')
        if (new_info.gds_lpp != (None, None)) and self.has_gds_lpp(new_info.gds_lpp):
            print(f'gds lpp {new_info.gds_lpp} (with cad lpp {new_info.cad_lpp}) already used in LayerInfoList')
        self.info_list.append(new_info)

    def merge_info_lists(self,
                         new_info_list: "LayerInfoList",
                         ) -> None:
        if not isinstance(new_info_list, LayerInfoList):
            raise ValueError(f'LayerInfoList.append_unique takes 1 LayerInfoList object as an argument.')

        for info in new_info_list.info_list:
            self.append_unique_layerinfo(info)

    def add_color(self, name, line, overwrite=True):
        if name in self.color_dict:
            if overwrite:
                print(f'Overwriting color: {name}:  \n'
                      f'{self.color_dict[name]}  -->  {line}')
                self.color_dict[name] = line

            else:
                print(f'DID NOT overwrite color: {name}')
        else:
            self.color_dict[name] = line

    def add_stipple(self, name, lines, overwrite=True):
        if name in self.stipple_dict:
            if overwrite:
                self.stipple_dict[name] = lines
                print(f'Overwriting stipple: {name}')
            else:
                print(f'DID NOT overwrite stipple: {name}')
        else:
            self.stipple_dict[name] = lines

    def add_linestyle(self, name, line, overwrite=True):
        if name in self.line_dict:
            if overwrite:
                self.line_dict[name] = line
                print(f'Overwriting line: {name}')
            else:
                print(f'DID NOT overwrite line: {name}')
        else:
            self.line_dict[name] = line

    def output_drf(self, filepath):

        with open(filepath, 'w') as f:
            f.write(f'drDefineDisplay(\n'
                    f' ( display       )\n'
                    f' ( versatecc     )\n'
                    f')\n\n')

            f.write(f'drDefineColor(\n')
            for color in self.color_dict:
                f.write(f'{self.color_dict[color]}')
            f.write(f')\n\n')

            f.write(f'drDefineStipple(\n')
            for stipple in self.stipple_dict:
                f.writelines(self.stipple_dict[stipple])
            f.write(f')\n\n')

            f.write(f'drDefineLineStyle(\n')
            for linestyle in self.line_dict:
                f.write(f'{self.line_dict[linestyle]}')
            f.write(f')\n\n')

            f.write(f'drDefinePacket(\n')
            for packet in self.info_list:
                tab = '\t'
                f.write(f' (\t{tab.join(packet.color_props)}\t)\n')
            f.write(f')\n\n')


def parse_tech_file(tech_file: str,
                    layer_info_list: "LayerInfoList" = None,
                    ) -> "LayerInfoList":
    """
    Parses a techfile to grab its techDisplays information

    Parameters
    ----------
    tech_file : str
        The filepath to the techfile.
    layer_info_list : LayerInfoList
        If passed, store layer data in the passed structure. If not passed, return a new LayerInfoList

    Returns
    -------
    layer_info_list : LayerInfoList
        A LayerInfoList with updated entries for the display packet name of the cad lpps that appear in the passed
        techfile
    """
    passed_layer_info_list = (layer_info_list is not None)
    if layer_info_list is None:
        layer_info_list = LayerInfoList()

    display_section_start_regex = re.compile(r'^\s*techDisplays\(')
    display_section_end_regex = re.compile(r'^\s*\)')

    display_line_regex = re.compile(r'^\s*\(\s*(\w+)\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)\s*\)')

    is_line_valid = False
    with open(tech_file, 'r') as f:
        for line in f:
            # Get rid of comments
            line_nocomment = line.split(';')[0]
            # start searching for the beginning of the techDisplays section
            if re.match(display_section_start_regex, line_nocomment):
                # once found, we should treat the next lines as valid display values
                is_line_valid = True
            elif is_line_valid and re.match(display_section_end_regex, line):
                is_line_valid = False
            elif is_line_valid:
                line_match = re.match(display_line_regex, line_nocomment)
                if line_match:
                    (cad_lay, cad_purpose, packet_name) = line_match.group(1), line_match.group(2), line_match.group(3)

                    if passed_layer_info_list:
                        raise ValueError('not yet implemented')
                    else:
                        layer_info = LayerInfo(
                            cad_layer=cad_lay,
                            cad_purpose=cad_purpose,
                            display_packet=f'display__{packet_name}',
                        )

                        layer_info_list.append_unique_layerinfo(layer_info)

    return layer_info_list


def parse_drf_file(drf_file: str,
                   layer_info_list: "LayerInfoList" = None,
                   ) -> "LayerInfoList":
    """
    Parses a drf file to grab its display information

    Parameters
    ----------
    drf_file : str
        The filepath to the drf file.
    layer_info_list : LayerInfoList
        If passed, store layer data in the passed structure. If not passed, return a new LayerInfoList

    Returns
    -------
    layer_info_list : LayerInfoList
        A LayerInfoList with updated entries for the display information of the display_packets that appear in
        the passed drf file
    """
    passed_layer_info_list = (layer_info_list is not None)
    if layer_info_list is None:
        layer_info_list = LayerInfoList()

    packet_section_start = re.compile(r'^\s*drDefinePacket\(')
    packet_section_end = re.compile(r'^\s*\)')
    stipple_section_start = re.compile(r'^\s*drDefineStipple\(')
    stipple_section_end = re.compile(r'^\s*\)')
    color_section_start = re.compile(r'^\s*drDefineColor\(')
    color_section_end = re.compile(r'^\s*\)')
    line_section_start = re.compile(r'^\s*drDefineLineStyle\(')
    line_section_end = re.compile(r'^\s*\)')


    # ( DisplayName  PacketName           Stipple    LineStyle  Fill       Outline    [FillStyle])
    packet_regex = re.compile(r'^\s*\(\s*(\w+)\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)?\s*\)')

    packet_section = False
    stipple_section = False
    color_section = False
    line_section = False
    stipple_paren_count = 0
    current_lines = []
    current_stipple_name = None

    current_section = None

    with open(drf_file, 'r') as f:
        for linenum, line in enumerate(f):

            # Get rid of comments
            line_nocomment = line.split(';')[0]
            if len(line_nocomment) == 0:
                continue

            # Figure out which section of code we are in
            if re.match(packet_section_start, line_nocomment):
                packet_section = True
                current_section = 'packet'
                continue
            elif re.match(stipple_section_start, line_nocomment):
                stipple_section = True
                current_section = 'stipple'
                continue
            elif re.match(color_section_start, line_nocomment):
                color_section = True
                current_section = 'color'
                continue
            elif re.match(line_section_start, line_nocomment):
                line_section = True
                current_section = 'line'
                continue
            elif re.match(line_section_end, line_nocomment) and line_section:
                line_section = False
                current_section = None
                continue
            elif re.match(color_section_end, line_nocomment) and color_section:
                color_section = False
                current_section = None
                continue
            elif re.match(stipple_section_end, line_nocomment) and stipple_section and stipple_paren_count == 0:
                stipple_section = False
                current_section = None
                continue
            elif re.match(packet_section_end, line_nocomment) and packet_section:
                packet_section = False
                current_section = None
                continue

            if int(packet_section) + int(stipple_section) + int(color_section) + int(line_section) > 1:
                raise ValueError(f'Should not get here')

            if current_section == 'packet':
                line_match = re.match(packet_regex, line_nocomment)

                if line_match:
                    matches = line_match.groups()
                    # (displayname, packet_name, stipple, linestyle, fill, outline, fillstyle)
                    color_props = \
                        (matches[0], matches[1], matches[2], matches[3], matches[4], matches[5],
                         '' if matches[6] is None else matches[6])

                    packet_id = f'{color_props[0]}__{color_props[1]}'
                    if passed_layer_info_list:
                        # If an LPP uses this color packet, assign the color properties
                        layers_with_packet = layer_info_list.has_display_packet(packet_id)
                        if layers_with_packet:
                            for layer in layers_with_packet:
                                layer.color_props = color_props
                                # layer_info_list.has_display_packet(packet_id).color_props = color_props
                                #  layer_info_list.has_display_packet(packet_id).display_packet = packet_id

                        else:
                            layer_info = LayerInfo(
                                display_packet=packet_id,
                                color_props=color_props,
                            )

                            layer_info_list.append_unique_layerinfo(layer_info)
                    else:
                        layer_info = LayerInfo(
                            display_packet=packet_id,
                            color_props=color_props,
                        )

                        layer_info_list.append_unique_layerinfo(layer_info)

            if current_section == 'stipple':
                if stipple_paren_count == 0:
                    current_lines = []
                    line_split = line_nocomment.split()
                    current_stipple_name = f'{line_split[1]}__{line_split[2]}'
                current_lines.append(line_nocomment)

                stipple_paren_count += (line_nocomment.count('(') - line.count(')'))

                if stipple_paren_count == 0:
                    layer_info_list.add_stipple(name=current_stipple_name,
                                                lines=current_lines,
                                                overwrite=True)

            if current_section == 'color':
                line_split = line_nocomment.split()
                color_name = f'{line_split[1]}__{line_split[2]}'
                layer_info_list.add_color(name=color_name,
                                          line=line_nocomment,
                                          overwrite=True)

            if current_section == 'line':
                line_split = line_nocomment.split()
                line_name = f'{line_split[1]}__{line_split[2]}'
                layer_info_list.add_linestyle(name=line_name,
                                              line=line_nocomment,
                                              overwrite=True)

    return layer_info_list


if __name__ == '__main__':
    base_gf_techpath = '/tools/gftech12/local/mod/V1.0_1.2/cdslib/45RFSOI_mod/techfile_8LM_3Mx_2Cx_1Ux_1Ox_LD.tf'
    base_gf_displaypath = '/tools/gftech12/local/mod/V1.0_1.2/cdslib/45RFSOI_mod/display_mod.drf'

    new_gf_techpath = '/tools/gftech45s/45SPCLO/V0.5_2.1/DesignEnv/VirtuosoOA/libs/45spclo/techfile_51201.tf'
    new_gf_displaypath = '/tools/gftech45s/45SPCLO/V0.5_2.1/DesignEnv/VirtuosoOA/setup/display.drf'

    outfile = 'gf45spclo_photonics/display/display.drf'

    base_tech_info = parse_tech_file(base_gf_techpath)
    base_tech_info = parse_drf_file(base_gf_displaypath, base_tech_info)

    new_tech_info = parse_tech_file(new_gf_techpath)
    new_tech_info = parse_drf_file(new_gf_displaypath, new_tech_info)

    name_diff = []

    # New and old packet names match very well. Simply update each packet's color information from the base tech.
    for layer_info in new_tech_info.info_list:
        # If the same cad layer exists in the reference information
        if base_tech_info.has_display_packet(layer_info.display_packet):
            base_layer_info = base_tech_info.has_display_packet(layer_info.display_packet)[0]

            new_color_props = layer_info.color_props
            original_color_props = base_layer_info.color_props

            # Update the new tech info with the original color packet information
            # (but dont change the packet name, just the color props)
            if new_color_props != original_color_props:

                print(f'Replacing packet:  {layer_info.display_packet}\n'
                      f'    {new_color_props}  -->  {original_color_props}\n')
                layer_info.color_props = original_color_props

        # Old way replaced packet name + color info based on cad purpose. Not needed.
        # if layer_info.cad_lpp != (None, None):
        #     # If the same cad layer exists in the reference information
        #     if base_tech_info.has_cad_lpp(layer_info.cad_lpp):
        #         base_layer_info = base_tech_info.has_cad_lpp(layer_info.cad_lpp)
        #
        #         new_color_packet_name = layer_info.display_packet
        #         original_color_packet_name = base_layer_info.display_packet
        #
        #         new_color_props = layer_info.color_props
        #         original_color_props = base_layer_info.color_props
        #
        #         # Update the new tech info with the original color packet information
        #         # (but dont change the packet name, just the color props)
        #         if new_color_packet_name != original_color_packet_name or new_color_props != original_color_props:
        #
        #             print(f'Replacing packet:  {layer_info.cad_lpp}\n'
        #                   f'    {new_color_props}  -->  {original_color_props}\n'
        #                   f'    {new_color_packet_name}  --> {original_color_packet_name}')
        #             layer_info.color_props = original_color_props
        #
        #             if new_color_packet_name != original_color_packet_name:
        #                 name_diff.append((new_color_packet_name, original_color_packet_name, layer_info.cad_lpp))

    # Replace new colors with original style
    for color, new_color_info in new_tech_info.color_dict.items():
        if color in base_tech_info.color_dict:
            base_color_info = base_tech_info.color_dict[color]
            if new_color_info != base_color_info:
                print(f'Replacing color {color}')
                new_tech_info.color_dict[color] = base_color_info

    # Replace new stipples with original style
    for stipple, new_stipple_info in new_tech_info.stipple_dict.items():
        if stipple in base_tech_info.stipple_dict:
            base_stipple_info = base_tech_info.stipple_dict[stipple]
            new_stipple_str = ''.join(new_stipple_info)
            base_stipple_str = ''.join(base_stipple_info)
            if new_stipple_str != base_stipple_str:
                print(f'Replacing stipple {stipple}')
                new_tech_info.stipple_dict[stipple] = base_stipple_info

    # Add original colors and stipples that werent in the new file but are now referenced
    for color, base_color_info in base_tech_info.color_dict.items():
        if color not in new_tech_info.color_dict.keys():
            new_tech_info.color_dict[color] = base_color_info
            print(f'Adding missing color: {color}')
    for linestyle, base_linestyle_info in base_tech_info.line_dict.items():
        if linestyle not in new_tech_info.line_dict.keys():
            new_tech_info.line_dict[linestyle] = base_linestyle_info
            print(f'Adding missing linestyle: {linestyle}')
    for stipple, base_stipple_info in base_tech_info.stipple_dict.items():
        if stipple not in new_tech_info.stipple_dict.keys():
            new_tech_info.stipple_dict[stipple] = base_stipple_info
            print(f'Adding missing stipple: {stipple}')



    new_tech_info.output_drf(outfile)
