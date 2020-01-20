from builtins import str
from builtins import range
import sys
from processing.core.outputs import OutputRaster

def getOutputFromString(s):
    tokens = s.split("|")
    params = [t if str(t) != "None" else None for t in tokens[1:]]
    clazz = getattr(sys.modules[__name__], tokens[0])
    return clazz(*params)

# This is the same as the original OutputRaster except that extensions come
# from the provider instead of dataobjects
class OutputRaster(OutputRaster):

    def getFileFilter(self, alg):
        exts = alg.provider.getSupportedOutputRasterLayerExtensions()
        for i in range(len(exts)):
            exts[i] = self.tr('%s files (*.%s)', 'OutputVector') % (exts[i].upper(), exts[i].lower())
        return ';;'.join(exts)
