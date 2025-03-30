#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\wallet\tabs\lpTab.py
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.util.color import Color
from eve.client.script.ui.control.eveLabel import EveLabelMediumBold
from eve.client.script.ui.shared.neocom.wallet.tabs.baseWalletTab import BaseWalletTab
from localization import GetByLabel

class LoyaltyPointsTab(BaseWalletTab):
    default_name = 'LoyaltyPointsTab'
    default_texturePath = 'res:/ui/Texture/WindowIcons/lpstore_24px.png'
    tabNamePath = 'UI/Journal/JournalWindow/Agents/LoyaltyPoints'
    default_underlayColor = Color.HextoRGBA('#B0C9EE')
    default_hint = GetByLabel('UI/Wallet/WalletWindow/LPDescription')
    default_height = 0.5
    default_padding = (2, 2, 2, 2)
    iconContainerSize = 32
    iconSize = 28
    __notifyevents__ = ['OnCharacterLPBalanceChange_Local']

    def __init__(self, **kwargs):
        self.loyaltyPointsWalletSvc = sm.GetService('loyaltyPointsWalletSvc')
        super(LoyaltyPointsTab, self).__init__(**kwargs)

    def ApplyAttributes(self, attributes):
        super(LoyaltyPointsTab, self).ApplyAttributes(attributes)
        sm.RegisterNotify(self)

    def ConstructDataContainer(self):
        dataContainer = Container(parent=self.mainContainer, align=uiconst.TOALL)
        self.tabNameLabel = EveLabelMediumBold(name='tabNameLabel', parent=dataContainer, align=uiconst.CENTERLEFT, left=6, text='')
        self.ConstructInfoIcon(dataContainer)
        self.Update()

    def Update(self):
        numCorpLPs = self.GetAmountOfCorporationsIHaveLoyaltyPointsWith()
        self.tabNameLabel.text = GetByLabel('UI/Wallet/WalletWindow/TabLPCorpNumber', numLPCorps=numCorpLPs)

    def GetAmountOfCorporationsIHaveLoyaltyPointsWith(self):
        return len(self.loyaltyPointsWalletSvc.GetAllCharacterLPBalancesExcludingEvermarks())

    def OnCharacterLPBalanceChange_Local(self, *args):
        self.Update()
