#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\station\securityOfficeSvc.py
from collections import defaultdict
import crimewatch.const
from eve.common.lib.appConst import stationOwnersWithSecurityService
from carbon.common.script.sys.service import Service
from eveuniverse.security import securityClassLowSec
from inventorycommon.const import containerHangar, flagHangar

class SecurityOfficeService(Service):
    __guid__ = 'svc.securityOfficeSvc'
    __dependencies__ = ['map', 'ui', 'invCache']
    __startupdependencies__ = []
    __notifyevents__ = []

    def CanAccessServiceInStation(self, stationID):
        stationInfo = self.ui.GetStationStaticInfo(stationID)
        if stationInfo is not None:
            if self.ui.GetStationOwner(stationID) in stationOwnersWithSecurityService:
                if self.CanAccessServiceInSolarSystem(stationInfo.solarSystemID):
                    return True
        return False

    def GetTagsInHangar(self):
        invContainer = self.invCache.GetInventory(containerHangar)
        items = invContainer.List(flagHangar)
        tagCountByTypeID = defaultdict(int)
        for item in items:
            if item.typeID in crimewatch.const.securityLevelsPerTagType:
                tagCountByTypeID[item.typeID] += item.stacksize

        return tagCountByTypeID

    def CanAccessServiceInSolarSystem(self, solarSystemID):
        return self.map.GetSecurityClass(solarSystemID) == securityClassLowSec
