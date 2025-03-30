#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\menu\__init__.py
import inventorycommon.const as invConst
from menu.menuLabel import MenuLabel
from menu.menulist import MenuList
NO_ARGUMENTS = 'Noargs'
CONTAINERGROUPS = {invConst.groupWreck,
 invConst.groupCargoContainer,
 invConst.groupSpawnContainer,
 invConst.groupSpewContainer,
 invConst.groupSecureCargoContainer,
 invConst.groupAuditLogSecureContainer,
 invConst.groupFreightContainer,
 invConst.groupDeadspaceOverseersBelongings,
 invConst.groupMissionContainer}
MULTI_FUNCTIONS = {'UI/Inventory/ItemActions/Repackage',
 'UI/Contracts/BreakContract',
 'UI/Inventory/ItemActions/Reprocess',
 'UI/Drones/LaunchDrones',
 'UI/Drones/LaunchDrone',
 'UI/Inventory/ItemActions/TrashIt',
 'UI/Inventory/ItemActions/SplitStack',
 'UI/SkillQueue/AddSkillMenu/TrainNowToLevel1',
 'UI/SkillQueue/InjectSkill',
 'UI/Inventory/ItemActions/PlugInImplant',
 'UI/Inventory/ItemActions/AssembleContainer',
 'UI/Inventory/ItemActions/OpenContainer',
 'UI/Inventory/ItemActions/AssembleShip',
 'UI/Inventory/ItemActions/FitToActiveShip',
 'UI/Commands/OpenDroneBay',
 'UI/Commands/OpenFighterBay',
 'UI/Commands/OpenCargoHold',
 'UI/Inventory/ItemActions/LaunchForSelf',
 'UI/Inventory/ItemActions/LaunchForCorp',
 'UI/Inventory/ItemActions/Jettison',
 'take out trash',
 'UI/Drones/EngageTarget',
 'UI/Drones/MineWithDrone',
 'UI/Drones/ReturnDroneAndOrbit',
 'UI/Drones/ReturnDroneToBay',
 'UI/Drones/DelegateDroneControl',
 'UI/Drones/DroneAssist',
 'UI/Drones/DroneGuard',
 'UI/Drones/ReturnDroneControl',
 'UI/Drones/AbandonDrone',
 'UI/Drones/ScoopDroneToBay',
 'UI/Inventory/ItemActions/LockItem',
 'UI/Inventory/ItemActions/UnlockItem',
 'UI/Drones/MoveToDroneBay',
 'UI/Inventory/ItemActions/CreateContract',
 'UI/Corporations/Common/AwardCorpMemberDecoration',
 'UI/Corporations/Common/ConfirmExpelMembers',
 'UI/Corporations/CorporationWindow/Members/CorpMember',
 'UI/Corporations/CorporationWindow/Members/Myself',
 'UI/EVEMail/SendPilotEVEMail',
 'UI/PeopleAndPlaces/RemoveFromAddressbook',
 'UI/PeopleAndPlaces/AddToAddressbook',
 'UI/Fleet/FormFleetWith',
 'UI/Commands/CapturePortrait',
 'UI/Inventory/ItemActions/LaunchShip',
 'UI/Inventory/ItemActions/LaunchShipFromBay',
 'UI/Inventory/ItemActions/GetRepairQuote',
 'UI/Inventory/ItemActions/DeliverTo',
 'UI/Commands/ActivateSkinLicense',
 'UI/Inventory/ItemActions/ConsumeBooster',
 'UI/Inventory/ItemActions/ConsumeSkinDesignComponentItem',
 'UI/Commands/Compress'}

def CaptionIsInMultiFunctions(caption):
    if isinstance(caption, MenuLabel):
        functionName = caption[0]
    else:
        functionName = caption
    return functionName in MULTI_FUNCTIONS
