#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\login\characterCreationContainer_new.py
import logging
import math
import random
import time
import types
import blue
import telemetry
import carbonui.const as uiconst
import charactercreator.client.animparams as animparams
import charactercreator.client.characterCreationMetrics as ccm
import charactercreator.client.scalingUtils as ccScalingUtils
import charactercreator.const as ccConst
import eve.common.lib.appConst as const
import evegraphics.settings as gfxsettings
import everesourceprefetch
import gatekeeper
import geo2
import localization
import paperdoll
import trinity
import uthread
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui.control.button import Button
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from carbonui.util.bunch import Bunch
from charactercreator.client.characterCreationSteps_new import ModeStorage, GetStepOrder, GetStepsUpToAndIncluding
from charactercreator.client.logging.stepLogger import StepLogger
from charactercreator.const import FINALIZE_BUTTON_ANALYTIC_ID, NEXT_BUTTON_ANALYTIC_ID, BACK_BUTTON_ANALYTIC_ID
from characterdata.races import CHARACTER_CREATION_RACE_IDS
from eve.client.script.ui.camera.charCreationCamera import CONTROL_NONE
from eve.client.script.ui.login.charcreation_new import charCreationSignals, soundConst
from eve.client.script.ui.login.charcreation_new.charCreationButtons import EXIT_BUTTON_SIZE
from eve.client.script.ui.login.charcreation_new.dollManager import GetCharacterCreationDollManager
from eve.client.script.ui.login.charcreation_new.loadingWheel import CharacterCreationLoadingWheel
from eve.client.script.ui.login.charcreation_new.portraitManager import GetCharacterCreationPortraitManager
from eve.client.script.ui.login.charcreation_new.sceneManager import GetCharacterCreationSceneManager
from eve.client.script.ui.login.charcreation_new.steps.characterCustomization import CharacterCustomization
from eve.client.script.ui.login.charcreation_new.steps.characterNaming import CharacterNaming
from eve.client.script.ui.login.charcreation_new.steps.characterPortrait import CharacterPortrait
from eve.client.script.ui.login.charcreation_new.steps.dollSelection.characterDollSelection import CharacterDollSelection
from eve.client.script.ui.login.charcreation_new.steps.empireSelectionStep import EmpireSelectionStep
from eve.client.script.ui.shared.colorThemes import DEFAULT_COLORTHEMEID, COLOR_THEME_ID_BY_RACE
from eve.client.script.ui.util.disconnectNotice import DisconnectNotice
from eve.common.lib import appConst
from eveexceptions import UserError
from eveprefs import prefs, boot
from locks import TempLock
from storylines.client.airnpe import is_air_npe_enabled
NETWORKMODE_BASIC = 1
NETWORKMODE_PORTRAIT = 2
LEFT_SIDE_WITH = 180
LEFT_SIDE_HEIGHT = 400
RIGHT_SIDE_WIDTH = 350
RIGHT_SIDE_HEIGHT = 150
BOTTOM_LEFT_SIDE_WIDTH = 220
BOTTOM_LEFT_SIDE_HEIGHT = ccConst.BUTTON_AREA_HEIGHT
BUTTON_WIDTH = 145
BUTTON_HEIGHT = 36
BUTTON_HEIGHT_PRIMARY = 50
BUTTON_WIDTH_PRIMARY = 200
BUTTON_FONT_SIZE = 18
BACKGROUND_TRANSITION_SECONDS = 2.5
RESOURCE_WHEEL_SEPARATION = 8
DOLLSTATES_TO_RETURN_TO_CC = [paperdoll.State.no_existing_customization, paperdoll.State.force_recustomize]
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
logger = logging.getLogger(__name__)

class CharacterData(object):

    def __init__(self, charID):
        self.charID = charID
        self.bloodlineID = None
        self.genderID = None
        self.dna = None


class CharacterCreationContainer_new(Container):
    __notifyevents__ = ['OnSetDevice',
     'OnGraphicSettingsChanged',
     'OnHideUI',
     'OnShowUI',
     'OnDollUpdated',
     'OnMapShortcut',
     'OnUIRefresh',
     'OnDisconnect']
    __update_on_reload__ = 1

    def ApplyAttributes(self, attributes):
        super(CharacterCreationContainer_new, self).ApplyAttributes(attributes)
        sm.RegisterNotify(self)
        self.sceneManager = GetCharacterCreationSceneManager()
        self.portraitManager = GetCharacterCreationPortraitManager()
        self.dollManager = GetCharacterCreationDollManager()
        self.needSculptingTutorial = True
        self.needNavigationTutorial = True
        self.dollSelected = False
        self.customizationStepSkipped = False
        self.step = None
        self.vignette = None
        self.exitButton = None
        self._characterData = {}
        self._activeCharID = None
        self._spareCharID = ccConst.SPARE_CHAR_ID
        self._characterData[self._spareCharID] = CharacterData(self._spareCharID)
        self._dollsDirty = False
        charCreationSignals.onEmpireFactionSelected.connect(self.OnEmpireFactionSelected)

    def SetNameCallback(self, name):
        self.charName = name

    @telemetry.ZONE_METHOD
    def OnSetDevice(self, *args):
        self.UpdateLayout()
        self.portraitManager.UpdateBackdrop()

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
                self.topNavigationContainer.width = desktopWidth
                self.topNavigationContainer.height = ccScalingUtils.GetTopNavHeight()
        finally:
            self.UnlockEverything()

    @telemetry.ZONE_METHOD
    def OnOpenView(self, **kwargs):
        self.startTime = blue.os.GetWallclockTime()
        self.sceneManager.Initialize()
        self.portraitManager.Initialize()
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
        self.characterSvc = sm.GetService('character')
        self.sceneManagerSvc = sm.GetService('sceneManager')
        self.fastCharacterCreation = gfxsettings.Get(gfxsettings.GFX_CHAR_FAST_CHARACTER_CREATION)
        self.mode = ccConst.MODE_FULLINITIAL_CUSTOMIZATION
        self.modeStorage = ModeStorage()
        self.modeObject = self.modeStorage.GetModeFor(self.mode)
        self.dollSelected = False
        self.customizationStepSkipped = False
        self.raceID = None
        self.schoolID = None
        self.charName = ''
        sm.GetService('cc').ClearMyAvailabelTypeIDs()
        self._stepID = None
        self.floor = None
        self.showingHelp = 0
        self.topNavigationContainer = None
        self.CreateUI()
        self.technologyViewsTracker = None
        self.audioService = sm.GetService('audio')
        self.worldLevel = self.audioService.GetWorldVolume()
        self.audioService.SetWorldVolume(0.0)
        self.stepLogger = StepLogger(blue.os.GetWallclockTime)
        self.finalStepLogger = None
        self.metrics = None
        self.approve_in_progress = False
        self.save_in_progress = False
        charCreationSignals.onDollSelectionRandomizeStarting.connect(self.OnDollRandomizeStarting)
        charCreationSignals.onDollSelectionDollRandomized.connect(self.OnDollRandomized)

    def Finalize(self):
        self.Save()

    def CreateLoadingWheel(self):
        self.loadingWheel = CharacterCreationLoadingWheel(name='loadingWheel', parent=self, align=uiconst.CENTER, state=uiconst.UI_NORMAL)
        self.loadingWheel.forcedOn = 0

    def CreateUI(self):
        self.uiContainer = Container(name='uiContainer', parent=self, align=uiconst.TOALL)
        self.CreateLoadingWheel()
        self.leftSide = Container(name='leftSide', parent=self.uiContainer, align=uiconst.TOPLEFT, pos=(0,
         0,
         LEFT_SIDE_WITH,
         LEFT_SIDE_HEIGHT))
        self.rightSide = Container(name='rightSide', parent=self.uiContainer, align=uiconst.BOTTOMRIGHT, pos=(0,
         BOTTOM_LEFT_SIDE_HEIGHT - BUTTON_HEIGHT,
         RIGHT_SIDE_WIDTH,
         RIGHT_SIDE_HEIGHT))
        self.bottomLeftSide = Container(name='bottomLeftSide', parent=self.uiContainer, align=uiconst.BOTTOMLEFT, pos=(0,
         0,
         BOTTOM_LEFT_SIDE_WIDTH,
         BOTTOM_LEFT_SIDE_HEIGHT))
        self.buttonNavLeft = Container(name='buttonNavLeft', parent=self.bottomLeftSide, align=uiconst.TOTOP, height=BUTTON_HEIGHT, padLeft=10)
        self.buttonNavRight = Container(name='buttonNavRight', parent=self.rightSide, align=uiconst.TOBOTTOM, height=BUTTON_HEIGHT_PRIMARY, padRight=20)
        self.finalizeBtn = Button(name='finalizeButtonCC', parent=self.buttonNavRight, align=uiconst.TORIGHT, label=localization.GetByLabel('UI/CharacterCreation/EnterGame'), func=self.Finalize, left=10, args=(), state=uiconst.UI_HIDDEN)
        self.saveBtn = Button(name='saveButtonCC', parent=self.buttonNavRight, align=uiconst.TORIGHT, label=localization.GetByLabel('UI/CharacterCreation/Finalize'), func=self.Save, left=10, args=(), state=uiconst.UI_HIDDEN, analyticID=FINALIZE_BUTTON_ANALYTIC_ID)
        self.approveBtn = Button(name='nextButtonCC', parent=self.buttonNavRight, align=uiconst.TORIGHT, label=localization.GetByLabel('UI/Generic/Next'), func=self.Approve, left=10, args=())
        self.backBtn = Button(name='backButtonCC', parent=self.buttonNavLeft, align=uiconst.TOLEFT, label=localization.GetByLabel('UI/Commands/Back'), func=self.Back, args=(), left=10)
        self.blackOut = Fill(name='blackOutFill', parent=self, color=(0.0, 0.0, 0.0, 0.0))
        self.mainCont = Container(name='mainCont', parent=self, align=uiconst.TOALL)
        self.topNavigationContainer = Container(name='topNavigationContainer', parent=self.uiContainer, align=uiconst.TOTOP_NOPUSH, width=self.uiContainer.width, height=ccScalingUtils.GetTopNavHeight(), bgColor=(0.0, 0.0, 0.0, 1.0))
        self.topNavigationContainer.SetOrder(1)
        self.UpdateLayout()

    def OnAvailabilityCheck(self, name):
        if self.finalStepLogger:
            self.finalStepLogger.AddTriedName(name)

    def OnUIRefresh(self):
        while self.dollManager.GetDoll(self._activeCharID) is None and self.dollManager.GetDoll(self._activeCharID).IsBusyUpdating():
            blue.synchro.Yield()

        self.Flush()
        self.CreateUI()
        self.SwitchStep(self.stepID)

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

    def GetActiveCharacterData(self):
        return self._characterData[self._activeCharID]

    def SetBloodline(self, charID, bloodlineID):
        self._characterData[charID].bloodlineID = bloodlineID

    def SetActiveBloodline(self, bloodlineID):
        self._characterData[self._activeCharID].bloodlineID = bloodlineID

    def SetActiveGender(self, genderID):
        self._characterData[self._activeCharID].genderID = genderID

    @telemetry.ZONE_METHOD
    def SetCharDetails(self, charID = None, gender = None, raceID = None, bloodlineID = None, dollState = None):
        self.portraitManager.ClearFacePortrait()
        self.dollState = dollState
        self.raceID = raceID
        self._activeCharID = 0
        self._characterData[0] = CharacterData(0)
        if charID is not None:
            if charID not in self._characterData:
                self._characterData[charID] = CharacterData(charID)
            self._characterData[charID].bloodlineID = bloodlineID
            self._characterData[charID].genderID = int(gender)
            self._activeCharID = charID
            if dollState not in (paperdoll.State.force_recustomize, paperdoll.State.no_existing_customization):
                self._characterData[self._activeCharID].dna = sm.GetService('paperdoll').GetMyPaperDollData(self._activeCharID)
            mode = self.GetModeIDForDollState(dollState)
        else:
            mode = ccConst.MODE_FULLINITIAL_CUSTOMIZATION
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
        if self.raceID is None:
            self._ChangeRace(self._GetRandomRaceID())
        if self.GetActiveCharacterData().bloodlineID is None or self.GetActiveCharacterData().genderID is None:
            self.SetActiveBloodline(self.SelectRandomBloodline())
            self.SetActiveGender(self.SelectRandomGender())
        self.SwitchStep(stepID)

    @telemetry.ZONE_METHOD
    def GetInfo(self):
        data = self.GetActiveCharacterData()
        return Bunch(charID=self._activeCharID, raceID=self.raceID, bloodlineID=data.bloodlineID, genderID=data.genderID, dna=data.dna, schoolID=self.schoolID, stepID=self.stepID, charName=self.charName)

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
        self.topNavigationContainer.Hide()
        sm.GetService('gameui').MoveResourceLoadingIndicator(newAlignment=uiconst.BOTTOMLEFT, newLeft=20, newTop=RESOURCE_WHEEL_SEPARATION + ccConst.BUTTON_AREA_HEIGHT)

    @telemetry.ZONE_METHOD
    def SwitchStep(self, toStep, *args):
        if GetStepOrder(toStep) > GetStepOrder(self.stepID):
            if not self.PassedStepCheck(toStep):
                return
        try:
            self.LockEverything()
            self.backBtn.state = uiconst.UI_NORMAL
            charCreationSignals.onStepSwitched(self.stepID, toStep)
            self.FadeToBlack(why=localization.GetByLabel('UI/Generic/Loading'))
            with TempLock('CharacterCreationLayerUpdate'):
                self.UnfreezeAnimationIfNeeded()
                self.BlockOnUpdate()
                self.ConstructNavigationIfNeeded(toStep)
                if self.stepID == ccConst.CUSTOMIZATIONSTEP:
                    sm.StartService('audio').SendUIEvent(unicode('ui_icc_sculpting_mouse_over_loop_stop'))
                    self.step.StoreHistorySliderPosition()
                elif self.stepID == ccConst.PORTRAITSTEP:
                    sm.StartService('audio').SendUIEvent(unicode('ui_icc_sculpting_mouse_over_loop_stop'))
                    self.sceneManager.StorePortraitCameraSettings()
                self.step = None
                raceTheme = COLOR_THEME_ID_BY_RACE.get(self.raceID, DEFAULT_COLORTHEMEID)
                sm.GetService('uiColor').SetNoCharTheme(raceTheme)
                self.BlockOnUpdate()
                self._UpdateNavigationButtons(toStep)
                self.mainCont.Flush()
                self.Cleanup()
                self.BlockOnUpdate()
                self.metrics.new_page(toStep)
                self.StartStep(toStep)
                self.stepID = toStep
                self.stepsUsed.add(toStep)
                self.portraitManager.UpdateBackdrop()
        finally:
            self.UnlockEverything()
            self.setupDone = 1
            self.FadeFromBlack()
            self.UnfreezeAnimationIfNeeded()
            sm.ScatterEvent('OnCharacterCreationStep', self.stepID, toStep)

    @property
    def stepID(self):
        return self._stepID

    @stepID.setter
    def stepID(self, newStepID):
        self._stepID = newStepID
        self.UpdateButtonAnalyticIDs(newStepID)

    def UpdateButtonAnalyticIDs(self, newStepID):
        self.backBtn.analyticID = BACK_BUTTON_ANALYTIC_ID % newStepID
        self.approveBtn.analyticID = NEXT_BUTTON_ANALYTIC_ID % newStepID

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
        self.approveBtn.Show()
        self.backBtn.Show()
        isGoingToFinalStep = toStep == self.availableSteps[-1]
        if toStep == ccConst.EMPIRESTEP:
            self.approveBtn.state = uiconst.UI_HIDDEN
            self.finalizeBtn.state = uiconst.UI_HIDDEN
            self.saveBtn.state = uiconst.UI_HIDDEN
        elif isGoingToFinalStep:
            self.approveBtn.state = uiconst.UI_HIDDEN
            isNewChar = self._activeCharID in (ccConst.DEFAULT_CHAR_ID, ccConst.SPARE_CHAR_ID)
            if isNewChar:
                self.finalizeBtn.state = uiconst.UI_HIDDEN
                self.saveBtn.state = uiconst.UI_HIDDEN
            else:
                self.finalizeBtn.state = uiconst.UI_HIDDEN
                self.saveBtn.state = uiconst.UI_NORMAL
        elif toStep == ccConst.DOLLSTEP:
            self.finalizeBtn.state = uiconst.UI_HIDDEN
            self.saveBtn.state = uiconst.UI_HIDDEN
            self.approveBtn.state = uiconst.UI_HIDDEN
        else:
            self.approveBtn.state = uiconst.UI_NORMAL
            self.finalizeBtn.state = uiconst.UI_HIDDEN
            self.saveBtn.state = uiconst.UI_HIDDEN

    def _HideBackButtonIfNoCharacters(self):
        if not sm.GetService('cc').GetCharactersToSelect():
            self.backBtn.Hide()

    def StartStep(self, toStep):
        self.stepLogger.SetStep(toStep)
        if toStep == ccConst.EMPIRESTEP:
            self.StartEmpireSelectionStep()
        elif toStep == ccConst.CUSTOMIZATIONSTEP:
            self.StartCustomizationStep()
        elif toStep == ccConst.PORTRAITSTEP:
            self.StartPortraitStep()
        elif toStep == ccConst.NAMINGSTEP:
            self.StartNamingStep()
        elif toStep == ccConst.DOLLSTEP:
            self.StartDollSelectionStep()
        else:
            raise NotImplementedError()

    def StartEmpireSelectionStep(self):
        self.dollSelected = False
        self.raceID = None
        self.schoolID = None
        self.step = EmpireSelectionStep(parent=self.mainCont)
        charCreationSignals.onEmpireFactionButtonClicked.connect(self.OnEmpireFactionButtonClicked)
        charCreationSignals.onEmpireSchoolButtonClicked.connect(self.SelectSchool)
        charCreationSignals.onEmpireSchoolSelected.connect(self.OnEmpireSchoolSelected)

    def OnEmpireFactionSelected(self, factionID):
        if self.sceneManager.avatarScene is not None:
            self._dollsDirty = True

    def OnEmpireFactionButtonClicked(self, factionID):
        raceID = appConst.raceByFaction[factionID]
        if raceID != self.raceID:
            self.SelectRace(raceID)
        self.PlayFactionSelectionSound(factionID)

    def PlayFactionSelectionSound(self, factionID):
        soundPath = ''
        if factionID == appConst.factionCaldariState:
            soundPath = soundConst.CALDARI_SELECTION_LOOP
        elif factionID == appConst.factionAmarrEmpire:
            soundPath = soundConst.AMARR_SELECTION_LOOP
        elif factionID == appConst.factionGallenteFederation:
            soundPath = soundConst.GALLENTE_SELECTION_LOOP
        elif factionID == appConst.factionMinmatarRepublic:
            soundPath = soundConst.MINMATAR_SELECTION_LOOP
        if not soundPath:
            return
        PlaySound(soundPath)

    def StopFactionSelectionSound(self):
        factionID = appConst.factionByRace.get(self.raceID, None)
        soundPath = ''
        if factionID == appConst.factionCaldariState:
            soundPath = soundConst.CALDARI_SELECTION_LOOP_STOP
        elif factionID == appConst.factionAmarrEmpire:
            soundPath = soundConst.AMARR_SELECTION_LOOP_STOP
        elif factionID == appConst.factionGallenteFederation:
            soundPath = soundConst.GALLENTE_SELECTION_LOOP_STOP
        elif factionID == appConst.factionMinmatarRepublic:
            soundPath = soundConst.MINMATAR_SELECTION_LOOP_STOP
        if not soundPath:
            return
        PlaySound(soundPath)

    def OnEmpireSchoolSelected(self, schoolID):
        if schoolID:
            self.AnimShowApproveButton()
        else:
            self.approveBtn.Hide()

    def OnDollSelectionDollClicked(self, charID):
        if charID is not None:
            self.SelectDoll(charID)

    def AnimShowApproveButton(self):
        self.approveBtn.state = uiconst.UI_NORMAL
        animations.FadeTo(self.approveBtn, 0.0, 1.0, duration=0.3, timeOffset=1.0, callback=self.approveBtn.Enable)

    def IsNamingStep(self, step):
        return step == ccConst.NAMINGSTEP

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
        if toStep == ccConst.CUSTOMIZATIONSTEP and (self.raceID is None or self.GetActiveCharacterData().bloodlineID is None or self.GetActiveCharacterData().genderID is None):
            raise UserError('CCMustSelectRaceAndBloodline')
        isNamingStep = self.IsNamingStep(toStep)
        if (toStep == ccConst.PORTRAITSTEP or isNamingStep) and not prefs.GetValue('ignoreCCValidation', False):
            info = self.GetInfo()
            self.dollManager.ToggleClothes(forcedValue=0)
            self.characterSvc.ValidateDollCustomizationComplete(info.charID)
        currentStepID = None
        if self.step:
            currentStepID = self.step.stepID
        if self.step:
            self.step.ValidateStepComplete()
        return True

    @telemetry.ZONE_METHOD
    def Approve(self, skipCustomization = True, *args):
        if not self.approve_in_progress:
            self.PlayApprovalSound()
            self.approve_in_progress = True
            self.stepLogger.IncrementNextTryCount()
            idx = self.availableSteps.index(self.stepID)
            try:
                if len(self.availableSteps) > idx + 1:
                    if self.stepID == ccConst.DOLLSTEP:
                        self.customizationStepSkipped = skipCustomization
                        if skipCustomization and len(self.availableSteps) > idx + 2:
                            nextStep = self.availableSteps[idx + 2]
                        else:
                            nextStep = self.availableSteps[idx + 1]
                    else:
                        nextStep = self.availableSteps[idx + 1]
                    self.SwitchStep(nextStep)
                    uicore.registry.SetFocus(self)
            finally:
                self.approve_in_progress = False

    def PlayApprovalSound(self):
        if self.stepID == ccConst.CUSTOMIZATIONSTEP:
            PlaySound(soundConst.CUSTOMIZATION_CONFIRMATION)
        else:
            PlaySound(soundConst.NEXT_STEP)

    @telemetry.ZONE_METHOD
    def GoToCustomization(self, *args):
        self.Approve(skipCustomization=False)

    @telemetry.ZONE_METHOD
    def RandomizeSelectedDoll(self, *args):
        if self.dollSelected:
            charCreationSignals.onDollSelectionRandomizeStarting(self._activeCharID)
            self.RandomizeCharacter(self._activeCharID, True)
            doll = self.characterSvc.GetSingleCharactersDoll(self._activeCharID)
            while doll.busyUpdating:
                blue.synchro.Yield()

            charCreationSignals.onDollSelectionDollRandomized(self._activeCharID)

    def OnDollRandomizeStarting(self, charID):
        self.backBtn.state = uiconst.UI_DISABLED

    def OnDollRandomized(self, charID):
        self.backBtn.state = uiconst.UI_NORMAL

    def RandomizeCharacter(self, charID = None, fullRandomize = False):
        if charID is None:
            charID = self._activeCharID
        doll = self.characterSvc.GetSingleCharactersDoll(charID)
        if doll.busyUpdating:
            return
        self.LockNavigation()
        PlaySound(soundConst.RANDOMIZE)
        if fullRandomize:
            self.RerollCharacter(charID)
        else:
            self.dollManager.ToggleClothes(forcedValue=0)
            if self._characterData[charID].genderID == ccConst.GENDERID_FEMALE:
                itemList = ccConst.femaleRandomizeItems.keys()
            else:
                itemList = ccConst.maleRandomizeItems.keys()
            canChangeBaseAppearance = self.CanChangeBaseAppearance()
            blacklist = ccConst.randomizerCategoryBlacklist[:]
            if not canChangeBaseAppearance:
                blacklist += ccConst.recustomizationRandomizerBlacklist
            if boot.region == 'optic' and self._characterData[charID].genderID == ccConst.GENDERID_FEMALE:
                blacklist.append(ccConst.scarring)
            categoryList = []
            for item in itemList:
                if item not in blacklist:
                    categoryList.append(item)

            self.characterSvc.RandomizeCharacterGroups(charID, self.raceID, categoryList, doUpdate=False, fullRandomization=True)
            if canChangeBaseAppearance:
                self.characterSvc.RandomizeCharacterSculpting(charID, self.raceID, doUpdate=False)
            decalModifiers = doll.buildDataManager.GetModifiersByCategory(ccConst.tattoo)
            for modifier in decalModifiers:
                modifier.IsDirty = True

        self.characterSvc.UpdateDoll(charID, 'RandomizeCharacter')
        self.UnlockNavigation()

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
                selectedPortraitInfo = self.portraitManager.GetActivePortraitInfo()
                if selectedPortraitInfo and selectedPortraitInfo.backgroundID < const.NCC_MIN_NORMAL_BACKGROUND_ID:
                    eve.Message('CustomInfo', {'info': localization.GetByLabel('UI/CharacterCreation/CannotSaveWithThisBackground')})
                    return
                self.LockEverything()
                if self.step:
                    self.step.ValidateStepComplete()
                if self.stepID != self.availableSteps[-1]:
                    raise UserError('CCCannotSave')
                if self._activeCharID is not None and self.modeObject.AskForPortraitConfirmation():
                    self.UpdateExistingCharacter()
                    return
                if self.GetActiveCharacterData().bloodlineID is None or self.GetActiveCharacterData().genderID is None:
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
        PlaySound(soundConst.FINALIZE)
        charID = self.SaveCurrentCharacter(characterName, self.portraitManager.activePortraitIndex)
        self.metrics.complete_cc(charid=charID)
        if charID:
            self.characterSvc.CachePortraitInfo(charID, self.portraitManager.GetActivePortraitInfo())
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
        self.StopFactionSelectionSound()

    @telemetry.ZONE_METHOD
    def Back(self, *args):
        idx = self.availableSteps.index(self.stepID)
        if idx == 0:
            self.CancelCharacterCreation()
        else:
            if self.stepID == ccConst.NAMINGSTEP and self.customizationStepSkipped and idx > 1:
                nextStep = self.availableSteps[idx - 2]
            else:
                nextStep = self.availableSteps[idx - 1]
            PlaySound(soundConst.PREVIOUS_STEP)
            self.SwitchStep(nextStep)
            uicore.registry.SetFocus(self)

    @telemetry.ZONE_METHOD
    def LockEverything(self, *args):
        if not getattr(self, 'setupDone', 0):
            return
        containers = [self, self.topNavigationContainer]
        for container in containers:
            container.pickState = uiconst.TR2_SPS_OFF

        self.LockNavigation()

    @telemetry.ZONE_METHOD
    def LockNavigation(self, *args):
        if not getattr(self, 'setupDone', 0):
            return
        self.buttonNavRight.state = uiconst.UI_DISABLED
        self.buttonNavLeft.state = uiconst.UI_DISABLED

    @telemetry.ZONE_METHOD
    def UnlockEverything(self, *args):
        containers = [self, self.topNavigationContainer]
        for container in containers:
            container.pickState = uiconst.TR2_SPS_CHILDREN

        self.UnlockNavigation()

    @telemetry.ZONE_METHOD
    def UnlockNavigation(self, *args):
        if not self.parent.isopen:
            return
        self.buttonNavRight.state = uiconst.UI_PICKCHILDREN
        self.buttonNavLeft.state = uiconst.UI_PICKCHILDREN

    @telemetry.ZONE_METHOD
    def SelectRaceIfDifferent(self, raceID, check = 1):
        if self.raceID != raceID:
            self._ChangeRace(raceID)
        self._UpdateResourcePriority(raceID)

    @telemetry.ZONE_METHOD
    def SelectRace(self, raceID):
        self._ChangeRace(raceID)
        self._UpdateResourcePriority(raceID)
        charCreationSignals.onEmpireFactionSelected(appConst.factionByRace[raceID])

    def _ChangeRace(self, raceID):
        self.ClearSteps(what='race')
        self.dollManager.ResetClothesStorage()
        self.raceID = raceID
        if hasattr(self.step, 'OnRaceSelected'):
            self.step.OnRaceSelected(raceID)
        self.portraitManager.UpdateBackdrop()

    def _GetRandomRaceID(self):
        return random.choice(CHARACTER_CREATION_RACE_IDS)

    def _UpdateResourcePriority(self, raceID):
        raceAsString = RACE_TO_RESOURCE_NAME.get(raceID, None)
        if raceAsString:
            everesourceprefetch.ScheduleFront('interior_' + raceAsString)
            everesourceprefetch.ScheduleFront('bloodline_select_' + raceAsString)

    @telemetry.ZONE_METHOD
    def SelectBloodline(self, bloodlineID):
        if self.GetActiveCharacterData().bloodlineID != bloodlineID:
            self.ClearSteps(what='bloodline')
            if self.stepID == ccConst.CUSTOMIZATIONSTEP:
                uthread.new(self._SwitchBloodlines, bloodlineID, fadeout=True)
            self.dollManager.ResetClothesStorage()

    def _SwitchBloodlines(self, bloodlineID, fadeout = False, resetToFace = False):
        if fadeout:
            self.FadeToBlack(why=localization.GetByLabel('UI/Common/Loading'))
        self.characterSvc.StopEditing()
        self.LockEverything()
        genderID = self.GetActiveCharacterData().genderID
        appearanceInfo = self.characterSvc.CopyCharacterAppearanceInfoForBloodline(self._activeCharID)
        self.SetActiveBloodline(bloodlineID)
        self.characterSvc.RemoveCharacter(self._activeCharID)
        self.AddCharacter(self._activeCharID, bloodlineID, self.raceID, genderID, dna=appearanceInfo)
        doll = self.characterSvc.GetSingleCharactersDoll(self._activeCharID)
        while doll.busyUpdating:
            blue.synchro.Yield()

        self.sceneManager.camera.UpdateAvatar(self.characterSvc.GetSingleCharactersAvatar(self._activeCharID))
        self.step.ReloadTattooMenu()
        self.step.GoToAssetMode(forcedMode=1)
        if resetToFace:
            if hasattr(self.step, 'LoadFaceMode'):
                uthread.new(self.step.LoadFaceMode)
        self.UnlockEverything()
        if fadeout:
            self.FadeFromBlack()

    @telemetry.ZONE_METHOD
    def SelectBloodlineAndGender(self, bloodlineID, genderID, check = 1):
        isBloodlineChanged = self.GetActiveCharacterData().bloodlineID != bloodlineID
        isGenderChanged = self.GetActiveCharacterData().genderID != genderID
        self.WarnOfUnsavedChanges(check, isBloodlineChanged, isGenderChanged)
        if isBloodlineChanged or isGenderChanged:
            self.ClearSteps(what='bloodline')
        self.SetActiveBloodline(bloodlineID)
        self.SetActiveGender(genderID)
        self.dollManager.ResetClothesStorage()
        if getattr(self.step, 'sr') and getattr(self.step.sr, 'historySlider'):
            self.step.sr.historySlider.LoadHistory(0)

    def SelectRandomBloodline(self):
        bloodlineIDs = [1,
         2,
         3,
         4,
         5,
         6,
         7,
         8,
         11,
         12,
         13,
         14]
        return random.choice(bloodlineIDs)

    def SelectRandomGender(self):
        genderIDs = [0, 1]
        return random.choice(genderIDs)

    def WarnOfUnsavedChanges(self, check, isBloodlineChanged, isGenderChanged):
        isBloodlineUnsaved = isBloodlineChanged and self.GetActiveCharacterData().bloodlineID is not None
        isGenderUnsaved = isGenderChanged and self.GetActiveCharacterData().genderID is not None
        areThereUnsavedChanges = isBloodlineUnsaved or isGenderUnsaved
        isCustomized = self.stepID == ccConst.CUSTOMIZATIONSTEP and ccConst.CUSTOMIZATIONSTEP in self.stepsUsed
        shouldWarn = check and areThereUnsavedChanges and isCustomized
        if shouldWarn:
            dnaLog = self.dollManager.GetDollDNAHistory()
            if dnaLog and len(dnaLog) > 1:
                message = 'CharCreationLoseChangeBloodline' if isBloodlineUnsaved else 'CharCreationLoseChangeGender'
                if eve.Message(message, {}, uiconst.YESNO) != uiconst.ID_YES:
                    return

    @telemetry.ZONE_METHOD
    def SelectSchool(self, schoolID):
        if schoolID == self.schoolID:
            return
        if self.finalStepLogger:
            self.finalStepLogger.SetSchool(schoolID)
        self.schoolID = schoolID
        uicore.layer.charactercreation.controller.metrics.pick_school(schoolID)
        charCreationSignals.onEmpireSchoolSelected(schoolID)

    @telemetry.ZONE_METHOD
    def OnDollUpdated(self, charID, redundantUpdate, fromWhere, *args):
        if fromWhere in ('AddCharacter', 'OnSetDevice', 'InitAvatarPositions_Naming'):
            return
        self.ClearSteps(what='dollUpdated')

    @telemetry.ZONE_METHOD
    def OnGraphicSettingsChanged(self, changes):
        shouldGoBack = False
        if gfxsettings.GFX_CHAR_FAST_CHARACTER_CREATION in changes:
            header = localization.GetByLabel('UI/CharacterCreation/LoseChangesHeader')
            text = localization.GetByLabel('UI/CharacterCreation/LoseChanges')
            if eve.Message('CustomQuestion', {'header': header,
             'question': text}, uiconst.YESNO) == uiconst.ID_YES:
                self.sceneManager.avatarScene = None
                shouldGoBack = True
            else:
                gfxsettings.Set(gfxsettings.GFX_CHAR_FAST_CHARACTER_CREATION, 0, pending=False)
        if shouldGoBack:
            if self._activeCharID is not None:
                trinity.WaitForResourceLoads()
                self.ExitToStation()
            else:
                sm.GetService('cc').GoBack()
        if gfxsettings.UI_NCC_GREEN_SCREEN in changes:
            self.portraitManager.UpdateBackdrop()
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
        self.sceneManager.TearDown()
        self.portraitManager.TearDown()
        self.dollManager.TearDown()
        self.freezingAnimation = False
        self.dollSelected = False
        self.customizationStepSkipped = False

    @telemetry.ZONE_METHOD
    def StartDollSelectionStep(self, *args):
        self.customizationStepSkipped = False
        info = self.GetInfo()
        self.sceneManagerSvc.Show2DBackdropScene()
        self.SetupSceneAndCharacter(extraDoll=True)
        avatar = self.characterSvc.GetSingleCharactersAvatar(info.charID)
        if avatar is not None:
            network = animparams.GetParamsPerAvatar(avatar, info.charID)
            network.SetControlParameter('ControlParameters|NetworkMode', NETWORKMODE_BASIC)
            self.sceneManager.SetupCamera(avatar, ccConst.CAMERA_MODE_BODY, callback=self.CameraMoveCB, frontClip=0.1, backClip=100.0, controlStyle=CONTROL_NONE)
        self.sceneManager.SetTwoDollsLighting()
        charCreationSignals.onDollSelectionDollClicked.connect(self.OnDollSelectionDollClicked)
        characterIDs = sorted([self._activeCharID, self._spareCharID])
        self.step = CharacterDollSelection(parent=self.mainCont, characterIDs=characterIDs, selectedCharacterID=self._activeCharID)
        self.step.InitAvatarPositions()
        self.sceneManager.scene.SetupShadowMaps()

    @telemetry.ZONE_METHOD
    def StartCustomizationStep(self, *args):
        info = self.GetInfo()
        self.sceneManagerSvc.Show2DBackdropScene()
        self.SetupSceneAndCharacter()
        avatar = self.characterSvc.GetSingleCharactersAvatar(info.charID)
        if avatar is not None:
            network = animparams.GetParamsPerAvatar(avatar, info.charID)
            network.SetControlParameter('ControlParameters|NetworkMode', NETWORKMODE_BASIC)
            self.sceneManager.SetupCamera(avatar, ccConst.CAMERA_MODE_FACE, callback=self.CameraMoveCB, frontClip=0.1, backClip=100.0)
        self.sceneManager.SetSingleDollLighting()
        self.step = CharacterCustomization(parent=self.mainCont)
        self.step.InitAvatarPositions()
        if self.CanChangeBaseAppearance():
            self.StartEditMode(showPreview=True, callback=self.step.ChangeSculptingCursor)
        self.sceneManager.camera.ToggleMode(ccConst.CAMERA_MODE_FACE, avatar=avatar, transformTime=500.0)
        self.sceneManager.scene.SetupShadowMaps()

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
    def StartPortraitStep(self):
        info = self.GetInfo()
        if not self.portraitManager.alreadyLoadedOldPortraitData:
            if self.modeObject.GetOldPortraitData():
                self.portraitManager.FetchOldPortraitData(info.charID)
        self.step = CharacterPortrait(parent=self.mainCont)
        self.SetupSceneAndCharacter()
        avatar = self.characterSvc.GetSingleCharactersAvatar(info.charID)
        if avatar is not None and avatar.animationUpdater is not None:
            network = animparams.GetParamsPerAvatar(avatar, info.charID)
            network.SetControlParameter('ControlParameters|NetworkMode', NETWORKMODE_PORTRAIT)
        self.sceneManager.SetupForPortraitStep(avatar)
        self.characterSvc.StartPosing(charID=info.charID, callback=self.step.ChangeSculptingCursor)

    @telemetry.ZONE_METHOD
    def StartNamingStep(self, *args):
        info = self.GetInfo()
        avatar = self.characterSvc.GetSingleCharactersAvatar(info.charID)
        self.SetupSceneAndCharacter()
        self.sceneManager.SetUpNamingStepCamera(self.characterSvc.GetSingleCharactersAvatar(info.charID))
        self.SetAvatarAnimationNetworkMode(NETWORKMODE_PORTRAIT)
        while not self.characterSvc.sculpting:
            blue.synchro.Yield()

        self.sceneManager.SetupCamera(avatar, ccConst.CAMERA_MODE_PORTRAIT, callback=self.CameraMoveCB)
        self.sceneManager.camera.Update()
        self.sceneManager.SetSingleDollCloseupLighting(self.GetInfo().genderID)
        self.step = CharacterNaming(parent=self.mainCont)
        self.step.InitAvatarPositions()
        doll = self.characterSvc.GetSingleCharactersDoll(info.charID)
        while doll.busyUpdating:
            blue.synchro.Yield()

        self.portraitManager.SetBackdrop(random.choice(ccConst.defaultBackgroundOptions))
        self.CapturePortrait(0)
        self.sceneManager.SetUpNamingStepCamera(self.characterSvc.GetSingleCharactersAvatar(info.charID))
        self.sceneManager.SetupCamera(avatar, ccConst.CAMERA_MODE_FACE)
        self.SetAvatarAnimationNetworkMode(NETWORKMODE_BASIC)
        charCreationSignals.onNameInputChanged.connect(self.OnNameInputChanged)

    def OnNameInputChanged(self, isValidName):
        if isValidName:
            if not self.saveBtn.display:
                self.saveBtn.Show()
                animations.FadeTo(self.saveBtn, 0.0, 1.0, duration=0.3)
        else:
            self.saveBtn.Hide()

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
        if self.stepID is None:
            return
        stepAlreadyCleared = getattr(self.step, 'stepAlreadyCleared', 0)
        if not force and stepAlreadyCleared:
            return
        currentStepID = self.stepID
        currentStepOrder = GetStepOrder(currentStepID)
        if currentStepOrder <= GetStepOrder(ccConst.CUSTOMIZATIONSTEP):
            self.portraitManager.ClearFacePortrait()
        firstStep = self.availableSteps[0]
        self.stepsUsed = GetStepsUpToAndIncluding(currentStepID) or {firstStep}
        if self.step:
            self.step.stepAlreadyCleared = 1

    @telemetry.ZONE_METHOD
    def Cleanup(self):
        self.characterSvc.StopEditing()
        info = self.GetInfo()
        charID = info.charID
        if charID in self.characterSvc.characters:
            self.characterSvc.StopPosing(charID)
        self.sceneManager.Cleanup()
        self.portraitManager.Cleanup()

    def SelectDoll(self, charID):
        if charID != self._activeCharID:
            self._spareCharID = self._activeCharID
            self._activeCharID = charID
        self.dollManager.ClearDnaLog()
        charCreationSignals.onDollSelectionDollSelected(charID)
        self.dollSelected = True

    @telemetry.ZONE_METHOD
    def SetupSceneAndCharacter(self, extraDoll = False):
        createExtraDoll = self.mode == ccConst.MODE_FULLINITIAL_CUSTOMIZATION
        if not createExtraDoll:
            extraDoll = False
        info = self.GetInfo()
        charA = min(self._activeCharID, self._spareCharID)
        charB = max(self._activeCharID, self._spareCharID)
        if self.sceneManager.SetAvatarScene(info):
            self.AddCharacter(self._activeCharID, info.bloodlineID, info.raceID, info.genderID, dna=info.dna)
            if createExtraDoll:
                spareBloodlineID = self.SelectRandomBloodline()
                spareGenderID = 1 - info.genderID
                self._characterData[self._spareCharID].bloodlineID = spareBloodlineID
                self._characterData[self._spareCharID].genderID = spareGenderID
                self.AddCharacter(self._spareCharID, spareBloodlineID, self.raceID, spareGenderID, dna=info.dna)
        elif self._dollsDirty:
            self.RerollCharacter(self._activeCharID, cameraUpdate=False)
            self.RerollCharacter(self._spareCharID, cameraUpdate=False)
            self._dollsDirty = False
        elif extraDoll:
            avatarA = self.characterSvc.GetSingleCharactersAvatar(charA)
            avatarA.display = True
            avatarB = self.characterSvc.GetSingleCharactersAvatar(charB)
            avatarB.display = True
        else:
            avatarA = self.characterSvc.GetSingleCharactersAvatar(self._activeCharID)
            avatarA.display = True
            if createExtraDoll:
                avatarB = self.characterSvc.GetSingleCharactersAvatar(self._spareCharID)
                avatarB.display = False
        self.BlockOnUpdate()

    @telemetry.ZONE_METHOD
    def AddCharacter(self, charID, bloodlineID, raceID, genderID, scene = None, dna = None, validateColors = True, position = (0.0, 0.0, 0.0)):
        self.dollManager.AddCharacter(charID, bloodlineID, raceID, genderID, scene or self.sceneManager.scene, dna, validateColors, position=position)

    @telemetry.ZONE_METHOD
    def RerollCharacter(self, charID, cameraUpdate = True):
        self.characterSvc.RemoveCharacter(charID)
        bloodlineID = self.SelectRandomBloodline()
        self.dollManager.AddCharacter(charID, bloodlineID, self.raceID, self._characterData[charID].genderID, self.sceneManager.scene, None, True)
        if self.step and hasattr(self.step, 'InitAvatarPositions'):
            self.step.InitAvatarPositions()
        doll = self.characterSvc.GetSingleCharactersDoll(charID)
        while doll.busyUpdating:
            blue.synchro.Yield()

        if cameraUpdate:
            self.sceneManager.camera.UpdateAvatar(self.characterSvc.GetSingleCharactersAvatar(charID))

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
    def SetRandomHairDarkness(self, doUpdate = True):
        self.SetHairDarkness(random.random(), doUpdate=doUpdate)

    @telemetry.ZONE_METHOD
    def SetHairDarkness(self, darkness, doUpdate = True):
        info = self.GetInfo()
        self.characterSvc.SetHairDarkness(info.charID, darkness)
        if doUpdate:
            sm.GetService('character').UpdateDoll(info.charID, fromWhere='SetHairDarkness')

    @telemetry.ZONE_METHOD
    def SaveCurrentCharacter(self, charactername, portraitID):
        total = 3
        sm.GetService('loading').ProgressWnd(localization.GetByLabel('UI/CharacterCreation/Registering'), localization.GetByLabel('UI/CharacterCreation/CompilePrefs'), 1, total)
        try:
            if self.portraitManager.portraitInfo[portraitID] is None:
                raise UserError('CharCreationNoPortrait')
            info = self.GetInfo()
            charInfo = self.characterSvc.GetCharacterAppearanceInfo(info.charID)
            data = self.GetActiveCharacterData()
            charID = sm.GetService('cc').CreateCharacterWithDoll(charactername, data.bloodlineID, data.genderID, appConst.ancestryUndefined, charInfo, self.portraitManager.portraitInfo[portraitID], info.schoolID, info.raceID)
        except UserError as what:
            if not what.msg.startswith('CharNameInvalid'):
                eve.Message(*what.args)
                return
            sm.GetService('loading').ProgressWnd(localization.GetByLabel('UI/CharacterCreation/Registering'), localization.GetByLabel('UI/CharacterCreation/FailedForSomeReason'), 3, total)
        except RuntimeError as e:
            logger.error('Failed to create character: %s' % e)
            sm.GetService('loading').ProgressWnd(localization.GetByLabel('UI/CharacterCreation/Registering'), localization.GetByLabel('UI/CharacterCreation/FailedForSomeReason'), 3, total)
        else:
            sm.GetService('loading').ProgressWnd(localization.GetByLabel('UI/CharacterCreation/Registering'), localization.GetByLabel('UI/CharacterCreation/InsertingRecord'), 2, total)
            sm.GetService('photo').AddPortrait(self.portraitManager.GetPortraitSnapshotPath(portraitID), charID)
            sm.GetService('loading').ProgressWnd(localization.GetByLabel('UI/CharacterCreation/Registering'), localization.GetByLabel('UI/Generic/Done'), 3, total)
            return charID
        finally:
            self.sessionSounds = []

    @telemetry.ZONE_METHOD
    def UpdateExistingCharacter(self, *args):
        charID = self._activeCharID
        activePortraitInfo = self.portraitManager.GetActivePortraitInfo()
        if activePortraitInfo is None:
            raise UserError('CharCreationNoPortrait')
        dollExists = self._characterData[charID].dna is not None
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
        info = self.GetInfo()
        if self.mode == ccConst.MODE_FULL_RECUSTOMIZATION:
            sm.GetService('cc').UpdateExistingCharacterBloodline(charID, info.bloodlineID, False)
            sm.GetService('cc').UpdateExistingCharacterFull(charID, dollInfo, activePortraitInfo, dollExists, flush=True)
        elif self.mode == ccConst.MODE_LIMITED_RECUSTOMIZATION:
            sm.GetService('cc').UpdateExistingCharacterLimited(charID, dollInfo, activePortraitInfo, dollExists)
        elif self.mode == ccConst.MODE_FULL_BLOODLINECHANGE:
            sm.GetService('cc').UpdateExistingCharacterBloodline(charID, info.bloodlineID, True)
        sm.GetService('photo').AddPortrait(self.portraitManager.GetPortraitSnapshotPath(self.portraitManager.activePortraitIndex), charID)
        self.characterSvc.CachePortraitInfo(self._activeCharID, self.portraitManager.GetActivePortraitInfo())
        self.metrics.complete_cc(charid=charID)
        if self.dollState != paperdoll.State.force_recustomize:
            self.ExitToStation()
        else:
            uthread.pool('GameUI::ActivateView::charsel', sm.GetService('viewState').ActivateView, 'charsel')

    @telemetry.ZONE_METHOD
    def StartEditMode(self, callback = None, **kwds):
        if callback is None and kwds.get('mode', None) == 'sculpt':
            callback = getattr(self.step, 'ChangeSculptingCursor', None)
        info = self.GetInfo()
        self.characterSvc.StartEditMode(info.charID, self.sceneManager.scene, self.sceneManager.camera, callback=callback, **kwds)

    @telemetry.ZONE_METHOD
    def UpdateBackdropLite(self, raceID, mouseEnter = False, *args):
        bdScene = self.sceneManagerSvc.Get2DBackdropScene()
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

    @telemetry.ZONE_METHOD
    def CapturePortrait(self, portraitID, *args):
        if self.sceneManager.camera is None:
            return
        poseData = self.characterSvc.GetPoseData()
        if poseData is None:
            return
        return self.portraitManager.CapturePortrait(portraitID, self.sceneManager.camera, poseData, self.sceneManager.lightingID, self.sceneManager.lightColorID, self.sceneManager.GetLightIntensity())

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
            character = self.characterSvc.GetSingleCharacter(self._activeCharID)
            for mod in modifiersToRemove:
                modifiers = self.characterSvc.GetModifiersByCategory(self._activeCharID, mod)
                for m in modifiers:
                    character.GetDoll(self._activeCharID).buildDataManager.RemoveModifier(m)
                    self.characterSvc.RemoveFromCharacterMetadata(self._activeCharID, mod)

            self.bodyModRemoved = 1
            sm.GetService('character').UpdateDollsAvatar(character)
        except Exception:
            pass

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
            try:
                currentIndex, _ = self.step.historySlider.GetCurrentIndexAndMaxIndex()
                self.dollManager.TryStoreDna(lastUpdateRedundant, currentIndex, self._activeCharID, force=force, allowRedundant=allowReduntant)
            except:
                pass

    @telemetry.ZONE_METHOD
    def PassMouseEventToSculpt(self, type, x, y):
        if not hasattr(self, 'characterSvc'):
            return
        if self.dollManager.GetDoll(self._activeCharID) and self.dollManager.GetDoll(self._activeCharID).IsBusyUpdating():
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
        if self.stepID == ccConst.PORTRAITSTEP:
            info = self.GetInfo()
            self.portraitManager.AnimateToStoredPortrait(newPortraitID, info.charID)

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
