#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\mapView\markers\mapMarkerBase.py
import types
import weakref
import geo2
import telemetry
import carbonui.const as uiconst
import eve.client.script.ui.shared.mapView.mapViewConst as mapViewConst
import trinity
import uthread
from carbon.client.script.environment.AudioUtil import PlaySound
from carbon.common.script.util.commonutils import StripTags
from carbonui.primitives.base import ScaleDpiF
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from carbonui.util.bunch import Bunch
from carbonui.control.link import Link
from eve.client.script.ui.control.glowSprite import GlowSprite
from eve.client.script.ui.inflight.scannerFiles.scannerUtil import COLOR_DSCAN
from eve.client.script.ui.shared.mapView.mapViewConst import SOLARSYSTEM_SCALE
from eve.client.script.ui.shared.mapView.mapViewUtil import MapPosToSolarSystemPos
from eve.client.script.ui.shared.maps.maputils import GetMyPos
from eve.client.script.ui.tooltips.tooltipHandler import TOOLTIP_SETTINGS_BRACKET, TOOLTIP_DELAY_BRACKET
from carbonui.uicore import uicore
from logmodule import LogException

class MarkerContainerBase(Container):
    default_align = uiconst.NOALIGN
    default_opacity = 1.0
    default_state = uiconst.UI_NORMAL
    markerObject = None
    isDragObject = True

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.markerObject = attributes.markerObject
        self.renderObject.displayY = -1000

    def Close(self, *args):
        Container.Close(self, *args)
        self.markerObject = None

    def OnClick(self, *args):
        return self.markerObject.OnClick(*args)

    def OnDblClick(self, *args):
        return self.markerObject.OnDblClick(*args)

    def OnMouseDown(self, *args):
        sm.ScatterEvent('OnMarkerMouseDown', *args)
        return self.markerObject.OnMouseDown(*args)

    def OnMouseUp(self, *args):
        sm.ScatterEvent('OnMarkerMouseUp', *args)
        return self.markerObject.OnMouseUp(*args)

    def OnMouseEnter(self, *args):
        return self.markerObject.OnMouseEnter(*args)

    def OnMouseExit(self, *args):
        return self.markerObject.OnMouseExit(*args)

    def GetMenu(self):
        return self.markerObject.GetMenu()

    def GetTooltipDelay(self):
        return settings.user.ui.Get(TOOLTIP_SETTINGS_BRACKET, TOOLTIP_DELAY_BRACKET)

    @apply
    def opacity():

        def fget(self):
            return self._opacity

        def fset(self, value):
            self._opacity = value
            self.renderObject.opacity = value

        return property(**locals())

    def UpdateBackgrounds(self):
        for each in self.background:
            pl, pt, pr, pb = each.padding
            each.displayRect = (ScaleDpiF(pl),
             ScaleDpiF(pt),
             self._displayWidth - ScaleDpiF(pl + pr),
             self._displayHeight - ScaleDpiF(pt + pb))

    def GetDragData(self, *args):
        return self.markerObject.GetDragData(self, *args)

    @classmethod
    def PrepareDrag(cls, *args):
        return Link.PrepareDrag(*args)


class MarkerBase(object):
    __metaclass__ = telemetry.ZONE_PER_METHOD
    isLoaded = False
    markerID = None
    position = (0, 0, 0)
    destroyed = False
    distanceFadeAlphaNearFar = (0.0, mapViewConst.MAX_MARKER_DISTANCE)
    displayStateOverride = None
    markerContainer = None
    parentContainer = None
    extraContainer = None
    curveSet = None
    eventHandler = None
    solarSystemID = None
    positionPickable = False
    hilightState = False
    activeState = False
    updated = False
    tooltipRowClass = None
    itemID = None
    typeID = None

    def __init__(self, markerID, markerHandler, parentContainer, position, curveSet, eventHandler = None, **kwds):
        self.isDscanHiliteShown = False
        self.dScanHilite = None
        self.markerID = markerID
        self.curveSet = None
        self.projectBracket = trinity.EveProjectBracket()
        if 'distanceFadeAlphaNearFar' in kwds:
            self._distanceFadeAlphaNearFar = kwds['distanceFadeAlphaNearFar']
        else:
            self._distanceFadeAlphaNearFar = self.distanceFadeAlphaNearFar
        self.SetBracketMaxDispRange()
        self.parentContainer = weakref.ref(parentContainer)
        self.markerHandler = markerHandler
        self.eventHandler = eventHandler
        self.SetPosition(position)
        self.projectBracket.bracketUpdateCallback = self.OnMapMarkerUpdated
        if curveSet:
            self.curveSet = weakref.ref(curveSet)
            curveSet.curves.append(self.projectBracket)

    def SetBracketMaxDispRange(self):
        if self._distanceFadeAlphaNearFar:
            self.projectBracket.maxDispRange = self._distanceFadeAlphaNearFar[1]

    def Close(self):
        self.DestroyRenderObject()
        if self.curveSet:
            curveSet = self.curveSet()
            if curveSet:
                curveSet.curves.fremove(self.projectBracket)
        self.markerHandler = None
        self.eventHandler = None
        self.curveSet = None
        if self.projectBracket:
            self.projectBracket.bracketUpdateCallback = None
        self.projectBracket = None
        self.parentContainer = None
        self.markerContainer = None

    def SetOverlappedState(self, overlapState):
        pass

    def RegisterOverlapMarkers(self, overlapMarkers):
        pass

    def FadeOutAndClose(self):
        if self.markerContainer and not self.markerContainer.destroyed and self.markerContainer.opacity:
            uicore.animations.FadeTo(self.markerContainer, startVal=self.markerContainer.opacity, endVal=0.0, callback=self.Close)
        else:
            self.Close()

    def GetExtraMouseOverInfo(self):
        if self.markerHandler:
            return self.markerHandler.GetExtraMouseOverInfoForMarker(self.markerID)

    def SetHilightState(self, hilightState):
        if hilightState != self.hilightState:
            self.hilightState = hilightState
            self.lastUpdateCameraValues = None
            self.UpdateActiveAndHilightState()

    def SetActiveState(self, activeState):
        if activeState != self.activeState:
            self.activeState = activeState
            self.lastUpdateCameraValues = None
            self.UpdateActiveAndHilightState()

    def UpdateActiveAndHilightState(self):
        pass

    def MoveToFront(self):
        if self.parentContainer:
            parentContainer = self.parentContainer()
            if not parentContainer or parentContainer.destroyed:
                return
            if self.markerContainer and not self.markerContainer.destroyed:
                renderObject = self.markerContainer.renderObject
                parentContainer.renderObject.children.remove(renderObject)
                parentContainer.renderObject.children.insert(0, renderObject)

    def GetBoundaries(self):
        mx, my = self.projectBracket.rawProjectedPosition
        return (mx - 6 + self.projectBracket.offsetX,
         my - 6 + self.projectBracket.offsetY,
         mx + 6 + self.projectBracket.offsetX,
         my + 6 + self.projectBracket.offsetY)

    def GetDisplayText(self):
        return None

    def GetLabelText(self):
        return None

    def GetDragText(self):
        return self.GetDisplayText()

    def GetCameraDistance(self):
        return self.projectBracket.cameraDistance

    def SetPosition(self, position):
        self.position = position
        self.projectBracket.trackPosition = position

    def GetDisplayPosition(self):
        if self.projectBracket:
            return self.projectBracket.trackPosition

    def OnMapMarkerUpdated(self, projectBracket):
        try:
            self._OnMapMarkerUpdated(projectBracket)
        except:
            LogException()
            raise

    def _OnMapMarkerUpdated(self, projectBracket):
        if self.displayStateOverride == False:
            if self.markerContainer:
                self.DestroyRenderObject()
            return
        cameraTranslationFromParent = self.markerHandler.cameraTranslationFromParent
        bracketCameraDistance = projectBracket.cameraDistance
        if (cameraTranslationFromParent, bracketCameraDistance) != getattr(self, 'lastUpdateCameraValues', None):
            self.lastUpdateCameraValues = (cameraTranslationFromParent, bracketCameraDistance)
            opacity = self.GetMarkerOpacity(bracketCameraDistance, cameraTranslationFromParent)
            self._UpdateRenderObjectVisibility(opacity)
        self.updated = True

    def _UpdateRenderObjectVisibility(self, opacity):
        if opacity is not None and opacity > 0.05:
            self._ShowRenderObject(opacity)
        elif self.markerContainer:
            self._HideRenderObject()

    def _HideRenderObject(self):
        self.markerContainer.Hide()

    def _ShowRenderObject(self, opacity):
        self.CreateRenderObject()
        self.markerContainer.opacity = opacity
        self.markerContainer.Show()

    def OnClick(self, *args, **kwds):
        self.ClickMarker()

    def OnDblClick(self, *args, **kwds):
        self.ClickMarker()

    def ClickMarker(self):
        if uicore.cmd.IsSomeCombatCommandLoaded():
            uicore.cmd.ExecuteCombatCommand(self.itemID, uiconst.UI_CLICK)
        else:
            self.markerHandler.OnMarkerSelected(self)

    def OnMouseDown(self, *args):
        pass

    def OnMouseUp(self, *args):
        pass

    def OnMouseEnter(self, *args):
        if uicore.uilib.leftbtn or uicore.uilib.rightbtn:
            return
        PlaySound(uiconst.SOUND_ENTRY_HOVER)
        self.markerHandler.OnMarkerMouseEnter(self)

    def OnMouseExit(self, *args):
        self.markerHandler.OnMarkerMouseExit(self)

    def CreateRenderObject(self):
        if self.parentContainer and (not self.markerContainer or self.markerContainer.destroyed):
            if not self.parentContainer():
                return
            self._CreateRenderObject()

    def _CreateRenderObject(self):
        self.markerContainer = self.GetMarkerContainerCls()(parent=self.parentContainer(), markerObject=self, name=self.__class__.__name__)
        self.projectBracket.bracket = self.markerContainer.renderObject
        self.Load()

    def GetMarkerContainerCls(self):
        return MarkerContainerBase

    def Reload(self):
        self.DestroyRenderObject()
        self.lastUpdateCameraValues = None

    def DestroyRenderObject(self):
        self.projectBracket.bracket = None
        if self.markerContainer and not self.markerContainer.destroyed:
            markerContainer = self.markerContainer
            self.markerContainer = None
            markerContainer.Close()
        if self.extraContainer and not self.extraContainer.destroyed:
            self.extraContainer.Close()
            self.extraContainer = None
        self.isLoaded = False
        self.lastUpdateCameraValues = None

    def Load(self):
        pass

    def GetMenu(self):
        try:
            objectID = int(self.markerID)
            return self.eventHandler.GetMenuForObjectID(objectID)
        except:
            pass

    def GetHint(self):
        return None

    def GetDragData(self, *args):
        displayText = self.GetDragText()
        if self.itemID and self.typeID and displayText:
            url = 'showinfo:%d//%d' % (self.typeID, self.itemID)
            entry = Bunch()
            entry.__guid__ = 'TextLink'
            entry.url = url
            entry.displayText = StripTags(displayText)
            return [entry]

    def HasEventHandler(self, handlerName):
        handlerArgs, handler = self.FindEventHandler(handlerName)
        if not handler:
            return False
        baseHandler = getattr(MarkerBase, handlerName, None)
        if baseHandler and getattr(handler, 'im_func', None) is baseHandler.im_func:
            return False
        return bool(handler)

    def GetOverlapSortValue(self, reset = False):
        return None

    def FindEventHandler(self, handlerName):
        handler = getattr(self, handlerName, None)
        if not handler:
            return (None, None)
        if type(handler) == types.TupleType:
            handlerArgs = handler[1:]
            handler = handler[0]
        else:
            handlerArgs = ()
        return (handlerArgs, handler)

    def ShowDscanHilite(self):
        resetOverlap = not self.isDscanHiliteShown
        self.isDscanHiliteShown = True
        if resetOverlap:
            self.GetOverlapSortValue(reset=True)
        if not self.IsPickable():
            return
        self.ConstructDscanHilite()
        if self.dScanHilite:
            self.dScanHilite.Show()

    def IsPartialResult(self):
        return False

    def IsDscanHiliteShown(self):
        return self.isDscanHiliteShown

    def ConstructDscanHilite(self):
        if not self.dScanHilite or self.dScanHilite.destroyed:
            if not self.markerContainer:
                return
            self.dScanHilite = Container(name='dScanHilite', parent=self.markerContainer, align=uiconst.CENTER, state=uiconst.UI_DISABLED, idx=-1, pos=(0, 0, 32, 32))
            Sprite(align=uiconst.CENTER, pos=(0, 0, 50, 50), parent=self.dScanHilite, color=COLOR_DSCAN, texturePath='res:/UI/Texture/classes/animations/radialGradient.png', opacity=0.3)
            GlowSprite(align=uiconst.CENTER, pos=(0, 0, 30, 30), parent=self.dScanHilite, color=COLOR_DSCAN, texturePath='res:/UI/Texture/classes/Bracket/selectionCircle.png')

    def IsPickable(self):
        if self.markerContainer:
            return self.markerContainer.pickState == uiconst.TR2_SPS_ON
        else:
            return False

    def HideDscanHilite(self):
        resetOverlap = self.isDscanHiliteShown
        self.isDscanHiliteShown = False
        if resetOverlap:
            self.GetOverlapSortValue(reset=True)
        if self.dScanHilite:
            self.dScanHilite.Hide()

    def AnimBlinkDscanHilite(self):
        if self.dScanHilite and self.dScanHilite.display:
            animations.FadeTo(self.dScanHilite, 3.0, 1.0, duration=1.0)

    def GetMarkerOpacity(self, bracketCameraDistance, cameraZoomDistance):
        if self.IsSelected() or self.IsHilighted():
            return mapViewConst.OPACITY_MARKER_SELECTED
        elif self.IsActive() or self._distanceFadeAlphaNearFar is None:
            return mapViewConst.OPACITY_MARKER_ACTIVE
        else:
            nearFadeDist, farFadeDist = self._distanceFadeAlphaNearFar
            baseOpacity = self.GetMarkerBaseOpacity(bracketCameraDistance, nearFadeDist, farFadeDist)
            nearFactor = self.GetNearFadeFactor(bracketCameraDistance, cameraZoomDistance)
            return round(baseOpacity * nearFactor, 2)

    def GetMarkerBaseOpacity(self, bracketCameraDistance, nearFadeDist, farFadeDist):
        if bracketCameraDistance < nearFadeDist:
            return bracketCameraDistance / nearFadeDist
        elif bracketCameraDistance < farFadeDist:
            return min(1.0, max(0.0, 1.0 - bracketCameraDistance / farFadeDist))
        else:
            return 0.0

    def GetNearFadeFactor(self, bracketCameraDistance, cameraZoomDistance):
        return min(1.0, cameraZoomDistance / bracketCameraDistance)

    def IsSelected(self):
        return self.activeState == mapViewConst.MARKER_SELECTED

    def IsHilighted(self):
        return bool(self.hilightState)

    def IsActive(self):
        return self.activeState == mapViewConst.MARKER_ACTIVE


class MarkerUniverseBased(MarkerBase):

    def __init__(self, *args, **kwds):
        MarkerBase.__init__(self, *args, **kwds)

    def SetYScaleFactor(self, yScaleFactor):
        x, y, z = self.position
        self.projectBracket.trackPosition = (x, y * yScaleFactor, z)


class MarkerSolarSystemBased(MarkerBase):
    inRangeIndicatorState = False
    itemID = None
    trackObjectID = None
    binding = None
    vectorSequencer = None

    def __init__(self, *args, **kwds):
        MarkerBase.__init__(self, *args, **kwds)
        self.mapPositionSolarSystem = kwds['mapPositionSolarSystem']
        self.mapPositionLocal = kwds['mapPositionLocal']
        self.solarSystemID = kwds['solarSystemID']
        self.trackObjectID = kwds.get('trackObjectID', None)
        self.trackObjectScale = kwds.get('trackObjectScale', 1.0)
        if self.trackObjectID:
            self.SetupTracking()

    def Close(self, *args, **kwds):
        self.TearDownTracking()
        MarkerBase.Close(self, *args, **kwds)

    def UpdateSolarSystemPosition(self, solarSystemPosition):
        self.mapPositionSolarSystem = solarSystemPosition
        self.position = solarSystemPosition
        self.projectBracket.trackPosition = self.position

    def SetInRangeIndicatorState(self, visibleState):
        self.inRangeIndicatorState = visibleState

    def GetDistance(self):
        if session.solarsystemid:
            if self.itemID:
                ballPark = sm.GetService('michelle').GetBallpark()
                if ballPark and self.itemID in ballPark.balls:
                    return ballPark.balls[self.itemID].surfaceDist
            if self.solarSystemID == session.solarsystemid:
                solarSystemPosition = self._GetSolarSystemPosition()
                myPosition = GetMyPos()
                return geo2.Vec3Length(geo2.Vec3Subtract(solarSystemPosition, (myPosition.x, myPosition.y, myPosition.z)))

    def _GetSolarSystemPosition(self):
        return MapPosToSolarSystemPos(self.mapPositionLocal)

    def TearDownTracking(self):
        if self.vectorSequencer:
            if self.curveSet:
                curveSet = self.curveSet()
                if curveSet:
                    curveSet.curves.remove(self.vectorSequencer)
                    curveSet.bindings.remove(self.binding)
        self.binding = None
        self.vectorSequencer = None

    def SetupTracking(self):
        self.TearDownTracking()
        bp = sm.GetService('michelle').GetBallpark()
        if not bp:
            return
        sunBall = None
        if self.trackObjectID == session.shipid:
            for itemID, each in bp.slimItems.iteritems():
                if each.groupID == const.groupSun:
                    sunBall = bp.GetBall(itemID)
                    break

        trackBallID = self.trackObjectID
        ball = bp.GetBall(trackBallID)
        if ball is None or sunBall is None:
            return
        vectorCurve = trinity.Tr2CurveVector3()
        scale = SOLARSYSTEM_SCALE * self.trackObjectScale
        vectorCurve.AddKey(0, (-scale, -scale, -scale))
        invSunPos = trinity.TriVectorSequencer()
        invSunPos.operator = trinity.TRIOP_MULTIPLY
        invSunPos.functions.append(sunBall)
        invSunPos.functions.append(vectorCurve)
        vectorCurve = trinity.Tr2CurveVector3()
        vectorCurve.AddKey(0, (scale, scale, scale))
        ballPos = trinity.TriVectorSequencer()
        ballPos.operator = trinity.TRIOP_MULTIPLY
        ballPos.functions.append(ball)
        ballPos.functions.append(vectorCurve)
        vectorSequencer = trinity.TriVectorSequencer()
        vectorSequencer.operator = trinity.TRIOP_ADD
        vectorSequencer.functions.append(invSunPos)
        vectorSequencer.functions.append(ballPos)
        bind = trinity.TriValueBinding()
        bind.copyValueCallable = self.OnBallPositionUpdate
        bind.sourceObject = vectorSequencer
        bind.sourceAttribute = 'value'
        self.binding = bind
        self.vectorSequencer = vectorSequencer
        if self.curveSet:
            curveSet = self.curveSet()
            if curveSet:
                curveSet.curves.append(vectorSequencer)
                curveSet.bindings.append(bind)

    def OnBallPositionUpdate(self, curveSet, *args):
        try:
            if curveSet.value == (0, 0, 0):
                uthread.new(self.TearDownTracking)
            else:
                self.UpdateMapPositionLocal(curveSet.value)
        except:
            LogException()
            raise

    def CheckDirectionalScanItem(self):
        doDScan = uicore.cmd.IsCombatCommandLoaded('CmdRefreshDirectionalScan')
        if doDScan:
            markerPosition = self.position
            uicore.cmd.GetCommandAndExecute('OpenDirectionalScanner', toggle=False)
            sm.GetService('directionalScanSvc').ScanTowardsItem(self.itemID, mapPosition=markerPosition)
        return doDScan
