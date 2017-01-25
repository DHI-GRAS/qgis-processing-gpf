"""
***************************************************************************
    GPFModelerScene.py
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

from PyQt4.QtGui import QGraphicsItem
from PyQt4.QtCore import QPointF
from processing.modeler.ModelerArrowItem import ModelerArrowItem
from processing.modeler.ModelerScene import ModelerScene
from processing_gpf.GPFModelerGraphicItem import GPFModelerGraphicItem

class GPFModelerScene(ModelerScene):
    
    # Function paintModel is exactly the same as in ModelerScene class from
    # QGIS 2.18.3 except that ModelerGraphicItem is replaced by 
    # GPFModelerGraphicItem
    def paintModel(self, model):
        self.model = model
        # Inputs
        for inp in model.inputs.values():
            item = GPFModelerGraphicItem(inp, model)
            item.setFlag(QGraphicsItem.ItemIsMovable, True)
            item.setFlag(QGraphicsItem.ItemIsSelectable, True)
            self.addItem(item)
            item.setPos(inp.pos.x(), inp.pos.y())
            self.paramItems[inp.param.name] = item

        # We add the algs
        for alg in model.algs.values():
            item = GPFModelerGraphicItem(alg, model)
            item.setFlag(QGraphicsItem.ItemIsMovable, True)
            item.setFlag(QGraphicsItem.ItemIsSelectable, True)
            self.addItem(item)
            item.setPos(alg.pos.x(), alg.pos.y())
            self.algItems[alg.name] = item

        # And then the arrows
        for alg in model.algs.values():
            idx = 0
            for parameter in alg.algorithm.parameters:
                if not parameter.hidden:
                    if parameter.name in alg.params:
                        value = alg.params[parameter.name]
                    else:
                        value = None
                    sourceItems = self.getItemsFromParamValue(value)
                    for sourceItem, sourceIdx in sourceItems:
                        arrow = ModelerArrowItem(sourceItem, sourceIdx, self.algItems[alg.name], idx)
                        sourceItem.addArrow(arrow)
                        self.algItems[alg.name].addArrow(arrow)
                        arrow.updatePath()
                        self.addItem(arrow)
                    idx += 1
            for depend in alg.dependencies:
                arrow = ModelerArrowItem(self.algItems[depend], -1,
                                         self.algItems[alg.name], -1)
                self.algItems[depend].addArrow(arrow)
                self.algItems[alg.name].addArrow(arrow)
                arrow.updatePath()
                self.addItem(arrow)

        # And finally the outputs
        for alg in model.algs.values():
            outputs = alg.outputs
            outputItems = {}
            idx = 0
            for key in outputs:
                out = outputs[key]
                if out is not None:
                    item = GPFModelerGraphicItem(out, model)
                    item.setFlag(QGraphicsItem.ItemIsMovable, True)
                    item.setFlag(QGraphicsItem.ItemIsSelectable, True)
                    self.addItem(item)
                    pos = alg.outputs[key].pos
                    if pos is None:
                        pos = (alg.pos + QPointF(GPFModelerGraphicItem.BOX_WIDTH, 0)
                               + self.algItems[alg.name].getLinkPointForOutput(idx))
                    item.setPos(pos)
                    outputItems[key] = item
                    arrow = ModelerArrowItem(self.algItems[alg.name], idx, item,
                                             -1)
                    self.algItems[alg.name].addArrow(arrow)
                    item.addArrow(arrow)
                    arrow.updatePath()
                    self.addItem(arrow)
                    idx += 1
                else:
                    outputItems[key] = None
            self.outputItems[alg.name] = outputItems