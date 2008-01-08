"""
<name>Bag of Words</name>
<description>Computes bag of words from text files and optionally also normalizes them.</description>
<icon>icons/BagOfWords.png</icon>
<contact></contact> 
<priority>1300</priority>
"""

from OWWidget import *
import OWGUI, orngText

class OWBagofWords(OWWidget):
    settingsList=["TFIDF", "norm"]

    def __init__(self, parent=None, signalManager=None):
        OWWidget.__init__(self,parent,signalManager,"BagofWords")
        self.inputs = [("Example Table", ExampleTable, self.dataset)]
        self.outputs = [("Example Table", ExampleTable)]

        self.TFIDF = 0
        self.norm = 0
        self.textAttribute = "-"
        self.nDocuments = "-"
        self.nWords = "-"
        self.data = None
        
        self.loadSettings()

        OWGUI.radioButtonsInBox(self.controlArea, self, "TFIDF", ["None", "log(1/f)"], "TFIDF", addSpace = True)
        OWGUI.radioButtonsInBox(self.controlArea, self, "norm", ["None", "L1 (Sum of elements)", "L2 (Euclidean)"], "Normalization", addSpace = True)

        box = OWGUI.widgetBox(self.controlArea, "Info", addSpace = True)
        OWGUI.label(box, self, "Number of documents: %(nDocuments)s")
        OWGUI.label(box, self, "Number of words: %(nWords)s")
        OWGUI.label(box, self, "Text attribute: %(textAttribute)s")
        
        box = OWGUI.widgetBox(self.controlArea, "Text attribute", addSpace = True)
        self.textAttributePos = None
        self.attributesCombo = OWGUI.comboBox(box, self, "textAttributePos", callback = self.setTextAttribute)


        OWGUI.button(self.controlArea, self, "Apply", self.apply)

        self.adjustSize()        
        

    def dataset(self, data):
        if data:
            self.textAttributePos = None
            for i in range(0, len(data.domain.attributes)):
                if isinstance(data.domain.attributes[i], orange.StringVariable):
                    self.attributesCombo.insertItem(data.domain.attributes[i].name)
                    self.textAttributePos = i
            if self.textAttributePos == None:
                #if no attribute is chosen as text attribute, then take the one named "text"
                for i in range(0, len(data.domain.attributes)):
                    if data.domain.attributes[i].name == "text":
                        #self.textAttributePos = len(data.domain.attributes) - i
                        #self.textAttribute = data.domain.attributes[-i].name
                        self.textAttribute = "text"
                        self.textAttributePos = i
                        self.nDocuments = len(data)
                        self.data = data
                        self.error()
                        break
                else:
                    self.error("The data has no string attributes")
                    self.textAttribute = "-"
                    self.nDocuments = "-"
                    self.nWords = "-"
                    self.data = None
            else:
                self.data = data
                self.nDocuments = len(data)
        else:
            self.textAttribute = "-"
            self.nDocuments = "-"
            self.nWords = "-"
            self.data = None

        self.apply()

    def apply(self):
        self.send("Example Table", None)
        if self.data:
            it = len(self.data)
            if self.norm:
                it += len(self.data)
            if self.TFIDF:
                it += len(self.data)
            pb = OWGUI.ProgressBar(self, iterations=it)
            newdata = orngText.bagOfWords(self.data, textAttributePos=self.textAttributePos, callback=pb.advance)
            if self.norm:
                newdata = orngText.Preprocessor_norm()(newdata, self.norm, callback=pb.advance)
            if self.TFIDF:
                newdata = orngText.PreprocessorConstructor_tfidf()(newdata)(newdata)
            self.send("Example Table", newdata)
            self.nWords = len(newdata.domain.getmetas(orngText.TEXTMETAID))
            pb.finish()
        else:
            self.send("Example Table", None)

    def setTextAttribute(self):
        #this is necessary if not all attributes are string attributes. In that case,
        #the value in the combo box does not correspond to the index of the attribute
        #and we have to use this function to determine it
        if not self.data: return
        name = self.attributesCombo.currentText()
        for i in range (len(self.data.domain.attributes)):
            if self.data.domain.attributes[i].name == name:
                self.textAttributePos = i
                self.textAttribute = name
                break

if __name__ == "__main__":
    t = orngText.loadFromXML(r'c:\test\orange\msnbc.xml')
    a = QApplication(sys.argv)
    ow = OWBagofWords()
    ow.data = t
    a.setMainWidget(ow)
    ow.show()
    a.exec_loop()
