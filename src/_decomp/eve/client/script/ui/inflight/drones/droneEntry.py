#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\drones\droneEntry.py
import carbonui.const as uiconst
import eveicon
import evetypes
import localization
import mathext
import trinity
import uthread
import uthread2
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui import TextColor, uiconst
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from carbonui.util.bunch import Bunch
from carbonui.util.color import Color
from carbonui.util.various_unsorted import IsUnder
from eve.client.script.environment import invControllers
from eve.client.script.parklife import states as state
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.entries.generic import Generic
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.control.itemIcon import ItemIcon
from eve.client.script.ui.inflight.drones import droneSignals, dronesDragData
from eve.client.script.ui.inflight.drones.buttonSeperatorLine import ButtonSeperatorLine
from eve.client.script.ui.inflight.drones.droneSettings import drones_view_mode_setting, VIEW_MODE_ICONS, drones_view_mode_compact_setting
from eve.client.script.ui.inflight.drones.dronesConst import DRONE_STATES, COLOR_BY_STATE, DRONESTATE_INBAY, DRONESTATE_INSPACE, damageIconInfo, DRONE_STATES_TEXTURES
from eve.client.script.ui.inflight.drones.dronesDragData import DroneEntryInSpaceDragData, DroneEntryInBayDragData, HasInBayDroneIDs, HasInSpaceDroneIDs
from eve.client.script.ui.inflight.drones.dronesUtil import IsDronesWindowCompact, GetPrimaryActionName
from eve.client.script.ui.inflight.shipHud import shipHudConst
from eve.client.script.ui.services.menuSvcExtras import droneFunctions
from eve.client.script.ui.shared.fittingScreen.droneTooltip import DroneTooltipWrapper
from eve.client.script.ui.util import uix
from eve.client.script.util import eveMisc
from eve.client.script.util.bubble import InBubble
from eveDrones.droneConst import DAMAGESTATE_NOT_READY
from eveInflight.damageStateValue import CalculateCurrentDamageStateValues
from eveservices.menu import GetMenuService
from localization import GetByLabel
from menu import MenuList, MenuLabel
HEALTH_GAUGE_HEIGHT = 4
ENTRY_HEIGHT = 24
ENTRY_HEIGHT_COMPACT = 22

class HealthGauge(Container):
    default_width = 32

    def ApplyAttributes(self, attributes):
        super(HealthGauge, self).ApplyAttributes(attributes)
        self.healthBar = Fill(parent=self, name='droneGaugeBar', align=uiconst.TOLEFT, color=shipHudConst.COLOR_HEALTH, blendMode=trinity.TR2_SBM_ADD)
        self.damageNeedle = Fill(name='damageNeedle', parent=self, align=uiconst.TOLEFT, width=2, color=eveColor.WHITE)
        Fill(parent=self, name='droneGaugeBarDmg', color=shipHudConst.COLOR_DAMAGE)

    def UpdateDamage(self, value):
        if value is None:
            return
        healthProp = round(value, 3)
        healthProp = mathext.clamp(healthProp, 0.0, 1.0)
        self.damageNeedle.display = healthProp > 0 and healthProp < 1.0
        self.healthBar.width = int(self.width * healthProp)


class DroneEntry(Generic):
    __guid__ = 'listentry.DroneEntry'
    isDragObject = True
    __notifyevents__ = ['OnStateChange', 'OnDroneStateChange2', 'OnDroneActivityChange']

    def OnMouseDown(self, *args):
        uthread.new(self.OnMouseDown_thread)

    def OnMouseDown_thread(self):
        selelectedDrones = self.sr.node.scroll.GetSelectedNodes(self.sr.node)
        droneState = self.sr.node.droneState
        displayLabel = self.sr.node.label
        if len(selelectedDrones) > 1:
            displayLabel += '<fontsize=14> + %s' % (len(selelectedDrones) - 1)
        if droneState == DRONESTATE_INBAY:
            nodesData = [ (drone.invItem, 0, None) for drone in selelectedDrones if drone.invItem is not None ]
            manyItemsData = Bunch(menuFunction=GetMenuService().InvItemMenu, itemData=nodesData, displayName='<b>%s</b>' % displayLabel)
        elif droneState == DRONESTATE_INSPACE:
            if len(selelectedDrones) > 1:
                nodesData = [ (drone.itemID,
                 drone.typeID,
                 drone.ownerID,
                 drone.locationID) for drone in selelectedDrones if drone.typeID ]
                manyItemsData = Bunch(menuFunction=GetMenuService().DroneMenu, itemData=nodesData, displayName='<b>%s</b>' % displayLabel)
            else:
                manyItemsData = None
        else:
            return
        GetMenuService().TryExpandActionMenu(itemID=self.sr.node.itemID, typeID=self.sr.node.typeID, clickedObject=self, manyItemsData=manyItemsData)

    def Startup(self, *args):
        super(DroneEntry, self).Startup(*args)
        sm.RegisterNotify(self)
        self.activityID = None
        self.activity = None
        mainCont = Container(name='mainCont', parent=self, idx=0)
        gaugesParent = ContainerAutoSize(name='gaugesParent', parent=mainCont, align=uiconst.TORIGHT, padright=8)
        self.buttonCont = ContainerAutoSize(name='buttonParent', parent=mainCont, align=uiconst.TORIGHT, state=uiconst.UI_HIDDEN, opacity=0.0, padRight=4)
        self.ConstructButtons()
        self.gaugesCont = ContainerAutoSize(name='gaugesContainer', parent=gaugesParent, align=uiconst.CENTERRIGHT, state=uiconst.UI_NORMAL, height=HEALTH_GAUGE_HEIGHT, opacity=0.05)
        self.gaugesCont.LoadTooltipPanel = self.LoadDamageGaugeTooltipPanel
        self.gaugesCont.DelegateEventsNotImplemented(self)
        self.ConstructGauges()
        tClip = Container(name='textClipper', parent=mainCont, state=uiconst.UI_PICKCHILDREN, clipChildren=1)
        self.sr.label.SetParent(tClip)
        self.tooltipPanelClassInfo = DroneTooltipWrapper()

    def ConstructButtons(self):
        pass

    def Load(self, node):
        preselected = node.selected
        selected, = sm.GetService('stateSvc').GetStates(node.itemID, [state.selected])
        node.selected = selected
        Generic.Load(self, node)
        self.sr.label.left = self.GetLabelLeft()
        self.sr.label.autoFadeSides = 16
        self.sr.label.rgba = TextColor.HIGHLIGHT
        self.sr.label.Update()
        if preselected and not node.selected:
            node.selected = 1
            node.scroll.UpdateSelection(node)
        if self.sr.node.droneState == DRONESTATE_INSPACE:
            self.UpdateState()
        uthread2.StartTasklet(self.UpdateDamageThread)

    def GetLabelLeft(self):
        return 4 + 8 * self.sr.node.sublevel

    def UpdateState(self, droneState = None):
        michelle = sm.GetService('michelle')
        droneRow = michelle.GetDroneState(self.sr.node.itemID)
        droneActivity = michelle.GetDroneActivity(self.sr.node.itemID)
        if droneActivity:
            self.activity, self.activityID = droneActivity
        if droneState is None and droneRow is not None:
            droneState = droneRow.activityState
        stateText = self._GetStateText(droneState)
        self.sr.label.text = '%s %s' % (self.sr.node.label, stateText)
        return droneState

    def GetDroneActivityDescription(self):
        if self.sr.node.droneState != DRONESTATE_INBAY and self.activityID and self.activity:
            activity = ''
            if self.activity == 'guard':
                activity = localization.GetByLabel('UI/Inflight/Drone/Guarding')
            elif self.activity == 'assist':
                activity = localization.GetByLabel('UI/Inflight/Drone/Assisting')
            return localization.GetByLabel('UI/Inflight/Drone/Activity', activity=activity, idInfo=cfg.eveowners.Get(self.activityID).name)

    def GetDroneStateDescription(self):
        michelle = sm.GetService('michelle')
        droneRow = michelle.GetDroneState(self.sr.node.itemID)
        if droneRow is None:
            return
        droneState = droneRow.activityState
        target = None
        if droneState in [const.entityCombat, const.entityEngage, const.entityMining]:
            targetID = droneRow.targetID
            targetTypeName = None
            pilotName = None
            if targetID:
                targetSlim = michelle.GetItem(targetID)
                if targetSlim:
                    if targetSlim.groupID == const.categoryShip:
                        pilotID = michelle.GetCharIDFromShipID(targetSlim.itemID)
                        if pilotID:
                            pilotName = cfg.eveowners.Get(pilotID).name
                    targetTypeName = uix.GetSlimItemName(targetSlim)
            if pilotName:
                target = pilotName
            elif targetTypeName:
                target = targetTypeName
            else:
                target = localization.GetByLabel('UI/Generic/Unknown')
        state = self._GetStateText(droneState)
        if target is not None:
            return u'{state} {target}'.format(state=state, target=target)
        else:
            return state

    def _GetStateText(self, droneState):
        stateText = localization.GetByLabel(DRONE_STATES.get(droneState, 'UI/Inflight/Drone/Incapacitated'))
        if droneState in COLOR_BY_STATE:
            stateText = '<color=%s>%s</color>' % (COLOR_BY_STATE[droneState], stateText)
        return stateText

    def GetHeight(self, node, width):
        node.height = ENTRY_HEIGHT_COMPACT if IsDronesWindowCompact() else ENTRY_HEIGHT
        return node.height

    def OnDroneStateChange2(self, droneID, oldActivityState, newActivityState):
        if self.sr.node and self.sr.node.droneState == DRONESTATE_INSPACE and droneID == self.sr.node.itemID:
            droneRow = sm.GetService('michelle').GetDroneState(self.sr.node.itemID)
            if droneRow:
                self.sr.node.controllerID = droneRow.controllerID
                self.sr.node.controllerOwnerID = droneRow.controllerOwnerID
                self.UpdateState(newActivityState)

    def OnDroneActivityChange(self, droneID, activityID, activity):
        if self.sr.node and self.sr.node.droneState in DRONESTATE_INSPACE and droneID == self.sr.node.itemID:
            self.activity = activity
            self.activityID = activityID
            self.UpdateState()

    def OnClick(self, *args):
        if self.sr.node:
            self.sr.node.scroll.SelectNode(self.sr.node)
            eve.Message('ListEntryClick')
            if not uicore.uilib.Key(uiconst.VK_CONTROL):
                if not uicore.uilib.Key(uiconst.VK_SHIFT):
                    sm.GetService('stateSvc').SetState(self.sr.node.itemID, state.selected, 1)
            else:
                sm.GetService('target').TryLockTarget(self.sr.node.itemID)

    def GetSelected(self):
        ids = []
        sel = self.sr.node.scroll.GetSelectedNodes(self.sr.node)
        for node in sel:
            if node.Get('typeID', None) is None:
                continue
            if evetypes.GetGroupID(node.typeID) == evetypes.GetGroupID(self.sr.node.typeID):
                ids.append(node.itemID)

        return ids

    def GetSelectedItems(self):
        items = []
        sel = self.sr.node.scroll.GetSelectedNodes(self.sr.node)
        for node in sel:
            items.append(node.invItem)

        return items

    def GetMenu(self):
        m = MenuList()
        if self.sr.node.customMenu:
            m += self.sr.node.customMenu(self.sr.node)
        if self.sr.node.droneState != DRONESTATE_INBAY:
            args = []
            selected = self.sr.node.scroll.GetSelectedNodes(self.sr.node)
            for node in selected:
                if node.Get('typeID', None) is None:
                    continue
                args.append((node.itemID,
                 None,
                 None,
                 node.typeID,
                 None))

            m += GetMenuService().CelestialMenu(args)
        else:
            selected = self.GetSelectedItems()
            args = []
            for rec in selected:
                if rec is None:
                    continue
                args.append((rec, 0, 0))

            m += GetMenuService().InvItemMenu(args).filter([MenuLabel('UI/Inventory/ItemActions/BuyThisType'),
             MenuLabel('UI/Inventory/ItemActions/AddTypeToMarketQuickbar'),
             MenuLabel('UI/Inventory/ItemActions/ViewTypesMarketDetails'),
             MenuLabel('UI/Inventory/ItemActions/FindInContracts')])
        return m

    def SelectAll(self):
        self.sr.node.scroll.SelectAll()
        sel = self.GetSelected()
        if len(sel) > 1:
            sm.ScatterEvent('OnDronesSelected', sel)

    def ConstructGauges(self):
        self.gaugeStruct = HealthGauge(parent=self.gaugesCont, name='structGauge', align=uiconst.TOLEFT, padRight=2)
        self.gaugeArmor = HealthGauge(parent=self.gaugesCont, name='armorGauge', align=uiconst.TOLEFT, padRight=2)
        self.gaugeShield = HealthGauge(parent=self.gaugesCont, name='shieldGauge', align=uiconst.TOLEFT)

    def LoadDamageGaugeTooltipPanel(self, tooltipPanel, *args):
        tooltipPanel.LoadStandardSpacing()
        self._LoadTooltipPanel_thread(tooltipPanel)
        self.tooltipThread = AutoTimer(500, self._LoadTooltipPanel_thread, tooltipPanel)

    def _LoadTooltipPanel_thread(self, tooltipPanel):
        currentMouseOver = uicore.uilib.mouseOver
        if self.destroyed or currentMouseOver != self and not currentMouseOver.IsUnder(self):
            self.tooltipThread = None
            return
        tooltipPanel.Flush()
        dmg = self.GetDamageTuple()
        if dmg in (DAMAGESTATE_NOT_READY, None):
            return
        dmgList = []
        for eachLayerDmgPerc in dmg[:3]:
            layerDmg = eachLayerDmgPerc * 100
            layerDmg = int(round(layerDmg))
            layerDmg = mathext.clamp(layerDmg, 0.0, 100)
            layerDmgText = localization.GetByLabel('UI/Common/Formatting/Percentage', percentage=layerDmg)
            dmgList.append(layerDmgText)

        dmgList.reverse()
        iconCont = Container(name='iconCont', parent=tooltipPanel, align=uiconst.CENTER, height=16, width=120, padTop=4)
        textCont = Container(name='textCont', parent=tooltipPanel, align=uiconst.CENTER, height=16, width=120, padTop=2)
        for i in xrange(len(dmgList)):
            Sprite(name='healthBar', parent=Container(parent=iconCont, align=uiconst.TOLEFT, width=40, height=16), align=uiconst.CENTER, width=16, height=16, texturePath=damageIconInfo.get(i, None))
            EveLabelMedium(parent=Container(parent=textCont, align=uiconst.TOLEFT, height=16, width=40), align=uiconst.CENTER, text=dmgList[i])

    def GetDragData(self, *args):
        return [ self._GetDragData(node.itemID, node.typeID) for node in self.sr.node.scroll.GetSelectedNodes(self.sr.node) ]

    def _GetDragData(self):
        raise NotImplementedError

    def Close(self):
        self.tooltipThread = None
        super(DroneEntry, self).Close()

    def UpdateDamageThread(self):
        while not self.destroyed:
            self.UpdateDamage()
            uthread2.Sleep(1.0)

    def UpdateDamage(self):
        pass

    def HideDamageDisplay(self):
        self.UpdateDamageGauges(1, 1, 1)
        self.gaugesCont.opacity = 0.05

    def GetDamageTuple(self):
        pass

    def GetShipID(self):
        if self.sr.node:
            return self.sr.node.itemID

    def OnMouseEnter(self, *args):
        super(DroneEntry, self).OnMouseEnter(*args)
        if self.sr.node:
            sm.GetService('stateSvc').SetState(self.GetIdForItem(), state.mouseOver, 1)
        self.ShowButtonCont()
        uicore.uilib.RegisterForTriuiEvents(uiconst.UI_MOUSEENTER, self.OnGlobalMouseEnter)

    def OnGlobalMouseEnter(self, obj, *args):
        if obj and not (IsUnder(obj, self) or obj == self):
            self.HideButtonCont()
            return False
        else:
            return True

    def OnMouseExit(self, *args):
        Generic.OnMouseExit(self, *args)
        if self.sr.node:
            sm.GetService('stateSvc').SetState(self.GetIdForItem(), state.mouseOver, 0)

    def ShowButtonCont(self):
        self.buttonCont.Show()
        animations.FadeTo(self.buttonCont, self.buttonCont.opacity, 1.0, duration=0.1)

    def HideButtonCont(self):
        animations.FadeTo(self.buttonCont, self.buttonCont.opacity, 0.0, duration=0.1, callback=self.buttonCont.Hide)

    def GetIdForItem(self):
        return self.sr.node.itemID

    def Select(self, *args):
        Generic.Select(self, *args)
        self.sr.node.selected = True

    def OnStateChange(self, itemID, flag, isActive, *args):
        if self.sr.node.itemID != itemID:
            return
        if flag == state.mouseOver:
            if isActive:
                self.ShowHilite()
            else:
                self.HideHilite()
        elif flag == state.selected:
            if isActive:
                self.Select()
            else:
                self.sr.node.scroll.DeselectAll()

    def Deselect(self, *args):
        Generic.Deselect(self, *args)
        self.sr.node.selected = False

    def UpdateDamageGauges(self, shield, armor, struct):
        self.gaugesCont.opacity = 1.0
        self.gaugeShield.UpdateDamage(shield)
        self.gaugeArmor.UpdateDamage(armor)
        self.gaugeStruct.UpdateDamage(struct)


ICONSIZE = 32
buttonSize = 20

class DroneInBayEntry(DroneEntry):
    fetchingDamageValue = False

    def ConstructButtons(self):
        ButtonIcon(parent=self.buttonCont, align=uiconst.TORIGHT, width=buttonSize, iconSize=16, texturePath=eveicon.launch_drones, func=self.OnLaunchDronesButton, hint=GetByLabel('UI/Drones/LaunchDrone', numDrones=1), blendMode=trinity.TR2_SBM_ADD)

    def OnLaunchDronesButton(self, *args):
        droneInvItem = invControllers.ShipDroneBay().GetItem(self.sr.node.itemID)
        if droneInvItem:
            eveMisc.LaunchFromShip([droneInvItem])

    def UpdateDamage(self):
        dmg = self.GetDamageTuple()
        if dmg in (None, DAMAGESTATE_NOT_READY):
            self.HideDamageDisplay()
        else:
            self.UpdateDamageGauges(*dmg)

    def GetDamageTuple(self):
        if self.sr.node.damageState == DAMAGESTATE_NOT_READY:
            if not self.fetchingDamageValue:
                self.fetchingDamageValue = True
                itemID = self.GetShipID()
                uthread.new(self.SetDamageValue_thread, itemID)
            return DAMAGESTATE_NOT_READY
        if self.sr.node.damageState:
            damageInMichelleFormat = self.sr.node.damageState.GetInfoInMichelleFormat()
            time = self.sr.node.damageState.timestamp
            ret = CalculateCurrentDamageStateValues(damageInMichelleFormat, time)
            return ret

    def SetDamageValue_thread(self, droneID):
        self.sr.node.damageState = sm.GetService('tactical').GetInBayDroneDamageTracker().GetDamageStateForDrone(droneID)
        self.fetchingDamageValue = False
        self.UpdateDamage()

    def OnDragEnter(self, dragSource, dragData):
        super(DroneInBayEntry, self).OnDragEnter(dragSource, dragData)
        if HasInSpaceDroneIDs(dragData):
            droneSignals.on_in_bay_entry_drag_enter()

    def _GetDragData(self, itemID, typeID):
        return DroneEntryInBayDragData(itemID, typeID)

    def OnDropData(self, dragSource, dragData):
        droneIDs = dronesDragData.GetInSpaceDroneIDs(dragData)
        if droneIDs:
            droneFunctions.ReturnToDroneBay(droneIDs)


def IsIconsViewMode():
    if IsDronesWindowCompact():
        return drones_view_mode_compact_setting.is_equal(VIEW_MODE_ICONS)
    else:
        return drones_view_mode_setting.is_equal(VIEW_MODE_ICONS)


class DroneInSpaceEntry(DroneEntry):
    STATE_SPRITE_PADDING = 20

    def Startup(self, *args):
        super(DroneInSpaceEntry, self).Startup(*args)
        self.stateSprite = Sprite(name='stateSprite', parent=self, align=uiconst.CENTERLEFT, pos=(2, 0, 16, 16))
        if IsIconsViewMode():
            self.icon = ItemIcon(parent=self, align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED, pos=(0,
             0,
             ICONSIZE,
             ICONSIZE))

    def Load(self, node):
        super(DroneInSpaceEntry, self).Load(node)
        normalLabelLeft = super(DroneInSpaceEntry, self).GetLabelLeft()
        if IsIconsViewMode():
            self.icon.SetTypeID(self.sr.node.typeID)
            self.icon.left = normalLabelLeft + self.STATE_SPRITE_PADDING
        self.stateSprite.left = normalLabelLeft

    def GetHeight(self, *args):
        if IsIconsViewMode():
            if IsDronesWindowCompact():
                return ICONSIZE + 4
            return ICONSIZE + 8
        elif IsDronesWindowCompact():
            return ENTRY_HEIGHT_COMPACT
        else:
            return ENTRY_HEIGHT

    def GetLabelLeft(self):
        labelLeft = super(DroneInSpaceEntry, self).GetLabelLeft() + self.STATE_SPRITE_PADDING
        if IsIconsViewMode():
            labelLeft = labelLeft + ICONSIZE + 4
        return labelLeft

    def ConstructButtons(self):
        ButtonIcon(parent=self.buttonCont, align=uiconst.TORIGHT, width=buttonSize, iconSize=16, texturePath=eveicon.recall_drones, func=self.OnRecallDronesButton, hint=GetByLabel('UI/Drones/ReturnDroneToBay'), blendMode=trinity.TR2_SBM_ADD)
        ButtonSeperatorLine(parent=self.buttonCont, align=uiconst.TORIGHT)
        ButtonIcon(parent=self.buttonCont, align=uiconst.TORIGHT, width=buttonSize, iconSize=16, texturePath=eveicon.return_and_orbit, func=self.OnReturnAndOrbitButton, hint=GetByLabel('UI/Drones/ReturnDroneAndOrbit'), blendMode=trinity.TR2_SBM_ADD)
        ButtonIcon(parent=self.buttonCont, align=uiconst.TORIGHT, width=buttonSize, iconSize=16, texturePath=eveicon.engage_target, func=self.OnPrimaryActionButton, hint=GetPrimaryActionName(self.sr.node.typeID), blendMode=trinity.TR2_SBM_ADD)

    def OnReturnAndOrbitButton(self, *args):
        droneFunctions.ReturnAndOrbit([self.sr.node.itemID])

    def OnPrimaryActionButton(self, *args):
        droneFunctions.PerformPrimaryAction([(self.sr.node.itemID, self.sr.node.typeID)])

    def OnRecallDronesButton(self, *args):
        droneFunctions.ReturnToDroneBay([self.sr.node.itemID])

    def GetDamageTuple(self):
        bp = sm.GetService('michelle').GetBallpark()
        if bp is None:
            return
        return bp.GetDamageState(self.GetShipID())

    def UpdateDamage(self):
        if not InBubble(self.GetShipID()):
            self.HideDamageDisplay()
            return
        if not getattr(self.sr.node, 'slimItem', None):
            categoryID = evetypes.GetCategoryID(self.sr.node.typeID)
        else:
            slimItem = self.sr.node.slimItem()
            if not slimItem:
                self.HideDamageDisplay()
                return
            categoryID = slimItem.categoryID
        shipID = self.GetShipID()
        if shipID and categoryID in (const.categoryShip, const.categoryDrone):
            dmg = self.GetDamageTuple()
            if dmg is not None:
                self.UpdateDamageGauges(*dmg[:3])
            else:
                self.HideDamageDisplay()

    def OnDragEnter(self, dragSource, dragData):
        super(DroneInSpaceEntry, self).OnDragEnter(dragSource, dragData)
        if HasInBayDroneIDs(dragData):
            droneSignals.on_in_space_entry_drag_enter()

    def _GetDragData(self, itemID, typeID):
        return DroneEntryInSpaceDragData(itemID, typeID)

    def OnDropData(self, dragSource, dragData):
        droneIDs = dronesDragData.GetInBayDroneIDs(dragData)
        if droneIDs:
            droneFunctions.LaunchDrones(droneIDs)
            droneSignals.on_drones_dropped_in_space()

    def UpdateState(self, droneState = None):
        droneState = super(DroneInSpaceEntry, self).UpdateState(droneState)
        texturePath = DRONE_STATES_TEXTURES.get(droneState, '')
        self.stateSprite.SetTexturePath(texturePath)
        stateLablePath = DRONE_STATES.get(droneState, None)
        stateText = localization.GetByLabel(stateLablePath) if stateLablePath else ''
        if droneState in COLOR_BY_STATE:
            colorHex = COLOR_BY_STATE[droneState]
            colorRGB = Color.HextoRGBA(colorHex)
        else:
            colorRGB = TextColor.NORMAL
        self.stateSprite.SetRGBA(*colorRGB)
        self.stateSprite.hint = stateText


class NoDroneInBayEntry(Generic):

    def OnDropData(self, dragObj, dragData):
        droneIDs = dronesDragData.GetInSpaceDroneIDs(dragData)
        if droneIDs:
            droneFunctions.ReturnToDroneBay(droneIDs)
            droneSignals.on_drones_dropped_to_bay()

    def OnDragEnter(self, dragSource, dragData):
        if dronesDragData.HasInSpaceDroneIDs(dragData):
            droneSignals.on_in_bay_entry_drag_enter()


class NoDroneInSpaceEntry(Generic):

    def OnDropData(self, dragObj, dragData):
        droneIDs = dronesDragData.GetInBayDroneIDs(dragData)
        if droneIDs:
            droneFunctions.LaunchDrones(droneIDs)
            droneSignals.on_drones_dropped_in_space()

    def OnDragEnter(self, dragSource, dragData):
        if dronesDragData.HasInBayDroneIDs(dragData):
            droneSignals.on_in_space_entry_drag_enter()
