"""
***************************************************************************
    GPFParameters.py
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

import sys

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessingParameterBand,
                       QgsProcessingParameterDefinition,
                       QgsProcessingParameterRasterLayer)


def getParameterFromString(s, context=''):
    # Try the parameter definitions used in description files
    if '|' in s and (s.startswith("QgsProcessingParameter") or
                     s.startswith("*QgsProcessingParameter") or
                     s.startswith('Parameter') or
                     s.startswith('*Parameter')):
        isAdvanced = False
        if s.startswith("*"):
            s = s[1:]
            isAdvanced = True
        tokens = s.split("|")
        params = [t if str(t) != str(None) else None for t in tokens[1:]]

        try:
            clazz = getattr(sys.modules[__name__], tokens[0])
        except AttributeError:
            return None
        # convert to correct type
        if clazz == ParameterBandExpression or clazz == ParameterPolarisations:
            if len(params) > 4:
                params[4] = True if params[4].lower() == 'true' else False
            if len(params) > 5:
                params[5] = True if params[5].lower() == 'true' else False
        elif clazz == ParameterSnapRasterLayer:
            if len(params) > 3:
                params[3] = True if params[3].lower() == 'true' else False
        else:
            return None

        param = clazz(*params)
        if isAdvanced:
            param.setFlags(param.flags() | QgsProcessingParameterDefinition.FlagAdvanced)

        param.setDescription(QCoreApplication.translate(context, param.description()))

        return param
    else:
        return None


# ParameterBandExpression is exacly the same as ParameterBand except that it has a different
# parameter widget (see GPFParametersPanel)
class ParameterBandExpression(QgsProcessingParameterBand):

    def __init__(self, name='', description='', defaultValue='', parentLayerParameterName='',
                 optional=False, allowMultiple=False):
        QgsProcessingParameterBand.__init__(self, name, description, defaultValue,
                                            parentLayerParameterName, optional, allowMultiple)
        self.setCustomWidget()

    def setCustomWidget(self):
        self.setMetadata(
            {'widget_wrapper': {
                'class': 'processing_gpf.GPFParameterWidgets.GPFBandExpressionWidgetWrapper'}})

    def type(self):
        return ParameterBandExpression.parameterType()

    def checkValueIsAcceptable(self, value, context=None):
        return QgsProcessingParameterDefinition.checkValueIsAcceptable(self, value, context)

    @staticmethod
    def parameterType():
        return "GpfParameterBandExpression"


# ParameterPolarisations is exacly the same as ParameterBand except that it has a different
# parameter widget (see GPFParametersPanel)
class ParameterPolarisations(QgsProcessingParameterBand):

    def __init__(self, name='', description='', defaultValue='', parentLayerParameterName='',
                 optional=False, allowMultiple=False):
        QgsProcessingParameterBand.__init__(self, name, description, defaultValue,
                                            parentLayerParameterName, optional, allowMultiple)
        self.setCustomWidget()

    def setCustomWidget(self):
        self.setMetadata(
            {'widget_wrapper': {
                    'class': 'processing_gpf.GPFParameterWidgets.GPFPolarisationsWidgetWrapper'}})

    def type(self):
        ParameterPolarisations.parameterType()

    @staticmethod
    def parameterType():
        return "GpfParameterPolarisations"


# ParameterSnapRasterLayer is exactly the same as QgsProcessingParameterRasterLayer except that
# it avoids being loaded as QgsRasterLayer since SNAP can open some formats not supported by
# GDAL
class ParameterSnapRasterLayer(QgsProcessingParameterRasterLayer):

    def checkValueIsAcceptable(self, value, context=None):
        return QgsProcessingParameterDefinition.checkValueIsAcceptable(self, value, context)

    def valueAsPythonString(self, value, context):
        return QgsProcessingParameterDefinition.valueAsPythonString(self, value, context)
