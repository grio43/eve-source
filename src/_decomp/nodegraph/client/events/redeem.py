#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\events\redeem.py
from .base import Event

class RedeemingQueueChanged(Event):
    atom_id = 561
    __notifyevents__ = ['OnRedeemingTokensUpdated']

    def OnRedeemingTokensUpdated(self, *args, **kwargs):
        self.invoke()
