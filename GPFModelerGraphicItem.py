"""
***************************************************************************
    GPFModelerGraphicItem.py
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

from processing.modeler.ModelerGraphicItem import ModelerGraphicItem
from processing.modeler.ModelerAlgorithm import ModelerParameter, Algorithm
from processing_gpf.GPFModelerParameterDefinitionDialog import GPFModelerParameterDefinitionDialog
from processing_gpf.GPFModelerParametersDialog import GPFModelerParametersDialog


class GPFModelerGraphicItem(ModelerGraphicItem):

    # Function editElement is exactly the same as in ModelerGraphicItem class from
    # QGIS 2.18.3 except that ModelerParameterDefinitionDialog is replaced by
    # GPFModelerParameterDefinitionDialog and ModelerParametersDialog is replaced
    # by GPFModelerParametersDialog
    def editElement(self):
        if isinstance(self.element, ModelerParameter):
            dlg = GPFModelerParameterDefinitionDialog(self.model,
                                                      param=self.element.param)
            dlg.exec_()
            if dlg.param is not None:
                self.model.updateParameter(dlg.param)
                self.element.param = dlg.param
                self.text = dlg.param.description
                self.update()
        elif isinstance(self.element, Algorithm):
            dlg = self.element.algorithm.getCustomModelerParametersDialog(self.model,
                                                                          self.element.name)
            if not dlg:
                dlg = GPFModelerParametersDialog(self.element.algorithm,
                                                 self.model,
                                                 self.element.name)
            dlg.exec_()
            if dlg.alg is not None:
                dlg.alg.name = self.element.name
                self.model.updateAlgorithm(dlg.alg)
                self.model.updateModelerView()
