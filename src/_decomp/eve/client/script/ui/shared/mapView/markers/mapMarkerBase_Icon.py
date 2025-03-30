#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\mapView\markers\mapMarkerBase_Icon.py
from carbon.common.script.util.format import FmtDist
from carbonui.primitives.base import ScaleDpi
from carbonui.primitives.container import Container
from carbonui.primitives.frame import Frame
from carbonui.primitives.sprite import Sprite
import eve.client.script.ui.shared.mapView.mapViewConst as mapViewConst
from carbonui.uianimations import animations
from eve.client.script.ui.shared.mapView.mapViewUtil import MapPosToSolarSystemPos
from eve.client.script.ui.shared.mapView.markers.mapMarkerBase import MarkerSolarSystemBased
from eve.client.script.ui.inflight.bracket import BracketShadowLabel
import carbonui.const as uiconst
import geo2
from eve.client.script.ui.shared.mapView.markers.mapMarkerTooltip import MarkerTooltipRowBase, MarkerTooltipWrapperBase
from carbonui.uicore import uicore

class MarkerIconBase(MarkerSolarSystemBased):
    tooltipRowClass = MarkerTooltipRowBase
    label = None
    highlightFrame = None
    texturePath = None
    iconColor = (1, 1, 1, 1)
    backgroundTexturePath = 'res:/UI/Texture/classes/MapView/tagBackground.png'
    backgroundColor = None
    width = 14
    height = 14
    clientBall = None
    overlapStackContainer = None
    overlapMarkers = None
    overlapEnabled = True
    overlapSortValue = None
    distanceSortEnabled = True
    inRangeIndicator = None
    distanceFadeAlphaNearFar = (0.0, mapViewConst.MAX_MARKER_DISTANCE)
    trackingTransforms = None

    def __init__(self, *args, **kwds):
        self.highlightOnLoad = kwds.get('highlightOnLoad', False)
        MarkerSolarSystemBased.__init__(self, *args, **kwds)
        self.texturePath = kwds.get('texturePath', self.texturePath)
        self.projectBracket.offsetY = -ScaleDpi(30)

    def Load(self):
        if self.isLoaded:
            return
        self.isLoaded = True
        self.iconSprite = Sprite(parent=self.markerContainer, texturePath=self.texturePath, pos=((self.width - 16) / 2,
         (self.height - 16) / 2,
         16,
         16), state=uiconst.UI_DISABLED, color=self.iconColor)
        self.backgroundSprite = Sprite(parent=self.markerContainer, texturePath=self.backgroundTexturePath, pos=((self.width - 64) / 2,
         (self.height - 64) / 2 + 12,
         64,
         64), state=uiconst.UI_DISABLED, color=self.backgroundColor)
        self.markerContainer.pos = (0,
         0,
         self.width,
         self.height)
        if self.highlightOnLoad and not self.updated:
            self.highlightOnLoad = False
            self.HighlightLoad()
        self.UpdateInRangeIndicatorState()
        self.markerContainer.tooltipPanelClassInfo = MarkerTooltipWrapperBase()

    def SetIconColor(self, color = None):
        self.iconColor = color
        if self.isLoaded:
            self.iconSprite.SetRGBA(*color)

    def DestroyRenderObject(self):
        MarkerSolarSystemBased.DestroyRenderObject(self)
        if self.label and not self.label.destroyed:
            self.label.Close()
            self.label = None

    def CreateClientBall(self):
        ballpark = sm.GetService('michelle').GetBallpark()
        if ballpark:
            ball = ballpark.AddClientSideBall(MapPosToSolarSystemPos(self.mapPositionLocal), isGlobal=True)
            self.clientBall = ball

    def RegisterTrackingTransform(self, transform):
        if self.trackingTransforms is None:
            self.trackingTransforms = []
        if transform not in self.trackingTransforms:
            self.trackingTransforms.append(transform)
        transform.translation = self.position

    def UnregisterTrackingTransform(self, transform):
        if transform in self.trackingTransforms:
            self.trackingTransforms.remove(transform)

    def Close(self, *args):
        MarkerSolarSystemBased.Close(self, *args)
        ballpark = sm.GetService('michelle').GetBallpark()
        if ballpark and self.clientBall and self.clientBall.id in ballpark.balls:
            ballpark.RemoveClientSideBall(self.clientBall.id)
        self.clientBall = None
        self.trackingTransforms = None

    def SetInRangeIndicatorState(self, visibleState):
        self.inRangeIndicatorState = visibleState
        if self.isLoaded:
            self.UpdateInRangeIndicatorState()

    def UpdateInRangeIndicatorState(self):
        if self.inRangeIndicatorState:
            pass
        elif self.inRangeIndicator and not self.inRangeIndicator.destroyed:
            self.inRangeIndicator.Close()
            self.inRangeIndicator = None

    def UpdateSolarSystemPosition(self, solarSystemPosition):
        self.mapPositionSolarSystem = solarSystemPosition
        self.position = geo2.Vec3Add(solarSystemPosition, self.mapPositionLocal)
        self.projectBracket.trackPosition = self.position
        if self.trackingTransforms:
            for each in self.trackingTransforms:
                each.translation = self.position

    def UpdateMapPositionLocal(self, mapPositionLocal, animate = False):
        self.mapPositionLocal = mapPositionLocal
        self.position = geo2.Vec3Add(self.mapPositionSolarSystem, mapPositionLocal)
        self.SetBracketPosition(animate)
        if self.trackingTransforms:
            for each in self.trackingTransforms:
                each.translation = self.position

    def SetBracketPosition(self, animate = False):
        if animate:
            animations.MorphVector3(self.projectBracket, 'trackPosition', self.projectBracket.trackPosition, self.position, duration=0.6)
        else:
            self.projectBracket.trackPosition = self.position

    def HighlightLoad(self):
        fill = Sprite(parent=self.markerContainer, color=(1, 1, 1, 0), align=uiconst.CENTER, pos=(0, 0, 2, 2), texturePath='res:/UI/Texture/classes/MapView/markerFadeIn.png')
        duration = 0.8
        uicore.animations.MorphScalar(fill, 'width', startVal=16, endVal=160, duration=duration)
        uicore.animations.MorphScalar(fill, 'height', startVal=16, endVal=160, duration=duration)
        uicore.animations.MorphScalar(fill, 'opacity', startVal=0.5, endVal=0.0, duration=duration, callback=fill.Close)

    def RegisterOverlapMarkers(self, overlapMarkers):
        if self.overlapMarkers == overlapMarkers:
            return
        self.overlapMarkers = overlapMarkers
        self.iconSprite.opacity = self.GetIconSpriteIdleOpacity()
        self.backgroundSprite.opacity = self.GetBackgroundSpriteIdleOpacity()
        if self.markerContainer:
            self.markerContainer.pickState = uiconst.TR2_SPS_ON
        amount = len(overlapMarkers)
        if self.overlapStackContainer is None or self.overlapStackContainer.destroyed:
            self.overlapStackContainer = Container(parent=self.markerContainer, align=uiconst.TOPLEFT, pos=((self.width - 20) / 2,
             (self.height - 20) / 2 - 2,
             20,
             20))
        if len(self.overlapStackContainer.children) != amount:
            self.overlapStackContainer.Flush()
            for i in xrange(min(5, amount)):
                Sprite(parent=self.overlapStackContainer, texturePath='res:/UI/Texture/classes/MapView/tagBackgroundStackIndicator.png', pos=(0,
                 -9 - i * 3,
                 20,
                 20), state=uiconst.UI_DISABLED, opacity=1.0 - i / 5.0)

    def GetIconSpriteIdleOpacity(self):
        return 1.0

    def GetBackgroundSpriteIdleOpacity(self):
        return 1.0

    def SetOverlappedState(self, overlapState):
        self.overlapMarkers = None
        if self.overlapStackContainer:
            overlapStackContainer = self.overlapStackContainer
            self.overlapStackContainer = None
            overlapStackContainer.Close()
        if overlapState:
            self.iconSprite.opacity = 0.0
            self.backgroundSprite.opacity = 0.0
            if self.dScanHilite:
                self.dScanHilite.Hide()
            if self.markerContainer:
                self.markerContainer.pickState = uiconst.TR2_SPS_OFF
        else:
            self.iconSprite.opacity = self.GetIconSpriteIdleOpacity()
            self.backgroundSprite.opacity = self.GetBackgroundSpriteIdleOpacity()
            if self.markerContainer:
                self.markerContainer.pickState = uiconst.TR2_SPS_ON

    def GetOverlapSortValue(self, reset = False):
        if self.overlapSortValue and not reset:
            return self.overlapSortValue
        self.overlapSortValue = (self.markerID[0], 0, (self.GetDisplayText() or '').lower())
        return self.overlapSortValue

    def UpdateActiveAndHilightState(self, *args, **kwds):
        if self.markerContainer:
            if self.hilightState or self.activeState:
                if self.highlightFrame is None or self.highlightFrame.destroyed:
                    self.highlightFrame = Sprite(parent=self.markerContainer, pos=(0, 0, 30, 30), name='highlightFrame', state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/Bracket/selectionCircle.png', align=uiconst.CENTER, color=(1.0, 1.0, 1.0, 0.3))
                self.highlightFrame.opacity = 0.5 if self.hilightState else 0.25
                self.ShowLabel()
            else:
                if self.highlightFrame and not self.highlightFrame.destroyed:
                    self.highlightFrame.opacity = 0.0
                if self.label:
                    self.label.Close()

    def GetLabelText(self):
        displayName = self.GetDisplayText()
        distance = self.GetDistance()
        if distance is not None:
            displayName += ' ' + FmtDist(distance)
        return displayName

    def ShowLabel(self):
        if not self.label or self.label.destroyed:
            self.label = BracketShadowLabel(parent=self.markerContainer.parent, name='marker_label', align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL, text=self.GetBracketLabelText(), bracket=self.markerContainer, idx=0)
            self._SetLabelOffset()
        else:
            self.label.SetOrder(0)

    def GetBracketLabelText(self):
        return self.GetLabelText()

    def _SetLabelOffset(self):
        xb, yb = self.label.bindings
        xb.offset = (ScaleDpi(26),
         0,
         0,
         0)
        yb.offset = (ScaleDpi(2),
         0,
         0,
         0)
