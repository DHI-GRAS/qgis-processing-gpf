from processing.modeler.CreateNewModelAction import CreateNewModelAction
from processing_gpf.GpfModelerDialog import GpfModelerDialog

class CreateNewGpfModelAction(CreateNewModelAction):
    
    def __init__(self, gpfAlgorithmProvider):
        CreateNewModelAction.__init__(self)
        self.gpfAlgorithmProvider = gpfAlgorithmProvider
    
    def execute(self):
        dlg = GpfModelerDialog(self.gpfAlgorithmProvider)
        dlg.exec_()
        if dlg.update:
            self.toolbox.updateProvider(self.gpfAlgorithmProvider.getName())