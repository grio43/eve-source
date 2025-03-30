#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\charsheet\standingsPanel\standingsHeader.py
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from carbonui.uicore import uicore
from eve.client.script.ui.control.eveIcon import OwnerIcon
from eve.client.script.ui.control.eveLabel import EveLabelLarge
from eve.client.script.ui.shared.info import infoConst
from eve.client.script.ui.shared.neocom.charsheet.standingsPanel.standingsAssociationsTooltip import StandingsAssociationTooltip
from eve.client.script.ui.shared.neocom.charsheet.standingsPanel.standingsHeaderButtons import StandingActionButton, StandingBenefitButton
from eve.client.script.ui.shared.standings import standingUIConst
from eve.client.script.ui.shared.standings.standingLabel import StandingLabel
from eve.client.script.ui.shared.standings.standingsBonusTooltip import StandingBonusTooltip
from eve.client.script.ui.shared.standings.standingsUIUtil import GetStandingActionIDs, GetStandingBenefitIDs
from eve.client.script.ui.station.agents.agentConversationIcon import AgentConversationIcon
from eve.common.script.sys import idCheckers
ICONSIZE = 26

class StandingsHeader(Container):
    default_name = 'StandingsHeader'

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.standingData = None
        self.iconCont = Container(parent=self, align=uiconst.CENTERLEFT, pos=(0, 0, 64, 64))
        self.ownerIcon = OwnerIcon(parent=self.iconCont, align=uiconst.TOALL, size=64)
        self.mainCont = Container(name='mainCont', parent=self, padLeft=70, padTop=8)
        self.ConstructMainCont()

    def ConstructMainCont(self):
        topCont = Container(name='topCont', align=uiconst.TOTOP, parent=self.mainCont, height=20)
        self.helpIconCont = Container(name='helpIconCont', parent=topCont, align=uiconst.TORIGHT, width=16, padLeft=5)
        self.helpIcon = Sprite(name='helpIcon', parent=self.helpIconCont, align=uiconst.CENTER, width=16, height=16, texturePath='res:/UI/Texture/Icons/generic/more_info_16.png')
        self.standingLabel = StandingLabel(parent=topCont, align=uiconst.TORIGHT, isRightToLeft=True, standingData=self.standingData, fontSize=14)
        labelCont = Container(parent=topCont, clipChildren=True, padRight=4)
        self.captionAndStandingCont = ContainerAutoSize(name='captionAndStandingCont', parent=labelCont, align=uiconst.TOLEFT)
        bottomCont = Container(name='bottomCont', parent=self.mainCont, align=uiconst.TOBOTTOM, height=ICONSIZE, top=4, clipChildren=True)
        self.actionsCont = ContainerAutoSize(name='actionsCont', parent=bottomCont, align=uiconst.TOLEFT)
        self.benefitsCont = Container(name='benefitsCont', parent=bottomCont, align=uiconst.TOALL, clipChildren=True)

    def UpdateCaptionAndStandingCont(self):
        self.captionAndStandingCont.Flush()
        self.standingLabel.SetStandingData(self.standingData)
        if self.standingData and self.standingData.GetOwnerID1() == session.charid and not idCheckers.IsPlayerOwner(self.standingData.GetOwnerID2()):
            self.helpIcon.tooltipPanelClassInfo = StandingBonusTooltip(self.standingData)
        else:
            self.helpIconCont.Hide()
        self.ownerNameLabel = EveLabelLarge(parent=self.captionAndStandingCont, align=uiconst.TOLEFT, text=self.standingData.GetOwner2Name())
        self.agentConversationIcon = Container(name='iconCont', parent=self.captionAndStandingCont, align=uiconst.TOLEFT, width=16, padLeft=6)
        ownerID = self.standingData.GetOwnerID2()
        if idCheckers.IsNPCCharacter(ownerID):
            AgentConversationIcon(parent=self.agentConversationIcon, align=uiconst.CENTER, agentID=ownerID)

    def Update(self, standingData):
        self.standingData = standingData
        ownerID = self.standingData.ownerID2
        self.ownerIcon.SetOwnerID(ownerID)
        if sm.GetService('agents').IsAgent(ownerID):
            self.ownerIcon.tooltipPanelClassInfo = StandingsAssociationTooltip(ownerID)
        else:
            self.ownerIcon.tooltipPanelClassInfo = None
        self.UpdateCaptionAndStandingCont()
        self.UpdateActionsCont(ownerID)
        self.UpdateBenefitsCont(ownerID)
        self.agentConversationIcon.display = idCheckers.IsNPCCharacter(ownerID)

    def UpdateActionsCont(self, ownerID):
        self.actionsCont.Flush()
        for actionID in GetStandingActionIDs(ownerID):
            if not self.IsActionEnabled(actionID):
                continue
            texturePath = standingUIConst.ICONS_BY_ACTIONID[actionID]
            func = self.GetFunctionByActionID(actionID)
            StandingActionButton(parent=self.actionsCont, align=uiconst.TOLEFT, width=ICONSIZE, state=uiconst.UI_NORMAL, texturePath=texturePath, padRight=4, func=func, actionID=actionID, standingData=self.standingData)

    def IsActionEnabled(self, actionID):
        if actionID == standingUIConst.ACTION_TRAINSKILL:
            return self.standingData.GetOwnerID1() == session.charid and self.standingData.GetSkillTypeID2To1() is not None
        return True

    def UpdateBenefitsCont(self, ownerID):
        self.benefitsCont.Flush()
        for benefitID in GetStandingBenefitIDs(ownerID):
            texturePath = standingUIConst.ICONS_BY_BENEFITID[benefitID]
            func = self.GetFunctionByBenefitID(benefitID)
            StandingBenefitButton(parent=self.benefitsCont, align=uiconst.TORIGHT, width=ICONSIZE, state=uiconst.UI_NORMAL, texturePath=texturePath, padLeft=4, func=func, benefitID=benefitID, standingData=self.standingData)

    def GetFunctionByActionID(self, actionID):
        if actionID == standingUIConst.ACTION_AGGRESSION:
            return self.OnActionAgression
        if actionID == standingUIConst.ACTION_DERIVEDOTHERFACTIONS:
            return self.OnActionDerivedOtherFactions
        if actionID == standingUIConst.ACTION_DERIVEDAGENTINFACTION:
            return self.OnActionDerivedAgentInFaction
        if actionID == standingUIConst.ACTION_DERIVEDAGENTINCORP:
            return self.OnActionDerivedAgentInCorp
        if actionID == standingUIConst.ACTION_FACTIONALWARFARE:
            return self.OnActionFactionalWarfare
        if actionID == standingUIConst.ACTION_FAILREJECTMISSION:
            return self.OnActionFailRejectMission
        if actionID == standingUIConst.ACTION_SPECIALMISSIONSFACTION:
            return self.OnActionSpecialMissionsFaction
        if actionID == standingUIConst.ACTION_SPECIALMISSIONSCORP:
            return self.OnActionSpecialMissionsCorp
        if actionID == standingUIConst.ACTION_COMPLETEMISSION:
            return self.OnActionCompleteMission
        if actionID == standingUIConst.ACTION_TRAINSKILL:
            return self.OnActionTrainSkill

    def GetFunctionByBenefitID(self, actionID):
        if actionID == standingUIConst.BENEFIT_REPROCESSINGTAX:
            return self.OnBenefitReprocessingTax
        if actionID == standingUIConst.BENEFIT_BROKERSFEE:
            return self.OnBenefitBrokersFee

    def OnActionTrainSkill(self):
        typeID = self.standingData.GetSkillTypeID2To1()
        sm.GetService('info').ShowInfo(typeID)

    def OnActionCompleteMission(self):
        sm.StartService('agents').OpenDialogueWindow(self.standingData.GetOwnerID2())

    def OnActionSpecialMissionsCorp(self):
        self._ShowInfoForThisOwner()

    def OnActionSpecialMissionsFaction(self):
        self._ShowInfoForThisOwner()

    def OnActionFailRejectMission(self):
        sm.StartService('agents').OpenDialogueWindow(self.standingData.GetOwnerID2())

    def OnActionFactionalWarfare(self):
        factionID = self.standingData.GetOwnerID2() if session.warfactionid is None else None
        uicore.cmd.OpenMilitia(factionID=factionID)

    def OnActionDerivedAgentInCorp(self):
        self._ShowInfoForThisOwner(infoConst.TAB_AGENTS)

    def OnActionDerivedAgentInFaction(self):
        self._ShowInfoForThisOwner(infoConst.TAB_MEMBEROFCORPS)

    def OnActionDerivedOtherFactions(self):
        self._ShowInfoForThisOwner(infoConst.TAB_STANDINGS)

    def OnActionAgression(self):
        self._ShowInfoForThisOwner(infoConst.TAB_SYSTEMS)

    def OnBenefitBrokersFee(self):
        self._ShowInfoForThisOwner(infoConst.TAB_SYSTEMS)

    def OnBenefitReprocessingTax(self):
        self._ShowInfoForThisOwner(infoConst.TAB_SYSTEMS)

    def _ShowInfoForThisOwner(self, tabID = None):
        sm.GetService('info').ShowInfo(self.standingData.GetOwner2TypeID(), self.standingData.GetOwnerID2(), selectTabType=tabID)
