"""
***************************************************************************
    S1TbxAlgorithm.py
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
from PyQt4.QtGui import *
from qgis.core import *
from xml.etree.ElementTree import Element, SubElement
from processing_gpf.GPFUtils import GPFUtils
from processing_gpf.GPFAlgorithm import GPFAlgorithm
try:
    from processing.parameters.ParameterRaster import ParameterRaster
except:
    from processing.core.parameters import ParameterRaster

class SNAPAlgorithm(GPFAlgorithm):
    
    def __init__(self, descriptionfile):
        GPFAlgorithm.__init__(self, descriptionfile)
        self.programKey = GPFUtils.snapKey()
        
    def processAlgorithm(self, progress):
        GPFAlgorithm.processAlgorithm(self, GPFUtils.s1tbxKey(), progress)
        
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
        GPFAlgorithm.helpFile(self, GPFUtils.snapKey())
        
    def getIcon(self):
        return  QIcon(os.path.dirname(__file__) + "/images/snap.png")
    
    def getCopy(self):
        newone = SNAPAlgorithm(self.descriptionFile)
        newone.provider = self.provider
        return newone
                
        