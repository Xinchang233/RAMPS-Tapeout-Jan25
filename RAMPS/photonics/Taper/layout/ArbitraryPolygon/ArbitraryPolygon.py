# -*- coding: utf-8 -*-
"""
Created on Thu Oct 25 13:43:10 2018

@author: djorde
"""

import BPG
from bag.layout.util import BBox
from operator import itemgetter
import numpy as np
from BPG.objects import PhotonicPath, PhotonicPolygon
from scipy.io import loadmat
from scipy.signal import resample


class ArbitraryPolygon(BPG.PhotonicTemplateBase):
    def __init__(self, temp_db, lib_name, params, used_names, **kwargs, ):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)
        self.params = params
        self.layer = params['layer']
        self.port_layer = params['port_layer']
        self.width = params['width']
        self.file = self.params['file']
        self.downsample = self.params['downsample']
        self.downsample_size = self.params['downsample_size']

    @classmethod
    def get_params_info(cls):
        return dict(
            layer='Physical layer where class object will be instantiated',
            port_layer='None',
            width='Width of the ArbPol coupler',
            file='.mat file with points that build up the ArbPol coupler',
            downsample='Determines if data from .mat file is downsampled. This is done if there are too many points and created polygone does not have uniform boundary',
            downsample_size='Determines by how many times will the data be downsampled. E.g. if downsample_size = 4, the new data will have lenght that is 4 times shorter than initial data.'
        )

    @classmethod
    def get_default_param_values(cls):
        return dict(
            layer=None,
            port_layer=None,
            width=None,
            file=None,
            downsample=None,
            downsample_size=None
        )

    def draw_layout(self) -> None:
        points1, points2 = self.read_points()
        poly1 = self.create_poly(points1, self.layer)
        poly2 = self.create_poly(points2, self.layer)
        self.add_obj(poly1)
        self.add_obj(poly2)

        ll = points1[0]  # Lower left end of waveguide
        ll[1] = (ll[1] + points1[-1][1]) / 2  # Place port in the middle of the wg

        ul = points2[0]  # Upper left end of waveguide
        ul[1] = (ul[1] + points2[-1][1]) / 2  # Place port in the middle of the wg

        lr = max(points1, key=itemgetter(0))

        index1 = np.argmax(points1, axis=0)[0]
        y1 = points1[index1][1]
        try:
            minSize = self.photonic_tech_info.dataprep_parameters['MinSpace'][
                self.layer]  # Read from tech file what is min size for the given layer
        except:
            minSize = 0.1  # 100 nm
        try:
            next_point_is_up = np.where(points1[:, 1] > y1 + minSize)[0][0]
            next_point_is_below = np.where(points1[:, 1] < y1 - minSize)[0][-1]

            if abs(next_point_is_up - index1) < abs(next_point_is_below - index1):
                lr[1] = (lr[1] + points1[next_point_is_up][1]) / 2
            else:
                lr[1] = (lr[1] + points1[next_point_is_below][1]) / 2
        except IndexError:
            if points1[index1][1] < points1[index1 + 1][1]:
                lr[1] = (lr[1] + points1[index1 + 1][1]) / 2
            else:
                lr[1] = (lr[1] + points1[index1 - 1][1]) / 2

        ur = max(points2, key=itemgetter(0))
        val2 = np.argmax(points2, axis=0)[0]
        if points2[val2][1] < points2[val2 + 1][1]:
            ur[1] = (ur[1] + points2[val2 + 1][1]) / 2
        else:
            ur[1] = (ur[1] + points2[val2 - 1][1]) / 2
        self.create_ports(ll, lr, ul, ur)

    def create_poly(self, points, layer) -> PhotonicPolygon:
        """
        Takes the list of points and generates a PhotonicPath shape
        """
        return PhotonicPolygon(
            resolution=self.grid.resolution,
            layer=layer,
            points=points,
            unit_mode=False,
        )

    def create_ports(self, ll, lr, ul, ur) -> None:
        """
        Add PORT0 to the left edge and add PORT1 to the right edge
        """
        self.add_photonic_port(
            name='PORT_IN_LOWER',
            center=(ll[0], ll[1]),
            orient='R0',
            width=self.width,
            layer=self.port_layer,
            resolution=self.grid.resolution,
            unit_mode=False,
            show=False
        )

        self.add_photonic_port(
            name='PORT_OUT_LOWER',
            center=(lr[0], lr[1]),
            orient='R180',
            width=self.width,
            layer=self.port_layer,
            resolution=self.grid.resolution,
            unit_mode=False,
            show=False
        )
        self.add_photonic_port(
            name='PORT_IN_UPPER',
            center=(ul[0], ul[1]),
            orient='R0',
            width=self.width,
            layer=self.port_layer,
            resolution=self.grid.resolution,
            unit_mode=False,
            show=False
        )
        self.add_photonic_port(
            name='PORT_OUT_UPPER',
            center=(ur[0], ur[1]),
            orient='R180',
            width=self.width,
            layer=self.port_layer,
            resolution=self.grid.resolution,
            unit_mode=False,
            show=False
        )

    def read_points(self) -> None:
        if self.downsample:
            try:

                ee = loadmat(self.file)
                coordsb = ee['bv'] * 1e6
                coordst = ee['tv'] * 1e6

                A = coordsb[1::self.downsample_size]
                B = coordst[1::self.downsample_size]

                A = np.append(A, coordsb[-self.downsample_size + 1:-1], axis=0)
                B = np.append(B, coordst[-self.downsample_size + 1:-1], axis=0)
                return A, B
            except IOError:
                print("There is no geometry designed with this parameters yet :(.\n Change input values.")
        else:
            ee = loadmat(self.file)
            coordsb = ee['bv'] * 1e6
            coordst = ee['tv'] * 1e6
            coordst += np.array([abs(coordsb[0][0]), 0])
            coordsb += np.array([abs(coordsb[0][0]), 0])
            return coordsb, coordst

    def read_points1(self) -> None:
        if self.downsample:
            try:
                ee = loadmat(self.file)
                coordsb = ee['bv'] * 1e6
                coordst = ee['tv'] * 1e6
                dw = 5
                dw_bus = 1
                n = 50
                # bottom input output parts
                ix = np.argmax(coordsb[:, 0])
                col1 = coordsb[:, 0]
                col2 = coordsb[:, 1]

                col1_1 = np.hstack((round(col1[0]), col1[0:5]))
                col2_1 = np.hstack((col2[0], col2[0:5]))
                ArbPol_inport1_dy = col2_1[0]

                col1_2 = col1[6:ix - 5]
                col2_2 = col2[6:ix - 5]
                col1_2 = col1_2[::n]
                col2_2 = col2_2[::n]

                col1_3 = np.hstack((col1[ix - 6:ix], round(col1[ix])))
                col2_3 = np.hstack((col2[ix - 6:ix], col2[ix]))

                self.ArbPol_length = round(col1[ix]) - round(col1[0])
                self.ArbPol_outport1_dx = col1_3[-1]
                ArbPol_outport1_dy = col2_3[-1]

                col1_4 = np.hstack((round(col1[ix]), col1[ix + 1:ix + 5]))
                col2_4 = np.hstack((col2[ix + 1], col2[ix + 1:ix + 5]))

                self.ArbPol_outport1_ux = col1_4[0]
                ArbPol_outport1_uy = col2_4[0]

                col1_5 = col1[ix + 6: - 6]
                col2_5 = col2[6 + ix: - 6]
                col1_5 = col1_5[::n]
                col2_5 = col2_5[::n]

                col1_6 = np.hstack((col1[-6:-1], round(col1[-1])))
                col2_6 = np.hstack((col2[-6:-1], col2[-1]))
                self.ArbPol_inport1_ux = col2_6[-1]
                ArbPol_inport1_uy = col2_6[-1]
                col1 = np.hstack((col1_1, col1_2, col1_3, col1_4, col1_5, col1_6))
                if 1 > 0:
                    col1a = np.hstack((col1_1, col1_2, col1_3))
                    col2a = np.hstack((col2_1, col2_2, col2_3))

                    ddwa = 0.5 * dw + col2a * 0
                    ixx = int(round(0.06 * len(ddwa)))
                    ddwa[0:ixx] = self.recta(col1a[0], col1a[ixx], -(0.4 - dw_bus) * 0.5, 0.5 * dw, col1a[0:ixx])
                    ddwa[-ixx: -1] = self.recta(col1a[-ixx], col1a[-1], 0.5 * dw, -(0.4 - dw_bus) * 0.5, col1a[-ixx:-1])
                    ddwa[-1] = -(0.4 - dw_bus) * 0.5
                    col2b = np.hstack((col2_4, col2_5, col2_6))

                    ddwb = 0.5 * dw + col2b * 0
                    ixx = int(round(0.06 * len(ddwb)))
                    ddwb[0:ixx] = self.recta(col1a[0], col1a[ixx], -(0.4 - dw_bus) * 0.5, 0.5 * dw, col1a[0:ixx])
                    ddwb[-ixx: -1] = self.recta(col1a[-ixx], col1a[-1], 0.5 * dw, -(0.4 - dw_bus) * 0.5, col1a[-ixx:-1])
                    ddwb[-1] = -(0.4 - dw_bus) * 0.5

                    col2a = col2a - ddwa
                    col2b = col2b + ddwb
                    col2 = np.hstack((col2a, col2b))
                coordsb = np.vstack((col1, col2)).T

                # top port
                ix = np.argmax(coordst[:, 0])
                col1 = coordst[:, 0]
                col2 = coordst[:, 1]

                col1_1 = np.hstack((round(col1[0]), col1[0:5]))
                col2_1 = np.hstack((col2[0], col2[0:5]))
                self.ArbPol_inport2_dx = round(col1_1[0])
                ArbPol_inport2_dy = col2_1[0]

                col1_2 = col1[6:ix - 5]
                col2_2 = col2[6:ix - 5]
                col1_2 = col1_2[::n]
                col2_2 = col2_2[::n]

                col1_3 = np.hstack((col1[ix - 6:ix], round(col1[ix])))
                col2_3 = np.hstack((col2[ix - 6:ix], col2[ix]))

                self.ArbPol_outport2_dx = col1_3[-1]
                ArbPol_outport2_dy = col2_3[-1]

                col1_4 = np.hstack((round(col1[ix]), col1[ix + 1:ix + 5]))
                col2_4 = np.hstack((col2[ix + 1], col2[ix + 1:ix + 5]))

                self.ArbPol_outport2_ux = col1_4[0]
                ArbPol_outport2_uy = col2_4[0]

                col1_5 = col1[ix + 6: - 6]
                col2_5 = col2[6 + ix: - 6]
                col1_5 = col1_5[::n]
                col2_5 = col2_5[::n]

                col1_6 = np.hstack((col1[-6:-1], round(col1[-1])))
                col2_6 = np.hstack((col2[-6:-1], col2[-1]))
                self.ArbPol_inport2_ux = col1_6[-1]
                ArbPol_inport2_uy = col2_6[-1]
                col1 = np.hstack((col1_1, col1_2, col1_3, col1_4, col1_5, col1_6))
                if 1 > 0:
                    col1a = np.hstack((col1_1, col1_2, col1_3))
                    col2a = np.hstack((col2_1, col2_2, col2_3))

                    ddwa = 0.5 * dw + col2a * 0
                    ixx = int(round(0.06 * len(ddwa)))
                    ddwa[0:ixx] = self.recta(col1a[0], col1a[ixx], -(0.4 - dw_bus) * 0.5, 0.5 * dw, col1a[0:ixx])
                    ddwa[-ixx: -1] = self.recta(col1a[-ixx], col1a[-1], 0.5 * dw, -(0.4 - dw_bus) * 0.5, col1a[-ixx:-1])
                    ddwa[-1] = -(0.4 - dw_bus) * 0.5
                    col2b = np.hstack((col2_4, col2_5, col2_6))

                    ddwb = 0.5 * dw + col2b * 0
                    ixx = int(round(0.06 * len(ddwb)))
                    ddwb[0:ixx] = self.recta(col1a[0], col1a[ixx], -(0.4 - dw_bus) * 0.5, 0.5 * dw, col1a[0:ixx])
                    ddwb[-ixx: -1] = self.recta(col1a[-ixx], col1a[-1], 0.5 * dw, -(0.4 - dw_bus) * 0.5, col1a[-ixx:-1])
                    ddwb[-1] = -(0.4 - dw_bus) * 0.5

                    col2a = col2a - ddwa
                    col2b = col2b + ddwb
                    col2 = np.hstack((col2a, col2b))
                coordst = np.vstack((col1, col2)).T
                return coordsb, coordst
            except IOError:
                print("There is no ArbPol geometry designed with this parameters yet :(.\n Change input values.")
        else:
            ee = loadmat(self.file)
            coordsb = ee['bv'] * 1e6
            coordst = ee['tv'] * 1e6
            coordst += np.array([abs(coordsb[0][0]), 0])
            coordsb += np.array([abs(coordsb[0][0]), 0])
            return coordsb, coordst

    def recta(self, x1, x2, y1, y2, x):
        y = (float(y2) - float(y1)) / (float(x2) - float(x1)) * (x - x2) + y2
        return y
