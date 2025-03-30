#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\uiblinker\insider\window.py
import eveui
import threadutils
import uthread2
from carbonui import uiconst
from carbonui.control.checkbox import Checkbox
from carbonui.control.combo import Combo
from carbonui.control.layer import LayerCore
from carbonui.control.scrollentries import SE_BaseClassCore
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.flowcontainer import FlowContainer
from carbonui.primitives.sprite import Sprite
from carbonui.uicore import uicore
from eve.client.script.ui.control import eveLabel
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.control.button import Button
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.eveScroll import Scroll
from carbonui.control.window import Window
from eve.client.script.ui.control.listgroup import ListGroup
from eve.client.script.ui.tooltips.tooltipUtil import RefreshTooltipForOwner
from uiblinker.blinker import BlinkerType
from uiblinker.reference.path import UiPathReference
from uiblinker.reference.ui_name import UniqueNameReference
from uiblinker.service import get_service

class UiBlinkerDebugWindow(Window):
    default_caption = 'UI Blinker Debugger'
    default_windowID = 'ui_blinker_debugger'
    default_minSize = (600, 300)
    default_width = 600
    default_height = 300

    def __init__(self, **kwargs):
        self._scroll = None
        self._ui_input_path = None
        self._ui_input_name = None
        self._blinker_type_input_path = None
        self._blinker_type_input_name = None
        self._chain_blinks_cb = None
        self._start_blinker_panel = None
        self._blinkers = []
        super(UiBlinkerDebugWindow, self).__init__(**kwargs)
        self._layout()
        self._load()

    def Close(self, setClosed = False, *args, **kwds):
        super(UiBlinkerDebugWindow, self).Close(setClosed, *args, **kwds)
        for blinker in self._blinkers:
            blinker.dispose()

    @threadutils.threaded
    def _load(self):
        self._populate_blinker_list()
        get_service().debug_get_on_blinkers_changed_signal().connect(self._on_blinkers_changed)

    def _layout(self):
        buttons = FlowContainer(parent=self.GetMainArea(), align=uiconst.TOTOP, contentSpacing=(8, 8), padding=8)
        Button(parent=buttons, align=uiconst.NOALIGN, label='Stop All', func=get_service().stop_all_blinkers, args=())
        self.add_input_controls_name()
        self.add_input_controls_path()
        self._scroll = Scroll(parent=self.GetMainArea(), align=uiconst.TOALL, hasUnderlay=False)

    def add_input_controls_path(self):
        bottom = ContainerAutoSize(parent=self.GetMainArea(), align=uiconst.TOBOTTOM, alignMode=uiconst.TOLEFT, height=32)
        self.add_pick_button_icon(bottom, self._pick_ui_element_path)
        self._ui_input_path = self.add_input_field(bottom, 'UI element path', UiPathReference)
        self._blinker_type_input_path = self.add_blinker_type(bottom)
        self.add_start_button(bottom, self._on_start_blinker_pressed_path)

    def add_input_controls_name(self):
        bottom = ContainerAutoSize(parent=self.GetMainArea(), align=uiconst.TOBOTTOM, alignMode=uiconst.TOLEFT, height=32)
        self.add_pick_button_icon(bottom, self._pick_ui_element_name)
        self._ui_input_name = self.add_input_field(bottom, 'Unique ui name', UniqueNameReference)
        self._blinker_type_input_name = self.add_blinker_type(bottom)
        self.add_start_button(bottom, self._on_start_blinker_pressed_name)
        cont = ContainerAutoSize(parent=bottom, align=uiconst.TOLEFT, left=8)
        self._chain_blinks_cb = Checkbox(text='Chain blinks', parent=cont, settingsKey='blink_debug_chain_blinks', checked=True, align=uiconst.CENTERLEFT, width=100)

    def add_pick_button_icon(self, parent, pickFunc):
        cont = ContainerAutoSize(parent=parent, align=uiconst.TOLEFT, left=8)
        ButtonIcon(parent=cont, align=uiconst.CENTER, width=18, height=18, texturePath='res:/UI/Texture/classes/insider/color_picker_18.png', iconSize=18, hint='Pick UI element', func=pickFunc, args=())

    def add_input_field(self, bottom, hintText, referenceClass):
        input = UiElementPathInput(parent=ContainerAutoSize(parent=bottom, align=uiconst.TOLEFT, left=8), align=uiconst.CENTER, hintText=hintText, referenceClass=referenceClass)
        return input

    def add_blinker_type(self, bottom):
        cont = ContainerAutoSize(parent=bottom, align=uiconst.TOLEFT, left=8)
        _blinker_type_input = Combo(parent=cont, align=uiconst.CENTER, options=[('Box', BlinkerType.box), ('Ring', BlinkerType.ring)], select=BlinkerType.box)
        return _blinker_type_input

    def add_start_button(self, bottom, startFunc):
        cont = ContainerAutoSize(parent=bottom, align=uiconst.TOLEFT, left=8)
        Button(parent=cont, align=uiconst.CENTER, label='Start', func=startFunc, args=())

    def _on_start_blinker_pressed_path(self):
        ui_element_path = self._ui_input_path.GetText()
        blinker_type = self._blinker_type_input_path.GetValue()
        validation = UiPathReference.validate_path(ui_element_path)
        if validation:
            return
        self._start_debug_blinker_path(reference=ui_element_path, blinker_type=blinker_type, group='ui_blinker_debugger')

    def _start_debug_blinker_path(self, reference, blinker_type, group):
        self._blinkers.append(get_service().start_blinker(reference=reference, blinker_type=blinker_type, group=group))

    def _on_start_blinker_pressed_name(self):
        uniqueName = self._ui_input_name.GetText()
        blinker_type = self._blinker_type_input_name.GetValue()
        chain_blinks = self._chain_blinks_cb.GetValue()
        self._start_debug_blinker_name(reference=uniqueName, blinker_type=blinker_type, group='ui_blinker_debugger', chain_blinks=chain_blinks)

    def _start_debug_blinker_name(self, reference, blinker_type, group, chain_blinks):
        self._blinkers.append(get_service().start_unique_name_blinker(reference=reference, blinker_type=blinker_type, group=group, chain_blinks=chain_blinks))

    def _populate_blinker_list(self):
        active_blinkers = get_service().debug_get_active_blinkers()
        blinkers_by_group = {}
        for blinker in active_blinkers:
            blinkers_by_group.setdefault(blinker.group, set()).add(blinker)

        def get_sub_content(node, group):
            return [ GetFromClass(BlinkerEntry, {'blinker': blinker,
             'start_blinker': self._start_debug_blinker_path,
             'group': group,
             'sublevel': 1}) for blinker in node.groupItems ]

        content = []
        for group, blinkers in blinkers_by_group.items():
            content.append(GetFromClass(ListGroup, {'GetSubContent': lambda node, _group = group: get_sub_content(node, _group),
             'label': group if group is not None else '(default group)',
             'id': (group, group),
             'groupItems': blinkers,
             'state': 'locked',
             'selected': 0,
             'BlockOpenWindow': 1,
             'hideFill': True}))

        self._scroll.Load(contentList=content, noContentHint='No active blinkers')

    @uthread2.debounce(wait=0.1)
    def _on_blinkers_changed(self):
        self._populate_blinker_list()

    @threadutils.threaded
    def _pick_ui_element_path(self):
        element = pick_ui_element('name')
        if element is None:
            return
        ui_element_path = generate_ui_element_path(element)
        self._ui_input_path.SetText(ui_element_path)

    @threadutils.threaded
    def _pick_ui_element_name(self):
        element = pick_ui_element('uniqueUiName')
        if element is None:
            return
        name = getattr(element, 'uniqueUiName', '')
        self._ui_input_name.SetText(name)


def pick_ui_element(nameAttribute):
    picker = ElementPicker(nameAttribute)
    element = picker.pick()
    picker.Close()
    return element


def generate_ui_element_path(element):
    significant_elements = [element]
    e = getattr(element, 'parent', None)
    while e and e != uicore.desktop:
        if e.name == 'Neocom':
            significant_elements.append(e)
            break
        if isinstance(e, (Window, LayerCore)):
            significant_elements.append(e)
            break
        e = getattr(e, 'parent', None)

    return '/**/'.join((e.name for e in reversed(significant_elements)))


class ElementPicker(Container):
    isTabStop = True

    def __init__(self, nameAttribute = 'name'):
        self.nameAttribute = nameAttribute
        self._picking = False
        self._hovered_element = None
        self._picked_element = None
        super(ElementPicker, self).__init__(parent=uicore.desktop, align=uiconst.TOALL, cursor=uiconst.UICURSOR_MAGNIFIER, idx=0)
        eveLabel.EveLabelLarge(parent=ContainerAutoSize(parent=self, align=uiconst.CENTERTOP, top=64, bgColor=(0.0, 0.0, 0.0, 0.5)), align=uiconst.TOPLEFT, top=8, left=16, padBottom=8, padRight=16, text='Picking a UI element. Press ESC to cancel.', color=(0.0, 1.0, 0.0))
        self._frame = Container(parent=self, align=uiconst.TOPLEFT, bgColor=(0.0, 1.0, 0.0, 0.2))
        self._frame.Hide()
        self._frame_label = eveLabel.EveLabelMedium(parent=self._frame, align=uiconst.CENTERBOTTOM, color=(0.0, 1.0, 0.0))

    def pick(self):
        if self._picking:
            raise RuntimeError('already picking')
        self._picking = True
        try:
            self.state = uiconst.UI_NORMAL
            self.isTabStop = True
            uicore.registry.SetFocus(self)
            cookie = uicore.uilib.RegisterForTriuiEvents([uiconst.UI_KEYDOWN], self._on_global_key)
            picked = None
            while self._picking:
                if self._picked_element is not None:
                    picked = self._picked_element
                    self._picked_element = None
                    self._hovered_element = None
                    break
                hovered = self._get_element_at_cursor()
                if hovered != self._hovered_element:
                    self._hovered_element = hovered
                    self._update_frame(hovered)
                eveui.wait_for_next_frame()

            uicore.uilib.UnregisterForTriuiEvents(cookie)
        finally:
            self.state = uiconst.UI_DISABLED
            self._picking = False

        return picked

    def _update_frame(self, element):
        if element is None:
            self._frame.Hide()
        else:
            self._frame.Show()
            self._frame.pos = element.GetAbsolute()
            self._frame_label.text = getattr(element, self.nameAttribute)
            self._frame_label.top = -(self._frame_label.textheight + 4)

    def OnClick(self, *args):
        if self._picking:
            element = self._get_element_at_cursor()
            self._picked_element = element

    def _on_global_key(self, *args, **kwargs):
        if self.destroyed:
            return False
        if eveui.Key.escape.is_down:
            self._picking = False
            uicore.uilib.StopKeyDownAcceleratorThread()
        else:
            return True

    def _get_element_at_cursor(self):
        self.state = uiconst.UI_DISABLED
        _, element = uicore.uilib.PickScreenPosition(*eveui.Mouse.position())
        self.state = uiconst.UI_NORMAL
        return element


class UiElementPathInput(SingleLineEditText):

    def __init__(self, parent, align, hintText, referenceClass = UiPathReference):
        self._validation_errors = set()
        self._validation_error_icon = None
        self.referenceClass = referenceClass
        super(UiElementPathInput, self).__init__(parent=parent, align=align, top=0, width=220, hintText=hintText, OnChange=self._validate_ui_element_path)

    def _validate_ui_element_path(self, ui_element_path):
        if not ui_element_path:
            self._validation_errors = set()
        else:
            self._validation_errors = self.referenceClass.validate_path(ui_element_path)
        if not self._validation_errors:
            if self._validation_error_icon is not None:
                self._validation_error_icon.Hide()
        else:
            has_errors = any((v.is_error for v in self._validation_errors))
            color = (1.0, 0.0, 0.0) if has_errors else (1.0, 0.6, 0.2)
            if self._validation_error_icon is None:
                self._validation_error_icon = Sprite(parent=ContainerAutoSize(parent=self, align=uiconst.TORIGHT, left=4, idx=0), align=uiconst.CENTER, width=16, height=16, texturePath='res:/UI/Texture/classes/agency/iconExclamation.png', color=color)
                self._validation_error_icon.LoadTooltipPanel = self._load_validation_error_tooltip
            else:
                self._validation_error_icon.Show()
                self._validation_error_icon.SetRGBA(*color)
            RefreshTooltipForOwner(self._validation_error_icon)

    def _load_validation_error_tooltip(self, panel, owner):
        panel.LoadStandardSpacing()
        for error in filter(lambda v: v.is_error, self._validation_errors):
            panel.AddLabelMedium(text=error.message, wrapWidth=300, color=(1.0, 0.0, 0.0))

        for warning in filter(lambda v: v.is_warning, self._validation_errors):
            panel.AddLabelMedium(text=warning.message, wrapWidth=300, color=(1.0, 0.6, 0.2))


class BlinkerEntry(SE_BaseClassCore):

    def __init__(self, *args, **kwargs):
        self._label = None
        self._stop_button = None
        self._blinker_type_combo = None
        super(BlinkerEntry, self).__init__(*args, **kwargs)

    def Startup(self, *args):
        self._stop_button = Button(parent=ContainerAutoSize(parent=self, align=uiconst.TORIGHT, left=16), align=uiconst.CENTER, label='Stop', args=())
        self._blinker_type_combo = Combo(parent=ContainerAutoSize(parent=self, align=uiconst.TORIGHT, left=8), align=uiconst.CENTER, callback=self._on_blinker_type_combo_changed)
        self._label = eveLabel.EveLabelMedium(parent=Container(parent=self, align=uiconst.TOALL, padRight=16), align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED, maxLines=1, autoFadeSides=16)

    def Load(self, node):
        self.sr.node = node
        self._label.text = node.blinker.debug_name
        sublevel_correction = self.sr.node.scroll.sr.get('sublevelCorrection', 0) if self.sr.node.scroll else 0
        sublevel = max(0, node.Get('sublevel', 0) - sublevel_correction)
        self._label.padLeft = 24 * sublevel
        self._blinker_type_combo.LoadOptions(entries=[('Box', BlinkerType.box), ('Ring', BlinkerType.ring)], select=node.blinker.blinker_type)
        self._stop_button.func = node.blinker.stop

    def GetHeight(self, *args):
        height = max(Button.default_minHeight, eveLabel.EveLabelMedium.default_minHeight) or 20
        return height + 8

    def _on_blinker_type_combo_changed(self, combo, key, value):
        blinker = getattr(self.sr.node, 'blinker', None)
        if blinker is None:
            return
        if value != blinker.blinker_type:
            reference = blinker.reference
            group = blinker.group
            self.sr.node.blinker = self.sr.node.start_blinker(reference=reference, blinker_type=value, group=group)
            blinker.stop()
