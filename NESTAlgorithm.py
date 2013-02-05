import os
from PyQt4.QtGui import *
from qgis.core import *
from xml.etree.ElementTree import Element, SubElement
from sextante_gpf.GPFUtils import GPFUtils
from sextante_gpf.GPFAlgorithm import GPFAlgorithm
from sextante.parameters.ParameterRaster import ParameterRaster

class NESTAlgorithm(GPFAlgorithm):
    
    def __init__(self, descriptionfile):
        GPFAlgorithm.__init__(self, descriptionfile)
        self.programKey = GPFUtils.nestKey()
        
    def processAlgorithm(self, progress):
        GPFAlgorithm.processAlgorithm(self, GPFUtils.nestKey(), progress)
        
    def addGPFNode(self, graph):
        graph = GPFAlgorithm.addGPFNode(self, graph)
        # split band element with multiple bands into multiple elements
        for parent in graph.findall(".//band/.."):
            for element in parent.findall("band"):
                bands = element.text.split(',')
                parent.remove(element)
                for band in bands:
                    if len(band) > 0:
                        newElement = SubElement(parent, "band")
                        newElement.text = band
        for parent in graph.findall(".//mapProjection/.."):
            for element in parent.findall("mapProjection"):
                crs = element.text
                try:
                    projection = QgsCoordinateReferenceSystem(int(crs), 2)
                    wkt = projection.toWkt()
                    element.text = str(wkt)
                except:
                    parent.remove(element)
                
        
        return graph
        
    def defineCharacteristicsFromFile(self):
        GPFAlgorithm.defineCharacteristicsFromFile(self)
        # check if there are multiple raster inputs
        inputsCount = 0
        for param in self.parameters:
            if isinstance(param, ParameterRaster):
                inputsCount+=1
        if inputsCount > 1:
            self.multipleRasterInput = True                    
        
    def helpFile(self):
        GPFAlgorithm.helpFile(self, GPFUtils.nestKey())
        
    def getIcon(self):
        return  QIcon(os.path.dirname(__file__) + "/images/nest.png")
    
    def getCopy(self):
        newone = NESTAlgorithm(self.descriptionFile)
        newone.provider = self.provider
        return newone
                
        