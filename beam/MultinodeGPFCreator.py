import os
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from sextante.gui.ToolboxAction import ToolboxAction
from sextante.core.QGisLayers import QGisLayers
from sextante.core.SextanteLog import SextanteLog
from sextante.gui.RectangleMapTool import RectangleMapTool
from sextante.core.SextanteConfig import SextanteConfig
from sextante.core.GeoAlgorithm import GeoAlgorithm
from sextante.beam.MultinodeGPFDialog import MultinodeGPFDialog

class MultinodeGPFCreator(GeoAlgorithm):
        def __init__(self):
            GeoAlgorithm.__init__(self)
            self.name="Create a multinode GPF"
            self.group="Miscellaneous"
            self.appkey = "multiGPF"
            self.cliName = "Multinode GPF creator"

        def getCopy(self):
            newone = MultinodeGPFCreator()
            newone.provider = self.provider
            return newone

        def getIcon(self):
            return  QIcon(os.path.dirname(__file__) + "/../images/beam.png")

        def getCustomParametersDialog(self):
            dlg = MultinodeGPFDialog()
            return dlg
            