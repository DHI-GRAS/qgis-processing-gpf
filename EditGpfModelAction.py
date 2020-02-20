from qgis.core import Qgis, QgsApplication
from qgis.PyQt.QtCore import QCoreApplication
from qgis.utils import iface
from processing.gui.ContextAction import ContextAction
from processing_gpf.GPFModelerAlgorithm import GPFModelerAlgorithm
from processing_gpf.GPFModelerDialog import GPFModelerDialog

class EditGpfModelAction(ContextAction):

    def __init__(self):
        super().__init__()
        self.name = self.tr('Edit GPF Graph', 'EditGpfModelAction')

    def isEnabled(self):
        return isinstance(self.itemData, GPFModelerAlgorithm) and self.itemData.provider().id() == "esa_snap"

    def execute(self):
        alg = self.itemData
        ok, msg = alg.canExecute()
        if not ok:
            iface.messageBar().pushMessage(QCoreApplication.translate('EditModelAction', 'Cannot edit GPF model: {}').format(msg), level=Qgis.Warning)
        else:
            dlg = GPFModelerDialog(alg)
            dlg.update_model.connect(self.updateModel)
            dlg.show()

    def updateModel(self):
        QgsApplication.processingRegistry().providerById('esa_snap').refreshAlgorithms()
