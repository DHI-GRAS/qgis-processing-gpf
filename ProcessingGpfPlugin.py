from qgis.core import *
import os, sys
import inspect
from processing.core.Processing import Processing
from processing_gpf.BEAMAlgorithmProvider import BEAMAlgorithmProvider 
from processing_gpf.NESTAlgorithmProvider import NESTAlgorithmProvider 

cmd_folder = os.path.split(inspect.getfile( inspect.currentframe() ))[0]
if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)

class ProcessingGpfPlugin:

    def __init__(self, iface):
        self.BeamProvider = BEAMAlgorithmProvider()
        self.NestProvider = NESTAlgorithmProvider()
        self.iface = iface
        
    def initGui(self):
        Processing.addProvider(self.BeamProvider, True)
        Processing.addProvider(self.NestProvider, True)

    def unload(self):
        Processing.removeProvider(self.BeamProvider)
        Processing.removeProvider(self.NestProvider)
