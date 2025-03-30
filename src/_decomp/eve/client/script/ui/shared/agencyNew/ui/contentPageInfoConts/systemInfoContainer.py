#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentPageInfoConts\systemInfoContainer.py
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.uianimations import animations
from eve.client.script.ui.control.eveLabel import EveCaptionMedium
from eve.client.script.ui.control.infoIcon import InfoIcon
from eve.common.lib import appConst

class SystemInfoContainer(Container):
    default_name = 'SystemInfoContainer'
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.infoPanelSvc = sm.GetService('infoPanel')
        self.contentPiece = None
        textCont = ContainerAutoSize(parent=self, align=uiconst.TOLEFT)
        self.systemNameLabel = EveCaptionMedium(name='systemNameLabel', parent=textCont, align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL)
        iconCont = Container(parent=self, align=uiconst.TOLEFT, width=16, padLeft=4)
        self.systemInfoIcon = InfoIcon(name='systemInfoIcon', parent=iconCont, align=uiconst.CENTER, top=1, typeID=appConst.typeSolarSystem)

    def UpdateContentPiece(self, contentPiece):
        self.Show()
        self.contentPiece = contentPiece
        systemText = self.infoPanelSvc.GetSolarSystemText(contentPiece.solarSystemID, solarSystemAlt='')
        self.systemNameLabel.SetText(systemText)
        self.systemInfoIcon.SetItemID(contentPiece.solarSystemID)
        animations.FadeTo(self, 0.0, 1.0, duration=0.2)

    def GetMenu(self):
        return sm.GetService('menu').GetMenuFromItemIDTypeID(self.contentPiece.solarSystemID, appConst.typeSolarSystem)
