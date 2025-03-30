#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\drones\droneGroup.py
import eveicon
import evetypes
import trinity
from carbonui import TextColor, uiconst
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from carbonui.util.various_unsorted import IsUnder
from eve.client.script.ui.control.listgroup import ListGroup as Group
from eve.client.script.ui.inflight.drones import droneSignals, dronesDragData, dronesUtil
from eve.client.script.ui.inflight.drones.buttonSeperatorLine import ButtonSeperatorLine
from eve.client.script.ui.inflight.drones.droneGroupsController import GetDroneGroupsController
from eve.client.script.ui.inflight.drones.dronesDragData import HasInBayDroneIDs, HasInSpaceDroneIDs
from eve.client.script.ui.inflight.drones.dronesUtil import LoadShortcutTooltip
from eve.client.script.ui.services.menuSvcExtras import droneFunctions
from localization import GetByLabel

class DroneSubGroup(Group):
    isDragObject = True

    def Startup(self, *etc):
        super(DroneSubGroup, self).Startup(*etc)
        self.ConstructButtonCont()
        self.ConstructButtons()
        if self.sr.fill:
            self.sr.fill.opacity = 0.9 * self.sr.fill.opacity

    def Load(self, node):
        super(DroneSubGroup, self).Load(node)
        self.sr.label.rgba = TextColor.HIGHLIGHT

    def ConstructButtonCont(self):
        self.buttonCont = ContainerAutoSize(name='buttonCont', align=uiconst.TORIGHT, parent=self, state=uiconst.UI_HIDDEN, padRight=4, opacity=0.0)

    def ConstructButtons(self):
        pass

    def OnMouseEnter(self, *args):
        super(DroneSubGroup, self).OnMouseEnter(*args)
        self.ShowButtonCont()
        uicore.uilib.RegisterForTriuiEvents(uiconst.UI_MOUSEENTER, self.OnGlobalMouseEnter)

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

    def _ConstructFill(self):
        self.sr.fill = None

    def GetDroneIDs(self):
        return GetDroneGroupsController().GetDroneIDsInSubGroup(self.sr.node.droneState, self.sr.node.groupName)

    def GetDroneIDsAndTypeIDs(self):
        droneData = self.GetDronesData()
        return [ (itemID, typeID) for itemID, typeID, _, _ in droneData ]

    def GetDronesData(self):
        return GetDroneGroupsController().GetDroneDataForSubGroup(self.sr.node.droneState, self.sr.node.groupName)

    def _MoveToGroup(self, typeID, droneIDs):
        GetDroneGroupsController().MoveToGroup(evetypes.GetGroupID(typeID), self.GetGroupName(), droneIDs)

    def GetGroupName(self):
        return self.sr.node.id[1][0]

    def ShowIconGlow(self):
        self.sr.icon.outputMode = uiconst.OUTPUT_COLOR_AND_GLOW
        animations.MorphScalar(self.sr.icon, 'glowBrightness', self.sr.icon.glowBrightness, 1.0, duration=uiconst.TIME_ENTRY)

    def OnDragExit(self, dragObj, drag, *args):
        self.HideIconGlow()

    def HideIconGlow(self):
        animations.MorphScalar(self.sr.icon, 'glowBrightness', self.sr.icon.glowBrightness, 0.0, duration=uiconst.TIME_EXIT)


buttonSize = 20

class DroneSubGroupInBay(DroneSubGroup):

    def ConstructButtons(self):
        button = ButtonIcon(parent=self.buttonCont, align=uiconst.TORIGHT, width=buttonSize, iconSize=16, texturePath=eveicon.launch_drones, func=self.OnLaunchDronesButton, hint=GetByLabel('UI/Drones/LaunchDrones'), blendMode=trinity.TR2_SBM_ADD)
        button.LoadTooltipPanel = self.LoadLaunchButtonTooltipPanel

    def LoadLaunchButtonTooltipPanel(self, tooltipPanel, *args):
        if self.sr.node.isFavorite:
            return LoadShortcutTooltip(tooltipPanel, commandName='CmdLaunchFavoriteDrones')
        command = uicore.cmd.commandMap.GetCommandByName('CmdLaunchFavoriteDrones')
        tooltipPanel.LoadGeneric1ColumnTemplate()
        tooltipPanel.AddLabelMedium(text=command.GetName())

    def OnLaunchDronesButton(self, *args):
        droneFunctions.LaunchDrones(self.GetDroneIDs())

    def OnDragEnter(self, dragSource, dragData):
        super(DroneSubGroupInBay, self).OnDragEnter(dragSource, dragData)
        if HasInSpaceDroneIDs(dragData):
            droneSignals.on_in_bay_entry_drag_enter()
        else:
            droneIDs = set(dronesDragData.GetInBayDroneIDs(dragData))
            if droneIDs.difference(self.GetDroneIDs()):
                self.ShowIconGlow()

    def GetDragData(self):
        return dronesDragData.DronesInBayDragData(self.GetDroneIDs())

    def OnDropData(self, dragObj, dragData):
        self.HideIconGlow()
        inSpaceDroneIDs = dronesDragData.GetInSpaceDroneIDs(dragData)
        if inSpaceDroneIDs:
            droneFunctions.ReturnToDroneBay(inSpaceDroneIDs)
            droneSignals.on_drones_dropped_to_bay()
        inBayDroneIDs = dronesDragData.GetInBayDroneIDs(dragData)
        if inBayDroneIDs:
            self._MoveToGroup(dragData[0].GetTypeID(), inBayDroneIDs)


class DroneSubGroupInSpace(DroneSubGroup):

    def ConstructButtons(self):
        ButtonIcon(parent=self.buttonCont, align=uiconst.TORIGHT, width=buttonSize, iconSize=16, texturePath=eveicon.recall_drones, func=self.OnRecallDronesButton, hint=GetByLabel('UI/Drones/ReturnDroneToBay'), blendMode=trinity.TR2_SBM_ADD)
        ButtonSeperatorLine(parent=self.buttonCont, align=uiconst.TORIGHT)
        ButtonIcon(parent=self.buttonCont, align=uiconst.TORIGHT, width=buttonSize, iconSize=16, texturePath=eveicon.return_and_orbit, func=self.OnReturnAndOrbitButton, hint=GetByLabel('UI/Drones/ReturnDroneAndOrbit'), blendMode=trinity.TR2_SBM_ADD, padRight=4)
        primaryActionBtn = ButtonIcon(name='primaryActionBtn', parent=self.buttonCont, align=uiconst.TORIGHT, width=buttonSize, iconSize=16, texturePath=eveicon.engage_target, func=self.OnPrimaryActionButton, blendMode=trinity.TR2_SBM_ADD)
        primaryActionBtn.GetHint = self.GetPrimaryActionBtnHint

    def GetPrimaryActionBtnHint(self):
        dronesData = self.GetDronesData()
        _, typeID, _, _ = dronesData[0]
        return dronesUtil.GetPrimaryActionName(typeID)

    def OnReturnAndOrbitButton(self, *args):
        droneFunctions.ReturnAndOrbit(self.GetDroneIDs())

    def OnPrimaryActionButton(self, *args):
        droneFunctions.PerformPrimaryAction(self.GetDroneIDsAndTypeIDs())

    def OnRecallDronesButton(self, *args):
        droneFunctions.ReturnToDroneBay(self.GetDroneIDs())

    def OnDragEnter(self, dragSource, dragData):
        if HasInBayDroneIDs(dragData):
            droneSignals.on_in_space_entry_drag_enter()
        else:
            droneIDs = set(dronesDragData.GetInSpaceDroneIDs(dragData))
            if droneIDs.difference(self.GetDroneIDs()):
                self.ShowIconGlow()

    def GetDragData(self):
        return dronesDragData.DronesInSpaceDragData(self.GetDroneIDs())

    def OnDropData(self, dragObj, dragData):
        self.HideIconGlow()
        inBayDroneIDs = dronesDragData.GetInBayDroneIDs(dragData)
        if inBayDroneIDs:
            droneFunctions.LaunchDrones(inBayDroneIDs)
            droneSignals.on_drones_dropped_in_space()
        inSpaceDroneIDs = dronesDragData.GetInSpaceDroneIDs(dragData)
        if inSpaceDroneIDs:
            self._MoveToGroup(dragData[0].GetTypeID(), inSpaceDroneIDs)
