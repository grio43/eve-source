#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\vgs\aurBalance.py
from carbon.common.script.util.format import FmtAmt
from carbonui import const as uiconst
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from eve.client.script.ui.plex.textures import PLEX_32_GRADIENT_YELLOW
from eve.client.script.ui.shared.vgs.label import VgsHeaderMedium, VgsLabelSmall
import localization

class AurBalance(ContainerAutoSize):

    def ApplyAttributes(self, attributes):
        super(AurBalance, self).ApplyAttributes(attributes)
        account = attributes.account
        self.AddIcon()
        self.AddLabel()
        self.AddAmount(account)

    def AddIcon(self):
        self.icon = Sprite(name='plexIcon', parent=self, align=uiconst.TOPLEFT, width=32, height=32, left=-4, texturePath=PLEX_32_GRADIENT_YELLOW)

    def AddLabel(self):
        self.balanceLabel = VgsLabelSmall(parent=self, align=uiconst.TOPLEFT, top=-3, left=self.icon.width + 4, text=localization.GetByLabel('UI/VirtualGoodsStore/AurBalance'), color=(1, 1, 1, 0.5))

    def AddAmount(self, account):
        self.balanceAmountLabel = VgsHeaderMedium(parent=self, align=uiconst.TOPLEFT, top=self.balanceLabel.height - 6, left=self.icon.width + 4)
        self.balance = account.GetAurumBalance()
        account.SubscribeToAurumBalanceChanged(self.OnBalanceChange)

    @property
    def balance(self):
        return self._balance

    @balance.setter
    def balance(self, value):
        self._balance = value
        self.balanceAmountLabel.SetText(FmtAmt(self._balance))

    def OnBalanceChange(self, balance, *args, **kwargs):

        def callback():
            self.balance = balance

        animations.MorphScalar(self, 'balance', startVal=self.balance, endVal=balance, curveType=uiconst.ANIM_SMOOTH, duration=1.5, callback=callback)
