import os
from PyQt4.QtGui import *
from processing.core.ProcessingConfig import ProcessingConfig, Setting
from processing.core.AlgorithmProvider import AlgorithmProvider
from processing.core.ProcessingLog import ProcessingLog
from processing_gpf.GPFUtils import GPFUtils
from processing_gpf.NESTAlgorithm import NESTAlgorithm

class NESTAlgorithmProvider(AlgorithmProvider):

    def __init__(self):
        AlgorithmProvider.__init__(self)
        self.activate = False
        self.createAlgsList() #preloading algorithms to speed up

    def initializeSettings(self):
        AlgorithmProvider.initializeSettings(self)
        ProcessingConfig.addSetting(Setting(self.getDescription(), GPFUtils.NEST_FOLDER, "NEST install directory", GPFUtils.programPath(GPFUtils.nestKey())))
        ProcessingConfig.addSetting(Setting(self.getDescription(), GPFUtils.NEST_THREADS, "Maximum number of parallel (native) threads", 4))

    def unload(self):
        AlgorithmProvider.unload(self)
        ProcessingConfig.removeSetting(GPFUtils.NEST_FOLDER)
        ProcessingConfig.removeSetting(GPFUtils.NEST_THREADS)
        
    def createAlgsList(self):
        self.preloadedAlgs = []
        folder = GPFUtils.gpfDescriptionPath(GPFUtils.nestKey())
        for descriptionFile in os.listdir(folder):
            if descriptionFile.endswith("txt"):
                try:
                    alg = NESTAlgorithm(os.path.join(folder, descriptionFile))
                    if alg.name.strip() != "":
                        self.preloadedAlgs.append(alg)
                    else:
                        ProcessingLog.addToLog(ProcessingLog.LOG_ERROR, "Could not open NEST algorithm: " + descriptionFile)
                except Exception,e:
                    ProcessingLog.addToLog(ProcessingLog.LOG_ERROR, "Could not open NEST algorithm: " + descriptionFile)
        # leave out for now as the functionality is not fully developed
        #self.preloadedAlgs.append(MultinodeGPFCreator())  
                    
    def getDescription(self):
        return "NEST (SAR image analysis)"

    def getName(self):
        return "nest"

    def getIcon(self):
        return QIcon(os.path.dirname(__file__) + "/images/nest.png")

    def _loadAlgorithms(self):
        self.algs = self.preloadedAlgs

    def getSupportedOutputRasterLayerExtensions(self):
        return ["tif", "dim", "hdr"]