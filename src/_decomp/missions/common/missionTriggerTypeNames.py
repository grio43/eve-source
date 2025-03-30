#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\missions\common\missionTriggerTypeNames.py
from evedungeons.common.triggers import dunTriggerArchaeologyFailure, dunTriggerArchaeologySuccess
from evedungeons.common.triggers import dunTriggerArmorConditionLevel, dunTriggerAttacked, dunTriggerCounterEQ, dunTriggerCounterGE
from evedungeons.common.triggers import dunTriggerCounterGT, dunTriggerCounterLE, dunTriggerCounterLT, dunTriggerEffectActivated
from evedungeons.common.triggers import dunTriggerExploding, dunTriggerFWShipEnteredProximity, dunTriggerFWShipLeftProximity
from evedungeons.common.triggers import dunTriggerHackingFailure, dunTriggerHackingSuccess, dunTriggerItemInCargo
from evedungeons.common.triggers import dunTriggerItemPlacedInMissionContainer, dunTriggerItemRemovedFromSpawnContainer
from evedungeons.common.triggers import dunTriggerMined, dunTriggerPlayerKilled, dunTriggerRoomCapturedAlliance
from evedungeons.common.triggers import dunTriggerRoomCapturedFacWar, dunTriggerRoomCapturedCorp, dunTriggerRoomEntered
from evedungeons.common.triggers import dunTriggerRoomMined, dunTriggerRoomMinedOut, dunTriggerRoomWipedOut
from evedungeons.common.triggers import dunTriggerSalvagingFailure, dunTriggerSalvagingSuccess, dunTriggerShieldConditionLevel
from evedungeons.common.triggers import dunTriggerShipEnteredProximity, dunTriggerShipLeftProximity, dunTriggerShipsEnteredRoom
from evedungeons.common.triggers import dunTriggerShipsLeftRoom, dunTriggerStructureConditionLevel, dunTriggerTimerComplete
from evedungeons.common.triggers import dunTriggerHackingInitialize
from evedungeons.common.triggers import dunTriggerOccupierReachedThreshold, dunTriggerAttackerReachedThreshold
NAME_BY_TRIGGER_TYPE = {dunTriggerArchaeologyFailure: 'dunTriggerArchaeologyFailure',
 dunTriggerArchaeologySuccess: 'dunTriggerArchaeologySuccess',
 dunTriggerArmorConditionLevel: 'dunTriggerArmorConditionLevel',
 dunTriggerAttacked: 'Attack',
 dunTriggerCounterEQ: 'dunTriggerCounterEQ',
 dunTriggerCounterGE: 'dunTriggerCounterGE',
 dunTriggerCounterGT: 'dunTriggerCounterGT',
 dunTriggerCounterLE: 'dunTriggerCounterLE',
 dunTriggerCounterLT: 'dunTriggerCounterLT',
 dunTriggerEffectActivated: 'dunTriggerEffectActivated',
 dunTriggerExploding: 'KillTrigger',
 dunTriggerFWShipEnteredProximity: 'dunTriggerFWShipEnteredProximity',
 dunTriggerFWShipLeftProximity: 'dunTriggerFWShipLeftProximity',
 dunTriggerHackingFailure: 'dunTriggerHackingFailure',
 dunTriggerHackingSuccess: 'Hack',
 dunTriggerHackingInitialize: 'dunTriggerHackingInitialize',
 dunTriggerItemInCargo: 'EventObtain',
 dunTriggerItemPlacedInMissionContainer: 'Place item in container',
 dunTriggerItemRemovedFromSpawnContainer: 'Remove item from container',
 dunTriggerMined: 'MissionFetchMineTrigger',
 dunTriggerPlayerKilled: 'EventGetKilled',
 dunTriggerRoomCapturedAlliance: 'dunTriggerRoomCapturedAlliance',
 dunTriggerRoomCapturedFacWar: 'dunTriggerRoomCapturedFacWar',
 dunTriggerRoomCapturedCorp: 'dunTriggerRoomCapturedCorp',
 dunTriggerRoomEntered: 'EventEnterRoom',
 dunTriggerRoomMined: 'MissionFetchMineTrigger',
 dunTriggerRoomMinedOut: 'MissionFetchMineTrigger',
 dunTriggerRoomWipedOut: 'Destroy all the enemies',
 dunTriggerSalvagingFailure: 'dunTriggerSalvagingFailure',
 dunTriggerSalvagingSuccess: 'Salvage',
 dunTriggerShieldConditionLevel: 'dunTriggerShieldConditionLevel',
 dunTriggerShipEnteredProximity: 'Approach',
 dunTriggerShipLeftProximity: 'dunTriggerShipLeftProximity',
 dunTriggerShipsEnteredRoom: 'dunTriggerShipsEnteredRoom',
 dunTriggerShipsLeftRoom: 'dunTriggerShipsLeftRoom',
 dunTriggerStructureConditionLevel: 'Damage structure to',
 dunTriggerTimerComplete: 'dunTriggerTimerComplete',
 dunTriggerOccupierReachedThreshold: 'dunTriggerOccupierReachedThreshold',
 dunTriggerAttackerReachedThreshold: 'dunTriggerAttackerReachedThreshold'}
