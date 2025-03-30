#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveaudio\__init__.py
import evetypes
try:
    const
except NameError:
    import devenv.libconst as const

import logging
logger = logging.getLogger(__name__)
g_audioManager = None
SHIPS_DESTROYED_TO_CHANGE_MUSIC = 10
PILOTS_IN_SPACE_TO_CHANGE_MUSIC = 100
WORMHOLE_SYSTEM_ID_STARTS = 31000000
SENTINEL_SOLARSYSTEM_ID = 31000001
BARBICAN_SOLARSYSTEM_ID = 31000002
VIDETTE_SOLARSYSTEM_ID = 31000003
CONFLUX_SOLARSYSTEM_ID = 31000004
THERA_SOLARSYSTEM_ID = 31000005
REDOUBT_SOLARSYSTEM_ID = 31000006
HANGAR_STATE_GALLENTE = 'set_hangar_rtpc_gallente'
HANGAR_STATE_THERA = 'set_hangar_rtpc_thera'
SPECIAL_HANGAR_STATES_SWITCHES = {THERA_SOLARSYSTEM_ID: HANGAR_STATE_THERA}
MUSIC_STATE_NULLSEC_SPECIAL_SYSTEMS = [SENTINEL_SOLARSYSTEM_ID,
 BARBICAN_SOLARSYSTEM_ID,
 VIDETTE_SOLARSYSTEM_ID,
 CONFLUX_SOLARSYSTEM_ID,
 REDOUBT_SOLARSYSTEM_ID]
THERA_SYSTEM_ENTRY_EVENT = 'thera_system_entry_play'
SPECIAL_SYSTEM_ENTRY_EVENT = 'special_system_entry_play'
SPECIAL_SYSTEM_ENTRY_SOUND = {THERA_SOLARSYSTEM_ID: THERA_SYSTEM_ENTRY_EVENT,
 SENTINEL_SOLARSYSTEM_ID: SPECIAL_SYSTEM_ENTRY_EVENT,
 BARBICAN_SOLARSYSTEM_ID: SPECIAL_SYSTEM_ENTRY_EVENT,
 VIDETTE_SOLARSYSTEM_ID: SPECIAL_SYSTEM_ENTRY_EVENT,
 CONFLUX_SOLARSYSTEM_ID: SPECIAL_SYSTEM_ENTRY_EVENT,
 REDOUBT_SOLARSYSTEM_ID: SPECIAL_SYSTEM_ENTRY_EVENT}
MUSIC_LOCATION_SPACE = 'music_eve_dynamic'
MUSIC_LOCATION_LOGIN = 'music_login'
MUSIC_LOCATION_CHARACTER_CREATION = 'music_character_creation'
MUSIC_STATE_EMPIRE = 'music_switch_empire'
MUSIC_STATE_LOWSEC = 'music_switch_danger'
MUSIC_STATE_NULLSEC = 'music_switch_zero'
MUSIC_STATE_NULLSEC_DEATHS = 'music_switch_zero_danger'
MUSIC_STATE_NULLSEC_WORMHOLE = 'music_switch_zero_wormhole'
MUSIC_STATE_NULLSEC_SPECIAL = 'music_switch_zero_special'
MUSIC_LOCATION_DUNGEON = 'music_switch_dungeon'
MUSIC_STATE_ZARZAKH = 'music_switch_zarzakh'
MUSIC_STATE_RACE_AMARR = 'music_switch_race_amarr'
MUSIC_STATE_RACE_CALDARI = 'music_switch_race_caldari'
MUSIC_STATE_RACE_GALLENTE = 'music_switch_race_gallente'
MUSIC_STATE_RACE_MINMATAR = 'music_switch_race_minmatar'
MUSIC_STATE_RACE_NORACE = 'music_switch_race_norace'
MUSIC_STATE_FULL = 'music_switch_full'
MUSIC_STATE_AMBIENT = 'music_switch_ambient'
MUSIC_STATE_DUNGEON_LEVEL_1 = 'music_switch_dungeon_level_01'
MUSIC_STATE_DUNGEON_LEVEL_2 = 'music_switch_dungeon_level_02'
MUSIC_STATE_DUNGEON_LEVEL_3 = 'music_switch_dungeon_level_03'
MUSIC_STATE_DUNGEON_LEVEL_4 = 'music_switch_dungeon_level_04'
HANGAR_STATE_POPULATION_FEW = 'hangar_population_state_few'
HANGAR_STATE_POPULATION_SOME = 'hangar_population_state_some'
HANGAR_STATE_POPULATION_MANY = 'hangar_population_state_many'
MUSIC_SWITCH_HAVOC_INSURGENCY = 'music_switch_havoc_insurgency'
MUSIC_SWITCH_HAVOC_INSURGENCY_LEVEL_A = 'music_switch_havoc_insurgency_level_A'
MUSIC_SWITCH_HAVOC_INSURGENCY_LEVEL_B = 'music_switch_havoc_insurgency_level_B'
MUSIC_SWITCH_HAVOC_INSURGENCY_LEVEL_C = 'music_switch_havoc_insurgency_level_C'
MUSIC_SWITCH_HAVOC_INSURGENCY_LEVEL_D = 'music_switch_havoc_insurgency_level_D'
MUSIC_SWITCH_HAVOC_INSURGENCY_LEVEL_E = 'music_switch_havoc_insurgency_level_E'
MUSIC_SWITCH_HAVOC_INSURGENCY_LEVEL_F = 'music_switch_havoc_insurgency_level_F'
MUSIC_SWITCH_HAVOC_INSURGENCY_COMBAT_PLAY = 'music_havoc_insurgency_combat_play'
MUSIC_SWITCH_HAVOC_INSURGENCY_COMBAT_STOP = 'music_havoc_insurgency_combat_stop'
RACIALMUSICDICT = {const.raceCaldari: MUSIC_STATE_RACE_CALDARI,
 const.raceMinmatar: MUSIC_STATE_RACE_MINMATAR,
 const.raceAmarr: MUSIC_STATE_RACE_AMARR,
 const.raceGallente: MUSIC_STATE_RACE_GALLENTE,
 None: MUSIC_STATE_RACE_NORACE}
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
DEFAULT_MUSIC_SOUNDBANK = 'Music.bnk'
TUTORIAL_MUSIC_SOUNDBANK = 'Tutorial_Music.bnk'
MUSIC_ESSENTIAL = 'Music_essential.bnk'
MUSIC_SOUNDBANKS = [DEFAULT_MUSIC_SOUNDBANK, TUTORIAL_MUSIC_SOUNDBANK, MUSIC_ESSENTIAL]
EVE_COMMON_BANKS = [DEFAULT_MUSIC_SOUNDBANK,
 MUSIC_ESSENTIAL,
 'Interface.bnk',
 'Voice.bnk',
 'Planets.bnk',
 'ShipEffects.bnk',
 'ShipAnimations.bnk',
 'ShipAmbience.bnk',
 'Common.bnk',
 'Boosters.bnk']
EVE_HANGAR_BANKS = ['Hangar.bnk']
EVE_SPACE_BANKS = ['Atmos.bnk',
 'Deployables.bnk',
 'Dungeons.bnk',
 'Effects.bnk',
 'Modules.bnk',
 'ShipAnimations.bnk',
 'Stations.bnk',
 'Structures.bnk',
 'Turrets.bnk',
 'Wormholes.bnk']
ALL_SOUNDBANKS = EVE_COMMON_BANKS + EVE_HANGAR_BANKS + EVE_SPACE_BANKS + MUSIC_SOUNDBANKS

def GetPilotsInSystem():
    return sm.GetService('chat').get_player_count_in_local()


def GetHangarPopulationSwitch(pilotsInChannel):
    if pilotsInChannel < 20:
        return HANGAR_STATE_POPULATION_FEW
    if pilotsInChannel < 80:
        return HANGAR_STATE_POPULATION_SOME
    return HANGAR_STATE_POPULATION_MANY


def SetTheraSystemHangarSwitch(solarsystemid2, eventPlayer):
    event = SPECIAL_HANGAR_STATES_SWITCHES.get(solarsystemid2, HANGAR_STATE_GALLENTE)
    if eventPlayer:
        eventPlayer.SendEvent(event)


def PlaySystemSpecificEntrySound(lastSystemID, currentSystemID, eventPlayer):
    if not eventPlayer or lastSystemID == currentSystemID:
        return
    if currentSystemID in SPECIAL_SYSTEM_ENTRY_SOUND:
        event = SPECIAL_SYSTEM_ENTRY_SOUND[currentSystemID]
        eventPlayer.SendEvent(event)
