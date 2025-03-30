#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\trees\corpsedisposal.py
from behaviors.composites import Sequence
from brennivin.itertoolsext import Bundle
from behaviors.trees.corpseharvesting import CORPSE_TYPES
from behaviors.trees.drifters.disappear import WORMHOLE_TYPE_IDS, WORMHOLE
from behaviors.actions.entities import RemoveTypesFromAdditionalLoot
from behaviors.conditions.entities import HasAnyOfTypesInEntityAdditionalLoot
from behaviors.actions.ballparks import GetItemIdByTypeId, ApproachObject

def CreateCorpseDisposalBehavior():
    return Sequence(Bundle(name='Corpse Disposal')).AddSubTask(HasAnyOfTypesInEntityAdditionalLoot(Bundle(name='Check For Corpses In Loot', typeIds=CORPSE_TYPES))).AddSubTask(GetItemIdByTypeId(Bundle(name='Get Wormhole ID', typeIds=WORMHOLE_TYPE_IDS, itemIdAddress=WORMHOLE))).AddSubTask(ApproachObject(Bundle(name='Approach Wormhole', itemIdAddress=WORMHOLE, notifyRange=2500, approachRange=500, blocking=True))).AddSubTask(RemoveTypesFromAdditionalLoot(Bundle(name='Dispose Of Corpses', typeIds=CORPSE_TYPES)))
