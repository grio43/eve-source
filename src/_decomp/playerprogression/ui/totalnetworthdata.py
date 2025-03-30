#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\playerprogression\ui\totalnetworthdata.py
from localization import GetByLabel
from eve.client.script.ui.plex.textures import PLEX_128_GRADIENT_WHITE
WALLET_BALANCE_TITLE_PATH = 'UI/VisualProgressStats/WalletBalanceTitle'
MARKET_ORDERS_TITLE_PATH = 'UI/VisualProgressStats/OutstandingMarketOrdersTitle'
CONTRACT_ESCROW_TITLE_PATH = 'UI/VisualProgressStats/OutstandingContractsTitle'
NET_ASSETS_WORTH_TITLE_PATH = 'UI/VisualProgressStats/NetAssetWorthTitle'
PLEX_WORTH_TITLE_PATH = 'UI/VisualProgressStats/PlexWorthTitle'
WALLET_ICON = 'res:/ui/Texture/WindowIcons/wallet.png'
MARKET_ICON = 'res:/ui/Texture/WindowIcons/market.png'
CONTRACTS_ICON = 'res:/ui/Texture/WindowIcons/contracts.png'
ASSETS_ICON = 'res:/ui/Texture/WindowIcons/assets.png'
ICON_SIZE = 36

class TotalNetWorthComponent(object):
    INITIAL_VALUE = 0

    def __init__(self, name, icon_path, label_path, button_function):
        self.value = self.INITIAL_VALUE
        self.old_value = self.INITIAL_VALUE
        self.name = name
        self.icon_path = icon_path
        self.icon_size = ICON_SIZE
        self.label = GetByLabel(label_path)
        self.button_function = button_function
        self.value_text_width = 0

    def get_value(self):
        return self.value

    def get_old_value(self):
        return self.old_value

    def set_value(self, value):
        self.value = value or self.INITIAL_VALUE

    def set_old_value(self, value):
        self.old_value = value or self.INITIAL_VALUE

    def update_value(self, value):
        self.set_value(value)
        return self.get_old_value() != self.get_value()

    def get_snapshot(self, get_old = False):
        if get_old:
            return (0, self.get_old_value())
        return (self.get_old_value(), self.get_value())


class AssetNetWorthValue(object):

    def __init__(self, assets, market_items, contract_items):
        self.assets = assets or 0
        self.market_items = market_items or 0
        self.contract_items = contract_items or 0

    def get_total(self):
        return self.assets + self.market_items + self.contract_items


class PlexWorthValue(object):

    def __init__(self, assets_plex, vault_plex):
        self.assets_plex = assets_plex or 0
        self.vault_plex = vault_plex or 0

    def get_total(self):
        return self.assets_plex + self.vault_plex


class AddedTotalNetWorthComponent(TotalNetWorthComponent):

    def __init__(self, *args, **kwargs):
        TotalNetWorthComponent.__init__(self, *args, **kwargs)

    def get_value(self):
        return self.value.get_total()

    def get_old_value(self):
        return self.old_value.get_total()


class AssetNetWorthComponent(AddedTotalNetWorthComponent):
    INITIAL_VALUE = AssetNetWorthValue(0, 0, 0)


class PlexWorthComponent(AddedTotalNetWorthComponent):
    INITIAL_VALUE = PlexWorthValue(0, 0)


class TooltipData(object):

    def __init__(self, isk_snapshot, market_snapshot, contract_snapshot, assets_snapshot, plex_snapshot):
        self.isk_snapshot = isk_snapshot
        self.market_snapshot = market_snapshot
        self.contract_snapshot = contract_snapshot
        self.assets_snapshot = assets_snapshot
        self.plex_snapshot = plex_snapshot


class TotalNetWorthData(object):

    def __init__(self):
        eveCommands = sm.GetService('cmd')
        self.wallet_data = TotalNetWorthComponent(name='wallet_data', icon_path=WALLET_ICON, label_path=WALLET_BALANCE_TITLE_PATH, button_function=eveCommands.OpenWallet)
        self.market_data = TotalNetWorthComponent(name='market_data', icon_path=MARKET_ICON, label_path=MARKET_ORDERS_TITLE_PATH, button_function=eveCommands.OpenMarket)
        self.contract_data = TotalNetWorthComponent(name='contract_data', icon_path=CONTRACTS_ICON, label_path=CONTRACT_ESCROW_TITLE_PATH, button_function=eveCommands.OpenContracts)
        self.assets_data = AssetNetWorthComponent(name='assets_data', icon_path=ASSETS_ICON, label_path=NET_ASSETS_WORTH_TITLE_PATH, button_function=eveCommands.OpenAssets)
        self.plex_data = PlexWorthComponent(name='plex_data', icon_path=PLEX_128_GRADIENT_WHITE, label_path=PLEX_WORTH_TITLE_PATH, button_function=eveCommands.OpenPlexVault)
        self.components = [self.wallet_data,
         self.assets_data,
         self.contract_data,
         self.market_data,
         self.plex_data]
        self.components_always_visible = [self.wallet_data, self.assets_data]
        self.components_not_always_visible = [self.contract_data, self.market_data, self.plex_data]

    def get_components(self):
        return self.components

    def get_components_always_visible(self):
        return self.components_always_visible

    def get_components_not_always_visible(self):
        return self.components_not_always_visible

    def get_total_net_worth(self):
        total_net_worth = 0
        for component in self.components:
            total_net_worth += component.get_value()

        return total_net_worth

    def get_old_total_net_worth(self):
        total_net_worth = 0
        for component in self.components:
            total_net_worth += component.get_old_value()

        return total_net_worth

    def update_old_values(self):
        for component in self.components:
            component.set_old_value(component.value)

    def get_tooltip_data(self, get_old = False):
        return TooltipData(isk_snapshot=self.wallet_data.get_snapshot(get_old), market_snapshot=self.market_data.get_snapshot(get_old), contract_snapshot=self.contract_data.get_snapshot(get_old), assets_snapshot=self.assets_data.get_snapshot(get_old), plex_snapshot=self.plex_data.get_snapshot(get_old))
