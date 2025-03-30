#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\environment\effects\Repository.py
from eve.client.script.environment.effects.accelerationGate import AccelerationGate
from eve.client.script.environment.effects.anchoring import AnchorDrop, AnchorLift
from eve.client.script.environment.effects.triglavianBeam import TriglavianBeam
from eve.client.script.environment.effects.CelestialBeam import CelestialBeam
from eve.client.script.environment.effects.cloaking import CloakNoAnim, Cloaking, CloakRegardless, Cloak, Uncloak
from eve.client.script.environment.effects.EMPWave import EMPWave
from eve.client.script.environment.effects.GenericEffect import ShipEffect, GenericEffect
from eve.client.script.environment.effects.Jump import JumpDriveIn, JumpDriveInBO, JumpDriveOut, JumpDriveOutBO, JumpIn, JumpOut, JumpOutWormhole, JumpOutAbyssal, JumpOutAbyssalBetween
from eve.client.script.environment.effects.Jump import GateActivity, WormholeActivity
from eve.client.script.environment.effects.JumpPortal import JumpPortal, JumpPortalBO
from eve.client.script.environment.effects.stretchEffect import LocatorStretchEffect, StretchEffect, TurretStretchEffect, LocatorStretchEffectSwitching, DamageLocatorToDamageLocatorStretchEffect, BoundsToCenterStretchEffect
from eve.client.script.environment.effects.MicroJumpDrive import MicroJumpDriveJump, MicroJumpDriveEngage
from eve.client.script.environment.effects.MultiEffect import MultiEffect
from eve.client.script.environment.effects.pointDefense import PointDefense
from eve.client.script.environment.effects.EffectController import SiegeMode, AttackMode, ControllerTrigger, MultiEffectControllerTrigger
from eve.client.script.environment.effects.TriageMode import TriageMode
from eve.client.script.environment.effects.skinChange import SkinChange
from eve.client.script.environment.effects.soundEffect import SoundEffect
from eve.client.script.environment.effects.shipRenderEffect import ShipRenderEffect, ShipRenderTargetedEffect
from eve.client.script.environment.effects.structures import StructureOnlined, StructureOnline, StructureOffline
from eve.client.script.environment.effects.superWeapon import SuperWeapon, SlashWeapon, DirectionalWeapon
from eve.client.script.environment.effects.turrets import StandardWeapon, CloudMining, MissileLaunch, ChainWeaponEffect
from eve.client.script.environment.effects.Warp import Warping
from eve.client.script.environment.effects.WarpDisruptFieldGenerating import WarpDisruptFieldGenerating
from eve.client.script.environment.effects.WarpFlash import WarpFlashOut, WarpFlashIn
from eve.client.script.environment.effects.impactEffect import ImpactEffect
from eve.client.script.environment.effects.postProcess import PostProcessEffect
from eve.client.script.environment.effects.SunHarvestingBeam import SunHarvestingBeam
from eve.client.script.environment.effects.StellarHarvester import StellarHarvester
from eve.client.script.environment.effects.shipEjector import ShipEjector, CapsuleFlare
from eve.client.script.environment.effects.modules import VisualModuleEffect
from eve.client.script.environment.effects.ProximityEffect import ProximityEffect
from eve.client.script.environment.effects.ChildEffect import ChildEffect
from eve.client.script.environment.effects.EveStretch3 import EveStretch3
from eve.client.script.environment.effects.CameraAttachmentEffect import CameraAttachmentEffect
from eve.client.script.environment.effects.GenericMultiEffect import GenericMultiEffect
from fsdBuiltData.client.effects import GetEffect, GetEffectType, GetEffectGraphicID, GetEffectGuids
from fsdBuiltData.common.graphicIDs import GetGraphicFile
typeToClass = {'AccelerationGate': AccelerationGate,
 'AnchorDrop': AnchorDrop,
 'AnchorLift': AnchorLift,
 'TriglavianBeam': TriglavianBeam,
 'CelestialBeam': CelestialBeam,
 'CloakNoAnim': CloakNoAnim,
 'Cloaking': Cloaking,
 'CloakRegardless': CloakRegardless,
 'Cloak': Cloak,
 'DirectionalWeapon': DirectionalWeapon,
 'Uncloak': Uncloak,
 'EMPWave': EMPWave,
 'ShipEffect': ShipEffect,
 'ShipRenderEffect': ShipRenderEffect,
 'ShipRenderTargetedEffect': ShipRenderTargetedEffect,
 'StretchEffect': StretchEffect,
 'LocatorStretchEffect': LocatorStretchEffect,
 'LocatorStretchEffectSwitching': LocatorStretchEffectSwitching,
 'TurretStretchEffect': TurretStretchEffect,
 'DamageLocatorToDamageLocatorStretchEffect': DamageLocatorToDamageLocatorStretchEffect,
 'BoundsToCenterStretchEffect': BoundsToCenterStretchEffect,
 'GenericEffect': GenericEffect,
 'ImpactEffect': ImpactEffect,
 'JumpDriveIn': JumpDriveIn,
 'JumpDriveInBO': JumpDriveInBO,
 'JumpDriveOut': JumpDriveOut,
 'JumpDriveOutBO': JumpDriveOutBO,
 'JumpIn': JumpIn,
 'JumpOut': JumpOut,
 'JumpOutWormhole': JumpOutWormhole,
 'JumpOutAbyssal': JumpOutAbyssal,
 'JumpOutAbyssalBetween': JumpOutAbyssalBetween,
 'GateActivity': GateActivity,
 'WormholeActivity': WormholeActivity,
 'JumpPortal': JumpPortal,
 'JumpPortalBO': JumpPortalBO,
 'MicroJumpDriveJump': MicroJumpDriveJump,
 'MicroJumpDriveEngage': MicroJumpDriveEngage,
 'MultiEffect': MultiEffect,
 'PointDefense': PointDefense,
 'SiegeMode': SiegeMode,
 'AttackMode': AttackMode,
 'TriageMode': TriageMode,
 'SkinChange': SkinChange,
 'SlashWeapon': SlashWeapon,
 'SoundEffect': SoundEffect,
 'StructureOnlined': StructureOnlined,
 'StructureOnline': StructureOnline,
 'StructureOffline': StructureOffline,
 'StandardWeapon': StandardWeapon,
 'SuperWeapon': SuperWeapon,
 'CloudMining': CloudMining,
 'MissileLaunch': MissileLaunch,
 'Warping': Warping,
 'WarpDisruptFieldGenerating': WarpDisruptFieldGenerating,
 'WarpFlashOut': WarpFlashOut,
 'WarpFlashIn': WarpFlashIn,
 'PostProcess': PostProcessEffect,
 'SunHarvestingBeam': SunHarvestingBeam,
 'ChainWeaponEffect': ChainWeaponEffect,
 'ShipEjector': ShipEjector,
 'ModuleEffect': VisualModuleEffect,
 'CapsuleFlare': CapsuleFlare,
 'ProximityEffect': ProximityEffect,
 'StellarHarvester': StellarHarvester,
 'ControllerTrigger': ControllerTrigger,
 'ChildEffect': ChildEffect,
 'EveStretch3': EveStretch3,
 'MultiEffectControllerTrigger': MultiEffectControllerTrigger,
 'CameraAttachmentEffect': CameraAttachmentEffect,
 'GenericMultiEffect': GenericMultiEffect}

def GetClassification(guid):
    guid = str(guid)
    effect = GetEffect(guid)
    if effect is None:
        return
    classType = typeToClass.get(GetEffectType(effect), None)
    graphicID = GetEffectGraphicID(effect)
    resPath = GetGraphicFile(graphicID)
    return (classType, effect, resPath)
