#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\ui\simplebuttonwindow.py
from carbonui import uiconst
from carbonui.control.button import Button
from carbonui.control.window import Window
from carbonui.uicore import uicore

def get_simple_button_window_name(button_text):
    return 'SimpleButtonWindow_{}'.format(button_text)


def get_simple_button_window_by_button_text(button_text):
    window_name = get_simple_button_window_name(button_text)
    return uicore.registry.GetWindowByClassAndName(SimpleButtonWindow, window_name)


class SimpleButtonWindow(Window):
    __guid__ = 'SimpleButtonWindow'
    default_fixedHeight = 100
    default_isCollapseable = False
    default_isCompactable = False
    default_isLockable = False
    default_isMinimizable = False
    default_isStackable = False
    default_isKillable = False
    default_isOverlayable = False
    BUTTON_PADDING = 20

    def ApplyAttributes(self, attributes):
        super(SimpleButtonWindow, self).ApplyAttributes(attributes)
        self.button_text = attributes.get('button_text')
        self.on_click_function = attributes.get('on_click_function')
        self.update_name()
        self.construct_button()
        self.update_width()

    def update_name(self):
        self.name = get_simple_button_window_name(self.button_text)

    def construct_button(self):
        self.button = Button(name='SimpleButton', label=self.button_text, func=lambda *args: self.on_click_function(), parent=self.sr.main, align=uiconst.CENTER)

    def update_width(self):
        self.width = max(self.width, self.button.width + 2 * self.BUTTON_PADDING)
