#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\progression\client\widgets\countergreaterthanwidget.py
from collections import defaultdict
from carbon.common.lib import telemetry
from carbonui import uiconst
from eve.client.script.ui.control.eveLabel import EveLabelMediumBold
from progression.client.const import COLOR_INFO_FOREGROUND, COLOR_UI_HIGHLIGHTING, COLOR_ALARM_FOREGROUND
from progression.client.widgets.basewidget import BaseWidget
from progression.common.widgets import TaskWidgetMode

class CounterGreaterThanWidget(BaseWidget):
    __notifyevents__ = ['DoBallsAdded', 'DoBallRemove', 'DoBallsRemove']

    def ApplyAttributes(self, attributes):
        super(CounterGreaterThanWidget, self).ApplyAttributes(attributes)
        self.ballpark = sm.GetService('michelle').GetBallpark()
        counter_value = attributes.widget_state
        self.counter_value = counter_value
        self.text = attributes.static_data.text
        self.mode = attributes.static_data.mode
        self.label_color = self._GetLabelColor()
        self.show_when_counter_greater_than = attributes.static_data.show_when_counter_greater_than
        self.dependent_type_list = getattr(attributes.static_data, 'dependent_type_list', [])
        self.is_visible = True
        self.dependent_types_present = defaultdict(lambda : 0)
        if self.dependent_type_list:
            sm.RegisterNotify(self)
        self._initialize_dependent_types()
        self._ConstructLabel()

    def _initialize_dependent_types(self):
        for slimItem in self.ballpark.slimItems.itervalues():
            if slimItem.typeID in self.dependent_type_list:
                self.dependent_types_present[slimItem.typeID] += 1

    def _is_dependent_type_present(self):
        if not self.dependent_type_list:
            return True
        return any((v > 0 for v in self.dependent_types_present.values()))

    def _ConstructLabel(self):
        self.mainContainer.Flush()
        if self.counter_value <= self.show_when_counter_greater_than:
            if self.parent:
                self.parent.Close()
            return
        self.label = EveLabelMediumBold(parent=self.mainContainer, text=self.text, align=uiconst.TOPLEFT, color=self.label_color, wrapMode=uiconst.WRAPMODE_FORCEWORD, maxWidth=250)
        if self.parent:
            textWidth, textHeight = self.label.GetAbsoluteSize()
            if not self._is_dependent_type_present():
                self.parent.height = 0
            else:
                self.parent.height = textHeight

    def _GetLabelColor(self):
        if self.mode == TaskWidgetMode.TASK_WIDGET_MODE_ALERT:
            return COLOR_ALARM_FOREGROUND
        return COLOR_INFO_FOREGROUND

    def OnMouseEnter(self, *args):
        self.label.SetTextColor(COLOR_UI_HIGHLIGHTING)
        super(CounterGreaterThanWidget, self).OnMouseEnter(*args)

    def OnMouseExit(self, *args):
        self.label.SetTextColor(self.label_color)
        super(CounterGreaterThanWidget, self).OnMouseExit(*args)

    def DoBallsAdded(self, ball_slim_items):
        changed = False
        for ball, slim_item in ball_slim_items:
            if slim_item.typeID in self.dependent_type_list:
                self.dependent_types_present[slim_item.typeID] += 1
                changed = True

        if changed:
            self._ConstructLabel()

    def DoBallRemove(self, ball, slim_item, terminal):
        changed = False
        if slim_item.typeID in self.dependent_type_list:
            self.dependent_types_present[slim_item.typeID] -= 1
            changed = True
        if changed:
            self._ConstructLabel()

    @telemetry.ZONE_METHOD
    def DoBallsRemove(self, python_balls, is_release):
        changed = False
        for ball, slimItem, terminal in python_balls:
            if slimItem.typeID in self.dependent_type_list:
                self.dependent_types_present[ball.typeID] -= 1
                changed = True

        if changed:
            self._ConstructLabel()

    def Close(self):
        if getattr(self, 'destroyed', False):
            return
        sm.UnregisterNotify(self)
        super(CounterGreaterThanWidget, self).Close()
