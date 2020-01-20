"""
***************************************************************************
    GPFModelerParametersDialog.py
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
from qgis.PyQt.QtWidgets import QComboBox
from processing.modeler.ModelerParametersDialog import ModelerParametersDialog
from processing_gpf.GPFParameters import ParameterBands


class GPFModelerParametersDialog(ModelerParametersDialog):

    def getWidgetFromParameter(self, param):
        if isinstance(param, ParameterBands):
            strings = self.getAvailableValuesOfType(ParameterBands)
            options = [(self.resolveValueDescription(s), s) for s in strings]
            item = QComboBox()
            item.setEditable(True)
            for desc, val in options:
                item.addItem(desc, val)
            item.setEditText(str(param.default or ""))
        else:
            item = ModelerParametersDialog.getWidgetFromParameter(self, param)

        return item
