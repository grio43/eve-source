#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\neocom\btnData\btnDataJobBoard.py
import uthread2
from localization import GetByLabel
from eve.client.script.ui.shared.neocom.neocom.btnData.btnDataNode import BtnDataNode
from corporation.client.goals.goalsController import CorpGoalsController
import corporation.client.goals.goalSignals as corpGoalsSignals
from dailygoals.client.goalsController import DailyGoalsController
import dailygoals.client.goalSignals as dailyGoalSignals
_has_unclaimed = False

class BtnDataNodeJobBoard(BtnDataNode):

    def __init__(self, *args, **kwargs):
        BtnDataNode.__init__(self, *args, **kwargs)
        dailyGoalSignals.on_unclaimed_goal_ids_changed.connect(self._update_badge)
        corpGoalsSignals.on_unclaimed_goal_ids_changed.connect(self._update_badge)
        self._update_badge()

    def _disconnect_signals(self):
        BtnDataNode._disconnect_signals(self)
        dailyGoalSignals.on_unclaimed_goal_ids_changed.disconnect(self._update_badge)
        corpGoalsSignals.on_unclaimed_goal_ids_changed.disconnect(self._update_badge)

    @uthread2.debounce(1)
    def _update_badge(self, *args, **kwargs):
        if not session.charid or self.destroyed:
            return
        has_unclaimed = DailyGoalsController.get_instance().has_unclaimed_rewards()
        if not has_unclaimed:
            has_unclaimed = CorpGoalsController.get_instance().has_unclaimed_rewards()
        self._update_has_unclaimed(has_unclaimed)

    def _update_has_unclaimed(self, value):
        global _has_unclaimed
        if value != _has_unclaimed:
            _has_unclaimed = value
            self.OnBadgeCountChanged()

    def GetItemCount(self):
        if _has_unclaimed:
            return 1
        return 0

    def GetUnseenItemsHint(self):
        numItems = self.GetItemCount()
        if numItems:
            return GetByLabel('UI/Neocom/UnclaimedRewards')
