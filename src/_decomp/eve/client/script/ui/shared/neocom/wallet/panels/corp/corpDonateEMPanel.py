#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\wallet\panels\corp\corpDonateEMPanel.py
import launchdarkly
from appConst import corpHeraldry
from carbon.common.script.util.format import FmtAmt
from carbonui import uiconst, TextAlign
from carbonui.control.singlelineedits.singleLineEditInteger import SingleLineEditInteger
from carbonui.primitives.container import Container
from corporation.common import FLAG_MIN_ALLIANCE_MEMBERSHIP_DURATION_FOR_EM_DONATION, FLAG_MIN_ALLIANCE_MEMBERSHIP_DURATION_FOR_EM_DONATION_DEFAULT, FLAG_EM_DONATION_KILLSWITCH_DEFAULT, FLAG_EM_DONATION_KILLSWITCH
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.eveLabel import EveLabelLarge, EveCaptionMedium
from eve.client.script.ui.control.infoNotice import InfoNotice
from eve.client.script.ui.shared.neocom.wallet.panels.corp.corpDonateLPPanel import CorpDonateLPPanel
from localization import GetByLabel

class CorpDonateEMPanel(CorpDonateLPPanel):
    default_name = 'corpDonateEMPanel'
    killSwitchKey = FLAG_EM_DONATION_KILLSWITCH
    killSwitchDefault = FLAG_EM_DONATION_KILLSWITCH_DEFAULT
    killSwitchLabel = 'UI/Wallet/WalletWindow/TransferFailedEMDonationsDisabled'

    def __init__(self, **kw):
        self._min_membership_days = FLAG_MIN_ALLIANCE_MEMBERSHIP_DURATION_FOR_EM_DONATION_DEFAULT
        ld_client = launchdarkly.get_client()
        ld_client.notify_flag(FLAG_MIN_ALLIANCE_MEMBERSHIP_DURATION_FOR_EM_DONATION, FLAG_MIN_ALLIANCE_MEMBERSHIP_DURATION_FOR_EM_DONATION_DEFAULT, self._on_min_membership_days_changed)
        super(CorpDonateEMPanel, self).__init__(**kw)

    def _on_min_membership_days_changed(self, ld_client, feature_key, fallback, _flagDeleted):
        self._min_membership_days = ld_client.get_int_variation(feature_key=feature_key, fallback=fallback)

    def _initialize_selected_corp_id(self):
        pass

    def _evaluate_can_make_donations(self):
        self._can_make_donations = session.allianceid is not None
        self._is_exec_corp = False
        self._member_corps = []
        self._selected_corp_id = None
        if self._can_make_donations:
            num_days = sm.RemoteSvc('allianceRegistry').GetDaysInAlliance(session.allianceid, session.corpid)
            self._can_make_donations = num_days >= self._min_membership_days
        if self._can_make_donations:
            alliance_info = sm.GetService('alliance').GetAlliance(session.allianceid)
            exec_corp = alliance_info.executorCorpID
            self._is_exec_corp = exec_corp == session.corpid
            if self._is_exec_corp:
                self._member_corps = sm.RemoteSvc('allianceRegistry').GetAllianceMembersOlderThan(session.allianceid, self._min_membership_days)
                cfg.eveowners.Prime([ m for m in self._member_corps ])
            else:
                self._selected_corp_id = exec_corp

    def _get_selected_issuer_corp_id_setting(self):
        return corpHeraldry

    def _set_selected_issuer_corp_id_setting(self, value):
        pass

    def _construct_main_cont_restricted(self):
        super(CorpDonateEMPanel, self)._construct_main_cont_restricted()
        label_cont = Container(name='labelCont', parent=self._main_cont, align=uiconst.TOTOP_PROP, textAlign=TextAlign.CENTER, height=0.5)
        EveLabelLarge(parent=label_cont, align=uiconst.TOBOTTOM, textAlign=TextAlign.CENTER, text=GetByLabel('UI/Wallet/WalletWindow/CorpEMTabRestricted', numDays=self._min_membership_days), color=eveColor.GUNMETAL_GREY)
        EveCaptionMedium(parent=label_cont, align=uiconst.TOBOTTOM, textAlign=TextAlign.CENTER, padBottom=4, text=GetByLabel('UI/Wallet/WalletWindow/AccessRestricted'))

    def _construct_main_cont_full(self):
        super(CorpDonateEMPanel, self)._construct_main_cont_full()
        if not self._is_exec_corp:
            label = GetByLabel('UI/Wallet/WalletWindow/TransferEMToExecCorpNotice', numDays=self._min_membership_days)
        else:
            label = GetByLabel('UI/Wallet/WalletWindow/TransferEMToNonExecCorpNotice', numDays=self._min_membership_days)
        info_cont = Container(parent=self, name='infoCont', align=uiconst.TORIGHT_PROP, width=0.5, padLeft=16)
        info_notice = InfoNotice(name='infoNotice', parent=info_cont, align=uiconst.TOTOP, labelText=label)
        info_notice.noticeLabel.maxLines = None

    def _construct_search_input(self):
        if not self._can_make_donations or not self._is_exec_corp:
            return
        super(CorpDonateEMPanel, self)._construct_search_input()

    def _filter_valid_corps(self, corps):
        if not self._can_make_donations or not self._is_exec_corp:
            return []
        valid_corps = super(CorpDonateEMPanel, self)._filter_valid_corps(corps)
        valid_corps = [ c for c in valid_corps if c.charID in self._member_corps ]
        return valid_corps

    def _construct_reset_search_button(self):
        if not self._can_make_donations or not self._is_exec_corp:
            return
        super(CorpDonateEMPanel, self)._construct_reset_search_button()

    def _reset_search_result(self):
        if not self._can_make_donations or not self._is_exec_corp:
            return
        super(CorpDonateEMPanel, self)._reset_search_result()

    def _construct_amount(self):
        amount_cont = Container(parent=self._main_cont, name='amountCont', align=uiconst.TOTOP, height=32, padTop=48)
        self._amount_input = SingleLineEditInteger(name='lpAmountInput', parent=amount_cont, align=uiconst.TOLEFT_PROP, width=0.6, hintText=GetByLabel('UI/Wallet/WalletWindow/EM'), label=GetByLabel('UI/Wallet/WalletWindow/GiveAmount'))
        self._amount_input.OnChange = self._on_amount_changed

    def _update_issuer_corp_options(self):
        pass

    def _get_raw_issuer_corp_list(self):
        return [corpHeraldry]

    def _set_transfer_button_func(self):
        self._transfer_button.SetFunc(self._transfer_lp)

    def _get_confirmation_message(self, amount):
        return GetByLabel('UI/Wallet/WalletWindow/CorpEMTransactionConfirmation', amount=FmtAmt(amount), corpName=cfg.eveowners.Get(self._selected_corp_id).name)
