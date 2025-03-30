#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\homestation\client\ui\panel.py
from carbonui import uiconst
from carbonui.primitives.container import Container
from homestation.client.service import Service
from homestation.client.ui.page.home import HomePage
from homestation.client.ui.page.select import SelectHomeStationPage
from homestation.client.ui.page.stack import PageStack

class HomeStationPanel(Container):
    default_name = 'HomeStationPanel'

    def __init__(self, **kwargs):
        self.is_loaded = False
        self.page_stack = None
        super(HomeStationPanel, self).__init__(**kwargs)

    def LoadPanel(self):
        if not self.is_loaded:
            try:
                self.layout()
            finally:
                self.is_loaded = True

    def UnloadPanel(self):
        pass

    def layout(self):
        home_page = HomePage()
        home_page.on_select_home_station.connect(self.show_select_home_station)
        self.page_stack = PageStack(parent=self, align=uiconst.TOALL, start_page=home_page)

    def show_select_home_station(self):
        self.page_stack.push_page(SelectHomeStationPage(Service.instance()))
