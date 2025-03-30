#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\skillPlan\browser\skillPlanScroll.py
import localization
from carbonui import uiconst
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.primitives.container import Container
from eve.client.script.ui.skillPlan.browser.skillPlanEntry import SkillPlanEntry

class SkillPlanScroll(ScrollContainer):
    default_scrollBarPadding = 10
    ENTRY_HEIGHT = 134
    __notifyevents__ = ['OnSkillQueueChanged']

    def ApplyAttributes(self, attributes):
        super(SkillPlanScroll, self).ApplyAttributes(attributes)
        self.rows = []
        self.entries = []
        self.selectedID = None
        self.numPerRow = None
        self.skillPlans = None
        self.addUniqueName = False
        self.isConstructing = False

    def ConstructSkillPlanEntries(self, skillPlans):
        self.isConstructing = True
        self.skillPlans = skillPlans
        for row in self.rows:
            row.Close()

        self.rows = []
        self.entries = []
        self.numPerRow = self._GetNumPerRow()
        sortedSkillPlans = localization.util.Sort(skillPlans, key=lambda x: x.GetName())
        for i, skillPlan in enumerate(sortedSkillPlans):
            if not i % self.numPerRow:
                row = Container(name='row_%s' % (i / self.numPerRow), parent=self, align=uiconst.TOTOP, height=self.ENTRY_HEIGHT, padBottom=20)
                self.rows.append(row)
            entry = SkillPlanEntry(parent=row, align=uiconst.TOLEFT_PROP, width=1.0 / self.numPerRow, skillPlan=skillPlan, padRight=30 if (i + 1) % self.numPerRow else 0, addUniqueName=self.addUniqueName)
            self.entries.append(entry)

        self.isConstructing = False

    def _GetNumPerRow(self):
        w, _ = self.GetAbsoluteSize()
        numPerRow = w / 325
        return max(1, numPerRow)

    def IsNumPerRowCorrect(self):
        return self.numPerRow == self._GetNumPerRow()

    def _OnSizeChange_NoBlock(self, width, height):
        super(SkillPlanScroll, self)._OnSizeChange_NoBlock(width, height)
        if not self.isConstructing and self.skillPlans and not self.IsNumPerRowCorrect():
            self.ConstructSkillPlanEntries(self.skillPlans)

    def OnSkillQueueChanged(self):
        for entry in self.entries:
            entry.UpdateState()

    def GetNumEntries(self):
        return len(self.entries)
