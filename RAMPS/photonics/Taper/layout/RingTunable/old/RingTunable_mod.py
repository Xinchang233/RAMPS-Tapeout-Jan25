import BPG
import importlib
# from Photonic_Core_Layout.AdiabaticPaths.AdiabaticPaths import AdiabaticPaths
from BPG.gds.io import GDSImport
from Photonic_Core_Layout.ViaStack.ViaStack import ViaStack
from BPG.objects import PhotonicRect, PhotonicRound, PhotonicPolygon
from bag.layout.util import BBox
from math import floor


class RingTunable(BPG.PhotonicTemplateBase):
    """
    This class creates
    """

    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)

        self.ring_on = params['ring_on']

        if self.ring_on:
            self.ring_rout = params['ring_rout']
            self.ring_width = params['ring_width']
            self.ring_layer = params['ring_layer']
        else:
            self.ring_rout = None
            self.ring_width = None
            self.ring_layer = None

        self.heater_rout = params['heater_rout']
        self.heater_width = params['heater_width']
        self.heater_layer = params['heater_layer']

        self.doping_layer = params['doping_layer']

        if self.ring_on:
            self.slab_on = params['slab_on']
            if self.slab_on:
                self.slab_layer = params['slab_layer']
            else:
                self.slab_layer = None
        else:
            self.slab_on = False

        self.top_cover_box_layer = params['top_cover_box_layer']

        self.wg_in_length = params['wg_in_length']
        self.wg_in_width = params['wg_in_width']
        self.wg_in_gap = params['wg_in_gap']

        self.wg_out_length = params['wg_out_length']
        self.wg_out_width = params['wg_out_width']
        self.wg_out_gap = params['wg_out_gap']

        self.dr = params['dr']

        self.extra_ring_info = params['extra_ring_info']  # list of dictionaries with rout, width, layer
        # self.extra_ring_info = [{'rout': 10, 'width': 2, 'layer': ('KG', 'drawing')}]

        self.via_stack_spacing_from_heater = params['via_stack_spacing_from_heater']
        self.via_stack_enclosure_vert = params['via_stack_enclosure_vert']
        self.via_stack_enclosure_horiz = params['via_stack_enclosure_horiz']
        self.via_stack_gds_name = params['via_stack_gds_name']

        self.via_stack_spacing_from_heater = params['via_stack_spacing_from_heater']
        self.via_stack_enclosure_vert = params['via_stack_enclosure_vert']
        self.via_stack_enclosure_horiz = params['via_stack_enclosure_horiz']
        self.via_stack_gds_name = params['via_stack_gds_name']

        self.pads_on = params['pads_on']

        if self.pads_on:

            self.pad_pitch = params['pad_pitch']
            self.pad_width = params['pad_width']
            self.pad_height = params['pad_height']

            self.pad_horizontal_shift_left  = params.get('pad_horizontal_shift_left',  0.0)

            if abs(self.pad_horizontal_shift_left)>0.001:
                self.pad_horizontal_shift_left_position = params['pad_horizontal_shift_left_position']
            else:
                self.pad_horizontal_shift_left_position = 0.0

            self.pad_horizontal_shift_right = params.get('pad_horizontal_shift_right', 0.0)

            if abs(self.pad_horizontal_shift_right)>0.001:
                self.pad_horizontal_shift_right_position  = params['pad_horizontal_shift_right_position']
            else:
                self.pad_horizontal_shift_right_position = 0.0

            self.pad_metal_layer = params['pad_metal_layer']
            self.pad_open_layer  = params['pad_open_layer']
            self.pad_open_inclusion  = params['pad_open_inclusion']

            self.pad_left_on  = params.get('pad_left_on',  True)
            self.pad_right_on = params.get('pad_right_on', True)

            self.pads_type = params['pads_type']

            if self.pads_type == 'going_up':

                self.intermediate_metal_layer = params['intermediate_metal_layer']
                self.intermediate_metal_length = params['intermediate_metal_length']
                self.intermediate_to_routing_length = params['intermediate_to_routing_length']

                self.routing_metal_layer = params['routing_metal_layer']
                self.routing_wire_spacing = params['routing_wire_spacing']
                self.routing_wire_width = params['routing_wire_width']

                self.pad_edge_distance = params['pad_edge_distance']

            else:
                raise ValueError('Pad routing type is not recognized')
        else:
            self.pad_pitch = None
            self.pad_width = None
            self.pad_height = None
            self.pad_metal_layer = None
            self.pad_open_layer  = None
            self.pad_open_inclusion  = None
            self.pads_type = None

#        self.rout = params['rout']

    @classmethod
    def get_params_info(cls) -> dict:

        return dict(
            ring_on='True/False -- whether to include a light ring with (possibly) input/output waveguides. Note that the "light" ring is the ring which carries light, it"s different from the heater ring which carries current.',
            ring_rout='outer radius of the light ring',
            ring_width = 'width of the light ring',
            ring_layer = 'layer of the light ring',
            heater_rout = 'outer radius of the heater ring',
            heater_width = 'width of the heater ring',
            heater_layer = 'layer of the heater ring; typically both heater ring and light ring are both in Si',
            doping_layer = 'doping layer for the heater ring',
            slab_on = 'if True, the light ring and the heater ring are connected by a partially etched slab (slab_layer)',
            slab_layer = 'layer for the partially etched slab which connects the light ring and the heater ring when slab_on=True',
            top_cover_box_layer = 'The heater ring is covered by a square box of of this layer; optional',
            wg_in_length = 'length of the input bus waveguide; input bus waveguide exists only if ring_on=True and wg_in_gap>0',
            wg_in_width = 'width of the input bus waveguide',
            wg_in_gap = 'gap of the input bus waveguide; negative value turns the bus waveguide off',
            wg_out_length = 'length of the drop-port waveguide; this waveguide exists only if ring_on=True and wg_out_gap>0',
            wg_out_width = 'width of the output waveguide',
            wg_out_gap = 'gap of the input bus waveguide; negative value turns the output waveguide off',
            dr = 'doping extends beyond the heater ring by dr',
            extra_ring_info = 'an optional list of dictionaries, each defining an additional ring with rout, width, layer entries',
            via_stack_spacing_from_heater = 'spacing between the via stack and the inner radius of the heater ring',
            via_stack_enclosure_vert = 'silicon extends by this much beyond the via stack along the vertical (SN) direction',
            via_stack_enclosure_horiz = 'silicon extends by this much beyond the via stack sideways',
            via_stack_gds_name = 'GDS file from which to load via stack; a required parameter.',
            pads_on = 'if True, heater is connected to pads. If False, all parameters below are not needed.',
            pads_type = 'type of wiring for the pads; at the moment, only "going_up" is supported',
            intermediate_metal_layer = 'the top metal where the via stack from the GDS ends (can =routing_metal_layer)',
            intermediate_metal_length = 'how far vertically (to N) the intermediate metal is routed',
            intermediate_to_routing_length = 'length of the overlap between the intermediate metal and routing metal; vias are created in this overlap region if intermediate_metal_layer!=routing_metal_layer',
            routing_metal_layer = 'metal of the wires going to the pads; can = intermediate_metal_layer',
            routing_wire_spacing = 'horizontal spacing between the edges of the routing_metal_layer wires going vertically up to the pads',
            routing_wire_width = 'width of vertical routing wires going up to the pads',
            pad_edge_distance = 'Vertical distance between the center of the ring and the furthermost edge of the pads',
            pad_pitch = 'pad pitch (period)',
            pad_width = 'width of the pad',
            pad_height = 'height of the pad',
            pad_horizontal_shift_left = 'left is shifted by this much left or right relative to the center of the ring; zero by default',
            pad_horizontal_shift_left_position = 'vertical position of the shift for the left pad wire, counter from the center of the ring',
            pad_horizontal_shift_right= 'right is shifted by this much left or right relative to the center of the ring; zero by default',
            pad_horizontal_shift_right_position = 'vertical position of the shift for the right pad wire, counter from the center of the ring',
            pad_metal_layer = 'metal layer of the pad',
            pad_open_layer = 'layer used to create pad opening',
            pad_open_inclusion = 'pad opening windiow is smaller than the metal pad region by this much',
            pad_left_on = 'if False, the left pad will not be created; can be useful for sharing pads',
            pad_right_on = 'if False, the right pad will not be created; can be useful for sharing pads'
        )

    @classmethod
    def get_default_param_values(cls) -> dict:
        return dict(
            ring_on=None,
            ring_rout=None,
            ring_width=None,
            ring_layer=None,
            heater_rout=None,
            heater_width=None,
            heater_layer=None,
            doping_layer=None,
            slab_on=None,
            slab_layer=None,
            wg_in_length=None,
            wg_in_width=None,
            wg_in_gap=None,
            wg_out_length=None,
            wg_out_width=None,
            wg_out_gap=None,
            dr=None,
            extra_ring_info=None,
            via_stack_spacing_from_heater=None,
            via_stack_enclosure_vert=None,
            via_stack_enclosure_horiz=None,
            via_stack_gds_name=None,
            pads_on=None,
            pads_type=None,
            intermediate_metal_layer=None,
            intermediate_metal_length=None,
            intermediate_to_routing_length=None,
            routing_metal_layer=None,
            routing_wire_spacing=None,
            routing_wire_width=None,
            pad_edge_distance=None,
            pad_pitch=None,
            pad_width=None,
            pad_height=None,
            pad_horizontal_shift_left=None,
            pad_horizontal_shift_left_position=None,
            pad_horizontal_shift_right=None,
            pad_horizontal_shift_right_position=None,
            pad_metal_layer=None,
            pad_open_layer=None,
            pad_open_inclusion=None,
            pad_left_on=None,
            pad_right_on=None
        )

    def draw_layout(self) -> None:

        if self.ring_on:

            if self.wg_in_gap > 0:
                self.add_obj(PhotonicRect(layer=self.ring_layer, bbox=BBox(left=-self.wg_in_length/2 , right=self.wg_in_length/2, top=-self.ring_rout-self.wg_in_gap, bottom=-self.ring_rout-self.wg_in_gap-self.wg_in_width, resolution=self.grid.resolution)))
                self.add_photonic_port(name='PORT_IN_0',  orient='R0',   angle=0, center=(-self.wg_in_length/2, -self.ring_rout-self.wg_in_gap - self.wg_in_width/2 ), width=self.wg_in_width, layer=self.ring_layer, resolution=self.grid.resolution, unit_mode=False, show=False)
                self.add_photonic_port(name='PORT_OUT_0', orient='R180', angle=0, center=( self.wg_in_length/2, -self.ring_rout-self.wg_in_gap - self.wg_in_width/2 ), width=self.wg_in_width, layer=self.ring_layer, resolution=self.grid.resolution, unit_mode=False, show=False)

            if self.wg_out_gap > 0:
                self.add_obj(PhotonicRect(layer=self.ring_layer, bbox=BBox(left=-self.wg_out_length/2 , right=self.wg_out_length/2, top=self.ring_rout+self.wg_out_gap+self.wg_in_width, bottom=self.ring_rout+self.wg_out_gap, resolution=self.grid.resolution)))
                self.add_photonic_port(name='PORT_IN_1',  orient='R180', angle=0, center=( self.wg_out_length/2, self.ring_rout+self.wg_out_gap + self.wg_out_width/2 ), width=self.wg_out_width, layer=self.ring_layer, resolution=self.grid.resolution, unit_mode=False, show=False)
                self.add_photonic_port(name='PORT_OUT_1', orient='R0',   angle=0, center=(-self.wg_out_length/2, self.ring_rout+self.wg_out_gap + self.wg_out_width/2 ), width=self.wg_out_width, layer=self.ring_layer, resolution=self.grid.resolution, unit_mode=False, show=False)

        if self.ring_on and self.slab_on:

            if self.heater_layer != self.ring_layer:
                raise ValueError('Layers for the ring and for the heater are different, and a slab connecting them is on. Cannot connect dissimilar levels with a slab!')

            self.add_obj(PhotonicRound(layer=self.ring_layer, rout=self.ring_rout, rin=self.heater_rout - self.heater_width, resolution=self.grid.resolution))
            self.add_obj(PhotonicRound(layer=self.slab_layer, rout=self.ring_rout-self.ring_width, rin=self.heater_rout, resolution=self.grid.resolution))

        else:
            if self.ring_on:
                self.add_obj(PhotonicRound(layer=self.ring_layer, resolution=self.grid.resolution, rout = self.ring_rout, rin = self.ring_rout-self.ring_width))

            self.add_obj(PhotonicRound(layer=self.heater_layer, resolution=self.grid.resolution, rout=self.heater_rout, rin=self.heater_rout - self.heater_width))

        # add silicon rectangles and via stacks in them
        self.via_stack_template = self.new_template(params={'gds_path': 'Photonic_Layout_45SPCLO/RingTunable/' + self.via_stack_gds_name + '.gds'}, temp_cls=GDSImport)

        via_stack_width = self.via_stack_template.bound_box.width
        via_stack_height = self.via_stack_template.bound_box.height

        contact_width = self.via_stack_spacing_from_heater + via_stack_width + self.via_stack_enclosure_horiz
        contact_height = via_stack_height + 2*self.via_stack_enclosure_vert

        d_contact = self.heater_rout - self.heater_width - contact_width

        self.add_obj(PhotonicRect(layer=self.heater_layer, bbox=BBox(left=-d_contact-contact_width, right=-d_contact, top=contact_height/2, bottom=-contact_height/2, resolution=self.grid.resolution)))
        self.add_obj(PhotonicRect(layer=self.heater_layer, bbox=BBox(left=d_contact, right=d_contact+contact_width,   top=contact_height/2, bottom=-contact_height/2, resolution=self.grid.resolution)))

        x1_left = [-d_contact-self.via_stack_enclosure_horiz-via_stack_width, -d_contact-self.via_stack_enclosure_horiz-via_stack_width/2]
        x1_right = [-x1_left[1], -x1_left[0]]
	    #x1_right
        #y1 = via_stack_height/2
        y1 = 0

        self.via_stack_left  = self.add_instance(self.via_stack_template, loc=(x1_left[1],  y1), orient='R180')
        self.via_stack_right = self.add_instance(self.via_stack_template, loc=(x1_right[0], y1), orient='R0')

        self.via_stack_left_center = ((self.via_stack_left.bound_box.left+self.via_stack_left.bound_box.right)/2,
                                      (self.via_stack_left.bound_box.top+self.via_stack_left.bound_box.bottom)/2)
        self.via_stack_right_center = ((self.via_stack_right.bound_box.left + self.via_stack_right.bound_box.right) / 2,
                                      (self.via_stack_right.bound_box.top + self.via_stack_right.bound_box.bottom) / 2)
        # add ports
        self.add_photonic_port(
            name='port_via_stack_left',
            center=(self.via_stack_left_center),
            orient='R180',
            width=via_stack_width,
            layer=('RX', 'port'),
            resolution=self.grid.resolution,
            unit_mode=False,
            show=False
        )
        self.add_photonic_port(
            name='port_via_stack_right',
            center=(self.via_stack_right_center),
            orient='R0',
            width=via_stack_width,
            layer=('RX', 'port'),
            resolution=self.grid.resolution,
            unit_mode=False,
            show=False
        )
        # add doping
        self.add_obj(PhotonicRound(layer=self.doping_layer, rout=self.heater_rout+self.dr, resolution=self.grid.resolution))

        # add extra rings, if any
        if self.extra_ring_info:
            for extra_ring in self.extra_ring_info:
                self.add_obj(PhotonicRound(layer=extra_ring['layer'], resolution=self.grid.resolution, rout=extra_ring['rout'], rin=extra_ring['rout'] - extra_ring['width']))

        # add "thermal" rectangle on top
        extra_top = 0
        extra_bottom = 0
        extra_r = 0
        if self.ring_on:
            extra_r = self.ring_rout - self.heater_rout
            if self.wg_in_gap > 0:
                extra_bottom = self.wg_in_gap + self.wg_in_width
            if self.wg_out_gap > 0:
                extra_top = self.wg_out_gap + self.wg_out_width

        if self.top_cover_box_layer:
            self.add_obj(PhotonicRect(layer=self.top_cover_box_layer, bbox=BBox(left=-self.heater_rout-extra_r-2.0, right=self.heater_rout+extra_r+2.0, top=self.heater_rout+extra_r+extra_top+2.1, bottom=-self.heater_rout-extra_r-extra_bottom-2.1, resolution=self.grid.resolution)))

        #####  Now add metal wiring going to the pads, and pads themselves





if __name__ == '__main__':
    spec_file = 'layout/RingTunable/specs/ring_tunable_mod.yaml'
    # spec_file = 'Photonic_Layout_45SPCLO/GDS_Library_Device/specs/gds_library_device.yaml'
    plm = BPG.PhotonicLayoutManager(spec_file)
    plm.generate_content()
    plm.generate_gds()
    plm.generate_flat_content()
    plm.generate_flat_gds()
    # plm.generate_lsf()
    plm.dataprep()
    plm.generate_dataprep_gds()

