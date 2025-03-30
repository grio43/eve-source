#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\wallet\panels\personal\personalDonateLPPanel.py
from corporation.common import FLAG_CHARACTER_LP_DONATION_KILLSWITCH, FLAG_CHARACTER_LP_DONATION_KILLSWITCH_DEFAULT
from eve.client.script.ui.shared.neocom.wallet.panels.donateLPPanel import DonateLPPanel
from eve.common.script.sys import idCheckers

class PersonalDonateLPPanel(DonateLPPanel):
    __notifyevents__ = ['OnCharacterLPBalanceChange_Local']
    default_name = 'personalDonateLPPanel'
    killSwitchKey = FLAG_CHARACTER_LP_DONATION_KILLSWITCH
    killSwitchDefault = FLAG_CHARACTER_LP_DONATION_KILLSWITCH_DEFAULT

    def _get_selected_issuer_corp_id_setting(self):
        return settings.user.ui.Get('donateCorpLPIssuer_personal', None)

    def _set_selected_issuer_corp_id_setting(self, value):
        settings.user.ui.Set('donateCorpLPIssuer_personal', value)

    def _get_balance(self, issuer_corp_id):
        return sm.GetService('loyaltyPointsWalletSvc').GetCharacterWalletLPBalance(issuer_corp_id)

    def _get_raw_issuer_corp_list(self):
        return [ x for x, _ in sm.GetService('loyaltyPointsWalletSvc').GetAllCharacterLPBalancesExcludingEvermarks() ]

    def OnCharacterLPBalanceChange_Local(self, *args, **kwargs):
        self._on_update_lp_balance()

    def _filter_valid_corps(self, corps):
        if not self._can_make_donations:
            return
        valid_corps = [ x for x in corps if idCheckers.IsPlayerCorporation(x.charID) ]
        valid_corps = [ x for x in valid_corps if sm.GetService('corp').GetCorporation(x.charID).memberCount > 0 ]
        return valid_corps

    def _set_transfer_button_func(self):
        self._transfer_button.SetFunc(self._transfer_lp)

    def _do_transfer(self, amount):
        sm.GetService('loyaltyPointsWalletSvc').TransferLPFromPlayerToCorp(self._selected_corp_id, self._selected_issuer_corp_id, amount)
