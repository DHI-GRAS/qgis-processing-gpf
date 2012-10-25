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
from sextante_beam.BEAMUtils import BEAMUtils
from sextante.parameters.ParameterExtent import ParameterExtent

class BEAMAlgorithm(GeoAlgorithm):

    OUTPUT_EXTENT = "OUTPUT_EXTENT"

    NOVALUEINT = -99999
    NOVALUEDOUBLE = -99999.9

    # static nodeIDNum, increased everytime an algorithm is created
    nodeIDNum = 0;

    def __init__(self, descriptionfile):
        GeoAlgorithm.__init__(self)
        self.descriptionFile = descriptionfile
        self.defineCharacteristicsFromFile()
        self.nodeID = ""+self.appkey+"_"+str(BEAMAlgorithm.nodeIDNum)
        BEAMAlgorithm.nodeIDNum +=1
        self.numExportedLayers = 0
        self.sourceFiles = ""
        self.previousAlgInGraph = None
        
    def getCopy(self):
        newone = BEAMAlgorithm(self.descriptionFile)
        newone.provider = self.provider
        return newone

    def getIcon(self):
        return  QIcon(os.path.dirname(__file__) + "/images/beam.png")
    
    def helpFile(self):
        folder = BEAMUtils.beamDocPath()
        if str(folder).strip() != "":
            helpfile = os.path.join( str(folder), self.appkey + ".html" )
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
                elif line.startswith("*Parameter"):
                    param = ParameterFactory.getFromString(line[1:])
                    param.isAdvanced = True
                    self.addParameter(param)
                else:
                    self.addOutput(OutputFactory.getFromString(line))
                line = lines.readline().strip("\n").strip()
            except Exception,e:
                SextanteLog.addToLog(SextanteLog.LOG_ERROR, "Could not open BEAM algorithm: " + self.descriptionFile + "\n" + line)
                raise e
        lines.close()
    
    
    def addGPFNode(self, graph):
        
        # if there are previous nodes that should be added to the graph, recursively go backwards and add them
        if self.previousAlgInGraph != None:
            self.previousAlgInGraph.addGPFNode(graph)

        # now create and add the current node
        node = SubElement(graph, "node", {"id":self.nodeID})
        operator = SubElement(node, "operator")
        operator.text = self.appkey
        
        # sources are added in the parameters loop below
        sources = SubElement(node, "sources")
        
        parametersNode = SubElement(node, "parameters")
        
        for param in self.parameters:
            # ignore parameters which should have no value unless set by user 
            if param.value == None or param.value == "" or param.value == BEAMAlgorithm.NOVALUEINT or param.value == BEAMAlgorithm.NOVALUEDOUBLE:
                continue
            else:
                # add a source product
                if isinstance(param, ParameterRaster) and operator.text != "Read":
                    # if the source is a file, then add an external "source product" file
                    if os.path.isfile(param.value):
                        source = SubElement(sources, param.name)
                        source.text = "${"+param.name+"}"
                        self.sourceFiles = self.sourceFiles +"".join("-S"+param.name+"=\"" + param.value + "\" ")
                    # else assume its a reference to a previous node and add a "source" element
                    else:
                        source = SubElement(sources, param.name)
                        source.text = param.value   
                # add parameters
                else:
                    # Set the name of the parameter
                    # First check if there are nested tags
                    tagList = param.name.split(">")
                    parentElement = parametersNode
                    parameter = None
                    for tag in tagList:
                        # if this is the last tag or there are no nested tags create the parameter element
                        if tag == tagList[-1]:
                            # special treatment for geoRegionExtent parameter in Subset operator
                            if tag == "geoRegionExtent":
                                tag = "geoRegion"
                            # there can be only one parameter element in each parent element 
                            if len(parentElement.findall(tag)) > 0:
                                parameter = parentElement.findall(tag)[0]
                            else:
                                parameter = SubElement(parentElement, tag)
                        # "!" means that a new element in the graph should be created as child of the parent element and set as a parent    
                        elif tag.startswith("!"):
                            parentElement = SubElement(parentElement, tag[1:])
                        # otherwise just find the last element with required name and set it as parent of the parameter element
                        # or create a new one if it can't be found    
                        else:
                            if len(parentElement.findall(tag)) > 0:
                                parentElement = (parentElement.findall(tag))[-1]
                            else:
                                parentElement = SubElement(parentElement, tag)
                    
                    # Set the value of the parameter    
                    if isinstance(param, ParameterBoolean):
                        if param.value:
                            parameter.text = "True"
                        else:
                            parameter.text = "False"
                    elif isinstance(param, ParameterSelection):
                        idx = int(param.value)
                        parameter.text = str(param.options[idx])
                    # create at WKT polygon from the extent values, used in Subset Operator
                    elif isinstance(param, ParameterExtent):
                        values = param.value.split(",")
                        parameter.text = "POLYGON(("
                        parameter.text += values[0] + ' ' + values[2] +", "
                        parameter.text += values[0] + ' ' + values[3] +", "
                        parameter.text += values[1] + ' ' + values[3] +", "
                        parameter.text += values[1] + ' ' + values[2] +", "
                        parameter.text += values[0] + ' ' + values[2] +"))"
                    else:          
                        parameter.text = str(param.value)
        
        return graph
        
    def processAlgorithm(self, progress):
        # create a GFP for execution with BEAM's GPT
        graph = Element("graph", {'id':self.appkey+'_gpf'})
        version = SubElement(graph, "version")
        version.text = "1.0"
        
        # add node with this algorithm's operator
        graph = self.addGPFNode(graph)
        
        # log the GPF 
        loglines = []
        loglines.append("BEAM Graph")
        loglines.append(tostring(graph))
        loglines.append(self.sourceFiles)
        SextanteLog.addToLog(SextanteLog.LOG_INFO, loglines)
        
        # Execute the GPF
        # !!! should check that there is at least one output        
        BEAMUtils.executeBeam(tostring(graph), (self.outputs[0]).value, self.sourceFiles, progress)
                
        