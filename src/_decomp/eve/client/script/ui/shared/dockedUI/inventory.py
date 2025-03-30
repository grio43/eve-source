#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\dockedUI\inventory.py
import logging
import localization
from carbon.common.script.sys.serviceManager import ServiceManager
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.control.tab import Tab
from carbonui.control.tabGroup import TabGroup
from inventorycommon.const import INVENTORY_ID_STATION_ITEMS, INVENTORY_ID_STATION_SHIPS, INVENTORY_ID_STRUCTURE_ITEMS, INVENTORY_ID_STRUCTURE_SHIPS
logger = logging.getLogger(__name__)

class InventoryPanel(Container):
    _initialized = False
    _items_panel = None
    _ships_panel = None
    _tabs = None

    def __init__(self, station_controller, **kwargs):
        self._station_controller = station_controller
        super(InventoryPanel, self).__init__(**kwargs)

    def on_drop_data(self, source, data):
        if self._items_panel:
            self._items_panel.OnDropData(source, data)

    def _layout(self):
        self._tabs = TabGroup(parent=self, align=uiconst.TOTOP, settingsID='lobbyInventoryPanel', UIIDPrefix='lobbyInventoryPanelTab')
        self._ships_panel = ShipsPanel(parent=self, align=uiconst.TOALL, state=uiconst.UI_HIDDEN, station_controller=self._station_controller)
        self._items_panel = ItemsPanel(parent=self, align=uiconst.TOALL, state=uiconst.UI_HIDDEN, station_controller=self._station_controller)
        self._tabs.AddTab(label=localization.GetByLabel('UI/Station/Ships'), panel=self._ships_panel, tabClass=InventoryTab)
        self._tabs.AddTab(label=localization.GetByLabel('UI/Station/Items'), panel=self._items_panel, tabClass=InventoryTab)
        self._tabs.AutoSelect()

    def _load(self):
        if not self._initialized:
            self._initialized = True
            self._layout()

    def LoadPanel(self):
        self._load()

    def OnDropData(self, dragSource, dragData):
        self.on_drop_data(dragSource, dragData)


class InventoryTab(Tab):
    __notifyevents__ = ('OnInventoryBadgingDestroyed', 'OnInventoryBadgingUpdated')

    def __init__(self, **kwargs):
        super(InventoryTab, self).__init__(**kwargs)
        ServiceManager.Instance().RegisterNotify(self)

    def _update_unseen_item_blink(self):
        panel = self.GetPanel()
        if panel is not None:
            if panel.has_unseen_items():
                self.Blink(True)
            else:
                self.Blink(False)

    def OnInventoryBadgingUpdated(self):
        self._update_unseen_item_blink()

    def OnInventoryBadgingDestroyed(self):
        self._update_unseen_item_blink()


class InventorySubPanel(Container):
    _container = None
    _loaded = False

    def __init__(self, station_controller, **kwargs):
        self._controller = station_controller
        super(InventorySubPanel, self).__init__(**kwargs)

    def has_unseen_items(self):
        inventory_id = self._get_inventory_id()
        if inventory_id is not None:
            neocom_service = ServiceManager.Instance().GetService('neocom')
            return neocom_service.HasUnseenInventoryItemsInLocation(inventory_id)
        else:
            return False

    def _get_inventory_id(self):
        raise NotImplementedError()

    def _get_inventory_container_class(self):
        raise NotImplementedError()

    def _get_inventory_controller_class(self):
        return self._get_inventory_container_class().__invControllerClass__

    def _load(self):
        if self._loaded:
            return
        self._loaded = True
        try:
            location_id = self._controller.GetItemID()
            container_class = self._get_inventory_container_class()
            self._container = container_class(parent=self, state=uiconst.UI_NORMAL, showControls=True, itemID=location_id)
        except Exception:
            logger.exception('Failed to load station inventory sub-panel')

    def LoadPanel(self):
        self._load()

    def OnDropData(self, dragSource, dragData):
        if self._container:
            self._container.OnDropData(dragSource, dragData)
        else:
            controller_class = self._get_inventory_controller_class()
            controller = controller_class(itemID=self._controller.GetItemID())
            controller.OnDropData(dragData)

    def OnSelectedTabDeselected(self):
        inventory_id = self._get_inventory_id()
        if inventory_id is not None:
            ServiceManager.Instance().ScatterEvent('OnStationServicesHangarDeselected', inventory_id)


class ShipsPanel(InventorySubPanel):

    def __init__(self, station_controller, **kwargs):
        super(ShipsPanel, self).__init__(name='StationServices_ShipContainer', station_controller=station_controller, **kwargs)

    def _get_inventory_id(self):
        if session.structureid:
            return INVENTORY_ID_STRUCTURE_SHIPS
        if session.stationid:
            return INVENTORY_ID_STATION_SHIPS

    def _get_inventory_container_class(self):
        container_class = self._controller.GetShipInventoryClass()
        return container_class


class ItemsPanel(InventorySubPanel):

    def __init__(self, station_controller, **kwargs):
        super(ItemsPanel, self).__init__(name='StationServices_ItemContainer', station_controller=station_controller, **kwargs)

    def _get_inventory_id(self):
        if session.structureid:
            return INVENTORY_ID_STRUCTURE_ITEMS
        if session.stationid:
            return INVENTORY_ID_STATION_ITEMS

    def _get_inventory_container_class(self):
        container_class = self._controller.GetItemInventoryClass()
        return container_class
