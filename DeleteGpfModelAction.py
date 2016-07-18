import os
from PyQt4.QtGui import QMessageBox
from processing.gui.ContextAction import ContextAction
from processing_gpf.GPFModelerAlgorithm import GPFModelerAlgorithm


class DeleteGpfModelAction(ContextAction):

    def __init__(self):   
        self.name = self.tr('Delete GPF Graph', 'DeleteGpfModelAction')
    
    # This is to make the plugin work both in QGIS 2.14 and 2.16. 
    # In 2.16 Processing self.alg was changed to self.itemData.
    def setData(self, itemData, toolbox):
        ContextAction.setData(self, itemData, toolbox)
        self.alg = itemData
    
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
            try:
                # QGIS 2.16 (and up?) Processing implementation
                from processing.core.alglist import algList
                algList.reloadProvider(self.alg.provider.getName())
            except ImportError:
                # QGIS 2.14 Processing implementation
                self.toolbox.updateProvider(self.alg.provider.getName())
                