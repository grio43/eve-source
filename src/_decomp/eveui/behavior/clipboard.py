#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveui\behavior\clipboard.py
import abc
import platform
from menu import MenuLabel
from eveui import clipboard
from eveui.keyboard import Key

class ClipboardBehavior(object):

    def copy(self):
        content = self.on_copy()
        if content:
            clipboard.set(content)

    def cut(self):
        content = self.on_cut()
        if content:
            clipboard.set(content)

    def paste(self):
        content = clipboard.get()
        if content:
            self.on_paste(content)

    def on_key_down(self, key):
        ctrl = Key.ctrl_or_cmd()
        if key == Key.c and ctrl.is_down:
            self.copy()
        elif key == Key.x and ctrl.is_down:
            self.cut()
        elif key == Key.v and ctrl.is_down:
            self.paste()
        else:
            try:
                return super(ClipboardBehavior, self).on_key_down(key)
            except AttributeError:
                return False

        return True

    def GetMenu(self):
        try:
            menu_entries = super(ClipboardBehavior, self).GetMenu()
        except AttributeError:
            menu_entries = []

        menu_entries.extend([(MenuLabel('/Carbon/UI/Controls/Common/Copy'), self.copy), (MenuLabel('/Carbon/UI/Controls/Common/Cut'), self.cut), (MenuLabel('/Carbon/UI/Controls/Common/Paste'), self.paste)])
        return menu_entries

    @abc.abstractmethod
    def on_copy(self):
        pass

    @abc.abstractmethod
    def on_cut(self):
        pass

    @abc.abstractmethod
    def on_paste(self, content):
        pass
