#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\epicArcs\epicArcChapterCont.py
import random
import carbonui
from carbonui.control.section import COLOR_HEADER
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.stretchspritevertical import StretchSpriteVertical
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.shared.agencyNew.ui.contentCards.epicArcAgentContentCard import EpicArcAgentContentCard
from eve.client.script.ui.shared.epicArcs.epicArcMissionCont import EpicArcMissionCont
from eve.client.script.ui.shared.epicArcs.epicArcUIUtil import GetLineColor
from eve.client.script.ui import eveColor
import eveicon
import eveui
from localization import GetByMessageID, GetByLabel
ICONSIZE_LARGE = 34
ICONSIZE_SMALL = 28

class EpicArcChapters(ContainerAutoSize):
    default_align = carbonui.Align.TOTOP

    def __init__(self, contentPiece, *args, **kwargs):
        super(EpicArcChapters, self).__init__(*args, **kwargs)
        self._contentPiece = contentPiece
        self._epicArc = contentPiece.epicArc
        self._chapterIDs = self._epicArc.GetChapterIDs()
        self._chapterContainers = {}
        self._currentChapterID = self._epicArc.GetCurrentChapterID()
        self._expandedChapterID = self._currentChapterID
        for index, chapterID in enumerate(self._chapterIDs):
            self._ConstructChapter(chapterID, index)

    @eveui.skip_if_destroyed
    def GetCurrentChapterPosFraction(self):
        y = self._chapterContainers[self._currentChapterID].parent.GetAbsoluteTop() - self.GetAbsoluteTop()
        _, h = self.GetAbsoluteSize()
        return y / float(h)

    def _ConstructChapter(self, chapterID, index):
        container = ContainerAutoSize(name='EpicArcChapter_{}'.format(chapterID), parent=self, align=carbonui.Align.TOTOP, padTop=8 if index else 0)
        missionNodes = self._epicArc.GetChapterMissions(chapterID)
        isChapterCompleted = True
        for missionNode in missionNodes:
            if not missionNode.IsComplete():
                isChapterCompleted = False
                break

        header = Container(parent=container, align=carbonui.Align.TOTOP, state=carbonui.uiconst.UI_NORMAL, height=30, bgColor=COLOR_HEADER, padding=(0, 0, 4, 6))
        header.OnClick = lambda *args, **kwargs: self._ToggleExpand(chapterID)
        if chapterID == self._currentChapterID:
            icon = eveicon.polestar
            color = carbonui.TextColor.NORMAL
        elif isChapterCompleted:
            icon = eveicon.checkmark
            color = carbonui.TextColor.SUCCESS
        else:
            icon = None
            color = carbonui.TextColor.SECONDARY
        Sprite(parent=header, align=carbonui.Align.CENTERLEFT, width=16, height=16, left=8, texturePath=icon, color=color)
        carbonui.TextBody(parent=header, align=carbonui.Align.CENTERLEFT, left=32, text=GetByLabel('UI/Agency/EpicArcChapter', chapterNum=index + 1, numChapters=len(self._chapterIDs), chapterName=GetByMessageID(chapterID)))
        self._chapterContainers[chapterID] = contentContainer = ContainerAutoSize(parent=container, align=carbonui.Align.TOTOP, clipChildren=True)
        if chapterID != self._currentChapterID:
            contentContainer.CollapseHeight()
        self._ConstructMissionNodes(contentContainer, missionNodes)

    def _ConstructMissionNodes(self, parent, missionNodes):
        activeMission = self._epicArc.GetActiveMission()
        for missionNode in missionNodes:
            EpicArcMissionEntry(parent=parent, align=carbonui.Align.TOTOP, missionNode=missionNode)
            if missionNode == activeMission:
                agentCard = EpicArcAgentContentCard(parent=parent, align=carbonui.Align.TOTOP, contentPiece=self._contentPiece.GetActiveAgentContentPiece(), padding=(40, 0, 40, 0))
                agentCard.AnimEnter()

    def _ToggleExpand(self, chapterID):
        if self._expandedChapterID and chapterID != self._expandedChapterID:
            self._chapterContainers[self._expandedChapterID].CollapseHeight()
        self._expandedChapterID = chapterID if self._expandedChapterID != chapterID else None
        container = self._chapterContainers[chapterID]
        if container.isCollapsed:
            container.ExpandHeight()
        else:
            container.CollapseHeight()


class EpicArcMissionEntry(Container):
    default_name = 'EpicArcMissionEntry'
    default_height = 34
    default_state = carbonui.uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        super(EpicArcMissionEntry, self).ApplyAttributes(attributes)
        self.missionNode = attributes.missionNode
        iconSize = self.GetIconSize()
        EpicArcMissionCont(parent=self, missionNode=self.missionNode, align=carbonui.Align.CENTERLEFT, state=carbonui.uiconst.UI_DISABLED, left=17 - iconSize / 2, width=iconSize, height=iconSize, iconSize=iconSize)
        opacity = 0.3 if not self.missionNode.IsOffered() else 1.0
        carbonui.TextBody(parent=self, align=carbonui.Align.CENTERLEFT, text=self.GetMissionText(), color=self.missionNode.GetStateColor(), opacity=opacity, left=40)
        if not self.missionNode.IsFirstInChapter():
            height = 8
            StretchSpriteVertical(parent=self, align=carbonui.Align.TOPLEFT, texturePath='res:/UI/Texture/Classes/EpicArcBar/lineVertical.png', topEdgeSize=4, bottomEdgeSize=4, pos=(14,
             -height / 2,
             6,
             height), color=GetLineColor(self.missionNode.IsComplete()))

    def GetMissionText(self):
        if not self.missionNode.IsOffered():
            return '%s %s %s %s' % (self._GetHex(),
             self._GetHex(),
             self._GetHex(),
             self._GetHex())
        else:
            return self.missionNode.GetName()

    def _GetHex(self):
        return str(hex(random.randint(0, 500))).upper()

    def GetIconSize(self):
        if self.missionNode.IsActive() or self.missionNode.IsLastInChapter():
            return ICONSIZE_LARGE
        else:
            return ICONSIZE_SMALL

    def LoadTooltipPanel(self, tooltipPanel, *args):
        tooltipPanel.LoadGeneric1ColumnTemplate()
        tooltipPanel.AddLabelMedium(text=self.missionNode.GetHint(), wrapWidth=200)

    def GetTooltipPointer(self):
        return carbonui.uiconst.POINT_RIGHT_2
