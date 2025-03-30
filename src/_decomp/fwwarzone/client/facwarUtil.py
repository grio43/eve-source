#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\fwwarzone\client\facwarUtil.py
from eve.common.script.util.facwarCommon import IsSameFwFaction, IsCombatEnemyFaction, IsOccupierEnemyFaction

def IsMyOccupierEnemyFaction(factionID):
    return IsOccupierEnemyFaction(session.warfactionid, factionID)


def IsMyCombatEnemyFaction(factionID):
    return IsCombatEnemyFaction(session.warfactionid, factionID)


def IsMyFwFaction(factionID):
    return IsSameFwFaction(factionID, session.warfactionid)
