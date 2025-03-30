#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\progression\client\widgets\counterwidget.py
from carbonui import uiconst
from eve.client.script.ui.control.eveLabel import EveLabelMedium, EveLabelMediumBold
from localization import GetByLabel
from progression.client.const import COLOR_INFO_FOREGROUND, COLOR_UI_HIGHLIGHTING, WIDGET_TEXT_BOLD_WHITE
from progression.client.widgets.basewidget import BaseWidget

class CounterWidget(BaseWidget):

    def ApplyAttributes(self, attributes):
        super(CounterWidget, self).ApplyAttributes(attributes)
        counter_value = attributes.widget_state
        self.counter_value = counter_value
        self.text = attributes.static_data.text
        self.target_value = attributes.static_data.target_value
        self._ConstructCounterUI()

    def _ConstructCounterUI(self):
        self.mainContainer.Flush()
        if self.counter_value is None:
            self.counter_value = 0
        self.label = EveLabelMedium(parent=self.mainContainer, text=self.text, align=uiconst.TOLEFT)
        counter_str = self.get_formatted_counter_string()
        self.counter_label = EveLabelMediumBold(parent=self.mainContainer, text=counter_str, align=uiconst.TORIGHT, color=COLOR_INFO_FOREGROUND)
        self.height = self.label.actualTextHeight

    def get_formatted_counter_string(self):
        if self.target_value:
            numerator = min(self.counter_value, self.target_value)
            counter_str = GetByLabel('UI/Progression/NumeratorDenominator', numerator=numerator, denominator=self.target_value)
        else:
            counter_value_str = str(int(round(self.counter_value)))
            counter_str = counter_value_str
        return counter_str

    def OnMouseEnter(self, *args):
        self.label.SetTextColor(COLOR_UI_HIGHLIGHTING)
        super(CounterWidget, self).OnMouseEnter(*args)

    def OnMouseExit(self, *args):
        self.label.SetTextColor(WIDGET_TEXT_BOLD_WHITE)
        super(CounterWidget, self).OnMouseExit(*args)
