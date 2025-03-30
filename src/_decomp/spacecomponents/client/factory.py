#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\spacecomponents\client\factory.py
import dynamicresources.client
from billboards.spacecomponents.client import billboard
from entosis.spacecomponents.client.entosisCommandNode import EntosisCommandNode
from entosis.spacecomponents.client.entosisSovereigntyStructure import EntosisSovereigntyStructure
from fighters.client.fighterSquadronComponent import FighterSquadronComponent
from spacecomponents.client.components.alignmentBasedToll import AlignmentBasedToll
from spacecomponents.client.components.autoMoonMiner import AutoMoonMiner
from spacecomponents.client.components.boombox import Boombox
from spacecomponents.client.components.builtLandingPad import BuiltLandingPad
from spacecomponents.client.components.filamentSpoolup import FilamentSpoolup
from spacecomponents.client.components.fwCapturePoint import FWCapturePoint
from spacecomponents.client.components.fwScoreboard import FWScoreboard
from spacecomponents.client.components.hackingSecurityState import HackingSecurityState
from spacecomponents.client.components.hostileBaiter import HostileBaiter
from spacecomponents.client.components.linkWithShip import LinkWithShip
from spacecomponents.client.components.mercenaryDen import MercenaryDen
from spacecomponents.client.components.orbitalSkyhook import OrbitalSkyhook
from spacecomponents.client.components.skyhookReagentSilo import SkyhookReagentSilo
from spacecomponents.client.components.shipcasterLauncher import ShipcasterLauncher
from spacecomponents.client.components.sovHub import SovHub
from spacecomponents.client.components.towGameOperator import TowGameOperator
from spacecomponents.client.components.towGameObjective import TowGameObjective
from spacecomponents.client.components.underConstruction import UnderConstruction
from spacecomponents.common import componentConst
from spacecomponents.client.components import dogmatic
from spacecomponents.client.components import scoop
from spacecomponents.client.components import cameraLimitation
from spacecomponents.client.components import cargobay
from spacecomponents.client.components import decay
from spacecomponents.client.components import activate
from spacecomponents.client.components import deploy
from spacecomponents.client.components import fitting
from spacecomponents.client.components import cynoInhibitor
from spacecomponents.client.components import cynoBeaconGenerator
from spacecomponents.client.components import reinforce
from spacecomponents.client.components import autoTractorBeam
from spacecomponents.client.components import autoLooter
from spacecomponents.client.components import siphon
from spacecomponents.common.components import bookmark
from spacecomponents.client.components import scanblocker
from spacecomponents.client.components import microJumpDriver
from spacecomponents.client.components import warpDisruption
from spacecomponents.client.components import behavior
from spacecomponents.client.components import turboshield
from spacecomponents.client.components import itemTraderNew
from spacecomponents.client.components import jumpPolarization
from spacecomponents.client.components import skybox
from spacecomponents.client.components import proximityLock
from spacecomponents.client.components import visualProximityEffect
from spacecomponents.client.components import proximityTrap
from spacecomponents.client.components import decloakEmitter
from spacecomponents.client.components import stellarHarvester
from spacecomponents.client.components import genericMultiEffect
from spacecomponents.common.components.component import Component
COMPONENTS = {componentConst.DEPLOY_CLASS: deploy.Deploy,
 componentConst.ACTIVATE_CLASS: activate.Activate,
 componentConst.DOGMATIC_CLASS: dogmatic.Dogmatic,
 componentConst.SCOOP_CLASS: scoop.Scoop,
 componentConst.DECAY_CLASS: decay.Decay,
 componentConst.FITTING_CLASS: fitting.Fitting,
 componentConst.CARGO_BAY: cargobay.CargoBay,
 componentConst.CYNO_INHIBITOR_CLASS: cynoInhibitor.CynoInhibitor,
 componentConst.CYNO_BEACON_GENERATOR_CLASS: cynoBeaconGenerator.CynoBeaconGenerator,
 componentConst.REINFORCE_CLASS: reinforce.Reinforce,
 componentConst.AUTO_TRACTOR_BEAM_CLASS: autoTractorBeam.AutoTractorBeam,
 componentConst.AUTO_LOOTER_CLASS: autoLooter.AutoLooter,
 componentConst.BOOKMARK_CLASS: bookmark.Bookmark,
 componentConst.SIPHON_CLASS: siphon.Siphon,
 componentConst.SCAN_BLOCKER_CLASS: scanblocker.ScanBlocker,
 componentConst.MICRO_JUMP_DRIVER_CLASS: microJumpDriver.MicroJumpDriver,
 componentConst.WARP_DISRUPTION_CLASS: warpDisruption.WarpDisruption,
 componentConst.BEHAVIOR: behavior.Behavior,
 componentConst.TURBO_SHIELD_CLASS: turboshield.TurboShield,
 componentConst.ENTOSIS_COMMAND_NODE: EntosisCommandNode,
 componentConst.ENTOSIS_SOVEREIGNTY_STRUCTURE: EntosisSovereigntyStructure,
 componentConst.ITEM_TRADER: itemTraderNew.ItemTrader,
 componentConst.JUMP_POLARIZATION_CLASS: jumpPolarization.JumpPolarization,
 componentConst.BILLBOARD_CLASS: billboard.BillboardComponent,
 componentConst.FIGHTER_SQUADRON_CLASS: FighterSquadronComponent,
 componentConst.ENTITY_STANDINGS_CLASS: Component,
 componentConst.SKYBOX_CLASS: skybox.Skybox,
 componentConst.PROXIMITY_LOCK_CLASS: proximityLock.ProximityLock,
 componentConst.CAMERA_LIMITATION_CLASS: cameraLimitation.CameraLimitation,
 componentConst.VISUAL_PROXIMITY_EFFECT: visualProximityEffect.VisualProximityEffect,
 componentConst.PROXIMITY_TRAP: proximityTrap.ProximityTrap,
 componentConst.DECLOAK_EMITTER: decloakEmitter.DecloakEmitter,
 componentConst.ESS_BRACKET: dynamicresources.client.EssBracket,
 componentConst.LINK_WITH_SHIP: LinkWithShip,
 componentConst.HOSTILE_BAITER: HostileBaiter,
 componentConst.STELLAR_HARVESTER: stellarHarvester.StellarHarvesterEffect,
 componentConst.FW_CAPTURE_POINT: FWCapturePoint,
 componentConst.FW_SCOREBOARD: FWScoreboard,
 componentConst.BOOMBOX: Boombox,
 componentConst.UNDER_CONSTRUCTION: UnderConstruction,
 componentConst.BUILT_LANDING_PAD: BuiltLandingPad,
 componentConst.SHIPCASTER_LAUNCHER: ShipcasterLauncher,
 componentConst.GENERICMULTIEFFECT: genericMultiEffect.GenericMultiEffect,
 componentConst.ALIGNMENT_BASED_TOLL: AlignmentBasedToll,
 componentConst.TOW_GAME_OBJECTIVE: TowGameObjective,
 componentConst.TOW_GAME_OPERATOR: TowGameOperator,
 componentConst.ORBITAL_SKYHOOK: OrbitalSkyhook,
 componentConst.AUTO_MOON_MINER: AutoMoonMiner,
 componentConst.SOV_HUB: SovHub,
 componentConst.SKYHOOK_REAGENT_SILO: SkyhookReagentSilo,
 componentConst.MERCENARY_DEN: MercenaryDen,
 componentConst.HACKING_SECURITY_STATE: HackingSecurityState,
 componentConst.FILAMENT_SPOOLUP: FilamentSpoolup}

def GetComponentClass(componentName):
    return COMPONENTS[componentName]
