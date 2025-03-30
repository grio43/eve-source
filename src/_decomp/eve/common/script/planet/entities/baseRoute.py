#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\common\script\planet\entities\baseRoute.py
import utillib
import weakref
import evetypes
import eve.common.script.util.planetCommon as planetCommon

class BaseRoute(object):
    __name__ = 'BaseRoute'
    __slots__ = ['colony',
     'routeID',
     'charID',
     'commodityTypeID',
     'commodityQuantity',
     'path']

    def __init__(self, colony, routeID, charID, typeID, qty):
        self.colony = weakref.proxy(colony)
        self.routeID = routeID
        self.charID = charID
        self.commodityTypeID = typeID
        self.commodityQuantity = qty
        self.path = []

    def __str__(self):
        return 'PI Route <ID:%d> <Owner:%d> <Path:%s> <Type:%s>' % (self.routeID,
         self.charID,
         self.path,
         self.commodityTypeID)

    def GetSourcePinID(self):
        if len(self.path) < 1:
            return None
        return self.path[0]

    def GetDestinationPinID(self):
        if len(self.path) < 1:
            return None
        return self.path[-1]

    def SetSourcePin(self, sourcePin):
        self.path = [sourcePin.id]

    def SetPath(self, newPath):
        self.path = newPath[:]

    def GetType(self):
        return self.commodityTypeID

    def GetQuantity(self):
        return self.commodityQuantity

    def TransitsLink(self, endpoint1id, endpoint2id):
        if len(self.path) < 2:
            return False
        if endpoint1id not in self.path or endpoint2id not in self.path:
            return False
        prevID = self.path[0]
        for pinID in self.path[1:]:
            if prevID == endpoint1id and pinID == endpoint2id:
                return True
            if prevID == endpoint2id and pinID == endpoint1id:
                return True
            prevID = pinID

        return False

    def GetRoutingInfo(self):
        return (self.path[0],
         self.path[-1],
         self.commodityTypeID,
         self.commodityQuantity)

    def GetBandwidthUsage(self):
        typeID = self.GetType()
        return self.GetBandwidthUsageForTypeID(typeID)

    def GetBandwidthUsageForTypeID(self, typeID):
        bwth = evetypes.GetVolume(typeID) * self.GetQuantity()
        cycleTime = self.GetRouteCycleTime()
        if cycleTime == 0.0 or cycleTime is None:
            return bwth
        else:
            return planetCommon.GetBandwidth(bwth, cycleTime)

    def GetRouteCycleTime(self):
        sourcePin = self.colony.GetPin(self.GetSourcePinID())
        if sourcePin.IsProducer():
            return sourcePin.GetCycleTime()
        if sourcePin.IsStorage():
            destinationPin = self.colony.GetPin(self.GetDestinationPinID())
            if destinationPin.IsConsumer():
                return destinationPin.GetCycleTime()
            return 0.0
        return 0.0

    def Serialize(self):
        return utillib.KeyVal(routeID=self.routeID, charID=self.charID, path=self.path, commodityTypeID=self.commodityTypeID, commodityQuantity=self.commodityQuantity)
