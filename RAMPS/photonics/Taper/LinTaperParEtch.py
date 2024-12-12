# partial etch taper
# currently for testing custom layer dataprep

import BPG
from Photonic_Core_Layout.Taper.TaperBase import TaperBase
from Photonic_Core_Layout.Taper.LinearTaper import LinearTaper

class LinTaperParEtch(TaperBase):
    """
    Draws a partial etch taper by overlaying one si_full and one si_partial taper

    for now, layers and etch width are hard coded

    Ports
    -----
    - PORT0: port connected to the left side of the taper. Always set to (0, 0)
    - PORT1: port connected to the right side of the taper

    Parameters
    ----------
    width0 : float
        width of the side of the taper connected to PORT0
    width1: float
        width of the side of the taper connected to PORT1
    length: float
        length of the entire linear taper section
 
    """

    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        # give taper base a dummy layer
        params['layer'] = ( 'si_full', 'drawing' )
        TaperBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)

    def draw_layout(self):
        """
        draws 2 tapers on top of each other
        """

        # add full thick wg taper
        params = self.params
        params['layer'] = ( 'si_full', 'drawing' )
        si_taper = self.new_template(params = params, temp_cls = LinearTaper ) 
        self.add_instance( si_taper, loc=(0.0,0.0) )

        # add partial etch taper
        params['layer'] = ( 'si_partial', 'drawing' )
        params['width0'] += 5
        params['width1'] += 5
        partial_taper = self.new_template( params = params, temp_cls = LinearTaper )
        self.add_instance( partial_taper, loc=(0.0, 0.0) )
