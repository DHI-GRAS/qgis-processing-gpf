"""
***************************************************************************
    BEAMAlgorithmProvider.py
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
from qgis.PyQt.QtGui import QIcon
from processing.core.ProcessingConfig import ProcessingConfig, Setting
from processing.core.AlgorithmProvider import AlgorithmProvider
from processing.core.ProcessingLog import ProcessingLog
from processing_gpf.GPFUtils import GPFUtils
from processing_gpf.BEAMAlgorithm import BEAMAlgorithm


class BEAMAlgorithmProvider(AlgorithmProvider):

    def __init__(self):
        AlgorithmProvider.__init__(self)
        self.activate = False
        self.createAlgsList()  # preloading algorithms to speed up

    def initializeSettings(self):
        AlgorithmProvider.initializeSettings(self)
        ProcessingConfig.addSetting(Setting(self.getDescription(),
                                            GPFUtils.BEAM_FOLDER,
                                            "BEAM install directory",
                                            GPFUtils.programPath(GPFUtils.beamKey())))
        ProcessingConfig.addSetting(Setting(self.getDescription(),
                                            GPFUtils.BEAM_THREADS,
                                            "Maximum number of parallel (native) threads",
                                            4))

    def unload(self):
        AlgorithmProvider.unload(self)
        ProcessingConfig.removeSetting(GPFUtils.BEAM_FOLDER)
        ProcessingConfig.removeSetting(GPFUtils.BEAM_THREADS)

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
                        ProcessingLog.addToLog(ProcessingLog.LOG_ERROR,
                                               "Could not open BEAM algorithm: " + descriptionFile)
                except Exception as e:
                    ProcessingLog.addToLog(ProcessingLog.LOG_ERROR,
                                           "Could not open BEAM algorithm: " + descriptionFile)
        # leave out for now as the functionality is not fully developed
        # self.preloadedAlgs.append(MultinodeGPFCreator())

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
