#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\planet\surveyUI.py
import math
import blue
import evetypes
import geo2
import localization
import uthread
from carbonui import fontconst, uiconst
from carbonui.control.slider import Slider
from carbonui.control.window import Window
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from carbonui.util.color import Color
from eve.client.script.ui.control import eveIcon, eveLabel
from eve.client.script.ui.control.bargraph import BarGraph
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.control.button import Button
from eve.client.script.ui.control.eveLabel import EveLabelSmall
from eve.client.script.ui.control.gauge import Gauge
from eve.client.script.ui.control.infoIcon import MoreInfoIcon
from eve.client.script.ui.shared.planet import planetCommon as planetCommonUI
from eve.client.script.ui.shared.planet.pinContainers.BasePinContainer import CaptionLabel, IconButton
from eve.common.lib import appConst
from eve.common.lib.PlanetResources import builder
from eve.common.script.util import planetCommon
from localization import GetByLabel
from localization.formatters.timeIntervalFormatters import FormatTimeIntervalShortWritten
BTNSIZE = 16

class SurveyWindow(Window):
    __notifyevents__ = ['OnPlanetViewChanged', 'OnEditModeChanged', 'OnEditModeBuiltOrDestroyed']
    default_fixedWidth = 730
    default_fixedHeight = 320
    default_windowID = 'PlanetSurvey'

    def ApplyAttributes(self, attributes):
        self.default_fixedHeight *= fontconst.fontSizeFactor
        super(SurveyWindow, self).ApplyAttributes(attributes)
        self.ecuPinID = attributes.get('ecuPinID')
        self.barGraphUpdating = False
        self.planetUISvc = sm.GetService('planetUI')
        self.planet = self.planetUISvc.planet
        self.pin = self.planet.GetPin(self.ecuPinID)
        self.extractionHeadValues = {}
        self.resourceTypeIDs = self.planet.remoteHandler.GetPlanetResourceInfo().keys()
        self.currResourceTypeID = self.pin.programType
        self.outputVals = []
        self.programCycleTime = None
        self.dragThread = None
        self.currCycleTime = None
        self.UpdateCurrentRadius()
        self.sh = None
        if self.currResourceTypeID is not None:
            inRange, self.sh = self.planetUISvc.planet.GetResourceData(self.currResourceTypeID)
        self.revertToResource = self.planetUISvc.selectedResourceTypeID
        self.currentResource = None
        self.editsEnabled = self.pin.GetExtractionType() is None or self.pin.GetTimeToExpiry() <= 0
        if self.editsEnabled:
            self.planetUISvc.myPinManager.UnlockHeads(self.pin.id)
        self.barTimeIndicatorThread = None
        self.overlapValues = {}
        self.stateColor = None
        self.pinData = None
        if self.pin.IsInEditMode():
            self.pinData = self.pin.Serialize()
        self.MakeUnResizeable()
        captionTxt = localization.GetByLabel('UI/PI/Common/SurveyingProgram', pinName=planetCommon.GetGenericPinName(self.pin.typeID, self.pin.id))
        self.SetCaption(captionTxt)
        Container(parent=self.sr.main, align=uiconst.TOTOP, height=10)
        self.leftCont = Container(name='leftCont', parent=self.sr.main, align=uiconst.TOLEFT, width=130, padding=(8, 0, 3, 6))
        self.rightCont = Container(name='rightCont', parent=self.sr.main, align=uiconst.TORIGHT, width=160, padding=(10, 0, 6, 6))
        self.centerCont = Container(name='centerCont', parent=self.sr.main, align=uiconst.TOALL)
        self._ConstructLeftContainer()
        self._ConstructCenterContainer()
        self._ConstructRightContainer()
        self.SetCurrentResource(self.currResourceTypeID)
        self.UpdateSubmitButton()

    def _ConstructLeftContainer(self):
        CaptionLabel(parent=self.leftCont, text=localization.GetByLabel('UI/PI/Common/ExtractorHeadUnits'), align=uiconst.TOTOP)
        self.ConstructExtractorHeadBtns()
        self.noExtractorsLabel = CaptionLabel(name='noExtractorsLabel', parent=self.leftCont, text=localization.GetByLabel('UI/PI/Common/NoExtractorsInstalled'), align=uiconst.TOTOP, padTop=4, color=Color.RED, state=uiconst.UI_HIDDEN)
        self.UpdateNoExtractorsLabel()
        MoreInfoIcon(parent=self.leftCont, align=uiconst.BOTTOMLEFT, hint=GetByLabel('UI/PI/Common/ECUHelpText'))

    def UpdateNoExtractorsLabel(self):
        if not self.pin.GetNumHeads():
            self.noExtractorsLabel.Show()
        else:
            self.noExtractorsLabel.Hide()

    def UpdateCurrentRadius(self):
        self.currentRadius = max(min(self.pin.headRadius, planetCommon.RADIUS_DRILLAREAMAX), planetCommon.RADIUS_DRILLAREAMIN)

    def ConstructExtractorHeadBtns(self):
        self.headButtons = []
        headEntryCont = Container(parent=self.leftCont, name='headEntryCont', align=uiconst.TOTOP, height=140, padTop=4)
        headEntryContLeft = Container(parent=headEntryCont, name='headEntryContLeft', align=uiconst.TOLEFT, width=self.leftCont.width / 2)
        headEntryContRight = Container(parent=headEntryCont, name='headEntryContRight', align=uiconst.TOLEFT, width=self.leftCont.width / 2)
        for i in xrange(planetCommon.ECU_MAX_HEADS):
            value = self.GetResourceLayerValueForHead(i)
            state = uiconst.UI_NORMAL if self.editsEnabled else uiconst.UI_DISABLED
            parent = headEntryContLeft if i < 5 else headEntryContRight
            btn = ExtractionHeadEntry(parent=parent, headID=i, ecuID=self.pin.id, align=uiconst.TOTOP, height=20, state=state, value=value, pin=self.pin)
            btn.OnClick = (self.OnHeadBtnClicked, i)
            self.headButtons.append(btn)

    def ConstructAreaSliderAndButtons(self):
        sliderParCont = ContainerAutoSize(name='sliderParCont', parent=self.rightCont, align=uiconst.TOTOP, padTop=10)
        CaptionLabel(parent=sliderParCont, text=localization.GetByLabel('UI/PI/Common/ProgramDuration'), align=uiconst.TOTOP, padBottom=2)
        sliderCont = ContainerAutoSize(parent=sliderParCont, name='sliderCont', align=uiconst.TOTOP, alignMode=uiconst.TOTOP)
        subtrBtn = ButtonIcon(parent=sliderCont, name='subtractBtn', align=uiconst.CENTERLEFT, texturePath='res:/UI/Texture/Icons/minus.png', iconSize=12, func=self.DecreaseDrillAreaSize, width=BTNSIZE)
        addBtn = ButtonIcon(parent=sliderCont, name='addBtn', align=uiconst.CENTERRIGHT, texturePath='res:/UI/Texture/Icons/plus.png', iconSize=12, func=self.IncreaseDrillAreaSize, width=BTNSIZE)
        sliderValue = math.sqrt((self.currentRadius - planetCommon.RADIUS_DRILLAREAMIN) / planetCommon.RADIUS_DRILLAREADIFF)
        self.programDurationSlider = Slider(parent=sliderCont, name='programDurationSlider', align=uiconst.TOTOP, minValue=0.0, maxValue=1.0, value=sliderValue, hint=localization.GetByLabel('UI/PI/Common/ExtractionAreaSize'), callback=self.OnProgramDurationSliderReleased, on_dragging=self.OnProgramDurationSliderMoved, padding=(BTNSIZE + 4,
         0,
         BTNSIZE + 4,
         0))
        self.programDurationSlider.barCont.OnMouseWheel = self.OnProgramDurationSliderMouseWheel
        if not self.editsEnabled:
            self.programDurationSlider.Disable()
            subtrBtn.Disable()
            addBtn.Disable()
        self.programDurationLabel = EveLabelSmall(name='programDurationLabel', parent=sliderParCont, align=uiconst.TOTOP, padTop=2)
        self.UpdateProgramDurationLabel()

    def UpdateProgramDurationLabel(self):
        self.programDurationLabel.text = self.GetProgramDurationText()

    def DecreaseDrillAreaSize(self, *args):
        self.ChangeDrillAreaSize(numSteps=-1)

    def IncreaseDrillAreaSize(self, *args):
        self.ChangeDrillAreaSize(numSteps=1)

    def ChangeDrillAreaSize(self, numSteps):
        newSliderValue = self._GetNextSliderValue(numSteps)
        self.programDurationSlider.SetValue(newSliderValue)
        self.UpdateProgramDuration()
        self.UpdateDurationLabels()

    def _GetNextSliderValue(self, numSteps):
        oldNumCycles = None
        sliderVal = self.programDurationSlider.value
        maxCount = 1000
        count = 0
        while count < maxCount:
            count += 1
            cycleTime, numCycles = self._GetCycleTimeAndNumCyclesFromSliderVal(sliderVal)
            if not oldNumCycles:
                oldNumCycles = numCycles
            if oldNumCycles != numCycles:
                break
            sliderVal += 0.001 * numSteps

        return sliderVal

    def _GetCycleTimeAndNumCyclesFromSliderVal(self, sliderVal):
        radius = self._GetRadiusFromSliderVal(sliderVal)
        programLength = planetCommon.GetProgramLengthFromHeadRadius(radius)
        cycleTime = planetCommon.GetCycleTimeFromProgramLength(programLength)
        numCycles = int(programLength / cycleTime)
        return (cycleTime, numCycles)

    def _GetRadiusFromSliderVal(self, sliderVal):
        return sliderVal ** 2 * planetCommon.RADIUS_DRILLAREADIFF + planetCommon.RADIUS_DRILLAREAMIN

    def OnProgramDurationSliderReleased(self, slider):
        self.UpdateProgramDuration()
        self.UpdateDurationLabels()

    def UpdateProgramDuration(self, updateBargraph = True):
        radius = self.programDurationSlider.value ** 2 * planetCommon.RADIUS_DRILLAREADIFF + planetCommon.RADIUS_DRILLAREAMIN
        self.planetUISvc.myPinManager.SetExtractionHeadRadius(self.pin.id, radius)
        self.currentRadius = radius
        self.UpdateProgram(updateBargraph=updateBargraph)

    def OnProgramDurationSliderMoved(self, slider):
        self.UpdateDurationLabels()
        self.UpdateProgramDuration(updateBargraph=False)

    def UpdateDurationLabels(self):
        text = self.GetProgramDurationText()
        self.barGraph.SetXLabels((localization.GetByLabel('UI/PI/Common/SurveyProgramStart'), text))
        self.programDurationLabel.text = text

    def GetProgramDurationText(self):
        cycleTime, numCycles = self._GetCycleTimeAndNumCyclesFromSliderVal(self.programDurationSlider.value)
        cycleTime = int(cycleTime * const.HOUR)
        text = self._GetProgramDurationText(cycleTime, numCycles)
        return text

    def _GetProgramDurationText(self, cycleTime, numCycles):
        return FormatTimeIntervalShortWritten(cycleTime * numCycles, showTo='minute')

    def OnProgramDurationSliderMouseWheel(self, dz, *args):
        self.ChangeDrillAreaSize(int(dz / 120))

    def _ConstructCenterContainer(self):
        self.barGraph = BarGraph(parent=self.centerCont, align=uiconst.TOALL, barUpdateDelayMs=1, barHintFunc=self.GetBarHint, padding=(0, 2, 0, 10))
        uthread.new(self.UpdateProgram)

    def GetBarHint(self, numBar, value, maxValue):
        accOutput = sum(self.outputVals[:numBar])
        accTime = self.currCycleTime * numBar
        accPerHour = appConst.HOUR * accOutput / accTime
        return localization.GetByLabel('UI/PI/Common/SurveyBarHint', numBar=numBar, value=value, accOutput=accOutput, accTime=accTime, accPerHour=accPerHour)

    def UpdateProgram(self, replaceHeadID = None, point = None, updateBargraph = True):
        if self.currentResource is None:
            return
        cycleTime, maxValue, numCycles = self.GetProgramParameters(point, replaceHeadID)
        self.currCycleTime = cycleTime
        self.programCycleTime = cycleTime
        self.outputVals = self.pin.GetProgramOutputPrediction(maxValue, cycleTime, numCycles)
        self._UpdateOutputPerHourLabel(numCycles)
        if updateBargraph:
            self._UpdateBargraph(numCycles)

    def GetProgramParameters(self, point, replaceHeadID):
        if self.editsEnabled:
            heads = self.pin.heads[:]
            if replaceHeadID is not None:
                for each in self.pin.heads:
                    if each[0] == replaceHeadID:
                        heads.remove(each)
                        heads.append((replaceHeadID, point.phi, point.theta))
                        break

            colony = self.GetColony()
            maxValue, cycleTime, numCycles, self.overlapValues = colony.CreateProgram(self.currentResource, self.pin.id, self.currResourceTypeID, points=heads, headRadius=self.currentRadius)
            self.UpdateOverlapValues()
            self.planetUISvc.myPinManager.SetEcuOverlapValues(self.pin.id, self.overlapValues)
        else:
            maxValue, cycleTime, numCycles = self.pin.GetProgramParameters()
        return (cycleTime, maxValue, numCycles)

    def _UpdateBargraph(self, numCycles):
        self.barGraph.SetValues(self.outputVals)
        xLabels = (localization.GetByLabel('UI/PI/Common/SurveyProgramStart'), self._GetProgramDurationText(self.programCycleTime, numCycles))
        self.barGraph.SetXLabels(xLabels)
        self.UpdateBarTimeIndicator()

    def UpdateOverlapValues(self):
        for id, headButton in enumerate(self.headButtons):
            headButton.SetOverlapValue(self.overlapValues.get(id, None))

    def _UpdateOutputPerHourLabel(self, numCycles):
        totalOutput = sum(self.outputVals)
        perHourOutput = float(totalOutput) * appConst.HOUR / (numCycles * self.programCycleTime)
        if self.currResourceTypeID:
            self.outputPerHourTxt.Show()
            self.outputPerHourTxt.SetText(localization.GetByLabel('UI/PI/Common/SurveyPerHourOutput', perHourOutput=perHourOutput))
            self.outputTotalTxt.SetText(localization.GetByLabel('UI/PI/Common/SurveyTotalOutput', totalOutput=totalOutput))
        else:
            self.outputPerHourTxt.Hide()

    def UpdateBarTimeIndicator(self):
        if self.pin.IsActive() and not self.pin.IsInEditMode():
            if self.barTimeIndicatorThread is None:
                self.barTimeIndicatorThread = uthread.new(self._UpdateBarTimeIndicator)
        else:
            self.barGraph.HideTimeIndicator()
            if self.barTimeIndicatorThread is not None:
                self.barTimeIndicatorThread.kill()
                self.barTimeIndicatorThread = None

    def _UpdateBarTimeIndicator(self):
        while self and not self.destroyed:
            indicatorValue = float(blue.os.GetWallclockTime() - self.pin.installTime) / (self.pin.expiryTime - self.pin.installTime)
            if indicatorValue > 0.0 and indicatorValue < 1.0:
                self.barGraph.ShowTimeIndicator(indicatorValue)
            blue.pyos.synchro.SleepWallclock(10000)

    def OnHeadEntryMouseEnter(self, headID):
        if not uicore.uilib.leftbtn:
            self.headButtons[headID].ShowFill()

    def OnHeadEntryMouseExit(self, headID):
        self.headButtons[headID].HideFill()

    def _ConstructRightContainer(self):
        self.ConstructResourceSelectionIcons()
        if self.pin.IsActive():
            self.ConstructCurrCycleGauge()
        else:
            self.ConstructAreaSliderAndButtons()
        self.ConstructOutputLabels()
        self.ConstructSubmitButton()
        self.ConstructStateIndicatorCont()

    def ConstructCurrCycleGauge(self):
        self.currCycleGauge = Gauge(parent=self.rightCont, align=uiconst.TOTOP, value=0.0, color=planetCommonUI.PLANET_COLOR_CYCLE, label=localization.GetByLabel('UI/PI/Common/CurrentCycle'), padTop=10)
        uthread.new(self._UpdateCurrCycleGauge)

    def ConstructOutputLabels(self):
        self.outputTxtCont = ContainerAutoSize(parent=self.rightCont, align=uiconst.TOTOP, height=40, padTop=10)
        CaptionLabel(parent=self.outputTxtCont, text=localization.GetByLabel('UI/PI/Common/Output'), align=uiconst.TOTOP)
        self.outputPerHourTxt = EveLabelSmall(parent=self.outputTxtCont, text=localization.GetByLabel('UI/Common/None'), align=uiconst.TOTOP)
        self.outputTotalTxt = EveLabelSmall(parent=self.outputTxtCont, align=uiconst.TOTOP)
        self.UpdateOutputTextCont()

    def UpdateOutputTextCont(self):
        if self.currResourceTypeID:
            self.outputTxtCont.Show()
        else:
            self.outputTxtCont.Hide()

    def ConstructStateIndicatorCont(self):
        stateParent = ContainerAutoSize(parent=self.rightCont, align=uiconst.TOBOTTOM, padBottom=2)
        self.stateTxt = eveLabel.EveLabelSmall(parent=stateParent, align=uiconst.CENTERTOP, color=Color.WHITE, state=uiconst.UI_NORMAL, padding=(0, 2, 0, 2), width=self.leftCont.width - 10)
        self.stateColorFill = Fill(bgParent=stateParent)
        self.UpdateStateInfoCont()

    def ConstructResourceSelectionIcons(self):
        CaptionLabel(parent=self.rightCont, text=localization.GetByLabel('UI/PI/Common/SelectedResource'), align=uiconst.TOTOP)
        self.resourceIconButtons = {}
        numIcons = len(self.resourceTypeIDs)
        ICONSIZE = 25
        PAD = 4
        if self.editsEnabled:
            state = uiconst.UI_PICKCHILDREN
        else:
            state = uiconst.UI_DISABLED
        iconCont = Container(parent=self.rightCont, align=uiconst.TOTOP, pos=(0,
         0,
         numIcons * (ICONSIZE + PAD),
         ICONSIZE), state=state, padding=(0, 2, 0, 2))
        resourceTypes = [ (evetypes.GetName(typeID), typeID) for typeID in self.resourceTypeIDs ]
        resourceTypes.sort()
        for i, (typeName, typeID) in enumerate(resourceTypes):
            ib = IconButton(parent=iconCont, pos=(i * (ICONSIZE + PAD),
             0,
             ICONSIZE,
             ICONSIZE), size=ICONSIZE, typeID=typeID, ignoreSize=True)
            self.resourceIconButtons[typeID] = ib
            ib.OnClick = (self.OnResourceBtnClicked, typeID)
            ib.OnMouseEnter = (self.OnResourceBtnMouseEnter, ib, typeID)
            ib.OnMouseExit = (self.OnResourceBtnMouseExit, ib)

        self.selectedResourceTxt = EveLabelSmall(parent=self.rightCont, text='', align=uiconst.TOTOP)
        self.SetCurrentResourceText(self.currResourceTypeID)

    def _UpdateCurrCycleGauge(self):
        while not self.destroyed:
            if self.pin.IsActive():
                self.currCycleGauge.Show()
                txt, cycleProportion = planetCommonUI.GetPinCycleInfo(self.pin, self.programCycleTime)
                self.currCycleGauge.SetValueInstantly(cycleProportion)
                self.currCycleGauge.SetSubText(txt)
            else:
                self.currCycleGauge.Hide()
            blue.pyos.synchro.SleepWallclock(1000)

    def UpdateStateInfoCont(self):
        if self.pin.IsInEditMode():
            color = Color.WHITE
            text = localization.GetByLabel('UI/PI/Common/EditsPending')
            animations.FadeTo(self.stateColorFill, 0.0, 0.5, duration=2.0, curveType=uiconst.ANIM_WAVE, loops=uiconst.ANIM_REPEAT)
        elif self.pin.IsActive():
            color = Color('GREEN').SetAlpha(0.4).GetRGBA()
            text = localization.GetByLabel('UI/PI/Common/SurveyProgramRunning')
            animations.FadeTo(self.stateColorFill, 0.2, 0.5, duration=3.0, curveType=uiconst.ANIM_WAVE, loops=uiconst.ANIM_REPEAT)
        else:
            color = Color.WHITE
            text = localization.GetByLabel('UI/Common/Idle')
            animations.FadeTo(self.stateColorFill, 0.0, 0.5, duration=2.0, curveType=uiconst.ANIM_WAVE, loops=uiconst.ANIM_REPEAT)
        self.stateColorFill.SetRGBA(*color)
        self.stateTxt.SetText('<center>' + text)

    def ConstructSubmitButton(self):
        if self.editsEnabled:
            btnName = localization.GetByLabel('UI/PI/Common/SurveyInstallProgram')
            func = self._ApplyProgram
        else:
            btnName = localization.GetByLabel('UI/PI/Common/SurveyStopProgram')
            func = self._StopProgram
        self.submitButton = Button(parent=self.rightCont, label=btnName, func=func, align=uiconst.TOBOTTOM, idx=0, fixedheight=20)

    def UpdateSubmitButton(self):
        nextEditTime = self.pin.GetNextEditTime()
        if nextEditTime is not None and nextEditTime > blue.os.GetWallclockTime() and not self.pin.IsInEditMode():
            self.submitButton.Disable()
            uthread.new(self._UnlockStopButtonThread).context = '_SetSubmitButtonState'
        elif self.currentResource is None or not self.pin.GetNumHeads():
            self.submitButton.Disable()
            self.submitButton.SetHint('')
        else:
            self.submitButton.Enable()
            self.submitButton.SetHint('')

    def _UnlockStopButtonThread(self):
        nextEditTime = self.pin.GetNextEditTime()
        while nextEditTime > blue.os.GetWallclockTime():
            self.submitButton.SetHint(localization.GetByLabel('UI/PI/Common/SurveyEditsAvailableIn', time=nextEditTime - blue.os.GetWallclockTime()))
            blue.pyos.synchro.SleepWallclock(200)
            if not self or self.destroyed:
                return

        self.UpdateSubmitButton()

    def OnHeadBtnClicked(self, headID):
        head = self.pin.FindHead(headID)
        if not head:
            self.PlaceProbeAtDefaultPosition(headID)
        else:
            self.planetUISvc.myPinManager.RemoveExtractionHead(self.pin.id, headID)
            if headID in self.extractionHeadValues:
                self.extractionHeadValues.pop(headID)
            self.headButtons[headID].SetValue(None)
        self.UpdateProgram()
        self.UpdateNoExtractorsLabel()
        self.UpdateSubmitButton()

    def OnBeginDragExtractionHead(self, headID, surfacePoint):
        sm.GetService('audio').SendUIEvent('msg_pi_extractor_play')
        sm.GetService('audio').SendUIEvent('msg_pi_extractor_distorted_play')
        if self.currResourceTypeID is not None:
            self.dragThread = uthread.new(self._WhileExtractionHeadDraggedThread, headID, surfacePoint)
        else:
            self.headButtons[headID].SetValue(0.0)

    def OnEndDragExtractionHead(self):
        sm.GetService('audio').SendUIEvent('msg_pi_extractor_stop')
        sm.GetService('audio').SendUIEvent('msg_pi_extractor_distorted_stop')
        if self.dragThread is not None:
            self.dragThread.kill()
            self.dragThread = None

    def OnExtractionHeadMoved(self, headID, surfacePoint):
        self.UpdateHeadPosition(headID, surfacePoint)

    def OnExtractionHeadAdded(self, headID, surfacePoint):
        self.UpdateProgram()
        self.UpdateNoExtractorsLabel()
        self._UpdateExtractorValues()

    def _UpdateExtractorValues(self):
        for i in xrange(planetCommon.ECU_MAX_HEADS):
            value = self.GetResourceLayerValueForHead(i)
            self.headButtons[i].SetValue(value)

    def OnExtractionHeadRemoved(self, headID):
        self.UpdateProgram()
        self.UpdateNoExtractorsLabel()
        self._UpdateExtractorValues()

    def _WhileExtractionHeadDraggedThread(self, headID, surfacePoint):
        while not self.destroyed:
            if self.currentResource is not None:
                self.UpdateProgram(replaceHeadID=headID, point=surfacePoint)
            blue.pyos.synchro.SleepWallclock(200)

    def UpdateHeadPosition(self, headID, surfacePoint):
        heads = self.pin.heads
        headRadius = self.pin.headRadius
        if self.currentResource is not None:
            value = self.GetResourceLayerValueForHead(headID, surfacePoint)
            overlapValue = self.overlapValues.get(headID, None)
            self.headButtons[headID].SetValue(value=value, overlapValue=overlapValue)
            if value is not None:
                sm.GetService('audio').SetGlobalRTPC('pitch_extractor_quality', 100 * value / 250)
            if overlapValue is not None:
                sm.GetService('audio').SetGlobalRTPC('volume_extractor_interference', 10 * overlapValue)
        else:
            self.headButtons[headID].SetValue(value=0.0)

    def UpdateHeadButtonValues(self):
        for headButton in self.headButtons:
            value = self.GetResourceLayerValueForHead(headButton.headID)
            self.extractionHeadValues[headButton.headID] = value
            headButton.SetValue(value)

    def GetResourceLayerValueForHead(self, headID, surfacePoint = None):
        if self.currResourceTypeID:
            head = self.pin.FindHead(headID)
            if head:
                headID, phi, theta = head
                if surfacePoint:
                    theta = 2.0 * math.pi - surfacePoint.theta
                    phi = surfacePoint.phi
                else:
                    theta = 2.0 * math.pi - theta
                    phi = phi
                return max(0.0, builder.GetValueAt(self.sh, theta, phi))
        else:
            if self.pin.FindHead(headID) is not None:
                return 0.0
            return

    def PlaceProbeAtDefaultPosition(self, headID):
        OFFSET = 0.08
        VEC_X = (-1, 0, 0)
        rotAngle = float(headID) / planetCommon.ECU_MAX_HEADS * 2 * math.pi
        ecuVector = self.planetUISvc.myPinManager.pinsByID[self.pin.id].surfacePoint.GetAsXYZTuple()
        normal = geo2.Vec3Cross(ecuVector, VEC_X)
        normal = geo2.Vector(*normal) * OFFSET
        posVec = geo2.Vec3Subtract(ecuVector, normal)
        posVec = geo2.Vec3Normalize(posVec)
        rotMat = geo2.MatrixRotationAxis(ecuVector, rotAngle)
        posVec = geo2.Multiply(rotMat, posVec)
        surfacePoint = planetCommon.SurfacePoint(*posVec)
        self.planetUISvc.myPinManager.PlaceExtractionHead(self.pin.id, surfacePoint, headID)
        self.UpdateHeadPosition(headID, surfacePoint)

    def _ApplyProgram(self, *args):
        if self.currResourceTypeID is not None:
            self.planet.InstallProgram(self.pin.id, self.currResourceTypeID, self.currentRadius)
        self.planetUISvc.myPinManager.ReRenderPin(self.pin)
        self.planetUISvc.eventManager.SelectPin(self.pin.id)
        self.Close()

    def _Cancel(self, *args):
        self.planetUISvc.CancelInstallProgram(self.pin.id, self.pinData)
        self.Close()

    def _StopProgram(self, *args):
        self.editsEnabled = True
        self.pin.inEditMode = True
        self.leftCont.Flush()
        self.rightCont.Flush()
        self.planetUISvc.myPinManager.UnlockHeads(self.pin.id)
        self.planetUISvc.GetCurrentPlanet().InstallProgram(self.pin.id, None, self.currentRadius)
        self._ConstructLeftContainer()
        self._ConstructRightContainer()
        self.SetCurrentResource(self.currResourceTypeID)
        self.UpdateSubmitButton()

    def OnResourceBtnClicked(self, typeID, *args):
        self.SetCurrentResource(typeID)

    def OnResourceBtnMouseEnter(self, btn, typeID, *args):
        self.SetCurrentResourceText(typeID)
        IconButton.OnMouseEnter(btn)

    def OnResourceBtnMouseExit(self, btn, *args):
        self.SetCurrentResourceText(self.currResourceTypeID)
        IconButton.OnMouseExit(btn)

    def SetCurrentResource(self, typeID = None):
        self.currResourceTypeID = typeID
        self.currentResource = None if typeID is None else self.planet.GetResourceHarmonic(typeID)
        self.UpdateSelectedResourceIconBtns(typeID)
        self.UpdateSubmitButton()
        if typeID is None:
            self.sh = None
        else:
            inRange, self.sh = self.planetUISvc.planet.GetResourceData(self.currResourceTypeID)
        self.SetCurrentResourceText(typeID)
        self.UpdateHeadButtonValues()
        self.UpdateProgram()
        self.planetUISvc.ShowResource(typeID)
        self.UpdateOutputTextCont()

    def UpdateSelectedResourceIconBtns(self, typeID):
        for ibTypeID, ib in self.resourceIconButtons.iteritems():
            if self.currResourceTypeID:
                ib.SetDeselected()
            if not self.editsEnabled and ibTypeID != typeID:
                ib.Disable()

        if typeID:
            ib = self.resourceIconButtons[typeID]
            ib.SetSelected()

    def SetCurrentResourceText(self, typeID):
        if typeID:
            text = evetypes.GetName(typeID)
        else:
            text = '<color=red>%s</color>' % localization.GetByLabel('UI/PI/Common/NoResourceSelected')
        self.selectedResourceTxt.text = text

    def OnPlanetViewChanged(self, newPlanet, oldPlanet):
        self.Close()

    def OnEditModeBuiltOrDestroyed(self, planetID):
        if not self or self.destroyed:
            return
        if self.planet.planetID != planetID:
            return
        if self.planet.GetPin(self.pin.id) is None:
            self.Close()

    def OnEditModeChanged(self, isEdit):
        if not self or self.destroyed:
            return
        if not isEdit:
            self.Close()

    def CloseByUser(self, *args):
        self.planetUISvc.CancelInstallProgram(self.pin.id, self.pinData)
        Window.CloseByUser(self, *args)

    def _OnClose(self, *args):
        if hasattr(self, 'revertToResource'):
            self.planetUISvc.ShowResource(self.revertToResource)
        self.planetUISvc.ExitSurveyMode()

    def GetColony(self):
        return self.planetUISvc.GetCurrentPlanet().GetColony(session.charid)


class ExtractionHeadEntry(Container):
    __guid__ = 'uicls.ExtractionHeadEntry'
    default_name = 'ExtractionHeadEntry'
    default_height = 20
    default_state = uiconst.UI_NORMAL
    default_padBottom = 9

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.headID = attributes.headID
        self.ecuID = attributes.ecuID
        self.value = attributes.get('value', None)
        self.pin = attributes.pin
        self.overlapValue = None
        self.fill = Fill(parent=self, align=uiconst.TOTOP, height=self.default_height, color=Color(*Color.WHITE).SetAlpha(0.1).GetRGBA(), state=uiconst.UI_HIDDEN, idx=0)
        self.icon = eveIcon.Icon(parent=self, icon='ui_77_32_38', size=self.default_height, ignoreSize=True, state=uiconst.UI_DISABLED, left=-2)
        self.label = EveLabelSmall(parent=self, text='', left=self.default_height, top=4)
        self.SetValue(self.value)

    def SetValue(self, value = None, overlapValue = None):
        self.value = value
        self.overlapValue = overlapValue
        if value is None:
            txt = localization.GetByLabel('UI/PI/Common/SurveyDashSign')
            self.opacity = 0.5
        else:
            if overlapValue:
                txt = localization.GetByLabel('UI/PI/Common/SurveyHeadValueDisturbed', value=value, percentage=int(math.ceil(100 * overlapValue)))
            else:
                txt = localization.GetByLabel('UI/PI/Common/SurveyHeadValue', value=value)
            self.opacity = 1.0
        self.label.text = txt

    def GetHint(self, *args):
        if self.value is None:
            return localization.GetByLabel('UI/PI/Common/SurveyInstallHeadHint', power=self.pin.GetExtractorHeadPowerUsage(), cpu=self.pin.GetExtractorHeadCpuUsage())
        if self.overlapValue:
            disturbanceText = localization.GetByLabel('UI/PI/Common/SurveyExtractorHeadDisturbanceHint', percentage=int(math.ceil(100 * self.overlapValue)))
        else:
            disturbanceText = ''
        hint = localization.GetByLabel('UI/PI/Common/SurveyExtractorHeadHint', headID=self.headID + 1, value=self.value, disturbanceText=disturbanceText)
        return hint

    def LoadTooltipPanel(self, tooltipPanel, *args):
        tooltipPanel.LoadGeneric2ColumnTemplate()
        tooltipPanel.AddLabelMedium(text=self.GetHint(), colSpan=2, cellPadding=(0, 0, 0, 10), wrapWidth=200)
        tooltipPanel.AddLabelShortcut(GetByLabel('UI/PI/Common/InstallExtractor'), GetByLabel('UI/PI/Common/InstallExtractorShortcut'))
        tooltipPanel.AddSpacer(height=1)
        tooltipPanel.AddLabelShortcut(GetByLabel('UI/PI/Common/MoveExtractor'), GetByLabel('UI/PI/Common/MoveExtractorShortcut'))

    def GetTooltipPointer(self):
        if self.headID < 5:
            return uiconst.POINT_RIGHT_2
        else:
            return uiconst.POINT_LEFT_2

    def SetOverlapValue(self, overlapValue):
        self.SetValue(self.value, overlapValue)

    def OnMouseEnter(self, *args):
        if not self or self.destroyed:
            return
        self.ShowFill()
        if self.value is None:
            self.label.text = localization.GetByLabel('UI/PI/Common/SurveyInstall')
            self.opacity = 1.0
        sm.GetService('planetUI').myPinManager.OnExtractionHeadMouseEnter(self.ecuID, self.headID)

    def OnMouseExit(self, *args):
        if not self or self.destroyed:
            return
        self.HideFill()
        if self.value is None:
            self.label.text = localization.GetByLabel('UI/PI/Common/SurveyDashSign')
            self.opacity = 0.5
        sm.GetService('planetUI').myPinManager.OnExtractionHeadMouseExit(self.ecuID, self.headID)

    def ShowFill(self):
        if self.overlapValue:
            self.fill.height = 28
        else:
            self.fill.height = self.default_height
        self.fill.state = uiconst.UI_DISABLED

    def HideFill(self):
        self.fill.state = uiconst.UI_HIDDEN
