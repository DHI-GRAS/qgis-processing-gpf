import os
import copy
import ast
import re
from qgis.core import QgsCoordinateReferenceSystem, QgsRasterLayer, QgsVectorLayer
from qgis.gui import QgsMessageBar
from qgis.utils import iface
from processing.core.parameters import getParameterFromString, ParameterSelection, ParameterCrs, ParameterRaster, ParameterVector, ParameterTable, ParameterTableField, ParameterBoolean, ParameterString, ParameterNumber, ParameterExtent, ParameterDataObject, ParameterMultipleInput
from processing.core.outputs import OutputRaster
from processing.core.GeoAlgorithmExecutionException import GeoAlgorithmExecutionException
from processing.core.ProcessingLog import ProcessingLog
from processing.tools import dataobjects
from processing.modeler.ModelerAlgorithm import Algorithm, ValueFromOutput, ValueFromInput, ModelerParameter, ModelerOutput
from processing.modeler.WrongModelException import WrongModelException
from processing.gui.Help2Html import getHtmlFromDescriptionsDict
from processing_gpf.GPFUtils import GPFUtils
from processing_gpf.GPFParametersDialog import GPFParametersDialog
from PyQt4.QtCore import QPointF
from PyQt4.QtGui import QIcon, QMessageBox
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

import traceback
from processing.core.GeoAlgorithm import GeoAlgorithm

# NOTE
# GPFModelerAlgorithm should really be a subclass of ModelerAlgorithm.
# However, that was causing EditModelAction to appear in the context menu
# of GPF Models present in the Processing Toolbox. To overcome this issue
# GPFModelerAlgorithm is now a subclass of GeoAlgorithm but still has the
# same interface as ModelerAlgorithm 
class GPFModelerAlgorithm (GeoAlgorithm):
    
    def __init__(self, gpfAlgorithmProvider):
        
        self.name = self.tr('GpfModel', 'GpfModelerAlgorithm')
        
        # The dialog where this model is being edited
        self.modelerdialog = None
        self.descriptionFile = None
        self.helpContent = {}
        # Geoalgorithms in this model. A dict of Algorithm objects, with names as keys
        self.algs = {}
        #Input parameters. A dict of Input objects, with names as keys
        self.inputs = {}
        
        # NOTE:
        # This doesn't seem used so remove it later from BEAMParmetersPanel and S1TbxAlgorithm
        self.multipleRasterInput = False
        
        GeoAlgorithm.__init__(self)
        
        self.provider = gpfAlgorithmProvider
        self.programKey = GPFUtils.getKeyFromProviderName(self.provider.getName())
        
    
    def getIcon(self):
        return  QIcon(os.path.dirname(__file__) + "/images/snap_graph.png")
    
    # BEAM parameters dialog is the same as normal parameters dialog except
    # it has a button next to raster inputs to show band names
    def getCustomParametersDialog(self):
        return GPFParametersDialog(self)
    
    def getCopy(self):
        newone = GPFModelerAlgorithm(self.provider)
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
            
            # Only Write operators can save raster outputs
            for out in alg.algorithm.outputs:
                if alg.algorithm.operator != "Write" and isinstance(out, OutputRaster):
                    if out.name in alg.outputs:
                        QMessageBox.warning(None, self.tr('Unable to save model'),
                                self.tr('Output rasters can only be saved by Write operator. Remove the value of raster output in %s algorithm or add a Write operator' % (alg.algorithm.operator,) ))
                        return
            
            graph = alg.algorithm.addGPFNode(graph)
            # Save also the position and settings of model inputs. 
            # They are saved as attributes of relevant parameter XML nodes.
            # This way they do not interfere with the model when it's opened
            # in SNAP.
            if alg.algorithm.operator != "Read":
                for param in alg.params.keys():
                    paramValue = str(alg.params[param])
                    if paramValue in modelInstance.inputs.keys():
                        # Only Read operators can read raster inputs
                        if param == "sourceProduct":
                            QMessageBox.warning(None, self.tr('Unable to save model'),
                                self.tr('Input rasters can only be loaded by Read operator. Change the value of raster input in %s algorithm to an output of another algorithm' % (alg.algorithm.operator,) ))
                            return
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
            if value:
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
            return None    
        elif isinstance(parameter, ParameterBoolean):
            return value == "True"
        else:
            return value

    @staticmethod
    def fromFile(filename, gpfAlgorithmProvider):
        try:
            tree = ET.parse(filename)
            root = tree.getroot()
            if root.tag == "graph" and "id" in root.attrib and root.attrib["id"] == "Graph":
                model = GPFModelerAlgorithm(gpfAlgorithmProvider)
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
                                modelAlg.params[param.name] = GPFModelerAlgorithm.parseParameterValue(param, paramNode.text)
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
                    else:
                        raise Exception("Unknown operator "+node.find("operator").text) 
                
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
        except Exception, e:
            raise WrongModelException("Error reading GPF XML file: "+str(e))
        
        
#####################################################################
# Unmodified methods copied from ModelerAlgorithm

    CANVAS_SIZE = 4000
    
    def defineCharacteristics(self):
        classes = [ParameterRaster, ParameterVector, ParameterTable, ParameterTableField,
                   ParameterBoolean, ParameterString, ParameterNumber]
        self.parameters = []
        for c in classes:
            for inp in self.inputs.values():
                if isinstance(inp.param, c):
                    self.parameters.append(inp.param)
        for inp in self.inputs.values():
            if inp.param not in self.parameters:
                self.parameters.append(inp.param)
        self.outputs = []
        for alg in self.algs.values():
            if alg.active:
                for out in alg.outputs:
                    modelOutput = copy.deepcopy(alg.algorithm.getOutputFromName(out))
                    modelOutput.name = self.getSafeNameForOutput(alg.name, out)
                    modelOutput.description = alg.outputs[out].description
                    self.outputs.append(modelOutput)
    
    def addParameter(self, param):
        self.inputs[param.param.name] = param
        
    def updateParameter(self, param):
        self.inputs[param.name].param = param
        
    def addAlgorithm(self, alg):
        name = self.getNameForAlgorithm(alg)
        alg.name = name
        self.algs[name] = alg    
    
    def getNameForAlgorithm(self, alg):
        i = 1
        while alg.consoleName.upper().replace(":", "") + "_" + str(i) in self.algs.keys():
            i += 1
        return alg.consoleName.upper().replace(":", "") + "_" + str(i)
    
    def updateAlgorithm(self, alg):
        alg.pos = self.algs[alg.name].pos
        self.algs[alg.name] = alg

        from processing.modeler.ModelerGraphicItem import ModelerGraphicItem
        for i, out in enumerate(alg.outputs):
            alg.outputs[out].pos = (alg.outputs[out].pos or
                    alg.pos + QPointF(
                        ModelerGraphicItem.BOX_WIDTH,
                        (i + 1.5) * ModelerGraphicItem.BOX_HEIGHT))
    
    def removeAlgorithm(self, name):
        """Returns True if the algorithm could be removed, False if
        others depend on it and could not be removed.
        """
        if self.hasDependencies(name):
            return False
        del self.algs[name]
        self.modelerdialog.hasChanged = True
        return True

    def removeParameter(self, name):
        """Returns True if the parameter could be removed, False if
        others depend on it and could not be removed.
        """
        if self.hasDependencies(name):
            return False
        del self.inputs[name]
        self.modelerdialog.hasChanged = True
        return True

    def hasDependencies(self, name):
        """This method returns True if some other element depends on
        the passed one.
        """
        for alg in self.algs.values():
            for value in alg.params.values():
                if value is None:
                    continue
                if isinstance(value, list):
                    for v in value:
                        if isinstance(v, ValueFromInput):
                            if v.name == name:
                                return True
                        elif isinstance(v, ValueFromOutput):
                            if v.alg == name:
                                return True
                if isinstance(value, ValueFromInput):
                    if value.name == name:
                        return True
                elif isinstance(value, ValueFromOutput):
                    if value.alg == name:
                        return True
        return False


    def getDependsOnAlgorithms(self, name):
        """This method returns a list with names of algorithms
        a given one depends on.
        """
        alg = self.algs[name]
        algs = set()
        algs.update(set(alg.dependencies))
        for value in alg.params.values():
            if value is None:
                continue
            if isinstance(value, list):
                for v in value:
                    if isinstance(v, ValueFromOutput):
                        algs.add(v.alg)
                        algs.update(self.getDependsOnAlgorithms(v.alg))
            elif isinstance(value, ValueFromOutput):
                algs.add(value.alg)
                algs.update(self.getDependsOnAlgorithms(value.alg))


        return algs

    def getDependentAlgorithms(self, name):
        """This method returns a list with the names of algorithms
        depending on a given one. It includes the algorithm itself
        """
        algs = set()
        algs.add(name)
        for alg in self.algs.values():
            for value in alg.params.values():
                if value is None:
                    continue
                if isinstance(value, list):
                    for v in value:
                        if isinstance(v, ValueFromOutput) and v.alg == name:
                            algs.update(self.getDependentAlgorithms(alg.name))
                elif isinstance(value, ValueFromOutput) and value.alg == name:
                            algs.update(self.getDependentAlgorithms(alg.name))

        return algs

    def setPositions(self, paramPos, algPos, outputsPos):
        for param, pos in paramPos.iteritems():
            self.inputs[param].pos = pos
        for alg, pos in algPos.iteritems():
            self.algs[alg].pos = pos
        for alg, positions in outputsPos.iteritems():
            for output, pos in positions.iteritems():
                self.algs[alg].outputs[output].pos = pos
                
    def prepareAlgorithm(self, alg):
        algInstance = alg.algorithm
        for param in algInstance.parameters:
            if not param.hidden:
                if param.name in alg.params:
                    value = self.resolveValue(alg.params[param.name])
                else:
                    iface.messageBar().pushMessage(self.tr("Warning"),
                                                   self.tr("Parameter %s in algorithm %s in the model is run with default value! Edit the model to make sure that this is correct." % (param.name, alg.name)), 
                                                   QgsMessageBar.WARNING, 4)
                    value = None
                if value is None and isinstance(param, ParameterExtent):
                    value = self.getMinCoveringExtent()
                # We allow unexistent filepaths, since that allows
                # algorithms to skip some conversion routines
                if not param.setValue(value) and not isinstance(param,
                        ParameterDataObject):
                    raise GeoAlgorithmExecutionException(
                        self.tr('Wrong value: %s', 'ModelerAlgorithm') % value)
        for out in algInstance.outputs:
            if not out.hidden:
                if out.name in alg.outputs:
                    name = self.getSafeNameForOutput(alg.name, out.name)
                    modelOut = self.getOutputFromName(name)
                    if modelOut:
                        out.value = modelOut.value
                else:
                    out.value = None

        return algInstance

    def deactivateAlgorithm(self, algName):
        dependent = self.getDependentAlgorithms(algName)
        for alg in dependent:
            self.algs[alg].active = False

    def activateAlgorithm(self, algName):
        parents = self.getDependsOnAlgorithms(algName)
        for alg in parents:
            if not self.algs[alg].active:
                return False
        self.algs[algName].active = True
        return True

    def getSafeNameForOutput(self, algName, outName):
        return outName + '_ALG' + algName

    def resolveValue(self, value):
        if value is None:
            return None
        if isinstance(value, list):
            return ";".join([self.resolveValue(v) for v in value])
        if isinstance(value, ValueFromInput):
            return self.getParameterFromName(value.name).value
        elif isinstance(value, ValueFromOutput):
            return self.algs[value.alg].algorithm.getOutputFromName(value.output).value
        else:
            return value

    def getMinCoveringExtent(self):
        first = True
        found = False
        for param in self.parameters:
            if param.value:
                if isinstance(param, (ParameterRaster, ParameterVector)):
                    found = True
                    if isinstance(param.value, (QgsRasterLayer, QgsVectorLayer)):
                        layer = param.value
                    else:
                        layer = dataobjects.getObjectFromUri(param.value)
                    self.addToRegion(layer, first)
                    first = False
                elif isinstance(param, ParameterMultipleInput):
                    found = True
                    layers = param.value.split(';')
                    for layername in layers:
                        layer = dataobjects.getObjectFromUri(layername)
                        self.addToRegion(layer, first)
                        first = False
        if found:
            return ','.join([str(v) for v in [self.xmin, self.xmax, self.ymin, self.ymax]])
        else:
            return None

    def addToRegion(self, layer, first):
        if first:
            self.xmin = layer.extent().xMinimum()
            self.xmax = layer.extent().xMaximum()
            self.ymin = layer.extent().yMinimum()
            self.ymax = layer.extent().yMaximum()
        else:
            self.xmin = min(self.xmin, layer.extent().xMinimum())
            self.xmax = max(self.xmax, layer.extent().xMaximum())
            self.ymin = min(self.ymin, layer.extent().yMinimum())
            self.ymax = max(self.ymax, layer.extent().yMaximum())
    
    def getAsCommand(self):
        if self.descriptionFile:
            return GeoAlgorithm.getAsCommand(self)
        else:
            return None
        
    def setModelerView(self, dialog):
        self.modelerdialog = dialog

    def updateModelerView(self):
        if self.modelerdialog:
            self.modelerdialog.repaintModel()

    def help(self):
        print self.helpContent
        try:
            return True, getHtmlFromDescriptionsDict(self, self.helpContent)
        except:
            return False, None