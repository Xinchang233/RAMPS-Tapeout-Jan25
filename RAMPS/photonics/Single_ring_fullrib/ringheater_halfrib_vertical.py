import BPG
from BPG.objects import PhotonicPolygon, PhotonicRound
from Photonic_Core_Layout.ViaStack.ViaStack import ViaStack
import numpy as np

from typing import TYPE_CHECKING, List, Tuple

if TYPE_CHECKING:
    from BPG.bpg_custom_types import dim_type, lpp_type
    from BPG.objects import PhotonicRect


class RingHeater(BPG.PhotonicTemplateBase):
    """
    Base ring-heater class

    """

    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)

        # Layer information
        self.electrode_bottom_lpp = self.params['electrode_bottom_layer']
        self.electrode_top_lpp = self.params['electrode_top_layer']
        self.electrode_label = self.params['electrode_label']
        self.device_layer = self.params['device_layer']

        lpp_check_list = ['electrode_bottom_layer', 'electrode_top_layer', 'device_layer']
        for lpp in lpp_check_list:
            self.check_lpp_entry(self.params[lpp], lpp)

        self.disk_layers = self.params['disk_layers']
        if self.disk_layers is not None:
            if not isinstance(self.disk_layers, list):
                self.disk_layers = [self.disk_layers]

        # Label
        if isinstance(self.electrode_label, str):
            self.electrode_label_p = self.electrode_label + '_P'
            self.electrode_label_n = self.electrode_label + '_N'
        elif isinstance(self.electrode_label, dict):
            if not ('P' in self.electrode_label.keys() and 'N' in self.electrode_label.keys()):
                raise ValueError(f'If specifying labels as a dictionary, must pass a '
                                 f'P and N key for the P and N labels')
            self.electrode_label_p = self.electrode_label['P']
            self.electrode_label_n = self.electrode_label['N']

        # Dimensions information
        self.rout = self.params['rout']
        self.width = self.params['width']
        self.contact_dist = self.params['contact_dist']
        self.contact_width = self.params['contact_width']
        self.disk_layer_extension = self.params['disk_layer_extension']

        # Electrode size
        self.electrode_top_x_span = self.params['electrode_top_x_span']
        self.electrode_top_y_span = self.params['electrode_top_y_span']

        # Assign dynamic defaults to electrode bottom span
        if self.params['electrode_bottom_x_span'] is None:
            self.electrode_bottom_x_span = self.contact_width
        else:
            self.electrode_bottom_x_span = self.params['electrode_bottom_x_span']
        if self.params['electrode_bottom_y_span'] is None:
            self.electrode_bottom_y_span = self.contact_width
        else:
            self.electrode_bottom_y_span = self.params['electrode_bottom_y_span']

    @classmethod
    def get_default_param_values(cls):
        return dict(
            electrode_top_x_span=1,
            electrode_top_y_span=1,
            electrode_bottom_x_span=None,
            electrode_bottom_y_span=None,
            electrode_label='Heat'
        )

    @classmethod
    def get_params_info(cls):  # Returns definition of the parameters.
        return dict(
            # Standard parameters
            rout='Outer radius of ring heater',
            width='Width of ring heater ring (width of annulus)',
            contact_dist='Distance between two inner edges of the two interior spokes that contact the heater ring.',
            contact_width='Width of interior contact spokes that connect the heater ring to the via stack',
            device_layer='LPP of ring heater device (ie layer of the actual heater)',
            disk_layers='List of additional LPPs on which disks covering the entire ring heater will be drawn',
            electrode_top_layer='LPP of top metal layer of the gs electrode',
            electrode_top_x_span='Electrode x-span on the top electrode metal layer (defaults to 1)',
            electrode_top_y_span='Electrode y-span on the top electrode metal layer (defaults to 1)',
            electrode_label='Electrode contact label text [str], or dictionary with keys P: <p_label> and N: <n_label>',
            electrode_bottom_x_span='Electrode x-span on the bottom electrode metal layer (defaults to contact_width)',
            electrode_bottom_y_span='Electrode y-span on the bottom electrode metal layer (defaults to contact_width)',
            # Advanced parameters
            disk_layer_extension='Size by which disk_layers should be drawn beyond outer radius of heater ring',
            # Technology parameter
            electrode_bottom_layer='LPP for the bottom electrode layer in the stack (should be the BAG '
                                   'equivalent layer of device_layer)',
        )

    @staticmethod
    def check_lpp_entry(lpp_entry, lpp_entry_name):
        if not (isinstance(lpp_entry, tuple) and len(lpp_entry) == 2
                and isinstance(lpp_entry[0], str) and isinstance(lpp_entry[1], str)):
            raise ValueError(f'LPP entry "{lpp_entry_name}" must be a tuple of two strings. Received {lpp_entry}')

    def draw_layout(self):
        # Draw the ring heater, contacts, and extra disk layers
        self.draw_heater_ring_and_contacts(
            heater_rout=self.rout-0.05,
            ring_width=self.width,
            contact_dist=self.contact_dist,
            contact_width=self.contact_width,
            device_layer=self.device_layer,
            disk_layers=self.disk_layers
        )

        # Create the electrode via stacks
        viastack_params = dict(
            top_layer=self.electrode_top_lpp,
            bottom_layer=self.electrode_bottom_lpp,
            top_x_span=self.electrode_top_x_span,
            top_y_span=self.electrode_top_y_span,
            bottom_x_span=self.electrode_bottom_x_span,
            bottom_y_span=self.electrode_bottom_y_span,
            #limit_x_or_y='y',
            side_align=True,
        )
        electrode_master = self.new_template(params=viastack_params, temp_cls=ViaStack)

        # Place the via stacks
        left_heater_loc = (-self.contact_dist/2.0, 0)
        self.add_instance(
            master=electrode_master,
            inst_name='heater_left_electrode',
            loc=left_heater_loc,
            orient='MY',
            unit_mode=False,
        )

        right_heater_loc = (self.contact_dist / 2.0, 0)
        self.add_instance(
            master=electrode_master,
            inst_name='heater_right_electrode',
            loc=right_heater_loc,
            orient='R0',
            unit_mode=False,
        )

        # Get the electrode's top layer for placing the pin label
        electrode_top_rect: PhotonicRect = electrode_master.top_layer_rect

        left_electrode = electrode_top_rect.transform(loc=left_heater_loc, orient='MY', unit_mode=False, copy=True)
        right_electrode = electrode_top_rect.transform(loc=right_heater_loc, orient='R0', unit_mode=False, copy=True)
        self.add_label(
            label=self.electrode_label_p,
            layer=self.electrode_top_lpp[0],
            bbox=left_electrode.bbox,
        )
        self.add_label(
            label=self.electrode_label_n,
            layer=self.electrode_top_lpp[0],
            bbox=right_electrode.bbox,
        )

    def draw_heater_ring_and_contacts(self,
                                      heater_rout: "dim_type",
                                      ring_width: "dim_type",
                                      contact_dist: "dim_type",
                                      contact_width: "dim_type",
                                      device_layer: "lpp_type",
                                      disk_layers: List["lpp_type"],
                                      ) -> None:
        """
        Draws the heater ring and the two interior contact spokes that connect the heater ring to the via stack.

        Parameters
        ----------
        heater_rout : Union[float, int]
            The outer radius of the heater.
        ring_width : Union[float, int]
            The width of the annulus of the heater.
        contact_dist : Union[float, int]
            The separation of the two inner edges of the interior contact spokes for the heater.
        contact_width : Union[float, int]
            The width (y span) of the interior contact spokes.
        device_layer : Tuple[str, str]
            The LPP on which to draw the heater and contact spokes.
        disk_layers : List[Tuple[str, str]]
            An optional list of additional layers which should be drawn to cover the entire heater structure.

        """
        # Create and add the heater ring
        heater_rin = heater_rout - ring_width
        ring = PhotonicRound(
            layer=device_layer,
            resolution=self.grid.resolution,
            rout=heater_rout,
            rin=heater_rin,
            unit_mode=False
        )
        #self.add_obj(ring)

        ring = self.add_round(
            layer=device_layer,
            resolution=self.grid.resolution,
            rout=heater_rout,
            rin=heater_rin,
            theta0=-65,
            theta1=245,
        )
        self.add_obj(ring)

        # Create the left side contact
        #contact_points = [(-heater_rin, -contact_width / 2.0),
        #                  (-contact_dist / 2.0, -contact_width / 2.0),
        #                  (-contact_dist / 2.0, contact_width / 2.0),
        #                  (-heater_rin, contact_width / 2.0)
        #                  ]
        contact_points = [(-contact_dist / 2.0-self.electrode_bottom_x_span, -heater_rin+0.08),
                         (-contact_dist / 2.0, -heater_rin+0.08),
                         (-contact_dist / 2.0, contact_width / 2.0),
                         (-contact_dist / 2.0-self.electrode_bottom_x_span, contact_width / 2.0)
                          ]
        polygon = PhotonicPolygon(
            resolution=self.grid.resolution,
            layer=device_layer,
            points=contact_points,
            unit_mode=False
        )
        self.add_obj(polygon)


        # RX piece addition to get DRC
        contact_points = [(-contact_dist / 2.0 - self.electrode_bottom_x_span-0.2, -heater_rin + 0.55),
                          (-contact_dist / 2.0, -heater_rin + 0.55),
                          (-contact_dist / 2.0, -heater_rin + 0.75),
                          (-contact_dist / 2.0 - self.electrode_bottom_x_span-0.2,-heater_rin + 0.75)
                          ]
        polygon = PhotonicPolygon(
            resolution=self.grid.resolution,
            layer=device_layer,
            points=contact_points,
            unit_mode=False
        )
        self.add_obj(polygon)

        # Create the right side contact
        contact_points = [(contact_dist / 2.0+self.electrode_bottom_x_span, -heater_rin+0.08),
                          (contact_dist / 2.0, -heater_rin+0.08),
                          (contact_dist / 2.0, contact_width / 2.0),
                          (contact_dist / 2.0+self.electrode_bottom_x_span, contact_width / 2.0)
                          ]
        polygon = PhotonicPolygon(
            resolution=self.grid.resolution,
            layer=device_layer,
            points=contact_points,
            unit_mode=False
        )
        self.add_obj(polygon)

        # RX piece addition to get DRC
        contact_points = [(contact_dist / 2.0 + self.electrode_bottom_x_span + 0.2, -heater_rin + 0.55),
                          (contact_dist / 2.0 + self.electrode_bottom_x_span + 0.2, -heater_rin + 0.75),
                          (contact_dist / 2.0, -heater_rin + 0.75),
                          (contact_dist / 2.0, -heater_rin + 0.55),

                                                    ]
        polygon = PhotonicPolygon(
            resolution=self.grid.resolution,
            layer=device_layer,
            points=contact_points,
            unit_mode=False
        )
        self.add_obj(polygon)

        # Cover the heater with extra layers
        if disk_layers:
            for layer in disk_layers:
                disk = PhotonicRound(
                    layer=layer,
                    resolution=self.grid.resolution,
                    rout=heater_rout + self.disk_layer_extension,
                    rin=0,
                    unit_mode=False
                )
                self.add_obj(disk)



    @staticmethod
    def design_heater_width_from_resistance(resistance,
                                            heater_rout,
                                            r_square,
                                            contact_width,
                                            contact_dist,
                                            ):
        """
        Calculates the required heater width for a given resistance, outer radius, r_square, contact width, and contact
        distance.

        Values must be passed in in units of microns and ohm/um^2

        Parameters
        ----------
        resistance : float
            The target resistance
        heater_rout : float
            The outer radius of the heater ring
        r_square : float
            The sheet resistance
        contact_width : float
            The width of the contacts that connect the heater ring to the via stack
        contact_dist : float
            The separation between the ends of the two contacts

        Returns
        -------
        ring_width : float
            The width of the heater ring required to achieve the target resistance for the specified geometry
        """
        # If you integrate across the radius to find effective resistance per 'pie-slice' of the annulus, and then
        # integrate over theta, one finds:
        # ring_width = rout - np.exp((4*resistance*np.log(rout) - rsq*np.pi^2) / 4*resistance)
        # This formula is with 10% of the magic code below. It does not include effects of the contacts

        # Magic formula from legacy designs
        # Magic formula from legacy designs
        # ring_width = \
        #    1 / (16 * r_square) * (
        #            -8 * contact_dist * r_square + 8 * heater_rout * r_square - 4 * resistance * contact_width -
        #            np.pi * r_square * contact_width +
        #            np.sqrt(
        #                64 * np.pi * heater_rout * r_square ** 2 * contact_width +
        #                (
        #                        8 * contact_dist * r_square - 8 * heater_rout * r_square +
        #                        4 * resistance * contact_width + np.pi * r_square * contact_width
        #                ) ** 2
        #            )
        #    )
        # return ring_width

        mm = (np.pi * contact_width - 2 * heater_rout + (resistance / r_square) * contact_width)
        ring_width = (-mm + np.sqrt((mm ** 2) + (8 * contact_width * (2 * np.pi * heater_rout - contact_dist)))) / 4
        print("contact width=", contact_width)
        print("R=", heater_rout)
        print("resistance=", resistance)
        print("contact_dist=", contact_dist)
        print("r_square=", r_square)
        print("ring_width=", ring_width)
        return ring_width


if __name__ == '__main__':
    spec_file = 'layout/Ring/specs/ringheater_specs.yaml'
    plm = BPG.PhotonicLayoutManager(spec_file)
    plm.generate_content()
    plm.generate_gds()
    plm.generate_flat_content()
    plm.generate_flat_gds()
