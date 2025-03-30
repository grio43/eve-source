#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\skillPlan\skillsCatalogue\skillGroupSkillsBrowser.py
from carbonui import uiconst
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.primitives.container import Container
from eve.client.script.ui.skillPlan.skillsCatalogue.skillCatalogueUtil import GetOrderedByColumn
from eve.client.script.ui.skillPlan.skillsCatalogue.skillGroupSkillEntry import SkillGroupSkillEntry
from localization import GetByLabel
from skills.client.skillGroupController import SkillGroupController

class SkillGroupSkillsBrowser(Container):
    __notifyevents__ = ['OnSkillsChanged', 'OnSkillQueueChanged', 'OnSubscriptionChanged']
    numColumns = 2

    def ApplyAttributes(self, attributes):
        super(SkillGroupSkillsBrowser, self).ApplyAttributes(attributes)
        sm.RegisterNotify(self)
        self.groupID = None
        self.controller = None
        self.showPrimaryButton = attributes.get('showPrimaryButton', False)
        self.entries = []
        self.scrollCont = ScrollContainer(parent=self)
        self.scrollCont.ShowNoContentHint(GetByLabel('UI/SkillPlan/NoSkillGroupSelected'))

    def SetGroupID(self, groupID):
        self.groupID = groupID
        self.controller = SkillGroupController(groupID)

    def ReconstructSkillEntries(self, skills):
        self.scrollCont.Flush()
        self.entries = []
        if len(skills) == 0:
            self.scrollCont.ShowNoContentHint(GetByLabel('UI/SkillPlan/NoSkillGroupSelected'))
        else:
            self.scrollCont.HideNoContentHint()
        skills = GetOrderedByColumn(skills, self.numColumns)
        for i, controller in enumerate(skills):
            if not i % self.numColumns:
                row = Container(name='row_%s' % i, parent=self.scrollCont, align=uiconst.TOTOP, height=SkillGroupSkillEntry.default_height, padBottom=8)
            entry = self._ConstructEntry(controller, row, i)
            self.entries.append(entry)

    def _ConstructEntry(self, controller, parent, i):
        return SkillGroupSkillEntry(parent=parent, align=uiconst.TOLEFT_PROP, width=0.5, controller=controller, showPrimaryButton=self.showPrimaryButton, padRight=0 if i % self.numColumns else 16)

    def OnSkillsChanged(self, skills):
        self._RefreshEntries()

    def OnSkillQueueChanged(self):
        self._RefreshEntries()

    def OnSubscriptionChanged(self):
        self._RefreshEntries()

    def UpdateEntries(self):
        self._RefreshEntries()

    def UpdateEntryButtons(self):
        for entry in self.entries:
            entry.UpdatePrimaryButton()

    def _RefreshEntries(self):
        for entry in self.entries:
            entry.Refresh()
