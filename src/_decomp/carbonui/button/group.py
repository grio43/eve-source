#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\button\group.py
import logging
import weakref
import eveicon
import localization
from carbonui import uiconst
from carbonui.button.const import ButtonFrameType, ButtonVariant
from carbonui.control.button import Button
from carbonui.control.contextMenu.menuData import MenuData
from carbonui.primitives.childrenlist import PyChildrenList
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize, UIChildrenListAutoSize
from carbonui.uiconst import Axis, AxisAlignment, Density
from carbonui.util.dpi import reverse_scale_dpi
from carbonui.util.various_unsorted import divide_evenly
log = logging.getLogger(__name__)

class ButtonSizeMode(object):
    DYNAMIC = 1
    EQUAL = 2
    STRETCH = 3
    DYNAMIC_STRETCH = 4


class OverflowAlign(object):
    RIGHT = 1
    LEFT = 2


class ButtonData(object):

    def __init__(self, text, callback = None, hint = None, icon = None, modal_result = False, is_default = False, is_cancel = False, ui_name = None, style = None, variant = None, button_class = Button, analytic_id = None, legacy_args = (), legacy_color = None, legacy_density = None):
        self.text = text
        self.callback = callback
        self.hint = hint
        self.icon = icon
        self.modal_result = modal_result
        self.is_default = is_default
        self.is_cancel = is_cancel
        self.ui_name = ui_name
        self.style = style
        self.variant = variant
        self.button_class = button_class
        self.analytic_id = analytic_id
        self._legacy_args = legacy_args
        self._legacy_color = legacy_color
        self._legacy_density = legacy_density

    @classmethod
    def from_legacy_tuple(cls, data, button_class):
        kwargs = {'text': data[0],
         'callback': data[1]}
        if len(data) > 2:
            kwargs['legacy_args'] = data[2]
        if len(data) > 4:
            kwargs['modal_result'] = data[4]
        if len(data) > 5:
            kwargs['is_default'] = data[5]
        if len(data) > 6:
            kwargs['is_cancel'] = data[6]
        if len(data) > 7:
            kwargs['hint'] = data[7]
        if len(data) > 8:
            kwargs['legacy_color'] = data[8]
        if len(data) > 9:
            kwargs['button_class'] = data[9] or button_class
        if len(data) > 10:
            kwargs['ui_name'] = data[10]
        if len(data) > 11:
            kwargs['style'] = data[11]
        if len(data) > 12:
            kwargs['legacy_density'] = data[12]
        if len(data) > 13:
            kwargs['variant'] = data[13]
        if len(data) > 14:
            kwargs['icon'] = data[14]
        if len(data) > 15:
            kwargs['analytic_id'] = data[15]
        return ButtonData(**kwargs)

    def create_button(self, density):
        if self._legacy_density is not None:
            density = self._legacy_density
        return self.button_class(name=self.ui_name or '%s_Btn' % self.text, label=self.text, texturePath=self.icon, func=self.callback, hint=self.hint, style=self.style, variant=self.variant, density=density, btn_modalresult=self.modal_result, btn_default=self.is_default, btn_cancel=self.is_cancel, args=self._legacy_args, color=self._legacy_color, fontStyle=self.button_class.default_fontStyle, fontFamily=self.button_class.default_fontFamily, fontPath=self.button_class.default_fontPath, fontsize=self.button_class.default_fontsize, analyticID=self.analytic_id)


IMPORTANCE_BY_VARIANT = {ButtonVariant.GHOST: 0,
 ButtonVariant.NORMAL: 1,
 ButtonVariant.PRIMARY: 2}

class ButtonGroup(Container):
    default_align = uiconst.TOBOTTOM
    default_state = uiconst.UI_PICKCHILDREN
    _button_container = None
    _overflow_button = None

    def __init__(self, buttons = None, button_alignment = AxisAlignment.CENTER, button_size_mode = ButtonSizeMode.EQUAL, density = Density.NORMAL, orientation = Axis.HORIZONTAL, overflow_align = OverflowAlign.RIGHT, ignore_overflow = False, **kwargs):
        self._button_alignment = button_alignment
        self._button_size_mode = button_size_mode
        self._density = density
        self._orientation = orientation
        self._overflow_align = overflow_align
        self._ignore_overflow = ignore_overflow
        super(ButtonGroup, self).__init__(**kwargs)
        self._layout()
        self.children = ButtonGroupChildrenList(self)
        if 'btns' in kwargs:
            for data in kwargs['btns']:
                self._add_button_data(ButtonData.from_legacy_tuple(data=data, button_class=Button))

        else:
            for button in buttons or []:
                self.add_button(button)

        if len(self._button_container.children) > 0:
            self._resize_self()

    @property
    def button_alignment(self):
        return self._button_alignment

    @button_alignment.setter
    def button_alignment(self, value):
        if self._button_alignment != value:
            self._button_alignment = value
            self._update_button_container_alignment()

    @property
    def button_size_mode(self):
        return self._button_size_mode

    @button_size_mode.setter
    def button_size_mode(self, value):
        if self._button_size_mode != value:
            self._button_size_mode = value
            self._update_button_size_mode()

    @property
    def buttons(self):
        buttons = []
        if self._button_container and not self._button_container.destroyed:
            for element in self._button_container.children:
                if isinstance(element, ButtonWrapper):
                    button = element.button
                    if button:
                        buttons.append(button)

        return buttons

    @property
    def density(self):
        return self._density

    @density.setter
    def density(self, value):
        if self._density != value:
            self._density = value
            self._update_button_density()

    @property
    def orientation(self):
        return self._orientation

    @orientation.setter
    def orientation(self, value):
        if self.orientation != value:
            self._orientation = value
            self._update_button_container_alignment()
            if not self.destroyed:
                self.FlagAlignmentDirty()

    def add_button(self, button, index = -1):
        if self.destroyed:
            return
        button.density = self._density
        ButtonWrapper(parent=self._button_container, align=uiconst.TOPLEFT, idx=index, button=button, on_child_removed=self._on_button_removed_from_wrapper)
        self._adjust_overflow_button_index()
        if hasattr(button, 'label') and button.label is not None:
            self.sr.Set('%s_Btn' % button.label, button)
        self.FlagAlignmentDirty('ButtonGroup.add_button()')
        return button

    def remove_button(self, button):
        if self.destroyed:
            return
        if button.parent is not None and button.parent.parent != self._button_container:
            raise ValueError('That button is not in this ButtonGroup')
        self._remove_button(button, wrapper=button.parent)

    def _remove_button(self, button, wrapper = None):
        if wrapper is None:
            wrapper = button.parent
        if wrapper is not None and self._button_container and not self._button_container.destroyed:
            self._button_container.children.remove(wrapper)
        if hasattr(button, 'label'):
            try:
                del self.sr['%s_Btn' % button.label]
            except KeyError:
                log.warning('Unable to remove the SR reference for a button: %s', '%s_Btn' % button.label)

    def _add_button_data(self, button_data):
        button = button_data.create_button(density=self._density)
        return self.add_button(button)

    def _create_overflow_button(self):
        if self._overflow_button is None:
            self._overflow_button = OverflowButton(parent=self._button_container, align=uiconst.TOPLEFT, get_menu=self._get_overflow_menu, density=self._density)
            self._overflow_button.display = False

    def _adjust_overflow_button_index(self):
        if self._overflow_button:
            button_count = len(self._button_container.children)
            current_index = self._overflow_button.GetOrder()
            if current_index < button_count - 1:
                self._overflow_button.SetOrder(-1)

    def _show_overflow_button(self):
        if self._overflow_button is not None:
            self._overflow_button.display = True

    def _hide_overflow_button(self):
        if self._overflow_button is not None:
            self._overflow_button.display = False

    def AddButton(self, label, func, args = None, fixedWidth = None, isModalResult = False, isDefault = False, isCancel = False, hint = None, color = None, btnClass = None, uiName = None, style = None, density = None, variant = None, texturePath = None):
        return self._add_button_data(button_data=ButtonData.from_legacy_tuple(data=(label,
         func,
         args,
         fixedWidth,
         isModalResult,
         isDefault,
         isCancel,
         hint,
         color,
         btnClass,
         uiName,
         style,
         density,
         variant,
         texturePath), button_class=Button))

    def Flush(self):
        self.FlushButtons()

    def FlushButtons(self):
        if self.destroyed:
            return
        for child in self._button_container.children[:]:
            if isinstance(child, ButtonWrapper):
                child.Close()

        to_remove = []
        for name in self.sr.keys():
            if name.endswith('_Btn'):
                to_remove.append(name)

        for name in to_remove:
            del self.sr[name]

    def ResetLayout(self):
        if not self.destroyed:
            self.FlagAlignmentDirty()

    def _layout(self):
        self._button_container = ContainerAutoSize(name='btns', parent=self, align=self._get_button_container_align())
        self._create_overflow_button()

    def _get_button_container_align(self):
        if self._button_alignment == AxisAlignment.START:
            return uiconst.TOPLEFT
        if self._button_alignment == AxisAlignment.CENTER:
            if self._orientation == Axis.HORIZONTAL:
                return uiconst.CENTERTOP
            if self._orientation == Axis.VERTICAL:
                return uiconst.CENTERLEFT
        elif self._button_alignment == AxisAlignment.END:
            if self._orientation == Axis.HORIZONTAL:
                return uiconst.TOPRIGHT
            if self._orientation == Axis.VERTICAL:
                return uiconst.BOTTOMLEFT

    def _update_button_container_alignment(self):
        if self._button_container and not self._button_container.destroyed:
            self._button_container.align = self._get_button_container_align()

    def _update_button_density(self):
        if not self.destroyed:
            for button in self._iter_buttons():
                button.density = self._density

            if self._overflow_button is not None:
                self._overflow_button.density = self._density

    def _get_button_gap(self):
        if self._density == Density.COMPACT:
            return 4
        else:
            return 8

    def _update_layout(self, budget_width, budget_height):
        if self._orientation == Axis.HORIZONTAL:
            if self.align in uiconst.ALIGNMENTS_WITH_RELEVANT_WIDTH:
                if self._button_size_mode == ButtonSizeMode.STRETCH:
                    budget_width = self.width
                else:
                    budget_width = None
            else:
                budget_width = budget_width
        elif self.align in uiconst.ALIGNMENTS_WITH_RELEVANT_HEIGHT:
            budget_height = None
        else:
            budget_height = budget_height
        if not self._ignore_overflow:
            self._update_button_overflow(budget_width, budget_height)
        if self._button_size_mode == ButtonSizeMode.EQUAL:
            self._resize_buttons_equal()
        elif self._button_size_mode == ButtonSizeMode.DYNAMIC:
            self._resize_buttons_dynamic()
        elif self._button_size_mode == ButtonSizeMode.STRETCH:
            self._resize_buttons_stretch(budget_width)
        elif self._button_size_mode == ButtonSizeMode.DYNAMIC_STRETCH:
            self._resize_buttons_dynamic_stretch(budget_width)
        self._position_buttons()
        self._update_button_frames()
        self._resize_self()

    def _iter_buttons(self):
        for element in self._button_container.children:
            if isinstance(element, ButtonWrapper):
                button = element.button
                if button:
                    yield button

    def _iter_visible_buttons(self):
        for element in self._button_container.children:
            if isinstance(element, ButtonWrapper):
                if element.display:
                    button = element.button
                    if button and button.display:
                        yield button

    def _iter_button_wrappers(self, check_reverse = False):
        elements = self._button_container.children
        if check_reverse and self._overflow_align == OverflowAlign.LEFT:
            elements = reversed(elements)
        return (element for element in elements if isinstance(element, ButtonWrapper))

    def _update_button_overflow(self, budget_width, budget_height):
        overflow_at_wrapper_index = self._check_button_overflow(budget_width, budget_height)
        if overflow_at_wrapper_index is not None:
            self._show_overflow_button()
            if self._orientation == Axis.HORIZONTAL:
                remaining_budget_width = budget_width - (self._overflow_button.get_intrinsic_width() + self._get_button_gap())
                overflow_at_wrapper_index = self._check_button_overflow(remaining_budget_width, budget_height)
            else:
                remaining_budget_height = budget_height - (self._overflow_button.height + self._get_button_gap())
                overflow_at_wrapper_index = self._check_button_overflow(budget_width, remaining_budget_height)
            self._update_overflow_button_variant(overflow_at_wrapper_index)
        else:
            self._hide_overflow_button()
        self._update_button_wrapper_display(overflow_at_wrapper_index)

    def _check_button_overflow(self, budget_width, budget_height):
        main_axis_budget = budget_width if self._orientation == Axis.HORIZONTAL else budget_height
        if main_axis_budget is None:
            return
        visible_button_count = 0
        max_button_size = 0
        total_size = 0
        gap_size = self._get_button_gap()
        for wrapper_index, wrapper in enumerate(self._iter_button_wrappers(check_reverse=True)):
            button = wrapper.button
            if not button or not button.display:
                continue
            visible_button_count += 1
            if self._button_size_mode in {ButtonSizeMode.EQUAL, ButtonSizeMode.STRETCH}:
                if self._orientation == Axis.HORIZONTAL:
                    max_button_size = max(max_button_size, button.get_intrinsic_width())
                elif self._orientation == Axis.VERTICAL:
                    max_button_size = max(max_button_size, button.height)
                total_gap_size = max(visible_button_count - 1, 0) * gap_size
                total_size = max_button_size * visible_button_count + total_gap_size
            elif self._button_size_mode == ButtonSizeMode.DYNAMIC:
                if self._orientation == Axis.HORIZONTAL:
                    button_size = button.get_intrinsic_width()
                else:
                    button_size = button.height
                total_size += button_size
                if visible_button_count > 1:
                    total_size += gap_size
            if main_axis_budget is not None and total_size > main_axis_budget:
                return wrapper_index

    def _resize_buttons_equal(self):
        max_button_width = 0
        for button in self._iter_visible_buttons():
            max_button_width = max(button.get_intrinsic_width(), max_button_width)

        if self._orientation == Axis.HORIZONTAL:
            for button in self._iter_visible_buttons():
                button.width = max_button_width

        elif self._orientation == Axis.VERTICAL:
            for button in self._iter_visible_buttons():
                button.width = max_button_width

            if self._overflow_button is not None and self._overflow_button.display:
                self._overflow_button.width = max_button_width

    def _resize_buttons_dynamic(self):
        for button in self._iter_visible_buttons():
            button.Update_Size_()

        if self._overflow_button is not None and self._overflow_button.display:
            self._overflow_button.Update_Size_()

    def _resize_buttons_stretch(self, budget_width):
        if self._orientation == Axis.VERTICAL:
            if self.align in uiconst.ALIGNMENTS_WITH_RELEVANT_WIDTH:
                budget_width = self.width
            for button in self._iter_visible_buttons():
                button.width = max(budget_width, button.get_intrinsic_width())

            if self._overflow_button is not None and self._overflow_button.display:
                self._overflow_button.width = max(budget_width, self._overflow_button.get_intrinsic_width())
        else:
            buttons = list(self._iter_visible_buttons())
            button_count = len(buttons)
            if self._overflow_button is not None and self._overflow_button.display and button_count > 0:
                budget_width -= self._overflow_button.get_intrinsic_width() + self._get_button_gap()
            total_button_width = budget_width - max(0, button_count - 1) * self._get_button_gap()
            if self.maxWidth:
                total_button_width = min(total_button_width, self.maxWidth)
            for i, button in enumerate(buttons):
                allocated_width = divide_evenly(value=total_button_width, index=i, total_count=button_count)
                button.width = max(allocated_width, button.get_intrinsic_width())

            if self._overflow_button is not None and self._overflow_button.display:
                if button_count > 0:
                    self._overflow_button.width = self._overflow_button.get_intrinsic_width()
                else:
                    self._overflow_button.width = max(budget_width, self._overflow_button.get_intrinsic_width())

    def _resize_buttons_dynamic_stretch(self, budget_width):
        if self._orientation == Axis.VERTICAL:
            if self.align in uiconst.ALIGNMENTS_WITH_RELEVANT_WIDTH:
                budget_width = self.width
            for button in self._iter_visible_buttons():
                button.width = max(budget_width, button.get_intrinsic_width())

            if self._overflow_button is not None and self._overflow_button.display:
                self._overflow_button.width = max(budget_width, self._overflow_button.get_intrinsic_width())
        else:

            def is_icon_button(btn):
                return btn.label is None or btn.label == ''

            buttons = list(self._iter_visible_buttons())
            button_count = len(buttons)
            if self._overflow_button is not None and self._overflow_button.display and button_count > 0:
                budget_width -= self._overflow_button.get_intrinsic_width() + self._get_button_gap()
            total_button_width = budget_width - max(0, button_count - 1) * self._get_button_gap()
            if self.maxWidth:
                total_button_width = min(total_button_width, self.maxWidth)
            for button in buttons:
                if is_icon_button(button):
                    width = button.height
                    button.width = width
                    total_button_width -= width

            big_button_count = len([ b for b in buttons if not is_icon_button(b) ])
            for i, button in enumerate([ b for b in buttons if not is_icon_button(b) ]):
                if is_icon_button(button):
                    continue
                allocated_width = divide_evenly(value=total_button_width, index=i, total_count=big_button_count)
                button.width = max(allocated_width, button.get_intrinsic_width())

            if self._overflow_button is not None and self._overflow_button.display:
                if button_count > 0:
                    self._overflow_button.width = self._overflow_button.get_intrinsic_width()
                else:
                    self._overflow_button.width = max(budget_width, self._overflow_button.get_intrinsic_width())

    def _position_buttons(self):
        left = 0
        top = 0
        button_gap = self._get_button_gap()
        for wrapper in self._iter_button_wrappers():
            if not wrapper.display:
                continue
            button = wrapper.button
            if not button:
                continue
            wrapper.top = top
            wrapper.left = left
            if self._orientation == Axis.VERTICAL:
                top += button.height + button_gap
            else:
                left += button.width + button_gap

        if self._overflow_button and self._overflow_button.display:
            self._overflow_button.top = top
            self._overflow_button.left = left

    def _update_button_frames(self):
        buttons = list(self._iter_visible_buttons())
        if self._overflow_button is not None and self._overflow_button.display:
            buttons.append(self._overflow_button)
        button_count = len(buttons)
        for i, button in enumerate(buttons):
            if self._button_size_mode == ButtonSizeMode.STRETCH and button_count == 1:
                frame_type = ButtonFrameType.CUT_BOTTOM_LEFT_RIGHT
            elif i == button_count - 1:
                if self._button_size_mode == ButtonSizeMode.STRETCH and self._orientation == Axis.VERTICAL:
                    frame_type = ButtonFrameType.CUT_BOTTOM_LEFT_RIGHT
                else:
                    frame_type = ButtonFrameType.CUT_BOTTOM_RIGHT
            elif i == 0 and self._button_size_mode == ButtonSizeMode.STRETCH and not self._orientation == Axis.VERTICAL:
                frame_type = ButtonFrameType.CUT_BOTTOM_LEFT
            else:
                frame_type = ButtonFrameType.RECTANGLE
            button.frame_type = frame_type

    def _update_button_wrapper_display(self, overflow_at_wrapper_index):
        for i, wrapper in enumerate(self._iter_button_wrappers(check_reverse=True)):
            if overflow_at_wrapper_index is None or i < overflow_at_wrapper_index:
                if wrapper.button.display:
                    wrapper.display = True
            elif i >= overflow_at_wrapper_index:
                wrapper.display = False

    def _update_overflow_button_variant(self, overflow_at_wrapper_index):
        variant = ButtonVariant.GHOST
        if self._overflow_button.display:
            for i, wrapper in enumerate(self._iter_button_wrappers(check_reverse=True)):
                if i >= overflow_at_wrapper_index:
                    if IMPORTANCE_BY_VARIANT[wrapper.button.variant] > IMPORTANCE_BY_VARIANT[variant]:
                        variant = wrapper.button.variant

            self._overflow_button.variant = variant

    def _resize_self(self):
        content_width, content_height = self._button_container.GetAutoSize()
        width = 0
        height = 0
        if self._button_size_mode == ButtonSizeMode.STRETCH:
            width = self.width
        elif self.align in uiconst.ALIGNMENTS_WITH_RELEVANT_WIDTH:
            width += content_width
            if self.align in uiconst.ALIGNMENTS_WITH_INCLUDED_HORIZONTAL_PADDING:
                width += self.padLeft + self.padRight
        if self.align in uiconst.ALIGNMENTS_WITH_RELEVANT_HEIGHT:
            height += content_height
            if self.align in uiconst.ALIGNMENTS_WITH_INCLUDED_VERTICAL_PADDING:
                height += self.padTop + self.padBottom
        self.width = width
        self.height = height

    def _update_button_size_mode(self):
        if not self.destroyed:
            self.FlagAlignmentDirty()

    def _get_overflow_menu(self):
        menu = MenuData()
        for wrapper in self._iter_button_wrappers(check_reverse=True):
            if not wrapper.display:
                button = wrapper.button
                if button and button.display:
                    menu_entry_data = button.get_menu_entry_data()
                    if menu_entry_data is not None:
                        menu.AppendMenuEntryData(menu_entry_data)

        return menu

    def _on_button_removed_from_wrapper(self, wrapper, button):
        self._remove_button(button, wrapper)

    def SetAlign(self, align):
        previous_align = self.align
        super(ButtonGroup, self).SetAlign(align)
        if self.align != previous_align:
            self._update_button_container_alignment()

    def UpdateAlignment(self, budgetLeft = 0, budgetTop = 0, budgetWidth = 0, budgetHeight = 0, updateChildrenOnly = False):
        budget_width = reverse_scale_dpi(budgetWidth)
        budget_width = max(0, budget_width - self.padLeft - self.padRight)
        budget_height = reverse_scale_dpi(budgetHeight)
        budget_height = max(0, budget_height - self.padTop - self.padBottom)
        self._update_layout(budget_width, budget_height)
        return super(ButtonGroup, self).UpdateAlignment(budgetLeft, budgetTop, budgetWidth, budgetHeight, updateChildrenOnly)


class ButtonGroupChildrenList(PyChildrenList):

    def __init__(self, button_group):
        super(ButtonGroupChildrenList, self).__init__(owner=button_group, children=button_group.children)

    def append(self, obj):
        return self.insert(-1, obj)

    def insert(self, idx, obj):
        button_group = self.GetOwner()
        if button_group:
            if not isinstance(obj, Button):
                log.error('Warning while adding child to ButtonGroup at {}'.format(_prepare_ancestor_chain_debug_description(button_group)))
                super(ButtonGroupChildrenList, self).insert(idx, obj)
            else:
                button_group.add_button(obj, index=idx)
            return self

    def remove(self, obj):
        button_group = self.GetOwner()
        if button_group:
            button_group.remove_button(obj)
            return self


def _prepare_ancestor_chain_debug_description(element):
    parts = []
    while element:
        parts.append('{}(name="{}")'.format(element.__class__.__name__, getattr(element, 'name', '???')))
        element = getattr(element, 'parent', None)

    return '.'.join(reversed(parts))


class OverflowButton(Button):
    expandOnLeft = True

    def __init__(self, get_menu, **kwargs):
        self._get_menu = get_menu
        super(OverflowButton, self).__init__(hint=localization.GetByLabel('UI/Common/More'), texturePath=eveicon.more_vertical, **kwargs)

    def GetMenu(self):
        return self._get_menu()

    def GetMenuPosition(self, element):
        return (self.absoluteLeft, self.absoluteBottom)


class ButtonWrapper(ContainerAutoSize):

    def __init__(self, button, on_child_removed, **kwargs):
        self._button_ref = weakref.ref(button)
        self._on_child_removed = on_child_removed
        super(ButtonWrapper, self).__init__(**kwargs)
        if button.parent is not None:
            button.SetParent(None)
        button.align = uiconst.TOPLEFT
        button.on_display_changed.connect(self._on_button_display_changed)
        button.SetParent(self)
        self.display = button.display

    @property
    def button(self):
        return self._button_ref()

    def Close(self):
        button = self._button_ref()
        if button:
            button.on_display_changed.disconnect(self._on_button_display_changed)
        super(ButtonWrapper, self).Close()

    def GetChildrenList(self):
        return ButtonWrapperChildrenList(owner=self, on_child_removed=self._emit_on_child_removed)

    def _emit_on_child_removed(self, child):
        self._on_child_removed(self, child)

    def _on_button_display_changed(self, button):
        self.display = button.display
        if self.parent and not self.parent.destroyed:
            self.parent.FlagAlignmentDirty()


class ButtonWrapperChildrenList(UIChildrenListAutoSize):

    def __init__(self, owner, on_child_removed):
        self._on_child_removed = on_child_removed
        super(ButtonWrapperChildrenList, self).__init__(owner)

    def remove(self, obj):
        super(ButtonWrapperChildrenList, self).remove(obj)
        owner = self.GetOwner()
        if owner:
            self._on_child_removed(obj)
