#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\expertSystems\client\ui\skill_list.py
from __future__ import division
import math
import blue
import evetypes
import threadutils
from carbonui import uiconst
from carbonui.primitives.gridcontainer import GridContainer
from carbonui.uianimations import animations
from expertSystems.client.ui.skill_row import SkillRow
from expertSystems.client.util import get_localized_sort_key

class DynamicGridContainer(GridContainer):

    def __init__(self, cell_height, max_cell_width, **kwargs):
        self.cell_height = cell_height
        self.max_cell_width = max_cell_width
        super(DynamicGridContainer, self).__init__(**kwargs)

    def UpdateAlignment(self, budgetLeft = 0, budgetTop = 0, budgetWidth = 0, budgetHeight = 0, updateChildrenOnly = False):
        width, _ = self.GetCurrentAbsoluteSize()
        columns = max(1, int(math.ceil(width / self.max_cell_width)))
        if columns != self.columns:
            self.columns = columns
        lines = max(1, int(math.ceil(len(self.children) / columns)))
        if lines != self.lines:
            self.lines = lines
        height = self.lines * self.cell_height
        if height != self.height:
            self.height = height
        return super(DynamicGridContainer, self).UpdateAlignment(budgetLeft, budgetTop, budgetWidth, budgetHeight, updateChildrenOnly)


class SkillList(DynamicGridContainer):

    def __init__(self, skills = None, max_cell_width = 300, **kwargs):
        self._skills = skills
        super(SkillList, self).__init__(cell_height=SkillRow.default_height, max_cell_width=max_cell_width, **kwargs)
        self.update_skills()
        self.skill_rows = []

    @property
    def skills(self):
        return self._skills

    @skills.setter
    def skills(self, skills):
        self._skills = skills
        self.update_skills()

    def on_select_skill_row(self, skill_row, deselect_others = True):
        if deselect_others:
            for row in self.skill_rows:
                if row == skill_row:
                    continue
                row.deselect()

        skill_row.select()

    def SelectAll(self):
        for row in self.skill_rows:
            row.select()

    def Copy(self):
        copyStrings = []
        for row in self.skill_rows:
            if row.selected:
                copyStrings.append(row.get_copy_data())

        blue.pyos.SetClipboardData('\n'.join(copyStrings))

    @threadutils.highlander_threaded
    def update_skills(self):
        self.Flush()
        if not self._skills:
            return
        sorted_skills = sorted(self._skills.iteritems(), key=lambda (skill_id, _): get_localized_sort_key(evetypes.GetName(skill_id)))
        for i, (skill_id, level) in enumerate(sorted_skills):
            skill_row = SkillRow(parent=self, align=uiconst.TOTOP, skill_type_id=skill_id, required_level=level, rowSelectFunc=self.on_select_skill_row)
            self.skill_rows.append(skill_row)
            animations.FadeTo(skill_row, startVal=0.0, endVal=1.0, duration=0.3, timeOffset=i * 0.02)
