import BPG
from layout.Single_ring_fullrib.ring import RingBase
from layout.Single_ring_fullrib.ringheater import RingHeater


class RingWithHeaterBase(BPG.PhotonicTemplateBase):
    """
    Ring-heater Design Script class
    """

    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)

        # Declare access length so it can be accessed by higher level scripts
        self.access_length = None

    @classmethod
    def get_default_param_values(cls):
        return dict(
            drop_slot=-1,  # Do not have a drop port by default
            bottom_electrode_label_layer=None,  # Do not place a label on the bottom metal layer
            heater_electrode_bottom_x_span=None,
            heater_electrode_bottom_y_span=None,
            ring_label='Contact',
            heater_label='Heat',
            heater_disable=False,
        )

    @classmethod
    def get_params_info(cls):  # Returns definition of the parameters.
        return dict(
            # Ring params
            # Standard parameters
            rout='Outer radius of ring',
            ring_width='Ring width',
            layer='Layer or LPP of the main ring and spokes',
            doping_spoke_info='List of spoke doping dictionaries containing: rout, rin, num, layer, '
                              'spoke_width_percentage, spoke_offset',
            extra_ring_info='List of extra ring dictionaries containing: rout, ring_width, layer',
            spoke_num='Number of n or p spokes (total spoke number is 2x this value',
            coupling_slot='Ring to access waveguide gap.',
            drop_slot='Ring to drop port gap',
            wg_width='Width of the access waveguide.',
            ring_label='Ring contact label text [str], or dictionary with keys P: <p_label> and N: <n_label>',

            outer_electrode_ring_layers='Ordered list of LPPs (bot to top) on which outer electrode ring is drawn.',
            inner_electrode_ring_layers='Ordered list of LPPs (bot to top) on which inner electrode ring is drawn.',

            # Advanced parameters: can change between designs per technology, but not recommended for standard users
            access_length='Length of the cosine-curved access wavelength',
            p_via_radius_offset='P via radius offset of ring device. If p_via_radius_offset > n_via_radius_offset, '
                                'inner electrode will be P, and the P silicon spokes will be longer.',
            n_via_radius_offset='N via radius offset of ring device. If p_via_radius_offset > n_via_radius_offset, '
                                'inner electrode will be P, and the P silicon spokes will be longer.',
            high_doping_rout_offset='Offset of outer high doping radius (distance from ring inner radius to outer '
                                    'high doping radius). Positive offset decreases outer radius.',
            high_doping_rin_offset='Offset of the inner high doping radius (radius of the inner edge of the high '
                                   'doping region). Positive offset decreases inner radius.',
            electrode_offset='Electrode offset away from the via locations',
            electrode_width_inner='Width of the inner electrode ring',
            electrode_width_outer='Width of the outer electrode ring',
            drop_taper_length='Length of the tapers on the drop port',
            salicide_radius_extension='Extra amount that should be added to the salicide disk covering the center of '
                                      'the ring (spoke tips).',
            high_doping_n_rin_offset='Offset of the inner radius high n doping region around the silicon contact '
                                     'spokes. Positive value makes rin of this doping larger (further from ring '
                                     'center). Used to space high n doping of spoke from high n doping of any central '
                                     'heater.',

            # Advanced tech params: should not need to change between designs in a given technology
            high_p_doping_layer='LPP for the high p doping silicon contacts',
            high_n_doping_layer='LPP for the high n doping silicon contacts',
            salicide_lpp='LPP for the salicide region for making low resistance silicon contacts',
            bottom_metal_electrode_layer='LPP for the bottom electrode layer in the stack (should be the BAG '
                                         'equivalent metal layer of the layer parameter).',
            bottom_electrode_label_layer='LPP for the layer on which an electrode label should be placed. '
                                         'If not provided, no bottom label is drawn.',

            # Heater params
            # Standard params
            heater_disable='True to not place the heater. Defaults to False (ie heater is present).',
            heater_radius_offset='Offset of outer heater radius from inner ring radius',
            resistance='Resistance target for the heater',
            contact_dist='Distance between two inner edges of the two interior spokes that contact the heater ring.',
            contact_width='Width of interior contact spokes that connect the heater ring to the via stack',
            heater_device_layer='LPP of ring heater device (ie layer of the actual heater)',
            heater_disk_layers='List of additional LPPs on which disks covering the entire ring heater will be drawn',
            heater_electrode_top_layer='LPP of top metal layer of the gs electrode',
            heater_electrode_top_x_span='Electrode x-span on the top electrode metal layer (defaults to 1)',
            heater_electrode_top_y_span='Electrode y-span on the top electrode metal layer (defaults to 1)',
            heater_label='Electrode contact label text [str], or dictionary with keys P: <p_label> and N: <n_label>',
            heater_electrode_bottom_x_span='Electrode x-span on the bottom electrode metal '
                                           'layer (defaults to contact_width)',
            heater_electrode_bottom_y_span='Electrode y-span on the bottom electrode metal '
                                           'layer (defaults to contact_width)',
            # Advanced parameters
            heater_disk_layer_extension='Size by which disk_layers should be drawn beyond outer radius of heater ring',
            # Technology parameter
            heater_electrode_bottom_layer='LPP for the bottom electrode layer in the stack (should be the BAG '
                                          'equivalent layer of device_layer)',

        )

    def draw_layout(self):
        # Set the ring parameters
        ring_params = dict(
            # Standard parameters
            rout=self.params['rout'],
            ring_width=self.params['ring_width'],
            layer=self.params['layer'],
            doping_spoke_info=self.params['doping_spoke_info'],
            extra_ring_info=self.params['extra_ring_info'],
            spoke_num=self.params['spoke_num'],
            coupling_slot=self.params['coupling_slot'],
            drop_slot=self.params['drop_slot'],
            wg_width=self.params['wg_width'],
            label=self.params['ring_label'],

            outer_electrode_ring_layers=self.params['outer_electrode_ring_layers'],
            inner_electrode_ring_layers=self.params['inner_electrode_ring_layers'],

            # Advanced parameters: can change between designs per technology, but not recommended for standard users
            access_length=self.params['access_length'],
            p_via_radius_offset=self.params['p_via_radius_offset'],
            n_via_radius_offset=self.params['n_via_radius_offset'],
            high_doping_rout_offset=self.params['high_doping_rout_offset'],
            high_doping_rin_offset=self.params['high_doping_rin_offset'],
            electrode_offset=self.params['electrode_offset'],
            electrode_width_inner=self.params['electrode_width_inner'],
            electrode_width_outer=self.params['electrode_width_outer'],
            drop_taper_length=self.params['drop_taper_length'],
            salicide_radius_extension=self.params['salicide_radius_extension'],
            high_doping_n_rin_offset=self.params['high_doping_n_rin_offset'],


            # Advanced tech params: should not need to change between designs in a given technology
            high_p_doping_layer=self.params['high_p_doping_layer'],
            high_n_doping_layer=self.params['high_n_doping_layer'],
            salicide_lpp=self.params['salicide_lpp'],
            bottom_metal_electrode_layer=self.params['bottom_metal_electrode_layer'],
            bottom_electrode_label_layer=self.params['bottom_electrode_label_layer'],
        )

        heater_params = dict(
            rout=(self.params['rout'] - self.params['ring_width'] -
                  max(self.params['p_via_radius_offset'], self.params['n_via_radius_offset']) -
                  self.params['heater_radius_offset']),
            resistance=self.params['resistance'],
            contact_dist=self.params['contact_dist'],
            contact_width=self.params['contact_width'],
            device_layer=self.params['heater_device_layer'],
            disk_layers=self.params['heater_disk_layers'],
            electrode_top_layer=self.params['heater_electrode_top_layer'],
            electrode_top_x_span=self.params['heater_electrode_top_x_span'],
            electrode_top_y_span=self.params['heater_electrode_top_y_span'],
            electrode_label=self.params['heater_label'],
            disk_layer_extension=self.params['heater_disk_layer_extension'],
            electrode_bottom_layer=self.params['heater_electrode_bottom_layer'],
        )

        # Assign dynamic defaults to heater electrode bottom span
        if self.params['heater_electrode_bottom_x_span'] is None:
            heater_params['electrode_bottom_x_span'] = heater_params['contact_width']
        else:

            heater_params['electrode_bottom_x_span'] = self.params['heater_electrode_bottom_x_span']
        if self.params['heater_electrode_bottom_y_span'] is None:
            heater_params['electrode_bottom_y_span'] = heater_params['contact_width']
        else:
            heater_params['electrode_bottom_y_span'] = self.params['heater_electrode_bottom_y_span']

        # Add ring instance
        ring_master = self.new_template(params=ring_params, temp_cls=RingBase)
        ring_inst = self.add_instance(master=ring_master)

        # Add the heater if it should be present
        if not self.params['heater_disable']:
            # Compute the width from the heater resistance design function
            heater_params['width'] = RingHeater.design_heater_width_from_resistance(
                resistance=heater_params['resistance'],
                heater_rout=heater_params['rout'],
                r_square=self.photonic_tech_info.sheet_resistance(heater_params['device_layer']),
                contact_width=heater_params['contact_width'],
                contact_dist=heater_params['contact_dist'],
            )
            heater_master = self.new_template(params=heater_params, temp_cls=RingHeater)
            self.add_instance(master=heater_master)

        # Extract
        self.extract_photonic_ports(
            inst=ring_inst,
            port_names=['PORT0', 'PORT1'],
        )

        self.access_length = ring_master.access_length


if __name__ == '__main__':
    spec_file = 'layout/Single_ring_fullrib/specs/ring_with_heater_specs.yaml'
    plm = BPG.PhotonicLayoutManager(spec_file)
    plm.generate_content()
    plm.generate_gds()
    plm.dataprep_calibre()

