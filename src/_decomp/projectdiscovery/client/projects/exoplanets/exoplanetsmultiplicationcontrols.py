#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\exoplanets\exoplanetsmultiplicationcontrols.py
from carbonui.control.singlelineedits.singleLineEditInteger import SingleLineEditInteger
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.button.group import ButtonGroup
from projectdiscovery.client.projects.exoplanets.exoplanetsutil import markers
import carbonui.const as uiconst
import localization

class ExoPlanetsMultiplicationControls(ContainerAutoSize):
    __notifyevents__ = []
    MIN_VALUE = 1
    MAX_VALUE = 99

    def ApplyAttributes(self, attributes):
        self._multiply_button = None
        self._divide_button = None
        self._minimum_period = markers.MINIMUM_PERIOD
        self._maximum_period = attributes.get('maximumPeriod', self._minimum_period)
        self._transit_selection_tool = attributes.get('transitSelectionTool')
        super(ExoPlanetsMultiplicationControls, self).ApplyAttributes(attributes)
        self._setup_layout()
        sm.RegisterNotify(self)

    def _setup_layout(self):
        self._number_edit = SingleLineEditInteger(name='numberInput', parent=self, align=uiconst.CENTERLEFT, width=35, setvalue='2', minValue=self.MIN_VALUE, maxValue=self.MAX_VALUE, OnReturn=self._on_line_edit, OnChange=self._update_button_states)
        self._button_group = ButtonGroup(name='ButtonGroup', parent=self, align=uiconst.CENTERLEFT, left=40, top=2)
        self._button_group.AddButton(localization.GetByLabel('UI/ProjectDiscovery/exoplanets/Multiply'), self._multiply)
        self._button_group.AddButton(localization.GetByLabel('UI/ProjectDiscovery/exoplanets/Divide'), self._divide)
        self._multiply_button = self._button_group.buttons[0]
        self._divide_button = self._button_group.buttons[1]

    def _on_line_edit(self, *args, **kwargs):
        self._number_edit.SetValue(self._get_multiplier())

    def _get_multiplier(self):
        value = int(self._number_edit.GetValue())
        return min(max(value, self.MIN_VALUE), self.MAX_VALUE)

    def _multiply(self, *args):
        period = self._transit_selection_tool.get_current_selection().get_period_length()
        if period:
            self._transit_selection_tool.set_orbital_period_of_current_selection(period * self._get_multiplier())
        self._update_button_states()

    def _divide(self, *args):
        period = self._transit_selection_tool.get_current_selection().get_period_length()
        if period:
            self._transit_selection_tool.set_orbital_period_of_current_selection(period / self._get_multiplier())
        self._update_button_states()

    def update_state(self):
        self._update_button_states()

    def _update_button_states(self, *args, **kwargs):
        if self._multiply_button and self._divide_button:
            period = self._transit_selection_tool.get_current_selection().get_period_length()
            multiplier = self._get_multiplier()
            if not period or period * multiplier > self._maximum_period:
                self._multiply_button.Disable()
            else:
                self._multiply_button.Enable()
            if not period or period / multiplier < self._minimum_period:
                self._divide_button.Disable()
            else:
                self._divide_button.Enable()

    def OnDataLoaded(self, data):
        time_values = zip(*data)[0]
        self._maximum_period = max(time_values) - min(time_values)
