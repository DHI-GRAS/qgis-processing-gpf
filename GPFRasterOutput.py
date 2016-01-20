"""
***************************************************************************
    Output.py
    ---------------------
    Date                 : August 2012
    Copyright            : (C) 2012 by Victor Olaya
    Email                : volayaf at gmail dot com
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""


__author__ = 'Victor Olaya'
__date__ = 'August 2012'
__copyright__ = '(C) 2012, Victor Olaya'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import sys
from processing.core.outputs import OutputRaster
from processing.core.outputs import Output

def getOutputFromString(s):
    tokens = s.split("|")
    params = [t if unicode(t) != "None" else None for t in tokens[1:]]
    clazz = getattr(sys.modules[__name__], tokens[0])
    return clazz(*params)

class OutputRaster(Output):

    def getFileFilter(self, alg):
        exts = alg.provider.getSupportedOutputRasterLayerExtensions()
        for i in range(len(exts)):
            exts[i] = self.tr('%s files (*.%s)', 'OutputVector') % (exts[i].upper(), exts[i].lower())
        return ';;'.join(exts)
