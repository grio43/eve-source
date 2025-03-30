#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fittingScreen\fittingSnapshot.py
import inventorycommon.const as invConst
from eve.client.script.ui.shared.fittingScreen import ONLINE, ACTIVE, OVERHEATED
allModuleSlots = invConst.subsystemSlotFlags + invConst.loSlotFlags + invConst.medSlotFlags + invConst.hiSlotFlags + invConst.serviceSlotFlags

class FittingSnapshot(object):

    def __init__(self, shipTypeID, fitData, chargeInfoToLoad, oringalItemIDByFlagAndTypeID, registeredDroneTypes, shipStanceID, currentStatusByFlagID, shipName):
        self.shipTypeID = shipTypeID
        self.fitData = fitData
        self.chargeInfoToLoad = chargeInfoToLoad
        self.oringalItemIDByFlagAndTypeID = oringalItemIDByFlagAndTypeID
        self.registeredDroneTypes = registeredDroneTypes
        self.shipStanceID = shipStanceID
        self.currentStatusByFlagID = currentStatusByFlagID
        self.shipName = shipName

    def __repr__(self):
        text = '----------------\r\nshipTypeID=%s\r\nfitData=%s\r\nchargeInfo=%s\r\noriginalItems=%s\r\nactiveDrones=%s\r\nstanceID=%s\r\ncurrentStatusByFlagID=%s' % (self.shipTypeID,
         self.fitData,
         self.chargeInfoToLoad,
         self.oringalItemIDByFlagAndTypeID,
         self.registeredDroneTypes,
         self.shipStanceID,
         self.currentStatusByFlagID)
        return text

    def GetOnlineModules(self):
        onlineModules = [ k for k, v in self.currentStatusByFlagID.iteritems() if v == ONLINE ]
        return [ x for x in allModuleSlots if x in onlineModules ]

    def GetActiveModules(self):
        activeModules = [ k for k, v in self.currentStatusByFlagID.iteritems() if v == ACTIVE ]
        return [ x for x in allModuleSlots if x in activeModules ]

    def GetOverheatedModules(self):
        overheatedModules = [ k for k, v in self.currentStatusByFlagID.iteritems() if v == OVERHEATED ]
        return [ x for x in allModuleSlots if x in overheatedModules ]

    def GetOfflineRigs(self):
        onlineModules = [ k for k, v in self.currentStatusByFlagID.iteritems() if v == ONLINE ]
        return [ x for x in invConst.rigSlotFlags if x not in onlineModules ]

    def GetOnlineRigs(self):
        onlineModules = [ k for k, v in self.currentStatusByFlagID.iteritems() if v == ONLINE ]
        return [ x for x in invConst.rigSlotFlags if x in onlineModules ]

    def __eq__(self, other):
        if not isinstance(other, FittingSnapshot):
            return False
        if self.shipTypeID != other.shipTypeID:
            return False
        if sorted(self.fitData) != sorted(other.fitData):
            return False
        if self.chargeInfoToLoad != other.chargeInfoToLoad:
            return False
        if self.oringalItemIDByFlagAndTypeID != other.oringalItemIDByFlagAndTypeID:
            return False
        if self.registeredDroneTypes != other.registeredDroneTypes:
            return False
        if self.shipStanceID != other.shipStanceID:
            return False
        if self.currentStatusByFlagID != other.currentStatusByFlagID:
            return False
        return True

    def __ne__(self, other):
        return not self == other
