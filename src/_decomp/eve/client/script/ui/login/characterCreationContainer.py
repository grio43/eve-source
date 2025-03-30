#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\login\characterCreationContainer.py
import copy
import math
import random
import time
import types
import blue
import geo2
import mathext
import telemetry
import carbonui.const as uiconst
import charactercreator.client.animparams as animparams
import charactercreator.client.characterCreationMetrics as ccm
import charactercreator.client.scalingUtils as ccScalingUtils
import charactercreator.const as ccConst
import eve.client.script.ui.login.charcreation.ccUtil as ccUtil
import eve.common.lib.appConst as const
import evegraphics.settings as gfxsettings
import everesourceprefetch
import gatekeeper
import localization
import log
import paperdoll
import utillib
from carbonui import Density
from carbonui.control.button import Button
from carbonui.primitives.fill import Fill
from carbonui.util.bunch import Bunch
from eve.client.script.ui.control.eveLoadingWheel import LoadingWheel
from eve.common.script.paperDoll.paperDollDefinitions import BODY_CATEGORIES, DEFAULT_NUDE_PARTS, DESIRED_ORDER, LOD_SKIN
from eve.common.script.util import paperDollUtil
import trinity
import uthread
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui.primitives.container import Container
from carbonui.primitives.gradientSprite import GradientSprite
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from charactercreator.client.characterCreationSteps import ModeStorage, GetStepOrder, GetStepsUpToAndIncluding, STEP_ORDER_LIST
from charactercreator.client.logging.stepLogger import StepLogger
from eve.client.script.ui.camera.charCreationCamera import CharCreationCamera
from carbonui.control.buttonIcon import ButtonIcon
from eve.client.script.ui.login.charcreation.charCreationButtons import EXIT_BUTTON_SIZE
from eve.client.script.ui.login.charcreation.empireStepContainer import EmpireStepContainer
from eve.client.script.ui.login.charcreation.portraitMaker import PortraitMaker
from eve.client.script.ui.login.charcreation.charCreationNavigation import CharCreationNavigation
from eve.client.script.ui.login.charcreation.steps.bloodLineStep import BloodlineStep
from eve.client.script.ui.login.charcreation.steps.characterCustomization import CharacterCustomization
from eve.client.script.ui.login.charcreation.steps.characterNaming import CharacterNaming
from eve.client.script.ui.login.charcreation.steps.characterPortrait import CharacterPortrait
from eve.client.script.ui.login.charcreation.steps.empireStep import EmpireStep
from eve.client.script.ui.login.charcreation.steps.technologyStep import TechnologyStep, GetEmpireNavigationWidth, GetEmpireNavigationHeight
from eve.client.script.ui.login.charcreation.technologyViewUtils import EmpireNavigation
from eve.client.script.ui.login.charcreation.technologyViewsTracker import TechnologyViewsTracker
from eve.client.script.ui.login.charcreation.assetMenu import femaleModifierDisplayNames, maleModifierDisplayNames
from eve.client.script.ui.shared.colorThemes import DEFAULT_COLORTHEMEID, COLOR_THEME_ID_BY_RACE
from eve.client.script.ui.util.disconnectNotice import DisconnectNotice
from eveprefs import prefs
from fsdBuiltData.common.graphicIDs import GetGraphicFile
from locks import TempLock
from eveexceptions import UserError
from storylines.client.airnpe import is_air_npe_enabled
NETWORKMODE_BASIC = 1
NETWORKMODE_PORTRAIT = 2
LEFT_SIDE_WITH = 180
LEFT_SIDE_HEIGHT = 400
RIGHT_SIDE_WIDTH = 350
RIGHT_SIDE_HEIGHT = ccConst.BUTTON_AREA_HEIGHT
BOTTOM_LEFT_SIDE_WIDTH = 220
BOTTOM_LEFT_SIDE_HEIGHT = ccConst.BUTTON_AREA_HEIGHT
BUTTON_WIDTH = 145
BUTTON_HEIGHT = 36
BUTTON_FONT_SIZE = 18
BACKGROUND_TRANSITION_SECONDS = 2.5
RESOURCE_WHEEL_SEPARATION = 8
DOLLSTATES_TO_RETURN_TO_CC = [paperdoll.State.no_existing_customization, paperdoll.State.force_recustomize]
CLOTHING_ITEMS = (ccConst.topouter,
 ccConst.topmiddle,
 ccConst.bottomouter,
 ccConst.outer,
 ccConst.feet,
 ccConst.glasses,
 ccConst.bottommiddle,
 ccConst.mask)
RACE_TO_RESOURCE_NAME = {const.raceCaldari: 'caldari',
 const.raceAmarr: 'amarr',
 const.raceMinmatar: 'minmatar',
 const.raceGallente: 'gallente'}
TOP_NAVIGATION_LINE_HEIGHT = 1
BOTTOM_NAVIGATION_LINE_HEIGHT = 1
TOP_NAVIGATION_LINE_OPACITY = 0.25
BOTTOM_NAVIGATION_LINE_OPACITY = 0.25
EXIT_BUTTON_MARGIN = 10
BG_OPACITY = 1.0
BG_WIDTH = 2117
BG_HEIGHT = 1200
VIGNETTE_RGB_DATA = ((0.0, (0.0, 0.0, 0.0)), (0.5, (0.0, 0.0, 0.0)), (1.0, (0.0, 0.0, 0.0)))
VIGNETTE_ALPHA_DATA = ((0.0, 0.0), (0.8, 0.5), (1.0, 1.0))
VIGNETTE_OPACITY = 0.7
STEPS_WITH_VIGNETTE_EFFECT = [ccConst.BLOODLINESTEP]

class CharacterCreationContainer(Container):
    __notifyevents__ = ['OnSetDevice',
     'OnGraphicSettingsChanged',
     'OnHideUI',
     'OnShowUI',
     'OnDollUpdated',
     'OnMapShortcut',
     'OnUIRefresh',
     'OnDisconnect',
     'OnUIScalingChange']
    __update_on_reload__ = 1

    def ApplyAttributes(self, attributes):
        super(CharacterCreationContainer, self).ApplyAttributes(attributes)
        sm.RegisterNotify(self)
        self.needSculptingTutorial = True
        self.needNavigationTutorial = True
        self.step = None
        self.mainNav = None
        self.vignette = None
        self.backgroundGradient = None
        self.backgroundSprite = None
        self.topNavigationWhiteLineContainer = None
        self.bottomNavigationWhiteLineContainer = None
        self.exitButton = None
        self.empireNavigationContainer = None

    def SetNameCallback(self, name):
        self.charName = name

    @telemetry.ZONE_METHOD
    def OnSetDevice(self, *args):
        self.UpdateLayout()
        self.UpdateBackdrop()

    def OnDisconnect(self, reason = 0, msg = ''):
        disconnectNotice = DisconnectNotice(logProvider=self)
        disconnectNotice.OnDisconnect(reason, msg)

    @telemetry.ZONE_METHOD
    def UpdateLayout(self):
        try:
            self.LockEverything()
            with TempLock('CharacterCreationLayerUpdate'):
                for each in self.mainCont.children:
                    if hasattr(each, 'UpdateLayout'):
                        each.UpdateLayout()

                desktopWidth = uicore.desktop.width
                self.empireStepContainer.UpdateLayout()
                self.topNavigationContainer.width = desktopWidth
                self.bottomNavigationContainer.width = desktopWidth
                self.topNavigationContainer.height = ccScalingUtils.GetTopNavHeight()
                self.bottomNavigationContainer.height = ccScalingUtils.GetBottomNavHeight()
                self.empireNavigationButtonContainer.width = ccScalingUtils.GetMainPanelWidth()
                self.empireNavigationButtonContainer.height = self.bottomNavigationContainer.height
                if self.empireNavigationContainer:
                    self.empireNavigationContainer.Close()
                    self._AddEmpireNavigation(self.stepID)
                self.AddWhiteLines()
                self.AddBackgroundGradient()
                self.AddVignetteEffect()
                self.UpdateVisualArtifacts(self.stepID)
        finally:
            self.UnlockEverything()

    def UpdateVisualArtifacts(self, stepID):
        if stepID in [ccConst.EMPIRESTEP, ccConst.TECHNOLOGYSTEP]:
            self.ShowWhiteLines()
            self.ShowBackgroundGradient()
        elif stepID == ccConst.BLOODLINESTEP:
            self.ShowWhiteLines()
            self.HideBackgroundGradient()
        else:
            self.HideWhiteLines()
            self.HideBackgroundGradient()
        if stepID in STEPS_WITH_VIGNETTE_EFFECT:
            self.ShowVignetteEffect()
        else:
            self.HideVignetteEffect()

    def ShowVignetteEffect(self):
        if self.vignette and not self.vignette.destroyed:
            self.vignette.opacity = VIGNETTE_OPACITY

    def HideVignetteEffect(self):
        if self.vignette and not self.vignette.destroyed:
            self.vignette.opacity = 0.0

    def AddVignetteEffect(self):
        width, height = self._GetBackdropSpriteSizes()
        if self.vignette and not self.vignette.destroyed:
            self.vignette.width = width
            self.vignette.height = height
            return
        self.vignette = GradientSprite(name='vignetteGradientSprite', align=uiconst.CENTER, parent=self, width=width, height=height, rgbData=VIGNETTE_RGB_DATA, alphaData=VIGNETTE_ALPHA_DATA, radial=True, opacity=0.0)

    def ShowBackgroundGradient(self):
        if self.backgroundGradient and not self.backgroundGradient.destroyed:
            self.backgroundGradient.opacity = 1.0

    def HideBackgroundGradient(self):
        if self.backgroundGradient and not self.backgroundGradient.destroyed:
            self.backgroundGradient.opacity = 0.0

    def AddBackgroundGradient(self):
        if self.backgroundGradient and not self.backgroundGradient.destroyed:
            self.backgroundGradient.Close()
        start = min(0.4, (uicore.desktop.width - ccScalingUtils.GetMainPanelWidth()) / (2 * uicore.desktop.width))
        self.backgroundGradient = GradientSprite(name='backgroundGradient', parent=self, align=uiconst.TOALL, rgbData=[(0, (0.0, 0.0, 0.0))], alphaData=[(0, 0.0),
         (start, 0.0),
         (0.4, 0.5),
         (0.6, 0.5),
         (1.0 - start, 0.0),
         (1.0, 0.0)], padTop=self.topNavigationContainer.height, padBottom=self.bottomNavigationContainer.height)

    def ShowWhiteLines(self):
        if self.topNavigationWhiteLineContainer and not self.topNavigationWhiteLineContainer.destroyed:
            self.topNavigationWhiteLineContainer.opacity = TOP_NAVIGATION_LINE_OPACITY
        if self.bottomNavigationWhiteLineContainer and not self.bottomNavigationWhiteLineContainer.destroyed:
            self.bottomNavigationWhiteLineContainer.opacity = BOTTOM_NAVIGATION_LINE_OPACITY

    def HideWhiteLines(self):
        if self.topNavigationWhiteLineContainer and not self.topNavigationWhiteLineContainer.destroyed:
            self.topNavigationWhiteLineContainer.opacity = 0.0
        if self.bottomNavigationWhiteLineContainer and not self.bottomNavigationWhiteLineContainer.destroyed:
            self.bottomNavigationWhiteLineContainer.opacity = 0.0

    def AddWhiteLines(self):
        if self.topNavigationWhiteLineContainer and not self.topNavigationWhiteLineContainer.destroyed:
            self.topNavigationWhiteLineContainer.Close()
        self.topNavigationWhiteLineContainer = Container(name='topNavigationWhiteLineContainer', parent=self.topNavigationContainer, align=uiconst.TOTOP_NOPUSH, width=self.uiContainer.width, height=self.topNavigationContainer.height, opacity=0.0)
        GradientSprite(name='topNavigationWhiteLine', parent=self.topNavigationWhiteLineContainer, align=uiconst.TOBOTTOM, width=self.uiContainer.width, height=TOP_NAVIGATION_LINE_HEIGHT, rgbData=[(0, (1.0, 1.0, 1.0))], alphaData=[(0, 0.0),
         (0.4, 1.0),
         (0.6, 1.0),
         (1.0, 0.0)])
        if self.bottomNavigationWhiteLineContainer and not self.bottomNavigationWhiteLineContainer.destroyed:
            self.bottomNavigationWhiteLineContainer.Close()
        self.bottomNavigationWhiteLineContainer = Container(name='bottomNavigationWhiteLineContainer', parent=self.bottomNavigationContainer, align=uiconst.TOBOTTOM_NOPUSH, width=self.uiContainer.width, height=self.bottomNavigationContainer.height, opacity=0.0)
        GradientSprite(name='bottomNavigationWhiteLine', parent=self.bottomNavigationWhiteLineContainer, align=uiconst.TOTOP, width=self.uiContainer.width, height=BOTTOM_NAVIGATION_LINE_HEIGHT, rgbData=[(0, (1.0, 1.0, 1.0))], alphaData=[(0, 0.0),
         (0.4, 1.0),
         (0.6, 1.0),
         (1.0, 0.0)])

    @telemetry.ZONE_METHOD
    def OnOpenView(self, **kwargs):
        self.startTime = blue.os.GetWallclockTime()
        self.backgroundGradient = None
        self.topNavigationWhiteLineContainer = None
        self.bottomNavigationWhiteLineContainer = None
        self.vignette = None
        uicore.cmd.commandMap.UnloadAllAccelerators()
        uicore.cmd.commandMap.LoadAcceleratorsByCategory('general')
        uicore.cmd.commandMap.LoadAcceleratorsByCategory('charactercreator')
        self.freezingAnimation = False
        from eve.client.script.ui.shared.preview import PreviewCharacterWnd, PreviewWnd
        previewCharWnd = PreviewCharacterWnd.GetIfOpen()
        if previewCharWnd:
            self.previewCharWindowWasOpenOn = (previewCharWnd.charID, previewCharWnd.dna)
            previewCharWnd.CloseByUser()
        else:
            self.previewCharWindowWasOpenOn = None
        previewWnd = PreviewWnd.GetIfOpen()
        if previewWnd:
            self.previewWindowWasOpenOn = previewWnd.typeID
            previewWnd.CloseByUser()
        else:
            self.previewWindowWasOpenOn = None
        self._setColorsByCategory = {}
        self._setSpecularityByCategory = {}
        self._setIntensityByCategory = {}
        self.characterSvc = sm.GetService('character')
        self.sceneManager = sm.GetService('sceneManager')
        self.alreadyLoadedOldPortraitData = False
        self.backdropPath = None
        self.colorCodedBackDrop = None
        self.posePath = None
        self.lightingID = ccConst.LIGHT_SETTINGS_ID[0]
        self.lightColorID = ccConst.LIGHT_COLOR_SETTINGS_ID[0]
        self.lightIntensity = 0.5
        self.camera = None
        self.cameraUpdateJob = None
        self.fastCharacterCreation = gfxsettings.Get(gfxsettings.GFX_CHAR_FAST_CHARACTER_CREATION)
        self.bloodlineSelector = None
        self.raceMusicStarted = False
        self.jukeboxWasPlaying = False
        self.mode = ccConst.MODE_FULLINITIAL_CUSTOMIZATION
        self.modeStorage = ModeStorage()
        self.modeObject = self.modeStorage.GetModeFor(self.mode)
        self.charID = None
        self.raceID = None
        self.bloodlineID = None
        self.genderID = None
        self.schoolID = None
        self.charName = ''
        self.clothesOff = 0
        self.clothesStorage = {}
        self.clothesMetaStorage = {}
        self.dnaList = None
        self.dna = None
        self.lastLitHistoryBit = None
        sm.GetService('cc').ClearMyAvailabelTypeIDs()
        self.backgroundSprite = None
        self.stepID = None
        self.floor = None
        self.showingHelp = 0
        self.empireStepContainer = None
        self.topNavigationContainer = None
        self.bottomNavigationContainer = None
        self.empireNavigationContainer = None
        self.CreateUI()
        self.avatarScene = None
        self.animatingToPortraitID = None
        self.animateToStoredPortraitThread = None
        self.technologyViewsTracker = None
        self.audioService = sm.GetService('audio')
        self.worldLevel = self.audioService.GetWorldVolume()
        self.audioService.SetWorldVolume(0.0)
        self.stepLogger = StepLogger(blue.os.GetWallclockTime)
        self.finalStepLogger = None
        self.metrics = None
        self.approve_in_progress = False
        self.save_in_progress = False

    def Finalize(self):
        self.Save()

    def CreateLoadingWheel(self):
        self.loadingWheel = LoadingWheel(name='loadingWheel', parent=self, align=uiconst.CENTER, state=uiconst.UI_NORMAL)
        self.loadingWheel.forcedOn = 0

    def CreateUI(self):
        self.uiContainer = Container(name='uiContainer', parent=self, align=uiconst.TOALL)
        self.CreateLoadingWheel()
        self.leftSide = Container(name='leftSide', parent=self.uiContainer, align=uiconst.TOPLEFT, pos=(0,
         0,
         LEFT_SIDE_WITH,
         LEFT_SIDE_HEIGHT))
        self.rightSide = Container(name='rightSide', parent=self.uiContainer, align=uiconst.BOTTOMRIGHT, pos=(0,
         0,
         RIGHT_SIDE_WIDTH,
         RIGHT_SIDE_HEIGHT))
        self.bottomLeftSide = Container(name='bottomLeftSide', parent=self.uiContainer, align=uiconst.BOTTOMLEFT, pos=(0,
         0,
         BOTTOM_LEFT_SIDE_WIDTH,
         BOTTOM_LEFT_SIDE_HEIGHT))
        self.buttonNavLeft = Container(name='buttonNavLeft', parent=self.bottomLeftSide, align=uiconst.TOTOP, height=BUTTON_HEIGHT, padLeft=10)
        self.buttonNavRight = Container(name='buttonNavRight', parent=self.rightSide, align=uiconst.TOTOP, height=BUTTON_HEIGHT, padRight=10)
        self.finalizeBtn = Button(name='finalizeButtonCC', parent=self.buttonNavRight, align=uiconst.TORIGHT, label=localization.GetByLabel('UI/CharacterCreation/EnterGame'), func=self.Finalize, left=10, args=(), state=uiconst.UI_HIDDEN, density=Density.EXPANDED)
        self.saveBtn = Button(name='saveButtonCC', parent=self.buttonNavRight, align=uiconst.TORIGHT, label=localization.GetByLabel('UI/CharacterCreation/Finalize'), func=self.Save, left=10, args=(), state=uiconst.UI_HIDDEN, density=Density.EXPANDED)
        self.approveBtn = Button(name='nextButtonCC', parent=self.buttonNavRight, align=uiconst.TORIGHT, label=localization.GetByLabel('UI/Generic/Next'), func=self.Approve, left=10, args=(), density=Density.EXPANDED)
        self.backBtn = Button(name='backButtonCC', parent=self.buttonNavLeft, align=uiconst.TOLEFT, label=localization.GetByLabel('UI/Commands/Back'), func=self.Back, args=(), left=10, density=Density.EXPANDED)
        self.blackOut = Fill(name='blackOutFill', parent=self, color=(0.0, 0.0, 0.0, 0.0))
        self.mainCont = Container(name='mainCont', parent=self, align=uiconst.TOALL)
        desktopHeight = uicore.desktop.height
        topNavHeight = ccScalingUtils.GetTopNavHeight()
        bottomNavHeight = ccScalingUtils.GetBottomNavHeight()
        width = ccScalingUtils.GetMainPanelWidth()
        height = desktopHeight - topNavHeight - bottomNavHeight
        self.empireStepContainer = EmpireStepContainer(name='empireStepContainer', parent=self.uiContainer, align=uiconst.CENTER, width=width, height=height, state=uiconst.UI_NORMAL, step=self)
        self.empireStepContainer.SetOrder(0)
        self.topNavigationContainer = Container(name='topNavigationContainer', parent=self.uiContainer, align=uiconst.TOTOP_NOPUSH, width=self.uiContainer.width, height=topNavHeight, bgColor=(0.0, 0.0, 0.0, 1.0))
        self.topNavigationContainer.SetOrder(1)
        self.bottomNavigationContainer = Container(name='bottomNavigationContainer', parent=self.uiContainer, align=uiconst.TOBOTTOM_NOPUSH, width=self.uiContainer.width, height=bottomNavHeight, bgColor=(0.0, 0.0, 0.0, 1.0))
        self.bottomNavigationContainer.SetOrder(2)
        self.empireNavigationButtonContainer = Container(parent=self.bottomNavigationContainer, align=uiconst.CENTER, width=width, height=self.bottomNavigationContainer.height)
        self.UpdateLayout()

    def OnAvailabilityCheck(self, name):
        if self.finalStepLogger:
            self.finalStepLogger.AddTriedName(name)

    def OnUIRefresh(self):
        while getattr(self, 'doll', None) and self.doll.IsBusyUpdating():
            blue.synchro.Yield()

        self.Flush()
        self.CreateUI()
        self.SwitchStep(self.stepID)

    def OnUIScalingChange(self, *args):
        if not self.destroyed and self.stepID in ccConst.EMPIRE_SELECTION_STEPS:
            self.UpdateLayout()
            self.UpdateBackdrop()

    def OnHelpMouseEnter(self, btn, *args):
        PlaySound('ui_icc_button_mouse_over_play')
        btn.sr.icon.SetAlpha(1.0)

    def OnHelpMouseExit(self, btn, *args):
        if not self.showingHelp:
            btn.sr.icon.SetAlpha(0.5)

    def SetHintText(self, modifier, hintText = ''):
        if self.stepID in (ccConst.CUSTOMIZATIONSTEP, ccConst.PORTRAITSTEP):
            self.step.SetHintText(modifier, hintText)

    def SetMode(self, modeID):
        self.mode = modeID
        self.modeObject = self.modeStorage.GetModeFor(modeID)

    def GetModeIDForDollState(self, dollState):
        mode = ccConst.MODE_LIMITED_RECUSTOMIZATION
        if dollState == paperdoll.State.full_recustomizing:
            mode = ccConst.MODE_FULL_BLOODLINECHANGE
        elif dollState in (paperdoll.State.resculpting, paperdoll.State.no_existing_customization, paperdoll.State.force_recustomize):
            mode = ccConst.MODE_FULL_RECUSTOMIZATION
        return mode

    @telemetry.ZONE_METHOD
    def SetCharDetails(self, charID = None, gender = None, raceID = None, bloodlineID = None, dollState = None):
        self.ClearFacePortrait()
        self.dollState = dollState
        self.dna = None
        self.charID = 0
        self.raceID = raceID
        if charID:
            self.bloodlineID = bloodlineID
            self.genderID = int(gender)
            self.charID = charID
            if dollState not in (paperdoll.State.force_recustomize, paperdoll.State.no_existing_customization):
                self.dna = sm.GetService('paperdoll').GetMyPaperDollData(self.charID)
            mode = self.GetModeIDForDollState(dollState)
        else:
            mode = ccConst.MODE_FULLINITIAL_CUSTOMIZATION
            if self._IsUserInSkipTechnologyStepCohort():
                self._DeleteTechStep()
        self.SetMode(mode)
        self.availableSteps = self.modeObject.GetSteps()
        stepID = self.availableSteps[0]
        self.stepsUsed = {stepID}
        self.mainCont.Flush()
        self.stepLogger.Start()
        if dollState in (paperdoll.State.force_recustomize, paperdoll.State.no_existing_customization) or mode == ccConst.MODE_FULLINITIAL_CUSTOMIZATION:
            self.metrics = ccm.CharacterCreationMetrics(mode, ccConst.LOGIN)
        else:
            self.metrics = ccm.CharacterCreationMetrics(mode, ccConst.HANGAR)
        self.needSculptingTutorial = self.CanChangeBaseAppearance()
        self.SwitchStep(stepID)

    @telemetry.ZONE_METHOD
    def _IsUserInSkipTechnologyStepCohort(self):
        if gatekeeper.user.IsInCohort(gatekeeper.cohortSkipTechScreen):
            return True
        else:
            return False

    def _DeleteTechStep(self):
        steps = self.modeStorage.GetModeFor(ccConst.MODE_FULLINITIAL_CUSTOMIZATION)
        if ccConst.TECHNOLOGYSTEP in steps.GetSteps():
            steps.GetSteps().remove(ccConst.TECHNOLOGYSTEP)
            STEP_ORDER_LIST.remove(ccConst.TECHNOLOGYSTEP)

    @telemetry.ZONE_METHOD
    def GetInfo(self):
        return Bunch(charID=self.charID, raceID=self.raceID, bloodlineID=self.bloodlineID, genderID=self.genderID, dna=self.dna, schoolID=self.schoolID, stepID=self.stepID, charName=self.charName)

    def CanChangeBaseAppearance(self, *args):
        return self.modeObject.CanChangeBaseAppearance()

    def GetMode(self, *args):
        return self.mode

    def CanChangeBloodline(self, *args):
        return self.modeObject.CanChangeBloodLine()

    def CanChangeGender(self, *args):
        return self.modeObject.CanChangeGender()

    def CanChangeName(self, *args):
        return self.modeObject.CanChangeName()

    def _AddExitButton(self, toStep):
        if self.exitButton and not self.exitButton.destroyed:
            self.exitButton.Close()
        self.exitButton = ButtonIcon(name='exitButton', parent=self.topNavigationContainer, func=self.CancelCharacterCreation, texturePath='res:/UI/Texture/Icons/73_16_45.png', align=uiconst.TOPRIGHT, left=EXIT_BUTTON_MARGIN, top=EXIT_BUTTON_MARGIN, width=EXIT_BUTTON_SIZE, height=EXIT_BUTTON_SIZE, idx=0)

    def ConstructNavigationIfNeeded(self, toStep):
        self._AddExitButton(toStep)
        self._AddEmpireNavigation(toStep)
        if toStep == ccConst.EMPIRESTEP:
            return
        if not self.mainNav or self.mainNav.destroyed:
            navSteps = copy.copy(self.availableSteps)
            if ccConst.EMPIRESTEP in navSteps:
                navSteps.remove(ccConst.EMPIRESTEP)
            self.mainNav = CharCreationNavigation(name='navigation', align=uiconst.CENTERTOP, parent=self.leftSide, pos=(12, 12, 0, 60), stepID=toStep, func=self.SwitchStepIfDifferent, stepsUsed=self.stepsUsed, availableSteps=navSteps)
        if toStep == ccConst.EMPIRESTEP:
            self.mainNav.Hide()
        else:
            self.mainNav.Show()
        if toStep in ccConst.EMPIRE_SELECTION_STEPS:
            self.mainNav.SetParent(self.topNavigationContainer)
            self.mainNav.align = uiconst.TOLEFT
            self.topNavigationContainer.Show()
            self.bottomNavigationContainer.Show()
            sm.GetService('gameui').MoveResourceLoadingIndicator(newAlignment=uiconst.BOTTOMLEFT, newLeft=10, newTop=10)
        else:
            self.mainNav.SetParent(self.leftSide, 0)
            self.mainNav.align = uiconst.TOLEFT
            self.topNavigationContainer.Hide()
            self.bottomNavigationContainer.Hide()
            sm.GetService('gameui').MoveResourceLoadingIndicator(newAlignment=uiconst.BOTTOMLEFT, newLeft=20, newTop=RESOURCE_WHEEL_SEPARATION + ccConst.BUTTON_AREA_HEIGHT)

    def _ShowOrHideCharacterScene(self, toStep):
        if toStep == ccConst.BLOODLINESTEP:
            self.sceneManager.characterRenderJob.DisableStep('RENDER_SCENE')
        elif self.stepID == ccConst.BLOODLINESTEP or self.stepID is None:
            self.sceneManager.characterRenderJob.EnableStep('RENDER_SCENE')

    @telemetry.ZONE_METHOD
    def SwitchStepIfDifferent(self, toStep, *args):
        if self.stepID == toStep:
            return
        if self.stepID == ccConst.TECHNOLOGYSTEP and toStep == ccConst.BLOODLINESTEP:
            self.step.techView.Enlist()
            return
        self.SwitchStep(toStep, args)

    @telemetry.ZONE_METHOD
    def SwitchStep(self, toStep, *args):
        if GetStepOrder(toStep) > GetStepOrder(self.stepID):
            if not self.PassedStepCheck(toStep):
                return
        try:
            self.LockEverything()
            isStepOutOfEmpireSelection = self.stepID is not None and self.stepID not in ccConst.EMPIRE_SELECTION_STEPS
            isToStepOutOfEmpireSelection = toStep not in ccConst.EMPIRE_SELECTION_STEPS
            isBlackScreenTransition = isStepOutOfEmpireSelection or isToStepOutOfEmpireSelection
            if isBlackScreenTransition:
                self.FadeToBlack(why=localization.GetByLabel('UI/Generic/Loading'))
            with TempLock('CharacterCreationLayerUpdate'):
                self.UnfreezeAnimationIfNeeded()
                self.BlockOnUpdate()
                self.ConstructNavigationIfNeeded(toStep)
                self.empireNavigationButtonContainer.Flush()
                if self.stepID == ccConst.CUSTOMIZATIONSTEP:
                    sm.StartService('audio').SendUIEvent(unicode('ui_icc_sculpting_mouse_over_loop_stop'))
                    self.step.StoreHistorySliderPosition()
                elif self.stepID == ccConst.PORTRAITSTEP:
                    sm.StartService('audio').SendUIEvent(unicode('ui_icc_sculpting_mouse_over_loop_stop'))
                    self.StorePortraitCameraSettings()
                self.step = None
                raceTheme = COLOR_THEME_ID_BY_RACE.get(self.raceID, DEFAULT_COLORTHEMEID)
                sm.GetService('uiColor').SetNoCharTheme(raceTheme)
                if self.mainNav:
                    stepsUsed = self.stepsUsed.copy()
                    uthread.new(self.mainNav.PerformStepChange, toStep, stepsUsed)
                self._ShowOrHideCharacterScene(toStep)
                self.BlockOnUpdate()
                self._UpdateNavigationButtons(toStep)
                if isBlackScreenTransition:
                    self.mainCont.Flush()
                if toStep in ccConst.EMPIRE_SELECTION_STEPS:
                    self.empireStepContainer.Show()
                else:
                    self.empireStepContainer.Hide()
                self.UpdateVisualArtifacts(toStep)
                if toStep != ccConst.EMPIRESTEP:
                    self.empireStepContainer.ShowBackgroundBanner(self.raceID)
                if toStep == ccConst.EMPIRESTEP:
                    self.empireStepContainer.ShowViewCaps()
                    self.empireStepContainer.HideBannerCaps()
                elif toStep == ccConst.TECHNOLOGYSTEP:
                    self.empireStepContainer.HideViewCaps()
                    self.empireStepContainer.SetBannerCapsForMenu()
                elif toStep == ccConst.BLOODLINESTEP:
                    self.empireStepContainer.HideViewCaps()
                    self.empireStepContainer.SetBannerCapsForView()
                self.Cleanup()
                self.BlockOnUpdate()
                self.metrics.new_page(toStep)
                self.StartStep(toStep)
                self.stepID = toStep
                self.stepsUsed.add(toStep)
                self.UpdateBackdrop()
        finally:
            self.UnlockEverything()
            self.setupDone = 1
            self.FadeFromBlack()
            self.UnfreezeAnimationIfNeeded()
            sm.ScatterEvent('OnCharacterCreationStep', self.stepID, toStep)

    def BlockOnUpdate(self):
        info = self.GetInfo()
        characters = self.characterSvc.characters
        if info.charID in characters and self.characterSvc.GetSingleCharactersDoll(info.charID).busyUpdating:
            start_time = time.clock()
            while self.characterSvc.GetSingleCharactersDoll(info.charID).busyUpdating and time.clock() - start_time < 60:
                blue.synchro.Yield()

            if self.characterSvc.GetSingleCharactersDoll(info.charID).busyUpdating:
                raise UserError('uiwarning01')

    def _UpdateNavigationButtons(self, toStep):
        if toStep in ccConst.EMPIRE_SELECTION_STEPS:
            self.backBtn.Hide()
            self.approveBtn.Hide()
            self.finalizeBtn.Hide()
            self.saveBtn.Hide()
            return
        self.approveBtn.Show()
        self.backBtn.Show()
        isGoingToFinalStep = toStep == self.availableSteps[-1]
        if isGoingToFinalStep:
            self.approveBtn.state = uiconst.UI_HIDDEN
            isNewChar = not self.charID
            if isNewChar:
                self.finalizeBtn.state = uiconst.UI_NORMAL
                self.saveBtn.state = uiconst.UI_HIDDEN
            else:
                self.finalizeBtn.state = uiconst.UI_HIDDEN
                self.saveBtn.state = uiconst.UI_NORMAL
        else:
            self.approveBtn.state = uiconst.UI_NORMAL
            self.finalizeBtn.state = uiconst.UI_HIDDEN
            self.saveBtn.state = uiconst.UI_HIDDEN

    def _SetUpSceneAndCamera(self, scene):
        self.sceneManager.Show2DBackdropScene()
        self.SetupScene(scene)
        self.camera = CharCreationCamera(None)
        self.camera.fieldOfView = 0.5
        self.camera.distance = 7.0
        self.camera.SetPointOfInterest((0.0, 1.3, 0.0))
        self.camera.frontClip = 3.5
        self.camera.backclip = 100.0
        self.SetupCameraUpdateJob()

    def _HideBackButtonIfNoCharacters(self):
        if not sm.GetService('cc').GetCharactersToSelect():
            self.backBtn.Hide()

    def StartEmpireStep(self):
        self.step = EmpireStep(parent=self.empireStepContainer, stepContainer=self.empireStepContainer)
        self._SetUpSceneAndCamera(ccConst.SCENE_PATH_RACE_SELECTION)
        self.camera.ToggleMode(ccConst.CAMERA_MODE_DEFAULT, avatar=None)

    def _AddEmpireNavigation(self, stepID):
        if stepID not in (ccConst.TECHNOLOGYSTEP, ccConst.BLOODLINESTEP):
            if self.empireNavigationContainer is not None and not self.empireNavigationContainer.destroyed:
                self.empireNavigationContainer.Close()
            return
        if self.empireNavigationContainer is not None and not self.empireNavigationContainer.destroyed:
            return
        width = GetEmpireNavigationWidth()
        height = GetEmpireNavigationHeight()
        self.empireNavigationContainer = Container(name='empireNavigationContainer', align=uiconst.CENTER, parent=self.topNavigationContainer, width=width, height=self.topNavigationContainer.height, idx=1)
        rightAlignedContainer = Container(name='rightAlignedContainer', align=uiconst.TORIGHT, parent=self.empireNavigationContainer, width=width, height=self.empireNavigationContainer.height)
        empireNavigationWrapper = Container(name='empireNavigationWrapper', align=uiconst.CENTERBOTTOM, parent=rightAlignedContainer, width=width, height=height)
        EmpireNavigation(name='empireNavigationContainer', align=uiconst.TOLEFT, parent=empireNavigationWrapper, width=width, height=height, raceSetter=self.SelectRaceIfDifferent, activeRace=self.raceID)

    def StartTechnologyStep(self):
        if self.technologyViewsTracker is None:
            self.technologyViewsTracker = TechnologyViewsTracker()
        self._SetUpSceneAndCamera(ccConst.SCENE_PATH_RACE_SELECTION)
        self.camera.ToggleMode(ccConst.CAMERA_MODE_DEFAULT, avatar=None)
        isStepChange = self.stepID != ccConst.TECHNOLOGYSTEP
        self.step = TechnologyStep(parent=self.empireStepContainer, shouldGoBackToStart=isStepChange, technologyViewsTracker=self.technologyViewsTracker)
        self.step.SetOrder(0)

    def StartNewBloodlineStep(self):
        try:
            self.ShowLoading()
            self.LoadBloodlineStep()
        finally:
            self.HideLoading()

    def _ShouldUseVideosInBloodlines(self):
        return not self.IsSlowMachine()

    def LoadBloodlineStep(self):
        self.step = BloodlineStep(parent=self.empireStepContainer, buttonContainer=uicore.layer.charactercreation.controller.empireNavigationButtonContainer, useVideos=self._ShouldUseVideosInBloodlines())
        self.step.SetOrder(0)
        self.step.ShowBloodlineInfo()
        self.step.ShowBoundingBoxes()
        self.step.ShowGenders()
        self.step.ShowNote()

    def ReloadBloodlineStep(self, updateRace = False):
        try:
            self.LockEverything()
            self.HideContent(updateRace)
            self.ShowLoading()
            if self.step and not self.step.destroyed:
                self.step.Close()
            self.LoadBloodlineStep()
            if updateRace:
                raceTheme = COLOR_THEME_ID_BY_RACE.get(self.raceID, DEFAULT_COLORTHEMEID)
                sm.GetService('uiColor').SetNoCharTheme(raceTheme)
                self.UpdateBackdrop()
            self.ShowContent(updateRace)
        finally:
            self.HideLoading()
            self.UnlockEverything()

    def ShowContent(self, updateRace):
        if self.empireStepContainer and not self.empireStepContainer.destroyed:
            self.empireStepContainer.Show()
            if updateRace:
                self.empireStepContainer.ExpandRace(self.raceID)
        if not updateRace and self.backgroundSprite and not self.backgroundSprite.destroyed:
            self.backgroundSprite.Show()

    def HideContent(self, updateRace):
        if self.empireStepContainer and not self.empireStepContainer.destroyed:
            self.empireStepContainer.Hide()
        if not updateRace and self.backgroundSprite and not self.backgroundSprite.destroyed:
            self.backgroundSprite.Hide()

    def StartStep(self, toStep):
        self.stepLogger.SetStep(toStep)
        start_method = {ccConst.CUSTOMIZATIONSTEP: self.StartCustomizationStep,
         ccConst.PORTRAITSTEP: self.StartPortraitStep,
         ccConst.NAMINGSTEP: self.StartNamingStep,
         ccConst.EMPIRESTEP: self.StartEmpireStep,
         ccConst.TECHNOLOGYSTEP: self.StartTechnologyStep,
         ccConst.BLOODLINESTEP: self.StartNewBloodlineStep}.get(toStep, None)
        if start_method is None:
            raise NotImplementedError
        start_method()

    def IsNamingStep(self, step):
        return step == ccConst.NAMINGSTEP

    @telemetry.ZONE_METHOD
    def StorePortraitCameraSettings(self):
        if self.camera is not None:
            self.storedPortraitCameraSettings = {'poi': self.camera.poi,
             'pitch': self.camera.pitch,
             'yaw': self.camera.yaw,
             'distance': self.camera.distance,
             'xFactor': self.camera.xFactor,
             'yFactor': self.camera.yFactor,
             'fieldOfView': self.camera.fieldOfView}

    @telemetry.ZONE_METHOD
    def FadeToBlack(self, why = ''):
        self.ShowLoading(why=why, forceOn=True)
        animations.FadeIn(self.blackOut, duration=0.5, sleep=True)

    @telemetry.ZONE_METHOD
    def FadeFromBlack(self):
        animations.FadeOut(self.blackOut, duration=0.5)
        self.HideLoading(forceOff=1)

    @telemetry.ZONE_METHOD
    def PassedStepCheck(self, toStep, *args):
        if toStep not in self.availableSteps:
            raise UserError('CCStepUnavailable')
        if toStep == ccConst.BLOODLINESTEP and self.raceID is None:
            raise UserError('CCMustSelectRace')
        if toStep == ccConst.CUSTOMIZATIONSTEP and (self.raceID is None or self.bloodlineID is None or self.genderID is None):
            raise UserError('CCMustSelectRaceAndBloodline')
        isNamingStep = self.IsNamingStep(toStep)
        if (toStep == ccConst.PORTRAITSTEP or isNamingStep) and not prefs.GetValue('ignoreCCValidation', False):
            info = self.GetInfo()
            self.ToggleClothes(forcedValue=0)
            self.characterSvc.ValidateDollCustomizationComplete(info.charID)
        currentStepID = None
        if self.step:
            currentStepID = self.step.stepID
        if self.step:
            self.step.ValidateStepComplete()
        return True

    @telemetry.ZONE_METHOD
    def Approve(self, *args):
        if not self.approve_in_progress:
            try:
                self.approve_in_progress = True
                self.stepLogger.IncrementNextTryCount()
                idx = self.availableSteps.index(self.stepID)
                if len(self.availableSteps) > idx + 1:
                    nextStep = self.availableSteps[idx + 1]
                    self.SwitchStep(nextStep)
                    uicore.registry.SetFocus(self)
            finally:
                self.approve_in_progress = False

    def CheckAndGetName(self):
        isAvailable = self.step.CheckAvailability()
        if isAvailable.charName is None:
            eve.Message('CustomInfo', {'info': isAvailable.reason})
        return isAvailable.charName

    @telemetry.ZONE_METHOD
    def Save(self, *args):
        if not self.save_in_progress:
            self.save_in_progress = True
            self.BlockOnUpdate()
            if self.finalStepLogger:
                self.finalStepLogger.Finalize()
            self.stepLogger.IncrementNextTryCount()
            try:
                selectedPortraitInfo = self.portraitInfo[self.activePortraitIndex]
                if selectedPortraitInfo and selectedPortraitInfo.backgroundID < const.NCC_MIN_NORMAL_BACKGROUND_ID:
                    eve.Message('CustomInfo', {'info': localization.GetByLabel('UI/CharacterCreation/CannotSaveWithThisBackground')})
                    return
                self.LockEverything()
                if self.step:
                    self.step.ValidateStepComplete()
                if self.stepID != self.availableSteps[-1]:
                    raise UserError('CCCannotSave')
                if self.charID and self.modeObject.AskForPortraitConfirmation():
                    self.UpdateExistingCharacter()
                    return
                if self.bloodlineID is None or self.genderID is None:
                    raise UserError('CCCannotSave2')
                else:
                    characterName = self.CheckAndGetName()
                    if characterName is None:
                        return
                    self.SaveAndEnterCurrentCharacter(characterName)
            finally:
                if self and not self.destroyed:
                    self.UnlockEverything()
                    self.save_in_progress = False

    def SaveAndEnterCurrentCharacter(self, characterName):
        self.audioService.SendUIEvent('ui_es_button_mouse_down_finalize_play')
        charID = self.SaveCurrentCharacter(characterName, self.bloodlineID, self.genderID, self.activePortraitIndex)
        self.metrics.complete_cc(charid=charID)
        if charID:
            self.characterSvc.CachePortraitInfo(charID, self.portraitInfo[self.activePortraitIndex])
            self.tryLoginElseCharacterSelection(charID)

    def tryLoginElseCharacterSelection(self, charID):
        try:
            if gatekeeper.user.IsInCohort(gatekeeper.cohortToCharacterSelectionTest):
                sm.GetService('cc').GetCharactersToSelect(force=True)
                uthread.pool('GameUI::ActivateView::charsel', sm.GetService('viewState').ActivateView, 'charsel')
            else:
                skipTutorial = self.CheckSkipTutorial() if is_air_npe_enabled() else True
                sm.GetService('cc').FinishCharacterCreation(charID, skipTutorial)
        except:
            cc = sm.GetService('cc')
            cc.StopIntro()
            cc.GetCharactersToSelect(force=True)
            sm.GetService('loading').ProgressWnd(localization.GetByLabel('UI/CharacterCreation/CharacterSelection'), localization.GetByLabel('UI/CharacterCreation/FailedToEnterGame'), 2, 2)
            uthread.pool('GameUI::ActivateView::charsel', sm.GetService('viewState').ActivateView, 'charsel')
            raise

    def CheckSkipTutorial(self):
        if sm.RemoteSvc('charUnboundMgr').GetNumCharacters() > 1:
            if eve.Message('AskStartWithTutorial', {}, uiconst.YESNO, default=uiconst.ID_NO) == uiconst.ID_NO:
                return True
        return False

    def OnEsc(self):
        self.Back()

    def CancelCharacterCreation(self):
        if self.modeObject.ExitToStation():
            msg = 'AskCancelCharCustomization'
        else:
            msg = 'AskCancelCharCreation'
        self.audioService.SendUIEvent('ui_es_pop_up_play')
        popUp = eve.Message(msg, {}, uiconst.YESNO)
        self.audioService.SendUIEvent('ui_es_pop_up_stop')
        if popUp != uiconst.ID_YES:
            return
        self.needNavigationTutorial = True
        self.needSculptingTutorial = True
        self.audioService.SendUIEvent('ui_es_stop')
        self.metrics.cancel_cc()
        if self.modeObject.ExitToStation():
            self.ExitToStation(updateDoll=False)
        else:
            sm.StartService('cc').GoBack()
        self.stepID = None

    @telemetry.ZONE_METHOD
    def Back(self, *args):
        idx = self.availableSteps.index(self.stepID)
        if idx == 0:
            self.CancelCharacterCreation()
        else:
            nextStep = self.availableSteps[idx - 1]
            self.SwitchStep(nextStep)
            uicore.registry.SetFocus(self)

    @telemetry.ZONE_METHOD
    def LockEverything(self, *args):
        if not getattr(self, 'setupDone', 0):
            return
        containers = [self,
         self.topNavigationContainer,
         self.bottomNavigationContainer,
         self.empireStepContainer]
        for container in containers:
            container.pickState = uiconst.TR2_SPS_OFF

        self.LockNavigation()

    @telemetry.ZONE_METHOD
    def LockNavigation(self, *args):
        if not getattr(self, 'setupDone', 0):
            return
        self.buttonNavRight.state = uiconst.UI_DISABLED
        self.buttonNavLeft.state = uiconst.UI_DISABLED
        if self.mainNav:
            self.mainNav.state = uiconst.UI_DISABLED

    @telemetry.ZONE_METHOD
    def UnlockEverything(self, *args):
        containers = [self,
         self.topNavigationContainer,
         self.bottomNavigationContainer,
         self.empireStepContainer]
        for container in containers:
            container.pickState = uiconst.TR2_SPS_CHILDREN

        self.UnlockNavigation()

    @telemetry.ZONE_METHOD
    def UnlockNavigation(self, *args):
        if not self.parent.isopen:
            return
        self.buttonNavRight.state = uiconst.UI_PICKCHILDREN
        self.buttonNavLeft.state = uiconst.UI_PICKCHILDREN
        if self.mainNav:
            self.mainNav.state = uiconst.UI_PICKCHILDREN

    @telemetry.ZONE_METHOD
    def SetActivePortrait(self, portraitNo, *args):
        self.activePortraitIndex = portraitNo
        self.activePortrait = self.facePortraits[portraitNo]

    @telemetry.ZONE_METHOD
    def GetActivePortrait(self):
        return self.activePortrait

    @telemetry.ZONE_METHOD
    def SetFacePortrait(self, photo, portraitNo, *args):
        self.facePortraits[portraitNo] = photo
        self.SetActivePortrait(portraitNo)

    @telemetry.ZONE_METHOD
    def ClearFacePortrait(self, *args):
        self.facePortraits = [None] * ccConst.NUM_PORTRAITS
        self.ClearPortraitInfo()
        self.activePortraitIndex = 0
        self.activePortrait = None

    @telemetry.ZONE_METHOD
    def SelectRaceIfDifferent(self, raceID, check = 1):
        if self.raceID != raceID:
            self._ChangeRace(raceID, check)
        self._UpdateResourcePriority(raceID)

    @telemetry.ZONE_METHOD
    def SelectRace(self, raceID, check = 1):
        self._ChangeRace(raceID, check)
        self._UpdateResourcePriority(raceID)

    def _ChangeRace(self, raceID, check = 1):
        oldRaceID = self.raceID
        bloodLineStepIsUsed = ccConst.BLOODLINESTEP in self.stepsUsed
        if check and oldRaceID is not None and bloodLineStepIsUsed:
            if self.stepID == ccConst.CUSTOMIZATIONSTEP:
                dnaLog = self.GetDollDNAHistory()
                if dnaLog and len(dnaLog) > 1:
                    if eve.Message('CharCreationLoseChangesRace', {}, uiconst.YESNO) != uiconst.ID_YES:
                        return
        self.ClearSteps(what='race')
        self.ResetClothesStorage()
        self.raceID = raceID
        if self.stepID == ccConst.BLOODLINESTEP:
            self.SelectBloodlineAndGender(None, None, check)
        else:
            self.SelectBloodline(None, check=check)
        if hasattr(self.step, 'OnRaceSelected'):
            self.step.OnRaceSelected(raceID)
        self.UpdateBackdrop()

    def _UpdateResourcePriority(self, raceID):
        raceAsString = RACE_TO_RESOURCE_NAME.get(raceID, None)
        if raceAsString:
            everesourceprefetch.ScheduleFront('interior_' + raceAsString)
            everesourceprefetch.ScheduleFront('bloodline_select_' + raceAsString)

    @telemetry.ZONE_METHOD
    def SelectBloodline(self, bloodlineID, check = 1):
        if self.bloodlineID != bloodlineID:
            oldBloodlineID = self.bloodlineID
            if check and oldBloodlineID is not None and ccConst.CUSTOMIZATIONSTEP in self.stepsUsed:
                if self.stepID == ccConst.CUSTOMIZATIONSTEP:
                    dnaLog = self.GetDollDNAHistory()
                    if dnaLog and len(dnaLog) > 1:
                        if eve.Message('CharCreationLoseChangeBloodline', {}, uiconst.YESNO) != uiconst.ID_YES:
                            return
            self.ClearSteps(what='bloodline')
            self.ResetClothesStorage()
            self.bloodlineID = bloodlineID
            if hasattr(self.step, 'OnBloodlineSelected'):
                self.step.OnBloodlineSelected(bloodlineID, oldBloodlineID)
            if self.bloodlineSelector is not None:
                self.bloodlineSelector.SelectBloodline(bloodlineID)

    @telemetry.ZONE_METHOD
    def SelectGender(self, genderID, check = 1):
        if not self.CanChangeGender():
            return
        if check and self.genderID not in [None, genderID] and ccConst.CUSTOMIZATIONSTEP in self.stepsUsed:
            if self.stepID == ccConst.CUSTOMIZATIONSTEP:
                dnaLog = self.GetDollDNAHistory()
                if dnaLog and len(dnaLog) > 1:
                    if eve.Message('CharCreationLoseChangeGender', {}, uiconst.YESNO) != uiconst.ID_YES:
                        return
        self.genderID = genderID
        self.ClearSteps(what='gender')
        self.ResetClothesStorage()
        if hasattr(self.step, 'OnGenderSelected'):
            self.step.OnGenderSelected(genderID)
        if getattr(self.step.sr, 'historySlider'):
            self.step.sr.historySlider.LoadHistory(0)

    @telemetry.ZONE_METHOD
    def SelectBloodlineAndGender(self, bloodlineID, genderID, check = 1):
        isBloodlineChanged = self.bloodlineID != bloodlineID
        isGenderChanged = self.genderID != genderID
        self.WarnOfUnsavedChanges(check, isBloodlineChanged, isGenderChanged)
        if isBloodlineChanged or isGenderChanged:
            self.ClearSteps(what='bloodline')
        self.bloodlineID = bloodlineID
        self.genderID = genderID
        self.ResetClothesStorage()
        if getattr(self.step, 'sr') and getattr(self.step.sr, 'historySlider'):
            self.step.sr.historySlider.LoadHistory(0)

    def WarnOfUnsavedChanges(self, check, isBloodlineChanged, isGenderChanged):
        isBloodlineUnsaved = isBloodlineChanged and self.bloodlineID is not None
        isGenderUnsaved = isGenderChanged and self.genderID is not None
        areThereUnsavedChanges = isBloodlineUnsaved or isGenderUnsaved
        isCustomized = self.stepID == ccConst.CUSTOMIZATIONSTEP and ccConst.CUSTOMIZATIONSTEP in self.stepsUsed
        shouldWarn = check and areThereUnsavedChanges and isCustomized
        if shouldWarn:
            dnaLog = self.GetDollDNAHistory()
            if dnaLog and len(dnaLog) > 1:
                message = 'CharCreationLoseChangeBloodline' if isBloodlineUnsaved else 'CharCreationLoseChangeGender'
                if eve.Message(message, {}, uiconst.YESNO) != uiconst.ID_YES:
                    return

    @telemetry.ZONE_METHOD
    def SelectSchool(self, schoolID):
        if self.finalStepLogger:
            self.finalStepLogger.SetSchool(schoolID)
        self.schoolID = schoolID
        if hasattr(self.step, 'OnSchoolSelected'):
            self.step.OnSchoolSelected(schoolID)

    @telemetry.ZONE_METHOD
    def OnDollUpdated(self, charID, redundantUpdate, fromWhere, *args):
        if fromWhere in ('AddCharacter', 'OnSetDevice'):
            return
        self.ClearSteps(what='dollUpdated')

    @telemetry.ZONE_METHOD
    def IsSlowMachine(self):
        if gfxsettings.Get(gfxsettings.GFX_CHAR_FAST_CHARACTER_CREATION):
            return True
        if gfxsettings.Get(gfxsettings.GFX_SHADER_QUALITY) < 2:
            return True
        return False

    @telemetry.ZONE_METHOD
    def OnGraphicSettingsChanged(self, changes):
        shouldGoBack = False
        if getattr(uicore.layer.charactercreation, 'isopen', 0):
            if gfxsettings.GFX_CHAR_FAST_CHARACTER_CREATION in changes:
                header = localization.GetByLabel('UI/CharacterCreation/LoseChangesHeader')
                text = localization.GetByLabel('UI/CharacterCreation/LoseChanges')
                if eve.Message('CustomQuestion', {'header': header,
                 'question': text}, uiconst.YESNO) == uiconst.ID_YES:
                    self.avatarScene = None
                    shouldGoBack = True
                else:
                    gfxsettings.Set(gfxsettings.GFX_CHAR_FAST_CHARACTER_CREATION, 0, pending=False)
        if shouldGoBack:
            if self.charID:
                trinity.WaitForResourceLoads()
                self.ExitToStation()
            else:
                sm.GetService('cc').GoBack()
        else:
            self.bloodlineSelector = None
            if self.stepID in ccConst.EMPIRE_SELECTION_STEPS:
                self.ReloadStep()
        if gfxsettings.UI_NCC_GREEN_SCREEN in changes:
            self.UpdateBackdrop()
            if self.floor:
                self.floor.display = not gfxsettings.Get(gfxsettings.UI_NCC_GREEN_SCREEN)

    def ReloadStep(self):
        self.ShowLoading()
        try:
            self.SwitchStep(self.stepID)
        finally:
            self.HideLoading()

    @telemetry.ZONE_METHOD
    def TearDown(self):
        self.Cleanup()
        self.characterSvc.TearDown()
        self.floor = None
        self.doll = None
        self.scene = None
        self.avatarScene = None
        self.ClearCamera()
        self.cameraUpdateJob = None
        if self.bloodlineSelector is not None:
            self.bloodlineSelector.TearDown()
        self.bloodlineSelector = None
        self.animateToStoredPortraitThread = None
        self.animatingToPortraitID = None
        self.freezingAnimation = False
        self.colorCodedBackDrop = None

    @telemetry.ZONE_METHOD
    def SetAvatarScene(self, skipAddCharacter = False):
        info = self.GetInfo()
        if self.avatarScene is None:
            self.SetupScene(ccConst.SCENE_PATH_CUSTOMIZATION)
            self.avatarScene = self.scene
            if not skipAddCharacter:
                self.AddCharacter(info.charID, info.bloodlineID, info.raceID, info.genderID, dna=info.dna)
            self.floor = trinity.Load(ccConst.CUSTOMIZATION_FLOOR)
            self.scene.dynamics.append(self.floor)
        else:
            self.scene = self.avatarScene
        self.sceneManager.SetActiveScene(self.scene, sceneKey='characterCreation')
        self.BlockOnUpdate()

    @telemetry.ZONE_METHOD
    def StartCustomizationStep(self, *args):
        info = self.GetInfo()
        self.sceneManager.Show2DBackdropScene()
        self.SetAvatarScene()
        avatar = self.characterSvc.GetSingleCharactersAvatar(info.charID)
        if avatar is not None:
            network = animparams.GetParamsPerAvatar(avatar, info.charID)
            network.SetControlParameter('ControlParameters|NetworkMode', NETWORKMODE_BASIC)
            self.camera = CharCreationCamera(avatar, ccConst.CAMERA_MODE_FACE)
            self.camera.frontClip = 0.1
            self.camera.backclip = 100.0
            self.SetupCameraUpdateJob()
            self.camera.SetMoveCallback(self.CameraMoveCB)
        self.SetDefaultLighting()
        self.step = CharacterCustomization(parent=self.mainCont)
        if self.CanChangeBaseAppearance():
            self.StartEditMode(showPreview=True, callback=self.step.ChangeSculptingCursor)
        self.camera.ToggleMode(ccConst.CAMERA_MODE_FACE, avatar=avatar, transformTime=500.0)
        self.scene.SetupShadowMaps()

    def CameraMoveCB(self, viewMatrix):
        info = self.GetInfo()
        if info.charID not in self.characterSvc.characters:
            return
        if not len(self.characterSvc.characters):
            return
        avatar = self.characterSvc.GetSingleCharactersAvatar(info.charID)
        matrix = geo2.MatrixInverse(viewMatrix.transform)
        view = matrix[3][:3]
        if info.genderID:
            height = 1.7
        else:
            height = 1.6
        head = (0, height, 0)
        rot = avatar.rotation
        vec = (view[0] - head[0], view[1] - head[1], view[2] - head[2])
        vecLength = geo2.Vec3Distance((0, 0, 0), vec)
        vec = geo2.QuaternionTransformVector(geo2.QuaternionInverse(rot), vec)
        norm = 1.0 / math.sqrt(vec[0] * vec[0] + vec[1] * vec[1] + vec[2] * vec[2])
        vec = (vec[0] * norm, vec[1] * norm, vec[2] * norm)
        leftright = math.atan2(vec[2], vec[0])
        updown = math.asin(vec[1])
        leftright = 1 - abs(leftright) / 3.1415927 * 2
        updown = 2 * updown / 3.1415927
        dist = (vecLength - 1.0) / 7.0
        network = animparams.GetParamsPerAvatar(avatar, info.charID)
        network.SetControlParameter('ControlParameters|HeadLookLeftRight', leftright)
        network.SetControlParameter('ControlParameters|HeadLookUpDown', updown)
        network.SetControlParameter('ControlParameters|CameraDistance', dist)

    @telemetry.ZONE_METHOD
    def FetchOldPortraitData(self, charID):
        PREFIX = 'ControlParameters|'
        cache = self.characterSvc.GetCachedPortraitInfo(charID)
        if cache is not None:
            self.lightingID = cache.lightID
            self.lightColorID = cache.lightColorID
            self.lightIntensity = cache.lightIntensity
            path = self.GetBackgroundPathFromID(cache.backgroundID)
            if path in self.GetAvailableBackgroundsPaths():
                self.backdropPath = path
            self.poseID = cache.poseData['PortraitPoseNumber']
            self.cameraPos = cache.cameraPosition
            self.cameraPoi = cache.cameraPoi
            self.cameraFov = cache.cameraFieldOfView
            params = []
            for key in cache.poseData:
                params.append((PREFIX + key, cache.poseData[key]))

            if len(params):
                self.characterSvc.SetControlParametersFromList(params, charID)
        else:
            portraitData = sm.GetService('cc').GetPortraitData(charID)
            if portraitData is not None:
                self.lightingID = portraitData.lightID
                self.lightColorID = portraitData.lightColorID
                self.lightIntensity = portraitData.lightIntensity
                path = self.GetBackgroundPathFromID(portraitData.backgroundID)
                if path in self.GetAvailableBackgroundsPaths():
                    self.backdropPath = path
                self.poseID = portraitData.portraitPoseNumber
                self.cameraPos = (portraitData.cameraX, portraitData.cameraY, portraitData.cameraZ)
                self.cameraPoi = (portraitData.cameraPoiX, portraitData.cameraPoiY, portraitData.cameraPoiZ)
                self.cameraFov = portraitData.cameraFieldOfView
                params = self.GetControlParametersFromPoseData(portraitData, fromDB=True).values()
                self.characterSvc.SetControlParametersFromList(params, charID)
        self.alreadyLoadedOldPortraitData = True

    @telemetry.ZONE_METHOD
    def StartPortraitStep(self):
        info = self.GetInfo()
        if not getattr(self, 'alreadyLoadedOldPortraitData', False):
            if self.modeObject.GetOldPortraitData():
                self.FetchOldPortraitData(info.charID)
        self.step = CharacterPortrait(parent=self.mainCont)
        self.SetAvatarScene()
        avatar = self.characterSvc.GetSingleCharactersAvatar(info.charID)
        if avatar is not None and avatar.animationUpdater is not None:
            network = animparams.GetParamsPerAvatar(avatar, info.charID)
            network.SetControlParameter('ControlParameters|NetworkMode', NETWORKMODE_PORTRAIT)
        if self.camera is None:
            self.camera = CharCreationCamera(avatar, ccConst.CAMERA_MODE_PORTRAIT)
            self.SetupCameraUpdateJob()
        else:
            self.camera.ToggleMode(ccConst.CAMERA_MODE_PORTRAIT, avatar=avatar, transformTime=500.0)
        if hasattr(self, 'cameraPos'):
            self.camera.PlacePortraitCamera(self.cameraPos, self.cameraPoi)
            xFactor, yFactor = self.camera.GetCorrectCameraXandYFactors(self.cameraPos, self.cameraPoi)
            self.camera.xFactor = self.camera.xTarget = xFactor
            self.camera.yFactor = self.camera.yTarget = yFactor
        if hasattr(self, 'storedPortraitCameraSettings'):
            self.camera.SetPointOfInterest(self.storedPortraitCameraSettings['poi'])
            self.camera.pitch = self.storedPortraitCameraSettings['pitch']
            self.camera.yaw = self.storedPortraitCameraSettings['yaw']
            self.camera.distance = self.storedPortraitCameraSettings['distance']
            self.camera.xFactor = self.storedPortraitCameraSettings['xFactor']
            self.camera.yFactor = self.storedPortraitCameraSettings['yFactor']
            self.camera.fieldOfView = self.storedPortraitCameraSettings['fieldOfView']
        self.UpdateLights()
        self.characterSvc.StartPosing(charID=info.charID, callback=self.step.ChangeSculptingCursor)

    @telemetry.ZONE_METHOD
    def StartNamingStep(self, *args):
        self.SetAvatarScene()
        self.SetDefaultLighting()
        self.CaptureAndSetActivePortrait()
        self.step = CharacterNaming(parent=self.mainCont)
        self.SetUpNamingStepCamera()
        self.SetAvatarAnimationNetworkMode(NETWORKMODE_BASIC)

    def CaptureAndSetActivePortrait(self):
        self.SetAvatarAnimationNetworkMode(NETWORKMODE_PORTRAIT)
        while not self.characterSvc.sculpting:
            blue.synchro.Yield()

        info = self.GetInfo()
        avatar = self.characterSvc.GetSingleCharactersAvatar(info.charID)
        self.camera = CharCreationCamera(avatar, ccConst.CAMERA_MODE_PORTRAIT)
        self.camera.SetMoveCallback(self.CameraMoveCB)
        self.camera.Update()
        self.backdropPath = random.choice(ccConst.defaultBackgroundOptions)
        self.activePortrait = self.CapturePortrait(0)

    def SetUpNamingStepCamera(self):
        info = self.GetInfo()
        avatar = self.characterSvc.GetSingleCharactersAvatar(info.charID)
        self.camera = CharCreationCamera(avatar=avatar)
        self.camera.fieldOfView = 0.3
        self.camera.distance = 8.0
        self.camera.frontClip = 3.5
        self.camera.backclip = 100.0
        self.SetupCameraUpdateJob()
        self.camera.SetPointOfInterest((0.0, self.camera.avatarEyeHeight / 2.0, 0.0))

    def SetAvatarAnimationNetworkMode(self, networkMode):
        info = self.GetInfo()
        avatar = self.characterSvc.GetSingleCharactersAvatar(info.charID)
        if avatar is not None:
            if info.charID in self.characterSvc.characters:
                network = animparams.GetParamsPerAvatar(avatar, info.charID)
                network.SetControlParameter('ControlParameters|NetworkMode', networkMode)
                while network.rebuilding:
                    blue.synchro.Yield()

    @telemetry.ZONE_METHOD
    def ClearSteps(self, what = None, force = 0, *args):
        stepAlreadyCleared = getattr(self.step, 'stepAlreadyCleared', 0)
        if not force and stepAlreadyCleared or not getattr(self.mainNav, 'ResetToStep', None):
            return
        currentStepID = self.stepID
        currentStepOrder = GetStepOrder(currentStepID)
        if currentStepOrder <= GetStepOrder(ccConst.CUSTOMIZATIONSTEP):
            self.ClearFacePortrait()
            self.ClearPortraitInfo()
            self.schoolID = None
            if what in ('bloodline', 'race'):
                self.schoolID = None
        if currentStepOrder <= GetStepOrder(ccConst.BLOODLINESTEP):
            self.avatarScene = None
            self.characterSvc.TearDown()
            self.schoolID = None
        if currentStepOrder <= GetStepOrder(ccConst.EMPIRESTEP):
            self.TearDown()
        firstStep = self.availableSteps[0]
        self.stepsUsed = GetStepsUpToAndIncluding(currentStepID) or {firstStep}
        self.mainNav.ResetToStep(currentStepID, stepsUsed=self.stepsUsed)
        if self.step:
            self.step.stepAlreadyCleared = 1

    @telemetry.ZONE_METHOD
    def Cleanup(self):
        self.characterSvc.StopEditing()
        info = self.GetInfo()
        charID = info.charID
        if charID in self.characterSvc.characters:
            self.characterSvc.StopPosing(charID)
        self.scene = None
        self.ClearCamera()
        self.sceneManager.UnregisterScene('characterCreation')

    @telemetry.ZONE_METHOD
    def SetupScene(self, path):
        scene = trinity.Load(path)
        blue.resMan.Wait()
        if self.IsSlowMachine():
            if hasattr(scene, 'shadowCubeMap'):
                scene.shadowCubeMap.enabled = False
            if hasattr(scene, 'ssao') and hasattr(scene.ssao, 'enable'):
                scene.ssao.enable = False
            if hasattr(scene, 'ambientColor'):
                scene.ambientColor = (0.25, 0.25, 0.25)
        elif scene:
            if hasattr(scene, 'shadowCubeMap'):
                scene.shadowCubeMap.enabled = False
        self.scene = scene
        self.sceneManager.RegisterScene(scene, 'characterCreation')
        self.sceneManager.SetRegisteredScenes('characterCreation')

    @telemetry.ZONE_METHOD
    def ReduceLights(self):
        scene = self.scene
        if hasattr(scene, 'lights'):
            lightsToRemove = []
            for each in scene.lights:
                if each.name != 'FrontMain':
                    lightsToRemove.append(each)

            for each in lightsToRemove:
                scene.lights.remove(each)

    def ApplyGraphicsSettingsToDoll(self, doll):
        doll.overrideLod = LOD_SKIN
        textureQuality = gfxsettings.Get(gfxsettings.GFX_CHAR_TEXTURE_QUALITY)
        doll.textureResolution = ccConst.TEXTURE_RESOLUTIONS[textureQuality]
        if self.IsSlowMachine():
            doll.useFastShader = True
        else:
            doll.useFastShader = False

    @telemetry.ZONE_METHOD
    def AddCharacter(self, charID, bloodlineID, raceID, genderID, scene = None, dna = None, validateColors = True, noRandomize = False):
        self.ResetDna()
        self.characterSvc.AddCharacterToScene(charID, scene or self.scene, ccUtil.GenderIDToPaperDollGender(genderID), dna=dna, bloodlineID=bloodlineID, raceID=raceID, updateDoll=False, noRandomize=noRandomize)
        self.doll = self.characterSvc.GetSingleCharactersDoll(charID)
        while self.doll.IsBusyUpdating():
            blue.synchro.Yield()

        self.ApplyGraphicsSettingsToDoll(self.doll)
        self.bloodlineID = bloodlineID
        self.characterSvc.SetDollBloodline(charID, bloodlineID)
        if validateColors:
            for categoryName in ccConst.COLORMAPPING.keys():
                self.UpdateColorSelectionFromDoll(categoryName)
                self.ValidateColors(categoryName)

        self.StartDnaLogging()
        self.characterSvc.UpdateDoll(charID, fromWhere='AddCharacter')

    def GetAvailableBackgroundsPaths(self):
        bgOptions = []
        if gfxsettings.Get(gfxsettings.UI_NCC_GREEN_SCREEN):
            bgOptions += ccConst.greenscreenBackgroundOptions
        authoredBackgrounds = self.characterSvc.GetAvailableBackgrounds()
        for eachResource in authoredBackgrounds:
            path = eachResource.resPath
            bgOptions.append(path)

        return bgOptions

    @telemetry.ZONE_METHOD
    def GetAvailableStyles(self, modifier):
        info = self.GetInfo()
        gender = info.genderID
        bloodline = info.bloodlineID
        currentModifier = self.characterSvc.GetModifierByCategory(info.charID, modifier)
        itemTypes = self.characterSvc.GetAvailableTypesByCategory(modifier, gender, info.raceID)
        activeIndex = None
        if currentModifier:
            currentType = currentModifier.GetTypeData()
            for i, each in enumerate(itemTypes):
                if each[1][0] == currentType[0] and each[1][1] == currentType[1] and each[1][2] == currentType[2]:
                    activeIndex = i

        return (itemTypes, activeIndex)

    def GetModifierIntensity(self, modifierPath):
        info = self.GetInfo()
        modifier = self.characterSvc.GetModifiersByCategory(info.charID, modifierPath)
        if modifier:
            return modifier[0].weight
        return 0.0

    @telemetry.ZONE_METHOD
    def GetAvailableColors(self, modifier):
        info = self.GetInfo()
        colors, activeColorIndex = self.characterSvc.GetCharacterColorVariations(info.charID, modifier)
        colors = tuple(colors)
        retColors = []
        for name, color in colors:
            if color and type(color[0]) == types.TupleType:
                r = g = b = 0
                for _r, _g, _b, _a in color:
                    r += _r
                    g += _g
                    b += _b

                r = r / float(len(color))
                g = g / float(len(color))
                b = b / float(len(color))
                retColors.append((name, (r,
                  g,
                  b,
                  1.0), color))
            else:
                retColors.append((name, color, color))

        return (retColors, activeColorIndex)

    @telemetry.ZONE_METHOD
    def SetColorValue(self, modifier, primaryColor, secondaryColor = None, doUpdate = True, ignoreValidate = False):
        self._setColorsByCategory[modifier] = (primaryColor, secondaryColor)
        info = self.GetInfo()
        self.characterSvc.SetColorValueByCategory(info.charID, modifier, primaryColor, secondaryColor, doUpdate=False)
        if ccUtil.HasUserDefinedSpecularity(modifier):
            specValue = self._setSpecularityByCategory.setdefault(modifier, 0.5)
            self.SetColorSpecularity(modifier, specValue, doUpdate=False)
        if ccUtil.HasUserDefinedWeight(modifier):
            defaultIntensity = ccConst.defaultIntensity.get(modifier, 0.5)
            intensityValue = self._setIntensityByCategory.setdefault(modifier, defaultIntensity)
            self.SetIntensity(modifier, intensityValue, doUpdate=False)
        if not ignoreValidate:
            self.ValidateColors(modifier)
        if doUpdate:
            self.characterSvc.UpdateDoll(info.charID, fromWhere='SetColorValue')

    def GetSpecularityByCategory(self, category):
        return self._setSpecularityByCategory.get(category, 0.5)

    def GetIntensityByCategory(self, category):
        return self._setIntensityByCategory.get(category, 0.5)

    @telemetry.ZONE_METHOD
    def SetRandomColorSpecularity(self, modifier, doUpdate = True):
        self.SetColorSpecularity(modifier, random.random(), doUpdate=doUpdate)

    @telemetry.ZONE_METHOD
    def SetColorSpecularity(self, modifier, specularity, doUpdate = True):
        self._setSpecularityByCategory[modifier] = specularity
        info = self.GetInfo()
        self.characterSvc.SetColorSpecularityByCategory(info.charID, modifier, specularity, doUpdate=doUpdate)

    @telemetry.ZONE_METHOD
    def SetRandomHairDarkness(self, doUpdate = True):
        self.SetHairDarkness(random.random(), doUpdate=doUpdate)

    @telemetry.ZONE_METHOD
    def SetHairDarkness(self, darkness, doUpdate = True):
        info = self.GetInfo()
        self.characterSvc.SetHairDarkness(info.charID, darkness)
        if doUpdate:
            sm.GetService('character').UpdateDoll(info.charID, fromWhere='SetHairDarkness')

    @telemetry.ZONE_METHOD
    def SetRandomIntensity(self, modifier, doUpdate = True):
        self.SetIntensity(modifier, random.random(), doUpdate=doUpdate)

    @telemetry.ZONE_METHOD
    def SetIntensity(self, modifier, value, doUpdate = True):
        info = self.GetInfo()
        if modifier == ccConst.muscle:
            self.characterSvc.SetCharacterMuscularity(info.charID, value, doUpdate=doUpdate)
        elif modifier == ccConst.weight:
            self.characterSvc.SetCharacterWeight(info.charID, value, doUpdate=doUpdate)
        else:
            self._setIntensityByCategory[modifier] = value
            self.characterSvc.SetWeightByCategory(info.charID, modifier, value, doUpdate=doUpdate)

    @telemetry.ZONE_METHOD
    def SetItemType(self, itemType, weight = 1.0, doUpdate = True):
        info = self.GetInfo()
        category = self.characterSvc.GetCategoryFromResPath(itemType[1][0])
        if category in CLOTHING_ITEMS:
            if category in self.clothesStorage:
                self.clothesStorage.pop(category)
                self.clothesMetaStorage.pop(category)
            self.ToggleClothes(forcedValue=0, doUpdate=False)
        self.characterSvc.ApplyTypeToDoll(info.charID, itemType, weight=weight, doUpdate=False)
        if category in self._setColorsByCategory:
            var1, var2 = self._setColorsByCategory[category]
            self.SetColorValue(category, var1, var2, doUpdate=False)
        self.ValidateColors(category)
        if doUpdate:
            self.characterSvc.UpdateDoll(info.charID, fromWhere='SetItemType')

    @telemetry.ZONE_METHOD
    def SetStyle(self, category, style, variation = None, doUpdate = True):
        info = self.GetInfo()
        if style or variation or category in CLOTHING_ITEMS:
            self.ToggleClothes(forcedValue=0, doUpdate=False)
        self.characterSvc.ApplyItemToDoll(info.charID, category, style, removeFirst=True, variation=variation, doUpdate=False)
        if style:
            if category in self._setColorsByCategory:
                var1, var2 = self._setColorsByCategory[category]
                self.SetColorValue(category, var1, var2, doUpdate=False)
            self.ValidateColors(category)
        if doUpdate:
            self.characterSvc.UpdateDoll(info.charID, fromWhere='SetStyle')

    @telemetry.ZONE_METHOD
    def ValidateColors(self, category):
        if category not in ccConst.COLORMAPPING:
            return
        info = self.GetInfo()
        categoryColors = self.characterSvc.GetAvailableColorsForCategory(category, info.genderID, info.raceID)
        if not categoryColors:
            return
        primary, secondary = categoryColors
        hasValidColor = False
        modifier = self.characterSvc.GetModifiersByCategory(info.charID, category)
        if modifier:
            currentColor = modifier[0].GetColorizeData()
            if secondary:
                if modifier[0].metaData.numColorAreas > 1:
                    for primaryColorTuple in primary:
                        primaryColorName, primaryDisplayColor, primaryColorValue = primaryColorTuple
                        pA, pB, pC = primaryColorValue['colors']
                        for secondaryColorTuple in secondary:
                            secondaryColorName, secondaryDisplayColor, secondaryColorValue = secondaryColorTuple
                            srA, srB, srC = secondaryColorValue['colors']
                            if pA == currentColor[0] and srB == currentColor[1] and srC == currentColor[2]:
                                hasValidColor = True
                                if category not in self._setColorsByCategory or self._setColorsByCategory[category][1] == None:
                                    self.SetColorValue(category, primaryColorTuple, secondaryColorTuple, doUpdate=False, ignoreValidate=True)
                                break

                        if hasValidColor:
                            break

                    if not hasValidColor:
                        for primaryColorTuple in primary:
                            primaryColorName, primaryDisplayColor, primaryColorValue = primaryColorTuple
                            if primaryColorValue['colors'] == currentColor:
                                hasValidColor = True
                                self.SetColorValue(category, primaryColorTuple, secondary[0], doUpdate=False, ignoreValidate=True)
                                break

                else:
                    for primaryColorTuple in primary:
                        primaryColorName, primaryDisplayColor, primaryColorValue = primaryColorTuple
                        if primaryColorValue['colors'] == currentColor:
                            hasValidColor = True
                            if category not in self._setColorsByCategory:
                                self.SetColorValue(category, primaryColorTuple, None, doUpdate=False, ignoreValidate=True)
                            break
                    else:
                        if category in self._setColorsByCategory:
                            hasValidColor = True
            else:
                for primaryColorTuple in primary:
                    primaryColorName, primaryDisplayColor, primaryColorValue = primaryColorTuple
                    if primaryColorValue['colors'] == currentColor:
                        hasValidColor = True
                        if category not in self._setColorsByCategory:
                            self.SetColorValue(category, primaryColorTuple, None, doUpdate=False, ignoreValidate=True)
                        break

            if not hasValidColor and primary:
                if secondary:
                    var2 = secondary[0]
                else:
                    var2 = None
                self.SetColorValue(category, primary[0], var2, doUpdate=False, ignoreValidate=True)

    def UpdateColorSelectionFromDoll(self, category):
        if category not in ccConst.COLORMAPPING:
            return
        info = self.GetInfo()
        categoryColors = self.characterSvc.GetAvailableColorsForCategory(category, info.genderID, info.raceID)
        if not categoryColors:
            return
        primary, secondary = categoryColors
        modifier = self.characterSvc.GetModifiersByCategory(info.charID, category)
        if modifier:
            corPrimary = None
            corSecondary = None
            try:
                chosenPrimary, chosenSecondary = self.characterSvc.GetSingleCharactersMetadata(info.charID).typeColors[category]
                for primaryColorTuple in primary:
                    if primaryColorTuple[0] == chosenPrimary:
                        corPrimary = primaryColorTuple
                        break

                if secondary and chosenSecondary:
                    for secondaryColorTuple in secondary:
                        if secondaryColorTuple[0] == chosenSecondary:
                            corSecondary = secondaryColorTuple
                            break

            except KeyError:
                log.LogWarn('KeyError when getting Metadata for a single character in characterCreationContainer.UpdateColorSelectionFromDoll', info.charID, category)

            if corPrimary is not None:
                self._setColorsByCategory[category] = (corPrimary, corSecondary)
            if category in self.characterSvc.characterMetadata[info.charID].typeWeights:
                self._setIntensityByCategory[category] = self.characterSvc.characterMetadata[info.charID].typeWeights[category]
            if category in self.characterSvc.characterMetadata[info.charID].typeSpecularity:
                self._setSpecularityByCategory[category] = self.characterSvc.characterMetadata[info.charID].typeSpecularity[category]

    @telemetry.ZONE_METHOD
    def ClearCategory(self, category, doUpdate = True):
        self.SetStyle(category, style=None, doUpdate=doUpdate)

    @telemetry.ZONE_METHOD
    def CheckDnaLog(self, trigger = None):
        if self.step and self.step.sr.historySlider:
            currentIndex, maxIndex = self.step.sr.historySlider.GetCurrentIndexAndMaxIndex()
            if currentIndex != maxIndex:
                self.ClearDnaLogFromIndex(currentIndex)

    @telemetry.ZONE_METHOD
    def ClearCamera(self):
        if self.camera is not None:
            for priority, behavior in self.camera.cameraBehaviors:
                behavior.camera = None

            del self.camera.cameraBehaviors[:]
            self.camera.avatar = None
            self.camera = None

    @telemetry.ZONE_METHOD
    def SetDefaultLighting(self):
        self.SetLightScene('res:/Graphics/Character/Global/PaperdollSettings/LightSettings/Normal.red')
        if self.IsSlowMachine():
            self.ReduceLights()

    @telemetry.ZONE_METHOD
    def SetupCameraUpdateJob(self):
        self.sceneManager.RefreshJob(self.camera)
        if self.cameraUpdateJob is None:
            self.cameraUpdateJob = trinity.renderJob.CreateRenderJob('cameraUpdate')
            r = trinity.TriStepPythonCB()
            r.SetCallback(self.UpdateCamera)
            self.cameraUpdateJob.steps.append(r)
        self.sceneManager.characterRenderJob.SetCameraUpdate(self.cameraUpdateJob)

    @telemetry.ZONE_METHOD
    def UpdateCamera(self):
        if self.camera is not None:
            self.camera.Update()

    @telemetry.ZONE_METHOD
    def PickObjectUV(self, pos):
        return self.scene.PickObjectUV(pos[0], pos[1], self.camera.projectionMatrix, self.camera.viewMatrix, trinity.device.viewport)

    @telemetry.ZONE_METHOD
    def PickObjectAndArea(self, pos):
        return self.scene.PickObjectAndArea(pos[0], pos[1], self.camera.projectionMatrix, self.camera.viewMatrix, trinity.device.viewport)

    @telemetry.ZONE_METHOD
    def PickObject(self, pos):
        if not self.step:
            return
        if self.scene is not None:
            return self.scene.PickObject(pos[0], pos[1], self.camera.projectionMatrix, self.camera.viewMatrix, self.step.GetViewportForPicking())

    @telemetry.ZONE_METHOD
    def SaveCurrentCharacter(self, charactername, bloodlineID, genderID, portraitID):
        total = 3
        sm.GetService('loading').ProgressWnd(localization.GetByLabel('UI/CharacterCreation/Registering'), localization.GetByLabel('UI/CharacterCreation/CompilePrefs'), 1, total)
        try:
            if self.portraitInfo[portraitID] is None:
                raise UserError('CharCreationNoPortrait')
            info = self.GetInfo()
            charInfo = self.characterSvc.GetCharacterAppearanceInfo(info.charID)
            charID = sm.GetService('cc').CreateCharacterWithDoll(charactername, bloodlineID, genderID, const.ancestryUndefined, charInfo, self.portraitInfo[portraitID], info.schoolID, info.raceID)
        except UserError as what:
            if not what.msg.startswith('CharNameInvalid'):
                eve.Message(*what.args)
                return
            sm.GetService('loading').ProgressWnd(localization.GetByLabel('UI/CharacterCreation/Registering'), localization.GetByLabel('UI/CharacterCreation/FailedForSomeReason'), 3, total)
        else:
            sm.GetService('loading').ProgressWnd(localization.GetByLabel('UI/CharacterCreation/Registering'), localization.GetByLabel('UI/CharacterCreation/InsertingRecord'), 2, total)
            sm.GetService('photo').AddPortrait(self.GetPortraitSnapshotPath(portraitID), charID)
            sm.GetService('loading').ProgressWnd(localization.GetByLabel('UI/CharacterCreation/Registering'), localization.GetByLabel('UI/Generic/Done'), 3, total)
            return charID
        finally:
            self.sessionSounds = []

    @telemetry.ZONE_METHOD
    def UpdateExistingCharacter(self, *args):
        portraitID = self.activePortraitIndex
        charID = self.charID
        activePortraitInfo = self.portraitInfo[portraitID]
        if activePortraitInfo is None:
            raise UserError('CharCreationNoPortrait')
        dollExists = self.dna is not None
        dollInfo = self.characterSvc.GetCharacterAppearanceInfo(charID)
        availableTypeIDs = sm.GetService('cc').GetMyApparel()
        metadata = self.characterSvc.characterMetadata[charID]
        typesInUse = metadata.types
        for resourceID in typesInUse.itervalues():
            if resourceID:
                info = cfg.paperdollResources.Get(resourceID)
                if info.typeID is not None and info.typeID not in availableTypeIDs:
                    raise UserError('ItemNotAtStation', {'item': info.typeID})

        bgInfo = cfg.paperdollPortraitResources.Get(activePortraitInfo.backgroundID)
        if bgInfo and bgInfo.typeID is not None and bgInfo.typeID not in availableTypeIDs:
            raise UserError('ItemNotAtStation', {'item': bgInfo.typeID})
        try:
            if self.mode == ccConst.MODE_FULL_RECUSTOMIZATION:
                sm.GetService('cc').UpdateExistingCharacterFull(charID, dollInfo, activePortraitInfo, dollExists)
            elif self.mode == ccConst.MODE_LIMITED_RECUSTOMIZATION:
                sm.GetService('cc').UpdateExistingCharacterLimited(charID, dollInfo, activePortraitInfo, dollExists)
            elif self.mode == ccConst.MODE_FULL_BLOODLINECHANGE:
                info = self.GetInfo()
                sm.GetService('cc').UpdateExistingCharacterBloodline(charID, info.bloodlineID, True)
        except UserError as e:
            if e.msg == 'CCInvalidClothing':
                if e.dict['genderID'] == 0:
                    modifierNames = femaleModifierDisplayNames
                else:
                    modifierNames = maleModifierDisplayNames
                modifierName = modifierNames.get(e.dict['modifierKey'], '')
                eve.Message('CustomInfo', {'info': localization.GetByLabel('UI/Login/CharacterCreation/InvalidApparelAssets', modifierName=localization.GetByLabel(modifierName))})
                return

        sm.GetService('photo').AddPortrait(self.GetPortraitSnapshotPath(portraitID), charID)
        self.characterSvc.CachePortraitInfo(self.charID, self.portraitInfo[self.activePortraitIndex])
        self.metrics.complete_cc(charid=charID)
        if self.dollState != paperdoll.State.force_recustomize:
            self.ExitToStation()
        else:
            uthread.pool('GameUI::ActivateView::charsel', sm.GetService('viewState').ActivateView, 'charsel')

    @telemetry.ZONE_METHOD
    def SetBackdrop(self, backdropPath):
        self.backdropPath = backdropPath

    @telemetry.ZONE_METHOD
    def SetPoseID(self, poseID):
        self.poseID = poseID

    @telemetry.ZONE_METHOD
    def SetLightScene(self, lightPath, scene = None):
        scene = scene or self.scene
        lightScene = trinity.Load(lightPath)
        if scene:
            lightList = []
            for l in scene.lights:
                lightList.append(l)

            for l in lightList:
                scene.RemoveLightSource(l)

            for l in lightScene.lights:
                scene.AddLightSource(l)

    @telemetry.ZONE_METHOD
    def SetLights(self, lightID):
        self.lightingID = lightID
        self.UpdateLights()

    @telemetry.ZONE_METHOD
    def GetLight(self):
        return self.lightingID

    @telemetry.ZONE_METHOD
    def SetLightColor(self, lightID):
        self.lightColorID = lightID
        self.UpdateLights()

    @telemetry.ZONE_METHOD
    def GetLightColor(self):
        return self.lightColorID

    @telemetry.ZONE_METHOD
    def SetLightsAndColor(self, lightID, colorID):
        self.lightingID = lightID
        self.lightColorID = colorID
        self.UpdateLights()

    @telemetry.ZONE_METHOD
    def SetLightIntensity(self, intensity):
        self.lightIntensity = intensity
        self.UpdateLights()

    @telemetry.ZONE_METHOD
    def GetLightIntensity(self):
        return self.lightIntensity

    @telemetry.ZONE_METHOD
    def UpdateLights(self):
        lightsPath = GetGraphicFile(self.lightingID)
        lightColorPath = GetGraphicFile(self.lightColorID)
        lightScene = trinity.Load(lightsPath)
        lightColorScene = trinity.Load(lightColorPath)
        ccUtil.SetupLighting(self.scene, lightScene, lightColorScene, self.lightIntensity)
        if self.IsSlowMachine():
            self.ReduceLights()

    @telemetry.ZONE_METHOD
    def GetBackdrop(self):
        return self.backdropPath

    @telemetry.ZONE_METHOD
    def GetPoseId(self):
        return getattr(self, 'poseID', 0)

    @telemetry.ZONE_METHOD
    def StartEditMode(self, callback = None, **kwds):
        if callback is None and kwds.get('mode', None) == 'sculpt':
            callback = getattr(self.step, 'ChangeSculptingCursor', None)
        info = self.GetInfo()
        self.characterSvc.StartEditMode(info.charID, self.scene, self.camera, callback=callback, **kwds)

    @telemetry.ZONE_METHOD
    def UpdateBackdropLite(self, raceID, mouseEnter = False, *args):
        bdScene = self.sceneManager.Get2DBackdropScene()
        if not bdScene:
            return
        blue.resMan.SetUrgentResourceLoads(True)
        for each in bdScene.children:
            each.display = False
            if mouseEnter:
                if raceID:
                    if each.name == 'mouseoverSprite_%d' % raceID:
                        each.display = True
                else:
                    each.display = True
            elif each.name == 'backdropSprite':
                each.texturePrimary.resPath = 'res:/UI/Texture/CharacterCreation/bg/RACE_Background_%d.dds' % raceID
                each.display = True

        blue.resMan.SetUrgentResourceLoads(False)

    def _GetDpiScaledWidthAndHeight(self):
        desktopWidth = int(uicore.desktop.width * uicore.desktop.dpiScaling)
        desktopHeight = int(uicore.desktop.height * uicore.desktop.dpiScaling)
        return (desktopWidth, desktopHeight)

    def _AssembleBackDropSprite(self, name, res_path, bgSize = None):
        desktopWidth, desktopHeight = self._GetDpiScaledWidthAndHeight()
        if bgSize is None:
            bgSize = max(desktopWidth, desktopHeight)
        sprite = trinity.Tr2Sprite2d()
        sprite.name = name
        sprite.displayWidth = bgSize
        sprite.displayHeight = bgSize
        sprite.displayY = (desktopHeight - bgSize) / 2
        sprite.displayX = (desktopWidth - bgSize) / 2
        sprite.texturePrimary = trinity.Tr2Sprite2dTexture()
        sprite.texturePrimary.resPath = res_path
        sprite.display = True
        return sprite

    def _GetCurrentSpritePath(self):
        if self.stepID == ccConst.EMPIRESTEP:
            return ccConst.EMPIRE_PANELS_BACKGROUND
        if self.stepID in ccConst.EMPIRE_SELECTION_STEPS:
            return ccConst.EMPIRE_BACKGROUND_BY_RACE.get(self.raceID, None)

    def _GetBackdropSpriteSizes(self):
        clientHeight = uicore.desktop.height
        percentOfClientHeight = float(clientHeight) / BG_HEIGHT
        height = clientHeight
        width = int(percentOfClientHeight * BG_WIDTH)
        return (width, height)

    def _CreateNewBackdropSprite(self, path):
        spriteID = const.races[self.raceID] if self.raceID else 'Global'
        width, height = self._GetBackdropSpriteSizes()
        return Sprite(name='charCreationBackground_%s' % spriteID, parent=self, texturePath=path, align=uiconst.CENTER, width=width, height=height, opacity=BG_OPACITY)

    def UpdateBackdropSprite(self):
        spritePath = self._GetCurrentSpritePath()
        if spritePath is None:
            if self.backgroundSprite and not self.backgroundSprite.destroyed:
                self.backgroundSprite.Close()
            return
        if self.backgroundSprite and not self.backgroundSprite.destroyed:
            if spritePath == self.backgroundSprite.texturePath:
                width, height = self._GetBackdropSpriteSizes()
                self.backgroundSprite.width = width
                self.backgroundSprite.height = height
                return
            oldSprite = self.backgroundSprite
            oldSpriteOrder = oldSprite.GetOrder()
            self.backgroundSprite = self._CreateNewBackdropSprite(spritePath)
            self.backgroundSprite.SetOrder(oldSpriteOrder)
            uicore.animations.SpMaskIn(self.backgroundSprite, duration=BACKGROUND_TRANSITION_SECONDS, callback=oldSprite.Close)
        elif self.stepID in ccConst.EMPIRE_SELECTION_STEPS:
            self.backgroundSprite = self._CreateNewBackdropSprite(spritePath)

    @telemetry.ZONE_METHOD
    def UpdateBackdrop(self, *args):
        self.UpdateBackdropSprite()
        bdScene = self.sceneManager.Get2DBackdropScene()
        if not bdScene:
            return
        bdScene.clearBackground = True
        for each in bdScene.children[:]:
            bdScene.children.remove(each)

        for each in bdScene.curveSets[:]:
            bdScene.curveSets.remove(each)

        self.colorCodedBackDrop = None
        desktopWidth, desktopHeight = self._GetDpiScaledWidthAndHeight()
        size = min(desktopHeight, desktopWidth)
        margin = -200
        info = self.GetInfo()
        if gfxsettings.Get(gfxsettings.UI_NCC_GREEN_SCREEN):
            backdropSprite = self._AssembleBackDropSprite(u'greenscreen', 'res:/UI/Texture/CharacterCreation/backdrops/Background_1001_thumb.dds')
            bdScene.children.append(backdropSprite)
        else:
            if self.stepID in ccConst.EMPIRE_SELECTION_STEPS:
                return
            if info.raceID == const.raceCaldari:
                rn = 'caldari'
                bgcolor = (74 / 255.0, 87 / 255.0, 97 / 255.0)
            elif info.raceID == const.raceAmarr:
                rn = 'amarr'
                bgcolor = (93 / 255.0, 89 / 255.0, 74 / 255.0)
            elif info.raceID == const.raceMinmatar:
                rn = 'minmatar'
                bgcolor = (92 / 255.0, 81 / 255.0, 80 / 255.0)
            elif info.raceID == const.raceGallente:
                rn = 'gallente'
                bgcolor = (77 / 255.0, 94 / 255.0, 93 / 255.0)
            else:
                rn = 'caldari'
                bgcolor = (74 / 255.0, 87 / 255.0, 97 / 255.0)
                log.LogWarn('Unknown raceID in characterCreationContainer.UpdateBackground', info.raceID)
            mainHalo = trinity.Tr2Sprite2d()
            mainHalo.name = u'mainHalo'
            mainHalo.texturePrimary = trinity.Tr2Sprite2dTexture()
            mainHalo.blendMode = trinity.TR2_SBM_ADD
            r, g, b = bgcolor
            mainHalo.color = (r * 0.75,
             g * 0.75,
             b * 0.75,
             1.0)
            mainHalo.displayWidth = mainHalo.displayHeight = max(desktopWidth, desktopHeight) * 1.5
            mainHalo.displayX = (desktopWidth - mainHalo.displayWidth) / 2
            mainHalo.displayY = (desktopHeight - mainHalo.displayHeight) / 2
            mainHalo.display = True
            mainHalo.texturePrimary.resPath = 'res:/UI/Texture/CharacterCreation/mainCenterHalo.dds'
            bdScene.children.append(mainHalo)
            if self.stepID == ccConst.PORTRAITSTEP:
                activeBackdrop = self.GetBackdrop()
                if activeBackdrop:
                    portraitBackground = trinity.Tr2Sprite2d()
                    portraitBackground.name = u'portraitBackground'
                    bdScene.children.insert(0, portraitBackground)
                    portraitBackground.displayX = (desktopWidth - size) * 0.5
                    portraitBackground.displayY = (desktopHeight - size) * 0.5
                    portraitBackground.displayWidth = size
                    portraitBackground.displayHeight = size
                    if not portraitBackground.texturePrimary:
                        portraitBackground.texturePrimary = trinity.Tr2Sprite2dTexture()
                        portraitBackground.texturePrimary.resPath = activeBackdrop
                    portraitBackground.color = (1, 1, 1, 1)
                    portraitBackground.display = True
                    portraitBackground.blendMode = trinity.TR2_SBM_BLEND
            else:
                if gfxsettings.Get(gfxsettings.UI_NCC_GREEN_SCREEN):
                    return
                mainSize = size - margin
                cs = trinity.TriCurveSet()
                cs.name = 'RotationCurveSet'
                bdScene.curveSets.append(cs)
                for textureNo, textureSize in ((1, 468 / 1024.0),
                 (2, 580 / 1024.0),
                 (3, 1.0),
                 (4, 1.0)):
                    tf = trinity.Tr2Sprite2dTransform()
                    tf.name = u'tf'
                    tf.displayX = desktopWidth * 0.5
                    tf.displayY = desktopHeight * 0.5
                    bdScene.children.append(tf)
                    circleBG = trinity.Tr2Sprite2d()
                    circleBG.name = u'circleBG'
                    circleBG.texturePrimary = trinity.Tr2Sprite2dTexture()
                    circleBG.texturePrimary.resPath = 'res:/UI/Texture/CharacterCreation/circularRaceBgs/%s_%s.dds' % (rn, textureNo)
                    circleBG.color = (0.025, 0.025, 0.025, 1.0)
                    circleBG.blendMode = trinity.TR2_SBM_BLEND
                    circleBG.displayWidth = mainSize * textureSize
                    circleBG.displayHeight = mainSize * textureSize
                    circleBG.displayX = -circleBG.displayWidth * 0.5
                    circleBG.displayY = -circleBG.displayHeight * 0.5
                    circleBG.display = True
                    tf.children.append(circleBG)
                    rotationCurve = self.CreatePerlinCurve(cs, scale=16.0, offset=10.0, speed=0.001, alpha=0.9, beta=1.0 + random.random())
                    self.CreateBinding(cs, rotationCurve, tf, 'rotation', 'value')

                cs.Play()

    @telemetry.ZONE_METHOD
    def CreateBinding(self, curveSet, curve, destinationObject, attribute, sourceAttribute = 'currentValue'):
        binding = trinity.TriValueBinding()
        curveSet.bindings.append(binding)
        binding.destinationObject = destinationObject
        binding.destinationAttribute = attribute
        binding.sourceObject = curve
        binding.sourceAttribute = sourceAttribute
        return binding

    @telemetry.ZONE_METHOD
    def CreatePerlinCurve(self, curveSet, scale = 1.0, offset = 6.0, speed = 1.1, alpha = 1.0, beta = 1.1):
        curve = trinity.TriPerlinCurve()
        curve.scale = scale
        curve.offset = offset
        curve.speed = speed
        curve.alpha = alpha
        curve.beta = beta
        curveSet.curves.append(curve)
        return curve

    @telemetry.ZONE_METHOD
    def GetLightID(self):
        path = self.lightingID
        files = ccConst.LIGHT_SETTINGS_ID
        for i, light in enumerate(files):
            if path == light:
                return i

        return 1

    @telemetry.ZONE_METHOD
    def GetLightColorID(self):
        path = self.lightColorID
        files = ccConst.LIGHT_COLOR_SETTINGS_ID
        for i, light in enumerate(files):
            if path == light:
                return i

        return 1

    @telemetry.ZONE_METHOD
    def GetCurrentBackgroundID(self):
        path = self.backdropPath
        return self.GetBackgroundID(path)

    def GetBackgroundID(self, path):
        authoredBackground = self.characterSvc.GetPortraitResourceByPath(path)
        if authoredBackground:
            return authoredBackground.portraitResourceID
        ID = path.split('_')[-1].split('.')[0]
        try:
            ID = int(ID)
        except ValueError:
            return None

        return ID

    @telemetry.ZONE_METHOD
    def GetBackgroundPathFromID(self, bgID):
        if bgID < const.NCC_MIN_NORMAL_BACKGROUND_ID:
            return 'res:/UI/Texture/CharacterCreation/backdrops/Background_' + str(bgID) + '.dds'
        resourceRow = cfg.paperdollPortraitResources.Get(bgID)
        if resourceRow:
            return resourceRow.resPath

    @telemetry.ZONE_METHOD
    def CapturePortrait(self, portraitID, *args):
        if self.camera is None:
            return
        poseData = self.characterSvc.GetPoseData()
        if poseData is None:
            return
        self.portraitInfo[portraitID] = utillib.KeyVal(cameraPosition=self.camera.GetPosition(), cameraFieldOfView=self.camera.fieldOfView, cameraPoi=self.camera.GetPointOfInterest(), backgroundID=self.GetCurrentBackgroundID(), lightID=self.lightingID, lightColorID=self.lightColorID, lightIntensity=self.GetLightIntensity(), poseData=poseData)
        maker = PortraitMaker(self.camera, self.backdropPath)
        return maker.GetPortraitTexture(portraitID)

    @telemetry.ZONE_METHOD
    def GetPortraitSnapshotPath(self, portraitID):
        return blue.paths.ResolvePathForWriting(u'cache:/Pictures/Portraits/PortraitSnapshot_%s_%s.jpg' % (portraitID, session.userid))

    @telemetry.ZONE_METHOD
    def ClearPortraitInfo(self):
        self.portraitInfo = [None] * ccConst.NUM_PORTRAITS

    @telemetry.ZONE_METHOD
    def GetPortraitInfo(self, portraitID):
        return self.portraitInfo[portraitID]

    @telemetry.ZONE_METHOD
    def GetDNA(self, getHiddenModifiers = False, getWeightless = False):
        return self.doll.GetDNA(getHiddenModifiers=getHiddenModifiers, getWeightless=getWeightless)

    @telemetry.ZONE_METHOD
    def OnHideUI(self, *args):
        self.uiContainer.state = uiconst.UI_HIDDEN

    @telemetry.ZONE_METHOD
    def OnShowUI(self, *args):
        self.uiContainer.state = uiconst.UI_PICKCHILDREN

    def OnMapShortcut(self, *args):
        uicore.cmd.commandMap.UnloadAllAccelerators()
        uicore.cmd.commandMap.LoadAcceleratorsByCategory('general')

    @telemetry.ZONE_METHOD
    def ShowLoading(self, why = '', top = 200, forceOn = 0, *args):
        wheel = self.loadingWheel
        wheel.top = top
        wheel.hint = why
        wheel.forcedOn = forceOn
        wheel.Show()

    @telemetry.ZONE_METHOD
    def HideLoading(self, why = '', forceOff = 0, *args):
        wheel = self.loadingWheel
        if not wheel.forcedOn or forceOff:
            self.loadingWheel.Hide()
            wheel.forcedOn = 0

    @telemetry.ZONE_METHOD
    def OnCloseView(self):
        uicore.cmd.LoadAllAccelerators()
        self.TearDown()
        self.audioService.SendUIEvent('ui_icc_sculpting_mouse_over_loop_stop')
        if self.audioService.GetWorldVolume() == 0.0:
            self.audioService.SetWorldVolume(self.worldLevel)
        sm.GetService('cc').ClearMyAvailabelTypeIDs()
        self.Flush()
        self.step = None
        if self.previewCharWindowWasOpenOn is not None:
            charID = self.previewCharWindowWasOpenOn[0]
            self.previewCharWindowWasOpenOn = None
            sm.GetService('preview').PreviewCharacter(charID)
        if self.previewWindowWasOpenOn is not None:
            typeID = self.previewWindowWasOpenOn
            sm.GetService('preview').PreviewType(typeID)

    @telemetry.ZONE_METHOD
    def ExitToStation(self, updateDoll = True):
        self.OnCloseView()
        if session.structureid:
            change = {'structureid': (None, session.structureid)}
        else:
            change = {'stationid': (None, session.stationid)}
        sm.GetService('gameui').OnSessionChanged(isRemote=False, session=session, change=change)

    def ToggleClothes(self, forcedValue = None, doUpdate = True, *args):
        valueBefore = self.clothesOff
        if forcedValue is None:
            self.clothesOff = not self.clothesOff
        else:
            self.clothesOff = forcedValue
        if valueBefore == self.clothesOff:
            return
        info = self.GetInfo()
        if info.charID in self.characterSvc.characters:
            character = self.characterSvc.GetSingleCharacter(info.charID)
            if self.clothesOff:
                self.RemoveClothes(character, doUpdate=doUpdate)
            else:
                self.ReApplyClothes(character, doUpdate=doUpdate)

    @telemetry.ZONE_METHOD
    def ReApplyClothes(self, character, doUpdate = True):
        if not self.clothesStorage or character is None:
            return
        doll = character.doll
        bdm = doll.buildDataManager
        for category in self.clothesMetaStorage:
            self.characterSvc.SetCharacterMetadataByCategory(self.charID, category, self.clothesMetaStorage[category])

        modifiers = doll.SortModifiersForBatchAdding(self.clothesStorage.values())
        for modifier in modifiers:
            bdm.AddModifier(modifier)

        self.ResetClothesStorage()
        if doUpdate:
            sm.GetService('character').UpdateDollsAvatar(character)

    @telemetry.ZONE_METHOD
    def RemoveClothes(self, character, doUpdate = True):
        if self.clothesStorage or character is None:
            return
        categoriesToRemove = BODY_CATEGORIES - (BODY_CATEGORIES.SKIN,
         BODY_CATEGORIES.TATTOO,
         BODY_CATEGORIES.TOPUNDERWEAR,
         BODY_CATEGORIES.BOTTOMUNDERWEAR,
         BODY_CATEGORIES.SKINTONE,
         BODY_CATEGORIES.SKINTYPE,
         BODY_CATEGORIES.SCARS)
        categoriesToRemove = list(categoriesToRemove)
        categoriesToRemove.sort(key=lambda x: -DESIRED_ORDER.index(x))
        self.ResetClothesStorage()
        bdm = character.doll.buildDataManager
        for category in categoriesToRemove:
            categoryModifiers = bdm.GetModifiersByCategory(category)
            self.StoreCharacterMetadata(category)
            self.characterSvc.RemoveFromCharacterMetadata(self.charID, category)
            for modifier in categoryModifiers:
                if modifier.respath not in DEFAULT_NUDE_PARTS:
                    self.clothesStorage[category] = modifier
                    bdm.RemoveModifier(modifier)

        modifier = self.characterSvc.GetModifierByCategory(self.charID, ccConst.glasses)
        if modifier:
            self.StoreCharacterMetadata(ccConst.glasses)
            self.characterSvc.RemoveFromCharacterMetadata(self.charID, ccConst.glasses)
            self.clothesStorage[ccConst.glasses] = modifier
            bdm.RemoveModifier(modifier)
        modifier = self.characterSvc.GetModifierByCategory(self.charID, ccConst.mask)
        if modifier:
            self.StoreCharacterMetadata(ccConst.mask)
            self.characterSvc.RemoveFromCharacterMetadata(self.charID, ccConst.mask)
            self.clothesStorage[ccConst.mask] = modifier
            bdm.RemoveModifier(modifier)
        if doUpdate:
            sm.GetService('character').UpdateDollsAvatar(character)

    def StoreCharacterMetadata(self, category):
        self.clothesMetaStorage[category] = self.characterSvc.GetCharacterMetadataByCategory(self.charID, category)

    def ResetClothesStorage(self, *args):
        self.clothesStorage.clear()
        self.clothesMetaStorage.clear()

    def RemoveBodyModifications(self, *args):
        try:
            if getattr(self, 'bodyModRemoved', 0):
                return
            modifiersToRemove = [ccConst.p_earslow,
             ccConst.p_earshigh,
             ccConst.p_nose,
             ccConst.p_nostril,
             ccConst.p_brow,
             ccConst.p_lips,
             ccConst.p_chin,
             ccConst.t_head,
             ccConst.s_head]
            character = self.characterSvc.GetSingleCharacter(self.charID)
            for mod in modifiersToRemove:
                modifiers = self.characterSvc.GetModifiersByCategory(self.charID, mod)
                for m in modifiers:
                    character.doll.buildDataManager.RemoveModifier(m)
                    self.characterSvc.RemoveFromCharacterMetadata(self.charID, mod)

            self.bodyModRemoved = 1
            sm.GetService('character').UpdateDollsAvatar(character)
        except Exception:
            pass

    @telemetry.ZONE_METHOD
    def StartDnaLogging(self):
        self.dnaList = []
        self.lastLitHistoryBit = None

    def ResetDna(self, *args):
        self.dnaList = None
        self.lastLitHistoryBit = None

    @telemetry.ZONE_METHOD
    def ClearDnaLogFromIndex(self, fromIndex):
        if self.dnaList:
            to = fromIndex + 1
            if to > len(self.dnaList):
                to = len(self.dnaList)
            self.dnaList = self.dnaList[:to]

    @telemetry.ZONE_METHOD
    def GetDollDNAHistory(self):
        return self.dnaList

    def TryStoreDna(self, lastUpdateRedundant, fromWhere, sculpting = 0, force = 0, allowReduntant = 0, *args):
        if not lastUpdateRedundant or fromWhere in ('RandomizeCharacterGroups', 'RandomizeCharacter', 'AddCharacter'):
            if not self.parent.isopen:
                return
            if self.stepID == ccConst.CUSTOMIZATIONSTEP:
                if self.step is None:
                    return
                if not force and self.step.menuMode == self.step.TATTOOMENU:
                    self.step.tattooChangeMade = 1
                    return
            if self.dnaList is not None:
                self.CheckDnaLog('UpdateDoll')
                dna = self.GetDNA(getHiddenModifiers=False, getWeightless=True)
                if not allowReduntant:
                    try:
                        currentIndex, maxIndex = self.step.sr.historySlider.GetCurrentIndexAndMaxIndex()
                        if dna == self.dnaList[currentIndex][0]:
                            return
                    except Exception:
                        pass

                currMetadata = copy.deepcopy(self.characterSvc.characterMetadata[self.charID])
                self.dnaList.append((dna, currMetadata))
                if lastUpdateRedundant or force:
                    sm.ScatterEvent('OnHistoryUpdated')

    @telemetry.ZONE_METHOD
    def LoadDnaFromHistory(self, historyIndex):
        if len(self.characterSvc.characters) > 0:
            character = self.characterSvc.GetSingleCharacter(self.charID)
            if character:
                historyIndex = max(0, min(len(self.dnaList) - 1, historyIndex))
                dna, metadata = self.dnaList[historyIndex]
                metadata = copy.deepcopy(metadata)
                self.ToggleClothes(forcedValue=0, doUpdate=False)
                self.characterSvc.MatchDNA(character, dna)
                self.characterSvc.characterMetadata[self.charID] = metadata
                if self.characterSvc.GetSculptingActive():
                    sculpting = self.characterSvc.GetSculpting()
                    sculpting.UpdateFieldsBasedOnExistingValues(character.doll)
                self.characterSvc.UpdateDoll(self.charID, fromWhere='LoadDnaFromHistory', registerDna=False)
                self.characterSvc.SynchronizeHairColors(self.charID)

    @telemetry.ZONE_METHOD
    def PassMouseEventToSculpt(self, type, x, y):
        if not hasattr(self, 'characterSvc'):
            return
        if getattr(self, 'doll', None) is None:
            return
        if self.doll.IsBusyUpdating():
            return
        sculpting = self.characterSvc.GetSculpting()
        if not uicore.uilib.leftbtn and sculpting and sculpting.startXY is not None and self.characterSvc.GetSculptingActive():
            type = 'LeftUp'
        pickValue = None
        if sculpting and self.characterSvc.GetSculptingActive():
            if type == 'LeftDown':
                pickValue = sculpting.PickWrapper(x, y)
            elif type == 'LeftUp':
                pickValue = sculpting.EndMotion(x, y)
            elif type == 'Motion':
                pickValue = sculpting.MotionWrapper(x, y)
        return pickValue

    def PickPortrait(self, newPortraitID):
        if self.stepID != ccConst.PORTRAITSTEP:
            return
        self.step.PickPortrait(newPortraitID)

    def AnimateToStoredPortrait(self, newPortraitID):
        if self.stepID != ccConst.PORTRAITSTEP:
            return
        if self.portraitInfo[newPortraitID] is None:
            return
        if self.animateToStoredPortraitThread and self.animateToStoredPortraitThread.alive:
            if self.animatingToPortraitID == newPortraitID:
                return
            self.animateToStoredPortraitThread.kill()
        self.animateToStoredPortraitThread = uthread.new(self.AnimateToStoredPortrait_thread, newPortraitID)

    def AnimateToStoredPortrait_thread(self, newPortraitID):
        portraitInfo = self.portraitInfo[newPortraitID]
        if portraitInfo is None:
            return
        newParams = self.GetControlParametersFromPortraitID(newPortraitID)
        if newParams is None:
            return
        oldParams = self.GetControlParametersFromPortraitID(None)
        if len(oldParams) < 1 or len(newParams) < 1:
            return
        self.animatingToPortraitID = newPortraitID
        thereIsCamera = self.camera is not None
        if thereIsCamera:
            oldCameraPos = self.camera.cameraPosition
            oldCameraPoi = self.camera.poi
            oldCameraFov = self.camera.fieldOfView
        info = self.GetInfo()
        start, ndt = blue.os.GetWallclockTime(), 0.0
        moveCamera = self.ShouldMoveCamera(portraitInfo.cameraPosition, portraitInfo.cameraPoi)
        while ndt != 1.0:
            timeValue = min(blue.os.TimeDiffInMs(start, blue.os.GetWallclockTime()) / 250.0, 1.0)
            ndt = math.sin(timeValue * math.pi - math.pi / 2.0) / 2.0 + 0.5
            params = []
            for shortKey, keyAndValue in oldParams.iteritems():
                longKey, value = keyAndValue
                if shortKey == 'HeadLookTarget':
                    lerpedValue = geo2.Lerp(value, newParams[shortKey][1], ndt)
                elif shortKey == 'PortraitPoseNumber':
                    continue
                else:
                    lerpedValue = mathext.lerp(value, newParams[shortKey][1], ndt)
                params.append([longKey, lerpedValue])

            sm.GetService('character').SetControlParametersFromList(params, info.charID)
            if thereIsCamera and moveCamera:
                posValue = geo2.Lerp(oldCameraPos, portraitInfo.cameraPosition, ndt)
                poiValue = geo2.Lerp(oldCameraPoi, portraitInfo.cameraPoi, ndt)
                self.cameraPos = posValue
                self.cameraPoi = poiValue
                self.camera.PlacePortraitCamera(self.cameraPos, self.cameraPoi)
            blue.pyos.synchro.Yield()

        xFactor, yFactor = self.camera.GetCorrectCameraXandYFactors(portraitInfo.cameraPosition, portraitInfo.cameraPoi)
        self.camera.xFactor = self.camera.xTarget = xFactor
        self.camera.yFactor = self.camera.yTarget = yFactor
        self.lightingID = portraitInfo.lightID
        self.lightIntensity = portraitInfo.lightIntensity
        self.lightColorID = portraitInfo.lightColorID
        shouldSnapPortrait = False
        path = self.GetBackgroundPathFromID(portraitInfo.backgroundID)
        if path in self.GetAvailableBackgroundsPaths():
            self.backdropPath = path
        elif not gfxsettings.Get(gfxsettings.UI_NCC_GREEN_SCREEN):
            shouldSnapPortrait = True
        self.poseID = int(portraitInfo.poseData['PortraitPoseNumber'])
        sm.GetService('character').SetControlParametersFromList([['ControlParameters|PortraitPoseNumber', float(self.poseID)]], info.charID)
        uicore.layer.charactercreation.controller.UpdateBackdrop()
        self.UpdateLights()
        sm.ScatterEvent('OnPortraitPicked')
        if shouldSnapPortrait and self.step:
            self.step.CapturePortrait(newPortraitID)

    def ShouldMoveCamera(self, newPos, newPoi):
        newDirection = geo2.Subtract(newPos, newPoi)
        distanceDiff = abs(self.camera.distance - geo2.Vec3Length(newDirection))
        direction2 = geo2.Vec3Normalize(newDirection)
        yaw = math.acos(direction2[0])
        yawDiff = abs(self.camera.yaw - yaw)
        pitch = math.asin(direction2[1]) + math.pi / 2.0
        pitchDiff = math.sqrt(math.pow(self.camera.pitch - pitch, 2))
        diffPos = geo2.Vec3Distance(self.camera.GetPosition(), newPos)
        if distanceDiff < 5e-07 and yawDiff < 5e-05 and pitchDiff < 5e-05 and diffPos < 0.05:
            return False
        return True

    def GetControlParametersFromPortraitID(self, portraitID, *args):
        PREFIX = 'ControlParameters|'
        params = {}
        if portraitID is not None:
            portraitInfo = uicore.layer.charactercreation.controller.portraitInfo[portraitID]
            if portraitInfo is None:
                return {}
            return self.GetControlParametersFromPoseData(portraitInfo.poseData)
        info = self.GetInfo()
        avatar = self.characterSvc.GetSingleCharactersAvatar(info.charID)
        if avatar is None:
            return {}
        for controlParameter in paperDollUtil.FACIAL_POSE_PARAMETERS.__dict__.iterkeys():
            if controlParameter.startswith('_'):
                continue
            longKey = PREFIX + controlParameter
            network = animparams.GetParamsPerAvatar(avatar, info.charID)
            value = network.GetControlParameterValue(longKey)
            params[controlParameter] = (longKey, value)

        return params

    def GetControlParametersFromPoseData(self, poseData, fromDB = False):
        if poseData is None:
            return {}
        if fromDB:
            allParameterKeys = poseData.__keys__
        else:
            allParameterKeys = poseData.keys()
        params = {}
        PREFIX = 'ControlParameters|'
        for key in allParameterKeys:
            if key in ('headLookTargetX', 'headLookTargetY', 'headLookTargetZ', 'cameraX', 'cameraY', 'cameraZ'):
                continue
            value = poseData[key]
            if fromDB:
                key = key.replace(key[0], key[0].upper(), 1)
            params[key] = (PREFIX + key, value)

        if fromDB:
            params['HeadLookTarget'] = (PREFIX + 'HeadLookTarget', (poseData['headLookTargetX'], poseData['headLookTargetY'], poseData['headLookTargetZ']))
        return params

    def TryFreezeAnimation(self, *args):
        if sm.GetService('machoNet').GetGlobalConfig().get('disableFreezeAnimationInNCC'):
            return
        if self.stepID != ccConst.CUSTOMIZATIONSTEP:
            return
        info = self.GetInfo()
        avatar = self.characterSvc.GetSingleCharactersAvatar(info.charID)
        if avatar is not None:
            network = animparams.GetParamsPerAvatar(avatar, info.charID)
            network.update = False
            self.freezingAnimation = True

    def UnfreezeAnimationIfNeeded(self, *args):
        if self.freezingAnimation:
            info = self.GetInfo()
            avatar = self.characterSvc.GetSingleCharactersAvatar(info.charID)
            if avatar is not None:
                network = animparams.GetParamsPerAvatar(avatar, info.charID)
                network.update = True
                self.freezingAnimation = False
