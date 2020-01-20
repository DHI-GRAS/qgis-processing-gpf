from processing.modeler.CreateNewModelAction import CreateNewModelAction
from processing_gpf.GPFModelerDialog import GPFModelerDialog
from qgis.PyQt.QtGui import QIcon
import os


class CreateNewGpfModelAction(CreateNewModelAction):

    def __init__(self, gpfAlgorithmProvider):
        CreateNewModelAction.__init__(self)
        self.name = self.tr('GPF Graph Builder', 'CreateNewGpfModelAction')
        self.gpfAlgorithmProvider = gpfAlgorithmProvider

    def getIcon(self):
        return QIcon(os.path.dirname(__file__) + '/images/snap_graph.png')

    def execute(self):
        dlg = GPFModelerDialog(self.gpfAlgorithmProvider)
        dlg.exec_()
        if dlg.update:
            try:
                # QGIS 2.16 (and up?) Processing implementation
                from processing.core.alglist import algList
                algList.reloadProvider(self.gpfAlgorithmProvider.getName())
            except ImportError:
                # QGIS 2.14 Processing implementation
                self.toolbox.updateProvider(self.gpfAlgorithmProvider.getName())
