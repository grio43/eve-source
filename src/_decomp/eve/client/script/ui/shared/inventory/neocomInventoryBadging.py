#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\inventory\neocomInventoryBadging.py
from carbon.common.lib.const import ixFlag, ixItemID, ixLocationID, ixOwnerID
from collections import defaultdict
from eve.client.script.ui.shared.inventory.invWindow import Inventory
from eve.client.script.ui.shared.inventory.plexUpdatesNotifier import PlexUpdatesNotifier
from eve.client.script.ui.shared.neocom.neocom.btnData.btnDataNodeNotification import BtnDataNodeNotification
from eve.client.script.ui.shared.neocom.neocom.fixedButtonExtension import AmountStorage, SeenItemMultipleLocationsStorage, UnseenItemsExtensionForExistingButton
from eve.client.script.ui.shared.neocom.neocom.neocomConst import BTNTYPE_INVENTORY
from eve.common.lib.appConst import locationAbstract, locationJunkyard
from eve.common.script.sys.idCheckers import IsCapsule, IsCharacter, IsPlex, IsShip, IsSolarSystem, IsStation
from evetypes import GetCategoryID
import inventorycommon.const as invConst
from localization import GetByLabel
from log import LogException
from uthread2 import call_after_wallclocktime_delay, BufferedCall
OPEN_INVENTORY_WINDOW_COMMAND_NAME = 'OpenInventory'
INVENTORY_NAME_LABEL = 'UI/Neocom/InventoryBtn'
INVENTORY_ICON_PATH = 'res:/UI/Texture/WindowIcons/items.png'
INVENTORY_ICON_ID = 'inventory'
NEW_ITEMS_UI_HIGHLIGHT_ID = 2241
NEW_ITEMS_UI_HIGHLIGHT_DELAY_SECS = 0.25
SETTINGS_KEY_SEEN_PLEX = 'SeenPlex'
SETTINGS_GROUP_UNSEEN_ITEMS = 'unseenInventoryItems'
SETTINGS_GROUP_SEEN_ITEMS = 'seenInventoryItems'

class UnseenInventoryItemsBtnData(BtnDataNodeNotification):
    default_btnType = BTNTYPE_INVENTORY
    default_cmdName = OPEN_INVENTORY_WINDOW_COMMAND_NAME
    default_iconPath = INVENTORY_ICON_PATH
    default_btnID = INVENTORY_ICON_ID
    default_label = GetByLabel(INVENTORY_NAME_LABEL)
    default_isBlinking = False
    default_isDraggable = True
    __notifyevents__ = ['OnInventoryItemUnseen']

    def GetItemCount(self):
        return sm.GetService('neocom').GetUnseenInventoryItemsCount()

    def OnInventoryItemUnseen(self, item_ids):
        self.OnBadgeCountChanged()


class NeocomInventoryBadging(object):
    __notifyevents__ = ['OnSessionChanged',
     'OnSessionMutated',
     'OnItemChange',
     'OnInventoryContainerShown',
     'OnInventoryClosed',
     'OnStationServicesHangarDeselected',
     'OnCrateLootSpawned',
     'OnTokensRedeemed',
     'OnClientEvent_MarketItemReceived']

    def __init__(self, inventory_cache, neocom):
        self.inventory_cache = inventory_cache
        self.neocom = neocom
        self._pending_OnInventoryItemUnseen = set()
        self._pending_OnInventoryItemSeen = set()
        sm.RegisterNotify(self)
        self.item_storage_locations = self.build_storage_locations()
        self.item_storages = defaultdict(dict)
        self.tracked_item_storage = None
        self.queued_item_changes = []
        self.plex_updates_notifier = PlexUpdatesNotifier(callback=self.on_plex_updated)
        self.plex_storage = AmountStorage(get_items_function=self.get_plex_balance, settings_container=settings.user.ui, settings_key=SETTINGS_KEY_SEEN_PLEX, start_as_seen=True)
        self.inventory_badging_extension = UnseenItemsExtensionForExistingButton(button_data_class=UnseenInventoryItemsBtnData, get_badge_count=self.get_unseen_items_count, button_id=INVENTORY_ICON_ID)
        self.neocom.RegisterFixedButtonExtension(self.inventory_badging_extension)
        self.inventory_badging_extension.connect_item_changes(self.plex_storage.on_items_changed)
        self.start_tracking()
        self.update_badging()
        self._remove_deprecated_settings_group()

    def _remove_deprecated_settings_group(self):
        settings.char.Remove(SETTINGS_GROUP_SEEN_ITEMS)

    def clear(self):
        self._disconnect_item_changes()
        self.inventory_badging_extension.disconnect_item_changes(self.plex_storage.on_items_changed)
        self.tracked_item_storage = None
        self.queued_item_changes = []
        self.inventory_badging_extension.reset_badge_count()
        self.inventory_badging_extension = None
        sm.UnregisterNotify(self)
        settings.user.ui.Delete(SETTINGS_KEY_SEEN_PLEX)
        settings.char.Remove(SETTINGS_GROUP_UNSEEN_ITEMS)

    def build_storage_locations(self):
        return {invConst.InventoryType.SHIP: [(invConst.INVENTORY_ID_SHIP_CARGO, self.inventory_cache.GetItemsInCurrentShipCargo)],
         invConst.InventoryType.STATION: [(invConst.INVENTORY_ID_STATION_SHIPS, self.inventory_cache.GetItemsInCurrentStationShipHangar), (invConst.INVENTORY_ID_STATION_ITEMS, self.inventory_cache.GetItemsInCurrentStationItemHangar)],
         invConst.InventoryType.STRUCTURE: [(invConst.INVENTORY_ID_STRUCTURE_SHIPS, self.inventory_cache.GetItemsInCurrentStructureShipHangar), (invConst.INVENTORY_ID_STRUCTURE_ITEMS, self.inventory_cache.GetItemsInCurrentStructureItemHangar)]}

    def _get_current_inventory(self):
        station_id = session.stationid
        if station_id:
            return (invConst.InventoryType.STATION, station_id)
        structure_id = session.structureid
        if structure_id:
            return (invConst.InventoryType.STRUCTURE, structure_id)
        ship_id = session.shipid
        if ship_id:
            return (invConst.InventoryType.SHIP, ship_id)

    def _connect_item_changes(self):
        if not self.tracked_item_storage or not self.inventory_badging_extension:
            return
        _, _, item_storage = self.tracked_item_storage
        if hasattr(item_storage, 'on_items_changed'):
            self.inventory_badging_extension.connect_item_changes(item_storage.on_items_changed)

    def _disconnect_item_changes(self):
        if not self.tracked_item_storage or not self.inventory_badging_extension:
            return
        _, _, item_storage = self.tracked_item_storage
        if hasattr(item_storage, 'on_items_changed'):
            self.inventory_badging_extension.disconnect_item_changes(item_storage.on_items_changed)

    def start_tracking(self):
        current_inventory = self._get_current_inventory()
        if current_inventory:
            storage_type, storage_id = current_inventory
            storage = self.create_storage(storage_type, storage_id)
            storage.remove_obsolete_unseen()
            self.tracked_item_storage = (storage_type, storage_id, storage)
        else:
            self.tracked_item_storage = None
        self._connect_item_changes()
        self.process_queued_item_changes()
        sm.GetService('sessionMgr').RegisterNotifyOfSessionChange(self, self.stop_tracking)

    def stop_tracking(self):
        self._disconnect_item_changes()
        self.tracked_item_storage = None
        sm.GetService('sessionMgr').UnregisterNotifyOfSessionChange(self)

    def restart_tracking(self):
        self.stop_tracking()
        self.start_tracking()

    def is_local_change(self, storage):
        if self.tracked_item_storage is None:
            return False
        _, _, tracked_storage = self.tracked_item_storage
        return storage == tracked_storage

    def create_storage(self, storage_type, storage_id):
        if storage_id not in self.item_storages[storage_type]:
            settings.char.CreateGroup(SETTINGS_GROUP_UNSEEN_ITEMS)
            storage = SeenItemMultipleLocationsStorage(settings_container=settings.char.unseenInventoryItems)
            locations = self.item_storage_locations[storage_type]
            for location_id, item_getter in locations:
                storage.add_location_storage(location_id=location_id, item_getter=item_getter, setting_key='%s_%s' % (location_id, storage_id))

            self.item_storages[storage_type][storage_id] = storage
        return self.item_storages[storage_type][storage_id]

    def get_tracked_item_storage(self):
        if self.tracked_item_storage:
            storage_type, storage_id, item_storage = self.tracked_item_storage
            if (storage_type, storage_id) == self._get_current_inventory():
                return item_storage

    def get_item_storage_by_location(self, location):
        if location:
            storage_type, storage_id, location_id = location
            if storage_id in self.item_storages[storage_type]:
                return self.item_storages[storage_type][storage_id]
        if self.tracked_item_storage:
            _, _, storage = self.tracked_item_storage
            return storage

    def get_or_create_item_storage_by_location(self, location):
        if location:
            storage_type, storage_id, location_id = location
            if storage_id in self.item_storages[storage_type]:
                return self.item_storages[storage_type][storage_id]
            return self.create_storage(storage_type, storage_id)

    def _get_item_location(self, type_id, flag_id, location_id):
        if flag_id == invConst.flagCargo:
            return (invConst.InventoryType.SHIP, location_id, invConst.INVENTORY_ID_SHIP_CARGO)
        if flag_id == invConst.flagHangar:
            is_ship = IsShip(categoryID=GetCategoryID(type_id))
            if IsStation(location_id):
                if is_ship:
                    return (invConst.InventoryType.STATION, location_id, invConst.INVENTORY_ID_STATION_SHIPS)
                return (invConst.InventoryType.STATION, location_id, invConst.INVENTORY_ID_STATION_ITEMS)
            if sm.GetService('structureDirectory').IsStructure(location_id):
                if is_ship:
                    return (invConst.InventoryType.STRUCTURE, location_id, invConst.INVENTORY_ID_STRUCTURE_SHIPS)
                return (invConst.InventoryType.STRUCTURE, location_id, invConst.INVENTORY_ID_STRUCTURE_ITEMS)

    def has_unseen_items(self):
        return bool(self.get_unseen_items_count())

    def get_unseen_items_count(self):
        item_storage = self.get_tracked_item_storage()
        unseen_items = item_storage.unseen_count if item_storage else 0
        unseen_plex = self.plex_storage.unseen_count
        return unseen_items + unseen_plex

    def is_item_unseen(self, item_id, type_id, flag_id, location_id):
        location = self._get_item_location(type_id, flag_id, location_id)
        item_storage = self.get_item_storage_by_location(location)
        if item_storage:
            return item_storage.is_unseen(item_id)
        return False

    def mark_item_seen(self, item_id, type_id, flag_id, location_id):
        location = self._get_item_location(type_id, flag_id, location_id)
        item_storage = self.get_item_storage_by_location(location)
        if not item_storage:
            return
        item_storage.mark_as_seen(item_id)
        sm.ScatterEvent('OnInventoryItemSeen', {item_id})
        if self.is_local_change(item_storage):
            sm.ScatterEvent('OnInventoryBadgingUpdated')
            self.neocom.BlinkOff(INVENTORY_ICON_ID)

    def has_unseen_items_in_location(self, location_id):
        if location_id == invConst.INVENTORY_ID_PLEX_VAULT:
            return self.plex_storage.has_unseen()
        item_storage = self.get_tracked_item_storage()
        if item_storage:
            return item_storage.has_unseen_items_in_location(location_id)
        return False

    def mark_items_seen_in_location(self, location_id):
        if location_id == invConst.INVENTORY_ID_PLEX_VAULT:
            self.plex_storage.mark_all_seen()
            self.update_plex_badging()
        else:
            item_storage = self.get_tracked_item_storage()
            if not item_storage:
                return
            item_storage.mark_seen_in_location(location_id)
            sm.ScatterEvent('OnInventoryBadgingUpdated')
            sm.ScatterEvent('OnInventoryLocationSeen', location_id)
        self.neocom.BlinkOff(INVENTORY_ICON_ID)

    def update_badging(self):
        self.plex_storage.update_unseen_count()
        item_storage = self.get_tracked_item_storage()
        if item_storage:
            item_storage.update_unseen_count()
        sm.ScatterEvent('OnInventoryBadgingUpdated')

    def update_plex_badging(self):
        self.plex_storage.update_unseen_count()
        sm.ScatterEvent('OnInventoryBadgingUpdated')

    def is_capsule_change(self, change, item):
        return self.is_automatic_change(change) and IsCapsule(item.groupID)

    def is_my_ship(self, item):
        return item.itemID == session.shipid

    def is_seen_item_id_change(self, change):
        if ixItemID not in change:
            return False
        item_storage = self.get_tracked_item_storage()
        if not item_storage:
            return False
        previous_item_id = change[ixItemID]
        return previous_item_id not in item_storage.get_unseen()

    def has_custom_info_attribute(self, item, name, default_value = False):
        return item.customInfo and hasattr(item.customInfo, 'get') and item.customInfo.get(name, default_value)

    def is_plex_from_vault(self, item):
        return self.has_custom_info_attribute(item, 'isPlexFromVault')

    def is_mined_ore(self, item):
        return self.has_custom_info_attribute(item, 'isMined')

    def is_ammo(self, item):
        return self.has_custom_info_attribute(item, 'isAmmo')

    def is_salvaged_item(self, item):
        return self.has_custom_info_attribute(item, 'isSalvaged')

    def is_item_empty(self, item):
        return item.quantity == 0 and item.stacksize == 0

    def is_item_removed(self, item):
        return item.locationID == locationJunkyard

    def is_item_from_space(self, change):
        return ixLocationID in change and IsSolarSystem(change[ixLocationID])

    def is_booster_consumed(self, item):
        return item.flagID == invConst.flagBooster

    def is_item_from_my_ship(self, change, item):
        if not session.shipid:
            return False
        if ixLocationID in change and change[ixLocationID] == session.shipid:
            return True
        try:
            return any([ each == session.shipid for each in item.customInfo ])
        except Exception:
            pass

        return False

    def is_automatic_change(self, change):
        return ixLocationID in change and change[ixLocationID] == locationAbstract

    def is_owner_change_from_system_to_me(self, change):
        if ixOwnerID not in change:
            return False
        previous_owner_id = change[ixOwnerID]
        return previous_owner_id == invConst.ownerSystem

    def is_owner_change_from_another_player_to_me(self, change):
        if ixOwnerID not in change:
            return False
        previous_owner_id = change[ixOwnerID]
        return session.charid != previous_owner_id and bool(IsCharacter(previous_owner_id))

    def is_crate_loot(self, change):
        if ixFlag not in change:
            return False
        previous_flag_id = change[ixFlag]
        return previous_flag_id == invConst.flagCrateLoot

    def is_seen_item(self, change, item):
        if self.is_capsule_change(change, item):
            return True
        if self.is_my_ship(item):
            return True
        if self.is_plex_from_vault(item):
            return True
        if self.is_mined_ore(item):
            return True
        if self.is_ammo(item):
            return True
        if self.is_salvaged_item(item):
            return True
        if self.is_seen_item_id_change(change):
            return True
        if self.is_item_empty(item):
            return True
        if self.is_item_removed(item):
            return True
        if self.is_item_from_space(change):
            return True
        if self.is_booster_consumed(item):
            return True
        if self.is_item_from_my_ship(change, item):
            return True
        return False

    def is_new_item(self, change, item):
        if self.is_automatic_change(change):
            return True
        if self.is_owner_change_from_system_to_me(change):
            return True
        if self.is_owner_change_from_another_player_to_me(change):
            return True
        if self.is_crate_loot(change):
            return True
        return False

    def OnSessionChanged(self, *args, **kwargs):
        self.on_session_updated()

    def OnSessionMutated(self, *args, **kwargs):
        self.on_session_updated()

    def on_session_updated(self):
        if not session.IsItSafe():
            return
        self.restart_tracking()
        ship_id = session.shipid
        if ship_id:
            item_storage = self.get_tracked_item_storage()
            if item_storage:
                item_storage.mark_as_seen(ship_id)
        sm.ScatterEvent('OnInventoryBadgingUpdated')

    def is_inventory_window_open(self):
        return Inventory.IsOpenByWindowClass()

    def is_badging_triggered(self, change, item, is_local_change):
        return not (is_local_change and self.is_inventory_window_open()) and not self.is_seen_item(change, item) and self.is_new_item(change, item)

    def process_item_change(self, item, change, location):
        storage = self.get_item_storage_by_location(location)
        if not storage:
            return
        item_id = item.itemID
        is_local_change = self.is_local_change(storage)
        is_new_item = self.is_badging_triggered(change, item, is_local_change)
        if is_new_item:
            storage.mark_as_unseen_in_location(item_id, location)
        else:
            storage.mark_as_seen_in_location(item_id, location)
        if is_new_item:
            self._pending_OnInventoryItemUnseen.add(item_id)
            self._pending_OnInventoryItemSeen.discard(item_id)
            self.scatter_buffered_unseen_event()
        else:
            self._pending_OnInventoryItemSeen.add(item_id)
            self._pending_OnInventoryItemUnseen.discard(item_id)
            self.scatter_buffered_seen_event()
        if is_local_change:
            if is_new_item:
                sm.ScatterEvent('OnInventoryBadgingUpdated')
            else:
                self.neocom.BlinkOff(INVENTORY_ICON_ID)

    @BufferedCall(500)
    def scatter_buffered_unseen_event(self):
        unseen_items = self._pending_OnInventoryItemUnseen.copy()
        self._pending_OnInventoryItemUnseen.clear()
        if unseen_items:
            sm.ScatterEvent('OnInventoryItemUnseen', unseen_items)

    @BufferedCall(500)
    def scatter_buffered_seen_event(self):
        seen_items = self._pending_OnInventoryItemSeen.copy()
        self._pending_OnInventoryItemSeen.clear()
        if seen_items:
            sm.ScatterEvent('OnInventoryItemSeen', seen_items)

    def process_queued_item_changes(self):
        if not self.tracked_item_storage:
            return
        while self.queued_item_changes:
            self.process_item_change(*self.queued_item_changes.pop())

    def OnItemChange(self, item, change, location):
        if self.tracked_item_storage:
            self.process_item_change(item, change, location)
        else:
            self.queued_item_changes.append((item, change, location))

    def OnInventoryContainerShown(self, current_inventory_container_id, previous_inventory_container_id):
        if previous_inventory_container_id and current_inventory_container_id != previous_inventory_container_id:
            location_id = previous_inventory_container_id[0]
            self.mark_items_seen_in_location(location_id)

    def OnInventoryClosed(self, inventory_container_id):
        if inventory_container_id:
            location_id = inventory_container_id[0]
            self.mark_items_seen_in_location(location_id)

    def OnStationServicesHangarDeselected(self, location_id):
        self.mark_items_seen_in_location(location_id)

    def get_plex_balance(self):
        try:
            account = sm.GetService('vgsService').GetStore().GetAccount()
            return int(account.GetAurumBalance())
        except Exception:
            LogException('Failed to retrieve the PLEX balance for NEOCOM Inventory badging')
            return 0

    def on_plex_updated(self, new_plex, is_user_move):
        if is_user_move:
            self.plex_storage.mark_amount_as_seen(new_plex)
        else:
            self.plex_storage.update_items(new_plex)
        sm.ScatterEvent('OnInventoryBadgingUpdated')

    def show_new_items_tooltip(self):
        call_after_wallclocktime_delay(tasklet_func=sm.GetService('uiHighlightingService').highlight_ui_element, delay=NEW_ITEMS_UI_HIGHLIGHT_DELAY_SECS, ui_highlight_id=NEW_ITEMS_UI_HIGHLIGHT_ID)

    def OnCrateLootSpawned(self):
        self.show_new_items_tooltip()

    def OnTokensRedeemed(self, character_id, station_id, tokens, numItemsCreated):
        if station_id not in (session.stationid, session.structureid):
            return
        if numItemsCreated:
            self.show_new_items_tooltip()

    def _get_item_location(self, type_id, flag_id, location_id):
        if flag_id == invConst.flagCargo:
            return (invConst.InventoryType.SHIP, location_id, invConst.INVENTORY_ID_SHIP_CARGO)
        if flag_id == invConst.flagHangar:
            is_ship = IsShip(categoryID=GetCategoryID(type_id))
            if IsStation(location_id):
                if is_ship:
                    return (invConst.InventoryType.STATION, location_id, invConst.INVENTORY_ID_STATION_SHIPS)
                return (invConst.InventoryType.STATION, location_id, invConst.INVENTORY_ID_STATION_ITEMS)
            if sm.GetService('structureDirectory').IsStructure(location_id):
                if is_ship:
                    return (invConst.InventoryType.STRUCTURE, location_id, invConst.INVENTORY_ID_STRUCTURE_SHIPS)
                return (invConst.InventoryType.STRUCTURE, location_id, invConst.INVENTORY_ID_STRUCTURE_ITEMS)

    def _is_remote_item_purchase_in_hangar(self, type_id, flag_id, station_id):
        is_local_change = station_id and station_id in (session.stationid, session.structureid)
        is_hangar_change = flag_id == invConst.flagHangar
        is_plex = IsPlex(type_id)
        return not is_local_change and is_hangar_change and not is_plex

    def OnClientEvent_MarketItemReceived(self, item_id, type_id, flag_id, location_id):
        if not self._is_remote_item_purchase_in_hangar(type_id, flag_id, location_id):
            return
        location = self._get_item_location(type_id, flag_id, location_id)
        storage = self.get_or_create_item_storage_by_location(location)
        if not storage:
            return
        storage.mark_as_unseen_in_location(item_id, location)
        sm.ScatterEvent('OnInventoryItemUnseen', {item_id})
