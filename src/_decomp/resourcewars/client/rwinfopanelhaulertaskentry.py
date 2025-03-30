#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\resourcewars\client\rwinfopanelhaulertaskentry.py
import carbonui.const as uiconst
import gametime
import uthread2
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from carbonui.uicore import uicore
import inventorycommon.const as invconst
import localization
import logging
from resourcewars.client.const import RW_PANEL_HAULER_PROGRESS_LABEL, RW_HAULER_PROGRESS_BAR_FULL_LABEL
from eve.client.script.parklife import states
from resourcewars.common.const import HAULER_CAPACITY_UNLIMITED, HAULER_CAPACITY_UNLIMITED_STR
logger = logging.getLogger(__name__)
HAULER_PROGRESS_COLOR = (0.984, 0.69, 0.231, 0.7)
HAULER_ORE_DEPOSITED_COLOR = HAULER_PROGRESS_COLOR
HAULER_WARP_OUT_COLOR = (0.161, 0.671, 0.886, 0.5)
HAULER_UNDER_ATTACK_COLOR = (0.937, 0.22, 0.0, 0.5)
DEATH_ICON_COLOR = (0.929, 0.11, 0.141, 0.5)
HAULER_STATE_DEFAULT_ICON = 'res:/UI/Texture/Icons/44_32_8.png'
HAULER_ORE_DEPOSITED_ICON = 'res:/UI/Texture/classes/ResourceWars/haulerDeposit.png'
HAULER_WARP_OUT_ICON = 'res:/UI/Texture/classes/ResourceWars/haulerWarping.png'
HAULER_UNDER_ATTACK_ICON = 'res:/UI/Texture/classes/ResourceWars/haulerUnderAttack.png'
HAULER_DEATH_ICON = 'res:/UI/Texture/classes/ResourceWars/haulerDestroyed.png'
HAULER_MILESTONE_AUDIO = {0.25: 'voc_rw_aura_hauler25_aura_play',
 0.5: 'voc_rw_aura_hauler50_aura_play',
 0.75: 'voc_rw_aura_hauler75_aura_play',
 1.0: 'voc_rw_aura_oreholdfull_aura_play'}

class DamageBar(Container):
    DAMAGE_COLOR = (0.0, 0.0, 0.0, 0.83)
    DAMAGE_FLASH_COLOR = (1.0, 0.0, 0.0, 0.8)
    default_bgColor = (1.0, 1.0, 1.0, 1.0)

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.damage = attributes.damage
        damageBarWidth = self._CalculateDamageBarWidth(self.damage)
        self.damageFlashContainer = Container(parent=self, width=self.width - damageBarWidth, height=self.height, bgColor=self.DAMAGE_FLASH_COLOR, align=uiconst.TOLEFT, opacity=0.0)
        self.damageContainer = Container(parent=self, width=damageBarWidth, height=self.height, bgColor=self.DAMAGE_COLOR, align=uiconst.TORIGHT)

    def SetDamageState(self, damage):
        global uicore
        if self.damage == damage:
            return
        tookDamage = self.damage > damage
        self.damage = damage
        newWidth = self._CalculateDamageBarWidth(damage)
        uicore.animations.StopAnimation(self.damageContainer, 'width')
        uicore.animations.MorphScalar(self.damageContainer, 'width', startVal=self.damageContainer.width, endVal=newWidth, duration=1.0)
        uicore.animations.MorphScalar(self.damageFlashContainer, 'width', startVal=self.damageFlashContainer.width, endVal=self.width - newWidth, duration=1.0)
        if tookDamage:
            self.damageFlashContainer.Show()
            uicore.animations.BlinkOut(self.damageFlashContainer, duration=1.0, curveType=uiconst.ANIM_BOUNCE, callback=self.damageFlashContainer.Hide)

    def _CalculateDamageBarWidth(self, damage):
        return max(self.width * (1.0 - damage), 0)


class HaulerDamageBars(Container):
    PAD_BETWEEN_BARS = 5
    DAMAGE_UPDATE_MS = 1000
    default_height = 3
    default_opacity = 0.75

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.ballpark = attributes.ballpark
        self.haulerID = attributes.haulerID
        damageState = self.ballpark.GetDamageState(self.haulerID)
        if damageState:
            shieldDamage, armorDamage, hullDamage, _, _ = self.ballpark.GetDamageState(self.haulerID)
        else:
            shieldDamage, armorDamage, hullDamage = (0.0, 0.0, 0.0)
        width, _ = self.GetAbsoluteSize()
        damageBarSize = (width - self.PAD_BETWEEN_BARS * 2) / 3
        self.shield = DamageBar(parent=self, damage=shieldDamage, align=uiconst.TORIGHT, width=damageBarSize, padLeft=self.PAD_BETWEEN_BARS)
        self.armor = DamageBar(parent=self, damage=armorDamage, align=uiconst.TORIGHT, width=damageBarSize, padLeft=self.PAD_BETWEEN_BARS)
        self.hull = DamageBar(parent=self, damage=hullDamage, align=uiconst.TORIGHT, width=damageBarSize)
        self.updateThread = AutoTimer(self.DAMAGE_UPDATE_MS, self._Update)

    def _Update(self):
        damageState = self.ballpark.GetDamageState(self.haulerID)
        wasHurt = False
        wasCritical = False
        if damageState:
            shieldDamage, armorDamage, hullDamage, _, _ = self.ballpark.GetDamageState(self.haulerID)
            wasHurt = shieldDamage < self.shield.damage or armorDamage < self.armor.damage or hullDamage < self.hull.damage
            wasCritical = hullDamage < self.hull.damage
            self.shield.SetDamageState(shieldDamage)
            self.armor.SetDamageState(armorDamage)
            self.hull.SetDamageState(hullDamage)
        if wasHurt:
            self.parent.parent.parent.OnHaulerDamage(self.haulerID, wasCritical)


class HaulerState(Container):
    default_width = 25
    default_height = 25
    BACKGROUND_COLOR = (0.0, 0.0, 0.0, 1.0)
    ICON = HAULER_STATE_DEFAULT_ICON
    LIFETIME_SECONDS = 5
    BLINK_DURATION = 0.5
    BLINK_LOOPS = 6
    HINT = ''
    default_state = uiconst.UI_NORMAL

    def GetColor(self):
        return self.BACKGROUND_COLOR

    def GetIcon(self):
        return self.ICON

    def ApplyAttributes(self, attributes):
        attributes.bgColor = self.GetColor()
        self.pulseTasklet = None
        Container.ApplyAttributes(self, attributes)
        self.sprite = Sprite(parent=self, width=self.width, height=self.height, align=uiconst.TOLEFT, texturePath=self.ICON)
        self.sprite.hint = self.HINT
        self.heartbeat = gametime.GetSimTime()
        uicore.animations.BlinkIn(self)

    def keep_alive(self):
        self.heartbeat = gametime.GetSimTime()
        uicore.animations.BlinkIn(self, duration=2.0, loops=1)

    def pulse(self):
        if self.pulseTasklet is None:
            self.pulseTasklet = uthread2.start_tasklet(self.do_pulse)

    def do_pulse(self):
        while not self.destroyed:
            self.opacity = 0.0
            uicore.animations.BlinkIn(self, duration=0.5, loops=1, sleep=True)
            uicore.animations.BlinkOut(self, duration=0.5, loops=1, sleep=True)

    def is_alive(self):
        return self.pulseTasklet is not None or gametime.GetSecondsSinceSimTime(self.heartbeat) < self.LIFETIME_SECONDS

    def update(self):
        if not self.is_alive():
            uicore.animations.BlinkOut(self, callback=self.Close)


class HaulerStateOreDeposited(HaulerState):
    BACKGROUND_COLOR = HAULER_ORE_DEPOSITED_COLOR
    ICON = HAULER_ORE_DEPOSITED_ICON
    HINT = localization.GetByLabel('UI/ResourceWars/HaulerIconOreAdded')

    def ApplyAttributes(self, attributes):
        HaulerState.ApplyAttributes(self, attributes)


class HaulerStateWarping(HaulerState):
    BACKGROUND_COLOR = HAULER_WARP_OUT_COLOR
    ICON = HAULER_WARP_OUT_ICON
    HINT = localization.GetByLabel('UI/ResourceWars/HaulerIconWarping')


class HaulerStateUnderAttack(HaulerState):
    BACKGROUND_COLOR = HAULER_UNDER_ATTACK_COLOR
    ICON = HAULER_UNDER_ATTACK_ICON
    HINT = localization.GetByLabel('UI/ResourceWars/HaulerIconAttacked')


class RWInfoPanelHaulerTaskEntry(ContainerAutoSize):
    default_padLeft = 0
    default_padRight = 0
    default_padTop = 0
    default_padBottom = 10
    default_state = uiconst.UI_NORMAL
    default_clipChildren = False
    default_alignMode = uiconst.TOTOP
    tooltipPointer = uiconst.POINT_LEFT_2
    HEADER_WIDTH = 270
    HEADER_HEIGHT = 25
    HEADER_MARGIN = 2
    HEADER_BG_COLOR = (0.1, 0.1, 0.1, 0.45)
    PROGRESS_HEIGHT = 20
    WARP_OUT_FADE_DURATION = 1.0
    LABEL_FADE_DURATION = 0.75
    BLINK_DURATION = 0.5
    BLINK_LOOPS = 6
    BRACKET_SIZE = 16
    __notifyevents__ = ['OnHaulerQuantityChangedInClient', 'OnHaulerFullInClient', 'OnHaulerDestroyedInClient']

    def ApplyAttributes(self, attributes):
        ContainerAutoSize.ApplyAttributes(self, attributes)
        self.haulerID = attributes.haulerID
        self.haulerProgress = attributes.haulerProgress
        self.displayedHaulerContentAmount = self.haulerProgress.contents
        self.ballpark = attributes.ballpark
        self.warpState = None
        self.notificationsPlayed = []
        self.haulerCont = Container(name='haulerCont', parent=self, width=self.HEADER_WIDTH, height=self.HEADER_HEIGHT, align=uiconst.TOTOP)
        bracketSvc = sm.GetService('bracket')
        bracket = bracketSvc.GetBracketDataByGroupID(invconst.groupNpcIndustrialCommand)
        self.bracketCont = Container(name='bracketCont', parent=self.haulerCont, width=self.HEADER_HEIGHT, height=self.HEADER_HEIGHT, bgColor=self.HEADER_BG_COLOR, align=uiconst.TOLEFT, texturePath=bracket.texturePath, padLeft=3)
        self.bracketSprite = Sprite(parent=self.bracketCont, align=uiconst.CENTER, texturePath=bracket.texturePath, width=self.BRACKET_SIZE, height=self.BRACKET_SIZE)
        self.bracketSprite.hint = localization.GetByLabel('UI/ResourceWars/HaulerHint')
        self.headerCont = Container(name='headerCont', parent=self.haulerCont, align=uiconst.TOALL, padLeft=self.HEADER_MARGIN, padRight=self.HEADER_HEIGHT)
        self.progressCont = Container(name='progressCont', parent=self.headerCont, height=self.PROGRESS_HEIGHT, bgColor=self.HEADER_BG_COLOR, align=uiconst.TOTOP)
        progressBarWidth = self._calculate_progress_bar_width(attributes.haulerProgress.contents)
        progressBarWrapper = Container(parent=self.progressCont, align=uiconst.TOALL)
        self.progressBar = Container(name='progressBar', parent=progressBarWrapper, bgColor=HAULER_PROGRESS_COLOR, width=progressBarWidth, align=uiconst.TOLEFT_PROP)
        self.progressLabel = None
        self._update_progress_label(self.haulerProgress.contents)
        self.stateCont = Container(name='stateCont', parent=self.haulerCont, height=self.HEADER_HEIGHT, width=self.HEADER_HEIGHT, align=uiconst.CENTERRIGHT)
        self.stateIcons = []
        self.stateIconThread = None
        self.haulerDamageBars = HaulerDamageBars(parent=self.headerCont, ballpark=self.ballpark, haulerID=self.haulerID, align=uiconst.TOBOTTOM, padRight=1)
        sm.RegisterNotify(self)

    def _FormatProgressText(self, contents):
        if self.haulerProgress.capacity == HAULER_CAPACITY_UNLIMITED:
            total = HAULER_CAPACITY_UNLIMITED_STR
        else:
            total = int(self.haulerProgress.capacity)
        return localization.GetByLabel(RW_PANEL_HAULER_PROGRESS_LABEL, current=int(contents), total=total)

    def get_capacity(self):
        return self.haulerProgress.capacity

    def _calculate_progress_bar_width(self, progress):
        if self.haulerProgress.capacity == HAULER_CAPACITY_UNLIMITED:
            return 0.0
        try:
            return float(progress) / self.haulerProgress.capacity
        except ZeroDivisionError:
            logger.warn('Hauler has no capacity')
            return 0.0

    def animate_progress_bar(self, new_progress):
        newWidth = self._calculate_progress_bar_width(new_progress)
        uicore.animations.StopAnimation(self.progressBar, 'width')
        uicore.animations.MorphScalar(self.progressBar, 'width', startVal=self.progressBar.width, endVal=newWidth, duration=1.0)
        if self.haulerProgress.contents >= self.haulerProgress.capacity:
            self.warpoutOverlay = Container(parent=self.progressCont, bgColor=HAULER_WARP_OUT_COLOR, align=uiconst.TOALL, opacity=0.0)
            uicore.animations.FadeIn(self.warpoutOverlay, duration=self.WARP_OUT_FADE_DURATION, timeOffset=1.0)
            uicore.animations.FadeOut(self.progressBar, duration=self.WARP_OUT_FADE_DURATION, timeOffset=1.0)
            completedText = localization.GetByLabel(RW_HAULER_PROGRESS_BAR_FULL_LABEL)
            self.completedLabel = EveLabelMedium(name='rw_completed_header_label', parent=self.progressCont, text=completedText, align=uiconst.TOLEFT_NOPUSH, padTop=3, padLeft=10, opacity=0)
            self.completedLabel.SetOrder(0)
            uicore.animations.FadeOut(self.progressLabel, timeOffset=self.WARP_OUT_FADE_DURATION, duration=self.LABEL_FADE_DURATION)
            uicore.animations.FadeIn(self.completedLabel, timeOffset=self.WARP_OUT_FADE_DURATION + self.LABEL_FADE_DURATION)
            if self.warpState is None:
                self.warpState = HaulerStateWarping(parent=self.stateCont, align=uiconst.TOLEFT, height=self.HEADER_HEIGHT, width=self.HEADER_HEIGHT, padLeft=3, opacity=0.0)
                self.warpState.pulse()

    def _update_progress_label(self, new_progress):
        text = self._FormatProgressText(new_progress)
        if self.progressLabel is not None and not self.progressLabel.destroyed:
            self.progressLabel.Close()
        self.progressLabel = EveLabelMedium(name='rw_progress_header_label', parent=self.progressCont, text=text, align=uiconst.TOLEFT_NOPUSH, padLeft=10, padTop=3)
        self.progressLabel.SetOrder(0)

    def play_milestone_audio(self, old_progress, new_progress):
        old_ratio = float(old_progress) / self.haulerProgress.capacity
        new_ratio = float(new_progress) / self.haulerProgress.capacity
        current_milestone = None
        event_to_play = None
        for milestone, audioEvent in HAULER_MILESTONE_AUDIO.iteritems():
            if milestone > old_ratio and milestone <= new_ratio and milestone > current_milestone:
                current_milestone = milestone
                event_to_play = audioEvent

        if event_to_play is not None:
            sm.GetService('audio').SendUIEvent(event_to_play)

    def update_progress(self, new_progress):
        self._update_progress_label(new_progress)
        self.animate_progress_bar(new_progress)
        self.play_milestone_audio(self.displayedHaulerContentAmount, new_progress)
        self.displayedHaulerContentAmount = new_progress

    def _add_hauler_state_icon(self, icon_class):
        for icon in self.stateIcons:
            if isinstance(icon, icon_class):
                icon.keep_alive()
                return

        state = icon_class(parent=self.stateCont, align=uiconst.TOLEFT, height=self.HEADER_HEIGHT, width=self.HEADER_HEIGHT, padLeft=3)
        self.stateIcons.append(state)
        self._kick_state_icon_thread()

    def OnHaulerQuantityChangedInClient(self, haulerID, quantity, totalQuantity, ownerID, typeID):
        if haulerID == self.haulerID:
            new_progress = max(self.haulerProgress.contents, totalQuantity)
            self.update_progress(new_progress)
            self._add_hauler_state_icon(HaulerStateOreDeposited)

    def OnHaulerFullInClient(self, haulerID):
        if haulerID in self.stateIcons:
            self.stateIcons.pop(haulerID)
        if haulerID == self.haulerID:
            if self.warpState:
                self.warpState.Close()
            self._add_hauler_state_icon(HaulerStateWarping)
            uicore.animations.BlinkOut(self.headerCont, duration=self.BLINK_DURATION, loops=self.BLINK_LOOPS, callback=self.Close)
            uicore.animations.BlinkOut(self.haulerDamageBars, duration=self.BLINK_DURATION, loops=self.BLINK_LOOPS, callback=self.Close)
            sm.GetService('audio').SendUIEvent('res_wars_haulers_warp_out_play')

    def play_notification_if_it_has_not_been_played_already(self, uiEventStr):
        if uiEventStr not in self.notificationsPlayed:
            self.notificationsPlayed.append(uiEventStr)
            sm.GetService('audio').SendUIEvent(uiEventStr)

    def OnHaulerDamage(self, haulerID, wasCritical):
        if haulerID == self.haulerID:
            self._add_hauler_state_icon(HaulerStateUnderAttack)
            event = 'voc_rw_aura_haulercritical_aura_play' if wasCritical else 'voc_rw_aura_haulerunderattack_aura_play'
            self.play_notification_if_it_has_not_been_played_already(event)

    def OnHaulerDestroyedInClient(self, haulerID):
        if haulerID == self.haulerID:
            self.animate_progress_bar(0)
            self.deathIconContainer = Container(parent=self.bracketCont, align=uiconst.TOALL, bgColor=DEATH_ICON_COLOR)
            self.deathSprite = Sprite(parent=self.deathIconContainer, align=uiconst.TOALL, texturePath=HAULER_DEATH_ICON, state=uiconst.UI_NORMAL)
            self.deathSprite.hint = localization.GetByLabel('UI/ResourceWars/HaulerIconDestroyed')
            self.deathIconContainer.SetOrder(0)
            uicore.animations.BlinkIn(self.deathIconContainer, duration=self.BLINK_DURATION, loops=self.BLINK_LOOPS, curveType=uiconst.ANIM_BOUNCE, callback=self.Close)
            self.play_notification_if_it_has_not_been_played_already('voc_rw_aura_haulerdestroyed_aura_play')

    def _state_icon_thread(self):
        while self.stateIcons:
            for icon in self.stateIcons[:]:
                icon.update()
                if not icon.is_alive():
                    self.stateIcons.remove(icon)

            uthread2.sleep_sim(1)

    def _kick_state_icon_thread(self):
        if self.stateIconThread is None or not self.stateIconThread.is_alive():
            self.stateIconThread = uthread2.start_tasklet(self._state_icon_thread)

    def OnClick(self, *args):
        sm.GetService('stateSvc').SetState(self.haulerID, states.selected, 1)
