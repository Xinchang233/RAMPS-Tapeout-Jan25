import BPG
from Taper.ArbSymmetricTaper import ArbSymmetricTaper
import numpy as np

class ParabolicTaper(ArbSymmetricTaper):
    """
    This class generates a parabolic taper using ArbSymmetricTaper as a base class.

    Ports
    -----
    - PORT0: port connected to the left side of the taper. Always set to (0, 0)
    - PORT1: port connected to the right side of the taper

    Parameters
    ----------
    width0 : float
        width of the side of the taper connected to PORT0
    width1 : float
        width of the side of the taper connected to PORT1
    length : float
        length of the entire linear taper section
    layer : str OR [str, str]
        layer that the taper will be placed on
    n_points : OPTIONAL integer
        number of points to use when generating the polygon (total number of vertices of polygon is n_points*2);
        default value: 100
    """

    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)

        self.width0 = self.params['width0']
        self.width1 = self.params['width1']
        self.length = self.params['length']
        if 'n_points' not in self.params:
            self.n_points = 100
        else:
            self.n_points = self.params['n_points']
        #Add parabolic point list to self.params['points'] for use by ArbSymmetricTaper
        self.generate_parabola()


        #ArbSymmetricTaper.__init__(self, temp_db, lib_name, self.params, used_names, **kwargs)

    #   end __init__()
    @classmethod
    def get_params_info(cls):
        return dict(
            width0='width of the first photonic port',
            width1='width of the second photonic port',
            length='distance between the photonics ports',
            layer='layer on which to draw the taper'
        )

    @classmethod
    def get_default_params_values(cls):
        return dict(
            width0 = None,
            width1 = None,
            length = None,
            layer = None
        )

    def generate_parabola(self) -> None:
        points = self.calculate_parabola(self.width0, self.width1, self.length, self.n_points)
        self.params['points'] = points

    @staticmethod
    def calculate_parabola(w0,w1,l,n):
        a = 4 * l / (w1 ** 2 - w0 ** 2)
        c = a * (w0 ** 2) / 4
        dx = l / (n - 1)
        points = list()
        x = 0.0
        y = w0/2
        for i in range(n):
            points.append((x,y))
            #debug
            #print(str(x) + ',' + str(y))
            x = x+dx
            y = ((x + c) / a) ** .5


        return points


if __name__ == '__main__':
    spec_file = 'Photonic_Core_Layout/Taper/specs/parabolic_taper.yaml'
    plm = BPG.PhotonicLayoutManager(spec_file=spec_file)
    plm.generate_template()
    plm.generate_content()
    plm.generate_gds()
