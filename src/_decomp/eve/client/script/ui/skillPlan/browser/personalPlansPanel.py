#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\skillPlan\browser\personalPlansPanel.py
import uthread2
from carbonui import TextAlign, uiconst
from carbonui.control.button import Button
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.eveLabel import EveCaptionLarge
from eve.client.script.ui.control.eveLoadingWheel import LoadingWheel
from eve.client.script.ui.skillPlan import skillPlanUISignals, skillPlanUtil
from eve.client.script.ui.skillPlan.browser.noContentHintContainer import NoContentHintContainer
from eve.client.script.ui.skillPlan.browser.skillPlanScroll import SkillPlanScroll
from eve.client.script.ui.skillPlan.skillPlanConst import BUTTON_GROUP_ID_SKILL_PLANS, BUTTON_GROUP_ID_TOP_LEVEL, PANEL_CERTIFIED, PANEL_SKILLS_CATALOGUE
from localization import GetByLabel
from skills.skillplan import skillPlanSignals, skillPlanConst
from skills.skillplan.errors import SkillPlanConnectionError
from skills.skillplan.skillPlanConst import MAX_PERSONAL_PLANS
from skills.skillplan.skillPlanService import GetSkillPlanSvc
CREATE_BUTTON_WIDTH = 200
CREATE_BUTTON_HEIGHT = 70
CREATE_BUTTON_FONT_SIZE = 16

def CreateNew(*args):
    skillPlanUISignals.on_create_new_personal_button()


class CreatePersonalPlanButton(Button):
    default_minWidth = 200
    default_width = 200
    default_height = 70
    default_label = GetByLabel('UI/SkillPlan/CreateNewSkillPlan')
    default_func = CreateNew

    def ApplyAttributes(self, attributes):
        super(CreatePersonalPlanButton, self).ApplyAttributes(attributes)
        self.numPlans = None

    def LoadTooltipPanel(self, tooltipPanel, owner):
        tooltipPanel.LoadStandardSpacing()
        tooltipPanel.columns = 1
        tooltipPanel.AddMediumHeader(text=GetByLabel('UI/SkillPlan/CreatePersonalSkillPlan'))
        tooltipPanel.AddLabelMedium(text=GetByLabel('UI/SkillPlan/PlansInTotal', numPlans=self.numPlans, numTotal=skillPlanConst.MAX_PERSONAL_PLANS))
        warningText = self._GetWarningText()
        if warningText:
            tooltipPanel.AddLabelMedium(text=warningText, color=eveColor.WARNING_ORANGE, wrapWidth=200)

    def _GetWarningText(self):
        if self.numPlans >= skillPlanConst.MAX_PERSONAL_PLANS:
            warningText = GetByLabel('UI/SkillPlan/MaximumSkillPlanReached', numPlans=skillPlanConst.MAX_PERSONAL_PLANS)
        else:
            warningText = ''
        return warningText

    def UpdateState(self, numPlans):
        self.numPlans = numPlans


class PersonalPlansPanel(Container):

    def ApplyAttributes(self, attributes):
        super(PersonalPlansPanel, self).ApplyAttributes(attributes)
        skillPlanSignals.on_deleted.connect(self.OnSkillPlanDeleted)
        skillPlanSignals.on_created.connect(self.OnSkillPlanCreated)
        skillPlanSignals.on_saved.connect(self.OnSkillPlanSaved)
        self.ConstructLayout()

    def Show(self, *args):
        super(PersonalPlansPanel, self).Show(*args)
        uthread2.start_tasklet(self.PopulateScroll)

    def ConstructLayout(self):
        self.noContentHint = NoContentHintContainer(parent=self, align=uiconst.VERTICALLY_CENTERED, state=uiconst.UI_HIDDEN, btnClass=CreatePersonalPlanButton)
        self.buttonCont = ContainerAutoSize(name='buttonCont', parent=self, align=uiconst.TOBOTTOM, state=uiconst.UI_HIDDEN, padTop=10)
        self.createBtn = CreatePersonalPlanButton(name='createBtn', parent=self.buttonCont, align=uiconst.CENTER)
        self.loadingWheel = LoadingWheel(parent=self, align=uiconst.CENTER, state=uiconst.UI_HIDDEN, idx=0)
        self.scroll = SkillPlanScroll(parent=self, padTop=20)
        self.scroll.onSizeChangeSignal.connect(self.OnScrollSizeChanged)

    def OnScrollSizeChanged(self, width, height):
        uthread2.start_tasklet(self.PositionButtonCont)

    def PositionButtonCont(self):
        if self.destroyed:
            return
        if not self.scroll.display:
            self.buttonCont.SetAlign(uiconst.CENTER)
            self.buttonCont.SetParent(self, 0)
        elif not self.scroll.IsVerticalScrollBarVisible():
            self.buttonCont.SetAlign(uiconst.TOTOP)
            self.buttonCont.SetParent(self.scroll)
        else:
            self.buttonCont.SetAlign(uiconst.TOBOTTOM)
            self.buttonCont.SetParent(self, 0)
        numPlans = len(GetSkillPlanSvc().GetAllPersonal())
        if numPlans >= MAX_PERSONAL_PLANS:
            self.createBtn.Disable()
            self.createBtn.hint = GetByLabel('UI/SkillPlan/MaximumSkillPlanReached', numPlans=numPlans)
        else:
            self.createBtn.Enable()
            self.createBtn.hint = ''

    def PopulateScroll(self):
        if self.destroyed:
            return
        skillPlans, noContentHint = self._GetSkillPlans()
        if skillPlans:
            self.scroll.Show()
            self.buttonCont.Show()
            self.buttonCont.SetParent(self, 0)
            self.noContentHint.Hide()
            self.scroll.ConstructSkillPlanEntries(skillPlans)
        else:
            self.scroll.Hide()
            self.buttonCont.Hide()
            self.noContentHint.SetText(noContentHint)
            self.noContentHint.state = uiconst.UI_PICKCHILDREN
        self.createBtn.UpdateState(len(skillPlans or []))
        self.PositionButtonCont()

    def _GetSkillPlans(self):
        self.loadingWheel.Show()
        self.buttonCont.Hide()
        try:
            skillPlans = GetSkillPlanSvc().GetAllPersonal().values()
        except SkillPlanConnectionError:
            skillPlans = None
            noContentHint = GetByLabel('UI/SkillPlan/ConnectionError')
            skillPlanUtil.SetPersistedPanelID(BUTTON_GROUP_ID_TOP_LEVEL, PANEL_SKILLS_CATALOGUE)
            skillPlanUtil.SetPersistedPanelID(BUTTON_GROUP_ID_SKILL_PLANS, PANEL_CERTIFIED)
        else:
            noContentHint = GetByLabel('UI/SkillPlan/NoPersonalSkillPlans')
            self.buttonCont.Show()
        finally:
            self.loadingWheel.Hide()

        return (skillPlans, noContentHint)

    def OnSkillPlanDeleted(self, skillPlanID):
        self.PopulateScroll()

    def OnSkillPlanCreated(self, skillPlanID):
        self.PopulateScroll()

    def OnSkillPlanSaved(self, skillPlan):
        return self.PopulateScroll()
