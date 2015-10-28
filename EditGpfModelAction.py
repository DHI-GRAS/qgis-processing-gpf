from processing.gui.ContextAction import ContextAction
from processing_gpf.GpfModelerAlgorithm import GpfModelerAlgorithm
from processing_gpf.GpfModelerDialog import GpfModelerDialog

class EditGpfModelAction(ContextAction):

    def __init__(self):
        self.name = self.tr('Edit GPF model', 'EditGpfModelAction')

    def isEnabled(self):
        return isinstance(self.alg, GpfModelerAlgorithm)

    def execute(self):
        dlg = GpfModelerDialog(self.alg.provider, self.alg.getCopy())
        dlg.exec_()
        if dlg.update:
            self.toolbox.updateProvider(self.alg.provider.getName())