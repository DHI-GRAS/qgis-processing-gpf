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

from builtins import str
import os
from qgis.PyQt.QtGui import QIcon
from qgis.core import QgsCoordinateReferenceSystem
from xml.etree.ElementTree import SubElement
from processing_gpf.GPFUtils import GPFUtils
from processing_gpf.GPFAlgorithm import GPFAlgorithm

# General SNAP algorithms (e.g. from Raster or Input-Output menus)


class SNAPAlgorithm(GPFAlgorithm):

    def __init__(self, descriptionfile):
        GPFAlgorithm.__init__(self, descriptionfile)
        self.programKey = GPFUtils.snapKey()

    def addGPFNode(self, parameters, graph, context):
        graph = GPFAlgorithm.addGPFNode(self, parameters, graph, context)
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
                except Exception:
                    parent.remove(element)

        return graph

    def helpUrl(self):
        GPFAlgorithm.helpUrl(self, GPFUtils.snapKey())

    def icon(self):
        return QIcon(os.path.dirname(__file__) + "/images/snap.png")

    def getCopy(self):
        newone = SNAPAlgorithm(self.descriptionFile)
        newone.setProvider(self.provider())
        return newone
