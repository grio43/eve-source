#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\ship\pages\studio\studioPageContainer.py
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.uianimations import animations
from cosmetics.client.ships.skins.live_data import current_skin_design
from eve.client.script.ui.cosmetics.ship.const import SkinrPage
from eve.client.script.ui.cosmetics.ship.pages.studio import studioSignals
from eve.client.script.ui.cosmetics.ship.pages import current_page
from eve.client.script.ui.cosmetics.ship.pages.studio.nameAndTierContainer import NameAndTierContainer
from eve.client.script.ui.cosmetics.ship.pages.studio.studioDesignerPage import StudioDesignerPage
from eve.client.script.ui.cosmetics.ship.pages.homepage.studioHomePage import StudioHomePage
from eve.client.script.ui.cosmetics.ship.pages.sequence.studioSequencePage import StudioSequencePage

class StudioPageContainer(Container):
    is_loaded = False
    page_id = None

    def construct_layout(self):
        self.content = Container(name='content', parent=self)
        self.home_page = StudioHomePage(parent=self.content, state=uiconst.UI_HIDDEN)
        self.designer_page = StudioDesignerPage(parent=self.content, state=uiconst.UI_HIDDEN)
        self.name_and_tier_cont = NameAndTierContainer(parent=self.content, state=uiconst.UI_HIDDEN)
        self.sequence_page = StudioSequencePage(parent=self, state=uiconst.UI_HIDDEN)

    def load_panel(self, page_id = None, page_args = None):
        if not self.is_loaded:
            self.is_loaded = True
            self.construct_layout()
            self.connect_signals()
            self.show_page(page_id, page_args, animate=False)

    def Close(self):
        try:
            if self.is_loaded:
                self.disconnect_signals()
        finally:
            super(StudioPageContainer, self).Close()

    def connect_signals(self):
        self.home_page.on_create_new_design_btn.connect(self.on_create_new_design_btn)
        self.designer_page.on_create_btn.connect(self.on_designer_create_btn)
        studioSignals.on_page_opened.connect(self.on_page_opened)

    def on_page_opened(self, page_id, page_args, last_page_id, animate = True):
        self.show_page(page_id, page_args, animate)

    def disconnect_signals(self):
        self.home_page.on_create_new_design_btn.disconnect(self.on_create_new_design_btn)
        self.designer_page.on_create_btn.disconnect(self.on_designer_create_btn)
        studioSignals.on_page_opened.disconnect(self.on_page_opened)

    def show_page(self, page_id, page_args = None, animate = True):
        if page_id == SkinrPage.STUDIO:
            self.show_home_page(page_args)
        elif page_id == SkinrPage.STUDIO_DESIGNER:
            self.show_designer_page()
        elif page_id == SkinrPage.STUDIO_SEQUENCING:
            self.show_sequence_page()
        self.update_content_right_padding(animate)

    def on_designer_create_btn(self):
        current_page.set_page_id(SkinrPage.STUDIO_SEQUENCING)

    def on_create_new_design_btn(self):
        current_page.set_page_id(SkinrPage.STUDIO_DESIGNER)

    def show_home_page(self, page_args = None, animate = True):
        self.home_page.LoadPanel(page_args)
        self.designer_page.UnloadPanel()
        self.sequence_page.UnloadPanel()
        self.name_and_tier_cont.UnloadPanel()

    def show_sequence_page(self, animate = True):
        self.sequence_page.LoadPanel()
        self.designer_page.UnloadPanel()
        self.home_page.UnloadPanel()
        self.name_and_tier_cont.LoadPanel()

    def update_content_right_padding(self, animate = True):
        width = current_page.get_content_right_padding()
        if animate:
            animations.MorphScalar(self.content, 'padRight', self.content.padRight, width, duration=0.6)
        else:
            self.content.padRight = width

    def show_designer_page(self, animate = True):
        self.designer_page.LoadPanel()
        self.home_page.UnloadPanel()
        self.sequence_page.UnloadPanel()
        self.name_and_tier_cont.LoadPanel()
