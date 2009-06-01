"""
<name>Preprocess</name>
<description>Lower case, tokenizer and lematizer for text.</description>
<icon>icons/TextPreprocess.png</icon>
<contact></contact> 
<priority>1200</priority>
"""

from OWWidget import *
import orngText
import OWGUI

class OWTextPreprocess(OWWidget):
    contextHandlers = {"": DomainContextHandler("", [ContextField("textAttribute", DomainContextHandler.Required)])}
    settingsList=["lowerCase", "stopWords", "lematizer", "selectedLanguage"]

    def __init__(self, parent=None, signalManager=None):
        OWWidget.__init__(self,parent,signalManager,"Preprocess")

        self.inputs = [("Example Table", ExampleTable, self.dataset)]
        self.outputs = [("Example Table", ExampleTable)]

        self.langDict = {0: 'bg', 1: 'cs', 2: 'en', 3: 'es', 4: 'et', 5: 'fr',
            6: 'ge', 7: 'hr', 8: 'hu', 9: 'it', 10: 'ro', 11: 'sl', 12: 'sr'}
        self.selectedLanguage = 2
        self.lowerCase = self.stopWords = self.lematizer = True
        self.textAttribute = None
        self.nDocuments = "N/A"; self.nStrAttributes = "N/A"
        self.data = None

        self.loadSettings()

        box = OWGUI.widgetBox(self.controlArea, "Info", addSpace = True)
        OWGUI.label(box, self, "Documents: %(nDocuments)s")
        OWGUI.label(box, self, "String attributes: %(nStrAttributes)s")

        box = OWGUI.widgetBox(self.controlArea, "Options", addSpace = True)
        OWGUI.checkBox(box, self, "lowerCase", "Convert to lower case")
        OWGUI.checkBox(box, self, "stopWords", "Remove stop words")
        OWGUI.checkBox(box, self, "lematizer", "Lematize")
        
        btnLabels = ["Bulgarian", "Czech", "English", "Spanish", "Estonian", "French", "German", "Croatian", "Hungarian", "Italian", "Romanian", "Slovenian", "Serbian"]

        self.langCombo = OWGUI.comboBox(self.controlArea, self, "selectedLanguage", box="Language", addSpace=True)
        for (i, label) in enumerate(btnLabels):
            self.langCombo.addItem(QIcon(QPixmap(os.path.dirname(__file__) + "/icons/" + self.langDict[i] +".png")), label)
        self.langCombo.setCurrentIndex(self.selectedLanguage)
        
        self.attributesCombo = OWGUI.comboBox(self.controlArea, self, "textAttribute", box="Text attribute", callback=self.apply)
        OWGUI.rubber(self.controlArea)
        self.adjustSize()  
        
    def dataset(self, data):
        self.closeContext()
        if data:
            self.textAttribute = None
            k = 0
            for (indx, att) in enumerate(data.domain.attributes):
                if isinstance(att, orange.StringVariable):
                    self.attributesCombo.addItem(att.name)
                    self.textAttribute = indx
                    k += 1
            if self.textAttribute==None:
                self.error("The data has no string attributes")
                self.nDocuments = "N/A"; self.nStrAttributes = "N/A"
                self.data = None
                self.send("Example Table", None)
                return
            self.nDocuments = len(data)
            self.nStrAttributes = k
        else:
            self.nDocuments = "N/A"; self.nStrAttributes = "N/A"
        self.error() # clear any error message
        self.data = data
        self.openContext("", data)
        self.apply()

    def apply(self):
        if self.data:
            it = len(self.data) * (0 + self.lowerCase + self.stopWords + self.lematizer)
            pb = OWGUI.ProgressBar(self, iterations=it)
            newData = orange.ExampleTable(orange.Domain(self.data.domain), self.data)
            preprocess = orngText.Preprocess(language = self.langDict[self.selectedLanguage])
            if self.lowerCase:
                newData = preprocess.doOnExampleTable(newData, self.textAttribute, preprocess.lowercase, callback=pb.advance)
            if self.stopWords:
                newData = preprocess.removeStopwordsFromExampleTable(newData, self.textAttribute, callback=pb.advance)
            if self.lematizer:
                newData = preprocess.lemmatizeExampleTable(newData, self.textAttribute, callback=pb.advance)
            pb.finish()
        else:
            newData = None
        self.send("Example Table", newData)

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
    a = QApplication(sys.argv)
    ow = OWTextPreprocess()
    ow.activateLoadedSettings()
    a.setMainWidget(ow)
    ow.show()

#   data = orngText.loadFromXML('r'c:\test\orange\msnbc.xml')
    data = orange.ExampleTable("tmp-pubmed-chemogenomics.tab")
    ow.dataset(data)
    a.exec_loop()
    ow.saveSettings()
