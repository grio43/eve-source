#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\skillTree\skillGroupSelectionCont.py
import evetypes
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.window.underlay import WindowUnderlay
from eve.client.script.ui.control.tabGroupVertical import TabGroupVertical
from eve.client.script.ui.skillTree.skillTreeDataProvider import GetSkillTreeDataProvider
from signals import Signal

class SkillGroupSelectionCont(Container):

    def ApplyAttributes(self, attributes):
        super(SkillGroupSelectionCont, self).ApplyAttributes(attributes)
        self.skillTreeDataProvider = GetSkillTreeDataProvider()
        self.onSkillGroupSelected = Signal()
        self.ConstructTabs()
        WindowUnderlay(bgParent=self)

    def ConstructTabs(self):
        self.groupTabs = TabGroupVertical(name='groupTabs', parent=self, align=uiconst.TOALL, width=0, height=0, callback=self.OnGroupTab)
        self.PopulateGroupTabs()

    def OnGroupTab(self, *args):
        groupID = self.groupTabs.GetSelectedID()
        self.onSkillGroupSelected(groupID)

    def PopulateGroupTabs(self, *args):
        self.groupTabs.AddTab(label='All', tabID=-1)
        groupIDs = self.skillTreeDataProvider.GetSkillGroups()
        for groupID in groupIDs:
            self.groupTabs.AddTab(label=evetypes.GetGroupNameByGroup(groupID), tabID=groupID)

        self.groupTabs.height = 0
