#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\playerprogression\assetnetworthnotifier.py
from carbon.common.lib.const import HOUR, MSEC
from playerprogression.timedplayerprogressionnotifier import TimedPlayerProgressionNotifier
from log import LogException

class AssetNetWorthProgression(object):

    def __init__(self, asset_worth, plex_worth):
        self.asset_worth = asset_worth
        self.plex_worth = plex_worth


class AssetNetWorthNotifier(TimedPlayerProgressionNotifier):
    __notifyevents__ = ['OnItemChangeProcessed']
    NOTIFIER_ID = 'assets'
    UPDATE_NOT_RECENT_AFTER_MIN = 12 * HOUR
    UPDATE_TIMER_DELAY_MSEC = 12 * HOUR / MSEC

    def __init__(self):
        TimedPlayerProgressionNotifier.__init__(self)
        sm.RegisterNotify(self)
        self.inv_cache = sm.GetService('invCache')

    def get_value(self):
        value = settings.char.ui.Get('%s_value' % self.NOTIFIER_ID, None)
        is_valid = isinstance(value, dict) and 'asset_worth' in value and 'plex_worth' in value
        if not is_valid:
            self.set_update_requirement(True)
            return AssetNetWorthProgression(0, 0)
        return AssetNetWorthProgression(value['asset_worth'], value['plex_worth'])

    def should_update_calculation(self):
        if self.get_value() is None:
            return True
        if self.get_last_update_date() is None:
            return True
        if self.is_last_update_recent():
            return False
        if self.get_update_requirement():
            return True
        return False

    def calculate_progression(self):
        self.set_update_requirement(False)
        asset_net_worth = None
        try:
            inv_container = self.inv_cache.GetInventory(const.containerGlobal)
            asset_worth, plex_worth = inv_container.GetAssetWorth()
            asset_net_worth = AssetNetWorthProgression(asset_worth, plex_worth)
        except Exception as exception:
            msg = 'Failed to retrieve asset worth, cause: %s' % getattr(exception, 'msg', str(exception))
            LogException(msg)

        if asset_net_worth is not None:
            value = {'asset_worth': asset_net_worth.asset_worth,
             'plex_worth': asset_net_worth.plex_worth}
            self.set_value(value)

    def OnItemChangeProcessed(self, item, change):
        self.set_update_requirement(True)
