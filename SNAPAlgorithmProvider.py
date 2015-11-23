import os
from PyQt4.QtGui import *
from processing.core.ProcessingConfig import ProcessingConfig, Setting
from processing.core.AlgorithmProvider import AlgorithmProvider
from processing.core.ProcessingLog import ProcessingLog
from processing.modeler.WrongModelException import WrongModelException
from processing_gpf.GPFUtils import GPFUtils
from processing_gpf.GpfModelerAlgorithm import GpfModelerAlgorithm
from processing_gpf.S1TbxAlgorithm import S1TbxAlgorithm
from processing_gpf.SNAPAlgorithm import SNAPAlgorithm
from processing_gpf.CreateNewGpfModelAction import CreateNewGpfModelAction
from processing_gpf.EditGpfModelAction import EditGpfModelAction

class SNAPAlgorithmProvider(AlgorithmProvider):

    def __init__(self):
        AlgorithmProvider.__init__(self)
        self.actions = [CreateNewGpfModelAction(self)]
        self.contextMenuActions = [EditGpfModelAction()]
        self.activate = False
        
        #self.createAlgsList() #preloading algorithms to speed up

    def initializeSettings(self):
        AlgorithmProvider.initializeSettings(self)
        ProcessingConfig.addSetting(Setting(self.getDescription(), GPFUtils.SNAP_FOLDER, "SNAP install directory", GPFUtils.programPath(GPFUtils.s1tbxKey())))
        ProcessingConfig.addSetting(Setting(self.getDescription(), GPFUtils.SNAP_THREADS, "Maximum number of parallel (native) threads", 4))
        ProcessingConfig.addSetting(Setting(self.getDescription(), GPFUtils.GPF_MODELS_FOLDER, "GPF models' directory", GPFUtils.modelsFolder()))
        ProcessingConfig.addSetting(Setting(self.getDescription(), GPFUtils.S1TBX_ACTIVATE, "Activate Sentinel-1 toolbox", False))

    def unload(self):
        AlgorithmProvider.unload(self)
        ProcessingConfig.removeSetting(GPFUtils.SNAP_FOLDER)
        ProcessingConfig.removeSetting(GPFUtils.SNAP_THREADS)
        ProcessingConfig.removeSetting(GPFUtils.GPF_MODELS_FOLDER)
        ProcessingConfig.removeSetting(GPFUtils.S1TBX_ACTIVATE)
        
    def createAlgsList(self):
        self.preloadedAlgs = []
        folder = GPFUtils.gpfDescriptionPath(GPFUtils.snapKey())
        for descriptionFile in os.listdir(folder):
            if descriptionFile.endswith("txt"):
                try:
                    alg = SNAPAlgorithm(os.path.join(folder, descriptionFile))
                    if alg.name.strip() != "":
                        alg.provider = self
                        self.preloadedAlgs.append(alg)
                    else:
                        ProcessingLog.addToLog(ProcessingLog.LOG_ERROR, "Could not open SNAP generic algorithm: " + descriptionFile)
                except Exception,e:
                    ProcessingLog.addToLog(ProcessingLog.LOG_ERROR, str(e))
                    ProcessingLog.addToLog(ProcessingLog.LOG_ERROR, "Could not open SNAP generic algorithm: " + descriptionFile)
                    
    def createS1AlgsList(self):
        self.preloadedS1Algs = []
        folder = GPFUtils.gpfDescriptionPath(GPFUtils.s1tbxKey())
        for descriptionFile in os.listdir(folder):
            if descriptionFile.endswith("txt"):
                try:
                    alg = S1TbxAlgorithm(os.path.join(folder, descriptionFile))
                    if alg.name.strip() != "":
                        alg.provider = self
                        self.preloadedS1Algs.append(alg)
                    else:
                        ProcessingLog.addToLog(ProcessingLog.LOG_ERROR, "Could not open S1 Toolbox algorithm: " + descriptionFile)
                except Exception,e:
                    ProcessingLog.addToLog(ProcessingLog.LOG_ERROR, str(e))
                    ProcessingLog.addToLog(ProcessingLog.LOG_ERROR, "Could not open S1 Toolbox algorithm: " + descriptionFile)
    
    def loadGpfModels(self, folder):
        if not os.path.exists(folder):
            return
        for path, subdirs, files in os.walk(folder):
            for descriptionFile in files:
                if descriptionFile.endswith('xml'):
                    try:
                        fullpath = os.path.join(path, descriptionFile)
                        alg = GpfModelerAlgorithm.fromFile(fullpath, self)
                        if alg and alg.name:
                            #alg.provider = self
                            alg.descriptionFile = fullpath
                            self.algs.append(alg)
                        else:
                            ProcessingLog.addToLog(ProcessingLog.LOG_ERROR,
                                self.tr('Could not load model %s', 'ModelerAlgorithmProvider') % descriptionFile)
                    except WrongModelException, e:
                        ProcessingLog.addToLog(ProcessingLog.LOG_ERROR,
                            self.tr('Could not load model %s\n%s', 'ModelerAlgorithmProvider') % (descriptionFile, e.msg))
                    
    def getDescription(self):
        return GPFUtils.providerDescription()

    def getName(self):
        return "snap"

    def getIcon(self):
        return QIcon(os.path.dirname(__file__) + "/images/snap.png")
    
    def getAlgorithmFromOperator(self, operatorName):
        for alg in self.algs:
            if alg.operator == operatorName:
                return alg
        return None

    def _loadAlgorithms(self):
        self.createAlgsList()
        self.algs = self.preloadedAlgs
        if ProcessingConfig.getSetting(GPFUtils.S1TBX_ACTIVATE) == True:
            self.createS1AlgsList()
            for alg in self.preloadedS1Algs:
                self.algs.append(alg)                
        # Also load models
        self.loadGpfModels(GPFUtils.modelsFolder())


    def getSupportedOutputRasterLayerExtensions(self):
        return ["tif", "dim", "hdr"]