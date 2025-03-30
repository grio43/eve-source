#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\progression\client\widgets\killcounterwidget.py
from carbonui import uiconst
from carbonui.primitives.container import Container
from eve.client.script.ui.control.eveLabel import EveLabelMediumBold
from localization import GetByLabel
from progression.client.const import COLOR_INFO_FOREGROUND, COLOR_UI_HIGHLIGHTING, WIDGET_TEXT_BOLD_WHITE
import math
from progression.client.widgets.basewidget import BaseWidget

class KillCounterWidget(BaseWidget):

    def ApplyAttributes(self, attributes):
        super(KillCounterWidget, self).ApplyAttributes(attributes)
        if attributes.widget_state is None:
            counter_value = 0
            self.highlight_type_ids = []
        else:
            counter_value, self.highlight_type_ids = attributes.widget_state
        self.counter_value = counter_value
        self.text = attributes.static_data.text
        self.bold = attributes.static_data.bold
        self._ConstructCounterUI()

    def _ConstructCounterUI(self):
        self.mainContainer.Flush()
        if self.counter_value is None:
            self.counter_value = 0
        labelCls = self.GetLabelClass()
        self.label = labelCls(name='npcName', parent=self.mainContainer, align=uiconst.TOPLEFT, text=self.text, wrapMode=uiconst.WRAPMODE_FORCEWORD, maxWidth=220)
        flooredPercentage = int(math.floor(self.counter_value))
        self.counter_label = EveLabelMediumBold(parent=self.mainContainer, text=GetByLabel('UI/Common/Formatting/Percentage', percentage=flooredPercentage), align=uiconst.TORIGHT, color=COLOR_INFO_FOREGROUND)
        textWidth, textHeight = self.label.GetAbsoluteSize()
        self.parent.height = textHeight

    def GetDynamicHighlightedTypeIDs(self):
        return self.highlight_type_ids

    def OnMouseEnter(self, *args):
        self.label.SetTextColor(COLOR_UI_HIGHLIGHTING)
        super(KillCounterWidget, self).OnMouseEnter(*args)

    def OnMouseExit(self, *args):
        self.label.SetTextColor(WIDGET_TEXT_BOLD_WHITE)
        super(KillCounterWidget, self).OnMouseExit(*args)
