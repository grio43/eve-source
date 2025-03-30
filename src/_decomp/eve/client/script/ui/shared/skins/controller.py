#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\skins\controller.py
import gametime
import uthread2
from cosmetics.client.shipSkinApplicationSvc import get_ship_skin_application_svc
from cosmetics.client.ships.ship_skin_signals import on_skin_state_set, on_skin_license_activated, on_skin_state_reapplied
from cosmetics.client.ships.skins.live_data.ship_skin_state import ShipSkinState
from cosmetics.client.shipSkinLicensesSvc import get_ship_skin_license_svc
from cosmetics.common.ships.skins.static_data.skin_type import ShipSkinType
from cosmetics.common.ships.skins.static_data.slot_configuration import is_skinnable_ship
from eve.client.script.ui.control.message import ShowQuickMessage
from eve.client.script.ui.shared.skins.skinUISignals import on_skin_selected
from eve.client.script.environment.spaceObject.cosmeticsManager import CosmeticsManager
from eve.client.script.environment.sofService import GetSofService
from eve.common.script.sys.idCheckers import IsShipType
from eveexceptions import UserError
from eveexceptions.exceptionEater import ExceptionEater
from itertoolsext import first
import locks
import uthread
import signals
import evetypes
from localization import GetByLabel
from structures import STATE_SHIELD_VULNERABLE
from evegraphics.utils import BuildSOFDNAFromTypeID
from inventorycommon.util import IsModularShip, GetSubSystemTypeIDsForDogmaLocation
import inventorycommon.const as invConst
from carbon.common.script.util.logUtil import LogException, LogInfo
from publicGateway.grpc.exceptions import GenericException
from stackless_response_router.exceptions import TimeoutException
SKIN_DELAY_STRUCTURES = 8

class ThirdPartySkinWrapper(object):

    def __init__(self, third_party_skin_license):
        self.skin = third_party_skin_license
        self.skin_data = self.skin.skin_design
        self.ship_type_id = self.skin.skin_design.ship_type_id

    @property
    def skin_type(self):
        return ShipSkinType.THIRD_PARTY_SKIN

    @property
    def skinID(self):
        return self.skin.skin_hex

    @property
    def name(self):
        return self.skin.skin_design.name

    @property
    def licensed(self):
        return True

    @property
    def expires(self):
        return None

    @property
    def iconTexturePath(self):
        return 'res:/UI/Texture/WindowIcons/paint_tool.png'

    def __eq__(self, other):
        if not isinstance(other, ThirdPartySkinWrapper):
            return False
        return self.skinID == other.skinID


class SkinPanelAdapter(object):

    def ApplySkin(self, controller, itemID, hullTypeID, skin):
        uthread.new(self._ApplySkinThread, controller, itemID, hullTypeID, skin)

    def _ApplySkinThread(self, controller, itemID, hullTypeID, skin):
        try:
            if skin and skin.skin_type == ShipSkinType.THIRD_PARTY_SKIN:
                self._ApplyThirdPartySkin(skin.skinID, itemID)
            else:
                self._ApplyFirstPartySkin(itemID, hullTypeID, skin)
        except Exception:
            controller.OnApplySkinFailed(itemID, skin, hullTypeID)
            raise

    def _ApplyFirstPartySkin(self, itemID, hullTypeID, skin):
        try:
            get_ship_skin_application_svc().apply_first_party_skin(itemID, hullTypeID, skin)
        except UserError as e:
            if e.msg != 'SkinAlreadyApplied':
                raise
        except Exception:
            raise

    def _ApplyThirdPartySkin(self, licenseID, itemID):
        get_ship_skin_application_svc().apply_third_party_skin(itemID, licenseID, apply_license=True, activate_license=False)

    def GetAppliedSkin(self, itemID, hullTypeID, licenseeID = None):
        cosmeticsSvc = sm.GetService('cosmeticsSvc')
        if licenseeID is None:
            skin_state = cosmeticsSvc.GetAppliedSkinStateForCurrentSession(itemID)
        else:
            skin_state = cosmeticsSvc.GetAppliedSkinState(licenseeID, itemID)
        if skin_state is None or skin_state.skin_type == ShipSkinType.NO_SKIN:
            return
        if skin_state.skin_type == ShipSkinType.FIRST_PARTY_SKIN:
            if licenseeID is None:
                return cosmeticsSvc.GetFirstPartySkinObjectForCurrentSession(skin_state.skin_data.skin_id)
            else:
                return cosmeticsSvc.GetFirstPartySkinObject(licenseeID, skin_state.skin_data.skin_id)
        if skin_state.skin_type == ShipSkinType.THIRD_PARTY_SKIN:
            if skin_state.character_id != session.charid:
                return
            else:
                try:
                    skin_license = get_ship_skin_license_svc().get_license(skin_state.skin_data.skin_id, skin_state.character_id)
                except (GenericException, TimeoutException):
                    ShowQuickMessage(GetByLabel('UI/Common/CannotConnectToServer'))
                    skin_license = None

                if skin_license:
                    return ThirdPartySkinWrapper(skin_license)
                return

    def GetSkins(self, hullTypeID):
        if not IsShipType(hullTypeID):
            return []
        skins = sm.GetService('cosmeticsSvc').GetSkins(hullTypeID)
        if is_skinnable_ship(hullTypeID):
            try:
                thirdPartySkins = [ ThirdPartySkinWrapper(skin_license) for skin_license in get_ship_skin_license_svc().get_my_activated_licenses(hullTypeID) ]
                skins.extend(thirdPartySkins)
            except:
                pass

        return sorted(skins, key=lambda s: s.name)

    def GetTypesForSkin(self, skinID):
        skin = sm.GetService('cosmeticsSvc').static.GetSkinByID(skinID)
        return skin.types

    def RegisterNotify(self, controller):
        sm.RegisterNotify(controller)

    def UnregisterNotify(self, controller):
        sm.UnregisterNotify(controller)


class SkinPanelController(object):
    __notifyevents__ = ['OnSkinLicenseActivated']

    def __init__(self, hullTypeID, adapter = None):
        self._adapter = adapter or SkinPanelAdapter()
        self._lock = locks.Lock()
        self.Reset(hullTypeID)
        self.onChange = signals.Signal(signalName='onChange')
        self.onSkinsChange = signals.Signal(signalName='onSkinsChange')
        self.on_position_changed = signals.Signal(signalName='on_position_changed')
        self.onSkinsChange.connect(self.onChange)
        on_skin_license_activated.connect(self._OnThirdPartySkinLicenseActivated)
        self._adapter.RegisterNotify(self)

    def Close(self):
        on_skin_license_activated.disconnect(self._OnThirdPartySkinLicenseActivated)
        self._adapter.UnregisterNotify(self)
        self.onSkinsChange.clear()
        self.onChange.clear()

    def Reset(self, hullTypeID):
        self._typeID = hullTypeID
        self._applied = None
        self._previewed = None
        self._pending = None
        self._skins = None
        self._lastSkinChange = sm.GetService('cosmeticsSvc').lastSkinChange
        self._forcedDelayInSec = 0

    @property
    def typeID(self):
        return self._typeID

    @typeID.setter
    def typeID(self, newTypeID):
        with self._lock:
            self.Reset(newTypeID)
            self.onSkinsChange()

    @property
    def applied(self):
        return self._applied

    @property
    def previewed(self):
        return self._previewed

    @property
    def pending(self):
        return self._pending

    @property
    def skins(self):
        if self._skins is None:
            self._skins = self._adapter.GetSkins(self._typeID)
        return self._skins

    def PickSkinAndMoveToIt(self, skin, deselectIfSame = True):
        self.PickSkin(skin, deselectIfSame)
        uthread2.call_after_wallclocktime_delay(self.on_position_changed, 1)

    def PickSkin(self, skin, deselectIfSame = True):
        with self._lock:
            if self._previewed and skin:
                if hasattr(self._previewed, 'materialID') and hasattr(skin, 'materialID') and self._previewed.materialID == skin.materialID and deselectIfSame:
                    skin = None
                elif self._previewed.skinID and skin.skinID and self._previewed.skinID == skin.skinID:
                    skin = None
            self._previewed = skin
            self.onChange()

    def OnSkinLicenseActivated(self, skinID, licenseeID):
        with self._lock:
            types = self._adapter.GetTypesForSkin(skinID)
            if self._typeID not in types:
                return
            self._skins = None
            self._UpdateActivatedSkin(skinID)
            self.onSkinsChange()

    def _OnThirdPartySkinLicenseActivated(self, licenseID):
        with self._lock:
            self._skins = None
            self._UpdateActivatedSkin(licenseID)
            self.onSkinsChange()

    def _UpdateActivatedSkin(self, skinID):
        if self._previewed is None:
            return
        try:
            skin = self._GetSkinByID(skinID)
            if skin and skin == self._previewed:
                self._previewed = skin
        except StopIteration:
            pass

    def _GetSkinByID(self, skinID):
        try:
            return first(self.skins, lambda s: s.skinID == skinID)
        except StopIteration:
            return None

    def IsSkinAccessRestricted(self):
        return False

    def IsDisabledDueToDamage(self):
        return False

    def GetAppliedSkin(self, itemID, hullTypeID):
        return self._adapter.GetAppliedSkin(itemID, hullTypeID)

    def GetTimeUntilNextAllowedSkinChange(self):
        if self._lastSkinChange is None or self._forcedDelayInSec <= 0:
            return 0
        timeUntil = self._lastSkinChange + self._forcedDelayInSec * const.SEC - gametime.GetWallclockTime()
        return max(0, float(timeUntil) / const.SEC)


class ShipInfoSkinPanelController(SkinPanelController):

    def __init__(self, itemID, ownerID, hullTypeID, adapter = None):
        self.itemID = itemID
        self.ownerID = ownerID
        super(ShipInfoSkinPanelController, self).__init__(hullTypeID, adapter)
        on_skin_state_set.connect(self._OnSkinStateSet)
        on_skin_state_reapplied.connect(self._OnSkinStateReapplied)

    def Reset(self, hullTypeID):
        super(ShipInfoSkinPanelController, self).Reset(hullTypeID)
        self._applied = self.GetAppliedSkin(self.itemID, hullTypeID)

    def GetAppliedSkin(self, itemID, hullTypeID):
        return self._adapter.GetAppliedSkin(itemID, hullTypeID, self.ownerID)

    def PickSkin(self, skin, deselectIfSame = True):
        itemID = self.itemID
        typeID = self.typeID
        if not itemID or self.ownerID != session.charid:
            super(ShipInfoSkinPanelController, self).PickSkin(skin, deselectIfSame)
            return
        with self._lock:
            if skin is not None and skin not in self.skins:
                raise SkinNotAvailableForType('%s not found in %s' % (skin, self.skins))
            if skin is None:
                self._ResetPick(itemID, typeID)
            elif skin.licensed and not self.IsSkinAccessRestricted() and not self.IsDisabledDueToDamage():
                if self.GetTimeUntilNextAllowedSkinChange():
                    raise UserError('CustomNotify', {'notify': GetByLabel('UI/Skins/SkinChangeUnderway')})
                self._PickLicensedSkin(skin, itemID, typeID)
            else:
                self._PickUnlicensedSkin(skin)

    def SetPreviewed(self, skin):
        self._previewed = skin

    def _ResetPick(self, itemID, hullTypeID):
        if all((s is None for s in (self._applied, self._pending, self._previewed))):
            return
        self._applied = None
        self._pending = None
        self._previewed = None
        self._adapter.ApplySkin(self, itemID, hullTypeID, None)
        self.onChange()

    def _PickUnlicensedSkin(self, skin):
        if self._previewed == skin:
            self._previewed = None
        else:
            self._previewed = skin
        self.onChange()

    def _PickLicensedSkin(self, skin, itemID, typeID):
        if self._applied == skin or self._pending == skin:
            skin = None
        self._pending = skin
        self._applied = None
        if skin is not None:
            self._previewed = None
        self._adapter.ApplySkin(self, itemID, typeID, skin)
        self.onChange()
        on_skin_selected(skin)

    def _OnSkinStateSet(self, itemID, skinState):
        if itemID != self.itemID:
            return
        with self._lock:
            if skinState is None and self._applied is None:
                return
            if skinState is None or skinState.skin_type == ShipSkinType.NO_SKIN:
                skin = None
            else:
                skin = self._GetSkinByID(skinState.skin_data.skin_id)
            if self._applied == skin:
                return
            if self._pending and self._pending == skin:
                self._pending = None
            self._applied = skin
            self._lastSkinChange = gametime.GetWallclockTime()
            sm.GetService('cosmeticsSvc').lastSkinChange = self._lastSkinChange
            self.onChange()

    def _OnSkinStateReapplied(self, itemID):
        skin_state = sm.GetService('cosmeticsSvc').GetCachedAppliedSkinState(session.charid, itemID)
        if skin_state:
            self._OnSkinStateSet(itemID, skin_state)


class SkinNotAvailableForType(Exception):
    pass


class FittingSkinPanelController(SkinPanelController):
    __notifyevents__ = SkinPanelController.__notifyevents__ + ['OnSkinLicenseRemoved']

    def __init__(self, fitting, adapter = None):
        self._fitting = fitting
        super(FittingSkinPanelController, self).__init__(hullTypeID=fitting.typeID, adapter=adapter)
        self._UpdateFittingMaterial()
        self.onChange.connect(self._UpdateFittingMaterial)
        on_skin_state_set.connect(self._OnSkinStateSet)
        on_skin_state_reapplied.connect(self._OnSkinStateReapplied)
        self._fitting.on_new_itemID.connect(self.OnNewItemID)

    @property
    def itemID(self):
        return self._itemID

    @property
    def isStructureSkin(self):
        return self._isStructureSkin

    def Reset(self, hullTypeID):
        super(FittingSkinPanelController, self).Reset(hullTypeID)
        self._itemID = self._fitting.itemID
        self._applied = self.GetAppliedSkin(self._itemID, hullTypeID)
        self._isStructureSkin = evetypes.GetCategoryID(hullTypeID) == const.categoryStructure
        if self.isStructureSkin:
            self._forcedDelayInSec = SKIN_DELAY_STRUCTURES

    def GetAppliedSkin(self, itemID, hullTypeID):
        ownerID = self.GetOwnerID()
        return self._adapter.GetAppliedSkin(itemID, hullTypeID, ownerID)

    def PickSkin(self, skin):
        itemID = self.itemID
        typeID = self.typeID
        with self._lock:
            if skin is not None and skin not in self.skins:
                raise SkinNotAvailableForType('%s not found in %s' % (skin, self.skins))
            if skin is None:
                self._ResetPick(itemID, typeID)
            elif skin.licensed and not self.IsSkinAccessRestricted() and not self.IsDisabledDueToDamage():
                if self.GetTimeUntilNextAllowedSkinChange():
                    raise UserError('CustomNotify', {'notify': GetByLabel('UI/Skins/SkinChangeUnderway')})
                self._PickLicensedSkin(skin, itemID, typeID)
            else:
                self._PickUnlicensedSkin(skin)

    def _ResetPick(self, itemID, hullTypeID):
        if all((s is None for s in (self._applied, self._pending, self._previewed))):
            return
        self._applied = None
        self._pending = None
        self._previewed = None
        self._adapter.ApplySkin(self, itemID, hullTypeID, None)
        self.onChange()

    def _PickLicensedSkin(self, skin, itemID, typeID):
        if self._applied == skin or self._pending == skin:
            skin = None
        self._pending = skin
        self._applied = None
        if skin is not None:
            self._previewed = None
        self._adapter.ApplySkin(self, itemID, typeID, skin)
        self.onChange()
        on_skin_selected(skin)

    def _PickUnlicensedSkin(self, skin):
        if self._previewed == skin:
            self._previewed = None
        else:
            self._previewed = skin
        self.onChange()

    def _OnSkinStateSet(self, itemID, skinState):
        if itemID != self.itemID:
            return
        with self._lock:
            if skinState is None and self._applied is None:
                return
            if skinState is None or skinState.skin_type == ShipSkinType.NO_SKIN:
                skin = None
            else:
                skin = self._GetSkinByID(skinState.skin_data.skin_id)
            if self._applied == skin:
                return
            if self._pending and self._pending == skin:
                self._pending = None
            self._applied = skin
            self._lastSkinChange = gametime.GetWallclockTime()
            sm.GetService('cosmeticsSvc').lastSkinChange = self._lastSkinChange
            self.onChange()

    def _OnSkinStateReapplied(self, itemID):
        skin_state = sm.GetService('cosmeticsSvc').GetCachedAppliedSkinState(session.charid, itemID)
        if skin_state:
            self._OnSkinStateSet(itemID, skin_state)

    def OnNewItemID(self, *args):
        self.typeID = self._fitting.typeID

    def OnApplySkinFailed(self, itemID, skin, hullTypeID):
        if itemID != self.itemID:
            return
        with self._lock:
            if self._pending == skin:
                self._pending = None
                self._applied = self.GetAppliedSkin(itemID, hullTypeID)
                self.onChange()

    def _UpdateActivatedSkin(self, skinID):
        if self._applied is not None and self._applied.skinID == skinID:
            self._applied = None
        if self._pending is not None and self._pending.skinID == skinID:
            self._pending = None
        if self._previewed is not None:
            try:
                skin = self._GetSkinByID(skinID)
                if self._previewed == skin:
                    self._previewed = None
            except StopIteration:
                pass

    def _UpdateFittingMaterial(self):
        if self._previewed:
            skin = self._previewed
        elif self._pending:
            skin = self._pending
        elif self._applied:
            skin = self._applied
        else:
            skin = None
        self._fitting.SetDisplayedSkin(skin)

    def OnSkinLicenseRemoved(self, skinID, itemID, typeID):
        with self._lock:
            if self.itemID != itemID:
                return
            types = self._adapter.GetTypesForSkin(skinID)
            if self._typeID not in types:
                return
            self._skins = None
            self.onSkinsChange()
            self._ResetPick(self.itemID, typeID)

    def IsSkinAccessRestricted(self):
        ownerID = self.GetOwnerID()
        if ownerID not in (session.charid, session.corpid):
            return True
        return False

    def GetOwnerID(self):
        if self.itemID:
            dogmaItem = self._fitting.dogmaItem
            if dogmaItem:
                return dogmaItem.ownerID

    def IsDisabledDueToDamage(self):
        return self._IsDamagedStructure()

    def _IsDamagedStructure(self):
        if not self.isStructureSkin:
            return False
        if not self.itemID or self.itemID != session.shipid:
            return False
        ballpark = sm.GetService('michelle').GetBallpark()
        if not ballpark:
            return False
        slimItem = ballpark.GetInvItem(self.itemID)
        if slimItem and slimItem.state != STATE_SHIELD_VULNERABLE:
            return True
        return False

    def Close(self):
        with ExceptionEater('FittingSkinPanelController:Closing '):
            self._fitting.on_new_itemID.disconnect(self.OnNewItemID)
            self._fitting = None
        on_skin_state_set.disconnect(self._OnSkinStateSet)
        on_skin_state_reapplied.disconnect(self._OnSkinStateReapplied)
        SkinPanelController.Close(self)


def GetSkinnedShipModel(skin, typeID, multiHullTypeIDList = None):
    try:
        if skin and skin.skin_type == ShipSkinType.THIRD_PARTY_SKIN:
            return GetSkinnedThirdPartyModel(skin, typeID)
        return GetSkinnedFirstPartyModel(skin, typeID, multiHullTypeIDList)
    except Exception as e:
        LogException(str(e))
        return None


def GetSkinnedFirstPartyModel(skin, typeID, multiHullTypeIDList = None):
    skinMaterialSetID = None
    if skin and skin.skin_type == ShipSkinType.FIRST_PARTY_SKIN:
        skinMaterialSetID = getattr(skin, 'materialSetID', None)
        if not skinMaterialSetID:
            skin_data = getattr(skin, 'skin_data', None)
            if skin_data:
                skinMaterialSetID = sm.GetService('cosmeticsSvc').GetFirstPartySkinMaterialSetID(skin_data.skin_id)
    dna = BuildSOFDNAFromTypeID(typeID, materialSetID=skinMaterialSetID, multiHullTypeIDList=multiHullTypeIDList)
    return GetSofService().spaceObjectFactory.BuildFromDNA(dna)


def GetSkinnedThirdPartyModel(skin, typeID):
    sofDNA = CosmeticsManager.CreateSOFDNAfromSkinState(skin, typeID)
    model = GetSofService().spaceObjectFactory.BuildFromDNA(sofDNA)
    CosmeticsManager.UpdatePatternProjectionParametersFromSkinState(skin, model, typeID)
    blend_mode = skin.skin_data.slot_layout.pattern_blend_mode
    if blend_mode is not None:
        CosmeticsManager.SetBlendMode(model, blendMode=blend_mode)
    return model


def GetMultiHullTypeIDList(typeID, itemID, dogmaLocation):
    if IsModularShip(typeID) and itemID and dogmaLocation:
        multiHullTypeIDList = GetSubSystemTypeIDsForDogmaLocation(itemID, typeID, dogmaLocation)
        if len(multiHullTypeIDList or []) < len(invConst.subsystemSlotFlags):
            return
    else:
        multiHullTypeIDList = None
    return multiHullTypeIDList
