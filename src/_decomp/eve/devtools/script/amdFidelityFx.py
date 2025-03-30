#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\amdFidelityFx.py
import trinity
from carbonui.control.singlelineedits.singleLineEditFloat import SingleLineEditFloat
from carbonui.primitives.containerAutoSize import ContainerAutoSize
import carbonui.const as uiconst
from carbonui.control.window import Window
from carbonui.control.button import Button
from eve.client.script.ui.control.eveLabel import EveHeaderSmall
from carbonui.control.checkbox import Checkbox

class FidelityFXWindow(Window):
    default_caption = 'FidelityFX'
    default_windowID = 'FidelityFXWindow'
    default_width = 260
    default_height = 220
    default_minSize = (260, 220)
    default_maxSize = (260, 220)
    __notifyevents__ = ['OnSessionChanged']

    def __init__(self, **kw):
        self.cachedFidelityFx = None
        self.fsrEnabled = False
        self.useRcas = False
        self.slowFSR = False
        self.fsrSharpness = 0.0
        self.upsamplingFactor = 1.0
        self.enabledCheckbox = None
        self.rcasCheckbox = None
        self.slowCheckbox = None
        self.sharpnessInput = None
        self.upsamplingInput = None
        super(FidelityFXWindow, self).__init__(**kw)
        self.MakeUnResizeable()
        sm.RegisterNotify(self)

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.CacheFidelityFX()
        self.GetValuesFromEffect(self.cachedFidelityFx)
        self.Layout()

    def GetValuesFromEffect(self, fx):
        self.fsrEnabled = getattr(fx, 'fsrEnabled', False)
        self.useRcas = getattr(fx, 'useRcas', False)
        self.slowFSR = getattr(fx, 'slowFSR', False)
        self.fsrSharpness = getattr(fx, 'sharpness', 0.0)
        self.upsamplingFactor = getattr(fx, 'upsamplingFactor', 1.0)
        if self.enabledCheckbox:
            self.enabledCheckbox.SetValue(self.fsrEnabled)
            self.rcasCheckbox.SetValue(self.useRcas)
            self.slowCheckbox.SetValue(self.slowFSR)
            self.sharpnessInput.SetValue(self.fsrSharpness)
            self.upsamplingInput.SetValue(self.upsamplingFactor)

    def CacheFidelityFX(self):
        scene = self.GetScene()
        self.cachedFidelityFx = getattr(scene.postprocess, 'fidelityFX', None)
        newfx = trinity.Tr2PPFidelityFXEffect()
        newfx.fsrEnabled = self.fsrEnabled
        newfx.useRcas = self.useRcas
        newfx.slowFSR = self.slowFSR
        newfx.sharpness = self.fsrSharpness
        newfx.upsamplingFactor = self.upsamplingFactor
        scene.postprocess.fidelityFX = newfx

    def OnSessionChanged(self, isRemote, sess, change):
        self.CacheFidelityFX()
        self.ApplyToScene(True)

    def GetScene(self):
        return sm.GetService('sceneManager').GetActiveScene()

    def ApplyToScene(self, resetBackbuffers = False):
        scene = self.GetScene()
        if not scene:
            print 'No scene...'
            return
        if not scene.postprocess:
            scene.postprocess = trinity.Tr2PostProcess2()
        fidelityFx = scene.postprocess.fidelityFX
        fidelityFx.fsrEnabled = self.fsrEnabled
        fidelityFx.useRcas = self.useRcas
        fidelityFx.slowFSR = self.slowFSR
        fidelityFx.sharpness = self.fsrSharpness
        fidelityFx.upsamplingFactor = self.upsamplingFactor
        fidelityFx.hdr = False
        if resetBackbuffers:
            rj = sm.GetService('sceneManager').fisRenderJob
            rj.SetSettingsBasedOnPerformancePreferences()

    def Layout(self):
        self.SetMinSize([260, 370])
        self.main_container = ContainerAutoSize(parent=self.content, align=uiconst.TOTOP)
        self.enabledCheckbox = Checkbox(parent=self.main_container, text=u'FSR Enabled', align=uiconst.TOTOP, checked=self.fsrEnabled, callback=self.OnToggled)
        self.rcasCheckbox = Checkbox(parent=self.main_container, text=u'RCAS Enabled', align=uiconst.TOTOP, checked=self.useRcas, callback=self.OnRcasToggled)
        self.slowCheckbox = Checkbox(parent=self.main_container, text=u'Slow Mode', align=uiconst.TOTOP, checked=self.slowFSR, callback=self.OnSlowToggled)
        self.sharpnessInput = SingleLineEditFloat(name='sharpness', parent=self.main_container, align=uiconst.TOTOP, padTop=24, setvalue='%s' % self.fsrSharpness, minValue=0.0, maxValue=float(1.0), decimalPlaces=2, OnChange=self.OnSharpnessChanged, OnReturn=self.OnSharpnessReturn, label='Sharpness')
        self.upsamplingInput = SingleLineEditFloat(name='upsampling', parent=self.main_container, align=uiconst.TOTOP, padTop=24, setvalue='%s' % self.upsamplingFactor, minValue=1.0, maxValue=float(4.0), decimalPlaces=2, OnChange=self.OnUpsamplingChanged, OnReturn=self.OnUpsamplingReturn, label='Upsampling')
        Button(parent=self.content, label='Reset', align=uiconst.CENTERBOTTOM, func=self.OnResetClicked)

    def OnToggled(self, cb):
        self.fsrEnabled = bool(cb.GetValue())
        self.ApplyToScene(resetBackbuffers=True)

    def OnRcasToggled(self, cb):
        self.useRcas = bool(cb.GetValue())
        self.ApplyToScene()

    def OnSlowToggled(self, cb):
        self.slowFSR = cb.GetValue()
        self.ApplyToScene()

    def OnSharpnessChanged(self, input):
        self.fsrSharpness = float(self.sharpnessInput.GetValue())
        self.ApplyToScene()

    def OnSharpnessReturn(self, *args):
        self.fsrSharpness = float(self.sharpnessInput.GetValue())
        self.ApplyToScene()

    def OnUpsamplingChanged(self, input):
        self.upsamplingFactor = float(self.upsamplingInput.GetValue())
        self.ApplyToScene(resetBackbuffers=True)

    def OnUpsamplingReturn(self, *args):
        self.upsamplingFactor = float(self.upsamplingInput.GetValue())
        self.ApplyToScene(resetBackbuffers=True)

    def OnResetClicked(self, _):
        self.GetValuesFromEffect(self.cachedFidelityFx)
        self.ApplyToScene(resetBackbuffers=True)

    def _AddHeader(self, text):
        return EveHeaderSmall(parent=self.main_container, text=text, align=uiconst.TOTOP, padding=(0, 0, 0, 0))
