#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\expertSystems\client\ui\character_sheet\home\skills_section.py
import localization
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from eve.client.script.ui.control import eveLabel
from eve.client.script.ui.control.themeColored import FillThemeColored
from expertSystems.client.ui.skill_list import SkillList
from expertSystems.client.ui.skill_scroll_cont import SkillScrollCont

class SkillsSection(Container):

    def __init__(self, controller, **kwargs):
        self.controller = controller
        self.header = None
        self.header_label = None
        self.skill_list = None
        super(SkillsSection, self).__init__(**kwargs)
        self.layout()
        self.update()
        self.controller.on_selected_expert_system_changed.connect(self._handle_selected_expert_system_changed)

    def layout(self):
        self.header = ContainerAutoSize(parent=self, align=uiconst.TOTOP, alignMode=uiconst.CENTERLEFT)
        FillThemeColored(parent=self.header, align=uiconst.TOLEFT, width=2, colorType=uiconst.COLORTYPE_FLASH)
        FillThemeColored(parent=self.header, align=uiconst.TOALL, colorType=uiconst.COLORTYPE_UIBASECONTRAST)
        label_container = ContainerAutoSize(parent=self.header, align=uiconst.CENTERLEFT)
        self.header_label = eveLabel.EveLabelLarge(parent=label_container, align=uiconst.TOPLEFT, padding=(16, 4, 16, 4))
        scroll = SkillScrollCont(parent=self, align=uiconst.TOALL, copyCallback=self.Copy, selectAllCallback=self.SelectAll)
        self.skill_list = SkillList(parent=scroll, align=uiconst.TOTOP)

    def SelectAll(self):
        self.skill_list.SelectAll()

    def Copy(self):
        self.skill_list.Copy()

    def update(self):
        if self.controller.selected_expert_system:
            self.skill_list.skills = self.controller.selected_expert_system.skills
        else:
            self.skill_list.skills = {}
        selected_expert_system = self.controller.selected_expert_system
        if selected_expert_system is None:
            self.display = False
            return
        self.display = True
        self.header_label.SetText(localization.GetByLabel('UI/ExpertSystem/SkillCountHint', skill_count=len(selected_expert_system.skills)))

    def _handle_selected_expert_system_changed(self):
        self.update()
