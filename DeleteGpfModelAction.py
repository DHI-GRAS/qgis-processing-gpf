import os
from qgis.PyQt.QtWidgets import QMessageBox
from qgis.core import QgsApplication
from processing.gui.ContextAction import ContextAction
from processing_gpf.GPFModelerAlgorithm import GPFModelerAlgorithm


class DeleteGpfModelAction(ContextAction):

    def __init__(self):
        super().__init__()
        self.name = self.tr('Delete GPF Graph', 'DeleteGpfModelAction')

    def isEnabled(self):
        return isinstance(self.itemData, GPFModelerAlgorithm)

    def execute(self):
        reply = QMessageBox.question(
            None,
            self.tr('Confirmation', 'DeleteGpfModelAction'),
            self.tr('Are you sure you want to delete this graph?', 'DeleteGpfModelAction'),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No)
        if reply == QMessageBox.Yes:
            os.remove(self.itemData.sourceFilePath())
            QgsApplication.processingRegistry().providerById("esa_snap").refreshAlgorithms()
