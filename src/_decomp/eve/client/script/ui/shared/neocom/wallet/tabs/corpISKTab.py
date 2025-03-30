#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\wallet\tabs\corpISKTab.py
import blue
from carbon.common.script.util.format import FmtAmt
from carbonui import uiconst
from carbonui.util.color import Color
from eve.client.script.ui.control.eveLabel import EveLabelMediumBold
from eve.client.script.ui.shared.neocom.wallet.tabs.baseWalletTab import BaseWalletTab
from eve.client.script.ui.shared.neocom.wallet.walletUtil import GetDivisionName, HaveAccessToCorpWallet, HaveAccessToCorpWalletAndActiveDivision
from localization import GetByLabel

class CorpISKTab(BaseWalletTab):
    default_name = 'CorpISKTab'
    default_texturePath = 'res:/UI/Texture/WindowIcons/wallet.png'
    default_underlayColor = Color.HextoRGBA('#6E966B')
    default_hint = GetByLabel('UI/Wallet/WalletWindow/CorpISKDescription')
    default_width = 0.5
    default_padding = (2, 2, 2, 2)
    __notifyevents__ = ['OnCorpAccountChangedClient']

    def ApplyAttributes(self, attributes):
        super(CorpISKTab, self).ApplyAttributes(attributes)
        sm.RegisterNotify(self)

    def Update(self):
        self.enabled = HaveAccessToCorpWallet()

    def ConstructTabNameLabel(self):
        text = '%s: %s' % (GetByLabel('Achievements/UI/active'), GetDivisionName(session.corpAccountKey)) if HaveAccessToCorpWallet() else ''
        self.tabNameLabel = EveLabelMediumBold(name='tabNameLabel', parent=self.topContainer, align=uiconst.CENTERLEFT, left=6, text=text)

    def PopulateBottomContainer(self):
        if not session.corpAccountKey:
            return
        if not HaveAccessToCorpWalletAndActiveDivision():
            return
        self.bottomLabel.SetText(FmtAmt(sm.GetService('wallet').GetCorpWealth()))

    def OnCorpAccountChangedClient(self, balance, accountKey, difference):
        if accountKey == session.corpAccountKey:
            self.AnimateBalanceChange(balance, difference)

    def AnimateBalanceChange(self, balance, difference):
        totalIterations = 20
        originalBalance = balance - difference
        for i in range(totalIterations):
            increment = (i + 1) / (1.0 * totalIterations)
            value = originalBalance + difference * increment
            self.bottomLabel.SetText(FmtAmt(value))
            blue.synchro.Sleep(25)
