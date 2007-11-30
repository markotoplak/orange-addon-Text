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
        

    def dataset(self, data):
        if data:
            self.data = orange.ExampleTable(data)
            self.tmpData = orange.ExampleTable(data)
            self.tmpDom = orange.Domain(data.domain)            
            #self.data.domain = orange.Domain(data.domain)
        else:
            self.data = None
            self.tmpData = None
            self.lblFeatureNo.setText("\nNo. of features: \n0")

        self.apply()

    def apply(self):
        if self.data:
            pb = OWGUI.ProgressBar(self, iterations=len(self.data))
            self.data = orange.ExampleTable(orange.Domain(self.tmpDom), self.tmpData)
            newdata = orngText.extractLetterNGram(self.data, self.size + 2, callback=pb.advance)
            self.lblFeatureNo.setText("\nNo. of features: \n%d" % len(newdata.domain.getmetas(orngText.TEXTMETAID)))
            self.send("Example Table", newdata)
            pb.finish()
        else:
            self.send("Example Table", None)


if __name__ == "__main__":
    t = orngText.loadFromXML(r'c:\test\msnbc.xml')
    a = QApplication(sys.argv)
    ow = OWLetterNgram()
    ow.data = t
    a.setMainWidget(ow)
    ow.show()
    a.exec_loop()
