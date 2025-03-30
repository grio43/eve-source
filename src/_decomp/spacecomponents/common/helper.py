#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\spacecomponents\common\helper.py
import componentConst
from spacecomponents.common.data import type_has_space_component
from spacecomponents.common.data import get_type_ids_with_space_component
from spacecomponents.common.data import get_space_component_for_type

def GetComponentTypeAttributes(typeID, componentClassName):
    return get_space_component_for_type(typeID, componentClassName)


def HasScoopComponent(typeID):
    return type_has_space_component(typeID, componentConst.SCOOP_CLASS)


def HasActivateComponent(typeID):
    return type_has_space_component(typeID, componentConst.ACTIVATE_CLASS)


def HasDeployComponent(typeID):
    return type_has_space_component(typeID, componentConst.DEPLOY_CLASS)


def HasDecayComponent(typeID):
    return type_has_space_component(typeID, componentConst.DECAY_CLASS)


def HasDogmaticComponent(typeID):
    return type_has_space_component(typeID, componentConst.DOGMATIC_CLASS)


def HasFittingComponent(typeID):
    return type_has_space_component(typeID, componentConst.FITTING_CLASS)


def HasCargoBayComponent(typeID):
    return type_has_space_component(typeID, componentConst.CARGO_BAY)


def HasUnderConstructionComponent(typeID):
    return type_has_space_component(typeID, componentConst.UNDER_CONSTRUCTION)


def HasReinforceComponent(typeID):
    return type_has_space_component(typeID, componentConst.REINFORCE_CLASS)


def HasProximityLockComponent(typeID):
    return type_has_space_component(typeID, componentConst.PROXIMITY_LOCK_CLASS)


def HasProximitySensorComponent(typeID):
    return type_has_space_component(typeID, componentConst.PROXIMITY_SENSOR_CLASS)


def HasPhysicsComponent(typeID):
    return type_has_space_component(typeID, componentConst.PHYSICS_CLASS)


def HasSiphonComponent(typeID):
    return type_has_space_component(typeID, componentConst.SIPHON_CLASS)


def HasMicroJumpDriverComponent(typeID):
    return type_has_space_component(typeID, componentConst.MICRO_JUMP_DRIVER_CLASS)


def HasTurboShieldComponent(typeID):
    return type_has_space_component(typeID, componentConst.TURBO_SHIELD_CLASS)


def HasShipGroupComponent(typeID):
    return type_has_space_component(typeID, componentConst.SHIP_GROUP_CLASS)


def HasShipcasterComponent(typeID):
    return type_has_space_component(typeID, componentConst.SHIPCASTER_LAUNCHER)


def HasAutoMoonMinerComponent(typeID):
    return type_has_space_component(typeID, componentConst.AUTO_MOON_MINER)


def HasPresenceTrackerComponent(typeID):
    return type_has_space_component(typeID, componentConst.PILOT_PRESENCE_TRACKER)


def IsActiveComponent(componentRegistry, typeID, itemID):
    if HasActivateComponent(typeID):
        activateComponent = componentRegistry.GetComponentForItem(itemID, componentConst.ACTIVATE_CLASS)
        return activateComponent.IsActive()
    return True


def is_character_authorized_to_skyhook_reagent_silo_component(component_registry, type_id, item_id, character_session):
    if not HasSkyhookReagentSiloComponent(type_id):
        return True
    silo_component = component_registry.GetComponentForItem(item_id, componentConst.SKYHOOK_REAGENT_SILO)
    skyhook_id = silo_component.get_parent_skyhook_id()
    if not instance_has_orbital_skyhook_component(component_registry, skyhook_id):
        return True
    skyhook_component = component_registry.GetComponentForItem(skyhook_id, componentConst.ORBITAL_SKYHOOK)
    return skyhook_component.IsCharacterAuthorised(character_session)


def is_theft_vulnerable_skyhook_reagent_silo_component(component_registry, type_id, item_id):
    if not HasSkyhookReagentSiloComponent(type_id):
        return True
    silo_component = component_registry.GetComponentForItem(item_id, componentConst.SKYHOOK_REAGENT_SILO)
    skyhook_id = silo_component.get_parent_skyhook_id()
    if not instance_has_orbital_skyhook_component(component_registry, skyhook_id):
        return True
    skyhook_component = component_registry.GetComponentForItem(skyhook_id, componentConst.ORBITAL_SKYHOOK)
    return skyhook_component.is_vulnerable_to_theft()


def IsReinforcedComponent(componentRegistry, typeID, itemID):
    if HasReinforceComponent(typeID):
        reinforceComponent = componentRegistry.GetComponentForItem(itemID, componentConst.REINFORCE_CLASS)
        return reinforceComponent.IsReinforced()
    return False


def HasWarpDisruptionComponent(typeID):
    return type_has_space_component(typeID, componentConst.WARP_DISRUPTION_CLASS)


def HasBehaviorComponent(typeID):
    return type_has_space_component(typeID, componentConst.BEHAVIOR)


def HasNpcPilotComponent(typeID):
    return type_has_space_component(typeID, componentConst.NPC_PILOT)


def HasTargetingComponent(typeID):
    return type_has_space_component(typeID, componentConst.TARGETING)


def GetTypesWithBehaviorComponent():
    return get_type_ids_with_space_component(componentConst.BEHAVIOR)


def GetReinforcedComponent(componentRegistry, typeID, itemID):
    if HasReinforceComponent(typeID):
        return componentRegistry.GetComponentForItem(itemID, componentConst.REINFORCE_CLASS)
    elif HasTurboShieldComponent(typeID):
        return componentRegistry.GetComponentForItem(itemID, componentConst.TURBO_SHIELD_CLASS)
    elif HasFighterSquadronComponent(typeID):
        return componentRegistry.GetComponentForItem(itemID, componentConst.FIGHTER_SQUADRON_CLASS)
    else:
        return None


def HasEntosisCommandNodeComponent(typeID):
    return type_has_space_component(typeID, componentConst.ENTOSIS_COMMAND_NODE)


def HasEntosisLootTargetComponent(typeID):
    return type_has_space_component(typeID, componentConst.ENTOSIS_LOOT_TARGET)


def HasEntosisSovereigntyStructureComponent(typeID):
    return type_has_space_component(typeID, componentConst.ENTOSIS_SOVEREIGNTY_STRUCTURE)


def GetEntosisTargetComponentClasses(typeID):
    componentClasses = []
    if HasEntosisCommandNodeComponent(typeID):
        componentClasses.append(componentConst.ENTOSIS_COMMAND_NODE)
    if HasEntosisLootTargetComponent(typeID):
        componentClasses.append(componentConst.ENTOSIS_LOOT_TARGET)
    if HasEntosisSovereigntyStructureComponent(typeID):
        componentClasses.append(componentConst.ENTOSIS_SOVEREIGNTY_STRUCTURE)
    return componentClasses


def HasNpcWarpBeacon(typeID):
    return type_has_space_component(typeID, componentConst.NPC_WARP_BEACON)


def HasItemTrader(typeID):
    return type_has_space_component(typeID, componentConst.ITEM_TRADER)


def HasJumpPolarizationComponent(typeID):
    return type_has_space_component(typeID, componentConst.JUMP_POLARIZATION_CLASS)


def HasProximityUnlockComponent(typeID):
    return type_has_space_component(typeID, componentConst.PROXIMITY_LOCK_CLASS)


def HasFighterSquadronComponent(typeID):
    return type_has_space_component(typeID, componentConst.FIGHTER_SQUADRON_CLASS)


def HasEntityStandingsComponent(typeID):
    return type_has_space_component(typeID, componentConst.ENTITY_STANDINGS_CLASS)


def HasDynamicEntityNameComponent(typeID):
    return type_has_space_component(typeID, componentConst.DYNAMIC_ENTITY_NAME_CLASS)


def HasEntityBountyComponent(typeID):
    return type_has_space_component(typeID, componentConst.ENTITY_BOUNTY_CLASS)


def HasFilamentSpoolupComponent(typeID):
    return type_has_space_component(typeID, componentConst.FILAMENT_SPOOLUP)


def GetEntityBountyTypeAttributes(typeID):
    return GetComponentTypeAttributes(typeID, componentConst.ENTITY_BOUNTY_CLASS)


def GetDeploymentComponentTypeAttributes(typeID):
    if HasDeployComponent(typeID):
        return GetComponentTypeAttributes(typeID, componentConst.DEPLOY_CLASS)


def HasIgnoreFittingRestrictionsComponent(typeID):
    return type_has_space_component(typeID, componentConst.IGNORE_FITTING_RESTRICTIONS_CLASS)


def HasAdditionalLootComponent(typeID):
    return type_has_space_component(typeID, componentConst.ADDITIONAL_LOOT)


def InstanceHasDogmaComponent(componentRegistry, itemId):
    return InstanceHasComponent(componentRegistry, itemId, componentConst.DOGMATIC_CLASS)


def HasEnforceCriminalFlagComponent(typeID):
    return type_has_space_component(typeID, componentConst.ENFORCE_CRIMINAL_FLAG_CLASS)


def HasStoreSlimItemFieldInItemSettingsComponent(typeID):
    return type_has_space_component(typeID, componentConst.STORE_SLIM_ITEM_FIELD_IN_ITEM_SETTINGS)


def HasAlignmentBasedTollSpaceComponent(typeID):
    return type_has_space_component(typeID, componentConst.ALIGNMENT_BASED_TOLL)


def GetAlignmentBasedTollSpaceComponent(componentRegistry, itemID):
    return componentRegistry.GetComponentForItem(itemID, componentConst.ALIGNMENT_BASED_TOLL)


def HasStandingsRestrictionSpaceComponent(typeID):
    return type_has_space_component(typeID, componentConst.STANDINGS_RESTRICTIONS)


def GetStandingsRestrictionSpaceComponent(componentRegistry, itemID):
    return componentRegistry.GetComponentForItem(itemID, componentConst.STANDINGS_RESTRICTIONS)


def GetFilamentSpoolupSpaceComponent(componentRegistry, itemID):
    return componentRegistry.GetComponentForItem(itemID, componentConst.FILAMENT_SPOOLUP)


def GetActivateSpaceComponent(componentRegistry, itemID):
    return componentRegistry.GetComponentForItem(itemID, componentConst.ACTIVATE_CLASS)


def InstanceHasBehaviorComponent(componentRegistry, itemId):
    return InstanceHasComponent(componentRegistry, itemId, componentConst.BEHAVIOR)


def InstanceHasEntityStandingComponent(componentRegistry, itemId):
    return InstanceHasComponent(componentRegistry, itemId, componentConst.ENTITY_STANDINGS_CLASS)


def InstanceHasRoomCaptureComponent(componentRegistry, itemId):
    return InstanceHasComponent(componentRegistry, itemId, componentConst.ROOM_CAPTURE_PROXIMITY_TRIGGER)


def instance_has_orbital_skyhook_component(componentRegistry, itemId):
    return InstanceHasComponent(componentRegistry, itemId, componentConst.ORBITAL_SKYHOOK)


def InstanceHasComponent(componentRegistry, itemId, component):
    try:
        componentRegistry.GetComponentForItem(itemId, component)
        return True
    except KeyError:
        return False


def GetEntityStandingsAttributes(typeID):
    return GetComponentTypeAttributes(typeID, componentConst.ENTITY_STANDINGS_CLASS)


def HasDestinyServerBallClassComponent(typeID):
    return type_has_space_component(typeID, componentConst.DESTINY_SERVER_BALL_CLASS)


def GetDestinyServerBallClassAttributes(typeID):
    return GetComponentTypeAttributes(typeID, componentConst.DESTINY_SERVER_BALL_CLASS)


def HasEssRegistrationComponent(typeID):
    return type_has_space_component(typeID, componentConst.ESS_REGISTRATION_CLASS)


def HasEssLinkComponent(typeID):
    return type_has_space_component(typeID, componentConst.ESS_LINK_CLASS)


def HasLinkWithShipComponent(typeID):
    return type_has_space_component(typeID, componentConst.LINK_WITH_SHIP)


def HasHostileBaiterComponent(typeID):
    return type_has_space_component(typeID, componentConst.HOSTILE_BAITER)


def HasBoomboxComponent(typeID):
    return type_has_space_component(typeID, componentConst.BOOMBOX)


def HasTowGameObjectiveComponent(typeID):
    return type_has_space_component(typeID, componentConst.TOW_GAME_OBJECTIVE)


def HasSkyhookReagentSiloComponent(typeID):
    return type_has_space_component(typeID, componentConst.SKYHOOK_REAGENT_SILO)


def HasMercenaryDenComponent(typeID):
    return type_has_space_component(typeID, componentConst.MERCENARY_DEN)


def GetItemTraderComponent(typeID):
    if HasItemTrader(typeID):
        return GetComponentTypeAttributes(typeID, componentConst.ITEM_TRADER)
