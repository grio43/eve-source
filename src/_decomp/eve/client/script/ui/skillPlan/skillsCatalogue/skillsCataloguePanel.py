#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\skillPlan\skillsCatalogue\skillsCataloguePanel.py
import blue
import uthread
from carbonui import uiconst
from carbonui.primitives.container import Container
from eve.client.script.ui.control.eveLabel import EveCaptionLarge, EveLabelLarge
from eve.client.script.ui.quickFilter import QuickFilterEdit
from eve.client.script.ui.skillPlan.browser.skillFilterCombo import SkillFilterCombo
from eve.client.script.ui.skillPlan.controls.skillPlanLine import SkillPlanLine
from eve.client.script.ui.skillPlan.skillsCatalogue.skillGroupBrowser import SkillGroupBrowser
from eve.client.script.ui.skillPlan.skillsCatalogue.skillGroupSkillsBrowser import SkillGroupSkillsBrowser
from localization import GetByLabel
from skills.skillConst import FILTER_SHOWALL, FILTER_HAVEPREREQUISITS

class SkillsCataloguePanel(Container):
    __notifyevents__ = ['OnSkillQueueChanged',
     'OnFreeSkillPointsChanged_Local',
     'OnSkillsChanged',
     'OnSkillQueueRefreshed']
    default_show_primary_buttons = True

    def ApplyAttributes(self, attributes):
        super(SkillsCataloguePanel, self).ApplyAttributes(attributes)
        self.updateSkillPointsThread = None
        self.isConstructed = False
        self.skillGroupSkillsBrowser = None
        self.skillPointsLabel = None
        sm.RegisterNotify(self)

    def ConstructLayout(self):
        self.topCont = Container(parent=self, name='topCont', height=32, align=uiconst.TOTOP)
        self.ConstructTopCont()
        self.skillPointsLabel = EveLabelLarge(parent=self, name='skillPointsLabel', align=uiconst.TOTOP)
        self.UpdateNumberOfSkillPoints()
        self.skillGroupBrowser = SkillGroupBrowser(parent=self, align=uiconst.TOTOP, height=0, padTop=16)
        self.skillGroupBrowser.onSkillSelected.connect(self.OnSkillGroupSelected)
        SkillPlanLine(parent=self, align=uiconst.TOTOP, state=uiconst.UI_DISABLED, padTop=16)
        self.ConstructSkillGroupSkillsBrowser()
        SkillPlanLine(parent=self, align=uiconst.TOBOTTOM, state=uiconst.UI_DISABLED)
        self.isConstructed = True

    def Show(self, *args):
        super(SkillsCataloguePanel, self).Show(*args)
        if not self.isConstructed:
            self.ConstructLayout()

    def ConstructSkillGroupSkillsBrowser(self):
        self.skillGroupSkillsBrowser = SkillGroupSkillsBrowser(parent=self, align=uiconst.TOALL, padding=(0, 16, 0, 16), showPrimaryButton=self.default_show_primary_buttons)

    def ConstructTopCont(self):
        self.skillsCaption = EveCaptionLarge(parent=self.topCont, align=uiconst.TOPLEFT, text=GetByLabel('UI/SkillPlan/Skills'))
        self.textFilterEdit = QuickFilterEdit(parent=self.topCont, align=uiconst.TORIGHT, width=140)
        self.textFilterEdit.ReloadFunction = self.OnQuickFilter
        prefskey, select = self.GetPrefsKeyAndSelect()
        self.skillFilterCombo = SkillFilterCombo(name='skillFilterCombo', parent=self.topCont, align=uiconst.TORIGHT, padRight=8, width=140, callback=self.OnSkillFilterCombo, prefskey=prefskey, select=select)

    def GetPrefsKeyAndSelect(self):
        configName = 'skillCatalogueCombo'
        prefskey = ('char', 'ui', configName)
        selectValue = settings.char.ui.Get(configName, FILTER_SHOWALL)
        return (prefskey, selectValue)

    def ReconstructSkillEntries(self):
        skills = self.GetSkillsFilteredAndSorted()
        self.skillGroupSkillsBrowser.ReconstructSkillEntries(skills)
        self.UpdateSkillGroupNumFilteredLabels()

    def UpdateSkillGroupNumFilteredLabels(self):
        for i, groupEntry in enumerate(self.skillGroupBrowser.GetAllSkillGroups()):
            skills = groupEntry.controller.GetSkillsFiltered(self.skillFilterCombo.GetValue(), self.textFilterEdit.GetValue())
            numSkills = len(skills)
            groupEntry.SetNumSkills(numSkills, i)

    def GetSkillsFilteredAndSorted(self):
        filterID = self.skillFilterCombo.GetValue()
        txtFilter = self.textFilterEdit.GetValue()
        if txtFilter:
            controllers = self.skillGroupBrowser.GetAllSkillGroupControllers()
        else:
            controllers = [self.skillGroupSkillsBrowser.controller]
        ret = []
        for controller in controllers:
            ret.extend(controller.GetSkillsFiltered(filterID, txtFilter))

        return sorted(ret, key=lambda x: x.GetName())

    def OnSkillGroupSelected(self, groupID):
        self.ResetQuickFilter()
        self.skillGroupSkillsBrowser.SetGroupID(groupID)
        self.ReconstructSkillEntries()

    def OnSkillFilterCombo(self, *args):
        self.skillFilterCombo.UpdateSettings()
        self.ReconstructSkillEntries()

    def OnQuickFilter(self, *args):
        self.ReconstructSkillEntries()

    def ResetQuickFilter(self):
        self.textFilterEdit.SetValue('', docallback=False)

    def _StartUpdateSkillPointsThread(self):
        if not self.updateSkillPointsThread:
            self.updateSkillPointsThread = uthread.new(self._UpdateNumberOfSkillPointsThread)

    def _UpdateNumberOfSkillPointsThread(self):
        while not self.destroyed:
            activeSkill = sm.GetService('skillqueue').SkillInTraining()
            if not activeSkill:
                break
            totalSkillPoints = sm.GetService('skillqueue').GetEstimatedTotalSkillPoints()
            self.skillPointsLabel.text = GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/SkillPoints', skillPoints=totalSkillPoints)
            blue.pyos.synchro.Sleep(2000)

        self.updateSkillPointsThread = None

    def UpdateNumberOfSkillPoints(self):
        if self.skillPointsLabel:
            skillPoints = sm.GetService('skills').GetTotalSkillPointsForCharacter()
            self.skillPointsLabel.text = GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/SkillPoints', skillPoints=skillPoints)
            self._StartUpdateSkillPointsThread()

    def OnSkillQueueChanged(self):
        self._OnSkillsStateChanged()

    def OnSkillsChanged(self, *args):
        self._OnSkillsStateChanged()

    def OnSkillQueueRefreshed(self):
        self._OnSkillsStateChanged()

    def OnFreeSkillPointsChanged_Local(self):
        self._OnSkillsStateChanged()

    def _OnSkillsStateChanged(self):
        if not self.isConstructed:
            return
        self.skillGroupSkillsBrowser.UpdateEntries()
        self.UpdateNumberOfSkillPoints()
        if self.skillFilterCombo.GetValue() == FILTER_HAVEPREREQUISITS:
            self.ReconstructSkillEntries()
