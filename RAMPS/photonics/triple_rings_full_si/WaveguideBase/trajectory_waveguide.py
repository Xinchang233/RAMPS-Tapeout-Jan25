import gdspy
import numpy as np
import yaml
from scipy.special import fresnel

from BPG.template import PhotonicTemplateBase
from BPG.port import PhotonicPort as BPGPort

EdgeLength_trajectory_wg = 0.015


class TrajectoryWaveguide(PhotonicTemplateBase):
    """
    Subclass of TemplatePhot assuming a trajectory-type path defines the center of the waveguide
    Mandatory parameters: LayerPurposePair, width
    Optional parameters: out_width
    """
    def __init__(self,   temp_db, lib_name,          params,  used_names, **kwargs):
        # type: (         TemplateDB,      str,  Dict[Str, Any],  Set[str], **Any) --> none
        PhotonicTemplateBase.__init__( self, temp_db, lib_name,          params,  used_names, **kwargs)
        self._Width0         = self.params['width']
        if( self.params['out_width'] is not None):
            self._Width1     = self.params['out_width'] 
            if(not(self._Width1)):
                self._Width1 = self._Width0   # Option None for Width1 means default to Width0
        else:
            self._Width1     = self._Width0
        self._Width          = None
        self._Path           = None
        self._PathDerivative = None
        self.LayerPurposePair = self.params['LayerPurposePair']
        if isinstance(self.LayerPurposePair, str):
            # This case should not occur, but lets support it anyway
            self.LPP_Port         = (self.LayerPurposePair,'port')
        else:
            self.LPP_Port         = (self.LayerPurposePair[0],'port')

    def find_port_orientations(self):
        dr0    = self._PathDerivative[0]
        theta0 = np.arctan2(dr0[1], dr0[0])
        orient0, mod_angle0, _, _ =  BPGPort.angle2orient(angle=theta0, mirrored=False)
        dr1    = self._PathDerivative[-1]
        theta1 = np.arctan2(-dr1[1], -dr1[0])
        orient1, mod_angle1, _, _ =  BPGPort.angle2orient(angle=theta1, mirrored=False)

        return (orient0,mod_angle0,orient1,mod_angle1)

    def add_next_phot_port(self, Port = None, discard_name=True):
        """
        Create a photonic port
        Parameters
        ----------
        Port:  port to be copied and added
        """
        if(Port is not None):
            Port_copy = Port.__copy__()
            if(discard_name or (Port_copy.name is None)):
                Port_copy.name = "Port%d" % len(self._photonic_ports)
            self.add_photonic_port(port = Port_copy ) 
            return Port_copy.name
        else:
            raise RuntimeError('add_next_phot_port: input not valid')


    def draw_layout(self):
        self.prim_top_layer = 3
        self._Path, self._PathDerivative  = self.Path()  # Must have a Path() method

        N = len(self._Path)
        Path1_pts = []
        Path2_pts = []
        for IndPoint in range(N):
            x = self._Path[IndPoint][0]
            y = self._Path[IndPoint][1]
            self._Width         = self._Width0 + (self._Width1 - self._Width0) * IndPoint / (N - 1)

            if self._PathDerivative:
                DeltaX = self._PathDerivative[IndPoint][0]  # xxPrime[IndPoint]
                DeltaY = self._PathDerivative[IndPoint][1]  # yyPrime[IndPoint]
            else:  # use finite differences to approximate derivative
                NextPoint = self._Path[min([IndPoint + 1, N - 1])]
                PrevPoint = self._Path[max([0, IndPoint - 1])]
                DeltaX = NextPoint[0] - PrevPoint[0]
                DeltaY = NextPoint[1] - PrevPoint[1]
            Hypotenuse = np.sqrt(DeltaX ** 2 + DeltaY ** 2)

            Path1_pts.append(   (x - DeltaY * self._Width / 2.0 / Hypotenuse, 
                                 y + DeltaX * self._Width / 2.0 / Hypotenuse))
            Path2_pts.insert(0, (x + DeltaY * self._Width / 2.0 / Hypotenuse, 
                                 y - DeltaX * self._Width / 2.0 / Hypotenuse))

        pointsPorts = [(self._Path[0][0], self._Path[0][1]), 
                       (self._Path[-1][0], self._Path[-1][1])]
        # orient0,orient1 = self.find_port_orientations()
        orient0,mod_angle0,orient1,mod_angle1 = self.find_port_orientations()
        # Use the second argument "layer number" of Polygon as an index to LayerPurposePairList
        shape = gdspy.Polygon(Path1_pts + Path2_pts,0) 
        PhotPorts     = [BPGPort( center=pointsPorts[0], orient=orient0, angle = mod_angle0, 
                                  name=None, width=self._Width0, layer=self.LPP_Port, resolution=self.grid.resolution),
                         BPGPort( center=pointsPorts[1], orient=orient1,  angle = mod_angle1, 
                                  name=None, width=self._Width1, layer=self.LPP_Port, resolution=self.grid.resolution)]

        frac_polys = gdspy.PolygonSet([(shape.points / self.grid.resolution) ]).fracture(max_points=3999, precision=1)
        # Add the polygon
        for points in frac_polys.polygons:
            if(len(points) > 0):
                self.add_polygon(points=points.astype(int), layer=self.LayerPurposePair,  
                                 resolution=self.grid.resolution, unit_mode=True)
            else:
                raise RuntimeError('In prepare_and_add_polygons, tried to add a zero-size polygon...interesting...')
        # # # Photonic PORTS
        for Port in PhotPorts:
            self.add_next_phot_port( Port=Port)  
        # self.mark_phot_ports()



class StraightPathWaveguide(TrajectoryWaveguide):
    def __init__(self,   temp_db, lib_name,          params,  used_names, **kwargs):
        # type: (         TemplateDB,      str,  Dict[Str, Any],  Set[str], **Any) --> none
        TrajectoryWaveguide.__init__( self, temp_db, lib_name,          params,  used_names, **kwargs)
    
    @classmethod
    def get_params_info(dummy):
        return {
            'Length':               'length along main axis',
            'width':                'Waveguide width, in microns, at 0 end',
            'out_width':            'Waveguide width, in microns, at 1 end',
            'LayerPurposePair':     'layer-purpose-pair',
        }

    @classmethod
    def get_default_param_values(cls):
        return {
            'out_width':         None, 
        }

    def Path(self):
        # gridres = self.grid.resolution
        # NSteps  = self.params['Length'] / gridres
        NSteps  = 2                              # NSteps can be as small as 1...there is no reason to make it large
        lnorm   = np.arange(NSteps + 1) / NSteps
        xx      = lnorm * self.params['Length']
        yy      =                         0.0 * lnorm  
        dxdln   = self.params['Length'] + 0.0 * lnorm 
        dydln   =                         0.0 * lnorm
        return ([ (xx[ind], yy[ind]) for ind in range(len(xx))], 
                [ (dxdln[ind], dydln[ind]) for ind in range(len(xx))])


class FilePathWaveguide(TrajectoryWaveguide):
    def __init__(self,   temp_db, lib_name,          params,  used_names, **kwargs):
        # type: (         TemplateDB,      str,  Dict[Str, Any],  Set[str], **Any) --> none
        TrajectoryWaveguide.__init__( self, temp_db, lib_name,          params,  used_names, **kwargs)
    
    @classmethod
    def get_params_info(dummy):
        return {
            # 'Length':               'length along main axis',
            'width':                'Waveguide width, in microns, at 0 end',
            'out_width':            'Waveguide width, in microns, at 1 end',
            'LayerPurposePair':     'layer-purpose-pair',
            'filename':             'filename of yaml with path coordinates',
        }

    @classmethod
    def get_default_param_values(cls):
        return {
        }

    def Path(self):
        with open(self.params['filename']) as ff:
            str        = ff.read()
            wgtraj = yaml.safe_load(str)
        xx   = wgtraj['x']
        yy   = wgtraj['y']
        xdot = wgtraj['xdot']
        ydot = wgtraj['ydot']
        return ([ (xx[ind],   yy[  ind]) for ind in range(len(xx))], 
                [ (xdot[ind], ydot[ind]) for ind in range(len(xx))])


class SBendPathWaveguide(TrajectoryWaveguide):
    '''
    Polgon path connecting parallel waveguides with zero curvature at the ends
    '''
    def __init__(self,   temp_db, lib_name,          params,  used_names, **kwargs):
        # type: (         TemplateDB,      str,  Dict[Str, Any],  Set[str], **Any) --> none
        TrajectoryWaveguide.__init__( self, temp_db, lib_name,          params,  used_names, **kwargs)
        # print('In SBendPathWaveguide, got self._Width0=%.3f', self._Width0)

    @classmethod
    def get_params_info(dummy):
        return {
            'Length':               'length along main axis',
            'Across':               'distance across',
            'width':                'Waveguide width, in microns, at 0 end',
            'out_width':            'Waveguide width, in microns, at 1 end',
            'LayerPurposePair':     'layer-purpose-pair',
        }

    @classmethod
    def get_default_param_values(cls):
        return {
            'out_width':         None, 
        }

    def Path(self):
        # print('In SBendPathWaveguide, Length %.2f, Across %.2f' % (self.params['Length'], self.params['Across']))

        # What should NSteps be?  Surely Across/gridres would be a more reasonable choice than Length/gridres
        # NSteps  = self.params['Length'] / gridres
        # NSteps  = self.params['Across'] / gridres
        EdgeLength = EdgeLength_trajectory_wg
        NSteps  = int(np.ceil(self.params['Length'] / EdgeLength))

        lnorm   = np.arange(NSteps + 1) / NSteps
        # 
        xx      = lnorm * self.params['Length']
        # print('xx has shape:')
        # print(xx.shape)
        ux      = 2 * xx / self.params['Length'] - 1   # x normalized to vary from -1 to 1 
        uy      = (15. / 8.) * ux  + (-10 / 8.)  * np.power(ux,3)  + (3.0 / 8.0) * np.power(ux,5)
        # print('uy has shape:')
        # print(uy.shape)
        # +-uy at ux = +-1 -->  (15 -10+3) / 8 = 1 ==> (xx,yy) matches end points
        yy      = (uy + 1.) * self.params['Across'] / 2
        dxdux   = self.params['Length'] / 2 + 0.0 * lnorm
        duydux  = (15. / 8.)  + (-30 / 8.)  * np.power(ux,2)  + (15.0 / 8.0) * np.power(ux,4)
        # duydux at ux=+-1 --> (15-30+15)/8 = 0 ==> (xx,yy) has zero slope in local frame
        # d2uydux2  = (-60 / 8.)  * np.power(ux,1)  + (60.0 / 8.0) * np.power(ux,4) ==> zero curvature at ends
        
        dydux   = duydux * self.params['Across'] / 2
        return ([ (xx[ind], yy[ind]) for ind in range(len(xx))], 
                [ (dxdux[ind], dydux[ind]) for ind in range(len(xx))])



class CosineWaveguide(TrajectoryWaveguide):
    def __init__(self,   temp_db, lib_name,          params,  used_names, **kwargs):
        # type: (         TemplateDB,      str,  Dict[Str, Any],  Set[str], **Any) --> none
        TrajectoryWaveguide.__init__( self, temp_db, lib_name,          params,  used_names, **kwargs)
    
    @classmethod
    def get_params_info(dummy):
        return {
            'Length':               'length along main axis',
            'width':                'Waveguide width, in microns, at 0 end',
            'out_width':            'Waveguide width, in microns, at 1 end',
            'LayerPurposePair':     'layer-purpose-pair',
            'CosineAmplitude':      'width along transverse axis for half-sinusoid',
            'Phi0':                 'phase of sinusoid at end 0',
            'Phi1':                 'phase of sinusoid at end 1',
        }

    @classmethod
    def get_default_param_values(cls):
        return {
            'Phi0':                 0.0,
            'Phi1':                 np.pi,
            'out_width':         None, 
        }

    def Path(self):
        Amp = self.params['CosineAmplitude']
        EdgeLength = EdgeLength_trajectory_wg
        NSteps  = int(np.ceil(self.params['Length'] / EdgeLength))
        lnorm   = np.arange(NSteps + 1) / NSteps
        Phi0    = self.params['Phi0']
        Phi1    = self.params['Phi1']
        Phi     = Phi0 + (Phi1 - Phi0 ) * lnorm
        xx      = lnorm * self.params['Length']
        yy      = Amp * np.cos( Phi )
        dxdln = self.params['Length'] + 0.0 * lnorm 
        dydln = ( -Amp * (Phi1 - Phi0 ) * np.sin( Phi))
        return ([ (xx[ind], yy[ind]) for ind in range(len(xx))], 
                [ (dxdln[ind], dydln[ind]) for ind in range(len(xx))])



class CircularPathWaveguide(TrajectoryWaveguide):
    def __init__(self,   temp_db, lib_name,          params,  used_names, **kwargs):
        # type: (         TemplateDB,      str,  Dict[Str, Any],  Set[str], **Any) --> none
        TrajectoryWaveguide.__init__( self, temp_db, lib_name,          params,  used_names, **kwargs)
        
    @classmethod
    def get_params_info(dummy):
        return {
            'AngularExtent':        'angle of end 1 minus angle of end 0',
            'RCenter':              'Radius at center of trajectory', 
            'width':                'Waveguide width, in microns, at 0 end',
            'out_width':            'Waveguide width, in microns, at 1 end',
            'LayerPurposePair':     'layer-purpose-pair',
        }

    @classmethod
    def get_default_param_values(cls):
        return {
            'AngularExtent':      np.pi / 2, 
            'RCenter':               48.0,
            'out_width':         None, 
        }

    def Path(self):
        EdgeLength = EdgeLength_trajectory_wg
        PathRadius = self.params['RCenter']
        AngularExtent = self.params['AngularExtent']
        NumAngleSteps = np.ceil(np.abs(AngularExtent * PathRadius / EdgeLength))
        index_vec = np.arange(NumAngleSteps + 1)
        angle_vec = AngularExtent * index_vec / NumAngleSteps 
        xx        =  PathRadius * np.cos( angle_vec)
        yy        =  PathRadius * np.sin( angle_vec)
        dxdangle  = -PathRadius * np.sin( angle_vec) * np.sign(AngularExtent)
        dydangle  =  PathRadius * np.cos( angle_vec) * np.sign(AngularExtent)
        return ([ (xx[ind], yy[ind]) for ind in range(len(xx))], 
                [ (dxdangle[ind], dydangle[ind]) for ind in range(len(xx))])



class euler_circle_turn(TrajectoryWaveguide):
    def __init__(self,   temp_db, lib_name,          params,  used_names, **kwargs):
        # type: (         TemplateDB,      str,  Dict[Str, Any],  Set[str], **Any) --> none
        TrajectoryWaveguide.__init__( self, temp_db, lib_name,          params,  used_names, **kwargs)
        # Euler from theta=0 to theta=thetaEuler1, then circle, then Euler again

    @classmethod
    def get_params_info(dummy):
        return {
            'turn_angle_deg':         'Total angle turned, in degrees', 
            'AngleTurnEuler':         'Angle turned in each euler', 
            'RadiusOfCurvatureMin':   'Radius of curvature in circle, microns', 
            'width':                'Waveguide width, in microns, at 0 end',
            'out_width':            'Waveguide width, in microns, at 1 end',
            'LayerPurposePair':     'layer-purpose-pair',
        }

    @classmethod
    def get_default_param_values(cls):
        return {
            'out_width':         None, 
        }

    def unpack_params(self):
        self.tEuler0        = 0
        self.thetaEuler0    = 0
        self.RoCMin         = self.params['RadiusOfCurvatureMin']
        self.kappa1         = 1 / self.params['RadiusOfCurvatureMin']
        # self.thetaEuler1    = np.pi/2  # self.params['AngleTurnEuler']
        self.thetaEuler1    = self.params['AngleTurnEuler']
        self.turn_angle_deg = self.params['turn_angle_deg']

        self.tEuler1 = np.sqrt(2 * self.thetaEuler1)
        self.aEuler  = self.tEuler1 / self.kappa1
        # print('>>>>>>>>>In euler_circle_turn, got curvature %.2f, RoCMin %.2f, aEuler %.2f' % 
        #       (self.kappa1, self.RoCMin, self.aEuler))

        if np.isclose(self.turn_angle_deg, 90):
            self.is90deg =  True
            self.is180deg = False
        elif np.isclose(self.turn_angle_deg, 180):
            self.is90deg =  False
            self.is180deg = True
        else:
            raise ValueError(f'Only 90 or 180 degree Euler-Circle-Euler bends are currently supported')            

        AngleTurnCircle = self.turn_angle_deg * np.pi / 180 - 2 * ( self.thetaEuler1 - self.thetaEuler0 )
        self.thetaCircle2 = -np.pi / 2 + self.thetaEuler1
        self.thetaCircle3 = self.thetaCircle2 + AngleTurnCircle
        # print(self.params)

    def EulerPath(self):
        # This is my matlab version, which correctly produced curvature ramp
        # thisWg.qq     = @(tj) thisWg.q0 + (thisWg.q1 - thisWg.q0) * tj;
        # dqdt          = thisWg.q1 - thisWg.q0;
        # thisWg.xfun   = thisWg.a0 .* sqrt(pi) * fresnelC(thisWg.qq(tj)/sqrt(pi))
        # thisWg.yfun   = thisWg.a0 .* sqrt(pi) * fresnelS(thisWg.qq(tj)/sqrt(pi))
        # thisWg.xdot   = @(tj)                ( thisWg.a0 .* cos(thisWg.qq(tj).^2 / 2) ) * dqdt ; 
        # thisWg.ydot   = @(tj)  thisWg.flip * ( thisWg.a0 .* sin(thisWg.qq(tj).^2 / 2) ) * dqdt ; 
        # thisWg.xddot  = @(tj)                (-thisWg.a0 .* thisWg.qq(tj) .* sin(thisWg.qq(tj).^2 / 2) ) * dqdt^2 ; 
        # thisWg.yddot  = @(tj)  thisWg.flip * ( thisWg.a0 .* thisWg.qq(tj) .* cos(thisWg.qq(tj).^2 / 2) ) * dqdt^2 ; 

        # # # UNPACK from params
        EdgeLength = EdgeLength_trajectory_wg

        PathLength =  np.abs(self.aEuler * (  self.tEuler1 -  self.tEuler0 ))
        NSteps     = int(np.ceil(PathLength / EdgeLength))
        lnorm      = np.arange(NSteps + 1) / NSteps
        tEuler     = self.tEuler0 + (  self.tEuler1 -  self.tEuler0 ) * lnorm 

        fresS,fresC  = fresnel(tEuler / np.sqrt(np.pi))
        xx   = self.aEuler * np.sqrt(np.pi) * fresC
        yy   = self.aEuler * np.sqrt(np.pi) * fresS
        xdot = self.aEuler * np.cos(np.power(tEuler,2) / 2) 
        ydot = self.aEuler * np.sin(np.power(tEuler,2) / 2) 

        return ([ (xx[ind], yy[ind]) for ind in range(len(xx))], 
                [ (xdot[ind], ydot[ind]) for ind in range(len(xx))])

    def CirclePath(self, x0y0=(0,0)):
        EdgeLength = EdgeLength_trajectory_wg
        PathLength = (self.thetaCircle3 - self.thetaCircle2 ) * self.RoCMin
        NSteps     = int(np.ceil(PathLength / EdgeLength))
        lnorm      = np.arange(NSteps + 1) / NSteps
        theta      =  self.thetaCircle2 + (  self.thetaCircle3 - self.thetaCircle2 ) * lnorm 

        xx   = self.RoCMin * np.cos(theta) 
        yy   = self.RoCMin * np.sin(theta) 
        xdot = -self.RoCMin * np.sin(theta)
        ydot = self.RoCMin * np.cos(theta)

        return ([ (xx[ind] + x0y0[0] - xx[0], yy[ind] + x0y0[1] - yy[0]) for ind in range(len(xx))], 
                [ (xdot[ind], ydot[ind]) for ind in range(len(xx))])

    def Path(self):
        # print('In euler trajectory, LPP is ' + str(self.LayerPurposePair))
        self.unpack_params()
        xyEul, xydotEul = self.EulerPath()
        xyCir, xydotCir = self.CirclePath(xyEul[-1])

        if(self.is180deg):
            # Another copy of the Euler is flipped y->-y, and indexed backwards
            dx = xyCir[-1][0] - xyEul[-1][0]
            dy = xyCir[-1][1] + xyEul[-1][1]
            xyEul_copy    = [ (coord[0] + dx,-coord[1] + dy) for coord in xyEul[::-1]]
            xydotEul_copy = [ (-xydot[0],xydot[1]) for xydot in xydotEul[::-1]]
        elif(self.is90deg):
            # Another copy of the Euler is flipped x <-> y, and indexed backwards
            dx = xyCir[-1][0] - xyEul[-1][1]
            dy = xyCir[-1][1] - xyEul[-1][0]
            xyEul_copy    = [ (coord[1] + dx,coord[0] + dy) for coord in xyEul[::-1]]
            xydotEul_copy = [ (-xydot[1],-xydot[0]) for xydot in xydotEul[::-1]]
            
        return( [it for section in [xyEul,xyCir,xyEul_copy] for it in section] , 
                [it for section in [xydotEul,xydotCir,xydotEul_copy] for it in section])
