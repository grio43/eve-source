#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\drone.py
import math
import blue
import dogma.data
import eve.client.script.ui.shared.pointerTool.pointerToolConst as pConst
import eve.common.script.mgt.entityConst as entities
import evetypes
import itertoolsext
import localization
import log
import mathext
import uthread
from carbon.client.script.util.misc import Uthreaded
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui import uiconst
from carbonui.control.button import Button
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.primitives.frame import Frame
from carbonui.primitives.line import Line
from carbonui.primitives.sprite import Sprite
from carbonui.services.setting import CharSettingBool
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from carbonui.util.bunch import Bunch
from carbonui.util.various_unsorted import SortListOfTuples, Transplant
from eve.client.script.parklife import states as state
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.entries.generic import Generic
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.control.eveScroll import Scroll
from eve.client.script.ui.control.listgroup import ListGroup as Group
from eve.client.script.ui.control.utilMenu import UtilMenu
from eve.client.script.ui.inflight import actionPanelDefaults
from eve.client.script.ui.inflight.actions import ActionPanel
from eve.client.script.ui.inflight.baseTacticalEntry import BaseTacticalEntry
from eve.client.script.ui.services.menuSvcExtras.droneFunctions import ReturnToDroneBay
from eve.client.script.ui.util import uix
from eve.client.script.ui.util.utilWindows import NamePopup
from eveDrones.droneConst import DAMAGESTATE_NOT_READY
from eveInflight.damageStateValue import CalculateCurrentDamageStateValues
from eveservices.menu import GetMenuService
from menu import MenuLabel, MenuList
from utillib import KeyVal
GROUPID_INBAY = 'inbay'
GROUPID_INLOCALSPACE = 'inlocalspace'
GROUPID_INDISTANCESPACE = 'indistantspace'
launchTexturePath = 'res:/UI/Texture/classes/Drones/launchDrones.png'
DRONE_STATES = {entities.STATE_IDLE: 'UI/Inflight/Drone/Idle',
 entities.STATE_COMBAT: 'UI/Inflight/Drone/Fighting',
 entities.STATE_MINING: 'UI/Inflight/Drone/Mining',
 entities.STATE_APPROACHING: 'UI/Inflight/Drone/Approaching',
 entities.STATE_DEPARTING: 'UI/Inflight/Drone/ReturningToShip',
 entities.STATE_DEPARTING_2: 'UI/Inflight/Drone/ReturningToShip',
 entities.STATE_OPERATING: 'UI/Inflight/Drone/Operating',
 entities.STATE_PURSUIT: 'UI/Inflight/Drone/Following',
 entities.STATE_FLEEING: 'UI/Inflight/Drone/Fleeing',
 entities.STATE_ENGAGE: 'UI/Inflight/Drone/Repairing',
 entities.STATE_SALVAGING: 'UI/Inflight/Drone/Salvaging',
 None: 'UI/Inflight/Drone/NoState'}
COLOR_BY_STATE = {entities.STATE_IDLE: '0xFF00FF00',
 entities.STATE_COMBAT: '0xFFFF0000',
 entities.STATE_MINING: '0xFFFF0000',
 entities.STATE_APPROACHING: '0xFFFFFF00',
 entities.STATE_DEPARTING: '0xFFFFFF00',
 entities.STATE_DEPARTING_2: '0xFFFFFF00',
 entities.STATE_OPERATING: '0xFFFF0000',
 entities.STATE_PURSUIT: '0xFFFFFF00',
 entities.STATE_FLEEING: '0xFFFFFF00',
 entities.STATE_ENGAGE: '0xFF00FF00',
 entities.STATE_SALVAGING: '0xFFFF0000'}
damageIconInfo = {0: 'res:/UI/Texture/classes/Fitting/StatsIcons/structureHP.png',
 1: 'res:/UI/Texture/classes/Fitting/StatsIcons/armorHP.png',
 2: 'res:/UI/Texture/classes/Fitting/StatsIcons/shieldHP.png'}

def GetFavoriteDroneGroupConfigName():
    shipTypeID = None
    if session.shipid:
        shipItem = sm.GetService('godma').GetItem(session.shipid)
        if shipItem:
            shipTypeID = shipItem.typeID
    return 'drones_favoriteGroupID_%s' % shipTypeID


class DroneEntry(BaseTacticalEntry):
    __guid__ = 'listentry.DroneEntry'
    isDragObject = True
    __notifyevents__ = ['OnStateChange', 'OnDroneStateChange2', 'OnDroneActivityChange']

    def UpdateDamage(self):
        if self.destroyed:
            self.sr.dmgTimer = None
            return
        if self.sr.node.droneState == 'inbay':
            return self.UpdateDamageInBay()
        return BaseTacticalEntry.UpdateDamage(self)

    def UpdateDamageInBay(self):
        droneID = self.GetShipID()
        dmg = self.GetDamageInBay(droneID)
        ret = False
        if dmg is not None:
            if self.sr.dmgTimer is None:
                self.sr.dmgTimer = AutoTimer(1000, self.UpdateDamage)
            if dmg == DAMAGESTATE_NOT_READY:
                return
            ret = self.SetDamageState(dmg)
            self.ShowDamageDisplay()
        else:
            self.HideDamageDisplay()
        return ret

    def GetDamageInBay(self, itemID):
        if self.sr.node.damageState == DAMAGESTATE_NOT_READY:
            if not getattr(self, 'fetchingDamageValue', False):
                self.fetchingDamageValue = True
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

    def OnMouseDown(self, *args):
        uthread.new(self.OnMouseDown_thread)

    def OnMouseDown_thread(self):
        selelectedDrones = self.sr.node.scroll.GetSelectedNodes(self.sr.node)
        droneState = self.sr.node.droneState
        displayLabel = self.sr.node.label
        if len(selelectedDrones) > 1:
            displayLabel += '<fontsize=14> + %s' % (len(selelectedDrones) - 1)
        if droneState == 'inbay':
            nodesData = [ (drone.invItem, 0, None) for drone in selelectedDrones if drone.invItem is not None ]
            manyItemsData = Bunch(menuFunction=GetMenuService().InvItemMenu, itemData=nodesData, displayName='<b>%s</b>' % displayLabel)
        elif droneState in ('inlocalspace', 'inDistantSpace'):
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
        BaseTacticalEntry.Startup(self, *args)
        self.activityID = None
        self.activity = None
        text_gaugeContainer = Container(name='text_gaugeContainer', parent=self, idx=0, pos=(0, 0, 0, 0))
        self.sr.gaugesContainer = Container(name='gaugesContainer', parent=text_gaugeContainer, width=85, align=uiconst.TORIGHT, state=uiconst.UI_HIDDEN)
        tClip = Container(name='textClipper', parent=text_gaugeContainer, state=uiconst.UI_PICKCHILDREN, clipChildren=1)
        Transplant(self.sr.label, tClip)

    def Load(self, node):
        preselected = node.selected
        super(DroneEntry, self).Load(node)
        if preselected and not node.selected:
            node.selected = 1
            node.scroll.UpdateSelection(node)
        if self.sr.node.droneState in ('inlocalspace', 'indistantspace'):
            self.UpdateState()
        self.sr.gaugesContainer.state = uiconst.UI_PICKCHILDREN

    def UpdateState(self, droneState = None):
        michelle = sm.GetService('michelle')
        droneRow = michelle.GetDroneState(self.sr.node.itemID)
        droneActivity = michelle.GetDroneActivity(self.sr.node.itemID)
        if droneActivity:
            self.activity, self.activityID = droneActivity
        if droneState is None and droneRow is not None:
            droneState = droneRow.activityState
        stateText = localization.GetByLabel(DRONE_STATES.get(droneState, 'UI/Inflight/Drone/Incapacitated'))
        if droneState in COLOR_BY_STATE:
            stateText = '<color=%s>%s</color>' % (COLOR_BY_STATE[droneState], stateText)
        label = localization.GetByLabel('UI/Inflight/Drone/Label', droneType=self.sr.node.label, state=stateText)
        target = ''
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
        tooltipExtra = ''
        if self.sr.node.ownerID != eve.session.charid:
            tooltipExtra = localization.GetByLabel('UI/Inflight/Drone/OwnershipText', owner=self.sr.node.ownerID)
        elif self.sr.node.controllerID != eve.session.shipid:
            tooltipExtra = localization.GetByLabel('UI/Inflight/Drone/ControllerText', controller=self.sr.node.controllerOwnerID)
        elif self.activityID and self.activity:
            activity = ''
            if self.activity == 'guard':
                activity = localization.GetByLabel('UI/Inflight/Drone/Guarding')
            elif self.activity == 'assist':
                activity = localization.GetByLabel('UI/Inflight/Drone/Assisting')
            tooltipExtra = localization.GetByLabel('UI/Inflight/Drone/Activity', activity=activity, idInfo=cfg.eveowners.Get(self.activityID).name)
        tooltip = localization.GetByLabel('UI/Inflight/Drone/Tooltip', droneType=self.sr.node.label, state=stateText, target=target, tooltipExtra=tooltipExtra)
        self.sr.label.text = label
        self.hint = tooltip

    def LoadTooltipPanel(self, tooltipPanel, *args):
        tooltipPanel.margin = (10, 3, 10, 3)
        self._LoadTooltipPanel_thread(tooltipPanel)
        self.tooltipThread = AutoTimer(500, self._LoadTooltipPanel_thread, tooltipPanel)

    def _LoadTooltipPanel_thread(self, tooltipPanel):
        currentMouseOver = uicore.uilib.mouseOver
        if self.destroyed or currentMouseOver != self and not currentMouseOver.IsUnder(self):
            self.tooltipThread = None
            return
        tooltipPanel.Flush()
        text = self.hint or evetypes.GetName(self.sr.node.typeID)
        textLabel = EveLabelMedium(align=uiconst.CENTER, width=200, autoFitToText=True, parent=tooltipPanel, text=text)
        droneID = self.GetShipID()
        if self.sr.node.droneState == 'inbay':
            dmg = self.GetDamageInBay(droneID)
        else:
            dmg = self.GetDamage(droneID)
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

    def GetHeight(self, *args):
        node, width = args
        node.height = uix.GetTextHeight('Xg', maxLines=1) + 4
        return node.height

    def OnDroneStateChange2(self, droneID, oldActivityState, newActivityState):
        if not self or getattr(self, 'sr', None) is None:
            return
        if self.sr.node and self.sr.node.droneState in ('inlocalspace', 'indistantspace') and droneID == self.sr.node.itemID:
            droneRow = sm.GetService('michelle').GetDroneState(self.sr.node.itemID)
            if droneRow:
                self.sr.node.controllerID = droneRow.controllerID
                self.sr.node.controllerOwnerID = droneRow.controllerOwnerID
                self.UpdateState(newActivityState)

    def OnDroneActivityChange(self, droneID, activityID, activity):
        if not self or getattr(self, 'sr', None) is None:
            return
        if self.sr.node and self.sr.node.droneState in ('inlocalspace', 'indistantspace') and droneID == self.sr.node.itemID:
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
        if self.sr.node.droneState != 'inbay':
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

    def InitGauges(self):
        if getattr(self, 'gaugesInited', False):
            self.sr.gaugeParent.state = uiconst.UI_DISABLED
            return
        parent = self.sr.gaugesContainer
        Line(parent=parent, align=uiconst.TOLEFT)
        barw, barh = (22, 6)
        borderw = 2
        barsw = (barw + borderw) * 3 + borderw
        par = Container(name='gauges', parent=parent, align=uiconst.TORIGHT, width=barsw + 2, height=0, left=0, top=0, idx=10)
        self.sr.gauges = []
        l = 2
        for each in ('STRUCT', 'ARMOR', 'SHIELD'):
            g = Container(parent=par, name='gauge_%s' % each.lower(), align=uiconst.CENTERLEFT, width=barw, height=barh, left=l)
            g.sr.bar = Fill(parent=g, name='droneGaugeBar', align=uiconst.TOLEFT, color=(1.0, 1.0, 1.0, 0.4))
            Fill(parent=g, name='droneGaugeBarDmg', color=(158 / 256.0,
             11 / 256.0,
             14 / 256.0,
             1.0))
            self.sr.gauges.append(g)
            setattr(self.sr, 'gauge_%s' % each.lower(), g)
            l += barw + borderw

        self.sr.gaugeParent = par
        self.gaugesInited = True

    def GetDragData(self, *args):
        return [ node for node in self.sr.node.scroll.GetSelectedNodes(self.sr.node) if node.__guid__ == 'listentry.DroneEntry' ]

    def Close(self):
        self.tooltipThread = None
        BaseTacticalEntry.Close(self)


class DroneView(ActionPanel):
    __guid__ = 'form.DroneView'
    __notifyevents__ = ['OnAttribute',
     'OnAttributes',
     'OnDroneControlLost',
     'OnItemChange',
     'OnItemLaunch',
     'OnClientEvent_WarpStarted',
     'OnClientEvent_WarpFinished',
     'OnWarpStarted2',
     'ProcessSessionChange']
    default_windowID = 'droneview'
    uniqueUiName = pConst.UNIQUE_NAME_DRONE_WND
    default_minSize = (240, 80)

    def get_wnd_menu_unique_name(self):
        return pConst.UNIQUE_NAME_DRONE_SETTINGS

    @staticmethod
    def default_left(*args):
        return actionPanelDefaults.GetDroneViewLeft()

    @staticmethod
    def default_top(*args):
        return actionPanelDefaults.GetDroneViewTop()

    @staticmethod
    def default_width():
        return actionPanelDefaults.GetDroneViewWidth()

    @staticmethod
    def default_height():
        return actionPanelDefaults.GetDroneViewHeight()

    def ApplyAttributes(self, attributes):
        self.droneAggressionDefVal = dogma.data.get_attribute_default_value(const.attributeDroneIsAggressive)
        self.droneFFDefVal = dogma.data.get_attribute_default_value(const.attributeDroneFocusFire)
        ActionPanel.ApplyAttributes(self, attributes)

    def OnItemLaunch(self, ids):
        reload = False
        for oldID, newIDs in ids.iteritems():
            group = self.GetDroneGroup(oldID)
            if group is not None:
                for newID in newIDs:
                    if newID != oldID:
                        group['droneIDs'].add(newID)
                        reload = True

        if reload:
            self.UpdateGroupSettings()
            self.CheckReloadDronesScroll(True)

    def ProcessSessionChange(self, *etc):
        self.CheckReloadDronesScroll(True)

    ProcessSessionChange = Uthreaded(ProcessSessionChange)

    def OnDroneControlLost(self, droneID):
        self.CheckReloadDronesScroll(True)

    def OnAttributes(self, l):
        for attributeName, item, newValue in l:
            self.OnAttribute(attributeName, item, newValue)

    def OnAttribute(self, attributeName, item, newValue):
        if not self or self.destroyed:
            return
        if item.itemID == session.charid and attributeName == 'maxActiveDrones':
            t = self.sr.lastUpdate
            if t is None:
                self.CheckReloadDronesScroll()
            else:
                self.UpdateHeader(t[0], t[1] + t[2])

    def OnItemChange(self, item, change, location):
        if item.locationID == session.shipid:
            if item.flagID == const.flagDroneBay or change.get(const.ixFlag, None) == const.flagDroneBay:
                ignoreClose = session.solarsystemid == change.get(const.ixLocationID, None)
                self.CheckReloadDronesScroll(ignoreClose=ignoreClose)
        elif change.get(const.ixLocationID, None) == session.shipid and change.get(const.ixFlag, None) == const.flagDroneBay:
            self.CheckReloadDronesScroll()

    def PostStartup(self):
        if not self or self.destroyed:
            return
        self.SetMinSize((240, 80))
        self.warpWarning = WarpWarning(parent=self.sr.main, align=uiconst.TOTOP, state=uiconst.UI_HIDDEN, padBottom=2)
        self.sr.scroll = Scroll(name='dronescroll', align=uiconst.TOALL, parent=self.sr.main)
        self.sr.scroll.multiSelect = 1
        self.sr.scroll.OnChar = self.OnDronesScrollChar
        self.sr.inSpace = None
        self.sr.lastUpdate = None
        self.settingsName = 'droneBlah2'
        self.reloading = 0
        self.pending = None
        openState = uicore.registry.GetListGroupOpenState(('dronegroups', 'inbay'), default=False)
        uicore.registry.GetLockedGroup('dronegroups', 'inbay', localization.GetByLabel('UI/Inflight/Drone/DronesInBay'), openState=openState)
        openState = uicore.registry.GetListGroupOpenState(('dronegroups', 'inlocalspace'), default=False)
        uicore.registry.GetLockedGroup('dronegroups', 'inlocalspace', localization.GetByLabel('UI/Inflight/Drone/DronesInLocalSpace'), openState=openState)
        uicore.registry.GetLockedGroup('dronegroups', 'indistantspace', localization.GetByLabel('UI/Inflight/Drone/DronesInDistantSpace'))
        self.groups = self.SettifyGroups(settings.user.ui.Get(self.settingsName, {}))
        droneSettingChanges = {const.attributeDroneIsAggressive: settings.char.ui.Get('droneAggression', self.droneAggressionDefVal),
         const.attributeDroneFocusFire: settings.char.ui.Get('droneFocusFire', self.droneFFDefVal)}
        sm.GetService('godma').GetStateManager().ChangeDroneSettings(droneSettingChanges)
        if self and not self.destroyed:
            uthread.new(self.CheckReloadDronesScroll)

    def OnDronesScrollChar(self, *args):
        return False

    def GroupXfier(fn):

        def XfyGroup(group):
            ret = group.copy()
            ret['droneIDs'] = fn(group['droneIDs'])
            return ret

        return lambda self, groups: dict([ (name, XfyGroup(group)) for name, group in groups.iteritems() ])

    ListifyGroups = GroupXfier(list)
    SettifyGroups = GroupXfier(set)
    del GroupXfier

    def GetSelected(self, fromNode):
        nodes = []
        sel = self.sr.scroll.GetSelectedNodes(fromNode)
        for node in sel:
            if node.Get('typeID', None) is None:
                continue
            if evetypes.GetGroupID(node.typeID) == evetypes.GetGroupID(fromNode.typeID):
                if node.droneState == fromNode.droneState:
                    nodes.append(node)

        return nodes

    def UpdateHeader(self, inBay, inSpace):
        self.SetCaption(localization.GetByLabel('UI/Inflight/Drone/PanelHeader', panelName=self.panelname, inSpace=len(inSpace), maxTotal=int(sm.GetService('godma').GetItem(session.charid).maxActiveDrones) or 0))

    def UpdateAll(self):
        if self.sr.main.state != uiconst.UI_PICKCHILDREN:
            self.sr.actionsTimer = None
            return
        self.CheckReloadDronesScroll()

    def GetSubGroups(self, what):
        return []

    def CheckReloadDronesScroll(self, force = False, ignoreClose = False, *args):
        if session.stationid:
            return
        if not self.pending:
            self.pending = ('updating',)
        else:
            if 'updating' in self.pending:
                self.pending = ('pending', force, ignoreClose)
                return
            if 'pending' in self.pending:
                p, oldForce, oldIgnoreClose = self.pending
                self.pending = ('pending', force or oldForce, ignoreClose or oldIgnoreClose)
                return
        if self.destroyed:
            return
        inBay = self.GetDronesInBay()
        inBayIDs = [ drone.itemID for drone in inBay ]
        inBayIDs.sort()
        uthread.new(sm.GetService('tactical').GetInBayDroneDamageTracker().FetchInBayDroneDamageToServer, inBayIDs)
        inLocalSpace = [ drone for drone in GetDronesInLocalSpace() if drone.droneID not in inBayIDs ]
        inLocalSpaceIDs = [ drone.droneID for drone in inLocalSpace ]
        inLocalSpaceIDs.sort()
        inDistantSpace = [ drone for drone in GetDronesInDistantSpace() if drone.droneID not in inBayIDs ]
        inDistantSpaceIDs = [ drone.droneID for drone in inDistantSpace ]
        inDistantSpaceIDs.sort()
        allDroneIDs = inBayIDs + inLocalSpaceIDs + inDistantSpaceIDs
        t = (inBayIDs, inLocalSpaceIDs, inDistantSpaceIDs)
        if self.sr.lastUpdate != t or force or inDistantSpace:
            self.sr.lastUpdate = t
            groupInfo = uicore.registry.GetListGroup(('dronegroups', GROUPID_INBAY))
            scrolllist = self.GetGroupListEntry(groupInfo, '%s' % GROUPID_INBAY, inBayIDs, allDroneIDs)
            groupInfo = uicore.registry.GetListGroup(('dronegroups', GROUPID_INLOCALSPACE))
            scrolllist += self.GetGroupListEntry(groupInfo, GROUPID_INLOCALSPACE, inLocalSpaceIDs)
            if inDistantSpaceIDs:
                groupInfo = uicore.registry.GetListGroup(('dronegroups', GROUPID_INDISTANCESPACE))
                scrolllist += self.GetGroupListEntry(groupInfo, GROUPID_INDISTANCESPACE, inDistantSpaceIDs)
            self.sr.scroll.Load(contentList=scrolllist)
        self.UpdateHeader(inBayIDs, inLocalSpaceIDs + inDistantSpaceIDs)
        self.CheckHint()
        self.UpdateWarpWarning()
        blue.pyos.synchro.SleepWallclock(500)
        if not self or self.destroyed:
            return
        if 'pending' in self.pending:
            p, force, ignoreClose = self.pending
            self.pending = None
            self.CheckReloadDronesScroll(force, ignoreClose)
            return
        self.pending = None
        if not ignoreClose and not self.destroyed:
            self.CheckClose()

    def CheckClose(self):
        if not (self.GetDronesInBay() or sm.GetService('michelle').GetDrones()) and hasattr(self, 'Close'):
            self.Close()

    def GetMainFolderMenu(self, node):
        m = MenuList([None])
        delMenu = [ (groupName, self.DeleteGroup, (groupName,)) for groupName, groupInfo in self.groups.iteritems() ]
        if delMenu:
            m += [(MenuLabel('UI/Commands/DeleteGroup'), delMenu), None]
        data = self.GetDroneDataForMainGroup(node)
        if not data:
            return m
        if node.droneState in ('inlocalspace', 'indistantspace'):
            m += GetMenuService().DroneMenu(data)
        else:
            m += GetMenuService().InvItemMenu(data).filter([MenuLabel('UI/Inventory/ItemActions/BuyThisType'),
             MenuLabel('UI/Inventory/ItemActions/AddTypeToMarketQuickbar'),
             MenuLabel('UI/Inventory/ItemActions/ViewTypesMarketDetails'),
             MenuLabel('UI/Inventory/ItemActions/FindInContracts')])
        return m

    def GetNodesToMoveAround(self, nodes):
        if len(nodes) > 1:
            return nodes
        firstNode = nodes[0]
        if firstNode['__guid__'] == 'listentry.DroneSubGroup':
            nodes = self.GetSubGroupContent(firstNode)
        elif firstNode['__guid__'] == 'listentry.DroneMainGroup':
            nodes = self.GetAllMainGroupContent(firstNode)
        return nodes

    def GroupDropData(self, dragObj, nodes):
        groupState = dragObj[1]
        self.LaunchOrPullDrones(groupState, nodes)

    def GetAllMainGroupContent(self, nodedata):
        nodes = self.GetGroupContent(nodedata)
        myNodes = []
        for eachNode in nodes:
            if eachNode.decoClass == DroneSubGroup:
                myNodes += self.GetSubGroupContent(eachNode)
            else:
                myNodes.append(eachNode)

        return myNodes

    def SubGroupDropData(self, dragObj, nodes):
        groupState = dragObj[0]
        groupNameAndID = dragObj[1]
        groupName = groupNameAndID[0]
        nodes = self.GetNodesToMoveAround(nodes)
        dronesWithChangedState = self.LaunchOrPullDrones(groupState, nodes)
        self.MoveDronesToSubGroup(groupName=groupName, nodes=nodes, excludedDrones=dronesWithChangedState)

    def MoveDronesToSubGroup(self, groupName, nodes, excludedDrones = []):
        subGroupInfo = self.GetSubGroup(groupName)
        movingDrones = []
        for droneNode in nodes:
            if droneNode in excludedDrones:
                continue
            if droneNode.itemID not in subGroupInfo['droneIDs']:
                movingDrones.append(droneNode)

        if movingDrones:
            firstDrone = movingDrones[0]
            self.MoveToGroup(groupName, firstDrone.itemID, evetypes.GetGroupID(firstDrone.typeID), movingDrones)

    def LaunchOrPullDrones(self, groupState, nodes, *args):
        nodes = self.GetNodesToMoveAround(nodes)
        changingState = []
        for droneNode in nodes:
            if droneNode.droneState in ('inlocalspace', 'inbay') and droneNode.droneState != groupState:
                changingState.append(droneNode)

        if changingState:
            if groupState == 'inlocalspace':
                GetMenuService().LaunchDrones([ droneNode.invItem for droneNode in changingState ])
            elif groupState == 'inbay':
                ReturnToDroneBay([ droneNode.itemID for droneNode in changingState ])
        return changingState

    def DeleteGroup(self, groupName):
        self.EmptyGroup(groupName)
        if groupName in self.groups:
            del self.groups[groupName]
        self.UpdateGroupSettings()
        self.UpdateAll()

    def GetSubFolderMenu(self, node):
        m = MenuList([None])
        data = self.GetDroneDataForSubGroup(node)
        if not data:
            return m
        if node.droneState in ('inlocalspace', 'indistantspace'):
            m += GetMenuService().DroneMenu(data)
        elif node.droneState == 'inbay':
            m += GetMenuService().InvItemMenu(data).filter([MenuLabel('UI/Inventory/ItemActions/BuyThisType'),
             MenuLabel('UI/Inventory/ItemActions/AddTypeToMarketQuickbar'),
             MenuLabel('UI/Inventory/ItemActions/ViewTypesMarketDetails'),
             MenuLabel('UI/Inventory/ItemActions/FindInContracts')])
        favoriteGroup = self.GetFavoriteGroupIdentifier()
        groupIdentifier = node.id[-1]
        if favoriteGroup == groupIdentifier:
            m += [(MenuLabel('UI/Drones/UnmarkAsFavorite'), self.RemoveAsFavorite, (groupIdentifier,))]
        else:
            m += [(MenuLabel('UI/Drones/MarkAsFavorite'), self.AddAsFavorite, (groupIdentifier,))]
        return m

    def AddAsFavorite(self, groupIdentifier):
        self.SetFavoriteGroupSetting(groupIdentifier)
        self.CheckReloadDronesScroll(force=True)

    def RemoveAsFavorite(self, groupIdentifier):
        favoriteGroupID = self.GetFavoriteGroupIdentifier()
        if groupIdentifier == favoriteGroupID:
            self.SetFavoriteGroupSetting(None)
            self.CheckReloadDronesScroll(force=True)

    def SetFavoriteGroupSetting(self, value):
        settingName = GetFavoriteDroneGroupConfigName()
        settings.user.ui.Set(settingName, value)

    def GroupMenu(self, droneNode):
        selected = self.GetSelected(droneNode)
        m = MenuList()
        move = [(MenuLabel('UI/Commands/NewGroup'), self.CreateSubGroup, (droneNode.itemID, evetypes.GetGroupID(droneNode.typeID), selected))]
        inGroup = []
        for node in selected:
            group = self.GetDroneGroup(node.itemID)
            if group:
                inGroup.append(node)

        if inGroup:
            move += [(MenuLabel('UI/Commands/OutOfThisGroup'), self.NoGroup, (inGroup,))]
        groupNames = self.groups.keys()[:]
        groupNames.sort(key=lambda x: x.lower())
        move += [ (groupName, self.MoveToGroup, (groupName,
          droneNode.itemID,
          evetypes.GetGroupID(droneNode.typeID),
          selected)) for groupName in groupNames ]
        m += [(MenuLabel('UI/Commands/MoveDrone'), move)]
        return m

    def GetEmptyGroups(self):
        empty = []
        for groupName, groupInfo in self.groups.iteritems():
            if not groupInfo['droneIDs']:
                empty.append(groupName)

        return empty

    def DeleteEmptyGroups(self, *args):
        for groupName in self.GetEmptyGroups():
            del self.groups[groupName]

    def GetDroneGroup(self, droneID, getall = 0):
        retall = []
        for groupName, group in self.groups.iteritems():
            if droneID in group['droneIDs']:
                if getall:
                    retall.append(group)
                else:
                    return group

        if getall:
            return retall

    def NoGroup(self, nodes):
        for node in nodes:
            for group in self.GetDroneGroup(node.itemID, getall=1):
                group['droneIDs'].remove(node.itemID)

        self.CheckReloadDronesScroll(1)
        self.UpdateGroupSettings()

    def EmptyGroup(self, groupName):
        droneGroup = self.GetSubGroup(groupName)
        for droneID in droneGroup.get('droneIDs', set()).copy():
            for group in self.GetDroneGroup(droneID, getall=1):
                group['droneIDs'].remove(droneID)

        self.CheckReloadDronesScroll(1)

    def MoveToGroup(self, groupName, droneID, droneGroupID, nodes):
        group = self.GetSubGroup(groupName)
        if group['droneIDs'] and group['droneGroupID'] != droneGroupID:
            eve.Message('CannotMixDrones')
            return
        for node in nodes:
            for group in self.GetDroneGroup(node.itemID, getall=1):
                group['droneIDs'].remove(node.itemID)

        group = self.GetSubGroup(groupName)
        if not group['droneIDs']:
            group['droneGroupID'] = droneGroupID
        if group:
            for node in nodes:
                group['droneIDs'].add(node.itemID)

        self.CheckReloadDronesScroll(1)
        self.UpdateGroupSettings()

    def GetSubGroup(self, groupName):
        if groupName in self.groups:
            return self.groups[groupName]

    def CreateSubGroup(self, droneID, droneGroupID, nodes = None):
        ret = NamePopup(localization.GetByLabel('UI/Generic/TypeGroupName'), localization.GetByLabel('UI/Generic/TypeNameForGroup'))
        if not ret:
            return
        droneIDs = set()
        for node in nodes:
            for group in self.GetDroneGroup(node.itemID, getall=1):
                group['droneIDs'].remove(node.itemID)

            droneIDs.add(node.itemID)

        origname = groupname = ret
        i = 2
        while groupname in self.groups:
            groupname = '%s_%i' % (origname, i)
            i += 1

        group = {}
        group['label'] = groupname
        group['droneIDs'] = droneIDs
        group['id'] = (groupname, str(blue.os.GetWallclockTime()))
        group['droneGroupID'] = droneGroupID
        self.groups[groupname] = group
        self.CheckReloadDronesScroll(1)
        self.UpdateGroupSettings()

    def OnMainGroupClick(self, group, *args):
        itemIDs = self.GetDroneIDsInMainGroup(group.sr.node)
        if itemIDs:
            sm.ScatterEvent('OnDronesSelected', itemIDs)

    def OnSubGroupClick(self, group, *args):
        itemIDs = self.GetDroneIDsInSubGroup(group.sr.node)
        if itemIDs:
            sm.ScatterEvent('OnDronesSelected', itemIDs)

    def GetDroneIDsInMainGroup(self, groupNode):
        droneDict = self.GetDroneDictFromDroneIDs(None, groupNode.droneState, includeFunction=self.IncludeAllDrones)
        return droneDict.keys()

    def GetDroneDataForMainGroup(self, groupNode):
        droneDict = self.GetDroneDictFromDroneIDs(None, groupNode.droneState, includeFunction=self.IncludeAllDrones)
        return droneDict.values()

    def GetDroneIDsInSubGroup(self, groupNode):
        droneDict = self.GetDroneDictForSubGroup(groupNode)
        return droneDict.keys()

    def GetDroneDataForSubGroup(self, groupNode):
        droneDict = self.GetDroneDictForSubGroup(groupNode)
        return droneDict.values()

    def GetDroneDictForSubGroup(self, groupNode):
        droneState = groupNode.droneState
        allDronesBelongingToGroup = self.GetSubGroup(groupNode.groupName)['droneIDs']
        droneDict = self.GetDroneDictFromDroneIDs(allDronesBelongingToGroup, droneState)
        return droneDict

    def GetDroneDictFromDroneIDs(self, itemIDs, droneState, includeFunction = None):
        if includeFunction is None:
            includeFunction = self.IsDroneIDinItemIDs
        droneDict = {}
        if droneState == 'inbay':
            droneDict = {drone.itemID:(drone, 0, None) for drone in self.GetDronesInBay() if includeFunction(drone.itemID, itemIDs)}
            return droneDict
        if droneState == 'inlocalspace':
            listOfDrones = GetDronesInLocalSpace()
        elif droneState == 'indistantspace':
            listOfDrones = GetDronesInDistantSpace()
        else:
            return droneDict
        droneDict = {drone.droneID:(drone.droneID,
         drone.typeID,
         drone.ownerID,
         drone.locationID) for drone in listOfDrones if includeFunction(drone.droneID, itemIDs)}
        return droneDict

    def IsDroneIDinItemIDs(self, droneID, itemIDs):
        return droneID in itemIDs

    def IncludeAllDrones(self, droneID, itemIDs):
        return True

    def OnMouseDownOnDroneMainGroup(self, group, *args):
        self.OnMouseDownOnDroneMainGroup_thread(group)

    def OnMouseDownOnDroneMainGroup_thread(self, group):
        groupNode = group.sr.node
        droneData = self.GetDroneDataForMainGroup(groupNode)
        return self.GetRadialMenuOnGroup(group, droneData)

    def OnMouseDownOnDroneSubGroup(self, group, *args):
        uthread.new(self.OnMouseDownOnDroneSubGroup_thread, group)

    def OnMouseDownOnDroneSubGroup_thread(self, group):
        groupNode = group.sr.node
        droneData = self.GetDroneDataForSubGroup(groupNode)
        return self.GetRadialMenuOnGroup(group, droneData)

    def GetRadialMenuOnGroup(self, group, droneData):
        if not droneData:
            return
        groupNode = group.sr.node
        droneState = groupNode.droneState
        if droneState == 'inbay':
            manyItemsData = Bunch(menuFunction=GetMenuService().InvItemMenu, itemData=droneData, displayName='<b>%s</b>' % groupNode.cleanLabel)
        elif droneState in ('inlocalspace', 'indistantspace'):
            manyItemsData = Bunch(menuFunction=GetMenuService().DroneMenu, itemData=droneData, displayName='<b>%s</b>' % groupNode.cleanLabel)
        else:
            return
        typeID = GetTypeIDForManyDrones(droneState, droneData)
        GetMenuService().TryExpandActionMenu(itemID=None, typeID=typeID, clickedObject=group, manyItemsData=manyItemsData)

    def GetDronesInBay(self, *args):
        if eve.session.shipid:
            return sm.GetService('invCache').GetInventoryFromId(eve.session.shipid).ListDroneBay()
        return []

    def GetSpaceDrone(self, droneID):
        return sm.GetService('michelle').GetDroneState(droneID)

    def GetGroupListEntry(self, group, state, items, allDroneIDs = None):
        if not group or 'id' not in group:
            return []
        numDrones = self.GetNumberOfDronesInGroup(state, items)
        states = {'INBAY': localization.GetByLabel('UI/Inflight/Drone/DronesInBay'),
         'INLOCALSPACE': localization.GetByLabel('UI/Inflight/Drone/DronesInLocalSpace'),
         'INDISTANTSPACE': localization.GetByLabel('UI/Inflight/Drone/DronesInDistantSpace')}
        icon = None
        if state == 'inbay' and not self.IsFavoriteGroupHere(allDroneIDs):
            icon = launchTexturePath
        data = {'GetSubContent': self.GetGroupContent,
         'DropData': self.GroupDropData,
         'MenuFunction': self.GetMainFolderMenu,
         'label': localization.GetByLabel('UI/Inflight/Drone/DroneGroupWithCount', groupLabel=states[state.upper()], count=numDrones),
         'id': group['id'],
         'groupItems': items,
         'iconMargin': 18,
         'state': 'locked',
         'sublevel': 0,
         'droneState': state,
         'BlockOpenWindow': 1,
         'OnClick': self.OnMainGroupClick,
         'showlen': 0,
         'groupName': group['label'],
         'name': 'droneOverview%s' % group['label'].replace(' ', '').capitalize(),
         'OnMouseDown': self.OnMouseDownOnDroneMainGroup,
         'showicon': icon,
         'GetUtilMenu': self.DroneSettings}
        groupCls = self._GetEntryGroupClass(state)
        return [GetFromClass(groupCls, data)]

    def _GetEntryGroupClass(self, groupID):
        if groupID == GROUPID_INLOCALSPACE:
            groupCls = DroneMainGroupInSpace
        else:
            groupCls = DroneMainGroup
        return groupCls

    def IsFavoriteGroupHere(self, allDroneIDs):
        favoriteGroupID = self.GetFavoriteGroupIdentifier()
        if favoriteGroupID is None:
            return False
        dronesByGroupIdentifiers = {x.get('id'):x.get('droneIDs') for x in self.groups.itervalues()}
        dronesInGroup = dronesByGroupIdentifiers.get(favoriteGroupID, [])
        if not dronesInGroup:
            return False
        if set(dronesInGroup).intersection(allDroneIDs):
            return True
        return False

    def GetFavoriteGroupIdentifier(self):
        settingName = GetFavoriteDroneGroupConfigName()
        return settings.user.ui.Get(settingName, None)

    def GetSubGroupListEntry(self, group, state, items):
        numDrones = self.GetNumberOfDronesInGroup(state, items)
        icon = None
        groupIdentifier = group['id']
        favoriteGroup = self.GetFavoriteGroupIdentifier()
        if favoriteGroup and favoriteGroup == groupIdentifier:
            icon = launchTexturePath
        return GetFromClass(DroneSubGroup, {'GetSubContent': self.GetSubGroupContent,
         'DropData': self.SubGroupDropData,
         'MenuFunction': self.GetSubFolderMenu,
         'label': localization.GetByLabel('UI/Inflight/Drone/DroneGroupWithCount', groupLabel=group['label'], count=numDrones),
         'id': (state, groupIdentifier),
         'droneGroupID': group['droneGroupID'],
         'groupItems': None,
         'iconMargin': 18,
         'state': 'locked',
         'sublevel': 1,
         'droneState': state,
         'BlockOpenWindow': 1,
         'OnClick': self.OnSubGroupClick,
         'showlen': 0,
         'groupName': group['label'],
         'OnMouseDown': self.OnMouseDownOnDroneSubGroup,
         'showicon': icon})

    def GetNumberOfDronesInGroup(self, droneState, items):
        t = 0
        if droneState == 'inbay':
            dronebay = {}
            for drone in self.GetDronesInBay():
                dronebay[drone.itemID] = drone

            for droneID in items:
                if droneID not in dronebay:
                    log.LogWarn("Drone we thought was in the dronebay wasn't actually there, droneID = ", droneID)
                    continue
                t += dronebay[droneID].stacksize

        else:
            t = len(items)
        return t

    def GetGroupContent(self, nodedata, newitems = 0):
        scrollList = []
        if nodedata.droneState == 'inbay':
            dronebay = {}
            for drone in self.GetDronesInBay():
                dronebay[drone.itemID] = drone

        subGroups = {}
        for droneID in nodedata.groupItems:
            group = self.GetDroneGroup(droneID)
            if group:
                subGroups.setdefault(group['label'], []).append(droneID)
                continue
            if nodedata.droneState == 'inbay':
                if dronebay.has_key(droneID):
                    entry = self.GetBayDroneEntry(dronebay[droneID], nodedata.sublevel, nodedata.droneState)
                    scrollList.append(((0, entry.label.lower()), entry))
            else:
                entry = self.GetSpaceDroneEntry(self.GetSpaceDrone(droneID), nodedata.sublevel, nodedata.droneState)
                scrollList.append(((0, entry.label.lower()), entry))

        for groupName, droneIDs in subGroups.iteritems():
            group = self.GetSubGroup(groupName)
            if group:
                entry = self.GetSubGroupListEntry(group, nodedata.droneState, droneIDs)
                scrollList.append(((1, entry.label.lower()), entry))

        if not scrollList:
            noItemEntry = self.GetNoItemEntry(sublevel=1, droneState=nodedata.droneState)
            scrollList.append((0, noItemEntry))
        return SortListOfTuples(scrollList)

    def GetSubGroupContent(self, nodedata, newitems = 0):
        scrollList = []
        subGroupInfo = self.GetSubGroup(nodedata.groupName)
        if nodedata.droneState == 'inbay':
            drones = self.GetDronesInBay()
            for drone in drones:
                if drone.itemID in subGroupInfo['droneIDs']:
                    entry = self.GetBayDroneEntry(drone, 1, nodedata.droneState)
                    scrollList.append(((entry.subLevel, entry.label), entry))

        elif nodedata.droneState == 'inlocalspace':
            drones = GetDronesInLocalSpace()
            for drone in drones:
                if drone.droneID in subGroupInfo['droneIDs']:
                    entry = self.GetSpaceDroneEntry(drone, 1, nodedata.droneState)
                    scrollList.append(((entry.subLevel, entry.label), entry))

        else:
            drones = GetDronesInDistantSpace()
            for drone in drones:
                if drone.droneID in subGroupInfo['droneIDs']:
                    entry = self.GetSpaceDroneEntry(drone, 1, nodedata.droneState)
                    scrollList.append(((entry.subLevel, entry.label), entry))

        if not scrollList:
            noItemEntry = self.GetNoItemEntry(sublevel=2, droneState=nodedata.droneState)
            scrollList.append((0, noItemEntry))
        return SortListOfTuples(scrollList)

    def GetNoItemEntry(self, sublevel, droneState, *args):
        data = KeyVal()
        data.droneState = droneState
        data.label = localization.GetByLabel('/Carbon/UI/Controls/Common/NoItem')
        data.sublevel = sublevel
        data.itemID = None
        data.OnDropData = lambda dragObject, nodes: self.DropDronesOnDroneEntry(data, dragObject, nodes)
        return GetFromClass(Generic, data)

    def GetDroneDamageState(self, droneID):
        damageTracker = sm.GetService('tactical').GetInBayDroneDamageTracker()
        if damageTracker.IsDroneDamageReady(droneID):
            damageState = damageTracker.GetDamageStateForDrone(droneID)
        else:
            damageState = -1
        return damageState

    def GetBayDroneEntry(self, drone, level, droneState):
        data = KeyVal()
        data.itemID = drone.itemID
        data.typeID = drone.typeID
        data.invItem = drone
        data.damageState = self.GetDroneDamageState(drone.itemID)
        data.displayName = evetypes.GetName(drone.typeID)
        if drone.stacksize > 1:
            data.label = localization.GetByLabel('UI/Inflight/Drone/DroneBayEntryWithStacksize', drone=drone.typeID, stacksize=drone.stacksize)
        else:
            data.label = evetypes.GetName(drone.typeID)
        data.sublevel = level
        data.customMenu = self.GroupMenu
        data.droneState = droneState
        data.OnDropData = lambda dragObject, nodes: self.DropDronesOnDroneEntry(data, dragObject, nodes)
        return GetFromClass(DroneEntry, data)

    def GetSpaceDroneEntry(self, drone, level, droneState):
        data = KeyVal()
        data.itemID = drone.droneID
        data.typeID = drone.typeID
        data.ownerID = drone.ownerID
        data.controllerID = drone.controllerID
        data.controllerOwnerID = drone.controllerOwnerID
        data.displayName = data.label = evetypes.GetName(drone.typeID)
        data.sublevel = level
        data.customMenu = self.GroupMenu
        data.droneState = droneState
        data.OnDropData = lambda dragObject, nodes: self.DropDronesOnDroneEntry(data, dragObject, nodes)
        return GetFromClass(DroneEntry, data)

    def DropDronesOnDroneEntry(self, entryData, dragObject, nodes):
        if dragObject.sr.node['__guid__'] not in ('listentry.DroneEntry', 'listentry.DroneMainGroup', 'listentry.DroneSubGroup'):
            return
        newGroupState = entryData.droneState
        dronesWithChangedState = self.LaunchOrPullDrones(newGroupState, nodes)
        droneEntries = [ node for node in nodes if node.__guid__ == 'listentry.DroneEntry' ]
        if not droneEntries:
            return
        group = self.GetDroneGroup(entryData.itemID)
        if group:
            self.MoveDronesToSubGroup(groupName=group['label'], nodes=droneEntries, excludedDrones=dronesWithChangedState)
        else:
            self.NoGroup(droneEntries)

    def CheckHint(self):
        if not self.sr.scroll.GetNodes():
            self.sr.scroll.ShowHint(localization.GetByLabel('UI/Inflight/Drone/NoDrones'))
        else:
            self.sr.scroll.ShowHint()

    def UpdateGroupSettings(self):
        settings.user.ui.Set(self.settingsName, self.ListifyGroups(self.groups))
        sm.GetService('settings').SaveSettings()

    def DroneSettings(self, menuParent):
        self.droneBehaviour = sm.GetService('godma').GetStateManager().GetDroneSettingAttributes()
        self.droneAggressionDefVal = dogma.data.get_attribute_default_value(const.attributeDroneIsAggressive)
        self.droneFFDefVal = dogma.data.get_attribute_default_value(const.attributeDroneFocusFire)
        if not self.droneBehaviour.has_key(const.attributeDroneIsAggressive):
            self.droneBehaviour[const.attributeDroneIsAggressive] = settings.char.ui.Get('droneSettingAttributeID ' + str(const.attributeDroneIsAggressive), 0)
        aggressive = settings.char.ui.Get('droneAggression', self.droneAggressionDefVal)
        menuParent.AddRadioButton(text=localization.GetByLabel('UI/Drones/AggressionStatePassive'), checked=not aggressive, callback=(self.AggressiveChange, False))
        menuParent.AddRadioButton(text=localization.GetByLabel('UI/Drones/AggressionStateAggressive'), checked=aggressive, callback=(self.AggressiveChange, True))
        focusFire = settings.char.ui.Get('droneFocusFire', self.droneFFDefVal)
        menuParent.AddCheckBox(text=localization.GetByLabel('UI/Drones/AttackModeFocusFire'), checked=focusFire, callback=(self.FocusFireChange, not focusFire))

    def GetMenuMoreOptions(self):
        menuData = super(DroneView, self).GetMenuMoreOptions()
        menuData.AddCheckbox(text=localization.GetByLabel('UI/Drones/WarpWarningOption'), setting=warp_warning_enabled_setting)
        return menuData

    def AggressiveChange(self, aggressive, *args):
        self.OnDroneSettingChanged(const.attributeDroneIsAggressive, 'droneAggression', aggressive)

    def FocusFireChange(self, focusFire, *args):
        self.OnDroneSettingChanged(const.attributeDroneFocusFire, 'droneFocusFire', focusFire)

    def OnDroneSettingChanged(self, attributeID, configName, value):
        settings.char.ui.Set(configName, value)
        sm.GetService('godma').GetStateManager().ChangeDroneSettings({attributeID: value})

    def OnClientEvent_WarpStarted(self, *args):
        self.UpdateWarpWarning()

    def OnWarpStarted2(self, *args):
        self.UpdateWarpWarning()

    def OnClientEvent_WarpFinished(self, *args):
        self.UpdateWarpWarning()

    def UpdateWarpWarning(self):
        if not warp_warning_enabled_setting.is_enabled():
            self.warpWarning.Hide()
            return
        michelle = sm.GetService('michelle')
        if michelle.IsPreparingWarp() and michelle.AreDronesOut():
            self.warpWarning.FadeIn()
        else:
            self.warpWarning.FadeOut()


def GetDronesInLocalSpace():
    ballpark = sm.GetService('michelle').GetBallpark()
    if ballpark is None:
        return []
    drones = sm.GetService('michelle').GetDrones()
    return [ drones[droneID] for droneID in drones if droneID in ballpark.slimItems and (drones[droneID].ownerID == eve.session.charid or drones[droneID].controllerID == eve.session.shipid) ]


def GetDronesInDistantSpace():
    ballpark = sm.GetService('michelle').GetBallpark()
    if ballpark is None:
        return []
    drones = sm.GetService('michelle').GetDrones()
    return [ drones[droneID] for droneID in drones if droneID not in ballpark.slimItems and (drones[droneID].ownerID == eve.session.charid or drones[droneID].controllerID == eve.session.shipid) ]


warp_warning_enabled_setting = CharSettingBool('drone_warp_warning_enabled', True)

class WarpWarning(ContainerAutoSize):
    default_alignMode = uiconst.TOTOP
    default_opacity = 0.0

    def __init__(self, **kwargs):
        super(WarpWarning, self).__init__(**kwargs)
        self.constructed = False
        self.is_active = False
        self.whiteout = None

    def layout(self):
        self.whiteout = Container(parent=self, align=uiconst.TOALL, bgColor=(1.0, 1.0, 1.0), opacity=0.5)
        Frame(bgParent=self, texturePath='res:/UI/Texture/Shared/DarkStyle/panel1Corner_Solid.png', rotation=math.pi, cornerSize=9, color=eveColor.WARNING_ORANGE, opacity=0.15)
        Sprite(name='cornerSprite', parent=self, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/Shared/DarkStyle/cornerTriSmall.png', width=5, height=5, color=eveColor.WARNING_ORANGE, opacity=0.5)
        warning_icon = Sprite(name='warningIcon', parent=self, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, width=32, height=32, left=10, top=8, texturePath='res:/UI/Texture/classes/agency/iconExclamation.png', color=eveColor.WARNING_ORANGE)
        animations.FadeTo(warning_icon, startVal=0.5, endVal=1.5, duration=0.7, loops=-1, curveType=uiconst.ANIM_WAVE)
        EveLabelMedium(name='warningLabel', parent=self, align=uiconst.TOTOP, padding=(52, 8, 8, 8), text=localization.GetByLabel('UI/Drones/WarpWarningMessage'), color=eveColor.WARNING_ORANGE)
        button_row_cont = ContainerAutoSize(parent=self, align=uiconst.TOTOP, padding=(52, 0, 8, 8))
        Button(parent=button_row_cont, align=uiconst.TOPLEFT, label=localization.GetByLabel('UI/Drones/StopAndRecall'), func=stop_and_recall_drones, args=())
        self.constructed = True

    def FadeIn(self):
        if not self.constructed:
            self.layout()
        if self.is_active:
            return
        self.is_active = True
        sm.GetService('audio').SendUIEvent('ui_warning_abandoning_drones')
        self.Show()
        animations.StopAllAnimations(self)
        animations.FadeIn(self, duration=0.3)
        animations.FadeTo(self.whiteout, startVal=0.0, endVal=1.0, duration=0.3, timeOffset=0.1, curveType=uiconst.ANIM_WAVE)

    def FadeOut(self):
        if not self.constructed:
            return
        self.is_active = False
        animations.StopAllAnimations(self.whiteout)
        animations.FadeOut(self.whiteout, duration=0.1)
        animations.FadeOut(self, duration=0.3, callback=self.Hide)


def stop_and_recall_drones():
    uicore.cmd.GetCommandAndExecute('CmdStopShip')
    ReturnToDroneBay([ drone.droneID for drone in GetDronesInLocalSpace() ])


class DroneMainGroup(Group):
    __guid__ = 'listentry.DroneMainGroup'
    isDragObject = True

    def Load(self, node):
        Group.Load(self, node)
        if node.showicon:
            self.sr.icon.state = uiconst.UI_NORMAL
            self.sr.icon.LoadTooltipPanel = LoadFavoriteTooltipPanel
            self.sr.icon.DelegateEvents(self)

    def GetDragData(self, *args):
        return [self.sr.node]


class DroneMainGroupInSpace(DroneMainGroup):

    def Load(self, node):
        super(DroneMainGroupInSpace, self).Load(node)
        utilMenu = UtilMenu(menuAlign=uiconst.TOPRIGHT, parent=self, align=uiconst.CENTERRIGHT, GetUtilMenu=node.GetUtilMenu)
        utilMenu.uniqueUiName = pConst.UNIQUE_NAME_DRONE_SETTINGS


class DroneSubGroup(Group):
    __guid__ = 'listentry.DroneSubGroup'
    isDragObject = True

    def Startup(self, *args):
        Group.Startup(self, args)
        if self.sr.fill:
            self.sr.fill.opacity = 0.9 * self.sr.fill.opacity

    def Load(self, node):
        Group.Load(self, node)
        if node.showicon:
            self.sr.icon.state = uiconst.UI_NORMAL
            self.sr.icon.LoadTooltipPanel = LoadFavoriteTooltipPanel
            self.sr.icon.DelegateEvents(self)

    def GetDragData(self, *args):
        return [self.sr.node]


def LoadFavoriteTooltipPanel(tooltipPanel, *args):
    tooltipPanel.LoadGeneric2ColumnTemplate()
    command = uicore.cmd.commandMap.GetCommandByName('CmdLaunchFavoriteDrones')
    detailedDescription = command.GetDetailedDescription()
    if detailedDescription:
        tooltipPanel.AddLabelMedium(text=detailedDescription, align=uiconst.TOPLEFT, wrapWidth=200, colSpan=tooltipPanel.columns)
    label = command.GetName()
    shortcutStr = command.GetShortcutAsString()
    labelObj, shortcutObj = tooltipPanel.AddLabelShortcut(label, shortcutStr)
    labelObj.top = shortcutObj.top = 6


def GetTypeIDForManyDrones(droneState, droneData):
    if not droneData:
        return None
    if droneState == 'inbay':
        firstDroneData = droneData[0]
        invItem, viewOnly, voucher = firstDroneData
        return invItem.typeID
    if droneState in ('inlocalspace', 'indistantspace'):
        lowPriorityDrones = [const.groupMiningDrone, const.groupSalvageDrone, const.groupUnanchoringDrone]

        def IsHigherPrioritySpaceDrone(droneData):
            droneID, typeID, ownerID, locationID = droneData
            if evetypes.GetGroupID(typeID) in lowPriorityDrones:
                return False
            return True

        priorityDrone = itertoolsext.first_or_default(droneData, predicate=IsHigherPrioritySpaceDrone, default=droneData[0])
        droneSlimItem = sm.GetService('michelle').GetItem(priorityDrone[0])
        if droneSlimItem:
            return droneSlimItem.typeID


def DropDronesInSpace(dragObj, nodes):
    if dragObj.sr.node.droneState != 'inbay':
        return
    droneWnd = DroneView.GetIfOpen()
    if droneWnd is None:
        return
    if dragObj.__guid__ in ('listentry.DroneSubGroup', 'listentry.DroneMainGroup'):
        if dragObj.__guid__ == 'listentry.DroneSubGroup':
            nodes = droneWnd.GetSubGroupContent(dragObj.sr.node)
        else:
            nodes = droneWnd.GetAllMainGroupContent(dragObj.sr.node)
    drones = [ node.invItem for node in nodes ]
    GetMenuService().LaunchDrones(drones)
