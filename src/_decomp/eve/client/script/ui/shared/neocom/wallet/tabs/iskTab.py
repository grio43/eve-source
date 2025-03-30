#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\wallet\tabs\iskTab.py
import blue
from carbon.common.script.util.format import FmtAmt
from carbonui.util.color import Color
from eve.client.script.ui.shared.neocom.wallet.tabs.baseWalletTab import BaseWalletTab
from localization import GetByLabel

class IskTab(BaseWalletTab):
    default_name = 'IskTab'
    default_texturePath = 'res:/UI/Texture/WindowIcons/wallet.png'
    tabNamePath = 'UI/Wallet/WalletWindow/ISK'
    default_underlayColor = Color.HextoRGBA('#6E966B')
    default_hint = GetByLabel('UI/Wallet/WalletWindow/ISKDescription')
    default_padding = (2, 2, 2, 2)
    amountFontSize = 14
    __notifyevents__ = ['OnPersonalAccountChangedClient']

    def ApplyAttributes(self, attributes):
        super(IskTab, self).ApplyAttributes(attributes)
        sm.RegisterNotify(self)

    def PopulateBottomContainer(self):
        self.bottomLabel.SetText(FmtAmt(sm.GetService('wallet').GetWealth()))

    def OnPersonalAccountChangedClient(self, balance, difference):
        self.AnimateBalanceChange(balance, difference)

    def AnimateBalanceChange(self, balance, difference):
        totalIterations = 20
        originalBalance = balance - difference
        for i in range(totalIterations):
            increment = (i + 1) / (1.0 * totalIterations)
            value = originalBalance + difference * increment
            self.bottomLabel.SetText(FmtAmt(value))
            blue.synchro.Sleep(25)
