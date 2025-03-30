#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\parklife\targetUtils.py
from collections import namedtuple
from inventorycommon.const import categoryEntity

def get_closest_entity_target(target_priority = None, max_radius = 500000):
    michelle = sm.GetService('michelle')
    ballpark = michelle.GetBallpark()
    if ballpark is None or michelle.InWarp():
        return
    entities_in_range = ballpark.GetItemsAndDistanceByCategory(categoryID=categoryEntity, maxRadius=max_radius)
    TargetCandidate = namedtuple('TargetCandidate', 'groupID, distance, itemID')
    target_candidates = [ TargetCandidate(entity.groupID, distance, entity.itemID) for distance, entity in entities_in_range ]
    if target_priority is None:
        target_candidates = sorted(target_candidates, key=lambda candidate: candidate.distance)
    else:
        target_candidates = sorted([ candidate for candidate in target_candidates if candidate.groupID in target_priority ], key=lambda candidate: (target_priority.index(candidate.groupID), candidate.distance))
    if target_candidates:
        _, _, closest_entity_id = target_candidates[0]
        return closest_entity_id
