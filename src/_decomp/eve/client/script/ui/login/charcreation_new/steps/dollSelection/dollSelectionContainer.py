#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\login\charcreation_new\steps\dollSelection\dollSelectionContainer.py
import localization
import trinity
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui import uiconst
from carbonui.control.button import Button
from carbonui.primitives.boundingboxbracket import BoundingBoxBracket
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.frame import Frame
from carbonui.primitives.transform import Transform
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from charactercreator.const import CUSTOMIZATION_BUTTON_ANALYTIC_ID, RANDOMIZATION_BUTTON_ANALYTIC_ID
from eve.client.script.ui.login.charcreation_new import charCreationSignals, soundConst
from eve.client.script.ui.login.charcreation_new.charCreationSignals import onDollSelectionRandomizeStarting, onDollSelectionDollRandomized, onDollSelectionDollHovered, onDollSelectionDollClicked
from eve.client.script.ui.login.charcreation_new.loadingWheel import CharacterCreationLoadingWheel
from eve.client.script.ui.login.charcreation_new.sceneManager import GetCharacterCreationSceneManager
from eve.client.script.ui.login.charcreation_new.steps.dollSelection.dollSelectionConst import DURATION_HOVER
from eveexceptions import ExceptionEater
CORNER_FRAME_SCALE_IDLE = (0.95, 0.95)
CORNER_FRAME_SCALE_SELECTED = (1.0, 1.0)
BUTTON_HEIGHT = 35
BUTTON_HEIGHT_PRIMARY = 50
BUTTON_FONT_SIZE = 18

class DollSelectionContainer(BoundingBoxBracket):
    default_screenMargin = 10.0

    def ApplyAttributes(self, attributes):
        super(DollSelectionContainer, self).ApplyAttributes(attributes)
        onDollSelectionRandomizeStarting.connect(self.OnDollRandomizeStarting)
        onDollSelectionDollRandomized.connect(self.OnDollRandomized)
        self.charID = attributes.charID
        self.isSelected = False
        self.ConstructTrackObject()
        charCreationSignals.onDollSelectionDollSelected.connect(self.OnDollSelected)
        self.ConstructLoadingWheel()
        self.mainCont = Container(name='mainCont', align=uiconst.TOPLEFT_PROP, parent=self, pos=(0.5, 30, 0.85, 0.92), maxWidth=260)
        self.ConstructButtons()
        self.ConstructBackground()

    def ConstructButtons(self):
        self.buttonCont = ContainerAutoSize(name='buttonCont', parent=self.mainCont, align=uiconst.TOBOTTOM, state=uiconst.UI_DISABLED, opacity=0)
        self.randomizeDollBtn = Button(name='randomizeDollButtonCC', parent=self.buttonCont, align=uiconst.TOTOP, label=localization.GetByLabel('UI/CharacterCreation/DollSelection/ShuffleCharacter'), func=uicore.layer.charactercreation.controller.RandomizeSelectedDoll, hint=localization.GetByLabel('UI/CharacterCreation/DollSelection/ShuffleCharacterTooltip'), analyticID=RANDOMIZATION_BUTTON_ANALYTIC_ID)
        self.goToCustomizationBtn = Button(name='customizationButtonCC', parent=self.buttonCont, align=uiconst.TOTOP, padTop=15, label=localization.GetByLabel('UI/CharacterCreation/DollSelection/FullCustomization'), func=uicore.layer.charactercreation.controller.GoToCustomization, hint=localization.GetByLabel('UI/CharacterCreation/DollSelection/FullCustomizationTooltip'), analyticID=CUSTOMIZATION_BUTTON_ANALYTIC_ID)
        self.approveBtn = Button(name='nextButtonCC', parent=self.buttonCont, align=uiconst.TOTOP, padTop=30, label=localization.GetByLabel('UI/Agents/Dialogue/Buttons/Continue'), func=uicore.layer.charactercreation.controller.Approve)

    def ConstructBackground(self):
        self.cornerFrameTransform = Transform(name='cornerFrameTransform', parent=self, align=uiconst.TOALL, scale=CORNER_FRAME_SCALE_IDLE, scalingCenter=(0.5, 0.5))
        self.cornersFrame = Frame(parent=self.cornerFrameTransform, opacity=0, texturePath='res:/UI/Texture/classes/CharacterSelection/EmpireSelection/dollSelectionFrameCorners.png', cornerSize=20)
        self.frame = Frame(parent=self, opacity=0, texturePath='res:/UI/Texture/classes/CharacterSelection/EmpireSelection/dollSelectionFrame.png', cornerSize=150)

    def ConstructLoadingWheel(self):
        self.loadingWheel = CharacterCreationLoadingWheel(name='loadingWheel', parent=self, top=-130, align=uiconst.CENTER, state=uiconst.UI_NORMAL)
        self.loadingWheel.forcedOn = 0
        self.loadingWheel.Hide()
        self.loadingWheel.hint = localization.GetByLabel('UI/CharacterCreation/DollSelection/ShuffleCharacterLoadingTooltip')

    def OnDollSelected(self, charID):
        if charID == self.charID:
            self.SetSelected()
        else:
            self.SetDeselected()

    def OnDollRandomizeStarting(self, charID):
        self.buttonCont.state = uiconst.UI_DISABLED
        if charID == self.charID:
            self.loadingWheel.Show()

    def OnDollRandomized(self, charID):
        self.buttonCont.state = uiconst.UI_NORMAL if self.isSelected else uiconst.UI_DISABLED
        if charID == self.charID:
            self.loadingWheel.Hide()

    def SetSelected(self):
        if self.isSelected:
            return
        self.isSelected = True
        duration = 0.2
        animations.Tr2DScaleTo(self.cornerFrameTransform, CORNER_FRAME_SCALE_IDLE, CORNER_FRAME_SCALE_SELECTED, duration=duration)
        animations.FadeIn(self.frame, duration=duration, timeOffset=0.3)
        animations.FadeIn(self.buttonCont, duration=duration, timeOffset=0.6)
        self.buttonCont.Enable()

    def SetDeselected(self):
        self.isSelected = False
        duration = 0.2
        animations.FadeOut(self.buttonCont, duration=duration)
        animations.FadeOut(self.frame, duration=duration)
        animations.Tr2DScaleTo(self.cornerFrameTransform, CORNER_FRAME_SCALE_SELECTED, CORNER_FRAME_SCALE_IDLE, duration=duration)
        self.buttonCont.Disable()

    def ConstructTrackObject(self):
        sceneMan = GetCharacterCreationSceneManager()
        doll = sceneMan.GetDoll(self.charID)
        trackObject = trinity.Load('res:/graphics/interior/charactercreation/plane/plane.red')
        trinity.WaitForResourceLoads()
        trackObject.translation = doll.translation
        trackObject.rotation = (0, 0, 0)
        trackObject.scaling = (1, 1, 1)
        trackObject.display = False
        trackObject.BoundingBoxOverride((-0.4, -0.1, -0.1), (0.4, 1.95, 0.1))
        sceneMan.scene.dynamics.append(trackObject)
        self.trackObject = trackObject

    def Close(self):
        sceneMan = GetCharacterCreationSceneManager()
        with ExceptionEater('characterCreation'):
            sceneMan.scene.dynamics.fremove(self.trackObject)
        self.trackObject = None
        super(DollSelectionContainer, self).Close()

    def OnMouseEnter(self, *args):
        PlaySound(uiconst.SOUND_BUTTON_HOVER)
        onDollSelectionDollHovered(self.charID)
        animations.FadeIn(self.cornersFrame, endVal=1.0, duration=DURATION_HOVER)

    def OnMouseExit(self, *args):
        onDollSelectionDollHovered(None)
        animations.FadeOut(self.cornersFrame, duration=DURATION_HOVER)

    def OnClick(self, *args):
        PlaySound(soundConst.SELECT_BODY)
        onDollSelectionDollClicked(self.charID)
