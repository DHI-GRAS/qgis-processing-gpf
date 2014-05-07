import os
from PyQt4.QtGui import *
from processing_gpf.GPFUtils import GPFUtils
from processing_gpf.GPFAlgorithm import GPFAlgorithm


class BEAMAlgorithm(GPFAlgorithm):
    
    def __init__(self, descriptionfile):
        GPFAlgorithm.__init__(self, descriptionfile)
        self.programKey = GPFUtils.beamKey()
        
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
                
        