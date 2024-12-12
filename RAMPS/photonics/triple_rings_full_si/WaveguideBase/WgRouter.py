import BPG
from Photonic_Core_Layout.Taper.LinearTaper import LinearTaper
from Photonic_Core_Layout.WaveguideBase.CircularBend import Circular90Bend
from Photonic_Core_Layout.WaveguideBase.EulerBendWaveguide import EulerBendWaveguide
import numpy as np
import logging

from typing import TYPE_CHECKING, Optional, List, Tuple, Dict
from BPG.bpg_custom_types import *

from Photonic_Core_Layout.WaveguideBase.SBendWaveguide import SBendWaveguide
# from phot_gen.phot_base.phot_waveguide import SBendPathWaveguide
from Photonic_Core_Layout.WaveguideBase.trajectory_waveguide import SBendPathWaveguide

if TYPE_CHECKING:
    from BPG.port import PhotonicPort


class WgRouter:
    """
    This class enables easy waveguide routing. This class consumes your generator class,
    and calls self.new_template(), self.add_instance_port_to_port(), etc. to iteratively add wg
    components for routing. You must initialize this class by providing a starting port. Then,
    you can repeatedly call methods such as add_90_bend() and add_straight_wg() to add a wg
    component to the end of the route.

    Examples
    --------
    from Photonic_Core_Layout.WaveguideBase.WgRouter import WgRouter
    ExampleCls(BPG.PhotonicTemplateBase):
        def draw_layout(self):
            self.add_photonic_port(name='init_port',
                                   center=(0, 0),
                                   orient='R0',
                                   width=1.0,
                                   layer='SI')
            router = WgRouter(gen_cls=self,
                              init_port=self.get_photonic_port('init_port'),
                              layer=('SI', 'drawing'),
                              name='route1')
            # Draw a straight waveguide and then a U-turn
            (router
             .add_straight_wg(length=10.0)
             .add_90_circular_bend(radius=5.0, direction='right')
             .add_90_circular_bend(radius=5.0, direction='right'))
    """

    # This dictionary allows routes to easily check which direction the current port is pointing in
    port_direction_mapping = {
        '+x': ['R180', 'MY'],
        '-x': ['R0', 'MX'],
        '+y': ['R270', 'MYR90'],
        '-y': ['R90', 'MXR90'],
    }

    # Set of allowed bend types for the cardinal router
    bend_types = ('circular', 'euler')

    def __init__(self, gen_cls, init_port, layer, name=''):
        self.gen_cls: BPG.PhotonicTemplateBase = gen_cls
        self.port: PhotonicPort = init_port
        self.inst = None
        self.layer = layer
        self.name = name
        self._bend_params = None

    @property
    def bend_params(self) -> Dict:
        return self._bend_params

    @bend_params.setter
    def bend_params(self,
                    bend_params: Dict,
                    ) -> None:
        """
        Set the bend parameters for the current router object.

        Parameters
        ----------
        bend_params : Dict
            See WgRouter.process_bend_params for details.

        """
        self._bend_params = self.process_bend_params(bend_params)

    def set_default_bend_params(self,
                                bend_params: Dict,
                                ) -> None:
        """
        Set the default bend parameters for the current router object.

        Parameters
        ----------
        bend_params : Dict
            See WgRouter.process_bend_params for details.

        """
        self._bend_params = self.process_bend_params(bend_params)

    def process_bend_params(self,
                            bend_params: Dict) -> Dict:
        """
        Processes the passed bend parameters and returns a valid bend_params dictionary with the proper defaults from
        the WgRouter settings.

        Parameters
        ----------
        bend_params : Dict
            A set of bend parameters to specify the bends.

            Parameters:
            -----------
                radius : float
                    Bend radius

            Optional Parameters:
            -------------------
                bend_type : str
                    Type of bend to use. Allowed options are listed in WgRouter.bend_types.  Defaults to 'circular'


        Returns
        -------
        params : Dict
            The valid bend parameters to use
        """

        if bend_params is None:
            if self.bend_params is None:
                raise ValueError(f'Default bend parameters not yet set. '
                                 f'Must either call WgRouter.bend_params = <bend_params_here> to set the default '
                                 f'parameters, or must pass a valid set of bend_params to current method call.')
            return self.bend_params

        else:
            if bend_params.get('already_processed', False):
                return bend_params
            else:
                bend_type = bend_params.get('bend_type')
                if bend_type not in self.bend_types:
                    raise ValueError(f'Unsupported bend type: {bend_type}. '
                                     f'Currently supported types are: {self.bend_types} '
                                     f'"bend_type" must be specified in bend_params.')

                if bend_type == 'circular':
                    params = dict()

                    for required_key in ['bend_type', 'radius']:
                        if required_key not in bend_params.keys():
                            raise ValueError(f'Specification of key {required_key} is '
                                             f'required for type circular bend params.')
                        params[required_key] = bend_params[required_key]

                    for disallowed_key in ['width', 'layer']:
                        if disallowed_key in params.keys():
                            raise ValueError(f'Specification of key {disallowed_key} is not allowed in bend_params.')

                elif bend_type == 'euler':
                    params = dict()

                    for required_key in ['bend_type', 'euler_percent', 'radius']:
                        if required_key not in bend_params.keys():
                            raise ValueError(f'Specification of key {required_key} is required '
                                             f'for type euler bend params.')
                        params[required_key] = bend_params[required_key]

                    for disallowed_key in ['width', 'theta_deg', 'layer']:
                        if disallowed_key in params.keys():
                            raise ValueError(f'Specification of key {disallowed_key} is not allowed in bend_params.')

                    params['theta_deg'] = 90
                    for optional_key in ['num', 'num_iterations', 'error_tolerance']:
                        if optional_key in bend_params:
                            params.update({optional_key: bend_params[optional_key]})
                else:
                    raise ValueError(f'Unrecognized bend. Should never be reached.')

                params['layer'] = self.layer
                params['width'] = self.port.width
                params['already_processed'] = True

                return params

    def add_straight_wg(self,
                        length: float,
                        out_width: Optional[float] = None
                        ) -> 'WgRouter':
        """
        Adds a straight waveguide to the current route. Can optionally linearly taper to a
        different waveguide width

        Parameters
        ----------
        length : float
            length of the waveguide to be drawn
        out_width : Optional[float]
            width at the output of the straight waveguide

        Returns
        -------
        self : WgRouter
            returns itself so that route segments can be easily chained together
        """
        if abs(length) <= self.gen_cls.grid.resolution:
            logging.warning(f'Attempted to generate a waveguide with near-zero length: {length}')
            return self

        if out_width is None:
            out_width = self.port.width
        params = dict(width0=self.port.width,
                      width1=out_width,
                      length=length,
                      layer=self.layer
                      )
        master = self.gen_cls.new_template(params=params, temp_cls=LinearTaper)
        inst = self.gen_cls.add_instance_port_to_port(inst_master=master,
                                                      instance_port_name='PORT0',
                                                      self_port=self.port,
                                                      reflect=False)
        # Move the current port pointer to the end of the new straight waveguide
        self.port = inst['PORT1']
        self.inst = inst
        return self

    def add_90_bend(self,
                    direction: str,
                    bend_params: Optional[Dict] = None,
                    ) -> 'WgRouter':
        """
        Adds a 90 degree circular bend to the current route.

        Parameters
        ----------
        bend_params : Optional[Dict]
            Dictionary of bend parameters.
            Required parameters:
            -------------------
                radius : Bend radius
            Optional parameters:
            -------------------
                type : 'circular' or 'euler'.  Defaults to 'circular'
        direction : str
            'right' or 'left' to tell what direction the route should bend

        Returns
        -------
        self : WgRouter
            returns itself so that route segments can be easily chained together
        """
        # Set the reflect parameter to match the desired routing direction
        if direction == 'right':
            reflect = True
        elif direction == 'left':
            reflect = False
        else:
            raise ValueError(f'{direction} is not a valid routing direction')

        bend_params = self.process_bend_params(bend_params)
        bend_type = bend_params['bend_type']

        if bend_type == 'circular':
            master = self.gen_cls.new_template(params=bend_params, temp_cls=Circular90Bend)
            inst = self.gen_cls.add_instance_port_to_port(inst_master=master,
                                                          instance_port_name='INPUT',
                                                          self_port=self.port,
                                                          reflect=reflect)
            self.port = inst['OUTPUT']
            self.inst = inst

        elif bend_type == 'euler':
            master = self.gen_cls.new_template(params=bend_params, temp_cls=EulerBendWaveguide)
            inst = self.gen_cls.add_instance_port_to_port(inst_master=master,
                                                          instance_port_name='PORT0',
                                                          self_port=self.port,
                                                          reflect=reflect)
            self.port = inst['PORT1']
            self.inst = inst
        else:
            raise ValueError(f'Unrecognized bend. Should never be reached.')

        return self

    def add_cosine_s_bend(self):
        pass

    def add_polygon_s_bend(self,
                           length:     float,
                           shift_left: float,
                           out_width: Optional[float] = None
                       ) -> 'WgRouter':
        """
        Adds an s-bend waveguide to the current route. 

        Parameters
        ----------
        length : float
            length of the waveguide to be drawn
        shift_left: float
            shift if microns of the path transverse to length, positive to the left and negative to the right
        out_width : Optional[float]
            width at the output of the straight waveguide

        Returns
        -------
        self : WgRouter
            returns itself so that route segments can be easily chained together
        """
        # if out_width is None:
        #     out_width = self.port.width
        # if out_width is not None:
        #     rause RuntimeError('width adaptation in s-bend not supported')

        if shift_left is None:
            shift_left = 0
        # if(out_width is None):
        #     params = dict(length=length,shift_left=shift_left, 
        #                   width=self.port.width, 
        #                   layer=self.layer)
        #     # width0=self.port.width,
        #     # width1=out_width,
        #     master = self.gen_cls.new_template(params=params, temp_cls=SBendWaveguide)
        #     port_name = 'PORT0'
        #     port_out = 'PORT1'
        # else:
        # print('** width adaptation in s-bend is supported, but requires SBendPathWaveguide...should we deprecate?')
        params = { 'Length':        length, 
                   'Across':        shift_left, 
                   'width':         self.port.width, 
                   'out_width':     out_width, 
                   'LayerPurposePair': self.layer}
        master = self.gen_cls.new_template(params=params, temp_cls=SBendPathWaveguide)
        port_name = 'Port0'
        port_out = 'Port1'
        # print('In add_polygon_s_bend, made a master with Ports:')
        # print(master._photonic_ports)
        inst = self.gen_cls.add_instances_port_to_port(inst_master=master,
                                                       instance_port_name=port_name,
                                                       self_port=self.port,
                                                       reflect=False)
        # Move the current port pointer to the end of the new straight waveguide
        self.port = inst[port_out]
        self.inst = inst
        return self

    def add_component(self,
                      params: dict,
                      temp_cls: BPG.PhotonicTemplateBase,
                      input_port_name: str,
                      output_port_name: str,
                      reflect: bool = False
                      ) -> 'WgRouter':
        """
        Adds an arbitrary user supplied component to the end of the route. The supplied input
        port will be aligned with the current port pointer. Then the port pointer will be updated
        to the supplied output port.

        Parameters
        ----------
        params : dict
            dict of parameters to send to self.new_template to generate the master
        temp_cls : BPG.PhotonicTemplateBase
            generator class that will be used to generate the new master
        input_port_name : str
            name of the port that will be aligned to the current port pointer
        output_port_name : str
            name of the port that will be used as the new port pointer
        reflect : bool
            reflection parameter passed to self.add_instance_port_to_port()

        Returns
        -------
        self : WgRouter
            returns itself so that route segments can be easily chained together
        """
        master = self.gen_cls.new_template(params=params, temp_cls=temp_cls)
        inst = self.gen_cls.add_instance_port_to_port(inst_master=master,
                                                      instance_port_name=input_port_name,
                                                      self_port=self.port,
                                                      reflect=reflect)
        self.port = inst[output_port_name]
        self.inst = inst
        return self

    def add_l_route(self,
                    dx: float,
                    dy: float,
                    bend_params: Dict,
                    omit_final_segment: bool = False
                    ) -> 'WgRouter':
        """
        Generates a straight waveguide and then a 90 degree circular bend so that the end port is re-located
        according to the provided dx, dy. Note that if the provided dx, dy requires a U-turn relative to the current
        routing direction, an error will be raised.

        Parameters
        ----------
        dx : float
            final x offset from the current port location
        dy : float
            final y offset from the current port location
        bend_params : Dict
            Dictionary of bend parameters. See WgRouter.add_90_bend for details.
        omit_final_segment : bool
            If True, the final segment after the bend will not be drawn. This may be useful if you want to use a
            custom component for the final segment

        Returns
        -------
        self : WgRouter
            returns itself so that route segments can be easily chained together
        """
        bend_params = self.process_bend_params(bend_params)
        bend_radius = bend_params['radius']

        # First check that dx/dy can support the desired bend radius
        if abs(dx) <= bend_radius or abs(dy) <= bend_radius:
            raise ValueError(f"Either dx: {dx} or dy: {dy} for this L-route is too small to support bend radius: "
                             f"{bend_radius}")

        if self.port.is_horizontal:
            # If currently pointing horizontally, start with dx
            # TODO: If dx is in the opposite direction from the current port orientation, do not draw a u-turn
            # Perform route direction checking
            if self.port.orientation in self.port_direction_mapping['+x'] and dx < 0:
                raise ValueError(f"Cannot route left while currently pointing to the right: (dx, dy) = ({dx}, {dy})")
            elif self.port.orientation in self.port_direction_mapping['-x'] and dx > 0:
                raise ValueError(f"Cannot route right while currently pointing to the left: (dx, dy) = ({dx}, {dy})")

            self.add_straight_wg(length=abs(dx) - bend_radius)
            # If moving right and up
            if (dx > 0) and (dy > 0):
                self.add_90_bend(bend_params=bend_params, direction='left')
            # If moving right and down
            elif (dx > 0) and (dy < 0):
                self.add_90_bend(bend_params=bend_params, direction='right')
            # If moving left and up
            elif (dx < 0) and (dy > 0):
                self.add_90_bend(bend_params=bend_params, direction='right')
            # If moving left and down
            elif (dx < 0) and (dy < 0):
                self.add_90_bend(bend_params=bend_params, direction='left')

            # Add final straight waveguide
            if omit_final_segment is False:
                self.add_straight_wg(length=abs(dy) - bend_radius)
        elif self.port.is_vertical:
            # If currently pointing vertically, start with dy
            # TODO: If dy is in the opposite direction from the current port orientation, do not draw a u-turn
            # Perform route direction checking
            if self.port.orientation in self.port_direction_mapping['+y'] and dy < 0:
                raise ValueError(f"Cannot route down while currently pointing up: (dx, dy) = ({dx}, {dy})")
            elif self.port.orientation in self.port_direction_mapping['-y'] and dy > 0:
                raise ValueError(f"Cannot route up while currently pointing down: (dx, dy) = ({dx}, {dy})")

            self.add_straight_wg(length=abs(dy) - bend_radius)
            # If moving up and right
            if (dy > 0) and (dx > 0):
                self.add_90_bend(bend_params=bend_params, direction='right')
            # If moving up and left
            elif (dy > 0) and (dx < 0):
                self.add_90_bend(bend_params=bend_params, direction='left')
            # If moving down and right
            elif (dy < 0) and (dx > 0):
                self.add_90_bend(bend_params=bend_params, direction='left')
            # If moving down and left
            elif (dy < 0) and (dx < 0):
                self.add_90_bend(bend_params=bend_params, direction='right')

            # Add final straight waveguide
            if omit_final_segment is False:
                self.add_straight_wg(length=abs(dx) - bend_radius)
        else:
            raise ValueError(f"The current port is in an invalid orientation state: {self.port}")

        return self

    def extract_port(self, port_name: str):
        """ Extract the current port up to the generator class and rename to the provided port name """
        self.gen_cls.extract_photonic_ports(inst=self.inst,
                                            port_names=self.port.name,
                                            port_renaming={self.port.name: port_name})

    ''' Automatic routing methods '''

    def cardinal_router(self,
                        points: List[Tuple],
                        bend_params: Optional[Dict] = None,
                        relative_coords: bool = False,
                        ):
        """
        Routes a waveguide network that contains all provided points. Any required bends use the user provided bend
        radius. Waveguides will only be drawn in the horizontal or vertical directions.

        Notes
        -----
        * This method attempts to generate a manhattanized list of points that contains all of the user
        provided points while minimizing the number of times the direction of the route changes
        * Then a set of cascaded L-routes is created to connect all of the coordinates in the mahattanized point list

        Parameters
        ----------
        points : List[Tuple]
            List of (x, y) points that the route will contain
        bend_params : Dict
            An optional set of bend parameters to specify the bends. See WgRouter.process_bend_params for more details.
            If not specified, the default bend settings are used.
        relative_coords : bool
            True if the list of coordinates are relative to the starting port's coordinate.
            False if the list of coordinates are absolute relative to the current PhotonicTemplate's origin

        Returns
        -------
        self : WgRouter
            returns itself so that route segments can be easily chained together
        """
        bend_params = self.process_bend_params(bend_params)

        # Initialize the starting location and routing direction
        if self.port.is_horizontal:
            current_dir = 'x'
        else:
            current_dir = 'y'

        if relative_coords:
            # If passed coordinates are relative, need to add WgRouter's port location to convert to absolute coords
            x0, y0 = self.port.center
            points = [(x + x0, y + y0) for x, y in points]

        # Generate a manhattanized list of waypoints on the route while minimizing the number of required bends
        manh_point_list = self.manhattanize_point_list(initial_direction=current_dir,
                                                       initial_point=self.port.center,
                                                       points=points)
        # Simplify the point list so that each point corresponds with a bend of the route, i.e. no co-linear points
        final_point_list = self.reduce_point_list(manh_point_list)
        final_point_list = final_point_list[1:]  # Ignore the first pt, since it is co-incident with the starting port

        # Draw a series of L-routes to follow the final simplified point list
        for point0, point1 in zip(final_point_list[:-1], final_point_list[1:]):
            # Starting from the current port, grab the next two points in the list and compute the derivatives
            current_point = self.port.center
            dx0, dy0 = (point0[0] - current_point[0]), (point0[1] - current_point[1])
            dx1, dy1 = (point1[0] - point0[0]), (point1[1] - point0[1])

            # Total dx, dy for an L-route is the sum of the derivatives for the next two manhattan points
            dx, dy = dx0 + dx1, dy0 + dy1

            # Draw the L-route while omitting the final straight waveguide so that another L-route can be appended to
            # it in the next for loop iteration
            self.add_l_route(dx=dx, dy=dy, bend_params=bend_params, omit_final_segment=True)

        # The loop does not draw the final straight waveguide segment, so add it here
        last_point = manh_point_list[-1]
        dx0, dy0 = (last_point[0] - self.port.center[0]), (last_point[1] - self.port.center[1])
        if abs(dx0) <= self.gen_cls.grid.resolution:
            self.add_straight_wg(length=abs(dy0))
        else:
            self.add_straight_wg(length=abs(dx0))

    @staticmethod
    def manhattanize_point_list(initial_direction, initial_point, points):
        """
        Manhattanizes a provided list of (x, y) points while minimizing the number of times the direction changes.
        Manhattanization ensures that every segment of the route only traverses either the x or y direction.

        Notes
        -----
        * Bend minimization is achieved in the following way: If the current direction is x, then the next point in
        the list will have dy = 0. If the current direction is y, then the next point in the list will have dx = 0

        Parameters
        ----------
        initial_direction : str
            The current routing direction which must be maintained in the first segment
        initial_point : Tuple
            (x, y) coordinate location where the route will begin
        points : List[Tuple[float, float]]
            List of coordinates which must also exist in the final manhattanized list

        Returns
        -------
        manh_point_list : List[Tuple[float, float]]
            A manhattanized point list
        """
        current_dir = initial_direction
        current_point = initial_point
        manh_point_list = [tuple(current_point)]
        # Iteratively generate a manhattan point list from the user provided point list
        for next_point in points:
            dx, dy = (next_point[0] - current_point[0]), (next_point[1] - current_point[1])
            # If the upcoming point has a relative offset in both dimensions
            if dx != 0 and dy != 0:
                # Add an intermediate point
                if current_dir == 'x':
                    # First move in x direction then y
                    manh_point_list.append((current_point[0] + dx, current_point[1]))
                    manh_point_list.append((current_point[0] + dx, current_point[1] + dy))
                    current_point = manh_point_list[-1]
                    current_dir = 'y'
                else:
                    # First move in y direction then x
                    manh_point_list.append((current_point[0], current_point[1] + dy))
                    manh_point_list.append((current_point[0] + dx, current_point[1] + dy))
                    current_point = manh_point_list[-1]
                    current_dir = 'x'
            # If the point does not move ignore it to avoid adding co-linear points
            elif dx == 0 and dy == 0:
                continue
            # If the next point only changes in one direction and it is not co-linear
            else:
                manh_point_list.append((current_point[0] + dx, current_point[1] + dy))
                current_point = manh_point_list[-1]
                if dx == 0:
                    current_dir = 'y'
                else:
                    current_dir = 'x'
        return manh_point_list

    @staticmethod
    def reduce_point_list(points: List[coord_type]):
        """
        Returns a new list with all co-linear points removed. This algorithm requires that the point list has already
        been manhattanized so that only dx or dy is 0 for any set of adjacent points. Redundant points must also have
        been removed.

        Notes
        -----
        * Create 3 pointers to locations on the point list: start, middle, end. Place them at the first three points
        in the list
        * Detect whether middle is co-linear with start and end by measuring the derivatives between the three points
        * If the derivatives are such that the points are not co-linear, add the middle point to the reduced point list
        * If the derivatives are such that the points are co-linear, do not add the middle point to the list
        * Increment all 3 pointers

        Parameters
        ----------
        points : List[coord_type]
            Input list of points outlining the route to be drawn

        Returns
        -------
        reduced_point_list : List[coord_type]
            Point list without co-linear or redundant points
        """
        reduced_point_list = list()
        reduced_point_list.append(points[0])  # Always start with the first point in the list

        # Initialize pointers to the first three elements in the list
        tot_length = len(points)
        start_pt = 0
        middle_pt = 1
        end_pt = 2

        while end_pt < tot_length:
            start = points[start_pt]
            middle = points[middle_pt]
            end = points[end_pt]

            # Compute start-middle and middle-end derivatives
            dx0, dy0 = (middle[0] - start[0]), (middle[1] - start[1])
            dx1, dy1 = (end[0] - middle[0]), (end[1] - middle[1])

            # Since the manhattanization routine ensures that either dx or dy is 0, but not both for all pairs of
            # adjacent points, co-linearity between 3 points can determined simply by checking if either dx is non-zero
            # for both pairs or dy is non-zero for both pairs
            if dx0 != 0 and dx1 != 0:
                colinear = True
            elif dy0 != 0 and dy1 != 0:
                colinear = True
            else:
                colinear = False

            # If not co-linear, add the middle point to the list
            if colinear is False:
                reduced_point_list.append(middle)

            # Increment pointers
            start_pt += 1
            middle_pt += 1
            end_pt += 1

        reduced_point_list.append(points[-1])  # Always finish with the last point in the list
        return reduced_point_list
