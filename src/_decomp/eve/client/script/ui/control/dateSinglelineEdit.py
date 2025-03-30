#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\dateSinglelineEdit.py
import calendar
import eveLocalization
from carbonui import fontconst
from carbonui.control.singlelineedits.singleLineEditInteger import SingleLineEditInteger
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from eve.client.script.ui.control.eveLabel import EveLabelSmall, Label
from carbonui.uicore import uicore
import carbonui.const as uiconst
import blue
from eve.client.script.ui.shared.fitting.fittingUtil import EatSignalChangingErrors
from localization import GetByLabel
from signals.signalUtil import ChangeSignalConnect

def _GetYearMonthDayFromTimestamp(timestamp):
    timestamp += eveLocalization.GetTimeDelta() * const.SEC
    year, month, _, day, _, _, _, _ = blue.os.GetTimeParts(timestamp)
    return (year, month, day)


def _GetTimestampFromYearMonthDay(endOfDay, yearValue, monthValue, dayValue):
    try:
        if endOfDay:
            timestamp = blue.os.GetTimeFromParts(yearValue, monthValue, dayValue, 23, 59, 59, 0)
        else:
            timestamp = blue.os.GetTimeFromParts(yearValue, monthValue, dayValue, 0, 0, 0, 0)
    except StandardError:
        timestamp = 0

    timestamp -= eveLocalization.GetTimeDelta() * const.SEC
    return timestamp


def _GetHourMinuteFromTimestamp(timestamp):
    timestamp += eveLocalization.GetTimeDelta() * const.SEC
    _, _, _, _, hour, minute, _, _ = blue.os.GetTimeParts(timestamp)
    return (hour, minute)


def _GetTimestampFromHourMinute(hourValue, minuteValue):
    timestamp = hourValue * const.HOUR + minuteValue * const.MIN
    timestamp -= eveLocalization.GetTimeDelta() * const.SEC
    return timestamp


class DateSinglelineEdit(SingleLineEditInteger):
    __guid__ = 'DateSinglelineEdit'
    default_width = 100
    default_left = 0
    default_top = 0
    default_textLeftMargin = 2
    default_textRightMargin = 2

    def ApplyAttributes(self, attributes):
        maxLength = attributes.get('maxLength', 0)
        self.numberFormatter = '{0:0>%s}' % maxLength
        super(DateSinglelineEdit, self).ApplyAttributes(attributes)
        self._textClipper.padLeft = 0
        self._textClipper.padRight = 0

    def ConstructBackground(self):
        pass

    def SetText(self, text, *args, **kwargs):
        if uicore.registry.GetFocus() is not self:
            text = self.GetAdjustedText(text) or text
        return super(DateSinglelineEdit, self).SetText(text)

    def FormatNumeric(self, otext, useGrouping = True, decimalPlaces = 0, leadingZeroes = 0):
        leadingZeroes = 2
        return super(DateSinglelineEdit, self).FormatNumeric(otext, useGrouping=False, decimalPlaces=decimalPlaces, leadingZeroes=leadingZeroes)

    def ShowNumericControls(self):
        pass

    def BlinkButtons(self, val):
        pass

    def RefreshTextClipper(self):
        pass

    def OnKillFocus(self, *args):
        super(DateSinglelineEdit, self).OnKillFocus(*args)
        self.AdjustValue()

    def AdjustValue(self):
        text = self.GetAdjustedText(self.GetText())
        if text is None:
            return
        self.SetText(text)

    def GetAdjustedText(self, textToAdjust):
        if not textToAdjust and textToAdjust != 0:
            return
        text = self.numberFormatter.format(textToAdjust)
        return text

    def OnKeyDown(self, vkey, flag):
        index = self.caretIndex[0]
        if vkey == uiconst.VK_LEFT:
            if index - 1 < 0:
                uicore.registry.FindFocus(-1)
                return
        elif vkey == uiconst.VK_RIGHT:
            if index + 1 > len(self.text):
                uicore.registry.FindFocus(1)
                return
        super(DateSinglelineEdit, self).OnKeyDown(vkey, flag)


class DatePickerControl(ContainerAutoSize):
    default_height = 18
    default_align = uiconst.TOPLEFT

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        fontSize = attributes.fontSize or fontconst.DEFAULT_FONTSIZE
        self.rangeStartTime = attributes.ranges[0]
        self.rangeStopTime = attributes.ranges[1]
        self.isEndField = attributes.get('isEndField', False)
        self.onEditFieldChangedFunc = attributes.get('OnEditFieldChanged', None)
        value = attributes.setValue
        background = SingleLineEditText(bgParent=self, padTop=0, padBottom=-1)
        minYear, maxYear = self.GetAvailableYears()
        self.yearEdit = DateSinglelineEdit(name='yearEdit', parent=self, align=uiconst.TOLEFT, minValue=minYear, maxValue=maxYear, setvalue=value[0], OnFocusLost=self.ApplyChanges, OnReturn=self.ApplyChanges, fontsize=fontSize)
        textMargins = DateSinglelineEdit.default_textLeftMargin + DateSinglelineEdit.default_textRightMargin - 1
        textWidth, textHeight = Label.MeasureTextSize('0000', fontsize=fontSize)
        self.yearEdit.width = textWidth + textMargins
        self.yearEdit.ChangeNumericValue = lambda x: self.ChangeNumericValue(self.yearEdit, x)
        self.yearEdit.background.display = False
        dot1 = ContainerAutoSize(name='dot1', parent=self, align=uiconst.TOLEFT)
        Label(parent=dot1, text='.', align=uiconst.CENTERLEFT, top=0, fontsize=fontSize)
        self.monthEdit = DateSinglelineEdit(name='monthEdit', parent=self, align=uiconst.TOLEFT, minValue=1, maxValue=12, setvalue=value[1], OnFocusLost=self.ApplyChanges, OnReturn=self.ApplyChanges, fontsize=fontSize)
        textWidth, textHeight = Label.MeasureTextSize('00', fontsize=fontSize)
        self.monthEdit.width = textWidth + textMargins
        self.monthEdit.ChangeNumericValue = lambda x: self.ChangeNumericValue(self.monthEdit, x)
        dot2 = ContainerAutoSize(name='dot2', parent=self, align=uiconst.TOLEFT)
        Label(parent=dot2, text='.', align=uiconst.CENTERLEFT, top=0, fontsize=fontSize)
        self.dayEdit = DateSinglelineEdit(name='dayEdit', parent=self, align=uiconst.TOLEFT, minValue=1, maxValue=31, setvalue=value[2], OnFocusLost=self.ApplyChanges, OnReturn=self.ApplyChanges, fontsize=fontSize)
        self.dayEdit.width = textWidth + textMargins
        self.dayEdit.ChangeNumericValue = lambda x: self.ChangeNumericValue(self.dayEdit, x)

    def ChangeNumericValue(self, editField, val):
        if editField != self.dayEdit:
            DateSinglelineEdit.ChangeNumericValue(editField, val)
            self.ApplyChanges()
            return
        if uicore.uilib.Key(uiconst.VK_CONTROL):
            val *= 10
        if val > 0:
            val = max(1, long(val))
        else:
            val = min(-1, long(val))
        current = editField.GetValue()
        new = current + val
        if editField.minValue <= new <= editField.maxValue:
            DateSinglelineEdit.ChangeNumericValue(editField, val)
            self.ApplyChanges()
            return
        currentTimestamp = self.GetTimestamp()
        newTimestamp = currentTimestamp + val * const.DAY
        self.SetPickerValueFromTimestamp(newTimestamp)
        self.ApplyChanges()

    def GetAvailableYears(self):
        startYear, _, _ = _GetYearMonthDayFromTimestamp(self.rangeStartTime)
        endYear, _, _ = _GetYearMonthDayFromTimestamp(self.rangeStopTime)
        if endYear < startYear:
            return [startYear, startYear]
        return [startYear, endYear]

    def SetPickerValueFromTimestamp(self, timestamp):
        year, month, day = _GetYearMonthDayFromTimestamp(timestamp)
        self.SetPickerValue(year, month, day)

    def SetPickerValue(self, year, month, day):
        self.yearEdit.SetText(year)
        self.monthEdit.SetText(month)
        self.dayEdit.SetText(day)

    def ApplyChanges(self, *args):
        self.CorrectFieldBoundaries()
        if self.AreInvalidFieldsInTransition():
            return
        if not self.AreTimestampsInRange():
            self.CorrectFields()
        if self.onEditFieldChangedFunc:
            self.onEditFieldChangedFunc(self, None, None)
        self.CheckAreFieldsValidAndCorrectThem()

    def CorrectFieldBoundaries(self):
        yearValue = self.yearEdit.GetValue() or self.yearEdit.minValue
        monthValue = self.monthEdit.GetValue() or self.monthEdit.minValue
        firstday, numdays = calendar.monthrange(yearValue, monthValue)
        if self.dayEdit.maxValue != numdays:
            self.dayEdit.SetMaxValue(numdays)
            self.dayEdit.ClampMinMaxValue()

    def AreInvalidFieldsInTransition(self):
        timeStamp = self.GetTimestamp()
        if timeStamp is None:
            return True
        return False

    def AreTimestampsInRange(self):
        timeStamp = self.GetTimestamp()
        rangeStartTime = self.GetMinStartTime()
        if rangeStartTime > timeStamp:
            return False
        rangeStopTime = self.GetMaxEndTime()
        if rangeStopTime < timeStamp:
            return False
        return True

    def GetMaxEndTime(self):
        rangeStopTime = self.rangeStopTime - const.DAY if not self.isEndField else self.rangeStopTime
        return rangeStopTime

    def GetMinStartTime(self):
        rangeStartTime = self.rangeStartTime + const.DAY if self.isEndField else self.rangeStartTime
        return rangeStartTime

    def CorrectFields(self):
        timeStamp = self.GetTimestamp()
        rangeStartTime = self.GetMinStartTime()
        if rangeStartTime > timeStamp:
            year, month, day = _GetYearMonthDayFromTimestamp(rangeStartTime)
            self.SetPickerValue(year, month, day)
            return
        rangeStopTime = self.GetMaxEndTime()
        if rangeStopTime < timeStamp:
            year, month, day = _GetYearMonthDayFromTimestamp(rangeStopTime)
            self.SetPickerValue(year, month, day)
            return

    def CheckAreFieldsValidAndCorrectThem(self):
        if not self.AreTimestampsInRange():
            self.CorrectFields()

    def GetTimestamp(self):
        yearValue = self.yearEdit.GetValue() or self.yearEdit.minValue
        monthValue = self.monthEdit.GetValue() or self.monthEdit.minValue
        dayValue = self.dayEdit.GetValue() or self.dayEdit.minValue
        timestamp = _GetTimestampFromYearMonthDay(self.isEndField, yearValue, monthValue, dayValue)
        return timestamp


class HourMinPickerControl(Container):
    default_height = 18
    default_align = uiconst.TOPLEFT

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        fontSize = attributes.fontSize or fontconst.DEFAULT_FONTSIZE
        self.onEditFieldChangedFunc = attributes.get('OnEditFieldChanged', None)
        self.onEditFieldRolledOverFunc = attributes.get('onEditFieldRolledOverFunc', None)
        value = attributes.setValue
        background = SingleLineEditText(bgParent=self, padTop=0, padBottom=-1)
        textMargins = DateSinglelineEdit.default_textLeftMargin + DateSinglelineEdit.default_textRightMargin - 1
        self.hourEdit = DateSinglelineEdit(name='hourEdit', parent=self, align=uiconst.TOLEFT, width=36, ints=[0, 23], maxLength=2, setvalue=value[0], OnFocusLost=self.ApplyChanges, OnReturn=self.ApplyChanges, fontsize=fontSize)
        textWidth, textHeight = Label.MeasureTextSize('00', fontsize=fontSize)
        self.hourEdit.width = textWidth + textMargins
        self.hourEdit.ChangeNumericValue = lambda x: self.ChangeNumericValue(self.hourEdit, x)
        self.hourEdit.background.display = False
        dot1 = ContainerAutoSize(name='dot2', parent=self, align=uiconst.TOLEFT)
        Label(parent=dot1, text=':', align=uiconst.CENTERLEFT, top=-2, fontsize=fontSize)
        self.minEdit = DateSinglelineEdit(name='minEdit', parent=self, align=uiconst.TOLEFT, width=20, maxLength=2, ints=[0, 59], setvalue=value[1], OnFocusLost=self.ApplyChanges, OnReturn=self.ApplyChanges, fontsize=fontSize)
        self.minEdit.width = textWidth + textMargins
        self.minEdit.ChangeNumericValue = lambda x: self.ChangeNumericValue(self.minEdit, x)
        self.width = self.hourEdit.width + self.minEdit.width + 3

    def ApplyChanges(self, *args):
        if self.onEditFieldChangedFunc:
            self.onEditFieldChangedFunc()

    def GetTimestamp(self):
        hourValue = self.hourEdit.GetValue() or self.hourEdit.minValue
        minuteValue = self.minEdit.GetValue() or self.minEdit.minValue
        timestamp = _GetTimestampFromHourMinute(hourValue, minuteValue)
        return timestamp

    def ChangeNumericValue(self, editField, val):
        if uicore.uilib.Key(uiconst.VK_CONTROL):
            val *= 10
        if val > 0:
            val = max(1, long(val))
        else:
            val = min(-1, long(val))
        if editField == self.minEdit:
            val *= 30
        current = editField.GetValue()
        new = current + val
        if not self.onEditFieldRolledOverFunc or editField.minValue <= new <= editField.maxValue:
            DateSinglelineEdit.ChangeNumericValue(editField, val)
            self.ApplyChanges()
            return
        currentTimestamp = self.GetTimestamp()
        if editField == self.hourEdit:
            newTimestamp = currentTimestamp + val * const.HOUR
        else:
            newTimestamp = currentTimestamp + val * const.MIN
        self.onEditFieldRolledOverFunc(newTimestamp)

    def SetPickerValue(self, hour, minute):
        self.hourEdit.SetText(hour)
        self.minEdit.SetText(minute)

    def SetPickerValueFromTimestamp(self, timestamp):
        hour, minute = _GetHourMinuteFromTimestamp(timestamp)
        self.SetPickerValue(hour, minute)


class DateRangePicker(Container):

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.sliderController = attributes.sliderController
        labelPaths = attributes.labelPaths
        fromTime = attributes.fromTime
        toTime = attributes.toTime
        ranges = self.sliderController.GetDataRange()
        fyear, fmonth, _, fday, _, _, _, _ = blue.os.GetTimeParts(fromTime)
        tyear, tmonth, _, tday, _, _, _, _ = blue.os.GetTimeParts(toTime)
        beforeText = GetByLabel(labelPaths[0])
        rangeLabel = EveLabelSmall(parent=self, text=beforeText, align=uiconst.TOPLEFT, top=5, left=0)
        left = rangeLabel.left + rangeLabel.textwidth + 10
        self.fromPicker = DatePickerControl(name='fromPicker', parent=self, OnEditFieldChanged=self.OnEditFieldChanged, setValue=[fyear, fmonth, fday], top=2, left=left, ranges=ranges)
        self.fromPicker.SetSizeAutomatically()
        left = self.fromPicker.left + self.fromPicker.width + 4
        betweenText = GetByLabel(labelPaths[1])
        toLabel = EveLabelSmall(parent=self, text=betweenText, align=uiconst.TOPLEFT, top=5, left=left)
        left = toLabel.left + toLabel.textwidth + 4
        self.toPicker = DatePickerControl(name='toPicker', parent=self, left=left, OnEditFieldChanged=self.OnEditFieldChanged, setValue=[tyear, tmonth, tday], top=2, ranges=ranges, isEndField=True)
        left = self.toPicker.left + self.toPicker.width + 4
        text = GetByLabel('UI/Common/InvalidRange')
        self.validLabel = EveLabelSmall(parent=self, text=text.upper(), align=uiconst.TOPLEFT, top=5, left=left)
        self.validLabel.SetRGBA(1, 0, 0, 0.75)
        self.validLabel.display = False
        self.ChangeSignalConnection()

    def ChangeSignalConnection(self, connect = True):
        signalAndCallback = [(self.sliderController.on_change, self.SetVisibleRange)]
        ChangeSignalConnect(signalAndCallback, connect)

    def OnEditFieldChanged(self, picker, editField, text):
        fromTimestamp = self.fromPicker.GetTimestamp()
        toTimeStamp = self.toPicker.GetTimestamp()
        if fromTimestamp and toTimeStamp:
            self.sliderController.SetVisibleRange((fromTimestamp, toTimeStamp))

    def SetVisibleRange(self):
        fromValues, fromTime, toValues, toTime = self.GetVisibleRangeTimeParts()
        self.fromPicker.SetPickerValue(*fromValues)
        self.toPicker.SetPickerValue(*toValues)
        if fromTime >= toTime:
            self.validLabel.display = True
        else:
            self.validLabel.display = False

    def GetVisibleRangeTimeParts(self):
        fromTime, toTime = self.sliderController.GetVisibleRange()
        fyear, fmonth, _, fday, _, _, _, _ = blue.os.GetTimeParts(fromTime)
        tyear, tmonth, _, tday, _, _, _, _ = blue.os.GetTimeParts(toTime)
        return ([fyear, fmonth, fday],
         fromTime,
         [tyear, tmonth, tday],
         toTime)

    def Close(self):
        with EatSignalChangingErrors(errorMsg='DateRangePicker'):
            self.ChangeSignalConnection(connect=False)
        Container.Close(self)
