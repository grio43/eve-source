#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\wallet\tabs\plexTab.py
import logging
from carbon.common.script.util.format import FmtAmt
from carbonui import uiconst
from carbonui.uicore import uicore
from carbonui.util.color import Color
from eve.client.script.ui.control.buttons import ButtonTextBoldness
from eve.client.script.ui.plex.textures import PLEX_128_GRADIENT_YELLOW
from eve.client.script.ui.shared.neocom.wallet.tabs.baseWalletTab import BaseWalletTab
from fastcheckout.client.purchasepanels.purchaseButton import SecondaryPurchaseButton
from fastcheckout.const import FROM_WALLET_PLUS_BUTTON
from localization import GetByLabel
from uthread2 import StartTasklet
logger = logging.getLogger(__name__)

class PlexTab(BaseWalletTab):
    default_name = 'PlexTab'
    default_texturePath = PLEX_128_GRADIENT_YELLOW
    tabNamePath = 'UI/Common/PLEX'
    default_underlayColor = Color.HextoRGBA('#E7B24C')
    labelColor = Color.HextoRGBA('#FAB400')
    default_hint = GetByLabel('UI/Wallet/WalletWindow/PLEXDescription')
    default_padding = (2, 2, 2, 2)

    def ApplyAttributes(self, attributes):
        super(PlexTab, self).ApplyAttributes(attributes)
        StartTasklet(self.UpdateBalance)
        self.GetAccount().accountAurumBalanceChanged.connect(self.UpdateBalance)

    def PopulateBottomContainer(self):
        buyPlexButtonTextColor = Color.WHITE
        buyPlexButtonSize = 20
        self.buyPlexButton = SecondaryPurchaseButton(name='buyPlexButton_+', parent=self.bottomContainer, align=uiconst.CENTERRIGHT, width=buyPlexButtonSize, height=buyPlexButtonSize, left=6, func=lambda *args: uicore.cmd.CmdBuyPlex(logContext=FROM_WALLET_PLUS_BUTTON), text=GetByLabel('UI/Wallet/WalletWindow/BuyPlex'), hint=GetByLabel('UI/VirtualGoodsStore/Buttons/BuyPlex'), mouseUpTextColor=buyPlexButtonTextColor, mouseEnterTextColor=buyPlexButtonTextColor, mouseDownTextColor=buyPlexButtonTextColor, disabledTextColor=buyPlexButtonTextColor, boldText=ButtonTextBoldness.NEVER_BOLD)
        self.bottomLabel.SetRGBA(*Color.HextoRGBA('#FAB400'))

    def GetAccount(self):
        return sm.GetService('vgsService').GetStore().GetAccount()

    def UpdateBalance(self, balance = None, *args, **kwargs):
        if balance is None:
            balance = self.GetBalance()
        self.bottomLabel.SetText(FmtAmt(balance))

    def GetBalance(self):
        account = self.GetAccount()
        try:
            return account.GetAurumBalance()
        except Exception:
            logger.warning('Failed to retrieve the PLEX balance in Wallet', exc_info=True)
            return 0
