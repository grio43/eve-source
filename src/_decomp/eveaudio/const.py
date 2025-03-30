#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveaudio\const.py
import os
from enum import Enum
import audio2
from inventorycommon import const
from utils import ControllerVariableEnum

class ShipState(Enum):
    preparing_warp = 0
    warping = 1
    idle = 2


AUDIO_SOURCES_P4_DEPOT_PATH = '//depot/content/EVE/Audio/EVE-Audio/Originals'
GENERATED_SOUNDBANKS_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'eve', 'client', 'res', 'Audio'))
WWISE_PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'audiotools', 'Wwise'))
WWISE_BIN_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'carbon', 'tools', 'audiotools', 'Authoring', audio2.GetWwiseVersion(), 'x64', 'Release', 'bin'))
WWISE_CLI_PATH = os.path.join(WWISE_BIN_PATH, 'WwiseConsole.exe')
MASTER_MUSIC_GRAPH = 805
UI_AUDIO_TRIGGERS = {'arena_opponent_matched': 'ui_pvp_arena_opponent_matched',
 'warp_prep': 'warp_ship_init',
 'warp_prep_abort': 'warp_ship_abort'}
PI_AUDIO_TRIGGERS = {const.typePlanetEarthlike: 'terrestrial_pi_play',
 const.typePlanetGas: 'gas_pi_play',
 const.typePlanetIce: 'ice_pi_play',
 const.typePlanetLava: 'lava_pi_play',
 const.typePlanetOcean: 'oceanic_pi_play',
 const.typePlanetSandstorm: 'barren_pi_play',
 const.typePlanetThunderstorm: 'storm_pi_play',
 const.typePlanetPlasma: 'plasma_pi_play',
 const.typePlanetShattered: 'plasma_pi_play',
 const.typePlanetScorched: 'plasma_pi_play'}
PLANET_3D_AUDIO_TRIGGERS = {const.typePlanetEarthlike: 'terrestrial_3d_play',
 const.typePlanetGas: 'gas_3d_play',
 const.typePlanetIce: 'ice_3d_play',
 const.typePlanetLava: 'lava_3d_play',
 const.typePlanetOcean: 'oceanic_3d_play',
 const.typePlanetSandstorm: 'barren_3d_play',
 const.typePlanetThunderstorm: 'storm_3d_play',
 const.typePlanetPlasma: 'plasma_3d_play',
 const.typePlanetShattered: 'plasma_3d_play',
 const.typePlanetScorched: 'plasma_3d_play'}
TRIG_PLANET_3D_TRIGGER = 'triglavian_planet_atmo_3d_play'
TRIG_PLANET_PI_TRIGGER = 'triglavian_planet_atmo_pi_play'
VIDEO_OVERLAY_STATE_ON = ('video_overlay', 'on')
VIDEO_OVERLAY_STATE_OFF = ('video_overlay', 'off')
MICROWARPDRIVE_GUID = 'effects.MicroWarpDrive'
AFTERBURNER_GUID = 'effects.Afterburner'
WARPING_GUID = 'effects.Warping'

class ModuleState(ControllerVariableEnum):
    deactivated = 1
    activated = 2
    powerdown = 3


class ModuleType(ControllerVariableEnum):
    microwarpdrive = 1
    afterburner = 2


class WarpState(ControllerVariableEnum):
    prep = 1
    start = 2
    decelerate = 3
    stop = 4
    finished = 5


class ActingParty(ControllerVariableEnum):
    firstParty = 1
    thirdParty = 2


STOP_SHIP_CTRL_VARIABLE = 'StopShipRequested'
ENGINE_LIMIT_MAX = 200
ENGINE_LIMIT_MIN = 40
ENGINE_LIMIT_RTPC = 'engine_voice_limit'
ENGINE_LIMITING_CATEGORIES = [const.categoryEntity, const.categoryShip]
USER_ERROR_KEY_TO_EVENT = {'CrystalRequired': 'msg_NoCharges_play',
 'NoCharges': 'msg_NoCharges_play',
 'NotEnoughCharges': 'msg_NoCharges_play',
 'WarpDriveActive': 'msg_WarpDriveActive_play'}
AURA_MESSAGES = ['msg_AlreadyCloaking_play',
 'msg_AutoPilotApproaching_play',
 'msg_AutoPilotApproachingStation_play',
 'msg_MiningDronesDeactivatedAsteroidEmpty_play',
 'msg_AutoPilotDisabled_play',
 'msg_AutoPilotDisabled_playlotDisabledStuckSystem_play',
 'msg_AutoPilotDisabledUnreachable_play',
 'msg_AutoPilotDisabledNoPathSet_play',
 'msg_AutoPilotWaypointReached_play',
 'msg_AutoPilotEnabled_play',
 'msg_AutoPilotJumping_play',
 'msg_AutoPilotWarpingTo_play',
 'msg_CannotMergeSingletonItems_play',
 'msg_CannotRemoveFromThatLocation_play',
 'msg_CannotSellActiveShip_play',
 'msg_CantAnchorNoMoonNearby_play',
 'msg_CantBuildNoPlanetNearby_play',
 'msg_CantCloakTargeted_play',
 'msg_CantCloakTargeting_play',
 'msg_CantConfigureDistant_play',
 'msg_CantConfigureNotOwner_play',
 'msg_CantConfigureThat_play',
 'msg_CantDockWhileCloaked_play',
 'msg_CantInEmpireSpace_play',
 'msg_CantInEmpireSpace2_play',
 'msg_CantJumpAfterAggression_play',
 'msg_CantJumpWhileCloaked_play',
 'msg_MiningDronesDeactivatedCargoHoldFull_play',
 'msg_OnConnecting_play',
 'msg_DeniedTargetingCloaked_play',
 'msg_DockingAccepted_play',
 'msg_CantDockAfterAggression_play',
 'msg_DockingRequestDenied_play',
 'msg_DroneCommandRequiresActiveTarget_play',
 'msg_NotEnoughPower_play',
 'msg_NotEnoughPowerOutput_play',
 'msg_InvalidItemForSlot_play',
 'msg_NoCharges_play',
 'msg_NotEnoughCharges_play',
 'msg_NoMergingDifferentContrabands_play',
 'msg_NotEnoughEnergy_play',
 'msg_OnDockingRequest_play',
 'msg_ShpCantAssembleInsideShip_play',
 'msg_SkillTrained_play',
 'msg_SlotAlreadyOccupied_play',
 'msg_SpeedZero_play',
 'msg_TargetLost_play',
 'msg_TargetElectronicsScanStrengthsIncompatible_play',
 'msg_WarpDriveActive_play',
 'msg_AutoPilotWarpingToStation_play',
 'msg_WarpingWithAvailablePower_play',
 'msg_WarpingWithinGlobalDisruptors_play',
 'msg_WaypointAlreadySet_play',
 'msg_RankLost_play',
 'msg_RankGained_play',
 'msg_SecurityStatusAggressionChange_play',
 'msg_SecurityStatusAssistanceChange_play',
 'msg_SecurityStatusPodKillChange_play',
 'msg_SecurityStatusPoliceAggressionChange_play',
 'msg_SecurityStatusPoliceKillChange_play',
 'voc_general_aura15_play']
