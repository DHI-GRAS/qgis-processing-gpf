import os
from qgis.core import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from xml.etree.ElementTree import Element, SubElement, Comment, tostring
from xml.dom import minidom
from sextante.core.GeoAlgorithm import GeoAlgorithm
from sextante.parameters.ParameterTable import ParameterTable
from sextante.parameters.ParameterNumber import ParameterNumber
from sextante.parameters.ParameterMultipleInput import ParameterMultipleInput
from sextante.parameters.ParameterRaster import ParameterRaster
from sextante.outputs.OutputRaster import OutputRaster
from sextante.parameters.ParameterVector import ParameterVector
from sextante.parameters.ParameterBoolean import ParameterBoolean
from sextante.parameters.ParameterSelection import ParameterSelection
from sextante.core.GeoAlgorithmExecutionException import GeoAlgorithmExecutionException
from sextante.core.SextanteLog import SextanteLog
from sextante.core.SextanteUtils import SextanteUtils
from sextante.core.QGisLayers import QGisLayers
from sextante.parameters.ParameterFactory import ParameterFactory
from sextante.outputs.OutputFactory import OutputFactory
from sextante_gpf.GPFUtils import GPFUtils
from sextante_gpf.BEAMParametersDialog import BEAMParametersDialog
from sextante.parameters.ParameterExtent import ParameterExtent
from sextante_gpf.GPFAlgorithm import GPFAlgorithm


class NESTAlgorithm(GPFAlgorithm):
        
    def processAlgorithm(self, progress):
        GPFAlgorithm.processAlgorithm(self, GPFUtils.nestKey(), progress)
        
    def helpFile(self):
        GPFAlgorithm.helpFile(self, GPFUtils.nestKey())
        
    def getIcon(self):
        return  QIcon(os.path.dirname(__file__) + "/images/nest.png")
    
    def getCopy(self):
        newone = NESTAlgorithm(self.descriptionFile)
        newone.provider = self.provider
        return newone
                
        