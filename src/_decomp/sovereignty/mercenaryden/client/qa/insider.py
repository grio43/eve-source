#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sovereignty\mercenaryden\client\qa\insider.py
from carbonui.control.contextMenu.menuEntryData import MenuEntryDataCheckbox
from sovereignty.mercenaryden.client.qa.settings.should_mock_data import SETTING_SHOULD_MOCK

def get_insider_qa_menu():
    menu = ('Mercenary Dens', [MenuEntryDataCheckbox('Use Mock Data', setting=SETTING_SHOULD_MOCK, hint='When ON, we mock all the data for Mercenary Dens. When OFF, we fetch it from Quasar.')])
    return menu
