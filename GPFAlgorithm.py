"""
***************************************************************************
    GPFAlgorithm.py
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

import os
import re
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
from processing.core.GeoAlgorithm import GeoAlgorithm
try:
    from processing.parameters.ParameterRaster import ParameterRaster
except:
    from processing.core.parameters import ParameterRaster
try:	
    from processing.parameters.ParameterBoolean import ParameterBoolean
except:
    from processing.core.parameters import ParameterBoolean
try:
    from processing.parameters.ParameterSelection import ParameterSelection
except:
    from processing.core.parameters import ParameterSelection
try:
    from processing.parameters.ParameterExtent import ParameterExtent
except:
    from processing.core.parameters import ParameterExtent
try:
    from processing.parameters.ParameterFactory import ParameterFactory
    getParameterFromString = ParameterFactory.getFromString 
except:
    from processing.core.parameters import getParameterFromString
try:
    from processing.outputs.OutputFactory import OutputFactory
    getOutputFromString = OutputFactory.getFromString
except:
    from processing.core.outputs import getOutputFromString
from processing.core.ProcessingLog import ProcessingLog
from processing_gpf.GPFUtils import GPFUtils
from processing_gpf.BEAMParametersDialog import BEAMParametersDialog


class GPFAlgorithm(GeoAlgorithm):

    OUTPUT_EXTENT = "OUTPUT_EXTENT"

    NOVALUEINT = 99999
    NOVALUEDOUBLE = 99999.9

    # static nodeIDNum, increased everytime an algorithm is created
    nodeIDNum = 0;

    def __init__(self, descriptionfile):
        GeoAlgorithm.__init__(self)
        self.multipleRasterInput = False
        self.descriptionFile = descriptionfile
        self.defineCharacteristicsFromFile()
        self.nodeID = ""+self.operator+"_"+str(GPFAlgorithm.nodeIDNum)
        GPFAlgorithm.nodeIDNum +=1
        self.sourceFiles = ""
        self.previousAlgInGraph = None
        
    def helpFile(self, key):
        folder = GPFUtils.gpfDocPath(key)
        if str(folder).strip() != "":
            helpfile = os.path.join( str(folder), self.operator + ".html" )
            return helpfile
        return None
    
    # BEAM parameters dialog is the same as normal parameters dialog except
    # it has a button next to raster inputs to show band names
    # For now S1Tbx uses the same dialog, maybe later that might have to change
    # if BEAM can't read band name from S1Tbx images.
    def getCustomParametersDialog(self):
        return BEAMParametersDialog(self)
    
    def defineCharacteristicsFromFile(self):
        lines = open(self.descriptionFile)
        line = lines.readline().strip("\n").strip()
        self.operator = line
        line = lines.readline().strip("\n").strip()
        self.description = line
        line = lines.readline().strip("\n").strip()
        self.name = line
        line = lines.readline().strip("\n").strip()
        self.group = line
        line = lines.readline().strip("\n").strip()
        while line != "":
            try:
                if line.startswith("Parameter"):
                    param = getParameterFromString(line)
                    self.addParameter(param)
                elif line.startswith("*Parameter"):
                    param = getParameterFromString(line[1:])
                    param.isAdvanced = True
                    self.addParameter(param)
                else:
                    self.addOutput(getOutputFromString(line))
                line = lines.readline().strip("\n").strip()
            except Exception,e:
                ProcessingLog.addToLog(ProcessingLog.LOG_ERROR, "Could not open GPF algorithm: " + self.descriptionFile + "\n" + line)
                raise e
        lines.close()
    
    def addGPFNode(self, graph):
        # if there are previous nodes that should be added to the graph, recursively go backwards and add them
        if self.previousAlgInGraph != None:
            self.previousAlgInGraph.addGPFNode(graph)

        # now create and add the current node
        node = ET.Element("node", {"id":self.nodeID})
        operator = ET.SubElement(node, "operator")
        operator.text = self.operator
        
        # sources are added in the parameters loop below
        sources = ET.SubElement(node, "sources")
        
        parametersNode = ET.SubElement(node, "parameters")
        
        for param in self.parameters:
            # ignore parameters which should have no value unless set by user 
            if param.value == None or param.value == GPFAlgorithm.NOVALUEINT or param.value == GPFAlgorithm.NOVALUEDOUBLE:
                continue
            else:
                # add a source product
                if isinstance(param, ParameterRaster) and operator.text != "Read":
                    # if the source is a file, then add an external "source product" file
                    if os.path.isfile(param.value):
                        # check if the file should be added individually or through the
                        # ProductSet-Reader used sometimes by S1 Toolbox
                        match = re.match("^\d*ProductSet-Reader>(.*)",param.name)
                        if match:
                            paramName = match.group(1)
                            sourceNodeId = self.addProductSetReaderNode(graph, param.value)
                        else:
                            paramName = param.name
                            sourceNodeId = self.addReadNode(graph, param.value)
                        if sources.find(paramName) == None:
                            source = ET.SubElement(sources, paramName)
                            source.set("refid",sourceNodeId)
                    # else assume its a reference to a previous node and add a "source" element
                    else:
                        source = ET.SubElement(sources, param.name, {"refid":param.value}) 
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
                                parameter = ET.SubElement(parentElement, tag)
                        # "!" means that a new element in the graph should be created as child of the parent element and set as a parent    
                        elif tag.startswith("!"):
                            parentElement = ET.SubElement(parentElement, tag[1:])
                        # otherwise just find the last element with required name and set it as parent of the parameter element
                        # or create a new one if it can't be found    
                        else:
                            if len(parentElement.findall(tag)) > 0:
                                parentElement = (parentElement.findall(tag))[-1]
                            else:
                                parentElement = ET.SubElement(parentElement, tag)
                    
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
                        if len(values) == 4:
                            parameter.text = "POLYGON(("
                            parameter.text += values[0] + ' ' + values[2] +", "
                            parameter.text += values[0] + ' ' + values[3] +", "
                            parameter.text += values[1] + ' ' + values[3] +", "
                            parameter.text += values[1] + ' ' + values[2] +", "
                            parameter.text += values[0] + ' ' + values[2] +"))"
                    else:          
                        parameter.text = str(param.value)
        
        graph.append(node)
        return graph
        
    def addProductSetReaderNode(self, graph, filename):
        nodeID = self.nodeID+"_ProductSet-Reader"
        node = graph.find(".//*[@id='"+nodeID+"']")
        
        # add ProductSet-Reader node if it doesn't exist yet   
        if node == None:
            node = ET.SubElement(graph, "node", {"id":nodeID})
            ET.SubElement(node, "sources")
            operator = ET.SubElement(node, "operator")
            operator.text = "ProductSet-Reader"
            # add the file list
            parametersNode = ET.SubElement(node, "parameters")
            parameter = ET.SubElement(parametersNode, "fileList")
            parameter.text=filename
        # otherwise append filename to the node's fileList
        else:
            parameter = node.find(".//fileList")
            parameter.text +=","+filename
        return nodeID
    
    def addReadNode(self, graph, filename):
        # Add read node
        nodeID = self.nodeID+"_read_"+str(GPFAlgorithm.nodeIDNum)
        GPFAlgorithm.nodeIDNum +=1
        node = ET.SubElement(graph, "node", {"id":nodeID})
        operator = ET.SubElement(node, "operator")
        operator.text = "Read"
        
        # Add empty source
        ET.SubElement(node, "sources")
        
        # Add file parameter with input file path
        parametersNode = ET.SubElement(node, "parameters")
        fileParameter = ET.SubElement(parametersNode, "file")
        fileParameter.text = filename
        
        return nodeID
          
    def addWriteNode(self, graph, key):
        # add write node
        nodeID = self.nodeID+"_write_"+str(GPFAlgorithm.nodeIDNum)
        GPFAlgorithm.nodeIDNum +=1
        node = ET.SubElement(graph, "node", {"id":nodeID})
        operator = ET.SubElement(node, "operator")
        operator.text = "Write"
        
        # add source
        sources = ET.SubElement(node, "sources")
        ET.SubElement(sources, "source", {"refid":self.nodeID})
    
        # add some options
        parametersNode = ET.SubElement(node, "parameters")
        parameter = ET.SubElement(parametersNode, "file")
        parameter.text = str((self.outputs[0]).value)
        parameter = ET.SubElement(parametersNode, "formatName")
        if (self.outputs[0]).value.lower().endswith(".dim"):
            parameter.text = "BEAM-DIMAP"
        else:
            if key == GPFUtils.beamKey():
                parameter.text = "GeoTIFF"
            else:
                parameter.text = "GeoTIFF-BigTIFF"
        return graph
    
    def processAlgorithm(self, key, progress):
        # create a GFP for execution with BEAM's GPT
        graph = ET.Element("graph", {'id':self.operator+'_gpf'})
        version = ET.SubElement(graph, "version")
        version.text = "1.0"
        
        # add node with this algorithm's operator
        graph = self.addGPFNode(graph)
        graph = self.addWriteNode(graph, key)
        
        # log the GPF 
        loglines = []
        loglines.append("GPF Graph")
        loglines.append(ET.tostring(graph))
        loglines.append(self.sourceFiles)
        ProcessingLog.addToLog(ProcessingLog.LOG_INFO, loglines)
        
        # Execute the GPF
        # !!! should check that there is at least one output        
        GPFUtils.executeGpf(key, ET.tostring(graph), (self.outputs[0]).value, self.sourceFiles, progress)
        
    def commandLineName(self):
        return self.provider.getName().lower().replace(" ", "") + ":" + self.operator.lower().replace("-","")
    
    ##############################################################################            
    # Below are GeoAlgorithm functions which need to be overwritten to support 
    # non-GDAL inputs (.safe, .zip, .dim) and outputs (.dim) in Processing toolbox.

    def convertUnsupportedFormats(self, progress):
        pass
    
    def checkOutputFileExtensions(self):
        pass
    
    def checkInputCRS(self):
        return True
        
    def _checkParameterValuesBeforeExecuting(self):
        msg = GeoAlgorithm._checkParameterValuesBeforeExecuting(self)
        # .safe and .zip file formats can be opened with Sentinel Toolbox
        # even though they can't be opened by GDAL. 
        if msg and (msg.endswith(".safe") or msg.endswith(".zip")):
            msg = None
        return msg  