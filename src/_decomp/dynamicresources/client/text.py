#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dynamicresources\client\text.py
import eveLocalization
import localization
from localization.parser import _Tokenize
from dynamicresources.common.ess.const import LINK_ERROR_ALREADY_LINKED, LINK_ERROR_INVALID_SHIP_TYPE, LINK_ERROR_LINK_OCCUPIED, LINK_ERROR_NO_BALLPARK, LINK_ERROR_NOT_ON_GRID, LINK_ERROR_OUT_OF_RANGE, LINK_ERROR_SYSTEM_OFFLINE, UNLINKED_PROXIMITY, UNLINKED_SHIP_CHANGE

class Label(object):

    def __init__(self, label, _placeholder = None):
        self.label = label
        self._placeholder = _placeholder

    def __call__(self, **kwargs):
        if self._placeholder:
            if not isinstance(self._placeholder, unicode):
                self._placeholder = self._placeholder.decode('utf8')
            tokens = _Tokenize(self._placeholder)
            return eveLocalization.Parse(self._placeholder, localization.const.LOCALE_SHORT_ENGLISH, tokens, **kwargs)
        return localization.GetByLabel(self.label, **kwargs)


title_main_bank = Label('UI/ESS/MainBankCardTitle')
action_hack_main_bank = Label('UI/ESS/LinkToMainBank')
main_bank_hack_initiated = Label('UI/ESS/MainBankHackingInitiated')
action_disconnect_main_bank = Label('UI/ESS/UnlinkFromMainBank')
main_bank_disconnected = Label('UI/ESS/MainBankLinkDisconnected')
main_bank_hack_successful = Label('UI/ESS/MainBankHackingSuccess')
title_reserve_bank = Label('UI/ESS/ReserveBankCardTitle')
action_unlock_reserve_bank = Label('UI/ESS/UnlockReserveBank')
action_link_to_reserve_bank = Label('UI/ESS/LinkToReserveBank')
action_unlink_from_reserve_bank = Label('UI/ESS/UnlinkFromReserveBank')
reserve_bank_linked = Label('UI/ESS/ReserveBankLinked')
reserve_bank_unlinked = Label('UI/ESS/ReserveBankUnlinked')
title_select_key = Label('UI/ESS/SelectKeyTitle')
action_use_key = Label('UI/ESS/ConfirmKeySelection')
hint_key_info = Label('UI/ESS/KeyHintDescription')
hint_key_unavailable = Label('UI/ESS/KeyHintUnavailable')
status_out_of_range = Label('UI/ESS/StateOutOfRange')
status_offline = Label('UI/ESS/StatusOffline')
link_error_offline = Label('UI/ESS/LinkErrorOffline')
link_error_out_of_range = Label('UI/ESS/LinkErrorOutOfRange')
link_error_invalid_ship = Label('UI/ESS/LinkErrorInvalidShip')
link_error_occupied = Label('UI/ESS/LinkErrorOccupied')
link_error_already_linked = Label('UI/ESS/LinkErrorAlreadyLinked')
unlink_reason_ship_change = Label('UI/ESS/UnlinkReasonShipChange')
unlink_reason_out_of_range = Label('UI/ESS/UnlinkReasonOutOfRange')

def link_error_description(error):
    if error == LINK_ERROR_SYSTEM_OFFLINE:
        return link_error_offline()
    if error in (LINK_ERROR_NOT_ON_GRID, LINK_ERROR_OUT_OF_RANGE, LINK_ERROR_NO_BALLPARK):
        return link_error_out_of_range()
    if error == LINK_ERROR_INVALID_SHIP_TYPE:
        return link_error_invalid_ship()
    if error == LINK_ERROR_LINK_OCCUPIED:
        return link_error_occupied()
    if error == LINK_ERROR_ALREADY_LINKED:
        return link_error_already_linked()


def unlink_reason_description(reason):
    if reason == UNLINKED_PROXIMITY:
        return unlink_reason_out_of_range()
    if reason == UNLINKED_SHIP_CHANGE:
        return unlink_reason_ship_change()
