#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\wallet\tabs\corpLPTab.py
from carbonui.util.color import Color
from eve.client.script.ui.shared.neocom.wallet.tabs.lpTab import LoyaltyPointsTab
from eve.client.script.ui.shared.neocom.wallet.walletUtil import HaveAccessToCorpLPWallet
from localization import GetByLabel

class CorpLPTab(LoyaltyPointsTab):
    default_name = 'CorpLPTab'
    default_texturePath = 'res:/ui/Texture/WindowIcons/lpstore_24px.png'
    default_underlayColor = Color.HextoRGBA('#B0C9EE')
    default_hint = GetByLabel('UI/Wallet/WalletWindow/LPDescription')
    default_height = 0.5
    default_padding = (2, 2, 2, 2)
    iconContainerSize = 32
    iconSize = 28
    __notifyevents__ = ['OnCorporationLPBalanceChange_Local']

    def ApplyAttributes(self, attributes):
        super(CorpLPTab, self).ApplyAttributes(attributes)

    def Update(self):
        self.enabled = HaveAccessToCorpLPWallet()
        if not HaveAccessToCorpLPWallet():
            return
        super(CorpLPTab, self).Update()

    def GetAmountOfCorporationsIHaveLoyaltyPointsWith(self):
        return len(self.loyaltyPointsWalletSvc.GetAllCorporationLPBalancesExcludingEvermarks())

    def OnCorporationLPBalanceChange_Local(self, _issuerCorpID):
        self.Update()
