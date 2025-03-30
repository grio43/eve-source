#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\pirateinsurgency\client\utils.py


def CalculateCurrentStageFromFraction(numerator, denominator, stageThresholds):
    value = float(numerator) / float(denominator)
    stage = 0
    for threshold in stageThresholds:
        if value >= threshold:
            stage += 1
        else:
            return stage

    return stage
