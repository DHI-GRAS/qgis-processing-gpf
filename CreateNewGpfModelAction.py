from processing.modeler.CreateNewModelAction import CreateNewModelAction
from processing_gpf.GpfModelerDialog import GpfModelerDialog
from PyQt4.QtGui import QIcon
import os

class CreateNewGpfModelAction(CreateNewModelAction):
    
    def __init__(self, gpfAlgorithmProvider):
        CreateNewModelAction.__init__(self)
        self.name = self.tr('GPF Graph Builder', 'CreateNewGpfModelAction')
        self.gpfAlgorithmProvider = gpfAlgorithmProvider
    
    def getIcon(self):
        return QIcon(os.path.dirname(__file__) + '/images/snap_graph.png')
    
    def execute(self):
        dlg = GpfModelerDialog(self.gpfAlgorithmProvider)
        dlg.exec_()
        if dlg.update:
            self.toolbox.updateProvider(self.gpfAlgorithmProvider.getName())