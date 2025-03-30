#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\navigation.py
from itertools import chain
import blue
import evecamera
import evetypes
import geo2
import uthread
from carbonui import uiconst
from carbonui.control.layer import LayerCore
from carbonui.primitives.base import ReverseScaleDpi
from carbonui.primitives.bracket import Bracket
from carbonui.primitives.container import Container
from carbonui.primitives.line import Line
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from eve.client.script.parklife import states
from eve.client.script.parklife.tacticalConst import is_interactable_entity
from eve.client.script.ui.camera.cameraUtil import GetCameraMaxLookAtRange, GetBallPosition
from eve.client.script.ui.camera.debugCameraController import DebugCameraController
from eve.client.script.ui.camera.enterSpaceCameraController import EnterSpaceCameraController
from eve.client.script.ui.camera.explosionCameraController import ExplosionCameraController
from eve.client.script.ui.camera.shipOrbitAbyssalSpaceCameraController import ShipOrbitCameraAbyssalSpaceController
from eve.client.script.ui.camera.shipOrbitCameraController import ShipOrbitCameraController
from eve.client.script.ui.camera.shipOrbitCameraRestrictedController import ShipOrbitCameraRestrictedController
from eve.client.script.ui.camera.shipOrbitHazardCameraController import ShipOrbitCameraHazardSpaceController
from eve.client.script.ui.camera.shipPOVCameraController import ShipPOVCameraController
from eve.client.script.ui.camera.tacticalCameraController import TacticalCameraController
from eve.client.script.ui.camera.undockCameraController import UndockCameraController
from eve.client.script.ui.control.marqueeCont import MarqueeCont
from eve.client.script.ui.inflight import positionalControl
from eve.client.script.ui.inflight.bracketsAndTargets.bracketVarious import GetOverlaps
from eve.client.script.ui.inflight.bracketsAndTargets.inSpaceBracketTooltip import PersistentInSpaceBracketTooltip
from eve.client.script.ui.inflight.drone import DropDronesInSpace
from eve.client.script.ui.inflight.drones import dronesUtil, dronesDragData, droneSignals
from eve.client.script.ui.inflight.drones.dronesDragData import AllDronesInBayDragData
from eve.client.script.ui.services.menuSvcExtras import droneFunctions
from eve.client.script.ui.shared.infoPanels.listSurroundingsBtn import ListSurroundingsBtn
from eve.client.script.ui.shared.radialMenu.spaceRadialMenuFunctions import AreOtherMouseBtnsDown, GetSingleMouseBtnBroadcastRadialMenu
from eve.client.script.ui.tooltips.tooltipHandler import TOOLTIP_SETTINGS_BRACKET, TOOLTIP_DELAY_BRACKET
from eve.common.lib import appConst
from eveservices.menu import GetMenuService
from menu import MenuLabel
from sensorsuite.overlay.brackets import SensorSuiteBracket
from spacecomponents.client.components import deploy
from spacecomponents.common.helper import HasDeployComponent
multiTargetCmds = ('CmdLockTargetItem', 'CmdToggleTargetItem', 'CmdSelectTargetItem', 'CmdUnlockTargetItem', 'CmdShowItemInfo')
nearestTargetCmds = ('CmdToggleLookAtItem', 'CmdToggleCameraTracking', 'CmdApproachItem', 'CmdAlignToItem', 'CmdOrbitItem', 'CmdKeepItemAtRange')

class InflightLayer(LayerCore):
    __guid__ = 'uicls.InflightLayer'
    __notifyevents__ = ['OnActiveCameraChanged', 'OnRadialMenuExpanded']

    def ApplyAttributes(self, attributes):
        LayerCore.ApplyAttributes(self, attributes)
        self.locked = 0
        self.sr.tcursor = None
        self.hoverbracket = None
        self.sr.spacemenu = None
        self.marqueeCont = None
        self.locks = {}
        self.mouseDown = False
        self._structureDeploymentSvc = None
        self.lastCamera = None
        self.cameraController = None
        self.positionalControl = positionalControl.PositionalControl()
        self.sr.tcursor = Container(name='targetingcursor', parent=self, align=uiconst.ABSOLUTE, width=1, height=1, state=uiconst.UI_HIDDEN)
        Line(parent=self.sr.tcursor, align=uiconst.RELATIVE, left=10, width=3000, height=1)
        Line(parent=self.sr.tcursor, align=uiconst.TOPRIGHT, left=10, width=3000, height=1)
        Line(parent=self.sr.tcursor, align=uiconst.RELATIVE, top=10, width=1, height=3000)
        Line(parent=self.sr.tcursor, align=uiconst.BOTTOMLEFT, top=10, width=1, height=3000)

    @property
    def structureDeploymentSvc(self):
        if not self._structureDeploymentSvc:
            self._structureDeploymentSvc = sm.GetService('structureDeployment')
        return self._structureDeploymentSvc

    def OnOpenView(self, **kwargs):
        camera = sm.GetService('sceneManager').GetActiveCamera()
        if camera:
            self.OnActiveCameraChanged(camera.cameraID)

    def OnCloseView(self):
        if self.cameraController:
            self.cameraController.Deactivate()

    def OnActiveCameraChanged(self, cameraID):
        if self.cameraController:
            self.cameraController.Deactivate()
        if cameraID == evecamera.CAM_SHIPORBIT:
            self.cameraController = ShipOrbitCameraController()
        elif cameraID == evecamera.CAM_SHIPORBIT_ABYSSAL_SPACE:
            self.cameraController = ShipOrbitCameraAbyssalSpaceController()
        elif cameraID == evecamera.CAM_SHIPORBIT_HAZARD:
            self.cameraController = ShipOrbitCameraHazardSpaceController()
        elif cameraID == evecamera.CAM_SHIPORBIT_RESTRICTED:
            self.cameraController = ShipOrbitCameraRestrictedController()
        elif cameraID == evecamera.CAM_TACTICAL:
            self.cameraController = TacticalCameraController()
        elif cameraID == evecamera.CAM_SHIPPOV:
            self.cameraController = ShipPOVCameraController()
        elif cameraID == evecamera.CAM_DEBUG:
            self.cameraController = DebugCameraController()
        elif cameraID == evecamera.CAM_UNDOCK:
            self.cameraController = UndockCameraController()
        elif cameraID == evecamera.CAM_ENTERSPACE:
            self.cameraController = EnterSpaceCameraController()
        elif cameraID == evecamera.CAM_EXPLOSION:
            self.cameraController = ExplosionCameraController()
        else:
            self.cameraController = None
        if self.cameraController:
            self.cameraController.Activate()
        self.positionalControl.SetCameraController(self.cameraController)
        if self.lastCamera == evecamera.CAM_SHIPPOV:
            self.UpdatePlayerImpactDamages()
        self.lastCamera = cameraID

    def UpdatePlayerImpactDamages(self):
        if eve.session.shipid is not None:
            michelle = sm.GetService('michelle')
            ball = michelle.GetBall(eve.session.shipid)

            def Delay():
                blue.synchro.SleepSim(50)
                if ball is not None and hasattr(ball, 'model') and ball.model is not None:
                    ball._UpdateImpacts()

            uthread.new(Delay)

    def GetSpaceMenu(self, solarsystemID):
        if self.sr.spacemenu:
            if self.sr.spacemenu.solarsystemID == solarsystemID:
                return self.sr.spacemenu
            m = self.sr.spacemenu
            self.sr.spacemenu = None
            m.Close()
        listbtn = ListSurroundingsBtn(name='gimp', parent=self, state=uiconst.UI_HIDDEN, pos=(0, 0, 0, 0), useDynamicMapItems=True, isInSpaceMenu=True)
        listbtn.SetSolarsystemID(solarsystemID)
        listbtn.sr.groupByType = 1
        listbtn.filterCurrent = 1
        self.sr.spacemenu = listbtn
        return self.sr.spacemenu

    def _OnClose(self):
        Container._OnClose(self)
        if sm.GetService('ui').IsUiVisible():
            uicore.layer.main.state = uiconst.UI_PICKCHILDREN

    def PrepareTooltipLoad(self, bracket):
        if uicore.uilib.leftbtn or uicore.uilib.rightbtn:
            return None
        currentPos = (uicore.uilib.x, uicore.uilib.y)
        lastPos = getattr(self, 'lastLoadPos', (None, None))
        if lastPos == currentPos:
            return None
        self.lastLoadPos = currentPos
        self.tooltipBracket = bracket
        currentTooltip = uicore.uilib.tooltipHandler.GetPersistentTooltipByOwner(self)
        if currentTooltip and not (currentTooltip.destroyed or currentTooltip.beingDestroyed):
            if currentTooltip.IsOverlapBracket(bracket):
                return None
            currentTooltip.Close()
        isFloating = bracket.IsFloating()
        overlaps, boundingBox = GetOverlaps(bracket, useMousePosition=isinstance(bracket, SensorSuiteBracket), customBracketParent=uicore.layer.bracket)
        overlapSites = sm.GetService('sensorSuite').GetOverlappingSites()
        if isFloating and len(overlaps) + len(overlapSites) == 1:
            return None
        overlapSites.sort(key=lambda x: x.data.GetSortKey())
        self.tooltipPositionRect = bracket.GetAbsolute()
        ro = bracket.renderObject
        self.bracketPosition = (ro.displayX,
         ro.displayY,
         ro.displayWidth,
         ro.displayHeight)
        for bracket in chain(overlaps, overlapSites):
            bracket.opacity = 2.0

        for layer in (uicore.layer.inflight, uicore.layer.sensorSuite):
            animations.FadeTo(layer, startVal=layer.opacity, endVal=0.5, duration=0.5)

        uicore.uilib.tooltipHandler.LoadPersistentTooltip(self, loadArguments=(bracket,
         overlaps,
         boundingBox,
         overlapSites), customTooltipClass=PersistentInSpaceBracketTooltip)

    def OnRadialMenuExpanded(self, *args):
        self.StopMarqueeSelection()

    def GetTooltipDelay(self):
        return settings.user.ui.Get(TOOLTIP_SETTINGS_BRACKET, TOOLTIP_DELAY_BRACKET)

    def GetTooltipPosition(self, *args, **kwds):
        return self.tooltipPositionRect

    def GetTooltipPointer(self):
        tooltipPanel = uicore.uilib.tooltipHandler.GetPersistentTooltipByOwner(self)
        if not tooltipPanel:
            return
        x, y, width, height = self.bracketPosition
        bracketLayerWidth = uicore.layer.bracket.displayWidth
        bracketLayerHeight = uicore.layer.bracket.displayHeight
        width = uicore.ReverseScaleDpi(width)
        height = uicore.ReverseScaleDpi(height)
        overlapAmount = len(tooltipPanel.overlaps)
        isCompact = tooltipPanel.isCompact
        if x <= 0:
            if isCompact and overlapAmount == 1:
                return uiconst.POINT_LEFT_2
            else:
                return uiconst.POINT_LEFT_3
        elif x + width >= bracketLayerWidth:
            if isCompact and overlapAmount == 1:
                return uiconst.POINT_RIGHT_2
            else:
                return uiconst.POINT_RIGHT_3
        elif y <= 0:
            if isCompact:
                return uiconst.POINT_TOP_2
            else:
                return uiconst.POINT_TOP_1
        elif y + height >= bracketLayerHeight:
            if isCompact:
                return uiconst.POINT_BOTTOM_2
            else:
                return uiconst.POINT_BOTTOM_1
        if isCompact:
            return uiconst.POINT_BOTTOM_2
        else:
            return uiconst.POINT_BOTTOM_1

    def GetTooltipPositionFallbacks(self):
        tooltipPanel = uicore.uilib.tooltipHandler.GetPersistentTooltipByOwner(self)
        if tooltipPanel:
            isCompact = tooltipPanel.isCompact
        else:
            isCompact = False
        if isCompact:
            return [uiconst.POINT_TOP_2,
             uiconst.POINT_TOPLEFT,
             uiconst.POINT_TOPRIGHT,
             uiconst.POINT_BOTTOMLEFT,
             uiconst.POINT_BOTTOMRIGHT]
        else:
            return [uiconst.POINT_TOP_1,
             uiconst.POINT_TOPLEFT,
             uiconst.POINT_TOPRIGHT,
             uiconst.POINT_BOTTOMLEFT,
             uiconst.POINT_BOTTOMRIGHT]

    def ShowTargetingCursor(self):
        self.sr.tcursor.left = uicore.uilib.x - 1
        self.sr.tcursor.top = uicore.uilib.y
        self.sr.tcursor.state = uiconst.UI_DISABLED

    def HideTargetingCursor(self):
        self.sr.tcursor.state = uiconst.UI_HIDDEN

    def GetMenu(self, itemID = None):
        if self.positionalControl.IsActive():
            self.positionalControl.AbortCommand()
            return
        if self.locked or sm.GetService('target').IsSomeModuleWaitingForTargetClick():
            return []
        m = []
        if not itemID and self.cameraController:
            picktype, pickobject = self.cameraController.GetPick()
            if pickobject and hasattr(pickobject, 'translationCurve') and hasattr(pickobject.translationCurve, 'id'):
                itemID = pickobject.translationCurve.id
            if pickobject:
                if sm.GetService('posAnchor').IsActive():
                    if pickobject.name[:6].lower() == 'cursor':
                        m.append((MenuLabel('UI/Inflight/POS/AnchorHere'), sm.GetService('posAnchor').SubmitAnchorPosSelect, ()))
                        m.append(None)
                        m.append((MenuLabel('UI/Inflight/POS/CancelAnchoring'), sm.GetService('posAnchor').CancelAchorPosSelect, ()))
                        return m
        if not itemID:
            locationShortcutActive = sm.GetService('cmd').IsCombatCommandLoaded('CmdGetLocationMenuForNavigation')
            if locationShortcutActive:
                m = sm.GetService('bookmarkSvc').GetBookmarkMenuForNavigation(includeTopLevel=False)
                if not m:
                    eve.Message('NoLocationsFoundForMenu')
                return m
            mm = self.GetSpaceMenu(session.solarsystemid2).GetMenu()
            m.extend([(MenuLabel('UI/Inflight/ResetCamera'), sm.GetService('sceneManager').GetActiveCamera().ResetCamera, ()),
             None,
             (MenuLabel('UI/Inflight/ShowSystemInMapBrowser'), GetMenuService().ShowInMapBrowser, (eve.session.solarsystemid2,)),
             None])
            return m + mm
        bp = sm.GetService('michelle').GetBallpark()
        if not bp:
            return m
        slimItem = bp.GetInvItem(itemID)
        if slimItem is None:
            return m
        pickid = slimItem.itemID
        groupID = slimItem.groupID
        categoryID = slimItem.categoryID
        if eve.session.shipid is None:
            return m
        m += GetMenuService().CelestialMenu(slimItem.itemID, slimItem=slimItem)
        return m

    def ShowRadialMenuIndicator(self, slimItem, *args):
        if not slimItem:
            return
        bracket = sm.GetService('bracket').GetBracket(slimItem.itemID)
        if bracket is None:
            return
        bracket.ShowRadialMenuIndicator()

    def HideRadialMenuIndicator(self, slimItem, *args):
        if slimItem is None:
            return
        bracket = sm.GetService('bracket').GetBracket(slimItem.itemID)
        if bracket is None:
            return
        bracket.HideRadialMenuIndicator()

    def OnDropData(self, dragObj, dragData):
        inBayDroneIDs = dronesDragData.GetInBayDroneIDs(dragData)
        if inBayDroneIDs:
            droneFunctions.LaunchDrones(inBayDroneIDs)
            droneSignals.on_drones_dropped_in_space()
        elif dragData and hasattr(dragData[0], '__guid__') and dragData[0].__guid__ in ('xtriui.InvItem', 'listentry.InvItem'):
            deployItems = []
            for node in dragData:
                if node.item.ownerID != session.charid:
                    return
                if node.item.locationID != session.shipid:
                    return
                if node.item.categoryID == appConst.categoryStructure:
                    self.structureDeploymentSvc.Deploy(node.item)
                    return
                if HasDeployComponent(node.item.typeID):
                    if not session.structureid:
                        deployItems.append(node.item)

            if deployItems:
                deploy.DeployAction(deployItems)

    def OnDragEnter(self, dragSource, dragData):
        if dronesDragData.HasInBayDroneIDs(dragData):
            droneSignals.on_in_space_entry_drag_enter()

    def OnMouseDown(self, *args):
        self.mouseDown = True
        if sm.GetService('ui').IsUiVisible():
            uicore.layer.main.state = uiconst.UI_DISABLED
        if not self.cameraController:
            return
        pickObject = self.cameraController.OnMouseDown(*args)
        if self.positionalControl.IsActive():
            return
        self.TryExpandActionMenu(pickObject)
        uicore.uilib.ClipCursor(0, 0, uicore.desktop.width, uicore.desktop.height)
        if pickObject and pickObject.name == 'StructurePlacement' and self.structureDeploymentSvc.IsOnPositionStep():
            self.structureDeploymentSvc.StartMovingStructure()
        elif uicore.uilib.leftbtn and not uicore.uilib.rightbtn and uicore.cmd.IsSomeCombatCommandLoaded():
            self.StartMarqueeSelection()
        elif uicore.uilib.rightbtn:
            self.StopMarqueeSelection()

    def StartMarqueeSelection(self):
        self.StopMarqueeSelection()
        self.marqueeCont = MarqueeCont(parent=self)

    def OnMouseUp(self, btnID):
        if sm.GetService('ui').IsUiVisible():
            uicore.layer.main.state = uiconst.UI_PICKCHILDREN
        if not uicore.uilib.leftbtn and not uicore.uilib.rightbtn:
            self.mouseDown = False
            uicore.uilib.UnclipCursor()
            if uicore.uilib.GetCapture() == self:
                uicore.uilib.ReleaseCapture()
        elif uicore.uilib.leftbtn or uicore.uilib.rightbtn:
            uicore.uilib.SetCapture(self)
        if self.structureDeploymentSvc.IsMovingStructure():
            self.structureDeploymentSvc.EndMovingStructure()
        if not self.cameraController:
            return
        if self.positionalControl.IsActive():
            if not self.cameraController.IsMouseDragged():
                if btnID == 0:
                    self.positionalControl.AddPoint()
            return
        if uicore.cmd.IsCombatCommandLoaded('CmdApproachItem') and not self.IsMarqueeActivated():
            self.positionalControl.StartMoveCommand()
        if self.IsMarqueeActivated():
            self.ApplyMarqueeCommands()
            self.cameraController.mouseDownPos = None
        else:
            if not self.cameraController.IsMouseDragged() and not uicore.cmd.IsSomeCombatCommandLoaded():
                sm.GetService('stateSvc').ResetByFlag(states.multiSelected)
            self.cameraController.OnMouseUp(btnID)
        self.StopMarqueeSelection()

    def SetMouseDownAndDoMouseUp(self, *args):
        btnID = uiconst.MOUSELEFT
        self.cameraController.OnMouseDown(btnID)
        self.OnMouseUp(btnID)

    def ApplyMarqueeCommands(self):
        balls = self.GetMarqueeSelectedBalls()
        if balls:
            sm.GetService('stateSvc').SetState(balls[0].id, states.selected, True)
            combatCmd = uicore.cmd.GetCombatCmdLoadedName()
            if not combatCmd:
                return
            if len(balls) > 1 and combatCmd and combatCmd.name in multiTargetCmds:
                self._ApplyCommandToMultiple(balls, combatCmd)
            else:
                self._ApplyCommandToNearest(balls, combatCmd)

    def _ApplyCommandToNearest(self, balls, combatCmd):
        if combatCmd.name == 'CmdToggleLookAtItem':
            radius = self._GetLookAtRadius(balls)
            uicore.cmd.ExecuteCombatCommand(balls[0].id, uiconst.UI_CLICK, radius=radius)
        else:
            uicore.cmd.ExecuteCombatCommand(balls[0].id, uiconst.UI_CLICK)

    def _ApplyCommandToMultiple(self, balls, combatCmd):
        ballsWithBracket = [ ball for ball in balls if ball.id in sm.GetService('bracket').brackets ]
        if ballsWithBracket:
            balls = ballsWithBracket
        balls = self._FilterBallsByCombatCmd(balls, combatCmd)
        for ball in balls:
            uicore.cmd.ExecuteActiveCombatCommand(ball.id)

    def _FilterBallsByCombatCmd(self, balls, combatCmd):
        if combatCmd.name == 'CmdLockTargetItem':
            maxTargets = sm.GetService('target').GetNumAdditionalTargetsAllowed()
            balls = balls[:int(maxTargets)]
        return balls

    def _GetLookAtRadius(self, balls):
        ret = 0.0
        v0 = GetBallPosition(balls[0])
        camera = self.cameraController.GetCamera()
        v0 = camera.ProjectWorldToCamera(v0)
        for ball in balls[1:]:
            v1 = GetBallPosition(ball)
            if geo2.Vec3Length(v1) > GetCameraMaxLookAtRange():
                continue
            v1 = camera.ProjectWorldToCamera(v1)
            diff = geo2.Vec3Subtract(v1, v0)
            dist = geo2.Vec2Length(diff[:2])
            if ret < dist:
                ret = dist

        return ret

    def IsMarqueeActivated(self):
        if not self.cameraController:
            return False
        return self.cameraController.GetMouseTravel() >= 5 and self.marqueeCont

    def GetMarqueeSelectedBalls(self):
        ret = []
        for itemID, x, y in self.GetAllSlimItemScreenCoords():
            if self.IsMarqueeSelected(x, y):
                ret.append(itemID)

        michelle = sm.GetService('michelle')
        balls = []
        for itemID in ret:
            ball = michelle.GetBall(itemID)
            if not ball:
                continue
            typeID = getattr(ball, 'typeID', None)
            if not typeID or is_interactable_entity(evetypes.GetGroupID(typeID)):
                balls.append(ball)

        return sorted(balls, key=self._GetDistanceToCamera)

    def GetBrackets(self):
        return sm.GetService('bracket').brackets.values()

    def GetAllSlimItemScreenCoords(self):
        bp = sm.GetService('michelle').GetBallpark()
        camera = self.cameraController.GetCamera()
        ret = []
        for itemID in self._GetAllSlimAndSiteItemIDs():
            ball = bp.GetBall(itemID)
            if not ball:
                continue
            vec = ball.GetVectorAt(blue.os.GetSimTime())
            vec = (vec.x, vec.y, vec.z)
            if camera.IsInFrontOfCamera(vec):
                x, y = self.cameraController.ProjectWorldToScreen(vec)
                ret.append((itemID, ReverseScaleDpi(int(x)), ReverseScaleDpi(int(y))))

        return ret

    def _GetAllSlimAndSiteItemIDs(self):
        bp = sm.GetService('michelle').GetBallpark()
        slimItemIDs = [ itemID for itemID, _ in bp.slimItems.iteritems() ]
        siteItemIDs = [ site.ballID for site in sm.GetService('sensorSuite').GetVisibleSites() ]
        return slimItemIDs + siteItemIDs

    def _GetDistanceToCamera(self, ball):
        bp = sm.GetService('michelle').GetBallpark()
        ballPos = GetBallPosition(ball)
        camPos = self.cameraController.GetCamera().eyePosition
        return geo2.Vec3Distance(ballPos, camPos)

    def IsMarqueeSelected(self, x, y):
        left, top, width, height = self.marqueeCont.GetAbsolute()
        if x < left:
            return False
        elif x > left + width:
            return False
        elif y < top:
            return False
        elif y > top + height:
            return False
        else:
            return True

    def OnDblClick(self, *args):
        if self.positionalControl.IsActive():
            return
        if self.cameraController:
            self.cameraController.OnDblClick(*args)

    def OnMouseWheel(self, *args):
        if self.cameraController:
            self.cameraController.OnMouseWheel(*args)

    def OnMouseEnter(self, *args):
        if self.destroyed or self.parent is None or self.parent.destroyed:
            return
        if sm.GetService('ui').IsUiVisible():
            uicore.layer.main.state = uiconst.UI_PICKCHILDREN
        if sm.IsServiceRunning('tactical'):
            uthread.new(sm.GetService('tactical').ClearModuleRange)
        if uicore.cmd.IsCombatCommandLoaded('CmdApproachItem') and not self.positionalControl.IsActive():
            self.positionalControl.StartMoveCommand()
        self.SetOrder(-1)

    def OnMouseExit(self, *args):
        if self._ShouldExitPositionalMode():
            self.positionalControl.OnSceneMouseExit()
        if self.cameraController:
            self.cameraController.OnMouseExit()

    def _ShouldExitPositionalMode(self):
        currentMouseOver = uicore.uilib.GetMouseOver()
        if currentMouseOver is None:
            return True
        if isinstance(currentMouseOver, Bracket):
            if self.positionalControl.IsTargeting():
                return False
        return True

    def OnMouseMove(self, *args):
        if uicore.IsDragging():
            return
        self.sr.hint = ''
        self.sr.tcursor.left = uicore.uilib.x - 1
        self.sr.tcursor.top = uicore.uilib.y
        self.CheckStartMoveCommand()
        if self.positionalControl.IsActive():
            if uicore.uilib.leftbtn and self.cameraController.IsMouseDragged():
                self.positionalControl.AbortCommand()
                self.StartMarqueeSelection()
            else:
                return
        if self.structureDeploymentSvc.IsMovingStructure():
            if uicore.uilib.leftbtn:
                if uicore.uilib.Key(uiconst.VK_CONTROL):
                    self.structureDeploymentSvc.RotateDragObject()
                else:
                    self.structureDeploymentSvc.MoveDragObject()
            elif uicore.uilib.rightbtn:
                self.structureDeploymentSvc.RotateDragObject()
        elif self.cameraController:
            if self.cameraController.CheckMoveSceneCursor():
                self.StopMarqueeSelection()
            elif not self.marqueeCont and self.mouseDown:
                self.cameraController.OnMouseMove(*args)

    def CheckStartMoveCommand(self):
        isMouseDown = uicore.uilib.leftbtn
        approachCmdActive = uicore.cmd.IsCombatCommandLoaded('CmdApproachItem')
        moveCommandActive = self.positionalControl.IsActive()
        if approachCmdActive and not moveCommandActive and not isMouseDown:
            self.positionalControl.StartMoveCommand()

    def StopMarqueeSelection(self):
        if self.marqueeCont:
            self.marqueeCont.Close()
            self.marqueeCont = None

    def TryExpandActionMenu(self, pickObj):
        if pickObj and hasattr(pickObj, 'translationCurve') and hasattr(pickObj.translationCurve, 'id'):
            uthread.new(sm.GetService('radialmenu').TryExpandActionMenu, pickObj.translationCurve.id, self)
        elif session.fleetid:
            myBtn = GetSingleMouseBtnBroadcastRadialMenu()
            if myBtn and uicore.uilib.GetMouseButtonState(myBtn) and not AreOtherMouseBtnsDown(myBtn):
                uthread.new(sm.GetService('radialmenu').TryExpandActionMenu, None, self)
                return
            combatCmdLoaded = uicore.cmd.combatCmdLoaded
            if combatCmdLoaded and combatCmdLoaded.name == 'CmdOpenBroadcastRadialMenu':
                uthread.new(sm.GetService('radialmenu').TryExpandActionMenu, None, self)

    def ZoomBy(self, amount):
        if self.cameraController:
            camera = self.cameraController.GetCamera()
            camera.Zoom(0.001 * amount)
