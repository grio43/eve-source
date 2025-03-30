#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\loginRewards\neocomBtn.py
from neocom2.btnIDs import LOGIN_REWARDS_ID
from eve.client.script.ui.shared.neocom.neocom import neocomConst
from eve.client.script.ui.shared.neocom.neocom.btnData.btnDataNodeNotification import BtnDataNodeNotification
from eve.client.script.ui.shared.neocom.neocom.btnData.btnDataRaw import BTNDATARAW_BY_ID
from eve.client.script.ui.shared.neocom.neocom.fixedButtonExtension import UnseenItemsExtension
from localization import GetByLabel
btnID = LOGIN_REWARDS_ID
btnData = BTNDATARAW_BY_ID[btnID]

class RewardsBtnData(BtnDataNodeNotification):
    default_btnType = neocomConst.BTNTYPE_REWARD
    default_cmdName = btnData.cmdName
    default_iconPath = btnData.iconPath
    default_btnID = btnID
    descriptionPath = 'UI/LoginRewards/WindowDescription'
    __notifyevents__ = ['OnDailyCampaignAwardClaimed', 'OnLoginRewardWindowOpened']

    def OnDailyCampaignAwardClaimed(self, *args):
        self.OnBadgeCountChanged()

    def OnLoginRewardWindowOpened(self):
        self.OnBadgeCountChanged()

    @property
    def default_label(self):
        return GetByLabel('UI/LoginRewards/WindowCaption')

    def GetItemCount(self):
        return len(sm.GetService('loginCampaignService').get_rewards_available())


class UnseenRewardsItemsExtension(UnseenItemsExtension):

    def __init__(self, button_data_class, get_badge_count, is_visible_function):
        self.is_visible_function = is_visible_function
        UnseenItemsExtension.__init__(self, button_data_class, get_badge_count)

    @property
    def is_visible(self):
        return self.is_visible_function()
