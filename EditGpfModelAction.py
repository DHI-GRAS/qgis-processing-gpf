from processing.gui.ContextAction import ContextAction
from processing_gpf.GPFModelerAlgorithm import GPFModelerAlgorithm
from processing_gpf.GPFModelerDialog import GPFModelerDialog

class EditGpfModelAction(ContextAction):

    def __init__(self):
        self.name = self.tr('Edit GPF Graph', 'EditGpfModelAction')

    def isEnabled(self):
        return isinstance(self.alg, GPFModelerAlgorithm)

    def execute(self):
        dlg = GPFModelerDialog(self.alg.provider, self.alg.getCopy())
        dlg.exec_()
        if dlg.update:
            self.toolbox.updateProvider(self.alg.provider.getName())