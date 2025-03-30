#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evefleet\members.py
from utillib import KeyVal

def GetNewMemberOptOutsKeyval(acceptsFleetWarp = True):
    return KeyVal(acceptsFleetWarp=acceptsFleetWarp, acceptsConduitJumps=True, acceptsFleetRegroups=True)
