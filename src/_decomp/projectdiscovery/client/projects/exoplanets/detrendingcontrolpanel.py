#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\exoplanets\detrendingcontrolpanel.py
import carbonui.const as uiconst
from carbonui.control.slider import Slider
from carbonui.primitives.container import Container
from carbonui.control.checkbox import Checkbox
import localization

class DetrendingControlPanel(Container):
    default_width = 300
    default_height = 20
    __notifyevents__ = ['OnDataLoaded', 'OnDisableDetrend', 'OnEnableDetrend']

    def ApplyAttributes(self, attributes):
        super(DetrendingControlPanel, self).ApplyAttributes(attributes)
        self._window_value_map = {7: '1',
         35: '5',
         71: '10',
         169: '24'}
        self.setup_layout()
        self._previous_window_size = self.granularitySlider.GetValue()
        self._prev_detrend_state = self._checkbox.GetValue()
        self.OnDisableDetrend()
        sm.RegisterNotify(self)

    def setup_layout(self):
        self._checkbox = Checkbox(name='DetrendCheck', parent=self, align=uiconst.TOLEFT, width=60, text=localization.GetByLabel('UI/ProjectDiscovery/exoplanets/DetrendLabel'), checked=False, callback=self.detrend, hint=localization.GetByLabel('UI/ProjectDiscovery/exoplanets/DetrendTooltip'))
        self._controls_container = Container(name='ControlsContainer', parent=self, align=uiconst.TOLEFT, width=100, padLeft=10, padRight=10, state=uiconst.UI_HIDDEN)
        self.granularitySlider = Slider(name='granularitySlider', parent=self._controls_container, align=uiconst.TOPLEFT, minValue=7, maxValue=169, width=100, increments=[7,
         35,
         71,
         169], value=71, callback=self.detrend)

    def OnDisableDetrend(self):
        self.Disable()

    def OnEnableDetrend(self):
        self.Enable()

    def OnDataLoaded(self, *args, **kwargs):
        self.initialize()

    def detrend(self, *args, **kwargs):
        self._controls_container.state = uiconst.UI_NORMAL if self._checkbox.GetValue() else uiconst.UI_HIDDEN
        if self.granularitySlider.GetValue() != self._previous_window_size or self._prev_detrend_state != self._checkbox.GetValue():
            self._previous_window_size = self.granularitySlider.GetValue()
            self._prev_detrend_state = self._checkbox.GetValue()
            sm.ScatterEvent('OnDetrend', self._checkbox.GetValue(), self.granularitySlider.GetValue())
        self._set_window_label()

    def _set_window_label(self):
        setting = self._window_value_map[self.granularitySlider.GetValue()]
        text = localization.GetByLabel('UI/ProjectDiscovery/exoplanets/GranularitySetting', setting=setting)
        self.granularitySlider.SetLabel(text)

    def _set_iterations_label(self, label, id, text, value):
        label.text = localization.GetByLabel('UI/ProjectDiscovery/exoplanets/IterationSetting', setting=value)

    def initialize(self):
        self.granularitySlider.SetValue(71)
        self._checkbox.SetChecked(False)
