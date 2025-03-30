#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\charsheet\standingsPanel\standingsAssociationsTooltip.py
import localization
from carbonui import uiconst
from eve.client.script.ui.control import tooltips
from eve.client.script.ui.control.eveIcon import OwnerIconAndLabel
from eve.client.script.ui.tooltips.tooltipsWrappers import TooltipBaseWrapper

class StandingsAssociationTooltip(TooltipBaseWrapper):

    def __init__(self, agent_id = None):
        super(TooltipBaseWrapper, self).__init__()
        self.agent_id = agent_id

    def CreateTooltip(self, parent, owner, idx):
        self.tooltipPanel = tooltips.TooltipPanel(parent=parent, owner=owner, idx=idx)
        self.tooltipPanel.state = uiconst.UI_NORMAL
        self.tooltipPanel.LoadGeneric2ColumnTemplate()
        factionID, corpID = self.GetAssociations(self.agent_id)
        self.tooltipPanel.AddSpacer(0, 4, 2)
        self.tooltipPanel.AddLabelMedium(text=localization.GetByLabel('UI/Common/Faction'), colSpan=2, bold=True)
        self.CreateAssociationRow(ownerID=factionID)
        self.tooltipPanel.AddSpacer(0, 4, 2)
        self.tooltipPanel.AddLabelMedium(text=localization.GetByLabel('UI/Agents/Dialogue/Corporation'), colSpan=2, bold=True)
        self.CreateAssociationRow(corpID)
        return self.tooltipPanel

    def CreateAssociationRow(self, ownerID):
        iconAndLabel = OwnerIconAndLabel(height=32, align=uiconst.TOPLEFT, iconSize=32, ownerID=ownerID, left=5, iconAlign=uiconst.TOLEFT)
        self.tooltipPanel.AddCell(iconAndLabel, colSpan=2)

    def GetAssociations(self, agentID):
        agent = sm.GetService('agents').GetAgentByID(agentID)
        return (agent.factionID, agent.corporationID)
