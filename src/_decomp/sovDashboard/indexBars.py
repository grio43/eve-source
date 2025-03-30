#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sovDashboard\indexBars.py
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
import carbonui.const as uiconst

class IndexBars(Container):
    __guid__ = 'sov.IndexBars'
    default_align = uiconst.CENTER
    default_state = uiconst.UI_NORMAL
    numLevels = 5
    gapSize = 2
    boxWidth = 13
    default_height = 8
    default_width = 88
    inactiveColor = (1, 1, 1, 0.2)
    partialColor = (1, 1, 1, 0.25)
    activeColor = (1, 1, 1, 0.65)

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.showHint = attributes.get('showHint', False)
        self.currentIndex = attributes.get('currentIndex', 0)
        self.partialValue = attributes.get('partialValue', 0)
        self.boxTooltipFunc = attributes.get('boxTooltipFunc', None)
        self.levelBoxes = []
        gapSize = 0
        for i in xrange(self.numLevels):
            levelBox = Container(parent=self, name='box', align=uiconst.TOLEFT, width=self.boxWidth, left=gapSize)
            levelBox.boxNumber = i
            levelBox.partialValue = 0
            if self.boxTooltipFunc:
                levelBox.state = uiconst.UI_NORMAL
            fullBox = Fill(bgParent=levelBox, color=self.inactiveColor)
            levelBox.fullBox = fullBox
            partialBox = Fill(parent=levelBox, color=self.partialColor, align=uiconst.TOLEFT_PROP)
            partialBox.display = False
            levelBox.partialBox = partialBox
            self.levelBoxes.append(levelBox)
            gapSize = self.gapSize

        self.width = self.numLevels * self.boxWidth + (self.numLevels - 1) * self.gapSize
        self.SetIndexStatus(self.currentIndex, self.partialValue)

    def SetIndexStatus(self, indexStatus, partial = 0):
        self.currentIndex = indexStatus
        self.partialValue = partial
        numBoxes = len(self.levelBoxes)
        for i, eachLevelCont in enumerate(self.levelBoxes):
            partialValue = 0
            fullBoxColor = self.inactiveColor
            partialBoxDisplayState = False
            if i + 1 <= indexStatus:
                fullBoxColor = self.activeColor
                if i == numBoxes - 1 and self.currentIndex == numBoxes:
                    partialValue = 1 + self.partialValue
            elif self.IsNextLevel(i):
                partialValue = self.partialValue
                partialBoxDisplayState = True
            eachLevelCont.fullBox.SetRGBA(*fullBoxColor)
            eachLevelCont.partialValue = partialValue
            eachLevelCont.partialBox.width = self.partialValue
            eachLevelCont.partialBox.display = partialBoxDisplayState
            if self.boxTooltipFunc:
                self.boxTooltipFunc(eachLevelCont)

    def IsNextLevel(self, boxIndex):
        return boxIndex == self.currentIndex
