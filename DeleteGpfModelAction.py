import os
from PyQt4.QtGui import QMessageBox
from processing.gui.ContextAction import ContextAction
from processing_gpf.GPFModelerAlgorithm import GPFModelerAlgorithm


class DeleteGpfModelAction(ContextAction):

    def __init__(self):
        self.name = self.tr('Delete GPF Graph', 'DeleteGpfModelAction')

    def isEnabled(self):
        return isinstance(self.alg, GPFModelerAlgorithm)

    def execute(self):
        reply = QMessageBox.question(
            None,
            self.tr('Confirmation', 'DeleteGpfModelAction'),
            self.tr('Are you sure you want to delete this graph?', 'DeleteGpfModelAction'),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No)
        if reply == QMessageBox.Yes:
            os.remove(self.alg.descriptionFile)
            self.toolbox.updateProvider(self.alg.provider.getName())
