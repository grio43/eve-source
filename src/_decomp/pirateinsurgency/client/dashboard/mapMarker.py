#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\pirateinsurgency\client\dashboard\mapMarker.py
import eveicon
from carbonui.primitives.transform import Transform
from eve.client.script.ui.services.insurgenceDashboardSvc import WrapCallbackWithErrorHandling
from functools import partial
from carbonui.primitives.container import Container
import carbonui.const as uiconst
import eve.client.script.ui.shared.mapView.mapViewConst as mapViewConst
import geo2
from carbonui.primitives.base import ScaleDpi
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from eve.client.script.ui.shared.mapView.mapViewUtil import MapPosToSolarSystemPos
from eve.client.script.ui.shared.mapView.markers.mapMarkerBase import MarkerSolarSystemBased
from pirateinsurgency.client.dashboard.const import STAGE_TO_BLOB_SIZE, STAGE_TO_BLOB_TEXTURE, STAGE_TO_STROKE_TEXTURE, GetPirateFactionIDFromWarzoneID, GetFactionColorFromPerspectiveOfMilitia, GetSuppressionColor
from pirateinsurgency.client.dashboard.widgets.gaugeStick import GaugeOnAStick
from pirateinsurgency.client.utils import CalculateCurrentStageFromFraction

class InsurgencyBlobMarker(MarkerSolarSystemBased):
    __notifyevents__ = ['OnCorruptionValueChanged_Local', 'OnSuppressionValueChanged_Local']
    label = None
    highlightFrame = None
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
    default_corruptionStage = 0
    default_suppressionStage = 0

    def __init__(self, *args, **kwds):
        self.highlightOnLoad = kwds.get('highlightOnLoad', False)
        MarkerSolarSystemBased.__init__(self, *args, **kwds)
        self.iconColor = (0, 0, 0, 0)
        self.texturePath = None
        self.corruptionStage = kwds.get('corruptionStage', self.default_corruptionStage)
        self.suppressionStage = kwds.get('suppressionStage', self.default_suppressionStage)
        self.dashboardSvc = kwds.get('dashboardSvc', self.default_suppressionStage)
        self.solarSystemID = kwds.get('solarSystemID')
        self.campaignSnapshot = kwds.get('snapshot')
        self.iceHeist = kwds.get('iceHeist', None)
        self.gauge = None
        self.selected = False
        self.iceHeistSprite = None
        sm.RegisterNotify(self)

    def GetMenu(self, *args):
        return sm.GetService('menu').CelestialMenu(self.solarSystemID)

    def Load(self):
        if self.isLoaded:
            return
        self.isLoaded = True
        self.ConstructLayout()
        self.ConstructVisualization()

    def OnSuppressionValueChanged_Local(self, systemID, data):
        if systemID != self.solarSystemID:
            return
        if not self.isLoaded:
            return
        numerator = data.numerator
        denominator = data.denominator
        callback = partial(self.UpdateSuppressionStageBasedOnFraction, numerator=numerator, denominator=denominator)
        wrappedCallback = WrapCallbackWithErrorHandling(callback, parentContainer=None)
        self.dashboardSvc.RequestSuppressionStages(wrappedCallback)

    def OnCorruptionValueChanged_Local(self, systemID, data):
        if systemID != self.solarSystemID:
            return
        if not self.isLoaded:
            return
        numerator = data.numerator
        denominator = data.denominator
        callback = partial(self.UpdateCorruptionStageBasedOnFraction, numerator=numerator, denominator=denominator)
        wrappedCallback = WrapCallbackWithErrorHandling(callback, parentContainer=None)
        self.dashboardSvc.RequestCorruptionStages(wrappedCallback)

    def UpdateCorruptionStageBasedOnFraction(self, stages, numerator, denominator):
        self.corruptionStage = CalculateCurrentStageFromFraction(numerator, denominator, stages)
        self.ConstructVisualization()

    def UpdateSuppressionStageBasedOnFraction(self, stages, numerator, denominator):
        self.suppressionStage = CalculateCurrentStageFromFraction(numerator, denominator, stages)
        self.ConstructVisualization()

    def ConstructLayout(self):
        self.gauge = GaugeOnAStick(parent=self.markerContainer, align=uiconst.TOBOTTOM_NOPUSH, height=248, lineHeight=200, width=48, dashboardSvc=self.dashboardSvc, solarSystemID=self.solarSystemID, top=5, opacity=0, corruptionStage=self.corruptionStage, suppressionStage=self.suppressionStage, iceHeist=self.iceHeist)
        self.dashboardSvc.SIGNAL_solarSystemSelectedFromMap.connect(self._OnSolarSystemSelectedFromMapCallback)
        self.markerContainer.pos = (0,
         0,
         self.width,
         self.height)
        if self.highlightOnLoad and not self.updated:
            self.highlightOnLoad = False
            self.HighlightLoad()
        self.UpdateInRangeIndicatorState()
        if self.selected:
            self._OnSolarSystemSelectedFromMapCallback(self.solarSystemID)
        dim = max(STAGE_TO_BLOB_SIZE[self.suppressionStage], STAGE_TO_BLOB_SIZE[self.corruptionStage])
        self.visCont = Container(parent=self.markerContainer, width=dim, height=dim, align=uiconst.CENTER)
        if self.iceHeist is not None:
            self.iceHeistSprite = Sprite(parent=Transform(parent=self.markerContainer, width=32, height=32, align=uiconst.TOTOP_NOPUSH, top=-14, left=-9), width=32, height=32, texturePath=eveicon.tow, state=uiconst.UI_DISABLED)

    def ConstructVisualization(self):
        self.visCont.Flush()
        gap = 10
        myFactionID = session.warfactionid
        pirateFactionID = GetPirateFactionIDFromWarzoneID(self.campaignSnapshot.warzoneID)
        corruptionFillColor = GetFactionColorFromPerspectiveOfMilitia(myFactionID, pirateFactionID)
        corruptionStrokeColor = GetFactionColorFromPerspectiveOfMilitia(myFactionID, pirateFactionID, fill=False)
        suppressionFillColor = GetSuppressionColor()
        suppressionStrokeColor = GetSuppressionColor()
        Sprite(parent=self.visCont, texturePath=STAGE_TO_BLOB_TEXTURE[self.corruptionStage], width=STAGE_TO_BLOB_SIZE[self.corruptionStage], height=STAGE_TO_BLOB_SIZE[self.corruptionStage], state=uiconst.UI_DISABLED, color=corruptionFillColor, align=uiconst.CENTER)
        Sprite(parent=self.visCont, texturePath=STAGE_TO_BLOB_TEXTURE[self.suppressionStage], width=STAGE_TO_BLOB_SIZE[self.suppressionStage] - gap, height=STAGE_TO_BLOB_SIZE[self.suppressionStage] - gap, state=uiconst.UI_DISABLED, color=suppressionFillColor, align=uiconst.CENTER)
        Sprite(parent=self.visCont, texturePath=STAGE_TO_STROKE_TEXTURE[self.corruptionStage], width=STAGE_TO_BLOB_SIZE[self.corruptionStage], height=STAGE_TO_BLOB_SIZE[self.corruptionStage], state=uiconst.UI_DISABLED, color=corruptionStrokeColor, align=uiconst.CENTER, outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, glowBrightness=2)
        Sprite(parent=self.visCont, texturePath=STAGE_TO_STROKE_TEXTURE[self.suppressionStage], width=STAGE_TO_BLOB_SIZE[self.suppressionStage] - gap, height=STAGE_TO_BLOB_SIZE[self.suppressionStage] - gap, state=uiconst.UI_DISABLED, color=suppressionStrokeColor, align=uiconst.CENTER, outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, glowBrightness=2)

    def _OnSolarSystemSelectedFromMapCallback(self, systemID):
        if self.gauge:
            if systemID == self.solarSystemID:
                self.selected = True
                animations.FadeIn(self.gauge, duration=0.25)
                animations.MorphScalar(self.gauge, 'height', startVal=0, endVal=248, duration=0.25)
                if self.iceHeistSprite is not None:
                    animations.FadeOut(self.iceHeistSprite)
            else:
                self.selected = False
                animations.FadeOut(self.gauge, duration=0.25)
                animations.MorphScalar(self.gauge, 'height', startVal=248, endVal=0, duration=0.25)
                if self.iceHeistSprite is not None:
                    animations.FadeIn(self.iceHeistSprite)

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
        self.dashboardSvc.SIGNAL_solarSystemSelectedFromMap.disconnect(self._OnSolarSystemSelectedFromMapCallback)

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

    def ShowLabel(self):
        pass

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
