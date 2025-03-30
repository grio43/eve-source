#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\services\wars\mutualWarInvites.py
from carbon.common.script.sys.service import Service

class MutualWarInvites(Service):
    __guid__ = 'svc.mutualWarInvites'
    __servicename__ = 'mutualWarInvites'
    __displayname__ = 'Mutual War Invite Client Service'
    __dependencies__ = []
    __notifyevents__ = ['OnMutualWarsUpdated_Remote']

    def GetInvites(self):
        invites = sm.RemoteSvc('mutualWarInviteMgr').GetPendingInvitesForSession()
        return invites

    def SendInvite(self, toOwnerID):
        sm.RemoteSvc('mutualWarInviteMgr').SendInviteByPlayer(toOwnerID)

    def WithdrawInvite(self, toOwnerID):
        sm.RemoteSvc('mutualWarInviteMgr').WithdrawInviteByPlayer(toOwnerID)

    def RespondToInvite(self, fromOwnerID, accepts):
        sm.RemoteSvc('mutualWarInviteMgr').RespondToInviteByPlayer(fromOwnerID, accepts)

    def OnMutualWarsUpdated_Remote(self):
        sm.ScatterEvent('OnMutualWarsUpdated')

    def SetInvitesBlocked(self, blocked):
        sm.RemoteSvc('mutualWarInviteMgr').SetInvitesBlockedByPlayer(blocked)

    def IsCorpInvitesBlocked(self):
        return sm.RemoteSvc('mutualWarInviteMgr').IsCorpInvitesBlockedPlayer()
