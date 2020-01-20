"""
***************************************************************************
    GPFModelerParameterDefinitionDialog.py
-------------------------------------
    Copyright (C) 2017 Radoslaw Guzinski

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
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, QDialogButtonBox, QMessageBox
from processing.modeler.ModelerParameterDefinitionDialog import ModelerParameterDefinitionDialog
from processing.core.parameters import Parameter, ParameterRaster
from processing_gpf.GPFParameters import ParameterBands


class GPFModelerParameterDefinitionDialog(ModelerParameterDefinitionDialog):

    PARAMETER_BANDS = "Raster bands"

    paramTypes = ModelerParameterDefinitionDialog.paramTypes
    if PARAMETER_BANDS not in paramTypes:
        paramTypes.extend([PARAMETER_BANDS])

    def setupUi(self):
        if self.paramType == GPFModelerParameterDefinitionDialog.PARAMETER_BANDS or \
           isinstance(self.param, ParameterBands):

            self.setWindowTitle(self.tr('Parameter definition'))

            self.verticalLayout = QVBoxLayout(self)
            self.verticalLayout.setSpacing(40)
            self.verticalLayout.setMargin(20)

            self.horizontalLayoutName = QHBoxLayout(self)
            self.horizontalLayoutName.setSpacing(2)
            self.horizontalLayoutName.setMargin(0)
            self.label = QLabel(self.tr('Parameter name'))
            self.horizontalLayoutName.addWidget(self.label)
            self.nameTextBox = QLineEdit()
            self.horizontalLayoutName.addWidget(self.nameTextBox)
            self.verticalLayout.addLayout(self.horizontalLayoutName)

            self.horizontalLayoutRequired = QHBoxLayout(self)
            self.horizontalLayoutRequired.setSpacing(2)
            self.horizontalLayoutRequired.setMargin(0)
            self.horizontalLayoutParent = QHBoxLayout(self)
            self.horizontalLayoutParent.setSpacing(2)
            self.horizontalLayoutParent.setMargin(0)
            self.horizontalLayoutDefault = QHBoxLayout(self)
            self.horizontalLayoutDefault.setSpacing(2)
            self.horizontalLayoutDefault.setMargin(0)
            self.horizontalLayoutDatatype = QHBoxLayout(self)
            self.horizontalLayoutDatatype.setSpacing(2)
            self.horizontalLayoutDatatype.setMargin(0)

            if isinstance(self.param, Parameter):
                self.nameTextBox.setText(self.param.description)

            self.horizontalLayoutDefault.addWidget(QLabel(self.tr('Default band')))
            self.defaultTextBox = QLineEdit()
            if self.param is not None:
                self.defaultTextBox.setText(self.param.default)
            self.horizontalLayoutDefault.addWidget(self.defaultTextBox)
            self.verticalLayout.addLayout(self.horizontalLayoutDefault)
            self.horizontalLayoutDefault.addWidget(QLabel(self.tr('Raster layer')))
            self.parentCombo = QComboBox()
            idx = 0
            for param in list(self.alg.inputs.values()):
                if isinstance(param.param, (ParameterRaster)):
                    self.parentCombo.addItem(param.param.description, param.param.name)
                    if self.param is not None:
                        if self.param.bandSourceRaster == param.param.name:
                            self.parentCombo.setCurrentIndex(idx)
                    idx += 1
            self.horizontalLayoutDefault.addWidget(self.parentCombo)
            self.verticalLayout.addLayout(self.horizontalLayoutDefault)

            self.horizontalLayoutRequired.addWidget(QLabel(self.tr('Required')))
            self.yesNoCombo = QComboBox()
            self.yesNoCombo.addItem(self.tr('Yes'))
            self.yesNoCombo.addItem(self.tr('No'))
            self.horizontalLayoutRequired.addWidget(self.yesNoCombo)
            if self.param is not None:
                self.yesNoCombo.setCurrentIndex(
                    1 if self.param.optional else 0)
            self.verticalLayout.addLayout(self.horizontalLayoutRequired)

            self.buttonBox = QDialogButtonBox(self)
            self.buttonBox.setOrientation(Qt.Horizontal)
            self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel
                                              | QDialogButtonBox.Ok)
            self.buttonBox.setObjectName('buttonBox')
            self.buttonBox.accepted.connect(self.okPressed)
            self.buttonBox.rejected.connect(self.cancelPressed)

            self.verticalLayout.addWidget(self.buttonBox)

            self.setLayout(self.verticalLayout)

        else:
            ModelerParameterDefinitionDialog.setupUi(self)

    def okPressed(self):
        if self.paramType == GPFModelerParameterDefinitionDialog.PARAMETER_BANDS or \
           isinstance(self.param, ParameterBands):
            description = str(self.nameTextBox.text())
            if description.strip() == '':
                QMessageBox.warning(self, self.tr('Unable to define parameter'),
                                    self.tr('Invalid parameter name'))
                return
            if self.param is None:
                validChars = \
                    'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
                safeName = ''.join(c for c in description if c in validChars)
                name = safeName.lower()
                i = 2
                while name in self.alg.inputs:
                    name = safeName.lower() + str(i)
            else:
                name = self.param.name

            if self.parentCombo.currentIndex() < 0:
                QMessageBox.warning(self, self.tr('Unable to define parameter'),
                                    self.tr('Wrong or missing parameter values'))
                return

            raster = self.parentCombo.itemData(self.parentCombo.currentIndex())
            default = str(self.defaultTextBox.text())
            self.param = ParameterBands(name, description, default, raster, optional=False)

            self.param.optional = self.yesNoCombo.currentIndex() == 1
            self.close()

        else:
            ModelerParameterDefinitionDialog.okPressed(self)
