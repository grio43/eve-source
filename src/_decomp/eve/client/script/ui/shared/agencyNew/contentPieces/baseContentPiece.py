#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\contentPieces\baseContentPiece.py
from collections import defaultdict
from evePathfinder.core import IsUnreachableJumpCount
import evetypes
from carbonui.util.color import Color
from eve.client.script.ui.const import buttonConst
from eve.client.script.ui.control.statefulButtonController import StatefulButtonController
from eve.client.script.ui.inflight.shipHud import ActiveShipController
from eve.client.script.ui.services.menuSvcExtras.movementFunctions import WarpToItem
from eve.client.script.ui.shared.agencyNew import agencyConst, agencyEventLog
from eve.client.script.ui.shared.agencyNew.ui import agencyUIConst
from eve.client.script.ui.shared.agencyNew.agencyUtil import GetNumberOfJumps, IsAvoidanceSystem, GetNoRouteFoundText
from eve.client.script.ui.shared.mapView import mapViewUtil
from eve.common.lib import appConst
from eve.common.script.sys import idCheckers
from eve.common.script.sys.idCheckers import IsStation, IsCorporation, IsKnownSpaceSystem
from eve.common.script.util.eveFormat import FmtSystemSecStatus
from localization import GetByLabel
from npcs.npccorporations import get_corporation_faction_id

def GetOwnerFactionID(ownerID):
    if not ownerID:
        return
    if idCheckers.IsNPCCorporation(ownerID):
        return get_corporation_faction_id(ownerID)
    if idCheckers.IsFaction(ownerID):
        return ownerID


class BaseContentPiece(StatefulButtonController, object):
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

    def GetBracketIconTexturePath(self):
        return 'res:/UI/Texture/classes/MapView/scanResultLocation.png'

    def GetCardText(self):
        text = ''
        subtitle = self.GetSubtitle()
        if subtitle:
            text += '%s<br>' % subtitle
        numJumps = self.GetSolarSystemAndSecurityAndNumJumpsText()
        if numJumps:
            text += '%s' % numJumps
        return text

    def GetHint(self):
        text = '<b>%s</b>' % self.GetTitle()
        subtitle = self.GetSubtitle()
        if subtitle:
            text += '<br>%s' % subtitle
        numJumps = self.GetSolarSystemAndSecurityAndNumJumpsText()
        if numJumps:
            text += '<br>%s' % numJumps
        expiryTime = self.GetExpiryTimeText()
        if expiryTime:
            text += '<br><b>%s</b>' % expiryTime
        return text

    def GetTitle(self):
        return self.GetSolarSystemName()

    def GetSolarSystemName(self):
        return cfg.evelocations.Get(self.solarSystemID).locationName

    def GetName(self):
        return self.GetSolarSystemName()

    def GetSubtitle(self):
        pass

    def GetItemID(self):
        return self.itemID

    def GetCardID(self):
        return (self.contentType, self.itemID)

    def __eq__(self, other):
        return other is not None and hasattr(other, 'GetCardID') and self.GetCardID() == other.GetCardID()

    def GetExpandedTitle(self):
        return self.GetTitle()

    def GetExpandedSubtitle(self):
        return self.GetSubtitle()

    def GetDescription(self):
        pass

    def GetOwnerID(self):
        return self.ownerID

    def GetOwnerName(self):
        return cfg.eveowners.Get(self.GetOwnerID()).ownerName

    def GetBlurbText(self):
        return ''

    def GetContentTypeID(self):
        return self.contentType

    def GetContentSubTypeID(self):
        return None

    def GetOwnerIDs(self):
        if not self.ownerID:
            return []
        ownerIDs = [self.ownerID]
        factionID = self.GetFactionID()
        if factionID:
            ownerIDs.append(factionID)
        return ownerIDs

    def GetCorpID(self):
        if idCheckers.IsNPCCorporation(self.ownerID):
            return self.ownerID

    def GetFactionID(self):
        return GetOwnerFactionID(self.ownerID)

    def GetEnemyOwnerID(self):
        return self.enemyOwnerID

    def GetEnemyFactionID(self):
        return GetOwnerFactionID(self.GetEnemyOwnerID())

    def GetContentTypeName(self):
        return agencyConst.LABEL_BY_CONTENTTYPE[self.contentType]

    def GetColor(self):
        return agencyUIConst.COLOR_BY_CONTENTTYPE.get(self.contentType, Color.GRAY)

    def GetBgColor(self):
        return agencyUIConst.BG_COLOR_BY_CONTENTTYPE[self.contentType]

    def GetIconTexturePath(self):
        return None

    def GetCardSortValue(self):
        return self.GetJumpsToSelfFromCurrentLocation()

    def GetSolarSystemAndSecurityAndNumJumpsText(self):
        if not self.solarSystemID:
            return None
        elif self.IsInCurrentStation():
            return GetByLabel('UI/Agency/ContentInCurrentStation')
        elif self.IsInCurrentSolarSystem():
            return GetByLabel('UI/Agency/ContentInCurrentSystem') + ' %s' % self.GetSecStatusNumberColoredText()
        else:
            return self.GetAgentLocationText()

    def GetAgentLocationText(self):
        isAvoided = self.solarSystemID and IsAvoidanceSystem(self.solarSystemID)
        return self.GetSystemSecurityAndNumJumpsText(isAvoided)

    def GetSystemAndSecurityText(self, isAvoided = False):
        secStatus = self.GetSecStatusNumberColoredText()
        label = 'UI/Agency/AvoidedLocation' if isAvoided else 'UI/Agency/Location'
        return GetByLabel(label, location=self.solarSystemID, secStatus=secStatus)

    def GetLocationAndSecurityText(self):
        return self.GetSystemAndSecurityText()

    def GetSystemSecurityAndNumJumpsText(self, isAvoided = False):
        label = 'UI/Agency/AvoidedLocationAndNumJumps' if isAvoided else 'UI/Agency/LocationAndNumJumps'
        return GetByLabel(label, location=self.GetDestinationSolarSystemID(), secStatus=self.GetSecStatusNumberColoredText(), jumps=self.GetNumJumpsText())

    def GetSecStatusNumberColoredText(self):
        sec = self.GetSystemSecurityStatus()
        secStatus, color = FmtSystemSecStatus(sec, True)
        color = Color.RGBtoHex(*color)
        iconText = self.GetSystemSecurityStatusModifierIconText()
        return "<color='%s'>%s</color>%s" % (color, secStatus, iconText)

    def GetSystemSecurityStatus(self):
        return sm.GetService('map').GetSecurityStatus(self.GetDestinationSolarSystemID())

    def GetSystemSecurityStatusModifierIconText(self):
        destinationSolarSystemID = self.GetDestinationSolarSystemID()
        return sm.GetService('securitySvc').get_security_modifier_icon_text(destinationSolarSystemID)

    def GetNumJumpsText(self):
        if self.IsInCurrentStation():
            return GetByLabel('UI/Generic/CurrentStation')
        if self.IsInCurrentSolarSystem():
            return GetByLabel('UI/Generic/CurrentSystem')
        if IsKnownSpaceSystem(session.solarsystemid2):
            numJumps = self.GetJumpsToSelfFromCurrentLocation()
            if numJumps:
                if IsUnreachableJumpCount(numJumps):
                    return GetByLabel('UI/Generic/NoGateToGateRoute')
                return GetByLabel('UI/Common/NumJumps', numJumps=numJumps)
        return GetByLabel('UI/Generic/NoGateToGateRoute')

    def GetJumpsToSelfFromCurrentLocation(self):
        return GetNumberOfJumps(self.solarSystemID)

    def GetStationID(self):
        return None

    def GetExpiryTimeText(self):
        pass

    def GetDisabledHint(self):
        return self.GetPrimaryActionDisabledHint()

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
            if self.GetStationID():
                return buttonConst.STATE_DOCK
            if self.IsWarpableTo():
                return buttonConst.STATE_WARPTO
        else:
            waypoints = sm.StartService('starmap').GetWaypoints()
            if waypoints and waypoints[-1] in (self.GetLocationID(), self.solarSystemID):
                return buttonConst.STATE_DESTINATIONSET
            return buttonConst.STATE_SETDESTINATION
        return super(BaseContentPiece, self)._GetButtonState()

    def IsWarpableTo(self):
        return True

    def GetButtonFunction(self):
        return lambda x: self._ExecutePrimaryFunction(self.buttonState)

    def _ExecutePrimaryFunction(self, buttonState):
        agencyEventLog.LogEventPrimaryButtonClick(self, buttonState)
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

    def GetMarkerID(self):
        return '%s_%s_%s' % (self.solarSystemID, self.itemID, self.contentType)

    def GetSubSolarSystemPosition(self):
        locationID = self.GetLocationID()
        if IsStation(locationID):
            stationInfo = sm.GetService('ui').GetStationStaticInfo(locationID)
            return (stationInfo.x, stationInfo.y, stationInfo.z)
        else:
            return mapViewUtil.TryGetPosFromItemID(locationID, self.solarSystemID)

    def GetMenu(self):
        return sm.GetService('menu').GetMenuFromItemIDTypeID(self.GetItemID(), self.typeID)

    def GetDragData(self):
        return []

    def GetModulesRequiredTypeIDs(self):
        return []

    def GetRewardTypes(self):
        return []

    def GetResourceTypeIDs(self):
        return []

    def GetCorpAndFactionStandingText(self):
        corpID = self.GetCorpID()
        if not corpID:
            return ''
        factionID = self.GetFactionID()
        corpStanding = sm.GetService('standing').GetStandingWithSkillBonus(corpID, session.charid)
        factionStanding = sm.GetService('standing').GetStandingWithSkillBonus(factionID, session.charid)
        return GetByLabel('UI/Agency/StandingWithCorpAndFaction', corpID=corpID, corpStanding=round(corpStanding, 2), factionID=factionID, factionStanding=round(factionStanding, 2))

    def GetAllowedShipTypeIDs(self):
        return []

    def GetAllowedShipTypeIDsByGroupID(self):
        typeIDsByGroupID = defaultdict(list)
        typeIDs = self.GetAllowedShipTypeIDs()
        for typeID in typeIDs:
            typeIDsByGroupID[evetypes.GetGroupID(typeID)].append(typeID)

        return typeIDsByGroupID

    def CombineGroupsUnderBrackets(self, typeIDsByGroupID):
        typeIDsByBracket = defaultdict(list)
        for groupID, typeIDs in typeIDsByGroupID.iteritems():
            bracketData = sm.GetService('bracket').GetBracketDataByGroupID(groupID)
            typeIDsByBracket[bracketData].extend(typeIDs)

        return typeIDsByBracket

    def IsActiveShipAllowed(self):
        typeID = ActiveShipController().GetTypeID()
        allowedTypes = self.GetAllowedShipTypeIDs()
        return not allowedTypes or typeID in allowedTypes

    def IsShipRestrictionShown(self):
        return not self.IsActiveShipAllowed()

    def GetEnemyRoamingText(self):
        ownerID = self.GetEnemyOwnerID()
        if ownerID != appConst.factionUnknown:
            ownerTypeID = self.GetEnemyOwnerTypeID()
            return GetByLabel('UI/Agency/EnemyRoaming', ownerID=ownerID, ownerTypeID=ownerTypeID)
        else:
            return GetByLabel('UI/Agency/UnknownEnemyRoaming')

    def GetEnemyOwnerTypeID(self):
        if IsCorporation(self.GetEnemyOwnerID()):
            return appConst.typeCorporation
        return appConst.typeFaction

    def GetChatChannelID(self):
        return None

    def GetSunTypeID(self):
        star = cfg.mapSolarSystemContentCache[self.solarSystemID].star
        return star.typeID

    def GetBGVideoPath(self):
        return None
