#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\careerPortal\neocom.py
from careergoals.client.career_goal_svc import get_career_goals_svc
from careergoals.client.signal import on_states_loaded, on_goal_completed, on_reward_claimed
from eve.client.script.ui.shared.neocom.neocom.btnData.btnDataNodeNotification import BtnDataNodeNotification
from eve.client.script.ui.shared.neocom.neocom import neocomConst
from localization import GetByLabel

class BtnDataNodeAirCareerProgram(BtnDataNodeNotification):
    default_btnType = neocomConst.BTNTYPE_CAREER_PROGRAM
    default_cmdName = 'CmdToggleAirCareerProgram'
    default_iconPath = 'res:/ui/texture/windowIcons/airCareerProgram.png'
    default_isBlinking = False
    default_isDraggable = True
    default_isRemovable = True

    def __init__(self, parent = None, iconPath = None, label = None, btnID = None, isBlinking = None, cmdName = None, btnType = None, isRemovable = None, labelAbbrev = None, wndCls = None, isDraggable = None, children = None, **kwargs):
        BtnDataNodeNotification.__init__(self, parent, iconPath, label, btnID, isBlinking, cmdName, btnType, isRemovable, labelAbbrev, wndCls, isDraggable, children, **kwargs)
        on_states_loaded.connect(self.OnClaimableGoalsChanged)
        on_reward_claimed.connect(self.OnClaimableGoalsChanged)
        on_goal_completed.connect(self.OnClaimableGoalsChanged)

    def OnClaimableGoalsChanged(self, *args):
        self.OnBadgeCountChanged()

    def GetItemCount(self):
        if get_career_goals_svc().get_goal_data_controller().are_goals_loaded():
            return get_career_goals_svc().get_goal_data_controller().get_claimable_rewards_count()
        return 0

    def GetUnseenItemsHint(self):
        numItems = self.GetItemCount()
        if numItems:
            return GetByLabel('UI/Neocom/NumUnclaimedRewards', numItems=numItems)
