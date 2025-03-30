#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\vgs\common\listeners.py
from carbon.common.script.util.timerstuff import AutoTimer
from eveexceptions import UserError
import log

class PlexWithdrawalListener(object):
    __notifyevents__ = ['OnPlexItemAddedToInventory', 'OnPlexWithdrawFailed']

    def __init__(self, user_id, amount, reference):
        sm.RegisterNotify(self)
        self.received_event = False
        self.received_item_id = None
        self.user_id = user_id
        self.amount = amount
        self.reference = reference
        self.expiry_timer = AutoTimer(10000, self.timeout)

    def timeout(self):
        self.received_event = True
        self.expiry_timer.KillTimer()
        log.LogError('Timeout waiting for withdrawal result event for user', self.user_id, 'with reference', self.reference, ', user may have lost', self.amount, 'PLX or it may be sitting in inventory')
        raise UserError('PlexWithdrawalTimeout')

    def OnPlexItemAddedToInventory(self, item_id, reference):
        if reference == self.reference:
            self.received_event = True
            self.received_item_id = item_id
            self.expiry_timer.KillTimer()

    def OnPlexWithdrawFailed(self, error_key, reference):
        if reference == self.reference:
            self.received_event = True
            self.expiry_timer.KillTimer()
            raise UserError(error_key)


class PlexDepositListener(object):
    __notifyevents__ = ['OnPlexDepositFailed', 'OnPlexDeposited']

    def __init__(self, user_id, amount, reference):
        sm.RegisterNotify(self)
        self.received_event = False
        self.deposited = False
        self.user_id = user_id
        self.amount = amount
        self.reference = reference
        self.expiry_timer = AutoTimer(10000, self.timeout)

    def timeout(self):
        self.received_event = True
        self.expiry_timer.KillTimer()
        log.LogError('Timeout waiting for deposit result event for user', self.user_id, 'with reference', self.reference, ', user may have lost', self.amount, 'PLX or it may be sitting in inventory')
        raise UserError('PlexDepositTimeout')

    def OnPlexDeposited(self, reference):
        if reference == self.reference:
            self.received_event = True
            self.deposited = True
            self.expiry_timer.KillTimer()

    def OnPlexDepositFailed(self, error_key, reference):
        if reference == self.reference:
            self.received_event = True
            self.expiry_timer.KillTimer()
            raise UserError(error_key)
