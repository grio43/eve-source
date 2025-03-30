#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\mapView\markers\mapMarkerScanResult.py
import math
from carbon.common.script.util.format import FmtDist
from carbonui.primitives.base import ScaleDpi
from carbonui.primitives.container import Container
from carbonui.primitives.transform import Transform
from carbonui.primitives.vectorlinetrace import VectorLineTrace
from carbonui.uianimations import animations
from carbonui.util.color import Color
from eve.client.script.ui.control.gaugeCircular import GaugeCircular
from eve.client.script.ui.control.themeColored import SpriteThemeColored
from eve.client.script.ui.inflight.scannerFiles.scannerUtil import GetScanDifficultyText
from eve.client.script.ui.shared.mapView.markers.mapMarkerBase_Icon import MarkerIconBase
from eve.client.script.ui.shared.mapView.markers.mapMarkerSpaceObjectRadialMenu import MapMarkerSpaceObjectRadialMenu
from eve.client.script.ui.shared.mapView.markers.mapMarkerUtil import GetResultColor, GetResultTexturePath
from eve.common.lib.appConst import minWarpDistance
import carbonui.const as uiconst
from localization import GetByLabel
from logmodule import LogException
from sensorsuite.overlay.controllers.probescanner import SiteDataFromScanResult
import geo2
from eveservices.menu import GetMenuService
MIN_WARP_DISTANCE_SQUARED = minWarpDistance ** 2

def IsResultWithinWarpDistance(result):
    ballpark = sm.GetService('michelle').GetBallpark()
    egoBall = ballpark.GetBall(ballpark.ego)
    egoPos = geo2.Vector(egoBall.x, egoBall.y, egoBall.z)
    resultPos = geo2.Vector(*result.data)
    distanceSquared = geo2.Vec3LengthSq(egoPos - resultPos)
    return distanceSquared > MIN_WARP_DISTANCE_SQUARED


class MarkerScanResult(MarkerIconBase):
    __notifyevents__ = ['OnSiteSelectionChanged', 'OnClientEvent_PerfectScanResultReached']
    distanceFadeAlphaNearFar = None
    backgroundTexturePath = None
    graph = None
    highlightFrame = None
    label = None

    def __init__(self, *args, **kwds):
        MarkerIconBase.__init__(self, *args, **kwds)
        sm.RegisterNotify(self)
        self.resultData = resultData = kwds['resultData']
        self.gaugeCircular = None
        self.gaugeCont = None
        self.texturePath = GetResultTexturePath(self.resultData)
        self.projectBracket.offsetY = 0
        self.iconSprite = None
        self.CreateClientBall()

    def UpdateIcon(self):
        self.texturePath = GetResultTexturePath(self.resultData)
        if self.iconSprite:
            self.iconSprite.texturePath = self.texturePath

    def Close(self, *args):
        MarkerIconBase.Close(self, *args)
        sm.UnregisterNotify(self)

    def UpdateResultData(self, resultData):
        self.resultData = resultData
        if self.isLoaded:
            self.UpdateScanResult()
            self.CheckShowGauge()
        self.UpdateIcon()

    def SetOverlappedState(self, overlapState):
        self.overlapMarkers = None
        if self.overlapStackContainer:
            overlapStackContainer = self.overlapStackContainer
            self.overlapStackContainer = None
            overlapStackContainer.Close()

    def Load(self):
        if self.isLoaded:
            return
        MarkerIconBase.Load(self)
        self.UpdateScanResult()
        self.CheckShowGauge()

    def CheckShowGauge(self):
        if sm.GetService('scanSvc').IsSiteSelected(self.resultData.id):
            self.ConstructGauge()
            self.UpdateCircularGauge()
            self.gaugeCont.Show()
        elif self.gaugeCont:
            self.gaugeCont.Hide()

    def ConstructGauge(self):
        if not self.gaugeCircular or self.gaugeCircular.destroyed or not self.gaugeCircular.parent:
            self.gaugeCont = Container(parent=self.markerContainer, pos=(0, 0, 60, 60), align=uiconst.CENTER)
            self.gaugeCircular = GaugeCircular(parent=self.gaugeCont, radius=22, align=uiconst.CENTER, lineWidth=2, showMarker=False, state=uiconst.UI_DISABLED)
            SpriteThemeColored(parent=self.gaugeCont, align=uiconst.TOALL, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/Shared/CircularGradient.png', colorType=uiconst.COLORTYPE_UIBASE, opacity=0.4)

    def GetResultColor(self):
        certainty = self.resultData.certainty
        return GetResultColor(certainty)

    def UpdateScanResult(self):
        color = self.GetResultColor()
        self.iconColor = color
        self.iconSprite.SetRGBA(*color)
        try:
            self.UpdateCircularGauge()
        except:
            LogException()
            raise

    def UpdateCircularGauge(self):
        if not self.gaugeCircular:
            return
        col = self.GetResultColor()
        colBg = Color(*col).SetBrightness(0.4).GetRGBA()
        colEnd = col
        brightness = Color(*col).GetBrightness()
        colStart = Color(*colEnd).SetBrightness(brightness * 0.8).GetRGBA()
        self.gaugeCircular.SetColor(colStart, colEnd)
        self.gaugeCircular.SetColorBg(colBg)
        certainty = self.resultData.certainty
        self.gaugeCircular.SetValue(certainty)

    def GetLabelText(self):
        scanSvc = sm.GetService('scanSvc')
        displayName = scanSvc.GetDisplayName(self.resultData)
        labelText = '%s %s' % (self.resultData.id, displayName)
        distance = self.GetDistance()
        if distance is not None:
            labelText += ' ' + FmtDist(distance)
        return labelText

    def GetBracketLabelText(self):
        labelText = MarkerIconBase.GetBracketLabelText(self)
        if self.resultData.certainty < 1.0:
            difficulty = GetScanDifficultyText(self.resultData.difficulty)
            labelText += '\n' + GetByLabel('UI/Inflight/Scanner/ScanningDifficulty', difficulty=difficulty)
        return labelText

    def _SetLabelOffset(self):
        MarkerIconBase._SetLabelOffset(self)
        xb, yb = self.label.bindings
        xb.offset = (ScaleDpi(32),
         0,
         0,
         0)
        if self.resultData.certainty < 1.0:
            yb.offset = (ScaleDpi(-8),
             0,
             0,
             0)
        else:
            yb.offset = (ScaleDpi(2),
             0,
             0,
             0)

    def IsPartialResult(self):
        return self.resultData.certainty < 1.0

    def GetMenu(self):
        scanSvc = sm.GetService('scanSvc')
        scanResult = SiteDataFromScanResult(self.resultData)
        return scanSvc.GetScanResultMenuWithIgnore(scanResult, self.resultData.groupID)

    def GetDistance(self):
        bp = sm.GetService('michelle').GetBallpark()
        if bp is None:
            return
        if not bp.ego:
            return
        ego = bp.balls[bp.ego]
        myPos = (ego.x, ego.y, ego.z)
        return self.resultData.GetDistance(myPos)

    def OnMouseDown(self, *args):
        siteData = SiteDataFromScanResult(self.resultData)
        if self.clientBall:
            GetMenuService().TryExpandActionMenu(itemID=self.clientBall.id, clickedObject=self, siteData=siteData, radialMenuClass=MapMarkerSpaceObjectRadialMenu, markerObject=self)

    def OnSiteSelectionChanged(self):
        self.CheckShowGauge()

    def OnClick(self, *args, **kwds):
        MarkerIconBase.OnClick(self, *args, **kwds)
        doDScan = self.CheckDirectionalScanItem()
        if not doDScan:
            sm.GetService('scanSvc').SelectSite(self.resultData.id)

    def OnClientEvent_PerfectScanResultReached(self, results):
        for result in results:
            if result.id == self.resultData.id:
                self.AnimPerfectResult()

    def AnimPerfectResult(self):
        if self.gaugeCircular:
            animations.BlinkIn(self.gaugeCircular, loops=4)
        self._AnimCircle(0.25)
        self._AnimCircle(0.65)

    def _AnimCircle(self, timeOffset):
        radius = 40
        transform = Transform(parent=self.markerContainer, align=uiconst.CENTER, width=radius * 2, height=radius * 2, state=uiconst.UI_DISABLED, scalingCenter=(0.5, 0.5))
        circle = Circle(parent=transform, radius=radius, color=(0.4, 1.0, 0.4, 1.0))
        duration = 0.8
        animations.FadeTo(circle, 0.3, 0.0, duration=duration, callback=circle.Close, timeOffset=timeOffset)
        animations.MorphVector2(transform, 'scale', (0.0, 0.0), (1.4, 1.4), duration=duration, curveType=uiconst.ANIM_LINEAR, timeOffset=timeOffset)
        animations.MorphScalar(circle, 'lineWidth', radius, 0.0, duration=duration, curveType=uiconst.ANIM_LINEAR, timeOffset=timeOffset, callback=transform.Close)

    def GetMarkerOpacity(self, bracketCameraDistance, cameraZoomDistance):
        if sm.GetService('scanSvc').IsSiteSelected(self.markerID[1][0]):
            return 1.0
        else:
            return 0.6


class Circle(VectorLineTrace):
    default_color = Color.WHITE
    default_radius = 10

    def ApplyAttributes(self, attributes):
        VectorLineTrace.ApplyAttributes(self, attributes)
        color = attributes.get('color', self.default_color)
        self.radius = attributes.get('radius', self.default_radius)
        self.isLoop = True
        numPoints = max(20, self.radius)
        w = self.lineWidth / 2.0
        stepSize = 2 * math.pi / numPoints
        for i in xrange(numPoints):
            t = float(i) * stepSize
            point = self.GetLinePoint(t, w)
            self.AddPoint(point, color)

    def GetLinePoint(self, t, w):
        r = self.radius - w
        xPoint = w + r * (1.0 + math.cos(t))
        yPoint = w + r * (1.0 + math.sin(t))
        return (xPoint, yPoint)
