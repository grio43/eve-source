#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\redeem\window.py
from carbonui.control.window import Window
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.shared.redeem.redeemItemsContainer import RedeemItemsContainer
from eve.client.script.ui.shared.redeem.redeemUiConst import REDEEM_WINDOW_ID, REDEEM_NOTIFICATION_ID
HEADER_HEIGHT = 32

def GetRedeemWindow():
    return RedeemWindowDark


class RedeemWindowDark(Window):
    __notifyevents__ = ['OnRedeemingTokensUpdated', 'OnUIScalingChange']
    __guid__ = 'form.RedeemWindowDark'
    default_windowID = REDEEM_WINDOW_ID
    default_captionLabelPath = 'UI/RedeemWindow/RedeemItem'
    default_iconNum = 'res:/ui/Texture/WindowIcons/redeemingQueue.png'
    default_isStackable = False
    default_width = 760
    default_height = 640
    default_minSize = (default_width, default_height)

    def ApplyAttributes(self, attributes):
        super(RedeemWindowDark, self).ApplyAttributes(attributes)
        self.stationID = attributes.stationID
        self.charID = attributes.charID
        self.redeemData = attributes.redeemData
        self.ConstructLayout()
        self._RemoveNeocomNotifications()
        sm.ScatterEvent('OnRedeemWndOpened')

    def ConstructLayout(self):
        self.ConstructHeader()
        self.ConstructMain()

    def ConstructHeader(self):
        self.redeemIconLabelContainer = Container(name='IconAndLabelContainer', parent=self.sr.headerParent, align=uiconst.TOLEFT_PROP, width=0.3, padding=(8, 0, 0, 0))
        self.redeemIconSprite = Sprite(name='RedeemIconSprite', parent=Container(name='RedeemIconContainer', parent=self.redeemIconLabelContainer, align=uiconst.TOLEFT, width=20), align=uiconst.CENTER, state=uiconst.UI_DISABLED, width=20, height=20, texturePath=self.iconNum)

    def ConstructMain(self):
        self.redeemItemsContainer = RedeemItemsContainer(name='RedeemItemsContainer', parent=self.sr.main, align=uiconst.TOALL, state=uiconst.UI_NORMAL, redeemData=self.redeemData)
        self.RedeemAll = self.redeemItemsContainer.RedeemAll
        self.IsReady = self.redeemItemsContainer.IsReady

    def OnUIScalingChange(self, *args):
        self.sr.main.Flush()
        self.ConstructMain()

    def _RemoveNeocomNotifications(self):
        sm.GetService('redeem').MarkAllTokensSeen()
        sm.GetService('neocom').BlinkOff(REDEEM_NOTIFICATION_ID)

    def OnRedeemingTokensUpdated(self):
        if sm.GetService('redeem').GetRedeemTokenCount() == 0:
            self.CloseByUser()
