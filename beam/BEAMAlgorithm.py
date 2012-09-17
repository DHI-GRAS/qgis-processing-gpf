import os
from qgis.core import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from xml.etree.ElementTree import Element, SubElement, Comment, tostring
from xml.dom import minidom
from sextante.core.GeoAlgorithm import GeoAlgorithm
from sextante.parameters.ParameterTable import ParameterTable
from sextante.parameters.ParameterMultipleInput import ParameterMultipleInput
from sextante.parameters.ParameterRaster import ParameterRaster
from sextante.outputs.OutputRaster import OutputRaster
from sextante.parameters.ParameterVector import ParameterVector
from sextante.parameters.ParameterBoolean import ParameterBoolean
from sextante.parameters.ParameterSelection import ParameterSelection
from sextante.core.GeoAlgorithmExecutionException import GeoAlgorithmExecutionException
from sextante.core.SextanteLog import SextanteLog
from sextante.core.SextanteUtils import SextanteUtils
from sextante.parameters.ParameterFactory import ParameterFactory
from sextante.outputs.OutputFactory import OutputFactory
from sextante.beam.BEAMUtils import BEAMUtils
from sextante.parameters.ParameterExtent import ParameterExtent

class BEAMAlgorithm(GeoAlgorithm):

    def __init__(self, descriptionfile):
        GeoAlgorithm.__init__(self)
        self.descriptionFile = descriptionfile
        self.defineCharacteristicsFromFile()
        self.numExportedLayers = 0
        
    def getCopy(self):
        newone = BEAMAlgorithm(self.descriptionFile)
        newone.provider = self.provider
        return newone

    def getIcon(self):
        return  QIcon(os.path.dirname(__file__) + "/../images/beam.png")
    
    def helpFile(self):
        folder = os.path.join( BEAMUtils.beamDescriptionPath(), 'doc' )
        if str(folder).strip() != "":
            helpfile = os.path.join( str(folder), self.appkey + ".html")
            return helpfile
        return None
    
    def defineCharacteristicsFromFile(self):
        lines = open(self.descriptionFile)
        line = lines.readline().strip("\n").strip()
        self.appkey = line
        line = lines.readline().strip("\n").strip()
        self.cliName = line
        line = lines.readline().strip("\n").strip()
        self.name = line
        line = lines.readline().strip("\n").strip()
        self.group = line
        while line != "":
            try:
                line = line.strip("\n").strip()
                if line.startswith("Parameter"):
                    param = ParameterFactory.getFromString(line)
                    self.addParameter(param)
                else:
                    self.addOutput(OutputFactory.getFromString(line))
                line = lines.readline().strip("\n").strip()
            except Exception,e:
                SextanteLog.addToLog(SextanteLog.LOG_ERROR, "Could not open BEAM algorithm: " + self.descriptionFile + "\n" + line)
                raise e
        lines.close()
        
    def processAlgorithm(self, progress):
        # create a GFP for execution with BEAM's GPT
        graph = Element("graph", {'id':self.appkey+'_gpf'})
        
        version = SubElement(graph, "version")
        version.text = "1.0"
        
        node = SubElement(graph, "node", {"id":self.appkey+'_node'})
        operator = SubElement(node, "operator")
        operator.text = self.appkey
        
        # !!!! source should come from the parameters
        sources = SubElement(node, "sources")
        
        parametersNode = SubElement(node, "parameters")
        for param in self.parameters:
            if param.value == None:
                continue
            else:
                # !!!! might have to have a list of parameters here and append to the end
                parameter = SubElement(parametersNode, param.name)
                parameter.text = param.value
        
        # log the GPF 
        loglines = []
        loglines.append("BEAM Graph")
        loglines.append(tostring(graph))
        SextanteLog.addToLog(SextanteLog.LOG_INFO, loglines)
        
        # Execute the GPF
        # !!! should check that there is at least one output        
        BEAMUtils.executeBeam(tostring(graph), (self.outputs[0]).value, progress)
                
        