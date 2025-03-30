#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\moonmining\timePicker.py
import datetime
import gametime
from carbon.client.script.environment.AudioUtil import PlaySound
from carbon.common.script.util.format import FmtDate
from carbonui import const as uiconst
from carbonui.control.slider import Slider
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.primitives.frame import Frame
from carbonui.primitives.gridcontainer import GridContainer
from carbonui.primitives.line import Line
from carbonui.uicore import uicore
from eve.client.script.ui import eveThemeColor, eveColor
from eve.client.script.ui.control.eveLabel import EveLabelSmall
from eve.client.script.ui.control.themeColored import FrameThemeColored, FillThemeColored, SpriteThemeColored, LineThemeColored
from eve.client.script.ui.moonmining import DAY_NAME_TEXT, VULNERABILITY_COLOR, NUM_HOURS_IN_BLOCK, NUM_HOURS_ZOOMER, PARTS_IN_HOUR, GetRangeTimeForSlider, DAY_NAME_TEXT_SHORT
from eve.client.script.ui.shared.fitting.fittingUtil import EatSignalChangingErrors
from localization import GetByLabel
from moonmining.const import MAXIMUM_EXTRACTION_DURATION
from signals.signalUtil import ChangeSignalConnect
import blue
MAX_EXTRACTION_HOURS = MAXIMUM_EXTRACTION_DURATION / 3600

class TimePicker(Container):
    default_height = 130
    default_clipChildren = True

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.schedulingController = attributes.schedulingController
        startVal = self.schedulingController.GetCurrentTimeAsPercentage()
        self.areaSlider = AreaSlider(parent=self, name='areaSlider', align=uiconst.TOTOP, padTop=20, minValue=0.0, maxValue=1.0, startVal=startVal, callback=self.OnSliderChanged, height=24, barHeight=24, on_dragging=self.OnSliderSetValue, schedulingController=self.schedulingController)
        self.zoomerCont = Container(parent=self, align=uiconst.TOTOP, height=36, padTop=20)
        self.zoomer = Zoomer(parent=self.zoomerCont, barHeight=16, schedulingController=self.schedulingController)
        self.ChangeSignalConnection()

    def ChangeSignalConnection(self, connect = True):
        signalAndCallback = [(self.schedulingController.on_hours_changed, self.OnHoursUpdated)]
        ChangeSignalConnect(signalAndCallback, connect)

    def OnSliderChanged(self, *args):
        pass

    def OnSliderSetValue(self, slider):
        value = slider.GetValue()
        self.schedulingController.SetTimestampFromPercentage(value)

    def OnHoursUpdated(self, wasChange):
        currentTime = self.schedulingController.GetCurrentTime()
        valuePercentage = self.schedulingController.GetCurrentTimeAsPercentage()
        self.areaSlider.SetValue(valuePercentage)
        self.zoomer.LoadZoomer(currentTime)

    def Close(self, *args, **kwds):
        with EatSignalChangingErrors(errorMsg='TimePicker'):
            self.ChangeSignalConnection(connect=False)
        Container.Close(self)


class SchedulingTimeline(Container):
    default_name = 'schedulingTimeline'
    default_state = uiconst.TOALL
    weekLineColor = (1, 1, 1, 0.3)
    fuelExpiryLineColor = (1, 0.25, 0, 1.0)

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.schedulingController = attributes.schedulingController
        self.fuelLine = None
        numBlocks = MAX_EXTRACTION_HOURS / NUM_HOURS_IN_BLOCK
        gridCont = GridContainer(name='mainCont', parent=self, align=uiconst.TOALL, lines=1, columns=numBlocks)
        self.hourContList = []
        self.hourContDict = {}
        startTime, _ = GetRangeTimeForSlider()
        for x in xrange(numBlocks):
            blockTimeStart = startTime + x * NUM_HOURS_IN_BLOCK * const.HOUR
            _, _, wd, day, hour, _, _, _ = blue.os.GetTimeParts(blockTimeStart)
            cName = '%s_%s_%s' % (wd, day, hour)
            c = Container(name=cName, parent=gridCont)
            if GetISOWeekDay(wd) == 0 and hour < NUM_HOURS_IN_BLOCK:
                Line(parent=c, align=uiconst.TOLEFT_NOPUSH, weight=1, color=self.weekLineColor)
            c.blockTimeStart = blockTimeStart
            self.hourContList.append(c)

        Fill(bgParent=self, color=(0.9, 0.9, 0.9, 0.075))
        self.MarkFuelExpiryTime()
        self.ChangeSignalConnection()

    def ChangeSignalConnection(self, connect = True):
        signalAndCallback = [(self.schedulingController.on_fuel_changed, self.MarkFuelExpiryTime)]
        ChangeSignalConnect(signalAndCallback, connect)

    def MarkFuelExpiryTime(self):
        fuelExpiryTime = self.schedulingController.GetFuelExpiryTime()
        if self.fuelLine and not self.fuelLine.destroyed:
            self.fuelLine.Close()
        self.fuelLine = None
        for each in self.hourContList:
            if each.blockTimeStart <= fuelExpiryTime < each.blockTimeStart + NUM_HOURS_IN_BLOCK * const.HOUR:
                self.fuelLine = Line(parent=each, align=uiconst.TOLEFT_NOPUSH, weight=2, color=self.fuelExpiryLineColor, padTop=-4, padBottom=-4, state=uiconst.UI_NORMAL)
                self.fuelLine.hint = GetByLabel('UI/Moonmining/FuelExpires', timestamp=FmtDate(fuelExpiryTime, 'ls'))
                return

    def Close(self):
        with EatSignalChangingErrors(errorMsg='Scheduling wnd'):
            self.ChangeSignalConnection(connect=False)
        Container.Close(self)


class AreaSlider(Slider):
    __guid__ = 'AreaSlider'
    default_barHeight = 13
    default_state = uiconst.UI_NORMAL
    zoomerFramePercentage = float(NUM_HOURS_ZOOMER) / MAX_EXTRACTION_HOURS

    def ApplyAttributes(self, attributes):
        self.sliderFillCont = None
        self.zoomerBinding = None
        self.curveSet = None
        self.schedulingController = attributes.schedulingController
        super(AreaSlider, self).ApplyAttributes(attributes)
        self.barCont.OnMouseEnter = self.OnMouseEnter
        self.barCont.OnMouseExit = self.OnMouseExit
        timeline = SchedulingTimeline(parent=self, schedulingController=self.schedulingController, idx=0)
        timeline.OnClick = self.OnSliderClicked
        timeline.OnMouseWheel = self.OnMouseWheel
        self.handle.SetOrder(0)
        self.zoomerFrameCont.SetOrder(0)
        startValue = self.schedulingController.GetCurrentTimeAsPercentage()
        self.SetValue(startValue)

    def _ConstructBackground(self):
        bgCont = Container(name='bgCont', parent=self, align=uiconst.TOTOP_NOPUSH, height=self.height, idx=0, state=uiconst.UI_DISABLED, padRight=2)
        self.sliderFillCont = Container(parent=bgCont, align=uiconst.TOLEFT_PROP)
        FillThemeColored(name='handleFill', parent=self.sliderFillCont, align=uiconst.TORIGHT_NOPUSH, state=uiconst.UI_DISABLED, colorType=uiconst.COLORTYPE_UIHILIGHTGLOW, width=3, padRight=-2, opacity=5.0)
        FrameThemeColored(parent=self.sliderFillCont, colorType=uiconst.COLORTYPE_UIHILIGHTGLOW, padLeft=0)
        FillThemeColored(parent=self.sliderFillCont, colorType=uiconst.COLORTYPE_UIHILIGHTGLOW, opacity=0.25)

    def _ConstructHandle(self):
        self.handleOffset = 0
        self.handle = Container(name='handle', parent=self, align=uiconst.BOTTOMLEFT, state=uiconst.UI_NORMAL, pos=(0,
         0,
         1,
         self.height), colorType=uiconst.COLORTYPE_UIHILIGHTGLOW, idx=0)
        self.handleFill = SpriteThemeColored(name='handleArrows', parent=self.handle, align=uiconst.CENTER, state=uiconst.UI_DISABLED, pos=(0, 0, 26, 24), color=eveThemeColor.THEME_FOCUS, outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, texturePath='res:/UI/Texture/classes/moonmining/sliderHandle3.png')
        self.zoomerFrameCont = ZoomerFrameCont(name='zoomerFrameCont', parent=self, align=uiconst.CENTERLEFT, pos=(0,
         0,
         60,
         self.height), state=uiconst.UI_NORMAL)
        Frame(parent=self.zoomerFrameCont, texturePath='res:/UI/Texture/Classes/Moonmining/zoomerFrame.png', cornerSize=6, padding=-1, color=eveThemeColor.THEME_ACCENT)
        self.SetZoomerFrameWidth()
        self.curveSet = uicore.animations.CreateCurveSet(useRealTime=True)
        self.curveSet.name = 'zoomerCurveSet'
        import trinity
        self.zoomerBinding = trinity.CreatePythonBinding(self.curveSet, self.handle, 'left', self.zoomerFrameCont, 'myLeft')
        self.curveSet.Play()
        self.handle.OnMouseDown = self.OnHandleMouseDown
        self.zoomerFrameCont.OnMouseDown = self.OnHandleMouseDown
        self.handle.OnMouseUp = self.OnHandleMouseUp
        self.zoomerFrameCont.OnMouseUp = self.OnHandleMouseUp
        self.handle.OnMouseMove = self.OnHandleMouseMove
        self.zoomerFrameCont.OnMouseMove = self.OnHandleMouseMove
        self.zoomerFrameCont.OnMouseEnter = self.OnHandleMouseEnter

    def OnMouseWheel(self, delta, *args):
        if delta < 0:
            direction = 1
        else:
            direction = -1
        self.schedulingController.AddNumHours(direction)

    def _ConstructLabel(self):
        pass

    def SetValue(self, value, *args, **kwargs):
        Slider.SetValue(self, value, *args, **kwargs)
        self.SetFill()

    def SetFill(self):
        value = self.schedulingController.GetCurrentTimeAsPercentage()
        self.sliderFillCont.width = value

    def Disable(self, *args):
        Slider.Disable(self, args)
        self.handle.state = uiconst.UI_HIDDEN

    def Enable(self, *args):
        Slider.Enable(self, args)
        self.handle.state = uiconst.UI_NORMAL

    def _OnResize(self, *args):
        if getattr(self, 'zoomerFrameCont', None):
            self.SetZoomerFrameWidth()
        if getattr(self, 'handle', None):
            self._UpdateHandlePosition(self.value)

    def SetZoomerFrameWidth(self):
        width = self.absoluteRight - self.absoluteLeft
        self.zoomerFrameCont.width = self.zoomerFramePercentage * width

    def Close(self):
        self.RemoveZoomerBinding()
        Slider.Close(self)

    def RemoveZoomerBinding(self):
        if self.zoomerBinding:
            self.curveSet.bindings.fremove(self.zoomerBinding)
            self.zoomerBinding = None
            self.curveSet = None


class Zoomer(Container):
    default_align = uiconst.TOALL
    default_state = uiconst.UI_NORMAL
    default_name = 'zoomer'
    LIGHT_FILL_COLOR = (1.0, 1.0, 1.0, 0.1)
    DARK_FILL_COLOR = (1.0, 1.0, 1.0, 0.05)
    FILL_COLORS = [LIGHT_FILL_COLOR, DARK_FILL_COLOR]

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.schedulingController = attributes.schedulingController
        barHeight = attributes.barHeight
        Frame(parent=self, color=(0.5, 0.5, 0.5, 0.2))
        SpriteThemeColored(parent=self, texturePath='res:/UI/Texture/classes/Moonmining/scheduleMarker.png', pos=(0, -10, 17, 9), align=uiconst.CENTERTOP, colorType=uiconst.COLORTYPE_UIHILIGHTGLOW, opacity=1.0, state=uiconst.UI_DISABLED)
        line = LineThemeColored(parent=self, align=uiconst.CENTERTOP, weight=2, height=barHeight, width=3, colorType=uiconst.COLORTYPE_UIHILIGHTGLOW)
        gridCont = GridContainer(name='hourGrid', parent=self, align=uiconst.TOTOP, height=barHeight, lines=1, columns=NUM_HOURS_ZOOMER)
        self.hourConts = []
        for x in xrange(NUM_HOURS_ZOOMER):
            c = Container(parent=gridCont, state=uiconst.UI_NORMAL)
            c.dayLine = Line(parent=c, align=uiconst.TOLEFT_NOPUSH, color=(1, 1, 1, 0.2))
            c.dayLine.display = False
            fillColor = self.FILL_COLORS[x % 2]
            c.fill = Fill(bgParent=c, color=fillColor)
            c.startTime = None
            c.OnClick = self.OnClick
            self.hourConts.append(c)

        currentTime = self.schedulingController.GetCurrentTime()
        self.LoadZoomer(currentTime)

    def LoadZoomer(self, currentTime):
        zoomCurrentTime = currentTime - NUM_HOURS_ZOOMER / 2 * const.HOUR
        year, month, wd, day, hour, min, sec, ms = blue.os.GetTimeParts(gametime.GetWallclockTime())
        currentWeek = datetime.date(year, month, day).isocalendar()[1]
        for i in xrange(NUM_HOURS_ZOOMER):
            year, month, wd, day, hour, min, sec, ms = blue.os.GetTimeParts(zoomCurrentTime)
            c = self.hourConts[i]
            c.startTime = zoomCurrentTime
            if hour == 0:
                c.dayLine.display = True
                self.ShowDayLabel(c, zoomCurrentTime, wd)
            else:
                c.dayLine.display = False
                self.HideDayLabel(c)
            zoomCurrentTime += const.HOUR

    def ShowDayLabel(self, parent, timestamp, wd):
        label = self.GetDayLabel(parent, create=True)
        dayName = DAY_NAME_TEXT_SHORT[wd]
        dateText = FmtDate(timestamp, fmt='ln')
        text = '%s | %s' % (dayName, dateText)
        label.text = text.upper()
        label.display = True

    def HideDayLabel(self, parent):
        label = self.GetDayLabel(parent, create=False)
        if label:
            label.display = False

    def GetDayLabel(self, parent, create = False):
        label = getattr(parent, 'dayLabel', None)
        if label or not create:
            return label
        parent.dayLabel = EveLabelSmall(name='dayLabel', parent=parent, align=uiconst.BOTTOMLEFT, text='', state=uiconst.UI_NORMAL, top=-16)
        return parent.dayLabel

    def OnSliderSetValue(self, slider):
        value = slider.GetValue()
        currentPos = value * NUM_HOURS_ZOOMER
        hoursToAdd = currentPos - NUM_HOURS_ZOOMER / 2
        hoursToAdd = int(round(hoursToAdd, 0))
        if hoursToAdd:
            self.schedulingController.AddNumHours(hoursToAdd)

    def OnMouseWheel(self, delta, *args):
        if delta < 0:
            direction = 1
        else:
            direction = -1
        self.schedulingController.AddNumHours(direction / float(PARTS_IN_HOUR), PARTS_IN_HOUR)

    def OnClick(self, *args):
        currentMouseOver = uicore.uilib.mouseOver
        if currentMouseOver in self.hourConts:
            timestamp = currentMouseOver.startTime
            self.schedulingController.SetTimestamp(timestamp)
            PlaySound(uiconst.SOUND_BUTTON_CLICK)


class ZoomerFrameCont(Container):

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)

    @apply
    def myLeft():

        def fset(self, value):
            self.left = int(value - self.width / 2)

        return property(**locals())


def GetISOWeekDay(wd):
    newWd = wd - 1
    if newWd < 0:
        newWd = 6
    return newWd
