#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\trees\drifters\drifter_aggression.py
from behaviors.monitors.effects import EffectUsageMonitor
from behaviors.trees.combat import COMBAT_TARGETS_SET
from brennivin.itertoolsext import Bundle
from dogma.const import effectEntosisLink

def CreateDrifterEntosisAggressionBehavior():
    return EffectUsageMonitor(Bundle(shipIdSetAddress=COMBAT_TARGETS_SET, effectId=effectEntosisLink))
