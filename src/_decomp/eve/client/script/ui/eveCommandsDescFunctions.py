#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\eveCommandsDescFunctions.py
from globalConfig.getFunctions import AllowCharacterLogoff
from localization import GetByLabel
from menucheckers import SessionChecker

def GetCmdLogoffHint(*args):
    if not session.charid or not AllowCharacterLogoff(sm.GetService('machoNet')):
        return
    if SessionChecker(session, sm).IsPilotInShipInSpace():
        return GetByLabel('UI/SystemMenu/SafeLogoffHint')
    return GetByLabel('UI/SystemMenu/LogOffHint')
