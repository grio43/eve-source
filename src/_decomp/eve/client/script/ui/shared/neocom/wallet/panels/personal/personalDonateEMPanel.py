#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\wallet\panels\personal\personalDonateEMPanel.py
import blue
import launchdarkly
from appConst import corpHeraldry
from carbon.common.script.util.format import FmtAmt
from carbonui import uiconst, TextAlign
from carbonui.control.combo import Combo
from carbonui.control.singlelineedits.singleLineEditInteger import SingleLineEditInteger
from carbonui.primitives.container import Container
from corporation.common import FLAG_MIN_ALLIANCE_MEMBERSHIP_DURATION_FOR_EM_DONATION_DEFAULT, FLAG_MIN_ALLIANCE_MEMBERSHIP_DURATION_FOR_EM_DONATION, FLAG_EM_DONATION_KILLSWITCH, FLAG_EM_DONATION_KILLSWITCH_DEFAULT
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.eveLabel import EveLabelLarge, EveCaptionMedium
from eve.client.script.ui.control.infoNotice import InfoNotice
from eve.client.script.ui.shared.neocom.wallet.panels.personal.personalDonateLPPanel import PersonalDonateLPPanel
from eve.common.lib import appConst
from eve.common.script.sys import idCheckers
from localization import GetByLabel

class PersonalDonateEMPanel(PersonalDonateLPPanel):
    default_name = 'personalDonateEMPanel'
    killSwitchKey = FLAG_EM_DONATION_KILLSWITCH
    killSwitchDefault = FLAG_EM_DONATION_KILLSWITCH_DEFAULT
    killSwitchLabel = 'UI/Wallet/WalletWindow/TransferFailedEMDonationsDisabled'

    def __init__(self, **kw):
        self._available_corps = []
        self._min_membership_days = FLAG_MIN_ALLIANCE_MEMBERSHIP_DURATION_FOR_EM_DONATION_DEFAULT
        ld_client = launchdarkly.get_client()
        ld_client.notify_flag(FLAG_MIN_ALLIANCE_MEMBERSHIP_DURATION_FOR_EM_DONATION, FLAG_MIN_ALLIANCE_MEMBERSHIP_DURATION_FOR_EM_DONATION_DEFAULT, self._on_min_membership_days_changed)
        super(PersonalDonateEMPanel, self).__init__(**kw)

    def _on_min_membership_days_changed(self, ld_client, feature_key, fallback, _flagDeleted):
        self._min_membership_days = ld_client.get_int_variation(feature_key=feature_key, fallback=fallback)

    def _get_selected_issuer_corp_id_setting(self):
        return corpHeraldry

    def _set_selected_issuer_corp_id_setting(self, value):
        pass

    def _initialize_selected_corp_id(self):
        pass

    def _evaluate_can_make_donations(self):
        self._selected_corp_id = None
        self._can_make_donations = False
        if self._is_corp_membership_valid():
            self._can_make_donations = True
            self._available_corps = [session.corpid]
            if session.allianceid is not None:
                num_days_in_alliance = sm.RemoteSvc('allianceRegistry').GetDaysInAlliance(session.allianceid, session.corpid)
                if num_days_in_alliance >= self._min_membership_days:
                    alliance_info = sm.GetService('alliance').GetAlliance(session.allianceid)
                    exec_corp = alliance_info.executorCorpID
                    if exec_corp != session.corpid:
                        num_days_in_alliance_exec = sm.RemoteSvc('allianceRegistry').GetDaysInAlliance(session.allianceid, exec_corp)
                        if num_days_in_alliance_exec >= self._min_membership_days:
                            self._available_corps.append(exec_corp)
        if len(self._available_corps) == 1:
            self._selected_corp_id = self._available_corps[0]

    def _is_corp_membership_valid(self):
        char_info = sm.RemoteSvc('charMgr').GetPublicInfo(session.charid)
        if char_info is None:
            return False
        char_start_date = char_info.corporationDateTime
        num_days_in_corp = (blue.os.GetWallclockTime() - char_start_date) / appConst.DAY
        return num_days_in_corp >= self._min_membership_days and idCheckers.IsPlayerCorporation(session.corpid)

    def is_panel_available(self):
        return self._is_corp_membership_valid()

    def _construct_main_cont_restricted(self):
        super(PersonalDonateEMPanel, self)._construct_main_cont_restricted()
        label_cont = Container(name='labelCont', parent=self._main_cont, align=uiconst.TOTOP_PROP, textAlign=TextAlign.CENTER, height=0.5)
        EveLabelLarge(parent=label_cont, align=uiconst.TOBOTTOM, textAlign=TextAlign.CENTER, text=GetByLabel('UI/Wallet/WalletWindow/PersonalEMTabRestricted', numDays=self._min_membership_days), color=eveColor.GUNMETAL_GREY)
        EveCaptionMedium(parent=label_cont, align=uiconst.TOBOTTOM, textAlign=TextAlign.CENTER, padBottom=4, text=GetByLabel('UI/Wallet/WalletWindow/AccessRestricted'))

    def _construct_main_cont_full(self):
        super(PersonalDonateEMPanel, self)._construct_main_cont_full()
        info_cont = Container(parent=self, name='infoCont', align=uiconst.TORIGHT_PROP, width=0.5, padLeft=16)
        info_notice = InfoNotice(name='infoNotice', parent=info_cont, align=uiconst.TOTOP, labelText=GetByLabel('UI/Wallet/WalletWindow/TransferPersonalEMNotice', numDaysCorp=self._min_membership_days, numDaysAlliance=self._min_membership_days))
        info_notice.noticeLabel.maxLines = None

    def _construct_search_input(self):
        if not self._can_make_donations or len(self._available_corps) == 1:
            return
        self._search_input_cont = Container(parent=self._main_cont, name='searchInputCont', height=32, padTop=14, align=uiconst.TOTOP)
        options = [ (cfg.eveowners.Get(x).name, x) for x in self._available_corps ]
        self._search_combo = Combo(label=GetByLabel('UI/Wallet/WalletWindow/TransferTo'), parent=self._search_input_cont, options=options, name='searchCombo', width=0.6, align=uiconst.TOLEFT_PROP, callback=self._on_corp_selected, nothingSelectedText=GetByLabel('UI/Wallet/WalletWindow/EMDonationSelectCorp'))

    def _on_corp_selected(self, _combo, _key, value):
        self._selected_corp_id = value
        self._show_search_result()

    def _filter_valid_corps(self, corps):
        if not self._can_make_donations:
            return
        valid_corps = [ x for x in corps if x.charID in self._available_corps ]
        return valid_corps

    def _construct_reset_search_button(self):
        if not self._can_make_donations or len(self._available_corps) == 1:
            return
        super(PersonalDonateEMPanel, self)._construct_reset_search_button()

    def _reset_search_result(self):
        if not self._can_make_donations or len(self._available_corps) == 1:
            return
        super(PersonalDonateEMPanel, self)._reset_search_result()
        self._search_combo.SetNothingSelected()

    def _construct_amount(self):
        amount_cont = Container(parent=self._main_cont, name='amountCont', align=uiconst.TOTOP, height=32, padTop=48)
        self._amount_input = SingleLineEditInteger(name='lpAmountInput', parent=amount_cont, align=uiconst.TOLEFT_PROP, width=0.6, hintText=GetByLabel('UI/Wallet/WalletWindow/EM'), label=GetByLabel('UI/Wallet/WalletWindow/GiveAmount'))
        self._amount_input.OnChange = self._on_amount_changed

    def _get_raw_issuer_corp_list(self):
        return [corpHeraldry]

    def _set_transfer_button_func(self):
        self._transfer_button.SetFunc(self._transfer_lp)

    def _get_confirmation_message(self, amount):
        return GetByLabel('UI/Wallet/WalletWindow/CorpEMTransactionConfirmation', amount=FmtAmt(amount), corpName=cfg.eveowners.Get(self._selected_corp_id).name)
