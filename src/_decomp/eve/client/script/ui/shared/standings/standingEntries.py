#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\standings\standingEntries.py
import math
from carbonui import uiconst
from carbonui.primitives.container import Container
from eve.client.script.ui.control.eveIcon import OwnerIconAndLabel, OwnerIcon
from eve.client.script.ui.control.eveWindowUnderlay import ListEntryUnderlay
from eve.client.script.ui.control.themeColored import GradientThemeColored, SpriteThemeColored
from eve.client.script.ui.shared.standings.standingLabel import StandingLabel
from eve.client.script.ui.shared.standings.standingsUIUtil import GetBGOpacity
from eve.common.script.util.standingUtil import OpenStandingsPanelOnOwnerByID

class StandingsEntry(Container):
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        super(StandingsEntry, self).ApplyAttributes(attributes)
        self.standingData = attributes.standingData
        self._hiliteFill = None

    def ConstructHiliteFill(self):
        if not self._hiliteFill:
            self._hiliteFill = ListEntryUnderlay(bgParent=self)

    def ShowHilite(self, animate = True):
        self.ConstructHiliteFill()
        self._hiliteFill.set_hovered(True, animate)

    def OnMouseEnter(self, *args):
        self.ShowHilite()

    def HideHilite(self, animate = True):
        self.ConstructHiliteFill()
        self._hiliteFill.set_hovered(False, animate)

    def OnMouseExit(self, *args):
        self.HideHilite()


class StandingsEntryOneWay(StandingsEntry):
    default_name = 'StandingsEntryOneWay'

    def ApplyAttributes(self, attributes):
        super(StandingsEntryOneWay, self).ApplyAttributes(attributes)
        self.commonOwnerID = attributes.commonOwnerID
        isEvenRow = attributes.isEvenRow
        self.hideName = getattr(attributes, 'hideName', False)
        self.ConstructRightCont()
        GradientThemeColored(bgParent=self, alphaData=((0.0, 0.0), (0.5, 0.5), (1.0, 0.0)), colorType=uiconst.COLORTYPE_UIBASECONTRAST, rotation=0)
        if self.standingData.IsRightToLeft():
            left = 12
            rotation = math.pi
        else:
            left = -12
            rotation = 0.0
        SpriteThemeColored(parent=self, align=uiconst.CENTER, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/Classes/Standings/arrowsBG.png', pos=(left,
         0,
         103,
         22), opacity=GetBGOpacity(isEvenRow), rotation=rotation)

    def ConstructRightCont(self):
        StandingLabel(parent=self, align=uiconst.CENTER, standingData=self.standingData, isRightToLeft=self.standingData.IsRightToLeft())
        align = uiconst.CENTERRIGHT if self.standingData.IsRightToLeft() else uiconst.CENTERLEFT
        iconAlign = uiconst.TORIGHT if self.standingData.IsRightToLeft() else uiconst.TOLEFT
        if self.hideName:
            ownerIconComponent = OwnerIcon
        else:
            ownerIconComponent = OwnerIconAndLabel
        ownerIconComponent(parent=self, align=align, ownerID=self.GetOwnerID(), iconSize=28, height=28, width=28, iconAlign=iconAlign)

    def GetOwnerID(self):
        if self.commonOwnerID == self.standingData.ownerID2:
            return self.standingData.ownerID1
        return self.standingData.ownerID2

    def GetStandingFormatted(self):
        if self.standingData.IsRightToLeft():
            return self.standingData.GetStanding2To1Formatted()
        else:
            return self.standingData.GetStanding1To2Formatted()

    def GetStanding(self):
        if self.standingData.IsRightToLeft():
            return self.standingData.GetStanding2To1()
        else:
            return self.standingData.GetStanding1To2()

    def OnDblClick(self):
        if self.standingData.GetOwnerID1() == session.charid and self.standingData.IsRightToLeft():
            OpenStandingsPanelOnOwnerByID(self.standingData.GetOwnerID2())


class StandingsEntryTwoWay(StandingsEntry):
    default_name = 'StandingsEntryTwoWay'

    def ApplyAttributes(self, attributes):
        super(StandingsEntryTwoWay, self).ApplyAttributes(attributes)
        self.isEvenRow = attributes.isEvenRow
        self.leftCont = Container(name='leftCont', parent=self, align=uiconst.TOLEFT_PROP, width=0.5, padRight=10)
        self.rightCont = Container(name='rightCont', parent=self, padLeft=10)
        self.ConstructLeftCont()
        self.ConstructRightCont()
        GradientThemeColored(bgParent=self, alphaData=((0.0, 0.0), (0.5, 0.5), (1.0, 0.0)), colorType=uiconst.COLORTYPE_UIBASECONTRAST, rotation=0)

    def ConstructLeftCont(self):
        self._ConstructContentHalf(self.leftCont, uiconst.CENTERRIGHT, isRightToLeft=False)

    def _ConstructContentHalf(self, parent, align, isRightToLeft, showBGArrows = True):
        standingCont = StandingLabel(parent=parent, align=align, standingData=self.standingData, isRightToLeft=isRightToLeft)
        standingCont.OnMouseEnter = self.OnMouseEnter
        standingCont.OnMouseExit = self.OnMouseExit
        if showBGArrows:
            align = uiconst.CENTERLEFT if isRightToLeft else uiconst.CENTERRIGHT
            rotation = math.pi if isRightToLeft else 0.0
            SpriteThemeColored(parent=parent, align=align, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/Classes/Standings/arrowsBG.png', pos=(1, 0, 103, 22), opacity=GetBGOpacity(self.isEvenRow), rotation=rotation)

    def ConstructRightCont(self):
        cont = Container(parent=self.rightCont, padLeft=30, clipChildren=True)
        OwnerIconAndLabel(parent=cont, ownerID=self.standingData.ownerID2, align=uiconst.CENTERRIGHT, iconSize=28, height=28, iconAlign=uiconst.TORIGHT)
        self._ConstructContentHalf(self.rightCont, uiconst.CENTERLEFT, isRightToLeft=True)
