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

from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.core import Qgis, QgsProcessingProvider, QgsMessageLog
from processing.core.ProcessingConfig import ProcessingConfig, Setting

from processing_gpf.GPFUtils import GPFUtils
from processing_gpf.BEAMAlgorithm import BEAMAlgorithm


class BEAMAlgorithmProvider(QgsProcessingProvider):

    activateSetting = "ACTIVATE_BEAM"
    
    def __init__(self):
        QgsProcessingProvider.__init__(self)
        self.activate = False
        self.algs = []

    def load(self):
        ProcessingConfig.settingIcons[self.name()] = self.icon()
        ProcessingConfig.addSetting(Setting(self.name(), self.activateSetting,
                                            self.tr('Activate'), True))
        ProcessingConfig.addSetting(Setting(self.name(),
                                            GPFUtils.BEAM_FOLDER,
                                            self.tr("BEAM install directory"),
                                            GPFUtils.programPath(GPFUtils.beamKey())))
        ProcessingConfig.addSetting(Setting(self.name(),
                                            GPFUtils.BEAM_THREADS,
                                            self.tr("Maximum number of parallel (native) threads"),
                                            4))
        ProcessingConfig.readSettings()
        self.refreshAlgorithms()
        return True

    def unload(self):
        ProcessingConfig.removeSetting(self.activateSetting)
        ProcessingConfig.removeSetting(GPFUtils.BEAM_FOLDER)
        ProcessingConfig.removeSetting(GPFUtils.BEAM_THREADS)

    def isActive(self):
        return ProcessingConfig.getSetting(self.activateSetting)

    def setActive(self, active):
        ProcessingConfig.setSettingValue(self.activateSetting, active)

    def createAlgsList(self):
        algs = []
        folder = GPFUtils.gpfDescriptionPath(GPFUtils.beamKey())
        for descriptionFile in os.listdir(folder):
            if descriptionFile.endswith("txt"):
                try:
                    alg = BEAMAlgorithm(os.path.join(folder, descriptionFile))
                    if alg.name().strip() != "":
                        algs.append(alg)
                    else:
                        QgsMessageLog.logMessage(
                                self.tr("Could not open BEAM algorithm: " + descriptionFile),
                                self.tr("Processing"),
                                Qgis.Critical)
                except Exception as e:
                    QgsMessageLog.logMessage(self.tr(str(e)), self.tr("Processing"), Qgis.Critical)
                    QgsMessageLog.logMessage(
                                self.tr("Could not open BEAM algorithm: " + descriptionFile),
                                self.tr("Processing"),
                                Qgis.Critical)
        return algs

    def longName(self):
        return "BEAM (Envisat image analysis)"

    def name(self):
        return "BEAM"

    def id(self):
        return "beam"

    def helpId(self):
        return "beam"

    def icon(self):
        return QIcon(os.path.dirname(__file__) + "/images/beam.png")

    def loadAlgorithms(self):
        self.algs = self.createAlgsList()
        for a in self.algs:
            self.addAlgorithm(a)

    def supportedOutputRasterLayerExtensions(self):
        return ["tif", "dim"]

    def supportsNonFileBasedOutput(self):
        return False

    def tr(self, string, context=''):
        if context == '':
            context = 'Grass7AlgorithmProvider'
        return QCoreApplication.translate(context, string)
