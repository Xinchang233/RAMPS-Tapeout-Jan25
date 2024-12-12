import BPG
from BPG.objects import PhotonicPolygon
from Photonic_Core_Layout.Taper.TaperBase import TaperBase
import numpy as np

# for loading .mat files
from scipy.io import loadmat

class ArbSymmetricTaper(TaperBase):
    """
    This class generates an arbitrary taper from a list of points. The taper is drawn to be
    symmetric about the x-axis. The points provided by the user are the (x, y) locations of the
    top-half of the taper. These points are then reflected about the x-axis so that the polygon is
    closed.

    Ports
    -----
    - PORT0: port connected to the left side of the taper. Always set to (0, 0)
    - PORT1: port connected to the right side of the taper

    Parameters
    ----------
    points: List[Tuple[float, float]]
        list of (x, y) points
    layer : str
        layer that the taper will be placed on
    matfile : str
        OPTIONAL name of matlab file to read points from
        the matlab file should have the x,y coordinates of the top half of the taper
    """

    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        
        # if matfile was specified, load points from that
        if 'matfile' in params:
            matdata = loadmat( params['matfile'] )
            xpts = matdata['x']
            ypts = matdata['y']
            # un-nest the list. is there an easier way of doing this?
            xpts = [ pt[0] for pt in xpts ]
            ypts = [ pt[0] for pt in ypts ]
            params['points'] = list( zip( xpts, ypts ) )
        else:
            params['matfile'] = 'dummy'
            
        TaperBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)

    #   end __init__()

    @classmethod
    def get_params_info(cls):
        return dict(
            points='List of (x, y) points defining the top side of the symmetric taper',
            layer='layer purpose pair on which to draw the taper',
            matfile = 'OPTIONAL matlab file to read points from'
        )

    def draw_layout(self):
        # calculate the input/output width and length of the taper in order to place the ports
        width_l = 2 * abs(self.params['points'][0][1])
        width_r = 2 * abs(self.params['points'][-1][1])
        length = abs(self.params['points'][-1][0] - self.params['points'][0][0])

        self.parameter_bounds_check(width_l, width_r, length)
        self.create_taper()
        self.create_ports(w_left=width_l,
                          w_right=width_r,
                          length=length,
                          layer=self.params['layer'])

        # save the length
        self.length = length

    def create_taper(self):
        """
        Generate the polygon corresponding to the desired linear taper shape and add it to the db
        """
        # The provided point list is for the top envelope of the taper
        top_points = np.array(self.params['points'])

        # shift the points so the left side of the taper starts at (0,0)
        top_points[:, 0] = top_points[:, 0] - top_points[0, 0]

        # Mirror the top points across the x-axis
        bot_points_x = top_points[:, 0]
        bot_points_y = np.negative(top_points[:, 1])
        bot_points = np.stack((bot_points_x, bot_points_y))
        bot_points = np.transpose(bot_points)

        # Flip point ordering so that polygon is drawn in clockwise fashion
        bot_points = np.flipud(bot_points)

        # Combine top and bottom point lists
        total_points = np.concatenate((top_points, bot_points))
        polygon = PhotonicPolygon(
            resolution=self.grid.resolution,
            layer=self.params['layer'],
            points=total_points,
            unit_mode=False,
        )
        self.add_obj(polygon)


if __name__ == '__main__':
    spec_file = 'Photonic_Core_Layout/Taper/specs/symmetric_taper.yaml'
    plm = BPG.PhotonicLayoutManager(spec_file=spec_file)
    plm.generate_template()
    plm.generate_content()
    plm.generate_gds()
