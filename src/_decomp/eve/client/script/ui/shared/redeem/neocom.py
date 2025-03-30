#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\redeem\neocom.py
from eve.client.script.ui.shared.neocom.neocom import neocomConst
from eve.client.script.ui.shared.neocom.neocom.btnData.btnDataNodeNotification import BtnDataNodeNotification
from eve.client.script.ui.shared.neocom.neocom.fixedButtonExtension import OnlyShowWhenAvailableExtension
from eve.client.script.ui.shared.redeem.redeemUiConst import OPEN_REDEEM_WINDOW_COMMAND_NAME, REDEEM_ICON_PATH, REDEEM_NOTIFICATION_ID, NEW_TOKENS_UI_HIGHLIGHT
from localization import GetByLabel

class UnseenRedeemItemsBtnData(BtnDataNodeNotification):
    default_btnType = neocomConst.BTNTYPE_REDEEM
    default_cmdName = OPEN_REDEEM_WINDOW_COMMAND_NAME
    default_iconPath = REDEEM_ICON_PATH
    default_btnID = REDEEM_NOTIFICATION_ID
    __notifyevents__ = ['OnRedeemingTokensUpdated', 'OnRedeemWndOpened']

    @property
    def default_label(self):
        return GetByLabel('UI/Redeem/NewRedeemItemsNotificationDescription')

    def GetItemCount(self):
        return sm.GetService('redeem').GetUnseenTokensCount()

    def OnRedeemingTokensUpdated(self):
        self.OnBadgeCountChanged()

    def OnRedeemWndOpened(self):
        self.OnBadgeCountChanged()


class RedeemIconExtension(OnlyShowWhenAvailableExtension):
    pass
