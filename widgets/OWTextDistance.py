"""
<name>Distance</name>
<description>Computes distances between documents.</description>
<icon>icons/TextDistance.png</icon>
<contact></contact> 
<priority>2200</priority>
"""

from OWWidget import *
import OWGUI, orngText

class OWTextDistance(OWWidget):
    def __init__(self, parent=None, signalManager=None):
        OWWidget.__init__(self,parent,signalManager,"Preprocess")
        self.inputs = [("Example Table", ExampleTable, self.dataset)]
        self.outputs = [("Distance Matrix", orange.SymMatrix)]
        self.data = None
        self.distanceType = 0
        self.nDocuments = "N/A"; self.nWords = "N/A"
        self.loadSettings()

        box = OWGUI.widgetBox(self.controlArea, "Info", addSpace = True)
        OWGUI.label(box, self, "Documents: %(nDocuments)s")
        OWGUI.label(box, self, "Words: %(nWords)s")

        OWGUI.radioButtonsInBox(self.controlArea, self, "distanceType", box = "Matrix type",
            btnLabels = ["Similarity [cos(fi)]", "Distance [1/cos(fi)]"], addSpace = True)
        OWGUI.button(self.controlArea, self, "Apply", self.apply)
        OWGUI.rubber(self.controlArea)
        self.adjustSize()

    def dataset(self, data):
        if data:
            words = len(data.domain.getmetas(orngText.TEXTMETAID))
            if words == 0:
                self.error("Bag-of-words data set empty (no words)")
                self.send("Distance Matrix", None)
                self.nDocuments = "N/A"; self.nWords = "N/A"
                self.data = None
                return
            self.nDocuments = len(data); self.nWords = words
        self.data = data
        self.apply()

    def apply(self):
        if self.data:
            # pb = OWGUI.ProgressBar(self, iterations=(len(self.data) ** 2)/2.)
            # dist = orngText.cos(self.data, distance = self.distanceType, callback = pb.advance)
            pb = OWGUI.ProgressBar(self, iterations=2)
            pb.advance()
            dist = orange.textCos(self.data, self.distanceType, orngText.TEXTMETAID)
            dist.setattr("items", self.data)
            self.send("Distance Matrix", dist)
            pb.finish()
        else:
            self.send("Distance Matrix", None)
