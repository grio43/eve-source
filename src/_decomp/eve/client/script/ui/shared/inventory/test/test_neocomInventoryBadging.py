#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\inventory\test\test_neocomInventoryBadging.py
from carbon.common.lib.const import ixItemID, ixOwnerID, ixLocationID, ixFlag
from eve.common.lib.appConst import locationAbstract, locationRAMInstalledItems, locationJunkyard
import inventorycommon.const as invconst
from mock import Mock, patch
from testhelpers.evemocks import SMMock
from testsuites.testcases import ClientTestCase
from unittest import main
SOLAR_SYSTEM_ID = 30005042L
STATION_ID = 60001327L
MY_SHIP_ID = 1000000123235L
ANOTHER_SHIP_ID = 1000000124167L
CHAR_ID_1 = 90000001
CHAR_ID_2 = 2112001018

class KeyValMock(object):

    def __init__(self, **kw):
        self.__dict__ = kw

    def get(self, key, defval = None):
        return self.__dict__.get(key, defval)


class ItemStorageMock(object):

    def __init__(self, unseen_item_ids):
        self.unseen_items = unseen_item_ids

    def get_unseen(self):
        return self.unseen_items


class ItemMock(object):
    __slots__ = ('itemID', 'typeID', 'ownerID', 'locationID', 'flagID', 'quantity', 'groupID', 'categoryID', 'customInfo', 'stacksize', 'singleton')

    def __init__(self, itemID, typeID, ownerID, locationID, flagID, quantity, groupID, categoryID, customInfo, stacksize, singleton):
        self.itemID = itemID
        self.typeID = typeID
        self.ownerID = ownerID
        self.locationID = locationID
        self.flagID = flagID
        self.quantity = quantity
        self.groupID = groupID
        self.categoryID = categoryID
        self.customInfo = customInfo
        self.stacksize = stacksize
        self.singleton = singleton


class InventoryBadgingTestCase(ClientTestCase):

    def setUp(self):
        super(InventoryBadgingTestCase, self).setUp()
        self._mock_globals()
        with patch.dict('sys.modules', self._mock_imported_modules()):
            from eve.client.script.ui.shared.inventory.neocomInventoryBadging import NeocomInventoryBadging
            self.badging = NeocomInventoryBadging(inventory_cache=Mock(), neocom=Mock())
            self.badging.is_inventory_window_open = Mock(return_value=False)

    def _mock_globals(self):
        import __builtin__
        session_mock = Mock()
        session_mock.shipid = MY_SHIP_ID
        __builtin__.session = session_mock
        __builtin__.settings = Mock()
        __builtin__.sm = SMMock()

    def _mock_imported_modules(self):
        imported_modules = {'blue': Mock(),
         'carbon.common.script.util.timerstuff': Mock(),
         'eve.client.script.environment.invCache': Mock(),
         'eve.client.script.ui.shared.inventory.invWindow': Mock(),
         'eve.client.script.ui.shared.neocom.neocom.btnData.btnDataNodeNotification': Mock(),
         'eve.client.script.ui.shared.neocom.neocom.fixedButtonExtension': Mock(),
         'eve.client.script.ui.shared.neocom.neocom.neocomConst': Mock(),
         'localization': Mock(),
         'log': Mock()}
        return imported_modules

    def _check_triggers_badging(self, change, item):
        self.assertTrue(self.badging.is_badging_triggered(change, item, is_local_change=True))

    def _check_does_not_trigger_badging(self, change, item):
        self.assertFalse(self.badging.is_badging_triggered(change, item, is_local_change=True))

    def test_no_badging_if_item_manually_moved_from_cargo_to_item_hangar(self):
        change = {ixLocationID: MY_SHIP_ID,
         ixFlag: invconst.flagCargo}
        item = ItemMock(itemID=1000000123391L, typeID=invconst.typeThrasherCombatCrate, ownerID=CHAR_ID_1, locationID=STATION_ID, flagID=invconst.flagHangar, quantity=1, groupID=invconst.groupSpecialEditionCommodities, categoryID=invconst.categorySpecialEditionAssets, customInfo='', stacksize=1, singleton=0)
        self._check_does_not_trigger_badging(change, item)

    def test_badging_if_item_redeemed(self):
        change = {ixLocationID: locationAbstract}
        item = ItemMock(itemID=1000000123399L, typeID=invconst.typeThrasherCombatCrate, ownerID=CHAR_ID_1, locationID=STATION_ID, flagID=invconst.flagHangar, quantity=1, groupID=invconst.groupSpecialEditionCommodities, categoryID=invconst.categorySpecialEditionAssets, customInfo=None, stacksize=1, singleton=0)
        self._check_triggers_badging(change, item)

    def test_badging_if_ship_redeemed(self):
        change = {ixLocationID: locationAbstract}
        item = ItemMock(itemID=1000000123400L, typeID=invconst.typeMerlin, ownerID=CHAR_ID_1, locationID=STATION_ID, flagID=invconst.flagHangar, quantity=1, groupID=invconst.groupFrigate, categoryID=invconst.categoryShip, customInfo=None, stacksize=1, singleton=0)
        self._check_triggers_badging(change, item)

    def test_badging_if_blueprint_copy_redeemed(self):
        change = {ixLocationID: locationAbstract}
        item = ItemMock(itemID=1000000140926L, typeID=invconst.typeGnosisBlueprint, ownerID=CHAR_ID_1, locationID=STATION_ID, flagID=invconst.flagHangar, quantity=-2, groupID=invconst.groupBattlecruiserBlueprint, categoryID=invconst.categoryBlueprint, customInfo=None, stacksize=1, singleton=2)
        self._check_triggers_badging(change, item)

    def test_badging_if_item_created_via_slash(self):
        change = {ixLocationID: locationAbstract}
        item = ItemMock(itemID=1000000123401L, typeID=invconst.typeThrasherCombatCrate, ownerID=CHAR_ID_1, locationID=STATION_ID, flagID=invconst.flagHangar, quantity=1, groupID=invconst.groupSpecialEditionCommodities, categoryID=invconst.categorySpecialEditionAssets, customInfo=None, stacksize=1, singleton=0)
        self._check_triggers_badging(change, item)

    def test_badging_when_crate_is_opened(self):
        change = {invconst.ixStackSize: 1}
        item = ItemMock(itemID=1000000123422L, typeID=invconst.typeA3DestroyerCrate, ownerID=CHAR_ID_1, locationID=STATION_ID, flagID=invconst.flagHangar, quantity=0, groupID=invconst.groupSpecialEditionCommodities, categoryID=invconst.categorySpecialEditionAssets, customInfo=None, stacksize=0, singleton=0)
        self._check_does_not_trigger_badging(change, item)
        change = {ixLocationID: locationAbstract}
        item = ItemMock(itemID=1000000123423L, typeID=invconst.typeSunesis, ownerID=CHAR_ID_1, locationID=STATION_ID, flagID=invconst.flagHangar, quantity=1, groupID=invconst.groupDestroyer, categoryID=invconst.categoryShip, customInfo=None, stacksize=1, singleton=0)
        self._check_triggers_badging(change, item)
        change = {ixLocationID: locationAbstract}
        item = ItemMock(itemID=1000000123424L, typeID=invconst.typeDamageControlI, ownerID=CHAR_ID_1, locationID=STATION_ID, flagID=invconst.flagHangar, quantity=1, groupID=invconst.groupDamageControl, categoryID=invconst.categoryModule, customInfo=None, stacksize=1, singleton=0)
        self._check_triggers_badging(change, item)
        change = {ixLocationID: locationAbstract}
        item = ItemMock(itemID=1000000123425L, typeID=invconst.typeTahronCustomHeatSink, ownerID=CHAR_ID_1, locationID=STATION_ID, flagID=invconst.flagHangar, quantity=1, groupID=invconst.groupHeatSink, categoryID=invconst.categoryModule, customInfo=None, stacksize=1, singleton=0)
        self._check_triggers_badging(change, item)

    def test_badging_if_item_bought_in_lp_store(self):
        change = {ixLocationID: locationAbstract}
        item = ItemMock(itemID=1000000123427L, typeID=invconst.typeLimitedMemoryAugmentation, ownerID=CHAR_ID_1, locationID=STATION_ID, flagID=invconst.flagHangar, quantity=1, groupID=invconst.groupCyberLearning, categoryID=invconst.categoryImplant, customInfo=None, stacksize=1, singleton=0)
        self._check_triggers_badging(change, item)

    def test_badging_if_item_bought_from_market(self):
        change = {ixLocationID: locationAbstract}
        item = ItemMock(itemID=1000000123428L, typeID=invconst.typeLimitedMemoryAugmentation, ownerID=CHAR_ID_1, locationID=STATION_ID, flagID=invconst.flagHangar, quantity=1, groupID=invconst.groupCyberLearning, categoryID=invconst.categoryImplant, customInfo=None, stacksize=1, singleton=0)
        self._check_triggers_badging(change, item)

    def test_badging_if_item_acquired_from_contract(self):
        item_id = 1000000123428L
        contract_item_id = 1000000123429L
        change = {ixOwnerID: invconst.ownerSystem,
         ixLocationID: contract_item_id,
         ixFlag: invconst.flagNone}
        item = ItemMock(itemID=item_id, typeID=invconst.typeLimitedMemoryAugmentation, ownerID=CHAR_ID_1, locationID=STATION_ID, flagID=invconst.flagHangar, quantity=1, groupID=invconst.groupCyberLearning, categoryID=invconst.categoryImplant, customInfo=None, stacksize=1, singleton=0)
        self._check_triggers_badging(change, item)

    def test_badging_if_item_acquired_from_trade(self):
        item_id = 1000000123431L
        trade_item_id = 1000000123430L
        previous_owner_id = CHAR_ID_2
        owner_id = CHAR_ID_1
        change = {ixOwnerID: previous_owner_id,
         ixLocationID: trade_item_id}
        item = ItemMock(itemID=item_id, typeID=invconst.typeLimitedMemoryAugmentation, ownerID=owner_id, locationID=STATION_ID, flagID=invconst.flagHangar, quantity=1, groupID=invconst.groupCyberLearning, categoryID=invconst.categoryImplant, customInfo=None, stacksize=1, singleton=0)
        self._check_triggers_badging(change, item)

    def test_badging_if_item_manufactured(self):
        blueprint_item_id = 1000000123432L
        item_id = 1000000123434L
        change = {ixLocationID: locationRAMInstalledItems}
        item = ItemMock(itemID=blueprint_item_id, typeID=invconst.type1MNCivilianAfterburnerBlueprint, ownerID=CHAR_ID_1, locationID=STATION_ID, flagID=invconst.flagHangar, quantity=-1, groupID=invconst.groupPropulsionModuleBlueprint, categoryID=invconst.categoryBlueprint, customInfo='', stacksize=1, singleton=1)
        self._check_does_not_trigger_badging(change, item)
        change = {ixLocationID: locationAbstract}
        item = ItemMock(itemID=item_id, typeID=invconst.type1MNCivilianAfterburner, ownerID=CHAR_ID_1, locationID=STATION_ID, flagID=invconst.flagHangar, quantity=-1, groupID=invconst.groupPropulsionModule, categoryID=invconst.categoryModule, customInfo=None, stacksize=1, singleton=0)
        self._check_triggers_badging(change, item)

    def test_badging_if_item_given_in_mission(self):
        change = {ixLocationID: locationAbstract}
        item = ItemMock(itemID=1000000123436L, typeID=invconst.typeCratesOfCoolant, ownerID=CHAR_ID_1, locationID=STATION_ID, flagID=invconst.flagHangar, quantity=3, groupID=invconst.groupMiscellaneous, categoryID=invconst.categoryCommodity, customInfo=None, stacksize=3, singleton=0)
        self._check_triggers_badging(change, item)

    def test_no_badging_if_ore_mined(self):
        change = {ixLocationID: locationAbstract}
        item = ItemMock(itemID=1000000123441L, typeID=invconst.typeVeldspar, ownerID=CHAR_ID_1, locationID=MY_SHIP_ID, flagID=invconst.flagCargo, quantity=72, groupID=invconst.groupVeldspar, categoryID=invconst.categoryAsteroid, customInfo=KeyValMock(isMined=True), stacksize=72, singleton=0)
        self._check_does_not_trigger_badging(change, item)

    def test_no_badging_if_ship_assembled(self):
        change = {invconst.ixSingleton: 0}
        item = ItemMock(itemID=1000000118245L, typeID=invconst.typeMerlin, ownerID=CHAR_ID_1, locationID=MY_SHIP_ID, flagID=invconst.flagHangar, quantity=-1, groupID=invconst.groupFrigate, categoryID=invconst.categoryShip, customInfo='', stacksize=1, singleton=1)
        self._check_does_not_trigger_badging(change, item)

    def test_no_badging_if_ship_repackaged(self):
        ship_item_id_before = 1000000118245L
        ship_item_id_after = 1000000123443L
        self.badging.get_tracked_item_storage = Mock(return_value=ItemStorageMock(unseen_item_ids=[]))
        change = {ixLocationID: STATION_ID}
        item = ItemMock(itemID=ship_item_id_before, typeID=invconst.typeMerlin, ownerID=CHAR_ID_1, locationID=locationJunkyard, flagID=invconst.flagHangar, quantity=-1, groupID=invconst.groupFrigate, categoryID=invconst.categoryShip, customInfo='', stacksize=1, singleton=1)
        self._check_does_not_trigger_badging(change, item)
        change = {ixItemID: ship_item_id_before,
         ixOwnerID: invconst.ownerSystem,
         ixLocationID: locationAbstract}
        item = ItemMock(itemID=ship_item_id_after, typeID=invconst.typeMerlin, ownerID=CHAR_ID_1, locationID=STATION_ID, flagID=invconst.flagHangar, quantity=1, groupID=invconst.groupFrigate, categoryID=invconst.categoryShip, customInfo='', stacksize=1, singleton=0)
        self._check_does_not_trigger_badging(change, item)

    def test_no_badging_if_stack_split(self):
        original_stack_item_id = 1000000123444L
        new_stack_item_id = 1000000123445L
        self.badging.get_tracked_item_storage = Mock(return_value=ItemStorageMock(unseen_item_ids=[]))
        change = {ixItemID: original_stack_item_id,
         ixLocationID: locationAbstract}
        item = ItemMock(itemID=new_stack_item_id, typeID=invconst.typeVeldspar, ownerID=CHAR_ID_1, locationID=STATION_ID, flagID=invconst.flagHangar, quantity=1, groupID=invconst.groupVeldspar, categoryID=invconst.categoryAsteroid, customInfo=None, stacksize=1, singleton=0)
        self._check_does_not_trigger_badging(change, item)
        change = {invconst.ixStackSize: 2}
        item = ItemMock(itemID=original_stack_item_id, typeID=invconst.typeVeldspar, ownerID=CHAR_ID_1, locationID=STATION_ID, flagID=invconst.flagHangar, quantity=1, groupID=invconst.groupVeldspar, categoryID=invconst.categoryAsteroid, customInfo=None, stacksize=1, singleton=0)
        self._check_does_not_trigger_badging(change, item)

    def test_no_badging_if_swapping_ammo(self):
        item_id_original_ammo_iron = 1000000123454L
        item_id_new_ammo_tungsten = 1000000123453L
        change = {ixLocationID: locationAbstract}
        item = ItemMock(itemID=item_id_original_ammo_iron, typeID=invconst.typeIronChargeS, ownerID=CHAR_ID_1, locationID=MY_SHIP_ID, flagID=invconst.flagCargo, quantity=80, groupID=invconst.groupHybridAmmo, categoryID=invconst.categoryCharge, customInfo=KeyValMock(isAmmo=True), stacksize=80, singleton=0)
        self._check_does_not_trigger_badging(change, item)
        change = {invconst.ixStackSize: 80}
        item = ItemMock(itemID=item_id_new_ammo_tungsten, typeID=invconst.typeTungstenChargeS, ownerID=CHAR_ID_1, locationID=MY_SHIP_ID, flagID=invconst.flagCargo, quantity=0, groupID=invconst.groupHybridAmmo, categoryID=invconst.categoryCharge, customInfo=None, stacksize=0, singleton=0)
        self._check_does_not_trigger_badging(change, item)
        change = {ixLocationID: None,
         ixFlag: None}
        item = ItemMock(itemID=(MY_SHIP_ID, invconst.flagHiSlot0, invconst.typeTungstenChargeS), typeID=invconst.typeTungstenChargeS, ownerID=CHAR_ID_1, locationID=MY_SHIP_ID, flagID=invconst.flagHiSlot0, quantity=0, groupID=invconst.groupHybridAmmo, categoryID=invconst.categoryCharge, customInfo=None, stacksize=0, singleton=0)
        self._check_does_not_trigger_badging(change, item)
        change = {ixLocationID: None,
         ixFlag: None}
        item = ItemMock(itemID=(MY_SHIP_ID, invconst.flagHiSlot0, invconst.typeTungstenChargeS), typeID=invconst.typeTungstenChargeS, ownerID=None, locationID=MY_SHIP_ID, flagID=invconst.flagHiSlot0, quantity=0, groupID=invconst.groupHybridAmmo, categoryID=invconst.categoryCharge, customInfo=1, stacksize=0, singleton=0)
        self._check_does_not_trigger_badging(change, item)
        change = {invconst.ixStackSize: 0.0}
        item = ItemMock(itemID=(MY_SHIP_ID, invconst.flagHiSlot0, invconst.typeTungstenChargeS), typeID=invconst.typeTungstenChargeS, ownerID=None, locationID=MY_SHIP_ID, flagID=invconst.flagHiSlot0, quantity=80, groupID=invconst.groupHybridAmmo, categoryID=invconst.categoryCharge, customInfo=None, stacksize=80, singleton=0)
        self._check_does_not_trigger_badging(change, item)

    def test_no_badging_if_swapping_crystal_ammo(self):
        item_id_original_ammo_ultraviolet = 1000000123458L
        item_id_new_ammo_gamma = 1000000123457L
        change = {ixFlag: invconst.flagHiSlot0}
        item = ItemMock(itemID=item_id_original_ammo_ultraviolet, typeID=invconst.typeUltravioletS, ownerID=CHAR_ID_1, locationID=MY_SHIP_ID, flagID=invconst.flagCargo, quantity=1, groupID=invconst.groupFrequencyCrystal, categoryID=invconst.categoryCharge, customInfo=None, stacksize=1, singleton=0)
        self._check_does_not_trigger_badging(change, item)
        change = {ixFlag: invconst.flagCargo}
        item = ItemMock(itemID=item_id_new_ammo_gamma, typeID=invconst.typeGammaS, ownerID=CHAR_ID_1, locationID=MY_SHIP_ID, flagID=invconst.flagHiSlot0, quantity=1, groupID=invconst.groupFrequencyCrystal, categoryID=invconst.categoryCharge, customInfo=None, stacksize=1, singleton=0)
        self._check_does_not_trigger_badging(change, item)

    def test_no_badging_if_loading_damageable_crystal_ammo_from_stack(self):
        aurora_stack_in_cargo_item_id = 1000000140921L
        aurora_loaded_item_id = 1000000140923L
        change = {invconst.ixStackSize: 2}
        item = ItemMock(itemID=aurora_stack_in_cargo_item_id, typeID=invconst.typeAuroraL, ownerID=CHAR_ID_1, locationID=MY_SHIP_ID, flagID=invconst.flagCargo, quantity=1, groupID=invconst.groupAdvancedBeamLaserCrystal, categoryID=invconst.categoryCharge, customInfo=None, stacksize=1, singleton=0)
        self._check_does_not_trigger_badging(change, item)
        change = {ixLocationID: 0}
        item = ItemMock(itemID=aurora_loaded_item_id, typeID=invconst.typeAuroraL, ownerID=CHAR_ID_1, locationID=MY_SHIP_ID, flagID=invconst.flagCargo, quantity=-1, groupID=invconst.groupAdvancedBeamLaserCrystal, categoryID=invconst.categoryCharge, customInfo=KeyValMock(isAmmo=True), stacksize=1, singleton=1)
        self._check_does_not_trigger_badging(change, item)
        change = {ixFlag: invconst.flagCargo}
        item = ItemMock(itemID=aurora_loaded_item_id, typeID=invconst.typeAuroraL, ownerID=CHAR_ID_1, locationID=MY_SHIP_ID, flagID=invconst.flagHiSlot0, quantity=-1, groupID=invconst.groupAdvancedBeamLaserCrystal, categoryID=invconst.categoryCharge, customInfo=None, stacksize=1, singleton=1)
        self._check_does_not_trigger_badging(change, item)

    def test_no_badging_if_probe_retracted(self):
        item_id_retracted_probe = 1000000123462L
        item_id_deployed_probe = 9000007165000001595L
        change = {ixLocationID: locationAbstract}
        item = ItemMock(itemID=item_id_retracted_probe, typeID=invconst.typeCombatScannerProbeI, ownerID=CHAR_ID_1, locationID=MY_SHIP_ID, flagID=invconst.flagCargo, quantity=1, groupID=invconst.groupScannerProbe, categoryID=invconst.categoryCharge, customInfo=(MY_SHIP_ID, MY_SHIP_ID), stacksize=1, singleton=0)
        self._check_does_not_trigger_badging(change, item)
        change = {ixLocationID: SOLAR_SYSTEM_ID}
        item = ItemMock(itemID=item_id_deployed_probe, typeID=invconst.typeCombatScannerProbeI, ownerID=CHAR_ID_1, locationID=locationJunkyard, flagID=invconst.flagNone, quantity=-1, groupID=invconst.groupScannerProbe, categoryID=invconst.categoryCharge, customInfo=(MY_SHIP_ID, MY_SHIP_ID), stacksize=1, singleton=1)
        self._check_does_not_trigger_badging(change, item)

    def test_no_badging_if_probe_retracted_on_stargate_jump(self):
        retracted_probe_item_id = 1000000140505L
        launched_probe_item_id = 9000007250000001843L
        change = {ixLocationID: locationAbstract}
        item = ItemMock(itemID=retracted_probe_item_id, typeID=invconst.typeCoreScannerProbe, ownerID=CHAR_ID_1, locationID=MY_SHIP_ID, flagID=invconst.flagCargo, quantity=1, groupID=invconst.groupScannerProbe, categoryID=invconst.categoryCharge, customInfo=(MY_SHIP_ID, MY_SHIP_ID), stacksize=1, singleton=0)
        self._check_does_not_trigger_badging(change, item)
        change = {ixLocationID: SOLAR_SYSTEM_ID}
        item = ItemMock(itemID=launched_probe_item_id, typeID=invconst.typeCoreScannerProbe, ownerID=CHAR_ID_1, locationID=locationJunkyard, flagID=invconst.flagNone, quantity=-1, groupID=invconst.groupScannerProbe, categoryID=invconst.categoryCharge, customInfo=(MY_SHIP_ID, MY_SHIP_ID), stacksize=1, singleton=1)
        self._check_does_not_trigger_badging(change, item)

    def test_no_badging_if_item_is_consumed(self):
        change = {invconst.ixStackSize: 25}
        item = ItemMock(itemID=1000000123469L, typeID=invconst.typeLiquidOzone, ownerID=CHAR_ID_1, locationID=MY_SHIP_ID, flagID=invconst.flagCargo, quantity=0, groupID=invconst.groupIceProduct, categoryID=invconst.categoryMaterial, customInfo=None, stacksize=0, singleton=0)
        self._check_does_not_trigger_badging(change, item)

    def test_no_badging_if_booster_is_consumed(self):
        change = {invconst.ixSingleton: 0}
        item = ItemMock(itemID=1000000124286L, typeID=invconst.typeQABooster, ownerID=CHAR_ID_1, locationID=STATION_ID, flagID=invconst.flagHangar, quantity=-1, groupID=invconst.groupBooster, categoryID=invconst.categoryImplant, customInfo=None, stacksize=1, singleton=1)
        self._check_does_not_trigger_badging(change, item)
        change = {ixLocationID: STATION_ID,
         ixFlag: invconst.flagHangar}
        item = ItemMock(itemID=1000000124286L, typeID=invconst.typeQABooster, ownerID=CHAR_ID_1, locationID=CHAR_ID_1, flagID=invconst.flagBooster, quantity=-1, groupID=invconst.groupBooster, categoryID=invconst.categoryImplant, customInfo=None, stacksize=1, singleton=1)
        self._check_does_not_trigger_badging(change, item)

    def test_no_badging_if_item_is_unspawned(self):
        change = {ixLocationID: MY_SHIP_ID}
        item = ItemMock(itemID=1000000123472L, typeID=invconst.typeVeldspar, ownerID=CHAR_ID_1, locationID=locationJunkyard, flagID=invconst.flagCargo, quantity=1, groupID=invconst.groupVeldspar, categoryID=invconst.categoryAsteroid, customInfo=None, stacksize=1, singleton=0)
        self._check_does_not_trigger_badging(change, item)

    def test_no_badging_if_item_unfitted(self):
        change = {ixLocationID: MY_SHIP_ID,
         ixFlag: invconst.flagMedSlot0}
        item = ItemMock(itemID=1000000123519L, typeID=invconst.type1MNCivilianAfterburner, ownerID=CHAR_ID_1, locationID=STATION_ID, flagID=invconst.flagHangar, quantity=-1, groupID=invconst.groupPropulsionModule, categoryID=invconst.categoryModule, customInfo=None, stacksize=1, singleton=1)
        self._check_does_not_trigger_badging(change, item)

    def test_no_badging_if_wreck_salvaged(self):
        change = {ixLocationID: locationAbstract}
        item = ItemMock(itemID=1000000123970L, typeID=invconst.typeMetalScraps, ownerID=CHAR_ID_1, locationID=MY_SHIP_ID, flagID=invconst.flagCargo, quantity=1, groupID=invconst.groupCommodities, categoryID=invconst.categoryCommodity, customInfo=KeyValMock(isSalvaged=True), stacksize=1, singleton=0)
        self._check_does_not_trigger_badging(change, item)

    def test_no_badging_if_my_drone_scooped(self):
        change = {ixLocationID: SOLAR_SYSTEM_ID,
         ixFlag: invconst.flagNone}
        item = ItemMock(itemID=1000000124245L, typeID=invconst.typeWarriorII, ownerID=CHAR_ID_1, locationID=MY_SHIP_ID, flagID=invconst.flagCargo, quantity=-1, groupID=invconst.groupCombatDrone, categoryID=invconst.categoryDrone, customInfo=(MY_SHIP_ID, None), stacksize=1, singleton=1)
        self._check_does_not_trigger_badging(change, item)

    def test_no_badging_if_not_my_drone_scooped(self):
        change = {ixOwnerID: CHAR_ID_2,
         ixLocationID: SOLAR_SYSTEM_ID,
         ixFlag: invconst.flagNone}
        item = ItemMock(itemID=1000000124245L, typeID=invconst.typeWarriorII, ownerID=CHAR_ID_1, locationID=MY_SHIP_ID, flagID=invconst.flagCargo, quantity=-1, groupID=invconst.groupCombatDrone, categoryID=invconst.categoryDrone, customInfo=(ANOTHER_SHIP_ID, None), stacksize=1, singleton=1)
        self._check_does_not_trigger_badging(change, item)

    def test_no_badging_if_item_moved_from_inactive_ship_cargo(self):
        change = {ixLocationID: ANOTHER_SHIP_ID,
         ixFlag: invconst.flagCargo}
        item = ItemMock(itemID=1000000124321L, typeID=invconst.typeVeldspar, ownerID=CHAR_ID_1, locationID=STATION_ID, flagID=invconst.flagCargo, quantity=1, groupID=invconst.groupVeldspar, categoryID=invconst.categoryAsteroid, customInfo=None, stacksize=1, singleton=0)
        self._check_does_not_trigger_badging(change, item)

    def test_no_badging_if_plex_withdrawn_from_vault(self):
        change = {ixLocationID: locationAbstract}
        item = ItemMock(itemID=1000000141792L, typeID=invconst.typePlex, ownerID=CHAR_ID_1, locationID=STATION_ID, flagID=invconst.flagHangar, quantity=1, groupID=invconst.groupCurrency, categoryID=invconst.categoryAccessories, customInfo=KeyValMock(isPlexFromVault=True), stacksize=1, singleton=0)
        self._check_does_not_trigger_badging(change, item)


if __name__ == '__main__':
    main()
