import os
from PyQt4.QtGui import *
from processing.core.GeoAlgorithm import GeoAlgorithm
from processing_gpf.MultinodeGPFDialog import MultinodeGPFDialog

class MultinodeGPFCreator(GeoAlgorithm):
        def __init__(self):
            GeoAlgorithm.__init__(self)
            self.name="Create a multinode GPF"
            self.group="Miscellaneous"
            self.operator = "multiGPF"
            self.description = "Multinode GPF creator"

        def getCopy(self):
            newone = MultinodeGPFCreator()
            newone.provider = self.provider
            return newone

        def getIcon(self):
            return  QIcon(os.path.dirname(__file__) + "/../images/beam.png")

        def getCustomParametersDialog(self):
            dlg = MultinodeGPFDialog()
            return dlg
            