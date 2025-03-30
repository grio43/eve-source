#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveSpaceObject\multiHullComponent.py
import evetypes
import eve.common.lib.appConst as const
from inventorycommon.const import subsystemSlotFlags
import logging
log = logging.getLogger(__name__)

class MultiHullComponent:

    def __init__(self, shipID):
        self.subPartsTypes = {}
        self._shipID = shipID

    def SetSubsystemModules(self, allModules):
        for _, typeID, _ in allModules:
            if evetypes.GetCategoryID(typeID) == const.categorySubSystem:
                self.subPartsTypes[evetypes.GetGroupID(typeID)] = typeID
                if typeID < 45000:
                    log.error('MultiHull ship ' + str(self._shipID) + ' has old subsystem module: ' + str(typeID))
                    self.subPartsTypes = {}
                    return False

        if len(self.subPartsTypes) != len(subsystemSlotFlags):
            log.error('MultiHull ship ' + str(self._shipID) + ' has wrong number of subsystem modules: ' + str(len(self.subPartsTypes)) + ' out of ' + str(allModules) + ' modules')
            return False
        log.info('MultiHull ship ' + str(self._shipID) + ' has new set of subsystem modules: ' + str(self.subPartsTypes))
        return True

    def GetTypeIDList(self):
        return self.subPartsTypes.values()
