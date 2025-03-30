#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\epicArcs\epicArcNodeContainer.py
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.gridcontainer import GridContainer
from carbonui.primitives.stretchspritehorizontal import StretchSpriteHorizontal
from carbonui.uianimations import animations
from eve.client.script.ui.shared.epicArcs.chapterLockCont import ChapterLockCont
from eve.client.script.ui.shared.epicArcs.epicArcMissionCont import EpicArcMissionCont
from eve.client.script.ui.shared.epicArcs.epicArcUIUtil import GetLineColor
ICONSIZE_LARGE = 40
ICONSIZE_SMALL = 34

class EpicArcNodeContainer(Container):
    default_name = 'EpicArcNodeContainer'
    default_height = 40

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.epicArc = attributes.epicArc
        self.chapterLockCont = ChapterLockCont(parent=self, align=uiconst.TORIGHT)
        self.iconCont = Container(name='iconCont', parent=self, align=uiconst.TOALL, state=uiconst.UI_NORMAL)
        self.lineGridCont = GridContainer(name='lineGridCont', parent=self, align=uiconst.TOALL, state=uiconst.UI_NORMAL, lines=1, padLeft=ICONSIZE_LARGE / 2, padRight=ICONSIZE_LARGE / 2)

    def ConstructNodes(self, chapterID, animate = False):
        if animate:
            animations.FadeOut(self, duration=0.2, sleep=True)
        missionNodes = self.epicArc.GetChapterMissions(chapterID)
        numIcons = self.ConstructMissionNodes(missionNodes)
        self.ConstructMissionConnectorLines(missionNodes, numIcons)
        lastNode = missionNodes[-1]
        self.chapterLockCont.SetNode(lastNode)
        if animate:
            animations.FadeIn(self, duration=0.3)

    def ConstructMissionConnectorLines(self, missionNodes, numIcons):
        self.lineGridCont.Flush()
        for i in xrange(len(missionNodes) - 1):
            padLeft = self.GetIconSize(missionNodes[i]) / 2 - 2
            padRight = self.GetIconSize(missionNodes[i + 1]) / 2 - 2
            if i < numIcons - 1:
                StretchSpriteHorizontal(parent=self.lineGridCont, align=uiconst.TOALL, texturePath='res:/UI/Texture/Classes/EpicArcBar/line.png', padding=(padLeft,
                 17,
                 padRight,
                 18), leftEdgeSize=4, rightEdgeSize=4, color=GetLineColor(missionNodes[i].IsComplete()))

    def ConstructMissionNodes(self, missionNodes):
        self.iconCont.Flush()
        numIcons = len(missionNodes)
        self.iconCont.columns = numIcons
        for i, missionNode in enumerate(missionNodes):
            iconSize = self.GetIconSize(missionNode)
            left = float(i) / (numIcons - 1)
            if left == 1:
                left -= 0.0001
            EpicArcMissionCont(parent=self.iconCont, missionNode=missionNode, align=uiconst.TOPLEFT_PROP, left=left, top=0.5, width=ICONSIZE_LARGE, height=ICONSIZE_LARGE, iconSize=iconSize)

        return numIcons

    def GetIconSize(self, missionNode):
        if missionNode.IsActive() or missionNode.IsLastInChapter():
            return ICONSIZE_LARGE
        else:
            return ICONSIZE_SMALL
