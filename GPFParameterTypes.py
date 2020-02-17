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

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import QgsProcessingParameterType

from processing_gpf.GPFParameters import ParameterBandExpression


# TODO: resume work when integrating parameters into modeller
class ParameterBandExpressionType(QgsProcessingParameterType):

    def create(self, name):
        return ParameterBandExpression(name)

    def description(self):
        return QCoreApplication.translate("Processing",
                                          "A raster band expression parameter, for creating band "+
                                          "expressions using existing bands from a raster source.")

    def name(self):
        return QCoreApplication.translate("Processing", "Raster Band Expression")

    def id(self):
        return "GpfParameterBandExpression"

    def pythonImportString(self):
        return "from processing_gpf.GPFParameters import ParameterBandExpression"

    def className(self):
        return "ParameterBandExpression"

    def acceptedPythonTypes(self):
        return ["str"]

    def acceptedStringValues(self):
        return ["Band expression consisting of mathematical symbols and band names"]