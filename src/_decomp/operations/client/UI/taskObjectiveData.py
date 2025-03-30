#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\operations\client\UI\taskObjectiveData.py
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.const import buttonConst
from eve.common.script.sys.eveCfg import IsControllingStructure
from eveexceptions import UserError
from eve.client.script.ui.services.menuSvcExtras.movementFunctions import WarpToOperationSite
from eve.client.script.ui.shared.infoPanels.infoPanelMissionObjective import MissionObjective
from localization import GetByMessageID
from operations.client.UI.operationDestinationController import GetSiteSolarSystem
from operations.common.warpSites import GetSiteByID
from eve.client.script.util.clientPathfinderService import ConvertStationIDToSolarSystemIDIfNecessary

class TaskObjective(MissionObjective):
    __notifyevents__ = MissionObjective.__notifyevents__ + ['OnOperationTaskCompleted']
    ICON_TEXTURE_PATH = 'res:/UI/Texture/classes/MissionTracker/tracker_kill.png'
    ICON_OPACITY = 0.6
    OBJECTIVE_ICON_SIZE = 32
    OBJECTIVE_ICON_PADDING = 4

    def __init__(self, category, operation, task):
        self.category = category
        self.operation = operation
        self.task = task
        objectiveText = getattr(self.task.taskHint, 'text', None)
        missionHint = GetByMessageID(objectiveText) if objectiveText else None
        super(TaskObjective, self).__init__(missionHint=missionHint)
        sm.RegisterNotify(self)

    def OnOperationTaskCompleted(self, *args):
        self.SetInactive()

    def GetCategoryName(self):
        return GetByMessageID(self.category.title)

    def GetOperationName(self):
        return GetByMessageID(self.operation.title)

    def GetHeaderText(self):
        return GetByMessageID(self.task.title)

    def HasIcon(self):
        return bool(getattr(self.task.taskHint, 'iconPath', None))

    def BuildIcon(self, name, parent, align, state, opacity, width, height):
        iconPath = getattr(self.task.taskHint, 'iconPath', None)
        if iconPath:
            Sprite(name=name, parent=parent, align=align, state=state, opacity=opacity, width=width - 2 * self.OBJECTIVE_ICON_PADDING, height=height - 2 * self.OBJECTIVE_ICON_PADDING, texturePath=iconPath)

    def GetLocation(self):
        return (self.GetButtonLabel(), (self.GetButtonFunction(), []), self.GetButtonTexturePath())

    def _GetButtonState(self):
        return buttonConst.STATE_NONE

    def _SetDestinationToSite(self, solarSystemID, locationID):
        sm.GetService('starmap').SetWaypoint(solarSystemID, True)
        sm.ScatterEvent('OnClientEvent_OperationDestinationSet', locationID)


class TaskTravelToCareerAgent(TaskObjective):

    def __init__(self, category, operation, task):
        super(TaskTravelToCareerAgent, self).__init__(category, operation, task)
        self.stationID = sm.GetService('agents').GetMySuggestetCareerAgentStation()
        self.stationInfo = sm.GetService('ui').GetStationStaticInfo(self.stationID)

    def GetButtonFunction(self):
        return lambda x: self._SetDestinationToSite(self.stationID, self.stationID)

    def _GetButtonState(self):
        if self.stationInfo.solarSystemID != session.solarsystemid2:
            waypoints = sm.StartService('starmap').GetWaypoints()
            if waypoints and ConvertStationIDToSolarSystemIDIfNecessary(waypoints[-1]) == self.stationInfo.solarSystemID:
                return buttonConst.STATE_DESTINATIONSET
            return buttonConst.STATE_SETDESTINATION
        return super(TaskTravelToCareerAgent, self)._GetButtonState()


class TaskWithSiteObjective(TaskObjective):

    def __init__(self, category, operation, task):
        super(TaskWithSiteObjective, self).__init__(category, operation, task)
        self.siteID = self.operation.siteID
        self.solarSystemID = GetSiteSolarSystem(session.charid, self.siteID) if self.siteID else None
        self.isInSite = self._IsInSite()
        self.siteInfoID = self._GetSiteInfoID()

    def _IsInSameSolarSystem(self):
        return self.solarSystemID == session.solarsystemid2

    def _IsInStationOrStructure(self):
        return session.stationid or session.structureid

    def _IsInSite(self):
        if not self.siteID or not self._IsInSameSolarSystem() or self._IsInStationOrStructure():
            return False
        try:
            return sm.RemoteSvc('keeper').IsOperationSite(self.siteID)
        except UserError:
            return False

    def _GetSiteInfoID(self):
        if self.siteID:
            siteInfo = GetSiteByID(self.siteID)
            return getattr(siteInfo, 'id', None)

    def GetButtonFunction(self):
        buttonState = self.buttonState
        if buttonState == buttonConst.STATE_WARPTO:
            return lambda x: WarpToOperationSite(self.siteInfoID)
        if buttonState == buttonConst.STATE_SETDESTINATION:
            return lambda x: self._SetDestinationToSite(self.solarSystemID, self.siteID)
        return super(TaskWithSiteObjective, self).GetButtonFunction()

    def _GetButtonState(self):
        if IsControllingStructure():
            return buttonConst.STATE_NONE
        warpingState = self.GetWarpingState()
        if warpingState and self.buttonState in (buttonConst.STATE_WARPTO,
         buttonConst.STATE_PREPARING_WARP,
         buttonConst.STATE_WARPING,
         buttonConst.STATE_DOCK,
         buttonConst.STATE_NONE):
            return warpingState
        if sm.GetService('undocking').IsExiting():
            return buttonConst.STATE_UNDOCKING
        if self.solarSystemID is None:
            return buttonConst.STATE_NONE
        if not self.task.is_site_relevant:
            return buttonConst.STATE_NONE
        if self._IsInStationOrStructure():
            return buttonConst.STATE_UNDOCK
        if self._IsInSameSolarSystem():
            if sm.GetService('michelle').CanWarpToOperationSite(self.siteInfoID):
                return buttonConst.STATE_WARPTO
            if self.isInSite:
                return buttonConst.STATE_NONE
        else:
            waypoints = sm.StartService('starmap').GetWaypoints()
            if waypoints and waypoints[-1] == self.solarSystemID:
                return buttonConst.STATE_DESTINATIONSET
            return buttonConst.STATE_SETDESTINATION
        return super(TaskWithSiteObjective, self)._GetButtonState()
