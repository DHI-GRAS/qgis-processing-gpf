import os
from PyQt4.QtGui import *
from sextante.core.SextanteConfig import SextanteConfig, Setting
from sextante.core.AlgorithmProvider import AlgorithmProvider
from sextante.core.SextanteLog import SextanteLog
from sextante_gpf.GPFUtils import GPFUtils
from sextante_gpf.BEAMAlgorithm import BEAMAlgorithm

class BEAMAlgorithmProvider(AlgorithmProvider):

    def __init__(self):
        AlgorithmProvider.__init__(self)
        self.activate = False
        self.createAlgsList() #preloading algorithms to speed up

    def initializeSettings(self):
        AlgorithmProvider.initializeSettings(self)
        SextanteConfig.addSetting(Setting(self.getDescription(), GPFUtils.BEAM_FOLDER, "BEAM install directory", GPFUtils.programPath(GPFUtils.beamKey())))

    def unload(self):
        AlgorithmProvider.unload(self)
        SextanteConfig.removeSetting(GPFUtils.BEAM_FOLDER)
        
    def createAlgsList(self):
        self.preloadedAlgs = []
        folder = GPFUtils.gpfDescriptionPath(GPFUtils.beamKey())
        for descriptionFile in os.listdir(folder):
            if descriptionFile.endswith("txt"):
                try:
                    alg = BEAMAlgorithm(os.path.join(folder, descriptionFile))
                    if alg.name.strip() != "":
                        self.preloadedAlgs.append(alg)
                    else:
                        SextanteLog.addToLog(SextanteLog.LOG_ERROR, "Could not open BEAM algorithm: " + descriptionFile)
                except Exception,e:
                    SextanteLog.addToLog(SextanteLog.LOG_ERROR, "Could not open BEAM algorithm: " + descriptionFile)
        # leave out for now as the functionality is not fully developed
        #self.preloadedAlgs.append(MultinodeGPFCreator())  
                    
    def getDescription(self):
        return "BEAM (Envisat image analysis)"

    def getName(self):
        return "beam"

    def getIcon(self):
        return QIcon(os.path.dirname(__file__) + "/images/beam.png")

    def _loadAlgorithms(self):
        self.algs = self.preloadedAlgs  
        
    def getSupportedOutputRasterLayerExtensions(self):
        return ["tif", "dim"]