#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\login\charcreation\empireStepContainer.py
import random
import carbonui.const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from carbonui.uicore import uicore
import charactercreator.client.scalingUtils as ccScalingUtils
import eve.client.script.ui.login.charcreation.ccUtil as ccUtil
from eve.client.script.ui.login.charcreation.empireui.empireBanner import EmpireBanner, BannerHeader
from eve.client.script.ui.login.charcreation.empireui.empireBanner import CURVED_GRADIENT_TEXTURE_BASE, CURVED_GRADIENT_OPACITY
from eve.common.lib import appConst
from localization import GetByLabel
from math import pi
from uthread2 import call_after_wallclocktime_delay, StartTasklet
from characterdata.races import CHARACTER_CREATION_RACE_IDS
HORIZONTAL_BANNER_FRAME = 'res:/UI/Texture/classes/EmpireSelection/panelSideDeco.png'
HORIZONTAL_BANNER_OPACITY = 0.3
EMPIRE_STEP_BANNER_HEADER_LABEL = 'UI/CharacterCreation/ChooseEmpire'
FORCE_TERMINATE_ANIMATION_SECS = 1.0
ANIMATION_THREAD_WAIT_MSECS = 100
PLAY_SOUNDS_ON_HOVER_DELAY_SECS = 0.1
FLARE_SOUND_PLAY = 'ui_es_enlist_flare_play'
FLARE_SOUND_STOP = 'ui_es_enlist_flare_stop'
BANNER_OPACITY_LIGHT = 1.0
BANNER_OPACITY_DARK = 0.3
BANNER_OPACITY_CHANGE_DURATION_SECS = 0.5
BANNER_FADEOUT_DURATION_SECS = 1.0

class EmpireBannerAnimationType:
    MOUSE_ENTER = 1
    MOUSE_EXIT = 2
    MOUSE_CLICK = 3


class EmpireStepContainer(Container):

    def ApplyAttributes(self, attributes):
        super(EmpireStepContainer, self).ApplyAttributes(attributes)
        self.step = attributes.step
        self.expandedRace = None
        self.currentAnimation = None
        self.processingAnimation = None
        self.nextAnimation = None
        self.isSelectingRace = False
        self.bannerFadeTasklet = None
        self.audioSvc = sm.GetService('audio')
        self.ConstructContents()
        self.PlayNoRaceMusic()

    def Close(self):
        if self.bannerFadeTasklet is not None:
            self.bannerFadeTasklet.kill()
            self.bannerFadeTasklet = None
        super(EmpireStepContainer, self).Close()

    def PlayNoRaceMusic(self):
        self.audioSvc.SendUIEvent('music_switch_race_norace')

    def ConstructContents(self):
        info = self.step.GetInfo()
        self.empireBanners = []
        self.header = BannerHeader(name='empireStepBannerHeader', parent=self, align=uiconst.TOTOP, width=self.width, height=ccScalingUtils.GetBannerHeaderHeight(), text=GetByLabel(EMPIRE_STEP_BANNER_HEADER_LABEL))
        self.buttonCont = Container(parent=self, name='buttonContainer', align=uiconst.CENTER, pos=(0,
         0,
         ccScalingUtils.GetBannersWidth(),
         ccScalingUtils.GetBannerHeight()), top=ccScalingUtils.GetBannerHeaderHeight())
        self.bannersContainer = Container(parent=self.buttonCont, name='bannersContainer', align=uiconst.CENTER, width=ccScalingUtils.GetBannersWidth(), height=ccScalingUtils.GetBannerHeight())
        padLeft = 0
        races = CHARACTER_CREATION_RACE_IDS
        random.shuffle(races)
        for raceID in races:
            factionID = appConst.factionByRace[raceID]
            isDisabled = ccUtil.IsFactionSelectionDisabled(factionID)
            banner = EmpireBanner(name='empireBanner', parent=self.bannersContainer, width=ccScalingUtils.GetBannerWidth(), height=ccScalingUtils.GetBannerHeight(), align=uiconst.TOLEFT, padLeft=padLeft, raceID=raceID, animationEnder=self.OnAnimationEnded, bannerEnterer=self.OnBannerEntered, bannerClicker=self.OnBannerClicked, bannerExiter=self.OnBannerExited, isDisabled=isDisabled)
            self.empireBanners.append(banner)
            padLeft = ccScalingUtils.BANNER_SEPARATION

        if info.raceID:
            self.raceID = info.raceID
        self.AddViewCaps()
        self.UpdateLayout()

    def UpdateLayout(self):
        self.TerminateAllAnimations()
        self.height = uicore.desktop.height - ccScalingUtils.GetTopNavHeight() - ccScalingUtils.GetBottomNavHeight()
        self.width = ccScalingUtils.GetMainPanelWidth()
        self._UpdateHeader()
        self._UpdateViewCaps()
        if self.expandedRace:
            self._UpdateExpandedBannerLayout()
        else:
            self._UpdateLayoutButtons()
        for child in self.children:
            if hasattr(child, 'UpdateLayout'):
                child.UpdateLayout()

    def _UpdateLayoutButtons(self):
        self._UpdateLayoutButtonContainer()
        self._UpdateLayoutBannersContainer()
        self._UpdateLayoutBanners()

    def _UpdateHeader(self):
        self.header.height = ccScalingUtils.GetBannerHeaderHeight()
        self.header.ResizeContent()

    def _UpdateViewCaps(self):
        width = ccScalingUtils.GetMainPanelWidth()
        height = ccScalingUtils.GetBannerHeaderHeight()
        self.topViewCap.width = width
        self.topViewCap.height = height
        self.topViewCap.top = -height
        self.bottomViewCap.width = width
        self.bottomViewCap.height = height

    def _UpdateExpandedBannerLayout(self):
        bannerWidth = ccScalingUtils.GetMainPanelWidth()
        bannerHeight = ccScalingUtils.GetMainPanelHeight()
        self.bannersContainer.width = bannerWidth
        self.bannersContainer.height = bannerHeight
        for banner in self.empireBanners:
            banner.Resize(bannerWidth, bannerHeight)

    def _UpdateLayoutButtonContainer(self):
        bannersWidthExpanded = ccScalingUtils.GetBannersWidth()
        bannersHeightExpanded = ccScalingUtils.GetBannerHeight()
        self.buttonCont.pos = (0,
         ccScalingUtils.GetBannerHeaderHeight(),
         bannersWidthExpanded,
         bannersHeightExpanded)

    def _UpdateLayoutBannersContainer(self):
        bannersWidth = ccScalingUtils.GetBannersWidth()
        bannersHeight = ccScalingUtils.GetBannerHeight()
        self.bannersContainer.width = bannersWidth
        self.bannersContainer.height = bannersHeight

    def _UpdateLayoutBanners(self):
        bannerWidth = ccScalingUtils.GetBannerWidth()
        bannerHeight = ccScalingUtils.GetBannerHeight()
        for banner in self.empireBanners:
            banner.width = bannerWidth
            banner.height = bannerHeight
            banner.ResizeContents(bannerWidth, bannerHeight)

        self.OnBannerExited()

    def ExpandRace(self, raceID):
        self.TerminateAllAnimations()
        self.expandedRace = raceID
        self.bannersContainer.width = ccScalingUtils.GetMainPanelWidth()
        self.bannersContainer.height = ccScalingUtils.GetMainPanelHeight()
        for banner in self.empireBanners:
            banner.padLeft = 0
            if banner.raceID != raceID:
                banner.Hide()
            else:
                banner.Show()
                banner.Expand()

        self.buttonCont.state = uiconst.UI_DISABLED
        self.header.Hide()

    def OnAnimationEnded(self, raceID):
        if self.processingAnimation and raceID in self.processingAnimation:
            self.processingAnimation[raceID] = None
        if not self.processingAnimation or not any(self.processingAnimation.values()):
            self.processingAnimation = None

    def OnBannerEntered(self, raceID):
        if self.isSelectingRace:
            return
        animation = {}
        for banner in self.empireBanners:
            if banner.raceID == raceID:
                animation[banner.raceID] = EmpireBannerAnimationType.MOUSE_ENTER
            else:
                animation[banner.raceID] = EmpireBannerAnimationType.MOUSE_EXIT

        self.nextAnimation = animation
        self.TriggerAnimation()

    def OnBannerExited(self):
        if self.isSelectingRace:
            return
        animation = {}
        for banner in self.empireBanners:
            animation[banner.raceID] = EmpireBannerAnimationType.MOUSE_EXIT

        self.nextAnimation = animation
        self.TriggerAnimation()

    def TriggerAnimation(self):
        StartTasklet(self.ProcessAnimations)

    def TerminateAllAnimations(self):
        self.currentAnimation = None
        self.processingAnimation = None
        self.nextAnimation = None
        self.StopFlareSound()

    def TerminateAnimation(self, animation):
        if self.processingAnimation == animation:
            self.processingAnimation = None
            self.StopFlareSound()

    def ProcessAnimations(self):
        if self.nextAnimation:
            self.currentAnimation = self.nextAnimation
            self.nextAnimation = None
            call_after_wallclocktime_delay(self.TerminateAnimation, FORCE_TERMINATE_ANIMATION_SECS, self.currentAnimation)
            self.ProcessAnimation()

    def ProcessAnimation(self):
        animationToProcess = {}
        enteredBannerRaceID = None
        isClickAnimation = False
        for banner in self.empireBanners:
            raceID = banner.raceID
            if raceID in self.currentAnimation:
                animationType = self.currentAnimation[raceID]
                if animationType == EmpireBannerAnimationType.MOUSE_ENTER:
                    banner.AnimateEntered()
                    call_after_wallclocktime_delay(banner.PlaySoundsOnEntered, PLAY_SOUNDS_ON_HOVER_DELAY_SECS)
                    enteredBannerRaceID = raceID
                elif animationType == EmpireBannerAnimationType.MOUSE_EXIT:
                    banner.AnimateExited()
                elif animationType == EmpireBannerAnimationType.MOUSE_CLICK:
                    self.AnimateClick(raceID)
                    isClickAnimation = True
                animationToProcess[raceID] = animationType

        self.processingAnimation = animationToProcess
        self.currentAnimation = None
        if isClickAnimation:
            self.TerminateAllAnimations()
            return
        self.AnimateBannerOpacityChange(enteredBannerRaceID)
        if enteredBannerRaceID is None:
            self.StopFlareSound()
        else:
            call_after_wallclocktime_delay(self.PlayFlareSound, PLAY_SOUNDS_ON_HOVER_DELAY_SECS)

    def AnimateBannerOpacityChange(self, enteredBannerRaceID):
        animation = animations.MorphScalar
        for banner in self.empireBanners:
            duration = BANNER_OPACITY_CHANGE_DURATION_SECS
            oldOpacity = banner.opacity
            showLightOpacity = enteredBannerRaceID is None or banner.raceID == enteredBannerRaceID
            newOpacity = BANNER_OPACITY_LIGHT if showLightOpacity else BANNER_OPACITY_DARK
            animation(banner, 'opacity', startVal=oldOpacity, endVal=newOpacity, duration=duration)

    def PlayFlareSound(self):
        self.audioSvc.SendUIEvent(FLARE_SOUND_PLAY)

    def StopFlareSound(self):
        self.audioSvc.SendUIEvent(FLARE_SOUND_STOP)

    def ShowBackgroundBanner(self, raceID):
        self.Flush()
        self.ConstructContents()
        self.ExpandRace(raceID)

    def SetTitle(self, text):
        for banner in self.empireBanners:
            banner.ConstructHeader(text)

    def AddViewCaps(self):
        width = ccScalingUtils.GetMainPanelWidth()
        height = ccScalingUtils.GetBannerHeaderHeight()
        texturePath = CURVED_GRADIENT_TEXTURE_BASE
        self.topViewCap = Sprite(name='topViewCap', parent=self, align=uiconst.TOTOP_NOPUSH, texturePath=texturePath, state=uiconst.UI_DISABLED, width=width, height=height, top=-height, rotation=pi, opacity=0.0)
        self.bottomViewCap = Sprite(name='bottomViewCap', parent=self, align=uiconst.TOBOTTOM_NOPUSH, texturePath=texturePath, state=uiconst.UI_DISABLED, width=width, height=height, rotation=0.0, opacity=0.0)

    def ShowViewCaps(self):
        self.topViewCap.opacity = CURVED_GRADIENT_OPACITY
        self.bottomViewCap.opacity = CURVED_GRADIENT_OPACITY

    def HideViewCaps(self):
        self.topViewCap.opacity = 0.0
        self.bottomViewCap.opacity = 0.0

    def SetBannerCapsForMenu(self):
        for banner in self.empireBanners:
            banner.ShowTopBlackGradient()
            banner.ShowBottomPanelCap()
            banner.HideTopPanelCap()

    def SetBannerCapsForView(self):
        for banner in self.empireBanners:
            banner.ShowTopPanelCap()
            banner.ShowBottomPanelCap()
            banner.HideTopBlackGradient()

    def HideBannerCaps(self):
        for banner in self.empireBanners:
            banner.HideTopPanelCap()
            banner.HideBottomPanelCap()
            banner.HideTopBlackGradient()

    def OnBannerClicked(self, raceID):
        if self.isSelectingRace:
            return
        self.isSelectingRace = True
        animation = {}
        for banner in self.empireBanners:
            if banner.raceID == raceID:
                animation[banner.raceID] = EmpireBannerAnimationType.MOUSE_CLICK

        self.nextAnimation = animation
        self.TriggerAnimation()

    def AnimateClick(self, raceID):
        animation = animations.FadeOut
        for banner in self.empireBanners:
            animation(banner, duration=BANNER_FADEOUT_DURATION_SECS)

        self.bannerFadeTasklet = call_after_wallclocktime_delay(self.SelectRace, BANNER_FADEOUT_DURATION_SECS, raceID)

    def SelectRace(self, raceID):
        self.bannerFadeTasklet = None
        uicore.layer.charactercreation.controller.SelectRace(raceID)
        self.isSelectingRace = False
