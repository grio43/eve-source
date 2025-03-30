#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\client\script\util\timeControl.py
import blue
import trinity
from carbonui import uiconst
from carbonui.control.singlelineedits.singleLineEditFloat import SingleLineEditFloat
from carbonui.control.singlelineedits.singleLineEditInteger import SingleLineEditInteger
from carbonui.primitives.container import Container
from carbonui.primitives.line import Line
from carbonui.control.checkbox import Checkbox
from carbonui.control.radioButton import RadioButton
from eve.client.script.ui.control.eveLabel import Label
from carbonui.control.window import Window

class TimeControlWindow(Window):
    default_width = 300
    default_height = 250
    default_caption = 'Time Control Window'
    default_minSize = (300, 250)
    default_windowID = 'TimeControlWindow'
    showTimeGraphs = False

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.topCont = Container(parent=self.GetMainArea(), name='topCont', align=uiconst.TOTOP, height=200)
        self.topLeftCont = Container(parent=self.topCont, name='topLeftCont', align=uiconst.TOLEFT, width=120, padding=(3, 20, 3, 3))
        self.topRightCont = Container(parent=self.topCont, name='topRightCont', align=uiconst.TOALL, padding=(3, 10, 3, 3))
        self.mainCont = Container(parent=self.GetMainArea(), name='mainCont')
        self.ConstructTopLeftCont()
        self.ConstructTopRightCont()

    def ConstructTopLeftCont(self):
        Line(parent=self.topLeftCont, align=uiconst.TORIGHT)
        Label(parent=self.topLeftCont, text='Select clock:', align=uiconst.TOTOP)
        RadioButton(parent=self.topLeftCont, text='Actual', groupname='clockGroup', align=uiconst.TOTOP, checked=not blue.os.useSmoothedDeltaT, callback=self.OnClockRadioButtonsChanged, retval=False)
        RadioButton(parent=self.topLeftCont, text='Smoothed', groupname='clockGroup', align=uiconst.TOTOP, checked=blue.os.useSmoothedDeltaT, callback=self.OnClockRadioButtonsChanged, retval=True)
        Label(parent=self.topLeftCont, align=uiconst.TOTOP, text='Time Scaler:', pos=(0, 0, 0, 0))
        SingleLineEditFloat(parent=self.topLeftCont, name='timeScaler', align=uiconst.TOTOP, maxValue=100.0, setvalue=blue.os.timeScaler, OnChange=self.OnTimeScalerChanged, pos=(0, 0, 20, 12))

    def OnTimeScalerChanged(self, value):
        if value:
            blue.os.timeScaler = float(value)

    def OnClockRadioButtonsChanged(self, button):
        blue.os.useSmoothedDeltaT = button.data['value']

    def ConstructTopRightCont(self):
        cont = Container(parent=self.topRightCont, align=uiconst.TOTOP, height=70, padTop=12, padBottom=10)
        Label(parent=cont, align=uiconst.TOTOP, text='Slug Min Time:', pos=(0, 0, 0, 0))
        SingleLineEditInteger(parent=cont, name='slugMinEdit', align=uiconst.TOTOP, maxValue=1000, setvalue=int(blue.os.slugTimeMinMs), OnChange=self.OnSlugMinChanged, pos=(0, 0, 100, 12))
        Label(parent=cont, align=uiconst.TOTOP, text='Slug Max Time:', pos=(0, 0, 0, 0))
        SingleLineEditInteger(parent=cont, name='slugMaxEdit', align=uiconst.TOTOP, maxValue=1000, setvalue=int(blue.os.slugTimeMaxMs), OnChange=self.OnSlugMaxChanged, pos=(0, 0, 100, 12))
        Checkbox(parent=self.topRightCont, text='Show Time Graphs', align=uiconst.TOTOP, checked=self.showTimeGraphs, callback=self.OnTimeGraphsChanged, padBottom=10)

    def OnSlugMinChanged(self, value):
        if value:
            blue.os.slugTimeMinMs = float(value)

    def OnSlugMaxChanged(self, value):
        if value:
            blue.os.slugTimeMaxMs = float(value)

    def OnTimeGraphsChanged(self, checkBox):
        print 'OnTimeGraphsChanged', checkBox
        timerList = ['Blue/actualDeltaT', 'Blue/smoothedDeltaT', 'Blue/usedDeltaT']
        if checkBox.GetValue():
            trinity.graphs.SetEnabled(True)
            fn = trinity.graphs.AddGraph
            seq = timerList
        else:
            fn = trinity.graphs.RemoveGraph
            seq = reversed(timerList)
        map(fn, seq)
        self.showTimeGraphs = checkBox.GetValue()
