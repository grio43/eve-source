#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\playerprogression\plexprogressionnotifier.py
from inventorycommon.const import typePlex
from inventorycommon.typeHelpers import GetAveragePrice
from log import LogException
from playerprogression.playerprogressionnotifier import PlayerProgressionNotifier

class PlexProgressionNotifier(PlayerProgressionNotifier):
    __notifyevents__ = ['OnAurumChangeFromVgs']
    NOTIFIER_ID = 'plex'

    def __init__(self):
        PlayerProgressionNotifier.__init__(self)
        sm.RegisterNotify(self)
        self.reset_value()
        self.plex_price = GetAveragePrice(typePlex) or 0.0

    def reset_value(self):
        self.set_value(None)

    def should_update_calculation(self):
        if self.get_value() is None:
            return True
        return False

    def calculate_progression(self):
        plex_worth = None
        try:
            account = sm.GetService('vgsService').GetStore().GetAccount()
            plex_amount = account.GetAurumBalance() or 0.0
            plex_worth = self.calculate_plex_worth(plex_amount)
        except Exception as exception:
            msg = 'Failed to retrieve PLEX worth, cause: %s' % getattr(exception, 'msg', str(exception))
            LogException(msg)

        if plex_worth is not None:
            self.set_value(plex_worth)

    def calculate_plex_worth(self, plex_amount):
        return self.plex_price * plex_amount

    def OnAurumChangeFromVgs(self, change_data):
        plex_amount = change_data['balance']
        new_plex_worth = self.calculate_plex_worth(plex_amount)
        self.set_value(new_plex_worth)
        self.start_updates()
