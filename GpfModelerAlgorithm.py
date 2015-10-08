import os
from processing.core.parameters import ParameterSelection, getParameterFromString
from processing.modeler.ModelerAlgorithm import ModelerAlgorithm, Algorithm, ValueFromOutput, ValueFromInput, ModelerParameter
from processing.modeler.WrongModelException import WrongModelException
from PyQt4.QtCore import QPointF
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET



class GpfModelerAlgorithm (ModelerAlgorithm):
    
    def __init__(self): #, gpfAlgorithmProvider):
        ModelerAlgorithm.__init__(self)
        #self.gpfAlgorithmProvider = gpfAlgorithmProvider
        self.name = self.tr('GpfModel', 'GpfModelerAlgorithm')
        
    def processAlgorithm(self, progress):
        pass
    
    def commandLineName(self):
        if self.descriptionFile is None:
            return ''
        else:
            return self.gpfAlgorithmProvider+':' + os.path.basename(self.descriptionFile)[:-4].lower()

    def indent(self, elem, level=0):
        i = "\n" + level*"  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                self.indent(elem, level+1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i
    
        
    def toXml(self):
        graph = ET.Element("graph", {'id':"Graph"})
        version = ET.SubElement(graph, "version")
        version.text = "1.0"
    
        # Copy also sets some internal model variables
        modelInstance = self.getCopy()
    
        # Set the connections between nodes
        for alg in modelInstance.algs.values():
            for param in alg.params.values():
                if isinstance(param, ValueFromOutput):
                    alg.algorithm.getParameterFromName("sourceProduct").setValue(modelInstance.algs[param.alg].algorithm.nodeID)
        
        # Save model parameters
        for alg in modelInstance.algs.values():
            modelInstance.prepareAlgorithm(alg)
            graph = alg.algorithm.addGPFNode(graph)
            
        # Save model layout
        presentation = ET.SubElement(graph, "applicationData", {"id":"Presentation", "name":self.name, "group":self.group})
        ET.SubElement(presentation, "Description")
        for alg in self.algs.values():
            node = ET.SubElement(presentation, "node", {"id":alg.algorithm.nodeID})
            ET.SubElement(node, "displayPosition", {"x":str(alg.pos.x()), "y":str(alg.pos.y())})     
        
        # Make it look nice in text file
        self.indent(graph)
        
        return ET.tostring(graph)
        
    # Need to set the parameter here while checking it's type to
    # accommodate drop-down list, CRS and possibly extent
    @staticmethod
    def parseParameterValue(parameter, value):
        if isinstance(parameter, ParameterSelection):
            return parameter.options.index(value)
        else:
            return value

    @staticmethod
    def fromFile(filename, gpfAlgorithmProvider):
        try:
            tree = ET.parse(filename)
            root = tree.getroot()
            if root.tag == "graph" and "id" in root.attrib and root.attrib["id"] == "Graph":
                model = GpfModelerAlgorithm()
                model.descriptionFile = filename
                modelConnections = {}
                # Process all graph nodes (algorithms)
                for node in root.findall("node"):
                    alg = gpfAlgorithmProvider.getAlgorithmFromOperator(node.find("operator").text)
                    
                    # Special treatment for Read operator since it provides
                    # the main raster input to the graph
                    if alg is not None and alg.operator == "Read":
                        modelAlg = Algorithm(alg.commandLineName())
                        modelAlg.description = node.attrib["id"]
                        param = getParameterFromString("ParameterRaster|file|Source product")
                        model.addParameter(ModelerParameter(param, QPointF( 100, 50)))
                        modelAlg.params["file"] = ValueFromInput("file")
                        model.addAlgorithm(modelAlg) 
                    
                    # Process other operators
                    elif alg is not None:
                        modelAlg = Algorithm(alg.commandLineName())
                        modelAlg.description = node.attrib["id"]
                        for param in alg.parameters:
                            modelAlg.params[param.name] = None
                            # Process parameter settings
                            if node.find("parameters/"+param.name) is not None:
                                modelAlg.params[param.name] = GpfModelerAlgorithm.parseParameterValue(param, node.find("parameters/"+param.name).text)
                            # Save the connections between nodes in the model
                            # Once all the nodes have been processed they will be processed
                            if node.find("sources/"+param.name) is not None:
                                refid = node.find("sources/"+param.name).attrib["refid"]
                                modelConnections[refid] = (modelAlg, param.name)
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
            return model
        except:
            raise WrongModelException("Error reading GPF XML file")
                    