#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\neocom\btnData\btnDataNodeEvent.py
from eve.client.script.ui.shared.neocom.neocom.btnData.btnDataNodeNotification import BtnDataNodeNotification

class BtnDataNodeEvent(BtnDataNodeNotification):
    __notifyevents__ = ['OnEventRewardsUpdated']

    def OnEventRewardsUpdated(self):
        self.OnBadgeCountChanged()

    def GetItemCount(self):
        return sm.GetService('seasonService').get_claimable_rewards_count()
