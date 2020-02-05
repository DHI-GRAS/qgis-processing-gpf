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

import os

from qgis.PyQt import QtCore
from qgis.PyQt.QtWidgets import (QPushButton, QLineEdit, QWidget, QHBoxLayout, QVBoxLayout,
                                 QDialogButtonBox, QTableWidget, QHeaderView, QLabel, QApplication,
                                 QDialog, QCheckBox)
from qgis.core import (Qgis,
                       QgsProcessingParameters,
                       QgsMessageLog,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingUtils)
from qgis.gui import (QgsProcessingParameterWidgetFactoryInterface,
                      QgsAbstractProcessingParameterWidgetWrapper,
                      QgsDoubleSpinBox)
from processing.tools import dataobjects

from processing_gpf.GPFUtils import GPFUtils
from processing_gpf.GPFParameters import (ParameterBandExpression,
                                          ParameterPolarisations,
                                          ParameterPixelSize)
from processing.gui.wrappers import WidgetWrapper


# GPF band expression widget is the same as normal string widget except that it has a button next
# to it to show dialog with band names
class GPFBandExpressionWidgetWrapper(WidgetWrapper):

    def __init__(self, parameter, widgetType, row=0, col=0, **kwargs):
        self.programKey = GPFUtils.snapKey()
        self.appendProductName = False
        super().__init__(parameter, widgetType, row, col, **kwargs)
        self.context = dataobjects.createContext()

    def createWidget(self):
        self._expressionPanel = QLineEdit()
        self._expressionPanel.textChanged.connect(lambda: self.widgetValueHasChanged.emit(self))
        self._metadataButton = QPushButton()
        self._metadataButton.setMaximumWidth(75)
        self._metadataButton.setText("Bands")
        self._metadataButton.clicked.connect(lambda: self.showBandsDialog())
        horizontalLayout = QHBoxLayout()
        horizontalLayout.setSpacing(2)
        horizontalLayout.setMargin(0)
        horizontalLayout.addWidget(self._expressionPanel)
        horizontalLayout.addWidget(self._metadataButton)
        widget = QWidget()
        widget.setLayout(horizontalLayout)
        widget.setToolTip(self.parameterDefinition().toolTip())
        return widget

    def postInitialize(self, wrappers):
        self._parentWrapper = None
        for wrapper in wrappers:
            if wrapper.parameterDefinition().name() == self.parameterDefinition().parentLayerParameterName():
                self._parentWrapper = wrapper
        if self._parentWrapper is None:
            QgsMessageLog.logMessage(
                            self.tr("Parent layer parameter of %s does not exist" %
                                    self.parameterDefinition().name()),
                            self.tr("Processing"),
                            Qgis.Critical)

    def setValue(self, value):
        self._expressionPanel.setText(value)

    def value(self):
        return self._expressionPanel.text()
    
    def wrappedWidget(self):
        return self.widget

    def _sourceProduct(self):
        sourceProduct = ""
        layer = self._parentWrapper.parameterValue()
        if isinstance(layer, QgsProcessingParameterRasterLayer):
            sourceProduct, _ = layer.source.valueAsString(self.context.expressionContext())
        if isinstance(layer, str):
            if os.path.exists(layer):
                sourceProduct = layer
            else:
                sourceProduct = QgsProcessingUtils.mapLayerFromString(layer, self.context).source()
        return sourceProduct

    def showBandsDialog(self):
        sourceProduct = self._sourceProduct()
        bands = GPFUtils.getBeamBandNames(
            sourceProduct, self.programKey, self.appendProductName)
        dlg = GPFBandsListDialog(bands, sourceProduct, self)
        dlg.show()

    def parameterType(self):
        return ParameterBandExpression.parameterType()


# Same as GPFBandExpressionWidgetWrapper except for polarisations
class GPFPolarisationsWidgetWrapper(GPFBandExpressionWidgetWrapper):

    def createWidget(self):
        widget = super().createWidget()
        self._metadataButton.setText("Polarisations")
        return widget

    def showBandsDialog(self):
        sourceProduct = self._sourceProduct()
        bands = GPFUtils.getPolarisations(sourceProduct)
        dlg = GPFBandsListDialog(bands, sourceProduct, self)
        dlg.show()

    def parameterType(self):
        return ParameterPolarisations.parameterType()


class GPFBandsListDialog(QDialog):
    def __init__(self, bands, filename, parent):
        self.bands = bands
        self.selectedBands = []
        self.filename = filename
        QDialog.__init__(self, parent.wrappedWidget())
        self.parent = parent
        self.setWindowModality(0)
        self.setupUi()

    def setupUi(self):
        self.resize(381, 320)
        self.setWindowTitle("Band names: "+str(self.filename))
        self.verticalLayout = QVBoxLayout(self)
        self.horizontalLayout = QHBoxLayout(self)
        self.horizontalLayout.setSpacing(2)
        self.horizontalLayout.setMargin(0)
        self.buttonBox = QDialogButtonBox()
        self.buttonBox.setOrientation(QtCore.Qt.Vertical)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Close)
        self.selectAllButton = QPushButton()
        self.selectAllButton.setText("(de)Select all")
        self.buttonBox.addButton(self.selectAllButton, QDialogButtonBox.ActionRole)
        self.copyButton = QPushButton()
        self.copyButton.setText("Copy band names")
        self.buttonBox.addButton(self.copyButton, QDialogButtonBox.ActionRole)
        self.setButton = QPushButton()
        self.setButton.setText("Set band names")
        self.buttonBox.addButton(self.setButton, QDialogButtonBox.ActionRole)
        self.table = QTableWidget()
        self.table.setColumnCount(1)
        self.table.setColumnWidth(0, 270)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setVisible(False)
        self.table.horizontalHeader().setResizeMode(QHeaderView.Stretch)
        self.setTableContent()
        self.horizontalLayout.addWidget(self.table)
        self.horizontalLayout.addWidget(self.buttonBox)
        self.setLayout(self.horizontalLayout)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.label = QLabel("Selected bands:")
        self.verticalLayout.addWidget(self.label)
        self.bandList = QLineEdit()
        self.verticalLayout.addWidget(self.bandList)
        self.buttonBox.rejected.connect(self.close)
        self.selectAllButton.clicked.connect(self.selectAll)
        self.copyButton.clicked.connect(self.copyBands)
        self.setButton.clicked.connect(self.setBands)

    def setTableContent(self):
        self.table.setRowCount(len(self.bands))
        for i in range(len(self.bands)):
            item = QCheckBox()
            item.setText(self.bands[i])
            self.table.setCellWidget(i, 0, item)
            item.stateChanged.connect(self.updateBandList)

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
        clipboard = QApplication.clipboard()
        clipboard.setText(self.bandList.text())

    def setBands(self):
        self.parent.setValue(self.bandList.text())
        QDialog.close(self)

    def close(self):
        QDialog.close(self)


# Special functionality for S1 Toolbox terrain-correction
# S1 Toolbox pixel size input panel is the same as normal number
# input panel except that it has a button next to it
# to show selected products pixel size.
class GPFPixelSizeWidgetWrapper(GPFBandExpressionWidgetWrapper):

    def __init__(self, parameter, widgetType, row=0, col=0, **kwargs):
        super().__init__(parameter, widgetType, row, col, **kwargs)

    def createWidget(self):
        # Numeric spin box
        numberDef = self.parameterDefinition()
        self._spinBox = QgsDoubleSpinBox()
        self._spinBox.setExpressionsEnabled(False)
        self._spinBox.setDecimals(6)
        self._spinBox.setSingleStep(int((numberDef.maximum() - numberDef.minimum())/10.0))
        self._spinBox.setMaximum(numberDef.maximum())
        self._spinBox.setMinimum(numberDef.minimum())
        if numberDef.defaultValue() is not None:
            defaultValue = numberDef.defaultValue().toDouble()
            self._spinBox.setClearValue(defaultValue)
            self._spinBox.setValue(defaultValue)
        else:
            self._spinBox.setClearValue(numberDef.minimum())
        self._spinBox.valueChanged.connect(lambda: self.widgetValueHasChanged(self))
        # Button to bring up the pixel size dialog
        metadataButton = QPushButton()
        metadataButton.setMaximumWidth(75)
        metadataButton.setText("Pixel Size")
        metadataButton.clicked.connect(lambda: self.showPixelSizeDialog())
        # Overall layout
        horizontalLayout = QHBoxLayout()
        horizontalLayout.setSpacing(2)
        horizontalLayout.setMargin(0)
        horizontalLayout.addWidget(self._spinBox)
        horizontalLayout.addWidget(metadataButton)
        widget = QWidget()
        widget.setLayout(horizontalLayout)
        widget.setToolTip(self.parameterDefinition().toolTip())
        return widget

    def showPixelSizeDialog(self):
        sourceProduct = self._sourceProduct()
        pixelSizes = GPFUtils.getS1TbxPixelSize(sourceProduct)
        dlg = S1TbxPixelSizeInputDialog(pixelSizes, sourceProduct, self)
        dlg.show()

    def setValue(self, value):
        self._spinBox.setValue(value)

    def value(self):
        return self._spinBox.value()

    def parameterType(self):
        return ParameterPixelSize.parameterType()


# Simple dialog displaying SAR image pixel sizes
class S1TbxPixelSizeInputDialog(QDialog):
    def __init__(self, pixelSizes, filename, parent):
        self.pixelSizes = pixelSizes
        self.filename = filename
        QDialog.__init__(self, parent)
        self.setWindowModality(0)
        self.setupUi()

    def setupUi(self):
        self.resize(500, 180)
        self.setWindowTitle("Pixel Sizes: "+str(self.filename))
        self.verticalLayout = QVBoxLayout(self)
        self.horizontalLayout = QHBoxLayout(self)
        self.horizontalLayout.setSpacing(2)
        self.horizontalLayout.setMargin(0)
        self.table = QTableWidget()
        self.table.setColumnCount(1)
        self.table.setColumnWidth(0, 270)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setVisible(False)
        self.table.horizontalHeader().setResizeMode(QHeaderView.Stretch)
        self.setTableContent()
        self.horizontalLayout.addWidget(self.table)
        self.setLayout(self.horizontalLayout)
        self.verticalLayout.addLayout(self.horizontalLayout)

    def setTableContent(self):
        self.table.setRowCount(len(self.pixelSizes))
        i = 0
        for k, v in list(self.pixelSizes.items()):
            item = QLineEdit()
            item.setReadOnly(True)
            text = str(k).strip() + ":\t\t" + str(v).strip()
            item.setText(text)
            self.table.setCellWidget(i, 0, item)
            i += 1
