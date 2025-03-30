#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\services\corporation\bco_members.py
import uthread
from caching.memoize import Memoize
from eve.client.script.ui.services.corporation.bco_base import BaseCorpObject
from eve.common.script.util.pagedCollection import PagedCollection
from evecorporation.roles import iter_roles

class PagedCorpMembers(PagedCollection):
    __notifyevents__ = ['OnCorporationMemberChanged']

    def __init__(self, totalCount):
        super(PagedCorpMembers, self).__init__()
        self.notify = []
        self.additions = []
        self.totalCount = totalCount
        sm.RegisterNotify(self)
        self.charIdIdx = {}

    def PopulatePage(self, page):
        if not self.page or page > self.page:
            rs = sm.GetService('corp').GetMembersPaged(page)
            self.Add(rs)
        start = self.perPage * (page - 1)
        return self[start:start + self.perPage]

    def PopulateByMemberIDs(self, memberIDs):
        missingKeys = []
        for eachID in memberIDs:
            if eachID not in self.charIdIdx:
                missingKeys.append(eachID)

        rows = sm.GetService('corp').GetMembersByIds(missingKeys)
        for member in rows:
            self.charIdIdx[member.characterID] = member

    def GetMember(self, memberID):
        return self.charIdIdx.get(memberID)

    def Add(self, resultSet):
        super(PagedCorpMembers, self).Add(resultSet)
        for character in resultSet:
            self.charIdIdx[character.characterID] = character

    def append(self, item):
        super(PagedCorpMembers, self).append(item)
        self.charIdIdx[item.characterID] = item

    def OnCorporationMemberChanged(self, corporationID, memberID, changes):
        member = self.GetMember(memberID)
        if 'corporationID' in changes:
            oldCorpID, newCorpID = changes['corporationID']
            if oldCorpID == eve.session.corpid:
                if not member:
                    self.totalCount -= 1
                    return
                try:
                    self.remove(member)
                except ValueError:
                    pass

            elif newCorpID == eve.session.corpid:
                if self.page == self.PageCount():
                    newMember = sm.GetService('corp').GetMembersByIds([memberID])[0]
                    if newMember.characterID not in (i.characterID for i in self.collection):
                        self.append(newMember)
                else:
                    self.totalCount += 1
        elif member:
            for key, values in changes.iteritems():
                if hasattr(member, key):
                    oldValue, newValue = values
                    member[key] = newValue

        for listener in self.notify:
            listener.DataChanged(memberID, changes)

    def AddListener(self, listener):
        if listener not in self.notify:
            self.notify.append(listener)

    def RemoveListener(self, listener):
        if listener in self.notify:
            self.notify.remove(listener)


class CorporationMembersO(BaseCorpObject):
    __guid__ = 'corpObject.members'

    def __init__(self, boundObject):
        BaseCorpObject.__init__(self, boundObject)
        self.__lock = uthread.Semaphore()
        self.__members = None
        self.__memberIDs = None

    def DoSessionChanging(self, isRemote, session, change):
        if 'corpid' in change:
            self.__members = None
            self.__memberIDs = None

    def OnSessionChanged(self, isRemote, session, change):
        if 'corpid' not in change:
            return
        oldID, newID = change['corpid']
        if newID is None:
            return
        self.__PrimeEveOwners()

    def PrimeCorpInformation(self):
        self.GetMemberIDs()
        self.corp__corporations.GetCorporation()

    def __PrimeEveOwners(self):
        with self.__lock:
            eveowners = self.GetCorpRegistry().GetEveOwners()
            self.__memberIDs = []
            for owner in eveowners:
                if not cfg.eveowners.data.has_key(owner.ownerID):
                    cfg.eveowners.data[owner.ownerID] = list(owner) + [None]
                self.__memberIDs.append(owner.ownerID)

    def __len__(self):
        return len(self.GetMembers())

    def GetMemberIDs(self):
        if self.__memberIDs is None:
            self.__PrimeEveOwners()
        return self.__memberIDs

    def GetMembers(self):
        memberCount = len(self.GetMemberIDs())
        if self.__members is None:
            self.__members = PagedCorpMembers(totalCount=memberCount)
        return self.__members

    @Memoize(0.1)
    def GetMember(self, charID):
        if charID not in self.GetMemberIDs():
            return
        if self.__members is not None:
            member = self.__members.GetMember(charID)
            if member:
                return member
        return self.GetCorpRegistry().GetMember(charID)

    def GetMembersPaged(self, page):
        return self.GetCorpRegistry().GetMembersPaged(page)

    def GetMembersByIds(self, memberIDs):
        return self.GetCorpRegistry().GetMembersByIds(memberIDs)

    def GetMembersAsEveOwners(self):
        return [ cfg.eveowners.Get(charID) for charID in self.GetMemberIDs() ]

    def MemberCanCreateCorporation(self):
        if sm.GetService('wallet').GetWealth() < const.corporationStartupCost:
            return 0
        if not sm.GetService('skills').GetSkill(const.typeCorporationManagement):
            return 0
        if self.corp__corporations.GetCorporation().ceoID == eve.session.charid:
            return 0
        return 1

    def GetMyGrantableRoles(self):
        charIsCEO = self.corp__corporations.GetCorporation().ceoID == eve.session.charid
        charIsActiveCEO = charIsCEO and eve.session.corprole & const.corpRoleDirector == const.corpRoleDirector
        grantableRoles = 0
        grantableRolesAtHQ = 0
        grantableRolesAtBase = 0
        grantableRolesAtOther = 0
        member = self.GetMember(eve.session.charid)
        if member is not None:
            if charIsActiveCEO or const.corpRoleDirector == member.roles & const.corpRoleDirector:
                locationalRoles = self.boundObject.GetLocationalRoles()
                for roleID, role in iter_roles():
                    if roleID not in locationalRoles:
                        if roleID == const.corpRoleDirector:
                            if charIsActiveCEO:
                                grantableRoles |= roleID
                        else:
                            grantableRoles |= roleID
                    else:
                        grantableRolesAtHQ |= roleID
                        grantableRolesAtBase |= roleID
                        grantableRolesAtOther |= roleID

            elif charIsCEO:
                pass
            else:
                grantableRoles = long(member.grantableRoles)
                grantableRolesAtHQ = long(member.grantableRolesAtHQ)
                grantableRolesAtBase = long(member.grantableRolesAtBase)
                grantableRolesAtOther = long(member.grantableRolesAtOther)
                if member.titleMask:
                    for titleID, title in self.corp__titles.GetTitles().iteritems():
                        if member.titleMask & titleID == titleID:
                            grantableRoles |= title.grantableRoles
                            grantableRolesAtHQ |= title.grantableRolesAtHQ
                            grantableRolesAtBase |= title.grantableRolesAtBase
                            grantableRolesAtOther |= title.grantableRolesAtOther

        return (grantableRoles,
         grantableRolesAtHQ,
         grantableRolesAtBase,
         grantableRolesAtOther)

    def OnCorporationMemberChanged(self, corporationID, memberID, change):
        if self.__memberIDs is None:
            return
        if 'corporationID' in change:
            oldCorpID, newCorpID = change['corporationID']
            if oldCorpID == eve.session.corpid:
                if memberID in self.__memberIDs:
                    self.__memberIDs.remove(memberID)
            elif newCorpID == eve.session.corpid:
                if memberID not in self.__memberIDs:
                    self.__memberIDs.append(memberID)

    def UpdateMember(self, charIDToUpdate, title = None, divisionID = None, squadronID = None, roles = None, grantableRoles = None, rolesAtHQ = None, grantableRolesAtHQ = None, rolesAtBase = None, grantableRolesAtBase = None, rolesAtOther = None, grantableRolesAtOther = None, baseID = None, titleMask = None, blockRoles = None):
        return self.GetCorpRegistry().UpdateMember(charIDToUpdate, title, divisionID, squadronID, roles, grantableRoles, rolesAtHQ, grantableRolesAtHQ, rolesAtBase, grantableRolesAtBase, rolesAtOther, grantableRolesAtOther, baseID, titleMask, blockRoles)

    def UpdateMembers(self, rows):
        return self.GetCorpRegistry().UpdateMembers(rows)

    def SetAccountKey(self, accountKey):
        return self.GetCorpRegistry().SetAccountKey(accountKey)

    def ExecuteActions(self, targetIDs, actions):
        remoteActions = []
        for action in actions:
            verb, property, value = action
            if verb != const.CTV_COMMS:
                remoteActions.append(action)
                continue

        return self.GetCorpRegistry().ExecuteActions(targetIDs, remoteActions)

    def MemberBlocksRoles(self):
        blocksRoles = 0
        member = self.GetMember(eve.session.charid)
        if member is not None:
            if member.blockRoles is not None:
                blocksRoles = member.blockRoles
        return blocksRoles

    def GetNumberOfPotentialCEOs(self):
        return self.GetCorpRegistry().GetNumberOfPotentialCEOs()
