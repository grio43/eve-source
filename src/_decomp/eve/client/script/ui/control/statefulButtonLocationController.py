#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\statefulButtonLocationController.py
from ballparkCommon.parkhelpers.warpSubjects import WarpSubjects
from eve.client.script.ui.const import buttonConst
from eve.client.script.ui.control.statefulButtonController import StatefulButtonController
from eve.client.script.ui.services.menuSvcExtras import movementFunctions
from eve.client.script.ui.services.menuSvcExtras.movementFunctions import WarpToItem
from eve.common.script.sys.idCheckers import IsStation, IsDockableLocationType
from localization import GetByLabel
from menucheckers import SessionChecker, CelestialChecker

class LocationButtonController(StatefulButtonController, object):

    def __init__(self, solarSystemID, dockabeLocationID, itemID, typeID, warpSubject = WarpSubjects.ITEM, **kwargs):
        self.solarSystemID = solarSystemID
        self.dockabeLocationID = dockabeLocationID
        self.itemID = itemID
        self.typeID = typeID
        self.warpSubject = warpSubject
        StatefulButtonController.__init__(self)

    def IsInCurrentSolarSystem(self):
        return self.solarSystemID == session.solarsystemid2

    def IsCurrentSolarSystem(self):
        return self.itemID == session.solarsystemid2

    def IsAvailable(self):
        return True

    def _GetButtonState(self):
        warpingState = self.GetWarpingState()
        if warpingState and self.buttonState in (buttonConst.STATE_WARPTO,
         buttonConst.STATE_PREPARING_WARP,
         buttonConst.STATE_WARPING,
         buttonConst.STATE_DOCK):
            return warpingState
        elif self.dockabeLocationID:
            return self._GetButtonStateForDockableLocation()
        else:
            return self._GetButtonStateForLocationInSpace()

    def _GetButtonStateForDockableLocation(self):
        if self.IsDocked():
            if sm.GetService('undocking').IsExiting():
                return buttonConst.STATE_UNDOCKING
            elif self.IsInDockableLocation():
                return buttonConst.STATE_NONE
            else:
                return buttonConst.STATE_UNDOCK
        if self.IsInCurrentSolarSystem():
            return buttonConst.STATE_DOCK
        else:
            waypoints = sm.StartService('starmap').GetWaypoints()
            if waypoints and waypoints[-1] == self.GetDockableLocationID():
                return buttonConst.STATE_DESTINATIONSET
            return buttonConst.STATE_SETDESTINATION

    def _GetButtonStateForLocationInSpace(self):
        if self.IsInCurrentSolarSystem():
            if self.IsCurrentSolarSystem():
                return buttonConst.STATE_NONE
            elif self.IsDocked():
                if sm.GetService('undocking').IsExiting():
                    return buttonConst.STATE_UNDOCKING
                return buttonConst.STATE_UNDOCK
            elif self.IsWarpableTo():
                return buttonConst.STATE_WARPTO
            elif self.IsApproachable():
                return buttonConst.STATE_APPROACH
            else:
                return buttonConst.STATE_NONE
        else:
            waypoints = sm.StartService('starmap').GetWaypoints()
            if waypoints and waypoints[-1] == self.solarSystemID:
                return buttonConst.STATE_DESTINATIONSET
            return buttonConst.STATE_SETDESTINATION

    def IsWarpableTo(self):
        if not self.IsInCurrentSolarSystem():
            return False
        elif self.IsDocked():
            return False
        else:
            michelle = sm.GetService('michelle')
            if self.GetDockableLocationID():
                coordinates = None
                if IsStation(self.dockabeLocationID):
                    stationInfo = sm.GetService('ui').GetStationStaticInfo(self.dockabeLocationID)
                    coordinates = (stationInfo.x, stationInfo.y, stationInfo.z)
                elif IsDockableLocationType(self.typeID):
                    structureInfo = sm.GetService('structureDirectory').GetStructureInfo(self.dockabeLocationID)
                    coordinates = (structureInfo.x, structureInfo.y, structureInfo.z)
                else:
                    return False
                return michelle.IsPositionWithinWarpDistance(coordinates)
            locationInfo = cfg.evelocations.GetIfExists(self.itemID)
            if locationInfo is None:
                return True
            coordinates = (locationInfo.x, locationInfo.y, locationInfo.z)
            return michelle.IsPositionWithinWarpDistance(coordinates)

    def IsApproachable(self):
        slimItem = sm.GetService('michelle').GetItem(self.itemID)
        if not slimItem:
            return False
        celestialChecker = CelestialChecker(slimItem, cfg, SessionChecker(session, sm))
        if celestialChecker.OfferApproachObject():
            return True
        return False

    def GetButtonFunction(self):
        return lambda x: self._ExecutePrimaryFunction(self.buttonState)

    def _ExecutePrimaryFunction(self, buttonState):
        if buttonState in (buttonConst.STATE_UNDOCK, buttonConst.STATE_UNDOCKING):
            sm.GetService('undocking').UndockBtnClicked()
        elif buttonState == buttonConst.STATE_DOCK:
            sm.GetService('menu').Dock(self.GetDockableLocationID())
        elif buttonState == buttonConst.STATE_WARPTO:
            self._ExecuteWarpTo()
        elif buttonState == buttonConst.STATE_SETDESTINATION:
            self.SetDestinationTo()
        elif buttonState == buttonConst.STATE_APPROACH:
            movementFunctions.Approach(self.itemID)

    def SetDestinationTo(self):
        sm.StartService('starmap').SetWaypoint(self.GetDestinationID(), clearOtherWaypoints=True)

    def _ExecuteWarpTo(self):
        if not self.itemID:
            return
        WarpToItem(self.itemID, warpSubject=self.warpSubject)

    def GetDisabledHint(self):
        buttonState = self.GetButtonState()
        if buttonState == buttonConst.STATE_WARPTO:
            michelle = sm.GetService('michelle')
            if michelle.InWarp():
                return GetByLabel('UI/Agency/DisabledHintAlreadyWarping')
            pos = self.GetSubSolarSystemPosition()
            if pos is None:
                return
            if not michelle.IsPositionWithinWarpDistance(pos):
                return GetByLabel('UI/Agency/DisabledHintAlreadyThere')

    def GetDestinationSolarSystemID(self):
        return self.solarSystemID

    def GetDockableLocationID(self):
        return self.dockabeLocationID

    def GetDestinationID(self):
        stationID = self.GetDockableLocationID()
        if stationID:
            return stationID
        else:
            return self.GetDestinationSolarSystemID()

    def IsDocked(self):
        return session.stationid is not None or session.structureid is not None

    def IsInDockableLocation(self):
        if self.dockabeLocationID is None:
            return False
        return self.dockabeLocationID in (session.stationid, session.structureid)

    def GetSubSolarSystemPosition(self):
        dockableLocationID = self.GetDockableLocationID()
        if IsStation(dockableLocationID):
            stationInfo = sm.GetService('ui').GetStationStaticInfo(dockableLocationID)
            return (stationInfo.x, stationInfo.y, stationInfo.z)
        if IsDockableLocationType(self.typeID):
            structureInfo = sm.GetService('structureDirectory').GetStructureInfo(dockableLocationID)
            return (structureInfo.x, structureInfo.y, structureInfo.z)
        locationInfo = cfg.evelocations.GetIfExists(self.itemID)
        if not locationInfo:
            return
        if locationInfo.solarSystemID != self.solarSystemID:
            return
        pos = (locationInfo.x, locationInfo.y, locationInfo.z)
        if pos != (0, 0, 0):
            return pos
