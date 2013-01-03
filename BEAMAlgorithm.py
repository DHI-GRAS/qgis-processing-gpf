import os
from PyQt4.QtGui import *
from sextante_gpf.GPFUtils import GPFUtils
from sextante_gpf.GPFAlgorithm import GPFAlgorithm


class BEAMAlgorithm(GPFAlgorithm):
        
    def processAlgorithm(self, progress):
        GPFAlgorithm.processAlgorithm(self, GPFUtils.beamKey(), progress)
        
    def helpFile(self):
        GPFAlgorithm.helpFile(self, GPFUtils.beamKey())
        
    def getIcon(self):
        return  QIcon(os.path.dirname(__file__) + "/images/beam.png")
    
    def getCopy(self):
        newone = BEAMAlgorithm(self.descriptionFile)
        newone.provider = self.provider
        return newone
                
        