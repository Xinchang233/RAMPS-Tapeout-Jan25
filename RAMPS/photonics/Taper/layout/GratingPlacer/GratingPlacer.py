import BPG
from copy import deepcopy
import importlib
from BPG.gds.io import GDSImport
import numpy as np

""" This class is used to place grating(s) at locations provided by <cords_file>
    <cords_file> is exported from Klayout and example line looks like this:
    "polygon (35,15.002;34.999,15.003;35,15.004)",9063/0,Modulators_cell,,"
    This code will parse the <cords_file> and obtain coordinates of grating place holder.
    Based on the obtained coordinates, code will determine where grating is to be placed 
    and orientation of the grating.
    Code offers two ways to save gratings. They can be written directly to the user provided gds file (<gds_path>),
    if <gds_path> is a string. Otherwise, code will place gratings in stand-alone file. 
    Writing directly to <gds_path> file  is not reccommended, because this operation is not 
    reversible and is prone to error, e.g. <gds_path> file needs to be flattened to generate proper <cords_file>
    and if this is not done the <cords_file> will hold coordinates of polygon relative to the origin of the cell
    and not relative to the origin of the overall layout. 
    
    NOTE: Current code only supports isosceles triangle as a place holder. 
    NOTE: Supported orientations are only in cardinal directions.
    """


class GratingPlacer(BPG.PhotonicTemplateBase):
    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)
        self.params = deepcopy(params)
        self.grating_module = importlib.import_module(self.params['grating_module'])
        self.grating_class = getattr(self.grating_module, params['grating_class'])
        self.cords_file = self.params['cords_file']
        self.gds_path = self.params['gds_path']

        self.cords_and_orient = []

    @classmethod
    def get_params_info(cls):
        return dict(
            gds_path='Path to gds to import',
            cords_file='File that has coordinates where grating should be placed',
            grating_class='BPG class for desired grating',
            grating_module='Path to the BPG class for desired grating'
        )

    def draw_layout(self):
        # Instantiate gds that requires substitution
        params = dict(gds_path=self.gds_path)
        if isinstance(self.gds_path,str):
            gds_template = self.new_template(params=params, temp_cls=GDSImport)
            self.add_instance(gds_template, loc=(0, 0), orient='R0')

        # Get coordinates and orientations for gratings from cords_file
        self.get_cords_and_orient()
        print(self.cords_and_orient)

        # Place gratings
        for cord_orient in self.cords_and_orient:
            temp = self.new_template(params=None, temp_cls=self.grating_class)
            inst = self.add_instance(temp, loc=cord_orient[1], orient=cord_orient[0])

    def get_cords_and_orient(self):
        # Read in the file, while ommiting the first , title, line
        f = open(self.cords_file, 'r').readlines()[1:]

        # Pack coordinates on a single line into a list. Then combine all lists and convert to numpy array
        all_cords = []
        for line in f:
            cords_in_line = []
            cords = line[line.find("(") + 1:line.find(")")].strip('\n')
            cords = cords.split(';')
            for cord in cords:
                cord_pair = tuple(list(map(float, cord.split(','))))
                cords_in_line.append(cord_pair)
            all_cords.append(cords_in_line)
        all_cords = np.array(all_cords)

        for i in range(len(all_cords)):
            A = all_cords[i]
            full_set = set([0, 1, 2])
            B = self.all_distances(A, A)

            point_of_max_length = np.argwhere(B == np.max(B))[0]
            third_point = int(list((full_set - set(point_of_max_length)))[0])

            p = A[point_of_max_length[0]]
            s = A[point_of_max_length[1]]
            cordinate = (A[point_of_max_length[0]] + A[point_of_max_length[1]]) / 2

            q = abs(A[point_of_max_length[0]] - A[point_of_max_length[1]])

            non_zero = np.argwhere(q > 1e-5)[0]

            if non_zero == 0:
                dif = A[point_of_max_length[0]] - A[third_point]
                if dif[1] > 0:
                    self.cords_and_orient.append(("R90", cordinate))
                else:
                    self.cords_and_orient.append(("R270", cordinate))
            else:
                dif = A[point_of_max_length[0]] - A[third_point]
                if dif[0] > 0:
                    self.cords_and_orient.append(("R0", cordinate))
                else:
                    self.cords_and_orient.append(("R180", cordinate))

    @staticmethod
    def all_distances(cords1, cords2):
        c1 = np.array(cords1)
        c2 = np.array(cords2)
        z = (c1[:, None, :] - c2[None, :, :]) ** 2
        return np.sum(z, axis=-1) ** 0.5
