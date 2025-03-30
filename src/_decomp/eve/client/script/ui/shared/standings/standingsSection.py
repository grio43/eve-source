#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\standings\standingsSection.py
import math
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control.eveIcon import OwnerIcon
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.control.themeColored import FillThemeColored, GradientThemeColored
from eve.client.script.ui.shared.standings.standingEntries import StandingsEntryOneWay, StandingsEntryTwoWay
from eve.client.script.ui.shared.standings.standingsUIUtil import GetStandingIconTexturePath, GetStandingColor

class StandingsSection(ContainerAutoSize):
    default_name = 'StandingsSection'

    def ApplyAttributes(self, attributes):
        ContainerAutoSize.ApplyAttributes(self, attributes)
        self.text = attributes.text
        self.commonOwnerID = attributes.ownerID
        self.standingsData = attributes.standingsData
        self.ConstructHeader()
        self.mainCont = ContainerAutoSize(name='mainCont', parent=self, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, padTop=0)
        self.ConstructCommonOwnerCont()
        self.standingsCont = ContainerAutoSize(name='standingsCont', parent=self.mainCont, align=uiconst.TOTOP, minHeight=36)
        self.ConstructStandingsEntries()

    def ConstructStandingsEntries(self):
        for i, standingData in enumerate(self.standingsData):
            if standingData.IsTwoWay():
                StandingsEntryTwoWay(parent=self.standingsCont, align=uiconst.TOTOP, height=22, standingData=standingData, commonOwnerID=self.commonOwnerID, padBottom=4, isEvenRow=bool(i % 2))
            else:
                StandingsEntryOneWay(parent=self.standingsCont, align=uiconst.TOTOP, height=22, top=7, standingData=standingData, commonOwnerID=self.commonOwnerID, isEvenRow=bool(i % 2))

    def ConstructCommonOwnerCont(self):
        align = uiconst.TOLEFT if self.standingsData[0].ownerID1 == self.commonOwnerID else uiconst.TORIGHT
        cont = Container(name='commonOwnerLayer', parent=self.mainCont, padding=(0, -4, 0, -4))
        self.commonOwnerCont = Container(name='commonOwnerCont', parent=cont, align=align, width=70)
        GradientThemeColored(bgParent=self.commonOwnerCont, alphaData=((0.0, 0.0),
         (0.25, 1.0),
         (0.75, 1.0),
         (1.0, 0.0)), colorType=uiconst.COLORTYPE_UIBASECONTRAST, rotation=math.pi / 2.0)
        iconSize = 32 if self.commonOwnerID == session.charid or len(self.standingsData) == 1 else 64
        OwnerIcon(parent=self.commonOwnerCont, ownerID=self.commonOwnerID, size=iconSize, pos=(0,
         0,
         iconSize,
         iconSize), align=uiconst.CENTER)

    def ConstructHeader(self):
        self.headerCont = Container(parent=self, name='headerCont', align=uiconst.TOTOP, height=26, padBottom=4)
        FillThemeColored(parent=self.headerCont, padBottom=1, colorType=uiconst.COLORTYPE_UIHILIGHT)


class StandingGoodOrBadIcon(Sprite):
    default_state = uiconst.UI_DISABLED

    def ApplyAttributes(self, attributes):
        Sprite.ApplyAttributes(self, attributes)
        standing = attributes.standing
        self.texturePath = GetStandingIconTexturePath(standing)
        color = GetStandingColor(standing)
        self.SetRGBA(*color)
