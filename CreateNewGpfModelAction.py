import os
from qgis.PyQt.QtGui import QIcon

from qgis.core import QgsApplication
from processing.modeler.CreateNewModelAction import CreateNewModelAction
from processing_gpf.GPFModelerDialog import GPFModelerDialog


class CreateNewGpfModelAction(CreateNewModelAction):

    def __init__(self):
        CreateNewModelAction.__init__(self)
        self.name = self.tr('GPF Graph Builder', 'CreateNewGpfModelAction')

    def getIcon(self):
        return QIcon(os.path.dirname(__file__) + '/images/snap_graph.png')

    def execute(self):
        dlg = GPFModelerDialog()
        dlg.update_model.connect(self.updateModel)
        dlg.show()

    def updateModel(self):
        QgsApplication.processingRegistry().providerById('snap').refreshAlgorithms()
