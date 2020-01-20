from processing.gui.ContextAction import ContextAction
from processing_gpf.GPFModelerAlgorithm import GPFModelerAlgorithm
from processing_gpf.GPFModelerDialog import GPFModelerDialog


class EditGpfModelAction(ContextAction):

    def __init__(self):
        self.name = self.tr('Edit GPF Graph', 'EditGpfModelAction')

    # This is to make the plugin work both in QGIS 2.14 and 2.16.
    # In 2.16 Processing self.alg was changed to self.itemData.
    def setData(self, itemData, toolbox):
        ContextAction.setData(self, itemData, toolbox)
        self.alg = itemData

    def isEnabled(self):
        return isinstance(self.alg, GPFModelerAlgorithm)

    def execute(self):
        dlg = GPFModelerDialog(self.alg.provider, self.alg.getCopy())
        dlg.exec_()
        if dlg.update:
            try:
                # QGIS 2.16 (and up?) Processing implementation
                from processing.core.alglist import algList
                algList.reloadProvider(self.alg.provider.getName())
            except ImportError:
                # QGIS 2.14 Processing implementation
                self.toolbox.updateProvider(self.alg.provider.getName())
