# -*- coding: utf-8 -*-
"""
Created on Tue Oct 30 16:51:10 2018

@author: djorde
"""

import BPG
from Photonic_Core_Layout.ArbitraryPolygon.ArbitraryPolygon import ArbitraryPolygon

if __name__ == '__main__':
    spec_file = 'Photonic_Core_Layout/ArbitraryPolygon/specs/arbitrary_polygon.yaml'
    PLM = BPG.PhotonicLayoutManager(spec_file)
    PLM.generate_content()
    PLM.generate_gds()
    PLM.generate_flat_content()
    PLM.dataprep()
    PLM.generate_dataprep_gds()
