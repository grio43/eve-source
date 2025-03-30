#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\dogmaTimeWnd.py
import datetime
import dogma.attributes.datetime
import datetimeutils
from carbonui import uiconst
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.primitives.container import Container
from carbonui.control.button import Button
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from eve.client.script.ui.control.dateSinglelineEdit import DatePickerControl, HourMinPickerControl
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from carbonui.control.window import Window
HINT_TEXT = 'Enter the date and time in the format YYYY/MM/DD - HH:MM Then click the button to update the result.'

class DogmaTimeConverterWindow(Window):
    default_windowID = 'DogmaTimeConverterWindow'
    default_name = 'DogmaTimeConverterWindow'
    default_caption = 'Dogma Datetime Converter'

    def ApplyAttributes(self, attributes):
        super(DogmaTimeConverterWindow, self).ApplyAttributes(attributes)
        self.Layout()

    def Layout(self):
        now = datetime.datetime.now()
        EveLabelMedium(parent=self.content, text=HINT_TEXT, align=uiconst.TOTOP)
        self.pickerCont = ContainerAutoSize(parent=self.content, align=uiconst.TOTOP, height=Button.default_height, padTop=8)
        self.datePicker = DatePickerControl(name='fromPicker', parent=self.pickerCont, setValue=[now.year, now.month, now.day], ranges=(0L, datetimeutils.date_to_blue(datetime.datetime.max)), fontSize=16, align=uiconst.TOLEFT)
        EveLabelMedium(parent=ContainerAutoSize(parent=self.pickerCont, align=uiconst.TOLEFT), text='-', align=uiconst.CENTER, padLeft=8, padRight=8)
        self.hourMinPicker = HourMinPickerControl(parent=self.pickerCont, setValue=(now.hour, now.minute), fontSize=16, align=uiconst.TOLEFT)
        self.button = Button(parent=self.pickerCont, align=uiconst.TOLEFT, func=self.OnButtonClick, label='Convert', padLeft=8)
        self.resultField = SingleLineEditText(parent=self.pickerCont, align=uiconst.TOLEFT, width=100, padLeft=8)
        self.ApplyWindowSize()

    def ApplyWindowSize(self):
        content_height = sum((each.height + each.padTop + each.padBottom + each.top for each in self.content.children))
        _, window_height = self.GetWindowSizeForContentSize(height=content_height)
        self.height = window_height
        self.width = 370
        self.SetMinSize([self.width, self.height], refresh=True)
        self.MakeUnResizeable()

    def LayoutOld(self):
        left = 10
        now = datetime.datetime.now()
        self.explanationCont = Container(parent=self.sr.main, align=uiconst.TOTOP, height=40)
        label = EveLabelMedium(parent=self.explanationCont, text=HINT_TEXT, align=uiconst.TOLEFT, width=340, padLeft=5)
        label.Layout()
        self.pickerCont = Container(parent=self.sr.main, align=uiconst.TOTOP, height=20)
        self.datePicker = DatePickerControl(name='fromPicker', parent=self.pickerCont, setValue=[now.year, now.month, now.day], left=left, ranges=(0L, datetimeutils.date_to_blue(datetime.datetime.max)), fontSize=16, align=uiconst.TOLEFT)
        EveLabelMedium(parent=self.pickerCont, text='-', align=uiconst.TOLEFT, width=7, padLeft=7)
        self.hourMinPicker = HourMinPickerControl(parent=self.pickerCont, left=left, setValue=(now.hour, now.minute), fontSize=16, align=uiconst.TOLEFT)
        self.button = Button(parent=self.pickerCont, align=uiconst.TOLEFT, func=self.OnButtonClick, width=100, height=20, label='Convert', padLeft=5)
        self.resultField = SingleLineEditText(parent=self.pickerCont, align=uiconst.TOLEFT, width=100, height=20, padLeft=5, top=0)

    def OnButtonClick(self, *args):
        dateStamp = self.datePicker.GetTimestamp()
        timeStamp = self.hourMinPicker.GetTimestamp()
        dateTimeStamp = dateStamp + timeStamp
        self.resultField.SetText(dogma.attributes.datetime.time_as_float(dateTimeStamp))


def OpenWindow():
    win = Window.GetIfOpen(windowID=DogmaTimeConverterWindow.default_windowID)
    if win:
        win.Show()
    else:
        DogmaTimeConverterWindow.Open()
