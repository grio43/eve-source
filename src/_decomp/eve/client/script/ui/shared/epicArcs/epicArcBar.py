#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\epicArcs\epicArcBar.py
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.control.buttonIcon import ButtonIcon
from eve.client.script.ui.control.eveLabel import EveLabelLarge
from eve.client.script.ui.shared.epicArcs.epicArcNodeContainer import EpicArcNodeContainer
from localization import GetByMessageID, GetByLabel

class EpicArcBar(ContainerAutoSize):

    def ApplyAttributes(self, attributes):
        ContainerAutoSize.ApplyAttributes(self, attributes)
        self.epicArc = attributes.epicArc
        labelCont = Container(name='labelCont', parent=self, align=uiconst.TOTOP, height=20, padTop=4)
        self.prevChapterBtn = ButtonIcon(name='prevButton', parent=labelCont, align=uiconst.CENTERLEFT, width=12, texturePath='res:/UI/Texture/Shared/arrows/arrowLeft.png', iconSize=9, func=self.SelectPreviousChapter)
        self.nextChapterBtn = ButtonIcon(name='nextButton', parent=labelCont, align=uiconst.CENTERLEFT, width=12, left=12, texturePath='res:/UI/Texture/Shared/arrows/arrowRight.png', iconSize=9, func=self.SelectNextChapter)
        self.chapterLabel = EveLabelLarge(parent=labelCont, align=uiconst.CENTERLEFT, left=30)
        self.nodeContainer = EpicArcNodeContainer(parent=self, align=uiconst.TOTOP, epicArc=self.epicArc, padTop=6)
        self._SetChapter(self.epicArc.GetCurrentChapterID())

    def _SetChapter(self, chapterID, animate = False):
        self.nodeContainer.ConstructNodes(chapterID, animate)
        self.UpdateChapterLabel(chapterID)
        self.chapterID = chapterID

    def SelectPreviousChapter(self):
        chapterIDs = self.epicArc.GetChapterIDs()
        currIdx = chapterIDs.index(self.chapterID)
        idx = currIdx - 1
        self._TryChangeChapter(chapterIDs, idx)

    def _TryChangeChapter(self, chapterIDs, idx):
        try:
            chapterID = chapterIDs[idx]
            self._SetChapter(chapterID, animate=True)
        except IndexError:
            pass

    def SelectNextChapter(self):
        chapterIDs = self.epicArc.GetChapterIDs()
        currIdx = chapterIDs.index(self.chapterID)
        idx = currIdx + 1
        if idx > len(chapterIDs) - 1:
            idx = 0
        self._TryChangeChapter(chapterIDs, idx)

    def UpdateChapterLabel(self, chapterID):
        chapterName = GetByMessageID(chapterID)
        chapterIDs = self.epicArc.GetChapterIDs()
        chapterNum = chapterIDs.index(chapterID) + 1
        numChapters = len(chapterIDs)
        self.chapterLabel.text = GetByLabel('UI/Agency/EpicArcChapter', chapterNum=chapterNum, numChapters=numChapters, chapterName=chapterName)
