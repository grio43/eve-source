#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\overview\overviewScrollEntry.py
import math
import evetypes
import gametime
import localization
import uthread
from carbonui import uiconst
from carbonui.control.scrollentries import SE_BaseClassCore
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from carbonui.util.color import Color
from eve.client.script.parklife import states as state
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.control.themeColored import FillThemeColored
from eve.client.script.ui.inflight.bracketsAndTargets.bracketVarious import GetIconColor
from eve.client.script.ui.inflight.overViewLabel import OverviewLabel
from eve.client.script.ui.inflight.overview.overviewConst import COLUMNMARGIN, COLUMN_ANGULARVELOCITY, COLUMN_DISTANCE, COLUMN_ICON, COLUMN_RADIALVELOCITY, COLUMN_TRANSVERSALVELOCITY, COLUMN_VELOCITY, FAINT_ENTRY_CATEGORIES, INVISIBLE_SPACEOBJECT_ICON, KILOMETERS10, KILOMETERS10000000, RIGHTALIGNEDCOLUMNS
from eve.client.script.ui.inflight.overview.overviewUtil import IsFleetMember
from eve.client.script.ui.inflight.overview.spaceObjectIcon import SpaceObjectIcon
from eve.client.script.ui.shared.fleet.fleetBroadcastConst import flagToName, iconsByBroadcastType
from eve.client.script.ui.shared.stateFlag import GetExtraInfoForNode
from eve.client.script.util.bubble import InBubble
from eve.common.lib import appConst as const
from eveexceptions import ExceptionEater
from eveservices.menu import GetMenuService
from homestation import client as homestation
from inventorycommon.util import IsNPC
from spacecomponents.common.componentConst import ORBITAL_SKYHOOK
from spacecomponents.common.helper import HasEntityStandingsComponent
import telemetry
import blue
from stargate.client.const import EMANATION_GATE_AVAILABLE, EMANATION_GATE_UNAVAILABLE

class OverviewScrollEntry(SE_BaseClassCore):
    __guid__ = 'listentry.OverviewScrollEntry'
    __notifyevents__ = []
    ENTRYHEIGHT = 24
    typeID = None
    hostileIndicator = None
    attackingMeIndicator = None
    myActiveTargetIndicator = None
    targetingIndicator = None
    flagIcon = None
    flagIconBackground = None
    flagBackground = None
    fleetBroadcastIcon = None
    fleetBroadcastID = None
    loadedIconAndBackgroundFlags = None
    loadedEwarGraphicIDs = None
    rightAlignedIconContainer = None
    selectionSprite = None
    globalMaxWidth = None
    hasLoaded = False

    def ApplyAttributes(self, attributes):
        super(OverviewScrollEntry, self).ApplyAttributes(attributes)
        self.mainIcon = None
        self.sr.flag = None
        self.sr.bgColor = None
        self.columnLabels = []
        self.ewarIcons = {}

    @telemetry.ZONE_METHOD
    def Startup(self, *args):
        node = self.sr.node
        self.updateItem = node.updateItem
        self.itemID = node.itemID
        self.stateItemID = node.itemID
        slimItem = node.slimItem()
        ball = node.ball()
        if not (slimItem and ball):
            return
        self.typeID = slimItem.typeID
        self._ConstructMainIcon(ball, slimItem)
        selected, hilited = sm.GetService('stateSvc').GetStates(self.stateItemID, [state.selected, state.mouseOver])
        if selected:
            self.ShowSelected()
        if hilited:
            self.ShowHilite()
        elif uicore.uilib.mouseOver is not self:
            self.HideHilite()
        self.UpdateFleetBroadcast()

    def _ConstructMainIcon(self, ball, slimItem):
        self.mainIcon = SpaceObjectIcon(name='mainIcon', parent=self, align=uiconst.CENTERLEFT, left=3, typeID=self.typeID)
        self.mainIcon.top = -(self.height % 2)
        self.mainIcon.LoadTooltipPanel = self.LoadIconTooltipPanel
        self.mainIcon.GetTooltipPointer = self.GetIconTooltipPointer
        self.mainIcon.DelegateEvents(self)
        self.mainIcon.UpdateSpaceObjectIcon(slimItem, ball)
        self.mainIcon.UpdateSpaceObjectState(slimItem, ball)

    @telemetry.ZONE_METHOD
    def Load(self, node):
        with ExceptionEater("Exception during overview's Load"):
            self.hasLoaded = True
            self.UpdateColumns()
            if (node.iconAndBackgroundFlags,
             node.useSmallColorTags,
             node.hasDockingRights,
             node.isHomeStation,
             node.gateLockValue) != self.loadedIconAndBackgroundFlags:
                slimItem = node.slimItem()
                if not slimItem:
                    return
                self.UpdateFlagAndBackground(slimItem)
            if node.ewarGraphicIDs != self.loadedEwarGraphicIDs:
                self.UpdateEwar()

    def _OnSizeChange_NoBlock(self, displayWidth, displayHeight):
        self.SetGlobalMaxWidth()

    def SetGlobalMaxWidth(self):
        if self.rightAlignedIconContainer and self.rightAlignedIconContainer.width:
            globalMaxWidth = self.width - self.rightAlignedIconContainer.width - 6
        else:
            globalMaxWidth = None
        self.globalMaxWidth = globalMaxWidth
        for each in self.columnLabels:
            each.globalMaxWidth = globalMaxWidth

    def CreateRightAlignedIconContainer(self):
        if self.rightAlignedIconContainer is None:
            self.rightAlignedIconContainer = Container(parent=self, name='rightAlignedIconContainer', align=uiconst.CENTERRIGHT, width=200, height=16, state=uiconst.UI_PICKCHILDREN, idx=0)
        return self.rightAlignedIconContainer

    def UpdateRightAlignedIconContainerSize(self):
        if self.rightAlignedIconContainer:
            preWidth = self.rightAlignedIconContainer.width
            self.rightAlignedIconContainer.width = newWidth = sum([ each.width for each in self.rightAlignedIconContainer.children if each.display ])
            if preWidth != newWidth:
                self.SetGlobalMaxWidth()

    @telemetry.ZONE_METHOD
    def UpdateFleetBroadcast(self):
        broadcastID, broadcastFlag, broadcastData = sm.GetService('fleet').GetCurrentFleetBroadcastOnItem(self.itemID)
        if broadcastID != self.fleetBroadcastID:
            if broadcastID is None:
                if self.fleetBroadcastIcon:
                    self.fleetBroadcastIcon.Close()
                    self.fleetBroadcastIcon = None
                    self.UpdateRightAlignedIconContainerSize()
                self.fleetBroadcastType = self.fleetBroadcastID = None
                return
            broadcastType = flagToName[broadcastFlag]
            if broadcastType in ('EnemySpotted', 'NeedBackup', 'InPosition', 'HoldPosition'):
                inBubble = InBubble(self.itemID)
                if not inBubble:
                    if self.fleetBroadcastID is not None:
                        if self.fleetBroadcastIcon:
                            self.fleetBroadcastIcon.Close()
                            self.fleetBroadcastIcon = None
                        self.fleetBroadcastType = self.fleetBroadcastID = None
                    return
            self.fleetBroadcastType = broadcastType
            self.fleetBroadcastID = broadcastID
            if not self.fleetBroadcastIcon:
                self.fleetBroadcastIcon = Icon(name='fleetBroadcastIcon', parent=self.CreateRightAlignedIconContainer(), align=uiconst.TORIGHT, pos=(0, 0, 16, 16), state=uiconst.UI_DISABLED)
            icon = iconsByBroadcastType[broadcastType]
            self.fleetBroadcastIcon.LoadIcon(icon)
            self.UpdateRightAlignedIconContainerSize()

    def UpdateName(self, slimItem):
        typeID = getattr(slimItem, 'typeID', None)
        if typeID:
            self.name = 'scrollentry_{typeID}'.format(typeID=typeID)

    @telemetry.ZONE_METHOD
    def UpdateFlagAndBackground(self, slimItem, *args):
        if self.destroyed or not self.updateItem or slimItem is None:
            return
        node = self.sr.node
        self.loadedIconAndBackgroundFlags = (node.iconAndBackgroundFlags,
         node.useSmallColorTags,
         node.hasDockingRights,
         node.isHomeStation,
         node.gateLockValue)
        self.UpdateName(slimItem)
        try:
            if slimItem.groupID != const.groupAgentsinSpace and (slimItem.ownerID and IsNPC(slimItem.ownerID) or slimItem.charID and IsNPC(slimItem.charID)) and not node.isHomeStation and not node.hasDockingRights and not node.gateLockValue:
                self.mainIcon.SetIconFlag(-1)
                if self.flagBackground:
                    self.flagBackground.Close()
                    self.flagBackground = None
            else:
                node = self.sr.node
                stateSvc = sm.GetService('stateSvc')
                iconFlag, backgroundFlag = node.iconAndBackgroundFlags
                self.mainIcon.SetIconFlag(iconFlag, extraInfo=GetExtraInfoForNode(node))
                if backgroundFlag and backgroundFlag != -1:
                    r, g, b, a = stateSvc.GetStateBackgroundColor(backgroundFlag)
                    opacityModifier = 0.125 if slimItem.categoryID in FAINT_ENTRY_CATEGORIES else 0.5
                    a = a * opacityModifier
                    if not self.flagBackground:
                        self.flagBackground = Fill(name='bgColor', parent=self, state=uiconst.UI_DISABLED, color=(r,
                         g,
                         b,
                         a))
                    else:
                        self.flagBackground.SetRGBA(r, g, b, a)
                    blink = stateSvc.GetStateBackgroundBlink(backgroundFlag)
                    if blink:
                        if not self.flagBackground.HasAnimation('color'):
                            uicore.animations.FadeTo(self.flagBackground, startVal=0.0, endVal=a, duration=0.75, loops=uiconst.ANIM_REPEAT, curveType=uiconst.ANIM_WAVE)
                    else:
                        self.flagBackground.StopAnimations()
                elif self.flagBackground:
                    self.flagBackground.Close()
                    self.flagBackground = None
                self.TryCorrectHostileUI()
        except AttributeError:
            if not self.destroyed:
                raise

    @telemetry.ZONE_METHOD
    def UpdateFlagPositions(self, *args, **kwds):
        pass

    @telemetry.ZONE_METHOD
    def UpdateColumns(self):
        node = self.sr.node
        haveIcon = False
        currentLabels = []
        columnOffset = 0
        currentColumns = node.columns
        for columnID in currentColumns:
            columnWidth = node.columnWidths[columnID]
            if columnID == COLUMN_ICON:
                if self.mainIcon:
                    self.mainIcon.left = columnOffset + 3
                    self.UpdateIconColor()
                    self.mainIcon.state = uiconst.UI_NORMAL
                columnOffset += columnWidth
                haveIcon = True
                continue
            displayValue = self.GetColumnDisplayValue(node, columnID)
            if not displayValue:
                columnOffset += columnWidth
                continue
            label = None
            if self.columnLabels:
                label = self.columnLabels.pop(0)
                if label.destroyed:
                    label = None
            if not label:
                label = OverviewLabel(parent=self, align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED, idx=0, fontSize=node.fontSize, typeID=self.typeID)
            columnHint = node.get('hint_' + columnID, None)
            if columnHint:
                label.state = uiconst.UI_NORMAL
            else:
                label.state = uiconst.UI_DISABLED
            label.columnWidth = columnWidth - COLUMNMARGIN * 2
            label.text = displayValue
            label.rightAligned = columnID in RIGHTALIGNEDCOLUMNS
            label.columnPosition = columnOffset + COLUMNMARGIN
            label.globalMaxWidth = self.globalMaxWidth
            label.hint = columnHint
            label.stateItemID = self.stateItemID
            columnOffset += columnWidth
            currentLabels.append(label)

        if not haveIcon and self.mainIcon:
            self.mainIcon.state = uiconst.UI_HIDDEN
        if self.columnLabels:
            while self.columnLabels:
                label = self.columnLabels.pop()
                label.Close()

        self.columnLabels = currentLabels

    def GetRadialMenuIndicator(self, create = True, *args):
        indicator = getattr(self, 'radialMenuIndicator', None)
        if indicator and not indicator.destroyed:
            return indicator
        if not create:
            return
        self.radialMenuIndicator = FillThemeColored(bgParent=self, name='radialMenuIndicator', colorType=uiconst.COLORTYPE_UIHILIGHT)
        return self.radialMenuIndicator

    def ShowRadialMenuIndicator(self, slimItem, *args):
        indicator = self.GetRadialMenuIndicator(create=True)
        indicator.display = True

    def HideRadialMenuIndicator(self, slimItem, *args):
        indicator = self.GetRadialMenuIndicator(create=False)
        if indicator:
            indicator.display = False

    @classmethod
    def GetColumnDisplayValue(cls, node, columnID):
        if columnID == COLUMN_DISTANCE:
            return cls._GetColumnValueDistance(node)
        elif columnID == COLUMN_ANGULARVELOCITY:
            return cls._GetColumnValueAngularVelocity(node)
        elif columnID == COLUMN_VELOCITY:
            return cls._GetColumnValueVelocity(node)
        elif columnID == COLUMN_RADIALVELOCITY:
            return cls._GetColumnValueRadialVelocity(node)
        elif columnID == COLUMN_TRANSVERSALVELOCITY:
            return cls._GetColumnValueTransversalVelocity(node)
        else:
            return node.Get('display_' + columnID, None)

    @classmethod
    def _GetColumnValueTransversalVelocity(cls, node):
        sortValue = node.rawTransveralVelocity
        if sortValue is not None:
            currentTransveralVelocity = int(sortValue)
            if currentTransveralVelocity != node.lastFormattedTransveralVelocity:
                node.display_TRANSVERSALVELOCITY = FMTFUNCTION(currentTransveralVelocity, useGrouping=True)
                node.lastFormattedTransveralVelocity = currentTransveralVelocity
        return node.display_TRANSVERSALVELOCITY or u'-'

    @classmethod
    def _GetColumnValueRadialVelocity(cls, node):
        sortValue = node.rawRadialVelocity
        if sortValue is not None:
            currentRadialVelocity = int(sortValue)
            if currentRadialVelocity != node.lastFormattedRadialVelocity:
                node.display_RADIALVELOCITY = FMTFUNCTION(currentRadialVelocity, useGrouping=True)
                node.lastFormattedRadialVelocity = currentRadialVelocity
        return node.display_RADIALVELOCITY or u'-'

    @classmethod
    def _GetColumnValueVelocity(cls, node):
        sortValue = node.rawVelocity
        if sortValue is not None:
            currentVelocity = int(sortValue)
            if currentVelocity != node.lastFormattedVelocity:
                node.display_VELOCITY = FMTFUNCTION(currentVelocity, useGrouping=True)
                node.lastFormattedVelocity = currentVelocity
        return node.display_VELOCITY or u'-'

    @classmethod
    def _GetColumnValueAngularVelocity(cls, node):
        sortValue = node.rawAngularVelocity
        if sortValue is not None:
            currentAngularVelocity = round(sortValue, 7)
            value = currentAngularVelocity * 180.0 / math.pi
            node.display_ANGULARVELOCITY = FMTFUNCTION(value, useGrouping=True)
            node.lastFormattedAngularVelocity = currentAngularVelocity
        return node.display_ANGULARVELOCITY or u'-'

    @classmethod
    def _GetColumnValueDistance(cls, node):
        surfaceDist = OverviewScrollEntry._GetSurfaceDistance(node)
        if surfaceDist is None:
            return u''
        if surfaceDist < KILOMETERS10:
            currentDist = int(round(surfaceDist))
            if currentDist != node.lastFormattedDistance:
                distanceText = get_distance_in_meters(FMTFUNCTION(currentDist, useGrouping=True))
                node.display_DISTANCE = distanceText
                node.lastFormattedDistance = currentDist
        elif surfaceDist < KILOMETERS10000000:
            currentDist = long(round(surfaceDist / 1000.0))
            if currentDist != node.lastFormattedDistance:
                distanceText = get_distance_in_kilometers(FMTFUNCTION(currentDist, useGrouping=True))
                node.display_DISTANCE = distanceText
                node.lastFormattedDistance = currentDist
        else:
            currentDist = round(surfaceDist / const.AU, 1)
            if currentDist != node.lastFormattedDistance:
                distanceText = get_distance_in_au(FMTFUNCTION(currentDist, useGrouping=True, decimalPlaces=1))
                node.display_DISTANCE = distanceText
                node.lastFormattedDistance = currentDist
        return node.display_DISTANCE or u''

    @classmethod
    def _GetSurfaceDistance(cls, node):
        ball = node.ball()
        if ball and ball.ballpark:
            dist = ball.GetVectorAt(gametime.GetSimTime()).Length()
            egoBall = ball.ballpark.GetBall(ball.ballpark.ego)
            return max(dist - ball.radius - egoBall.radius, 0)
        else:
            return node.rawDistance

    @telemetry.ZONE_METHOD
    def UpdateEwar(self):
        node = self.sr.node
        ewarGraphicIDs = node.ewarGraphicIDs
        self.loadedEwarGraphicIDs = ewarGraphicIDs
        for graphicID, icon in self.ewarIcons.iteritems():
            if not ewarGraphicIDs or graphicID not in ewarGraphicIDs:
                icon.state = uiconst.UI_HIDDEN

        if ewarGraphicIDs:
            for graphicID in ewarGraphicIDs:
                if graphicID in self.ewarIcons:
                    self.ewarIcons[graphicID].state = uiconst.UI_NORMAL
                else:
                    icon = Icon(parent=self.CreateRightAlignedIconContainer(), align=uiconst.TORIGHT, state=uiconst.UI_NORMAL, width=16, hint=node.ewarHints[graphicID], graphicID=graphicID, ignoreSize=True)
                    self.ewarIcons[graphicID] = icon

        self.UpdateRightAlignedIconContainerSize()

    def OnStateChange(self, itemID, flag, status, *args):
        if self.stateItemID != itemID:
            return
        if flag == state.mouseOver:
            self.Hilite(status)
        elif flag == state.selected:
            if status:
                self.ShowSelected()
            else:
                self.ShowDeselected()
        elif flag == state.threatTargetsMe:
            attacking, = sm.StartService('stateSvc').GetStates(itemID, [state.threatAttackingMe])
            if attacking:
                self.Attacking(True)
            else:
                self.Hostile(status)
        elif flag == state.threatAttackingMe:
            self.Attacking(status)
            if not status:
                hostile, = sm.StartService('stateSvc').GetStates(itemID, [state.threatTargetsMe])
                self.Hostile(hostile)
        elif flag == state.targeted:
            self.Targeted(status)
        elif flag == state.targeting:
            self.Targeting(status)
        elif flag == state.activeTarget:
            self.ActiveTarget(status)
        elif flag == state.flagWreckAlreadyOpened:
            self.UpdateIconColor()
        elif flag == state.flagWreckEmpty:
            self.UpdateIcon()
        else:
            broadcastDataName = flagToName.get(flag, None)
            if broadcastDataName is not None:
                self.UpdateFleetBroadcast()

    def TryCorrectHostileUI(self):
        if not self.mainIcon or not self.mainIcon.hostileIndicator:
            return
        isFleetMember = IsFleetMember(self.sr.node.slimItem())
        self.mainIcon.SetHostileIndicatorColor(isFleetMember)

    @telemetry.ZONE_METHOD
    def Hostile(self, state, *args, **kwds):
        fleetMember = IsFleetMember(self.sr.node.slimItem())
        self.mainIcon.SetHostileState(state, fleetMember)

    def Attacking(self, state):
        self.mainIcon.SetAttackingState(state)
        self.UpdateIconColor()

    @telemetry.ZONE_METHOD
    def Targeting(self, state):
        self.mainIcon.SetTargetingState(state)

    def Targeted(self, activestate, *args, **kwds):
        if activestate and self.targetingIndicator:
            self.targetingIndicator.Close()
            self.targetingIndicator = None
        self.mainIcon.SetTargetedByMeState(activestate)

    def ActiveTarget(self, activestate):
        if activestate and self.targetingIndicator:
            self.targetingIndicator.Close()
            self.targetingIndicator = None
        self.mainIcon.SetActiveTargetState(activestate)

    def Hilite(self, isHovered):
        if isHovered:
            self.ShowHilite()
        else:
            self.HideHilite()

    def Select(self, *args):
        pass

    def Deselect(self, *args):
        pass

    def ShowSelected(self, *args):
        SE_BaseClassCore.Select(self, *args)

    def ShowDeselected(self, *args):
        SE_BaseClassCore.Deselect(self, *args)

    @telemetry.ZONE_METHOD
    def UpdateIcon(self, *args, **kwds):
        slimItem = self.sr.node.slimItem()
        ball = self.sr.node.ball()
        if slimItem and ball:
            self.mainIcon.UpdateSpaceObjectIcon(slimItem, ball)

    @telemetry.ZONE_METHOD
    def UpdateIconColor(self):
        if self.destroyed:
            return
        node = self.sr.node
        slimItem = node.slimItem()
        if not slimItem:
            return
        if node.iconColor and not HasEntityStandingsComponent(slimItem.typeID):
            iconColor = node.iconColor
        else:
            iconColor, colorSortValue = GetIconColor(slimItem, getSortValue=True)
            if node.sortIconIndex is not None:
                node.sortValue[node.sortIconIndex][1] = colorSortValue
            node.iconColor = iconColor
        if slimItem.groupID in (const.groupWreck, const.groupSpawnContainer) and sm.GetService('wreck').IsViewedWreck(slimItem.itemID):
            iconColor = Color(*iconColor).SetBrightness(0.55).GetRGBA()
        self.mainIcon.SetIconColor(iconColor)

    def OnDblClick(self, *args):
        if uicore.cmd.IsSomeCombatCommandLoaded():
            return
        slimItem = self.sr.node.slimItem()
        if slimItem:
            GetMenuService().Activate(slimItem)

    def OnMouseEnter(self, *args):
        SE_BaseClassCore.OnMouseEnter(self, *args)
        sm.GetService('stateSvc').SetState(self.sr.node.itemID, state.mouseOver, 1)

    def OnMouseExit(self, *args):
        SE_BaseClassCore.OnMouseExit(self, *args)
        sm.GetService('stateSvc').SetState(self.sr.node.itemID, state.mouseOver, 0)

    def LoadIconTooltipPanel(self, tooltipPanel, *args):
        if self.sr.node.slimItem:
            slimItem = self.sr.node.slimItem()
            ball = self.sr.node.ball()
            if not (slimItem and ball):
                return
            stateService = sm.GetService('stateSvc')
            tooltipPanel.LoadGeneric3ColumnTemplate()
            iconObj = SpaceObjectIcon(typeID=slimItem.typeID)
            iconObj.UpdateSpaceObjectIcon(slimItem, ball)
            iconObj.UpdateSpaceObjectIconColor(slimItem)
            iconObj.UpdateSpaceObjectState(slimItem, ball)
            iconObj.UpdateSpaceObjectFlagAndBackgroundColor(slimItem, ball)
            uthread.new(self.UpdateTooltipIconThread, iconObj)
            if iconObj.iconSprite.texturePath != INVISIBLE_SPACEOBJECT_ICON:
                tooltipPanel.AddCell(iconObj, cellPadding=(-5, 0, 6, 0))
            else:
                tooltipPanel.AddSpacer(width=1, height=1)
            tooltipPanel.AddLabelMedium(text=evetypes.GetGroupNameByGroup(slimItem.groupID), align=uiconst.CENTERLEFT, bold=True, colSpan=tooltipPanel.columns - 1)
            attacking, hostile = stateService.GetStates(slimItem.itemID, [state.threatAttackingMe, state.threatTargetsMe])
            if attacking:
                tooltipPanel.AddCell()
                tooltipPanel.AddLabelMedium(text=localization.GetByLabel('Tooltips/Overview/HostileAction'), align=uiconst.CENTERLEFT, colSpan=tooltipPanel.columns - 1)
            elif hostile:
                tooltipPanel.AddCell()
                tooltipPanel.AddLabelMedium(text=localization.GetByLabel('Tooltips/Overview/TargetLock'), align=uiconst.CENTERLEFT, colSpan=tooltipPanel.columns - 1)
            iconHint = iconObj.iconHint
            if iconHint:
                tooltipPanel.AddCell()
                tooltipPanel.AddLabelMedium(text=iconHint, align=uiconst.CENTERLEFT, colSpan=tooltipPanel.columns - 1)
            flagStateOwnerHint = iconObj.flagStateOwnerHint if slimItem.categoryID == const.categoryStructure else None
            flagStateHint = flagStateOwnerHint or iconObj.flagStateHint
            if flagStateHint:
                tooltipPanel.AddCell()
                tooltipPanel.AddLabelMedium(text=flagStateHint, align=uiconst.CENTERLEFT, colSpan=tooltipPanel.columns - 1)
            colorHint = iconObj.iconColorHint
            if colorHint:
                tooltipPanel.AddCell()
                tooltipPanel.AddLabelMedium(text=colorHint, align=uiconst.CENTERLEFT, colSpan=tooltipPanel.columns - 1)
            self.AddTypeSpecificInfoToTooltip(slimItem, tooltipPanel)
            if self.sr.node.isHomeStation:
                tooltipPanel.AddCell()
                tooltipPanel.AddLabelMedium(text=homestation.text.bracket_hint(), align=uiconst.CENTERLEFT, colSpan=tooltipPanel.columns - 1)
            elif self.sr.node.gateLockValue:
                tooltipPanel.AddCell()
                text = ''
                if self.sr.node.gateLockValue == EMANATION_GATE_AVAILABLE:
                    text = localization.GetByLabel('Tooltips/Overview/LockedToThisGate')
                elif self.sr.node.gateLockValue == EMANATION_GATE_UNAVAILABLE:
                    text = localization.GetByLabel('Tooltips/Overview/LockedToAnotherGate')
                tooltipPanel.AddLabelMedium(text=text, align=uiconst.CENTERLEFT, colSpan=tooltipPanel.columns - 1)

    def AddTypeSpecificInfoToTooltip(self, slimItem, tooltipPanel):
        if slimItem.groupID == const.groupSkyhook:
            try:
                comp = sm.GetService('michelle').GetBallpark().componentRegistry.GetComponentForItem(slimItem.itemID, ORBITAL_SKYHOOK)
                text = comp.GetProducingText()
                if text:
                    tooltipPanel.AddCell()
                    tooltipPanel.AddLabelMedium(text=text, align=uiconst.CENTERLEFT, colSpan=tooltipPanel.columns - 1)
            except StandardError as e:
                pass

    def UpdateTooltipIconThread(self, iconObj):
        while not iconObj.destroyed:
            slimItem = self.sr.node.slimItem()
            ball = self.sr.node.ball()
            if not (slimItem and ball):
                break
            iconObj.UpdateSpaceObjectState(slimItem, ball)
            blue.synchro.Sleep(200)

    def GetIconTooltipPointer(self):
        currentColumns = self.sr.node.columns
        if currentColumns and currentColumns[0] == 'ICON':
            return uiconst.POINT_RIGHT_2

    def OnClick(self, *args):
        eve.Message('ListEntryClick')
        uicore.cmd.ExecuteCombatCommand(self.sr.node.itemID, uiconst.UI_CLICK)

    def OnMouseDown(self, *args):
        self.sr.node.scroll.SelectNode(self.sr.node)
        GetMenuService().TryExpandActionMenu(self.itemID, self)

    def GetMenu(self, *args):
        return GetMenuService().CelestialMenu(self.sr.node.itemID)

    def SetLabelAlpha(self, alpha):
        self.sr.label.opacity = alpha

    def UpdateTutorialHighlight(self, isActive):
        frame = getattr(self, 'tutorialHighlight', None)
        if isActive:
            from eve.client.script.ui.services.tutoriallib import TutorialColor
            if frame is None:
                self.tutorialHighlight = Fill(parent=self, color=TutorialColor.HINT_FRAME, opacity=0.0)
                animations.FadeTo(self.tutorialHighlight, 0.0, 0.8, duration=1.6, curveType=uiconst.ANIM_WAVE, loops=uiconst.ANIM_REPEAT)
        elif frame is not None:
            self.tutorialHighlight.Close()
            self.tutorialHighlight = None


def get_distance_in_meters(meters):
    return localization.GetByLabel('/Carbon/UI/Common/FormatDistance/fmtDistInMeters', distance=meters)


def get_distance_in_kilometers(kilometers):
    return localization.GetByLabel('/Carbon/UI/Common/FormatDistance/fmtDistInKiloMeters', distance=kilometers)


def get_distance_in_au(au):
    return localization.GetByLabel('/Carbon/UI/Common/FormatDistance/fmtDistInAU', distance=au)


FMTFUNCTION = localization.formatters.FormatNumeric
