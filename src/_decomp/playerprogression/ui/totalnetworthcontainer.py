#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\playerprogression\ui\totalnetworthcontainer.py
from carbonui import TextColor, uiconst
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from eve.client.script.ui.control.eveLabel import EveLabelLarge
from eve.client.script.ui.shared.neocom.wallet import walletUtil
from eve.client.script.util.contractutils import FmtISKWithDescription
from localization import GetByLabel
from playerprogression.ui.totalnetworthdata import TotalNetWorthData, AssetNetWorthValue, PlexWorthValue
from playerprogression.ui.totalnetworthtooltip import TotalNetWorthTooltipButton, TOOLTIP_WIDTH
TOTAL_NET_WORTH_TITLE_PATH = 'UI/VisualProgressStats/TotalNetWorthTitle'
COUNTER_COLOR = '<color=0xffffffff>'
TOTAL_NET_WORTH_TITLE_OPACITY = 1.0
TOTAL_NET_WORTH_VALUE_OPACITY = 1.0
COUNTER_TO_TOOLTIP_ICON_PADDING = 6
STATE_UPDATE_DELAY_MSEC = 2000

class TotalNetWorthProgressionContainer(Container):
    __notifyevents__ = ['OnPersonalAccountChangedClient']

    def ApplyAttributes(self, attributes):
        self._is_subscribed_to_updates = False
        Container.ApplyAttributes(self, attributes)
        sm.RegisterNotify(self)
        self._wallet_svc = sm.GetService('wallet')
        self._market_svc = sm.GetService('marketQuote')
        self._contracts_svc = sm.GetService('contracts')
        self._assets_svc = sm.GetService('assets')
        self.data = TotalNetWorthData()
        self.tooltip = None
        self._setup_ui()
        self.update_thread = None
        isk = self._wallet_svc.GetWealth()
        self.data.wallet_data.update_value(isk)
        self._subscribe_to_updates()

    def _subscribe_to_updates(self):
        self._market_svc.SubscribeMarketProgressWatcher(self, self._update_market_escrow)
        self._contracts_svc.SubscribeContractProgressWatcher(self, self._update_contract_escrow)
        self._assets_svc.SubscribeAssetNetWorthWatcher(self, self._update_asset_net_worth)
        self._assets_svc.SubscribePlexWorthWatcher(self, self._update_plex_worth)
        self._is_subscribed_to_updates = True

    def _unsubscribe_from_updates(self):
        if self._is_subscribed_to_updates:
            self._market_svc.UnsubscribeMarketProgressWatcher(self)
            self._contracts_svc.UnsubscribeContractProgressWatcher(self)
            self._assets_svc.UnsubscribeAssetNetWorthWatcher(self)
            self._assets_svc.UnsubscribePlexWorthWatcher(self)
            self._is_subscribed_to_updates = False

    def _setup_ui(self):
        self._add_title()
        self._add_counter()
        self._add_tooltip()

    def _add_title(self):
        title_container = ContainerAutoSize(name='total_net_worth_title_container', parent=self, align=uiconst.TOLEFT, height=self.height, padRight=10)
        EveLabelLarge(name='total_net_worth_title', parent=title_container, text=GetByLabel(TOTAL_NET_WORTH_TITLE_PATH), align=uiconst.CENTERLEFT, opacity=TOTAL_NET_WORTH_TITLE_OPACITY, color=TextColor.SECONDARY)

    def _add_counter(self):
        counter_container = ContainerAutoSize(name='total_net_worth_counter_container', parent=self, align=uiconst.TOLEFT, height=self.height)
        self.counter = EveLabelLarge(name='total_net_worth_counter', parent=counter_container, text='', align=uiconst.CENTER, opacity=TOTAL_NET_WORTH_VALUE_OPACITY)

    def _add_tooltip(self):
        tooltipCont = Container(name='tooltipCont', parent=self, align=uiconst.TOLEFT, width=TOOLTIP_WIDTH, height=self.height, padLeft=COUNTER_TO_TOOLTIP_ICON_PADDING)
        self.tooltip = TotalNetWorthTooltipButton(name='tooltipIcon', parent=tooltipCont, align=uiconst.CENTERRIGHT, data=self.data)

    def Close(self):
        self._unsubscribe_from_updates()
        Container.Close(self)

    def OnPersonalAccountChangedClient(self, new_balance, difference):
        new_isk = self._wallet_svc.GetWealth()
        self.data.wallet_data.update_value(new_isk)
        self._start_state_update()

    def _update_market_escrow(self, new_market_escrow):
        if new_market_escrow is not None:
            self._update_component_value(self.data.market_data, new_market_escrow.isk_escrow)
            assets_value = self.data.assets_data.value
            new_assets_value = AssetNetWorthValue(assets=assets_value.assets, market_items=new_market_escrow.items_escrow, contract_items=assets_value.contract_items)
            self._update_component_value(self.data.assets_data, new_assets_value)

    def _update_contract_escrow(self, new_contract_escrow):
        if new_contract_escrow is not None:
            self._update_component_value(self.data.contract_data, new_contract_escrow.isk_escrow)
            assets_value = self.data.assets_data.value
            new_assets_value = AssetNetWorthValue(assets=assets_value.assets, market_items=assets_value.market_items, contract_items=new_contract_escrow.items_escrow)
            self._update_component_value(self.data.assets_data, new_assets_value)

    def _update_asset_net_worth(self, new_asset_net_worth):
        if new_asset_net_worth is not None:
            assets_value = self.data.assets_data.value
            new_assets_value = AssetNetWorthValue(assets=new_asset_net_worth.asset_worth, market_items=assets_value.market_items, contract_items=assets_value.contract_items)
            self._update_component_value(self.data.assets_data, new_assets_value)
            plex_value = self.data.plex_data.value
            new_plex_value = PlexWorthValue(assets_plex=new_asset_net_worth.plex_worth, vault_plex=plex_value.vault_plex)
            self._update_component_value(self.data.plex_data, new_plex_value)

    def _update_plex_worth(self, new_plex_worth):
        if new_plex_worth is not None:
            plex_value = self.data.plex_data.value
            new_plex_value = PlexWorthValue(assets_plex=plex_value.assets_plex, vault_plex=new_plex_worth)
            self._update_component_value(self.data.plex_data, new_plex_value)

    def _update_component_value(self, data, new_value):
        data.update_value(new_value)
        self._start_state_update()

    def _start_state_update(self):
        if self.update_thread is None:
            self.update_thread = AutoTimer(STATE_UPDATE_DELAY_MSEC, self._update_state)

    def _update_state(self):
        try:
            new_total_net_worth = self.data.get_total_net_worth()
            tooltip_data = self.data.get_tooltip_data(get_old=False)
            self.data.update_old_values()
            self.tooltip.update_data(tooltip_data)
            if new_total_net_worth > 1000000000000L:
                self.counter.SetText(FmtISKWithDescription(new_total_net_worth, True))
            else:
                self.counter.SetText(walletUtil.GetBalanceFormatted(new_total_net_worth, COUNTER_COLOR, const.creditsISK))
        finally:
            self.update_thread = None
