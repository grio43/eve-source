#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\fwwarzone\client\dashboard\nearestEnlistmentOfficeCard\buttonController.py
from eve.client.script.ui.const import buttonConst
from eve.client.script.ui.control.statefulButtonController import StatefulButtonController
from eve.client.script.ui.services.menuSvcExtras.movementFunctions import WarpToItem, IsApproachingBall
from eve.client.script.ui.shared.mapView import mapViewUtil
from eve.common.script.sys import idCheckers
from eve.common.script.sys.idCheckers import IsStation
from localization import GetByLabel
from npcs.npccorporations import get_corporation_faction_id

def GetOwnerFactionID(ownerID):
    if not ownerID:
        return
    if idCheckers.IsNPCCorporation(ownerID):
        return get_corporation_faction_id(ownerID)
    if idCheckers.IsFaction(ownerID):
        return ownerID


class StationButtonController(StatefulButtonController, object):
    contentType = None

    def __init__(self, solarSystemID = None, locationID = None, itemID = None, typeID = None, ownerID = None, enemyOwnerID = None, isNew = False, **kwargs):
        self.solarSystemID = solarSystemID
        self.locationID = locationID
        self.itemID = itemID
        self.typeID = typeID
        self.ownerID = ownerID
        self.enemyOwnerID = enemyOwnerID
        self.isNew = isNew
        StatefulButtonController.__init__(self)

    def GetStationID(self):
        return self.locationID

    def IsInCurrentSolarSystem(self):
        return self.solarSystemID == session.solarsystemid2

    def IsInCurrentStation(self):
        locationID = self.GetLocationID()
        return session.stationid is not None and session.stationid == locationID

    def IsAvailable(self):
        return True

    def GetLocationID(self):
        return self.locationID

    def _GetButtonState(self):
        warpingState = self.GetWarpingState()
        if warpingState and self.buttonState in (buttonConst.STATE_WARPTO,
         buttonConst.STATE_PREPARING_WARP,
         buttonConst.STATE_WARPING,
         buttonConst.STATE_DOCK):
            return warpingState
        if self.IsInCurrentSolarSystem():
            if self.IsInStation():
                if sm.GetService('undocking').IsExiting():
                    return buttonConst.STATE_UNDOCKING
                return buttonConst.STATE_UNDOCK
            else:
                return buttonConst.STATE_DOCK
        else:
            waypoints = sm.StartService('starmap').GetWaypoints()
            if waypoints and waypoints[-1] in (self.GetLocationID(), self.solarSystemID):
                return buttonConst.STATE_DESTINATIONSET
            return buttonConst.STATE_SETDESTINATION

    def IsWarpableTo(self):
        return True

    def GetButtonFunction(self):
        return lambda x: self._ExecutePrimaryFunction(self.buttonState)

    def _ExecutePrimaryFunction(self, buttonState):
        if buttonState in (buttonConst.STATE_UNDOCK, buttonConst.STATE_UNDOCKING):
            sm.GetService('undocking').UndockBtnClicked()
        elif buttonState == buttonConst.STATE_DOCK:
            sm.GetService('menu').Dock(self.GetStationID())
        elif buttonState == buttonConst.STATE_WARPTO:
            self._ExecuteWarpTo()
        elif buttonState == buttonConst.STATE_SETDESTINATION:
            self.SetDestinationTo()

    def SetDestinationTo(self):
        sm.StartService('starmap').SetWaypoint(self.GetDestinationID(), clearOtherWaypoints=True)

    def _ExecuteWarpTo(self):
        locationID = self.GetLocationID()
        if locationID:
            WarpToItem(locationID)

    def GetPrimaryActionDisabledHint(self):
        buttonState = self.GetButtonState()
        if buttonState == buttonConst.STATE_SETDESTINATION:
            if self.GetDestinationID() in sm.StartService('starmap').GetWaypoints():
                return GetByLabel('UI/Agency/DisabledHintWaypointAlreadySet')
            if self.GetDestinationSolarSystemID() == session.solarsystemid2:
                return GetByLabel('UI/Agency/DisabledHintAlreadyThere')
        elif buttonState == buttonConst.STATE_WARPTO:
            michelle = sm.GetService('michelle')
            if michelle.InWarp():
                return GetByLabel('UI/Agency/DisabledHintAlreadyWarping')
            if not michelle.IsPositionWithinWarpDistance(self.GetSubSolarSystemPosition()):
                return GetByLabel('UI/Agency/DisabledHintAlreadyThere')

    def GetDestinationSolarSystemID(self):
        return self.solarSystemID

    def GetDestinationID(self):
        stationID = self.GetStationID()
        if stationID:
            return stationID
        else:
            return self.GetDestinationSolarSystemID()

    def IsInStation(self):
        return session.stationid is not None or session.structureid is not None

    def GetSubSolarSystemPosition(self):
        locationID = self.GetLocationID()
        if IsStation(locationID):
            stationInfo = sm.GetService('ui').GetStationStaticInfo(locationID)
            return (stationInfo.x, stationInfo.y, stationInfo.z)
        else:
            return mapViewUtil.TryGetPosFromItemID(locationID, self.solarSystemID)
