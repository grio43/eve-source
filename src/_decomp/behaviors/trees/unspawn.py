#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\trees\unspawn.py
from behaviors.composites import Sequence
from behaviors.conditions.blackboards import IsBlackboardValueTrue
from behaviors.const.blackboardchannels import UNSPAWN_ENTITY
from behaviors.monitors.blackboards import BlackboardMessageMonitor
from behaviors.trees.travel import CreateWarpAndUnspawnBehavior
from brennivin.itertoolsext import Bundle

def CreateUnspawnBehavior():
    return Sequence(Bundle(name='Unspawn Self')).AddSubTask(BlackboardMessageMonitor(Bundle(messageAddress=UNSPAWN_ENTITY))).AddSubTask(IsBlackboardValueTrue(Bundle(valueAddress=UNSPAWN_ENTITY))).AddSubTask(CreateWarpAndUnspawnBehavior())
