#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\skillPlan\browser\skillPlansBrowserPanel.py
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from eve.client.script.ui.control.toggleButtonGroup import ToggleButtonGroup
from eve.client.script.ui.skillPlan import skillPlanUtil
from eve.client.script.ui.skillPlan.browser.certifiedPlansPanel import CertifiedPlansPanel
from eve.client.script.ui.skillPlan.browser.corpPlansPanel import CorpPlansPanel
from eve.client.script.ui.skillPlan.browser.personalPlansPanel import PersonalPlansPanel
from eve.client.script.ui.shared.pointerTool.pointerToolConst import UNIQUE_NAME_SKILL_PLANS_CERTIFIED_TAB, UNIQUE_NAME_SKILL_PLANS_CORP_TAB, UNIQUE_NAME_SKILL_PLANS_PERSONAL_TAB
from eve.client.script.ui.skillPlan.skillPlanConst import BUTTON_GROUP_ID_SKILL_PLANS, PANEL_CERTIFIED, PANEL_CORP, PANEL_PERSONAL
from eve.common.script.sys import idCheckers
from localization import GetByLabel

class SkillPlansBrowserPanel(Container):

    def ApplyAttributes(self, attributes):
        super(SkillPlansBrowserPanel, self).ApplyAttributes(attributes)
        self.isInitialized = False
        self.certifiedSkillPlans = None
        self.mainCont = Container(name='mainCont', parent=self)
        if sm.GetService('publicGatewaySvc').is_available():
            self.tabCont = ContainerAutoSize(name='tabCont', parent=self.mainCont, align=uiconst.TOTOP, padding=(0, 5, 0, 20))
            self.ConstructToggleButtonGroup()
        else:
            self.tabCont = self.toggleButtonGroup = None
            CertifiedPlansPanel(parent=self.mainCont)

    def ConstructToggleButtonGroup(self):
        isInPlayerCorp = idCheckers.IsPlayerCorporation(session.corpid)
        self.toggleButtonGroup = ToggleButtonGroup(parent=self.tabCont, align=uiconst.CENTERTOP, fontsize=16, width=500 if isInPlayerCorp else 400, callback=self.OnToggleButtonGroup)
        self.certifiedSkillPlans = CertifiedPlansPanel(parent=self.mainCont, state=uiconst.UI_HIDDEN)
        self.toggleButtonGroup.AddButton(btnID=PANEL_CERTIFIED, label=GetByLabel('UI/SkillPlan/CertifiedPlans'), panel=self.certifiedSkillPlans, hint=GetByLabel('UI/SkillPlan/CertifiedPlansHoverTooltip'), analyticID='SkillPlanTabs_CertifiedPlans', uniqueUiName=UNIQUE_NAME_SKILL_PLANS_CERTIFIED_TAB)
        panelPersonal = PersonalPlansPanel(parent=self.mainCont, state=uiconst.UI_HIDDEN)
        self.toggleButtonGroup.AddButton(btnID=PANEL_PERSONAL, label=GetByLabel('UI/SkillPlan/PersonalPlans'), panel=panelPersonal, hint=GetByLabel('UI/SkillPlan/PersonalPlansHoverTooltip'), analyticID='SkillPlanTabs_PersonalPlans', uniqueUiName=UNIQUE_NAME_SKILL_PLANS_PERSONAL_TAB)
        if isInPlayerCorp:
            panelCorp = CorpPlansPanel(parent=self.mainCont, state=uiconst.UI_HIDDEN)
            self.toggleButtonGroup.AddButton(btnID=PANEL_CORP, label=GetByLabel('UI/SkillPlan/CorpPlans'), panel=panelCorp, hint=GetByLabel('UI/SkillPlan/CorpPlansHoverTooltip'), analyticID='SkillPlanTabs_CorpPlans', uniqueUiName=UNIQUE_NAME_SKILL_PLANS_CORP_TAB)

    def Show(self, *args):
        super(SkillPlansBrowserPanel, self).Show(*args)
        if not self.isInitialized:
            self.AutoSelectTab()
            self.isInitialized = True

    def AutoSelectTab(self):
        if not self.toggleButtonGroup:
            return
        btnID = skillPlanUtil.GetPersistedPanelID(BUTTON_GROUP_ID_SKILL_PLANS)
        self.toggleButtonGroup.SelectByID(btnID)

    def OnToggleButtonGroup(self, btnID, oldBtnID):
        skillPlanUtil.SetPersistedPanelID(BUTTON_GROUP_ID_SKILL_PLANS, btnID)

    def ShowCertifiedPlans(self, careerID):
        self.toggleButtonGroup.SelectByID(PANEL_CERTIFIED)
        self.certifiedSkillPlans.ShowCertifiedPlans(careerID)
