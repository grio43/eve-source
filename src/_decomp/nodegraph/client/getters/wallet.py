#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\getters\wallet.py
from .base import GetterAtom

class GetISKAmount(GetterAtom):
    atom_id = 374

    def get_values(self):
        return {'isk_amount': sm.GetService('wallet').GetWealth()}


class GetPlexBalance(GetterAtom):
    atom_id = 556

    def get_values(self):
        account = sm.GetService('vgsService').GetStore().GetAccount()
        return {'plex_balance': account.GetAurumBalance()}
