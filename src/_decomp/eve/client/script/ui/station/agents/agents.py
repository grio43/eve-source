#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\station\agents\agents.py
import types
import weakref
from collections import defaultdict
import blue
from appConst import factionByRace
import telemetry
import triui
import carbonui.const as uiconst
import clonegrade
import evetypes
import localization
import log
import uthread
from carbon.client.script.environment.AudioUtil import PlaySound
from carbon.common.script.sys.service import Service
from carbon.common.script.sys.serviceConst import ROLE_SERVICE, SERVICE_RUNNING
from carbon.common.script.util.format import FmtTimeInterval, FmtDate
from carbonui.uicore import uicore
from characterdata.schools import get_school
from eve.client.script.ui.shared.cloneGrade import ORIGIN_AGENTS
from eve.client.script.ui.station.agents.agentDialogueWindow import AgentDialogueWindow
from eve.client.script.ui.station.agents.missionDetailsWindow import MissionDetailsWindow
from eve.client.script.ui.util import uix
from eve.client.script.ui.util.utilWindows import NamePopup
from eve.common.lib import appConst
from eve.common.script.net import eveMoniker
from eve.common.script.sys.idCheckers import IsStation, IsSolarSystem, IsStructure
from eve.common.script.util.eveFormat import FmtISK
from eveagent.data import get_agents_in_space
from evemissions.client.const import CAREER_PATH_BY_DIVISION
from evemissions.client.ui.missiongiver import MissionGiver
from evemissions.client.ui.utils import get_agent_conversation_window_id, get_mission_details_window_id
from globalConfig import GetNewMissionGiverEnabled
from jobboard.client import open_mission
from jobboard.client.feature_flag import is_job_board_available, are_missions_in_job_board_available
import launchdarkly
from npcs.npccorporations import get_corporation_faction_id
SERVICETYPE_RESEARCH = 'research'
SERVICETYPE_LOCATE = 'locate'
SERVICETYPE_MISSION = 'mission'
SERVICETYPE_OFFER = 'offer'
HERALDRY_ENABLED_KEY = 'are_heraldry_agents_enabled'
HERALDRY_ENABLED_DEFAULT = True
AGENTS_WITH_NEW_UI = [appConst.agentTypeHeraldry]

class Agents(Service):
    __exportedcalls__ = {'OpenDialogueWindow': [],
     'RemoteNamePopup': [ROLE_SERVICE],
     'GetQuantity': [ROLE_SERVICE],
     'PopupSelect': [ROLE_SERVICE],
     'YesNo': [ROLE_SERVICE],
     'MessageBox': [ROLE_SERVICE],
     'SingleChoiceBox': [ROLE_SERVICE],
     'CheckCargoCapacity': [ROLE_SERVICE],
     'GetAgentByID': [],
     'GetAgentsByID': [],
     'GetAgentsByStationID': [],
     'GetAgentsByCorpID': [],
     'GetAgentsByFactionID': [],
     'IsCareerAgentStation': [],
     'IsCareerAgentSystem': [],
     'IsAgent': [],
     'PopupMission': [ROLE_SERVICE],
     'RemoveOfferFromJournal': [],
     'ShowMissionObjectives': [ROLE_SERVICE],
     'PopupDungeonShipRestrictionList': [ROLE_SERVICE]}
    __guid__ = 'svc.agents'
    __servicename__ = 'agents'
    __displayname__ = 'Agent Service'
    __dependencies__ = ['map']
    __notifyevents__ = ['OnAgentMissionChange',
     'OnSessionReset',
     'OnInteractWith',
     'ProcessUIRefresh',
     'OnDatacoreBought',
     'OnAgentSlashCommandExecuted',
     'OnGlobalConfigChanged']
    __startupdependencies__ = ['faction']

    def __GetAllAgents(self):
        if self.allAgents is None:
            agentsInSpace = get_agents_in_space()
            agents = sm.RemoteSvc('agentMgr').GetAgents().Clone()
            agents.AddField('factionID', None)
            agents.AddField('solarsystemID', None)
            for agent in agents:
                if agent.stationID:
                    uiSvc = sm.GetService('ui')
                    stationInfo = uiSvc.GetStationStaticInfo(agent.stationID)
                    agent.corporationID = agent.corporationID or uiSvc.GetStationOwner(agent.stationID)
                    agent.solarsystemID = stationInfo.solarSystemID
                elif agent.agentID in agentsInSpace:
                    info = agentsInSpace.get(agent.agentID)
                    agent.solarsystemID = info.solarSystemID
                else:
                    agent.solarsystemID = None
                agent.factionID = get_corporation_faction_id(agent.corporationID)

            self.allAgentsByID = agents.Index('agentID')
            self.allAgentsByStationID = agents.Filter('stationID')
            self.allAgentsBySolarSystemID = agents.Filter('solarsystemID')
            self.allAgentsByCorpID = agents.Filter('corporationID')
            self.allAgentsByFactionID = agents.Filter('factionID')
            self.allAgentsByType = agents.Filter('agentTypeID')
            self.allAgents = agents

    def GetAgentByID(self, agentID):
        self.__GetAllAgents()
        if agentID in self.allAgentsByID:
            return self.allAgentsByID[agentID]

    def GetAgentIDByNameInStation(self, agentName, stationID):
        agentsInStation = self.GetAgentsByStationID()[stationID]
        for agent in agentsInStation:
            if cfg.eveowners.Get(agent.agentID).name == agentName:
                return agent.agentID

    def GetAgentsByID(self):
        self.__GetAllAgents()
        return self.allAgentsByID

    def GetAgentsByStationID(self):
        self.__GetAllAgents()
        return self.allAgentsByStationID

    def GetAgentsBySolarSystemID(self):
        self.__GetAllAgents()
        return self.allAgentsBySolarSystemID

    def GetAgentsByCorpID(self, corpID):
        self.__GetAllAgents()
        return self.allAgentsByCorpID[corpID]

    def GetAgentsByFactionID(self, factionID):
        self.__GetAllAgents()
        return self.allAgentsByFactionID[factionID]

    def GetAgentsByType(self, agentTypeID):
        self.__GetAllAgents()
        return self.allAgentsByType[agentTypeID]

    def GetAllAgents(self):
        self.__GetAllAgents()
        return self.allAgents

    def _GetCareerPathID(self, agentID):
        agentInfo = self.GetAgentByID(agentID)
        if agentInfo:
            divisionID = agentInfo.divisionID
            if divisionID in CAREER_PATH_BY_DIVISION:
                return CAREER_PATH_BY_DIVISION[divisionID]

    def IsCareerAgent(self, agentID):
        agentInfo = self.GetAgentByID(agentID)
        if agentInfo:
            agentTypeID = agentInfo.agentTypeID
            return self.IsCareerAgentType(agentTypeID)
        return False

    def GetAgentLocation(self, agentID):
        agentInfo = self.GetAgentByID(agentID)
        if agentInfo:
            return agentInfo.stationID or agentInfo.solarsystemID

    def GetAgentConversationWindowName(self, agentID):
        careerPathID = self._GetCareerPathID(agentID)
        return get_agent_conversation_window_id(careerPathID, agentID)

    def GetMissionJournalWindowName(self, agentID):
        careerPathID = self._GetCareerPathID(agentID)
        return get_mission_details_window_id(careerPathID, agentID)

    def IsCareerAgentStation(self, stationID):
        if stationID is None or not IsStation(stationID):
            return False
        agentsByStation = self.GetAgentsByStationID()
        if stationID in agentsByStation:
            for agent in agentsByStation[stationID]:
                if agent.agentTypeID == appConst.agentTypeCareerAgent:
                    return True

        return False

    def IsCareerAgentSystem(self, solarSystemID):
        if solarSystemID is None or not IsSolarSystem(solarSystemID):
            return False
        agentsBySolarSystem = self.GetAgentsBySolarSystemID()
        if solarSystemID in agentsBySolarSystem:
            for agent in agentsBySolarSystem[solarSystemID]:
                if agent.agentTypeID == appConst.agentTypeCareerAgent:
                    return True

        return False

    def IsAgent(self, agentID):
        self.__GetAllAgents()
        return agentID in self.allAgentsByID

    def CheckPrimeCompletedCareerAgentIDs(self, agentIDs):
        allPresent = all([ agentID in self._careerAgentsCompletedByID for agentID in agentIDs ])
        if not allPresent:
            careerAgentsAvailableByID = sm.RemoteSvc('agentMgr').GetCompletedCareerAgentIDs(agentIDs)
            self._careerAgentsCompletedByID.update(careerAgentsAvailableByID)

    def IsCareerAgentCompleted(self, agentID):
        if agentID not in self._careerAgentsCompletedByID:
            self.CheckPrimeCompletedCareerAgentIDs([agentID])
        return self._careerAgentsCompletedByID[agentID]

    def IsCareerAgentType(self, agentTypeID):
        return agentTypeID == appConst.agentTypeCareerAgent

    def GetClosestAgent(self, agentTypeID = None, divisionID = None, factionID = None, careerPathID = None, onlyIncomplete = False):
        factionID = self._GetMyFactionID() if factionID is None else factionID
        agentsBySolarSystemID = defaultdict(list)
        agents = self.GetAgentsByType(agentTypeID) if agentTypeID else self.GetAllAgents()
        for agent in agents:
            if factionID == agent.factionID:
                if divisionID and divisionID != agent.divisionID:
                    continue
                if careerPathID and careerPathID != CAREER_PATH_BY_DIVISION.get(agent.divisionID, None):
                    continue
                if onlyIncomplete and self.IsCareerAgentType(agentTypeID) and self.IsCareerAgentCompleted(agent.agentID):
                    continue
                agentsBySolarSystemID[agent.solarsystemID].append(agent.agentID)

        if not agentsBySolarSystemID:
            return
        closestSolarSystemID = self._GetClosestSystem(agentsBySolarSystemID.keys())
        closestAgents = agentsBySolarSystemID[closestSolarSystemID]
        if len(closestAgents):
            return closestAgents[0]

    def GetMySuggestedCareerAgents(self):
        agents = self._GetMyFactionAgents()
        return self._GetNearestSetOfAgents(agents)

    def GetMySuggestetCareerAgentStation(self):
        agents = self.GetMySuggestedCareerAgents()
        return agents[0].stationID

    def IsCareerAgentPathCompleted(self, agentDivisionID):
        agents = self.GetMySuggestedCareerAgents()
        for agent in agents:
            if agent.divisionID == agentDivisionID:
                return self.IsCareerAgentCompleted(agent.agentID)

    def _GetMyFactionAgents(self):
        allCareerAgents = self.GetAgentsByType(appConst.agentTypeCareerAgent)
        myFactionID = self._GetMyFactionID()
        return [ agent for agent in allCareerAgents if agent.factionID == myFactionID ]

    def _GetMyFactionID(self):
        myFactionID = factionByRace[session.raceID]
        return myFactionID

    def _GetNearestSetOfAgents(self, myFactionAgents):
        agentsBySolarSystemID = defaultdict(list)
        for agent in myFactionAgents:
            agentsBySolarSystemID[agent.solarsystemID].append(agent)

        solarSystemID = self._GetClosestSystem(agentsBySolarSystemID.keys())
        return agentsBySolarSystemID[solarSystemID]

    def _GetClosestSystem(self, solarSystemIDs):
        sortedList = sorted(solarSystemIDs, key=self._GetNumJumpsToSystem)
        return sortedList[0]

    def _GetNumJumpsToSystem(self, solarSystemID):
        return sm.GetService('clientPathfinderService').GetJumpCountFromCurrent(solarSystemID)

    def GetAgentTimers(self, agentIDs):
        timers = {}
        characterID = session.charid
        if characterID:
            for agentID in agentIDs:
                agent = self.GetAgentMoniker(agentID)
                timers[agentID] = agent.GetReplayTimestamp(characterID)

        return timers

    def GetAgentMoniker(self, agentID):
        if agentID not in self.agentMonikers:
            if getattr(self, 'allAgentsByID', False) and agentID in self.allAgentsByID and self.allAgentsByID[agentID].stationID:
                self.agentMonikers[agentID] = eveMoniker.GetAgent(agentID, self.allAgentsByID[agentID].stationID)
            else:
                self.agentMonikers[agentID] = eveMoniker.GetAgent(agentID)
        self.lastMonikerAccess = blue.os.GetWallclockTime()
        return self.agentMonikers[agentID]

    def _ClearAgentMonikersThread(self):
        while self.state == SERVICE_RUNNING:
            blue.pyos.synchro.SleepWallclock(300000)
            if blue.os.GetWallclockTime() > self.lastMonikerAccess + 30 * appConst.MIN:
                self.agentMonikers.clear()

    def Run(self, memStream = None):
        self.LogInfo('Agent Service')
        self.allAgents = None
        self.careerAgents = None
        self.divisions = None
        self.agentMonikers = {}
        self.agentArgs = {}
        self.missionArgs = {}
        self.lastMonikerAccess = blue.os.GetWallclockTime()
        self._careerAgentsCompletedByID = {}
        self.processing = 0
        self.isExecutingAgentAction = False
        self.isUpdatingJournalWindow = False
        self.agentDialogWindows = weakref.WeakValueDictionary()
        self.missionDetailsWindows = weakref.WeakValueDictionary()
        self.agentSolarSystems = {}
        self._disabledMissions = None
        self.isHeraldryAvailable = HERALDRY_ENABLED_DEFAULT
        launchdarkly.get_client().notify_flag(HERALDRY_ENABLED_KEY, HERALDRY_ENABLED_DEFAULT, self._OnFlagChanged)
        self._UpdateMissionGiverClass()
        uthread.worker('agents::ClearMonikers', self._ClearAgentMonikersThread)

    @property
    def disabledMissions(self):
        if self._disabledMissions is None:
            self._disabledMissions = sm.RemoteSvc('agentMgr').GetDisabledMissions()
        return self._disabledMissions

    def IsMissionDisabled(self, missionID):
        return missionID in self.disabledMissions

    def _OnFlagChanged(self, launchDarklyClient, *args, **kwargs):
        previousValue = self.isHeraldryAvailable
        self.isHeraldryAvailable = launchDarklyClient.get_bool_variation(feature_key=HERALDRY_ENABLED_KEY, fallback=HERALDRY_ENABLED_DEFAULT)
        if self.isHeraldryAvailable != previousValue:
            sm.ScatterEvent('OnHeraldryAvailabilityChanged')

    def IsHeraldryAvailable(self):
        return self.isHeraldryAvailable

    def _UpdateMissionGiverClass(self):
        isNewMissionGiverEnabled = GetNewMissionGiverEnabled(sm.GetService('machoNet'))
        self.careerAgentWindowClass = MissionGiver if isNewMissionGiverEnabled else AgentDialogueWindow

    def OnGlobalConfigChanged(self, *args, **kwargs):
        self._UpdateMissionGiverClass()
        self.ReloadAgentDialogWindows()

    def CheckCargoCapacity(self, mandatoryCargoUnits, extraFlagsToCheck):
        activeShipID = session.shipid
        if activeShipID is None:
            capacity, used = (0, 0)
        else:
            capacity, used = sm.GetService('invCache').GetInventoryFromId(activeShipID).GetCapacity(appConst.flagCargo)
            for flag in extraFlagsToCheck:
                flagCapacity, flagUsed = sm.GetService('invCache').GetInventoryFromId(activeShipID).GetCapacity(flag)
                capacity += flagCapacity
                used += flagUsed

        if session.stationid is None and capacity - (used + mandatoryCargoUnits) < 0:
            rejectMessage = localization.GetByLabel('UI/Agents/StandardMissionCargoCapWarning', cargoUnits=mandatoryCargoUnits)
            self.MessageBox(localization.GetByLabel('UI/Agents/CannotAcceptMission'), rejectMessage)
            return ('mission.offeredinsufficientcargospace', rejectMessage)

    def YesNo(self, title, body, agentID = None, contentID = None, suppressID = None):
        if isinstance(title, basestring):
            titleText = title
        else:
            titleText = self.ProcessMessage((title, contentID), agentID)
        if isinstance(body, basestring):
            bodyText = body
        else:
            bodyText = self.ProcessMessage((body, contentID), agentID)
        options = {'text': bodyText,
         'title': titleText,
         'buttons': uiconst.YESNO,
         'icon': uiconst.QUESTION}
        ret = self.ShowMessageWindow(options, suppressID)
        return ret == uiconst.ID_YES

    def MessageBox(self, title, body, agentID = None, contentID = None, suppressID = None):
        if isinstance(title, basestring):
            titleText = title
        else:
            titleText = self.ProcessMessage((title, contentID), agentID)
        if isinstance(body, basestring):
            bodyText = body
        else:
            bodyText = self.ProcessMessage((body, contentID), agentID)
        options = {'text': bodyText,
         'title': titleText,
         'buttons': triui.OK,
         'icon': triui.INFO}
        self.ShowMessageWindow(options, suppressID)

    def ShowMessageWindow(self, options, suppressID = None):
        if suppressID:
            supp = settings.user.suppress.Get('suppress.' + suppressID, None)
            if supp is not None:
                return supp
            options['suppText'] = localization.GetByLabel('UI/Common/SuppressionShowMessage')
        ret, block = sm.StartService('gameui').MessageBox(**options)
        if suppressID and block and ret not in [uiconst.ID_NO]:
            settings.user.suppress.Set('suppress.' + suppressID, ret)
        return ret

    def SingleChoiceBox(self, title, body, choices, agentID = None, contentID = None, suppressID = None):
        if isinstance(title, basestring):
            titleText = title
        else:
            titleText = self.ProcessMessage((title, contentID), agentID)
        if isinstance(body, basestring):
            bodyText = body
        else:
            bodyText = self.ProcessMessage((body, contentID), agentID)
        choicesText = []
        for choice in choices:
            if type(choice) is tuple:
                choicesText.append(localization.GetByLabel(choice[0], **choice[1]))
            else:
                choicesText.append(choice)

        options = {'text': bodyText,
         'title': titleText,
         'icon': triui.QUESTION,
         'buttons': uiconst.OKCANCEL,
         'radioOptions': choicesText}
        if suppressID:
            supp = settings.user.suppress.Get('suppress.' + suppressID, None)
            if supp is not None:
                return supp
            options['suppText'] = localization.GetByLabel('UI/Common/SuppressionShowMessageRemember')
        ret, block = sm.StartService('gameui').RadioButtonMessageBox(**options)
        if suppressID and block:
            settings.user.suppress.Set('suppress.' + suppressID, ret)
        return (ret[0] == uiconst.ID_OK, ret[1])

    def GetQuantity(self, **keywords):
        for k in ('caption', 'label'):
            if k in keywords and not isinstance(keywords[k], basestring):
                keywords[k] = self.ProcessMessage((keywords[k], None), keywords.get('agentID', None))

        ret = uix.QtyPopup(**keywords)
        if not ret:
            return
        return ret.get('qty', None)

    def RemoteNamePopup(self, caption, label, agentID):
        if isinstance(caption, basestring):
            captionText = caption
        else:
            captionText = self.ProcessMessage((caption, None), agentID)
        if isinstance(label, basestring):
            labelText = label
        else:
            labelText = self.ProcessMessage((label, None), agentID)
        return NamePopup(captionText, labelText)

    def PopupSelect(self, title, explanation, agentID, **keywords):
        if isinstance(title, basestring):
            titleText = title
        else:
            titleText = self.ProcessMessage((title, None), agentID)
        if isinstance(explanation, basestring):
            explanationText = explanation
        else:
            explanationText = self.ProcessMessage((explanation, None), agentID)
        if 'typeIDs' in keywords:
            displayList = []
            for typeID in keywords['typeIDs']:
                displayList.append([evetypes.GetName(typeID), typeID, typeID])

            ret = uix.ListWnd(displayList, 'type', titleText, explanationText, 0, 300)
        else:
            return
        if ret:
            return ret[2]
        else:
            return

    def Stop(self, memStream = None):
        self.LogInfo('Stopping Agent Services')
        Service.Stop(self)

    def GetAuraAgentID(self):
        charinfo = sm.RemoteSvc('charMgr').GetPublicInfo(session.charid)
        schoolinfo = get_school(charinfo.schoolID)
        corpinfo = sm.GetService('corp').GetCorporation(schoolinfo.corporationID)
        agents = self.allAgentsByStationID[corpinfo.stationID]
        for agent in agents:
            if agent.agentTypeID == appConst.agentTypeAura:
                return agent.agentID

    def OnInteractWith(self, agentID):
        self.OpenDialogueWindow(agentID)

    def _GetWindowClass(self, agentID, agentTypeID):
        if not self.IsCareerAgent(agentID) and agentTypeID not in AGENTS_WITH_NEW_UI:
            return AgentDialogueWindow
        return self.careerAgentWindowClass

    def OnAgentSlashCommandExecuted(self, agentID):
        windowName = self.GetAgentConversationWindowName(agentID)
        agentInfo = self.GetAgentByID(agentID)
        windowClass = self._GetWindowClass(agentID, agentInfo.agentTypeID)
        window = windowClass.GetIfOpen(windowID=windowName)
        if window:
            window.Close()
            self.OpenDialogueWindow(agentID)

    def IsCheatingWithAgent(self, agentID):
        return self.GetAgentMoniker(agentID).IsCheatingWithAgent()

    def ShouldAlwaysAllowReplay(self, agentID):
        return self.GetAgentMoniker(agentID).ShouldAlwaysAllowReplay()

    @telemetry.ZONE_METHOD
    def OpenDialogueWindow(self, agentID, maximize = True):
        agentInfo = self.GetAgentByID(agentID)
        if agentInfo.level >= clonegrade.RESTRICTED_AGENT_LEVEL:
            if sm.GetService('cloneGradeSvc').GetCloneGrade() == clonegrade.CLONE_STATE_ALPHA:
                sm.GetService('cmd').OpenCloneUpgradeWindow(ORIGIN_AGENTS, 'toohighagentlevel')
                return
        wnd = None
        if agentID in self.agentDialogWindows:
            wnd = self.agentDialogWindows[agentID]
            if wnd.destroyed:
                wnd = None
            if wnd is not None and not wnd.destroyed:
                if maximize:
                    wnd.Maximize()
        if wnd is None:
            agentInfo = self.GetAgentByID(agentID)
            if agentInfo and agentInfo.agentTypeID == appConst.agentTypeAura:
                uicore.Message('NewNPEClickOnTutorialLinkDisabled', {})
                return
            windowName = self.GetAgentConversationWindowName(agentID)
            windowClass = self._GetWindowClass(agentID, agentInfo.agentTypeID)
            wnd = windowClass.Open(windowID=windowName, agentID=agentID, npcCharacterID=agentID)
            self.agentDialogWindows[agentID] = wnd
        wnd.InteractWithAgent()
        if not wnd.destroyed and wnd.stacked:
            if not isinstance(wnd, MissionGiver):
                wnd.RefreshBrowsers()

    def ReloadAgentDialogWindows(self):
        windowStates = {agentID:window.state for agentID, window in self.agentDialogWindows.iteritems()}
        for agentID in windowStates.iterkeys():
            window = self.agentDialogWindows.get(agentID, None)
            if window or not window.destroyed:
                window.Close()

        for agentID, state in windowStates.iteritems():
            self.OpenDialogueWindow(agentID)
            self.agentDialogWindows[agentID].SetState(state)

    def ProcessUIRefresh(self):
        if not getattr(self, 'divisions', None):
            return
        for row in self.divisions.values():
            row.divisionName = localization.GetByMessageID(row.divisionNameID)
            row.leaderType = localization.GetByMessageID(row.leaderTypeID)

        self.ReloadAgentDialogWindows()

    def GetAgentArgs(self, agentID):
        agentInfo = self.GetAgentByID(agentID)
        if not agentInfo:
            return {}
        agentArgs = {'agentID': agentInfo.agentID}
        agentArgs['agentCorpID'] = agentInfo.corporationID
        agentArgs['agentFactionID'] = agentInfo.factionID
        agentArgs['agentSolarSystemID'] = agentInfo.solarsystemID
        agentArgs['agentLocation'] = agentInfo.solarsystemID
        if getattr(agentInfo, 'stationID', None):
            agentArgs['agentStationID'] = agentInfo.stationID
            agentArgs['agentLocation'] = agentInfo.stationID
        agentArgs['agentConstellationID'] = self.map.GetConstellationForSolarSystem(agentInfo.solarsystemID)
        agentArgs['agentRegionID'] = self.map.GetRegionForSolarSystem(agentInfo.solarsystemID)
        return agentArgs

    def PrimeMessageArguments(self, agentID, contentID, missionKeywords = None):
        if contentID is not None:
            if agentID is None:
                raise RuntimeError('Agent message received a content ID without an agent ID. Something is wrong!')
            if (agentID, contentID) not in self.missionArgs:
                if not missionKeywords:
                    missionKeywords = self.GetAgentMoniker(agentID).GetMissionKeywords(contentID)
                self.missionArgs[agentID, contentID] = missionKeywords
        if agentID is not None:
            if agentID not in self.agentArgs:
                self.agentArgs[agentID] = self.GetAgentArgs(agentID)

    def ProcessMessage(self, msg, agentID = None):
        if isinstance(msg, types.TupleType):
            msgInfo, contentID = msg
            if isinstance(msgInfo, basestring):
                return msgInfo
            msgArgs = {}
            self.PrimeMessageArguments(agentID, contentID)
            if contentID is not None:
                msgArgs.update(self.missionArgs[agentID, contentID])
            if agentID is not None:
                msgArgs.update(self.agentArgs[agentID])
            if isinstance(msgInfo, tuple):
                for k in msgInfo[1]:
                    if k in ('missionCompletionText', 'missionOfferText', 'missionBriefingText', 'declineMessageText', 'locationString') or isinstance(msgInfo[1][k], tuple):
                        msgInfo[1][k] = self.ProcessMessage((msgInfo[1][k], contentID), agentID)

                msgArgs.update(msgInfo[1])
                try:
                    return localization.GetByLabel(msgInfo[0], **msgArgs)
                except:
                    log.LogException('Error parsing message with label %s' % msgInfo[0])
                    return localization.GetByLabel('UI/Agents/Dialogue/StandardMission/CorruptBriefing')

            else:
                try:
                    return localization.GetByMessageID(msgInfo, **msgArgs)
                except:
                    log.LogException('Error parsing agent message with ID %s' % msgInfo)
                    return localization.GetByLabel('UI/Agents/Dialogue/StandardMission/CorruptBriefing') + '<br>----------------------<br>' + localization._GetRawByMessageID(msgInfo)

        else:
            return msg

    def DoAction(self, agentID, actionID = None):
        if self.isExecutingAgentAction:
            return
        self.isExecutingAgentAction = True
        try:
            if agentID in self.agentDialogWindows:
                window = self.agentDialogWindows[agentID]
                window.InteractWithAgent(actionID)
        finally:
            self.isExecutingAgentAction = False

    def OnAgentMissionChange(self, actionID, agentID):
        if agentID in self.agentDialogWindows:
            agentDialogueWindow = self.agentDialogWindows[agentID]
            if actionID in (appConst.agentMissionOfferRemoved, appConst.agentMissionReset, appConst.agentTalkToMissionCompleted):
                if not agentDialogueWindow.destroyed:
                    agentDialogueWindow.CloseByUser()
                del self.agentDialogWindows[agentID]
        if actionID in (appConst.agentMissionOffered, appConst.agentMissionReset):
            keys = [ x for x in self.missionArgs.keys() if x[0] == agentID ]
            for key in keys:
                del self.missionArgs[key]

        wnd = self.agentDialogWindows.get(agentID, None)
        if isinstance(wnd, MissionGiver):
            if actionID == appConst.agentMissionAccepted:
                PlaySound('career_agent_window_accept_mission_play')
            elif actionID == appConst.agentMissionCompleted:
                PlaySound('career_agent_window_mission_complete_play')
        elif actionID == appConst.agentMissionCompleted:
            PlaySound('ui_notify_mission_rewards_play')
        if actionID == appConst.agentMissionCompleted:
            if agentID in self._careerAgentsCompletedByID:
                self._careerAgentsCompletedByID.pop(agentID)

    def OnDatacoreBought(self, characterID, agentID, balance):
        self.LogInfo('OnDatacoreBought', characterID, agentID, balance)
        sm.ScatterEvent('OnAgentMissionChange', appConst.agentMissionResearchUpdatePPD, agentID)
        sm.ScatterEvent('OnAccountChange', 'cash', characterID, balance)

    def OnSessionReset(self):
        self.careerAgents = None
        self.agentDialogWindows.clear()

    def PopupMission(self, agentID, charID = None, contentID = None):
        if is_job_board_available() and are_missions_in_job_board_available():
            self._PopupMissionInJobBoard(agentID, charID)
        else:
            self._PopupMissionJournalWindow(agentID, charID, contentID)

    def _PopupMissionInJobBoard(self, agentID, charID):
        open_mission(agentID, charID)

    def _PopupMissionJournalWindow(self, agentID, charID = None, contentID = None):
        wnd = self.missionDetailsWindows.get(agentID, None)
        if not wnd or wnd.destroyed:
            windowName = self.GetMissionJournalWindowName(agentID)
            wnd = MissionDetailsWindow.Open(windowID=windowName, caption=localization.GetByLabel('UI/Agents/MissionJournalWithAgent', agentID=agentID))
            self.missionDetailsWindows[agentID] = wnd
        uthread.new(wnd.ReconstructLayout, agentID, charID, contentID)

    def GetMissionInfo(self, agentID, charID = None, contentID = None):
        return self.GetAgentMoniker(agentID).GetMissionJournalInfo(charID, contentID)

    def GetMissionBriefingInfo(self, agentID):
        briefingInformation = self.GetAgentMoniker(agentID).GetMissionBriefingInfo()
        if briefingInformation and briefingInformation[appConst.agentMissionBriefingMissionID]:
            self.missionArgs[agentID, briefingInformation[appConst.agentMissionBriefingMissionID]] = briefingInformation[appConst.agentMissionBriefingKeywords]
        return briefingInformation

    def CheckCourierCargo(self, agentID, stationID, contentID):
        missionInfo = self.GetAgentMoniker(agentID).GetMissionJournalInfo()
        if missionInfo:
            for objType, objData in missionInfo['objectives']['objectives']:
                if objType == 'transport':
                    pickupOwnerID, pickupLocation, dropoffOwnerID, dropoffLocation, cargo = objData
                    return cargo['hasCargo']

        return False

    def PopupDungeonShipRestrictionList(self, agentID, charID = None, dungeonID = None):
        from evedungeons.client.ship_restrictions_window import ShipRestrictionsWindow
        ShipRestrictionsWindow.Open(dungeon_id=dungeonID)

    def RemoveOfferFromJournal(self, agentID):
        self.GetAgentMoniker(agentID).RemoveOfferFromJournal()

    def ShowMissionObjectives(self, agentID, contentID = None):
        if agentID not in self.agentDialogWindows:
            self.OpenDialogueWindow(agentID)
        elif not self.isUpdatingJournalWindow:
            self.isUpdatingJournalWindow = True
            try:
                agentDialogueWindow = self.agentDialogWindows[agentID]
                agentDialogueWindow.ShowMissionObjectives(contentID)
            finally:
                self.isUpdatingJournalWindow = False

    def GetSolarSystemOfAgent(self, agentID):
        if agentID not in self.agentSolarSystems:
            self.agentSolarSystems[agentID] = sm.RemoteSvc('agentMgr').GetSolarSystemOfAgent(agentID)
        return self.agentSolarSystems[agentID]

    def ProcessAgentInfoKeyVal(self, data):
        infoFunc = {SERVICETYPE_RESEARCH: self._ProcessResearchServiceInfo,
         SERVICETYPE_LOCATE: self._ProcessLocateServiceInfo,
         SERVICETYPE_MISSION: self._ProcessMissionServiceInfo}.get(data.agentServiceType, None)
        if infoFunc:
            return infoFunc(data)
        else:
            return []

    def _ProcessResearchServiceInfo(self, data):
        header = localization.GetByLabel('UI/Agents/Research/ResearchServices', session.languageID)
        skillList = []
        for skillTypeID, skillInfo in data.skills:
            skillList.append(localization.GetByLabel('UI/Agents/Research/SkillListing', session.languageID, skillID=skillTypeID, skillLevel=skillInfo.effectiveSkillLevel))

        if not skillList:
            skills = localization.GetByLabel('UI/Agents/Research/ErrorNoRelevantResearchSkills', session.languageID)
        else:
            skillList = localization.util.Sort(skillList)
            skills = localization.formatters.FormatGenericList(skillList)
        details = [(localization.GetByLabel('UI/Agents/Research/RelevantSkills', session.languageID), skills)]
        status = []
        if data.researchData:
            researchData = data.researchData
            researchStuff = [(localization.GetByLabel('UI/Agents/Research/ResearchField', session.languageID), evetypes.GetName(researchData['skillTypeID'])), (localization.GetByLabel('UI/Agents/Research/CurrentStatus', session.languageID), localization.GetByLabel('UI/Agents/Research/CurrentStatusRP', session.languageID, rpAmount=researchData['points'])), (localization.GetByLabel('UI/Agents/Research/ResearchRate', session.languageID), localization.GetByLabel('UI/Agents/Research/ResearchRateRPDay', session.languageID, rpAmount=researchData['pointsPerDay']))]
            status = [(localization.GetByLabel('UI/Agents/Research/YourResearch', session.languageID), researchStuff)]
        return [(header, details)] + status

    def _ProcessLocateServiceInfo(self, data):
        header = localization.GetByLabel('UI/Agents/Locator/LocationServices', session.languageID)
        if data.frequency:
            details = [(localization.GetByLabel('UI/Agents/Locator/MaxFrequency', session.languageID), localization.GetByLabel('UI/Agents/Locator/EveryInterval', session.languageID, interval=data.frequency))]
        else:
            details = [(localization.GetByLabel('UI/Agents/Locator/MaxFrequency', session.languageID), localization.GetByLabel('UI/Generic/NotAvailableShort', session.languageID))]
        for delayRange, delay, cost in data.delays:
            rangeText = [localization.GetByLabel('UI/Agents/Locator/SameSolarSystem', session.languageID),
             localization.GetByLabel('UI/Agents/Locator/SameConstellation', session.languageID),
             localization.GetByLabel('UI/Agents/Locator/SameRegion', session.languageID),
             localization.GetByLabel('UI/Agents/Locator/DifferentRegion', session.languageID)][delayRange]
            if not delay:
                delay = localization.GetByLabel('UI/Agents/Locator/ResultsInstantaneous', session.languageID)
            else:
                delay = FmtTimeInterval(delay * appConst.SEC)
            details.append((rangeText, localization.formatters.FormatGenericList((FmtISK(cost), delay))))

        if data.callbackID:
            details.append((localization.GetByLabel('UI/Agents/Locator/Availability', session.languageID), localization.GetByLabel('UI/Agents/Locator/NotAvailableInProgress', session.languageID)))
        elif data.lastUsed and blue.os.GetWallclockTime() - data.lastUsed < data.frequency:
            details.append((localization.GetByLabel('UI/Agents/Locator/AvailableAgain', session.languageID), FmtDate(data.lastUsed + data.frequency)))
        return [(header, details)]

    def _ProcessMissionServiceInfo(self, data):
        if data.available:
            return [(localization.GetByLabel('UI/Agents/MissionServices', session.languageID), [(localization.GetByLabel('UI/Agents/MissionAvailability', session.languageID), localization.GetByLabel('UI/Agents/MissionAvailabilityStandard', session.languageID))])]
        else:
            return [(localization.GetByLabel('UI/Agents/MissionServices', session.languageID), [(localization.GetByLabel('UI/Agents/MissionAvailability', session.languageID), localization.GetByLabel('UI/Agents/MissionAvailabilityNone', session.languageID))])]
