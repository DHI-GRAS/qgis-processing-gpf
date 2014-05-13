from processing.gui.ParametersPanel import ParametersPanel
from processing.gui.InputLayerSelectorPanel import InputLayerSelectorPanel
from processing.gui.NumberInputPanel import NumberInputPanel
from processing.tools import dataobjects 
from qgis.core import QgsRasterLayer 
from processing.parameters.ParameterRaster import ParameterRaster
from processing.parameters.ParameterNumber import ParameterNumber
from processing_gpf.GPFUtils import GPFUtils
from PyQt4 import QtGui, QtCore
import pyperclip

# BEAM parameters panel is the same as normal parameters panel except
# it has a button next to raster inputs to show band names
class BEAMParametersPanel(ParametersPanel):
    
    def getWidgetFromParameter(self, param):
        if isinstance(param, ParameterRaster):
            layers = dataobjects.getRasterLayers()
            items = []
            if (param.optional):
                items.append((self.NOT_SELECTED, None))
            for layer in layers:
                items.append((layer.name(), layer))
            item = BEAMInputLayerSelectorPanel(items, self.parent, self.alg.programKey, self.alg.multipleRasterInput)
        # special treatment for NEST Terrain-Correction to get pixel sizes from SAR image
        elif isinstance(param, ParameterNumber) and (param.name == "pixelSpacingInMeter" or param.name == "pixelSpacingInDegree") and self.alg.commandLineName() == "nest:terraincorrection":
            item = NESTPixelSizeInputPanel(param.default, param.isInteger, self.parent, self.alg.programKey)
        else:
            item = ParametersPanel.getWidgetFromParameter(self, param)
            
        return item

# Special functionality for NEST terrain-correction
# NEST pixel size input panel is the same as normal number
# input panel except that it has a button next to it
# to show selected products pixel size.     
class NESTPixelSizeInputPanel(NumberInputPanel):
    
    def __init__(self, default, isInteger, parent, programKey):
        self.parent = parent
        self.programKey = programKey
        NumberInputPanel.__init__(self, default, None, None, isInteger)
        self.metadataButton = QtGui.QPushButton()
        self.metadataButton.setText("Pixel Size")
        self.metadataButton.clicked.connect(self.showMetadataDialog)
        self.horizontalLayout.addWidget(self.metadataButton)

    def showMetadataDialog(self):
        sourceProduct = self.parent.paramTable.valueItems["sourceProduct"].getFilePath()
        pixelSizes = GPFUtils.getNESTPixelSize(sourceProduct, self.programKey)
        dlg = NESTPixelSizeInputDialog(pixelSizes, sourceProduct, self.parent)
        dlg.show()
        
# Simple dialog displaying SAR image pixel sizes           
class NESTPixelSizeInputDialog(QtGui.QDialog): 
    def __init__(self, pixelSizes, filename, parent):
        self.pixelSizes = pixelSizes
        self.filename = filename
        QtGui.QDialog.__init__(self, parent)
        self.setWindowModality(0)
        self.setupUi()
      
    def setupUi(self):
        self.resize(500, 180)
        self.setWindowTitle("Pixel Sizes: "+str(self.filename))
        self.verticalLayout = QtGui.QVBoxLayout(self)
        self.horizontalLayout = QtGui.QHBoxLayout(self)
        self.horizontalLayout.setSpacing(2)
        self.horizontalLayout.setMargin(0)
        self.table = QtGui.QTableWidget()
        self.table.setColumnCount(1)
        self.table.setColumnWidth(0,270)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setVisible(False)
        self.table.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        self.setTableContent()
        self.horizontalLayout.addWidget(self.table)
        self.setLayout(self.horizontalLayout)
        self.verticalLayout.addLayout(self.horizontalLayout)
       
    def setTableContent(self):
        self.table.setRowCount(len(self.pixelSizes))
        i=0
        for k,v in self.pixelSizes.items():
            item = QtGui.QLineEdit()
            item.setReadOnly(True)
            text = str(k).strip() + ":\t\t" + str(v).strip()
            item.setText(text)
            self.table.setCellWidget(i,0, item)
            i += 1     
    
# BEAM input layer selecor panel is the same as normal input layer
# selector panel except that it has a button next to it
# to show band names            
class BEAMInputLayerSelectorPanel(InputLayerSelectorPanel):
    
    def __init__(self, options, parent, programKey, appendProductName):
        self.parent = parent
        InputLayerSelectorPanel.__init__(self, options)
        self.bandsButton = QtGui.QPushButton()
        self.bandsButton.setText("Bands")
        self.bandsButton.clicked.connect(self.showBandsDialog)
        self.horizontalLayout.addWidget(self.bandsButton)
        self.appendProductName = appendProductName
        self.programKey = programKey
        
    def showBandsDialog(self):
        bands = GPFUtils.getBeamBandNames(self.getFilePath(), self.programKey, self.appendProductName)
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
            item.setText(self.bands[i])
            self.table.setCellWidget(i,0, item)
            QtCore.QObject.connect(item, QtCore.SIGNAL("stateChanged(int)"), self.updateBandList)
    
    
    def updateBandList(self):
        selectedBands = ""
        for i in range(len(self.bands)):
            widget = self.table.cellWidget(i, 0)
            if widget.isChecked(): 
                selectedBands+=widget.text()
                selectedBands+=","
        if selectedBands:
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