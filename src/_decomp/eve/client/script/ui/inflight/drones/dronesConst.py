#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\drones\dronesConst.py
import eveicon
from eve.client.script.ui import eveColor
from eve.common.script.mgt import entityConst as entities
DRONESTATE_INBAY = 'inbay'
DRONESTATE_INSPACE = 'inlocalspace'
DRONE_STATES = {entities.STATE_IDLE: 'UI/Inflight/Drone/Idle',
 entities.STATE_COMBAT: 'UI/Inflight/Drone/Fighting',
 entities.STATE_MINING: 'UI/Inflight/Drone/Mining',
 entities.STATE_APPROACHING: 'UI/Inflight/Drone/Approaching',
 entities.STATE_DEPARTING: 'UI/Inflight/Drone/ReturningToShip',
 entities.STATE_DEPARTING_2: 'UI/Inflight/Drone/ReturningToShip',
 entities.STATE_OPERATING: 'UI/Inflight/Drone/Operating',
 entities.STATE_PURSUIT: 'UI/Inflight/Drone/Following',
 entities.STATE_FLEEING: 'UI/Inflight/Drone/Fleeing',
 entities.STATE_ENGAGE: 'UI/Inflight/Drone/Repairing',
 entities.STATE_SALVAGING: 'UI/Inflight/Drone/Salvaging',
 None: 'UI/Inflight/Drone/NoState'}
DRONE_STATES_TEXTURES = {entities.STATE_IDLE: eveicon.hourglass,
 entities.STATE_COMBAT: eveicon.engage_target,
 entities.STATE_MINING: eveicon.mining,
 entities.STATE_APPROACHING: eveicon.approach,
 entities.STATE_DEPARTING: eveicon.recall_drones,
 entities.STATE_DEPARTING_2: eveicon.recall_drones,
 entities.STATE_PURSUIT: eveicon.visibility,
 entities.STATE_FLEEING: eveicon.flag,
 entities.STATE_ENGAGE: 'res:/UI/Texture/classes/Drones/repairing_16px.png',
 entities.STATE_SALVAGING: eveicon.salvage}
COLOR_BY_STATE = {entities.STATE_IDLE: eveColor.SUCCESS_GREEN_HEX,
 entities.STATE_COMBAT: eveColor.DANGER_RED_HEX,
 entities.STATE_MINING: eveColor.DANGER_RED_HEX,
 entities.STATE_APPROACHING: eveColor.SAND_YELLOW_HEX,
 entities.STATE_DEPARTING: eveColor.SAND_YELLOW_HEX,
 entities.STATE_DEPARTING_2: eveColor.SAND_YELLOW_HEX,
 entities.STATE_OPERATING: eveColor.DANGER_RED_HEX,
 entities.STATE_PURSUIT: eveColor.SAND_YELLOW_HEX,
 entities.STATE_FLEEING: eveColor.SAND_YELLOW_HEX,
 entities.STATE_ENGAGE: eveColor.SUCCESS_GREEN_HEX,
 entities.STATE_SALVAGING: eveColor.DANGER_RED_HEX}
damageIconInfo = {0: 'res:/UI/Texture/classes/Fitting/StatsIcons/structureHP.png',
 1: 'res:/UI/Texture/classes/Fitting/StatsIcons/armorHP.png',
 2: 'res:/UI/Texture/classes/Fitting/StatsIcons/shieldHP.png'}
