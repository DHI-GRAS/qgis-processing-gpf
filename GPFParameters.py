import sys
from processing.core.parameters import ParameterNumber, ParameterString

# Copied from processing.core.parameters
def getParameterFromString(s):
    tokens = s.split("|")
    params = [t if unicode(t) != "None" else None for t in tokens[1:]]
    clazz = getattr(sys.modules[__name__], tokens[0])
    return clazz(*params)

# ParameterBands is very similar to ParameterString except that it keeps the name
# of the ParameterRaster (in bandSourceRaster) whos bands should be selected in
# this parameter. It also has a different parameter panel (see GPFParametersPanel)
class ParameterBands(ParameterString):
    
    def __init__(self, name='', description='', default='', bandSourceRaster = '', optional = True):
        ParameterString.__init__(self, name, description, default, multiline=False, optional=optional)
        self.bandSourceRaster = bandSourceRaster

# ParameterPixelSize is exactly like parameter number except is has a 
# different name since it requires different parameter panel (see GPFParametersPanel)   
class ParameterPixelSize(ParameterNumber):
    
    def __init__(self, name='', description='', minValue=None, maxValue=None,
                 default=0.0):
        ParameterNumber.__init__(self, name, description, minValue, maxValue, default)     