#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\raffles\client\widget\wallet_balance.py
import eveui
import eveformat
from carbonui import TextColor
from raffles.client.localization import Text

class WalletBalance(eveui.ContainerAutoSize):
    default_state = eveui.State.normal

    def __init__(self, **kwargs):
        super(WalletBalance, self).__init__(**kwargs)
        self._wallet_svc = sm.GetService('wallet')
        self._layout()
        self._update_wealth()
        sm.RegisterForNotifyEvent(self, 'OnPersonalAccountChangedClient')

    def OnClick(self, *args):
        sm.GetService('cmd').OpenWallet()

    def Close(self):
        super(WalletBalance, self).Close()
        sm.UnregisterForNotifyEvent(self, 'OnPersonalAccountChangedClient')

    def OnPersonalAccountChangedClient(self, *args, **kwargs):
        self._update_wealth()

    def _update_wealth(self):
        wealth = self._wallet_svc.GetWealth()
        self.isk_amount_label.text = eveformat.isk(wealth)
        self.hint = eveformat.isk_readable(wealth)

    def _layout(self):
        eveui.EveLabelSmall(parent=self, align=eveui.Align.top_right, text=Text.wallet_balance(), color=TextColor.SECONDARY)
        self.isk_amount_label = eveui.EveLabelMediumBold(parent=self, align=eveui.Align.top_right, top=12)
