from sextante.gui.ParametersPanel import ParametersPanel
from sextante.gui.InputLayerSelectorPanel import InputLayerSelectorPanel
from sextante.core.QGisLayers import QGisLayers
from qgis.core import QgsRasterLayer 
from sextante.parameters.ParameterRaster import ParameterRaster
from sextante_beam.BEAMUtils import BEAMUtils
from PyQt4 import QtGui, QtCore

# BEAM parameters panel is the same as normal parameters panel except
# it has a button next to raster inputs to show band names
class BEAMParametersPanel(ParametersPanel):
    
    def getWidgetFromParameter(self, param):
        if isinstance(param, ParameterRaster):
            layers = QGisLayers.getRasterLayers()
            items = []
            if (param.optional):
                items.append((self.NOT_SELECTED, None))
            for layer in layers:
                items.append((layer.name(), layer))
            item = BEAMInputLayerSelectorPanel(items)
        else:
            item = ParametersPanel.getWidgetFromParameter(self, param)
            
        return item
    
# BEAM input layer selecor panel is the same as normal input layer
# selector panel except that it has a button next to it
# to show band names            
class BEAMInputLayerSelectorPanel(InputLayerSelectorPanel):
    
    def __init__(self, options):
        InputLayerSelectorPanel.__init__(self, options)
        self.bandsButton = QtGui.QPushButton()
        self.bandsButton.setText("Bands")
        self.bandsButton.clicked.connect(self.showBandsDialog)
        self.horizontalLayout.addWidget(self.bandsButton)
        
    def showBandsDialog(self):
        bands = BEAMUtils.getBeamBandNames(self.getFilePath())
        dlg = BEAMBandsListDialog(bands, self.getFilePath())
        dlg.exec_()
        
    def getFilePath(self):
        obj = self.getValue()
        if isinstance(obj, QgsRasterLayer):
            value = unicode(obj.dataProvider().dataSourceUri())
        else:
            value = self.getValue()
        return value

# Simple dialog displaying a list of bands            
class BEAMBandsListDialog(QtGui.QDialog):
    def __init__(self, bands, filename):
        self.bands = bands
        self.filename = filename
        QtGui.QDialog.__init__(self)
        self.setWindowModality(1)
        self.setupUi()

    def setupUi(self):
        self.resize(381, 320)
        self.setWindowTitle("Band names: "+str(self.filename))
        self.horizontalLayout = QtGui.QHBoxLayout(self)
        self.horizontalLayout.setSpacing(2)
        self.horizontalLayout.setMargin(0)
        self.buttonBox = QtGui.QDialogButtonBox()
        self.buttonBox.setOrientation(QtCore.Qt.Vertical)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok)
        self.table = QtGui.QTableWidget()
        self.table.setColumnCount(1)
        self.table.setColumnWidth(0,270)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setVisible(False)
        self.table.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        self.setTableContent()
        self.horizontalLayout.addWidget(self.table)
        self.horizontalLayout.addWidget(self.buttonBox)
        self.setLayout(self.horizontalLayout)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), self.close)
        QtCore.QMetaObject.connectSlotsByName(self)
        
    def setTableContent(self):
        self.table.setRowCount(len(self.bands))
        for i in range(len(self.bands)):
            item = QtGui.QLineEdit()
            item.setText(self.bands[i])
            item.setReadOnly(True)
            self.table.setCellWidget(i,0, item)