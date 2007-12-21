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
    settingsList=["lowerCase", "stopWords", "lematizer", "selectedLanguage"]

    def __init__(self, parent=None, signalManager=None):
        OWWidget.__init__(self,parent,signalManager,"Preprocess")
        self.langDict = {0: 'bg', 1: 'cs', 2: 'en', 3: 'es', 4: 'et', 5: 'fr',
            6: 'ge', 7: 'hr', 8: 'hu', 9: 'it', 10: 'ro', 11: 'sl', 12: 'sr'}
        self.selectedLanguage = 2
        #OWWidget.__init__(self,parent,"Rules")
        self.inputs = [("Example Table", ExampleTable, self.dataset)]
        self.outputs = [("Example Table", ExampleTable)]

        self.lowerCase = self.stopWords = self.lematizer = True
        self.textAttribute = "-"
        self.nDocuments = "-"
        self.data = None

        

        box = OWGUI.widgetBox(self.controlArea, "Options", addSpace = True)
        OWGUI.checkBox(box, self, "lowerCase", "Convert to lower case")
        OWGUI.checkBox(box, self, "stopWords", "Remove stop words")
        OWGUI.checkBox(box, self, "lematizer", "Lematize")
        
        btnLabels = ["Bulgarian", "Czech", "English", "Spanish", "Estonian", "French", "German", "Croatian", "Hungarian", "Italian", "Romanian", "Slovenian", "Serbian"]
        box = OWGUI.widgetBox(self.controlArea, "Language", addSpace = True)
        self.langCombo = OWGUI.comboBox(box, self, "selectedLanguage")
        for i in range(0, len(btnLabels)):
            self.langCombo.insertItem(QPixmap(os.path.dirname(__file__) + "/icons/" + self.langDict[i] +".png"), btnLabels[i])
        
        self.loadSettings()
        
        box = OWGUI.widgetBox(self.controlArea, "Text attribute", addSpace = True)
        self.textAttributePos = None
        self.attributesCombo = OWGUI.comboBox(box, self, "textAttributePos", callback = self.setTextAttribute)

        box = OWGUI.widgetBox(self.controlArea, "Info", addSpace = True)
        OWGUI.label(box, self, "Number of documents: %(nDocuments)s")
        OWGUI.label(box, self, "Text attribute: %(textAttribute)s")


        OWGUI.button(self.controlArea, self, "Apply", self.apply)

        self.adjustSize()       
        

    def dataset(self, data):
        if data:
            self.textAttributePos = None
            for i in range(0, len(data.domain.attributes)):
                if isinstance(data.domain.attributes[i], orange.StringVariable):
                    self.attributesCombo.insertItem(data.domain.attributes[i].name)
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
                    self.data = None
            else:
                self.data = data
                self.nDocuments = len(data)
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

    def setTextAttribute(self):
        #this is necessary if not all attributes are string attributes. In that case,
        #the value in the combo box does not correspond to the index of the attribute
        #and we have to use this function to determine it
        name = self.attributesCombo.currentText()
        for i in range (len(self.data.domain.attributes)):
            if self.data.domain.attributes[i].name == name:
                self.textAttributePos = i
                self.textAttribute = names
                break

if __name__ == "__main__":
    a = QApplication(sys.argv)
    ow = OWTextPreprocess()
    a.setMainWidget(ow)
    ow.show()
    a.exec_loop()
