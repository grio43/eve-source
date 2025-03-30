#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\moonmining\planningCont.py
import eveLocalization
import gametime
import uthread
from carbonui.primitives.container import Container
import carbonui.const as uiconst
from dogma.const import attributeExtractionAutoFractureDelay
from carbonui.control.buttonIcon import ButtonIcon
from eve.client.script.ui.control.dateSinglelineEdit import DatePickerControl, HourMinPickerControl
from eve.client.script.ui.control.eveLabel import Label
from eve.client.script.ui.control.infoIcon import MoreInfoIcon
from eve.client.script.ui.moonmining import DAY_NAME_TEXT, PARTS_IN_HOUR, GetYieldMultiplier, DAY_NAME_TEXT_SHORT
import blue
from eve.client.script.ui.moonmining.outputCont import SchedulingOutputPanel
from eve.client.script.ui.moonmining.timePicker import TimePicker
from eve.client.script.ui.shared.fitting.fittingUtil import EatSignalChangingErrors
from localization import GetByLabel
from signals import Signal
from signals.signalUtil import ChangeSignalConnect
from carbonui.uicore import uicore

class PlanningCont(Container):

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.structureID = attributes.structureID
        self.schedulingController = attributes.schedulingController
        self.moonMaterialInfo = attributes.moonMaterialInfo
        self.centerCont = Container(name='centerCont', parent=self, height=140, align=uiconst.TOTOP)
        self.bottomCont = Container(name='bottomCont', parent=self, align=uiconst.TOALL)
        self.BuildCenter()
        self.BuildBottom()
        self.UpdateTimebasedUI()
        self.ChangeSignalConnection()

    def ChangeSignalConnection(self, connect = True):
        signalAndCallback = [(self.schedulingController.on_hours_changed, self.OnHoursUpdated), (self.upDownControl.on_value_changed, self.UpDownValueChanged)]
        ChangeSignalConnect(signalAndCallback, connect)

    def UpDownValueChanged(self, diff):
        self.schedulingController.AddNumHours(diff / float(PARTS_IN_HOUR), PARTS_IN_HOUR)

    def UpdateTimebasedUI(self, wasChange = True):
        self.SetAvailableTimeLabel()
        self.SetCountdownLabel()
        if wasChange:
            timestamp = self.schedulingController.GetCurrentTime()
            now = gametime.GetWallclockTime()
            numSec = float(timestamp - now) / const.SEC
            self.outputPanel.SetEstimation(numSec, GetYieldMultiplier(self.structureID))

    def BuildBottom(self):
        self.outputPanel = SchedulingOutputPanel(parent=self.bottomCont, moonMaterialInfo=self.moonMaterialInfo, top=8)

    def BuildCenter(self):
        self.timePickerCont = Container(name='timePickerCont', parent=self.centerCont, align=uiconst.TOTOP_NOPUSH, height=10, top=12)
        fontSize = 16
        self.weekdayLabel = Label(name='weekdayLabel', parent=self.timePickerCont, text='', align=uiconst.CENTERLEFT, fontsize=fontSize)
        weekdayLabelWidth = max([ uicore.font.GetTextWidth(x, fontSize, uppercase=True) for x in DAY_NAME_TEXT_SHORT ])
        fromTime = self.schedulingController.GetSliderStartTime()
        toTime = self.schedulingController.GetMaxValidTime()
        left = weekdayLabelWidth + 2
        self.fromPicker = DatePickerControl(name='fromPicker', parent=self.timePickerCont, OnEditFieldChanged=self.OnEditFieldChanged, setValue=[0, 0, 0], left=left, ranges=(fromTime, toTime), fontSize=fontSize, align=uiconst.CENTERLEFT)
        left += self.fromPicker.width + 10
        self.hourMinPicker = HourMinPickerControl(parent=self.timePickerCont, left=left, setValue=(0, 0), fontSize=fontSize, OnEditFieldChanged=self.OnEditFieldChanged, onEditFieldRolledOverFunc=self.OnEditFieldRolledOver)
        left += self.hourMinPicker.width + 10
        self.upDownControl = UpDownControl(parent=self.timePickerCont, iconSize=9, pos=(left,
         0,
         16,
         16), align=uiconst.CENTERLEFT)
        self.traversalHelpIcon = MoreInfoIcon(parent=self.timePickerCont, align=uiconst.CENTERRIGHT, padLeft=4)
        self.traversalHelpIcon.LoadTooltipPanel = self.LoadTraversalInfoTooltipPanel
        self.traversalLabelTime = Label(name='traversalLabel', parent=self.timePickerCont, align=uiconst.CENTERRIGHT, text='', state=uiconst.UI_NORMAL, fontsize=16, left=20)
        self.timePickerCont.height = self.fromPicker.height
        self.headerCont = Container(name='headerCont', parent=self.centerCont, align=uiconst.TOTOP, height=20, top=6)
        self.centerInnerCont = Container(name='centerInnerCont', parent=self.centerCont, align=uiconst.TOTOP, top=0, height=100)
        TimePicker(parent=self.centerInnerCont, align=uiconst.TOTOP, schedulingController=self.schedulingController)

    def OnEditFieldChanged(self, *args):
        hourMinTimestamp = self.hourMinPicker.GetTimestamp()
        self.SetTimestampsFromEditFields(hourMinTimestamp)

    def OnEditFieldRolledOver(self, hourMinTimestamp):
        self.SetTimestampsFromEditFields(hourMinTimestamp)

    def SetTimestampsFromEditFields(self, hourMinTimestamp):
        timeStamp = self.fromPicker.GetTimestamp() + hourMinTimestamp
        self.schedulingController.SetTimestamp(timeStamp, numParts=2)

    def SetAvailableTimeLabel(self):
        timestamp = self.schedulingController.GetCurrentTime()
        self.hourMinPicker.SetPickerValueFromTimestamp(timestamp)
        self.fromPicker.SetPickerValueFromTimestamp(timestamp)
        _, _, wd, _, _, _, _, _ = blue.os.GetTimeParts(timestamp + eveLocalization.GetTimeDelta() * const.SEC)
        self.weekdayLabel.text = DAY_NAME_TEXT_SHORT[wd].upper()

    def SetCountdownLabel(self):
        timestamp = self.schedulingController.GetCurrentTime()
        now = gametime.GetWallclockTime()
        diff = timestamp - now
        d = diff / const.DAY
        h = diff % const.DAY / const.HOUR
        m = diff % const.HOUR / const.MIN
        countdownText = GetByLabel('UI/Moonmining/CountdownShort', days=d, hours=h, minutes=m)
        self.traversalLabelTime.text = GetByLabel('UI/Moonmining/TraversalPeriod', countdownText=countdownText)

    def UpdateUI(self):
        pass

    def OnHoursUpdated(self, wasChange):
        self.UpdateTimebasedUI(wasChange)

    def LoadTraversalInfoTooltipPanel(self, tooltipPanel, *args):
        tooltipPanel.LoadGeneric1ColumnTemplate()
        dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
        fractureDelayInSec = dogmaLocation.GetAttributeValue(self.structureID, attributeExtractionAutoFractureDelay)
        fractureDelay = long(fractureDelayInSec * const.SEC)
        text = GetByLabel('UI/Moonmining/AutomaticFractureTooltip', fractureDelay=fractureDelay)
        tooltipPanel.AddLabelMedium(text=text, wrapWidth=200)

    def Close(self):
        with EatSignalChangingErrors(errorMsg='Moonmining planning'):
            self.ChangeSignalConnection(connect=False)
        Container.Close(self)


class UpDownControl(Container):
    default_align = uiconst.TORIGHT
    default_width = 20
    default_padLeft = 0
    default_padRight = 4
    default_padTop = 1
    default_padBottom = 1
    default_opacity = 0.75
    default_iconSize = 7

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        iconSize = attributes.get('iconSize', self.default_iconSize)
        buttonSize = iconSize + 2
        centerOffset = iconSize / 2 + 1
        self.on_value_changed = Signal(signalName='on_value_changed')
        self.upButton = ButtonIcon(name='upButton', parent=self, align=uiconst.CENTER, pos=(0,
         -centerOffset,
         buttonSize,
         buttonSize), iconSize=iconSize, texturePath='res:/UI/Texture/Shared/up.png', soundClick=uiconst.SOUND_VALUECHANGE_TICK)
        self.upButton.OnMouseDown = self.OnNumericUpButtonMouseDown
        self.upButton.OnMouseUp = self.OnNumericUpButtonMouseUp
        self.downButton = ButtonIcon(name='downButton', parent=self, align=uiconst.CENTER, pos=(0,
         centerOffset,
         buttonSize,
         buttonSize), iconSize=iconSize, texturePath='res:/UI/Texture/Shared/down.png', soundClick=uiconst.SOUND_VALUECHANGE_TICK)
        self.downButton.OnMouseDown = self.OnNumericDownButtonMouseDown
        self.downButton.OnMouseUp = self.OnNumericDownButtonMouseUp

    def OnNumericUpButtonMouseDown(self, *args):
        ButtonIcon.OnMouseDown(self.upButton, *args)
        self.updateNumericInputThread = uthread.new(self.UpdateNumericInputThread, 1)

    def OnNumericDownButtonMouseDown(self, *args):
        ButtonIcon.OnMouseDown(self.downButton, *args)
        self.updateNumericInputThread = uthread.new(self.UpdateNumericInputThread, -1)

    def UpdateNumericInputThread(self, diff):
        sleepTime = 500
        while uicore.uilib.leftbtn:
            self.on_value_changed(diff)
            blue.synchro.SleepWallclock(sleepTime)
            sleepTime -= 0.5 * sleepTime
            sleepTime = max(10, sleepTime)

    def KillNumericInputThread(self):
        if self.updateNumericInputThread:
            self.updateNumericInputThread.kill()
            self.updateNumericInputThread = None

    def OnNumericUpButtonMouseUp(self, *args):
        ButtonIcon.OnMouseUp(self.upButton, *args)
        self.KillNumericInputThread()

    def OnNumericDownButtonMouseUp(self, *args):
        ButtonIcon.OnMouseUp(self.downButton, *args)
        self.KillNumericInputThread()
