#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\itemcompression\client\inSpaceCompression.py
from math import sqrt
from itemcompression import SLIM_ATTRIBUTE_COMPRESSION_FACILITY_TYPELISTS, MAX_FACILITY_ACTIVATION_RANGE

def GetFacilitiesInRange(ballpark, fleetMembers):
    facilities = []
    if ballpark.ego:
        slimItem = ballpark.slimItems.get(ballpark.ego, None)
        if slimItem:
            typeListIDs = set()
            for compressibleTypeListID in _IterSlimItemFacilitiesWithinRange(slimItem, 0):
                typeListIDs.add(compressibleTypeListID)

            if typeListIDs:
                facilities.append((ballpark.ego, typeListIDs))
        for ballID, slimItem in ballpark.slimItems.iteritems():
            if ballID == ballpark.ego:
                continue
            if not getattr(slimItem, SLIM_ATTRIBUTE_COMPRESSION_FACILITY_TYPELISTS, None):
                continue
            charID = getattr(slimItem, 'charID', None)
            if charID not in fleetMembers:
                continue
            ballDistance = ballpark.GetSurfaceDist(ballpark.ego, ballID)
            typeListIDs = set()
            for compressibleTypeListID in _IterSlimItemFacilitiesWithinRange(slimItem, ballDistance):
                typeListIDs.add(compressibleTypeListID)

            if typeListIDs:
                facilities.append((ballID, typeListIDs))

    return facilities


def _IterSlimItemFacilitiesWithinRange(slimItem, distance):
    ballFacilities = getattr(slimItem, SLIM_ATTRIBUTE_COMPRESSION_FACILITY_TYPELISTS, None)
    if ballFacilities is None:
        return
    for compressibleTypeListID, activationRange in ballFacilities.iteritems():
        if distance > activationRange:
            continue
        yield compressibleTypeListID
