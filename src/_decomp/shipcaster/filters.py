#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\shipcaster\filters.py
from npcs.common.owner import get_npc_faction

def FilterLandingPadsForFaction(landingPadDataList, factionIDs):
    return [ x for x in landingPadDataList if get_npc_faction(x.factionID) in factionIDs ]


def FilterUnderConstructionLandingPads(landingPadDataList):
    return [ x for x in landingPadDataList if not x.isBuilt ]


def FilterBuiltLandingPads(landingPadDataList):
    return [ x for x in landingPadDataList if x.isBuilt ]


def FilterLinkedLandingPads(landingPadDataList):
    return [ x for x in landingPadDataList if x.linkTimestamp ]


def FilterUnlinkedLandingPads(landingPadDataList):
    return [ x for x in landingPadDataList if not x.linkTimestamp ]


def FilterLinkableUnlinkedLandingPads(landingPadDataList):
    return [ x for x in landingPadDataList if x.canBeLinked and not x.linkTimestamp ]
