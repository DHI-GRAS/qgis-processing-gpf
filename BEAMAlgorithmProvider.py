import os
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from sextante.core.SextanteConfig import SextanteConfig, Setting
from sextante.core.AlgorithmProvider import AlgorithmProvider
from sextante.core.SextanteLog import SextanteLog
from sextante_beam.BEAMUtils import BEAMUtils
from sextante_beam.BEAMAlgorithm import BEAMAlgorithm
from sextante_beam.MultinodeGPFCreator import MultinodeGPFCreator
from sextante.core.SextanteUtils import SextanteUtils

class BEAMAlgorithmProvider(AlgorithmProvider):

    def __init__(self):
        AlgorithmProvider.__init__(self)
        self.activate = False
        self.createAlgsList() #preloading algorithms to speed up

    def initializeSettings(self):
        AlgorithmProvider.initializeSettings(self)
        SextanteConfig.addSetting(Setting(self.getDescription(), BEAMUtils.BEAM_FOLDER, "OTB command line tools folder", BEAMUtils. beamPath()))

    def unload(self):
        AlgorithmProvider.unload(self)
        SextanteConfig.removeSetting(BEAMUtils.BEAM_FOLDER)
        
    def createAlgsList(self):
        self.preloadedAlgs = []
        folder = BEAMUtils.beamDescriptionPath()
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
        self.preloadedAlgs.append(MultinodeGPFCreator())  
                    
    def getDescription(self):
        return "BEAM (Envisat image analysis)"

    def getName(self):
        return "beam"

    def getIcon(self):
        return QIcon(os.path.dirname(__file__) + "/images/beam.png")

    def _loadAlgorithms(self):
        self.algs = self.preloadedAlgs  