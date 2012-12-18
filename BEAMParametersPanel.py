from sextante.gui.ParametersPanel import ParametersPanel
from sextante.gui.InputLayerSelectorPanel import InputLayerSelectorPanel
from sextante.core.QGisLayers import QGisLayers
from qgis.core import QgsRasterLayer 
from sextante.parameters.ParameterRaster import ParameterRaster
from sextante_beam.BEAMUtils import BEAMUtils
from PyQt4 import QtGui, QtCore
import pyperclip

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
            item = BEAMInputLayerSelectorPanel(items, self.parent)
        else:
            item = ParametersPanel.getWidgetFromParameter(self, param)
            
        return item
    
# BEAM input layer selecor panel is the same as normal input layer
# selector panel except that it has a button next to it
# to show band names            
class BEAMInputLayerSelectorPanel(InputLayerSelectorPanel):
    
    def __init__(self, options, parent):
        self.parent = parent
        InputLayerSelectorPanel.__init__(self, options)
        self.bandsButton = QtGui.QPushButton()
        self.bandsButton.setText("Bands")
        self.bandsButton.clicked.connect(self.showBandsDialog)
        self.horizontalLayout.addWidget(self.bandsButton)
        
    def showBandsDialog(self):
        bands = BEAMUtils.getBeamBandNames(self.getFilePath())
        dlg = BEAMBandsListDialog(bands, self.getFilePath(), self.parent)
        dlg.show()
        
    def getFilePath(self):
        obj = self.getValue()
        if isinstance(obj, QgsRasterLayer):
            value = unicode(obj.dataProvider().dataSourceUri())
        else:
            value = self.getValue()
        return value

# Simple dialog displaying a list of bands            
class BEAMBandsListDialog(QtGui.QDialog):
    def __init__(self, bands, filename, parent):
        self.bands = bands
        self.selectedBands = []
        self.filename = filename
        QtGui.QDialog.__init__(self, parent)
        self.setWindowModality(0)
        self.setupUi()

    def setupUi(self):
        self.resize(381, 320)
        self.setWindowTitle("Band names: "+str(self.filename))
        self.verticalLayout = QtGui.QVBoxLayout(self)
        self.horizontalLayout = QtGui.QHBoxLayout(self)
        self.horizontalLayout.setSpacing(2)
        self.horizontalLayout.setMargin(0)
        self.buttonBox = QtGui.QDialogButtonBox()
        self.buttonBox.setOrientation(QtCore.Qt.Vertical)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Close)
        self.selectAllButton = QtGui.QPushButton()
        self.selectAllButton.setText("(de)Select all")
        self.buttonBox.addButton(self.selectAllButton, QtGui.QDialogButtonBox.ActionRole)
        self.copyButton = QtGui.QPushButton()
        self.copyButton.setText("Copy band names")
        self.buttonBox.addButton(self.copyButton, QtGui.QDialogButtonBox.ActionRole)
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
        self.verticalLayout.addLayout(self.horizontalLayout)
        label = QtGui.QLabel("Selected bands:")
        self.verticalLayout.addWidget(label)
        self.bandList = QtGui.QLineEdit()
        self.verticalLayout.addWidget(self.bandList)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), self.close)
        QtCore.QObject.connect(self.selectAllButton, QtCore.SIGNAL("clicked()"), self.selectAll)
        QtCore.QObject.connect(self.copyButton, QtCore.SIGNAL("clicked()"), self.copyBands)
        QtCore.QMetaObject.connectSlotsByName(self)
        
    def setTableContent(self):
        self.table.setRowCount(len(self.bands))
        for i in range(len(self.bands)):
            item = QtGui.QCheckBox()
            item.setText(QtCore.QString(self.bands[i]).simplified())
            self.table.setCellWidget(i,0, item)
            QtCore.QObject.connect(item, QtCore.SIGNAL("stateChanged(int)"), self.updateBandList)
    
    
    def updateBandList(self):
        selectedBands = ""
        for i in range(len(self.bands)):
            widget = self.table.cellWidget(i, 0)
            if widget.isChecked(): 
                selectedBands+=widget.text()
                selectedBands+=","
        if selectedBands[-1] == ",":
            selectedBands = selectedBands[:-1]
        self.bandList.setText(selectedBands)
            
    def selectAll(self):
        checked = False
        for i in range(len(self.bands)):
            widget = self.table.cellWidget(i, 0)
            if not widget.isChecked():
                checked = True
                break
        for i in range(len(self.bands)):
            widget = self.table.cellWidget(i, 0)
            widget.setChecked(checked)
            
    def copyBands(self):
        pyperclip.copy(self.bandList.text())
        
    def close(self):
        self.copyBands()
        QtGui.QDialog.close(self)