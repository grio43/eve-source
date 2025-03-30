#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\contentPieces\epicArcAgentContentPiece.py
from carbon.common.script.sys.serviceConst import ROLE_PROGRAMMER
from carbonui.util.color import Color
from eve.client.script.ui.shared.agencyNew import agencyConst
from eve.client.script.ui.shared.agencyNew.contentPieces.agentContentPiece import AgentContentPiece
from eve.client.script.ui.shared.agencyNew.ui import agencyUIConst
from eve.client.script.ui.shared.epicArcs import epicArcConst
from eve.common.lib import appConst
from localization import GetByLabel
import blue

class EpicArcAgentContentPiece(AgentContentPiece):
    contentType = agencyConst.CONTENTTYPE_EPICARCS

    def __init__(self, epicArc, *args, **kwargs):
        self.epicArc = epicArc
        AgentContentPiece.__init__(self, *args, **kwargs)

    def GetCardSortValue(self):
        return (self.epicArc.GetState(), self.GetJumpsToSelfFromCurrentLocation())

    def GetTitle(self):
        return self.GetEpicArcName()

    def GetExpandedTitle(self):
        return self.GetEpicArcName()

    def GetEpicArcName(self):
        return self.epicArc.GetName()

    def GetEpicArcProgressRatio(self):
        return self.epicArc.GetProgressRatio()

    def GetExpandedSubtitle(self):
        return self.GetEpicArcFlavorLine()

    def GetEpicArcFlavorLine(self):
        return GetByLabel(epicArcConst.FLAVORLINES_BY_EPICARCID[self.epicArc.epicArcID])

    def GetNumMissionsCompletedText(self):
        return GetByLabel('UI/Agency/NumMissionsCompleted', numCompleted=self.epicArc.GetNumMissionsCompleted(), numMissions=self.epicArc.GetNumMissions())

    def GetSubtitle(self):
        return self.GetEpicArcStateText()

    def GetEpicArcStateText(self):
        state = self.epicArc.GetState()
        if state == epicArcConst.ARC_UNAVAILABLE:
            color = Color.RGBtoHex(*agencyUIConst.COLOR_UNAVAILABLE_HILIGHT)
            return '<color=%s>' % color + GetByLabel('UI/Menusvc/MenuHints/Unavailable') + '</color>'
        if state == epicArcConst.ARC_AVAILABLE:
            color = Color.RGBtoHex(*agencyUIConst.COLOR_AVAILABLE_HILIGHT)
            return '<color=%s>' % color + GetByLabel('UI/Agency/EpicArcAvailable') + '</color>'
        if state == epicArcConst.ARC_COMPLETE:
            completeTime = self.epicArc.GetCompleteTime()
            return GetByLabel('UI/Agency/EpicArcComplete', completeTime=completeTime)

    def IsAvailable(self):
        return self.epicArc.IsStandingSufficientToStart()

    def GetStanding(self):
        return self.epicArc.GetRequiredStanding()

    def GetBlurbText(self):
        ownerName = cfg.eveowners.Get(self.ownerID).ownerName
        return GetByLabel('UI/Agency/Blurbs/EpicArcAgent', ownerName=ownerName)

    def GetRewardTypes(self):
        return [agencyConst.REWARDTYPE_ISK3, agencyConst.REWARDTYPE_LOOT]

    def GetBGVideoPath(self):
        factionID = self.GetFactionID()
        if factionID == appConst.factionMinmatarRepublic:
            return 'res:/Video/Agency/epicArcMinmatar.webm'
        if factionID == appConst.factionGallenteFederation:
            return 'res:/Video/Agency/epicArcGallente.webm'
        if factionID == appConst.factionCaldariState:
            return 'res:/Video/Agency/epicArcCaldari.webm'
        if factionID == appConst.factionAmarrEmpire:
            return 'res:/Video/Agency/epicArcAmarr.webm'
        if factionID == appConst.factionSistersOfEVE:
            return 'res:/Video/Agency/epicArcSOE.webm'
        if factionID == appConst.factionGuristasPirates:
            return 'res:/Video/Agency/epicArcGuristas.webm'
        if factionID == appConst.factionAngelCartel:
            return 'res:/Video/Agency/epicArcAngels.webm'

    def GetIconTexturePath(self):
        factionID = self.GetFactionID()
        if factionID == appConst.factionMinmatarRepublic:
            return 'res:/UI/Texture/Classes/Agency/Icons/ContentTypes/MinmatarEpic.png'
        if factionID == appConst.factionGallenteFederation:
            return 'res:/UI/Texture/Classes/Agency/Icons/ContentTypes/GallenteEpic.png'
        if factionID == appConst.factionCaldariState:
            return 'res:/UI/Texture/Classes/Agency/Icons/ContentTypes/CaldariEpic.png'
        if factionID == appConst.factionAmarrEmpire:
            return 'res:/UI/Texture/Classes/Agency/Icons/ContentTypes/AmarrEpic.png'
        if factionID == appConst.factionSistersOfEVE:
            return 'res:/UI/Texture/Classes/Agency/Icons/ContentTypes/SOEEpic.png'
        if factionID == appConst.factionGuristasPirates:
            return 'res:/UI/Texture/Classes/Agency/Icons/ContentTypes/GuiristasEpic.png'
        if factionID == appConst.factionAngelCartel:
            return 'res:/UI/Texture/Classes/Agency/Icons/ContentTypes/AngelsEpic.png'

    def GetSubSolarSystemPosition(self):
        agentEntryPoint = sm.GetService('agents').GetAgentMoniker(self.itemID).GetEntryPoint()
        return agentEntryPoint or super(EpicArcAgentContentPiece, self).GetSubSolarSystemPosition()

    def GetFactionID(self):
        return self.epicArc.GetFactionID()

    def GetCorpID(self):
        return self.agent.corporationID

    def GetCardID(self):
        return (self.contentType, self.epicArc.epicArcID)

    def GetMenu(self):
        m = AgentContentPiece.GetMenu(self)
        if session.role & ROLE_PROGRAMMER:
            m.insert(0, ('Epic arc id: %s' % self.epicArc.epicArcID, blue.pyos.SetClipboardData, (str(self.epicArc.epicArcID),)))
        return m

    def GetChatChannelID(self):
        return None

    def IsInCurrentStation(self):
        if session.stationid is None:
            return False
        if self.IsActiveAndAcceptedMission():
            return super(EpicArcAgentContentPiece, self).IsInCurrentStation()
        agent = self.epicArc.GetActiveAgent()
        if agent:
            return session.stationid == agent.stationID
        return False

    def GetActiveAgentContentPiece(self):
        agent = self.epicArc.GetActiveAgent()
        return AgentContentPiece(solarSystemID=agent.solarsystemID, itemID=agent.agentID, locationID=agent.stationID, typeID=agent.agentTypeID, ownerID=agent.corporationID, agent=agent)
