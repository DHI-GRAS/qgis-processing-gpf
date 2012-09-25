from qgis.core import *
import os, sys
import inspect
from sextante.core.Sextante import Sextante
from sextante_beam.BEAMAlgorithmProvider import BEAMAlgorithmProvider 


cmd_folder = os.path.split(inspect.getfile( inspect.currentframe() ))[0]
if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)

class SextanteBeamPlugin:

    def __init__(self):
        self.provider = BEAMAlgorithmProvider()
    def initGui(self):
        Sextante.addProvider(self.provider)

    def unload(self):
        Sextante.removeProvider(self.provider)
