#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\shipModuleButton\shipmodulebutton.py
import math
import numbers
import re
import dogma.data
import eveicon
import evetypes
from carbon.client.script.environment.AudioUtil import PlaySound
from carbon.client.script.util.misc import HasAttrs
from carbon.common.script.sys.serviceConst import ROLE_GML, ROLE_WORLDMOD
from carbon.common.script.util import timerstuff
from carbon.common.script.util.format import FmtAmt
from carbonui.control.contextMenu.menuEntryData import MenuEntryData
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from eve.client.script.environment.godma import MODULE_NOT_OVERLOADED, MODULE_OVERLOADED, MODULE_PENDING_OVERLOADING, MODULE_PENDING_STOPOVERLOADING
from eve.client.script.ui.control import eveIcon, eveLabel
from eveexceptions import UserError
from inventorycommon.util import GetItemVolume
import uthread
from eve.client.script.ui.util import uix
import blue
from eve.client.script.parklife import states as state
import carbonui.const as uiconst
import inventorycommon.const as invconst
import log
import localization
import trinity
from eve.client.script.ui.crimewatch import crimewatchConst
from eve.client.script.ui.inflight.shipModuleButton.moduleButtonTooltip import TooltipModuleWrapper
from eve.client.script.ui.inflight.shipModuleButton.ramps import DamageStateCont, ShipModuleButtonRamps, ShipModuleReactivationTimer
from eve.client.script.ui.tooltips.tooltipHandler import TOOLTIP_SETTINGS_MODULE, TOOLTIP_DELAY_MODULE
from eve.common.script.sys.eveCfg import IsDocked
from eve.common.script.sys.rowset import IndexedRows
from carbonui.uicore import uicore
from menu import MenuLabel
cgre = re.compile('chargeGroup\\d{1,2}')
GLOWCOLOR = (0.24, 0.67, 0.16, 0.75)
BUSYCOLOR = (1.0, 0.13, 0.0, 0.73)
OVERLOADBTN_INDEX = 1
MODULEHINTDELAY = 800
GROUPS_THAT_ALWAYS_AUTO_REPEAT = (invconst.groupMiningLaser, invconst.groupStripMiner, invconst.groupEntosisLink)
SOUND_MODULE_ONLINE = 'ui_module_online_play'
SOUND_MODULE_OFFLINE = 'ui_module_offline_play'

class ModuleButton(Container):
    __guid__ = 'xtriui.ModuleButton'
    __notifyevents__ = ['OnStateChange',
     'OnModuleRepaired',
     'OnAmmoInBankChanged',
     'OnFailLockTarget',
     'OnChargeBeingLoadedToModule',
     'OnModulesDeactivating',
     'OnMultiModuleRepairStarted']
    __update_on_reload__ = 1
    __cgattrs__ = []
    __chargesizecache__ = {}
    default_name = 'ModuleButton'
    default_pickRadius = 20
    isDragObject = True
    def_effect = None
    charge = None
    target = None
    waitingForActiveTarget = 0
    online = False
    stateManager = None
    dogmaLocation = None
    autorepeat = 0
    autoreload = 0
    quantity = None
    invReady = 1
    invCookie = None
    isInvItem = 1
    isBeingRepaired = 0
    blinking = 0
    blinkingDamage = 0
    effect_activating = 0
    typeName = ''
    ramp_active = False
    isMaster = 0
    animation = None
    isPendingUnlockForDeactivate = False
    moduleHintTimer = None
    shouldUpdate = False
    moduleButtonHint = None
    moduleinfo = None
    tooltipPanelClassInfo = TooltipModuleWrapper()

    @property
    def reloadingAmmo(self):
        try:
            return self.stateManager.IsModuleReloading(self.moduleinfo.itemID)
        except KeyError:
            return False

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.icon = eveIcon.Icon(parent=self, align=uiconst.TOALL, state=uiconst.UI_DISABLED)
        self.reloadAnimationThread = self.blinkButtonThread = None
        sm.RegisterNotify(self)

    def Close(self, *args, **kwds):
        if getattr(self, 'invCookie', None) is not None:
            sm.GetService('inv').Unregister(self.invCookie)
        Container.Close(self, *args, **kwds)

    def GetRepeatCount(self):
        repeat = settings.char.autorepeat.Get(self.moduleinfo.itemID, -1)
        alwaysAutoRepeats = evetypes.GetGroupID(self.moduleinfo.typeID) in GROUPS_THAT_ALWAYS_AUTO_REPEAT
        containsRepeatableEffect = any(map(self.IsEffectRepeatable, self.moduleinfo.effects.itervalues()))
        if alwaysAutoRepeats:
            return 1000
        if repeat != -1:
            return repeat
        if containsRepeatableEffect:
            return 1000
        return 0

    def Setup(self, moduleinfo, grey = None):
        self.crimewatchSvc = sm.GetService('crimewatchSvc')
        if not len(self.__cgattrs__):
            self.__cgattrs__.extend([dogma.data.get_charge_group_attribute_ids()])
        self.id = moduleinfo.itemID
        self.moduleinfo = moduleinfo
        self.locationFlag = moduleinfo.flagID
        self.stateManager = sm.StartService('godma').GetStateManager()
        self.dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
        self.grey = grey
        self.isInActiveState = True
        self.isDeactivating = False
        icon = self.parent.GetChild('overloadBtn')
        icon.hint = localization.GetByLabel('UI/Inflight/Overload/TurnOnOverload')
        icon.OnClick = self.ToggleOverload
        icon.OnMouseDown = (self.OLButtonDown, icon)
        icon.OnMouseUp = (self.OLButtonUp, icon)
        icon.OnMouseEnter = (self.OLMouseEnter, icon)
        icon.OnMouseExit = (self.OLMouseExit, icon)
        icon.SetOrder(OVERLOADBTN_INDEX)
        self.sr.overloadButton = icon
        if cfg.IsChargeCompatible(moduleinfo):
            self.invCookie = sm.GetService('inv').Register(self)
        self.autoreload = settings.char.autoreload.Get(self.moduleinfo.itemID, 1)
        if evetypes.GetCategoryID(moduleinfo.typeID) == const.categoryCharge:
            self.SetCharge(moduleinfo)
        else:
            self.SetCharge(None)
        self.autoreload = settings.char.autoreload.Get(self.moduleinfo.itemID, 1)
        for key in moduleinfo.effects.iterkeys():
            effect = moduleinfo.effects[key]
            if self.IsEffectActivatible(effect):
                self.def_effect = effect
                if effect.isActive:
                    if effect.isDeactivating:
                        self.SetDeactivating()
                    else:
                        self.SetActive()
            if effect.effectName == 'online':
                if effect.isActive:
                    self.ShowOnline()
                else:
                    self.ShowOffline()

        self.autoreload = settings.char.autoreload.Get(self.moduleinfo.itemID, 1)
        repairTimeStamps = self.stateManager.GetRepairTimeStamp(self.id)
        if repairTimeStamps:
            self.isBeingRepaired = True
            self.SetRepairing(repairTimeStamps)
        self.TryStartCooldownTimers()
        reloadTimes = self.stateManager.GetReloadTimes(self.id)
        if reloadTimes:
            startTime, duration = reloadTimes
            self.DoReloadAnimation(duration, startTime=startTime)
        repeatCount = self.GetRepeatCount()
        self.SetRepeat(repeatCount)
        self.autoreload = settings.char.autoreload.Get(self.moduleinfo.itemID, 1)
        if not self.isDeactivating:
            self.isInActiveState = True
        else:
            self.isInActiveState = False
        self.slaves = self.dogmaLocation.GetSlaveModules(self.moduleinfo.itemID, session.shipid)
        self.UpdateModuleDamage()
        self.EnableDrag()
        self.autoreload = settings.char.autoreload.Get(self.moduleinfo.itemID, 1)
        uthread.new(self.BlinkIcon)

    def UpdateModuleDamage(self):
        moduleDamage = self.GetModuleDamage()
        if moduleDamage:
            self.SetDamage(moduleDamage / self.moduleinfo.hp)
        else:
            self.SetDamage(0.0)

    def OLButtonDown(self, btn, *args):
        btn.top = 6

    def OLButtonUp(self, btn, *args):
        btn.top = 5

    def OLMouseExit(self, btn, *args):
        btn.top = 5

    def OLMouseEnter(self, btn, *args):
        PlaySound(uiconst.SOUND_BUTTON_HOVER)

    def ToggleOverload(self, *args):
        if settings.user.ui.Get('lockOverload', 0):
            existingModal = uicore.registry.GetModalWindow()
            if existingModal and existingModal.msgKey == 'LockedOverloadState':
                return
            eve.Message('error')
            eve.Message('LockedOverloadState')
            return
        for effect in self.moduleinfo.effects.itervalues():
            if effect.effectCategory == const.dgmEffOverload:
                effectID = effect.effectID
                break
        else:
            return

        overloadState = self.stateManager.GetOverloadState(self.moduleinfo.itemID)
        eve.Message('click')
        itemID = self.moduleinfo.itemID
        if overloadState == MODULE_NOT_OVERLOADED:
            self.stateManager.Overload(itemID, effectID)
            self.sr.overloadButton.hint = localization.GetByLabel('UI/Inflight/Overload/TurnOffOverload')
        elif overloadState == MODULE_OVERLOADED:
            self.stateManager.StopOverload(itemID, effectID)
            self.sr.overloadButton.hint = localization.GetByLabel('UI/Inflight/Overload/TurnOnOverload')
        elif overloadState == MODULE_PENDING_OVERLOADING:
            self.stateManager.StopOverload(itemID, effectID)
        elif overloadState == MODULE_PENDING_STOPOVERLOADING:
            self.stateManager.StopOverload(itemID, effectID)

    def UpdateOverloadState(self):
        overloadState = self.stateManager.GetOverloadState(self.moduleinfo.itemID)
        if overloadState == MODULE_PENDING_OVERLOADING:
            self.animation = uicore.animations.BlinkIn(self.sr.overloadButton, startVal=1.8, endVal=1.0, duration=0.5, loops=uiconst.ANIM_REPEAT)
        elif overloadState == MODULE_PENDING_STOPOVERLOADING:
            self.animation = uicore.animations.BlinkIn(self.sr.overloadButton, startVal=0.2, endVal=1.0, duration=0.5, loops=uiconst.ANIM_REPEAT)
        else:
            if self.animation:
                self.animation.Stop()
            self.sr.overloadButton.SetAlpha(1.0)
        if overloadState == MODULE_OVERLOADED:
            self.sr.overloadButton.hint = localization.GetByLabel('UI/Inflight/Overload/TurnOffOverload')
        elif overloadState == MODULE_NOT_OVERLOADED:
            self.sr.overloadButton.hint = localization.GetByLabel('UI/Inflight/Overload/TurnOnOverload')

    def InitQuantityLabel(self):
        if self.sr.qtylabel is None:
            quantityParent = Container(parent=self, name='quantityParent', pos=(18, 27, 24, 10), align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, idx=0)
            self.sr.qtylabel = eveLabel.Label(text='', parent=quantityParent, fontsize=9, letterspace=1, left=3, top=0, width=30, state=uiconst.UI_DISABLED)
            underlay = Sprite(parent=quantityParent, name='underlay', pos=(0, 0, 0, 0), align=uiconst.TOALL, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/ShipUI/slotQuantityUnderlay.png', color=(0.0, 0.0, 0.0, 1.0))

    def SetCharge(self, charge):
        if charge and charge.stacksize != 0:
            if self.charge is None or charge.typeID != self.charge.typeID:
                self.icon.LoadIconByTypeID(charge.typeID)
            self.charge = charge
            self.stateManager.ChangeAmmoTypeForModule(self.moduleinfo.itemID, charge.typeID)
            self.id = charge.itemID
            self.UpdateChargeQuantity(charge)
        else:
            self.icon.LoadIconByTypeID(self.moduleinfo.typeID)
            if self.sr.qtylabel:
                self.sr.qtylabel.parent.state = uiconst.UI_HIDDEN
            self.quantity = 0
            self.id = self.moduleinfo.itemID
            self.charge = None
        self.CheckOverload()
        self.CheckOnline()
        self.CheckMasterSlave()

    def UpdateChargeQuantity(self, charge):
        if charge is self.charge:
            if evetypes.GetGroupID(charge.typeID) in cfg.GetCrystalGroups():
                if self.sr.qtylabel:
                    self.sr.qtylabel.parent.state = uiconst.UI_HIDDEN
                return
            self.InitQuantityLabel()
            self.quantity = charge.stacksize
            self.sr.qtylabel.text = '%s' % FmtAmt(charge.stacksize)
            self.sr.qtylabel.parent.state = uiconst.UI_DISABLED

    def ShowGroupHighlight(self):
        self.dragging = True
        if self.sr.groupHighlight is None:
            groupHighlight = Container(parent=self.parent, name='groupHighlight', pos=(0, 0, 64, 64), align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED)
            leftCircle = Sprite(parent=groupHighlight, name='leftCircle', pos=(0, 0, 32, 64), texturePath='res:/UI/Texture/classes/ShipUI/slotRampLeft.png')
            rightCircle = Sprite(parent=groupHighlight, name='leftCircle', pos=(32, 0, 32, 64), texturePath='res:/UI/Texture/classes/ShipUI/slotRampRight.png')
            self.sr.groupHighlight = groupHighlight
        else:
            self.sr.groupHighlight.state = uiconst.UI_DISABLED
        uthread.new(self.PulseGroupHighlight)

    def StopShowingGroupHighlight(self):
        self.dragging = False
        if self.sr.groupHighlight:
            self.sr.groupHighlight.state = uiconst.UI_HIDDEN

    def PulseGroupHighlight(self):
        pulseSize = 0.4
        opacity = 1.0
        startTime = blue.os.GetSimTime()
        while self.dragging:
            self.sr.groupHighlight.opacity = opacity
            blue.pyos.synchro.SleepWallclock(200)
            if not self or self.destroyed:
                break
            sinWave = math.cos(float(blue.os.GetSimTime() - startTime) / (0.5 * const.SEC))
            opacity = min(sinWave * pulseSize + (1 - pulseSize / 2), 1)

    def SetDamage(self, damage):
        if not damage or damage < 0.0001:
            if self.sr.damageState:
                self.sr.damageState.state = uiconst.UI_HIDDEN
            return
        imageIndex = max(1, int(damage * 8))
        if self.sr.damageState is None:
            if self.sr.ramps:
                idx = OVERLOADBTN_INDEX + 2
            else:
                idx = OVERLOADBTN_INDEX + 1
            self.sr.damageState = DamageStateCont(parent=self.parent, name='damageState', pos=(0, 0, 64, 64), align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL, texturePath='res:/UI/Texture/classes/ShipUI/slotDamage_%s.png' % imageIndex, idx=idx)
        self.sr.damageState.state = uiconst.UI_NORMAL
        self.sr.damageState.SetDamage(damage)
        amount = self.moduleinfo.damage / self.moduleinfo.hp * 100
        self.sr.damageState.hint = localization.GetByLabel('UI/Inflight/Overload/hintDamagedModule', preText='', amount=amount)
        self.sr.damageState.Blink(damage)

    def GetVolume(self):
        if self.charge:
            return GetItemVolume(self.charge, 1)

    def IsItemHere(self, rec):
        ret = rec.locationID == eve.session.shipid and rec.flagID == self.locationFlag and evetypes.GetCategoryID(rec.typeID) == const.categoryCharge
        return ret

    def AddItem(self, rec):
        if evetypes.GetCategoryID(rec.typeID) == const.categoryCharge:
            self.SetCharge(rec)

    def UpdateItem(self, rec, change):
        if evetypes.GetCategoryID(rec.typeID) == const.categoryCharge:
            self.SetCharge(rec)

    def RemoveItem(self, rec):
        if evetypes.GetCategoryID(rec.typeID) == const.categoryCharge:
            if self.charge and rec.itemID == self.id:
                self.SetCharge(None)

    def GetShell(self):
        return sm.GetService('invCache').GetInventoryFromId(eve.session.shipid)

    def IsCorrectChargeSize(self, item, wantChargeSize):
        if not self.__chargesizecache__.has_key(item.typeID):
            cRS = dogma.data.get_type_attributes(item.typeID)
            cAttribs = IndexedRows(cRS, ('attributeID',))
            if cAttribs.has_key(const.attributeChargeSize):
                gotChargeSize = cAttribs[const.attributeChargeSize].value
            else:
                gotChargeSize = 0
            self.__chargesizecache__[item.typeID] = gotChargeSize
        else:
            gotChargeSize = self.__chargesizecache__[item.typeID]
        if wantChargeSize != gotChargeSize:
            return 0
        return 1

    def BlinkIcon(self, time = None):
        if self.destroyed or self.blinking:
            return
        startTime = blue.os.GetSimTime()
        if time is not None:
            timeToBlink = time * 10000
        while self.reloadingAmmo or self.waitingForActiveTarget or time:
            if time is not None:
                if blue.os.GetSimTime() - startTime > timeToBlink:
                    break
            blue.pyos.synchro.SleepWallclock(250)
            if self.destroyed:
                return
            self.icon.SetAlpha(0.25)
            blue.pyos.synchro.SleepWallclock(250)
            if self.destroyed:
                return
            self.icon.SetAlpha(1.0)

        if self.destroyed:
            return
        self.blinking = 0
        self.CheckOverload()
        self.CheckOnline()

    def DoNothing(self, *args):
        pass

    def CopyItemIDToClipboard(self, itemID):
        blue.pyos.SetClipboardData(str(itemID))

    def GetMenu(self):
        ship = sm.GetService('godma').GetItem(eve.session.shipid)
        if ship is None:
            return []
        m = []
        if session.role & (ROLE_GML | ROLE_WORLDMOD):
            m.append(('GM / WM Extras', self._GetMenuElevated()))
        groupID = evetypes.GetGroupID(self.moduleinfo.typeID)
        if cfg.IsChargeCompatible(self.moduleinfo):
            chargeTypeID, chargeQuantity, roomForReload = self.GetChargeReloadInfo()
            m.extend(self.dogmaLocation.GetAmmoMenu(session.shipid, self.moduleinfo.itemID, self.charge, roomForReload))
            if self.autoreload == 0:
                m.append((MenuLabel('UI/Inflight/ModuleRacks/AutoReloadOn'), self.SetAutoReload, (1,)))
            else:
                m.append((MenuLabel('UI/Inflight/ModuleRacks/AutoReloadOff'), self.SetAutoReload, (0,)))
        overloadLock = settings.user.ui.Get('lockOverload', 0)
        itemID = self.moduleinfo.itemID
        slaves = self.dogmaLocation.GetSlaveModules(itemID, session.shipid)
        thermodynamicsLevel = sm.GetService('skills').GetMyLevel(invconst.typeThermodynamics)
        for key in self.moduleinfo.effects.iterkeys():
            effect = self.moduleinfo.effects[key]
            if self.IsEffectRepeatable(effect) and groupID not in GROUPS_THAT_ALWAYS_AUTO_REPEAT:
                if self.autorepeat == 0:
                    m.append((MenuLabel('UI/Inflight/ModuleRacks/AutoRepeatOn'), self.SetRepeat, (1000,)))
                else:
                    m.append((MenuLabel('UI/Inflight/ModuleRacks/AutoRepeatOff'), self.SetRepeat, (0,)))
            if effect.effectName == 'online':
                m.append(None)
                if not slaves:
                    if effect.isActive:
                        m.append((MenuLabel('UI/Inflight/ModuleRacks/PutModuleOffline'), self.ChangeOnline, (0,)))
                    else:
                        m.append((MenuLabel('UI/Inflight/ModuleRacks/PutModuleOnline'), self.ChangeOnline, (1,)))
            if not overloadLock and effect.effectCategory == const.dgmEffOverload:
                requiredThermoLevel = self.dogmaLocation.GetAttributeValue(itemID, const.attributeRequiredThermoDynamicsSkill)
                if thermodynamicsLevel >= requiredThermoLevel:
                    active = effect.isActive
                    if active:
                        m.append(MenuEntryData(MenuLabel('UI/Inflight/Overload/TurnOffOverload'), lambda _effect = effect: self.Overload(False, _effect), texturePath=eveicon.pause))
                    else:
                        m.append(MenuEntryData(MenuLabel('UI/Inflight/Overload/TurnOnOverload'), lambda _effect = effect: self.Overload(True, _effect), texturePath=eveicon.circle_plus))
                    m.append((MenuLabel('UI/Inflight/OverloadRack'), self.OverloadRack, ()))
                    m.append((MenuLabel('UI/Inflight/StopOverloadingRack'), self.StopOverloadRack, ()))

        moduleDamage = self.GetModuleDamage()
        if moduleDamage:
            if self.stateManager.IsBeingRepaired(self.moduleinfo.itemID):
                m.append((MenuLabel('UI/Inflight/menuCancelRepair'), self.CancelRepair, ()))
            else:
                unitsToRepair = int(self.GetNumUnitsToRepair())
                if unitsToRepair:
                    m.append((MenuLabel('UI/Inflight/RepairWithQty', {'qty': unitsToRepair}), self.RepairModule, ()))
                else:
                    m.append((MenuLabel('UI/Commands/Repair'), self.RepairModule, ()))
        damagedModulesAndRepairCost = self.GetDamagedModulesAndRepairCost()
        if len(damagedModulesAndRepairCost) > 1:
            unitsToRepair = sum((x[1] for x in damagedModulesAndRepairCost))
            moduleIDs = [ x[0] for x in damagedModulesAndRepairCost ]
            if self.moduleinfo.itemID in moduleIDs and moduleIDs.index(self.moduleinfo.itemID) != 0:
                moduleIDs.remove(self.moduleinfo.itemID)
                moduleIDs.insert(0, self.moduleinfo.itemID)
            if unitsToRepair:
                m.append((MenuLabel('UI/Inflight/RepairAllWithQty', {'qty': int(unitsToRepair)}), self.RepairManyModules, (moduleIDs,)))
            else:
                m.append((MenuLabel('UI/Commands/RepairAll'), self.RepairManyModules, (moduleIDs,)))
        allRepairingModuleIDs = self.GetAllRepairingModules()
        if len(allRepairingModuleIDs) > 1:
            m.append((MenuLabel('UI/Inflight/menuCancelAllRepairs'), self.CancelRepairManyModuels, (allRepairingModuleIDs,)))
        if slaves:
            m.append((MenuLabel('UI/Fitting/ClearGroup'), self.UnlinkModule, ()))
        m += [(MenuLabel('UI/Commands/ShowInfo'), sm.GetService('info').ShowInfo, (self.moduleinfo.typeID,
           self.moduleinfo.itemID,
           0,
           self.moduleinfo))]
        return m

    def _GetMenuElevated(self):
        m = []
        effectMenu = []
        if cfg.IsChargeCompatible(self.moduleinfo):
            m += [('Launcher: ' + str(self.moduleinfo.itemID), self.CopyItemIDToClipboard, (self.moduleinfo.itemID,))]
            if self.id != self.moduleinfo.itemID:
                m += [('Charge: ' + str(self.id), self.CopyItemIDToClipboard, (self.id,)), None]
                chargeTypeID, _, _ = self.GetChargeReloadInfo()
                chargeDefaultEffectID, chargeEffectName = self._GetDefaultEffectIDAndName(chargeTypeID)
                if chargeDefaultEffectID:
                    effectMenu += [('Charge defaultEffect: %s (%s)' % (chargeEffectName, chargeDefaultEffectID), self.CopyItemIDToClipboard, (chargeDefaultEffectID,))]
        else:
            m += [(str(self.id), self.CopyItemIDToClipboard, (self.id,)), None]
        defaultEffectID, effectName = self._GetDefaultEffectIDAndName(self.moduleinfo.typeID)
        if defaultEffectID:
            effectMenu.insert(0, ('Module defaultEffect: %s (%s)' % (effectName, defaultEffectID), self.CopyItemIDToClipboard, (defaultEffectID,)))
        if effectMenu:
            m += effectMenu
            m += [None]
        m += sm.GetService('menu').GetGMTypeMenu(self.moduleinfo.typeID, itemID=self.id, divs=True, unload=True)
        return m

    def _GetDefaultEffectIDAndName(self, typeID):
        try:
            defaultEffectID = self.dogmaLocation.dogmaStaticMgr.GetDefaultEffect(typeID)
            if not defaultEffectID:
                return (None, None)
            effect = self.dogmaLocation.dogmaStaticMgr.GetEffect(defaultEffectID)
            return (defaultEffectID, effect.effectName)
        except StandardError:
            return (None, None)

    def RepairModule(self):
        error = None
        success = False
        try:
            success = self.stateManager.RepairModule(self.moduleinfo.itemID)
        except UserError as e:
            if e.msg == 'NotEnoughRepairMaterialToFinishAllRepairs':
                error = e
            else:
                raise

        if self.slaves:
            for slave in self.slaves:
                try:
                    success = self.stateManager.RepairModule(slave) or success
                except UserError as e:
                    if e.msg == 'NotEnoughRepairMaterialToFinishAllRepairs':
                        error = e
                    else:
                        raise

        if success:
            self.isBeingRepaired = True
            self.SetRepairing()
        if error:
            raise error

    def RepairManyModules(self, moduleIDs):
        self.stateManager.RepairManyModules(moduleIDs)

    def CancelRepair(self):
        success = self.stateManager.StopRepairModule(self.moduleinfo.itemID)
        if self.slaves:
            for slave in self.slaves:
                success = self.stateManager.StopRepairModule(slave) and success

        if success == True:
            self.isBeingRepaired = False
            self.RemoveRepairing()

    def CancelRepairManyModuels(self, moduleIDs):
        self.stateManager.StopRepairModuleManyModules(moduleIDs)

    def OnModulesDeactivating(self, moduleIDs):
        if self.moduleinfo.itemID in moduleIDs:
            self.SetDeactivating()

    def OnFailLockTarget(self, tid, *args):
        self.waitingForActiveTarget = 0

    def OnMultiModuleRepairStarted(self, moduleIDs):
        if self.moduleinfo.itemID not in moduleIDs:
            return
        self.isBeingRepaired = True
        self.SetRepairing()

    def OnModuleRepaired(self, itemID):
        if itemID == self.moduleinfo.itemID:
            self.RemoveRepairing()
            self.isBeingRepaired = False
            self.UpdateModuleDamage()

    def OnAmmoInBankChanged(self, masterID):
        slaves = self.dogmaLocation.GetSlaveModules(masterID, session.shipid)
        if self.moduleinfo.itemID in slaves:
            self.SetCharge(self.moduleinfo)

    def OnChargeBeingLoadedToModule(self, itemIDs, chargeTypeID, time):
        if self.moduleinfo.itemID not in itemIDs:
            return
        if chargeTypeID is None:
            if self.reloadAnimationThread and self.reloadAnimationThread.alive:
                self.reloadAnimationThread.kill()
            if self.blinkButtonThread and self.blinkButtonThread.alive:
                self.blinkButtonThread.kill()
            if self.sr.ramps:
                self.sr.ramps.display = False
        else:
            chargeGroupID = evetypes.GetGroupID(chargeTypeID)
            params = {'ammoGroupName': (const.UE_GROUPID, chargeGroupID),
             'launcherGroupName': (const.UE_GROUPID, self.moduleinfo.groupID),
             'time': time / 1000}
            self.DoReloadAnimation(time)
            self.DisplayLoadMessage(params)

    def DoReloadAnimation(self, duration, startTime = None):
        if startTime:
            blinkTime = max(0, duration - (blue.os.GetSimTime() - startTime) / 10000)
        else:
            blinkTime = duration
        self.reloadAnimationThread = uthread.new(self.ShowReloadLeft, duration, startTime)
        self.blinkButtonThread = uthread.new(self.BlinkIcon, blinkTime)

    def DisplayLoadMessage(self, params):
        blue.pyos.synchro.SleepSim(0.1)
        if self.reloadAnimationThread and self.reloadAnimationThread.alive:
            eve.Message('LauncherLoadDelay', params)

    def TryStartCooldownTimers(self):
        cooldownTimes = self.stateManager.GetCooldownTimes(self.moduleinfo.itemID)
        if cooldownTimes:
            startTime, duration = cooldownTimes
            self.DoReactivationAnimation(duration, startTime=startTime)

    def DoReactivationAnimation(self, duration, startTime = None):
        uthread.new(self.ShowReactivationLeft, duration, startTime)

    def UnlinkModule(self):
        self.dogmaLocation.DestroyWeaponBank(session.shipid, self.moduleinfo.itemID)

    def Overload(self, onoff, eff):
        if onoff:
            eff.Activate()
        else:
            eff.Deactivate()

    def OverloadRack(self):
        sm.GetService('godma').OverloadRack(self.moduleinfo.itemID)

    def StopOverloadRack(self):
        sm.GetService('godma').StopOverloadRack(self.moduleinfo.itemID)

    def GetChargeReloadInfo(self, ignoreCharge = 0):
        evetypes.RaiseIFNotExists(self.moduleinfo.typeID)
        lastChargeTypeID = self.stateManager.GetAmmoTypeForModule(self.moduleinfo.itemID)
        if self.charge and not ignoreCharge:
            chargeTypeID = self.charge.typeID
            chargeQuantity = self.charge.stacksize
        elif lastChargeTypeID is not None:
            chargeTypeID = lastChargeTypeID
            chargeQuantity = 0
        else:
            chargeTypeID = None
            chargeQuantity = 0
        if chargeTypeID is not None:
            roomForReload = int(evetypes.GetCapacity(self.moduleinfo.typeID) / evetypes.GetVolume(chargeTypeID) - chargeQuantity + 1e-07)
        else:
            roomForReload = 0
        return (chargeTypeID, chargeQuantity, roomForReload)

    def SetAutoReload(self, on):
        settings.char.autoreload.Set(self.moduleinfo.itemID, on)
        self.autoreload = on
        self.AutoReload()

    def AutoReload(self, force = 0, useItemID = None, useQuant = None):
        if self.reloadingAmmo is not False:
            return
        if not cfg.IsChargeCompatible(self.moduleinfo) or not (self.autoreload or force):
            return
        chargeTypeID, chargeQuantity, roomForReload = self.GetChargeReloadInfo()
        if chargeQuantity > 0 and not force or roomForReload <= 0:
            return
        if not uicore.layer.shipui:
            return
        self.dogmaLocation.LoadAmmoTypeToModule(self.moduleinfo.itemID, chargeTypeID)

    def CheckOverload(self):
        if not self or self.destroyed:
            return
        isActive = False
        hasOverloadEffect = False
        if not HasAttrs(self, 'moduleinfo', 'effects'):
            return
        for key in self.moduleinfo.effects.iterkeys():
            effect = self.moduleinfo.effects[key]
            if effect.effectCategory == const.dgmEffOverload:
                if effect.isActive:
                    isActive = True
                hasOverloadEffect = True

        if hasOverloadEffect:
            self.sr.overloadButton.top = 5
            if self.online:
                if isActive:
                    self.sr.overloadButton.LoadTexture('res:/UI/Texture/classes/ShipUI/slotOverloadOn.png')
                    self.sr.overloadButton.hint = localization.GetByLabel('UI/Inflight/Overload/TurnOffOverload')
                else:
                    self.sr.overloadButton.LoadTexture('res:/UI/Texture/classes/ShipUI/slotOverloadOff.png')
                    self.sr.overloadButton.hint = localization.GetByLabel('UI/Inflight/Overload/TurnOnOverload')
                self.sr.overloadButton.state = uiconst.UI_NORMAL
            else:
                self.sr.overloadButton.LoadTexture('res:/UI/Texture/classes/ShipUI/slotOverloadDisabled.png')
                self.sr.overloadButton.state = uiconst.UI_DISABLED
        else:
            self.sr.overloadButton.top = 6
            self.sr.overloadButton.LoadTexture('res:/UI/Texture/classes/ShipUI/slotOverloadDisabled.png')
            self.sr.overloadButton.state = uiconst.UI_DISABLED

    def CheckMasterSlave(self):
        if not self or self.destroyed:
            return
        itemID = self.moduleinfo.itemID
        slaves = self.dogmaLocation.GetSlaveModules(itemID, session.shipid)
        if slaves:
            if self.sr.stackParent is None:
                stackParent = Container(parent=self, name='stackParent', pos=(6, 27, 12, 10), align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, idx=0)
                self.sr.stacklabel = eveLabel.Label(text=len(slaves) + 1, parent=stackParent, fontsize=9, letterspace=1, left=5, top=0, width=30, state=uiconst.UI_DISABLED, shadowOffset=(0, 0), color=(1.0, 1.0, 1.0, 1))
                underlay = Sprite(parent=stackParent, name='underlay', pos=(0, 0, 0, 0), align=uiconst.TOALL, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/ShipUI/slotStackUnderlay.png', color=(0.51, 0.0, 0.0, 1.0))
                self.sr.stackParent = stackParent
            else:
                self.sr.stackParent.state = uiconst.UI_DISABLED
                self.sr.stacklabel.text = len(slaves) + 1
        elif self.sr.stackParent:
            self.sr.stackParent.state = uiconst.UI_HIDDEN

    def CheckOnline(self, sound = 0):
        if not self or self.destroyed:
            return
        if not HasAttrs(self, 'moduleinfo', 'effects'):
            return
        for key in self.moduleinfo.effects.keys():
            effect = self.moduleinfo.effects[key]
            if effect.effectName == 'online':
                if effect.isActive:
                    self.ShowOnline()
                    if sound:
                        PlaySound(SOUND_MODULE_ONLINE)
                else:
                    self.ShowOffline()
                return

    def ChangeOnline(self, on = 1):
        uthread.new(self._ChangeOnline, on)

    def _ChangeOnline(self, on):
        masterID = self.dogmaLocation.IsInWeaponBank(session.shipid, self.moduleinfo.itemID)
        if masterID:
            if not on:
                ret = eve.Message('CustomQuestion', {'header': 'OFFLINE',
                 'question': "When offlining this module you will destroy the weapons bank it's in. Are you sure you want to offline it? "}, uiconst.YESNO)
                if ret != uiconst.ID_YES:
                    return
        elif not on and eve.Message('PutOffline', {}, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
            return
        for key in self.moduleinfo.effects.keys():
            effect = self.moduleinfo.effects[key]
            if effect.effectName == 'online':
                if on:
                    effect.Activate()
                else:
                    self.ShowOffline(1)
                    try:
                        effect.Deactivate()
                    except UserError:
                        self.ShowOnline()
                        raise

                return

    def ShowOverload(self, on):
        self.CheckOverload()

    def ShowOnline(self):
        self.isMaster = 0
        if self.AreModulesOffline():
            self.ShowOffline()
            return
        self.online = True
        if self.grey:
            self.icon.SetAlpha(0.1)
        else:
            self.icon.SetAlpha(1.0)
        self.CheckOverload()

    def ShowOffline(self, ping = 0):
        self.online = False
        if self.grey:
            self.icon.SetAlpha(0.1)
        else:
            self.icon.SetAlpha(0.25)
        if ping:
            PlaySound(SOUND_MODULE_OFFLINE)
        self.CheckOverload()
        self.isInActiveState = True

    def AreModulesOffline(self):
        slaves = self.dogmaLocation.GetSlaveModules(self.moduleinfo.itemID, session.shipid)
        if not slaves:
            return False
        self.isMaster = 1
        onlineEffect = self.stateManager.GetEffect(self.moduleinfo.itemID, 'online')
        if onlineEffect is None or not onlineEffect.isActive:
            return True
        for slave in slaves:
            onlineEffect = self.stateManager.GetEffect(slave, 'online')
            if onlineEffect is None or not onlineEffect.isActive:
                return True

        return False

    def IsEffectRepeatable(self, effect, activatibleKnown = 0):
        if activatibleKnown or self.IsEffectActivatible(effect):
            if not effect.item.disallowRepeatingActivation:
                return effect.durationAttributeID is not None
        return 0

    def IsEffectActivatible(self, effect):
        return effect.isDefault and effect.effectName != 'online' and effect.effectCategory in (const.dgmEffActivation, const.dgmEffTarget)

    def SetRepeat(self, num):
        settings.char.autorepeat.Set(self.moduleinfo.itemID, num)
        self.autorepeat = num

    def GetDefaultEffect(self):
        if not self or self.destroyed:
            return
        if self.sr is None or self.moduleinfo is None or not self.stateManager.IsItemLoaded(self.moduleinfo.itemID):
            return
        for key in self.moduleinfo.effects.iterkeys():
            effect = self.moduleinfo.effects[key]
            if self.IsEffectActivatible(effect):
                return effect

    def OnClick(self, *args):
        if not self or self.IsBeingDragged() or not self.isInActiveState:
            return
        PlaySound(uiconst.SOUND_BUTTON_CLICK)
        if uicore.uilib.Key(uiconst.VK_SHIFT):
            self.ToggleOverload()
            return
        ctrlRepeat = 0
        if uicore.uilib.Key(uiconst.VK_CONTROL):
            ctrlRepeat = 1000
        self.Click(ctrlRepeat)

    def Click(self, ctrlRepeat = 0):
        if self.stateManager.IsModuleReloading(self.moduleinfo.itemID):
            return
        if self.waitingForActiveTarget:
            sm.GetService('target').CancelTargetOrder(self)
            self.waitingForActiveTarget = 0
        else:
            if self.def_effect is None:
                log.LogWarn('No default Effect available for this moduletypeID:', self.moduleinfo.typeID)
                eve.Message('CustomNotify', {'notify': localization.GetByLabel('UI/Inflight/ModuleRacks/TryingToActivatePassiveModule')})
                return
            if not self.online:
                if getattr(self, 'isMaster', None):
                    eve.Message('ClickOffllineGroup')
                else:
                    eve.Message('ClickOffllineModule')
                return
            if self.IsModuleActivatingInGodma():
                return
            if self.def_effect.isActive:
                self.DeactivateEffect(self.def_effect)
            elif not self.effect_activating:
                self.activationTimer = timerstuff.AutoTimer(500, self.ActivateEffectTimer)
                self.effect_activating = 1
                self.ActivateEffect(self.def_effect, ctrlRepeat=ctrlRepeat)

    def ActivateModule(self):
        if self.def_effect and not self.def_effect.isActive and not self.effect_activating:
            self.Click()

    def DeactivateModule(self):
        if self.def_effect and self.def_effect.isActive:
            self.Click()

    def ActivateEffectTimer(self, *args):
        self.effect_activating = 0
        self.activationTimer = None

    def OnEndDrag(self, *args):
        uthread.new(uicore.layer.shipui.ResetSwapMode)

    def GetDragData(self, *args):
        if settings.user.ui.Get('lockModules', 0):
            return []
        if self.charge:
            fakeNode = uix.GetItemData(self.charge, 'icons')
            fakeNode.isCharge = 1
        else:
            fakeNode = uix.GetItemData(self.moduleinfo, 'icons')
            fakeNode.isCharge = 0
        fakeNode.__guid__ = 'xtriui.ShipUIModule'
        fakeNode.slotFlag = self.moduleinfo.flagID
        uicore.layer.shipui.StartDragMode(self.moduleinfo.itemID, self.moduleinfo.typeID)
        return [fakeNode]

    def OnDropData(self, dragObj, nodes):
        log.LogInfo('Module.OnDropData', self.id)
        if not IsDocked() and dragObj.__guid__ == 'listentry.InvAssetItem':
            return
        flag1 = self.moduleinfo.flagID
        flag2 = None
        for node in nodes:
            if node.Get('__guid__', None) == 'xtriui.ShipUIModule':
                flag2 = node.slotFlag
                break

        if flag1 == flag2:
            return
        if flag2 is not None:
            uicore.layer.shipui.ChangeSlots(flag1, flag2)
            return
        chargeTypeID = None
        chargeItems = []
        for node in nodes:
            if not hasattr(node, 'rec'):
                return
            chargeItem = node.rec
            if not isinstance(chargeItem.itemID, numbers.Integral):
                return
            if not hasattr(chargeItem, 'categoryID'):
                return
            if chargeItem.categoryID != const.categoryCharge:
                continue
            if chargeTypeID is None:
                chargeTypeID = chargeItem.typeID
            if chargeItem.typeID == chargeTypeID:
                chargeItems.append(chargeItem)

        if len(chargeItems) > 0:
            self.dogmaLocation.DropLoadChargeToModule(self.moduleinfo.itemID, chargeTypeID, chargeItems=chargeItems)

    def OnMouseHover(self, *args):
        if uicore.uilib.Key(uiconst.VK_SHIFT):
            self.OverloadHiliteOn()
        else:
            self.OverloadHiliteOff()

    def OnMouseDown(self, *args):
        Container.OnMouseDown(self, *args)
        log.LogInfo('Module.OnMouseDown', self.id)
        if getattr(self, 'downTop', None) is not None or not self.isInActiveState or self.def_effect is None:
            return
        if not uicore.uilib.Key(uiconst.VK_SHIFT) and self.IsModuleActivatingInGodma():
            return
        self.downTop = self.parent.top
        self.parent.top += 2

    def IsModuleActivatingInGodma(self):
        effectName = self.def_effect.effectName
        isActivating = self.stateManager.IsModuleActivating(self.moduleinfo.itemID, effectName)
        if isActivating:
            return True
        return False

    def OnMouseUp(self, *args):
        Container.OnMouseUp(self, *args)
        if self.destroyed:
            return
        log.LogInfo('Module.OnMouseUp', self.id)
        if getattr(self, 'downTop', None) is not None:
            self.parent.top = self.downTop
            self.downTop = None
        if len(args) > 0 and args[0] == uiconst.MOUSERIGHT and getattr(uicore.layer.hint, 'moduleButtonHint', None):
            uicore.layer.hint.moduleButtonHint.FadeOpacity(0.0)

    def OnMouseEnter(self, *args):
        uthread.pool('ShipMobuleButton::MouseEnter', self.MouseEnter)

    def MouseEnter(self, *args):
        if self.destroyed or sm.GetService('godma').GetItem(self.moduleinfo.itemID) is None:
            return
        PlaySound(uiconst.SOUND_BUTTON_HOVER)
        if uicore.uilib.Key(uiconst.VK_SHIFT):
            self.OverloadHiliteOn()
        self.SetHilite()
        tacticalSvc = sm.GetService('tactical')
        bracketMgr = sm.GetService('bracket')
        maxRange, falloffDist, bombRadius, _ = tacticalSvc.FindMaxRange(self.moduleinfo, self.charge)
        if maxRange > 0:
            bracketMgr.ShowModuleRange(self.moduleinfo.itemID, maxRange + falloffDist)
            bracketMgr.ShowHairlinesForModule(self.moduleinfo.itemID)
        log.LogInfo('Module.OnMouseEnter', self.id)
        if settings.user.ui.Get('showModuleTooltips', 1):
            if self.tooltipPanelClassInfo is None:
                self.tooltipPanelClassInfo = TooltipModuleWrapper()
        else:
            self.tooltipPanelClassInfo = None
        uthread.new(tacticalSvc.ShowModuleRange, self.moduleinfo, self.charge)

    def GetTooltipDelay(self):
        return settings.user.ui.Get(TOOLTIP_SETTINGS_MODULE, TOOLTIP_DELAY_MODULE)

    def OnMouseExit(self, *args):
        self.RemoveHilite()
        sm.GetService('bracket').StopShowingModuleRange(self.moduleinfo.itemID)
        self.OverloadHiliteOff()
        log.LogInfo('Module.OnMouseExit', self.id)
        uthread.new(sm.GetService('tactical').ClearModuleRange)
        self.OnMouseUp(None)

    def UpdateInfo_TimedCall(self):
        self.UpdateInfo()

    def UpdateInfo(self):
        if self.destroyed or not self.moduleButtonHint or self.moduleButtonHint.destroyed:
            self.moduleButtonHint = None
            self.updateTimer = None
            return False
        if not self.stateManager.IsItemLoaded(self.id):
            return False
        chargeItemID = None
        if self.charge:
            chargeItemID = self.charge.itemID
        self.moduleButtonHint.UpdateAllInfo(self.moduleinfo.itemID, chargeItemID)
        requiredSafetyLevel = self.GetRequiredSafetyLevel()
        if self.crimewatchSvc.CheckUnsafe(requiredSafetyLevel):
            self.moduleButtonHint.SetSafetyWarning(requiredSafetyLevel)
        else:
            self.moduleButtonHint.RemoveSafetyWarning()
        return True

    def GetSafetyWarning(self):
        requiredSafetyLevel = self.GetRequiredSafetyLevel()
        if self.crimewatchSvc.CheckUnsafe(requiredSafetyLevel):
            return requiredSafetyLevel
        else:
            return None

    def GetModuleDamage(self):
        return uicore.layer.shipui.controller.GetModuleGroupDamage(self.moduleinfo.itemID)

    def GetNumUnitsToRepair(self):
        return uicore.layer.shipui.controller.GetNumUnitsToRepairModuleBank(self.moduleinfo.typeID, self.moduleinfo.itemID)

    def GetDamagedModulesAndRepairCost(self):
        return uicore.layer.shipui.controller.GetDamagedModulesAndRepairCost()

    def GetAllRepairingModules(self):
        return uicore.layer.shipui.controller.GetAllRepairingModules()

    def GetAccuracy(self, targetID = None):
        if self is None or self.destroyed:
            return

    def SetActive(self):
        self.InitGlow()
        self.sr.glow.state = uiconst.UI_DISABLED
        sm.GetService('ui').BlinkSpriteA(self.sr.glow, 0.75, 1000, None, passColor=0)
        self.effect_activating = 0
        self.activationTimer = None
        self.isInActiveState = True
        self.ActivateRamps()

    def SetDeactivating(self):
        self.isDeactivating = True
        if self.sr.glow:
            self.sr.glow.state = uiconst.UI_HIDDEN
        self.InitBusyState()
        self.sr.busy.state = uiconst.UI_DISABLED
        sm.GetService('ui').BlinkSpriteA(self.sr.busy, 0.75, 1000, None, passColor=0)
        self.isInActiveState = False
        self.DeActivateRamps()

    def SetIdle(self):
        self.isDeactivating = False
        if self.sr.glow:
            self.sr.glow.state = uiconst.UI_HIDDEN
            sm.GetService('ui').StopBlink(self.sr.glow)
        if self.sr.busy:
            self.sr.busy.state = uiconst.UI_HIDDEN
            sm.GetService('ui').StopBlink(self.sr.busy)
        self.isInActiveState = True
        self.IdleRamps()
        self.TryStartCooldownTimers()

    def SetRepairing(self, startTime = None):
        self.InitGlow()
        self.sr.glow.state = uiconst.UI_DISABLED
        self.sr.glow.SetRGBA(1, 1, 1, 1)
        sm.GetService('ui').BlinkSpriteA(self.sr.glow, 0.9, 2500, None, passColor=0)
        self.isInActiveState = True
        uthread.new(self.ShowRepairLeft, startTime)

    def RemoveRepairing(self):
        if self.sr.glow:
            sm.GetService('ui').StopBlink(self.sr.glow)
            self.sr.glow.SetRGBA(*GLOWCOLOR)
            self.sr.glow.state = uiconst.UI_HIDDEN
        if self.sr.damageState:
            self.sr.damageState.StopRepair()

    def SetHilite(self):
        self.InitHilite()
        self.sr.hilite.display = True
        requiredSafetyLevel = self.GetRequiredSafetyLevel()
        if self.crimewatchSvc.CheckUnsafe(requiredSafetyLevel):
            self.InitSafetyGlow()
            if requiredSafetyLevel == const.shipSafetyLevelNone:
                color = crimewatchConst.Colors.Criminal
            else:
                color = crimewatchConst.Colors.Suspect
            self.sr.safetyGlow.SetRGBA(*color.GetRGBA())
            self.sr.safetyGlow.display = True

    def GetRequiredSafetyLevel(self):
        requiredSafetyLevel = self.crimewatchSvc.GetRequiredSafetyLevelForEffect(self.GetRelevantEffect(), targetID=None)
        return requiredSafetyLevel

    def RemoveHilite(self):
        if self.sr.hilite:
            self.sr.hilite.display = False
        if self.sr.safetyGlow:
            self.sr.safetyGlow.display = False

    def InitSafetyGlow(self):
        if self.sr.safetyGlow is None:
            self.sr.safetyGlow = Sprite(parent=self.parent, name='safetyGlow', padding=2, align=uiconst.TOALL, state=uiconst.UI_HIDDEN, texturePath='res:/UI/Texture/classes/ShipUI/slotGlow.png', color=crimewatchConst.Colors.Yellow.GetRGBA())

    def InitGlow(self):
        if self.sr.glow is None:
            self.sr.glow = Sprite(parent=self.parent, name='glow', padding=2, align=uiconst.TOALL, state=uiconst.UI_HIDDEN, texturePath='res:/UI/Texture/classes/ShipUI/slotGlow.png', color=GLOWCOLOR)

    def InitBusyState(self):
        if self.sr.busy is None:
            self.sr.busy = Sprite(parent=self.parent, name='busy', padding=2, align=uiconst.TOALL, state=uiconst.UI_HIDDEN, texturePath='res:/UI/Texture/classes/ShipUI/slotGlow.png', color=BUSYCOLOR)

    def InitHilite(self):
        if self.sr.hilite is None:
            if getattr(self.parent, 'mainShape', None) is not None:
                idx = max(-1, self.parent.mainShape.GetOrder() - 1)
            else:
                idx = -1
            self.sr.hilite = Sprite(parent=self.parent, name='hilite', padding=(10, 10, 10, 10), align=uiconst.TOALL, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/ShipUI/slotHilite.png', blendMode=trinity.TR2_SBM_ADDX2, idx=idx)
            self.sr.hilite.display = False

    def OverloadHiliteOn(self):
        self.sr.overloadButton.SetAlpha(1.5)

    def OverloadHiliteOff(self):
        self.sr.overloadButton.SetAlpha(1.0)

    def GetEffectByName(self, effectName):
        for key in self.moduleinfo.effects.iterkeys():
            effect = self.moduleinfo.effects[key]
            if effect.effectName == effectName:
                return effect

    def Update(self, effectState):
        if not self or self.destroyed:
            return
        if not self.stateManager.IsItemLoaded(self.id):
            return
        if self.def_effect and effectState.effectName == self.def_effect.effectName:
            if effectState.start:
                self.SetActive()
            else:
                self.SetIdle()
        effect = self.GetEffectByName(effectState.effectName)
        if effect and effect.effectCategory == const.dgmEffOverload:
            self.ShowOverload(effect.isActive)
        if effectState.effectName == 'online':
            if effectState.active:
                self.ShowOnline()
            else:
                self.ShowOffline()
        if effect.effectCategory in [const.dgmEffTarget, const.dgmEffActivation, const.dgmEffArea] and effect.effectID != const.effectOnline:
            if not effectState.active and self.quantity == 0:
                self.AutoReload()
        self.UpdateInfo()

    def GetRelevantEffect(self):
        if self.def_effect and (self.def_effect.effectName == 'useMissiles' or self.def_effect.effectName == 'warpDisruptSphere' and self.charge is not None):
            if self.charge is None:
                return
            effect = sm.GetService('godma').GetStateManager().GetDefaultEffect(self.charge.typeID)
        else:
            effect = self.def_effect
        return effect

    def ActivateEffect(self, effect, targetID = None, ctrlRepeat = 0):
        if self.charge and self.charge.typeID in const.orbitalStrikeAmmo:
            return False
        relevantEffect = self.GetRelevantEffect()
        if relevantEffect is None:
            typeID, _ = self.GetModuleType()
            raise UserError('NoCharges', {'launcher': (const.UE_TYPEID, typeID)})
        if relevantEffect and not targetID and relevantEffect.effectCategory == 2:
            targetID = sm.GetService('target').GetActiveTargetID()
            if not targetID:
                sm.GetService('target').OrderTarget(self)
                uthread.new(self.BlinkIcon)
                self.waitingForActiveTarget = 1
                return
        if self.sr.Get('moduleinfo'):
            for key in self.moduleinfo.effects.iterkeys():
                checkeffect = self.moduleinfo.effects[key]
                if checkeffect.effectName == 'online':
                    if not checkeffect.isActive:
                        self._ChangeOnline(1)
                    break

        if self.def_effect:
            if relevantEffect.isOffensive:
                if not sm.GetService('consider').DoAttackConfirmations(targetID, relevantEffect):
                    return
            repeats = ctrlRepeat or self.autorepeat
            if not self.IsEffectRepeatable(self.def_effect, 1):
                repeats = 0
            if not self.charge:
                self.stateManager.ChangeAmmoTypeForModule(self.moduleinfo.itemID, None)
            targetPointCount = self.moduleinfo.isPointTargeted
            if targetPointCount:
                eveCommands = sm.GetService('cmd')
                eveCommands.CmdAimWeapon(self.moduleinfo.itemID, self.def_effect, targetPointCount)
                return
            try:
                self.def_effect.Activate(targetID, repeats)
            except UserError as e:
                if e.msg == 'ModuleReactivationDelayed2':
                    self.SetReactivationTime(e.dict)
                raise

            sm.ScatterEvent('OnClientEvent_ActivateModule', self.def_effect.effectID)

    def DeactivateEffect(self, effect):
        self.SetDeactivating()
        try:
            effect.Deactivate()
            sm.ScatterEvent('OnClientEvent_DeactivateModule', self.def_effect.effectID)
        except UserError as e:
            if e.msg == 'EffectStillActive':
                if not self.isPendingUnlockForDeactivate:
                    self.isPendingUnlockForDeactivate = True
                    uthread.new(self.DelayButtonUnlockForDeactivate, max(0, e.dict['timeLeft']))
            raise

    def SetReactivationTime(self, errorDict):
        try:
            timeSinceLastStop = errorDict['timeSinceLastStop']
            itemID = errorDict['itemID']
            cooldownTimes = self.stateManager.GetCooldownTimes(itemID)
            if cooldownTimes:
                return
            startTime = blue.os.GetSimTime() - timeSinceLastStop * const.MSEC
            if startTime < 0:
                return
            self.stateManager.RecordLastStopTime(itemID, startTime)
            self.TryStartCooldownTimers()
        except Exception as e:
            pass

    def DelayButtonUnlockForDeactivate(self, sleepTimeBlue):
        blue.pyos.synchro.SleepSim(sleepTimeBlue / const.MSEC)
        self.isInActiveState = True
        self.isPendingUnlockForDeactivate = False

    def OnStateChange(self, itemID, flag, isTrue, *args):
        if self and isTrue and flag == state.activeTarget and self.waitingForActiveTarget:
            self.waitingForActiveTarget = 0
            self.ActivateEffect(self.def_effect, itemID)
            sm.GetService('target').CancelTargetOrder(self)

    def GetModuleType(self):
        return (self.moduleinfo.typeID, self.moduleinfo.itemID)

    def ActivateRamps(self):
        if not self or self.destroyed:
            return
        if self.ramp_active:
            self.UpdateRamps()
            return
        self.DoActivateRamps()

    def DeActivateRamps(self):
        self.UpdateRamps()

    def IdleRamps(self):
        self.ramp_active = False
        if not uicore.layer.shipui:
            return
        moduleID = self.moduleinfo.itemID
        rampTimers = uicore.layer.shipui.sr.rampTimers
        if rampTimers.has_key(moduleID):
            del rampTimers[moduleID]
        if self.sr.ramps:
            self.sr.ramps.display = False

    def UpdateRamps(self):
        self.DoActivateRamps()

    def DoActivateRamps(self):
        if self.ramp_active:
            return
        uthread.new(self.DoActivateRampsThread)

    def InitRamps(self):
        if self.sr.ramps and not self.sr.ramps.destroyed:
            return
        self.sr.ramps = ShipModuleButtonRamps(parent=self.parent, idx=OVERLOADBTN_INDEX + 1)

    def InitReactivationRamps(self):
        if self.sr.reactivationRamps and not self.sr.reactivationRamps.destroyed:
            return
        self.sr.reactivationRamps = ShipModuleReactivationTimer(parent=self.parent, idx=-1)

    def DoActivateRampsThread(self):
        if not self or self.destroyed:
            return
        (firstActivation, startTime), durationInMilliseconds = self.GetEffectTiming()
        if durationInMilliseconds <= 0:
            return
        now = blue.os.GetSimTime()
        if firstActivation:
            startTimeAdjustment = now - startTime
            if startTimeAdjustment > const.SEC:
                startTimeAdjustment = 0
            correctionTimeMS = durationInMilliseconds / 2
            adjustmentDecayPerSec = float(-startTimeAdjustment) / (correctionTimeMS / 1000)
        else:
            startTimeAdjustment = 0
            correctionTimeMS = 0
        self.ramp_active = True
        self.InitRamps()
        self.sr.ramps.display = True
        while self and not self.destroyed and self.ramp_active and durationInMilliseconds:
            newNow = blue.os.GetSimTime()
            deltaTime = newNow - now
            now = newNow
            if correctionTimeMS != 0:
                deltaMS = min(deltaTime / const.MSEC, correctionTimeMS)
                startTimeAdjustment += long(adjustmentDecayPerSec * (float(deltaMS) / 1000))
                correctionTimeMS -= deltaMS
            else:
                startTimeAdjustment = 0
            portionDone = blue.os.TimeDiffInMs(startTime + startTimeAdjustment, now) / durationInMilliseconds
            if portionDone > 1:
                iterations = int(portionDone)
                startTime += long(durationInMilliseconds * iterations * const.MSEC)
                _, durationInMilliseconds = self.GetEffectTiming()
                try:
                    uicore.layer.shipui.sr.rampTimers[self.moduleinfo.itemID] = (False, startTime)
                except AttributeError:
                    pass

                portionDone -= iterations
                if self.InLimboState():
                    self.IdleRamps()
                    sm.ScatterEvent('OnClientEvent_DeactivateModule', self.def_effect.effectID)
                    break
            self.sr.ramps.SetRampValues(portionDone)
            blue.pyos.synchro.Yield()

    def InLimboState(self):
        for each in ['waitingForActiveTarget', 'reloadingAmmo', 'isDeactivating']:
            if getattr(self, each, False):
                return True

        return False

    def GetRampStartTime(self):
        if not uicore.layer.shipui:
            return
        moduleID = self.moduleinfo.itemID
        rampTimers = uicore.layer.shipui.sr.rampTimers
        if moduleID not in rampTimers:
            now = blue.os.GetSimTime()
            default = getattr(self.def_effect, 'startTime', now) or now
            rampTimers[moduleID] = (True, default)
        return rampTimers[moduleID]

    def ShowRepairLeft(self, startTime = None):
        if self.sr.damageState is None:
            return
        dmg = self.GetModuleDamage()
        rateOfRepair = self.stateManager.GetAttribute(session.charid, 'moduleRepairRate')
        repairTime = dmg / rateOfRepair
        repairTime = int(repairTime * const.MIN)
        if startTime is None:
            startTime = blue.os.GetSimTime()
        hp = self.dogmaLocation.GetAttributeValue(self.moduleinfo.itemID, const.attributeHp)
        self.sr.damageState.AnimateRepair(dmg, hp, repairTime, startTime)

    def ShowReloadLeft(self, reloadTime, startTime = None):
        if startTime is None:
            startTime = blue.os.GetSimTime()
        reloadTime = int(reloadTime * const.MSEC)
        if self.sr.reactivationRamps and self.sr.reactivationRamps.endTime > startTime + reloadTime:
            return
        self.InitRamps()
        self.sr.ramps.display = True
        self.sr.ramps.AnimateReload(startTime, reloadTime)

    def ShowReactivationLeft(self, reactivationTime, startTime = None):
        self.InitReactivationRamps()
        reactivationTime = int(reactivationTime * const.MSEC)
        if startTime is None:
            startTime = blue.os.GetSimTime()
        self.sr.reactivationRamps.AnimateTimer(startTime, reactivationTime)

    def GetEffectTiming(self):
        rampStartTime = self.GetRampStartTime()
        durationInMilliseconds = 0.0
        durationAttributeID = getattr(self.def_effect, 'durationAttributeID', None)
        attribute = dogma.data.get_attribute(durationAttributeID) if durationAttributeID is not None else None
        item = self.stateManager.GetItem(self.def_effect.itemID)
        if item is None:
            return (0, 0.0)
        if attribute:
            durationInMilliseconds = self.stateManager.GetAttribute(self.def_effect.itemID, attribute.name)
        if not durationInMilliseconds:
            durationInMilliseconds = getattr(self.def_effect, 'duration', 0.0)
        return (rampStartTime, durationInMilliseconds)
