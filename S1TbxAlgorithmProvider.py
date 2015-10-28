"""
***************************************************************************
    S1TbxAlgorithmProvider.py
-------------------------------------
    Copyright (C) 2014 TIGER-NET (www.tiger-net.org)

***************************************************************************
* This plugin is part of the Water Observation Information System (WOIS)  *
* developed under the TIGER-NET project funded by the European Space      *
* Agency as part of the long-term TIGER initiative aiming at promoting    *
* the use of Earth Observation (EO) for improved Integrated Water         *
* Resources Management (IWRM) in Africa.                                  *
*                                                                         *
* WOIS is a free software i.e. you can redistribute it and/or modify      *
* it under the terms of the GNU General Public License as published       *
* by the Free Software Foundation, either version 3 of the License,       *
* or (at your option) any later version.                                  *
*                                                                         *
* WOIS is distributed in the hope that it will be useful, but WITHOUT ANY * 
* WARRANTY; without even the implied warranty of MERCHANTABILITY or       *
* FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License   *
* for more details.                                                       *
*                                                                         *
* You should have received a copy of the GNU General Public License along *
* with this program.  If not, see <http://www.gnu.org/licenses/>.         *
***************************************************************************
"""

import os
from PyQt4.QtGui import *
from processing.core.ProcessingConfig import ProcessingConfig, Setting
from processing.core.AlgorithmProvider import AlgorithmProvider
from processing.core.ProcessingLog import ProcessingLog
from processing.modeler.WrongModelException import WrongModelException
from processing_gpf.GPFUtils import GPFUtils
from processing_gpf.GpfModelerAlgorithm import GpfModelerAlgorithm
from processing_gpf.S1TbxAlgorithm import S1TbxAlgorithm
from processing_gpf.CreateNewGpfModelAction import CreateNewGpfModelAction
from processing_gpf.EditGpfModelAction import EditGpfModelAction

class S1TbxAlgorithmProvider(AlgorithmProvider):

    def __init__(self):
        AlgorithmProvider.__init__(self)
        self.actions = [CreateNewGpfModelAction(self)]
        self.contextMenuActions = [EditGpfModelAction()]
        self.activate = False
        self.createAlgsList() #preloading algorithms to speed up

    def initializeSettings(self):
        AlgorithmProvider.initializeSettings(self)
        ProcessingConfig.addSetting(Setting(self.getDescription(), GPFUtils.S1TBX_FOLDER, "S1 Toolbox install directory", GPFUtils.programPath(GPFUtils.s1tbxKey())))
        ProcessingConfig.addSetting(Setting(self.getDescription(), GPFUtils.S1TBX_THREADS, "Maximum number of parallel (native) threads", 4))
        ProcessingConfig.addSetting(Setting(self.getDescription(), GPFUtils.MODELS_FOLDER, "GPF models' directory", GPFUtils.modelsFolder()))

    def unload(self):
        AlgorithmProvider.unload(self)
        ProcessingConfig.removeSetting(GPFUtils.S1TBX_FOLDER)
        ProcessingConfig.removeSetting(GPFUtils.S1TBX_THREADS)
        
    def createAlgsList(self):
        self.preloadedAlgs = []
        folder = GPFUtils.gpfDescriptionPath(GPFUtils.s1tbxKey())
        for descriptionFile in os.listdir(folder):
            if descriptionFile.endswith("txt"):
                try:
                    alg = S1TbxAlgorithm(os.path.join(folder, descriptionFile))
                    if alg.name.strip() != "":
                        alg.provider = self
                        self.preloadedAlgs.append(alg)
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
        return "S1 Toolbox (SAR image analysis)"

    def getName(self):
        return "s1tbx"

    def getIcon(self):
        return QIcon(os.path.dirname(__file__) + "/images/s1tbx.png")
    
    def getAlgorithmFromOperator(self, operatorName):
        for alg in self.algs:
            if alg.operator == operatorName:
                return alg
        return None

    def _loadAlgorithms(self):
        self.algs = self.preloadedAlgs
        # Also load models
        self.loadGpfModels(GPFUtils.modelsFolder())

    def getSupportedOutputRasterLayerExtensions(self):
        return ["tif", "dim", "hdr"]