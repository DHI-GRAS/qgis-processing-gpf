"""
***************************************************************************
    GPFParametersPanel.py
-------------------------------------
    Copyright (C) 2014 TIGER-NET (www.tiger-net.org)

***************************************************************************
* This plugin is part of the Water Observation Information System (WOIS)  *
* developed under the TIGER-NET project funded by the European Space      *
* Agency as part of the long-term TIGER initiative aiming at promoting    *
* the use of Earth Observation (EO) for improved Integrated Water         *
* Resources Management (IWRM) in Africa.                                  *
*                                                                         *
* WOIS is a free software i.e. you can redistribute it and/or modify      *
* it under the terms of the GNU General Public License as published       *
* by the Free Software Foundation, either version 3 of the License,       *
* or (at your option) any later version.                                  *
*                                                                         *
* WOIS is distributed in the hope that it will be useful, but WITHOUT ANY * 
* WARRANTY; without even the implied warranty of MERCHANTABILITY or       *
* FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License   *
* for more details.                                                       *
*                                                                         *
* You should have received a copy of the GNU General Public License along *
* with this program.  If not, see <http://www.gnu.org/licenses/>.         *
***************************************************************************
"""

from builtins import str
from builtins import range
from processing.gui.ParametersPanel import ParametersPanel
from processing_gpf.GPFUtils import GPFUtils
from processing_gpf.GPFParameters import ParameterBands, ParameterPolarisations, ParameterPixelSize
from qgis.PyQt import QtGui, QtCore

# GPF parameters panel is the same as normal parameters panel except
# it can also handle ParameterBands, ParameterPolarisations and
# ParameterPixelSize with special UI


class GPFParametersPanel(ParametersPanel):

    def getWidgetFromParameter(self, param):
        if isinstance(param, ParameterPolarisations):
            item = GPFPolarisationsSelectorPanel(
                param.default, self.parent, self.alg.programKey, param.bandSourceRaster, False)
        elif isinstance(param, ParameterBands):
            item = GPFBandsSelectorPanel(param.default, self.parent,
                                         self.alg.programKey, param.bandSourceRaster, False)
        # Special treatment for S1 Toolbox Terrain-Correction to get pixel sizes from SAR image
        elif isinstance(param, ParameterPixelSize):
            item = S1TbxPixelSizeInputPanel(
                param.default, param.isInteger, self.parent, self.alg.programKey)
        else:
            item = ParametersPanel.getWidgetFromParameter(self, param)
        return item


# Special functionality for S1 Toolbox terrain-correction
# S1 Toolbox pixel size input panel is the same as normal number
# input panel except that it has a button next to it
# to show selected products pixel size.
class S1TbxPixelSizeInputPanel(QtGui.QWidget):

    def __init__(self, default, isInteger, parent, programKey):
        QtGui.QWidget.__init__(self)
        self.parent = parent
        self.programKey = programKey
        self.numberPanel = QtGui.QLineEdit()
        self.numberPanel.setText(str(default))
        self.metadataButton = QtGui.QPushButton()
        self.metadataButton.setMaximumWidth(75)
        self.metadataButton.setText("Pixel Size")
        self.metadataButton.clicked.connect(self.showMetadataDialog)
        self.horizontalLayout = QtGui.QHBoxLayout(self)
        self.horizontalLayout.setSpacing(2)
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.addWidget(self.numberPanel)
        self.horizontalLayout.addWidget(self.metadataButton)

    def showMetadataDialog(self):
        sourceProduct = self.parent.getRasterParamPath("sourceProduct")
        pixelSizes = GPFUtils.getS1TbxPixelSize(sourceProduct, self.programKey)
        dlg = S1TbxPixelSizeInputDialog(pixelSizes, sourceProduct, self.parent)
        dlg.show()

    def getValue(self):
        return self.numberPanel.text()

    def text(self):
        return self.getValue()

# Simple dialog displaying SAR image pixel sizes


class S1TbxPixelSizeInputDialog(QtGui.QDialog):
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
        self.table.setColumnWidth(0, 270)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setVisible(False)
        self.table.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        self.setTableContent()
        self.horizontalLayout.addWidget(self.table)
        self.setLayout(self.horizontalLayout)
        self.verticalLayout.addLayout(self.horizontalLayout)

    def setTableContent(self):
        self.table.setRowCount(len(self.pixelSizes))
        i = 0
        for k, v in list(self.pixelSizes.items()):
            item = QtGui.QLineEdit()
            item.setReadOnly(True)
            text = str(k).strip() + ":\t\t" + str(v).strip()
            item.setText(text)
            self.table.setCellWidget(i, 0, item)
            i += 1

# GPF bands selector panel is the same as normal text panel
# except that it has a button next to it to show band names


class GPFBandsSelectorPanel(QtGui.QWidget):

    def __init__(self, default, parent, programKey, bandSourceRaster, appendProductName):
        QtGui.QWidget.__init__(self)
        self.parent = parent
        self.appendProductName = appendProductName
        self.bandSourceRaster = bandSourceRaster
        self.programKey = programKey
        self.bandsPanel = QtGui.QLineEdit()
        self.bandsPanel.setText(str(default))
        self.bandsButton = QtGui.QPushButton()
        self.bandsButton.setMaximumWidth(85)
        self.bandsButton.setText("Bands")
        self.bandsButton.clicked.connect(self.showBandsDialog)
        self.horizontalLayout = QtGui.QHBoxLayout(self)
        self.horizontalLayout.setSpacing(2)
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.addWidget(self.bandsPanel)
        self.horizontalLayout.addWidget(self.bandsButton)

    def setBandsPanel(self, bands):
        self.bandsPanel.setText(bands)

    def showBandsDialog(self):
        bands = GPFUtils.getBeamBandNames(
            self.getFilePath(), self.programKey, self.appendProductName)
        dlg = GPFBandsListDialog(bands, self.getFilePath(), self)
        dlg.show()

    def getFilePath(self):
        value = self.parent.getRasterParamPath(self.bandSourceRaster)
        return value

    def getValue(self):
        return self.bandsPanel.text()

    def text(self):
        return self.getValue()

# Simple dialog displaying a list of bands


class GPFBandsListDialog(QtGui.QDialog):
    def __init__(self, bands, filename, parent):
        self.bands = bands
        self.selectedBands = []
        self.filename = filename
        QtGui.QDialog.__init__(self, parent)
        self.parent = parent
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
        self.setButton = QtGui.QPushButton()
        self.setButton.setText("Set band names")
        self.buttonBox.addButton(self.setButton, QtGui.QDialogButtonBox.ActionRole)
        self.table = QtGui.QTableWidget()
        self.table.setColumnCount(1)
        self.table.setColumnWidth(0, 270)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setVisible(False)
        self.table.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        self.setTableContent()
        self.horizontalLayout.addWidget(self.table)
        self.horizontalLayout.addWidget(self.buttonBox)
        self.setLayout(self.horizontalLayout)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.label = QtGui.QLabel("Selected bands:")
        self.verticalLayout.addWidget(self.label)
        self.bandList = QtGui.QLineEdit()
        self.verticalLayout.addWidget(self.bandList)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), self.close)
        QtCore.QObject.connect(self.selectAllButton, QtCore.SIGNAL("clicked()"), self.selectAll)
        QtCore.QObject.connect(self.copyButton, QtCore.SIGNAL("clicked()"), self.copyBands)
        QtCore.QObject.connect(self.setButton, QtCore.SIGNAL("clicked()"), self.setBands)
        QtCore.QMetaObject.connectSlotsByName(self)

    def setTableContent(self):
        self.table.setRowCount(len(self.bands))
        for i in range(len(self.bands)):
            item = QtGui.QCheckBox()
            item.setText(self.bands[i])
            self.table.setCellWidget(i, 0, item)
            QtCore.QObject.connect(item, QtCore.SIGNAL("stateChanged(int)"), self.updateBandList)

    def updateBandList(self):
        selectedBands = ""
        for i in range(len(self.bands)):
            widget = self.table.cellWidget(i, 0)
            if widget.isChecked():
                selectedBands += widget.text()
                selectedBands += ","
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
        clipboard = QtGui.QApplication.clipboard()
        clipboard.setText(self.bandList.text())

    def setBands(self):
        self.parent.setBandsPanel(self.bandList.text())
        QtGui.QDialog.close(self)

    def close(self):
        QtGui.QDialog.close(self)


class GPFPolarisationsSelectorPanel(GPFBandsSelectorPanel):
    def __init__(self, default, parent, programKey, bandSourceRaster, appendProductName):
        super(GPFPolarisationsSelectorPanel, self).__init__(
            default, parent, programKey, bandSourceRaster, appendProductName)
        self.bandsButton.setText("Polarisations")

    def showBandsDialog(self):
        polarisations = GPFUtils.getPolarisations(self.getFilePath())
        dlg = GPFPolarisationsListDialog(polarisations, self.getFilePath(), self)
        dlg.show()


class GPFPolarisationsListDialog(GPFBandsListDialog):
    def setupUi(self):
        super(GPFPolarisationsListDialog, self).setupUi()
        self.setWindowTitle("Polarisations: "+str(self.filename))
        self.copyButton.setText("Copy polarisations")
        self.setButton.setText("Set polarisations")
        self.label.setText("Selected polarisations:")
