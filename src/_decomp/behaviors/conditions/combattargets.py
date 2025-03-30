#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\conditions\combattargets.py
from behaviors.const.combat import COMBAT_MIN_EFFECTIVE_RANGE
from behaviors.tasks import Task
from behaviors.utility.ballparks import is_ball_in_range, is_coordinate_in_range
from behaviors.utility.roles import is_logistic_role
from ccpProfile import TimedFunction
MAX_DISTANCE_FROM_COMMANDER = 50000

class HasPendingTarget(Task):

    @TimedFunction('behaviors::conditions::combattargets::HasPendingTarget::OnEnter')
    def OnEnter(self):
        if self.context.dogmaLM.HasPendingTarget(self.context.myItemId, self._get_my_target()):
            self.SetStatusToSuccess()
        else:
            self.SetStatusToFailed()

    def _get_my_target(self):
        return self.GetLastBlackboardValue(self.attributes.targetAddress)


class AmIWithinMyEffectiveCombatRangeOfMyTarget(Task):

    @TimedFunction('behaviors::conditions::combattargets::AmIWithinMyEffectiveCombatRangeOfMyTarget::OnEnter')
    def OnEnter(self):
        self.SetStatusToFailed()
        max_effective_combat_range = self.get_my_max_effective_combat_range()
        if self._is_within_range(max_effective_combat_range):
            self.SetStatusToSuccess()

    def get_my_max_effective_combat_range(self):
        max_effective_combat_range = self.GetLastBlackboardValue(self.attributes.maxEffectiveCombatRangeAddress)
        return max(max_effective_combat_range, COMBAT_MIN_EFFECTIVE_RANGE)

    def _is_within_range(self, max_effective_combat_range):
        target_id = self.GetLastBlackboardValue(self.attributes.targetAddress)
        orbit_target_id = self.GetLastBlackboardValue(self.attributes.orbitTargetAddress)
        commander_id = self.GetLastBlackboardValue(self.attributes.commanderAddress)
        if orbit_target_id != commander_id:
            return is_ball_in_range(self, self.context.myBall.id, target_id, max_effective_combat_range)
        elif is_logistic_role(self, self.context.myItemId):
            return is_ball_in_range(self, self.context.myBall.id, orbit_target_id, max_effective_combat_range)
        else:
            return is_ball_in_range(self, self.context.myBall.id, orbit_target_id, MAX_DISTANCE_FROM_COMMANDER)


class IsCoordinateWithinMyEffectiveCombatRange(AmIWithinMyEffectiveCombatRangeOfMyTarget):

    def _is_within_range(self, max_effective_combat_range):
        coordinate = self.GetLastBlackboardValue(self.attributes.coordinateAddress)
        return is_coordinate_in_range(self, coordinate, max_effective_combat_range)


class IsTargeting(Task):

    @TimedFunction('behaviors::conditions::combattargets::IsTargeting::OnEnter')
    def OnEnter(self):
        if self.context.dogmaLM.IsTargeting(self.context.myItemId, self._get_my_target()):
            self.SetStatusToSuccess()
        else:
            self.SetStatusToFailed()

    def _get_my_target(self):
        return self.GetLastBlackboardValue(self.attributes.targetAddress)
