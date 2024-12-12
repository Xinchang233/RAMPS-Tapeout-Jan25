import numpy as np
from Photonic_Core_Layout.WaveguideBase.PathWaveguide import PathWaveguide

EdgeLength = 0.015


class SBendWaveguide(PathWaveguide):

    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        PathWaveguide.__init__(self, temp_db, lib_name, params, used_names, **kwargs)
        self.length = self.params['length']
        self.shift_left = self.params['shift_left']

        # Parameter checking: Make sure parameters are valid type and values
        if any(val <= 0 for val in [self.length]):
            raise ValueError("The width, amplitude, and wavelength cannot be zero or negative")
        if any(not isinstance(val, (int, float)) for val in [self.length, self.shift_left]):
            raise ValueError('Width, amplitude, wavelength must be int or float')

    @classmethod
    def get_params_info(dummy):
        return {
            'length':               'length along main axis',
            'shift_left':           'transverse shift, positive is to left negative is to the right',
            'width':                'Waveguide width',
            'layer':                'Layer or LPP on which to draw the waveguide',
            # 'width0':               'Waveguide width at "0" end',
            # 'width1':               'Waveguide width at "1" end',
        }

    # @classmethod
    # def get_default_param_values(cls):
    #     pass

    def create_point_list(self) -> None:
        """
        Defines the points representing the path segments to be drawn
        """
        # EdgeLength = GlobalEdgeLength 
        # EdgeLength = 1.0
        NSteps  = int(np.ceil(self.length / EdgeLength))
        lnorm   = np.arange(NSteps + 1) / NSteps
        # BPG code CosineWaveguide uses one tiny step at each end to keep end normal...
        lnorm   = np.insert(lnorm, [1,-1], [0 + 0.01 / NSteps, 1 - 0.01 / NSteps])

        xx      = lnorm * self.length
        ux      = 2 * xx / self.length - 1   # x normalized to vary from -1 to 1 
        uy      = (15. / 8.) * ux  + (-10 / 8.)  * np.power(ux,3)  + (3.0 / 8.0) * np.power(ux,5)
        yy      = (uy + 1.) * self.shift_left / 2
        self.points = [(xx[ind], yy[ind]) for ind in range(xx.shape[0])]
        # print('In SBendPathWaveguide: ')
        # print([p[0] for p in self.points])

        # dxdux   = self.length / 2 + 0.0 * lnorm
        # duydux  = (15. / 8.)  + (-30 / 8.)  * np.power(ux,2)  + (15.0 / 8.0) * np.power(ux,4)
        # dydux   = duydux * self.shift_left / 2
        # return ([ (xx[ind], yy[ind]) for ind in range(len(xx))], 
        #         [ (dxdux[ind], dydux[ind]) for ind in range(len(xx))])

        # dx = min(self.wavelength / 100, self.grid.resolution * 10)  # TODO: magic numbers
        # x = np.arange(self.start / 4 * self.wavelength, self.end / 4 * self.wavelength, dx)
        # y = self.amp * np.cos(2 * np.pi * x / self.wavelength)
        # self.points = [(x[ind], y[ind]) for ind in range(x.shape[0])]




