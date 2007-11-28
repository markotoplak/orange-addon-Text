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
    settingsList=["lowerCase", "stopWords", "lematizer"]

    def __init__(self, parent=None, signalManager=None):
        OWWidget.__init__(self,parent,signalManager,"Preprocess")
        self.langDict = {0: 'bg', 1: 'cs', 2: 'en', 3: 'es', 4: 'et', 5: 'fr',
            6: 'ge', 7: 'hr', 8: 'hu', 9: 'it', 10: 'ro', 11: 'sl', 12: 'sr'}
        self.selectedLanguage = 0
        #OWWidget.__init__(self,parent,"Rules")
        self.inputs = [("Example Table", ExampleTable, self.dataset)]
        self.outputs = [("Example Table", ExampleTable)]

        self.lowerCase = self.stopWords = self.lematizer = True
        self.textAttribute = "-"
        self.nDocuments = "-"
        self.data = None
        
        self.loadSettings()

        box = OWGUI.widgetBox(self.controlArea, "Options", addSpace = True)
        OWGUI.checkBox(box, self, "lowerCase", "Convert to lower case")
        OWGUI.checkBox(box, self, "stopWords", "Remove stop words")
        OWGUI.checkBox(box, self, "lematizer", "Lematize")
        OWGUI.radioButtonsInBox(self.controlArea, self, "selectedLanguage", box = "Language",
            btnLabels = ["Bulgarian", "Czech", "English", "Spanish",
            "Estonian", "French", "German", "Croatian", "Hungarian", 
            "Italian", "Romanian", "Slovenian", "Serbian"], addSpace = True)

        box = OWGUI.widgetBox(self.controlArea, "Info", addSpace = True)
        OWGUI.label(box, self, "Number of documents: %(nDocuments)s")
        OWGUI.label(box, self, "Text attribute: %(textAttribute)s")

        OWGUI.button(self.controlArea, self, "Apply", self.apply)

        self.adjustSize()        
        

    def dataset(self, data):
        if data:
            for i in range(1, len(data.domain.attributes)+1):
                if data.domain.attributes[-i]:
                    self.textAttributePos = len(data.domain.attributes) - i
                    self.textAttribute = data.domain.attributes[-i].name
                    self.nDocuments = len(data)
                    self.data = data
                    self.error()
                    break
            else:
                self.error("The data has no string attributes")
                self.textAttribute = "-"
                self.nDocuments = "-"
                self.data = None
        else:
            self.textAttribute = "-"
            self.nDocuments = "-"
            self.data = None

        self.apply()

    def apply(self):
        if self.data:
            it = len(self.data) * (0 + self.lowerCase + self.stopWords + self.lematizer)
            pb = OWGUI.ProgressBar(self, iterations=it)
            newData = orange.ExampleTable(orange.Domain(self.data.domain), self.data)
            preprocess = orngText.Preprocess(language = self.langDict[self.selectedLanguage])
            if self.lowerCase:
                newData = preprocess.doOnExampleTable(newData, self.textAttributePos, preprocess.lowercase, callback=pb.advance)
            if self.stopWords:
                newData = preprocess.removeStopwordsFromExampleTable(newData, self.textAttributePos, callback=pb.advance)
            if self.lematizer:
                newData = preprocess.lemmatizeExampleTable(newData, self.textAttributePos, callback=pb.advance)
            pb.finish()
        else:
            newData = None
        self.send("Example Table", newData)


if __name__ == "__main__":
    a = QApplication(sys.argv)
    ow = OWTextPreprocess()
    a.setMainWidget(ow)
    ow.show()
    a.exec_loop()
