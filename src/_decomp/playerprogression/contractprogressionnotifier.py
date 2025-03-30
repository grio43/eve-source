#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\playerprogression\contractprogressionnotifier.py
from carbon.common.lib.const import HOUR, MSEC
from playerprogression.timedplayerprogressionnotifier import TimedPlayerProgressionNotifier

class ContractProgression(object):

    def __init__(self, isk_escrow, items_escrow):
        self.isk_escrow = isk_escrow
        self.items_escrow = items_escrow


class ContractProgressionNotifier(TimedPlayerProgressionNotifier):
    __notifyevents__ = ['OnContractEscrowChanged']
    NOTIFIER_ID = 'contract'
    UPDATE_NOT_RECENT_AFTER_MIN = 12 * HOUR
    UPDATE_TIMER_DELAY_MSEC = 12 * HOUR / MSEC

    def __init__(self, get_contract_escrow_function):
        TimedPlayerProgressionNotifier.__init__(self)
        sm.RegisterNotify(self)
        self.get_contract_escrow_function = get_contract_escrow_function

    def get_value(self):
        value = settings.char.ui.Get('%s_value' % self.NOTIFIER_ID, None)
        is_valid = isinstance(value, dict) and 'isk_escrow' in value and 'items_escrow' in value
        if not is_valid:
            self.set_update_requirement(True)
            return ContractProgression(0, 0)
        return ContractProgression(value['isk_escrow'], value['items_escrow'])

    def should_update_calculation(self):
        if self.get_value() is None:
            return True
        if self.get_last_update_date() is None:
            return True
        if self.is_last_update_recent():
            return False
        return self.get_update_requirement()

    def calculate_progression(self):
        self.set_update_requirement(False)
        total_isk_escrow, total_items_escrow = self.get_contract_escrow_function()
        value = {'isk_escrow': total_isk_escrow,
         'items_escrow': total_items_escrow}
        self.set_value(value)

    def OnContractEscrowChanged(self):
        self.set_update_requirement(True)
