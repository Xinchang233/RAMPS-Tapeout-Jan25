import re
import yaml
import os
from pathlib import Path

from typing import List, Dict, Tuple


class KlayoutLayer(dict):
    items = ['frame-color', 'fill-color', 'frame-brightness', 'fill-brightness', 'dither-pattern',
             'valid', 'visible', 'transparent', 'width', 'marked', 'animation', 'name', 'source']
    # < frame-color >  # 7d0000</frame-color>
    # <fill-color>#7d0000</fill-color>
    # <frame-brightness>0</frame-brightness>
    # <fill-brightness>0</fill-brightness>
    # <dither-pattern>C52</dither-pattern>
    # <line-style/><valid>true</valid>
    # <visible>true</visible>
    # <transparent>false</transparent>
    # <width>1</width>
    # <marked>false</marked>
    # <xfill>false</xfill>
    # <animation>0</animation>
    # <name>rx free - 41/200</name>
    # <source>41/200@1</source>

    def __init__(self,
                 layer_text: str,
                 ):
        prop_dict = dict()
        for prop_name in self.items:
            matches = re.search(f'<{prop_name}>(.*)</{prop_name}>', layer_text)
            prop_dict[prop_name] = matches.group(1)

        kv_iter = ((key, prop_dict.get(key, [])) for key in self.items)
        dict.__init__(self, kv_iter)

        # gds_lpp = prop_dict['name'].split(' ')[0]
        # self['lpp_name'] = (gds_lpp.split('.')[0].lower(), gds_lpp.split('.')[1].lower())
        self['lpp_name'] = prop_dict['name']

        gds_numbers = prop_dict['source']
        gds_numbers = gds_numbers.split('@')[0]  # Strip the @1
        self['gds_pair'] = (int(gds_numbers.split('/')[0]), int(gds_numbers.split('/')[1]))

    def printlines(self) -> List[str]:
        outlines = []
        for propname in self.items:
            outlines.append(f'<{propname}>{self[propname]}</{propname}>')
        return outlines


def parse_lyp_for_layers(filepath) -> Dict[Tuple[int, int], KlayoutLayer]:
    """
    Parse an existing .lyp and return a dict with one entry for each klayout layer
    """

    # Read in all the lines
    with open(filepath, 'r') as ff:
        lines = ff.readlines()

    # Strip lines of any spaces
    for ind, line in enumerate(lines):
        lines[ind] = line.strip()

    # Merge lines
    all_text = ''.join(lines)

    all_search_results = list()
    # Find any standalone layer objects. This will capture layer groups as well
    search_string = r'<properties>(.*?)</properties>'
    # Find each layer entry
    search_results = re.findall(search_string, all_text)

    # Filter out the layer groups, the catch-all at the end, and empty groups
    for result in search_results:
        if 'group-members' not in result and '<source>*/*@*</source>' not in result and '<source>' in result:
            all_search_results.append(result)

    # Now find layer object entries in any layer groups
    search_string = r'<group-members>(.*?)</group-members>'
    # Find each layer entry
    search_results = re.findall(search_string, all_text)

    all_search_results.extend(search_results)

    # Create a dictionary for each layer's klayout properties
    all_layers = dict()
    for result in all_search_results:
        try:
            layer_obj = KlayoutLayer(result)

            if layer_obj['gds_pair'] in all_layers:
                raise ValueError(f'GDS layer {layer_obj["gds_pair"]} is duplicated in source lyp.')

            all_layers[layer_obj['gds_pair']] = layer_obj
        except:
            raise ValueError(f'Layer did not produce a valid klayout object:  {result}')

    return all_layers


def parse_lyp_for_stipples(filepath) -> list:
    # search_string = r'(<custom-dither-pattern>.*?</custom-dither-pattern>)'
    # r'(<custom-dither-pattern>.*?</custom-dither-pattern>)'
    search_string = r'(<custom-dither-pattern>.*?</custom-dither-pattern>)'

    # Read in all the lines
    with open(filepath, 'r') as ff:
        lines = ff.readlines()

    for ind, line in enumerate(lines):
        lines[ind] = line.strip()
    all_text = ''.join(lines)

    search_results = re.findall(search_string, all_text, re.DOTALL)

    final_results = list()

    for dither_ind, dither_str in enumerate(search_results):
        dither_str_list = dither_str.split('><')
        for ind, line in enumerate(dither_str_list):
            if ind == 0:
                dither_str_list[ind] = f'{line}>'
            elif ind == len(dither_str_list) - 1:
                dither_str_list[ind] = f'<{line}'
            else:
                dither_str_list[ind] = f'<{line}>'
        final_results.extend(dither_str_list)

    return final_results


def get_layer_order(filepath):
    with open(filepath, 'r') as ff:
        layer_ordering = yaml.load(ff)

    return layer_ordering['layer_groups']


def create_dummy_lyp_entry(lpp_name, gds_lpp):
    return [
        f' <frame-color>#00FFFF</frame-color>',
        f' <fill-color>#00FFFF</fill-color>',
        f' <frame-brightness>0</frame-brightness>',
        f' <fill-brightness>0</fill-brightness>',
        f' <dither-pattern>C47</dither-pattern>',
        f' <valid>true</valid>',
        f' <visible>true</visible>',
        f' <transparent>false</transparent>',
        f' <width>1</width>',
        f' <marked>false</marked>',
        f' <animation>0</animation>',
        f' <name>{lpp_name[0]}.{lpp_name[1]}</name>',
        f' <source>{gds_lpp[0]}/{gds_lpp[1]}@1</source>',
    ]


def sort_layers_and_export(dict_of_klayout_layer_obj: Dict[tuple, "KlayoutLayer"],
                           ordering_list: List[dict],
                           stipples_lines: list
                           ):

    used_layer_gds_lpps = list()

    outlines = list()
    outlines.append('<?xml version="1.0" encoding="utf-8"?>')
    outlines.append('<layer-properties>')

    newly_added_layers = list()


    # Check that all GDS layers appear in the grouping file
    all_groupfile_entries = []
    for group in ordering_list:
        entries = group.get('entries', [])
        if entries is None:
            entries = []
        for entry in entries:
            if isinstance(entry, dict):
                all_groupfile_entries.append(list(entry.keys())[0])
            else:
                all_groupfile_entries.append(entry)

    all_groupfile_entries_set = set(all_groupfile_entries)
    if len(all_groupfile_entries) != len(all_groupfile_entries_set):
        print(f'Grouping file contains duplicate entries:')
        tmp = []
        for el in all_groupfile_entries:
            if el not in tmp:
                tmp.append(el)
            else:
                print(el)
        raise ValueError('Grouping file contains duplicate entries.')

    all_layermap_entires = set(gds_layermap.keys())

    if len(all_layermap_entires - all_groupfile_entries_set) > 0:
        raise ValueError(f'Not all GDS layers appear in grouping file:\n'
                         f'{all_layermap_entires - all_groupfile_entries_set}')

    # Go through the display groups
    for group in ordering_list:
        # Get name
        outlines.append(f' <properties>')
        outlines.append(f'  <name>{group["groupname"]}</name>')
        if group.get('visible', True):
            outlines.append(f'  <visible>true</visible>')
        else:
            outlines.append(f'  <visible>false</visible>')

        entries = group.get('entries', [])
        if entries is None:
            entries = []
        for lpp_entry in entries:
            # lpp_entry is either a dict that contains special attributes, or is just a tuple of lpp name strings
            if isinstance(lpp_entry, dict):
                lpp_name_tuple = list(lpp_entry.keys())[0]
            else:
                lpp_name_tuple = lpp_entry

            # Get gds number of lpp layer name, and convert to tuple.
            try:
                entry_gds_lpp = gds_layermap[lpp_name_tuple]
                entry_gds_lpp = (entry_gds_lpp[0], entry_gds_lpp[1])
                used_layer_gds_lpps.append(entry_gds_lpp)

                # Try to map existing GDS LPP to entry in the non-grouped LPP list
                try:
                    lpp_obj = dict_of_klayout_layer_obj[entry_gds_lpp]
                    if isinstance(lpp_entry, dict):
                        lpp_entry_values = list(lpp_entry.values())[0]
                        if lpp_entry_values is not None and 'name' in lpp_entry_values:
                            lpp_obj['name'] = lpp_entry_values['name'] + f' - {entry_gds_lpp[0]}/{entry_gds_lpp[1]}'

                    outlines.append(f'   <group-members>')
                    for line in lpp_obj.printlines():
                        outlines.append('    ' + line)
                    outlines.append(f'   </group-members>')
                except KeyError:
                    newlines = create_dummy_lyp_entry(lpp_name=lpp_name_tuple,
                                                      gds_lpp=entry_gds_lpp)
                    outlines.append(f'   <group-members>')
                    for line in newlines:
                        outlines.append('    ' + line)
                    outlines.append(f'   </group-members>')

                    print(f'Warning type 1: Layer appears in KLayout Layer Grouping file, '
                          f'but does not appear in the template Klayout layerprop file:\n'
                          f'    GDS {entry_gds_lpp} = LPP {lpp_name_tuple} \n'
                          f'  Added dummy layer entry')
                    newly_added_layers.append(f'GDS: {entry_gds_lpp}       LPP:  {lpp_name_tuple}\n')

            except KeyError:
                print(f'Warning type 2: Layer appears in KLayout Layer Grouping file, '
                      f'but does not appear in the GDS layermap:  \n  '
                      f'    GDS {entry_gds_lpp} , LPP {lpp_name_tuple} ')

        outlines.append(f' </properties>')

    # Go through all the LPPs in the template lyp, and add them to the output KLayout LYP without any grouping
    for layer_gds_lpp, layer_info_obj in dict_of_klayout_layer_obj.items():
        # If we haven't yet added the LPP to a group, add it to the end
        if layer_gds_lpp not in used_layer_gds_lpps:
            used_layer_gds_lpps.append(layer_gds_lpp)

            outlines.append(f' <properties>')
            for line in layer_info_obj.printlines():
                outlines.append('  ' + line)
            outlines.append(f' </properties>')

            print(f'Info type 1: Layer appears in template KLayout layerprop file, ',
                  f'but does not appear in the KLayout Layer Grouping file:\n'
                  f'    GDS {layer_gds_lpp} = LPP {layer_info_obj["name"]} ')

    outlines.extend([
        f' <properties>',
        f'  <source>*/*@*</source>',
        f' </properties>'
    ])
    outlines.append(f' <name/>')
    outlines.extend(stipples_lines)
    outlines.append(f'</layer-properties>')

    # Warning for layers that are in the gds layermap file, but do not have an entry in the output layermap file
    # Should update the template
    for layer_lpp, gds_lpp in gds_layermap.items():
        if (gds_lpp[0], gds_lpp[1]) not in used_layer_gds_lpps:
            print(f'Warning type 3: Layer appears in the GDS layermap, '
                  f'but does not appear in the output KLayout layerprop file:\n'
                  f'    GDS Layer ({gds_lpp[0]}, {gds_lpp[1]})  =  ({layer_lpp[0]}, {layer_lpp[1]})')

    # Write template file of the missing lines
    with open('gf45spclo_photonics/display/newly_added_layers.lyp', 'w') as f:
        for line in newly_added_layers:
            f.write(line + '\n')

    return outlines


if __name__ == '__main__':
    # GDS map
    gds_layermap_file = Path(os.environ['BAG_WORK_DIR']) / 'gf45spclo_photonics/gds_map_generated.yaml'
    # KLayout group file
    klayout_group_file = 'gf45spclo_photonics/display/KLayout_groups.yaml'

    # Input layerproperties file. Should be the most recent 'golden' lyp file in use.
    starting_layerprop_file = 'gf45spclo_photonics/display/KLayout_layerprops_CLO_grouped.lyp'

    # Name of generated output file
    outfile = 'gf45spclo_photonics/display/KLayout_layerprops_CLO_grouped_out.lyp'

    # Get the GDS layermap
    with open(gds_layermap_file, 'r') as f:
        gds_file_info = yaml.load(f)
        gds_layermap: Dict[Tuple[str, str], List[int]] = gds_file_info['layer_map']

    # Get the template's layer properties
    layers = parse_lyp_for_layers(starting_layerprop_file)
    # Get the template's stipples
    stipples = parse_lyp_for_stipples(starting_layerprop_file)

    # Get the group ordering
    ordering = get_layer_order(klayout_group_file)

    # Perform the sorting and error checking
    lines_to_write = sort_layers_and_export(dict_of_klayout_layer_obj=layers,
                                            ordering_list=ordering,
                                            stipples_lines=stipples)

    # Write the output file
    with open(outfile, 'w') as tempfile:
        tempfile.write('\n'.join(lines_to_write))
