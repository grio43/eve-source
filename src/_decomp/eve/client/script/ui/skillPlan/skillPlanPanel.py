#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\skillPlan\skillPlanPanel.py
import uthread2
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.uianimations import animations
from eve.client.script.ui.control.floatingToggleButtonGroup import FloatingToggleButtonGroup
from eve.client.script.ui.shared.monetization.events import LogMultiPilotTrainingBannerImpression
from eve.client.script.ui.shared.monetization.multiTrainingOverlay import MultiTrainingOverlay
from eve.client.script.ui.shared.pointerTool.pointerToolConst import UNIQUE_NAME_SKILL_PLANS_TAB, UNIQUE_NAME_SKILL_CATALOGUE_TAB
from eve.client.script.ui.skillPlan import skillPlanUISignals, skillPlanUtil
from eve.client.script.ui.skillPlan.browser.skillPlansBrowserPanel import SkillPlansBrowserPanel
from eve.client.script.ui.skillPlan.selectedPlan.selectedSkillPlanContainer import SelectedSkillPlanContainer
from eve.client.script.ui.skillPlan.skillPlanConst import BUTTON_GROUP_ID_TOP_LEVEL, PANEL_SKILLS_CATALOGUE, PANEL_SKILL_PLANS
from eve.client.script.ui.skillPlan.skillPlanEditor.skillPlanEditorPanel import SkillPlanEditorPanel
from eve.client.script.ui.skillPlan.skillPlanUtil import IsExternalServicePanelSelected
from eve.client.script.ui.skillPlan.skillsCatalogue.skillsCataloguePanel import SkillsCataloguePanel
from eve.client.script.ui.skillPlan.trainingOverviewPanel.trainingOverviewPanel import TrainingOverviewPanel
from eve.client.script.ui.skilltrading.dailyAlphaInjectorOverlay import DailyAlphaInjectorOverlay
from localization import GetByLabel
from skills.skillplan import skillPlanSignals
from skills.skillplan.skillPlanService import GetSkillPlanSvc
from skills.skillplan.skillPlanTemplate import SkillPlanTemplate

class SkillPlanPanel(Container):

    def ApplyAttributes(self, attributes):
        super(SkillPlanPanel, self).ApplyAttributes(attributes)
        PlaySound('skills_planner_window_open_play')
        PlaySound('skills_planner_background_loop_play')
        self.selectedSkillPlan = None
        self.skillPlanEditor = None
        self.multiTrainingOverlay = None
        self.dailyAlphaInjectorOverlay = None
        self.skillPlanBrowser = None
        skillPlanSignals.on_created.connect(self.OnSkillPlanCreated)
        skillPlanSignals.on_saved.connect(self.OnSkillPlanSaved)
        skillPlanSignals.on_deleted.connect(self.OnSkillPlanDeleted)
        skillPlanUISignals.on_create_new_personal_button.connect(self.OnCreateNewPersonalSkillPlanButton)
        skillPlanUISignals.on_create_new_corp_button.connect(self.OnCreateNewCorpSkillPlanButton)
        skillPlanUISignals.on_edit_button.connect(self.OnEditSkillPlanButton)
        skillPlanUISignals.on_delete_button.connect(self.OnDeleteSkillPlanButton)
        skillPlanUISignals.on_close_new_button.connect(self.OnCloseNewSkillPlanButton)
        skillPlanUISignals.on_selected.connect(self.OnSkillPlanSelected)
        skillPlanUISignals.on_close_button.connect(self.OnSkillPlanCloseButton)
        skillPlanUISignals.on_show_multi_training_msg.connect(self.OnShowMultiTrainingMessage)
        skillPlanUISignals.on_show_alpha_training_msg.connect(self.OnShowAlphaTrainingMessage)
        self.overlayCont = Container(name='overlayCont', parent=self, state=uiconst.UI_HIDDEN)
        self.rightCont = Container(name='rightCont', parent=self, align=uiconst.TORIGHT_PROP, width=1.0 - 1.0 / uiconst.GOLDEN_RATIO, padLeft=32)
        self.leftCont = Container(name='leftCont', parent=self)
        self._ConstructLeft()
        self._ConstructRight()
        uthread2.start_tasklet(self.AutoSelectTab)
        self.skillPlanTemplate = attributes.get('skillPlanTemplate', None)
        if self.skillPlanTemplate:
            self.OnCreateNewPersonalSkillPlanWithTemplate(self.skillPlanTemplate)

    def _ConstructLeft(self):
        self.leftOverlayCont = Container(parent=self.leftCont, name='leftOverlayCont', state=uiconst.UI_HIDDEN)
        self.leftTabContentsCont = Container(name='leftTabContents', parent=self.leftCont, state=uiconst.UI_PICKCHILDREN)
        tabcont = ContainerAutoSize(name='tabCont', parent=self.leftTabContentsCont, align=uiconst.TOTOP, padBottom=16)
        self.topLevelToggleButtonGroup = FloatingToggleButtonGroup(parent=tabcont, align=uiconst.CENTERTOP, fontsize=16, width=400, callback=self.OnTopLevelToggleButtonGroup)
        self.skillPlanBrowser = SkillPlansBrowserPanel(parent=self.leftTabContentsCont, state=uiconst.UI_HIDDEN)
        skillsCataloguePanel = SkillsCataloguePanel(parent=self.leftTabContentsCont, state=uiconst.UI_HIDDEN)
        self.topLevelToggleButtonGroup.AddButton(btnID=PANEL_SKILL_PLANS, label=GetByLabel('UI/SkillPlan/SkillPlans'), panel=self.skillPlanBrowser, hint=GetByLabel('UI/SkillPlan/SkillPlansHoverTooltip'), analyticID='TopLevelTabs_SkillPlans', uniqueUiName=UNIQUE_NAME_SKILL_PLANS_TAB)
        self.topLevelToggleButtonGroup.AddButton(btnID=PANEL_SKILLS_CATALOGUE, label=GetByLabel('UI/SkillPlan/SkillCatalogue'), panel=skillsCataloguePanel, hint=GetByLabel('UI/SkillPlan/SkillsCatalogueHoverTooltip'), analyticID='TopLevelTabs_SkillCatalogue', uniqueUiName=UNIQUE_NAME_SKILL_CATALOGUE_TAB)

    def AutoSelectTab(self):
        if IsExternalServicePanelSelected() and not sm.GetService('publicGatewaySvc').is_available():
            panelID = PANEL_SKILLS_CATALOGUE
        else:
            panelID = skillPlanUtil.GetPersistedPanelID(BUTTON_GROUP_ID_TOP_LEVEL)
        self.topLevelToggleButtonGroup.SelectByID(panelID)

    def OnTopLevelToggleButtonGroup(self, btnID, oldBtnID):
        skillPlanUtil.SetPersistedPanelID(BUTTON_GROUP_ID_TOP_LEVEL, btnID)

    def _ConstructRight(self):
        self.rightMainCont = Container(name='rightMainCont', parent=self.rightCont, padTop=16)
        self.trainingOverviewPanel = TrainingOverviewPanel(parent=self.rightMainCont, align=uiconst.TOALL)

    def _ConstructMultiTrainingOverlay(self):
        if self.multiTrainingOverlay is None or self.multiTrainingOverlay.destroyed:
            self.multiTrainingOverlay = MultiTrainingOverlay(parent=self, padding=(-2, 0, -2, 2), idx=0)

    def _ConstructAlphaOverlay(self):
        if self.dailyAlphaInjectorOverlay is None or self.dailyAlphaInjectorOverlay.destroyed:
            self.dailyAlphaInjectorOverlay = DailyAlphaInjectorOverlay(parent=self, padding=(-2, 0, -2, 2), idx=0)

    def ShowCertifiedPlans(self, careerID):
        self.topLevelToggleButtonGroup.SelectByID(PANEL_SKILL_PLANS)
        self.skillPlanBrowser.ShowCertifiedPlans(careerID)

    def OnSkillPlanCloseButton(self):
        self._HideAllOverlays()

    def OnCloseNewSkillPlanButton(self):
        self._HideAllOverlays()

    def OnSkillPlanCreated(self, skillPlanID):
        self._HideAllOverlays()

    def OnSkillPlanSaved(self, skillPlan):
        self._HideAllOverlays()

    def OnSkillPlanDeleted(self, skillPlanID):
        if self.selectedSkillPlan and skillPlanID == self.selectedSkillPlan.GetID():
            self._HideAllOverlays()

    def _HideAllOverlays(self):
        self._DisableLeftOverlay()
        self._DisableOverlay()
        self.trainingOverviewPanel.Show()
        self.skillPlanEditor = None

    def OnCreateNewPersonalSkillPlanButton(self):
        skillPlan = GetSkillPlanSvc().GetNewUnsavedPersonal()
        self._ShowSkillPlanEditor(skillPlan)

    def OnCreateNewCorpSkillPlanButton(self):
        skillPlan = GetSkillPlanSvc().GetNewUnsavedCorp()
        self._ShowSkillPlanEditor(skillPlan)

    def OnEditSkillPlanButton(self, skillPlan):
        self._HideAllOverlays()
        newSkillPlan = skillPlan.GetCopy()
        self._ShowSkillPlanEditor(newSkillPlan)

    def OnCreateNewPersonalSkillPlanWithTemplate(self, skillPlanTemplate):
        skillPlan = GetSkillPlanSvc().GetNewUnsavedPersonal()
        skillPlanTemplate.Apply(skillPlan)
        self._ShowSkillPlanEditor(skillPlan)

    def OnDeleteSkillPlanButton(self, skillPlan):
        GetSkillPlanSvc().Delete(skillPlan)

    def _ShowSkillPlanEditor(self, skillPlan):
        self._EnableOverlay()
        self.trainingOverviewPanel.Hide()
        if not skillPlan:
            return
        self.skillPlanEditor = SkillPlanEditorPanel(parent=self.overlayCont, skillPlan=skillPlan, padTop=16)

    def OnSkillPlanSelected(self, skillPlan):
        if self.destroyed:
            return
        if skillPlan == self.selectedSkillPlan:
            return
        self._EnableLeftOverlay()
        self.leftOverlayCont.Flush()
        self.selectedSkillPlanContainer = SelectedSkillPlanContainer(parent=self.leftOverlayCont, skillPlan=skillPlan, padTop=45)
        self._SelectSkillPlan(skillPlan)

    def _SelectSkillPlan(self, skillPlan):
        if self.selectedSkillPlan != skillPlan:
            self.selectedSkillPlan = skillPlan
            sm.ScatterEvent('OnSelectedSkillPlanChanged')

    def _DeselectSkillPlan(self):
        if self.selectedSkillPlan:
            self.selectedSkillPlan = None
            sm.ScatterEvent('OnSelectedSkillPlanChanged')

    def IsSkillPlanContainerShown(self, skillPlanID):
        return self.selectedSkillPlan == skillPlanID

    def OnBack(self, *args):
        self._HideAllOverlays()

    def _EnableOverlay(self):
        duration = 0.3
        animations.FadeTo(self.leftTabContentsCont, self.leftTabContentsCont.opacity, 0.0, duration=duration)
        self.leftTabContentsCont.Disable()
        self.overlayCont.Show()
        animations.FadeTo(self.overlayCont, 0.0, 1.0, duration=duration)

    def _DisableOverlay(self):
        if not self.overlayCont.display:
            return
        self.overlayCont.Hide()
        self.overlayCont.Flush()
        animations.FadeTo(self.leftTabContentsCont, self.leftTabContentsCont.opacity, 1.0, duration=uiconst.TIME_EXIT)
        self.leftTabContentsCont.Enable()

    def _EnableLeftOverlay(self):
        duration = 0.3
        animations.FadeTo(self.leftTabContentsCont, self.leftTabContentsCont.opacity, 0.2, duration=duration)
        self.leftTabContentsCont.Disable()
        self.leftOverlayCont.Show()
        animations.FadeTo(self.leftOverlayCont, 0.0, 1.0, duration=duration)
        animations.MorphScalar(self.leftOverlayCont, 'left', -0.01, 0, duration=duration)

    def _DisableLeftOverlay(self):
        if not self.leftOverlayCont.display:
            return
        self.leftOverlayCont.Hide()
        self.leftOverlayCont.Flush()
        animations.FadeTo(self.leftTabContentsCont, self.leftTabContentsCont.opacity, 1.0, duration=uiconst.TIME_EXIT)
        self.leftTabContentsCont.Enable()
        self._DeselectSkillPlan()

    def OnShowMultiTrainingMessage(self):
        self._ConstructMultiTrainingOverlay()
        uthread2.start_tasklet(self.multiTrainingOverlay.Display)
        LogMultiPilotTrainingBannerImpression()

    def OnShowAlphaTrainingMessage(self, message):
        self._ConstructAlphaOverlay()
        uthread2.start_tasklet(self.dailyAlphaInjectorOverlay.Display, message)

    def Close(self):
        super(SkillPlanPanel, self).Close()
        PlaySound('skills_planner_background_loop_stop')
