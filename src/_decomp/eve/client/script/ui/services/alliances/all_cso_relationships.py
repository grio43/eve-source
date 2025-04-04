#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\services\alliances\all_cso_relationships.py
import blue
from eve.client.script.ui.services.alliances.all_cso_base import BaseAllianceObject
from eve.client.script.ui.shared.neocom.corporation import corpUISignals

class AllianceRelationshipsO(BaseAllianceObject):
    __guid__ = 'allianceObject.relationships'

    def __init__(self, boundObject):
        BaseAllianceObject.__init__(self, boundObject)
        self.relationships = None

    def DoSessionChanging(self, isRemote, session, change):
        if 'allianceid' in change:
            self.relationships = None

    def Get(self):
        if self.relationships is None:
            self.relationships = self.GetMoniker().GetRelationships()
        return self.relationships

    def Set(self, relationship, toID):
        relationships = self.Get()
        if relationships.has_key(toID):
            if relationships[toID] == relationship:
                return
        self.GetMoniker().SetRelationship(relationship, toID)

    def Delete(self, toID):
        relationships = self.Get()
        if not relationships.has_key(toID):
            return
        return self.GetMoniker().DeleteRelationship(toID)

    def OnAllianceRelationshipChanged(self, allianceID, toID, change):
        if allianceID != eve.session.allianceid:
            return
        bAdd, bRemove = self.GetAddRemoveFromChange(change)
        if self.relationships is not None:
            if bAdd:
                if len(change) != len(self.relationships.columns):
                    self.LogWarn('IncorrectNumberOfColumns ignoring change as Add change:', change)
                    return
                line = []
                for columnName in self.relationships.columns:
                    line.append(change[columnName][1])

                self.relationships[toID] = blue.DBRow(self.relationships.header, line)
            else:
                if not self.relationships.has_key(toID):
                    return
                if bRemove:
                    del self.relationships[toID]
                else:
                    member = self.relationships[toID]
                    for columnName in change.iterkeys():
                        setattr(member, columnName[0], change[columnName][1])

        corpUISignals.on_alliance_relationship_changed(allianceID, toID, change)
