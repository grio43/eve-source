#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\resourcewars\client\incomingtransmissionwindow.py
import evetypes
from carbon.common.script.util.format import FmtAmt
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import StreamingVideoSprite, Sprite
from carbonui.util.color import Color
from carbonui.control.button import Button
from eve.client.script.ui.control import eveLabel
from eve.client.script.ui.control.eveLabel import Label, EveLabelMediumBold
from carbonui.control.window import Window
from eve.common.lib import appConst
from localization import GetByLabel, GetByMessageID
from resourcewars.common.const import FACTION_TO_RW_ORE_TYPE
MENTOR_AMARR = 'res:/UI/Texture/classes/ConversationUI/ConversationAgents/mentor_amarr_loop.webm'
MENTOR_CALDARI = 'res:/UI/Texture/classes/ConversationUI/ConversationAgents/mentor_caldari_loop.webm'
MENTOR_GALLENTE = 'res:/UI/Texture/classes/ConversationUI/ConversationAgents/mentor_gallente_loop.webm'
MENTOR_MINMATAR = 'res:/UI/Texture/classes/ConversationUI/ConversationAgents/mentor_minmatar_loop.webm'
VIDEOS_BY_FACTION_ID = {appConst.factionAmarrEmpire: MENTOR_AMARR,
 appConst.factionCaldariState: MENTOR_CALDARI,
 appConst.factionGallenteFederation: MENTOR_GALLENTE,
 appConst.factionMinmatarRepublic: MENTOR_MINMATAR}
TITLES_BY_FACTION_ID = {appConst.factionAmarrEmpire: 'UI/ResourceWars/IncomingTransmission/IncomingTransmisssionHeaderAmarr',
 appConst.factionCaldariState: 'UI/ResourceWars/IncomingTransmission/IncomingTransmisssionHeaderCaldari',
 appConst.factionGallenteFederation: 'UI/ResourceWars/IncomingTransmission/IncomingTransmisssionHeaderGallente',
 appConst.factionMinmatarRepublic: 'UI/ResourceWars/IncomingTransmission/IncomingTransmisssionHeaderMinmatar'}
RW_ICON = 'res:/UI/Texture/Classes/Agency/Icons/resourceWars.png'
ISK_ICON = 'res:/UI/Texture/WindowIcons/wallet.png'
LP_ICON = 'res:/UI/Texture/WindowIcons/lpstore.png'
STANDINGS_ICON = 'res:/UI/Texture/WindowIcons/factionalwarfare.png'
ORE_MISSION_ICON = 'res:/UI/Texture/classes/ResourceWars/rwSiteOre.png'
WARP_OUT_ICON = 'res:/UI/Texture/classes/ResourceWars/haulerWarping.png'
DESTROY_PIRATES_ICON = 'res:/UI/Texture/classes/ResourceWars/haulerUnderAttack.png'
PROTECT_MINERS_ICON = 'res:/UI/Texture/classes/ResourceWars/supportRole.png'

class IncomingTransmissionWindow(Window):
    TOP_BAR_HEIGHT = 42
    BAR_COLOR = (0.0, 0.0, 0.0, 0.6)
    ICON_SIZE = 200
    OBJECTIVE_ICON_SIZE = 20
    OBJECTIVE_LEFT_PAD = 10
    PROTECT_MINERS_ICON_SIZE = 18
    PROTECT_MINERS_ICON_OPACITY = 0.75
    __guid__ = 'RWIncomingTransmissionWindow'
    default_minSize = (580, 370)
    default_caption = GetByLabel('UI/ResourceWars/IncomingTransmission/Caption')
    default_windowID = 'IncomingTransmissionWindow'

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.minutes = attributes.minutes
        self.topBar = Container(parent=self.GetMainArea(), align=uiconst.TOTOP, height=self.TOP_BAR_HEIGHT, bgColor=self.BAR_COLOR, padLeft=3, padRight=3)
        Button(parent=ContainerAutoSize(parent=self.GetMainArea(), align=uiconst.TOBOTTOM, padding=8), align=uiconst.CENTER, label=GetByLabel('UI/Common/Buttons/Close'), func=self.CloseByUser, args=())
        color = (0.624, 0.224, 0.812, 1.0)
        bgColor = Color(*color).SetAlpha(0.075).GetRGBA()
        icon = 'res:/UI/Texture/Classes/Agency/Icons/ContentTypes/resourceWars.png'
        self.iconContainer = Container(parent=self.topBar, align=uiconst.TOLEFT, height=self.TOP_BAR_HEIGHT, width=self.TOP_BAR_HEIGHT, bgColor=bgColor)
        self.icon = Sprite(parent=self.iconContainer, align=uiconst.TOALL, texturePath=icon, color=color)
        titleContainer = Container(name='titleContainer', parent=self.topBar, align=uiconst.TOLEFT, height=self.TOP_BAR_HEIGHT, width=self.ICON_SIZE, padLeft=5)
        self.rewardIconContainer = Container(parent=self.topBar, align=uiconst.TORIGHT, width=self.ICON_SIZE)
        self.standingsIcon = Sprite(parent=self.rewardIconContainer, align=uiconst.TORIGHT, texturePath=STANDINGS_ICON, width=self.TOP_BAR_HEIGHT)
        self.lpIcon = Sprite(parent=self.rewardIconContainer, align=uiconst.TORIGHT, texturePath=LP_ICON, width=self.TOP_BAR_HEIGHT)
        self.iskIcon = Sprite(parent=self.rewardIconContainer, align=uiconst.TORIGHT, texturePath=ISK_ICON, width=self.TOP_BAR_HEIGHT)
        mainTitleText = GetByMessageID(attributes.dungeonNameID)
        self.mainTitle = eveLabel.EveLabelMedium(parent=titleContainer, align=uiconst.TOLEFT, text=mainTitleText, top=6)
        subTitleText = GetByLabel('UI/ResourceWars/IncomingTransmission/SubTitle', level=attributes.level)
        self.subTitle = Label(parent=titleContainer, align=uiconst.TOPLEFT, top=20, text=subTitleText)
        self.centerContainer = Container(parent=self.sr.main, align=uiconst.TOALL)
        videoPath = VIDEOS_BY_FACTION_ID[attributes.factionID]
        self._create_video_sprite(videoPath)
        self._create_main_content(attributes.factionID, attributes.oreTarget, attributes.tooLate)

    def _create_video_sprite(self, path):
        self.bracketSpriteLoop = StreamingVideoSprite(parent=self.centerContainer, name='spaceObjectHighlightBracketLoopVideo', videoPath=path, videoLoop=True, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, width=self.ICON_SIZE, height=self.ICON_SIZE, disableAudio=True, padLeft=5, padTop=3)

    def _create_main_content(self, factionID, oreTarget, tooLate):
        self.create_main_content_area(factionID)
        self._add_time_remaining_text()
        if self.minutes:
            self._add_ore_objective(factionID, oreTarget, tooLate)
            self._add_pirate_objective()
            self._add_protect_objective()
            self._add_warp_objective()
            if tooLate:
                self._add_too_late()

    def create_main_content_area(self, factionID):
        self.mainContent = Container(parent=self.centerContainer, name='mainContentCont', align=uiconst.TOALL, padLeft=3, padRight=3)
        self.mainContentTitleText = GetByLabel(TITLES_BY_FACTION_ID[factionID])
        self.mainContentTitle = EveLabelMediumBold(parent=self.mainContent, text=self.mainContentTitleText, padTop=10, padLeft=self.bracketSpriteLoop.width + self.OBJECTIVE_LEFT_PAD, align=uiconst.TOTOP)

    def _add_time_remaining_text(self):
        if self.minutes:
            self.mainContentSubtitleText = GetByLabel('UI/ResourceWars/IncomingTransmission/MainContentSubtitleText', mins=self.minutes)
        else:
            self.mainContentSubtitleText = GetByLabel('UI/ResourceWars/IncomingTransmission/SiteAlreadyDetonated')
        self.mainContentSubtitle = Label(parent=self.mainContent, text=self.mainContentSubtitleText, padLeft=self.bracketSpriteLoop.width + self.OBJECTIVE_LEFT_PAD, padTop=5, align=uiconst.TOTOP)

    def _add_too_late(self):
        self.tooLateLabel = Label(parent=self.mainContent, text=GetByLabel('UI/ResourceWars/IncomingTransmission/TooLateText'), padLeft=self.bracketSpriteLoop.width + self.OBJECTIVE_LEFT_PAD, padRight=5, padTop=5, align=uiconst.TOTOP)

    def _add_ore_objective(self, factionID, oreTarget, tooLate):
        self.haulerMissionContainer = Container(parent=self.mainContent, padTop=30 if not tooLate else 10, align=uiconst.TOTOP, padLeft=self.bracketSpriteLoop.width + self.OBJECTIVE_LEFT_PAD, height=self.OBJECTIVE_ICON_SIZE, width=self.ICON_SIZE)
        self.haulerMissionIcon = Sprite(parent=self.haulerMissionContainer, align=uiconst.TOLEFT, width=self.OBJECTIVE_ICON_SIZE, height=self.OBJECTIVE_ICON_SIZE, texturePath=ORE_MISSION_ICON)
        oreTypeID = FACTION_TO_RW_ORE_TYPE[factionID]
        oreType = evetypes.GetName(oreTypeID)
        haulerMissionText = GetByLabel('UI/ResourceWars/IncomingTransmission/HaulerMissionText', oreAmount=FmtAmt(oreTarget), oreType=oreType)
        self.haulerMissionLabel = Label(parent=self.haulerMissionContainer, align=uiconst.TOLEFT, text=haulerMissionText, padLeft=5)

    def _add_warp_objective(self):
        self.warpMissionContainer = Container(parent=self.mainContent, padTop=5, align=uiconst.TOTOP, padLeft=self.bracketSpriteLoop.width + self.OBJECTIVE_LEFT_PAD, height=self.OBJECTIVE_ICON_SIZE, width=self.ICON_SIZE)
        self.warpMissionIcon = Sprite(parent=self.warpMissionContainer, align=uiconst.TOLEFT, width=self.OBJECTIVE_ICON_SIZE, height=self.OBJECTIVE_ICON_SIZE, texturePath=WARP_OUT_ICON)
        warpMissionText = GetByLabel('UI/ResourceWars/IncomingTransmission/WarpMissionText', mins=self.minutes)
        self.warpMissionLabel = Label(parent=self.warpMissionContainer, align=uiconst.TOLEFT, text=warpMissionText, padLeft=5)

    def _add_pirate_objective(self):
        self.pirateMissionContainer = Container(parent=self.mainContent, padTop=5, align=uiconst.TOTOP, padLeft=self.bracketSpriteLoop.width + self.OBJECTIVE_LEFT_PAD, height=self.OBJECTIVE_ICON_SIZE, width=self.ICON_SIZE)
        self.pirateMissionIcon = Sprite(parent=self.pirateMissionContainer, align=uiconst.TOLEFT, width=self.OBJECTIVE_ICON_SIZE, height=self.OBJECTIVE_ICON_SIZE, texturePath=DESTROY_PIRATES_ICON)
        pirateMissionText = GetByLabel('UI/ResourceWars/IncomingTransmission/PirateMissionText')
        self.pirateMissionLabel = Label(parent=self.pirateMissionContainer, align=uiconst.TOLEFT, text=pirateMissionText, padLeft=5)

    def _add_protect_objective(self):
        self.protectMissionContainer = Container(parent=self.mainContent, padTop=5, align=uiconst.TOTOP, padLeft=self.bracketSpriteLoop.width + self.OBJECTIVE_LEFT_PAD, height=self.OBJECTIVE_ICON_SIZE, width=self.ICON_SIZE)
        iconSizeDifferencePadding = max(0, (self.OBJECTIVE_ICON_SIZE - self.PROTECT_MINERS_ICON_SIZE) / 2)
        self.protectMissionIcon = Sprite(parent=self.protectMissionContainer, align=uiconst.CENTERLEFT, width=self.PROTECT_MINERS_ICON_SIZE, height=self.PROTECT_MINERS_ICON_SIZE, texturePath=PROTECT_MINERS_ICON, opacity=self.PROTECT_MINERS_ICON_OPACITY, left=iconSizeDifferencePadding)
        protectMissionText = GetByLabel('UI/ResourceWars/IncomingTransmission/ProtectMissionText')
        self.protectMissionLabel = Label(parent=self.protectMissionContainer, align=uiconst.TOLEFT, text=protectMissionText, padLeft=5 + 2 * iconSizeDifferencePadding + self.PROTECT_MINERS_ICON_SIZE)


def show_incoming_transmission_window(siteData, secondsRemaining):
    minutes = int(secondsRemaining / 60)
    tooLate = secondsRemaining <= siteData.timeLimitSeconds / 2
    oldWindow = IncomingTransmissionWindow.GetIfOpen()
    if oldWindow:
        oldWindow.Close()
    window = IncomingTransmissionWindow(factionID=siteData.factionID, level=siteData.level, minutes=minutes, oreTarget=siteData.oreTarget, tooLate=tooLate, dungeonNameID=siteData.dungeonNameID)
    window.Show()
    sm.GetService('audio').SendUIEvent('npe_mentor_incoming_transmission_play')
