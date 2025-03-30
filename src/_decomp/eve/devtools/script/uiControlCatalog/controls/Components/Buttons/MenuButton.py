#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\uiControlCatalog\controls\Components\Buttons\MenuButton.py
import eveicon
from eve.client.script.ui.control.message import ShowQuickMessage
from eve.devtools.script.uiControlCatalog.sample import Sample

class Sample1(Sample):

    def sample_code(self, parent):
        from carbonui.button.menu import MenuButton
        from carbonui.control.contextMenu.menuData import MenuData

        def get_menu_data():
            menu = MenuData()
            menu.AddEntry(text='Coke', func=lambda : ShowQuickMessage('You chose Coke'))
            menu.AddEntry(text='Pepsi', func=lambda : ShowQuickMessage('You chose Pepsi'))
            return menu

        MenuButton(parent=parent, label='Choose a drink ...', texturePath=eveicon.load, get_menu_func=get_menu_data)
