import codecs
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QMessageBox, QTreeWidget, QTreeWidgetItem, QFileDialog
from processing.modeler.ModelerDialog import ModelerDialog, TreeAlgorithmItem
from processing.gui.HelpEditionDialog import HelpEditionDialog
from processing.gui.AlgorithmDialog import AlgorithmDialog
from processing.core.ProcessingLog import ProcessingLog
from processing.modeler.WrongModelException import WrongModelException
from processing_gpf.GPFModelerAlgorithm import GPFModelerAlgorithm
from processing_gpf.GPFUtils import GPFUtils

class GPFModelerDialog(ModelerDialog):
    
    def __init__(self, gpfAlgorithmProvider, alg=None):
        self.gpfAlgorithmProvider = gpfAlgorithmProvider
        ModelerDialog.__init__(self, alg)
        if alg is None:
            self.alg = GPFModelerAlgorithm(gpfAlgorithmProvider)
            self.alg.modelerdialog = self
    
    def editHelp(self):
        if self.alg.provider is None:
            # Might happen if model is opened from modeler dialog
            self.alg.provider = self.gpfAlgorithmProvider
        alg = self.alg.getCopy()
        dlg = HelpEditionDialog(alg)
        dlg.exec_()
        if dlg.descriptions:
            self.hasChanged = True
            
    def runModel(self):
        if len(self.alg.algs) == 0:
            QMessageBox.warning(self, self.tr('Empty model'),
                    self.tr("Model doesn't contains any algorithms and/or "
                            "parameters and can't be executed"))
            return

        if self.alg.provider is None:
            # Might happen if model is opened from modeler dialog
            self.alg.provider = self.gpfAlgorithmProvider
        alg = self.alg.getCopy()
        dlg = AlgorithmDialog(alg)
        dlg.exec_()
        
    def fillAlgorithmTree(self):
        
        self.fillAlgorithmTreeUsingProviders()

        self.algorithmTree.sortItems(0, Qt.AscendingOrder)

        text = unicode(self.searchBox.text())
        if text != '':
            self.algorithmTree.expandAll()
            
    def fillAlgorithmTreeUsingProviders(self):
        self.algorithmTree.clear()
        text = unicode(self.searchBox.text())
        groups = {}
        
        # Add only GPF algorithms
        for alg in self.gpfAlgorithmProvider.algs:
            if not alg.showInModeler or alg.allowOnlyOpenedLayers:
                continue
            if text == '' or text.lower() in alg.name.lower():
                if alg.group in groups:
                    groupItem = groups[alg.group]
                else:
                    groupItem = QTreeWidgetItem()
                    groupItem.setText(0, alg.group)
                    groupItem.setToolTip(0, alg.group)
                    groups[alg.group] = groupItem
                algItem = TreeAlgorithmItem(alg)
                groupItem.addChild(algItem)

        if len(groups) > 0:
            providerItem = QTreeWidgetItem()
            providerItem.setText(0,
                    self.gpfAlgorithmProvider.getDescription())
            providerItem.setToolTip(0,
                    self.gpfAlgorithmProvider.getDescription())
            providerItem.setIcon(0,
                    self.gpfAlgorithmProvider.getIcon())
            for groupItem in groups.values():
                providerItem.addChild(groupItem)
            self.algorithmTree.addTopLevelItem(providerItem)
            providerItem.setExpanded(text != '')
            for groupItem in groups.values():
                if text != '':
                    groupItem.setExpanded(True)

        self.algorithmTree.sortItems(0, Qt.AscendingOrder)
        
    def openModel(self):
        filename = unicode(QFileDialog.getOpenFileName(self,
                           self.tr('Open GPF Model'), GPFUtils.modelsFolder(),
                           self.tr('GPF models (*.xml *.XML)')))
        if filename:
            try:
                alg = GPFModelerAlgorithm.fromFile(filename, self.gpfAlgorithmProvider)
                self.alg = alg
                self.alg.setModelerView(self)
                self.textGroup.setText(alg.group)
                self.textName.setText(alg.name)
                self.repaintModel()
    
                self.view.centerOn(0, 0)
                self.hasChanged = False
                
            except WrongModelException, e:
                ProcessingLog.addToLog(ProcessingLog.LOG_ERROR,
                    self.tr('Could not load model %s\n%s') % (filename, e.msg))
                QMessageBox.critical(self, self.tr('Could not open model'),
                        self.tr('The selected model could not be loaded.\n'
                                'See the log for more information.'))
            except Exception, e:
                ProcessingLog.addToLog(ProcessingLog.LOG_ERROR,
                    self.tr('Could not load model %s\n%s') % (filename, e.args[0]))
                QMessageBox.critical(self, self.tr('Could not open model'),
                    self.tr('The selected model could not be loaded.\n'
                            'See the log for more information.'))
            
                
            
    def saveModel(self, saveAs):
        if unicode(self.textGroup.text()).strip() == '' \
                or unicode(self.textName.text()).strip() == '':
            QMessageBox.warning(
                self, self.tr('Warning'), self.tr('Please enter group and model names before saving')
            )
            return
        self.alg.name = unicode(self.textName.text())
        self.alg.group = unicode(self.textGroup.text())
        if self.alg.descriptionFile is not None and not saveAs:
            filename = self.alg.descriptionFile
        else:
            filename = unicode(QFileDialog.getSaveFileName(self,
                               self.tr('Save GPF Model'),
                               GPFUtils.modelsFolder(),
                               self.tr('GPF models (*.xml)')))
            if filename:
                if not filename.endswith('.xml'):
                    filename += '.xml'
                self.alg.descriptionFile = filename
        if filename:
            text = self.alg.toXml()
            if not text:
                return
            try:
                fout = codecs.open(filename, 'w', encoding='utf-8')
            except:
                if saveAs:
                    QMessageBox.warning(self, self.tr('I/O error'),
                            self.tr('Unable to save edits. Reason:\n %s') % unicode(sys.exc_info()[1]))
                else:
                    QMessageBox.warning(self, self.tr("Can't save model"),
                            self.tr("This model can't be saved in its "
                                    "original location (probably you do not "
                                    "have permission to do it). Please, use "
                                    "the 'Save as...' option."))
                return
            fout.write(text)
            fout.close()
            self.update = True
            QMessageBox.information(self, self.tr('Model saved'),
                                    self.tr('Model was correctly saved.'))

            self.hasChanged = False