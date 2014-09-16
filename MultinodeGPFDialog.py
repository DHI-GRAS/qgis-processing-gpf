"""
***************************************************************************
    MultinodeGPFDialog.py
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

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import QtCore, QtGui
from processing.modeler.ModelerUtils import ModelerUtils
from processing.modeler.Providers import Providers
from processing.gui.ParametersDialog import ParametersDialog
from processing.gui.InputLayerSelectorPanel import InputLayerSelectorPanel

# This class is not currently being used.
class MultinodeGPFDialog(ParametersDialog):
    def __init__(self, alg=None):
        QtGui.QDialog.__init__(self)
        self.setupUi()
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowSystemMenuHint |
                            QtCore.Qt.WindowMinMaxButtonsHint)
        
        # list of algorithms (nodes) in the GPF
        self.algList = []
        
#        if alg:
#            self.alg = alg
#            self.textGroup.setText(alg.group)
#            self.textName.setText(alg.name)
#            self.repaintModel()
#            last = self.scene.getLastAlgorithmItem()
#            if last:
#                self.view.ensureVisible(last)
#        else:
#            self.alg = ModelerAlgorithm()
#        self.alg.setModelerView(self)

        self.help = None
        self.update = False #indicates whether to update or not the toolbox after closing this dialog
        self.executed = False

    def setupUi(self):
        self.resize(1000, 600)
        self.setWindowTitle("Multi node GPF creator")
        self.tabWidget = QtGui.QTabWidget()
        self.tabWidget.setMaximumSize(QtCore.QSize(350, 10000))
        self.tabWidget.setMinimumWidth(300)
        
        #left hand side part
        #==================================
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setSpacing(2)
        self.verticalLayout.setMargin(0)
        self.searchBox = QtGui.QLineEdit()
        self.searchBox.textChanged.connect(self.fillAlgorithmTree)
        self.verticalLayout.addWidget(self.searchBox)
        self.algorithmTree = QtGui.QTreeWidget()
        self.algorithmTree.setHeaderHidden(True)
        self.fillAlgorithmTree()
        self.verticalLayout.addWidget(self.algorithmTree)
        self.algorithmTree.doubleClicked.connect(self.addAlgorithm)

        self.algorithmsTab = QtGui.QWidget()
        self.algorithmsTab.setLayout(self.verticalLayout)
        self.tabWidget.addTab(self.algorithmsTab, "Algorithms")

        #right hand side part
        #==================================
        self.textName = QtGui.QLineEdit()
        if hasattr(self.textName, 'setPlaceholderText'):
            self.textName.setPlaceholderText("[Enter model name here]")
        self.textGroup = QtGui.QLineEdit()
        if hasattr(self.textGroup, 'setPlaceholderText'):
            self.textGroup.setPlaceholderText("[Enter group name here]")
        self.horizontalLayoutNames = QtGui.QHBoxLayout()
        self.horizontalLayoutNames.setSpacing(2)
        self.horizontalLayoutNames.setMargin(0)
        self.horizontalLayoutNames.addWidget(self.textName)
        self.horizontalLayoutNames.addWidget(self.textGroup)

        self.canvasTabWidget = QtGui.QTabWidget()
        self.canvasTabWidget.setMinimumWidth(300)

        self.canvasLayout = QtGui.QVBoxLayout()
        self.canvasLayout.setSpacing(2)
        self.canvasLayout.setMargin(0)
        self.canvasLayout.addLayout(self.horizontalLayoutNames)
        self.canvasLayout.addWidget(self.canvasTabWidget)

        #upper part, putting the two previous parts together
        #===================================================
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setSpacing(2)
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.addWidget(self.tabWidget)
        self.horizontalLayout.addLayout(self.canvasLayout)

        #And the whole layout
        #==========================

        self.progress = QtGui.QProgressBar()
        self.progress.setMinimum(0)
        self.progress.setMaximum(100)
        self.progress.setValue(0)

        self.buttonBox = QtGui.QDialogButtonBox()
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.runButton = QtGui.QPushButton()
        self.runButton.setText("Run")
        self.buttonBox.addButton(self.runButton, QtGui.QDialogButtonBox.ActionRole)
        #self.openButton = QtGui.QPushButton()
        #self.openButton.setText("Open")
        #self.buttonBox.addButton(self.openButton, QtGui.QDialogButtonBox.ActionRole)
        #self.saveButton = QtGui.QPushButton()
        #self.saveButton.setText("Save")
        #self.buttonBox.addButton(self.saveButton, QtGui.QDialogButtonBox.ActionRole)
        self.closeButton = QtGui.QPushButton()
        self.closeButton.setText("Close")
        self.buttonBox.addButton(self.closeButton, QtGui.QDialogButtonBox.ActionRole)
        #QObject.connect(self.openButton, QtCore.SIGNAL("clicked()"), self.openModel)
        #QObject.connect(self.saveButton, QtCore.SIGNAL("clicked()"), self.saveModel)
        QObject.connect(self.closeButton, QtCore.SIGNAL("clicked()"), self.closeWindow)
        QObject.connect(self.runButton, QtCore.SIGNAL("clicked()"), self.runModel)
        
        self.globalLayout = QtGui.QVBoxLayout()
        self.globalLayout.setSpacing(2)
        self.globalLayout.setMargin(0)
        self.globalLayout.addLayout(self.horizontalLayout)
        self.globalLayout.addWidget(self.progress)
        self.globalLayout.addWidget(self.buttonBox)
        self.setLayout(self.globalLayout)
        QtCore.QMetaObject.connectSlotsByName(self)

    def closeWindow(self):
        self.close()

    #===========================================================================
    # def createScript(self):
    #    if str(self.textGroup.text()).strip() == "":
    #        QMessageBox.warning(self, "Warning", "Please enter group name before saving")
    #        return
    #    filename = QtGui.QFileDialog.getSaveFileName(self, "Save Script", ScriptUtils.scriptsFolder(), "Python scripts (*.py)")
    #    if filename:
    #        fout = open(filename, "w")
    #        fout.write(str(self.textGroup.text()) + "=group")
    #        fout.write(self.alg.getAsPythonCode())
    #        fout.close()
    #        self.update = True
    #===========================================================================

    def runModel(self):
      #  if self.algList.__len__() > 0:
      #      self.algList[self.algList.__len__()-1].execute(self.progress)
      #  else:
      #      None        
#        ##TODO: enable alg cloning without saving to file
#        if self.alg.descriptionFile is None:
#            self.alg.descriptionFile = ProcessingUtils.getTempFilename("model")
#            text = self.alg.serialize()
#            fout = open(self.alg.descriptionFile, "w")
#            fout.write(text)
#            fout.close()
#            self.alg.provider = Providers.providers["model"]
#            alg = self.alg.getCopy()
#            dlg = ParametersDialog(alg)
#            dlg.exec_()
#            self.alg.descriptionFile = None
#            alg.descriptionFile = None
#        else:
#            if self.alg.provider is None: # might happen if model is opened from modeler dialog
#                self.alg.provider = Providers.providers["model"]
#            alg = self.alg.getCopy()
#            dlg = ParametersDialog(alg)

        # Go through all the tabs in the dialog, set the parameters for all of them and then
        # execute the last one. The GPF will be created with all the previous nodes.
        parametersDialogList = self.canvasTabWidget.findChildren(ParametersDialog)       
        for dialog in parametersDialogList:
            dialog.ui.setParamValues()   
        parametersDialogList[parametersDialogList.__len__()-1].ui.accept()
        parametersDialogList[parametersDialogList.__len__()-1].repaint()
        self.canvasTabWidget.repaint()
        

#    def saveModel(self):
#        if str(self.textGroup.text()).strip() == "" or str(self.textName.text()).strip() == "":
#            QMessageBox.warning(self, "Warning", "Please enter group and model names before saving")
#            return
#        self.alg.setPositions(self.scene.getParameterPositions(), self.scene.getAlgorithmPositions())
#        self.alg.name = str(self.textName.text())
#        self.alg.group = str(self.textGroup.text())
#        if self.alg.descriptionFile != None:
#            filename = self.alg.descriptionFile
#        else:
#            filename = str(QtGui.QFileDialog.getSaveFileName(self, "Save Model", ModelerUtils.modelsFolder(), "SEXTANTE models (*.model)"))
#            if filename:
#                if not filename.endswith(".model"):
#                    filename += ".model"
#                self.alg.descriptionFile = filename
#        if filename:
#            text = self.alg.serialize()
#            fout = open(filename, "w")
#            fout.write(text)
#            fout.close()
#            self.update = True
#            #if help strings were defined before saving the model for the first time, we do it here
#            if self.help:
#                f = open(self.alg.descriptionFile + ".help", "wb")
#                pickle.dump(self.help, f)
#                f.close()
#                self.help = None
#            QtGui.QMessageBox.information(self, "Model saving", "Model was correctly saved.")
#
#    def openModel(self):
#        filename = QtGui.QFileDialog.getOpenFileName(self, "Open Model", ModelerUtils.modelsFolder(), "SEXTANTE models (*.model)")
#        if filename:
#            try:
#                alg = ModelerAlgorithm()
#                alg.openModel(filename)
#                self.alg = alg;
#                self.alg.setModelerView(self)
#                self.textGroup.setText(alg.group)
#                self.textName.setText(alg.name)
#                self.repaintModel()
#                self.view.ensureVisible(self.scene.getLastAlgorithmItem())
#            except WrongModelException, e:
#                QMessageBox.critical(self, "Could not open model", "The selected model could not be loaded\nWrong line:" + e.msg)
#
#
#    def repaintModel(self):
#        self.scene = ModelerScene()
#        self.scene.setSceneRect(QtCore.QRectF(0, 0, 4000, 4000))
#        self.scene.paintModel(self.alg)
#        self.view.setScene(self.scene)
#        #self.pythonText.setText(self.alg.getAsPythonCode())

    def addAlgorithm(self):
        item = self.algorithmTree.currentItem()
        if isinstance(item, TreeAlgorithmItem):
            alg = ModelerUtils.getAlgorithm(item.alg.commandLineName())
            alg = alg.getCopy()#copy.deepcopy(alg)
            
            # let the algorithm know what the previous alg in the GPF graph was
            if self.algList.__len__() > 0:
                alg.previousAlgInGraph = self.algList[self.algList.__len__()-1]
            
            # create a tab for this algorithm
            algDialog = ParametersDialog(alg)
            # add previous alg nodes to the drop down lists for raster selection panels
            panelList = algDialog.paramTable.findChildren(InputLayerSelectorPanel)
            for panel in panelList:
                comboBox = panel.text
                for algorithm in self.algList:
                    comboBox.addItem(algorithm.nodeID, algorithm.nodeID)            
            algDialog.buttonBox.hide()
            algDialog.progress.hide()
            algDialog.progress = self.progress
            self.canvasTabWidget.addTab(algDialog, alg.appkey)
            
            # add this alg to the list 
            self.algList.append(alg)
        

    def fillAlgorithmTree(self):
        self.algorithmTree.clear()
        text = str(self.searchBox.text())
        allAlgs = ModelerUtils.getAlgorithms()
        for providerName in allAlgs.keys():
            groups = {}
            provider = allAlgs[providerName]
            algs = provider.values()
            # only add BEAM algorithms
            if providerName == "beam":
                for alg in algs:
                    if text == "" or text.lower() in alg.name.lower():
                        if alg.group in groups:
                            groupItem = groups[alg.group]
                        else:
                            groupItem = QtGui.QTreeWidgetItem()
                            groupItem.setText(0, alg.group)
                            groups[alg.group] = groupItem
                        algItem = TreeAlgorithmItem(alg)
                        groupItem.addChild(algItem)
    
                if len(groups) > 0:
                    providerItem = QtGui.QTreeWidgetItem()
                    providerItem.setText(0, Providers.providers[providerName].getDescription())
                    providerItem.setIcon(0, Providers.providers[providerName].getIcon())
                    for groupItem in groups.values():
                        providerItem.addChild(groupItem)
                    self.algorithmTree.addTopLevelItem(providerItem)
                    providerItem.setExpanded(True)
                    for groupItem in groups.values():
                        if text != "":
                            groupItem.setExpanded(True)

        self.algorithmTree.sortItems(0, Qt.AscendingOrder)


class TreeAlgorithmItem(QtGui.QTreeWidgetItem):

    def __init__(self, alg):
        QTreeWidgetItem.__init__(self)
        self.alg = alg
        self.setText(0, alg.name)
        self.setIcon(0, alg.getIcon())


