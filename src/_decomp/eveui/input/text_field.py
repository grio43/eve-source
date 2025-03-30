#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveui\input\text_field.py
import platform
import re
import eveui
import menu
import proper
import signals
import threadutils
import uthread2
import weakness
from carbonui import TextColor
from carbonui.decorative.inputUnderlay import InputUnderlay
from eveui import Container, ContainerAutoSize, EveLabelMedium, Fill
from eveui.animation import animate
from eveui.audio import Sound
from eveui.behavior.clipboard import ClipboardBehavior
from eveui.behavior.history import HistoryBehavior
from eveui.behavior.ime import ImeBehavior
from eveui.compatibility import CarbonEventHandler
from eveui.constants import Align, State
from eveui.decorators import lazy, skip_if_destroyed
from eveui.keyboard import Key
from eveui.mouse import Mouse
from eveui.once_per_frame import wait_for_next_frame

class TextField(ClipboardBehavior, HistoryBehavior, ImeBehavior, CarbonEventHandler, proper.Observable, Container):
    CARET_COLOR = (1.0, 1.0, 1.0, 1.0)
    FOCUS_HIGHLIGHT_COLOR_IDLE = (1.0, 1.0, 1.0, 0.2)
    FOCUS_HIGHLIGHT_COLOR_FOCUSED = (0.5, 0.5, 0.5, 1.0)
    SELECTION_HIGHLIGHT_COLOR = (0.5, 0.5, 0.5, 0.5)
    UNDERLAY_COLOR_IDLE = (0.1, 0.1, 0.1, 0.8)
    UNDERLAY_COLOR_ACTIVE = (0.12, 0.12, 0.12, 0.8)
    default_height = 32
    default_state = State.normal

    def __init__(self, text = None, controller = None, icon = None, **kwargs):
        self.controller = controller or TextFieldController(text=text)
        self._icon = icon
        self.__is_drag_selection_active = False
        self.__focus_highlight = None
        super(TextField, self).__init__(**kwargs)
        self._layout()
        self._update_text()
        self._update_caret_position()
        self._update_placeholder()
        self._update_selection()
        self._update_text_scroll()
        self._update_focus()
        self.controller.bind(caret_position=self._on_caret_position_changed, selection=self._on_selection_changed, text=self._on_text_changed)
        self.controller.on_save_history.connect(self.save_state_to_history)

    @proper.alias
    def text(self):
        return self.controller.text

    @text.setter
    def text(self, text):
        self.controller.text = text

    @proper.ty(default=None)
    def placeholder(self):
        pass

    @lazy
    def leading_container(self):
        return ContainerAutoSize(parent=self, align=Align.to_left, idx=self._text_clipper.GetOrder())

    @lazy
    def trailing_container(self):
        return ContainerAutoSize(parent=self, align=Align.to_right, idx=self._text_clipper.GetOrder() + 1)

    def on_char(self, character):
        self.controller.insert_text(character)
        return True

    def on_click(self, click_count):
        super(TextField, self).on_click(click_count)
        if click_count > 2:
            self.controller.select_all()
        elif click_count > 1:
            self.controller.select_word()
        return True

    def on_key_down(self, key):
        is_mac = platform.system() == 'Darwin'

        def k(win, mac):
            if is_mac:
                return mac
            return win

        ctrl = Key.control.is_down
        cmd = Key.win_left.is_down
        alt = Key.menu.is_down
        if key == Key.delete:
            self.controller.do_delete(word=Key.control.is_down)
        elif key == Key.backspace:
            self.controller.do_backspace(word=Key.control.is_down)
        elif key == Key.left and (not is_mac or not cmd):
            self.controller.move_caret_left(select=Key.shift.is_down, word=k(win=ctrl, mac=alt))
        elif key == Key.right and (not is_mac or not cmd):
            self.controller.move_caret_right(select=Key.shift.is_down, word=k(win=ctrl, mac=alt))
        elif key == Key.home or is_mac and key == Key.left and cmd:
            self.controller.move_caret_home(select=Key.shift.is_down)
        elif key == Key.end or is_mac and key == Key.right and cmd:
            self.controller.move_caret_to_end(select=Key.shift.is_down)
        elif key == Key.a and k(win=ctrl, mac=alt):
            self.controller.select_all()
        else:
            return super(TextField, self).on_key_down(key)
        return True

    def on_mouse_down(self, button):
        if button == Mouse.left:
            self._start_drag_selection()

    def on_mouse_up(self, button):
        if button == Mouse.left:
            self._stop_drag_selection()
            self.controller.caret_position = self._get_caret_position_at_cursor()

    def on_mouse_enter(self):
        Sound.text_field_hover.play()

    def on_mouse_exit(self):
        pass

    def on_copy(self):
        text = self.controller.selected_text
        if text is None:
            text = self.controller.text
        return text

    def on_cut(self):
        if self.controller.selection is None:
            return
        text = self.controller.selected_text
        self.controller.delete_selection()
        return text

    def on_paste(self, text):
        self.controller.insert_text(text)

    def get_state_for_history(self):
        return self.controller.get_state_for_history()

    def set_state_from_history(self, state):
        self.controller.set_state_from_history(state)

    def _layout(self):
        self._underlay = InputUnderlay(name='underlay', bgParent=self)
        if self._icon:
            icon_cont = ContainerAutoSize(name='icon_cont', parent=self, align=Align.to_left, padLeft=8)
            eveui.Sprite(parent=icon_cont, align=Align.center_left, pos=(0, 0, 16, 16), color=TextColor.SECONDARY, texturePath=self._icon)
        self._text_clipper = Container(name='text_clipper', parent=self, clipChildren=True, padding=(8, 0, 8, 0))
        self._text_scroll = Container(name='text_scroll', parent=self._text_clipper)
        self._caret = Caret(name='caret', parent=self._text_scroll, align=Align.center_left, color=self.CARET_COLOR, pos=(0, 0, 1, 14), active=self.focused, blink=True)
        self._text_label = EveLabelMedium(name='text', parent=self._text_scroll, align=Align.center_left, state=State.disabled, maxLines=1)
        self._selection = Fill(name='selection', parent=self._text_scroll, align=Align.center_left, state=State.disabled, color=self.SELECTION_HIGHLIGHT_COLOR, height=14)
        self._selection.display = False
        self._placeholder_label = EveLabelMedium(name='placeholder', parent=self._text_clipper, align=Align.center_left, state=State.disabled, maxLines=1, text=self.placeholder, opacity=0.4)
        self._text_clipper._OnSizeChange_NoBlock = weakness.WeakMethod(self._on_clipper_size_changed)

    @threadutils.threaded
    def _start_drag_selection(self):
        if self.__is_drag_selection_active:
            return
        self.__is_drag_selection_active = True
        self.controller.move_caret_to(self._get_caret_position_at_cursor(), select=Key.shift.is_down)
        while self.__is_drag_selection_active and not self.destroyed:
            self.controller.move_caret_to(self._get_caret_position_at_cursor(), select=True)
            wait_for_next_frame()

    def _stop_drag_selection(self):
        self.__is_drag_selection_active = False

    def _get_caret_position_at_cursor(self):
        left, _ = self._text_label.GetAbsolutePosition()
        mouse_x, _ = Mouse.position()
        relative_cursor_position = mouse_x - left
        index, _ = self._text_label.GetIndexUnderPos(relative_cursor_position)
        return index

    def _on_clipper_size_changed(self, new_width, new_height):
        if new_width:
            self._update_text_scroll()

    def on_focused(self, is_focused):
        self._update_focus()
        self._update_selection()
        self._update_text_scroll()

    def _update_focus(self):
        if self.focused:
            self._caret.is_active = True
        else:
            self._caret.is_active = False

    def __show_focus_highlight(self):
        if self.__focus_highlight is None:
            self.__focus_highlight = Fill(parent=self.__focus_highlight_container, align=Align.to_left_prop, width=0.0, color=self.FOCUS_HIGHLIGHT_COLOR_FOCUSED)
            animate(self.__focus_highlight, 'width', end_value=1.0, duration=0.15)

    def __hide_focus_highlight(self):
        if self.__focus_highlight is not None:
            self.__focus_highlight.Close()
            self.__focus_highlight = None

    def on_placeholder(self, placeholder):
        self._placeholder_label.SetText(self.placeholder)
        self._update_placeholder()

    def _update_placeholder(self):
        if self.controller.text:
            self._placeholder_label.Hide()
        else:
            self._placeholder_label.Show()

    @skip_if_destroyed
    def _on_caret_position_changed(self, *args):
        self._update_caret_position()
        self._update_text_scroll()

    def _update_caret_position(self):
        _, self._caret.left = self._text_label.GetWidthToIndex(self.controller.caret_position)
        self._caret.reset_blink_cycle()

    def _update_text_scroll(self):
        if not self.focused:
            self._text_scroll.left = 0
        else:
            clipper_width, _ = self._text_clipper.GetAbsoluteSize()
            if self._text_label.textwidth < clipper_width:
                self._text_scroll.left = 0
            elif self._text_label.textwidth + self._text_scroll.left < clipper_width:
                self._text_scroll.left = clipper_width - self._text_label.textwidth - self._caret.width
            if self._caret.left > clipper_width - self._text_scroll.left:
                self._text_scroll.left = clipper_width - self._caret.left - self._caret.width
            elif self._caret.left < -self._text_scroll.left:
                self._text_scroll.left = -self._caret.left
        self._update_text_fade()

    def _update_text_fade(self):
        clipper_width, _ = self._text_clipper.GetAbsoluteSize()
        if self._text_scroll.left == 0:
            self._text_label.SetLeftAlphaFade(0, 0)
        else:
            self._text_label.SetLeftAlphaFade(abs(self._text_scroll.left), 10)
        self._text_label.SetRightAlphaFade(clipper_width - self._text_scroll.left, 10)

    def _on_text_changed(self, *args):
        self._update_text()
        self._update_text_scroll()
        self._update_placeholder()

    def _update_text(self):
        self._text_label.SetText(self.controller.text)

    def _on_selection_changed(self, *args):
        self._update_selection()

    def _update_selection(self):
        if self.controller.selection is None or not self.focused:
            self._selection.display = False
        else:
            _, start = self._text_label.GetWidthToIndex(self.controller.selection_start)
            _, end = self._text_label.GetWidthToIndex(self.controller.selection_end)
            self._selection.left = start
            self._selection.width = end - start
            self._selection.display = True

    def GetMenu(self):
        menu_entries = super(TextField, self).GetMenu()
        menu_entries.append((menu.MenuLabel('UI/Common/SelectAll'), self.controller.select_all))
        return menu_entries


class Caret(Fill):
    default_color = (1.0, 1.0, 1.0, 0.8)
    default_state = State.disabled
    default_width = 1
    BLINK_INTERVAL = 0.4

    def __init__(self, active = False, blink = True, **kwargs):
        super(Caret, self).__init__(**kwargs)
        self._is_active = active
        self._is_blinking = blink
        self._blink_interval = self.BLINK_INTERVAL
        self.display = self._is_active
        if self._is_blinking:
            self._start_blinking()

    @property
    def is_active(self):
        return self._is_active

    @is_active.setter
    def is_active(self, is_active):
        self._is_active = is_active
        self.display = is_active

    def reset_blink_cycle(self):
        if not self._is_blinking:
            return
        self.display = True
        self._start_blinking()

    @threadutils.highlander_threaded
    def _start_blinking(self):
        while not self.destroyed and self._is_blinking:
            uthread2.sleep(self._blink_interval)
            if self.is_active:
                self.display = not self.display

    def _stop_blinking(self):
        self._is_blinking = False


class Action(object):
    insert = 1
    delete = 2
    move_caret = 3


class TextFieldController(proper.Observable):

    def __init__(self, **kwargs):
        super(TextFieldController, self).__init__(**kwargs)
        self.on_save_history = signals.Signal(signalName='on_save_history')
        self._last_action = None

    @proper.ty(factory=unicode)
    def text(self):
        pass

    @text.validator
    def _validate_text(self, text):
        if text is None:
            return u''
        return text

    @text.after_change
    def _ensure_caret_and_selection_valid(self, text):
        with self.deferred_dispatch():
            self.caret_position = min(self.caret_position, len(text))
            if self.selection:
                self.selection = (min(self.selection_start, len(text)), min(self.selection_end, len(text)))

    @proper.ty(default=0)
    def caret_position(self):
        pass

    @caret_position.validator
    def _clamp_caret_position(self, caret_position):
        if caret_position < 0:
            caret_position = len(self.text) + caret_position + 1
        if caret_position < 0 or len(self.text) < caret_position:
            raise ValueError('caret position out of range')
        return caret_position

    @proper.ty(default=None)
    def selection(self):
        pass

    @selection.validator
    def _clamp_selection(self, selection):
        if selection is None:
            return
        start = self._clamp_caret_position(selection[0])
        end = self._clamp_caret_position(selection[1])
        if start > end:
            raise ValueError('invalid selection')
        elif start == end:
            return
        return (start, end)

    @proper.alias
    def selection_start(self):
        if self.selection is not None:
            return self.selection[0]

    @proper.alias
    def selection_end(self):
        if self.selection is not None:
            return self.selection[1]

    @proper.alias
    def selected_text(self):
        if self.selection is None:
            return
        return self.text[self.selection_start:self.selection_end]

    def insert_text(self, text):
        insert_start = insert_end = self.caret_position
        if self.selection is not None:
            insert_start, insert_end = self.selection
        new_text = self.text[:insert_start] + text + self.text[insert_end:]
        is_first_insert = not self.text
        is_selection_insert = insert_start != insert_end
        is_end_of_word = _is_end_of_word_at(new_text, insert_start)
        force_save_history = is_first_insert or is_selection_insert or is_end_of_word
        self._on_action_performed(Action.insert, force_save_history=force_save_history)
        with self.deferred_dispatch():
            self.selection = None
            self.text = new_text
            self.caret_position = insert_start + len(text)

    def replace_text(self, text):
        with self.deferred_dispatch():
            self.text = text
            self.selection = None
            self.caret_position = -1

    def clear_text(self):
        self.text = u''

    def delete_selection(self):
        if self.selection is None:
            return
        self._on_action_performed(Action.delete)
        with self.deferred_dispatch():
            selection_start, selection_end = self.selection
            self.caret_position = selection_start
            self.selection = None
            self.text = self.text[:selection_start] + self.text[selection_end:]

    def select_all(self):
        with self.deferred_dispatch():
            self.selection = (0, len(self.text))
            self.caret_position = -1

    def select_word(self):
        right = _find_boundary_right_from(self.text, self.caret_position)
        left = _find_boundary_left_from(self.text, self.caret_position)
        if _is_start_of_word_at(self.text, self.caret_position):
            left = self.caret_position
        elif _is_end_of_word_at(self.text, self.caret_position):
            right = self.caret_position
        with self.deferred_dispatch():
            self.selection = (left, right)
            self.caret_position = right

    def cancel_selection(self):
        self.selection = None

    def do_backspace(self, word = False):
        if self.selection is not None:
            self.delete_selection()
        elif self.caret_position > 0:
            self._on_action_performed(Action.delete)
            new_position = self.caret_position - 1
            if word:
                new_position = _find_boundary_left_from(self.text, new_position)
            with self.deferred_dispatch():
                self.text = self.text[:new_position] + self.text[self.caret_position:]
                self.caret_position = new_position

    def do_delete(self, word = False):
        if self.selection is not None:
            self.delete_selection()
        elif self.caret_position < len(self.text):
            self._on_action_performed(Action.delete)
            new_position = self.caret_position + 1
            if word:
                new_position = _find_boundary_right_from(self.text, self.caret_position)
            with self.deferred_dispatch():
                self.text = self.text[:self.caret_position] + self.text[new_position:]

    def move_caret_left(self, select = False, word = False):
        if word:
            new_position = _find_boundary_left_from(self.text, self.caret_position)
        elif not select and self.selection is not None:
            new_position = self.selection_start
        else:
            new_position = max(self.caret_position - 1, 0)
        self.move_caret_to(new_position, select=select)

    def move_caret_right(self, select = False, word = False):
        if word:
            new_position = _find_boundary_right_from(self.text, self.caret_position)
        elif not select and self.selection is not None:
            new_position = self.selection_end
        else:
            new_position = min(self.caret_position + 1, len(self.text))
        self.move_caret_to(new_position, select=select)

    def move_caret_home(self, select = False):
        self.move_caret_to(0, select=select)

    def move_caret_to_end(self, select = False):
        self.move_caret_to(len(self.text), select=select)

    def move_caret_to(self, position, select = False):
        self._on_action_performed(Action.move_caret)
        with self.deferred_dispatch():
            if select:
                self._update_selection(position)
            else:
                self.selection = None
            self.caret_position = position

    def get_state_for_history(self):
        return (self.text,
         self.caret_position,
         self.selection,
         self._last_action)

    def set_state_from_history(self, state):
        text, caret_position, selection, last_action = state
        with self.deferred_dispatch():
            self.text = text
            self.caret_position = caret_position
            self.selection = selection
            self._last_action = last_action

    def _on_action_performed(self, action, force_save_history = False):
        is_different_action = action != self._last_action
        if is_different_action and action != Action.move_caret or force_save_history:
            self.on_save_history()
        self._last_action = action

    def _update_selection(self, new_caret_position):
        if self.selection is None:
            self.selection = (min(new_caret_position, self.caret_position), max(new_caret_position, self.caret_position))
        else:
            caret_position_change = new_caret_position - self.caret_position
            start = self.selection_start
            end = self.selection_end
            if self.caret_position == self.selection_start:
                start += caret_position_change
            elif self.caret_position == self.selection_end:
                end += caret_position_change
            else:
                start = min(new_caret_position, self.caret_position)
                end = max(new_caret_position, self.caret_position)
            self.selection = (min(start, end), max(start, end))


def _iter_text_gaps(text):
    for match in re.finditer('\\A|\\s+|\\Z', text, flags=re.UNICODE):
        yield (match.start(), match.end())


def _find_boundary_left_from(text, position):
    boundary_position = 0
    for _, gap_end in _iter_text_gaps(text):
        if gap_end >= position:
            break
        boundary_position = gap_end

    return boundary_position


def _find_boundary_right_from(text, position):
    boundary_position = len(text)
    for gap_start, _ in _iter_text_gaps(text):
        if gap_start > position:
            boundary_position = gap_start
            break

    return boundary_position


def _is_end_of_word_at(text, index):
    for match in re.finditer('(?<!\\s)\\s', text, flags=re.UNICODE):
        if match.start() == index:
            return True

    return False


def _is_start_of_word_at(text, index):
    for match in re.finditer('(?:(?<=\\s)|\\A)\\S', text, flags=re.UNICODE):
        if match.start() == index:
            return True

    return False
