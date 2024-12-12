import BPG
from bag.layout.util import BBox

from Photonic_Core_Layout.VerticalGratingCoupler.VGCBase import VerticalGratingCouplerBase

# python debugger
import pdb

class VerticalGratingCouplerCLO(VerticalGratingCouplerBase):
    """
    Generates a grating coupler based on a list of arbitrarily specified rectangles

    For CLO process, which basically means adding a 'grating' box

    Parameters
    ----------
    rect_list : list
        list of dictionaries specifying how to draw each rectangle. Requires layer, left_edge, width, length
            OPTIONAL: center 
    matfile : string
        OPTIONAL: name of .mat file to load rect_list data from. Contains 4 (5) arrays - layer, (purpose, optional), left_edge, width, length
            in matlab: layer (and purpose) are cell arrays of strings
                        left_edge, width, and length are arrays of doubles
    etch_depth : string
        OPTIONAL: either 'full', 'partial', or 'none'. If 'partial', then draws si_partial, if 'none', then draws si_full
                    For poly interfacing gratings with body teeth, etch_depth should be 'full'. I think defaults to 'full'
    add_BO : bool
        OPTIONAL: set to true to add BO over the grating
    """

    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):

        # check for optional etch_depth arg, default to full
        if 'etch_depth' not in params:
            params['etch_depth'] = 'full'

        if 'add_BO' not in params:
            params['add_BO'] = False

        super().__init__(temp_db, lib_name, params, used_names, **kwargs)
    # end constructor


    @classmethod
    def get_params_info(cls):
        return dict(
            rect_list='list of rectangle dictionaries with the following properties: layer, left_edge, width, length',
            matfile = 'OPTIONAL matlab file to read points from',
            etch_depth = 'OPTIONAL: either "full" or "partial" or "none"',
            add_BO = 'OPTIONAL: set to true to add BO over the grating'
        )

    def draw_layout(self):
        """
        Draws layout
        """
        # call super class draw layout
        super().draw_layout()

        # draw the grating block layers
        box_size  = 5.0     # additional size around edge of grating to draw fill block
#        pdb.set_trace() 
        leftmost_edge   = min( [ rect['left_edge'] for rect in self.params['rect_list'] ] )
        rightmost_edge  = max( [ rect['left_edge'] + rect['length'] for rect in self.params['rect_list'] ] ) 
        max_width       = max( [ rect['width'] for rect in self.params['rect_list'] ] ) 
        self.add_rect(  layer   = ('grating', 'drawing'),
                        bbox    = BBox( left    = leftmost_edge - box_size,
                                        bottom  = -.5 * max_width - box_size,
                                        right   = rightmost_edge + box_size,
                                        top     = .5 * max_width + box_size,
                                        resolution = self.grid.resolution ) )

        # add BO over everything too
        if self.params['add_BO']:
            BO_extra_width = 10.0
            self.add_rect(  layer   = ('BO', 'drawing'),
                            bbox    = BBox( left    = leftmost_edge - BO_extra_width,
                                            bottom  = -.5 * max_width - BO_extra_width,
                                            right   = rightmost_edge + BO_extra_width,
                                            top     = .5 * max_width + BO_extra_width,
                                            resolution = self.grid.resolution ) )
            self.add_rect(  layer   = ('PHOTON', 'drawing'),
                            bbox    = BBox( left    = leftmost_edge - BO_extra_width - 10.0,
                                            bottom  = -.5 * max_width - BO_extra_width - 10.0,
                                            right   = rightmost_edge + BO_extra_width + 10.0,
                                            top     = .5 * max_width + BO_extra_width + 10.0,
                                            resolution = self.grid.resolution ) )


        # add in extra layers if needed
        if self.params['etch_depth'] == 'partial':
            # if partial etch, draw the partial etch layer to fill in the gaps
            self.add_rect(  layer   = ('si_partial', 'drawing'),
                            bbox    = BBox( left    = leftmost_edge,
                                            bottom  = -.5 * max_width,
                                            right   = rightmost_edge,
                                            top     = .5 * max_width,
                                            resolution = self.grid.resolution ) )

        elif self.params['etch_depth'] == 'none':
            # probably a single level design, so draw in waveguide
            self.add_rect(  layer   = ('si_full', 'drawing'),
                            bbox    = BBox( left    = leftmost_edge,
                                            bottom  = -.5 * max_width,
                                            right   = rightmost_edge,
                                            top     = .5 * max_width,
                                            resolution = self.grid.resolution ) )
 

    # end draw_layout()


