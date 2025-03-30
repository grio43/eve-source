#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\structure\components\structureSelector.py
import eveicon
from carbonui import uiconst, TextAlign
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.primitives.flowcontainer import FlowContainer
from carbonui.primitives.vectorarc import VectorArc
from carbonui.primitives.container import Container
from eve.client.script.ui.control.eveLabel import EveCaptionLarge
from localization import GetByLabel

class StructureNameSelector(FlowContainer):

    def __init__(self, options = None, selected_index = 0, callback = None, *args, **kwargs):
        super(StructureNameSelector, self).__init__(*args, **kwargs)
        if options is None:
            raise ValueError('No options list provided')
        self._options = options
        self._selected_index = selected_index
        self._callback = callback
        self._name_label = None
        self._construct_layout()

    def _construct_layout(self):
        button_size = 26
        icon_size = 8
        text_width = 240
        left_arrow_cont = Container(parent=self, name='left_arrow_cont', align=uiconst.NOALIGN, width=button_size, height=button_size)
        VectorArc(name='circle', parent=left_arrow_cont, align=uiconst.CENTER, radius=0.5 * button_size, lineWidth=1, fill=False, glowBrightness=0)
        ButtonIcon(name='prev_button', parent=left_arrow_cont, align=uiconst.CENTER, width=button_size, height=button_size, iconSize=icon_size, texturePath=eveicon.chevron_left, func=self.select_prev)
        label_container = Container(name='label_container', parent=self, align=uiconst.NOALIGN, width=text_width, height=button_size, state=uiconst.UI_NORMAL)
        self._name_label = EveCaptionLarge(name='name_label', parent=label_container, align=uiconst.CENTER, textAlign=TextAlign.CENTER, width=240)
        label_container.hint = GetByLabel('UI/Personalization/PaintTool/SelectedStructureTooltip')
        right_arrow_cont = Container(parent=self, name='right_arrow_cont', align=uiconst.NOALIGN, width=button_size, height=button_size)
        VectorArc(name='circle', parent=right_arrow_cont, align=uiconst.CENTER, radius=0.5 * button_size, lineWidth=1, fill=False, glowBrightness=0)
        ButtonIcon(name='next_button', parent=right_arrow_cont, align=uiconst.CENTER, width=button_size, height=button_size, iconSize=icon_size, texturePath=eveicon.chevron_right, func=self.select_next)

    def select_prev(self):
        if self._selected_index == 0:
            self.select_by_index(len(self._options) - 1)
        else:
            self.select_by_index(self._selected_index - 1)

    def select_next(self):
        if self._selected_index == len(self._options) - 1:
            self.select_by_index(0)
        else:
            self.select_by_index(self._selected_index + 1)

    def select_by_index(self, index, notify = True):
        self._selected_index = index
        selected_name, selected_value = self._options[self._selected_index]
        self._name_label.text = selected_name
        if notify and self._callback:
            self._callback(self, selected_name, selected_value)

    def select_by_value(self, value, notify = True):
        for i, option in enumerate(self._options):
            if option[1] == value:
                self.select_by_index(i, notify=notify)
                return

    def get_value(self):
        return self._options[self._selected_index][1]
