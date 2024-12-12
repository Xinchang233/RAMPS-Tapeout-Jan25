"""

Draws a taper to convert from fully etched wg to rib wg
is basically two tapers on top of each other

"""

import BPG
from Photonic_Core_Layout.Taper.TaperBase import TaperBase
from Photonic_Core_Layout.Taper.LinearTaper import LinearTaper

class StripToRibTaper(TaperBase):
    """
    Draws a partial etch taper by overlaying one si_full and one si_partial taper

    Ports
    -----
    - PORT0: port connected to the left side of the taper. Always set to (0, 0)
    - PORT1: port connected to the right side of the taper

    Parameters
    ----------
    width0 : float
        width of full si on the side of the taper connected to PORT0, strip wg
    width1: float
        width of full si on the side of the taper connected to PORT1, rib wg
    width_partial: float
        width of the partial etch on the rib wg end
    length: float
        length of the entire linear taper section
    """

    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        # give taper base a dummy layer
        params['layer'] = ( 'si_full_free', 'drawing' )
        TaperBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)

    @classmethod
    def get_params_info(cls):
        return dict(
            width0='width of the first photonic port',
            width1='width of the second photonic port',
            length='distance between the photonics ports',
            # layer='layer on which to draw the taper',
            width_partial='width of partial etch slab on rib wg side'
        )

    def draw_layout(self):
        """
        draws 2 tapers on top of each other
        """

        # add full thick wg taper
        # params_full          = self.params
        # params_full['layer'] = ( 'si_full', 'drawing' )
        si_taper        = self.new_template(params = {'width0': self.params['width0'],
                                                            'width1': self.params['width1'],
                                                            'length': self.params['length'],
                                                            'layer': ('si_full_free', 'drawing')},
                                                temp_cls = LinearTaper )
        self.add_instance( si_taper, loc=(0.0,0.0) )

        # add partial etch taper
        # params['layer']     = ( 'si_partial', 'drawing' )
        # params['width1']    = self.params['width_partial']
        partial_taper       = self.new_template( params = {'width0': self.params['width0'],
                                                            'width1': self.params['width_partial'],
                                                            'length': self.params['length'],
                                                            'layer': ('si_partial', 'drawing') },
                                                temp_cls = LinearTaper )
        self.add_instance( partial_taper, loc=(0.0, 0.0) )

        # add KG everything
        extrakg = 0.2   # extra kg beyond taper ends
        self.add_rect( layer = ('KG', 'drawing'),
                        coord1 = (0.0 - extrakg, -self.params['width_partial']/2.0 - extrakg),
                        coord2 = (self.params['length'] + extrakg, self.params['width_partial']/2.0 + extrakg) )

        self.create_ports(  w_left = self.params['width0'], 
                            w_right = self.params['width1'], 
                            length = self.params['length'], 
                            layer = ('si_full', 'PORT') )
