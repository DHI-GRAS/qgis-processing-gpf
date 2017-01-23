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
from processing.core.parameters import ParameterNumber, ParameterString

# Copied from processing.core.parameters
def getParameterFromString(s):
    barsub = '<barsub>'
    s = s.replace('\\|', barsub)
    tokens = s.split("|")
    tokens = [t.replace(barsub, '|') for t in tokens]
    params = [t if unicode(t) != "None" else None for t in tokens[1:]]
    clazz = getattr(sys.modules[__name__], tokens[0])
    return clazz(*params)

# ParameterBands is very similar to ParameterString except that it keeps the name
# of the ParameterRaster (in bandSourceRaster) whos bands should be selected in
# this parameter. It also has a different parameter panel (see GPFParametersPanel)
class ParameterBands(ParameterString):

    def __init__(self, name='', description='', default='', bandSourceRaster = '', optional=True):
        ParameterString.__init__(self, name, description, default, multiline=False, optional=optional)
        self._bandSourceRaster = bandSourceRaster

    # Band source raster is a property rather then variable because in GPF modeler it is possible
    # to treat it as ParameterString and then value of bandSourceRaster is not set in __init__.
    @property
    def bandSourceRaster(self):
        try:
            return self._bandSourceRaster
        except AttributeError:
            return None
    @bandSourceRaster.setter
    def bandSourceRaster(self, value):
        self._bandSourceRaster = value
            

# ParameterPolarisations is very similar to ParameterString except that it keeps the name
# of the ParameterRaster (in bandSourceRaster) whos polarisations should be selected in
# this parameter. It also has a different parameter panel (see GPFParametersPanel)
class ParameterPolarisations(ParameterBands):

    def __init__(self, name='', description='', default='', bandSourceRaster = '', optional=True):
        ParameterBands.__init__(self, name, description, default, bandSourceRaster, optional)

# ParameterPixelSize is exactly like parameter number except is has a
# different name since it requires different parameter panel (see GPFParametersPanel)
class ParameterPixelSize(ParameterNumber):

    def __init__(self, name='', description='', minValue=None, maxValue=None,
                 default=0.0):
        ParameterNumber.__init__(self, name, description, minValue, maxValue, default)
