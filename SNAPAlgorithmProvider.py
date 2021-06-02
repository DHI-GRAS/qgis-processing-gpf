from builtins import str
import os

from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.core import (Qgis,
                       QgsApplication,
                       QgsProcessingProvider,
                       QgsMessageLog,
                       QgsProcessingException)
from qgis.gui import QgsGui
from processing.core.ProcessingConfig import ProcessingConfig, Setting
from processing.gui.ProviderActions import (ProviderActions,
                                            ProviderContextMenuActions)
from processing_gpf.GPFUtils import GPFUtils
from processing_gpf.GPFModelerAlgorithm import GPFModelerAlgorithm
from processing_gpf.S1TbxAlgorithm import S1TbxAlgorithm
from processing_gpf.S2TbxAlgorithm import S2TbxAlgorithm
from processing_gpf.S3TbxAlgorithm import S3TbxAlgorithm
from processing_gpf.SNAPAlgorithm import SNAPAlgorithm
# Do not use GPF model addition or edit functionality until it has been fully ported to QGIS 3.x
# from processing_gpf.CreateNewGpfModelAction import CreateNewGpfModelAction
# from processing_gpf.EditGpfModelAction import EditGpfModelAction
# from processing_gpf.DeleteGpfModelAction import DeleteGpfModelAction
from processing_gpf.GPFParameterTypes import ParameterBandExpressionType
from processing_gpf.GPFParameterWidgets import GPFBandExpressionWidgetFactory


class SNAPAlgorithmProvider(QgsProcessingProvider):

    def __init__(self):
        QgsProcessingProvider.__init__(self)
        # self.actions = [CreateNewGpfModelAction()]
        # self.contextMenuActions = [EditGpfModelAction(), DeleteGpfModelAction()]
        self.activate = False
        self.algs = []
        self.models = []

    def load(self):
        ProcessingConfig.settingIcons[self.name()] = self.icon()
        ProcessingConfig.addSetting(Setting(self.name(),
                                            GPFUtils.SNAP_FOLDER,
                                            self.tr("SNAP install directory"),
                                            GPFUtils.programPath(GPFUtils.snapKey())))
        ProcessingConfig.addSetting(Setting(self.name(),
                                            GPFUtils.SNAP_THREADS,
                                            self.tr("Maximum number of parallel (native) threads"),
                                            4))
        ProcessingConfig.addSetting(Setting(self.name(),
                                            GPFUtils.GPF_MODELS_FOLDER,
                                            self.tr("GPF models' directory"),
                                            GPFUtils.modelsFolder()))
        ProcessingConfig.addSetting(Setting(self.name(),
                                            GPFUtils.S1TBX_ACTIVATE,
                                            self.tr("Activate Sentinel-1 toolbox"),
                                            False))
        ProcessingConfig.addSetting(Setting(self.name(),
                                            GPFUtils.S2TBX_ACTIVATE,
                                            self.tr("Activate Sentinel-2 toolbox"),
                                            False))
        ProcessingConfig.addSetting(Setting(self.name(),
                                            GPFUtils.S3TBX_ACTIVATE,
                                            self.tr("Activate Sentinel-3 toolbox"),
                                            False))
        # TODO: uncomment below when working on integrating GPF parameters into modeller
        #QgsApplication.processingRegistry().addParameterType(ParameterBandExpressionType())
        #QgsGui.processingGuiRegistry().addParameterWidgetFactory(GPFBandExpressionWidgetFactory())
        #ProviderActions.registerProviderActions(self, self.actions)
        #ProviderContextMenuActions.registerProviderContextMenuActions(self.contextMenuActions)
        ProcessingConfig.readSettings()
        # Load operators
        self.loadAlgorithms()

        return True

    def unload(self):
        ProcessingConfig.removeSetting(GPFUtils.SNAP_FOLDER)
        ProcessingConfig.removeSetting(GPFUtils.SNAP_THREADS)
        ProcessingConfig.removeSetting(GPFUtils.GPF_MODELS_FOLDER)
        ProcessingConfig.removeSetting(GPFUtils.S1TBX_ACTIVATE)
        ProcessingConfig.removeSetting(GPFUtils.S2TBX_ACTIVATE)
        ProcessingConfig.removeSetting(GPFUtils.S3TBX_ACTIVATE)
        # TODO: uncomment below when working on integrating GPF parameters into modeller
        #QgsApplication.processingRegistry().removeParameterType(ParameterBandExpressionType())
        #QgsGui.processingGuiRegistry().removeParameterWidgetFactory(GPFBandExpressionWidgetFactory())

    def createAlgsList(self, key, gpfAlgorithm):
        algs = []
        folder = GPFUtils.gpfDescriptionPath(key)
        for descriptionFile in os.listdir(folder):
            if descriptionFile.endswith("txt"):
                try:
                    alg = gpfAlgorithm(os.path.join(folder, descriptionFile))
                    if alg.name().strip() != "":
                        alg.setProvider(self)
                        algs.append(alg)
                    else:
                        QgsMessageLog.logMessage(
                                self.tr("Could not open " + key + " SNAP generic algorithm: " +
                                        descriptionFile),
                                self.tr("Processing"),
                                Qgis.Critical)
                except Exception as e:
                    QgsMessageLog.logMessage(self.tr(str(e)), self.tr("Processing"), Qgis.Critical)
                    QgsMessageLog.logMessage(
                            self.tr("Could not open " + key + " generic algorithm: " +
                                    descriptionFile),
                            self.tr("Processing"),
                            Qgis.Critical)
        return algs

    def loadGpfModels(self, folder=GPFUtils.modelsFolder()):
        self.models = []
        if not os.path.exists(folder):
            return
        for path, subdirs, files in os.walk(folder):
            for descriptionFile in files:
                if descriptionFile.endswith('xml'):
                    try:
                        fullpath = os.path.join(path, descriptionFile)
                        model = GPFModelerAlgorithm()
                        success = model.fromFile(fullpath)
                        if success:
                            model.setProvider(self)
                            self.models.append(model)
                        else:
                            QgsMessageLog.logMessage(
                                    self.tr('Could not load model %s', 'ModelerAlgorithmProvider')
                                            % descriptionFile,
                                    self.tr("Processing"),
                                    Qgis.Critical)
                    except ValueError as e:
                        QgsMessageLog.logMessage(
                                self.tr('Could not load model %s\n%s', 'ModelerAlgorithmProvider')
                                        % (descriptionFile, str(e)),
                                self.tr("Processing"),
                                Qgis.Critical)
        for m in self.models:
            self.addAlgorithm(m)
        if self.models:
            self.algorithmsLoaded.emit()

    def refreshAlgorithms(self):
        super().refreshAlgorithms()
        self.loadGpfModels()

    def longName(self):
        return "SNAP Toolbox (Sentinel Application Platform)"

    def name(self):
        return "SNAP"

    def id(self):
        return "esa_snap"

    def helpId(self):
        return "esa_snap"

    def icon(self):
        return QIcon(os.path.dirname(__file__) + "/images/snap.png")

    def getAlgorithmFromOperator(self, operatorName):
        for alg in self.algs:
            if alg.operator == operatorName:
                return alg
        return None

    def loadAlgorithms(self):
        self.algs = self.createAlgsList(GPFUtils.snapKey(), SNAPAlgorithm)
        if ProcessingConfig.getSetting(GPFUtils.S1TBX_ACTIVATE):
            self.algs.extend(self.createAlgsList(GPFUtils.s1tbxKey(), S1TbxAlgorithm))
        if ProcessingConfig.getSetting(GPFUtils.S2TBX_ACTIVATE):
            self.algs.extend(self.createAlgsList(GPFUtils.s2tbxKey(), S2TbxAlgorithm))
        if ProcessingConfig.getSetting(GPFUtils.S3TBX_ACTIVATE):
            self.algs.extend(self.createAlgsList(GPFUtils.s3tbxKey(), S3TbxAlgorithm))
        for a in self.algs:
            self.addAlgorithm(a)

    def supportedOutputRasterLayerExtensions(self):
        return ["tif", "dim", "hdr"]

    def supportsNonFileBasedOutput(self):
        return False

    def tr(self, string, context=''):
        if context == '':
            context = 'SnapProvider'
        return QCoreApplication.translate(context, string)
