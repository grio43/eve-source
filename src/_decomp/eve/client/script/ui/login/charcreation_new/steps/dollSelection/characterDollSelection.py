#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\login\charcreation_new\steps\dollSelection\characterDollSelection.py
import blue
import geo2
import carbonui.const as uiconst
import localization
import trinity
import uthread
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from charactercreator import const as ccConst
from eve.client.script.ui.login.charcreation_new import soundConst
import eve.client.script.ui.login.charcreation_new.ccUtil as ccUtil
from eve.client.script.ui.login.charcreation_new.charCreation import BaseCharacterCreationStep
from eve.client.script.ui.login.charcreation_new.dollManager import GetCharacterCreationDollManager
from eve.client.script.ui.login.charcreation_new.sceneManager import GetCharacterCreationSceneManager
from eve.client.script.ui.login.charcreation_new.charCreationSignals import onDollSelectionDollHovered, onDollSelectionDollSelected, onDollSelectionRandomizeStarting, onDollSelectionDollRandomized
from eve.client.script.ui.login.charcreation_new.steps.dollSelection import dollSelectionConst
from eve.client.script.ui.login.charcreation_new.steps.dollSelection.dollSelectionConst import DURATION_HOVER
from eve.client.script.ui.login.charcreation_new.steps.dollSelection.dollSelectionContainer import DollSelectionContainer
from eve.client.script.ui.login.charcreation_new.steps.stepHeader import StepHeader
from localization import GetByLabel

class CharacterDollSelection(BaseCharacterCreationStep):
    __guid__ = 'uicls.CharacterDollSelection'
    __notifyevents__ = ['OnColorPaletteChanged', 'OnHideUI', 'OnShowUI']
    stepID = ccConst.DOLLSTEP

    def ApplyAttributes(self, attributes):
        BaseCharacterCreationStep.ApplyAttributes(self, attributes)
        onDollSelectionRandomizeStarting.connect(self.OnDollRandomizeStarting)
        onDollSelectionDollRandomized.connect(self.OnDollRandomized)
        self.characterIDs = attributes.characterIDs
        self.selectedCharacterID = None
        self.hoveredCharacterID = None
        onDollSelectionDollSelected.connect(self.OnDollSelected)
        onDollSelectionDollHovered.connect(self.OnDollHovered)
        self.header = StepHeader(parent=self, align=uiconst.CENTERTOP, top=60, title=GetByLabel('UI/CharacterCreation/DollSelection/DollSelectionTitle'), subtitle=GetByLabel('UI/CharacterCreation/DollSelection/DollSelectionSubtitle'))
        self.loadingThread = None
        self._StartLoadingThread()
        PlaySound(soundConst.BODY_TYPE_SELECTION_LOOP)

    def _StartLoadingThread(self, charIDsLoading = None):
        if not self.loadingThread:
            self.loadingThread = uthread.new(self.LoadCharactersThread, charIDsLoading=charIDsLoading)

    def OnDoneLoadingCharacters(self):
        self.InitAvatarPositions()
        self.ConstructPickContainers()
        self.AnimEntryLights()

    def ConstructPickContainers(self):
        self.leftSidePickingContainer = DollSelectionContainer(parent=self, charID=self.characterIDs[0], state=uiconst.UI_NORMAL)
        self.rightSidePickingContainer = DollSelectionContainer(parent=self, charID=self.characterIDs[1], state=uiconst.UI_NORMAL)

    def OnDollRandomizeStarting(self, charID):
        self.leftSidePickingContainer.state = uiconst.UI_PICKCHILDREN
        self.rightSidePickingContainer.state = uiconst.UI_PICKCHILDREN

    def OnDollRandomized(self, charID):
        self.leftSidePickingContainer.state = uiconst.UI_NORMAL
        self.rightSidePickingContainer.state = uiconst.UI_NORMAL

    def OnDollHovered(self, characterID):
        self.hoveredCharacterID = characterID
        if characterID == self.characterIDs[0]:
            leftFalloff = 1.5
            rightFalloff = 0.0
        elif characterID:
            leftFalloff = 0.0
            rightFalloff = 1.5
        else:
            leftFalloff = rightFalloff = 0.0
        self.AnimateLightFalloff('LeftSelectionSpotlight', leftFalloff, DURATION_HOVER)
        self.AnimateLightFalloff('RightSelectionSpotlight', rightFalloff, DURATION_HOVER)

    def AnimEntryLights(self):
        duration = 3.0
        timeOffset = 0.2
        if ccUtil.IsSlowMachine():
            FALLOFF_FRONTMAIN = 4.0
        else:
            FALLOFF_FRONTMAIN = 0.6
        FALLOFF_FRONTAMBIENT = 2.5
        self.AnimateLightFalloff('FrontMain', FALLOFF_FRONTMAIN, duration, timeOffset)
        self.AnimateLightFalloff('FrontAmbient', FALLOFF_FRONTAMBIENT, duration, timeOffset)

    def AnimateLightFalloff(self, lightName, value, duration, timeOffset = 0.0):
        light = self.GetLight(lightName)
        if light:
            animations.MorphScalar(light, 'falloff', light.falloff, value, duration=duration, timeOffset=timeOffset)

    def GetLight(self, lightName):
        return GetCharacterCreationSceneManager().GetLightByName(lightName)

    def OnDollSelected(self, characterID):
        self.selectedCharacterID = characterID

    def GetCamera(self):
        ccSceneMan = GetCharacterCreationSceneManager()
        camera = ccSceneMan.camera
        return camera

    def InitAvatarPositions(self):
        characterSvc = sm.GetService('character')
        leftAvatar = self.GetAvatar(self.characterIDs[0])
        leftAvatar.translation = dollSelectionConst.DOLL_POSITION_LEFT
        leftAvatar.rotation = geo2.QuaternionRotationSetYawPitchRoll(dollSelectionConst.DOLL_LEFT_YAW, 0.0, 0.0)
        characterSvc.UpdateDoll(self.characterIDs[0], fromWhere='InitAvatarPositions', forceUpdate=True)
        rightAvatar = self.GetAvatar(self.characterIDs[1])
        rightAvatar.translation = dollSelectionConst.DOLL_POSITION_RIGHT
        rightAvatar.rotation = geo2.QuaternionRotationSetYawPitchRoll(dollSelectionConst.DOLL_RIGHT_YAW, 0.0, 0.0)
        characterSvc.UpdateDoll(self.characterIDs[1], fromWhere='InitAvatarPositions', forceUpdate=True)

    def GetAvatar(self, charID):
        characterSvc = sm.GetService('character')
        return characterSvc.GetSingleCharactersAvatar(charID)

    def LoadCharactersThread(self, charIDsLoading = None, *args):
        if charIDsLoading is None:
            charIDsLoading = self.characterIDs
        layer = uicore.layer.charactercreation.controller
        dolls = (GetCharacterCreationDollManager().GetDoll(charID) for charID in charIDsLoading)
        layer.ShowLoading(why=localization.GetByLabel('UI/CharacterCreation/UpdatingCharacter'))
        isReady = False
        while not self.destroyed and not isReady:
            isReady = all((doll.IsReady() for doll in dolls))
            blue.pyos.synchro.Yield()

        layer.HideLoading()
        self.OnDoneLoadingCharacters()
        self.loadingThread = None

    def Close(self):
        PlaySound(soundConst.BODY_TYPE_SELECTION_LOOP_STOP)
        super(CharacterDollSelection, self).Close()
