#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\services\alliances\all_cso_applications.py
import blue
from eve.client.script.ui.services.alliances.all_cso_base import BaseAllianceObject
from eve.client.script.ui.shared.neocom.corporation import corpUISignals
from eve.common.lib import appConst as const

class AllianceApplicationsO(BaseAllianceObject):
    __guid__ = 'allianceObject.applications'

    def __init__(self, boundObject):
        BaseAllianceObject.__init__(self, boundObject)
        self.applications = None

    def DoSessionChanging(self, isRemote, session, change):
        if 'allianceid' in change:
            self.applications = None

    def GetApplications(self, showRejected = False):
        if self.applications is None:
            self.applications = self.GetMoniker().GetApplications()
        if showRejected:
            return self.applications
        ret = {}
        for corpID in self.applications:
            app = self.applications[corpID]
            if app.state != const.allianceApplicationRejected:
                ret[corpID] = app

        return ret

    def UpdateApplication(self, corpID, applicationText, state):
        return self.GetMoniker().UpdateApplication(corpID, applicationText, state)

    def OnAllianceApplicationChanged(self, allianceID, corpID, change):
        if allianceID != eve.session.allianceid:
            return
        bAdd, bRemove = self.GetAddRemoveFromChange(change)
        if self.applications is not None:
            if bAdd:
                if len(change) != len(self.applications.columns):
                    self.LogWarn('IncorrectNumberOfColumns ignoring change as Add change:', change)
                    return
                line = []
                for columnName in self.applications.columns:
                    line.append(change[columnName][1])

                self.applications[corpID] = blue.DBRow(self.applications.header, line)
            else:
                if not self.applications.has_key(corpID):
                    return
                if bRemove:
                    del self.applications[corpID]
                else:
                    application = self.applications[corpID]
                    for columnName in change.iterkeys():
                        setattr(application, columnName, change[columnName][1])

        corpUISignals.on_alliance_application_changed(allianceID, corpID, change)
