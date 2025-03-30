#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\expertSystems\client\ui\character_sheet\browse\page.py
import eveicon
import localization
from carbonui import uiconst
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from eve.client.script.ui.control import eveLabel
from carbonui.control.buttonIcon import ButtonIcon
from eve.client.script.ui.control.themeColored import FillThemeColored
from expertSystems.client.ui.character_sheet.browse.controller import PageController
from expertSystems.client.ui.character_sheet.browse.details import ExpertSystemDetails
from expertSystems.client.ui.character_sheet.browse.entry import ExpertSystemEntry
from expertSystems.client.util import sorted_by_name

class BrowsePage(Container):
    back_button_size = 16

    def __init__(self, controller = None, **kwargs):
        if controller is None:
            controller = PageController()
        self.controller = controller
        self.expert_system_list = None
        super(BrowsePage, self).__init__(**kwargs)
        self.layout()

    def layout(self):
        main_container = Container(parent=self, align=uiconst.TOALL)
        header_container = ContainerAutoSize(parent=main_container, align=uiconst.TOTOP, top=8, padBottom=16)
        ButtonIcon(parent=header_container, align=uiconst.CENTERLEFT, width=self.back_button_size, height=self.back_button_size, texturePath=eveicon.navigate_back, iconEnabledOpacity=0.5, hint=localization.GetByLabel('UI/ExpertSystem/BackToHome'), func=self.controller.go_back, args=())
        eveLabel.EveCaptionMedium(parent=header_container, align=uiconst.CENTERLEFT, left=self.back_button_size + 8, text=localization.GetByLabel('UI/ExpertSystem/BrowseHeader'))
        left_container = Container(parent=main_container, align=uiconst.TOLEFT_PROP, width=0.5, padRight=4)
        FillThemeColored(bgParent=left_container, colorType=uiconst.COLORTYPE_UIBASECONTRAST)
        self.expert_system_list = ScrollContainer(parent=left_container, align=uiconst.TOALL)
        right_container = Container(parent=main_container, align=uiconst.TOALL, padLeft=4)
        FillThemeColored(bgParent=right_container, colorType=uiconst.COLORTYPE_UIBASECONTRAST)
        ExpertSystemDetails(parent=right_container, align=uiconst.TOALL, padding=8, page_controller=self.controller)

    def load(self):
        expert_systems = sorted_by_name(self.controller.expert_systems)
        if expert_systems:
            self.controller.selected_expert_system = expert_systems[0]
        for expert_system in expert_systems:
            ExpertSystemEntry(parent=self.expert_system_list, align=uiconst.TOTOP, expert_system=expert_system, page_controller=self.controller)
