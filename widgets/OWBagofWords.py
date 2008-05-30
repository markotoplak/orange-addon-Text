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
    contextHandlers = {"": DomainContextHandler("", [ContextField("textAttribute", DomainContextHandler.Required)])}
    settingsList=["TFIDF", "norm"]

    def __init__(self, parent=None, signalManager=None):
        OWWidget.__init__(self,parent,signalManager,"BagofWords")
        self.inputs = [("Example Table", ExampleTable, self.dataset)]
        self.outputs = [("Bag-of-Words", ExampleTable)]

        self.TFIDF = 0
        self.norm = 0
        self.nDocuments = "N/A"; self.nStrAttributes = "N/A"; self.nWords = "N/A"
        self.textAttribute = None
        self.data = None
        
        self.loadSettings()

        box = OWGUI.widgetBox(self.controlArea, "Info", addSpace = True)
        OWGUI.label(box, self, "Documents: %(nDocuments)s")
        OWGUI.label(box, self, "String attributes: %(nStrAttributes)s")
        OWGUI.label(box, self, "Words: %(nWords)s")

        OWGUI.radioButtonsInBox(self.controlArea, self, "TFIDF", ["None", "log(1/f)"], "TFIDF", addSpace = True)
        OWGUI.radioButtonsInBox(self.controlArea, self, "norm", ["None", "L1 (Sum of elements)", "L2 (Euclidean)"], "Normalization", addSpace = True)
        
        self.attributesCombo = OWGUI.comboBox(self.controlArea, self, "textAttribute", box="Text attribute", callback=self.apply)
        self.adjustSize()        
        
    def dataset(self, data):
        self.closeContext()
        if data:
            self.textAttribute = None
            k = 0
            for (indx, att) in enumerate(data.domain.attributes):
                if isinstance(att, orange.StringVariable):
                    self.attributesCombo.insertItem(att.name)
                    self.textAttribute = indx
                    k += 1
            if not self.textAttribute:
                self.error("The data has no string attributes")
                self.nDocuments = "N/A"; self.nStrAttributes = "N/A"; self.nWords = "N/A"
                self.data = None
                self.send("Bag-of-Words", None)
                return
            self.nDocuments = len(data)
            self.nStrAttributes = k
        else:
            self.nDocuments = "N/A"; self.nStrAttributes = "N/A"; self.nWords = "N/A"
            self.send("Bag-of-words", None)
            self.data = data
            return
        self.error() # clear any error message
        self.data = data
        self.openContext("", data)
        self.apply()

    def apply(self):
        it = len(self.data)
        if self.norm:
            it += len(self.data)
        if self.TFIDF:
            it += len(self.data)
        pb = OWGUI.ProgressBar(self, iterations=it)
        newdata = orngText.bagOfWords(self.data, textAttribute=self.textAttribute, callback=pb.advance)
        if self.norm:
            newdata = orngText.Preprocessor_norm()(newdata, self.norm, callback=pb.advance)
        if self.TFIDF:
            newdata = orngText.PreprocessorConstructor_tfidf()(newdata)(newdata)
        self.send("Bag-of-Words", newdata)
        self.nWords = len(newdata.domain.getmetas(orngText.TEXTMETAID))
        pb.finish()

if __name__ == "__main__":
    a = QApplication(sys.argv)
    ow = OWBagofWords()
    ow.activateLoadedSettings()
    a.setMainWidget(ow)
    ow.show()

#   data = orngText.loadFromXML('r'c:\test\orange\msnbc.xml')
    data = orange.ExampleTable("tmp-pubmed-chemogenomics.tab")
    ow.dataset(data)
    a.exec_loop()
    ow.saveSettings()
