#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\epicArcs\epicArcController.py
from carbonui.util.color import Color
from eve.client.script.ui.shared.epicArcs import epicArcConst
from eve.client.script.ui.station.agents import agentConst
from eve.client.script.ui.station.agents.agentUtil import IsAgentStandingSufficientToUse, GetAgentStandingThreshold
from evemissions.common.epic_arcs_data import MESSAGE_CHAPTER_TITLE
from evemissions.common.epic_arcs_data import MESSAGE_COMPLETED
from evemissions.common.epic_arcs_data import MESSAGE_IN_PROGRESS
from evemissions.common.epic_arcs_data import get_agent_in_epic_arc_mission
from evemissions.common.epic_arcs_data import get_epic_arc_missions
from evemissions.common.epic_arcs_data import iter_epic_arcs
from evemissions.common.epic_arcs_data import get_epic_arc_restart_interval
from evemissions.common.epic_arcs_data import get_next_epic_arc_missions
from localization import GetByMessageID, GetByLabel
from evemissions.common.epic_arcs_data import get_epic_arc_faction_id

class EpicArcController(object):

    def __init__(self, missionStatusesByEpicArcID):
        self.epicArcs = self._GetEpicArcs()
        self._missionStatusesByEpicArcID = missionStatusesByEpicArcID
        self._GetEpicArcNodesByMissionID()
        for arc in self.epicArcs.values():
            arc.FixChapterIDs()

    def GetEpicArcs(self):
        return self.epicArcs

    def _GetEpicArcs(self):
        epicArcs = {}
        for epicArcID, epicArcNameID in iter_epic_arcs():
            if self.IsValidArc(epicArcID):
                epicArcs[epicArcID] = EpicArc(epicArcID, epicArcNameID)

        return epicArcs

    def IsValidArc(self, epicArcID):
        arcRestartInterval = get_epic_arc_restart_interval(epicArcID)
        return arcRestartInterval > 1

    def _GetFirstMissionIDs(self, connections):
        nextMissionIDs = [ c.nextMissionID for c in connections ]
        return [ c.currentMissionID for c in connections if c.currentMissionID not in nextMissionIDs ]

    def _GetEpicArcNodesByMissionID(self):
        self.nodesByMissionID = {}
        for epicArcID, _ in iter_epic_arcs():
            missions = get_epic_arc_missions(epicArcID)
            for missionID in missions:
                self._ConstructNode(epicArcID, missionID)

        self._ConnectAllNodes()
        firstNodes = [ node for node in self.nodesByMissionID.values() if not node.previousNodes ]
        for node in firstNodes:
            epicArc = self.epicArcs.get(node.epicArcID, None)
            if epicArc:
                epicArc.AddStartNode(node)

    def _GetMissionMessageID(self, missionID, messageType):
        messages = sm.RemoteSvc('agentMgr').GetMessagesForEpicArcMissions()
        return messages.get(messageType, {}).get(missionID, None)

    def _ConnectAllNodes(self):
        for node in self.nodesByMissionID.values():
            chapterID = self._GetMissionMessageID(node.missionID, MESSAGE_CHAPTER_TITLE)
            node.SetChapterID(chapterID)
            nextMissions = get_next_epic_arc_missions(node.epicArcID, node.missionID, [])
            for nextMissionID in nextMissions:
                nextNode = self.nodesByMissionID.get(nextMissionID, None)
                if nextNode:
                    node.AddNextNode(nextNode)

    def _ConstructNode(self, epicArcID, missionID):
        acceptedDate, completedDate, nameID, quitDate = self._GetMissionStatus(epicArcID, missionID)
        agentID = get_agent_in_epic_arc_mission(epicArcID, missionID)
        node = EpicArcMissionNode(epicArcID=epicArcID, missionID=missionID, agentID=agentID, inProgressMsgID=self._GetMissionMessageID(missionID, MESSAGE_IN_PROGRESS), completedMsgID=self._GetMissionMessageID(missionID, MESSAGE_COMPLETED), acceptedDate=acceptedDate, completedDate=completedDate, quitDate=quitDate, nameID=nameID)
        self.nodesByMissionID[node.missionID] = node

    def _GetMissionStatus(self, epicArcID, missionID):
        status = self._missionStatusesByEpicArcID.get(epicArcID, {}).get(missionID, None)
        if status:
            acceptedDate = status.acceptedDate
            completedDate = status.completedDate
            quitDate = status.quitDate
            nameID = status.nameID
        else:
            acceptedDate = completedDate = quitDate = nameID = None
        return (acceptedDate,
         completedDate,
         nameID,
         quitDate)


class EpicArcMissionNode(object):

    def __init__(self, epicArcID, missionID, agentID, inProgressMsgID, completedMsgID, acceptedDate = None, completedDate = None, quitDate = None, nameID = None):
        self.epicArcID = epicArcID
        self.missionID = missionID
        self.agentID = agentID
        self.inProgressMsgID = inProgressMsgID
        self.completedMsgID = completedMsgID
        self.acceptedDate = acceptedDate
        self.completedDate = completedDate
        self.quitDate = quitDate
        self.nameID = nameID
        self.nextNodes = []
        self.previousNodes = []
        self.chapterID = None

    def GetAgentID(self):
        return self.agentID

    def GetDestinationAgentID(self):
        activeMission = sm.GetService('journal').GetActiveMissionForAgent(self.GetAgentID())
        if activeMission:
            return activeMission.GetDestinationAgentID()
        else:
            return self.GetAgentID()

    def AddNextNode(self, node):
        self.nextNodes.append(node)
        node.previousNodes.append(self)

    def GetLastNodesInArc(self):
        lastNodes = set()
        self._GetLastNodesInArc(lastNodes)
        return lastNodes

    def _GetLastNodesInArc(self, lastNodes):
        if self.IsLastInArc():
            lastNodes.add(self)
        else:
            for node in self.nextNodes:
                node._GetLastNodesInArc(lastNodes)

    def SetChapterID(self, chapterID):
        self.chapterID = chapterID

    def GetChapterID(self):
        if self.chapterID:
            return self.chapterID
        if self.previousNodes:
            return self.previousNodes[0].GetChapterID()

    def IsLastInChapter(self):
        if self.IsLastInArc():
            return True
        else:
            return self.GetChapterID() != self.nextNodes[0].GetChapterID()

    def IsFirstInChapter(self):
        if self.IsFirstInArc():
            return True
        else:
            return self.GetChapterID() != self.previousNodes[0].GetChapterID()

    def GetName(self):
        if self.nameID:
            return GetByMessageID(self.nameID)

    def GetInProgressText(self):
        return GetByMessageID(self.inProgressMsgID)

    def GetCompletedText(self):
        return GetByMessageID(self.completedMsgID)

    def GetStateText(self):
        state = self.GetState()
        if state == epicArcConst.MISSION_COMPLETED:
            text = GetByLabel('UI/Agency/EpicArcComplete', completeTime=self.completedDate)
        elif state == epicArcConst.MISSION_ACCEPTED:
            text = GetByLabel('UI/Agency/EpicArcMissionAccepted')
        elif state == epicArcConst.MISSION_OFFERED:
            text = GetByLabel('UI/Agency/EpicArcMissionOffered')
        elif state == epicArcConst.MISSION_UNAVAILABLE:
            if self.IsFirstInArc():
                text = GetByLabel('UI/Agency/EpicArcMissionUnavailableFirst', agent=self.agentID)
            else:
                text = GetByLabel('UI/Agency/EpicArcMissionUnavailable')
        color = self.GetStateColor()
        return '<color=%s>%s</color>' % (Color.RGBtoHex(*color), text)

    def GetHint(self):
        stateText = self.GetStateText()
        if not self.IsOffered():
            return stateText
        if self.IsComplete():
            text = self.GetCompletedText()
        else:
            text = self.GetInProgressText()
        return '<b>%s</b>\n%s\n%s' % (self.GetName(), text, stateText)

    def GetStateColor(self):
        state = self.GetState()
        if state == epicArcConst.MISSION_COMPLETED:
            if self.IsLastInChapter():
                return agentConst.COLOR_ACCEPTED_LAST
            else:
                return agentConst.COLOR_ACCEPTED
        else:
            if state == epicArcConst.MISSION_ACCEPTED:
                return agentConst.COLOR_ACCEPTED
            if state == epicArcConst.MISSION_OFFERED:
                return agentConst.COLOR_OFFERED
            if state == epicArcConst.MISSION_UNAVAILABLE:
                return (1.0, 1.0, 1.0, 0.85)

    def IsLastInArc(self):
        return not bool(self.nextNodes)

    def IsFirstInArc(self):
        return not bool(self.previousNodes)

    def IsComplete(self):
        return bool(self.completedDate)

    def IsNextComplete(self):
        node = self._GetNextNode()
        if node:
            return node.IsComplete()

    def IsAccepted(self):
        return bool(self.acceptedDate)

    def IsOffered(self):
        return bool(self.nameID)

    def IsActive(self):
        return self.IsOffered() and not self.IsComplete()

    def GetState(self):
        if self.IsComplete():
            return epicArcConst.MISSION_COMPLETED
        elif self.IsAccepted():
            return epicArcConst.MISSION_ACCEPTED
        elif self.IsOffered():
            return epicArcConst.MISSION_OFFERED
        else:
            return epicArcConst.MISSION_UNAVAILABLE

    def IsArcComplete(self):
        if self.IsLastInArc():
            return self.IsComplete()
        else:
            for node in self.nextNodes:
                if node.IsArcComplete():
                    return True

            return False

    def GetArcCompleteTime(self):
        if self.IsLastInArc():
            return self.completedDate
        else:
            return self._GetNextNode().GetArcCompleteTime()

    def GetActiveMissions(self):
        if self.IsActive():
            return [self]
        for node in self.nextNodes:
            ret = node.GetActiveMissions()
            if ret:
                return ret

    def GetNumMissions(self, num):
        if self.nextNodes:
            num += self.nextNodes[0].GetNumMissions(num)
        return num + 1

    def GetMissionNumber(self, num = 0):
        if not self.IsFirstInArc():
            num += self.previousNodes[0].GetMissionNumber(num)
        return num + 1

    def GetNumChapters(self, num):
        if self.nextNodes:
            num += self.nextNodes[0].GetNumChapters(num)
        if self.chapterID:
            num += 1
        return num

    def GetChapterMissions(self, chapterID, missions):
        if missions and self.chapterID and self.chapterID != chapterID:
            return
        if self.chapterID == chapterID or missions:
            missions.append(self)
        node = self._GetNextNode()
        if node:
            node.GetChapterMissions(chapterID, missions)

    def _GetNextNode(self):
        if not self.nextNodes:
            return
        for node in self.nextNodes:
            if node.IsAccepted():
                return node

        for node in self.nextNodes:
            if node.IsOffered():
                return node

        return self.nextNodes[0]

    def GetChapterIDs(self, chapterIDs):
        if self.chapterID and self.chapterID not in chapterIDs:
            chapterIDs.append(self.chapterID)
        nextNode = self._GetNextNode()
        if nextNode:
            nextNode.GetChapterIDs(chapterIDs)

    def GetCurrentChapterID(self, chapterID = None):
        if self.chapterID:
            chapterID = self.chapterID
        if self.IsActive():
            return chapterID
        node = self._GetNextNode()
        if node:
            return node.GetCurrentChapterID(chapterID)

    def GetNextChapterID(self):
        nextNode = self._GetNextNode()
        if not nextNode:
            return
        elif nextNode.chapterID:
            return nextNode.chapterID
        else:
            return nextNode.GetNextChapterID()

    def PrintArc(self):
        print '%s: %s\n' % (self.missionID, self.GetName())
        node = self._GetNextNode()
        if node:
            node.PrintArc()


class EpicArc(object):

    def __init__(self, epicArcID, nameID):
        self.epicArcID = epicArcID
        self.nameID = nameID
        self.startNodes = []

    def AddStartNode(self, startNode):
        self.startNodes.append(startNode)

    def FixChapterIDs(self):
        for node in self.startNodes:
            if not node.chapterID:
                node.chapterID = node.GetNextChapterID()

    def GetName(self):
        return GetByMessageID(self.nameID)

    def GetDescription(self):
        pass

    def GetFactionID(self):
        return get_epic_arc_faction_id(self.epicArcID)

    def IsComplete(self):
        for node in self.startNodes:
            if node.IsArcComplete():
                return True

        return False

    def GetActiveMissions(self):
        missions = None
        for node in self.startNodes:
            if node.IsAccepted():
                missions = node.GetActiveMissions()

        return missions or self.startNodes[:]

    def GetState(self):
        if self.IsComplete():
            return epicArcConst.ARC_COMPLETE
        elif self.IsStarted():
            return epicArcConst.ARC_STARTED
        elif self.IsStandingSufficientToStart():
            return epicArcConst.ARC_AVAILABLE
        else:
            return epicArcConst.ARC_UNAVAILABLE

    def IsStandingSufficientToStart(self):
        for node in self.startNodes:
            agent = self._GetAgent(node.GetAgentID())
            if IsAgentStandingSufficientToUse(agent):
                return True

        return False

    def GetRequiredStanding(self):
        for node in self.startNodes:
            agent = self._GetAgent(node.GetAgentID())
            return GetAgentStandingThreshold(agent.level)

    def IsStarted(self):
        for node in self.startNodes:
            if node.IsAccepted():
                return True

        return False

    def GetNumMissions(self):
        return self._GetStartNode().GetNumMissions(0)

    def GetNumChapters(self):
        return len(self.GetChapterIDs())

    def GetCurrChapterNum(self):
        if not self.IsStarted():
            return 0
        chapterID = self.GetCurrentChapterID()
        return self.GetChapterIDs().index(chapterID) + 1

    def GetActiveAgent(self):
        mission = self.GetActiveMission()
        if mission:
            return self._GetAgent(mission.GetDestinationAgentID())

    def GetActiveMission(self):
        missions = self.GetActiveMissions()
        missions = sorted(missions, key=self._GetAgentSortKey)
        return missions[0]

    def _GetAgent(self, agentID):
        return sm.GetService('agents').GetAgentByID(agentID)

    def _GetAgentSortKey(self, mission):
        agent = self._GetAgent(mission.agentID)
        return -int(IsAgentStandingSufficientToUse(agent))

    def GetActiveMissionNum(self):
        if not self.IsStarted():
            return 0
        mission = self.GetActiveMissions()[0]
        return mission.GetMissionNumber()

    def GetNumMissionsCompleted(self):
        if self.IsComplete():
            return self.GetNumMissions()
        return max(0, self.GetActiveMissionNum() - 1)

    def GetProgressRatio(self):
        return float(self.GetNumMissionsCompleted()) / self.GetNumMissions()

    def GetCompleteTime(self):
        return self._GetStartNode().GetArcCompleteTime()

    def GetChapterIDs(self):
        chapterIDs = []
        startNode = self._GetStartNode()
        startNode.GetChapterIDs(chapterIDs)
        return chapterIDs

    def GetChapterMissions(self, chapterID):
        missions = []
        node = self._GetStartNode()
        node.GetChapterMissions(chapterID, missions)
        return missions

    def _GetStartNode(self):
        for node in self.startNodes:
            if node.IsAccepted():
                return node

        for node in self.startNodes:
            if node.IsOffered():
                return node

        return self.GetActiveMission()

    def GetCurrentChapterID(self):
        node = self._GetStartNode()
        chapterID = node.GetCurrentChapterID()
        return chapterID or self.GetChapterIDs()[0]

    def PrintArc(self):
        node = self._GetStartNode()
        node.PrintArc()

    def GetStartNodes(self):
        return self.startNodes

    def GetEndNodes(self):
        nodes = set()
        for node in self.GetStartNodes():
            nodes.update(node.GetLastNodesInArc())

        return nodes
