import BPG
from bag.layout.util import BBox
from Photonic_Core_Layout.ViaStack_test.ViaStack import ViaStack

class LinearHeater(BPG.PhotonicTemplateBase):
    """
    This Class can be used for generating linear heater with two rails that can be placed on both sides of a waveguide .
    """

    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)

        # Master declaration
        self.contact_master = None
        self.contact_doping_master = None

        # Hard coded params
        self.heat_loc = (0, 0)

        # Initialize the variables and dictionary of parameters.
        # basic heater parameters
        self.heat_layer = self.params['heat_layer']
        self.heat_length = self.params['heat_length']
        self.heat_width = self.params['heat_width']
        self.heat_dist = self.params['heat_dist']

        # parameters of doping layers
        self.doping_info = self.params['doping_info']

        # parameters of heater electrodes
        self.contact_bottom_layer = self.params['contact_bottom_layer']
        self.contact_bottom_width = self.params['contact_bottom_width']
        self.contact_bottom_length = self.params['contact_bottom_length']
        self.contact_top_layer = self.params['contact_top_layer']
        self.contact_top_width = self.params['contact_top_width']
        self.contact_top_length = self.params['contact_top_length']
        self.contact_doping_extend = self.params['contact_doping_extend']
        self.contact_doping_info = self.params['contact_doping_info']

    @classmethod
    def get_params_info(cls) -> dict:
        return dict(
            # basic heater parameters
            heat_layer='Layer on which heater body is drawn',
            heat_length='Length of heater',
            heat_width='Width of heater',
            heat_dist='Distance between two parallel arms of the heater',

            # parameters of doping layers
            doping_info='List of doping dictionaries containing width and layer name of the implant layer',

            # parameters of heater electrodes
            contact_bottom_layer='Bottom layer name of heater contact',
            contact_bottom_width='Bottom width of heater contact',
            contact_bottom_length='Bottom length of heater contact',
            contact_top_layer='Top layer name of heater contact',
            contact_top_width='Top width of heater contact',
            contact_top_length='Top length of heater contact',
            contact_doping_extend='',
            contact_doping_info='',
        )

    def draw_layout(self) -> None:
        self.draw_heater_body()
        self.draw_doping_layers()
        self.create_contacts()
        self.draw_contact_doping_layers()

    def draw_heater_body(self) -> None:
        """
        Draws heater consisting of two parallel strips of silicon
        """
        # draw left strip
        self.add_rect(layer=self.heat_layer,
                      bbox=BBox(left=self.heat_loc[0]-self.heat_dist/2-self.heat_width,
                                right=self.heat_loc[0]-self.heat_dist/2,
                                bottom=self.heat_loc[1]-self.heat_length/2,
                                top=self.heat_loc[1]+self.heat_length/2,
                                resolution=self.grid.resolution)
                      )
        # draw right strip
        self.add_rect(layer=self.heat_layer,
                      bbox=BBox(left=self.heat_loc[0]+self.heat_dist/2,
                                right=self.heat_loc[0]+self.heat_dist/2+self.heat_width,
                                bottom=self.heat_loc[1]-self.heat_length/2,
                                top=self.heat_loc[1]+self.heat_length/2,
                                resolution=self.grid.resolution)
                      )

    def draw_doping_layers(self):
        """
        Draws doping layers on the heater body using the information given in doping_info
        """
        for count in range(len(self.doping_info)):
            self.add_rect(layer=self.doping_info[count]['layer'],
                          bbox=BBox(left=self.heat_loc[0]-self.heat_dist/2 -
                                         self.heat_width/2-self.doping_info[count]['width']/2,
                                    bottom=self.heat_loc[1]-self.heat_length/2,
                                    right=self.heat_loc[0]-self.heat_dist/2 -
                                          self.heat_width/2+self.doping_info[count]['width']/2,
                                    top=self.heat_loc[1]+self.heat_length/2,
                                    resolution=self.grid.resolution)
                          )

            self.add_rect(layer=self.doping_info[count]['layer'],
                          bbox=BBox(left=self.heat_loc[0]+self.heat_dist/2 +
                                         self.heat_width/2-self.doping_info[count]['width']/2,
                                    bottom=self.heat_loc[1]-self.heat_length/2,
                                    right=self.heat_loc[0]+self.heat_dist/2 +
                                          self.heat_width/2+self.doping_info[count]['width']/2,
                                    top=self.heat_loc[1]+self.heat_length/2,
                                    resolution=self.grid.resolution)
                          )

    def draw_contact_doping_layers(self):
        """
        Draws doping layers on the contact region of the heater
        """
        for count in range(len(self.contact_doping_info)):
            # top left
            self.add_rect(layer=self.contact_doping_info[count],
                          bbox=BBox(left=self.heat_loc[0] - self.heat_dist/2 -
                                         self.heat_width/2 - self.contact_bottom_width/2 -self.contact_doping_extend,
                                    right=self.heat_loc[0] - self.heat_dist/2 -
                                          self.heat_width/2 + self.contact_bottom_width/2 + self.contact_doping_extend,
                                    bottom=self.heat_loc[1] + self.heat_length/2 - self.contact_doping_extend,
                                    top=self.heat_loc[1] + self.heat_length/2 +
                                        self.contact_bottom_length + self.contact_doping_extend,
                                    resolution=self.grid.resolution)
                          )
            # bottom left
            self.add_rect(layer=self.contact_doping_info[count],
                          bbox=BBox(left=self.heat_loc[0] - self.heat_dist/2 -
                                         self.heat_width/2 - self.contact_bottom_width/2 -self.contact_doping_extend,
                                    right=self.heat_loc[0] - self.heat_dist/2 -
                                          self.heat_width/2 + self.contact_bottom_width/2 + self.contact_doping_extend,
                                    top=self.heat_loc[1] - self.heat_length/2 + self.contact_doping_extend,
                                    bottom=self.heat_loc[1] - self.heat_length/2 -
                                           self.contact_bottom_length - self.contact_doping_extend,
                                    resolution=self.grid.resolution)
                          )
            # top right
            self.add_rect(layer=self.contact_doping_info[count],
                          bbox=BBox(left=self.heat_loc[0] + self.heat_dist / 2 + self.heat_width / 2 -
                                         self.contact_bottom_width / 2 - self.contact_doping_extend,
                                    right=self.heat_loc[0] + self.heat_dist / 2 + self.heat_width / 2 +
                                          self.contact_bottom_width / 2 + self.contact_doping_extend,
                                    bottom=self.heat_loc[1] + self.heat_length / 2 - self.contact_doping_extend,
                                    top=self.heat_loc[1] + self.heat_length / 2 +
                                        self.contact_bottom_length + self.contact_doping_extend,
                                    resolution=self.grid.resolution)
                          )
            # bottom right
            self.add_rect(layer=self.contact_doping_info[count],
                          bbox=BBox(left=self.heat_loc[0] + self.heat_dist / 2 + self.heat_width / 2 -
                                         self.contact_bottom_width / 2 - self.contact_doping_extend,
                                    right=self.heat_loc[0] + self.heat_dist / 2 + self.heat_width / 2 +
                                          self.contact_bottom_width / 2 + self.contact_doping_extend,
                                    top=self.heat_loc[1] - self.heat_length / 2 + self.contact_doping_extend,
                                    bottom=self.heat_loc[1] - self.heat_length / 2 -
                                           self.contact_bottom_length - self.contact_doping_extend,
                                    resolution=self.grid.resolution)
                          )

    def create_contacts(self):
        """
        Create metal vias and electrodes
        """
        self.contact_master = \
            self.new_template(params={'top_layer': self.contact_top_layer,
                                      'bottom_layer': self.contact_bottom_layer,
                                      'top_y_span': self.contact_top_length,
                                      'top_x_span': self.contact_top_width,
                                      'bottom_y_span': self.contact_bottom_length,
                                      'bottom_x_span': self.contact_bottom_width,
                                      'align': 'center_align',
                                      'top_bot_offset': 0
                                      },
                              temp_cls=ViaStack)
        # place left top contact
        self.add_instance(self.contact_master,
                          loc=(self.heat_loc[0] - self.heat_dist/2 - self.heat_width/2,
                               self.heat_loc[1] + self.heat_length/2 + self.contact_bottom_length/2),
                          orient='R0')

        # place left bottom contact
        self.add_instance(self.contact_master,
                          loc=(self.heat_loc[0] - self.heat_dist/2 - self.heat_width/2,
                               self.heat_loc[1] - self.heat_length/2 - self.contact_bottom_length/2),
                          orient='R0')

        # place left top contact
        self.add_instance(self.contact_master,
                          loc=(self.heat_loc[0] + self.heat_dist/2 + self.heat_width/2,
                               self.heat_loc[1] + self.heat_length/2 + self.contact_bottom_length/2),
                          orient='R0')

        # place left bottom contact
        self.add_instance(self.contact_master,
                          loc=(self.heat_loc[0] + self.heat_dist/2 + self.heat_width/2,
                               self.heat_loc[1] - self.heat_length/2 - self.contact_bottom_length/2),
                          orient='R0')

        # connect left and right contacts
        # bottom
        self.add_rect(layer=self.contact_top_layer,
                      bbox=BBox(left=self.heat_loc[0] - self.heat_dist / 2 - self.heat_width / 2 -
                                     self.contact_top_width / 2,
                                right=self.heat_loc[0] + self.heat_dist / 2 + self.heat_width / 2 +
                                      self.contact_top_width / 2,
                                top=self.heat_loc[1] - self.heat_length / 2 -
                                    self.contact_bottom_length/2 + self.contact_top_length/2,
                                bottom=self.heat_loc[1] - self.heat_length / 2 -
                                       self.contact_bottom_length / 2 - self.contact_top_length/2,
                                resolution=self.grid.resolution)
                      )
        # top
        self.add_rect(layer=self.contact_top_layer,
                      bbox=BBox(left=self.heat_loc[0] - self.heat_dist / 2 - self.heat_width / 2 -
                                     self.contact_top_width / 2,
                                right=self.heat_loc[0] + self.heat_dist / 2 + self.heat_width / 2 +
                                      self.contact_top_width / 2,
                                bottom=self.heat_loc[1] + self.heat_length / 2 +
                                       self.contact_bottom_length/2 - self.contact_top_length/2,
                                top=self.heat_loc[1] + self.heat_length / 2 +
                                    self.contact_bottom_length/2 + self.contact_top_length/2,
                                resolution=self.grid.resolution)
                      )