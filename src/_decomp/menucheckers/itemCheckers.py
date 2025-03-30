#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\menucheckers\itemCheckers.py
import crates
import evetypes
import inventorycommon.const as invConst
import inventorycommon.util as invUtil
import industry.const as industryConst
import repackaging
import repair
import dogma.const as dogmaConst
from caching import Memoize
from dynamicitemattributes import IsMutator
from eve.common.lib import appConst
from eve.common.script.sys import idCheckers
from evetypes import IsCategoryHardwareByCategory
from globalConfig.getFunctions import IsContentComplianceControlSystemActive
from inventoryrestrictions import is_trashable, is_contractable
from itemcompression import is_compression_enabled, is_compressible_type, STRUCTURE_COMPRESSIBLE_TYPE_LIST_ID
from menucheckers.baseCheckers import _BaseItemChecker
from menucheckers import decorated_checker
from spacecomponents.common.helper import HasCargoBayComponent, HasDeployComponent, GetDeploymentComponentTypeAttributes
from typematerials.data import get_reprocessing_options, is_decompressible_gas_type

@Memoize
def _GetTypesWithRestrictedRenaming():
    return evetypes.GetTypeIDsByListID(evetypes.TYPE_LIST_RESTRICTED_RENAMING)


@decorated_checker

class ItemChecker(_BaseItemChecker):

    def OfferActivateAbyssalKey(self):
        return self.item.groupID == invConst.groupAbyssalKeys and self.IsOwnedByMe() and self.IsInPilotLocation()

    def OfferRandomJumpKey(self):
        return self.item.groupID in (invConst.groupRandomJumpKeys, invConst.groupTriglavianJumpKeys) and self.IsOwnedByMe() and self.IsInPilotLocation()

    def OfferActivateVoidSpaceKey(self):
        return self.item.groupID == invConst.groupVoidSpaceKeys and self.IsOwnedByMe() and self.IsInPilotLocation()

    def OfferPVPFilamentKey(self):
        return self.item.groupID == invConst.groupPVPfilamentKeys and self.IsOwnedByMe() and self.IsInPilotLocation()

    def OfferWarpVector(self):
        return self.item.groupID == invConst.groupWarpVectorItems and self.IsOwnedByMe() and self.IsInPilotLocation()

    def OfferActivateCharacterReSculptToken(self):
        return self.IsReSculptToken()

    def OfferActivateMultiTraining(self):
        return self.IsMultiTrainingToken()

    def OfferActivateSkillExtractor(self):
        return self.IsSkillExtractor()

    def OfferActivateSkillInjector(self):
        return self.IsSkillInjector()

    def OfferActivateShipSkinLicense(self):
        return self.IsShipSkin()

    def OfferConsumeShipSkinDesignComponent(self):
        return self.IsShipSkinDesignComponent()

    def IsDecodable(self):
        if idCheckers.IsFakeItem(self.item.itemID):
            return False
        if self.item.ownerID not in (self.session.charid, self.session.corpid):
            return False
        if self.item.typeID not in evetypes.GetTypeIDsByListID(evetypes.const.TYPE_LIST_CORRUPTED_TRINARY_FRAGMENT):
            return False
        return True

    def OfferAddToMarketQuickBar(self):
        if not self.OfferViewTypesMarketDetails():
            return False
        if self.IsCapsule():
            return False
        if self.IsContractable():
            return True
        return False

    def OfferAssembleContainer(self):
        if not self.IsPlayerDeployedContainer():
            return False
        if self.item.groupID == invConst.groupSiphonPseudoSilo:
            return False
        if self.IsSingleton():
            return False
        if not self.session.IsPilotDocked():
            return False
        if not self.IsInPilotLocation():
            return False
        return True

    def OfferAssembleShip(self):
        if not self.IsShip():
            return False
        if self.IsSingleton():
            return False
        if self.session.IsPilotDocked():
            if not self.IsOwnedByMe():
                return False
            if not self.IsInPilotLocation():
                return False
            if not self.IsDirectlyInPersonalHangar():
                return False
            if self.sm.GetService('invCache').IsItemLocked(self.item.itemID):
                return False
            return True
        if self.session.IsPilotInShipInSpace():
            if self.IsInCargoHold() and self.IsOwnedByMe():
                return True
            if self.IsInCorpHangarArray():
                locationItem = self.GetInSpaceLocationItem()
                if locationItem and locationItem.groupID in (const.groupCorporateHangarArray, const.groupAssemblyArray, const.groupPersonalHangar):
                    return True
        return False

    def OfferAssembleAndBoardShip(self):
        if not self.IsShip():
            return False
        if self.IsSingleton():
            return False
        if not self.IsOwnedByMe():
            return False
        if not self.session.IsPilotDocked():
            return False
        if not self.IsDirectlyInPersonalHangar():
            return False
        if not self.IsInPilotLocation():
            return False
        if self.session.IsPilotControllingStructure():
            return False
        if self.sm.GetService('invCache').IsItemLocked(self.item.itemID):
            return False
        return True

    def OfferBoardShip_FromSMA(self):
        if not self.session.IsPilotInShipInSpace():
            return False
        if not self.IsShip():
            return False
        if not self.IsInShipMA():
            return False
        return True

    def OfferBoardShipFromBay(self):
        if not self.session.IsPilotInShipInSpace():
            return False
        if not self.IsShip():
            return False
        if not self.IsInShipMAShipHangar():
            return False
        if self.IsInActiveShip():
            return False
        return True

    def OfferBreakContract(self):
        if not self.IsPlasticWrap():
            return False
        if not self.IsSingleton():
            return False
        if not self.IsInPilotLocation():
            return False
        if not self.IsPlayerDeployedContainer():
            return False
        if self.IsInCorpDeliveries():
            return False
        if not self.session.IsPilotDocked():
            return False
        if not self.IsDirectlyInPersonalHangar():
            return False
        return True

    def OfferBuyThisType(self):
        return self.OfferViewTypesMarketDetails()

    def OfferChangeName(self):
        if not self.IsShip():
            return False
        if not self.IsSingleton():
            return False
        if not self.IsOwnedByMe():
            return False
        if not self.session.IsPilotDocked():
            return False
        if not self.IsInPilotLocation():
            return False
        return True

    def OfferCombineSkillInjector(self):
        return self.item.typeID == invConst.typeSmallSkillInjector

    def OfferCompareButton(self):
        if not self.IsComparible():
            return False
        return bool(self.GetAttributeDict())

    def OfferCompressInSpace(self):
        if not self.IsCompressibleType():
            return False
        if not is_compression_enabled(self.sm.GetService('machoNet')):
            return False
        if not self.session.IsPilotInShipInSpace():
            return False
        if not self.IsDirectlyInActiveShip():
            return False
        return True

    def OfferCompressInStructure(self):
        if not self.IsCompressibleType():
            return False
        if not is_compression_enabled(self.sm.GetService('machoNet')):
            return False
        if not self.session.IsPilotInStructure():
            return False
        if not self.IsInPilotLocation():
            return False
        if self.item.typeID not in evetypes.GetTypeIDsByListID(STRUCTURE_COMPRESSIBLE_TYPE_LIST_ID):
            return False
        if not (self.IsDirectlyInPersonalStructureHangar() or self.IsDirectlyInActiveShip() or self.IsInDockableCorpOfficeWithAccess()):
            return False
        return True

    def OfferConfigureOrbitalPoco(self):
        if not super(ItemChecker, self).OfferConfigureOrbital():
            return False
        if self.IsOrbitalSkyhook():
            return False
        if not self.IsDirectlyInSpace():
            return False
        return True

    def OfferConfigureOrbitalSkyhook(self):
        if not super(ItemChecker, self).OfferConfigureOrbital():
            return False
        if not self.IsOrbitalSkyhook():
            return False
        if not self.IsDirectlyInSpace():
            return False
        return True

    def OfferConfigureShipCloneFacility(self):
        if not self.IsShip():
            return False
        if not self.IsSingleton():
            return False
        if not self.IsActiveShip():
            return False
        if not self.IsDirectlyInPersonalHangar():
            return False
        if not self.session.IsPilotDocked():
            return False
        if not self.IsInPilotLocation():
            return False
        if not self.IsCloneCapableShip():
            return False
        if self.IsInAssetSafety():
            return False
        return True

    def OfferConsumeBooster(self):
        if not self.IsBooster():
            return False
        if not self.IsInPilotLocation():
            return False
        if self.GetBoosterSlot() in {b.boosterSlot for b in self.getBoosters().values()}:
            return False
        return True

    def OfferCraftDynamicItem(self):
        if not IsMutator(self.item.typeID):
            return False
        if not self.IsOwnedByMe():
            return False
        if not self.IsInPilotLocation():
            return False
        return True

    def OfferCreateContract(self):
        if not self.IsContractable():
            return False
        if self.IsActiveShip():
            return False
        if self.IsStation():
            return False
        if not self.IsOwnedByMeOrCorp():
            return False
        if self.IsPlexVaultItem():
            return False
        if self.IsDirectlyInPersonalHangar():
            return True
        if self.IsOwnedByMyCorp() and self.IsInCorpDeliveries():
            return True
        if self.IsInDockableCorpOfficeWithAccess():
            return True
        return False

    def OfferDeliverCourierPackage(self):
        return self.OfferBreakContract()

    def OfferDeliverTo(self):
        if not self.session.IsPilotInStructure():
            return False
        if not self.IsInPilotLocation():
            return False
        if self.IsActiveShip():
            return False
        if self.IsCapsule():
            return False
        if not self.IsOwnedByMeOrCorp():
            return False
        if self.IsOwnedByMyCorp() and self.IsInCorpDeliveries():
            return True
        if self.IsDirectlyInPersonalStructureHangar():
            return True
        if self.IsInDockableCorpOfficeWithAccess():
            return True
        return False

    def OfferDeliverToCorp(self):
        if self.IsInCorpDeliveries() and idCheckers.IsStation(self.item.locationID) and self.session.CanTakeFromDeliveries():
            return True
        if self.IsInDockableCorpOffice() and idCheckers.IsStation(self.GetLocationIDOfItemInCorpOffice()) and self.session.canTakeFromCorpDivision(self.GetLocationIDOfItemInCorpOffice(), self.item.flagID):
            return True
        return False

    def OfferFindContract(self):
        return self.IsPlayerDeployedContainer() and self.IsPlasticWrap()

    def OfferFindInContracts(self):
        if not self.IsPublished():
            return False
        if self.IsStation():
            return False
        if self.IsContractable():
            return True
        return False

    def OfferFindInPersonalAssets(self):
        if not self.IsPublished():
            return False
        if self.IsStation():
            return False
        return True

    def OfferFitToActiveShip(self):
        if self.IsBooster():
            return False
        if self.IsImplant():
            return False
        if not self.session.IsPilotDocked():
            return False
        if not self.IsInPilotLocation():
            return False
        if not self.IsHardware():
            return False
        if not self.session.shipid:
            return False
        return True

    def OfferInjectSkill(self):
        if not self.IsSkillBook():
            return False
        if not self.IsPublished():
            return False
        if not self.IsInPilotLocation():
            return False
        skills = self.getSkills()
        if self.item.typeID in skills and skills[self.item.typeID].trainedSkillLevel is not None:
            return False
        return True

    def OfferInsureItem(self, stationServices):
        if not self.IsSingleton():
            return False
        if not self.IsShip():
            return False
        if not self.session.IsPilotDocked():
            return False
        if not self.IsInPilotLocation():
            return False
        if not self.session.canInsure(stationServices):
            return False
        if not self.IsOwnedByMeOrCorp():
            return False
        if self.IsOwnedByMyCorp() and not self.session.IsAccountant():
            return False
        if not self.IsInsurable():
            return False
        if self.IsInAssetSafety():
            return False
        return True

    def OfferJettison(self):
        if self.session.IsPilotInShipInSpace():
            if self.IsPlasticWrap():
                return False
            if not self.IsJettisonable():
                return False
            return True
        if self.session.IsPilotControllingUndockableStructure():
            if not self.IsInStructureFuelBay():
                return False
            if not self.IsOwnedByMyCorp():
                return False
            if not (self.session.IsStationManager() or self.session.IsStarbaseCaretaker()):
                return False
            if self.IsFuel() or self.IsLiquidOzone():
                return True
        return False

    def OfferLaunchContainerFromContainerInSpace(self):
        if not self.IsSingleton():
            return False
        if not self.IsPlayerDeployedContainer():
            return False
        if not self.IsInCargoContainerInSpace():
            return False
        return True

    def OfferLaunchDrones(self):
        if not self.session.IsPilotInShipInSpace():
            return False
        if not self.IsDrone():
            return False
        if not self.IsInDroneBay():
            return False
        return True

    def OfferLaunchForCorp(self):
        if not self.session.IsPilotInShipInSpace():
            return False
        if not (self.IsInCargoHold() or self.IsInInfrastructureHangar() or self.IsInFleetHangar()):
            return False
        if self.IsStructure() and self.session.IsStationManager() and self.hasInFlightViewActive():
            return True
        if HasDeployComponent(self.item.typeID):
            if self.IsSovereigntyStructure():
                return True
            if self.IsComponentCorpDeployable():
                return True
        if not self.IsAnchorable():
            return False
        if not self.IsInActiveShip():
            return False
        return True

    def OfferLaunchForSelf(self):
        if not self.session.IsPilotInShipInSpace():
            return False
        if not (self.IsInCargoHold() or self.IsInInfrastructureHangar() or self.IsInFleetHangar()):
            return False
        if self.IsStructure() and self.session.IsStationManager() and self.hasInFlightViewActive():
            return False
        if HasDeployComponent(self.item.typeID):
            if self.IsSovereigntyStructure():
                return False
            if self.IsComponentCorpDeployable():
                return False
            return True
        if not self.IsAnchorable():
            return False
        if not self.IsInActiveShip():
            return False
        if self.IsStarbase():
            return False
        if self.IsOrbital():
            return False
        return True

    def OfferLaunchForSelf_Container(self):
        if not self.session.IsPilotInShipInSpace():
            return False
        if self.IsJettisonable():
            return False
        if not self.IsInActiveShip():
            return False
        return self.IsPlayerDeployedContainer() and not self.IsAnchorable()

    def OfferLaunchFromContainer(self):
        if self.OfferJettison():
            return False
        if self.OfferLaunchForSelf_Container():
            return False
        return self.OfferLaunchContainerFromContainerInSpace()

    def OfferLaunchShip(self):
        if not self.session.IsPilotInShipInSpace():
            return False
        if not self.IsShip():
            return False
        return self.IsInShipMA() or self.OfferLaunchShipFromSpaceContainer()

    def OfferLaunchShipFromBay(self):
        if not self.session.IsPilotInShipInSpace():
            return False
        if not self.IsShip():
            return False
        if not self.IsInShipMAShipHangar():
            return False
        return True

    def OfferLaunchShipFromSpaceContainer(self):
        if not self.session.IsPilotInShipInSpace():
            return False
        if not self.IsShip():
            return False
        if not (self.IsInCargoContainerInSpace() or self.IsInWreckInSpace()):
            return False
        if self.IsSingleton():
            return True
        if self.IsInWreckInSpace() or self.GetInSpaceLocationItem().typeID == invConst.typeHangarContainer:
            if not self.IsModularShip():
                return True
        return False

    def OfferLeaveShip(self):
        if not self.IsActiveShip():
            return False
        if self.IsCapsule():
            return False
        if not self.session.IsPilotDocked():
            return False
        if not self.IsDirectlyInPersonalHangar():
            return False
        if not self.IsInPilotLocation():
            return False
        return True

    def OfferLockItem(self):
        return self.item.flagID == invConst.flagUnlocked

    def OfferMakeShipActive(self):
        if not self.IsShip():
            return False
        if not self.IsSingleton():
            return False
        if self.IsActiveShip():
            return False
        if not self.IsOwnedByMe():
            return False
        if not self.session.IsPilotDocked():
            return False
        if not self.IsDirectlyInPersonalHangar():
            return False
        if not self.IsInPilotLocation():
            return False
        if self.session.IsPilotControllingStructure():
            return False
        return True

    def OfferMoveToDroneBay(self):
        if not self.IsDrone():
            return False
        if not self.session.IsPilotInShipInSpace():
            return False
        if self.IsInDroneBay():
            return False
        bp = self.GetBallpark()
        if bp is None:
            return False
        for slimItem in bp.slimItems.itervalues():
            if slimItem.groupID == invConst.groupShipMaintenanceArray or slimItem.categoryID == invConst.categoryShip and self.godma.GetType(slimItem.typeID).hasShipMaintenanceBay:
                otherBall = self.session.getBall(slimItem.itemID)
                if otherBall and otherBall.surfaceDist < appConst.maxConfigureDistance:
                    return True

        return False

    def OfferOpenCargoHold(self):
        if not self.IsShip():
            return False
        if not self.IsSingleton():
            return False
        if self.IsCapsule():
            return False
        if not self.IsDirectlyInPersonalHangar():
            return False
        if not self.IsInPilotLocation():
            return False
        if self.IsInAssetSafety():
            return False
        return True

    def OfferOpenContainer(self):
        if not self.IsSingleton():
            return False
        if not self.IsInPilotLocation():
            return False
        if not self.IsPlayerDeployedContainer():
            return False
        if self.IsInCorpDeliveries():
            return False
        return True

    def OfferOpenCrate(self):
        return self.IsCrate()

    def OfferOpenFleetHangar(self):
        return self.OfferOpenCargoHold() and self.IsFleetHangarShip()

    def OfferOpenShipMaintenanceBay(self):
        return self.OfferOpenCargoHold() and self.IsSMBShip()

    def OfferPlugInImplant(self):
        if not self.IsImplant():
            return False
        if not self.IsInPilotLocation():
            return False
        if self.GetImplantSlot() in self.getImplants():
            return False
        return True

    def OfferProposeBlueprintLockdownVote(self):
        if not self.session.IsPilotDocked():
            return False
        if not self.IsBlueprint():
            return False
        if self.IsReactionFormula():
            return False
        if not self.IsSingleton():
            return False
        if self.IsBlueprintCopy():
            return False
        if not self.IsOwnedByMyCorp():
            return False
        if not self.session.IsCorpDirector():
            return False
        if not self.IsInDockableCorpOffice():
            return False
        locationID = self.GetLocationIDOfItemInCorpOffice()
        if not locationID:
            return False
        if self.sm.GetService('lockedItems').IsItemLocked(self.item):
            return False
        return True

    def OfferProposeBlueprintUnlockVote(self):
        if not self.session.IsPilotDocked():
            return False
        if not self.IsBlueprint():
            return False
        if not self.IsSingleton():
            return False
        if not self.IsOwnedByMyCorp():
            return False
        if not self.session.IsCorpDirector():
            return False
        locationID = self.GetLocationIDOfItemInCorpOffice() if self.IsInDockableCorpOffice() else None
        if locationID is None and not (self.IsInPilotLocation() and self.IsInAssetSafety()):
            return False
        if not self.sm.GetService('lockedItems').IsItemLocked(self.item):
            return False
        corpvotes = self.sm.GetService('corpvotes')
        if corpvotes.IsBlueprintSubjectOfActiveVoteCase(self.item.itemID):
            return False
        if corpvotes.IsBlueprintSubjectOfPendingUnlockAction(self.item.itemID):
            return False
        return True

    def OfferRedeemCurrency(self):
        if self.IsPlexVaultItem():
            return False
        if not self.IsCurrency():
            return False
        if self.IsFakeItemRecord():
            return False
        try:
            if self.IsInAssetSafety():
                return False
            if self.IsInTradeSession():
                return False
        except UserError as e:
            if e.msg != 'FakeItemNotFound':
                return False

        return True

    def OfferRepackage(self):
        if not self.IsSingleton():
            return False
        if self.IsActiveShip():
            return False
        if not self.IsRepackable():
            return False
        if self.IsStation():
            return False
        if not self.IsOwnedByMeOrCorp():
            return False
        if self.IsPlasticWrap():
            return False
        if self.IsDirectlyInPersonalHangar() or self.IsInPersonalHangarArray():
            return True
        if self.IsInDockableCorpOfficeWithAccess() or self.IsInCorpHangarArray() and self.session.canTakeFromCorpDivision(self.item.locationID, self.item.flagID):
            return True
        return False

    def OfferRepairItems(self):
        if not self.IsOwnedByMe():
            return False
        if not self.IsRepairable():
            return False
        if not self.IsInPilotLocation():
            return False
        if self.session.IsPilotDocked() and self.IsDirectlyInPersonalHangar():
            if self.session.IsPilotInStation() and not self.session.CanRepairAtStation():
                return False
            return True
        return False

    def OfferReprocess(self, stationServices):
        if self.IsNewbieShip():
            return False
        if self.session.IsPilotDocked():
            if not self.session.canRefine(stationServices):
                return False
            if self.IsInCorpDeliveries():
                return False
            if self.IsActiveShip():
                return False
            if not self.IsInPilotLocation():
                return False
            if self.IsInAssetSafety():
                return False
            if self.IsRefinable() and self.IsMinable():
                return True
            if self.IsRecycleAble():
                return True
        else:
            locationItem = self.GetInSpaceLocationItem()
            if locationItem is not None and locationItem.groupID == invConst.groupReprocessingArray and self.IsRefinable() and self.IsMinable():
                return True
        return False

    def OfferDecompressGas(self):
        if not self.IsDecompressibleGas():
            return False
        if not is_compression_enabled(self.sm.GetService('machoNet')):
            return False
        if not self.session.IsPilotInStructure():
            return False
        if not self.IsInPilotLocation():
            return False
        if not (self.IsInDockableCorpOfficeWithAccess() or self.IsDirectlyInPersonalStructureHangar()):
            return False
        return True

    def OfferReverseRedeem(self):
        return self.IsReverseRedeemable()

    def OfferSellThisItem(self):
        if not self.OfferViewTypesMarketDetails():
            return False
        if self.IsActiveShip():
            return False
        if self.IsStation():
            return False
        if not self.IsOwnedByMeOrCorp():
            return False
        if self.IsPlexVaultItem():
            return True
        if self.IsSingleton():
            if not self.IsInPilotLocation():
                return False
            if not self.IsRepackable():
                return False
        if self.IsDirectlyInPersonalHangar():
            return True
        if self.IsInDockableCorpOfficeWithAccess():
            return True
        return False

    def OfferSetName(self):
        if not self.IsSingleton():
            return False
        if not self.IsInPilotLocation():
            return False
        if not self.IsPlayerDeployedContainer():
            return False
        if self.IsOrbital():
            return False
        if self.IsRenamingRestrictedForType():
            return False
        return True

    def OfferSetNewConfigPasswordForContainer(self):
        if not super(ItemChecker, self).OfferSetNewConfigPasswordForContainer():
            return False
        if not self.session.IsPilotDocked():
            return False
        return True

    def OfferSetNewPasswordForContainer(self):
        if not super(ItemChecker, self).OfferSetNewPasswordForContainer():
            return False
        if not self.IsSingleton():
            return False
        if not self.session.IsPilotDocked():
            return False
        return True

    def OfferSimulateShip(self):
        if not self.IsShip():
            return False
        if self.IsSingleton():
            return False
        return True

    def OfferSimulateShipFitting(self):
        if not self.IsShip():
            return False
        if not self.IsSingleton():
            return False
        if self.IsOwnedByMyCorp() and self.IsInDockableCorpOffice():
            return True
        if not self.IsOwnedByMe():
            return False
        return True

    def OfferSplitSkillInjector(self):
        return self.item.typeID == invConst.typeSkillInjector

    def OfferSplitStack(self):
        if not self.IsStacked():
            return False
        if self.IsInCorpDeliveries():
            return False
        if not self.IsOwnedByMyCorp():
            return False
        if not self.session.IsPilotDocked():
            return False
        if self.IsInDockableCorpOfficeWithAccess():
            return True
        return False

    def OfferStripFitting(self):
        if not self.IsShip():
            return False
        if not self.IsSingleton():
            return False
        if self.IsCapsule():
            return False
        if not self.session.IsPilotDocked():
            return False
        if not self.IsInPilotLocation():
            return False
        if not self.IsDirectlyInPersonalHangar():
            return False
        return True

    def OfferTrainNowToLevel1(self):
        if not self.IsSkillBook():
            return False
        if not self.IsPublished():
            return False
        if not self.IsInPilotLocation():
            return False
        if self.hasSkillQueueOpen():
            return False
        if self.item.typeID in self.getSkills():
            return False
        return True

    def OfferTransferAmmoToCargo(self):
        if not self.session.IsPilotInShipInSpace():
            return False
        if not self.IsDBLessAmmo():
            return False
        if not self.IsInStarbase():
            return False
        return True

    def OfferLoadCharges(self):
        if not self.session.IsPilotInShipInSpace():
            return False
        if not (self.IsInCargoHold() or self.IsInAmmoHold()):
            return False
        return idCheckers.IsCharge(self.item.categoryID)

    def OfferTrashIt(self):
        if self.IsActiveShip():
            return False
        if not self.IsTrashableType():
            return False
        if self.IsOwnedByMe():
            return self.IsDirectlyInPersonalHangar() or self.IsInDeliveries() or self.IsAssetSafetyWrap()
        if self.IsOwnedByMyCorp() and self.session.IsCorpDirector():
            if self.IsDirectlyInSpace() or self.IsInControlTower():
                return False
            if self.IsShip() and self.IsInStarbase():
                return False
            if self.sm.GetService('lockedItems').IsItemLocked(self.item):
                return False
            if self.IsAssetSafetyWrap():
                return True
            if self.IsInDockableCorpOfficeWithAccess():
                return True
        return False

    def OfferUndock(self):
        if not self.IsShip():
            return False
        if not self.IsActiveShip():
            return False
        if not (self.session.IsPilotInStation() or self.session.IsPilotInStructure()):
            return False
        if not self.IsInPilotLocation():
            return False
        return True

    def OfferUnlockItem(self):
        return self.item.flagID == invConst.flagLocked

    def OfferUseBlueprint(self):
        if self.OfferUseFormula():
            return False
        return self.IsBlueprint() or self.IsAncientRelic()

    def OfferUseFormula(self):
        return self.IsReactionFormula()

    def OfferViewContents(self):
        if not self.IsSingleton():
            return False
        if not self.IsContainer():
            return False
        if self.IsOwnedByMe():
            if self.IsCapsule():
                return False
            return self.IsDirectlyInPersonalHangar()
        if self.IsOwnedByMyCorp():
            return self.IsInDockableCorpOffice()
        return False

    def OfferViewLog(self):
        if not self.IsSingleton():
            return False
        return super(ItemChecker, self).OfferViewLog()

    def IsDirectlyInActiveShip(self):
        return self.item.locationID == self.session.shipid

    def IsDirectlyInPersonalHangar(self):
        return self.IsDirectlyInPersonalNPCStationHangar() or self.IsDirectlyInPersonalStructureHangar()

    def IsDirectlyInPersonalNPCStationHangar(self):
        return idCheckers.IsStation(self.item.locationID) and self.item.flagID == invConst.flagHangar

    def IsDirectlyInPersonalStructureHangar(self):
        return self.item.flagID == invConst.flagHangar and self.IsDirectlyInStructure()

    def IsDirectlyInSpace(self):
        return bool(appConst.minSolarSystem <= self.item.locationID <= appConst.maxSolarSystem)

    def IsDirectlyInStructure(self):
        if self.session.structureid and self.session.structureid == self.item.locationID:
            return True
        return self.sm.GetService('structureDirectory').GetStructureInfo(self.item.locationID) is not None

    def IsInActiveShip(self):
        return self.IsDirectlyInActiveShip() or self.GetInSpaceLocationItem() == self.session.shipid

    def IsInAmmoHold(self):
        return self.item.flagID == invConst.flagSpecializedAmmoHold

    def IsInAssetSafety(self):
        if self.item.typeID == invConst.typeAssetSafetyWrap:
            return True
        if idCheckers.IsStation(self.item.locationID) or idCheckers.IsSolarSystem(self.item.locationID):
            return False
        if self.item.locationID in (self.session.locationid, self.session.structureid, self.session.shipid):
            return False
        invCache = self.sm.GetService('invCache')
        locationItem = invCache.GetInventoryFromId(self.item.locationID).GetItem()
        while locationItem and locationItem.itemID not in (self.session.stationid, self.session.structureid) and locationItem.locationID > appConst.minStation:
            if locationItem.typeID == invConst.typeAssetSafetyWrap:
                return True
            locationItem = invCache.GetInventoryFromId(locationItem.locationID).GetItem()

        return False

    def IsInCargoContainerInSpace(self):
        inSpaceLocationItem = self.GetInSpaceLocationItem()
        return inSpaceLocationItem is not None and inSpaceLocationItem.groupID == invConst.groupCargoContainer

    def IsInCargoHold(self):
        return self.item.flagID == invConst.flagCargo

    def IsInControlTower(self):
        inSpaceLocationItem = self.GetInSpaceLocationItem()
        return inSpaceLocationItem is not None and inSpaceLocationItem.groupID == invConst.groupControlTower

    def IsInCorpDeliveries(self):
        return self.item.flagID == invConst.flagCorpDeliveries

    def IsInCorpHangarArray(self):
        if not idCheckers.IsPlayerItem(self.item.locationID):
            return False
        if not self.IsOwnedByMyCorp():
            return False
        if self.item.flagID not in invConst.flagCorpSAGs:
            return False
        if self.GetLocationIDOfItemInCorpOffice() is not None:
            return False
        locationItem = None
        if self.sm.GetService('invCache').IsInventoryPrimedAndListed(self.item.locationID):
            locationItem = self.sm.GetService('invCache').GetInventoryFromId(self.item.locationID).GetItem()
        elif self.session.IsPilotInShipInSpace():
            locationItem = self.GetInSpaceLocationItem()
        if locationItem is None:
            return False
        if locationItem.groupID not in (invConst.groupCorporateHangarArray, invConst.groupAssemblyArray):
            return False
        return True

    def IsInDeliveries(self):
        return self.item.flagID == invConst.flagDeliveries

    def IsInDockableCorpOffice(self):
        if self.item.ownerID != self.session.corpid:
            return False
        if invUtil.IsNPC(self.item.ownerID):
            return False
        return self.item.flagID in invConst.flagCorpSAGs and self.GetLocationIDOfItemInCorpOffice()

    def IsInDockableCorpOfficeWithAccess(self):
        return self.IsInDockableCorpOffice() and self.session.canTakeFromCorpDivision(self.GetLocationIDOfItemInCorpOffice(), self.item.flagID)

    def IsInDroneBay(self):
        return self.item.flagID == invConst.flagDroneBay

    def IsInFleetHangar(self):
        return self.item.flagID == invConst.flagFleetHangar

    def IsInInfrastructureHangar(self):
        return self.item.flagID == invConst.flagColonyResourcesHold

    def IsInLocalContainer(self):
        if idCheckers.IsPlayerItem(self.item.locationID) and self.sm.GetService('invCache').IsInventoryPrimedAndListed(self.item.locationID):
            locationItem = self.sm.GetService('invCache').GetInventoryFromId(self.item.locationID).GetItem()
            if locationItem.typeID == invConst.typeOffice:
                return False
            if invUtil.IsTypeContainer(locationItem.typeID) or locationItem.typeID == invConst.typeAssetSafetyWrap:
                return True
        return False

    def IsInLocalCorpOffice(self):
        office = self.sm.GetService('officeManager').GetCorpOfficeAtLocation()
        return office is not None and self.item.locationID == office.officeID

    def IsInPersonalHangarArray(self):
        if not idCheckers.IsPlayerItem(self.item.locationID):
            return False
        if not self.IsOwnedByMe():
            return False
        if self.item.flagID != invConst.flagHangar:
            return False
        locationItem = None
        if self.sm.GetService('invCache').IsInventoryPrimedAndListed(self.item.locationID):
            locationItem = self.sm.GetService('invCache').GetInventoryFromId(self.item.locationID).GetItem()
        elif self.session.IsPilotInShipInSpace():
            locationItem = self.GetInSpaceLocationItem()
        if locationItem is None:
            return False
        if locationItem.groupID != invConst.groupPersonalHangar:
            return False
        return True

    def IsInPilotLocation(self):
        if super(ItemChecker, self).IsInPilotLocation():
            return True
        if self.IsInPilotStation():
            return True
        if self.IsInLocalCorpOffice():
            return True
        if self.IsInLocalContainer():
            return True
        return False

    def IsInPilotStation(self):
        pilotStation = self.session.stationid
        if not pilotStation:
            return False
        if self.item.locationID == pilotStation:
            return True
        if getattr(self.item, 'stationID', None) == pilotStation:
            return True
        if self.IsInLocalCorpOffice():
            return True
        if self.IsInLocalContainer():
            return True
        return False

    def IsInShipMA(self):
        locationItem = self.GetInSpaceLocationItem()
        if locationItem is None:
            return False
        return locationItem.groupID in (invConst.groupShipMaintenanceArray, invConst.groupAssemblyArray)

    def IsInShipMAShipHangar(self):
        locationItem = self.GetInSpaceLocationItem()
        if locationItem is None:
            return False
        if locationItem.categoryID != invConst.categoryShip:
            return False
        if self.item.flagID != invConst.flagShipHangar:
            return False
        return bool(self.godma.GetType(locationItem.typeID).hasShipMaintenanceBay)

    def IsInStarbase(self):
        inSpaceLocationItem = self.GetInSpaceLocationItem()
        return inSpaceLocationItem is not None and inSpaceLocationItem.categoryID == invConst.categoryStarbase

    def IsInStructureFuelBay(self):
        return self.item.flagID == invConst.flagStructureFuel

    def IsInTradeSession(self):
        if self.item.typeID in (invConst.typeTrade, invConst.typeTradeSession, invConst.typeTrading):
            return True
        if idCheckers.IsStation(self.item.locationID) or idCheckers.IsSolarSystem(self.item.locationID):
            return False
        if self.item.locationID in (self.session.locationid, self.session.structureid, self.session.shipid):
            return False
        invCache = self.sm.GetService('invCache')
        locationItem = invCache.GetInventoryFromId(self.item.locationID).GetItem()
        while locationItem and locationItem.itemID not in (self.session.stationid, self.session.structureid) and locationItem.locationID > appConst.minStation:
            if locationItem.typeID == invConst.typeTradeSession:
                return True
            locationItem = invCache.GetInventoryFromId(locationItem.locationID).GetItem()

        return False

    def IsInWreckInSpace(self):
        inSpaceLocationItem = self.GetInSpaceLocationItem()
        return inSpaceLocationItem is not None and inSpaceLocationItem.groupID == invConst.groupWreck

    def IsAlphaSkillInjector(self):
        return self.item.typeID == invConst.typeAlphaTrainingInjector

    def IsAncientRelic(self):
        return self.item.categoryID == invConst.categoryAncientRelic

    def IsAssembledShip(self):
        return idCheckers.IsAssembledShip(self.item.categoryID, self.item.singleton)

    def IsAssetSafetyWrap(self):
        return self.item.typeID == invConst.typeAssetSafetyWrap

    def IsAurumToken(self):
        return self.item.groupID == invConst.groupGameTime

    def IsBlueprint(self):
        return self.item.categoryID == invConst.categoryBlueprint

    def IsBlueprintCopy(self):
        return self.IsBlueprint() and self.IsSingleton() and abs(self.item.quantity) == appConst.singletonBlueprintCopy

    def IsBooster(self):
        if self.item.groupID != invConst.groupBooster:
            return False
        return bool(self.GetBoosterSlot())

    def IsComponentCorpDeployable(self):
        deployAttributes = GetDeploymentComponentTypeAttributes(self.item.typeID)
        if not deployAttributes or not deployAttributes.launchForOwnCorp:
            return False
        return True

    def IsNewbieShip(self):
        return idCheckers.IsNewbieShip(self.item.groupID)

    def IsCompressibleType(self):
        return is_compressible_type(self.item.typeID)

    def IsContainer(self):
        return invUtil.IsTypeContainer(self.item.typeID)

    def IsContractable(self):
        return is_contractable(self.item.typeID)

    def IsCrate(self):
        return self.item.typeID in crates.CratesStaticData().get_crates_by_type().keys()

    def IsCurrency(self):
        return self.item.groupID == invConst.groupCurrency

    def IsDBLessAmmo(self):
        return isinstance(self.item.itemID, tuple)

    def IsFakeItemRecord(self):
        itemID = getattr(self.item, 'itemID', None)
        return not bool(itemID) or itemID >= invConst.minFakeItem

    def IsFuel(self):
        return self.item.groupID == invConst.groupFuelBlock

    def IsHardware(self):
        return IsCategoryHardwareByCategory(self.item.categoryID)

    def IsImplant(self):
        if self.item.categoryID != invConst.categoryImplant:
            return False
        return bool(self.GetImplantSlot())

    def IsInsurable(self):
        return sm.GetService('insurance').GetInsurancePrice(self.item.typeID) > 0

    def IsJettisonable(self):
        if not self.session.IsPilotInShipInSpace():
            return False
        if self.item.categoryID == invConst.categoryShip:
            return False
        if self.item.groupID in invConst.playerDeployedContainers:
            return False
        if HasCargoBayComponent(self.item.typeID):
            return False
        if self.item.flagID not in invConst.jettisonableFlags:
            return False
        locationItem = self.GetInSpaceLocationItem()
        return locationItem and not HasCargoBayComponent(locationItem.typeID)

    def IsLiquidOzone(self):
        return self.item.typeID == invConst.typeLiquidOzone

    def IsMinable(self):
        return self.item.categoryID == invConst.categoryAsteroid or self.item.groupID == invConst.groupHarvestableCloud

    def IsMultiTrainingToken(self):
        return self.item.typeID == invConst.typeMultiTrainingToken

    def IsNonDiminishingInjectionBooster(self):
        return self.godma.GetTypeAttribute(self.item.typeID, dogmaConst.attributeNonDiminishingSkillInjectorUses, 0)

    def IsPlasticWrap(self):
        return self.item.typeID == invConst.typePlasticWrap

    def IsPlayerDeployedContainer(self):
        return self.item.groupID in invConst.playerDeployedContainers

    def IsPlexVaultItem(self):
        return self.item.typeID == invConst.typePlex and getattr(self.item, 'isInPlexVault', False)

    def IsReactionFormula(self):
        return self.item.categoryID == invConst.categoryBlueprint and self.item.groupID in industryConst.REACTION_GROUPS

    def IsRecycleAble(self):
        return get_reprocessing_options(self.item.typeID).isRecyclable

    def IsRefinable(self):
        return get_reprocessing_options(self.item.typeID).isRefinable

    def IsDecompressibleGas(self):
        return is_decompressible_gas_type(self.item.typeID)

    def IsRenamingRestrictedForType(self):
        if not IsContentComplianceControlSystemActive(self.sm.GetService('machoNet')):
            return False
        return self.item.typeID in _GetTypesWithRestrictedRenaming()

    def IsRepackable(self):
        return repackaging.CanRepackageType(self.item.typeID)

    def IsRepairable(self):
        return repair.IsRepairable(self.item)

    def IsReSculptToken(self):
        return self.item.typeID == invConst.typeReSculptToken

    def IsReverseRedeemable(self):
        return self.item.groupID in invConst.reverseRedeemingLegalGroups

    def IsServiceItem(self):
        return self.item.groupID == invConst.groupServices

    def IsShipSkin(self):
        return self.item.categoryID == invConst.categoryShipSkin

    def IsShipSkinDesignComponent(self):
        return self.item.groupID == invConst.groupShipSkinDesignComponents

    def IsSkinForCurrentShip(self):
        if self.IsShipSkin():
            current_ship_type = self._get_current_ship_type()
            types_skin_applies_to = self._get_types_skin_applies_to(self.item.typeID)
            return current_ship_type in types_skin_applies_to
        return False

    def _get_types_skin_applies_to(self, skin_type_id):
        licenceType = sm.GetService('cosmeticsSvc').GetSkinByLicenseType(skin_type_id)
        if licenceType:
            return licenceType.types
        return []

    def _get_current_ship_type(self):
        if session.shipid:
            item = sm.GetService('invCache').GetInventoryFromId(session.shipid).GetItem()
            if item:
                return item.typeID

    def IsSkillBook(self):
        return self.item.categoryID == invConst.categorySkill

    def IsSkillExtractor(self):
        return self.item.typeID == invConst.typeSkillExtractor

    def IsSkillInjector(self):
        return self.item.groupID == invConst.groupSkillInjectors

    def IsStacked(self):
        return self.item.stacksize > 1

    def IsTrashableType(self):
        if not is_trashable(self.item.typeID):
            return False
        return not (self.IsAurumToken() or self.IsServiceItem() or self.IsCurrency() or self.IsTutorialItem())

    def IsTutorialItem(self):
        return self.item.typeID in invConst.inceptionPackageTypes

    def GetAttributeDict(self):
        return self.sm.GetService('info').GetAttributeDictForType(self.item.typeID)

    def GetBoosterSlot(self):
        return self.GetStateManager().GetType(self.item.typeID).boosterness

    def GetImplantSlot(self):
        return self.GetStateManager().GetType(self.item.typeID).implantness

    def GetInSpaceLocationItem(self):
        return self.sm.GetService('michelle').GetItem(self.item.locationID)

    def GetLocationIDOfItemInCorpOffice(self):
        for office in self.sm.GetService('officeManager').GetMyCorporationsOffices():
            if office.officeID == self.item.locationID:
                return office.stationID
