from qgis.core import *
import os, sys
import inspect
from sextante.core.Sextante import Sextante
from sextante_gpf.BEAMAlgorithmProvider import BEAMAlgorithmProvider 
from sextante_gpf.NESTAlgorithmProvider import NESTAlgorithmProvider 

cmd_folder = os.path.split(inspect.getfile( inspect.currentframe() ))[0]
if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)

class SextanteGpfPlugin:

    def __init__(self):
        self.BeamProvider = BEAMAlgorithmProvider()
        self.NestProvider = NESTAlgorithmProvider()
        
    def initGui(self):
        Sextante.addProvider(self.BeamProvider)
        Sextante.addProvider(self.NestProvider)

    def unload(self):
        Sextante.removeProvider(self.BeamProvider)
        Sextante.removeProvider(self.NestProvider)
