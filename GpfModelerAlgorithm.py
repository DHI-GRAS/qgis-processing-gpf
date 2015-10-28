import os
import copy
import ast
import re
from qgis.core import QgsCoordinateReferenceSystem
from processing.core.parameters import ParameterSelection, ParameterCrs, ParameterExtent, getParameterFromString
from processing.modeler.ModelerAlgorithm import ModelerAlgorithm, Algorithm, ValueFromOutput, ValueFromInput, ModelerParameter, ModelerOutput
from processing.modeler.WrongModelException import WrongModelException
from processing.core.ProcessingLog import ProcessingLog
from processing_gpf.GPFUtils import GPFUtils
from processing_gpf.BEAMParametersDialog import BEAMParametersDialog
from PyQt4.QtCore import QPointF
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

import traceback

class GpfModelerAlgorithm (ModelerAlgorithm):
    
    def __init__(self, gpfAlgorithmProvider):
        ModelerAlgorithm.__init__(self)
        self.provider = gpfAlgorithmProvider
        self.programKey = GPFUtils.getKeyFromProviderName(self.provider.getName())
        self.name = self.tr('GpfModel', 'GpfModelerAlgorithm')
        
        # NOTE:
        # This doesn't seem used so remove it later from BEAMParmetersPanel and S1TbxAlgorithm
        self.multipleRasterInput = False
    
    # BEAM parameters dialog is the same as normal parameters dialog except
    # it has a button next to raster inputs to show band names
    def getCustomParametersDialog(self):
        return BEAMParametersDialog(self)
    
    def getCopy(self):
        newone = GpfModelerAlgorithm(self.provider)
        newone.algs = copy.deepcopy(self.algs)
        newone.inputs = copy.deepcopy(self.inputs)
        newone.defineCharacteristics()
        newone.name = self.name
        newone.group = self.group
        newone.descriptionFile = self.descriptionFile
        newone.helpContent = copy.deepcopy(self.helpContent)
        return newone
        
    def processAlgorithm(self, progress):
        gpfXml = self.toXml(forExecution = True)
        loglines = []
        loglines.append("GPF Graph")
        for line in gpfXml.splitlines():
            loglines.append(line)
        ProcessingLog.addToLog(ProcessingLog.LOG_INFO, loglines)
        GPFUtils.executeGpf(GPFUtils.getKeyFromProviderName(self.provider.getName()), gpfXml, progress)
    
    def commandLineName(self):
        if self.descriptionFile is None:
            return ''
        else:
            return self.provider.getName()+':' + os.path.basename(self.descriptionFile)[:-4].lower()
        
    def toXml(self, forExecution = False):
        graph = ET.Element("graph", {'id':"Graph"})
        version = ET.SubElement(graph, "version")
        version.text = "1.0"
    
        # Copy also sets some internal model variables but if
        # XML is created to execute the algorithm then the 
        # copy was already made
        if forExecution:
            modelInstance = self
        else:
            modelInstance = self.getCopy()
        
    
        # Set the connections between nodes
        for alg in modelInstance.algs.values():
            for param in alg.params.values():
                if isinstance(param, ValueFromOutput):
                    alg.algorithm.getParameterFromName("sourceProduct").setValue(modelInstance.algs[param.alg].algorithm.nodeID)
                
        # Save model algorithms
        for alg in modelInstance.algs.values():
            modelInstance.prepareAlgorithm(alg)
            graph = alg.algorithm.addGPFNode(graph)
            # Save also the position and settings of model inputs. 
            # They are saved as attributes of relevant parameter XML nodes.
            # This way they do not interfere with the model when it's opened
            # in SNAP.
            if alg.algorithm.operator != "Read":
                for param in alg.params.keys():
                    paramValue = str(alg.params[param])
                    if paramValue in modelInstance.inputs.keys():
                        paramTag = graph.find('node[@id="'+alg.algorithm.nodeID+'"]/parameters/'+param)
                        pos = modelInstance.inputs[paramValue].pos
                        paramTag.attrib["qgisModelInputPos"] = str(pos.x())+","+str(pos.y())
                        paramTag.attrib["qgisModelInputVars"] = str(modelInstance.inputs[paramValue].param.todict())
            
        # Save model layout
        presentation = ET.SubElement(graph, "applicationData", {"id":"Presentation", "name":self.name, "group":self.group})
        ET.SubElement(presentation, "Description")
        for alg in self.algs.values():
            node = ET.SubElement(presentation, "node", {"id":alg.algorithm.nodeID})
            ET.SubElement(node, "displayPosition", {"x":str(alg.pos.x()), "y":str(alg.pos.y())})     
        
        # Make it look nice in text file
        GPFUtils.indentXML(graph)
        
        return ET.tostring(graph)
        
    # Need to set the parameter here while checking it's type to
    # accommodate drop-down list, CRS and extent
    @staticmethod
    def parseParameterValue(parameter, value):
        if isinstance(parameter, ParameterSelection):
            return parameter.options.index(value)
        elif isinstance(parameter, ParameterCrs):
            return QgsCoordinateReferenceSystem(value).authid()
        elif isinstance(parameter, ParameterExtent):
            match = re.match("POLYGON\s*\(\((.*)\)\)", value)
            if match:
                xmin, xmax, ymin, ymax = (None, None, None, None)
                polygon = match.group(1)
                for point in polygon.split(","):
                    x = float(point.lstrip().split(" ")[0])
                    y = float(point.lstrip().split(" ")[1])
                    xmin = x if xmin is None else min(xmin, x)
                    xmax = x if xmax is None else max(xmax, x)
                    ymin = y if ymin is None else min(ymin, y)
                    ymax = y if ymax is None else max(ymax, y)
                if xmin is not None:
                    return "("+str(xmin)+","+str(xmax)+","+str(ymin)+","+str(ymax)+")"
            return ""    
        else:
            return value

    @staticmethod
    def fromFile(filename, gpfAlgorithmProvider):
        try:
            tree = ET.parse(filename)
            root = tree.getroot()
            if root.tag == "graph" and "id" in root.attrib and root.attrib["id"] == "Graph":
                model = GpfModelerAlgorithm(gpfAlgorithmProvider)
                model.descriptionFile = filename
                modelConnections = {}
                inConnections = {}
                outConnections = {}
                # Process all graph nodes (algorithms)
                for node in root.findall("node"):
                    alg = gpfAlgorithmProvider.getAlgorithmFromOperator(node.find("operator").text)
                    if alg is not None:
                        modelAlg = Algorithm(alg.commandLineName())
                        modelAlg.description = node.attrib["id"]
                        for param in alg.parameters:
                            modelAlg.params[param.name] = None
                            # Set algorithm parameter values
                            paramNode = node.find("parameters/"+param.name)
                            if paramNode is not None:
                                modelAlg.params[param.name] = GpfModelerAlgorithm.parseParameterValue(param, paramNode.text)
                                # Process model inputs which are saved as XML attributes
                                # of a model parameters
                                if "qgisModelInputPos" in paramNode.attrib and "qgisModelInputVars" in paramNode.attrib:
                                    modelInput = ModelerParameter()
                                    modelInput.param = copy.deepcopy(param)
                                    modelInput.param.__dict__ = ast.literal_eval(paramNode.attrib["qgisModelInputVars"])
                                    pos = paramNode.attrib["qgisModelInputPos"].split(',')
                                    modelInput.pos = QPointF(float(pos[0]), float(pos[1]))
                                    model.addParameter(modelInput)
                                    modelAlg.params[param.name] = ValueFromInput(modelInput.param.name)
                                    
                                    
                            # Save the connections between nodes in the model
                            # Once all the nodes have been processed they will be processed
                            if node.find("sources/"+param.name) is not None:
                                refid = node.find("sources/"+param.name).attrib["refid"]
                                modelConnections[refid] = (modelAlg, param.name)
                            
                            # Special treatment for Read operator since it provides
                            # the main raster input to the graph    
                            if alg.operator == "Read":
                                param = getParameterFromString("ParameterRaster|file|Source product")
                                modelParameter = ModelerParameter(param, QPointF(0, 0))
                                model.addParameter(modelParameter)
                                modelAlg.params["file"] = ValueFromInput("file")
                                inConnections[modelAlg] = modelParameter
                            
                            # Special treatment for Write operator since it provides
                            # the main raster output from the graph    
                            if alg.operator == "Write":
                                modelOutput = ModelerOutput("Output file")
                                modelOutput.pos = QPointF(0, 0)
                                modelAlg.outputs["file"] = modelOutput
                                outConnections[modelAlg] = modelOutput
                                           
                        model.addAlgorithm(modelAlg) 
                
                # Set up connections between nodes of the graph
                for connection in modelConnections:
                    for alg in model.algs.values():
                        if alg.description == connection:
                            modelAlg = modelConnections[connection][0]
                            paramName = modelConnections[connection][1]
                            modelAlg.params[paramName] = ValueFromOutput(alg.name, "-out")
                            break
                
                presentation = root.find('applicationData[@id="Presentation"]')
                # Set the model name and group
                model.name = presentation.attrib["name"] if "name" in presentation.attrib.keys() else os.path.splitext(os.path.basename(filename))[0]
                model.group = presentation.attrib["group"] if "group" in presentation.attrib.keys() else "Uncategorized"
                # Place the nodes on the graph canvas
                for alg in model.algs.values():
                    position = presentation.find('node[@id="'+alg.description+'"]/displayPosition')
                    if position is not None:
                        alg.pos = QPointF(float(position.attrib["x"]), float(position.attrib["y"])) 
                        # For algorithms that have input or output model parameters set those parameters
                        # in position relative to the algorithm
                        if alg in inConnections:
                            inConnections[alg].pos = QPointF(max(alg.pos.x()-50, 0), max(alg.pos.y()-50, 0))
                        if alg in outConnections:
                            outConnections[alg].pos = QPointF(alg.pos.x()+50, alg.pos.y()+50)     
            return model
        except:
            raise WrongModelException("Error reading GPF XML file")
                    