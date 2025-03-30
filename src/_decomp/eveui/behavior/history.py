#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveui\behavior\history.py
import abc
import caching
from eveui.keyboard import Key

class HistoryBehavior(object):
    __metaclass__ = abc.ABCMeta

    @caching.lazy_property
    def history(self):
        return History()

    def undo(self):
        if not self.history.can_undo:
            return
        self.set_state_from_history(self.history.undo(self.get_state_for_history()))

    def redo(self):
        if not self.history.can_redo:
            return
        self.set_state_from_history(self.history.redo(self.get_state_for_history()))

    def save_state_to_history(self):
        self.history.push(self.get_state_for_history())

    def on_key_down(self, key):
        ctrl = Key.ctrl_or_cmd()
        if key == Key.z and ctrl.is_down:
            self.undo()
        elif key == Key.y and ctrl.is_down:
            self.redo()
        else:
            try:
                return super(HistoryBehavior, self).on_key_down(key)
            except AttributeError:
                return False

        return True

    @abc.abstractmethod
    def get_state_for_history(self):
        pass

    @abc.abstractmethod
    def set_state_from_history(self):
        pass


class History(object):

    def __init__(self):
        self._undo_stack = []
        self._redo_stack = []

    @property
    def can_undo(self):
        return bool(self._undo_stack)

    @property
    def can_redo(self):
        return bool(self._redo_stack)

    @property
    def next(self):
        if not self.can_redo:
            raise RuntimeError('no state on the redo stack')
        return self._redo_stack[-1]

    @property
    def previous(self):
        if not self.can_undo:
            raise RuntimeError('no state on the undo stack')
        return self._undo_stack[-1]

    def push(self, new_state):
        self._undo_stack.append(new_state)
        self._redo_stack = []

    def undo(self, current_state):
        self._redo_stack.append(current_state)
        return self._undo_stack.pop()

    def redo(self, current_state):
        self._undo_stack.append(current_state)
        return self._redo_stack.pop()

    def clear(self):
        self._undo_stack = []
        self._redo_stack = []
