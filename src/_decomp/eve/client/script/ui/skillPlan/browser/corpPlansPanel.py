#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\skillPlan\browser\corpPlansPanel.py
import math
import localization
import uthread2
from carbonui import uiconst
from carbonui.control.button import Button
from carbonui.primitives.container import Container
from characterdata import careerpath
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.control.eveLoadingWheel import LoadingWheel
from eve.client.script.ui.control.toggleButtonGroupCircular import ToggleButtonGroupCircular
from eve.client.script.ui.quickFilter import QuickFilterEdit
from eve.client.script.ui.shared.careerPortal import careerConst
from eve.client.script.ui.skillPlan import skillPlanUISignals, skillPlanUtil
from eve.client.script.ui.skillPlan.browser.noContentHintContainer import NoContentHintContainer
from eve.client.script.ui.skillPlan.browser.skillPlanScroll import SkillPlanScroll
from eve.client.script.ui.skillPlan.skillPlanConst import BUTTON_GROUP_ID_SKILL_PLANS, BUTTON_GROUP_ID_TOP_LEVEL, PANEL_CERTIFIED, PANEL_SKILLS_CATALOGUE
from eve.common.lib import appConst
from localization import GetByLabel, GetByMessageID
from skills.skillplan import skillPlanSignals, skillPlanConst
from skills.skillplan.errors import SkillPlanConnectionError
from skills.skillplan.skillPlanService import GetSkillPlanSvc
NUM_PER_PAGE = 12

def CreateNew(self, *args):
    skillPlanUISignals.on_create_new_corp_button()


class CreateCorpPlanButton(Button):
    default_minWidth = 200
    default_width = 200
    default_height = 70
    default_label = GetByLabel('UI/SkillPlan/CreateNewSkillPlan')
    default_func = CreateNew

    def ApplyAttributes(self, attributes):
        super(CreateCorpPlanButton, self).ApplyAttributes(attributes)
        self.numPlans = None

    def UpdateState(self, numPlans):
        self.numPlans = numPlans
        if not session.corprole & appConst.corpRoleSkillPlanManager:
            self.Disable()
        elif numPlans >= skillPlanConst.MAX_CORP_PLANS:
            self.Disable()
        else:
            self.Enable()

    def LoadTooltipPanel(self, tooltipPanel, owner):
        tooltipPanel.LoadStandardSpacing()
        tooltipPanel.columns = 1
        tooltipPanel.AddMediumHeader(text=GetByLabel('UI/SkillPlan/CreateCorpSkillPlan'))
        tooltipPanel.AddLabelMedium(text=GetByLabel('UI/SkillPlan/PlansInTotal', numPlans=self.numPlans, numTotal=skillPlanConst.MAX_CORP_PLANS))
        warningText = self._GetWarningText()
        if warningText:
            tooltipPanel.AddLabelMedium(text=warningText, color=eveColor.WARNING_ORANGE, wrapWidth=200)

    def _GetWarningText(self):
        if not session.corprole & appConst.corpRoleSkillPlanManager:
            warningText = GetByLabel('UI/SkillPlan/CorpPlanCreateRequiresRoleHint')
        elif self.numPlans >= skillPlanConst.MAX_CORP_PLANS:
            warningText = GetByLabel('UI/SkillPlan/MaximumSkillPlanReached', numPlans=skillPlanConst.MAX_CORP_PLANS)
        else:
            warningText = ''
        return warningText


class CorpSkillPlansPaginationController(object):

    def __init__(self, numPerPage):
        self.numPerPage = numPerPage
        self.currPage = 0
        self.categoryID = None
        self.filterText = None

    def GetData(self):
        allData = self.GetAllData()
        start = self.currPage * self.numPerPage
        end = min(len(allData), (self.currPage + 1) * self.numPerPage)
        return allData[start:end]

    def GetNumPages(self):
        return int(math.ceil(len(self.GetAllData()) / float(self.numPerPage)))

    def SetNumPerPage(self, numPerPage):
        self.numPerPage = numPerPage

    def SetCurrPage(self, currPage):
        self.currPage = currPage

    def GetAllData(self):
        skillPlans = GetSkillPlanSvc().GetAllCorp().values()
        skillPlans = filter(self._ApplyFilters, skillPlans)
        skillPlans = localization.util.Sort(skillPlans, key=lambda x: x.GetName())
        return skillPlans

    def _ApplyFilters(self, skillPlan):
        categoryID = self.categoryID
        if categoryID and categoryID != skillPlan.GetCategoryID():
            return False
        if self.filterText:
            return self.filterText in skillPlan.GetName().lower()
        return True

    def SetCategoryID(self, value):
        self.categoryID = value

    def SetFilterText(self, value):
        if value:
            self.filterText = value.lower()
        else:
            self.filterText = None


class CorpPlansPanel(Container):

    def ApplyAttributes(self, attributes):
        super(CorpPlansPanel, self).ApplyAttributes(attributes)
        skillPlanSignals.on_deleted.connect(self.OnSkillPlanDeleted)
        skillPlanSignals.on_created.connect(self.OnSkillPlanCreated)
        skillPlanSignals.on_saved.connect(self.OnSkillPlanSaved)
        self.ConstructLayout()
        self.paginationController = CorpSkillPlansPaginationController(NUM_PER_PAGE)

    def Show(self, *args):
        super(CorpPlansPanel, self).Show(*args)
        uthread2.start_tasklet(self.ReconstructPagination)

    def ConstructLayout(self):
        self.filtersCont = Container(name='filtersCont', parent=self, align=uiconst.TOTOP, height=48, padding=(0, 10, 10, 10))
        self.quickFilterEdit = QuickFilterEdit(parent=self.filtersCont, align=uiconst.CENTERRIGHT, width=200, height=32, callback=self.OnQuickFilterEdit)
        self.numShownLabel = EveLabelMedium(parent=self.filtersCont, align=uiconst.CENTERRIGHT, left=210)
        self.categoryButtonGroup = ToggleButtonGroupCircular(parent=self.filtersCont, align=uiconst.TOLEFT, callback=self.OnCategoryButtonGroup, isOptional=True)
        for label, careerPathID in self.GetCategoryButtonData():
            self.categoryButtonGroup.AddButton(btnID=careerPathID, iconPath=careerConst.CAREERS_32_SIZES.get(careerPathID), iconSize=32, btnSize=48, hint=label)

        self.noContentHint = NoContentHintContainer(parent=self, align=uiconst.VERTICALLY_CENTERED, state=uiconst.UI_HIDDEN, btnClass=CreateCorpPlanButton)
        self.buttonCont = Container(name='buttonCont', parent=self, align=uiconst.TOBOTTOM, state=uiconst.UI_HIDDEN, padTop=12, height=30)
        self.paginationButtonGroup = ToggleButtonGroupCircular(parent=self.buttonCont, align=uiconst.TOLEFT, callback=self.OnPaginationButton)
        self.createBtn = CreateCorpPlanButton(name='createBtn', parent=self.buttonCont, align=uiconst.CENTER)
        self.loadingWheel = LoadingWheel(parent=self, align=uiconst.CENTER, state=uiconst.UI_HIDDEN, idx=0)
        self.scroll = SkillPlanScroll(parent=self, padTop=20, padBottom=10)
        self.scroll.onSizeChangeSignal.connect(self.OnScrollSizeChanged)

    def OnQuickFilterEdit(self):
        self.paginationController.SetFilterText(self.quickFilterEdit.GetValue())
        self.ReconstructPagination()

    def ReconstructPagination(self):
        try:
            numPages = self.paginationController.GetNumPages()
            show_pagination = numPages > 1
            self.paginationButtonGroup.display = show_pagination
            self.paginationButtonGroup.ClearButtons()
            self.createBtn.align = uiconst.TORIGHT if show_pagination else uiconst.CENTER
            for i in range(numPages):
                self.paginationButtonGroup.AddButton(btnID=i, label=str(i + 1), btnSize=32)

            if numPages:
                self.paginationButtonGroup.SelectByID(0)
            else:
                self.PopulateScroll()
        except SkillPlanConnectionError:
            self.HandleSkillPlanConnectionError()

    def HandleSkillPlanConnectionError(self):
        skillPlanUtil.SetPersistedPanelID(BUTTON_GROUP_ID_TOP_LEVEL, PANEL_SKILLS_CATALOGUE)
        skillPlanUtil.SetPersistedPanelID(BUTTON_GROUP_ID_SKILL_PLANS, PANEL_CERTIFIED)
        self.filtersCont.Hide()
        self.scroll.Hide()
        self.noContentHint.Show()
        self.noContentHint.SetText(GetByLabel('UI/SkillPlan/ConnectionError'))
        self.noContentHint.HideCreateBtn()

    def OnPaginationButton(self, *args):
        self.paginationController.SetCurrPage(self.paginationButtonGroup.GetValue())
        self.PopulateScroll()

    def OnCategoryButtonGroup(self, *args):
        self.paginationController.SetCategoryID(self.categoryButtonGroup.GetValue())
        self.ReconstructPagination()

    def GetCategoryButtonData(self):
        return [ (GetByMessageID(c.nameID), cID) for cID, c in careerpath.get_career_paths().iteritems() ]

    def OnScrollSizeChanged(self, width, height):
        uthread2.start_tasklet(self.UpdateState)

    def UpdateState(self):
        if self.destroyed:
            return
        numPlansTotal = self.GetNumPlansTotal()
        self._UpdateFilterCont(numPlansTotal)
        self._UpdateButtonCont()
        self.createBtn.UpdateState(numPlansTotal)
        self.noContentHint.UpdateState(numPlansTotal)
        numShown = len(self.paginationController.GetData())
        self.numShownLabel.text = GetByLabel('UI/SkillPlan/NumShown', numShown=numShown, numTotal=numPlansTotal)

    def GetNumPlansTotal(self):
        numPlans = len(GetSkillPlanSvc().GetAllCorp())
        return numPlans

    def _UpdateFilterCont(self, numPlans):
        self.filtersCont.display = numPlans > 0

    def _UpdateButtonCont(self):
        if not self.scroll.display:
            self.buttonCont.Hide()
            self.buttonCont.SetParent(self, 0)
        elif not self.scroll.IsVerticalScrollBarVisible():
            self.buttonCont.SetAlign(uiconst.TOTOP)
            self.buttonCont.SetParent(self.scroll)
        else:
            self.buttonCont.SetAlign(uiconst.TOBOTTOM)
            self.buttonCont.SetParent(self, 0)

    def PopulateScroll(self):
        if self.destroyed:
            return
        skillPlansShown = self._GetSkillPlans()
        if skillPlansShown:
            self.scroll.Show()
            self.buttonCont.SetParent(self, 0)
            self.scroll.ConstructSkillPlanEntries(skillPlansShown)
        else:
            self.scroll.Hide()
        self._UpdateNoContentHint()
        self.UpdateState()

    def _UpdateNoContentHint(self):
        noContentHint = self._GetNoContentHint()
        if noContentHint:
            self.noContentHint.SetText(noContentHint)
            self.noContentHint.state = uiconst.UI_PICKCHILDREN
        else:
            self.noContentHint.Hide()

    def _GetNoContentHint(self):
        if self.paginationController.GetData():
            return None
        elif self.GetNumPlansTotal():
            return GetByLabel('UI/SkillPlan/NoSkillPlansMatchingFilters')
        else:
            return GetByLabel('UI/SkillPlan/NoCorpSkillPlans')

    def _GetSkillPlans(self):
        self.loadingWheel.Show()
        self.buttonCont.Hide()
        try:
            skillPlans = self.paginationController.GetData()
            self.buttonCont.Show()
        finally:
            self.loadingWheel.Hide()

        return skillPlans

    def OnSkillPlanDeleted(self, skillPlanID):
        self.ReconstructPagination()

    def OnSkillPlanCreated(self, skillPlanID):
        self.ReconstructPagination()

    def OnSkillPlanSaved(self, skillPlan):
        self.ReconstructPagination()
