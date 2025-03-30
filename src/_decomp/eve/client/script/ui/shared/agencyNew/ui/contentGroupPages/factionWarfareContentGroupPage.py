#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentGroupPages\factionWarfareContentGroupPage.py
import trinity
import math
import inventorycommon.const as invConst
from carbonui import uiconst
from carbonui.control.button import Button
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.frame import Frame
from carbonui.primitives.gridcontainer import GridContainer
from carbonui.primitives.sprite import Sprite, StreamingVideoSprite
from carbonui.util.color import Color
from eve.client.script.ui.control.eveIcon import OwnerIcon
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.control.utilButtons.showInfoButton import ShowInfoButton
from eve.client.script.ui.shared.agencyNew.contentGroups import contentGroupConst
from eve.client.script.ui.shared.agencyNew.contentPieces.stationContentPiece import StationContentPiece
from eve.client.script.ui.shared.agencyNew.ui import agencyUIConst
from eve.client.script.ui.shared.agencyNew.ui.agencyUIConst import CONTENT_PAGE_WIDTH_HALF
from eve.client.script.ui.shared.agencyNew.ui.common.descriptionIcon import DescriptionIconLabel
from eve.client.script.ui.shared.agencyNew.ui.contentGroupCards import contentGroupCardConstants
from eve.client.script.ui.shared.agencyNew.ui.contentGroupCards.horizontalContentGroupCard import HorizontalContentGroupCard
from eve.client.script.ui.shared.agencyNew.ui.contentGroupPages.baseContentGroupPage import BaseContentGroupPage
from carbonui.control.section import Section, SectionAutoSize
from eve.client.script.ui.shared.agencyNew.ui.tooltips.factionWarfare.alliancesTooltip import FactionWarfareAlliancesTooltip
from eve.client.script.ui.shared.agencyNew.ui.tooltips.factionWarfare.enlistmentTooltip import FactionWarfareEnlistmentTooltip
from eve.client.script.ui.shared.agencyNew.ui.tooltips.factionWarfare.systemCaptureMechanicsTooltip import FactionWarfareSystemCaptureMechanicsTooltip
from eve.client.script.ui.util.uix import EditStationName
from localization import GetByLabel
from eve.client.script.ui.control.statefulButton import StatefulButton
MAIN_CONT_PADDING = 10

class FactionWarfareContentGroupPage(BaseContentGroupPage):
    default_name = 'FactionWarfareContentGroupPage'
    contentGroupID = contentGroupConst.contentGroupFactionalWarfare
    default_top = 0
    mainContHeight = 500 + 2 * MAIN_CONT_PADDING
    clippingParentTop = 0

    def ConstructLayout(self):
        super(FactionWarfareContentGroupPage, self).ConstructLayout()
        self.factionWarfareSvc = sm.GetService('facwar')
        self.ConstructLeftContainer()
        self.ConstructRightContainer()

    def ConstructRightContainer(self):
        self.rightMainContainer = Container(name='RightMainContainer', parent=self.mainCont, align=uiconst.CENTERTOP, pos=(0,
         0,
         CONTENT_PAGE_WIDTH_HALF,
         self.mainContHeight - 2 * MAIN_CONT_PADDING))
        self.ConstructEnlistmentInfoContainer()
        self.cardsContainer = SectionAutoSize(name='cardsContainer', parent=self.rightMainContainer, align=uiconst.TOBOTTOM, headerText=GetByLabel('UI/Agency/takeMeTo'))

    def ConstructEnlistmentInfoContainer(self):
        self.enlistmentInfoContainer = SectionAutoSize(name='enlistmentInfoContainer', parent=self.rightMainContainer, align=uiconst.TOTOP, headerText=GetByLabel('UI/Agency/FactionWarfare/enlistment'))
        if not session.warfactionid:
            EveLabelMedium(parent=ScrollContainer(parent=self.enlistmentInfoContainer, align=uiconst.TOTOP, height=60), align=uiconst.TOTOP, text=GetByLabel('UI/Agency/FactionWarfare/enlistmentPrompt'), opacity=0.75)
            self.ConstructNearestFWStationContainer()
        else:
            factionContainer = Container(parent=self.enlistmentInfoContainer, align=uiconst.TOTOP, height=64)
            OwnerIcon(parent=factionContainer, align=uiconst.TOLEFT, ownerID=session.warfactionid, size=64, width=64, height=64)
            EveLabelMedium(parent=Container(parent=factionContainer), align=uiconst.CENTERLEFT, maxWidth=345, text=GetByLabel('UI/Agency/FactionWarfare/factionWarfareWindowPrompt', factionID=session.warfactionid, typeID=invConst.typeFaction), state=uiconst.UI_NORMAL)
        Button(name='openFwButton', parent=Container(parent=self.enlistmentInfoContainer, align=uiconst.TOTOP, height=35, top=10), align=uiconst.CENTERLEFT, texturePath='res:/UI/Texture/WindowIcons/factionalwarfare.png', label=GetByLabel('UI/Agency/FactionWarfare/openFactionWarfareWindow'), func=sm.GetService('cmd').OpenMilitia)

    def ConstructNearestFWStationContainer(self):
        jumpsToNearestStation, nearestStationID = self.factionWarfareSvc.GetNearestFactionWarfareStationData()
        if not nearestStationID:
            return
        uiService = sm.GetService('ui')
        stationInfo = uiService.GetStationStaticInfo(nearestStationID)
        stationTypeID = stationInfo.stationTypeID
        solarSystemID = stationInfo.solarSystemID
        stationName = uiService.GetStationName(nearestStationID)
        stationContentPiece = StationContentPiece(stationID=nearestStationID, solarSystemID=solarSystemID, locationID=nearestStationID, typeID=stationTypeID)
        nearestStationContainer = ContainerAutoSize(name='nearestStationContainer', parent=self.enlistmentInfoContainer, align=uiconst.TOTOP, top=10)
        EveLabelMedium(parent=nearestStationContainer, align=uiconst.TOPLEFT, text=GetByLabel('UI/Agency/FactionWarfare/nearestMilitiaOffice'), opacity=0.75)
        stationContainer = Container(name='stationContainer', parent=nearestStationContainer, align=uiconst.TOPLEFT, top=25, height=agencyUIConst.CONTENTCARD_HEIGHT, width=agencyUIConst.CONTENTCARD_WIDTH)
        Sprite(parent=stationContainer, align=uiconst.TOTOP_NOPUSH, texturePath='res:/UI/Texture/classes/Agency/contentCardTop.png', height=11, state=uiconst.UI_DISABLED, opacity=agencyUIConst.OPACITY_SLANTS)
        Sprite(parent=stationContainer, align=uiconst.TOBOTTOM_NOPUSH, texturePath='res:/UI/Texture/classes/Agency/contentCardTop.png', height=11, state=uiconst.UI_DISABLED, rotation=math.pi, opacity=agencyUIConst.OPACITY_SLANTS)
        Frame(bgParent=stationContainer, texturePath='res:/UI/Texture/Shared/DarkStyle/panel2Corner_Solid.png', cornerSize=9, color=Color.BLACK, opacity=0.75)
        stationSprite = Sprite(name='stationSprite', parent=Container(parent=stationContainer, align=uiconst.TOLEFT, width=76, left=5), align=uiconst.CENTER, width=76, height=76, textureSecondaryPath='res:/UI/Texture/classes/Agency/contentCardMask.png', spriteEffect=trinity.TR2_SFX_MASK, state=uiconst.UI_DISABLED)
        sm.GetService('photo').GetIconByType(stationSprite, stationTypeID, itemID=nearestStationID, size=76)
        stationInfoContainer = Container(name='stationInfoContainer', parent=stationContainer, padding=(5, 5, 0, 5))
        ShowInfoButton(parent=stationInfoContainer, align=uiconst.TOPRIGHT, typeID=stationTypeID, itemID=nearestStationID, left=5)
        shortStationName = EditStationName(stationName, usename=True, compact=True)
        stationLabel = EveLabelMedium(name='stationLabel', parent=stationInfoContainer, align=uiconst.TOTOP, text='<url=showinfo:%s//%s>%s</url>' % (stationTypeID, nearestStationID, shortStationName), state=uiconst.UI_NORMAL, singleline=True)
        stationLabel.SetRightAlphaFade(fadeEnd=180, maxFadeWidth=10)
        EveLabelMedium(name='solarSystemLabel', parent=stationInfoContainer, align=uiconst.TOTOP, text='%s - %s' % (sm.GetService('infoPanel').GetSolarSystemText(solarSystemID, solarSystemAlt=''), GetByLabel('UI/Common/numberOfJumps', numJumps=jumpsToNearestStation)), state=uiconst.UI_NORMAL, top=3)
        StatefulButton(name='stationButton', parent=stationInfoContainer, align=uiconst.BOTTOMLEFT, iconAlign=uiconst.TORIGHT, label=self.GetStationButtonLabel(solarSystemID), func=lambda x: self._ExecuteStationButtonFunc(nearestStationID, solarSystemID), controller=stationContentPiece)

    def GetStationButtonLabel(self, solarSystemID):
        if solarSystemID == session.solarsystemid2:
            return GetByLabel('UI/Inflight/DockInStation')
        else:
            return GetByLabel('UI/Commands/SetDestination')

    def _ExecuteStationButtonFunc(self, stationID, solarSystemID):
        if solarSystemID == session.solarsystemid2:
            sm.GetService('menu').Dock(stationID)
        else:
            sm.GetService('starmap').SetWaypoint(stationID, clearOtherWaypoints=True)

    def ConstructLeftContainer(self):
        self.leftMainContainer = Section(name='leftMainContainer', parent=self.mainCont, align=uiconst.CENTERTOP, pos=(0,
         0,
         496,
         self.mainContHeight - 2 * MAIN_CONT_PADDING), headerText=GetByLabel('UI/Overview/Overview'), insidePadding=(20,
         MAIN_CONT_PADDING,
         20,
         0))
        EveLabelMedium(name='descriptionLabel', parent=ScrollContainer(parent=self.leftMainContainer, align=uiconst.TOTOP, height=120), align=uiconst.TOTOP, text=GetByLabel('UI/Agency/FactionWarfare/factionWarfareSummary'), opacity=0.75)
        self.ConstructFwSpriteContainer()
        self.ConstructInformationContainer()

    def ConstructInformationContainer(self):
        infoContainer = GridContainer(name='infoGridContainer', parent=self.leftMainContainer, align=uiconst.TOALL, lines=2, columns=2)
        maxWidth = self.leftMainContainer.width / 2 - 30
        DescriptionIconLabel(parent=infoContainer, align=uiconst.TOALL, text=GetByLabel('UI/Agency/FactionWarfare/enlisting'), tooltipPanelClassInfo=FactionWarfareEnlistmentTooltip(), maxWidth=maxWidth, height=0)
        DescriptionIconLabel(parent=infoContainer, align=uiconst.TOALL, text=GetByLabel('UI/Agency/FactionWarfare/alliances'), tooltipPanelClassInfo=FactionWarfareAlliancesTooltip(), maxWidth=maxWidth, height=0, left=10)
        DescriptionIconLabel(parent=infoContainer, align=uiconst.TOALL, text=GetByLabel('UI/Agency/FactionWarfare/systemCaptureMechanics'), tooltipPanelClassInfo=FactionWarfareSystemCaptureMechanicsTooltip(), maxWidth=maxWidth, height=0)

    def ConstructFwSpriteContainer(self):
        fwSpriteContainer = Container(name='fwSpriteContainer', parent=self.leftMainContainer, align=uiconst.TOTOP, top=10, height=260)
        Frame(bgParent=fwSpriteContainer, texturePath='res:/UI/Texture/Shared/DarkStyle/panel1Corner_Stroke.png', cornerSize=9, opacity=0.1)
        StreamingVideoSprite(name='complexCaptureVideo', parent=fwSpriteContainer, align=uiconst.CENTER, width=445, height=250, videoLoop=True, videoPath='res:/video/agency/agencyFactionWarfare.webm')

    def _ConstructContentGroupCard(self, contentGroup, index):
        cardContainer = Container(name='cardContainer', parent=self.cardsContainer, align=uiconst.TOTOP, height=contentGroupCardConstants.HORIZONTAL_CARD_HEIGHT, top=10 if index > 0 else 0)
        self.cards.append(HorizontalContentGroupCard(parent=cardContainer, align=uiconst.CENTER, state=uiconst.UI_NORMAL, contentGroup=contentGroup, contentGroupID=self.contentGroupID))
