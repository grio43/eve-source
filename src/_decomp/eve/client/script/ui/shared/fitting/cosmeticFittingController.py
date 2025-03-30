#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fitting\cosmeticFittingController.py
from eve.client.script.ui.inflight.shipstance import ShipStanceButtonController
import logging
from eve.client.script.ui.shared.fitting.fittingController import IsSubsystemBeingLoaded
from eve.client.script.ui.shared.skins.controller import GetSkinnedShipModel, GetMultiHullTypeIDList
from shipcosmetics.common.const import CosmeticsType
from cosmetics.common.cosmeticsConst import BACKGROUND_PATH_BY_TYPE, HINT_BY_TYPE
from eve.client.script.ui.shared.fitting.cosmeticSlotController import CosmeticSlotController
import inventorycommon.const as invConst
from eve.common.lib import appConst as const
import signals
from eve.client.script.ui.shared.fitting.fittingUtil import GetTypeIDForController
from localization import GetByLabel
logger = logging.getLogger(__name__)

class CosmeticFittingController(object):
    __notifyevents__ = ['ProcessActiveShipChanged', 'OnDogmaItemChange']
    SLOT_GROUP_LAYOUT_ARCS = {0: (-34, 80),
     1: (55, 20),
     2: (75, 60),
     3: (145, 80),
     4: (236, 70),
     5: (306, 10)}
    SLOT_GROUPS = {0: (CosmeticsType.NONE,
         CosmeticsType.NONE,
         CosmeticsType.NONE,
         CosmeticsType.NONE,
         CosmeticsType.NONE,
         CosmeticsType.NONE,
         CosmeticsType.NONE,
         CosmeticsType.NONE),
     1: (CosmeticsType.ALLIANCE_LOGO, CosmeticsType.CORPORATION_LOGO),
     2: (CosmeticsType.NONE,
         CosmeticsType.NONE,
         CosmeticsType.NONE,
         CosmeticsType.NONE,
         CosmeticsType.NONE,
         CosmeticsType.NONE),
     3: (CosmeticsType.NONE,
         CosmeticsType.NONE,
         CosmeticsType.NONE,
         CosmeticsType.NONE,
         CosmeticsType.NONE,
         CosmeticsType.NONE,
         CosmeticsType.NONE,
         CosmeticsType.NONE),
     4: (CosmeticsType.NONE,
         CosmeticsType.NONE,
         CosmeticsType.NONE,
         CosmeticsType.NONE,
         CosmeticsType.NONE,
         CosmeticsType.NONE,
         CosmeticsType.NONE),
     5: (CosmeticsType.SKIN,)}

    def __init__(self, itemID, typeID = None):
        super(CosmeticFittingController, self).__init__()
        sm.RegisterNotify(self)
        self._dogmaLocation = None
        self._skin = None
        self._slotControllers = {}
        self._itemID = itemID
        self._typeID = typeID or GetTypeIDForController(itemID)
        self.on_skin_material_changed = signals.Signal(signalName='on_skin_material_changed')
        self.on_new_itemID = signals.Signal(signalName='on_new_itemID')
        self.on_hardpoints_fitted = signals.Signal(signalName='on_hardpoints_fitted')
        self.on_subsystem_fitted = signals.Signal(signalName='on_subsystem_fitted')

    def Close(self):
        self.on_new_itemID.clear()
        self.on_skin_material_changed.clear()
        sm.UnregisterNotify(self)

    @property
    def itemID(self):
        return self._itemID

    @property
    def typeID(self):
        return self._typeID

    @property
    def dogmaLocation(self):
        if not self._dogmaLocation:
            self._dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
        return self._dogmaLocation

    @property
    def dogmaItem(self):
        return self.dogmaLocation.SafeGetDogmaItem(self.itemID)

    @property
    def scenePath(self):
        return 'res:/dx9/scene/fitting/fitting.red'

    @property
    def model(self):
        multiHullTypeIDList = GetMultiHullTypeIDList(self.typeID, self.itemID, self.dogmaLocation)
        return GetSkinnedShipModel(self._skin, self.typeID, multiHullTypeIDList)

    @property
    def texturePath(self):
        if not self._skin:
            return None
        return self._skin.iconTexturePath

    def SetDisplayedSkin(self, skin):
        if self._skin == skin:
            return
        self._skin = skin
        self.on_skin_material_changed()

    def GetStanceBtnControllerClass(self):
        return ShipStanceButtonController

    def IsSimulated(self):
        return False

    def GetSlotController(self, cosmeticsType):
        if cosmeticsType == CosmeticsType.NONE:
            return
        backgroundIconPath = BACKGROUND_PATH_BY_TYPE.get(cosmeticsType, '')
        hintPath = HINT_BY_TYPE.get(cosmeticsType, '')
        hint = GetByLabel(hintPath) if hintPath else ''
        return CosmeticSlotController(backgroundIconPath, hint)

    def ProcessActiveShipChanged(self, shipID, oldShipID):
        if not self.IsSimulated():
            self.UpdateItem(shipID)

    def UpdateItem(self, itemID, typeID = None):
        oldItemID = self._itemID
        oldTypeID = self._typeID
        self._itemID = itemID
        if typeID is None:
            typeID = GetTypeIDForController(itemID)
        self._typeID = typeID
        self.on_new_itemID(itemID, oldItemID, typeID, oldTypeID)

    def OnDogmaItemChange(self, item, change):
        locationOrFlagIsInChange = const.ixFlag in change or const.ixLocationID in change
        didStacksizeFlagOrLocationChange = const.ixStackSize in change or locationOrFlagIsInChange
        if not didStacksizeFlagOrLocationChange:
            return
        oldLocationID = change.get(const.ixLocationID, None)
        if self.itemID not in (oldLocationID, item.locationID):
            return
        if item.groupID in invConst.turretModuleGroups:
            self.on_hardpoints_fitted()
        if IsSubsystemBeingLoaded(change, item, self.itemID):
            self.on_subsystem_fitted(throttle=True)
