#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\login\charcreation\charCreationNavigation.py
import localization
import telemetry
from carbon.common.script.sys.serviceConst import ROLE_PROGRAMMER
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from charactercreator import const as ccConst
from charactercreator.client.characterCreationSteps import GetStepOrder
from eve.client.script.ui import eveColor
from eve.client.script.ui.login.charcreation.label import CCLabel
from eve.client.script.ui.util.uix import GetTextWidth

class CharCreationNavigationElement(Container):
    SHAPE_INACTIVE = 1
    SHAPE_ACTIVE = 2
    SHAPE_LOCKED = 3
    SHAPE_COMPLETED = 4
    SHAPE_INACTIVE_FURTHEST = 5
    SHAPE_ACTIVE_FURTHEST = 6
    default_shape = 1

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        activeShape = attributes.get('shape', self.default_shape)
        self.shapeSprites = {self.SHAPE_ACTIVE: self._CreateSprite('activeSprite', 'res:/UI/Texture/classes/EmpireSelection/navdotFull.png', color=eveColor.PRIMARY_BLUE),
         self.SHAPE_ACTIVE_FURTHEST: self._CreateSprite('activeFurthestSprite', 'res:/UI/Texture/classes/EmpireSelection/navdotFurthest.png', color=eveColor.PRIMARY_BLUE),
         self.SHAPE_COMPLETED: self._CreateSprite('completedSprite', 'res:/UI/Texture/classes/EmpireSelection/navdotFull.png'),
         self.SHAPE_INACTIVE: self._CreateSprite('inactiveSprite', 'res:/UI/Texture/classes/EmpireSelection/navdotFull.png'),
         self.SHAPE_INACTIVE_FURTHEST: self._CreateSprite('inactiveFurthestSprite', 'res:/UI/Texture/classes/EmpireSelection/navdotFurthest.png'),
         self.SHAPE_LOCKED: self._CreateSprite('lockedSprite', 'res:/UI/Texture/classes/EmpireSelection/navdotEmpty.png')}
        self._SetShape(activeShape)

    def _SetShape(self, shape):
        self.activeShape = shape
        for k in self.shapeSprites:
            if k == shape:
                self.shapeSprites[k].state = uiconst.UI_DISABLED
            else:
                self.shapeSprites[k].state = uiconst.UI_HIDDEN

    def Activate(self, furthest = True):
        self._SetShape(self.SHAPE_ACTIVE_FURTHEST if furthest else self.SHAPE_ACTIVE)

    def Complete(self):
        self._SetShape(self.SHAPE_COMPLETED)

    def Deactivate(self, furthest = False):
        self._SetShape(self.SHAPE_INACTIVE_FURTHEST if furthest else self.SHAPE_INACTIVE)

    def Lock(self):
        self._SetShape(self.SHAPE_LOCKED)

    def _CreateSprite(self, name, texturePath, color = None):
        return Sprite(name=name, parent=self, align=uiconst.TOPLEFT, pos=(2, 2, 32, 32), state=uiconst.UI_DISABLED, texturePath=texturePath, color=color)


class CharCreationNavigation(Container):
    default_align = uiconst.TOPLEFT
    default_height = 110
    default_state = uiconst.UI_NORMAL
    ANIMATIONTIME = 500.0
    MOUSEOVEROPACITY = 0.8
    NORMALOPACITY = 0.3
    ACTIVEOPACITY = 1.0
    FONTSIZE = 16
    STEPSIZE = 36
    stepLabelDict = {ccConst.CUSTOMIZATIONSTEP: 'UI/CharacterCreation/Step3',
     ccConst.PORTRAITSTEP: 'UI/CharacterCreation/Step4',
     ccConst.NAMINGSTEP: 'UI/CharacterCreation/Step5',
     ccConst.EMPIRESTEP: 'UI/CharacterCreation/Step7',
     ccConst.TECHNOLOGYSTEP: 'UI/CharacterCreation/Step8',
     ccConst.BLOODLINESTEP: 'UI/CharacterCreation/Step2'}

    @telemetry.ZONE_METHOD
    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.stepID = attributes.stepID
        self.furthestStepID = self.stepID
        self.stepsUsed = attributes.stepsUsed
        self.availableSteps = attributes.availableSteps
        self.stepIndex = {}
        self.navigationElements = {}
        stepIndex = 0
        for stepID in self.availableSteps:
            self.stepIndex[stepIndex] = stepID
            stepIndex += 1

        self.attributesApplied = 0
        self.callbackFunc = attributes.func
        width = len(self.availableSteps) * self.STEPSIZE
        self.width = width
        self.stepCont = Container(name='stepCont', parent=self, align=uiconst.CENTERTOP, pos=(0,
         0,
         width,
         self.STEPSIZE))
        headerContainer = Container(name='headerContainer', parent=self, align=uiconst.TOTOP, top=26, width=width, height=26)
        self.header = CCLabel(name='header', parent=headerContainer, align=uiconst.CENTER, top=0, uppercase=1, letterspace=2, color=(0.9, 0.9, 0.9, 0.8), fontsize=self.FONTSIZE, bold=False, opacity=0.0)
        self.ResetToStep(self.stepID, set(self.stepsUsed))

    def StepIndexToStepId(self, stepindex):
        return self.stepIndex[stepindex]

    def GetNextStepIDForStepID(self, stepID):
        nextStepUpcoming = False
        for i in range(0, len(self.availableSteps)):
            currentStep = self.availableSteps[i]
            if nextStepUpcoming:
                return currentStep
            if currentStep is stepID:
                nextStepUpcoming = True

    def makeConnectors(self):
        left = 20
        connectorFile = 'res:/UI/Texture/classes/EmpireSelection/navdotConnector.png'
        for stepID in self.availableSteps[1:]:
            connectorWidth = 0
            if stepID in self.stepsUsed:
                connectorWidth = 32
            cont = Container(name='space%s' % stepID, parent=self.stepCont, align=uiconst.TOPLEFT, pos=(left,
             10,
             connectorWidth,
             16), state=uiconst.UI_DISABLED, clipChildren=1)
            setattr(self, 'connector%s' % stepID, cont)
            sprite = Sprite(name='connector%s' % stepID, parent=cont, align=uiconst.TOPLEFT, pos=(0, 0, 32, 16), state=uiconst.UI_DISABLED, texturePath=connectorFile)
            sprite.SetAlpha(self.NORMALOPACITY)
            left += self.STEPSIZE

    @telemetry.ZONE_METHOD
    def CreateSteps(self, *args):
        self.stepCont.Flush()
        left = 0
        currentStepOrder = GetStepOrder(self.stepID)
        for stepID in self.availableSteps:
            step = Container(name='step%s' % stepID, parent=self.stepCont, align=uiconst.TOPLEFT, pos=(left,
             0,
             self.STEPSIZE,
             self.STEPSIZE), state=uiconst.UI_DISABLED)
            stepOrder = GetStepOrder(stepID)
            if stepOrder > currentStepOrder:
                shape = CharCreationNavigationElement.SHAPE_LOCKED
            elif stepOrder < currentStepOrder:
                shape = CharCreationNavigationElement.SHAPE_INACTIVE
            else:
                shape = CharCreationNavigationElement.SHAPE_ACTIVE
            self.navigationElements[stepID] = CharCreationNavigationElement(parent=step, shape=shape)
            step.SetOpacity(self.NORMALOPACITY)
            left += self.STEPSIZE
            step.id = stepID
            step.OnMouseEnter = (self.OnStepMouseOver, step)
            step.OnMouseExit = (self.OnStepMouseExit, step)
            step.OnClick = (self.OnStepClicked, step)
            setattr(self, 'step%s' % stepID, step)

        self.stepCont.width = left
        self.makeConnectors()
        self.attributesApplied = 1

    @telemetry.ZONE_METHOD
    def ResetToStep(self, resetToStep, stepsUsed, *args):
        self.stepID = resetToStep
        self.stepsUsed = stepsUsed
        self.CreateSteps()
        firstCont = self.GetStepContainer(self.availableSteps[0])
        firstCont.state = uiconst.UI_NORMAL
        if max(stepsUsed) < 1:
            firstCont.SetOpacity(self.ACTIVEOPACITY)
            secondCont = self.GetStepContainer(self.availableSteps[1])
            secondCont.state = uiconst.UI_NORMAL
        else:
            for stepID in xrange(self.availableSteps[0], resetToStep + 1):
                self.PerformStepChange(stepID, stepsUsed, forceOpen=1, time=0)

        self.stepsUsed.add(resetToStep)

    def GetStepContainer(self, stepID):
        return getattr(self, 'step%s' % stepID, None)

    def GetStepContainerViaGetAttr(self, stepID):
        return getattr(self, 'step%s' % stepID, None)

    def GetConnectorForStep(self, stepID):
        return getattr(self, 'connector%s' % stepID, None)

    def UpdateHeader(self, stepID, opacity):
        labelPath = self.stepLabelDict.get(stepID)
        headerText = localization.GetByLabel(labelPath)
        headerWidth = GetTextWidth(strng=headerText, fontsize=self.FONTSIZE, hspace=2, uppercase=1)
        if headerWidth > self.width:
            self.header.SetAlign(uiconst.CENTERLEFT)
        else:
            self.header.SetAlign(uiconst.CENTER)
        self.header.text = headerText
        self.header.SetAlpha(opacity)

    def _UpdateActiveNavigationElement(self, *args):
        if self.stepID in self.navigationElements:
            stepOrder = GetStepOrder(self.stepID)
            furthestOrder = GetStepOrder(self.furthestStepID)
            self.navigationElements[self.stepID].Activate(furthest=stepOrder >= furthestOrder)

    @telemetry.ZONE_METHOD
    def PerformStepChange(self, stepID, stepsUsed, forceOpen = 0, time = None):
        if not self.attributesApplied:
            return
        if time is None:
            time = self.ANIMATIONTIME
        self.stepID = stepID
        self.stepsUsed = stepsUsed
        furthestOrder = GetStepOrder(self.furthestStepID)
        currentOrder = GetStepOrder(self.stepID)
        if currentOrder > furthestOrder:
            self.furthestStepID = self.stepID
            furthestOrder = GetStepOrder(self.furthestStepID)
        container = self.GetStepContainerViaGetAttr(stepID)
        currentContainerStepID = None
        if container:
            currentContainerStepID = container.id
        stepsUsed = self.stepsUsed.copy()
        try:
            for availableStepID in self.availableSteps:
                connectorFromPreviousStep = self.GetConnectorForStep(availableStepID)
                if availableStepID == stepID:
                    pass
                elif availableStepID in stepsUsed:
                    if connectorFromPreviousStep:
                        connectorFromPreviousStep.width = 32
                    stepOrder = GetStepOrder(availableStepID)
                    if stepOrder > currentOrder:
                        self.navigationElements[availableStepID].Deactivate(furthest=stepOrder == furthestOrder)
                    elif stepOrder < currentOrder:
                        self.navigationElements[availableStepID].Complete()
                else:
                    self.navigationElements[availableStepID].Lock()
                    if connectorFromPreviousStep:
                        connectorFromPreviousStep.width = 0
                cont = self.GetStepContainerViaGetAttr(availableStepID)
                if cont and availableStepID != currentContainerStepID:
                    cont.SetOpacity(self.NORMALOPACITY)

            cont = self.GetStepContainerViaGetAttr(currentContainerStepID)
            if currentContainerStepID not in stepsUsed or forceOpen:
                connector = self.GetConnectorForStep(currentContainerStepID)
                if connector:
                    if time:
                        animations.MorphScalar(connector, 'width', endVal=32, duration=time / 1000.0, sleep=True, callback=self._UpdateActiveNavigationElement)
                    else:
                        self._UpdateActiveNavigationElement()
                        connector.width = 32
                    cont.SetOpacity(self.ACTIVEOPACITY)
                else:
                    self._UpdateActiveNavigationElement()
                nextStepID = self.GetNextStepIDForStepID(currentContainerStepID)
                nextStep = self.GetStepContainer(nextStepID)
                if nextStep:
                    nextStep.state = uiconst.UI_NORMAL
            else:
                self._UpdateActiveNavigationElement()
            if container and not container.destroyed and container.id == self.stepID:
                container.SetOpacity(self.ACTIVEOPACITY)
        except AttributeError as e:
            if self is None or self.destroyed or e.message == 'SetOpacity':
                sm.GetService('cc').LogWarn('Attibute error ignored when performing step change')
            else:
                raise

    @telemetry.ZONE_METHOD
    def OnStepClicked(self, stepClicked, *args):
        if self.callbackFunc:
            if self.stepID == stepClicked.id:
                if not eve.session.role & ROLE_PROGRAMMER:
                    return
            apply(self.callbackFunc, (stepClicked.id,))

    @telemetry.ZONE_METHOD
    def OnStepMouseOver(self, container, *args):
        mousedStep = container.id
        sm.StartService('audio').SendUIEvent(unicode('ui_icc_button_mouse_over_play'))
        if container.id != self.stepID:
            container.SetOpacity(self.MOUSEOVEROPACITY)
        self.UpdateHeader(stepID=mousedStep, opacity=self.ACTIVEOPACITY)

    @telemetry.ZONE_METHOD
    def OnStepMouseExit(self, container, *args):
        if container.id != self.stepID:
            container.SetOpacity(self.NORMALOPACITY)
        self.UpdateHeader(stepID=self.stepID, opacity=0.0)
