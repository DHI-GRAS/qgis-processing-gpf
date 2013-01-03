import os
from PyQt4.QtGui import *
from sextante_gpf.GPFUtils import GPFUtils
from sextante_gpf.GPFAlgorithm import GPFAlgorithm


class NESTAlgorithm(GPFAlgorithm):
        
    def processAlgorithm(self, progress):
        GPFAlgorithm.processAlgorithm(self, GPFUtils.nestKey(), progress)
        
    def helpFile(self):
        GPFAlgorithm.helpFile(self, GPFUtils.nestKey())
        
    def getIcon(self):
        return  QIcon(os.path.dirname(__file__) + "/images/nest.png")
    
    def getCopy(self):
        newone = NESTAlgorithm(self.descriptionFile)
        newone.provider = self.provider
        return newone
                
        