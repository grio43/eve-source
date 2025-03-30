#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\services\wars\warPermit.py
from carbon.common.script.sys.service import Service
from eve.common.script.sys.idCheckers import IsAlliance

class WarPermit(Service):
    __guid__ = 'svc.warPermit'
    __servicename__ = 'warPermit'
    __displayname__ = 'War Permit Service'
    __notifyevents__ = ['OnAllowWarUpdated']

    def __init__(self, *args):
        Service.__init__(self)
        self.myCorpAllowsWar = None

    def CanDeclareWarAgainst(self, otherID = None):
        if self.GetMyCorpsWarPermitStatus():
            if otherID is None:
                return True
            if IsAlliance(otherID):
                otherID = sm.RemoteSvc('allianceRegistry').GetAlliancePublicInfo(otherID).executorCorpID
            return self.GetWarPermitStatusForCorp(otherID)
        return False

    def DoesMyCorpHaveNegativeWarPermit(self):
        return self.GetMyCorpsWarPermitStatus() == False

    def GetMyCorpsWarPermitStatus(self):
        if self.myCorpAllowsWar is None:
            corpInfo = sm.GetService('corp').GetCorporation(session.corpid)
            self.myCorpAllowsWar = corpInfo.allowWar
        return self.myCorpAllowsWar

    def GetWarPermitStatusForCorp(self, corpID):
        if corpID == session.corpid:
            return self.GetMyCorpsWarPermitStatus()
        corpInfo = sm.RemoteSvc('corpmgr').GetPublicInfo(corpID)
        return corpInfo.allowWar

    def OnAllowWarUpdated(self, corpID, allowWar):
        if corpID != session.corpid:
            raise RuntimeError("Getting updates about a corp I don't belong to")
        self.myCorpAllowsWar = allowWar
        self.ResetCaches()

    def OnSessionChanged(self, isRemote, session, change):
        if 'corpid' in change or 'allianceid' in change:
            self.myCorpAllowsWar = None

    def ResetCaches(self):
        sm.GetService('corp').ResetCacheForMyCorp()
        sm.GetService('alliance').ResetCacheForMyAlliance()
