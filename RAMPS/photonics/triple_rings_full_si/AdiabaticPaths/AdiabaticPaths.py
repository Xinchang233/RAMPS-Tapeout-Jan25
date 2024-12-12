import matplotlib.pyplot as plt
import BPG
from bag.layout.util import BBox
from BPG.objects import PhotonicPath, PhotonicPolygon
import numpy as np
from numpy import sqrt, pi
from scipy.special import fresnel
from scipy.optimize import brentq
from copy import deepcopy


class AdiabaticPaths(BPG.PhotonicTemplateBase):
    """
    The class generates continuous series of arcs, which can be adiabatic (Euler, or clothoid) bends, circular bends,
    or straight waveguides. The input contains a list of arc definitions, which include arc type (for example,
    "bend_90_deg") and arc parameters corresponding to this arc type. The start angle and coordinate of the first arc are
    specified in user-defined parameters x_start, y_start, angle_start, which are applied to the first arc. Each
    subsequent arc is automatically aligned to its previous arc in terms of coordinate and the angle.
    Note that the final output is a list of polygons, and polygons are generated in two steps. First, the class generates
    "arcs", which contain coordinate lists of the center of the waveguide, the normal vectors (which are calculated
    analytically rather than numerically), the start and end angles of the arc, the start and end curvatures, and the
    length. As a second (final) step, the arcs ar converted to polygons. The reason for generating arcs and not polygons
    from the beginning is that it's easier to operate with arcs: for example, it's very easy to merge multiple arcs into
    a single arc, while for plotting it's better to keep arcs separate.

    the class supports plotting the arcs, so that it's not necessary to open GDS file to see the result. THe plot also
    includes numerical information such as the rate of change of curvature, which is useful for designing compelex arcs

    The two main functions are generate_arbitrary_arc() and generate_straight_wg() which provide core interface for
    producing arcs; the functions such as 180-deg bends just call generate_arbitrary_arc() with proper parameters.

    Description of the fields of an arc:
    each element of "arc_list" list is a dictionary with the following entries:
    x, y -- list of coordinates of the arc line
    x_norm, y_norm -- unit vector coordinates of the normal to the curve
    a -- parameter "a" of the clothoid; 1/a is the rate of curvature change
    length -- the length of the arc
    angle -- a 2-element vector with angle at the start & the end of the arc
    curvature -- a 2-element vector of curvature at the start & end of the arc
    width -- list of waveguide width values along the arc
    """

    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)

        self.params = params
        self.layer = params['layer']
        self.port_layer = params['port_layer']

        self.x_start = params.get('x_start', 0)
        self.y_start = params.get('y_start', 0)
        self.angle_start = params.get('angle_start', 0)

        self.arc_params = params['arc_params']
        self.merge_arcs = params['merge_arcs']
        self.show_plot = params.get('show_plot', False)
        self.show_plot_labels = params.get('show_plot_labels', False)
        self.pts_spacing = params.get('pts_spacing', 70 * self.grid.resolution)
        self.print_diagnostics = params.get('print_diagnostics', False)

        self.radius_threshold = params.get('radius_threshold', 0)
        self.curvature_rate_threshold = params.get('curvature_rate_threshold', float('NaN'))

        self.arc_list = []
        self.path_list = []

    @classmethod
    def get_default_param_values(cls) -> dict:
        return dict(
            layer=None,
            port_layer=None,
            x_start=None,
            y_start=None,
            angle_start=None,
            radius_threshold=None,
            curvature_rate_threshold=None,
            merge_arcs=None,
            show_plot=None,
            show_plot_labels=None,
            arc_params=None)

    @classmethod
    def get_params_info(cls) -> dict:
        return dict(
            layer="None",
            port_layer="None",
            x_start="None",
            y_start="None",
            angle_start="None",
            radius_threshold="None",
            curvature_rate_threshold="None",
            merge_arcs="None",
            show_plot="None",
            show_plot_labels="None",
            arc_params="None"
        )

    def draw_layout(self) -> None:

        for params in self.arc_params:

            if params['arc_type'] == 'straight_wg':
                arc_list = self.generate_straight_wg(params)

            elif params['arc_type'] == '90_bend':
                arc_list = self.generate_90_bend(params)

            elif params['arc_type'] == '180_bend':
                arc_list = self.generate_180_bend(params)

            elif params['arc_type'] == 'offset_bend':
                arc_list = self.generate_offset_bend(params)

            elif params['arc_type'] == 'wrapped_ring_coupler':
                arc_list = self.generate_wrapped_ring_coupler(params)
            elif params['arc_type'] == 'wrapped_ring_coupler1':
                arc_list = self.generate_wrapped_ring_coupler1(params)
            elif params['arc_type'] == 'wrapped_ring_coupler2':
                arc_list = self.generate_wrapped_ring_coupler2(params)

            elif params['arc_type'] == 'arbitrary_arc':
                arc_list = self.generate_arbitrary_arc(params)

            elif params['arc_type'] == '90bends_uturn':
                arc_list = self.generate_90_bends_uturn(params)

            else:
                raise ValueError('Unknown type of arc specified ({0}).'.format(params['arc_type']))

            self.append_arcs(arc_list)

        if self.merge_arcs:
            self.merge_all_arcs()

        self.convert_arc_to_path()
        self.place_path()

        if self.show_plot:
            self.plot_path()

        self.add_ports()

    # Arc generation functions #

    def generate_wrapped_ring_coupler(self, params):
        """
        wrap-around coupler, which consists of the following sections (assuming
        the start angle is zero, but actually the start angle can be specified in alpha_or_arc_list_in):
        1) Input section: change waveguide angle from 0 to alpha_zero_in, with 0
        curvature at both angles. Min bending radius in this section is rmin_in.
        2) Transition section: going from zero curvature at alpha_zero_in angle to R_coupling bending radius
        3) Coupling section: an arc with constant radius R_coupling, the angular size of the arc is angle_coupling.
        NOTE:
        if alpha_zero_in is negative, the ring is assumed to be above the waveguide
        if alpha_zero_in is positive, the ring is below.
        angle_coupling always > 0.
        """
        rmin_in = params['rmin_in']
        alpha_zero_in = params['alpha_zero_in']
        w_in = params['w_in']
        r_coupling = params['r_coupling']
        angle_coupling = params['angle_coupling']
        w_coupling = params['w_coupling']

        if isinstance(w_in, list):
            raise ValueError('w_in must be a scalar')

        if isinstance(w_coupling, list):
            raise ValueError('w_coupling must be a scalar')

        arc_list = []
        if abs(alpha_zero_in) < (angle_coupling / 2):
            raise ValueError(
                "The slope at the end of the input bend must exceed the slope of the const-R coupling region. In other "
                "words, must have abs(alpha_zero_in)>(angle_coupling/2)")

        if angle_coupling < 1e-13:
            raise ValueError(
                "Negative or zero angle of the const-R coupling region is not supported. If this is needed, use "
                "arbitrary arc instead.")

        u = -np.sign(alpha_zero_in)

        w_av = (w_in + w_coupling) / 2

        alpha = [0, alpha_zero_in / 2, alpha_zero_in, -u * angle_coupling / 2, +u * angle_coupling / 2, -alpha_zero_in,
                 -alpha_zero_in / 2, 0]

        K = [0, u / rmin_in, 0, -u / r_coupling, -u / r_coupling, 0, u / rmin_in, 0]

        if abs(w_in - w_coupling) > 1e-13:
            w = [w_in, w_av, w_coupling, w_coupling, w_coupling, w_coupling, w_av, w_in]
        else:
            w = w_av

        arc_list = self.generate_arbitrary_arc({'angle': alpha, 'curvature': K, 'width': w})

        return arc_list

    def generate_wrapped_ring_coupler1(self, params):
        """
        wrap-around coupler, which consists of the following sections (assuming
        the start angle is zero, but actually the start angle can be specified in alpha_or_arc_list_in):
        1) Input section: change waveguide angle from 0 to alpha_zero_in, with 0
        curvature at both angles. Min bending radius in this section is rmin_in.
        2) Transition section: going from zero curvature at alpha_zero_in angle to R_coupling bending radius
        3) Coupling section: an arc with constant radius R_coupling, the angular size of the arc is angle_coupling.
        NOTE:
        if alpha_zero_in is negative, the ring is assumed to be above the waveguide
        if alpha_zero_in is positive, the ring is below.
        angle_coupling always > 0.
        """
        rmin_in = params['rmin_in']
        alpha_zero_in = params['alpha_zero_in']
        w_in = params['w_in']
        r_coupling = params['r_coupling']
        angle_coupling = params['angle_coupling']
        w_coupling = params['w_coupling']

        if isinstance(w_in, list):
            raise ValueError('w_in must be a scalar')

        if isinstance(w_coupling, list):
            raise ValueError('w_coupling must be a scalar')

        arc_list = []
        if abs(alpha_zero_in) < (angle_coupling / 2):
            raise ValueError(
                "The slope at the end of the input bend must exceed the slope of the const-R coupling region. In other "
                "words, must have abs(alpha_zero_in)>(angle_coupling/2)")

        if angle_coupling < 1e-13:
            raise ValueError(
                "Negative or zero angle of the const-R coupling region is not supported. If this is needed, use "
                "arbitrary arc instead.")

        u = -np.sign(alpha_zero_in)

        w_av = (w_in + w_coupling) / 2

        alpha = [0, alpha_zero_in / 2, alpha_zero_in, -u * angle_coupling / 2, 0] #, +u * angle_coupling / 2, -alpha_zero_in,
                 #-alpha_zero_in / 2, 0]

        K = [0, u / rmin_in, 0, -u / r_coupling, -u / r_coupling] #, -u / r_coupling, 0, u / rmin_in, 0]

        if abs(w_in - w_coupling) > 1e-13:
            w = [w_in, w_av, w_coupling, w_coupling, w_coupling] #, w_coupling, w_coupling, w_av, w_in]
        else:
            w = w_av

        arc_list = self.generate_arbitrary_arc({'angle': alpha, 'curvature': K, 'width': w})

        return arc_list

    def generate_wrapped_ring_coupler2(self, params):
        """
        wrap-around coupler, which consists of the following sections (assuming
        the start angle is zero, but actually the start angle can be specified in alpha_or_arc_list_in):
        1) Input section: change waveguide angle from 0 to alpha_zero_in, with 0
        curvature at both angles. Min bending radius in this section is rmin_in.
        2) Transition section: going from zero curvature at alpha_zero_in angle to R_coupling bending radius
        3) Coupling section: an arc with constant radius R_coupling, the angular size of the arc is angle_coupling.
        NOTE:
        if alpha_zero_in is negative, the ring is assumed to be above the waveguide
        if alpha_zero_in is positive, the ring is below.
        angle_coupling always > 0.
        """
        rmin_in = params['rmin_in']
        alpha_zero_in = params['alpha_zero_in']
        w_in = params['w_in']
        r_coupling = params['r_coupling']
        angle_coupling = params['angle_coupling']
        w_coupling = params['w_coupling']

        if isinstance(w_in, list):
            raise ValueError('w_in must be a scalar')

        if isinstance(w_coupling, list):
            raise ValueError('w_coupling must be a scalar')

        arc_list = []
        if abs(alpha_zero_in) < (angle_coupling / 2):
            raise ValueError(
                "The slope at the end of the input bend must exceed the slope of the const-R coupling region. In other "
                "words, must have abs(alpha_zero_in)>(angle_coupling/2)")

        if angle_coupling < 1e-13:
            raise ValueError(
                "Negative or zero angle of the const-R coupling region is not supported. If this is needed, use "
                "arbitrary arc instead.")

        u = -np.sign(alpha_zero_in)

        w_av = (w_in + w_coupling) / 2

        alpha = [ +u * angle_coupling / 2, +u * angle_coupling / 2, -alpha_zero_in,
                 -alpha_zero_in / 2, 0]

        K = [ 0, -u / r_coupling, 0, u / rmin_in, 0]

        if abs(w_in - w_coupling) > 1e-13:
            w = [ w_coupling, w_coupling, w_av, w_in]
        else:
            w = w_av

        arc_list = self.generate_arbitrary_arc({'angle': alpha, 'curvature': K, 'width': w})

        return arc_list

    def generate_offset_bend(self, params):
        """
        generates an offset sideways (in y-direction); returns a list of 4 or 5 arcs
        offset > 0: shifting right, offset < 0: shifting left
        rmin is user-specified
        the mid-way angle is calculated automatically (by solving a nonlinear equation numerically). The largest
        mid-way angle is pi/2 (corresponding to 90-deg bend); if offset is too large to be covered with two 90-deg
        bends, a straight section is added between them (in which case 5 arcs are returned).
        Note that the x-size of the arc is not user specified so it's not known where the arc will end up along x axis
        """
        w = self._listize(params['width'])
        offset = params['offset']
        rmin = params['rmin']
        if rmin < 0:
            raise ValueError(
                'Offset_bend parameters error: minimum radius of curvature must be positive (but note that offset value'
                ' can be of either sign')

        length = params.get('length', None)
        length_add_at_the_end = params.get('length_add_at_the_end', True)

        arc_list = []

        if len(w) != 1 and len(w) != 2:
            raise ValueError('Either a single or a pair of width values need to be specified')

        offset_90deg = rmin * 1.870095846646268

        if abs(offset) > (2 * offset_90deg + 1e-13):  # need two 90-deg bends with a straight waveguide between them

            L_straight = abs(offset) - 2 * offset_90deg

            if len(w) == 1:
                w1 = w2 = w3 = w
            else:
                L_90deg = pi * rmin
                L_total = 2 * L_90deg + L_straight  # total path length

                w1 = [w[0], w[0] + (w[1] - w[0]) * L_90deg / L_total]
                w2 = [w1[1], w[0] + (w[1] - w[0]) * (L_90deg + L_straight) / L_total]
                w3 = [w2[1], w[1]]

            if offset < 0:
                turn_left = True
            else:
                turn_left = False

            D = dict()
            D['rmin'] = rmin
            D['turn_left'] = turn_left
            D['width'] = w1
            arc_list += self.generate_90_bend(D)

            arc_list += self.generate_straight_wg({'width': w2, 'length': L_straight})
            D['turn_left'] = not turn_left
            D['width'] = w3
            arc_list += self.generate_90_bend(D)

        else:

            t = brentq(self._find_offset_mismatch, 0, sqrt(pi / 2), args=(abs(offset), rmin), xtol=1e-10)

            angle4 = t ** 2 / 2
            curvature4 = 1 / rmin

            alpha = -np.array([0, 1, 2, 1, 0]) * np.sign(offset) * angle4
            curvature = -np.array([0, -1, 0, 1, 0]) * np.sign(offset) * curvature4

            if len(w) == 1:
                w_values = w
            elif len(w) == 2:
                w_values = list(np.linspace(w[0], w[1], len(alpha)))
            else:
                raise ValueError('A single value or a pair of width values should be specified')

            arc_list += self.generate_arbitrary_arc({'angle': alpha, 'curvature': curvature, 'width': w_values})

        if length is not None:

            arc_list = self._align_arc_list(arc_list)

            current_length = arc_list[-1]['x'][-1]
            if current_length > length:
                raise ValueError('Obtained length after required offset is already larger than the required length')
            else:
                if length_add_at_the_end:
                    arc_list += self.generate_straight_wg({'length': length-current_length, 'width': w[-1]})
                else:
                    tmp = self.generate_straight_wg({'length': length - current_length, 'width': w[-1]})
                    arc_list.insert(0, tmp[0])

        arc_list = self._align_arc_list(arc_list)

        return arc_list

    def generate_90_bend(self, params):
        """
        adiabatic 90-deg bend, returns two arcs going in curvature from 0 to max, and then from max back to 0
        either minimum radius rmin or the size of the bend can be specified
        width can contain 1 value, 2 values (start width and and width), or 3 values (start, middle, and end width).
        """
        if ('size' in params) and ('rmin' in params):
            raise ValueError('Either size or radius must be specified, but not both')

        if 'size' in params:
            radius = params['size'] / 1.870095846646268
        elif 'rmin' in params:
            radius = params['rmin']
        else:
            raise ValueError("Neither radius nor size of the 90 degree band are specified")

        width = self._listize(params['width'])
        if len(width) == 1 or len(width) == 3:
            w_path = width
        elif len(width) == 2:
            w_path = [width[0], (width[0] + width[1]) / 2, width[1]]
        else:
            raise ValueError("Either 1, 2, or 3 width values must be specified")

        if params['turn_left']:
            angle = [0, pi / 4, pi / 2]
            curvature = [0, -1 / radius, 0]
        else:
            angle = [0, -pi / 4, -pi / 2]
            curvature = [0, +1 / radius, 0]

        arc = self.generate_arbitrary_arc({'angle': angle, 'curvature': curvature, 'width': w_path})

        return arc

    def generate_90_bends_uturn(self, params):
        """
        adiabatic 90-deg bend, returns two arcs going in curvature from 0 to max, and then from max back to 0
        either minimum radius rmin or the size of the bend can be specified
        width can contain 1 value, 2 values (start width and and width), or 3 values (start, middle, and end width).
        """

        arc_list = []

        D = deepcopy(params)


        arc_list += self.generate_90_bend(D)
        arc_list += self.generate_straight_wg(D)
        arc_list += self.generate_90_bend(D)

        # return arc_list

        return arc_list



    def generate_180_bend(self, params):
        """
        adiabatic 180-deg bend, returns two arcs going in curvature from 0 to max, and then from max back to 0
        either minimum radius rmin or the size of the bend can be specified
        width can contain 1 value, 2 values (start width and and width), or 3 values (start, middle, and end width).
        """
        if 'size' in params.keys():
            radius = params['size'] / 2.753663435620129

        elif 'rmin' in params.keys():
            radius = params['rmin']

        else:
            raise ValueError("Neither radius nor size of the 90 degree band are specified")

        width = self._listize(params['width'])
        if len(width) == 1 or len(width) == 3:
            w_path = width
        elif len(width) == 2:
            w_path = [width[0], (width[0] + width[1]) / 2, width[1]]
        else:
            raise ValueError("Either 1, 2, or 3 width values must be specified")

        if params['turn_left']:
            angle = [0, pi / 2, pi]
            curvature = [0, -1 / radius, 0]
        else:
            angle = [0, -pi / 2, -pi]
            curvature = [0, +1 / radius, 0]

        arc = self.generate_arbitrary_arc({'angle': angle, 'curvature': curvature, 'width': w_path})
        return arc

    def generate_straight_wg(self, params):
        # generates an arc for a straight waveguide
        # starts at (0,0) wih angle=0

        length = params['length']
        width = self._listize(params['width'])
        if len(width) != 1 and len(width) != 2:
            raise ValueError('Straight waveguide width must contain 1 or 2 values')

        D = dict()
        D['x'] = np.array([0, length])
        D['y'] = np.array([0, 0])
        D['curvature'] = np.array([0, 0])
        D['x_norm'] = np.array([0, 0])
        D['y_norm'] = np.array([1, 1])
        if len(width) == 1:
            D['width'] = np.array([width[0], width[0]])
        else:
            D['width'] = np.array(width)
        D['length'] = length
        D['a'] = float('Inf')
        D['angle'] = [0.0, 0.0]

        return [D]

    def generate_arbitrary_arc(self, params):
        """
        A very important function which creates a list of arcs connecting points with user-specified
        angles and curvatures. All other arc generation functions (except generate_straight_wg() just call this
        function with proper parameters.

        The arc is an adiabatic (clothoid, or Euler) bend with curvature changing linearly along each arc. Each arc
        has a constant rate of change of curvature, and the rate of change of curvature can be different for different
        arcs. It is acceptable to have curvature of the start and the end points be
        equal, in this case it is just treated as a circle.

        INPUTS
        angle is the list of slopes of the start and the end point of the arcs
              must contain N+1 elements for N arcs
        K are the curvatures at the points of the arcs; can be arrays when multiple
                       arcs are needed
        w are the waveguide widths. Can be a single value (constant width) or a
                       list of N+1 values (one value per arc end point)
        self.pts_spacing defines the spacing at which arc points are generated

        OUTPUTS: arc_list is a list each element of which is a dictionary with the following elements:
        x, y are the coordinates of the center of the arc.
        w are the widths; can be a single value or a list
        x_norm, y_norm defines the normal unit vectors, which points to the left relative to travel direction

        NOTE: the 1st point of the 1st list is always (0,0), and the slope is zero too!
        An error is generated if angle[0] is not zero. To produce an arc which starts from specific angle and
        coordinate, parameters of the class self.x_start, self.y_start, self.angle_start can be used (or the arc can
        be stitched to another arc)
        """

        angle = params['angle']
        curvature = params['curvature']
        width = self._listize(params['width'])

        N = len(angle) - 1
        if len(curvature) != (N + 1): raise ValueError(
            'The number of arc curvatures doesnt match the number of arc angles')
        if (len(width) != 1) and (len(width) != (N + 1)): raise ValueError(
            'Incorrect number of widths provided; should be 1 or equal length to curvature and angle')

        if abs(angle[0]) > 1e-14:
            raise ValueError(
                'The start angle of the arc is not zero; if arc_list_in is specified, the arc "angle" must start from '
                'zero angle and the start angle will be taken from angle parameter')

        arc_list = [dict() for i in range(N)]

        for i in range(N):

            if self.print_diagnostics:
                print('Arc {}: angle {}->{} ({})  R= {} ({})-> {} ({})   '.format(i, angle(i) * 180 / pi,
                                                                                  # TODO: fix formating
                                                                                  angle[i + 1] * 180 / pi,
                                                                                  self.LR(angle[i + 1] - angle[i]),
                                                                                  1 / curvature[i],
                                                                                  self._lr(-curvature[i]),
                                                                                  1 / curvature[i + 1],
                                                                                  self._lr(-curvature(i + 1))))

            if abs(curvature[i] - curvature[i + 1]) > 1e-4:  # adiabatic curve
                arc_list[i] = self._calculate_adiabatic_line(angle1=angle[i], angle2=angle[i + 1],
                                                             curvature1=curvature[i], curvature2=curvature[i + 1])
                if self.print_diagnostics: print('curv. change rate (1/a)={:5.3f}\n'.format(1 / arc_list[i]['a']))
            else:
                arc_list[i] = self._calculate_circular_line(angle1=angle[i], angle2=angle[i + 1],
                                                            curvature=(curvature[i] + curvature[i + 1]) / 2)
                if self.print_diagnostics:
                    print('Circle; curvature=const\n')

            arc_list[i]['angle'] = angle[i:i + 2]
            arc_list[i]['curvature'] = curvature[i:i + 2]
            M = len(arc_list[i]['x'])

            if len(width) == 1:
                arc_list[i]['width'] = width[0] * np.ones(M)
            else:
                arc_list[i]['width'] = np.linspace(width[i], width[i + 1], M, endpoint=True)

        # put the beginning of each arc at the end of the previous arc
        # this of course assumes that each arc starts from the origin, i.e. (0,0)
        for i in range(1, len(arc_list)):
            arc_list[i]['x'] += arc_list[i - 1]['x'][-1]
            arc_list[i]['y'] += arc_list[i - 1]['y'][-1]

        for arc in arc_list:
            if 1 / arc['a'] > self.curvature_rate_threshold:
                raise ValueError(
                    'Rate of change of curvature is higher than allowed by parameter curvature_rate_threshold; aborting'
                    ' to avoid excessive optical loss.')

            if abs(self.radius_threshold) < 1e-30:
                curvature_threshold = float('Inf')
            else:
                curvature_threshold = 1 / self.radius_threshold

            if (abs(arc['curvature'][0]) > curvature_threshold) or (abs(arc['curvature'][1]) > curvature_threshold):
                raise ValueError(
                    'Rate of change of curvature is higher than allowed by parameter curvature_rate_threshold; aborting'
                    ' to avoid excessive optical loss.')

            self.radius_threshold = params.get('radius_threshold', 0)

        return arc_list

    # Arc manipulation and plotting functions #

    def append_arcs(self, arc_list_to_append):
        """
        adds arc_list_to_append to the internal arc_list of the class
        aligns the start coordinates and the angle of arc_list_to_append
        to the last arc in self.arc_list. If self.arc_list is empty, aligns the arcs
        according to user-specified self.x_start, self.y_start, self.angle_start
        """
        if not arc_list_to_append:
            return

        for arc in arc_list_to_append:

            if not self.arc_list:  # align using user-specified coordinates and the angle
                arc_aligned = self._align_arc(arc, x0=self.x_start, y0=self.y_start, angle=self.angle_start)
            else:  # align to the previous arc already in the list
                arc_aligned = self._align_arc(arc, previous_arc=self.arc_list[-1])

            self.arc_list += [arc_aligned]
            self._check_arc_continuity(last_only=True)  # check if the last added arc is continuous with
            # the previous arc. Will raise an exception if e.g. width is discontinuous.

    def merge_all_arcs(self):
        """
        merges all arcs in self.arc_list into a single arc
        """
        if not self.arc_list:
            return

        merged = deepcopy(self.arc_list[0])

        # CheckArcContinuity(arc_list)

        for i in range(1, len(self.arc_list)):
            arc = self.arc_list[i]

            merged['x'] = np.concatenate((merged['x'], arc['x'][1:]))
            merged['y'] = np.concatenate((merged['y'], arc['y'][1:]))
            merged['x_norm'] = np.concatenate((merged['x_norm'], arc['x_norm'][1:]))
            merged['y_norm'] = np.concatenate((merged['y_norm'], arc['y_norm'][1:]))
            merged['width'] = np.concatenate((merged['width'], arc['width'][1:]))

        merged['curvature'][-1] = self.arc_list[-1]['curvature'][1]
        merged['angle'][-1] = self.arc_list[-1]['angle'][1]

        total_length = 0
        for arc in self.arc_list:
            total_length += arc['length']

        merged['length'] = total_length

        for i in range(1, len(self.arc_list)):
            if abs(self.arc_list[i - 1]['a'] - self.arc_list[i]['a']) > 1e-14:
                merged['a'] = float('nan')
            break

        self.arc_list = [merged]

    def convert_arc_to_path(self):
        """
        converts arcs from self.arc_list to polygons in self.path_list
        arcs contain center coordinates, width, and normal unit vectors
        so it's easy to create polygons based on this information
        """
        self._check_arc_continuity()  # check just in case. There should be no discontinuities if the code is working
        # properly but it doesn't hurt to check one more time

        path_list = []

        for arc in self.arc_list:
            x_left = arc['x'] + arc['x_norm'] * arc['width'] / 2
            y_left = arc['y'] + arc['y_norm'] * arc['width'] / 2
            x_right = arc['x'] - arc['x_norm'] * arc['width'] / 2
            y_right = arc['y'] - arc['y_norm'] * arc['width'] / 2

            D = dict()
            D['x'] = np.concatenate([x_left, np.flipud(x_right), np.array([x_left[0]])])
            D['y'] = np.concatenate([y_left, np.flipud(y_right), np.array([y_left[0]])])
            D['length'] = arc['length']

            self.path_list.append(D)

    def place_path(self):
        # add polygons from self.poly_list to BPG object list

        for path in self.path_list:
            points = np.stack([path['x'], path['y']], 1)

            poly = PhotonicPolygon(
                resolution=self.grid.resolution,
                layer=self.layer,
                points=points.tolist(),
                unit_mode=False, )
            self.add_obj(poly)

    def plot_path(self):
        """
        plots the obtains polygons in self.poly_list. This is useful for:
        (a) quickly checking the bend without having to open the gds file
        (b) seeing which parts the overall bend is composed of; note that even simple bends can be composed of more
        than one part: for example, 180-deg bend has two parts, where curvature goes 0--> max, and max-->0
        (c) examining the properties of the bends using numerical data displayed next to the bends when
        self.show_plot_labels==True. This data includes angles and curvatures at the start and the end of each arc,
        and curvature change rate along each arc.
        """

        def add_point_label(arc, idx, plot_size):

            shift = max([arc['width'][idx] * 0.75, 1])

            x_text = [arc['x'][idx] + arc['x_norm'][idx] * shift, arc['x'][idx] - arc['x_norm'][idx] * shift]
            y_text = [arc['y'][idx] + arc['y_norm'][idx] * shift, arc['y'][idx] - arc['y_norm'][idx] * shift]

            if arc['x_norm'][idx] < 0:
                x_text[0] = x_text[0] - abs(arc['x_norm'][0]) * plot_size / 30
            else:
                x_text[1] = x_text[1] - abs(arc['x_norm'][0]) * plot_size / 30

            curv = arc['curvature'][idx]
            if abs(curv) < 1e-20:
                curv_text = 'Inf'
            else:
                curv_text = '{0:.2f}'.format(1 / curv)

            plt.text(x_text[0], y_text[0], 'R=' + curv_text, fontsize=8)
            plt.text(x_text[1], y_text[1], '{0:.2f}\u03C0'.format(arc['angle'][idx] / pi), fontsize=8)

        for path in self.path_list:
            plt.plot(path['x'], path['y'])

        plt.axis('equal')

        if self.show_plot_labels:

            min_x = float('Inf')
            min_y = float('Inf')
            max_x = -float('Inf')
            max_y = -float('Inf')

            for arc in self.arc_list:
                min_arc_x = np.min(arc['x'])
                min_arc_y = np.min(arc['y'])
                max_arc_x = np.max(arc['x'])
                max_arc_y = np.max(arc['y'])

                if min_arc_x < min_x:
                    min_x = min_arc_x
                if min_arc_y < min_y:
                    min_y = min_arc_y
                if max_arc_x > max_x:
                    max_x = min_arc_x
                if max_arc_x > max_x:
                    max_y = max_arc_y

            plot_size = max([max_x - min_x, max_y - min_y])

            for arc in self.arc_list:

                add_point_label(arc, 0, plot_size)

                if len(arc['x']) % 2 == 1:
                    n2 = round((len(arc['x']) - 1) / 2)
                    xc = arc['x'][n2]
                    yc = arc['y'][n2]
                else:
                    n2 = round(len(arc['x']) / 2) - 1
                    xc = (arc['x'][n2] + arc['x'][n2 + 1]) / 2
                    yc = (arc['y'][n2] + arc['y'][n2 + 1]) / 2

                plt.text(xc, yc, '{0:.3f}'.format(1 / arc['a']), color='blue', fontsize=7)

            add_point_label(self.arc_list[-1], -1, plot_size)
            plt.figtext(0.1, 0.01, 'Blue numbers curvature change rate = d(curvature)/dL = 1/a', color='blue',
                        fontsize=9)

        total_length = 0
        for arc in self.arc_list:
            total_length += arc['length']

        plt.title('Total length = {0:.3f}'.format(total_length), fontsize=10)

        plt.grid()
        plt.show()

    # Internal functions not intended to be called by users #

    def _calculate_adiabatic_line(self, angle1, angle2, curvature1, curvature2):
        """
        # the main function of the class
        # generates an arc which is a part of Euler (clothoid) curve
        # connecting two points with given slopes angle1, angle2 and curvatures
        # curvature1, curvature2.
        # not supposed to be called directly but through generate_arbitrary_arc()
        """

        if abs(abs(curvature1) - abs(curvature2)) < 1e-13:
            if abs(angle1 - angle2) < 1e-13:
                raise ValueError(
                    'Adiabatic bend error: Solution is not unique when start angle=end angle, '
                    'abs(start curvature)=abs(end curvature). Consider adding intermediate points on the curve.')
            else:
                raise ValueError('Adiabatic bend error: No solution when abs(start curvature)=abs(end curvature)')

        XX = 2 * (angle2 - angle1) / (
                curvature2 ** 2 - curvature1 ** 2)  # from properties of clothoid curves; see my word notes

        if curvature1 > curvature2:  # curvature is decreasing
            if XX > 0:
                a = np.sqrt(XX)
            else:
                raise ValueError(
                    'Adiabatic bend error: impossible to generate the bend with given angles and curvatures')

            t1 = -a * curvature1
            t2 = -a * curvature2
            obtained_alpha1 = t1 ** 2 / 2
        else:
            if XX < 0:
                a = np.sqrt(-XX)
            else:
                raise ValueError(
                    'Adiabatic bend error: impossible to generate the bend with given angles and curvatures')

            t1 = a * curvature1
            t2 = a * curvature2
            obtained_alpha1 = -t1 ** 2 / 2

        rotation_angle = angle1 - obtained_alpha1

        length = a * abs(t2 - t1)  # from properties of clothoid curve
        Npts = np.ceil(length / self.pts_spacing) + 1

        t = np.linspace(t1, t2, int(Npts), endpoint=True)

        temp = fresnel(t / np.sqrt(pi))
        x1 = a * np.sqrt(pi) * temp[1]
        y1 = a * np.sqrt(pi) * temp[0]
        # find tangent unit vector
        tangent_x1 = np.cos(t ** 2 / 2)  # from properties of clothoid curve
        tangent_y1 = np.sin(t ** 2 / 2)

        if curvature2 > curvature1:  # increasing curvature case
            y1 = -y1
            tangent_y1 = -tangent_y1

        # put the beginning at zero; important also because we'll be rotating around this point
        x1 = x1 - x1[0]
        y1 = y1 - y1[0]

        # rotate the curve by rotation_angle. The curve starts with (0,0) points so it's rotated around this point.
        x = x1 * np.cos(rotation_angle) - y1 * np.sin(rotation_angle)
        y = x1 * np.sin(rotation_angle) + y1 * np.cos(rotation_angle)

        # need to rotate the tangent too this can be made more efficient by substituting cos(t.^2 /2) above when
        # we find unrotated tangent directly with cos(t**2 /2 + rotation_angle).
        # Keeping it slow and simple for now.
        x_tan = tangent_x1 * np.cos(rotation_angle) - tangent_y1 * np.sin(rotation_angle)
        y_tan = tangent_x1 * np.sin(rotation_angle) + tangent_y1 * np.cos(rotation_angle)

        # find the normal
        x_norm = -y_tan
        y_norm = x_tan

        D = dict()
        D['x'] = x
        D['y'] = y
        D['x_norm'] = x_norm
        D['y_norm'] = y_norm
        D['a'] = a
        D['length'] = length

        return D

    def _calculate_circular_line(self, angle1, angle2, curvature):
        # finds coordinates of a circular arc with given curvature. The arc starts with slope "angle1" and ends with
        # slope "angle2"
        # returns a dictionary with x, y, x_norm, y_norm, L
        # not supposed to be called directly but through generate_arbitrary_arc()

        # note that angle1 and angle2 are the slope angles, NOT the arc angles (i.e. angle1=0, angle2=pi/2 will
        # generate an arc in 4th quadrant, not 1st quadrant).

        if curvature > 0:
            arc_angle1 = angle1 + pi / 2
            arc_angle2 = angle2 + pi / 2
        else:
            arc_angle1 = angle1 - pi / 2
            arc_angle2 = angle2 - pi / 2

        if ((arc_angle2 - arc_angle1) > 0) and (curvature > 0):
            raise ValueError('Circular bend error: impossible to generate the bend with given angles and curvatures')
        elif ((arc_angle2 - arc_angle1) < 0) and (curvature < 0):
            raise ValueError('Circular bend error: impossible to generate the bend with given angles and curvatures')

        radius = abs(1 / curvature)

        length = radius * abs(angle2 - angle1)

        Npts = np.ceil(length / self.pts_spacing) + 1

        alpha = np.linspace(arc_angle1, arc_angle2, int(Npts), endpoint=True)

        x_norm = np.cos(alpha)
        y_norm = np.sin(alpha)

        x1 = radius * x_norm
        y1 = radius * y_norm

        x = x1 - x1[0]
        y = y1 - y1[0]

        if curvature < 0:
            x_norm = -x_norm  # to make sure the left/right boundaries are not mixed up
            y_norm = -y_norm

        D = dict()
        D['x'] = x
        D['y'] = y
        D['x_norm'] = x_norm
        D['y_norm'] = y_norm
        D['a'] = float('inf')
        D['length'] = length

        return D

    def _align_arc(self, arc, previous_arc=None, x0=None, y0=None, angle=None):
        """
        if previous_arc is provided, aligns "arc" to it, i.e. places the beginning of the arc at the end of
        previous_arc in terms of coordinates and the angle.
        if previous_arc is not provided, it is expected that x0, y0, and angle are provided, which are used for
        aligning the supplied "arc"
        """
        if previous_arc is None:
            if x0 is None:
                x0 = 0
            if y0 is None:
                y0 = 0
            if angle is None:
                angle = 0
        else:
            if (x0 is not None) or (y0 is not None) or (angle is not None):
                raise ValueError('Either previous_arc or x0, y0, angle should be specified, but not both')
            x0 = previous_arc['x'][-1]
            y0 = previous_arc['y'][-1]
            angle = previous_arc['angle'][1]

        rotation_angle = angle - arc['angle'][0]

        # if (abs(arc['x'][0]) > 1e-14) or (abs(arc['y'][0]) > 1e-14): # TODO: figure out if it's needed
        #  raise ValueError('Internal error: the arc to be aligned does not start at origin')

        x = arc['x'] - arc['x'][0]
        y = arc['y'] - arc['y'][0]

        arc_aligned = dict()

        arc_aligned['x'] = x0 + x * np.cos(rotation_angle) - y * np.sin(rotation_angle)
        arc_aligned['y'] = y0 + x * np.sin(rotation_angle) + y * np.cos(rotation_angle)

        arc_aligned['x_norm'] = arc['x_norm'] * np.cos(rotation_angle) - arc['y_norm'] * np.sin(rotation_angle)
        arc_aligned['y_norm'] = arc['x_norm'] * np.sin(rotation_angle) + arc['y_norm'] * np.cos(rotation_angle)

        arc_aligned['curvature'] = deepcopy(arc['curvature'])
        arc_aligned['width'] = deepcopy(arc['width'])
        arc_aligned['length'] = arc['length']  # scalar
        arc_aligned['a'] = arc['a']  # scalar
        arc_aligned['angle'] = [arc['angle'][0] + rotation_angle, arc['angle'][1] + rotation_angle]

        return arc_aligned

    def _align_arc_list(self, arc_list):
        """
        aligns all arcs in self.arc_list by placing the beginning of each arc at the end of the previous arc in terms
        of coordinates and the angle.
        """
        arc_list_aligned = [deepcopy(arc_list[0])]

        for i in range(1, len(arc_list)):
            arc_list_aligned.append(self._align_arc(arc_list[i], arc_list_aligned[i - 1]))

        return arc_list_aligned

    def _check_arc_continuity(self, last_only=False):
        """
        checks if the arcs in self.arc_list are continuous, i.e. whether the 1st point of the arc is the same as the
        last point of the previous arc
        if last_only==False, checks all arcs in self.arc_list
        if last_only==True, checks only the last arc (whether it's continuous with the last-but-one arc
        in self.arc_list)
        """
        N = len(self.arc_list)

        if N < 2:
            return

        if last_only:
            indices = range(N - 1, N)
        else:
            indices = range(1, N)

        for i in indices:

            d_x = self.arc_list[i]['x'][0] - self.arc_list[i - 1]['x'][-1]
            d_y = self.arc_list[i]['y'][0] - self.arc_list[i - 1]['y'][-1]
            d_x_norm = self.arc_list[i]['x_norm'][0] - self.arc_list[i - 1]['x_norm'][-1]
            d_y_norm = self.arc_list[i]['y_norm'][0] - self.arc_list[i - 1]['y_norm'][-1]
            d_alpha = self.arc_list[i]['angle'][0] - self.arc_list[i - 1]['angle'][1]
            d_K = self.arc_list[i]['curvature'][0] - self.arc_list[i - 1]['curvature'][1]
            d_w = self.arc_list[i]['width'][0] - self.arc_list[i - 1]['width'][-1]

            d_alpha = d_alpha - 2 * pi * round(d_alpha / (2 * pi))

            if sqrt(d_x ** 2 + d_y ** 2) > 1e-14:
                raise ValueError('Internal error. Arc list mismatch: coordinates are discontinuous.')

            if sqrt(d_x_norm ** 2 + d_y_norm ** 2) > 1e-14:
                raise ValueError('Internal error. Arc list mismatch: normal is discontinuous.')

            if abs(d_alpha) > 1e-14:
                raise ValueError('Internal error. Arc list mismatch: slope angle is discontinuous.')

            if abs(d_K) > 1e-14:
                raise ValueError('Internal error. Arc list mismatch: curvature is discontinuous.')

            if abs(d_w) > 1e-14:
                raise ValueError(
                    'Internal error. Arc list mismatch: width between {}  and {} arc is discontinuous.'.format(i,
                                                                                                               i - 1))

    def _find_offset_mismatch(self, t_guess, target_offset, rmin):
        """
        a helper function for generate_offset_bend() where it's used in nonlinear equaton solver
        given a guess of t parameter, provides a mismatch between target offset and obtained offset
        """
        if abs(t_guess) < 1e-14:
            mismatch = target_offset
        else:
            a = t_guess * rmin  # this is the parameter a of the clothoid
            temp = fresnel(t_guess / sqrt(pi))
            x1 = a * np.sqrt(pi) * temp[1]
            y1 = a * np.sqrt(pi) * temp[0]
            b = t_guess ** 2 / 2
            d = np.arctan(y1 / x1)
            c = b - d
            A = sqrt(x1 ** 2 + y1 ** 2)
            L = 2 * A * np.cos(c)
            obtained_offset = 2 * L * np.sin(b)
            mismatch = target_offset - obtained_offset

        return mismatch

    def _listize(self, x):
        """
        if x is a scalar, converts it into a one-element list
        conventient for handling cases when input parameters can be a scalar or a list
        such as width parameter.
        """
        if isinstance(x, list):
            return x
        else:
            return [x]

    def _lr(self, x):
        if x > 1e-13:
            return 'L'
        elif x < 1e-13:
            return 'R'
        else:
            return '|'

    def add_ports(self):
        self.add_photonic_port(
            name='PORT_IN',
            orient='R0',
            angle=self.angle_start,
            center=(0, 0),
            width=self.arc_list[0]['width'][0],
            layer=self.port_layer,
            resolution=self.grid.resolution,
            unit_mode=False,
            show=False)

        if self.arc_params[-1]['arc_type'] == 'straight_wg':
            x = (self.path_list[-1]['x'][2] + self.path_list[-1]['x'][1]) / 2
            y = (self.path_list[-1]['y'][2] + self.path_list[-1]['y'][1]) / 2
            self.add_photonic_port(
                name='PORT_OUT',
                orient='R180',
                angle=self.arc_list[-1]['angle'][1],
                center=(x, y),
                width=self.arc_list[-1]['width'][-1],
                layer=self.port_layer,
                resolution=self.grid.resolution,
                unit_mode=False,
                show=False)
        else:

            l = len(self.path_list[-1]['y'])
            if l % 2 == 1:
                l += 1

            l = int(l / 2)
            x = (self.path_list[-1]['x'][l - 1] + self.path_list[-1]['x'][l - 2]) / 2
            y = (self.path_list[-1]['y'][l - 1] + self.path_list[-1]['y'][l - 2]) / 2
            self.add_photonic_port(
                name='PORT_OUT',
                orient='R180',
                angle=self.arc_list[-1]['angle'][1],
                center=(x, y),
                width=self.arc_list[-1]['width'][-1],
                layer=self.port_layer,
                resolution=self.grid.resolution,
                unit_mode=False,
                show=False)
