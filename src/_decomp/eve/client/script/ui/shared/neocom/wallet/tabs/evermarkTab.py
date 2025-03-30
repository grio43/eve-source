#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\wallet\tabs\evermarkTab.py
import evetypes
from appConst import corpHeraldry
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.util.color import Color
from eve.client.script.ui.shared.neocom.wallet.tabs.baseWalletTab import BaseWalletTab
from eve.client.script.ui.shared.neocom.wallet.walletUtil import HaveAccessToCorpEMWallet
from inventorycommon.const import typeLoyaltyPointsHeraldry
from localization import GetByLabel
from eve.client.script.ui.control.eveLabel import EveLabelMediumBold

class CorpEverMarkTab(BaseWalletTab):
    default_name = 'CorpEverMarkTab'
    default_height = 0.5
    default_texturePath = 'res:/ui/texture/WindowIcons/evermark_24px.png'
    default_underlayColor = Color.HextoRGBA('#6E966B')
    default_hint = evetypes.GetDescription(typeLoyaltyPointsHeraldry)
    default_padding = (2, 2, 2, 2)
    iconContainerSize = 32
    iconSize = 24
    __notifyevents__ = ['OnCorporationLPBalanceChange_Local']

    def ApplyAttributes(self, attributes):
        super(CorpEverMarkTab, self).ApplyAttributes(attributes)
        sm.RegisterNotify(self)

    def ConstructDataContainer(self):
        dataContainer = Container(parent=self.mainContainer, align=uiconst.TOALL)
        self.tabNameLabel = EveLabelMediumBold(name='tabNameLabel', parent=dataContainer, align=uiconst.CENTERLEFT, left=6, text='')
        self.ConstructInfoIcon(dataContainer)
        self.Update()

    def Update(self):
        self.enabled = HaveAccessToCorpEMWallet()
        if not HaveAccessToCorpEMWallet():
            return
        everMarks = sm.GetService('loyaltyPointsWalletSvc').GetCorporationEvermarkBalance()
        self.tabNameLabel.text = GetByLabel('UI/Wallet/WalletWindow/EvermarkAmount', everMarkAmount=everMarks)

    def OnCorporationLPBalanceChange_Local(self, issuerCorpID):
        if issuerCorpID == corpHeraldry:
            self.Update()


class EverMarkTab(BaseWalletTab):
    default_name = 'EvermarkTab'
    default_height = 0.5
    default_texturePath = 'res:/ui/texture/WindowIcons/evermark_24px.png'
    default_underlayColor = Color.HextoRGBA('#6E966B')
    default_hint = evetypes.GetDescription(typeLoyaltyPointsHeraldry)
    default_padding = (2, 2, 2, 2)
    iconContainerSize = 32
    iconSize = 24
    __notifyevents__ = ['OnCharacterLPBalanceChange_Local']

    def ApplyAttributes(self, attributes):
        super(EverMarkTab, self).ApplyAttributes(attributes)
        sm.RegisterNotify(self)

    def ConstructDataContainer(self):
        dataContainer = Container(parent=self.mainContainer, align=uiconst.TOALL)
        self.tabNameLabel = EveLabelMediumBold(name='tabNameLabel', parent=dataContainer, align=uiconst.CENTERLEFT, left=6, text='')
        self.ConstructInfoIcon(dataContainer)
        self.Update()

    def Update(self):
        everMarks = sm.GetService('loyaltyPointsWalletSvc').GetCharacterEvermarkBalance()
        self.tabNameLabel.text = GetByLabel('UI/Wallet/WalletWindow/EvermarkAmount', everMarkAmount=everMarks)

    def PopulateBottomContainer(self):
        pass

    def OnCharacterLPBalanceChange_Local(self, issuerCorpID, _lpBefore, _lpAfter):
        if issuerCorpID == corpHeraldry:
            self.Update()
