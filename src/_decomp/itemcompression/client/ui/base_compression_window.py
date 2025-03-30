#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\itemcompression\client\ui\base_compression_window.py
import localization
from carbonui import uiconst
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.primitives.container import Container
from carbonui.primitives.flowcontainer import FlowContainer
from carbonui.control.button import Button
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from carbonui.control.window import Window
from itemcompression.client.ui.label_paths import output_materials_label_path, input_materials_label_path, cancel_action_label_path

class BaseCompressionWindow(Window):
    default_width = 450
    default_height = 350

    def ApplyAttributes(self, attributes):
        super(BaseCompressionWindow, self).ApplyAttributes(attributes)
        self.ConstructLayout()

    def ConstructLayout(self):
        self.bottom_cont = Container(name='bottom_cont', parent=self.sr.main, align=uiconst.TOBOTTOM, height=Button.default_height, padTop=16)
        self.ConstructBottomButtons()
        panel_cont = Container(name='panel_cont', parent=self.sr.main, align=uiconst.TOALL, padTop=12)
        self.inputPanel = Container(name='input_panel', parent=panel_cont, align=uiconst.TOLEFT_PROP, width=0.5, padRight=8)
        self.output_panel = Container(name='output_panel', parent=panel_cont, align=uiconst.TORIGHT_PROP, width=0.5, padLeft=8)
        self.ConstructInputPanel()
        self.ConstructOutputPanel()

    def ConstructOutputPanel(self):
        output_header_cont = Container(name='output_header_cont', parent=self.output_panel, align=uiconst.TOTOP, height=18, padBottom=8)
        EveLabelMedium(name='output_header_label', parent=output_header_cont, align=uiconst.CENTERLEFT, text=localization.GetByLabel(output_materials_label_path), padLeft=2)
        output_panel_scroll = ScrollContainer(parent=self.output_panel, align=uiconst.TOALL, pushContent=False, showUnderlay=True)
        self.output_cont = FlowContainer(name='output_cont', parent=output_panel_scroll, align=uiconst.TOTOP, contentSpacing=(2, 2), minHeight=100, clipChildren=True)

    def ConstructInputPanel(self):
        self.input_header_cont = Container(name='input_header_cont', parent=self.inputPanel, align=uiconst.TOTOP, height=18, padBottom=8)
        EveLabelMedium(name='input_header_label', parent=self.input_header_cont, align=uiconst.CENTERLEFT, text=localization.GetByLabel(input_materials_label_path))
        input_panel_scroll = ScrollContainer(parent=self.inputPanel, align=uiconst.TOALL, pushContent=False, showUnderlay=True)
        self.input_cont = FlowContainer(name='input_cont', parent=input_panel_scroll, align=uiconst.TOTOP, contentSpacing=(2, 2), minHeight=100, clipChildren=True)

    def ConstructBottomButtons(self):
        Button(name='cancel_button', parent=self.bottom_cont, align=uiconst.TOPLEFT, label=localization.GetByLabel(cancel_action_label_path), func=self.Close)
