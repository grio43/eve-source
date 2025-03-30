#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveui\behavior\ime.py
import itertools
from carbonui.uicore import uicore
from .focus import FocusBehavior

class ImeBehavior(FocusBehavior):

    def __init__(self, **kwargs):
        super(ImeBehavior, self).__init__(**kwargs)
        self.bind(focused=self.__on_focused)

    def get_ime_position(self, width, height):
        my_left, my_top, my_width, my_height = self.GetAbsolute()
        return (my_left, my_top + my_height)

    def __on_focused(self, *args):
        self.__update_ime_handler()

    def __update_ime_handler(self):
        if not uicore.imeHandler:
            return
        if self.__class__ not in uicore.imeHandler.allowedWidgetTypes:
            previous_allowed = uicore.imeHandler.allowedWidgetTypes
            uicore.imeHandler.allowedWidgetTypes = tuple(itertools.chain(previous_allowed, (self.__class__,)))
        if self.focused:
            uicore.imeHandler.SetFocus(self)
        else:
            uicore.imeHandler.KillFocus(self)

    def GetMenu(self):
        try:
            menu_entries = super(ImeBehavior, self).GetMenu()
        except AttributeError:
            menu_entries = []

        return menu_entries
