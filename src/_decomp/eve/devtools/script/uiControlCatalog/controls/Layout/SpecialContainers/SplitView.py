#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\uiControlCatalog\controls\Layout\SpecialContainers\SplitView.py
from carbonui.primitives.split_view import SplitView
from carbonui import uiconst
from carbonui.control.checkbox import Checkbox
from carbonui.control.combo import Combo
from carbonui.control.slider import Slider
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.primitives.split_view import PanelMode, PanelPlacement
from eve.client.script.ui import eveColor
from eve.client.script.ui.control import eveLabel
from eve.devtools.script.uiControlCatalog.sample import Sample

class Sample(Sample):
    name = 'Playground'
    description = "A container that is split into a main content area and a side panel.\n\n    The 'content' area is always present, but the 'panel' can be collapsed. The panel\n    is either displayed side-by-side with the content or overlaid on it depending on\n    the 'panel_mode' property. Instead of adding child elements directly to this\n    container you should use the 'panel' and 'content' properties."

    def construct_sample(self, parent):
        split_view = SplitView(parent=parent, align=uiconst.TOPLEFT, width=400, height=300)
        Fill(bgParent=split_view.content, color=eveColor.MATTE_BLACK)
        eveLabel.EveLabelLarge(parent=split_view.content, align=uiconst.CENTER, text='Content')
        Fill(bgParent=split_view.panel, color=eveColor.GUNMETAL_GREY)
        eveLabel.EveLabelLarge(parent=split_view.panel, align=uiconst.CENTER, text='Panel')
        create_split_view_harness(split_view)


def create_split_view_harness(split_view):
    parent = split_view.parent
    main_cont = Container(parent=parent, align=uiconst.TOPLEFT, width=600, height=300)
    split_view.SetParent(main_cont)
    controls_cont = Container(parent=main_cont, align=uiconst.TORIGHT, width=176)

    def toggle_expanded(checkbox):
        split_view.expanded = checkbox.checked

    Checkbox(parent=controls_cont, align=uiconst.TOTOP, text='Expanded', checked=split_view.expanded, callback=toggle_expanded)
    eveLabel.EveLabelMedium(parent=controls_cont, align=uiconst.TOTOP, text='Panel mode', top=16)

    def set_panel_mode(combo, key, value):
        split_view.panel_mode = value

    Combo(parent=controls_cont, align=uiconst.TOTOP, callback=set_panel_mode, options=[('Inline', PanelMode.INLINE),
     ('Inline Compact', PanelMode.COMPACT_INLINE),
     ('Overlay', PanelMode.OVERLAY),
     ('Overlay Compact', PanelMode.COMPACT_OVERLAY)], select=PanelMode.INLINE)
    eveLabel.EveLabelMedium(parent=controls_cont, align=uiconst.TOTOP, top=16, text='Panel placement')

    def set_panel_placement(combo, key, value):
        split_view.panel_placement = value

    Combo(parent=controls_cont, align=uiconst.TOTOP, callback=set_panel_placement, options=[('Left', PanelPlacement.LEFT), ('Right', PanelPlacement.RIGHT)], select=PanelPlacement.LEFT)
    eveLabel.EveLabelMedium(parent=controls_cont, align=uiconst.TOTOP, top=16, text='Compact panel width')

    def set_compact_panel_width(slider):
        split_view.compact_panel_width = int(slider.value)

    slider = Slider(parent=controls_cont, align=uiconst.TOTOP, value=split_view.compact_panel_width, minValue=0, maxValue=250, on_dragging=set_compact_panel_width, getHintFunc=lambda s: '{} px'.format(int(s.value)))
    slider._set_compact_panel_width = set_compact_panel_width
    eveLabel.EveLabelMedium(parent=controls_cont, align=uiconst.TOTOP, top=16, text='Expanded panel width')

    def set_expanded_panel_width(slider):
        split_view.expanded_panel_width = int(slider.value)

    slider = Slider(parent=controls_cont, align=uiconst.TOTOP, value=split_view.expanded_panel_width, minValue=0, maxValue=split_view.width, on_dragging=set_expanded_panel_width, getHintFunc=lambda s: '{} px'.format(int(s.value)))
    slider._set_expanded_panel_width = set_expanded_panel_width

    def set_static_panel_inner_width(checkbox):
        split_view.static_panel_inner_width = checkbox.checked

    Checkbox(parent=controls_cont, align=uiconst.TOTOP, top=16, text='Static panel inner width', hint="When enabled, the inner width of the panel is static and always equal to expanded_panel_width. This is useful when you don't want the content of the panel to compress/expand when the panel is collapsed/expanded.", checked=split_view.static_panel_inner_width, callback=set_static_panel_inner_width)
