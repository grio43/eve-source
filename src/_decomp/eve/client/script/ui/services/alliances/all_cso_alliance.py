#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\services\alliances\all_cso_alliance.py
import blue
import utillib
from carbon.common.script.sys.crowset import CRowset
from eve.client.script.ui.services.alliances.all_cso_base import BaseAllianceObject
from eve.client.script.ui.shared.neocom.corporation import corpUISignals

class AllianceO(BaseAllianceObject):
    __guid__ = 'allianceObject.alliance'

    def __init__(self, boundObject):
        BaseAllianceObject.__init__(self, boundObject)
        self.alliancesByAllianceID = None
        self.rankedAlliances = utillib.KeyVal(time=None, alliances=None, standings=None, maxLen=None)

    def DoSessionChanging(self, isRemote, session, change):
        pass

    def GetRankedAlliances(self, maxLen = 100):
        if self.rankedAlliances.time is not None:
            if self.rankedAlliances.maxLen != maxLen or blue.os.TimeDiffInMs(self.rankedAlliances.time, blue.os.GetWallclockTime()) > 5000:
                self.rankedAlliances.time = None
        if self.rankedAlliances.time is None:
            self.rankedAlliances.time = blue.os.GetWallclockTime()
            self.rankedAlliances.maxLen = maxLen
            self.rankedAlliances.alliances = sm.RemoteSvc('allianceRegistry').GetRankedAlliances(maxLen)
            self.rankedAlliances.standings = {}
            for a in self.rankedAlliances.alliances:
                s = sm.GetService('standing').GetStanding(eve.session.corpid, a.allianceID)
                self.rankedAlliances.standings[a.allianceID] = s

        return self.rankedAlliances

    def UpdateAlliance(self, description, url):
        return self.GetMoniker().UpdateAlliance(description, url)

    def GetAlliance(self, allianceID = None):
        if allianceID is None:
            allianceID = eve.session.allianceid
        if allianceID is None:
            raise RuntimeError('NoSuchAlliance')
        if self.alliancesByAllianceID is not None and self.alliancesByAllianceID.has_key(allianceID):
            return self.alliancesByAllianceID[allianceID]
        alliance = None
        if allianceID == eve.session.allianceid:
            alliance = self.GetMoniker().GetAlliance()
        else:
            alliance = sm.RemoteSvc('allianceRegistry').GetAlliance(allianceID)
        self.LoadAlliance(alliance)
        return self.alliancesByAllianceID[allianceID]

    def LoadAlliance(self, alliance):
        if self.alliancesByAllianceID is None:
            self.alliancesByAllianceID = CRowset(alliance.__header__, []).Index('allianceID')
        self.alliancesByAllianceID[alliance.allianceID] = alliance

    def OnAllianceChanged(self, allianceID, change):
        bAdd, bRemove = self.GetAddRemoveFromChange(change)
        if self.alliancesByAllianceID is not None:
            if bAdd:
                if len(change) != len(self.alliancesByAllianceID.columns):
                    self.LogWarn('IncorrectNumberOfColumns ignoring change as Add change:', change)
                    return
                line = []
                for columnName in self.alliancesByAllianceID.columns:
                    line.append(change[columnName][1])

                self.alliancesByAllianceID[allianceID] = blue.DBRow(self.alliancesByAllianceID.header, line)
            else:
                if not self.alliancesByAllianceID.has_key(allianceID):
                    return
                if bRemove:
                    del self.alliancesByAllianceID[allianceID]
                else:
                    alliance = self.alliancesByAllianceID[allianceID]
                    for columnName in change.iterkeys():
                        setattr(alliance, columnName, change[columnName][1])

                    if cfg.allianceshortnames.data.has_key(allianceID):
                        header = cfg.allianceshortnames.header
                        line = cfg.allianceshortnames.data[allianceID]
                        i = -1
                        for columnName in header:
                            i = i + 1
                            if not change.has_key(columnName):
                                continue
                            line[i] = change[columnName][1]

        corpUISignals.on_alliance_changed(allianceID, change)

    def ResetCacheForMyAlliance(self):
        allianceID = session.allianceid
        if not allianceID:
            return
        if self.alliancesByAllianceID and allianceID in self.alliancesByAllianceID:
            self.alliancesByAllianceID.pop(allianceID, None)
