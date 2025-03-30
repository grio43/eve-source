#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\drones\droneGroupHeader.py
import dogma.attributes.format as attributeFormat
import eveicon
import trinity
import uthread2
from carbonui import TextColor, uiconst
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.control.contextMenu.menuData import MenuData
from carbonui.control.contextMenu.menuEntryData import MenuEntryData
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from carbonui.util.various_unsorted import IsUnder
from dogma.data import get_attribute
from eve.client.script.environment import invControllers
from eve.client.script.ui import eveColor
from eve.client.script.ui.control import eveLabel
from eve.client.script.ui.control.tooltips import TooltipPanel
from eve.client.script.ui.inflight.drones import droneSignals, dronesDragData
from eve.client.script.ui.inflight.drones.buttonSeperatorLine import ButtonSeperatorLine
from eve.client.script.ui.inflight.drones.droneGroupsController import GetDroneGroupsController
from eve.client.script.ui.inflight.drones.droneSettings import drones_aggressive_setting, drones_focus_fire_setting
from eve.client.script.ui.inflight.drones.dronesConst import DRONESTATE_INSPACE, DRONESTATE_INBAY
from eve.client.script.ui.inflight.drones.dronesDragData import AllDronesInBayDragData, AllDronesInSpaceDragData, HasInBayDroneIDs, HasInSpaceDroneIDs
from eve.client.script.ui.inflight.drones.dronesUtil import LoadShortcutTooltip, GetDroneIDsInBay, GetDroneIDsInSpace, GetMaxDronesInSpace, ExpandRadialMenuForInBayGroup, ExpandRadialMenuForInSpaceGroup, GetDronesInLocalSpace, GetNumberOfDronesInBay
from eve.client.script.ui.services.menuSvcExtras import droneFunctions
from eve.client.script.ui.shared.pointerTool import pointerToolConst as pConst
from eve.client.script.ui.shared.shipTree.infoBubble import SkillEntry
from eve.client.script.util import eveMisc
from eve.common.lib import appConst
from eveservices.menu import GetMenuService
from fsdBuiltData.common.iconIDs import GetIconFile
from localization import GetByLabel
from menu import MenuList, MenuLabel
from shipfitting.droneUtil import GetDroneBandwidth
from signals import Signal
BUTTON_SIZE = 20

def GetDeleteGroupMenuEntry():
    delMenuEntries = [ (groupName, DeleteGroup, (groupName,)) for groupName, groupInfo in GetDroneGroupsController().GetGroupsByName().iteritems() ]
    if delMenuEntries:
        return MenuEntryData(MenuLabel('UI/Commands/DeleteGroup'), subMenuData=delMenuEntries)


def DeleteGroup(groupName):
    GetDroneGroupsController().DeleteGroup(groupName)


class BaseDroneGroupHeader(Container):
    default_state = uiconst.UI_NORMAL
    default_height = 24
    isDragObject = True
    captionLabel = None
    __notifyevents__ = ['OnExternalDragEnded']

    def __init__(self, reserved_space_right = 0, **kwargs):
        self._reserved_space_right = reserved_space_right
        self.buttonCont = None
        super(BaseDroneGroupHeader, self).__init__(**kwargs)

    def ApplyAttributes(self, attributes):
        super(BaseDroneGroupHeader, self).ApplyAttributes(attributes)
        sm.RegisterNotify(self)
        self.isExpanded = True
        self.on_open_changed = Signal('on_open_changed')
        labelCont = self.ConstructLabelCont()
        self.icon = Sprite(parent=labelCont, align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED, pos=(4, 0, 16, 16), outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, glowBrightness=0.0)
        self.label = eveLabel.EveLabelMedium(parent=labelCont, align=uiconst.CENTERLEFT, color=TextColor.HIGHLIGHT, left=24)
        self.ConstructButtonCont()
        self.ConstructButtons()
        self.underlay = Fill(bgParent=self, color=(1, 1, 1, 0.05), outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, glowBrightness=0.0)
        self.blinkUnderlay = Fill(bgParent=self, color=(1, 1, 1, 0.0), outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, glowBrightness=0.0)
        self.UpdateIcon()
        self.UpdateLabelText()

    def ConstructLabelCont(self):
        labelCont = ContainerAutoSize(parent=self, align=uiconst.TOLEFT)
        return labelCont

    @property
    def reserved_space_right(self):
        return self._reserved_space_right

    @reserved_space_right.setter
    def reserved_space_right(self, value):
        if value != self._reserved_space_right:
            self._reserved_space_right = value
            self._update_button_cont_padding()

    def _update_button_cont_padding(self):
        if self.buttonCont is not None:
            self.buttonCont.padding = self._get_button_cont_padding()

    def _get_button_cont_padding(self):
        return (0,
         0,
         max(self._reserved_space_right, 4),
         0)

    def OnExternalDragEnded(self, *args):
        self.HideDragHighlight()

    def ShowDragHighlight(self, *args):
        animations.MorphScalar(self.underlay, 'glowBrightness', self.underlay.glowBrightness, 1.0, duration=uiconst.TIME_ENTRY)
        animations.FadeTo(self.underlay, self.underlay.opacity, 0.1, duration=uiconst.TIME_ENTRY)
        uicore.uilib.RegisterForTriuiEvents(uiconst.UI_DRAGEXIT, self.OnGlobalDragExit)

    def OnGlobalDragExit(self, obj, *args):
        self.HideDragHighlight()

    def HideDragHighlight(self, *args):
        animations.MorphScalar(self.underlay, 'glowBrightness', self.underlay.glowBrightness, 0.0, duration=uiconst.TIME_EXIT)
        animations.FadeTo(self.underlay, self.underlay.opacity, 0.05, duration=uiconst.TIME_EXIT)

    def UpdateLabelText(self):
        pass

    def OnClick(self, *args):
        super(BaseDroneGroupHeader, self).OnClick(*args)
        if self.isExpanded:
            self.SetAsCollapsed()
        else:
            self.SetAsExpanded()

    def SetAsExpanded(self):
        self._SetExpanedState(True)

    def SetAsCollapsed(self):
        self._SetExpanedState(False)

    def _SetExpanedState(self, isExpanded):
        self.isExpanded = isExpanded
        self.UpdateIcon()
        self.on_open_changed(self.isExpanded)

    def UpdateIcon(self):
        self.icon.texturePath = eveicon.caret_down if self.isExpanded else eveicon.caret_right

    def ConstructButtonCont(self):
        self.buttonCont = ContainerAutoSize(name='buttonCont', align=uiconst.TORIGHT, parent=self, state=uiconst.UI_HIDDEN, padding=self._get_button_cont_padding(), opacity=0.0)

    def ConstructButtons(self):
        pass

    def OnMouseEnter(self, *args):
        super(BaseDroneGroupHeader, self).OnMouseEnter(*args)
        self.ShowButtonCont()
        uicore.uilib.RegisterForTriuiEvents(uiconst.UI_MOUSEENTER, self.OnGlobalMouseEnter)
        animations.MorphScalar(self.icon, 'glowBrightness', self.icon.glowBrightness, 1.0, duration=uiconst.TIME_ENTRY)

    def OnMouseExit(self, *args):
        super(BaseDroneGroupHeader, self).OnMouseExit(*args)
        animations.MorphScalar(self.icon, 'glowBrightness', self.icon.glowBrightness, 0.0, duration=uiconst.TIME_EXIT)

    def OnGlobalMouseEnter(self, obj, *args):
        if obj and not (IsUnder(obj, self) or obj == self):
            self.HideButtonCont()
            return False
        else:
            return True

    def ShowButtonCont(self):
        self.buttonCont.Show()
        animations.FadeTo(self.buttonCont, self.buttonCont.opacity, 1.0, duration=0.1)

    def HideButtonCont(self):
        animations.FadeTo(self.buttonCont, self.buttonCont.opacity, 0.0, duration=0.1, callback=self.buttonCont.Hide)

    def GetDragData(self, *args):
        pass

    def GetDroneIDs(self):
        pass

    def OnMouseDown(self, *args):
        uthread2.StartTasklet(self.ExpandRadialMenu)

    def ExpandRadialMenu(self):
        pass

    def Blink(self):
        duration = 0.6
        animations.MorphScalar(self.blinkUnderlay, 'glowBrightness', 1.0, 0.0, duration=duration)
        animations.MorphScalar(self.blinkUnderlay, 'opacity', 0.25, 0.0, duration=duration)


class DroneGroupHeaderInBay(BaseDroneGroupHeader):

    def ApplyAttributes(self, attributes):
        super(DroneGroupHeaderInBay, self).ApplyAttributes(attributes)
        droneSignals.on_in_bay_entry_drag_enter.connect(self.ShowDragHighlight)
        droneSignals.on_drones_dropped_to_bay.connect(self.Blink)

    def ConstructLabelCont(self):
        labelCont = ContainerAutoSize(parent=self, align=uiconst.TOLEFT, state=uiconst.UI_NORMAL)
        labelCont.MakeDragObject()
        labelCont.GetDragData = self.GetDragData
        labelCont.GetMenu = self.GetMenu
        labelCont.OnDropData = self.OnDropData
        labelCont.OnDragEnter = self.OnDragEnter
        labelCont.OnClick = self.OnClick
        labelCont.OnMouseDown = self.OnMouseDown
        return labelCont

    def GetMenu(self):
        m = MenuList([None])
        delMenuEntry = GetDeleteGroupMenuEntry()
        if delMenuEntry:
            m.append(delMenuEntry)
        data = GetDroneGroupsController().GetDroneDataForMainGroup(DRONESTATE_INBAY)
        if data:
            m += GetMenuService().InvItemMenu(data).filter([MenuLabel('UI/Inventory/ItemActions/BuyThisType'),
             MenuLabel('UI/Inventory/ItemActions/AddTypeToMarketQuickbar'),
             MenuLabel('UI/Inventory/ItemActions/ViewTypesMarketDetails'),
             MenuLabel('UI/Inventory/ItemActions/FindInContracts')])
        return m

    def ConstructButtons(self):
        button = ButtonIcon(parent=self.buttonCont, align=uiconst.TORIGHT, width=BUTTON_SIZE, iconSize=16, texturePath=eveicon.launch_drones, func=self.OnLaunchDronesButton, hint=GetByLabel('UI/Drones/LaunchDrones'), blendMode=trinity.TR2_SBM_ADD)
        button.LoadTooltipPanel = self.LoadLaunchDronesTooltipPanel

    def LoadLaunchDronesTooltipPanel(self, tooltipPanel, *args):
        if not GetDroneGroupsController().GetFavoriteGroupDroneIDsInBayOrSpace():
            tooltipPanel.LoadGeneric2ColumnTemplate()
            shortcut = uicore.cmd.GetShortcutStringByFuncName('CmdLaunchFavoriteDrones')
            tooltipPanel.AddLabelShortcut(GetByLabel('UI/Drones/LaunchDrones'), shortcut)

    def OnLaunchDronesButton(self, *args):
        droneInvItems = [ item for item in invControllers.ShipDroneBay().GetItems() if item.itemID in self.GetDroneIDs() ]
        if droneInvItems:
            eveMisc.LaunchFromShip(droneInvItems)

    def GetDroneIDs(self):
        return GetDroneIDsInBay()

    def UpdateLabelText(self):
        self.label.text = '%s (%s)' % (GetByLabel('UI/Inflight/Drone/DronesInBay'), GetNumberOfDronesInBay())

    def ExpandRadialMenu(self):
        droneData = GetDroneGroupsController().GetDroneDataForMainGroup(DRONESTATE_INBAY)
        if droneData:
            ExpandRadialMenuForInBayGroup(self, self.label.text, droneData)

    def GetDragData(self, *args):
        return AllDronesInBayDragData()

    def OnDragEnter(self, dragSource, dragData):
        if HasInSpaceDroneIDs(dragData):
            droneSignals.on_in_bay_entry_drag_enter()

    def OnDropData(self, dragSource, dragData):
        droneIDs = dronesDragData.GetInSpaceDroneIDs(dragData)
        if droneIDs:
            droneFunctions.ReturnToDroneBay(droneIDs)
            droneSignals.on_drones_dropped_to_bay()


class DroneGroupHeaderInSpace(BaseDroneGroupHeader):

    def ApplyAttributes(self, attributes):
        super(DroneGroupHeaderInSpace, self).ApplyAttributes(attributes)
        droneSignals.on_in_space_entry_drag_enter.connect(self.ShowDragHighlight)
        droneSignals.on_drones_dropped_in_space.connect(self.Blink)

    def ConstructButtons(self):
        button = ButtonIcon(parent=self.buttonCont, align=uiconst.TORIGHT, width=BUTTON_SIZE, iconSize=16, texturePath=eveicon.recall_drones, func=self.OnRecallDronesButton, blendMode=trinity.TR2_SBM_ADD)
        button.LoadTooltipPanel = lambda tooltipPanel, *args: LoadShortcutTooltip(tooltipPanel, commandName='CmdDronesReturnToBay')
        ButtonSeperatorLine(parent=self.buttonCont, align=uiconst.TORIGHT)
        button = ButtonIcon(parent=self.buttonCont, align=uiconst.TORIGHT, width=BUTTON_SIZE, iconSize=16, texturePath=eveicon.return_and_orbit, func=self.OnReturnAndOrbitButton, blendMode=trinity.TR2_SBM_ADD, padRight=4)
        button.LoadTooltipPanel = lambda tooltipPanel, *args: LoadShortcutTooltip(tooltipPanel, commandName='CmdDronesReturnAndOrbit')
        button = ButtonIcon(parent=self.buttonCont, align=uiconst.TORIGHT, width=BUTTON_SIZE, iconSize=16, texturePath=eveicon.engage_target, func=self.OnEngageButton, blendMode=trinity.TR2_SBM_ADD)
        button.LoadTooltipPanel = lambda tooltipPanel, *args: LoadShortcutTooltip(tooltipPanel, commandName='CmdDronesEngage')
        settingsButton = ButtonIcon(menuAlign=uiconst.TOPRIGHT, parent=self.buttonCont, align=uiconst.TORIGHT, width=BUTTON_SIZE, texturePath=eveicon.settings, padRight=4, blendMode=trinity.TR2_SBM_ADD, uniqueUiName=pConst.UNIQUE_NAME_DRONE_SETTINGS)
        settingsButton.expandOnLeft = True
        settingsButton.GetMenu = self.GetSettingsMenu

    def GetSettingsMenu(self, *args):
        m = MenuData()
        m.AddCheckbox(text=GetByLabel('UI/Drones/AutoAttack'), setting=drones_aggressive_setting, hint=GetByLabel('UI/Drones/AutoAttackHint'))
        m.AddCheckbox(text=GetByLabel('UI/Drones/AttackModeFocusFire'), setting=drones_focus_fire_setting, hint=GetByLabel('UI/Drones/AttackModeFocusFireHint'))
        return m

    def GetMenu(self):
        m = MenuList([None])
        delMenuEntry = GetDeleteGroupMenuEntry()
        if delMenuEntry:
            m.append(delMenuEntry)
        data = GetDroneGroupsController().GetDroneDataForMainGroup(DRONESTATE_INSPACE)
        if data:
            m += GetMenuService().DroneMenu(data)
        return m

    def OnReturnAndOrbitButton(self, *args):
        droneFunctions.ReturnAndOrbit(self.GetDroneIDs())

    def OnEngageButton(self, *args):
        droneFunctions.PerformPrimaryAction(self.GetDroneItemAndTypeIDs())

    def OnRecallDronesButton(self, *args):
        droneFunctions.ReturnToDroneBay(self.GetDroneIDs())

    def GetDroneIDs(self):
        return GetDroneIDsInSpace()

    def GetDroneItemAndTypeIDs(self):
        return [ (drone.droneID, drone.typeID) for drone in GetDronesInLocalSpace() ]

    def UpdateLabelText(self):
        self.label.text = '%s (%s/%s)' % (GetByLabel('UI/Inflight/Drone/DronesInSpace'), len(self.GetDroneIDs()), GetMaxDronesInSpace())

    def ExpandRadialMenu(self):
        droneData = GetDroneGroupsController().GetDroneDataForMainGroup(DRONESTATE_INSPACE)
        if droneData:
            ExpandRadialMenuForInSpaceGroup(self, self.label.text, droneData)

    def GetDragData(self, *args):
        return AllDronesInSpaceDragData()

    def OnDragEnter(self, dragSource, dragData):
        if HasInBayDroneIDs(dragData):
            droneSignals.on_in_space_entry_drag_enter()

    def OnDropData(self, dragSource, dragData):
        droneIDs = dronesDragData.GetInBayDroneIDs(dragData)
        if droneIDs:
            droneFunctions.LaunchDrones(droneIDs)
            droneSignals.on_drones_dropped_in_space()

    def ConstructTooltipPanel(self):
        return DroneGroupHeaderInSpaceTooltipPanel()


class DroneGroupHeaderInSpaceTooltipPanel(TooltipPanel):
    default_margin = 16
    default_pointerDirection = uiconst.POINT_RIGHT_2

    def ApplyAttributes(self, attributes):
        super(DroneGroupHeaderInSpaceTooltipPanel, self).ApplyAttributes(attributes)
        drones = {drone.droneID:1 for drone in GetDronesInLocalSpace()}
        text = GetByLabel('UI/Inflight/Drone/MaxDronesInSpace', numDrones=len(drones), numMax=GetMaxDronesInSpace())
        self.AddLabelMedium(text=text, colSpan=2, wrapWidth=250)
        self.AddRow(rowClass=SkillEntry, typeID=appConst.typeDrones, showLevel=False, cellPadding=(0, 0))
        self.AddSpacer(height=8)
        used, total = GetDroneBandwidth(session.shipid, sm.GetService('clientDogmaIM').GetDogmaLocation(), drones)
        texturePath = GetIconFile(attributeFormat.GetIconID(appConst.attributeDroneBandwidth))
        attributeType = get_attribute(appConst.attributeDroneBandwidth)
        totalText = attributeFormat.GetFormatAndValue(attributeType, total)
        text = '<color=%s>%s</color> %s/%s' % (eveColor.LED_GREY_HEX,
         GetByLabel('UI/Inflight/Drone/BandwidthUsed'),
         int(used),
         totalText)
        self.AddIconLabel(texturePath, text)
