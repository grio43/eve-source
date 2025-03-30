#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\expertSystems\client\ui\character_sheet\home\page.py
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.uianimations import animations
from eve.client.script.ui.control.eveLoadingWheel import LoadingWheel
from expertSystems.client.ui.character_sheet.home.controller import PageController, State
from expertSystems.client.ui.character_sheet.home.details import DetailsSection
from expertSystems.client.ui.character_sheet.home.intro import IntroSection
from expertSystems.client.ui.character_sheet.home.skills_section import SkillsSection
from expertSystems.client.ui.character_sheet.home.slot import ExpertSystemSlot

class HomePage(Container):

    def __init__(self, on_browse, controller = None, **kwargs):
        if controller is None:
            controller = PageController()
        self.controller = controller
        self.slots = []
        self.loading_indicator = None
        self.main_container = None
        self.top_container = None
        self.intro_section = None
        self.skills_section = None
        super(HomePage, self).__init__(**kwargs)
        self.layout()
        self.controller.on_browse.connect(on_browse)
        self.controller.on_state_changed.connect(self.handle_on_state_changed)
        self.controller.on_selected_expert_system_changed.connect(self.handle_on_selection_changed)

    def load(self):
        if self.controller.state == State.initial:
            self.controller.load()
        else:
            self._enter_state(self.controller.state)

    def layout(self):
        self.loading_indicator = LoadingWheel(parent=self, align=uiconst.CENTER, state=uiconst.UI_DISABLED, opacity=0.0)
        self.main_container = Container(parent=self, align=uiconst.TOALL, padding=8, opacity=0.0 if self.controller.state == State.initial else 1.0)
        self.top_container = ContainerAutoSize(parent=self.main_container, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, top=16, minHeight=70)
        systems_container = SpreadContainer(parent=self.top_container, align=uiconst.TOLEFT_PROP, width=0.5)
        DetailsSection(parent=self.top_container, align=uiconst.TOTOP, minHeight=70, page_controller=self.controller)
        for slot in self.controller.slots:
            ExpertSystemSlot(parent=systems_container, align=uiconst.TOPLEFT, controller=slot)

        self.intro_section = IntroSection(parent=ContainerAutoSize(parent=self.main_container, align=uiconst.TOTOP), align=uiconst.CENTERTOP, top=32, width=460, on_browse=self.controller.browse)
        self.intro_section.display = False
        self.skills_section = SkillsSection(parent=self.main_container, align=uiconst.TOALL, padTop=16, controller=self.controller)

    def handle_on_state_changed(self, state, old_state):
        if old_state == State.loading:
            self.hide_loading()
        elif old_state == State.error:
            self.hide_error()
        self._enter_state(state)

    def _enter_state(self, state):
        if state == State.loading:
            self.show_loading()
        elif state == State.ready:
            self.update_content()
        elif state == State.error:
            self.show_error()

    def handle_on_selection_changed(self):
        self.intro_section.display = self.controller.selected_expert_system is None

    def show_loading(self):
        animations.FadeOut(self.main_container, duration=0.3)
        animations.FadeIn(self.loading_indicator, duration=0.3)

    def hide_loading(self):
        animations.FadeIn(self.main_container, duration=0.3)
        animations.FadeOut(self.loading_indicator, duration=0.3)

    def update_content(self):
        self.top_container.display = self.controller.selected_expert_system is not None
        self.intro_section.display = self.controller.selected_expert_system is None

    def show_error(self):
        pass

    def hide_error(self):
        pass


class SpreadContainer(Container):

    def UpdateAlignment(self, *args, **kwargs):
        budget = super(SpreadContainer, self).UpdateAlignment(*args, **kwargs)
        width, _ = self.GetCurrentAbsoluteSize()
        content_width = sum((child.width for child in self.children))
        available_space = width - content_width
        gap = available_space / (len(self.children) + 1)
        accumulated_content_width = 0
        for i, child in enumerate(self.children):
            child.left = accumulated_content_width + (i + 1) * gap
            accumulated_content_width += child.width

        return budget
