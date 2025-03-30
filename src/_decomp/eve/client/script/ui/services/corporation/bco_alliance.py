#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\services\corporation\bco_alliance.py
import blue
from eve.client.script.ui.services.corporation.bco_base import BaseCorpObject
from eve.client.script.ui.shared.neocom.corporation import corpUISignals

class CorpAllianceO(BaseCorpObject):
    __guid__ = 'corpObject.alliance'

    def __init__(self, boundObject):
        BaseCorpObject.__init__(self, boundObject)
        self.__applicationsByAllianceID = None

    def DoSessionChanging(self, isRemote, session, change):
        if 'corpid' in change or 'allianceid' in change:
            self.__applicationsByAllianceID = None

    def GetSuggestedAllianceShortNames(self, allianceName):
        return self.GetCorpRegistry().GetSuggestedAllianceShortNames(allianceName)

    def CreateAlliance(self, allianceName, shortName, description, url):
        return self.GetCorpRegistry().CreateAlliance(allianceName, shortName, description, url)

    def GetAllianceApplications(self):
        if self.__applicationsByAllianceID is None:
            self.__applicationsByAllianceID = self.GetCorpRegistry().GetAllianceApplications()
        return self.__applicationsByAllianceID

    def DeleteAllianceApplication(self, allianceID):
        return self.GetCorpRegistry().DeleteAllianceApplication(allianceID)

    def OnAllianceApplicationChanged(self, allianceID, corpID, change):
        try:
            if corpID == eve.session.corpid:
                bAdd, bRemove = self.GetAddRemoveFromChange(change)
                if self.__applicationsByAllianceID is not None:
                    if bAdd:
                        if len(change) != len(self.__applicationsByAllianceID.columns):
                            self.LogWarn('IncorrectNumberOfColumns ignoring change as Add change:', change)
                            return
                        line = []
                        for columnName in self.__applicationsByAllianceID.columns:
                            line.append(change[columnName][1])

                        self.__applicationsByAllianceID[allianceID] = blue.DBRow(self.__applicationsByAllianceID.header, line)
                    else:
                        if not self.__applicationsByAllianceID.has_key(allianceID):
                            return
                        if bRemove:
                            del self.__applicationsByAllianceID[allianceID]
                        else:
                            application = self.__applicationsByAllianceID[allianceID]
                            for columnName in change.iterkeys():
                                setattr(application, columnName, change[columnName][1])

        finally:
            corpUISignals.on_alliance_application_changed(allianceID, corpID, change)
