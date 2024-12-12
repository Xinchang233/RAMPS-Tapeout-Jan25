# -*- coding: utf-8 -*-
"""
@author: bohan

CLO specific grating coupler cell
"""
import BPG

# Import grating coupler cell
from Photonic_Core_Layout.VerticalGratingCoupler.VGCCell import GratingCouplerCell

# import lib module for loading other packages
import importlib


class GratingCouplerCellCLO(GratingCouplerCell):
    """
    Generates a grating coupler that is readily pluggable into another person's layout,
    i.e. a grating coupler + taper

    with some hard-coded parameters specific to CLO

    Parameters
    ----------
    grating_params : dict
        VGC_CLO params. See aforementioned class
    taper_params : dict
        ArbSymmetricTaper params. See aforementioned class
   """
    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):

        # hard coded parameters
        params['grating_package'] = 'Photonic_Layout_45SPCLO.GratingCoupler.base.VGC_CLO'
        params['grating_class'] = 'VerticalGratingCouplerCLO'
        params['taper_package'] = 'Photonic_Core_Layout.Taper.ArbSymmetricTaper'
        params['taper_class'] = 'ArbSymmetricTaper'
        
        super().__init__(temp_db, lib_name, params, used_names, **kwargs)
    # end __init__()


