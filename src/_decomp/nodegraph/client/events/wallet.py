#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\events\wallet.py
from .base import Event

class IskBalanceChanged(Event):
    atom_id = 559
    __notifyevents__ = ['OnPersonalAccountChangedClient']

    def OnPersonalAccountChangedClient(self, *args, **kwargs):
        self.invoke()


class PlexBalanceChanged(Event):
    atom_id = 560

    def _register(self):
        account = sm.GetService('vgsService').GetStore().GetAccount()
        account.SubscribeToAurumBalanceChanged(self._plex_balance_changed)

    def _unregister(self):
        account = sm.GetService('vgsService').GetStore().GetAccount()
        account.UnsubscribeFromAurumBalanceChanged(self._plex_balance_changed)

    def _plex_balance_changed(self, new_balance, old_balance):
        self.invoke(difference=new_balance - old_balance)
