import BPG
import importlib
# from Photonic_Core_Layout.AdiabaticPaths.AdiabaticPaths import AdiabaticPaths
from BPG.gds.io import GDSImport
from Photonic_Core_Layout.ViaStack.ViaStack import ViaStack
from BPG.objects import PhotonicRect, PhotonicRound, PhotonicPolygon
from bag.layout.util import BBox
from math import floor


class RingTunable(BPG.PhotonicTemplateBase):
    """
    This class creates
    """

    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)
        self.ring_params = self.params['ring_params']
        self.heater_params = self.params['heater_params']
        self.via_params = self.params['via_params']

        # Master declaration

        self.ringtunable_master = dict()
        self.wgs_master = dict()

        # Instances declaration
        self.ringtunable = dict()
        self.wgs = dict()



