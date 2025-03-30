#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\conditions\wallet.py
from .base import Condition

class WalletBalance(Condition):
    atom_id = None

    def __init__(self, minimum_amount = None, **kwargs):
        super(WalletBalance, self).__init__(**kwargs)
        self.minimum_amount = self.get_atom_parameter_value('minimum_amount', minimum_amount)

    def _get_amount(self):
        return 0

    def validate(self, **kwargs):
        return self._get_amount() >= self.minimum_amount

    @classmethod
    def get_subtitle(cls, minimum_amount = None, **kwargs):
        return str(cls.get_atom_parameter_value('minimum_amount', minimum_amount))


class IskBalance(WalletBalance):
    atom_id = 558

    def _get_amount(self):
        from nodegraph.client.getters.wallet import GetISKAmount
        return GetISKAmount().get_values()['isk_amount']


class PlexBalance(WalletBalance):
    atom_id = 557

    def _get_amount(self):
        from nodegraph.client.getters.wallet import GetPlexBalance
        return GetPlexBalance().get_values()['plex_balance']
