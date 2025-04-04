#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sensorsuite\overlay\sitecompass.py
import bluepy
from carbon.common.lib.const import SEC
from carbon.common.script.util.mathUtil import MATH_PI_2, MATH_2_PI, MATH_PI_8
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui.control.checkbox import Checkbox
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.transform import Transform
import carbonui.const as uiconst
import geo2
import math
import logging
from carbonui.uianimations import animations
from carbonui.util import colorblind
from eve.client.script.ui.control.tooltips import ShortcutHint
import gametime
import sensorsuite.overlay.const as overlayConst
from localization import GetByLabel
from sensorsuite.overlay.sitetype import *
from eve.client.script.util.settings import IsShipHudTopAligned
from sensorsuite.overlay.siteconst import COMPASS_DIRECTIONS_COLOR, COMPASS_SWEEP_COLOR, COMPASS_OPACITY_ACTIVE
from sensorsuite.overlay.sitefilter import SiteButton
import trinity
from carbonui.uicore import uicore
logger = logging.getLogger(__name__)
COMPASS_WIDTH = 200
INDICATOR_RADIUS_OFFSET = 16
INDICATOR_HEIGHT = 18
INDICATOR_WIDTH = 15
INCLINATION_TICK_MAX_OFFSET = 6
INCLINATION_TICK_TOP_OFFSET = 0
INCLINATION_TICK_BASE_OPACITY = 0.5
INCLINATION_TICK_HIGHLIGHT_OPACITY = 0.4
INCLINATION_HIGHLIGHT_RANGE_RADIANS = MATH_PI_8

def AreVectorsEqual(a, b, delta):
    for x in xrange(3):
        if math.fabs(a[x] - b[x]) > delta:
            return False

    return True


class Compass(Container):
    default_name = 'compass'
    default_width = COMPASS_WIDTH
    default_height = COMPASS_WIDTH
    default_align = uiconst.CENTER
    default_state = uiconst.UI_NORMAL
    default_pickRadius = COMPASS_WIDTH / 2.0 - 10

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.michelle = sm.GetService('michelle')
        self.frameContainer = Container(name='compass_transform', parent=self, width=COMPASS_WIDTH, height=COMPASS_WIDTH, align=uiconst.CENTER)
        self.compassTransform = Transform(name='compass_transform', parent=self, width=COMPASS_WIDTH, height=COMPASS_WIDTH, align=uiconst.CENTER, opacity=COMPASS_OPACITY_ACTIVE)
        Sprite(name='compass_dots', bgParent=self.compassTransform, texturePath='res:/UI/Texture/classes/SensorSuite/compass_dots.png', color=COMPASS_DIRECTIONS_COLOR.GetRGBA())
        self.sweepTransform = Transform(bgParent=self.compassTransform, name='compass_transform', width=COMPASS_WIDTH, height=COMPASS_WIDTH, align=uiconst.CENTER, opacity=0.0)
        Sprite(name='sensor_sweep', bgParent=self.sweepTransform, texturePath='res:/UI/Texture/classes/SensorSuite/scan_sweep.png', blendMode=trinity.TR2_SBM_ADD, color=COMPASS_SWEEP_COLOR.GetRGBA())
        Sprite(name='sensor_centerline', bgParent=self.frameContainer, texturePath='res:/UI/Texture/classes/SensorSuite/compass_centerline.png', blendMode=trinity.TR2_SBM_ADD, opacity=0.2)
        Sprite(name='compass_underlay', bgParent=self.frameContainer, texturePath='res:/UI/Texture/classes/SensorSuite/compass_underlay.png')
        self.sensorSuite = sm.GetService('sensorSuite')
        self.siteIndicatorsBySiteID = {}
        self.lastPose = None
        logger.debug('Compass updating starting')
        self.timer = AutoTimer(40, self.__UpdateCompass)
        self.sensorSuite.Subscribe(overlayConst.MESSAGE_ON_SENSOR_OVERLAY_SITE_CHANGED, self.OnSiteChanged)
        self.sensorSuite.Subscribe(overlayConst.MESSAGE_ON_SENSOR_OVERLAY_SWEEP_STARTED, self.OnSweepStarted)
        self.sensorSuite.Subscribe(overlayConst.MESSAGE_ON_SENSOR_OVERLAY_SWEEP_ENDED, self.OnSweepEnded)
        self.sensorSuite.Subscribe(overlayConst.MESSAGE_ON_SENSOR_OVERLAY_ENABLED, self.OnSensorOverlayEnabled)
        self.sensorSuite.Subscribe(overlayConst.MESSAGE_ON_SENSOR_OVERLAY_DISABLED, self.OnSensorOverlayDisabled)
        self.sensorSuite.Subscribe(overlayConst.MESSAGE_ON_SENSOR_OVERLAY_SITE_MOVED, self.OnSiteMoved)
        if self.sensorSuite.IsOverlayActive():
            self.OnSensorOverlayEnabled()
        else:
            self.OnSensorOverlayDisabled()

    def OnSensorOverlayEnabled(self):
        animations.FadeIn(self.frameContainer, endVal=1.0, duration=0.2, curveType=uiconst.ANIM_SMOOTH)
        animations.FadeIn(self.compassTransform, endVal=COMPASS_OPACITY_ACTIVE, duration=0.2, curveType=uiconst.ANIM_OVERSHOT5)

    def OnSensorOverlayDisabled(self):
        animations.FadeTo(self.frameContainer, startVal=self.frameContainer.opacity, endVal=0.1, duration=0.75, curveType=uiconst.ANIM_SMOOTH)
        animations.FadeTo(self.compassTransform, startVal=self.compassTransform.opacity, endVal=0.15, duration=0.4, curveType=uiconst.ANIM_SMOOTH)

    def GetCamera(self):
        return sm.GetService('sceneManager').GetActiveSpaceCamera()

    def Close(self):
        Container.Close(self)
        self.timer = None
        self.sensorSuite.Unsubscribe(overlayConst.MESSAGE_ON_SENSOR_OVERLAY_SITE_CHANGED, self.OnSiteChanged)
        self.sensorSuite.Unsubscribe(overlayConst.MESSAGE_ON_SENSOR_OVERLAY_SWEEP_STARTED, self.OnSweepStarted)
        self.sensorSuite.Unsubscribe(overlayConst.MESSAGE_ON_SENSOR_OVERLAY_SWEEP_ENDED, self.OnSweepEnded)
        self.sensorSuite.Unsubscribe(overlayConst.MESSAGE_ON_SENSOR_OVERLAY_ENABLED, self.OnSensorOverlayEnabled)
        self.sensorSuite.Unsubscribe(overlayConst.MESSAGE_ON_SENSOR_OVERLAY_DISABLED, self.OnSensorOverlayDisabled)
        self.sensorSuite.Unsubscribe(overlayConst.MESSAGE_ON_SENSOR_OVERLAY_SITE_MOVED, self.OnSiteMoved)

    @bluepy.TimedFunction('sitecompass::__UpdateCompass')
    def __UpdateCompass(self):
        bp = self.michelle.GetBallpark()
        if bp is None:
            return
        camera = self.GetCamera()
        camParentRotation = camera.GetRotationQuat()
        camRotation = geo2.QuaternionRotationGetYawPitchRoll(camParentRotation)
        cx, cy, cz = geo2.QuaternionTransformVector(camParentRotation, (0, 0, -1.0))
        camLengthInPlane = geo2.Vec2Length((cx, cz))
        camAngle = math.atan2(cy, camLengthInPlane)
        yaw = camRotation[0]
        self.compassTransform.rotation = -yaw + math.pi
        myPos = bp.GetCurrentEgoPos()
        if self.lastPose:
            lastCamRot, lastPos = self.lastPose
            isNewCamRotation = not AreVectorsEqual(lastCamRot, camRotation, 0.05)
            isNewPosition = not AreVectorsEqual(lastPos, myPos, 0.5)
            isNewPose = isNewPosition or isNewCamRotation
        else:
            isNewPosition = True
            isNewPose = True
        for siteID, indicator in self.siteIndicatorsBySiteID.iteritems():
            if indicator.isNew or isNewPose:
                toSiteVec = geo2.Vec3SubtractD(indicator.data.position, myPos)
                toSiteVec = geo2.Vec3NormalizeD(toSiteVec)
                if indicator.isNew or isNewPosition:
                    angle = math.atan2(-toSiteVec[2], toSiteVec[0])
                    indicator.SetRotation(angle + MATH_PI_2)
                sx, sy, sz = toSiteVec
                siteLengthInPlane = geo2.Vec2Length((sx, sz))
                siteAngle = math.atan2(sy, siteLengthInPlane)
                inclinationAngle = siteAngle - camAngle
                verticalAngle = min(inclinationAngle, MATH_PI_2)
                indicator.SetInclination(verticalAngle)
                indicator.isNew = False

        self.lastPose = (camRotation, myPos)

    def OnSiteChanged(self, siteData):
        indicator = self.siteIndicatorsBySiteID.get(siteData.siteID)
        if indicator:
            indicator.isNew = True
        self.UpdateVisibleSites()

    def OnSweepStarted(self, systemReadyTime, durationInSec, viewAngleInPlane, orderedDelayAndSiteList, sweepStartDelaySec):
        logger.debug('OnSweepStarted readyTime=%s durationInSec=%s angle=%s sweepStartDelayMSec=%s', systemReadyTime, durationInSec, viewAngleInPlane, sweepStartDelaySec)
        timeNow = gametime.GetSimTime()
        timeSinceStartSec = float(timeNow - systemReadyTime) / SEC
        if timeSinceStartSec > sweepStartDelaySec:
            logger.debug('OnSweepStarted too late. timeSinceStartSec=%s timeNow=%s', timeSinceStartSec, timeNow)
            self.UpdateVisibleSites()
            self.OnSweepEnded()
            return
        curveSet = animations.CreateCurveSet(useRealTime=False)
        timeOffset = sweepStartDelaySec - timeSinceStartSec
        self.UpdateVisibleSites()
        animations.FadeTo(self.sweepTransform, duration=durationInSec, startVal=0.0, endVal=0.0, curveType=((0.05, 1.0), (0.95, 1.0)), timeOffset=timeOffset, curveSet=curveSet)
        viewAngleInPlane += MATH_PI_2
        animations.Tr2DRotateTo(self.sweepTransform, duration=durationInSec, startAngle=viewAngleInPlane, endAngle=viewAngleInPlane + MATH_2_PI, curveType=uiconst.ANIM_LINEAR, timeOffset=timeOffset, curveSet=curveSet)
        for delaySec, siteData in orderedDelayAndSiteList:
            indicator = self.siteIndicatorsBySiteID.get(siteData.siteID)
            if indicator:
                animations.FadeIn(indicator, duration=0.2, curveType=uiconst.ANIM_OVERSHOT, timeOffset=delaySec - timeSinceStartSec, curveSet=curveSet)

    def OnSweepEnded(self):
        for indicator in self.compassTransform.children:
            indicator.opacity = 1.0

    @bluepy.TimedFunction('sitecompass::UpdateVisibleSites')
    def UpdateVisibleSites(self):
        setattr(self, 'updateVisibleSitesTimerThread', AutoTimer(200, self._UpdateVisibleSites))

    @bluepy.TimedFunction('sitecompass::_UpdateVisibleSites')
    def _UpdateVisibleSites(self):
        try:
            if not self.sensorSuite.IsSolarSystemReady():
                return
            siteMap = self.sensorSuite.siteController.GetVisibleSiteMap()
            for siteID in self.siteIndicatorsBySiteID.keys():
                if siteID not in siteMap:
                    self.RemoveSiteIndicator(siteID)

            for siteData in siteMap.itervalues():
                if siteData.siteID not in self.siteIndicatorsBySiteID:
                    self.AddSiteIndicator(siteData)

        finally:
            self.updateVisibleSitesTimerThread = None

    def AddSiteIndicator(self, siteData):
        logger.debug('adding site indicator %s', siteData.siteID)
        indicator = CompassIndicator(parent=self.compassTransform, siteData=siteData)
        if self.sensorSuite.IsSweepDone() or IsSiteInstantlyAccessible(siteData):
            indicator.opacity = 1.0
        else:
            indicator.opacity = 0.0
        self.siteIndicatorsBySiteID[siteData.siteID] = indicator

    def RemoveSiteIndicator(self, siteID):
        logger.debug('removing site indicator %s', siteID)
        indicator = self.siteIndicatorsBySiteID.pop(siteID)
        indicator.Close(self.compassTransform)

    def RemoveAll(self):
        for siteID in self.siteIndicatorsBySiteID.keys():
            self.RemoveSiteIndicator(siteID)

    def LoadTooltipPanel(self, tooltipPanel, *args):
        LoadSensorOverlayFilterTooltip(tooltipPanel)

    def GetTooltipPosition(self):
        left, top, width, height = self.GetAbsolute()
        left += width / 2
        if IsShipHudTopAligned():
            top += height - 7
        else:
            top += 9
        return (left,
         top,
         0,
         0)

    def GetTooltipPointer(self):
        if IsShipHudTopAligned():
            return uiconst.POINT_TOP_2
        return uiconst.POINT_BOTTOM_2

    def OnSiteMoved(self, siteData):
        indicator = self.siteIndicatorsBySiteID.get(siteData.siteID, None)
        if not indicator:
            return
        indicator.UpdateSitePosition(siteData.position)
        indicator.isNew = True


class CompassIndicator(object):

    def __init__(self, parent = None, siteData = None):
        self.data = siteData
        self.isNew = True
        self._renderObject = trinity.Tr2Sprite2dTransform()
        self._renderObject.rotationCenter = (0.5, 0.5)
        self._renderObject.name = 'compass_indicator2'
        self._renderObject.displayX = uicore.ScaleDpi(INDICATOR_RADIUS_OFFSET / 2)
        self._renderObject.displayY = uicore.ScaleDpi(INDICATOR_RADIUS_OFFSET / 2)
        self._renderObject.displayWidth = uicore.ScaleDpi(COMPASS_WIDTH - INDICATOR_RADIUS_OFFSET)
        self._renderObject.displayHeight = uicore.ScaleDpi(COMPASS_WIDTH - INDICATOR_RADIUS_OFFSET)
        self._renderObject.pickState = uiconst.TR2_SPS_OFF
        self._sprite = trinity.Tr2Sprite2d()
        self._sprite.name = 'VisibleBase'
        self._sprite.blendMode = trinity.TR2_SBM_ADDX2
        self._sprite.spriteEffect = trinity.TR2_SFX_COPY
        self._sprite.color = colorblind.CheckReplaceColor(self.data.baseColor.GetRGBA())
        self._sprite.displayX = uicore.ScaleDpi((COMPASS_WIDTH - INDICATOR_RADIUS_OFFSET - INDICATOR_WIDTH) / 2)
        self._sprite.displayY = 0
        self._sprite.displayWidth = uicore.ScaleDpi(INDICATOR_WIDTH)
        self._sprite.displayHeight = uicore.ScaleDpi(INDICATOR_HEIGHT)
        self._sprite.texturePrimary = trinity.Tr2Sprite2dTexture()
        self._sprite.texturePrimary.resPath = 'res:/UI/Texture/classes/SensorSuite/small_tick.png'
        self._renderObject.children.append(self._sprite)
        self._verticalSprite = trinity.Tr2Sprite2d()
        self._verticalSprite.name = 'VisibleBase'
        self._verticalSprite.blendMode = trinity.TR2_SBM_ADD
        self._verticalSprite.spriteEffect = trinity.TR2_SFX_COPY
        self._verticalSprite.color = colorblind.CheckReplaceColor(self.data.baseColor.GetRGBA())
        self._verticalSprite.displayX = uicore.ScaleDpi((COMPASS_WIDTH - INDICATOR_RADIUS_OFFSET - INDICATOR_WIDTH) / 2)
        self._verticalSprite.displayY = 0
        self._verticalSprite.displayWidth = uicore.ScaleDpi(INDICATOR_WIDTH)
        self._verticalSprite.displayHeight = uicore.ScaleDpi(INDICATOR_HEIGHT)
        self._verticalSprite.texturePrimary = trinity.Tr2Sprite2dTexture()
        self._verticalSprite.texturePrimary.resPath = 'res:/UI/Texture/classes/SensorSuite/big_tick.png'
        self._verticalSprite.color = colorblind.CheckReplaceColor(self._verticalSprite.color[:3] + (0.5,))
        self._renderObject.children.append(self._verticalSprite)
        if parent.renderObject:
            parent.renderObject.children.append(self._renderObject)

    def SetRotation(self, rotation):
        self._renderObject.rotation = -rotation

    def SetInclination(self, angle):
        offset = -angle / MATH_PI_2 * INCLINATION_TICK_MAX_OFFSET
        offset = min(max(offset, -INCLINATION_TICK_MAX_OFFSET), INCLINATION_TICK_MAX_OFFSET)
        self._sprite.displayY = uicore.ScaleDpi(INCLINATION_TICK_TOP_OFFSET + offset)
        absAngle = math.fabs(angle)
        if absAngle < INCLINATION_HIGHLIGHT_RANGE_RADIANS:
            opacity = INCLINATION_TICK_BASE_OPACITY + (1 - absAngle / INCLINATION_HIGHLIGHT_RANGE_RADIANS) * INCLINATION_TICK_HIGHLIGHT_OPACITY
        else:
            opacity = INCLINATION_TICK_BASE_OPACITY
        self._sprite.color = colorblind.CheckReplaceColor(self._sprite.color[:3] + (opacity,))

    def UpdateSitePosition(self, position):
        self.data.position = position

    def Close(self, parent):
        try:
            parent.renderObject.children.remove(self._renderObject)
        except RuntimeError:
            pass


def AddShortcut(tooltipPanel, shortcut):
    ml, mt, mr, mb = tooltipPanel.margin
    shortcutObj = ShortcutHint(text=shortcut)
    tooltipPanel.AddCell(shortcutObj, cellPadding=(7,
     0,
     -mr + 6,
     0))


def LoadSensorOverlayFilterTooltip(tooltipPanel):
    sensorSuite = sm.GetService('sensorSuite')
    if sensorSuite.IsOverlaySuppressed():
        return
    tooltipPanel.pickState = uiconst.TR2_SPS_ON
    tooltipPanel.LoadGeneric3ColumnTemplate()
    cmd = uicore.cmd.commandMap.GetCommandByName('CmdToggleSensorOverlay')
    label = cmd.GetName()
    shortcutStr = cmd.GetShortcutAsString()
    tooltipPanel.AddLabelMedium(text=label, padTop=2)
    tooltipPanel.AddCell(OverlayCheckbox(align=uiconst.CENTERTOP, width=48))
    tooltipPanel.AddShortcutCell(shortcutStr)
    tooltipPanel.AddCell(Container(height=8, align=uiconst.NOALIGN), colSpan=3)
    buttons = []
    siteTypes = [ANOMALY,
     STATIC_SITE,
     BOOKMARK,
     SHARED_BOOKMARK,
     SIGNATURE,
     STRUCTURE,
     MISSION]
    for siteType in siteTypes:
        handler = sensorSuite.siteController.GetSiteHandler(siteType)
        config = handler.GetFilterConfig()
        button = SiteButton(filterConfig=config, isActive=config.enabled)
        buttons.append(button)
        tooltipPanel.AddCell(button)

    maxWidth = max([ b.width for b in buttons ])
    for b in buttons:
        b.width = maxWidth


class OverlayCheckbox(Checkbox):
    default_state = uiconst.UI_NORMAL
    default_text = GetByLabel('UI/Inflight/Scanner/SensorOverlayOn')

    def ApplyAttributes(self, attributes):
        super(OverlayCheckbox, self).ApplyAttributes(attributes)
        self.sensorSuite = sm.GetService('sensorSuite')
        self.UpdateCheckboxState()
        self.Subscribe()

    def OnChange(self):
        if self.checked:
            self.sensorSuite.EnableSensorOverlay()
        else:
            self.sensorSuite.DisableSensorOverlay()

    def UpdateCheckboxState(self):
        self.SetValue(self.sensorSuite.IsOverlayActive())

    def Subscribe(self):
        self.sensorSuite.Subscribe(overlayConst.MESSAGE_ON_SENSOR_OVERLAY_ENABLED, self.UpdateCheckboxState)
        self.sensorSuite.Subscribe(overlayConst.MESSAGE_ON_SENSOR_OVERLAY_DISABLED, self.UpdateCheckboxState)

    def Unsubscribe(self):
        self.sensorSuite.Unsubscribe(overlayConst.MESSAGE_ON_SENSOR_OVERLAY_ENABLED, self.UpdateCheckboxState)
        self.sensorSuite.Unsubscribe(overlayConst.MESSAGE_ON_SENSOR_OVERLAY_DISABLED, self.UpdateCheckboxState)

    def Close(self):
        super(OverlayCheckbox, self).Close()
        self.Unsubscribe()
