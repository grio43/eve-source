#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\skillPlan\skillsCatalogue\skillGroupBrowser.py
import evetypes
import inventorycommon.const as invConst
import uthread2
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from eve.client.script.ui.skillPlan.skillsCatalogue.skillCatalogueUtil import GetOrderedByColumn
from eve.client.script.ui.skillPlan.skillsCatalogue.skillGroupEntry import SkillGroupEntry
from signals import Signal
from skills import skillConst
NUM_COLUMNS = 3
SELECTED_SETTING = 'skillCatalogue_skillGroupSelected'

class SkillGroupBrowser(ContainerAutoSize):
    __notifyevents__ = ['OnSkillsChanged']

    def ApplyAttributes(self, attributes):
        super(SkillGroupBrowser, self).ApplyAttributes(attributes)
        self.onSkillSelected = Signal('SkillGroupBrowser_onSkillSelected')
        self.entries = []
        self.ConstructEntries()
        skillGroupSelected = settings.user.ui.Get('%s' % SELECTED_SETTING, invConst.groupSpaceshipCommand)
        if skillGroupSelected:
            uthread2.start_tasklet(self.SetGroupAsSelected, skillGroupSelected)

    def ConstructEntries(self):
        groupIDs = self.GetGroupIDs()
        for i, groupID in enumerate(groupIDs):
            if not i % NUM_COLUMNS:
                row = Container(name='row_%s' % i, parent=self, align=uiconst.TOTOP, height=32, padBottom=4)
            entry = SkillGroupEntry(parent=row, align=uiconst.TOLEFT_PROP, width=0.333, groupID=groupID, padRight=8 if (i + 1) % 3 else 0)
            entry.onClickSignal.connect(self.OnEntryClicked)
            self.entries.append(entry)

    def GetGroupIDs(self):
        groupIDs = sorted(skillConst.skill_group_ids, key=lambda x: evetypes.GetGroupNameByGroup(x))
        return GetOrderedByColumn(groupIDs, NUM_COLUMNS)

    def OnEntryClicked(self, clickedEntry):
        if clickedEntry.isSelected:
            return
        self.SetGroupAsSelected(clickedEntry.groupID)

    def SetGroupAsSelected(self, groupID):
        for entry in self.entries:
            if entry.groupID == groupID:
                entry.SetSelected()
            else:
                entry.SetDeselected()

        settings.user.ui.Set('%s' % SELECTED_SETTING, groupID)
        self.onSkillSelected(groupID)

    def GetAllSkillGroupControllers(self):
        return [ x.controller for x in self.entries ]

    def GetAllSkillGroups(self):
        return self.entries

    def OnSkillsChanged(self, skillInfos):
        for entry in self.entries:
            entry.UpdateProgress()
