#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\expertSystems\client\ui\character_sheet\panel.py
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.uianimations import animations
from expertSystems.client.ui.character_sheet import browse, home

class ExpertSystemsPanel(Container):

    def __init__(self, **kwargs):
        self.is_loaded = False
        self.current_page = None
        self.home_page_controller = None
        super(ExpertSystemsPanel, self).__init__(**kwargs)

    def layout(self):
        pass

    def show_page(self, page):
        if self.current_page:
            animations.FadeOut(self.current_page, duration=0.3, callback=self.current_page.Close)
        self.current_page = page
        page.align = uiconst.TOALL
        page.SetParent(self)
        animations.FadeTo(page, startVal=0.0, endVal=1.0, duration=0.3)
        page.load()

    def show_home_page(self):
        if self.home_page_controller is None:
            self.home_page_controller = home.PageController()
        self.show_page(home.HomePage(on_browse=self.show_browse_page, controller=self.home_page_controller))

    def show_browse_page(self):
        controller = browse.PageController()
        controller.on_back.connect(self.show_home_page)
        self.show_page(browse.BrowsePage(controller=controller))

    def LoadPanel(self):
        if not self.is_loaded:
            self.layout()
            self.show_home_page()
            self.is_loaded = True
