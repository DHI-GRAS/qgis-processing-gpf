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

from builtins import str
import os
import re
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

from qgis.PyQt.QtCore import QCoreApplication, QUrl
from qgis.core import (Qgis,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterExtent,
                       QgsProcessingParameterCrs,
                       QgsMessageLog,
                       QgsProcessingException,
                       QgsCoordinateReferenceSystem)
from processing.core.parameters import getParameterFromString

from processing_gpf.GPFUtils import GPFUtils
from processing_gpf import GPFParameters


class GPFAlgorithm(QgsProcessingAlgorithm):

    OUTPUT_EXTENT = "OUTPUT_EXTENT"

    NOVALUEINT = 99999
    NOVALUEDOUBLE = 99999.9

    def __init__(self, descriptionfile):
        QgsProcessingAlgorithm.__init__(self)
        self._name = ''
        self._display_name = ''
        self._short_description = ''
        self._group = ''
        self._groupId = ''
        self.groupIdRegex = re.compile(r'^[^\(]+')
        self.descriptionFile = descriptionfile
        self.defineCharacteristicsFromFile()
        self.nodeId = self.operator
        self.programKey = GPFUtils.snapKey()

    def createInstance(self):
        return self.__class__(self.descriptionFile)

    def name(self):
        return self._name

    def displayName(self):
        return self._display_name

    def shortDescription(self):
        return self._short_description

    def group(self):
        return self._group

    def groupId(self):
        return self._groupId

    def flags(self):
        # TODO - maybe it's safe to background thread this?
        return super().flags() | QgsProcessingAlgorithm.FlagNoThreading | QgsProcessingAlgorithm.FlagDisplayNameIsLiteral

    def helpUrl(self, key):
        folder = GPFUtils.gpfDocPath(key)
        if str(folder).strip() != "":
            helpfile = os.path.join(str(folder), self.operator + ".html")
            return QUrl.fromLocalFile(helpfile).toString
        return None

    def svgIconPath(self):
        return ""

    def initAlgorithm(self, config=None):
        pass

    def defineCharacteristicsFromFile(self):
        with open(self.descriptionFile) as lines:
            line = lines.readline().strip("\n").strip()
            self.operator = line
            self._display_name = self.tr(line)
            line = lines.readline().strip("\n").strip()
            self._name = self.tr(line)
            line = lines.readline().strip("\n").strip()
            self._short_description = self.tr(line)
            line = lines.readline().strip("\n").strip()
            self._group = self.tr(line)
            self._groupId = self.groupIdRegex.search(line).group(0).lower().replace(" ", "_")
            line = lines.readline().strip("\n").strip()
            while line != "":
                try:
                    # Initialize GPF specific parameters ...
                    param = GPFParameters.getParameterFromString(line)
                    if param is None:
                        # ... and generic Processing parameters
                        param = getParameterFromString(line, "SnapAlgorithm")
                    if param is not None:
                        # We use createOutput argument for automatic output creation
                        self.addParameter(param, True)
                    line = lines.readline().strip("\n").strip()
                except Exception as e:
                    QgsMessageLog.logMessage(
                            self.tr("Could not open GPF algorithm: " + self.descriptionFile +
                                    "\n" + line),
                            self.tr("Processing"),
                            Qgis.Critical)
                    raise e

    def addGPFNode(self, parameters, graph, context, nodeId=None):
        if nodeId:
            self.nodeId = nodeId

        # now create and add the current node
        node = ET.Element("node", {"id": self.nodeId})
        operator = ET.SubElement(node, "operator")
        operator.text = self.operator

        # sources are added in the parameters loop below
        sources = ET.SubElement(node, "sources")

        parametersNode = ET.SubElement(node, "parameters")

        noOutputs = [o for o in self.parameterDefinitions() if o not in
                     self.destinationParameterDefinitions()]
        for param in noOutputs:

            # add a source product
            if isinstance(param, QgsProcessingParameterRasterLayer):
                value = self.parameterAsString(parameters, param.name(), context)
                if value:
                    if not os.path.exists(value):
                        value = self.parameterAsRasterLayer(parameters,
                                                            param.name(),
                                                            context).source()
                    value, dataFormat = GPFUtils.gdalPathToSnapPath(value)
                    if value.startswith("Error:"):
                        raise QgsProcessingException(value)
                    # if the source is a file, then add an external "source product" file
                    if os.path.isfile(value):
                        # check if the file should be added individually or through the
                        # ProductSet-Reader used sometimes by S1 Toolbox
                        match = re.match("^\d*ProductSet-Reader>(.*)", param.name())
                        if match:
                            paramName = match.group(1)
                            sourceNodeId = self.addProductSetReaderNode(graph, value)
                        else:
                            paramName = param.name()
                            if operator.text == "Read":
                                sourceNodeId = self.addReadNode(graph, value, dataFormat,
                                                                self.nodeId)
                                return graph
                            else:
                                sourceNodeId = self.addReadNode(graph, value, dataFormat)
                        if sources.find(paramName) is None:
                            source = ET.SubElement(sources, paramName)
                            source.set("refid", sourceNodeId)
                    # else assume its a reference to a previous node and add a "source" element
                    elif value is not None:
                        source = ET.SubElement(sources, param.name(), {"refid": value})
                # This is to allow GPF graphs to save custom names of input rasters
                elif operator.text == "Read":
                    dataFormat = 'GeoTIFF'
                    value = ""
                    sourceNodeId = self.addReadNode(graph, value, dataFormat, self.nodeId)
                    return graph

            # add parameters
            else:
                # Set the name of the parameter
                # First check if there are nested tags
                tagList = param.name().split(">")
                parentElement = parametersNode
                parameter = None
                for tag in tagList:
                    # if this is the last tag or there are no nested tags create the parameter
                    # element
                    if tag == tagList[-1]:
                        # special treatment for geoRegionExtent parameter in Subset operator
                        if tag == "geoRegionExtent":
                            tag = "geoRegion"
                        # there can be only one parameter element in each parent element
                        if len(parentElement.findall(tag)) > 0:
                            parameter = parentElement.findall(tag)[0]
                        else:
                            parameter = ET.SubElement(parentElement, tag)
                    # "!" means that a new element in the graph should be created as child of the
                    # parent element and set as a parent
                    elif tag.startswith("!"):
                        parentElement = ET.SubElement(parentElement, tag[1:])
                    # otherwise just find the last element with required name and set it as parent
                    # of the parameter element or create a new one if it can't be found
                    else:
                        if len(parentElement.findall(tag)) > 0:
                            parentElement = (parentElement.findall(tag))[-1]
                        else:
                            parentElement = ET.SubElement(parentElement, tag)

                # Set the value of the parameter
                value = self.parameterAsDouble(parameters, param.name(), context)
                if value is None or value == GPFAlgorithm.NOVALUEINT or\
                   value == GPFAlgorithm.NOVALUEDOUBLE:
                    pass
                elif isinstance(param, QgsProcessingParameterEnum):
                    idx = self.parameterAsEnums(parameters, param.name(), context)[0]
                    parameter.text = str(param.options()[idx])
                # create at WKT polygon from the extent values, used in Subset Operator
                elif isinstance(param, QgsProcessingParameterExtent):
                    extent = self.parameterAsExtent(parameters, param.name(), context,
                                                    QgsCoordinateReferenceSystem.fromEpsgId(4326))
                    parameter.text = extent.asWktPolygon()
                elif isinstance(param, QgsProcessingParameterCrs):
                    authId = self.parameterAsCrs(parameters, param.name(), context).authid()
                    parameter.text = authId
                else:
                    parameter.text = self.parameterAsString(parameters, param.name(), context)

        # For "Write" operator also save the output raster as a parameter
        if self.operator == "Write":
            fileParameter = ET.SubElement(parametersNode, "file")
            paramName = self.destinationParameterDefinitions()[0].name()
            fileParameter.text = self.parameterAsString(parameters, paramName, context)

        graph.append(node)
        return graph

    def addProductSetReaderNode(self, graph, filename):
        nodeId = self.nodeId+"_ProductSet-Reader"
        node = graph.find(".//*[@id='"+nodeId+"']")

        # add ProductSet-Reader node if it doesn't exist yet
        if node is None:
            node = ET.SubElement(graph, "node", {"id": nodeId})
            ET.SubElement(node, "sources")
            operator = ET.SubElement(node, "operator")
            operator.text = "ProductSet-Reader"
            # add the file list
            parametersNode = ET.SubElement(node, "parameters")
            parameter = ET.SubElement(parametersNode, "fileList")
            parameter.text = filename
        # otherwise append filename to the node's fileList
        else:
            parameter = node.find(".//fileList")
            parameter.text += ","+filename
        return nodeId

    def addReadNode(self, graph, filename, dataFormat="", nodeId=""):
        # Add read node
        if not nodeId:
            nodeId = self.nodeId+"_read"
        node = ET.SubElement(graph, "node", {"id": nodeId})
        operator = ET.SubElement(node, "operator")
        operator.text = "Read"

        # Add empty source
        ET.SubElement(node, "sources")

        # Add file parameter with input file path
        parametersNode = ET.SubElement(node, "parameters")
        fileParameter = ET.SubElement(parametersNode, "file")
        fileParameter.text = filename
        if dataFormat:
            dataFormatParameter = ET.SubElement(parametersNode, "formatName")
            dataFormatParameter.text = dataFormat

        return nodeId

    def addWriteNode(self, parameters, graph, output, key, context):

        # add write node
        nodeId = self.nodeId+"_write"
        node = ET.SubElement(graph, "node", {"id": nodeId})
        operator = ET.SubElement(node, "operator")
        operator.text = "Write"
        value = self.parameterAsOutputLayer(parameters, output.name(), context)

        # add source
        sources = ET.SubElement(node, "sources")
        ET.SubElement(sources, "sourceProduct", {"refid": self.nodeId})

        # add some options
        parametersNode = ET.SubElement(node, "parameters")
        parameter = ET.SubElement(parametersNode, "file")
        parameter.text = value
        parameter = ET.SubElement(parametersNode, "formatName")
        if value.lower().endswith(".dim"):
            parameter.text = "BEAM-DIMAP"
        elif value.lower().endswith(".hdr"):
            parameter.text = "ENVI"
        else:
            if key == GPFUtils.beamKey():
                parameter.text = "GeoTIFF"
            else:
                parameter.text = "GeoTIFF-BigTIFF"
        return graph

    def processAlgorithm(self, parameters, context, progress):
        key = self.programKey
        results = {}

        # Create a GFP for execution with SNAP's GPT
        graph = ET.Element("graph", {'id': self.operator+'_gpf'})
        version = ET.SubElement(graph, "version")
        version.text = "1.0"

        # Add node with this algorithm's operator
        graph = self.addGPFNode(parameters, graph, context)

        # Add outputs as write nodes (except for Write operator)
        if self.operator != "Write" and len(self.destinationParameterDefinitions()) >= 1:
            for output in self.destinationParameterDefinitions():
                graph = self.addWriteNode(parameters, graph, output, key, context)

        # Log the GPF
        loglines = []
        loglines.append("GPF Graph")
        GPFUtils.indentXML(graph)
        for line in ET.tostring(graph, encoding="unicode").splitlines():
            loglines.append(line)
        QgsMessageLog.logMessage("".join(loglines), self.tr("Processing"), Qgis.Info)

        # Execute the GPF
        GPFUtils.executeGpf(key, ET.tostring(graph, encoding="unicode"), progress)

        for output in self.destinationParameterDefinitions():
            results[output.name()] = self.parameterAsFileOutput(parameters, output.name(), context)
        return results

    def tr(self, string, context=''):
        if context == '':
            context = self.__class__.__name__
        return QCoreApplication.translate(context, string)

    ##############################################################################
    # Below are QgsProcessingAlgorithm functions which need to be overwritten to support
    # non-GDAL inputs (.safe, .zip, .dim) and outputs (.dim) in Processing toolbox.

    def validateInputCRS(self):
        return True
