#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\station\pvptrade\tradeUtil.py
from eve.common.script.sys.idCheckers import IsEvePlayerCharacter

def TryInitiateTrade(charID, nodes):
    if charID == session.charid:
        return
    if not IsEvePlayerCharacter(charID):
        return
    if session.stationid or session.structureid:
        return sm.StartService('pvptrade').StartTradeSession(charID, tradeItems=nodes)
