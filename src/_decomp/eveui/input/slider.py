#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveui\input\slider.py
from __future__ import division
from bisect import bisect_left
import collections
import contextlib
import itertools
import math
import numbers
import caching
import itertoolsext
from mathext import clamp
import proper
import signals
import threadutils
from eveui import Container, Fill, EveLabelSmall
from eveui.animation import animate
from eveui.behavior.focus import FocusBehavior
from eveui.compatibility import CarbonEventHandler
from eveui.constants import Align, State
from eveui.decorators import lazy
from eveui.keyboard import Key
from eveui.mouse import Mouse
from eveui.once_per_frame import wait_for_next_frame

class VerticalCenteredContainer(CarbonEventHandler, Container):

    def UpdateAlignment(self, budgetLeft = 0, budgetTop = 0, budgetWidth = 0, budgetHeight = 0, updateChildrenOnly = False):
        alignment_result = super(VerticalCenteredContainer, self).UpdateAlignment(budgetLeft, budgetTop, budgetWidth, budgetHeight, updateChildrenOnly)
        if self.children:
            for child in self.children:
                child.top = int(round((self.height - child.height) / 2.0))

        return alignment_result


class SliderController(proper.Observable):

    def __init__(self, **kwargs):
        super(SliderController, self).__init__(**kwargs)

    @proper.ty(default=(0, 100))
    def bounds(self):
        pass

    @proper.alias
    def min(self):
        if self.bounds is not None:
            return self.bounds[0]

    @proper.alias
    def max(self):
        if self.bounds is not None:
            return self.bounds[1]

    @proper.ty(default=1)
    def step(self):
        pass

    @proper.ty(default=None)
    def marks(self):
        pass

    @proper.ty(default=False)
    def mark_at_step(self):
        pass

    @proper.ty
    def value(self):
        pass

    @proper.ty(default=0)
    def min_distance(self):
        pass

    @proper.ty(default=True)
    def allow_cross(self):
        pass

    @proper.alias
    def value_count(self):
        if isinstance(self.value, numbers.Number):
            return 1
        return len(self.value)

    def get_value_at(self, value_index):
        if isinstance(self.value, numbers.Number):
            if value_index != 0:
                raise IndexError()
            return self.value
        else:
            return self.value[value_index]

    def normalize_value(self, value):
        return (value - self.min) / (self.max - self.min)

    def increment(self, value_index = 0):
        current_value = self.get_value_at(value_index)
        next_value = itertoolsext.first_or_default(itertoolsext.skip(self.__iter_valid_stops(value_index, start=current_value), 1), default=current_value)
        new_value, new_value_index = self.__get_replaced_value_at(value_index, next_value)
        self.value = ValidatedValue(new_value)
        return new_value_index

    def decrement(self, value_index = 0):
        current_value = self.get_value_at(value_index)
        next_value = itertoolsext.first_or_default(itertoolsext.skip(self.__iter_valid_stops(value_index, start=current_value, reverse=True), 1), default=current_value)
        new_value, new_value_index = self.__get_replaced_value_at(value_index, next_value)
        self.value = ValidatedValue(new_value)
        return new_value_index

    def replace_value_at(self, value_index, value):
        new_value, new_value_index = self.__get_replaced_value_at(value_index, value)
        self.value = ValidatedValue(new_value)
        return new_value_index

    def iter_marks(self):
        marks = self.__iter_marks()
        if self.mark_at_step:
            steps = ((s, self.__step_label_func(s)) for s in self.__iter_steps_from())
            return itertoolsext.unique_sorted(itertoolsext.merge_sorted(marks, steps, key=lambda x: x[0]), transform=lambda x: x[0])
        else:
            return marks

    def iter_value(self):
        if isinstance(self.value, numbers.Number):
            return iter([self.value])
        else:
            return iter(self.value)

    def is_value_selected(self, value):
        if isinstance(self.value, numbers.Number):
            return value <= self.value
        else:
            return min(self.value) <= value <= max(self.value)

    @proper.alias
    def __mark_values(self):
        return list((value for value, label in self.__iter_marks()))

    @property
    def __step_label_func(self):
        if callable(self.mark_at_step):
            return self.mark_at_step
        return str

    def __iter_valid_stops(self, value_index, start = None, reverse = False):
        valid_stop_iter = self.__iter_stops(start=start, reverse=reverse)
        if not self.allow_cross:
            if value_index > 0:
                valid_stop_iter = filter(lambda v: v > self.value[value_index - 1], valid_stop_iter)
            if value_index + 1 < self.value_count:
                valid_stop_iter = filter(lambda v: v < self.value[value_index + 1], valid_stop_iter)
        valid_stop_iter = filter(lambda v: all((i == value_index or abs(v - self.value[i]) >= self.min_distance for i in range(self.value_count))), valid_stop_iter)
        return valid_stop_iter

    def __get_closest_valid_stop(self, value_index, value):
        valid_stop_iter = self.__iter_valid_stops(value_index, start=self.value[value_index], reverse=value < self.value[value_index])
        return itertoolsext.first_or_default(sorted(valid_stop_iter, key=lambda v: (abs(v - value), abs(v - self.value[value_index]))), default=self.value[value_index])

    def __get_replaced_value_at(self, value_index, value):
        if isinstance(self.value, numbers.Number):
            if value_index != 0:
                raise IndexError()
            return (value, value_index)
        elif value == self.value[value_index]:
            return (self.value, value_index)
        else:
            closest_valid_stop = self.__get_closest_valid_stop(value_index, value)
            new_value = [ (closest_valid_stop if i == value_index else v) for i, v in enumerate(self.value) ]
            new_value = sorted(new_value)
            if new_value[value_index] != closest_valid_stop:
                new_value_index = new_value.index(closest_valid_stop)
            else:
                new_value_index = value_index
            return (new_value, new_value_index)

    def __iter_marks(self):
        if self.marks is None:
            raise StopIteration
        if self.marks is True:
            for value in frange(self.min, self.max + self.step, self.step):
                yield (value, str(value))

        elif isinstance(self.marks, numbers.Number):
            start = self.min + self.marks
            for value in frange(start, self.max, self.marks):
                yield (value, str(value))

        elif hasattr(self.marks, 'iteritems'):
            for value, label in self.marks.iteritems():
                if self.min <= value <= self.max:
                    yield (value, label)

        else:
            for value in self.marks:
                if self.min <= value <= self.max:
                    yield (value, str(value))

    def __iter_stops(self, start = None, reverse = False):
        return itertoolsext.unique_sorted(itertoolsext.merge_sorted(self.__iter_marks_from(start, reverse=reverse), self.__iter_steps_from(start, reverse=reverse), reverse=reverse))

    def __iter_marks_from(self, start = None, reverse = False):
        if start is None:
            start = self.max if reverse else self.min
        if reverse:
            return itertools.dropwhile(lambda x: x >= start, reversed(self.__mark_values))
        else:
            return itertools.dropwhile(lambda x: x <= start, self.__mark_values)

    def __iter_steps_from(self, start = None, reverse = False):
        if self.step is None:
            return iter([])
        else:
            if start is None:
                start = self.max if reverse else self.min
            if reverse:
                start = math.ceil((start - self.min) / self.step) * self.step + self.min
                return frange(start, self.min - self.step, -self.step)
            start = math.floor((start - self.min) / self.step) * self.step + self.min
            return frange(start, self.max + self.step, self.step)

    @value.validator
    def __validate_value(self, value):
        if value is None:
            raise ValueError('Value must not be None')
        if isinstance(value, ValidatedValue):
            return value.value
        elif isinstance(value, numbers.Number):
            return self.__constrain_value_to_stops(value)
        else:
            return [ self.__constrain_value_to_stops(v) for v in value ]

    @marks.validator
    def __validate_marks(self, marks):
        if marks is None or isinstance(marks, numbers.Number):
            return marks
        elif hasattr(marks, 'iteritems'):
            return collections.OrderedDict(sorted(marks.iteritems()))
        else:
            return sorted(marks)

    def __constrain_value_to_stops(self, value):
        closest_step = None
        if self.step:
            closest_step = find_closest_in_range(self.min, self.max, self.step, value)
        closest_mark = None
        if self.marks:
            closest_mark = take_closest(self.__mark_values, value)
        values = filter(lambda x: x is not None, (closest_step, closest_mark))
        return take_closest(sorted(values), value)


class ValidatedValue(object):

    def __init__(self, value):
        self.value = value


class Slider(proper.Observable, CarbonEventHandler, Container):
    default_height = 8
    default_width = 160
    default_state = State.normal

    def __init__(self, value = None, bounds = (0, 100), step = 1, marks = None, mark_at_step = False, show_mark_label = True, mark_label_format = None, on_change = None, on_change_committed = None, allow_cross = True, min_distance = 0, **kwargs):
        if bounds is None:
            if marks is None:
                raise ValueError('Bounds value of None implies that marks should be used to determine the bounds, but marks was None as well.')
            try:
                sorted_marks = sorted(marks)
                bounds = (sorted_marks[0], sorted_marks[-1])
            except TypeError:
                raise ValueError('Bounds value of None implies that marks should be used to determine the bounds, but marks is not iterable.')

        if step is None and marks is None:
            raise ValueError('You must define either step or marks')
        self.controller = SliderController(bounds=bounds, step=step, marks=marks, value=value, mark_at_step=mark_at_step, allow_cross=allow_cross, min_distance=min_distance)
        self._show_mark_label = show_mark_label
        if self._show_mark_label:
            kwargs['height'] = max(self.default_height + 12, kwargs.get('height', 0))
        self._mark_label_format = mark_label_format
        super(Slider, self).__init__(**kwargs)
        self._handles = []
        self._tracks = []
        self._marks = []
        self.__drag_track_thread = None
        self.__mark_container = None
        self.__layout()
        self.controller.bind(value=self.__on_value_changed, marks=self.__on_marks_changed)
        if on_change is not None:
            self.on_change.connect(on_change)
        if on_change_committed is not None:
            self.on_change_committed.connect(on_change_committed)

    @caching.lazy_property
    def on_change(self):
        return signals.Signal(signalName='on_change')

    @caching.lazy_property
    def on_change_committed(self):
        return signals.Signal(signalName='on_change_committed')

    @proper.alias
    def value(self):
        return self.controller.value

    @value.setter
    def value(self, value):
        self.controller.value = value

    def commit_value(self, value):
        with self.__transaction():
            self.value = value

    def on_mouse_down(self, button):
        if button == Mouse.left:
            self.__start_drag_track()
            return True

    def __find_closest_handle(self, x, y):
        if isinstance(self.controller.value, numbers.Number):
            return 0
        else:
            value_normalized = self._position_to_value_normalized(x, y)
            value_denormalized = value_normalized * (self.controller.max - self.controller.min) + self.controller.min
            closest_value = take_closest(list(sorted(self.controller.value)), value_denormalized)
            handle_index = self.controller.value.index(closest_value)
            return handle_index

    def __start_drag_track(self):
        if not self.__drag_track_thread:
            self.__drag_track_thread = self.__drag_track()

    @contextlib.contextmanager
    def __transaction(self):
        initial_value = self.controller.value
        try:
            yield
        finally:
            new_value = self.controller.value
            if new_value != initial_value:
                self.on_change_committed(self.value)

    def __step(self, value_index, steps):
        with self.__transaction():
            if steps > 0:
                new_value_index = self.controller.increment(value_index)
            else:
                new_value_index = self.controller.decrement(value_index)
            self._handles[new_value_index].focused = True

    @threadutils.threaded
    def __drag_track(self):
        try:
            x, y = Mouse.position()
            value_index = self.__find_closest_handle(x, y)
            self._handles[value_index].focused = True
            with self.__transaction():
                while Mouse.left.is_down and not self.destroyed:
                    x, y = Mouse.position()
                    value_normalized = self._position_to_value_normalized(x, y)
                    value = value_normalized * (self.controller.max - self.controller.min) + self.controller.min
                    value_index = self.controller.replace_value_at(value_index, value)
                    self._handles[value_index].focused = True
                    wait_for_next_frame()

        finally:
            self.__drag_track_thread = None

    def _position_to_value_normalized(self, x, y):
        track_left, track_top, track_width, track_height = self._rail.GetAbsolute()
        value_normalized = (x - track_left) / track_width
        return clamp(value_normalized, 0.0, 1.0)

    def __on_value_changed(self, controller, value):
        self.__update_handles()
        self.on_change(self.value)

    def __update_handles(self):
        for handle in self._handles:
            left = self.__get_handle_left(handle.value_index)
            handle.left = left

        for track, (left, right) in itertools.izip(self._tracks, self.__iter_track_positions()):
            track.left = left
            track.width = right - left

    def __on_marks_changed(self, controller, marks):
        self.__mark_container.Flush()
        del self._marks[:]
        self.__create_marks()

    def __layout(self):
        self._main_cont = VerticalCenteredContainer(parent=self, align=Align.to_top, height=Handle.default_height)
        pad = Handle.default_width / 2 - Mark.default_width / 2
        self._rail = Container(parent=self._main_cont, align=Align.to_top_no_push, height=2, padding=(pad,
         0,
         pad,
         0))
        Fill(parent=self._rail, opacity=0.2)
        self.__create_handles()
        self.__create_tracks()
        self.__create_marks()
        self._main_cont._OnSizeChange_NoBlock = self.__on_main_cont_size_change
        self._rail._OnSizeChange_NoBlock = self.__on_rail_size_change

    def __create_handles(self):
        values = self.controller.value
        if isinstance(values, numbers.Number):
            values = [values]
        for i, value in enumerate(values):
            handle = Handle(parent=self._main_cont, align=Align.top_left, left=self.__get_handle_left(i), value_index=i, on_step=self.__step)
            self._handles.append(handle)

    def __get_handle_left(self, value_index):
        width, _ = self._main_cont.GetAbsoluteSize()
        value = self.controller.get_value_at(value_index)
        value_normalized = self.controller.normalize_value(value)
        return value_normalized * (width - Handle.default_width)

    def __get_value_left(self, value):
        width, _ = self._rail.GetAbsoluteSize()
        value_normalized = self.controller.normalize_value(value)
        return value_normalized * width

    def __create_tracks(self):
        for a, b in self.__iter_track_positions():
            track = Fill(parent=self._rail, align=Align.top_left, height=2, left=a + Handle.default_width / 2, width=b - a + Handle.default_width / 2, color=(0.75, 0.75, 0.75, 1.0))
            self._tracks.append(track)

    def __iter_track_positions(self):
        if isinstance(self.controller.value, numbers.Number):
            values = [self.controller.min, self.controller.value]
        else:
            values = self.controller.value
        pairs = itertools.izip(values, itertoolsext.skip(values, 1))
        for a, b in pairs:
            a_left = self.__get_value_left(a)
            b_left = self.__get_value_left(b)
            yield (a_left, b_left)

    def __create_marks(self):
        self.__mark_container = Container(parent=self._main_cont, align=Align.to_top_no_push, padTop=2, height=2)
        for value, label in self.controller.iter_marks():
            if self._mark_label_format:
                label = self._mark_label_format(value)
            left = self.__get_mark_left(value)
            self._marks.append(Mark(parent=self.__mark_container, align=Align.top_left, left=left, value=value, slider_controller=self.controller, label=label if self._show_mark_label else None))

    def __on_main_cont_size_change(self, width, height):
        for mark in self._marks:
            mark.left = self.__get_mark_left(mark.value)

    def __on_rail_size_change(self, width, height):
        self.__update_handles()

    def __get_mark_left(self, value):
        value_normalized = (value - self.controller.min) / (self.controller.max - self.controller.min)
        width, _ = self.GetAbsoluteSize()
        left = value_normalized * (width - Handle.default_width) + Handle.default_width / 2 - Mark.default_width / 2
        return left


class OptionSlider(Slider):

    def __init__(self, options, value = None, show_mark_label = True, mark_label_format = None, on_change = None, on_change_committed = None, **kwargs):
        self.options = options
        if value is None:
            value = options[0]
        elif isinstance(value, numbers.Number):
            value = options.index(value)
        else:
            value = [ options.index(v) for v in value ]
        wrapped_mark_label_format = None
        if mark_label_format is not None:
            wrapped_mark_label_format = lambda value: mark_label_format(self.options[int(value)])
        kwargs['bounds'] = (0, len(options) - 1)
        kwargs['marks'] = {i:option for i, option in enumerate(options)}
        kwargs['step'] = 1
        super(OptionSlider, self).__init__(value=value, show_mark_label=show_mark_label, mark_label_format=wrapped_mark_label_format, on_change=on_change, on_change_committed=on_change_committed, **kwargs)

    @proper.alias
    def value(self):
        if isinstance(self.controller.value, numbers.Number):
            return self.options[int(self.controller.value)]
        else:
            return [ self.options[int(v)] for v in self.controller.value ]

    @value.setter
    def value(self, value):
        if isinstance(value, numbers.Number):
            self.controller.value = self.options.index(value)
        else:
            self.controller.value = [ self.options.index(v) for v in value ]


class Mark(Container):
    default_width = 2
    default_height = 2

    def __init__(self, slider_controller, value, label = None, **kwargs):
        self.value = value
        self._controller = slider_controller
        self._label = label
        super(Mark, self).__init__(**kwargs)
        self._layout()
        self._controller.bind(value=self.__on_value)

    def __on_value(self, controller, value):
        self._fill.opacity = self.__get_opacity()
        if self._label is not None:
            self._label_element.opacity = self.__get_label_opacity()

    def __get_opacity(self):
        if self._controller.is_value_selected(self.value):
            return 1.0
        return 0.2

    def __get_label_opacity(self):
        if self._controller.is_value_selected(self.value):
            return 1.0
        return 0.4

    def _layout(self):
        self._fill = Fill(bgParent=self, opacity=self.__get_opacity())
        if self._label is not None:
            self._label_element = EveLabelSmall(parent=self, align=Align.center_top, top=4, text=self._label, opacity=self.__get_label_opacity())


class Handle(FocusBehavior, CarbonEventHandler, Container):
    default_state = State.normal
    default_height = 8
    default_width = 8

    def __init__(self, value_index, on_step = None, **kwargs):
        self.value_index = value_index
        self._on_step = on_step
        super(Handle, self).__init__(**kwargs)
        self._layout()

    @lazy
    def _focus(self):
        return Fill(parent=self, align=Align.center, width=0, height=0, opacity=0.2)

    def _show_focus(self):
        animate(self._focus, 'width', end_value=16, duration=0.1)
        animate(self._focus, 'height', end_value=16, duration=0.1)

    def _hide_focus(self):
        animate(self._focus, 'width', end_value=0, duration=0.1)
        animate(self._focus, 'height', end_value=0, duration=0.1)

    def on_focused(self, focused):
        if self.focused:
            self._show_focus()
        else:
            self._hide_focus()

    def on_key_down(self, key):
        if key == Key.right and self._on_step is not None:
            self._on_step(self.value_index, 1)
        elif key == Key.left and self._on_step is not None:
            self._on_step(self.value_index, -1)
        else:
            return False
        return True

    def on_mouse_down(self, button):
        return False

    def _layout(self):
        Fill(parent=self, align=Align.to_all, color=(0.75, 0.75, 0.75, 1.0))


def find_closest_in_range(low, high, step, value):
    return round((clamp(low, value, high) - low) / step) * step + low


def take_closest(sequence, value):
    pos = bisect_left(sequence, value)
    if pos == 0:
        return sequence[0]
    elif pos == len(sequence):
        return sequence[-1]
    before = sequence[pos - 1]
    after = sequence[pos]
    if after - value < value - before:
        return after
    else:
        return before


def frange(start, stop, step = 1.0):
    i = 0
    value = start
    if start < stop:
        predicate = lambda a, b: a < b
    else:
        predicate = lambda a, b: a > b
    while predicate(value, stop):
        yield value
        i += 1
        value = start + i * step
