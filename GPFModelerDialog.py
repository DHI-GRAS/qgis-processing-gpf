"""
***************************************************************************
    GPFModelerDialog.py
-------------------------------------
    Copyright (C) 2017 Radoslaw Guzinski

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

from builtins import str
import sys
from qgis.PyQt.QtCore import QDir, QUrl
from qgis.PyQt.QtWidgets import QMessageBox, QFileDialog
from qgis.core import Qgis, QgsApplication, QgsMessageLog
from processing.modeler.ModelerDialog import ModelerDialog
from processing_gpf.GPFModelerAlgorithm import GPFModelerAlgorithm
from processing_gpf.GPFUtils import GPFUtils


class GPFModelerDialog(ModelerDialog):

    def __init__(self, model=None):
        ModelerDialog.__init__(self, model)

        # Customise the GUI
        self.variables_dock.hide()
        self.algorithmTree.setFilterString("esa_snap")
        self.searchBox.hide()

        if model is None:
            self.model = GPFModelerAlgorithm()
            self.model.modelerdialog = self

    def openModel(self):
        filename, __ = QFileDialog.getOpenFileName(self,
                                                   self.tr('Open GPF Model'),
                                                   GPFUtils.modelsFolder(),
                                                   self.tr('GPF models (*.xml *.XML)'))
        if filename:
            self.loadModel(filename)

    def loadModel(self, filename):
        alg = GPFModelerAlgorithm()
        if alg.fromFile(filename):
            self.model = alg
            self.model.setProvider(QgsApplication.processingRegistry().providerById('esa_snap'))
            self.textGroup.setText(alg.group())
            self.textName.setText(alg.name())
            self.repaintModel()

            self.update_variables_gui()

            self.view.centerOn(0, 0)
            self.hasChanged = False

        else:
            QgsMessageLog.logMessage(self.tr('Could not load model {0}').format(filename),
                                     self.tr('Processing'),
                                     Qgis.Critical)
            QMessageBox.critical(self, self.tr('Open Model'),
                                 self.tr('The selected model could not be loaded.\n'
                                         'See the log for more information.'))

    def saveModel(self, saveAs):
        if not self.can_save():
            return
        self.model.setName(str(self.textName.text()))
        self.model.setGroup(str(self.textGroup.text()))
        if self.model.sourceFilePath() and not saveAs:
            filename = self.model.sourceFilePath()
        else:
            filename, filter = QFileDialog.getSaveFileName(self,
                                                           self.tr('Save GPF Model'),
                                                           GPFUtils.modelsFolder(),
                                                           self.tr('GPF models (*.xml)'))
            if filename:
                if not filename.endswith('.xml'):
                    filename += '.xml'
                self.model.setSourceFilePath(filename)
        if filename:
            if not self.model.toFile(filename):
                if saveAs:
                    QMessageBox.warning(self, self.tr('I/O error'),
                                        self.tr('Unable to save edits. Reason:\n {0}').format(str(sys.exc_info()[1])))
                else:
                    QMessageBox.warning(self, self.tr("Can't save model"),
                                        self.tr("This model can't be saved in its "
                                                "original location (probably you do not "
                                                "have permission to do it). Please, use "
                                                "the 'Save as...' option."))
                return
            self.update_model.emit()
            if saveAs:
                self.bar.pushMessage("", self.tr("GPF model was correctly saved to <a href=\"{}\">{}</a>").format(QUrl.fromLocalFile(filename).toString(), QDir.toNativeSeparators(filename)), level=Qgis.Success, duration=5)
            else:
                self.bar.pushMessage("", self.tr("GPF model was correctly saved"), level=Qgis.Success, duration=5)

            self.hasChanged = False
