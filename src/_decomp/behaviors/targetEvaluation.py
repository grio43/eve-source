#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\targetEvaluation.py
from behaviors.const.combat import RANDOM_TARGET_EVALUATOR, THREAT_TARGET_EVALUATOR, COST_TARGET_EVALUATOR, TOWING_TOW_OBJECTIVE_EVALUATOR
from behaviors.const.combat import RANGE_TARGET_EVALUATOR, BASIC_TARGET_EVALUATOR, FITTED_MODULE_GROUP_TARGET_EVALUATOR
from behaviors.const.combat import SIZE_TARGET_EVALUATOR, SIGNATURE_RADIUS_AND_VELOCITY_EVALUATOR
from behaviors.utility.threat import evaluate_target
from ccpProfile import TimedFunction
from dogma.const import attributeSignatureRadius, attributeMaxVelocity
from inventorycommon.typeHelpers import GetAveragePrice
from random import random
from spacecomponents.common.components.towGameObjective import SLIM_KEY_TOWING_ID

class TargetEvaluator(object):

    def __init__(self, context, attributes):
        pass

    def EvaluateTarget(self, targetId):
        return 0


class RandomTargetEvaluator(TargetEvaluator):

    def EvaluateTarget(self, targetId):
        return random()


class SizeTargetEvaluator(TargetEvaluator):

    def __init__(self, context, attributes):
        super(SizeTargetEvaluator, self).__init__(context, attributes)
        self.inventory2 = context.ballpark.inventory2
        self.GetAttributeValue = context.dogmaLM.dogmaStaticMgr.GetTypeAttribute2

    @TimedFunction('behaviors::targetEvaluation::SizeTargetEvaluator::EvaluateTarget')
    def EvaluateTarget(self, targetId):
        typeId = self.inventory2.GetItem(targetId).typeID
        return self.GetAttributeValue(typeId, attributeSignatureRadius)


class ThreatTargetEvaluator(TargetEvaluator):

    def __init__(self, context, attributes):
        super(ThreatTargetEvaluator, self).__init__(context, attributes)
        self.threatSampleIntervalSeconds = getattr(attributes, 'threatSampleIntervalSeconds', 10)
        self.damageTracker = sm.GetService('damageTracker').GetTrackerForSystem(context.solarSystemId)
        self.dogmaLM = context.dogmaLM

    @TimedFunction('behaviors::targetEvaluation::ThreatTargetEvaluator::EvaluateTarget')
    def EvaluateTarget(self, targetId):
        return evaluate_target(self.damageTracker, self.dogmaLM, targetId, self.threatSampleIntervalSeconds)


class CostTargetEvaluator(TargetEvaluator):

    def __init__(self, context, attributes):
        super(CostTargetEvaluator, self).__init__(context, attributes)
        self.ballpark = context.ballpark

    @TimedFunction('behaviors::targetEvaluation::ThreatTargetEvaluator::EvaluateTarget')
    def EvaluateTarget(self, targetId):
        slimItem = self.ballpark.slims.get(targetId)
        return GetAveragePrice(slimItem.typeID) or 0.0


class FittedModuleGroupTargetEvaluator(TargetEvaluator):

    def __init__(self, context, attributes):
        super(FittedModuleGroupTargetEvaluator, self).__init__(context, attributes)
        self.dogmaLM = context.ballpark.dogmaLM
        self.preferredModuleGroups = getattr(attributes, 'preferredModuleGroups', [])

    @TimedFunction('behaviors::targetEvaluation::ShipGroupTargetEvaluator::EvaluateTarget')
    def EvaluateTarget(self, targetId):
        fittedModuleGroupIds = self.dogmaLM.GetFittedModulesGroupIdsForShip(targetId)
        for moduleGroupId in self.preferredModuleGroups:
            if moduleGroupId in fittedModuleGroupIds:
                return 1

        return 0


class RangeTargetEvaluator(TargetEvaluator):

    def __init__(self, context, attributes):
        super(RangeTargetEvaluator, self).__init__(context, attributes)
        self.my_ball_id = context.myBall.id
        self.distance_between = context.ballpark.DistanceBetween

    @TimedFunction('behaviors::targetEvaluation::ThreatTargetEvaluator::EvaluateTarget')
    def EvaluateTarget(self, target_id):
        distance = self.distance_between(self.my_ball_id, target_id)
        return 1 - distance


class SignatureRadiusAndVelocityEvaluator(TargetEvaluator):

    def __init__(self, context, attributes):
        super(SignatureRadiusAndVelocityEvaluator, self).__init__(context, attributes)
        self.inventory2 = context.ballpark.inventory2
        self.GetAttributeValue = context.dogmaLM.GetAttributeValue

    @TimedFunction('behaviors::targetEvaluation::SignatureRadiusAndVelocityEvaluator::EvaluateTarget')
    def EvaluateTarget(self, target_id):
        signature_radius = self.GetAttributeValue(target_id, attributeSignatureRadius)
        max_velocity = self.GetAttributeValue(target_id, attributeMaxVelocity)
        return signature_radius / max(1, max_velocity)


class TowingTowObjectiveEvaulator(TargetEvaluator):

    def __init__(self, context, attributes):
        super(TowingTowObjectiveEvaulator, self).__init__(context, attributes)
        self.GetInvItem = context.ballpark.GetInvItem

    @TimedFunction('behaviors::targetEvaluation::TowingTowObjectiveEvaulator::EvaluateTarget')
    def EvaluateTarget(self, target_id):
        slimItem = self.GetInvItem(target_id)
        if slimItem:
            towing = getattr(slimItem, SLIM_KEY_TOWING_ID, default=None)
            if towing is not None:
                return 1
            else:
                return 0
        else:
            return 0


targetEvaluationRegistry = {RANDOM_TARGET_EVALUATOR: RandomTargetEvaluator,
 SIZE_TARGET_EVALUATOR: SizeTargetEvaluator,
 THREAT_TARGET_EVALUATOR: ThreatTargetEvaluator,
 COST_TARGET_EVALUATOR: CostTargetEvaluator,
 BASIC_TARGET_EVALUATOR: TargetEvaluator,
 FITTED_MODULE_GROUP_TARGET_EVALUATOR: FittedModuleGroupTargetEvaluator,
 RANGE_TARGET_EVALUATOR: RangeTargetEvaluator,
 SIGNATURE_RADIUS_AND_VELOCITY_EVALUATOR: SignatureRadiusAndVelocityEvaluator,
 TOWING_TOW_OBJECTIVE_EVALUATOR: TowingTowObjectiveEvaulator}
