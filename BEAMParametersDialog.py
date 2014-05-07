from processing.gui.AlgorithmExecutionDialog import AlgorithmExecutionDialog
from processing.gui.ParametersDialog import ParametersDialog
from processing_gpf.BEAMParametersPanel import BEAMParametersPanel

# BEAM parameters dialog is the same as normal parameters dialog except
# it has a button next to raster inputs to show band names
class BEAMParametersDialog(ParametersDialog):
    def __init__(self, alg):
        self.paramTable = BEAMParametersPanel(self, alg)
        AlgorithmExecutionDialog.__init__(self, alg, self.paramTable)
        self.executed = False