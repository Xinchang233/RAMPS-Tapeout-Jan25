import BPG
from ...triple_rings_full_si.AdiabaticPaths.AdiabaticPaths import AdiabaticPaths
from ...triple_rings_full_si.BasicElements.ParabolicPolygon.ParabolicPolygon import ParabolicPolygon
from copy import deepcopy


class AdiabaticRouter:
    """This class implements a waveguide router made out of AdiabaticPaths class instances
        Currently supported bend are straight, 90 degree, 180 degree, offset bend wrapped ring coupler bend, parabolic
        polygon and arbitrary bend.
        This class is not an ordinary BPG.PhotonicTemplateBase, so it cannot be used on its own to build layout.
        However, when instantiated within another class, self of that class is passes as input parameter gen_cls.
        This will enable adding instances to layout.
        Override_width argument is added so that non-continues waveguide shapes can be created - non-default behavior

        Example
    --------
    ExampleCls(BPG.PhotonicTemplateBase):
        def draw_layout(self):
            self.add_photonic_port(name='init_port', center=(0, 0), orient='R0', width=1.0, layer='SI')

            Wg = AdiabaticRouter(gen_cls=self, nit_port=self.get_photonic_port('init_port'),
                              layer=('SI', 'drawing'), name='route1')

            Wg.add_straight_wg(length=5)
            Wg.add_bend_90(size=10)
            Wg.add_straight_wg(length=30)
            Wg.add_bend_180(rmin=5, turn_left=False, width=3)
            Wg.add_straight_wg(length=10, width=1)
            Wg.add_offset_bend(offset=10, rmin=2)
    """
    port_layer = ('RX', 'port')
    def __init__(self, gen_cls, init_port, layer, **kwargs):
        """Arguments supplied to __init__ are  BPG.PhotonicTemplateBase, layer where bends will be instantiated and
        staring/initial port from which routing will start. Attributes that are created and associated with self are:
            * inst -> dictionary where key is # of instance in the router - 1 and value is the AdiabaticPath instance
         """

        self.gen_cls: BPG.PhotonicTemplateBase = gen_cls
        self.layer = layer
        self.init_port = init_port

        self.inst = dict()
        self.bend_params = dict(layer=self.layer, port_layer=self.port_layer,
                                radius_threshold=1, curvature_rate_threshold=0.9, merge_arcs=False)
        self.port = self.init_port

    def add_straight_wg(self, length: float, width=None, override_width=False):

        if not override_width:
            if width is None or width == self.port.width:
                width = self.port.width
            else:
                width = [self.port.width, width]
        else:
            width = width

        bend_params = deepcopy(self.bend_params)
        bend_params['arc_params'] = [dict(arc_type='straight_wg', length=length, width=width)]
        temp = self.gen_cls.new_template(params=bend_params, temp_cls=AdiabaticPaths)
        index = len(self.inst)
        self.inst[index] = self.gen_cls.add_instance_port_to_port(inst_master=temp, instance_port_name='PORT_IN',
                                                                  self_port=self.port)
        self.port = self.inst[index]['PORT_OUT']

    def add_bend_90(self, rmin: float = 0,
                    size: float = 0,
                    turn_left: bool = True,
                    width=None):
        bend_params = deepcopy(self.bend_params)
        if width is None or width == self.port.width:
            width = self.port.width
        else:
            width = [self.port.width] + self._listize(width)

        if size <= 0 and rmin <= 0:
            raise ValueError("size or rmin parameter needs to be larger than 0")
        if size > 0:
            bend_params['arc_params'] = [
                dict(arc_type='90_bend', turn_left=turn_left, width=width, size=size)]
        else:
            bend_params['arc_params'] = [
                dict(arc_type='90_bend', turn_left=turn_left, width=width, rmin=rmin)]

        temp = self.gen_cls.new_template(params=bend_params, temp_cls=AdiabaticPaths)
        index = len(self.inst)
        self.inst[index] = self.gen_cls.add_instance_port_to_port(inst_master=temp, instance_port_name='PORT_IN',
                                                                  self_port=self.port)

        self.port = self.inst[index]['PORT_OUT']

    def add_bend_180(self, rmin: float = 0,
                     size: float = 0,
                     turn_left: bool = True,
                     width=None):
        bend_params = deepcopy(self.bend_params)
        if width == None or width == self.port.width:
            width = self.port.width
        else:
            width = [self.port.width, width]

        if size <= 0 and rmin <= 0:
            raise ValueError("size or rmin parameter needs to be larger than 0")
        if size > 0:
            bend_params['arc_params'] = [
                dict(arc_type='180_bend', turn_left=turn_left, width=width, size=size)]
        else:
            bend_params['arc_params'] = [
                dict(arc_type='180_bend', turn_left=turn_left, width=width, rmin=rmin)]

        temp = self.gen_cls.new_template(params=bend_params, temp_cls=AdiabaticPaths)
        index = len(self.inst)
        self.inst[index] = self.gen_cls.add_instance_port_to_port(inst_master=temp, instance_port_name='PORT_IN',
                                                                  self_port=self.port)
        self.port = self.inst[index]['PORT_OUT']

    def add_offset_bend(self, offset: float, rmin: float, width=None):
        bend_params = deepcopy(self.bend_params)
        if width == None or width == self.port.width:
            width = self.port.width
        else:
            width = [self.port.width, width]

        bend_params['arc_params'] = [dict(arc_type='offset_bend', rmin=rmin, width=width, offset=offset)]

        temp = self.gen_cls.new_template(params=bend_params, temp_cls=AdiabaticPaths)
        index = len(self.inst)
        self.inst[index] = self.gen_cls.add_instance_port_to_port(inst_master=temp, instance_port_name='PORT_IN',
                                                                  self_port=self.port)
        self.port = self.inst[index]['PORT_OUT']

    def add_wrapped_ring_coupler(self, rmin_in: float, alpha_zero_in: float, r_coupling: float,
                                 angle_coupling: float, w_coupling: float, width: float = None, ):
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
        bend_params = deepcopy(self.bend_params)
        if width == None or width == self.port.width:
            width = self.port.width
        else:
            width = [self.port.width, width]

        bend_params['arc_params'] = [
            dict(arc_type='wrapped_ring_coupler', w_in=width, rmin_in=rmin_in, alpha_zero_in=alpha_zero_in,
                 r_coupling=r_coupling, angle_coupling=angle_coupling, w_coupling=w_coupling)]

        temp = self.gen_cls.new_template(params=bend_params, temp_cls=AdiabaticPaths)
        index = len(self.inst)
        self.inst[index] = self.gen_cls.add_instance_port_to_port(inst_master=temp, instance_port_name='PORT_IN',
                                                                  self_port=self.port)
        self.port = self.inst[index]['PORT_OUT']

    def add_wrapped_ring_coupler_centport(self, rmin_in: float, alpha_zero_in: float, r_coupling: float,
                                 angle_coupling: float, w_coupling: float, width: float = None, ):
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
        bend_params = deepcopy(self.bend_params)
        bend_params2 = deepcopy(self.bend_params)
        if width == None or width == self.port.width:
            width = self.port.width
        else:
            width = [self.port.width, width]

        bend_params['arc_params'] = [
            dict(arc_type='wrapped_ring_coupler1', w_in=width, rmin_in=rmin_in, alpha_zero_in=alpha_zero_in,
                 r_coupling=r_coupling, angle_coupling=angle_coupling, w_coupling=w_coupling)]

        temp = self.gen_cls.new_template(params=bend_params, temp_cls=AdiabaticPaths)
        index = len(self.inst)
        self.inst[index] = self.gen_cls.add_instance_port_to_port(inst_master=temp, instance_port_name='PORT_IN',
                                                                  self_port=self.port)
        self.port = self.inst[index]['PORT_OUT']

        # self.extract_photonic_ports(
        #     inst=self.inst[index],
        #     port_names = 'PORT_OUT',
        #     port_renaming = 'PORT_CENTER'
        # )

        bend_params2['arc_params'] = [
            dict(arc_type='wrapped_ring_coupler1', w_in=width, rmin_in=rmin_in, alpha_zero_in=alpha_zero_in,
                 r_coupling=r_coupling, angle_coupling=angle_coupling, w_coupling=w_coupling)]

        temp2 = self.gen_cls.new_template(params=bend_params2, temp_cls=AdiabaticPaths)
        index = len(self.inst)
        self.inst[index] = self.gen_cls.add_instance_port_to_port(inst_master=temp2, instance_port_name='PORT_OUT',
                                                                  self_port=self.port, reflect=True)

        self.port = self.inst[index]['PORT_IN']

    def add_parabolic_polygon(self, wout: float, length: float, win: float = None, ):

        if win is None or win == self.port.width:
            win = self.port.width

        params = {'win': win, 'wout': wout, 'length': length, 'layer': self.layer}
        temp = self.gen_cls.new_template(params=params, temp_cls=ParabolicPolygon)
        index = len(self.inst)
        self.inst[index] = self.gen_cls.add_instance_port_to_port(inst_master=temp, instance_port_name='PORT_IN',
                                                                  self_port=self.port)
        self.port = self.inst[index]['PORT_OUT']


    def add_arb_bend(self, angle: list, curvature: list, width: float = None, override_width=False):

        bend_params = deepcopy(self.bend_params)
        if not override_width:
            if width is None or width == self.port.width:
                width = self.port.width
            else:
                width = [self.port.width] + self._listize(width)
        else:
            width = width  # Redundant statement

        bend_params['arc_params'] = [dict(arc_type='arbitrary_arc', curvature=curvature, width=width, angle=angle)]

        temp = self.gen_cls.new_template(params=bend_params, temp_cls=AdiabaticPaths)
        index = len(self.inst)
        self.inst[index] = self.gen_cls.add_instance_port_to_port(inst_master=temp, instance_port_name='PORT_IN',
                                                                  self_port=self.port)
        self.port = self.inst[index]['PORT_OUT']

    def rotate(self, loc, angle):
        for i in range(len(self.inst)):
            self.inst[i].rotate(loc=loc, angle = angle) #To be removed after testing

    def translate(self, dx, dy):
        for i in range(len(self.inst)):
            self.inst[i].move_by(dx =dx, dy=dy) #To be removed after testing

    @staticmethod
    def _listize(x):
        """
        if x is a scalar, converts it into a one-element list
        conventient for handling cases when input parameters can be a scalar or a list
        such as width parameter.
        """
        if isinstance(x, list):
            return x
        else:
            return [x]
