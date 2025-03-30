#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\fwwarzone\client\dashboard\nearestEnlistmentOfficeCard\nearestEnlistmentOfficeCard.py
import math
import trinity
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.frame import Frame
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.statefulButton import StatefulButton
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.control.utilButtons.showInfoButton import ShowInfoButton
from eve.client.script.ui.shared.agencyNew.ui import agencyUIConst
from eve.client.script.ui.util.uix import EditStationName
from fwwarzone.client.dashboard.nearestEnlistmentOfficeCard.buttonController import StationButtonController
from localization import GetByLabel

class NearestEnlistmentOfficeCard(Container):

    def ApplyAttributes(self, attributes):
        super(NearestEnlistmentOfficeCard, self).ApplyAttributes(attributes)
        self.stationInfo = attributes.get('stationInfo')
        self.stationTypeID = attributes.get('stationTypeID')
        self.solarSystemID = attributes.get('solarSystemID')
        self.stationName = attributes.get('stationName')
        self.nearestStationID = attributes.get('nearestStationID')
        self.jumpsToNearestStation = attributes.get('jumpsToNearestStation')
        self.ConstructLayout()

    def ConstructLayout(self):
        stationContentPiece = StationButtonController(stationID=self.nearestStationID, solarSystemID=self.solarSystemID, locationID=self.nearestStationID, typeID=self.stationTypeID)
        stationContainer = Container(name='stationContainer', parent=self, align=uiconst.TOALL)
        Sprite(parent=stationContainer, align=uiconst.TOTOP_NOPUSH, texturePath='res:/UI/Texture/classes/Agency/contentCardTop.png', height=11, state=uiconst.UI_DISABLED, opacity=agencyUIConst.OPACITY_SLANTS)
        Sprite(parent=stationContainer, align=uiconst.TOBOTTOM_NOPUSH, texturePath='res:/UI/Texture/classes/Agency/contentCardTop.png', height=11, state=uiconst.UI_DISABLED, rotation=math.pi, opacity=agencyUIConst.OPACITY_SLANTS)
        Frame(bgParent=stationContainer, texturePath='res:/UI/Texture/Shared/DarkStyle/panel2Corner_Solid.png', cornerSize=9, color=eveColor.BLACK, opacity=0.3)
        stationSprite = Sprite(name='stationSprite', parent=Container(parent=stationContainer, align=uiconst.TOLEFT, width=76, left=5), align=uiconst.CENTER, width=76, height=76, textureSecondaryPath='res:/UI/Texture/classes/Agency/contentCardMask.png', spriteEffect=trinity.TR2_SFX_MASK, state=uiconst.UI_DISABLED)
        sm.GetService('photo').GetIconByType(stationSprite, self.stationTypeID, itemID=self.nearestStationID, size=76)
        stationInfoContainer = Container(name='stationInfoContainer', parent=stationContainer, padding=(5, 5, 0, 5))
        ShowInfoButton(parent=stationInfoContainer, align=uiconst.TOPRIGHT, typeID=self.stationTypeID, itemID=self.nearestStationID, left=5)
        shortStationName = EditStationName(self.stationName, usename=True, compact=True)
        stationLabel = EveLabelMedium(name='stationLabel', parent=stationInfoContainer, align=uiconst.TOTOP, text='<url=showinfo:%s//%s>%s</url>' % (self.stationTypeID, self.nearestStationID, shortStationName), state=uiconst.UI_NORMAL, singleline=True)
        stationLabel.SetRightAlphaFade(fadeEnd=150, maxFadeWidth=100)
        EveLabelMedium(name='solarSystemLabel', parent=stationInfoContainer, align=uiconst.TOTOP, text='%s - %s' % (sm.GetService('infoPanel').GetSolarSystemText(self.solarSystemID, solarSystemAlt=''), GetByLabel('UI/Common/numberOfJumps', numJumps=self.jumpsToNearestStation)), state=uiconst.UI_NORMAL, top=3)
        StatefulButton(name='stationButton', parent=stationInfoContainer, align=uiconst.BOTTOMLEFT, iconAlign=uiconst.TORIGHT, controller=stationContentPiece)
