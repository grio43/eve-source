#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\skillPlan\browser\certifiedPlansPanel.py
import characterdata
import characterdata.factions
import localization
from carbonui import TextAlign, uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.line import Line
from characterdata import careerpathconst, careerpath, bloodlines
from eve.client.script.ui.control.eveLabel import EveCaptionLarge
from eve.client.script.ui.control.toggleButtonGroup import ToggleButtonGroup
from eve.client.script.ui.skillPlan.browser.airSkillPlanContainer import AirSkillPlanContainer
from eve.client.script.ui.skillPlan.browser.careerPathToggleButtonGroup import CareerPathToggleButtonGroupButton, SimpleCareerPathToggleButtonGroupButton
from eve.client.script.ui.skillPlan.browser.empireFactionToggleButtonGroup import EmpireFactionToggleButtonGroupButton
from eve.client.script.ui.skillPlan.browser.skillPlanScroll import SkillPlanScroll
from eve.client.script.ui.skillPlan.skillPlanConst import ICON_BY_FACTION_ID
from eve.common.lib import appConst
from localization import GetByLabel
from skills.skillplan.skillPlanService import GetSkillPlanSvc
from uihighlighting.uniqueNameConst import GetUniqueSkillPlanFactionName, GetUniqueSkillPlanCareerName

class CertifiedPlansPanel(Container):
    __notifyevents__ = ['OnSkillsChanged', 'OnSkillQueueChanged']

    def ApplyAttributes(self, attributes):
        super(CertifiedPlansPanel, self).ApplyAttributes(attributes)
        self.careerPathID = None
        self.factionID = None
        self.isLimitedHeight = False
        self.empireFactionContainer = None
        self.ReconstructLayout()
        sm.RegisterNotify(self)

    def ReconstructLayout(self):
        self.Flush()
        if GetSkillPlanSvc().HasFinishedAIRSkillPlan():
            self.ConstructCareerPathTabGroup()
            self.ConstructEmpireFactionTabGroup()
            self.scroll = SkillPlanScroll(parent=self, padTop=10)
            self.scroll.addUniqueName = True
            self.AutoSelectCareerPath()
        else:
            self.ConstructAirSkillPlanContainer()
            self.ConstructCareerPathTabGroup()
            self.careerPathTabGroup.Disable()
            self.careerPathTabGroup.opacity = 0.3

    def AutoSelectCareerPath(self):
        btnID = settings.char.ui.Get('skillPlanCareerPathID', None)
        if btnID:
            self.careerPathTabGroup.SelectByID(btnID)
            self.careerPathID = btnID

    def ShowCertifiedPlans(self, careerID):
        if GetSkillPlanSvc().HasFinishedAIRSkillPlan():
            self.careerPathTabGroup.SelectByID(careerID)
            if self.HasFactionTabGroup():
                self.empireFactionToggleButtons.SelectByID(session.raceID)

    def ConstructAirSkillPlanContainer(self):
        AirSkillPlanContainer(parent=self, align=uiconst.TOTOP_PROP, height=0.6, padTop=-100, clipChildren=True)

    def ConstructCareerPathTabGroup(self):
        if self.isLimitedHeight:
            self.careerPathTabGroup = ToggleButtonGroup(parent=self, align=uiconst.TOTOP, padding=(10, 25, 10, 50), callback=self.OnCareerPathTabGroup, height=60, btnClass=SimpleCareerPathToggleButtonGroupButton, selectSound='skills_planner_path_details_play')
        else:
            self.careerPathTabGroup = ToggleButtonGroup(parent=self, align=uiconst.TOTOP, height=315, padTop=0, padBottom=50, callback=self.OnCareerPathTabGroup, btnClass=CareerPathToggleButtonGroupButton, selectSound='skills_planner_path_details_play')
        self.selectCareerPathHint = EveCaptionLarge(parent=self, align=uiconst.TOTOP, textAlign=TextAlign.CENTER, padTop=60, text=GetByLabel('UI/SkillPlan/SelectCareerPathHint'))
        for careerPathID, careerPath in careerpath.get_career_paths().iteritems():
            label = localization.GetByMessageID(careerPath.nameID)
            self.careerPathTabGroup.AddButton(btnID=careerPathID, label=label, careerPathHint=localization.GetByMessageID(careerPath.descriptionID), analyticID='CareerPath_%s' % careerPathID, uniqueUiName=GetUniqueSkillPlanCareerName(careerPathID))

    def UpdateFactionUniqueNames(self):
        for btn in self.empireFactionToggleButtons.buttons:
            btn.uniqueUiName = GetUniqueSkillPlanFactionName(self.careerPathID, btn.btnID)

    def OnCareerPathTabGroup(self, btnID, oldBtnID):
        self.careerPathID = btnID
        self.factionID = None
        self.empireFactionToggleButtons.SelectByID(None)
        if self.careerPathID == careerpathconst.career_path_industrialist:
            self.empireFactionContainer.Hide()
            self.PopulateScroll()
        else:
            self.empireFactionContainer.Show()
            raceID = bloodlines.get_race_id(session.bloodlineID)
            factionID = appConst.factionByRace[raceID]
            self.empireFactionToggleButtons.SelectByID(factionID)
        self.UpdateFactionUniqueNames()
        self.selectCareerPathHint.Hide()
        settings.char.ui.Set('skillPlanCareerPathID', btnID)
        if btnID and oldBtnID != btnID:
            sm.ScatterEvent('OnSkillPlansCareerPathTabChanged', self.careerPathID)

    def GetVisibleCareerPathTabGroup(self):
        return self.careerPathID

    def GetVisibleFactionTabGroup(self):
        return self.factionID

    def HasFactionTabGroup(self):
        return self.empireFactionContainer and not self.empireFactionContainer.IsHidden()

    def ConstructEmpireFactionTabGroup(self):
        self.empireFactionContainer = Container(parent=self, align=uiconst.TOTOP, height=48, padding=(0, 25, 0, 25), state=uiconst.UI_HIDDEN)
        leftCont = Container(name='leftCont', parent=self.empireFactionContainer, align=uiconst.TOLEFT_PROP, width=0.275)
        Line(parent=leftCont, align=uiconst.TOPLEFT_PROP, pos=(0.999, 0.5, 0.999, 2), opacity=0.1)
        rightCont = Container(name='rightCont', parent=self.empireFactionContainer, align=uiconst.TORIGHT_PROP, width=0.275)
        Line(parent=rightCont, align=uiconst.TOPLEFT_PROP, pos=(0, 0.5, 0.999, 2), opacity=0.1)
        self.empireFactionToggleButtons = ToggleButtonGroup(parent=self.empireFactionContainer, align=uiconst.TOALL, height=0, callback=self.OnEmpireFactionTabGroup, btnClass=EmpireFactionToggleButtonGroupButton, selectSound='skills_planner_race_select_play')
        for factionID in appConst.factionByRace.values():
            hint = characterdata.factions.get_faction_name(factionID)
            self.empireFactionToggleButtons.AddButton(btnID=factionID, hint=hint, analyticID='Faction_%s' % factionID, iconPath=ICON_BY_FACTION_ID[factionID])

    def OnEmpireFactionTabGroup(self, tabID, oldTabID):
        self.factionID = tabID
        self.PopulateScroll()
        if tabID and oldTabID != tabID:
            sm.ScatterEvent('OnSkillPlanFactionTabChanged', self.factionID)

    def PopulateScroll(self):
        skillPlans = GetSkillPlanSvc().GetAllCertifiedForCareerPath(self.careerPathID)
        if self.factionID:
            skillPlans = [ skillPlan for skillPlan in skillPlans if skillPlan.factionID == self.factionID ]
        self.scroll.ConstructSkillPlanEntries(skillPlans)

    def OnSkillsChanged(self, skillInfoChange):
        self.ReconstructLayout()

    def OnSkillQueueChanged(self):
        self.ReconstructLayout()

    def _OnSizeChange_NoBlock(self, *args):
        super(CertifiedPlansPanel, self)._OnSizeChange_NoBlock(*args)
        w, h = self.GetAbsoluteSize()
        if h < 550 or w < 860:
            self.SetLimitedHeight()
        else:
            self.SetNotLimitedHeight()

    def SetNotLimitedHeight(self):
        if self.isLimitedHeight:
            self.isLimitedHeight = False
            self.ReconstructLayout()

    def SetLimitedHeight(self):
        if not self.isLimitedHeight:
            self.isLimitedHeight = True
            self.ReconstructLayout()
