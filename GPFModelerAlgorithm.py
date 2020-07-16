"""
***************************************************************************
    GPFModelerAlgorithm.py
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

from builtins import str
import os
import ast
import re

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (Qgis,
                       QgsApplication,
                       QgsMessageLog,
                       QgsProcessingAlgorithm,
                       QgsCoordinateReferenceSystem,
                       QgsProcessingModelAlgorithm,
                       QgsProcessingModelParameter,
                       QgsProcessingModelOutput,
                       QgsProcessingModelChildAlgorithm,
                       QgsProcessingModelChildParameterSource,
                       QgsProcessingParameterRasterDestination,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterCrs,
                       QgsProcessingParameterExtent,
                       QgsProcessingException)
from processing.tools.dataobjects import createContext, load
from processing_gpf.GPFParameters import (getParameterFromString,
                                          ParameterBandExpression,
                                          ParameterPolarisations)
from processing_gpf.GPFUtils import GPFUtils
from qgis.PyQt.QtCore import QPointF
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QMessageBox
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET


SNAP_ID = "esa_snap"


class GPFModelerAlgorithm(QgsProcessingModelAlgorithm):

    def __init__(self, name=None, group=None, groupId=None):

        QgsProcessingModelAlgorithm.__init__(self, name, group, groupId)
        self._group = ""
        self._groupId = ""
        self.descriptionFile = None

        self.setProvider(QgsApplication.processingRegistry().providerById(SNAP_ID))
        self.programKey = GPFUtils.getKeyFromProviderName(self.provider().name())

    def icon(self):
        return QIcon(os.path.dirname(__file__) + "/images/snap_graph.png")

    def group(self):
        return self._group

    def setGroup(self, name):
        self._group = name

    def groupId(self):
        groupIdRegex = re.compile(r'^[^\(]+')
        return groupIdRegex.search(self.group()).group(0).lower().replace(" ", "_")

    def flags(self):
        # TODO - maybe it's safe to background thread this?
        return super().flags() | QgsProcessingAlgorithm.FlagNoThreading | QgsProcessingAlgorithm.FlagDisplayNameIsLiteral

    def processAlgorithm(self, parameters, context, feedback):
        gpfXml = self.toXml(executionParameters=parameters, context=context)
        loglines = []
        loglines.append("GPF Graph")
        for line in gpfXml.splitlines():
            loglines.append(line)
        QgsMessageLog.logMessage("".join(loglines), self.tr("Processing"), Qgis.Info)
        GPFUtils.executeGpf(GPFUtils.getKeyFromProviderName(self.provider().name()),
                            gpfXml,
                            feedback)

        # Extract paths to model outputs from XML
        results = {}
        root = ET.fromstring(gpfXml)
        for out in self.destinationParameterDefinitions():
            outputNodeId = out.name().split(":")[1]
            node = root.find("./node[@id='"+outputNodeId+"']")
            value = node.find("./parameters/file").text
            results[out.name()] = value
        # For some reason outputs do not load automatically so as a quick workaround they are
        # loaded manually. 
        for out in results.values():
            load(out, isRaster=True)
        return results

    def createInstance(self):
        instance = GPFModelerAlgorithm()
        instance.fromXml(self.toXml())
        instance.setSourceFilePath(self.sourceFilePath())
        return instance

    def toFile(self, filename):
        try:
            with open(filename, "w") as fp:
                fp.write(self.toXml())
            return True
        except Exception:
            return False

    def toXml(self, executionParameters=None, context=None):
        if context is None:
            context = createContext()
        graph = ET.Element("graph", {"id": "Graph"})
        version = ET.SubElement(graph, "version")
        version.text = "1.0"

        # Every time self.childAlgorithms() is called it creates new objects for the actual
        # algorithms (SNAP operators) of the model child algorithms. So it might be better to call
        # it once to get algorithm Id's and then use them to get the algorithms.
        for algId in self.childAlgorithms().keys():
            alg = self.childAlgorithm(algId)
            if isinstance(alg.algorithm(), GPFModelerAlgorithm):
                QMessageBox.warning(None, self.tr("Unable to save model"),
                                    self.tr("Sub-graphs are currently not supported."))
                return
            staticParameters = {}
            modelParameters = {}
            childOutputParameters = {}
            for name, source in alg.parameterSources().items():
                if source[0].staticValue():
                    staticParameters[name] = source[0].staticValue()
                elif source[0].parameterName():
                    modelParameters[name] = source[0].parameterName()
                elif source[0].outputChildId():
                    childOutputParameters[name] = source[0].outputChildId()

            # If graph is being created for execution then values of parameters and outputs taken
            # from model inputs and outputs should also be set.
            if executionParameters is not None:
                for algParamName, modelParamName in modelParameters.items():
                    staticParameters[algParamName] = executionParameters[modelParamName]
                for modelOutput in list(alg.modelOutputs().values()):
                    outputId = ":".join([algId, modelOutput.name()])
                    output = executionParameters[outputId]
                    outputValue = output.sink.staticValue()
                    staticParameters[modelOutput.childOutputName()] = outputValue

            # Save model algorithm
            if alg.algorithm().nodeId == alg.algorithm().operator:
                nodeId = alg.childId().split(":")[1]
            else:
                nodeId = alg.algorithm().nodeId

            graph = alg.algorithm().addGPFNode(staticParameters, graph, createContext(), nodeId)

            # Save connections between nodes
            for name, sourceNodeId in childOutputParameters.items():
                sources = graph.find("./node[@id='"+alg.algorithm().nodeId+"']/sources")
                source = ET.SubElement(sources, name)
                source.set("refid", sourceNodeId.split(":")[1])

            # Save model parameters connected to that algorithm
            for name, modelParameterName in modelParameters.items():
                # Only Read operators can load raster inputs
                if re.match("sourceProduct\d*", name) and alg.algorithm().operator != "Read":
                    QMessageBox.warning(None, self.tr("Unable to save model"),
                                        self.tr("Input rasters can only be loaded by Read operator. Change the value of raster input in %s algorithm to an output of another algorithm" % (alg.algorithm().operator,)))
                    return
                param = graph.find(
                    './node[@id="'+alg.algorithm().nodeId+'"]/parameters/'+name.replace('!', '').replace('>', '/'))
                if param is not None:
                    param.set("qgisModelInputVars",
                              self.parameterDefinition(modelParameterName).toVariantMap())
                    position = self.parameterComponent(modelParameterName).position()
                    param.set("qgisModelInputPos", str(position.x())+","+str(position.y()))

            # Save model outputs connected to that algorithm
            for out in list(alg.modelOutputs().values()):
                outParam = alg.algorithm().parameterDefinition(out.childOutputName())
                # Only Write operators can save raster outputs
                if alg.algorithm().operator != "Write" and isinstance(outParam, QgsProcessingParameterRasterDestination):
                    QMessageBox.warning(None, self.tr("Unable to save model"),
                                        self.tr("Output rasters can only be saved by Write operator. Remove the value of raster output in %s algorithm or add a Write operator" % (alg.algorithm().operator,)))
                    return
                outTag = graph.find(
                        './node[@id="'+alg.algorithm().nodeId+'"]/parameters/'+out.childOutputName())
                if outTag is not None:
                    outTag.attrib["qgisModelOutputName"] = out.description()
                    break

        # Save model layout
        presentation = ET.SubElement(graph, "applicationData", {"id": "Presentation",
                                                                "name": self.name(),
                                                                "group": self.group()})
        ET.SubElement(presentation, "Description")
        for algId in self.childAlgorithms().keys():
            alg = self.childAlgorithm(algId)
            node = ET.SubElement(presentation, "node", {"id": alg.algorithm().nodeId})
            ET.SubElement(node, "displayPosition", {"x": str(alg.position().x()),
                                                    "y": str(alg.position().y())})

        # Make it look nice in text file
        GPFUtils.indentXML(graph)

        return ET.tostring(graph, encoding="unicode")

    # Need to set the parameter here while checking it's type to
    # accommodate drop-down list, CRS and extent
    def parseParameterValue(self, parameter, value):
        if isinstance(parameter, QgsProcessingParameterEnum):
            return parameter.options().index(value)
        elif isinstance(parameter, QgsProcessingParameterCrs):
            return QgsCoordinateReferenceSystem(value).authid()
        elif isinstance(parameter, QgsProcessingParameterExtent):
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
        elif isinstance(parameter, QgsProcessingParameterBoolean):
            return value == "True"
        else:
            return value

    def fromFile(self, filename):
        try:
            tree = ET.parse(filename)
            if tree:
                self.setSourceFilePath(filename)
                return self.fromXml(ET.tostring(tree.getroot(), encoding="unicode"))
            else:
                return False
        except Exception:
            return False

    def fromXml(self, xml):
        try:
            root = ET.fromstring(xml)
            if root.tag == "graph" and "id" in root.attrib and root.attrib["id"] == "Graph":
                modelConnections = []
                inConnections = {}
                outConnections = {}
                # Process all graph nodes (algorithms)
                for node in root.findall("node"):
                    operator = node.find("operator").text
                    alg = self.provider().getAlgorithmFromOperator(operator)
                    if alg is not None:
                        modelAlg = QgsProcessingModelChildAlgorithm(alg.id())
                        modelAlg.setChildId(SNAP_ID+":"+node.attrib["id"])
                        modelAlg.setDescription(modelAlg.childId())
                        _alg = modelAlg.algorithm()
                        _alg._name = node.attrib["id"]
                        _alg._display_name = operator
                        _alg._short_description = operator
                        _alg.nodeId = node.attrib["id"]
                        for param in _alg.parameterDefinitions():
                            # Set algorithm parameter values
                            paramNode = node.find(
                                "parameters/"+param.name().replace('!', '').replace('>', '/'))
                            if paramNode is not None:
                                # Process model inputs which are saved as XML attributes
                                # of a algorithm parameters
                                if ("qgisModelInputPos" in paramNode.attrib and
                                        "qgisModelInputVars" in paramNode.attrib):
                                    paramAttribs = ast.literal_eval(
                                                        paramNode.attrib["qgisModelInputVars"])
                                    modelInput = QgsProcessingModelParameter(paramAttribs["name"])
                                    modelParam = param.clone()
                                    modelParam.fromVariantMap(paramAttribs)
                                    # fromVariantMap overwrites parameter metadata so below we make
                                    # sure that correct widgets are used for special parameter
                                    # types.
                                    if (isinstance(modelParam, ParameterBandExpression) or
                                            isinstance(modelParam, ParameterPolarisations)):
                                        modelParam.setCustomWidget()
                                    pos = paramNode.attrib["qgisModelInputPos"].split(',')
                                    modelInput.setPosition(QPointF(float(pos[0]), float(pos[1])))
                                    self.addModelParameter(modelParam, modelInput)
                                    paramSources = [
                                            QgsProcessingModelChildParameterSource().fromModelParameter(modelInput.parameterName())]
                                else:
                                    value = self.parseParameterValue(param, paramNode.text)
                                    paramSources = [
                                        QgsProcessingModelChildParameterSource().fromStaticValue(value)]
                                modelAlg.addParameterSources(param.name(), paramSources)

                            # Save the connections between nodes in the model
                            # Once all the nodes have been processed they will be processed
                            if node.find("sources/"+param.name()) is not None:
                                refid = node.find("sources/"+param.name()).attrib["refid"]
                                modelConnections.append((SNAP_ID+":"+refid,
                                                         modelAlg.childId(),
                                                         param.name()))

                        # Process model outputs which are saved as XML attributes
                        # of a algorithm parameters
                        for output in _alg.destinationParameterDefinitions():
                            outputNode = node.find("parameters/"+output.name())
                            if outputNode is not None:
                                if "qgisModelOutputName" in outputNode.attrib:
                                    outputDescription = outputNode.attrib["qgisModelOutputName"]
                                    modelOutput = QgsProcessingModelOutput(outputDescription,
                                                                           outputDescription)
                                    modelOutput.setChildId(modelAlg.childId())
                                    modelOutput.setChildOutputName(output.name())
                                    modelOutput.setPosition(QPointF(0, 0))
                                    modelAlg.setModelOutputs({outputDescription: modelOutput})
                                    outConnections[modelAlg.childId()] = outputDescription

                        # Special treatment for Read operator since it provides
                        # the main raster input to the graph. This is used in case
                        # the graph comes straight from SNAP and the Read operator
                        # does not have a QgsProcessingParameterRasterLayer.
                        if operator == "Read" and not modelAlg.parameterSources()["file"][0].parameterName():
                            modelParam = getParameterFromString("ParameterSnapRasterLayer|file|Source product|None|False")
                            modelInput = QgsProcessingModelParameter("Read")
                            self.addModelParameter(modelParam, modelInput)
                            paramSources = [
                                QgsProcessingModelChildParameterSource().fromModelParameter(modelInput.parameterName())]
                            modelAlg.addParameterSources("file", paramSources)
                            inConnections[modelAlg.childId()] = modelInput

                        # Special treatment for Write operator since it provides
                        # the main raster output from the graph. This is used in case
                        # the graph comes straight from SNAP and the Write operator
                        # does not have a QGIS QgsProcessingParameterRasterDestination.
                        algOutputNameList = [o.childOutputName() for o in modelAlg.modelOutputs().values()]
                        if operator == "Write" and "file" not in algOutputNameList:
                            outputName = "file"
                            outputDescription = "Output file"
                            modelOutput = QgsProcessingModelOutput(outputDescription, outputDescription)
                            modelOutput.setChildId(modelAlg.childId())
                            modelOutput.setChildOutputName(outputName)
                            modelOutput.pos = QPointF(0, 0)
                            modelAlg.setModelOutputs({outputDescription: modelOutput})
                            outConnections[modelAlg.childId()] = outputDescription

                        self.addChildAlgorithm(modelAlg)
                        self.updateDestinationParameters()
                    else:
                        raise QgsProcessingException("Unknown operator "+operator)

                # Set up connections between nodes of the graph
                for connection in modelConnections:
                    modelAlg = self.childAlgorithm(connection[1])
                    paramName = connection[2]
                    modelAlg.addParameterSources(
                        paramName,
                        [QgsProcessingModelChildParameterSource().fromChildOutput(connection[0],
                                                                                  "-out")])

                presentation = root.find('applicationData[@id="Presentation"]')
                # Set the model name and group
                if "name" in list(presentation.attrib.keys()):
                    self.setName(presentation.attrib["name"])
                else:
                    self.setName("Unknown")
                if "group" in list(presentation.attrib.keys()):
                    self.setGroup(presentation.attrib["group"])
                else:
                    self.setGroup("Uncategorized")
                # Place the nodes on the graph canvas
                for algId in self.childAlgorithms().keys():
                    alg = self.childAlgorithm(algId)
                    nodeId = alg.childId().split(":")[1]
                    position = presentation.find('node[@id="'+nodeId+'"]/displayPosition')
                    if position is not None:
                        alg.setPosition(QPointF(float(position.attrib["x"]),
                                                float(position.attrib["y"])))
                        # For algorithms that have input or output model parameters set those
                        # parameters in position relative to the algorithm
                        if algId in inConnections:
                            inConnections[algId].setPosition(
                                    QPointF(max(alg.position().x()-50, 0),
                                            max(alg.position().y()-50, 0)))
                        if algId in outConnections:
                            modelOutput = alg.modelOutput(outConnections[algId])
                            modelOutput.setPosition(QPointF(alg.position().x()+50,
                                                            alg.position().y()+50))

                self.updateDestinationParameters()
                return True
        except Exception as e:
            raise QgsProcessingException("Error reading GPF XML file: "+str(e))

    def tr(self, string, context=''):
        if context == '':
            context = self.__class__.__name__
        return QCoreApplication.translate(context, string)


    ##############################################################################
    # Below are QgsProcessingAlgorithm functions which need to be overwritten to support
    # non-GDAL inputs (.safe, .zip, .dim) and outputs (.dim) in Processing toolbox.

    def validateInputCRS(self):
        return True
