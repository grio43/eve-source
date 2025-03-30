#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\skillPlan\contents\skillPlanContents.py
import blue
import evetypes
import itertoolsext
from carbonui import uiconst
from carbonui.control.button import Button
from carbonui.control.checkbox import Checkbox
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.uicore import uicore
from eve.client.script.ui.control.eveLabel import EveCaptionLarge
from eve.client.script.ui.control.utilMenu import UtilMenu
from eve.client.script.ui.quickFilter import QuickFilterEdit
from eve.client.script.ui.skillPlan.contents.SkillPlanContentsSkillEntry import SkillPlanContentsSkillEntry
from eve.client.script.ui.skillPlan.skillPlanConst import NO_REQ
from eve.client.script.ui.skillPlan.skillPlanUtil import GetPreReqsAndRequiredForSkillLevel, GetRequirementStateForEntry
from eve.client.script.ui.skillPlan.skillQueuePanel.skillQueueButtons import OmegaButton
from eveui import clipboard
from localization import GetByLabel
from skills.client.util import buy_missing_skills
from skills.skillplan.loggers.skillPlanLogger import log_certified_skill_plan_buy_missing_skillbooks_clicked, log_certified_skill_plan_omega_button_clicked
from skills.skillplan.skillPlanService import GetSkillPlanSvc
from carbon.common.script.sys.serviceConst import ROLE_GML

def IsHideTrainedSkillsEnabled():
    return settings.char.ui.Get('SkillPlanContentsHideTrained', True)


def SetHideTrainedSkillsEnabled(isEnabled):
    settings.char.ui.Set('SkillPlanContentsHideTrained', isEnabled)


class SkillPlanOmegaButton(OmegaButton):

    def ApplyAttributes(self, attributes):
        super(SkillPlanOmegaButton, self).ApplyAttributes(attributes)
        self.skillPlan = attributes.skillPlan

    def OnClick(self, *args):
        super(SkillPlanOmegaButton, self).OnClick(*args)
        if self.skillPlan.IsCertified():
            log_certified_skill_plan_omega_button_clicked(self.skillPlan.GetID())

    def SetSkillPlan(self, skillPlan):
        self.skillPlan = skillPlan


class SkillPlanContents(Container):
    __notifyevents__ = ['OnSkillsChanged',
     'OnSkillQueueChanged',
     'OnSubscriptionChanged',
     'OnSkillsAvailable']

    def ApplyAttributes(self, attributes):
        super(SkillPlanContents, self).ApplyAttributes(attributes)
        sm.RegisterNotify(self)
        self.skillPlan = None
        self.entries = []
        self.askedAboutTracking = False
        self.topCont = ContainerAutoSize(name='topCont', parent=self, align=uiconst.TOTOP, alignMode=uiconst.TOPLEFT, padBottom=10)
        self.ConstructTopCont()
        self.filtersCont = Container(name='filtersCont', parent=self, align=uiconst.TOTOP, height=26, padBottom=20)
        self.ConstructFiltersCont()
        self.skillbooksMissingBtn = Button(parent=self, align=uiconst.TOBOTTOM, state=uiconst.UI_HIDDEN, func=self.OnMissingSkillbooksButton, padTop=5, analyticID='BuyAllMissingSkillbooks')
        self.omegaButton = SkillPlanOmegaButton(name='omegaButton', parent=self, align=uiconst.TOBOTTOM, iconSize=32, fixedheight=36, padTop=10, label=GetByLabel('UI/CloneState/UpgradeCloneState'), skillPlan=self.skillPlan)
        self.scroll = ScrollContainer(parent=self, align=uiconst.TOALL)

    def ConstructTopCont(self):
        EveCaptionLarge(parent=self.topCont, name='skillPlanOverviewLabel', align=uiconst.TOPLEFT, text=GetByLabel('UI/SkillPlan/SkillPlanOverview'))
        UtilMenu(parent=self.topCont, align=uiconst.CENTERRIGHT, texturePath='res:/UI/Texture/Icons/77_32_49.png', pos=(-5, 0, 24, 24), GetUtilMenu=self.GetUtilMenu, iconSize=24)

    def ConstructFiltersCont(self):
        self.quickFilterEdit = QuickFilterEdit(parent=self.filtersCont, align=uiconst.TORIGHT, width=140, callback=self.OnQuickFilterEdit)
        checkboxCont = Container(name='checkboxCont', parent=self.filtersCont, clipChildren=True)
        Checkbox(parent=checkboxCont, align=uiconst.CENTERLEFT, text=GetByLabel('UI/SkillPlan/HideTrainedSkills'), callback=self.OnHideTrainedCheckbox, checked=IsHideTrainedSkillsEnabled())

    def GetUtilMenu(self, menuParent):
        menuParent.AddIconEntry(icon='res:/UI/Texture/classes/UtilMenu/BulletIcon.png', text=GetByLabel('UI/SkillPlan/CopySkillsToClipboard'), callback=self.CopySkillsToClipboard)
        if session.role & ROLE_GML:
            menuParent.AddIconEntry(icon='res:/UI/Texture/classes/UtilMenu/BulletIcon.png', text='Train all skills', callback=self._TrainAllSkillsInPlan)

    def _TrainAllSkillsInPlan(self):
        if session.role & ROLE_GML:
            skillsAndLevels = {t:l for t, l in self.skillPlan.GetSkillRequirements()}
            sm.GetService('info').DoGiveSkills(skillsAndLevels, None)

    def CopySkillsToClipboard(self):
        clipboard.set(self.skillPlan.GetRequirementsClipboardText())

    def OnHideTrainedCheckbox(self, cb, *args):
        SetHideTrainedSkillsEnabled(cb.GetValue())
        self.PopulateScroll()

    def OnQuickFilterEdit(self):
        self.PopulateScroll()

    def OnMissingSkillbooksButton(self, *args):
        skillsBought = buy_missing_skills(self.skillPlan.GetMissingSkillbooks())
        if skillsBought and self.skillPlan.IsCertified():
            log_certified_skill_plan_buy_missing_skillbooks_clicked(self.skillPlan.GetID())

    def SetSkillPlan(self, skillPlan):
        if skillPlan != self.skillPlan:
            self.skillPlan = skillPlan
            self.UpdateSkillsMissingBanner()
            self.UpdateOmegaBanner()
            self.omegaButton.SetSkillPlan(skillPlan)
            self.PopulateScroll()

    def UpdateSkillsMissingBanner(self):
        if not self.skillPlan:
            return
        numMissing = len(self.skillPlan.GetMissingSkillbooks())
        if numMissing:
            self.skillbooksMissingBtn.label = GetByLabel('UI/SkillPlan/BuyMissingSkillbooks', numMissing=numMissing)
            self.skillbooksMissingBtn.Show()
        else:
            self.skillbooksMissingBtn.Hide()

    def UpdateOmegaBanner(self):
        if self.skillPlan.IsOmegaLocked():
            self.omegaButton.Show()
        else:
            self.omegaButton.Hide()

    def PopulateScroll(self):
        self.scroll.Flush()
        self.entries = []
        for typeID, level in self.skillPlan.GetSkillRequirements():
            if not self.IsSkillVisible(level, typeID):
                continue
            entry = self._ConstructEntry(level, typeID)
            self.entries.append(entry)
            blue.pyos.BeNice()

        if not self.entries:
            self.scroll.ShowNoContentHint(GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/NoSkillsMatchingFilters'))

    def _ConstructEntry(self, level, typeID):
        entry = SkillPlanContentsSkillEntry(parent=self.scroll, typeID=typeID, level=level, padBottom=8)
        entry.onClickSignal.connect(self.OnEntryClicked)
        entry.onDblClickSignal.connect(self.OnEntryDblClicked)
        entry.onSkillAddedToQueue.connect(self.OnEntrySkillAddedToQueue)
        return entry

    def IsSkillVisible(self, level, typeID):
        if IsHideTrainedSkillsEnabled() and sm.GetService('skills').GetMyLevel(typeID) >= level:
            return False
        filterTxt = self.quickFilterEdit.GetValue()
        if filterTxt and filterTxt.lower() not in evetypes.GetName(typeID).lower():
            return False
        return True

    def OnEntryDblClicked(self, entry):
        sm.GetService('skillqueue').AddSkillToQueue(entry.typeID)

    def OnEntryClicked(self, clickedEntry):
        prereqs, reqForTypeIDs = GetPreReqsAndRequiredForSkillLevel(clickedEntry.typeID, clickedEntry.level)
        if uicore.uilib.Key(uiconst.VK_CONTROL):
            deselectEntry = itertoolsext.first_or_default(self.entries, lambda x: x.isSelected) == clickedEntry
        else:
            deselectEntry = False
        for entry in self.entries:
            if entry == clickedEntry:
                if deselectEntry:
                    entry.SetDeselected()
                else:
                    entry.SetSelected()
                entry.UpdateReqState(NO_REQ)
            else:
                entry.SetDeselected()
                if deselectEntry:
                    entry.UpdateReqState(NO_REQ)
                else:
                    reqState = GetRequirementStateForEntry(clickedEntry.typeID, clickedEntry.level, entry, prereqs, reqForTypeIDs)
                    entry.UpdateReqState(reqState)

    def OnEntrySkillAddedToQueue(self, typeID, level):
        if not GetSkillPlanSvc().IsSkillPlanTracked(self.skillPlan.GetID()) and not self.askedAboutTracking:
            if uicore.Message('AskTrackPlan', {}, uiconst.YESNO, suppress=uiconst.ID_YES) == uiconst.ID_YES:
                GetSkillPlanSvc().SetTrackedSkillPlanID(self.skillPlan.GetID())
            self.askedAboutTracking = True

    def OnSkillsChanged(self, skills):
        self._RefreshEntries()

    def OnSkillQueueChanged(self):
        self._RefreshEntries()

    def _RefreshEntries(self):
        for entry in self.entries:
            entry.Refresh()

    def OnSkillsAvailable(self, typeIDs):
        for entry in self.entries:
            if entry.typeID in typeIDs:
                entry.Refresh()

        self.UpdateSkillsMissingBanner()

    def OnSubscriptionChanged(self):
        self._RefreshEntries()
