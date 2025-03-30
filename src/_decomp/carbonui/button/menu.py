#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\button\menu.py
import eveicon
import localization
from carbonui.control.button import Button
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.control.contextMenu.menuEntryData import MenuEntryData

class MenuButtonIcon(ButtonIcon):
    default_texturePath = eveicon.more_vertical
    default_width = 24
    default_height = 24
    default_iconSize = 16
    expandOnLeft = True
    default_hint = localization.GetByLabel('UI/Common/More')

    def ApplyAttributes(self, attributes):
        super(MenuButtonIcon, self).ApplyAttributes(attributes)
        if attributes.get_menu_func:
            self.get_menu_func = attributes.get_menu_func

    def GetMenu(self):
        return self.get_menu_func()

    def GetMenuPosition(self, element):
        return (self.absoluteLeft + 2, self.absoluteBottom)


class MenuButton(Button):
    expandOnLeft = True

    def __init__(self, get_menu_func, **kwargs):
        self.get_menu_func = get_menu_func
        super(MenuButton, self).__init__(**kwargs)

    def get_menu_entry_data(self):
        icon = self.texturePath if self.texturePath != eveicon.more_vertical else None
        return MenuEntryData(text=self.label or self.hint, texturePath=icon, subMenuData=self.get_menu_func)

    def GetMenu(self):
        return self.get_menu_func()

    def GetMenuPosition(self, element):
        return (self.absoluteLeft, self.absoluteBottom)
