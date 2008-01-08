"""
<name>Letter n-Grams</name>
<description>Computes the letter ngram representation.</description>
<icon>icons/LetterNgram.png</icon>
<contact>Sasa Petrovic</contact> 
<priority>1405</priority>
"""

from OWWidget import *
import OWGUI, orngText

class OWLetterNgram(OWWidget):
    settingsList = ["size"]

    def __init__(self, parent=None, signalManager=None):
        OWWidget.__init__(self,parent,signalManager,"LetterNgram")
        self.inputs = [("Example Table", ExampleTable, self.dataset)]
        self.outputs = [("Example Table", ExampleTable)]

        self.size = 0
        self.data = None
        
        self.loadSettings()
        
        OWGUI.radioButtonsInBox(self.controlArea, self, "size", box = "Ngram size", btnLabels = ["2", "3", "4"], addSpace = True)
        OWGUI.button(self.controlArea, self, "Apply", self.apply)
        self.lblFeatureNo = QLabel("\nNo. of features: ", self.controlArea)
        self.adjustSize()
        
        box = OWGUI.widgetBox(self.controlArea, "Text attribute", addSpace = True)
        self.textAttributePos = None
        self.attributesCombo = OWGUI.comboBox(box, self, "textAttributePos", callback = self.setTextAttribute)

        

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
                            self.data = orange.ExampleTable(data)
                            self.tmpData = orange.ExampleTable(data)
                            self.tmpDom = orange.Domain(data.domain) 
                            self.error()
                            break
                    else:
                        self.error("The data has no string attributes")
                        self.textAttribute = "-"
                        self.data = None
                else:
                    self.data = orange.ExampleTable(data)
                    self.tmpData = orange.ExampleTable(data)
                    self.tmpDom = orange.Domain(data.domain)            
        else:
            self.data = None
            self.tmpData = None
            self.textAttribute = "-"
            self.lblFeatureNo.setText("\nNo. of features: \n0")

        self.apply()

    def apply(self):
        if self.data:
            pb = OWGUI.ProgressBar(self, iterations=len(self.data))
            self.data = orange.ExampleTable(orange.Domain(self.tmpDom), self.tmpData)
            newdata = orngText.extractLetterNGram(self.data, self.size + 2, textAttributePos=self.textAttributePos, callback=pb.advance)
            self.lblFeatureNo.setText("\nNo. of features: \n%d" % len(newdata.domain.getmetas(orngText.TEXTMETAID)))
            self.send("Example Table", newdata)
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
    t = orngText.loadFromXML(r'c:\test\msnbc.xml')
    a = QApplication(sys.argv)
    ow = OWLetterNgram()
    ow.data = t
    a.setMainWidget(ow)
    ow.show()
    a.exec_loop()
