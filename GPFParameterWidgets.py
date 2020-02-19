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
                                 QDialog, QCheckBox, QComboBox)
from qgis.core import (Qgis,
                       QgsMessageLog,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingUtils)
from qgis.gui import (QgsProcessingParameterWidgetFactoryInterface,
                      QgsProcessingGui)
from processing.tools import dataobjects

from processing_gpf.GPFUtils import GPFUtils
from processing_gpf.GPFParameters import ParameterBandExpression, ParameterPolarisations
from processing.gui.wrappers import WidgetWrapper


# TODO: Resume work when integrating GPF parameters into modeller
class GPFBandExpressionWidgetFactory(QgsProcessingParameterWidgetFactoryInterface):

    def parameterType(self):
        return ParameterBandExpression.parameterType()

    def createWidgetWrapper(self, parameter, widgetType):
        return GPFBandExpressionWidgetWrapper(parameter, widgetType)

    def createModelerWidgetWrapper(self, model, childId, parameter, context):
        return GPFBandExpressionWidgetWrapper(parameter, QgsProcessingGui.Modeler)

    def createParameterDefinitionWidget(self, context, widgetContext, definition, algorithm):
        return GPFBandExpressionParameterDefinitionWidget(context, widgetContext, definition,
                                                          algorithm)


# GPF band expression widget is the same as normal string widget except that it has a button next
# to it to show dialog with band names
class GPFBandExpressionWidgetWrapper(WidgetWrapper):

    def __init__(self, parameter, widgetType, row=0, col=0, **kwargs):
        self.programKey = GPFUtils.snapKey()
        self.appendProductName = False
        super().__init__(parameter, widgetType, row, col, **kwargs)
        self.context = dataobjects.createContext()
        self._parentWrapper = None

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
        if self._parentWrapper is None:
            return sourceProduct
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


# TODO: Resume work when integrating GPF parameters into modeller
class GPFBandExpressionParameterDefinitionWidget():

    def __init__(self, context, widgetContext, definition, algorithm, parent=None):
        super().__init__(context, widgetContext, definition, algorithm, parent)
        verticalLayout = QVBoxLayout()
        verticalLayout.setMargin(0)
        verticalLayout.setContentsMargins(0, 0, 0, 0)
        verticalLayout.addWidget(QLabel(self.tr('Default Value')))
        self.defaultLineEdit = QLineEdit()
        self.defaultLineEdit.setText(definition.defaultValue())
        verticalLayout.addWidget(self.defaultLineEdit)
        verticalLayout.addWidget(QLabel(self.tr('Parent layer')))
        self.parentCombo = QComboBox()
        idx = 0
        for param in list(algorithm.parameterComponents().values()):
            paramDef = algorithm.parameterDefinition(param.parameterName())
            if isinstance(paramDef, (QgsProcessingParameterRasterLayer)):
                self.parentCombo.addItem(paramDef.description(), paramDef.name())
                if param is not None:
                    if definition.parentLayerParameterName() == paramDef.name():
                        self.parentCombo.setCurrentIndex(idx)
                idx += 1
        verticalLayout.addWidget(self.parentCombo)
        self.setLayout(verticalLayout)

    def createParameter(self, name, description, flags):
        defaultValue = self.defaultLineEdit.text()
        parentLayerParameterName = self.parentCombo.currentText()
        param = ParameterBandExpression(name, description, defaultValue, parentLayerParameterName)
        param.setFlags(flags)
        return param


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
