import BPG
from BPG.objects import PhotonicPath
from Photonic_Core_Layout.FixedPhotonicPath.FixedPhotonicPath import FixedPhotonicPath
import numpy as np
from copy import deepcopy


class RibbonPathWaveguide(BPG.PhotonicTemplateBase):
    """
    Class which generates an array of waveguides in a "ribbon" format with centerline coordinates given in the points input.


    Parameters
    ----------
    add_ports: boolean
        If true adds photonic ports at inputs and outputs
    widths: float or list of floats
        Value(s) of waveguide widths
    layer: str or [str, str]
        Process layer or PP layer to write waveguides on
    seps: float or list of floats
        Value(s) of center-to-center waveguide separations
    n_wgs: integer
        Number of waveguides in ribbon
    points: list of tuples in the form (x,y)
        Centerline path for the waveguide ribbon
        NOTE: centerline is defined not by the middle waveguide but the center of the total "width" of the ribbon,
        the outer edges of the outer two waveguides
    angle_in: float (Degrees)
        (OPTIONAL) Force input angle to specified value; otherwise rounds to nearest 45 degree angle
    angle_out: float (Degrees)
        (OPTIONAL) Force output angle to specified value; otherwise rounds to nearest 45 degree angle
    """



    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)

        # Initialize the variables and dictionary of parameters.
        self.add_ports = self.params['add_ports']
        self.n_wgs = self.params['n_wgs']
        if isinstance(self.params['widths'],(int,float)):
            width = self.params['widths']
            self.widths = []
            for ii in range(self.n_wgs):
                self.widths.append(width)
        else:
            self.widths = self.params['widths']

        if isinstance(self.params['seps'],(int,float)):
            sep = self.params['seps']
            self.seps = []
            for ii in range(self.n_wgs - 1):
                self.seps.append(sep)
        else:
            self.seps = self.params['seps']

        if 'block_layer' in self.params:
            self.block_layer = self.params['block_layer']
        else:
            self.block_layer = None

        if self.block_layer is not None:
            self.block_margin = self.params['block_margin']
            self.block_points = None
            self.block_path = None

        self.layer = self.params['layer']
        self.points = self.params['points']

        # Parameter checking: Make sure parameters are valid type and values
        #TODO: Fix this stuff, was throwing incorrect errors
        '''
        if any(val <= 0 for val in [self.widths]):
            raise ValueError("All waveguide widths must be >0")
        if any(val <= 0 for val in [self.seps]):
            raise ValueError("All waveguide separations must be >0")
        if any(not isinstance(val, (int, float)) for val in [self.widths]):
            raise ValueError('Waveguide widths must be int or float')
        if any(not isinstance(val, (int, float)) for val in [self.seps]):
            raise ValueError('Waveguide separations must be int or float')
        if any(not isinstance(val, (str, tuple)) for val in [self.layer]):
            raise ValueError('Layer must be str or tuple')
        #if any(not len(val) == 2 for val in [self.points]):
        #    raise ValueError('Points must be a list of tuples with length == 2')
        if len(self.points) < 2:
            raise ValueError('Points must be a list with length >=2')
        if not isinstance(self.widths,(int,float)) and not len(self.widths) == self.n_wgs:
            raise ValueError('"widths" must be list of length n_wgs or a float/int')
        if not isinstance(self.seps,(int,float)) and not (len(self.seps) + 1) == self.n_wgs:
            raise ValueError('"seps" must be list of length n_wgs-1 or a float/int')
        '''

        #Calculate angles
        angles_dict = self.calc_angles(self.points)
        self.angles = angles_dict['angles']
        self.dangles = angles_dict['dangles']
        #Import angle_in/angle_out
        if 'angle_in' in self.params and self.params['angle_in'] is not None:
            self.angle_in = self.params['angle_in']*np.pi/180
        else:
            #Round to nearest 45 degree angle
            self.angle_in = int(np.round(self.angles[0]*4/np.pi))*np.pi/4
        if 'angle_out' in self.params and self.params['angle_out'] is not None:
            self.angle_out = self.params['angle_out']*np.pi/180
        else:
            #Round to nearest 45 degree angle
            self.angle_out = int(np.round(self.angles[-1]*4/np.pi))*np.pi/4

        self.angles[0] = self.angle_in
        self.angles[-1] = self.angle_out

        self.paths = {ii: None for ii in range(self.n_wgs)}
        self.path_points = [[(0.0,0.0) for ii in range(len(self.points))] for jj in range(self.n_wgs)]

    @classmethod
    def get_params_info(cls) -> dict:
        return dict(
            add_ports = 'Boolean to turn on photonic ports at inputs and outputs',
            widths = 'Value(s) of waveguide widths',
            layer = 'Process layer or PP layer to write waveguides to',
            block_layer = 'Process layer or PP layer to write block fill to',
            block_margin = 'Extra margin around waveguides in which to write block fill',
            seps = 'Value(s) of center-to-center waveguide separations',
            n_wgs = 'Number of waveguides in ribbon',
            points = 'Centerline path for the waveguide ribbon',
            angle_in='(OPTIONAL) Force input angle to specified value in degrees; otherwise rounds to nearest 45 degree angle',
            angle_out = '(OPTIONAL) Force output angle to specified value in degrees;; otherwise rounds to nearest 45 degree angle',
        )

    @classmethod
    def get_default_param_values(cls) -> dict:
        return dict(
            add_ports = True,
            widths = (0.45,0.45,0.45),
            layer = ['SI','drawing'],
            block_layer=None,
            block_margin=5.0,
            seps = (5.0,2.0),
            n_wgs = 3,
            points = ((0.0,0.0),(10.0,0.0)),
            angle_in = 0,
            angle_out = 0,
        )

    @staticmethod
    def calc_angles(points):
        #Calculate angles of each straight line segment
        line_angles = []
        angles = []
        dangles = []
        for ii in range(len(points)-1):
            dy = points[ii+1][1]-points[ii][1]
            dx = points[ii+1][0]-points[ii][0]
            line_angles.append(np.arctan2(dy, dx))
        #Append initial and final values
        line_angles.insert(0, line_angles[0])
        line_angles.append(line_angles[-1])
        #Average angles to find "effective" angles at points
        for ii in range(len(points)):
            angles.append((line_angles[ii]+line_angles[ii+1])/2)
            dangles.append(line_angles[ii+1]-line_angles[ii])

        output = {'angles':angles,
                  'dangles':dangles}

        return output

    def draw_layout(self) -> None:
        self.calc_paths()
        self.create_paths()
        if self.add_ports:
            self.create_ports()
        for ii in range(self.n_wgs):
            self.add_obj(self.paths[ii])
        if self.block_layer is not None:
            self.create_block_path()
            self.add_obj(self.block_path)

    def calc_paths(self) -> None:
        #center = 0.0
        ribbon_width = sum(np.array(self.seps))
        left_edge = -ribbon_width/2
        loc = left_edge
        for ii in range(self.n_wgs):
            pitch = loc
            for jj in range(len(self.points)):
                scale = 1/np.sin((np.pi-self.dangles[jj])/2)
                xshift = np.sin(self.angles[jj])*pitch*scale
                yshift = -np.cos(self.angles[jj])*pitch*scale
                self.path_points[ii][jj] = (self.points[jj][0]+xshift,self.points[jj][1]+yshift)
            if ii<(self.n_wgs-1):
                loc += self.seps[ii]

    def create_block_path(self) -> None:
        block_width = sum(np.array(self.seps))+(self.widths[0]+self.widths[-1])/2+2*self.block_margin
        self.block_points = deepcopy(self.points)
        self.block_points[0] = (self.block_points[0][0]-self.block_margin*np.cos(self.angles[0]),
                                self.block_points[0][1]-self.block_margin*np.sin(self.angles[0]))
        self.block_points[-1] = (self.block_points[-1][0] + self.block_margin * np.cos(self.angles[-1]),
                                self.block_points[-1][1] + self.block_margin * np.sin(self.angles[-1]))
        self.block_path = FixedPhotonicPath(
            resolution=self.grid.resolution,
            layer=self.block_layer,
            width=block_width,
            points=self.block_points,
            unit_mode=False,
        )



    def create_paths(self) -> None:
        """
        Takes the list of points and generates a PhotonicPath shape
        """
        #TODO: return to PhotonicPath once base script fixed
        for ii in range(self.n_wgs):
            self.paths[ii] = FixedPhotonicPath(
                resolution=self.grid.resolution,
                layer=self.layer,
                width=self.widths[ii],
                points=self.path_points[ii],
                unit_mode=False,
        )

    def create_ports(self) -> None:
        """
        Place ports at the input and output each waveguide
        """
        orient = {
            0: "R0",
            1: "R90",
            2: "R180",
            3: "R270",
            4: "R0",
            5: "R90",
        }
        #Get angles to nearest 90
        angle_in_90 = int(np.floor(self.angle_in/(np.pi/2)))
        angle_out_90 = int(np.floor(self.angle_out / (np.pi / 2)))
        for ii in range(self.n_wgs):
            #Input port
            self.add_photonic_port(
                name='PORT0,'+str(ii),
                center=self.path_points[ii][0],
                orient=orient[angle_in_90],
                angle=self.angle_in-np.pi/2*angle_in_90,
                width=self.widths[ii],
                layer=self.layer,
                overwrite_purpose=False,
                resolution=self.grid.resolution,
                unit_mode=False,
                show=True,
            )
            # Output port
            self.add_photonic_port(
                name='PORT1,'+str(ii),
                center=self.path_points[ii][-1],
                orient=orient[angle_out_90+2],
                angle=self.angle_out - np.pi / 2 * angle_out_90,
                width=self.widths[ii],
                layer=self.layer,
                overwrite_purpose=False,
                resolution=self.grid.resolution,
                unit_mode=False,
                show=True,
            )

if __name__ == '__main__':
    spec_file = 'Photonic_Core_Layout/WaveguideBase/specs/ribbonwg.yaml'
    plm = BPG.PhotonicLayoutManager(spec_file)
    plm.generate_content()
    plm.generate_gds()
    plm.generate_flat_content()
    plm.generate_flat_gds()
