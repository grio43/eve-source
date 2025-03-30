#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\cloneGrade\cloneStateWindow.py
import trinity
import threadutils
from eveexceptions.exceptionEater import ExceptionEater
import localization
import eveicon
from eve.client.script.ui import eveColor
import carbonui
import eveui
from carbonui.control.window import Window
from carbonui.decorative.selectionIndicatorLine import SelectionIndicatorLine
from carbonui.window.underlay import WindowUnderlay
from carbonui.primitives.sprite import Sprite, StreamingVideoSprite
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.primitives.stretchspritehorizontal import StretchSpriteHorizontal
from carbonui.primitives.frame import Frame
from eve.client.script.ui.control.infoIcon import InfoGlyphIcon, CheckMarkGlyphIcon, ExclamationMarkGlyphIcon
from eve.client.script.ui.shared.cloneGrade.upgradeButton import UpgradeIconButton
from eve.client.script.ui.shared.cloneGrade import ORIGIN_LAPSENOTIFYWINDOW
from eve.common.lib.vgsConst import CATEGORYTAG_GAMETIME

def open_upgrade_window(origin = None, reason = None):
    CloneStateWindow.CloseIfOpen()
    window = CloneStateWindow.Open(origin=origin, reason=reason, omega=True, show_upgrade_buttons=True, headline_label='UI/CloneState/UpgradeToday', body_header_label='UI/CloneState/OmegaBenefits', body_header_icon_class=InfoGlyphIcon, body_header_color=carbonui.TextColor.HIGHLIGHT, bullet_points=[{'icon': 'res:/UI/Texture/classes/cloneGrade/benefits/allShipsAndModules.png',
      'label': 'UI/CloneState/PilotAllUniqueShips'},
     {'icon': 'res:/UI/Texture/classes/cloneGrade/benefits/trainSkillsFast.png',
      'label': 'UI/CloneState/BenefitFasterTraining'},
     {'icon': 'res:/UI/Texture/classes/cloneGrade/benefits/allSkills.png',
      'label': 'UI/CloneState/UnlimitedTraining'},
     {'icon': 'res:/UI/Texture/classes/cloneGrade/benefits/SKINR.png',
      'label': 'UI/CloneState/SequenceOmegaShips'},
     {'icon': 'res:/UI/Texture/classes/cloneGrade/benefits/wallet.png',
      'label': 'UI/CloneState/EarnOmegaRewards'},
     {'icon': 'res:/UI/Texture/classes/cloneGrade/benefits/PlanetaryIndustry.png',
      'label': 'UI/CloneState/PlanetaryIndustry'},
     {'icon': 'res:/UI/Texture/classes/cloneGrade/benefits/Opportunities.png',
      'label': 'UI/CloneState/UnlockAgentMissions'}])
    window.ShowDialog(modal=True, closeWhenClicked=True)


def open_omega_state_window():
    CloneStateWindow.CloseIfOpen()
    CloneStateWindow.Open(omega=True, show_upgrade_buttons=False, headline_label='UI/CloneState/CloneStateOmega', body_header_label='UI/CloneState/YouHaveAll', body_header_icon_class=CheckMarkGlyphIcon, body_header_color=carbonui.TextColor.SUCCESS, bullet_points=[{'icon': 'res:/UI/Texture/classes/cloneGrade/benefits/allShipsAndModules.png',
      'label': 'UI/CloneState/PilotAllUniqueShips'},
     {'icon': 'res:/UI/Texture/classes/cloneGrade/benefits/trainSkillsFast.png',
      'label': 'UI/CloneState/BenefitFasterTraining'},
     {'icon': 'res:/UI/Texture/classes/cloneGrade/benefits/allSkills.png',
      'label': 'UI/CloneState/UnlimitedTraining'},
     {'icon': 'res:/UI/Texture/classes/cloneGrade/benefits/SKINR.png',
      'label': 'UI/CloneState/SequenceOmegaShips'},
     {'icon': 'res:/UI/Texture/classes/cloneGrade/benefits/wallet.png',
      'label': 'UI/CloneState/EarnOmegaRewards'},
     {'icon': 'res:/UI/Texture/classes/cloneGrade/benefits/PlanetaryIndustry.png',
      'label': 'UI/CloneState/PlanetaryIndustry'},
     {'icon': 'res:/UI/Texture/classes/cloneGrade/benefits/Opportunities.png',
      'label': 'UI/CloneState/UnlockAgentMissions'}])


def open_alpha_state_window():
    CloneStateWindow.CloseIfOpen()
    window = CloneStateWindow.Open(origin=ORIGIN_LAPSENOTIFYWINDOW, omega=False, show_upgrade_buttons=True, headline_label='UI/CloneState/CloneStateAlpha', body_header_label='UI/CloneState/LapseWindow/Downgrade', body_header_icon_class=ExclamationMarkGlyphIcon, body_header_color=carbonui.TextColor.WARNING, bullet_points=[{'icon': 'res:/UI/Texture/classes/cloneGrade/benefits/allSkills.png',
      'label': 'UI/CloneState/SkillRestrictions',
      'sub_points': ['UI/CloneState/LostOmegaSkillAccess', 'UI/CloneState/SlowerSkillTraining', 'UI/CloneState/SkillQueuePaused']},
     {'icon': 'res:/UI/Texture/classes/cloneGrade/benefits/SKINR.png',
      'label': 'UI/CloneState/SequencingRestricted',
      'sub_points': ['UI/CloneState/NoSequenceForOmegaShips']},
     {'icon': 'res:/UI/Texture/classes/cloneGrade/benefits/wallet.png',
      'label': 'UI/CloneState/ReducedRewards',
      'sub_points': ['UI/CloneState/LostRewardAccess']},
     {'icon': 'res:/UI/Texture/classes/cloneGrade/benefits/PlanetaryIndustry.png',
      'label': 'UI/CloneState/PlanetaryAccessLost',
      'sub_points': ['UI/CloneState/UnableToExport']},
     {'icon': 'res:/UI/Texture/classes/cloneGrade/benefits/Opportunities.png',
      'label': 'UI/CloneState/AgentMissionsRestricted',
      'sub_points': ['UI/CloneState/AgentMissionsCapped']}])


class CloneStateSelectionIndicatorLine(SelectionIndicatorLine):
    default_color = eveColor.OMEGA_YELLOW


class CloneStateWindowUnderlay(WindowUnderlay):
    default_clipChildren = True

    def ConstructLayout(self):
        super(CloneStateWindowUnderlay, self).ConstructLayout()
        self.video = StreamingVideoSprite(parent=self, videoPath='res:/video/shared/SplashBGLoop.webm', videoLoop=True, align=carbonui.Align.CENTERTOP, width=640, height=360, top=-35, color=eveColor.Color(*eveColor.OMEGA_YELLOW).SetSaturation(0.5).GetRGBA(), opacity=0, spriteEffect=trinity.TR2_SFX_COPY, blendMode=trinity.TR2_SBM_ADD)
        eveui.fade_in(self.video, end_value=0.6, duration=2)
        self.background_image = Sprite(name='bgTexture', parent=self, align=carbonui.Align.CENTERTOP, width=540, height=729, texturePath='res:/UI/Texture/Classes/CloneGrade/background.png')

    def ConstructAccentLine(self):
        self.headerAccentLine = CloneStateSelectionIndicatorLine(parent=self, align=carbonui.Align.TOTOP_NOPUSH, weight=self.ACCENT_LINE_THICKNESS)

    def OnColorThemeChanged(self):
        pass


class CloneStateWindow(Window):
    default_windowID = 'clone_state_window'
    default_isCollapseable = False
    default_isMinimizable = False
    default_isLightBackgroundConfigurable = False
    default_isStackable = False
    default_isLockable = False
    default_isOverlayable = False
    default_extend_content_into_header = True
    default_width = 540
    default_height = 729
    default_minSize = (default_width, default_height)
    default_maxSize = (default_width, default_height)
    hasWindowIcon = False

    def ApplyAttributes(self, attributes):
        if not attributes.show_upgrade_buttons:
            attributes['analyticID'] = None
        elif attributes.omega:
            attributes['analyticID'] = 'omega_upgrade_window'
        else:
            attributes['analyticID'] = 'omega_lapsed_window'
        Window.ApplyAttributes(self, attributes)
        self.MakeUnResizeable()
        self._origin = attributes.origin
        self._reason = attributes.reason
        self._construct_top(attributes.omega, attributes.headline_label)
        if attributes.show_upgrade_buttons:
            self._construct_upgrade_buttons(len(attributes.bullet_points), attributes.omega)
            self._log_window_opened()
        self._construct_body(attributes.body_header_label, attributes.body_header_color, attributes.body_header_icon_class, attributes.bullet_points)

    def Prepare_Background_(self):
        self.sr.underlay = CloneStateWindowUnderlay(parent=self, padding=1)

    def _construct_top(self, omega, headline_label):
        icon_container = Container(parent=self.content, pickState=carbonui.PickState.OFF, align=carbonui.Align.CENTERTOP, top=60, width=128, height=128)
        if omega:
            Sprite(parent=icon_container, align=carbonui.Align.CENTER, texturePath='res:/UI/Texture/Classes/CloneGrade/omega_hex_icon_128.png', outputMode=carbonui.uiconst.OUTPUT_COLOR_AND_GLOW, glowBrightness=0.3, height=51, width=46)
            Sprite(parent=icon_container, align=carbonui.Align.CENTER, texturePath='res:/UI/Texture/Classes/CloneGrade/omega_hex_bg_128.png', outputMode=carbonui.uiconst.OUTPUT_COLOR_AND_GLOW, height=94, width=110)
        else:
            Sprite(parent=icon_container, align=carbonui.Align.CENTER, texturePath='res:/UI/Texture/Classes/CloneGrade/Alpha_128.png', outputMode=carbonui.uiconst.OUTPUT_COLOR_AND_GLOW, glowBrightness=0.3, height=128, width=128)
        carbonui.TextHeadline(parent=self.content, align=carbonui.Align.TOTOP, textAlign=carbonui.TextAlign.CENTER, color=carbonui.TextColor.HIGHLIGHT, bold=True, top=183, outputMode=carbonui.uiconst.OUTPUT_COLOR_AND_GLOW, glowBrightness=0.5, text=localization.GetByLabel(headline_label))

    def _construct_body(self, body_header_label, body_header_color, body_header_icon_class, bullet_points):
        wrapper = Container(parent=self.content, align=carbonui.Align.TOALL, padding=(35, 60, 35, 35))
        Frame(bgParent=wrapper, texturePath='res:/UI/Texture/classes/Button/background_cut_bottom_left_right.png', cornerSize=9, color=(0, 0, 0, 0.85))
        title_container = ContainerAutoSize(parent=wrapper, align=carbonui.Align.CENTERTOP, alignMode=carbonui.Align.CENTERLEFT, height=32, top=-16)
        StretchSpriteHorizontal(bgParent=title_container, texturePath='res:/UI/Texture/Classes/CloneGrade/omegaHilite.png', leftEdgeSize=12, rightEdgeSize=12, color=(0, 0, 0))
        icon_container = Container(parent=title_container, align=carbonui.Align.CENTERLEFT, height=32, width=32, left=6)
        body_header_icon_class(parent=icon_container, align=carbonui.Align.CENTER, pickState=carbonui.PickState.OFF)
        carbonui.TextBody(parent=title_container, align=carbonui.Align.CENTERLEFT, text=localization.GetByLabel(body_header_label), color=body_header_color, left=36, padRight=16)
        bullet_points_container = ScrollContainer(parent=wrapper, align=carbonui.Align.TOALL, padding=32)
        _, text_height = carbonui.TextBody.MeasureTextSize(' ')
        _, sub_point_text_height = carbonui.TextDetail.MeasureTextSize(' ')
        for index, bullet_point in enumerate(bullet_points):
            sub_points = bullet_point.get('sub_points', [])
            icon_size = 24 if sub_points else 32
            padding = 8 if sub_points else 10
            container = ContainerAutoSize(parent=bullet_points_container, align=carbonui.Align.TOTOP, alignMode=carbonui.Align.TOTOP, padTop=padding, padBottom=padding, opacity=0)
            eveui.fade_in(container, duration=0.5, time_offset=index * 0.2)
            text_container = ContainerAutoSize(parent=container, align=carbonui.Align.TOTOP, alignMode=carbonui.Align.TOTOP)
            Sprite(parent=text_container, align=carbonui.Align.CENTERLEFT, width=icon_size, height=icon_size, texturePath=bullet_point['icon'])
            carbonui.TextBody(parent=text_container, align=carbonui.Align.TOTOP, text=localization.GetByLabel(bullet_point['label']), color=carbonui.TextColor.HIGHLIGHT, padLeft=icon_size + 8)
            for sub_point in sub_points:
                bullet_point_container = ContainerAutoSize(parent=container, align=carbonui.Align.TOTOP, alignMode=carbonui.Align.TOTOP, padLeft=icon_size + 10)
                Sprite(parent=bullet_point_container, align=carbonui.Align.TOPLEFT, width=2, height=2, top=sub_point_text_height / 2 - 1, texturePath='res:/UI/Texture/Shared/smallDot.png', color=carbonui.TextColor.NORMAL)
                carbonui.TextDetail(parent=bullet_point_container, align=carbonui.Align.TOTOP, text=localization.GetByLabel(sub_point), padLeft=6)

    def _construct_upgrade_buttons(self, num_bulletpoints, omega):
        container = Container(parent=self.content, align=carbonui.Align.TOBOTTOM_NOPUSH, height=40, top=15, opacity=0)
        eveui.fade_in(container, duration=num_bulletpoints * 0.2, time_offset=0.5)
        left = Container(parent=container, align=carbonui.Align.TOLEFT_PROP, width=0.5)
        right = Container(parent=container, align=carbonui.Align.TOALL)
        store_button = UpgradeIconButton(parent=left, align=carbonui.Align.CENTERRIGHT, height=40, left=4, text=localization.GetByLabel('UI/CloneState/UpgradeInStore'), icon='res:/UI/Texture/Icons/79_64_11.png', iconSize=(16, 16), onClick=self._upgrade_in_store, analyticID='upgrade_omega_secure' if omega else 'upgrade_omega_lapsed_secure')
        plex_button = UpgradeIconButton(parent=right, align=carbonui.Align.CENTERLEFT, height=40, left=4, text=localization.GetByLabel('UI/CloneState/UpgradeWithPLEX'), icon=eveicon.plex, iconSize=(16, 16), onClick=self._upgrade_with_plex, analyticID='upgrade_omega_nes' if omega else 'upgrade_omega_lapsed_nes')
        width = max(store_button.width, plex_button.width) + 4
        store_button.width = width
        plex_button.width = width

    def _upgrade_in_store(self, *args, **kwargs):
        sm.GetService('cloneGradeSvc').UpgradeCloneAction(self._origin, self._reason)
        self.Close()

    def _upgrade_with_plex(self, *args, **kwargs):
        sm.GetService('vgsService').OpenStore(categoryTag=CATEGORYTAG_GAMETIME)
        self.Close()

    @threadutils.threaded
    def _log_window_opened(self):
        with ExceptionEater('eventLog'):
            sm.ProxySvc('eventLog').LogClientEvent('trial', ['origin', 'reason'], 'ShowCloneUpgradeWindow', self._origin, self._reason)
