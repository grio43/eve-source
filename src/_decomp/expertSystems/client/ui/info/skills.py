#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\expertSystems\client\ui\info\skills.py
import blue
import localization
from carbonui import uiconst
from carbonui.decorative.panelUnderlay import PanelUnderlay
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.util.color import Color
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.shared.neocom.skillConst import COLOR_SKILL_1
from expertSystems import get_expert_system
from expertSystems.client.ui.skill_row import SkillRow
from expertSystems.client.ui.skill_scroll_cont import SkillScrollCont
from expertSystems.client.util import get_sorted_expert_system_provided_skills

class SkillsPanel(Container):

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.expertSystemTypeID = attributes.get('expertSystemTypeID', None)
        self.expertSystemsPanel = None
        self.Load()

    def Load(self):
        if self.expertSystemsPanel:
            self.expertSystemsPanel.Load()
        else:
            timeRemainingLabelCont = ContainerAutoSize(align=uiconst.TOTOP, alignMode=uiconst.TOPLEFT, parent=self)
            expertSystem = get_expert_system(self.expertSystemTypeID)
            totalTime = sm.GetService('skills').GetTrainingTimeLeftForSkillLevels(expertSystem.skills)
            totalTimeText = localization.GetByLabel('UI/SkillQueue/Skills/TotalTrainingTime', timeLeft=long(totalTime), color=Color(*COLOR_SKILL_1).GetHex())
            EveLabelMedium(parent=timeRemainingLabelCont, align=uiconst.TOPLEFT, text=totalTimeText, padding=(8, 4, 0, 0))
            self.expertSystemsPanel = ExpertSystemsSkillsContainer(parent=self, expertSystemTypeID=self.expertSystemTypeID)


class ExpertSystemsSkillsContainer(Container):
    default_padding = 4
    __notifyevents__ = ['OnSkillsChanged']

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.expertSystemTypeID = attributes.get('expertSystemTypeID', None)
        sm.RegisterNotify(self)
        self.skillRows = []
        self.ConstructLayout()

    def ConstructLayout(self):
        self.scroll = SkillScrollCont(copyCallback=self.CopySelectedRows, selectAllCallback=self.SelectAllRows, name='scroll', parent=self, rowPadding=2, padTop=6)
        PanelUnderlay(parent=self, name='background')

    def CopySelectedRows(self):
        copyStrings = []
        for row in self.skillRows:
            if row.selected:
                copyStrings.append(row.get_copy_data())

        blue.pyos.SetClipboardData('\n'.join(copyStrings))

    def SelectAllRows(self):
        for row in self.skillRows:
            row.select()

    def GetTooltipPointer(self):
        return uiconst.POINT_LEFT_2

    def Load(self):
        self.scroll.Flush()
        self.skillRows = []
        skills = get_expert_system(self.expertSystemTypeID).skills
        sortedSkills = get_sorted_expert_system_provided_skills(self.expertSystemTypeID)
        for skillTypeID in sortedSkills:
            skillRow = SkillRow(parent=self.scroll, align=uiconst.TOTOP, height=32, padTop=2, skill_type_id=skillTypeID, rowSelectFunc=self.OnRowSelect, required_level=skills[skillTypeID])
            self.skillRows.append(skillRow)

    def OnRowSelect(self, skillRow, deselect_others = True):
        if deselect_others:
            for row in self.skillRows:
                if row == skillRow:
                    continue
                row.deselect()

        skillRow.select()

    def OnSkillsChanged(self, *args):
        self.Load()
