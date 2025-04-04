#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\services\alliances\all_cso.py
import blue
import localization
from carbon.common.script.sys.service import Service
from carbon.common.script.sys.serviceConst import SERVICE_RUNNING, SERVICE_START_PENDING
from eve.client.script.ui.services.alliances.all_cso_alliance import AllianceO
from eve.client.script.ui.services.alliances.all_cso_applications import AllianceApplicationsO
from eve.client.script.ui.services.alliances.all_cso_members import AllianceMembersO
from eve.client.script.ui.services.alliances.all_cso_relationships import AllianceRelationshipsO
from eve.common.script.net import eveMoniker
from eveexceptions import UserError
from eve.common.lib import appConst as const
DATA_OBJECT_TYPE_MAP = {'alliance': AllianceO,
 'applications': AllianceApplicationsO,
 'members': AllianceMembersO,
 'relationships': AllianceRelationshipsO}

class Alliances(Service):
    __guid__ = 'svc.alliance'
    __notifyevents__ = ['DoSessionChanging',
     'OnSessionChanged',
     'OnAllianceChanged',
     'OnAllianceApplicationChanged',
     'OnAllianceMemberChanged',
     'OnAllianceRelationshipChanged']
    __servicename__ = 'alliance'
    __displayname__ = 'Alliance Client Service'
    __dependencies__ = []
    __functionalobjects__ = ['alliance',
     'members',
     'applications',
     'relationships']

    def __init__(self):
        Service.__init__(self)

    def GetDependencies(self):
        return self.__dependencies__

    def GetObjectNames(self):
        return self.__functionalobjects__

    def Run(self, memStream = None):
        self.LogInfo('Starting Alliances')
        self.bulletins = None
        self.bulletinsTimestamp = 0
        self.state = SERVICE_START_PENDING
        self.__allianceMoniker = None
        self.__allianceMonikerAllianceID = None
        for objectName in self.__functionalobjects__:
            if objectName == 'base':
                continue
            dataObject = None
            dataObjectType = DATA_OBJECT_TYPE_MAP.get(objectName, None)
            if dataObjectType is not None:
                self.LogInfo('Setting', objectName, 'to instance of', dataObjectType)
                dataObject = dataObjectType(self)
            if dataObject is None:
                raise RuntimeError('FunctionalObject not found %s' % objectName)
            setattr(self, objectName, dataObject)

        for objectName in self.__functionalobjects__:
            object = getattr(self, objectName)
            object.DoObjectWeakRefConnections()

        self.state = SERVICE_RUNNING
        if eve.session.allianceid is not None:
            self.GetMoniker()

    def Stop(self, memStream = None):
        self.__allianceMoniker = None
        self.__allianceMonikerAllianceID = None

    def RefreshMoniker(self):
        if self.__allianceMoniker is not None:
            self.__allianceMoniker = None
            self.__allianceMonikerAllianceID = None

    def GetMoniker(self):
        if self.__allianceMoniker is None:
            self.__allianceMoniker = eveMoniker.GetAlliance()
            self.__allianceMonikerAllianceID = eve.session.allianceid
            self.__allianceMoniker.Bind()
        if self.__allianceMonikerAllianceID != eve.session.allianceid:
            if self.__allianceMoniker is not None:
                self.__allianceMoniker = None
            self.__allianceMoniker = eveMoniker.GetAlliance()
            self.__allianceMonikerAllianceID = eve.session.allianceid
            self.__allianceMoniker.Bind()
        return self.__allianceMoniker

    def DoSessionChanging(self, isRemote, session, change):
        if 'corprole' in change:
            old, new = change['corprole']
            if old & const.corpRoleDirector != new & const.corpRoleDirector:
                self.members.members = None
        for objectname in self.__functionalobjects__:
            function = getattr(objectname, 'DoSessionChanging', None)
            if function is None:
                self.LogInfo(objectname, 'DOES NOT PROCESS DoSessionChanging')
            else:
                function(isRemote, session, change)

        if 'charid' in change and change['charid'][0] or 'userid' in change and change['userid'][0]:
            sm.StopService(self.__guid__[4:])

    def OnSessionChanged(self, isremote, sess, change):
        if 'allianceid' in change:
            oldID, newID = change['allianceid']
            self.bulletins = None
            self.bulletinsTimestamp = 0
            if newID is not None:
                self.GetMoniker()
            else:
                self.RefreshMoniker()

    def OnAllianceChanged(self, allianceID, change):
        self.alliance.OnAllianceChanged(allianceID, change)
        self.members.ResetMembers()

    def GetAlliance(self, allianceID = None):
        return self.alliance.GetAlliance(allianceID)

    def GetAlliancePublicInfo(self, allianceID):
        return sm.RemoteSvc('allianceRegistry').GetAlliancePublicInfo(allianceID)

    def ResetCacheForMyAlliance(self):
        self.alliance.ResetCacheForMyAlliance()

    def UpdateAlliance(self, description, url):
        return self.alliance.UpdateAlliance(description, url)

    def GetRankedAlliances(self, maxLen = 100):
        return self.alliance.GetRankedAlliances(maxLen)

    def GetApplications(self, showRejected = False):
        return self.applications.GetApplications(showRejected)

    def UpdateApplication(self, corpID, applicationText, state):
        return self.applications.UpdateApplication(corpID, applicationText, state)

    def OnAllianceApplicationChanged(self, allianceID, corpID, change):
        if allianceID == eve.session.allianceid:
            self.applications.OnAllianceApplicationChanged(allianceID, corpID, change)

    def GetMembers(self):
        return self.members.GetMembers()

    def OnAllianceMemberChanged(self, allianceID, corpID, change):
        if allianceID == eve.session.allianceid:
            self.members.OnAllianceMemberChanged(allianceID, corpID, change)

    def DeclareExecutorSupport(self, corpID):
        self.members.DeclareExecutorSupport(corpID)

    def DeleteMember(self, corpID):
        self.members.DeleteMember(corpID)

    def GetRelationships(self):
        return self.relationships.Get()

    def SetRelationship(self, relationship, toID):
        return self.relationships.Set(relationship, toID)

    def DeleteRelationship(self, toID):
        return self.relationships.Delete(toID)

    def OnAllianceRelationshipChanged(self, allianceID, toID, change):
        if allianceID == eve.session.allianceid:
            self.relationships.OnAllianceRelationshipChanged(allianceID, toID, change)
            sm.ChainEvent('ProcessOnUIAllianceRelationshipChanged', allianceID, toID, change)

    def DeclareWarAgainst(self, againstID, warHQ = None):
        return self.GetMoniker().DeclareWarAgainst(againstID, warHQ)

    def PayBill(self, billID, fromAccountKey):
        if not const.corpRoleAccountant & eve.session.corprole == const.corpRoleAccountant:
            reason = localization.GetByLabel('UI/Corporations/AccessRestrictions/AccountantToPayBills')
            raise UserError('CrpAccessDenied', {'reason': reason})
        return self.GetMoniker().PayBill(billID, fromAccountKey)

    def GetBillBalance(self, billID):
        if const.corpRoleAccountant & eve.session.corprole == const.corpRoleAccountant:
            pass
        elif const.corpRoleJuniorAccountant & eve.session.corprole == const.corpRoleJuniorAccountant:
            pass
        else:
            reason = localization.GetByLabel('UI/Corporations/AccessRestrictions/AccountantToViewBillBalance')
            raise UserError('CrpAccessDenied', {'reason': reason})
        return self.GetMoniker().GetBillBalance(billID)

    def GetBills(self):
        if const.corpRoleAccountant & eve.session.corprole == const.corpRoleAccountant:
            pass
        elif const.corpRoleJuniorAccountant & eve.session.corprole == const.corpRoleJuniorAccountant:
            pass
        else:
            reason = localization.GetByLabel('UI/Corporations/AccessRestrictions/AccountantToViewBills')
            raise UserError('CrpAccessDenied', {'reason': reason})
        return self.GetMoniker().GetBills()

    def GetBillsReceivable(self):
        if const.corpRoleAccountant & eve.session.corprole == const.corpRoleAccountant:
            pass
        elif const.corpRoleJuniorAccountant & eve.session.corprole == const.corpRoleJuniorAccountant:
            pass
        else:
            reason = localization.GetByLabel('UI/Corporations/AccessRestrictions/AccountantToViewBills')
            raise UserError('CrpAccessDenied', {'reason': reason})
        return self.GetMoniker().GetBillsReceivable()

    def GetAllianceBulletins(self):
        if self.bulletins is None or self.bulletinsTimestamp < blue.os.GetWallclockTime():
            self.bulletins = self.GetMoniker().GetBulletins()
            self.bulletinsTimestamp = blue.os.GetWallclockTime() + 15 * const.MIN
        return self.bulletins

    def UpdateBulletinOrder(self, newOrder):
        sm.GetService('alliance').GetMoniker().UpdateBulletinOrder(newOrder)
        self.bulletinsTimestamp = 0

    def GetContactList(self):
        if not session.allianceid:
            return {}
        return self.GetMoniker().GetAllianceContacts()

    def AddAllianceContact(self, contactID, relationshipID):
        self.GetMoniker().AddAllianceContact(contactID, relationshipID)

    def EditAllianceContact(self, contactID, relationshipID):
        self.GetMoniker().EditAllianceContact(contactID, relationshipID)

    def RemoveAllianceContacts(self, contactIDs):
        self.GetMoniker().RemoveAllianceContacts(contactIDs)

    def EditContactsRelationshipID(self, contactIDs, relationshipID):
        self.GetMoniker().EditContactsRelationshipID(contactIDs, relationshipID)

    def GetLabels(self):
        return self.GetMoniker().GetLabels()

    def CreateLabel(self, name, color = 0):
        return self.GetMoniker().CreateLabel(name, color)

    def DeleteLabel(self, labelID):
        self.GetMoniker().DeleteLabel(labelID)

    def EditLabel(self, labelID, name = None, color = None):
        self.GetMoniker().EditLabel(labelID, name, color)

    def AssignLabels(self, contactIDs, labelMask):
        self.GetMoniker().AssignLabels(contactIDs, labelMask)

    def RemoveLabels(self, contactIDs, labelMask):
        self.GetMoniker().RemoveLabels(contactIDs, labelMask)

    def GMAcceptApplication(self, corporationID):
        self.GetMoniker().GMForceAcceptApplication(corporationID)

    def GetPrimeTimeInfo(self):
        return self.GetMoniker().GetPrimeTimeInfo()

    def SetPrimeHour(self, hour):
        self.GetMoniker().SetPrimeHour(hour)

    def GetCapitalSystemInfo(self):
        return self.GetMoniker().GetCapitalSystemInfo()

    def SetCapitalSystem(self, solarSystemID):
        self.GetMoniker().SetCapitalSystem(solarSystemID)
        sm.ScatterEvent('OnUpdateCapitalInfo')

    def CancelCapitalSystemTransition(self):
        self.GetMoniker().CancelCapitalSystemTransition()
        sm.ScatterEvent('OnUpdateCapitalInfo')
