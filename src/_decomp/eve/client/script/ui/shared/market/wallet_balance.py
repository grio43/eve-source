#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\market\wallet_balance.py
import eveformat
import eveicon
import eveui
import localization
from carbonui import TextColor, uiconst
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.control.contextMenu.menuData import MenuData
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.services.setting import CharSettingEnum
from carbonui.uianimations import animations
from eve.client.script.ui import eveColor
from eve.client.script.ui.control import eveLabel
from eve.client.script.ui.shared.neocom.wallet.walletUtil import HaveAccessToCorpWallet, HaveReadAccessToCorpWalletDivision
from eve.client.script.ui.shared.neocom.wallet.walletWnd import WalletWindow

class Wallet(object):
    PERSONAL = 1
    CORPORATION = 2
    _ALL = (PERSONAL, CORPORATION)

    @classmethod
    def all(cls):
        return list(cls._ALL)

    @classmethod
    def iter(cls):
        iter(cls._ALL)

    @classmethod
    def from_owner_and_account_key(cls, owner, account_key):
        if owner == session.charid:
            return cls.PERSONAL
        if owner == session.corpid:
            return cls.CORPORATION


selected_wallet_setting = CharSettingEnum(settings_key='selected_market_wallet_balance', options=Wallet.all(), default_value=Wallet.PERSONAL)

def get_wallet_balance_options_menu():
    menu = MenuData()
    wallet_menu = MenuData()
    menu.AddEntry(text=localization.GetByLabel('UI/Market/WalletBalanceOptionsMenuTitle'), subMenuData=wallet_menu, texturePath=eveicon.isk)
    wallet_menu.AddRadioButton(text=localization.GetByLabel('UI/Market/PersonalWallet'), value=Wallet.PERSONAL, setting=selected_wallet_setting)
    wallet_menu.AddRadioButton(text=localization.GetByLabel('UI/Market/CorporationWallet'), value=Wallet.CORPORATION, setting=selected_wallet_setting)
    return menu


class WalletBalance(ContainerAutoSize):
    __notifyevents__ = ('OnAccountChange_Local', 'OnSessionChanged')
    _balance = None
    _balance_label = None
    _caption_label = None
    BALANCE_TEXT_COLOR = TextColor.SECONDARY

    def __init__(self, **kwargs):
        self._balance = self._get_current_balance()
        super(WalletBalance, self).__init__(**kwargs)
        self._layout()
        selected_wallet_setting.on_change.connect(self._on_selected_wallet_setting_changed)
        sm.RegisterNotify(self)

    @property
    def balance(self):
        return self._balance

    @balance.setter
    def balance(self, value):
        if self._balance != value:
            self._balance = value
            self._update_balance()

    def animate_balance_to(self, value):
        if value > self._balance:
            color = eveColor.SUCCESS_GREEN
        else:
            color = eveColor.WARNING_ORANGE
        animations.SpColorMorphTo(self._balance_label, startColor=color, endColor=self.BALANCE_TEXT_COLOR, duration=0.75)
        eveui.animate(self, 'balance', start_value=self.balance or 0.0, end_value=value, duration=0.75)

    def _layout(self):
        grid = LayoutGrid(parent=self, align=uiconst.CENTERLEFT, columns=2, cellSpacing=(4, 4))
        ButtonIcon(parent=grid, align=uiconst.CENTER, width=24, height=24, iconSize=16, texturePath=eveicon.isk, func=WalletWindow.Open, hint=localization.GetByLabel('UI/Commands/OpenWallet'))
        self._balance_label = eveLabel.EveLabelMedium(parent=grid, align=uiconst.CENTERLEFT, text=self._get_balance_text(), color=self.BALANCE_TEXT_COLOR)

    def _get_current_balance(self):
        wallet = selected_wallet_setting.get()
        if wallet == Wallet.PERSONAL:
            return sm.GetService('wallet').GetWealth()
        if wallet == Wallet.CORPORATION:
            if not self._have_access_to_corporation_wallet():
                return None
            return sm.GetService('wallet').GetCorpWealth()

    def _have_access_to_corporation_wallet(self):
        if not HaveAccessToCorpWallet():
            return False
        account_key = session.corpAccountKey
        if account_key is None or not HaveReadAccessToCorpWalletDivision(account_key):
            return False
        return True

    def _get_balance_text(self):
        if self._balance is None:
            return eveformat.color(localization.GetByLabel('UI/Market/WalletBalanceUnavailable'), TextColor.DISABLED)
        return eveformat.isk(self._balance)

    def _update_balance(self):
        self._balance_label.text = self._get_balance_text()

    def _on_selected_wallet_setting_changed(self, value):
        self._update_displayed_wallet()

    def _update_displayed_wallet(self):
        self._balance = self._get_current_balance()
        self._update_balance()

    def OnAccountChange_Local(self, account_key, owner_id, balance):
        wallet = Wallet.from_owner_and_account_key(owner_id, account_key)
        if wallet == selected_wallet_setting.get():
            self.animate_balance_to(self._get_current_balance())

    def OnSessionChanged(self, is_remote, session, change):
        if 'corpAccountKey' in change:
            self._update_displayed_wallet()
