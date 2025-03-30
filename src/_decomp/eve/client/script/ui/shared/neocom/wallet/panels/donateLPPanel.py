#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\wallet\panels\donateLPPanel.py
import launchdarkly
from carbon.common.script.util.format import FmtAmt
from carbonui import uiconst
from carbonui.control.combo import Combo
from carbonui.control.singlelineedits.singleLineEditInteger import SingleLineEditInteger
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from eve.client.script.ui import eveColor
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.control.button import Button
from eve.client.script.ui.control.eveIcon import CorpIcon
from eve.client.script.ui.control.eveLabel import EveLabelMedium, EveLabelLarge
from eve.client.script.ui.control.searchinput import SearchInput
from eve.client.script.ui.control.themeColored import FillThemeColored
from eve.client.script.ui.shared.userentry import User
from eve.client.script.ui.util import searchUtil
from eve.common.script.search.const import MatchBy
from eveexceptions import UserError
from localization import GetByLabel
from lpOffers.exceptions import TransfersDisabledError
MAX_NAME_LENGTH = 64

class DonateLPPanel(Container):
    default_name = 'donateLPPanel'
    killSwitchKey = None
    killSwitchDefault = None
    killSwitchLabel = 'UI/Wallet/WalletWindow/TransferFailedTransactionsDisabled'

    def __init__(self, **kw):
        self._amount_input = None
        self._transaction_result_label = None
        self._search_input_cont = None
        self._search_by_combo = None
        self._search_input = None
        self._result_cont = None
        self._result_icon = None
        self._corp_name_label = None
        self._transfer_button = None
        self._issuer_corp_combo = None
        self._can_make_donations = True
        self._evaluate_can_make_donations()
        self._initialize_selected_corp_id()
        self._selected_issuer_corp_id = self._get_selected_issuer_corp_id_setting()
        super(DonateLPPanel, self).__init__(**kw)

    def _initialize_selected_corp_id(self):
        self._selected_corp_id = None

    def _evaluate_can_make_donations(self):
        self._can_make_donations = True

    def ApplyAttributes(self, attributes):
        super(DonateLPPanel, self).ApplyAttributes(attributes)
        self._init_killswitch()
        sm.RegisterNotify(self)
        self._construct_main_cont()
        self._construct_layout_full()
        self._reset_search()
        self._update_amount_input()

    def _init_killswitch(self):
        if self.killSwitchKey is None or self.killSwitchDefault is None:
            self._killswitch = False
        self._killswitch = self.killSwitchDefault
        ld_client = launchdarkly.get_client()
        ld_client.notify_flag(self.killSwitchKey, self.killSwitchDefault, self._on_killswitch_changed)

    def OnTabSelect(self):
        self.on_tab_select()

    def _get_selected_issuer_corp_id_setting(self):
        raise NotImplementedError

    def _set_selected_issuer_corp_id_setting(self, value):
        raise NotImplementedError

    def _construct_layout_full(self):
        if not self._can_make_donations:
            return
        self._construct_search_input()
        self._construct_error()
        self._construct_search_result()
        self._construct_amount()
        self._construct_transfer_button()

    def _construct_main_cont(self):
        if not self._can_make_donations:
            self._construct_main_cont_restricted()
        else:
            self._construct_main_cont_full()

    def _construct_main_cont_full(self):
        self._main_cont = ContainerAutoSize(name='mainCont', align=uiconst.TOLEFT_PROP, alignMode=uiconst.TOTOP, width=0.5, parent=self)

    def _construct_main_cont_restricted(self):
        self._main_cont = Container(name='mainCont', align=uiconst.TOALL, parent=self)

    def on_tab_select(self):
        self._hide_transaction_result_label()

    def _construct_search_input(self):
        if not self._can_make_donations:
            return
        self._search_input_cont = Container(parent=self._main_cont, name='searchInputCont', height=32, padTop=14, align=uiconst.TOTOP)
        self._search_by_combo = Combo(label=GetByLabel('UI/Common/SearchBy'), parent=self._search_input_cont, options=searchUtil.GetSearchByChoices(), name='searchCombo', select=settings.user.ui.Get('ppSearchBy', MatchBy.partial_terms), width=0.4, align=uiconst.TORIGHT_PROP, padLeft=8, callback=self._change_search_by)
        self._search_input = SearchInput(parent=self._search_input_cont, name='searchInput', align=uiconst.TOLEFT_PROP, width=0.6, GetSearchEntries=self._search_for_corporation, maxLength=MAX_NAME_LENGTH, OnSearchEntrySelected=self._on_search_entry_selected, hintText=GetByLabel('UI/Wallet/WalletWindow/SearchForCorpHint'), allowBrowsing=True, isCharacterField=True, label=GetByLabel('UI/Wallet/WalletWindow/TransferTo'))
        self._search_input.SetHistoryVisibility(False)

    def _search_for_corporation(self, search_string):
        if len(search_string) < 3:
            self._show_no_results_error(False)
            return []
        else:
            search_terms = settings.user.ui.Get('ppSearchBy', MatchBy.partial_terms)
            valid_corps = searchUtil.SearchCorporations(search_string, searchBy=search_terms)
            valid_corps = self._filter_valid_corps(valid_corps)
            self._show_no_results_error(not valid_corps)
            return valid_corps

    def _filter_valid_corps(self, corps):
        raise NotImplementedError

    def _change_search_by(self, _entry, _header, value, *args):
        settings.user.ui.Set('ppSearchBy', value)

    def _construct_search_result(self):
        self._result_cont = Container(name='resultCont', parent=self._main_cont, align=uiconst.TOTOP, height=44, padTop=2)
        FillThemeColored(bgParent=self._result_cont, colorType=uiconst.COLORTYPE_UIBASECONTRAST)
        self._result_icon = CorpIcon(corpID=self._selected_corp_id, parent=self._result_cont, align=uiconst.CENTERLEFT, pos=(2, 0, 42, 42))
        self._corp_name_label = EveLabelMedium(parent=self._result_cont, name='corpNameLabel', align=uiconst.CENTERLEFT, text=cfg.eveowners.Get(self._selected_corp_id).name if self._selected_corp_id else '', width=150, left=50)
        self._construct_reset_search_button()

    def _construct_reset_search_button(self):
        if not self._can_make_donations:
            return
        ButtonIcon(parent=self._result_cont, name='resetButton', texturePath='res:/UI/Texture/Icons/73_16_210.png', align=uiconst.TOPRIGHT, func=self._reset_search, width=7, height=7, iconSize=14, left=5, top=5)

    def _reset_search(self, *args, **kwargs):
        self._reset_search_result()
        if self._search_input_cont:
            self._search_input_cont.Show()
        if self._search_by_combo:
            self._search_by_combo.Show()
        self._update_transfer_button()
        if self._search_input:
            uicore.registry.SetFocus(self._search_input)

    def _reset_search_result(self):
        if not self._can_make_donations:
            return
        self._selected_corp_id = None
        if self._result_cont:
            self._result_cont.Hide()

    def _on_search_entry_selected(self, result):
        if isinstance(result, User):
            result = result.sr.node
        else:
            result = result[0]
        self._selected_corp_id = result.itemID
        self._show_search_result()

    def _show_search_result(self):
        if self._result_icon:
            self._result_icon.Load(self._selected_corp_id)
        if self._corp_name_label:
            self._corp_name_label.text = cfg.eveowners.Get(self._selected_corp_id).name
        if self._search_input:
            self._search_input.SetValue('')
        self._hide_transaction_result_label()
        if self._search_input_cont:
            self._search_input_cont.Hide()
        if self._result_cont:
            self._result_cont.Show()
        if self._search_by_combo:
            self._search_by_combo.Hide()
        self._update_transfer_button()
        if self._search_input:
            self._search_input.CloseResultMenu()

    def _construct_error(self):
        self._error_label = EveLabelMedium(name='errorLabel', parent=self._main_cont, align=uiconst.TOTOP_NOPUSH, text=GetByLabel('UI/Common/NothingFound'), color=eveColor.WARNING_ORANGE, opacity=0.75, state=uiconst.UI_HIDDEN)

    def _show_no_results_error(self, show):
        self._error_label.display = show

    def _construct_amount(self):
        amount_cont = Container(parent=self._main_cont, name='amountCont', align=uiconst.TOTOP, height=32, padTop=48)
        self._issuer_corp_combo = Combo(parent=amount_cont, name='issuerCorpCombo', label=GetByLabel('UI/Common/Corporation'), width=0.6, align=uiconst.TOLEFT_PROP, callback=self._on_issuer_corp_changed)
        self._update_issuer_corp_options()
        self._amount_input = SingleLineEditInteger(name='lpAmountInput', parent=amount_cont, align=uiconst.TORIGHT_PROP, width=0.4, hintText=GetByLabel('UI/Wallet/WalletWindow/LP'), decimalPlaces=0, padLeft=8, label=GetByLabel('UI/Wallet/WalletWindow/GiveAmount'))
        self._amount_input.OnChange = self._on_amount_changed

    def _on_amount_changed(self, *args):
        self._update_transfer_button()

    def _update_issuer_corp_options(self):
        options = self._get_issuer_corp_list()
        if self._selected_issuer_corp_id is not None and self._selected_issuer_corp_id not in [ x for _, x in options ]:
            self._selected_issuer_corp_id = None
            if self._amount_input is not None:
                self._amount_input.SetValue(0)
        if self._selected_issuer_corp_id is None and len(options) > 0:
            self._selected_issuer_corp_id = options[0][1]
        if self._issuer_corp_combo is not None:
            self._issuer_corp_combo.LoadOptions(options, self._selected_issuer_corp_id)

    def _get_balance(self, issuer_corp_id):
        raise NotImplementedError

    def _get_issuer_corp_list(self):

        def _sort_func(e):
            return e[0].lower()

        corp_ids = self._get_raw_issuer_corp_list()
        corp_ids = [ x for x in corp_ids if self._get_balance(x) > 0 ]
        corp_list = [ (cfg.eveowners.Get(corp_id).ownerName, corp_id) for corp_id in corp_ids ]
        corp_list.sort(key=_sort_func)
        return corp_list

    def _get_raw_issuer_corp_list(self):
        raise NotImplementedError

    def _on_issuer_corp_changed(self, _entry, _header, value, *args):
        self._set_selected_issuer_corp_id_setting(value)
        self._selected_issuer_corp_id = value
        self._update_amount_input()
        self._hide_transaction_result_label()

    def _update_amount_input(self):
        if self._amount_input is None:
            return
        max_lp_value = self._get_balance(self._selected_issuer_corp_id) if self._selected_issuer_corp_id is not None else 0
        if max_lp_value == 0:
            self._amount_input.enabled = False
            self._amount_input.SetMinValue(0)
            self._amount_input.SetMaxValue(0)
            self._amount_input.SetValue(0)
        else:
            self._amount_input.enabled = self._selected_issuer_corp_id is not None
            self._amount_input.SetMinValue(0)
            self._amount_input.SetMaxValue(max_lp_value)
            self._amount_input.SetValue(min(max_lp_value, self._amount_input.GetValue()))

    def _on_update_lp_balance(self):
        self._update_issuer_corp_options()
        self._update_amount_input()

    def _construct_transfer_button(self):
        cont = ContainerAutoSize(parent=self._main_cont, name='transferCont', align=uiconst.TOTOP, padTop=32)
        grid = LayoutGrid(parent=cont, name='transferGrid', columns=2, cellSpacing=(16, 0))
        self._transfer_button = Button(name='transferButton', parent=grid, align=uiconst.CENTER, label=GetByLabel('UI/HangarTransfer/TransferBtn'), func=self._transfer_lp)
        self._update_transfer_button()
        self._set_transfer_button_func()
        self._transaction_result_label = EveLabelLarge(parent=grid, name='transactionResultLabel', align=uiconst.CENTERLEFT, opacity=0.0)

    def _set_transfer_button_func(self):
        self._transfer_button.SetFunc(self._transfer_lp)

    def _update_transfer_button(self):
        if self._transfer_button:
            if self._selected_corp_id is None or self._selected_issuer_corp_id is None or self._amount_input.GetValue() <= 0:
                self._transfer_button.Disable()
            else:
                self._transfer_button.Enable()

    def _show_success_label(self):
        if self._transaction_result_label is None:
            return
        self._transaction_result_label.color = eveColor.SUCCESS_GREEN
        self._transaction_result_label.text = GetByLabel('UI/Wallet/WalletWindow/TransferSuccessful')
        animations.FadeIn(self._transaction_result_label)

    def _show_failure_label(self, label):
        if self._transaction_result_label is None:
            return
        self._transaction_result_label.color = eveColor.SUCCESS_GREEN
        self._transaction_result_label.text = label
        animations.FadeIn(self._transaction_result_label)

    def _hide_transaction_result_label(self):
        if self._transaction_result_label is None:
            return
        animations.FadeOut(self._transaction_result_label)

    def _get_confirmation_message(self, amount):
        return GetByLabel('UI/Wallet/WalletWindow/CorpLPTransactionConfirmation', amount=FmtAmt(amount), issuerCorpName=cfg.eveowners.Get(self._selected_issuer_corp_id).ownerName, corpName=cfg.eveowners.Get(self._selected_corp_id).name)

    def _check_killswitch_on(self):
        if self._killswitch is not None:
            return self._killswitch
        return False

    def _get_killswitch_label(self):
        return GetByLabel(self.killSwitchLabel)

    def _transfer_lp(self, *args):
        if self._check_killswitch_on():
            self._show_failure_label(self._get_killswitch_label())
            return
        amount = self._amount_input.GetValue() if self._amount_input else 0
        if amount <= 0:
            self._show_failure_label(GetByLabel('UI/Wallet/WalletWindow/TransferEmptyAmount'))
            return
        message = self._get_confirmation_message(amount)
        if eve.Message('AskAreYouSure', {'cons': message}, uiconst.YESNO) != uiconst.ID_YES:
            return
        try:
            self._do_transfer(amount)
            self._show_success_label()
        except TransfersDisabledError:
            self._show_failure_label(self._get_killswitch_label())
        except UserError as e:
            raise e
        except Exception:
            self._show_failure_label(GetByLabel('UI/Wallet/WalletWindow/TransferFailed'))
        finally:
            self._reset_search()

    def _do_transfer(self, amount):
        raise NotImplementedError

    def _on_killswitch_changed(self, ld_client, feature_key, fallback, _flagDeleted):
        self._killswitch = ld_client.get_bool_variation(feature_key=feature_key, fallback=fallback)
