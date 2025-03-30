#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\wallet\panels\corp\corpDonateLPPanel.py
from corporation.common import FLAG_CORP_LP_DONATIONS_KILLSWITCH, FLAG_CORP_LP_DONATIONS_KILLSWITCH_DEFAULT
from eve.client.script.ui.shared.neocom.wallet.panels.donateLPPanel import DonateLPPanel
from eve.common.script.sys import idCheckers
MAX_NAME_LENGTH = 64

class CorpDonateLPPanel(DonateLPPanel):
    __notifyevents__ = ['OnCorporationLPBalanceChange_Local']
    default_name = 'corpDonateLPPanel'
    killSwitchKey = FLAG_CORP_LP_DONATIONS_KILLSWITCH
    killSwitchDefault = FLAG_CORP_LP_DONATIONS_KILLSWITCH_DEFAULT

    def _get_selected_issuer_corp_id_setting(self):
        return settings.user.ui.Get('donateCorpLPIssuer', None)

    def _set_selected_issuer_corp_id_setting(self, value):
        settings.user.ui.Set('donateCorpLPIssuer', value)

    def _get_balance(self, issuer_corp_id):
        return sm.GetService('loyaltyPointsWalletSvc').GetCorporationWalletLPBalance(issuer_corp_id)

    def _get_raw_issuer_corp_list(self):
        return [ x for x, _ in sm.GetService('loyaltyPointsWalletSvc').GetAllCorporationLPBalancesExcludingEvermarks() ]

    def OnCorporationLPBalanceChange_Local(self, _issuer_corp_id):
        self._on_update_lp_balance()

    def _filter_valid_corps(self, corps):
        if not self._can_make_donations:
            return
        valid_corps = [ x for x in corps if idCheckers.IsPlayerCorporation(x.charID) and x.charID != session.corpid ]
        valid_corps = [ x for x in valid_corps if sm.GetService('corp').GetCorporation(x.charID).memberCount > 0 ]
        return valid_corps

    def _set_transfer_button_func(self):
        self._transfer_button.SetFunc(self._transfer_lp)

    def _do_transfer(self, amount):
        sm.GetService('loyaltyPointsWalletSvc').TransferLPFromCorpToCorp(self._selected_corp_id, self._selected_issuer_corp_id, amount)
