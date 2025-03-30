#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\telemetrypanel.py
import blue
import uthread
from carbonui import uiconst
from carbonui.control.singlelineedits.singleLineEditFloat import SingleLineEditFloat
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.control.button import Button
from carbonui.control.checkbox import Checkbox
from eve.client.script.ui.control.eveLabel import Label
from carbonui.control.window import Window

class TelemetryPanel(Window):
    __guid__ = 'form.TelemetryPanel'
    default_caption = 'Telemetry Panel'
    default_minSize = (500, 260)
    default_windowID = 'telemetrypanel'

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        optionsContainer = LayoutGrid(parent=self.sr.main, align=uiconst.TOTOP, height=60, padding=10, columns=4, cellPadding=5)
        self.cppCaptureChk = Checkbox(parent=optionsContainer, align=uiconst.TOPLEFT, text='C++ capture', width=120, checked=blue.statistics.isCppCaptureEnabled, callback=self._OnCppCaptureChk)
        self.taskletCaptureChk = Checkbox(parent=optionsContainer, align=uiconst.TOPLEFT, text='Tasklet capture', width=120, checked=blue.statistics.isTaskletCaptureEnabled, callback=self._OnTaskletCaptureChk)
        self.pythonCaptureChk = Checkbox(parent=optionsContainer, align=uiconst.TOPLEFT, text='Python capture', width=120, checked=blue.statistics.isPythonCaptureEnabled, callback=self._OnPythonCaptureChk)
        self.taskletTimersChk = Checkbox(parent=optionsContainer, align=uiconst.TOPLEFT, text='Tasklet timers', width=120, checked=True)
        self.timedCaptureChk = Checkbox(parent=optionsContainer, align=uiconst.TOPLEFT, text='Timed capture', width=120, checked=False, callback=self._OnTimedCaptureChk)
        self.durationEdit = SingleLineEditFloat(parent=optionsContainer, label='Duration:', minValue=0.1, maxValue=10.0)
        self.durationEdit.Disable()
        if blue.pyos.markupZonesInPython:
            msg = 'Python Telemetry markup enabled'
        else:
            msg = 'Python Telemetry markup is NOT enabled'
        Label(parent=self.sr.main, align=uiconst.TOBOTTOM, text=msg, padding=10)
        buttonContainer = LayoutGrid(parent=self.sr.main, align=uiconst.TOALL, columns=4, cellPadding=4, cellSpacing=10, padding=10)
        self.startBtn = Button(parent=buttonContainer, label='Start', func=self._Start, fixedwidth=80, fixedheight=60)
        self.stopBtn = Button(parent=buttonContainer, label='Stop', func=self._Stop, fixedwidth=80, fixedheight=60)
        self.pauseBtn = Button(parent=buttonContainer, label='Pause', func=self._Pause, fixedwidth=80, fixedheight=60)
        self.resumeBtn = Button(parent=buttonContainer, label='Resume', func=self._Resume, fixedwidth=80, fixedheight=60)
        uthread.new(self._CheckStatus)

    def _OnCppCaptureChk(self, checkbox):
        blue.statistics.isCppCaptureEnabled = checkbox.GetValue()

    def _OnTaskletCaptureChk(self, checkbox):
        blue.statistics.isTaskletCaptureEnabled = checkbox.GetValue()

    def _OnPythonCaptureChk(self, checkbox):
        blue.statistics.isPythonCaptureEnabled = checkbox.GetValue()

    def _OnTimedCaptureChk(self, checkbox):
        if checkbox.GetValue():
            self.durationEdit.Enable()
        else:
            self.durationEdit.Disable()

    def _Start(self, args):
        if self.taskletTimersChk.GetValue():
            blue.pyos.taskletTimer.telemetryOn = True
        if self.timedCaptureChk.GetValue():
            duration = float(self.durationEdit.text)
            print 'Starting Telemetry timed capture (%4.2f seconds)' % duration
            blue.statistics.StartTimedTelemetry('localhost', duration)
        else:
            print 'Starting Telemetry'
            blue.statistics.StartTelemetry('localhost')

    def _Stop(self, args):
        print 'Stopping Telemetry'
        blue.statistics.StopTelemetry()
        blue.pyos.taskletTimer.telemetryOn = False

    def _Pause(self, args):
        print 'Pausing Telemetry'
        blue.statistics.PauseTelemetry()

    def _Resume(self, args):
        print 'Resuming Telemetry'
        blue.statistics.ResumeTelemetry()

    def _CheckStatus(self):
        while not self.destroyed:
            self.cppCaptureChk.SetChecked(blue.statistics.isCppCaptureEnabled, report=False)
            if blue.statistics.isTelemetryConnected:
                self.startBtn.Disable()
                self.stopBtn.Enable()
                if blue.statistics.isTelemetryPaused:
                    self.pauseBtn.Disable()
                    self.resumeBtn.Enable()
                else:
                    self.pauseBtn.Enable()
                    self.resumeBtn.Disable()
            else:
                self.startBtn.Enable()
                self.stopBtn.Disable()
                self.pauseBtn.Disable()
                self.resumeBtn.Disable()
                blue.pyos.taskletTimer.telemetryOn = False
            blue.synchro.SleepWallclock(500)
