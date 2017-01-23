"""
***************************************************************************
    GPFParametersDialog.py
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

from PyQt4.QtGui import  QPushButton, QWidget, QVBoxLayout
from processing.gui.AlgorithmDialog import AlgorithmDialog
from processing.gui.AlgorithmDialogBase import AlgorithmDialogBase
from processing_gpf.GPFParametersPanel import GPFParametersPanel
from qgis.core import QgsRasterLayer, QgsMapLayerRegistry

# GPF parameters dialog is the same as normal parameters dialog except
# it can handle special GPF parameters
class GPFParametersDialog(AlgorithmDialog):
    def __init__(self, alg):
        AlgorithmDialogBase.__init__(self, alg)

        self.alg = alg

        self.mainWidget = GPFParametersPanel(self, alg)
        self.setMainWidget()
        
        # Same look as AlgorithmDialog
        cornerWidget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 5)
        self.tabWidget.setStyleSheet("QTabBar::tab { height: 30px; }")
        runAsBatchButton = QPushButton("Run as batch process...")
        runAsBatchButton.clicked.connect(self.runAsBatch)
        layout.addWidget(runAsBatchButton)
        cornerWidget.setLayout(layout)
        self.tabWidget.setCornerWidget(cornerWidget)
        
        QgsMapLayerRegistry.instance().layerWasAdded.connect(self.mainWidget.layerAdded)
        QgsMapLayerRegistry.instance().layersWillBeRemoved.connect(self.mainWidget.layersWillBeRemoved)
        
    def getRasterParamPath(self, paramName):
        if paramName is not None:
            param = self.mainWidget.valueItems[paramName]
            obj = param.getValue()
            if isinstance(obj, QgsRasterLayer):
                value = unicode(obj.dataProvider().dataSourceUri())
            else:
                value = param.getValue()
        else:
            value = ""
        return value