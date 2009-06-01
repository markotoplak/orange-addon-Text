"""
<name>Feature Selection</name>
<description>Removes features from the data according to given criteria.</description>
<icon>icons/TextFeatureSelection.png</icon>
<contact>Sasa Petrovic</contact> 
<priority>1500</priority>
"""

from OWWidget import *
from copy import deepcopy
import OWGUI, orngText, warnings

class OWTextFeatureSelection(OWWidget):    

    def __init__(self, parent=None, signalManager=None):
        OWWidget.__init__(self,parent,signalManager,"FeatureSelection")
        self.inputs = [("Example Table", ExampleTable, self.dataset)]
        self.outputs = [("Example Table", ExampleTable)]

        warnings.filterwarnings("ignore", "", orange.AttributeWarning)
        
        self.data = None
        self.chosenMeasure = [0]
        self.measures = ['Term frequency', 'Random', 'Term document frequency', 'Word frequency', 'Number of features']
        self.chosenOp = [0]
        self.measureDict = {0: 'TF', 1: 'RAND', 2: 'TDF', 3: 'WF', 4: 'NF'}
        self.operators = ['MIN', 'MAX']
        self.tmpData = None
        self.perc = 1
        self.threshold = 90
        self.selections = []

        #GUI
        #ca=QFrame(self.controlArea)
        #gl=QGridLayout(ca)
        selectionbox = OWGUI.widgetBox(self.controlArea, "Feature selection", "horizontal") #OWGUI.QHGroupBox('Feature selection', self.controlArea)

        OWGUI.listBox(selectionbox, self, 'chosenMeasure', 'measures', box = 'Select measure', callback = self.selectionChanged)
        OWGUI.listBox(selectionbox, self, 'chosenOp', 'operators', box = 'Select operator', callback = self.selectionChanged)

        boxAttrStat = OWGUI.widgetBox(self.controlArea, "Statistics for features") #QVGroupBox("Statistics for features", self.controlArea)
        self.lblFeatNo = OWGUI.widgetLabel(boxAttrStat, "No. of features: ") #QLabel("No. of features: ", boxAttrStat)
        self.lblMin = OWGUI.widgetLabel(boxAttrStat, "Min: ") #QLabel("Min: ", boxAttrStat)
        self.lblAvg = OWGUI.widgetLabel(boxAttrStat, "Avg: ") #QLabel("Avg: ", boxAttrStat)
        self.lblMax = OWGUI.widgetLabel(boxAttrStat, "Max: ") #QLabel("Max: ", boxAttrStat)

        boxDocStat = OWGUI.widgetBox(self.controlArea, "Statistics for documents") #QVGroupBox("Statistics for documents", self.controlArea)
        self.lblDocNo = OWGUI.widgetLabel(boxDocStat, "No. of documents: ") #QLabel("No. of documents: ", boxDocStat)
        self.lblDocAvg = OWGUI.widgetLabel(boxDocStat, "Avg: ") #QLabel("Avg: ", boxDocStat)
        self.lblDocMax = OWGUI.widgetLabel(boxDocStat, "Max: ") #QLabel("Max: ", boxDocStat)
        self.lblDocMin = OWGUI.widgetLabel(boxDocStat, "Min: ") #QLabel("Min: ", boxDocStat)

        optionBox = OWGUI.widgetBox(selectionbox, "") #OWGUI.QVGroupBox('', selectionbox)        

        self.applyButton = OWGUI.button(optionBox, self, "Apply", self.apply)
        self.applyButton.setDisabled(1)
        OWGUI.checkBox(optionBox, self, "perc", "percentage", callback = self.selectionChanged)
        #OWGUI.spin(optionBox, self, "threshold", 0, 10000, label="Threshold:", callback = None)
        OWGUI.lineEdit(optionBox, self, "threshold", orientation="horizontal", valueType=float, box="Threshold", callback = self.selectionChanged)
        OWGUI.rubber(self.controlArea)
        self.controlArea.adjustSize()


    def apply(self):
        pb = OWGUI.ProgressBar(self, iterations=3)
        pb.advance()
        if self.measureDict[self.chosenMeasure[0]] == 'WF' or self.measureDict[self.chosenMeasure[0]] == 'NF':
            #self.data = orngText.DSS(self.data, self.measures[self.chosenMeasure[0]], self.operators[self.chosenOp[0]], self.threshold)
            self.data = orngText.DSS(self.tmpData, self.measureDict[self.chosenMeasure[0]], self.operators[self.chosenOp[0]], self.threshold, callback=pb.advance)
        else:
            #self.data = orngText.FSS(self.data, self.measures[self.chosenMeasure[0]], self.operators[self.chosenOp[0]], self.threshold, self.perc)
            self.data = orngText.FSS(self.tmpData, self.measureDict[self.chosenMeasure[0]], self.operators[self.chosenOp[0]], self.threshold, self.perc, callback=pb.advance)
        self.selections.append(self.measureDict[self.chosenMeasure[0]] + ' ' + self.operators[self.chosenOp[0]] + ' ' + str(self.threshold) + ' percentage=' + str(self.perc))
        self.data.selection = deepcopy(self.selections)
        self.send("Example Table", self.data)
        pb.finish()
        self.computeStatistics()
        self.applyButton.setDisabled(1)

    def dataset(self, data):
        if data:
            self.selections = []
            self.data = orange.ExampleTable(data)
            self.tmpData = orange.ExampleTable(data)
            self.tmpDom = orange.Domain(data.domain)
            #self.computeStatistics()
            self.apply()
            self.applyButton.setDisabled(1)
        else:
            self.data = None
            self.tmpData = None
            self.lblDocNo.setText("No. of documents: 0")
            self.lblDocAvg.setText("Avg: 0")
            self.lblDocMax.setText("Max: 0")
            self.lblDocMin.setText("Min: 0")
            self.lblFeatNo.setText("No. of features: 0")
            self.lblMin.setText("Min: 0  Min word = 0")
            self.lblMax.setText("Max: 0  Max word = 0")
            self.lblAvg.setText("Avg: 0.0")
            self.applyButton.setDisabled(1)
            self.send("Example Table", None)

    def computeStatistics(self):
        docNo = len(self.data)
        if not docNo:
            docNo = 1
        self.lblDocNo.setText("No. of documents: %d" % docNo)
        #compute document statistics        
        #max = min = len(self.data[0].getmetas())
        pb = OWGUI.ProgressBar(self, iterations=2 * docNo)
        max = 0
        min = ()
        sum = 0
        for doc in self.data:
            featNo = len(doc.getmetas(orngText.TEXTMETAID))
            sum += featNo
            if featNo > max:
                max = featNo
            if featNo < min:
                min = featNo
            pb.advance()
        avg = sum / docNo
        if min == ():
            min = 0
        self.lblDocAvg.setText("Avg: %.3f" % avg)
        self.lblDocMax.setText("Max: %d" % max)
        self.lblDocMin.setText("Min: %d" % min)

        #compute feature statistics
        words = {}
        sum = 0
        if not self.data.domain.getmetas(orngText.TEXTMETAID) or not self.data:
          self.lblFeatNo.setText("No. of features: 0")
          self.lblMin.setText("Min: %d  Min word = 0")
          self.lblMax.setText("Max: %d  Max word = 0")
          self.lblAvg.setText("Avg: 0.0")
          return
        max = 0
        min = ()
        maxword = minword = ''
        
        for ex in self.data:
            for v in ex.getmetas(orngText.TEXTMETAID).values():
                varname = v.variable.name
                if words.has_key(varname):
                    words[varname] += v.value
                else:
                    words[varname] = v.value
            pb.advance()
        pb.finish()

        pb = OWGUI.ProgressBar(self, iterations = len(words))
        for word,freq in words.items():
            if freq > max:
                max = freq
                maxword = word
            if freq < min:
                min = freq
                minword = word
            sum += freq
            pb.advance()
        avg = sum / len(words)
        if min == ():
            min = 0
        self.lblFeatNo.setText("No. of features: %d" % len(words))
        self.lblMin.setText("Min: %d  Min word = %s" % (min, minword))
        self.lblMax.setText("Max: %d  Max word = %s" % (max,maxword))
        self.lblAvg.setText("Avg: %.3f" % avg)
        pb.finish()

    def selectionChanged(self):
        if self.data:
            self.applyButton.setDisabled(0)


if __name__ == "__main__":
    a = QApplication(sys.argv)
    t = orngText.loadFromXML(r'c:\test\orange\msnbc.xml')
    t2 = orngText.extractLetterNGram(t)
    #print t2.domain.getmetas().values()
    ow = OWTextFeatureSelection()
    a.setMainWidget(ow)
    ow.show()
    ow.dataset(t2)
    a.exec_loop()
