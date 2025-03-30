#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\planet\planetUIPins.py
import math
import random
import evetypes
import inventorycommon.typeHelpers
import trinity
import blue
import uthread
import geo2
import utillib
from carbon.common.script.sys.serviceConst import ROLE_GML
from carbonui import uiconst
from carbonui.uianimations import animations
from carbonui.util.color import Color
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.shared.planet import planetConst
from eve.client.script.ui.shared.planet.planetUILinks import LinkBase
from eve.common.lib import appConst
import localization
from eve.common.script.util.planetCommon import SurfacePoint
import eve.common.script.util.planetCommon as planetCommon
from fsdBuiltData.common.graphicIDs import GetGraphicFile
from fsdBuiltData.common.planet import get_schematic_types
from eve.client.script.ui.shared.planet import planetCommon as planetCommonUI
from eveservices.menu import GetMenuService
from menu import MenuLabel
RADIUS_PIN = 0.006
RADIUS_PIN_SELECTED = RADIUS_PIN * 1.2
RADIUS_PINEXTENDED = RADIUS_PIN * 1.65
RADIUS_CYCLE = RADIUS_PIN * 0.7
RADIUS_CYCLEEXTENDED = RADIUS_PIN * 1.25
RADIUS_LOGO = RADIUS_PIN * 0.5
RADIUS_SHADOW = RADIUS_PIN * 1.2
RADIUS_SHADOWEXTENDED = RADIUS_PINEXTENDED * 1.2
RADIUS_BUILDPIN = RADIUS_PIN * 0.8
RADIUS_PINOTHERS = RADIUS_PIN * 0.5
RADIUS_EXTRACTIONHEAD = 0.003
SCALE_PINBASE = 1.01
SCALE_PINLIFTED = 1.0105
SCALE_ONGROUND = 1.001
SCALE_PINOTHERS = 1.005
SCALE_HOLOGRAM = 1.026
SCALE_HOLOGRAMMODEL = 0.025
PINCOLORS = {appConst.groupCommandPins: planetCommonUI.PLANET_COLOR_ICON_COMMANDCENTER,
 appConst.groupExtractorPins: planetCommonUI.PLANET_COLOR_ICON_EXTRACTOR,
 appConst.groupStoragePins: planetCommonUI.PLANET_COLOR_ICON_STORAGE,
 appConst.groupSpaceportPins: planetCommonUI.PLANET_COLOR_ICON_SPACEPORT,
 appConst.groupProcessPins: planetCommonUI.PLANET_COLOR_ICON_PROCESSOR,
 appConst.groupExtractionControlUnitPins: planetCommonUI.PLANET_COLOR_ICON_EXTRACTOR}
PINICONPATHS = {appConst.groupCommandPins: 'res:/UI/Texture/Planet/command.dds',
 appConst.groupExtractorPins: 'res:/UI/Texture/Planet/extractor.dds',
 appConst.groupStoragePins: 'res:/UI/Texture/Planet/storage.dds',
 appConst.groupSpaceportPins: 'res:/UI/Texture/Planet/spaceport.dds',
 appConst.groupProcessPins: 'res:/UI/Texture/Planet/process.dds',
 appConst.groupExtractionControlUnitPins: 'res:/UI/Texture/Planet/extractor.dds'}

def GetPinIconPath(typeID):
    groupID = evetypes.GetGroupID(typeID)
    if groupID == appConst.groupProcessPins:
        if typeID in planetConst.TYPEIDS_PROCESSORS_HIGHTECH:
            return 'res:/UI/Texture/Planet/processHighTech.dds'
        elif typeID in planetConst.TYPEIDS_PROCESSORS_ADVANCED:
            return 'res:/UI/Texture/Planet/processAdvanced.dds'
        else:
            return 'res:/UI/Texture/Planet/process.dds'
    else:
        return PINICONPATHS[groupID]


class SpherePinStack():

    def __init__(self, surfacePoint, maxRadius):
        self.spherePins = []
        self.transformsBySpherePins = {}
        self.surfacePoint = surfacePoint
        self.maxRadius = maxRadius
        self.destroyed = False
        self.hologramModel = None

    def CreateSpherePin(self, textureName, layer, radius, transform, isGauge = False, scale = 1.01, color = Color.WHITE, display = True, offsetScale = 1.0, xOffset = 0.0, yOffset = 0.0, maxRadius = None):
        if isGauge:
            shaderName = 'res:/Graphics/Effect/Managed/Space/UI/SpherePinThreshold.fx'
        else:
            shaderName = 'res:/Graphics/Effect/Managed/Space/UI/SpherePin1.fx'
        sp = trinity.EveSpherePin()
        transform.children.append(sp)
        self.spherePins.append(sp)
        self.transformsBySpherePins[sp] = transform
        sp.pinEffectResPath = shaderName
        sp.pinRadius = radius
        sp.pinMaxRadius = maxRadius or self.maxRadius
        sp.centerNormal = self.surfacePoint.GetAsXYZTuple()
        sp.scaling = (scale, scale, scale)
        sp.display = display
        sp.sortValueMultiplier = 1.0 - 0.01 * layer - 0.1 * scale
        sp.uvAtlasScaleOffset = (offsetScale,
         offsetScale,
         xOffset,
         yOffset)
        sm.GetService('planetUI').LoadSpherePinResources(sp, textureName)
        sp.pinColor = color
        return sp

    def CreateIconSpherePin(self, layer, radius, transform, typeID, scale = 1.01, color = Color.WHITE):
        iconFile = inventorycommon.typeHelpers.GetIcon(typeID).iconFile
        path = Icon.ConvertIconNoToResPath(None, iconFile)
        return self.CreateSpherePin(textureName=path, layer=layer, radius=radius, transform=transform, scale=scale, color=color, offsetScale=1.0, xOffset=0.0, yOffset=0.0)

    def SetLocation(self, surfacePoint):
        self.surfacePoint.Copy(surfacePoint)
        for spherePin in self.spherePins:
            centerNormal = self.surfacePoint.GetAsXYZTuple()
            spherePin.centerNormal = centerNormal

    def Remove(self):
        self.destroyed = True
        for spherePin, transform in self.transformsBySpherePins.iteritems():
            if spherePin in transform.children:
                transform.children.remove(spherePin)
                animations.StopAllAnimations(spherePin)

        self.transformsBySpherePins = {}
        self.HideHologramModel()

    def RemoveSpherePin(self, spherePin):
        if self.destroyed:
            return
        transform = self.transformsBySpherePins.pop(spherePin)
        transform.children.remove(spherePin)

    def ShowHologramModel(self):
        uthread.new(self._ShowHologramModel)

    def _ShowHologramModel(self):
        if not self.hologramModel:
            self.hologramModel = self.ConstructHologramModel()
            self.transform.children.append(self.hologramModel)
        scale = (SCALE_HOLOGRAMMODEL, SCALE_HOLOGRAMMODEL, SCALE_HOLOGRAMMODEL)
        self.hologramModel.scaling = scale
        self.hologramModel.sortValueMultiplier = 0.5
        self.hologramModel.translation = geo2.Vec3Scale(self.surfacePoint.GetAsXYZTuple(), SCALE_HOLOGRAM)
        animations.MorphVector3(self.hologramModel, 'scaling', (SCALE_HOLOGRAMMODEL * 2, 0.0, 0.0), scale, duration=0.3)
        uthread.new(self._Rotate3dModel)

    def ConstructHologramModel(self):
        pass

    def _Rotate3dModel(self):
        t = 0.0
        plnSurfRotMat = geo2.MatrixRotationAxis(geo2.Vec3Cross(geo2.Vec3Normalize(self.surfacePoint.GetAsXYZTuple()), (0.0, 1.0, 0.0)), -math.acos(geo2.Vec3Dot(geo2.Vec3Normalize(self.surfacePoint.GetAsXYZTuple()), (0.0, 1.0, 0.0))))
        while self.hologramModel:
            t += 0.5 / blue.os.fps
            zRotMat = geo2.MatrixRotationAxis((0.0, 1.0, 0.0), -t)
            rotation = geo2.MatrixMultiply(zRotMat, plnSurfRotMat)
            rotQuat = geo2.QuaternionRotationMatrix(rotation)
            self.hologramModel.rotation = rotQuat
            blue.pyos.synchro.Yield()

    def HideHologramModel(self):
        if not self.hologramModel:
            return
        if self.hologramModel in self.transform.children:
            uthread.new(self._HideHologramModel, self.hologramModel)
        self.hologramModel = None

    def _HideHologramModel(self, hologramModel):
        animations.MorphVector3(hologramModel, 'scaling', hologramModel.scaling, (0.5 * SCALE_HOLOGRAMMODEL, 0, 0), duration=0.15, sleep=True)
        self.transform.children.remove(hologramModel)


class BasePlanetPin(SpherePinStack):
    __notifyevents__ = ['ProcessColonyDataSet']
    baseColor = planetCommonUI.PLANET_COLOR_STORAGE

    def __init__(self, surfacePoint, pin, transform, maxRadius = RADIUS_PINEXTENDED):
        SpherePinStack.__init__(self, surfacePoint, maxRadius)
        sm.RegisterNotify(self)
        self.destroyed = False
        self.renderState = utillib.KeyVal(mouseHover=False, asRoute=False, selected=False)
        self.pin = pin
        self.spherePins = []
        self.hologramModel = None
        self.producerCycleTime = 0.0
        self.transform = transform
        self.resourceIcons = []
        self.border = self.CreateSpherePin(textureName='res:/UI/Texture/Planet/pin_base_y.dds', layer=0, radius=RADIUS_PINEXTENDED, transform=transform, scale=SCALE_PINBASE, color=(0.0, 0.0, 0.0, 0.0))
        self.border.display = False
        self.logo = self.CreateSpherePin(textureName=GetPinIconPath(self.pin.typeID), layer=2, radius=RADIUS_LOGO, transform=transform, scale=SCALE_PINBASE, color=self.GetPinColor())
        self.mainPin = self.CreateSpherePin(textureName='res:/UI/Texture/Planet/pin_base.dds', layer=1, radius=RADIUS_PIN, transform=transform, scale=SCALE_PINBASE, color=(0.0, 0.0, 0.0, 0.4))
        self.gaugeUnderlay = self.CreateSpherePin(textureName='res:/UI/Texture/Planet/gauge_15px.dds', layer=3, radius=RADIUS_PIN, transform=transform, scale=SCALE_PINLIFTED, color=self.baseColor)
        self.gauge = self.CreateSpherePin(textureName='res:/UI/Texture/Planet/gauge_15px.dds', layer=4, radius=RADIUS_PIN, transform=transform, scale=SCALE_PINLIFTED, isGauge=True, color=planetCommonUI.PLANET_COLOR_USED_STORAGE)
        self.multiSelected = self.CreateSpherePin(textureName='res:/UI/Texture/Planet/gauge_15px.dds', layer=12, radius=RADIUS_PIN_SELECTED, transform=transform, scale=SCALE_PINLIFTED, isGauge=True, color=eveColor.CRYO_BLUE, display=False)
        self.multiSelected.pinAlphaThreshold = 1.0
        self.cycle = self.CreateSpherePin(textureName='res:/UI/Texture/Planet/cycle_10px.dds', layer=5, radius=RADIUS_CYCLE, transform=transform, scale=SCALE_PINLIFTED, isGauge=True, color=planetCommonUI.PLANET_COLOR_CYCLE)
        self.shadow = self.CreateSpherePin(textureName='res:/UI/Texture/Planet/disc_shadow.dds', layer=0, radius=RADIUS_SHADOW, transform=transform, scale=SCALE_ONGROUND, color=(0.0, 0.0, 0.0, 0.3))
        self.needsAttentionIndicator = None
        self.CheckShowNeedsAttentionIndicator()
        self.SetResourceIcons()
        self.pinExpansions = [(self.mainPin, RADIUS_PIN, RADIUS_PINEXTENDED),
         (self.gauge, RADIUS_PIN, RADIUS_PINEXTENDED),
         (self.gaugeUnderlay, RADIUS_PIN, RADIUS_PINEXTENDED),
         (self.cycle, RADIUS_CYCLE, RADIUS_CYCLEEXTENDED),
         (self.shadow, RADIUS_SHADOW, RADIUS_SHADOWEXTENDED)]
        self.AssignIDsToPins()
        self.UpdateStorageGauge()
        self.UpdateEditModeColors()
        uthread.new(self.UpdateCycleTimer)
        uthread.new(self.UpdateResourceIcons)

    def ShowNeedsAttentionIndicator(self):
        if self.needsAttentionIndicator:
            if self.needsAttentionIndicator.display:
                return
            self.needsAttentionIndicator.color = planetCommonUI.PLANET_COLOR_NEEDSATTENTION
            self.needsAttentionIndicator.pinRadius = RADIUS_PIN
            self.needsAttentionIndicator.display = True
        else:
            self._ConstructNeedsAttentionIndicator()
        animations.FadeTo(self.needsAttentionIndicator, 1.0, 0.5, duration=2.0, curveType=uiconst.ANIM_WAVE, loops=uiconst.ANIM_REPEAT, curveSet='piBlink')
        animations.MorphScalar(self.needsAttentionIndicator, 'pinRadius', self.needsAttentionIndicator.pinRadius, 1.2 * RADIUS_PIN, duration=2.0, loops=uiconst.ANIM_REPEAT, curveType=uiconst.ANIM_WAVE)

    def _ConstructNeedsAttentionIndicator(self):
        self.needsAttentionIndicator = self.CreateSpherePin(textureName='res:/UI/Texture/Planet/gauge_20px.dds', layer=20, radius=RADIUS_PIN, transform=self.transform, scale=1.0106, color=planetCommonUI.PLANET_COLOR_NEEDSATTENTION)
        self.needsAttentionIndicator.name = ''

    def HideNeedsAttentionIndicator(self):
        if self.needsAttentionIndicator:
            uthread.new(self._HideNeedsAttentionIndicator)

    def _HideNeedsAttentionIndicator(self):
        self.needsAttentionIndicator.color = planetConst.LINK_COLOR_ROUTED
        duration = 1.0
        animations.FadeTo(self.needsAttentionIndicator, 1.0, 0.0, duration=duration)
        animations.MorphScalar(self.needsAttentionIndicator, 'pinRadius', self.needsAttentionIndicator.pinRadius, 4 * RADIUS_PIN, duration=duration, sleep=True)
        self.needsAttentionIndicator.display = False

    def GetPinColor(self):
        groupID = evetypes.GetGroupID(self.pin.typeID)
        return PINCOLORS[groupID]

    def SetResourceIcons(self):
        pass

    def UpdateResourceIcons(self):
        t = 0.0
        cycleTimeBase = 4.0
        while not getattr(self, 'destroyed', False):
            numIcons = len(self.resourceIcons)
            if numIcons > 1:
                cycleTime = cycleTimeBase * numIcons
                t += 1.0 / blue.os.fps
                t = t % cycleTime
                for i, icon in enumerate(self.resourceIcons):
                    icon.display = t > i * cycleTimeBase and t < (i + 1) * cycleTimeBase
                    x = t - i * cycleTimeBase
                    alpha = math.sin(math.pi * (2 * x / cycleTimeBase - 0.5)) / 2 + 0.5
                    icon.pinColor = (1.0,
                     1.0,
                     1.0,
                     alpha * 0.8)

            blue.pyos.synchro.Yield()

    def AssignIDsToPins(self):
        for pin in self.spherePins:
            if isinstance(self.pin.id, tuple):
                pinType = planetCommonUI.PINTYPE_NORMALEDIT
                pin.name = '%s,%s,%s' % (pinType, self.pin.id[0], self.pin.id[1])
            else:
                pinType = planetCommonUI.PINTYPE_NORMAL
                pin.name = '%s,%s' % (pinType, self.pin.id)

        self.border.name = self.shadow.name = ''
        if self.needsAttentionIndicator:
            self.needsAttentionIndicator.name = ''

    def UpdateEditModeColors(self):
        if self and self.pin:
            if self.pin.IsInEditMode():
                self.mainPin.pinColor = planetCommonUI.PLANET_COLOR_PINEDITMODE
            else:
                self.mainPin.pinColor = (0.0, 0.0, 0.0, 0.4)

    def UpdateStorageGauge(self):
        if self.pin.IsStorage():
            usage = self.pin.capacityUsed / self.pin.GetCapacity()
        else:
            usage = 0.0
        if usage > 0:
            self.gauge.display = True
        else:
            self.gauge.display = False
        self.gauge.pinAlphaThreshold = usage

    def UpdateCycleTimer(self):
        while not getattr(self, 'destroyed', False):
            if self.pin.GetCycleTime() and self.pin.GetNextRunTime() and self.pin.IsActive() and not self.pin.IsInEditMode():
                self.cycle.display = True
                self.cycle.pinColor = Color.WHITE
                currCycle = self.pin.GetCycleTime() - (self.pin.GetNextRunTime() - blue.os.GetWallclockTime())
                cycleProportion = currCycle / float(self.pin.GetCycleTime())
                self.cycle.pinAlphaThreshold = cycleProportion
            elif self.pin.IsProducer() and getattr(self.pin, 'schematicID', False):
                cycleLength = 3.0
                elapsed = 1.0 / blue.os.fps
                self.producerCycleTime += elapsed
                if self.producerCycleTime > cycleLength:
                    self.producerCycleTime -= cycleLength
                self.cycle.display = True
                self.cycle.pinAlphaThreshold = 1.0
                alpha = math.sin(math.pi * self.producerCycleTime / cycleLength)
                self.cycle.pinColor = (1.0,
                 1.0,
                 1.0,
                 alpha)
            else:
                self.cycle.display = False
            blue.pyos.synchro.Yield()

    def RenderAccordingToState(self):
        renderState = self.renderState
        if renderState.mouseHover:
            self.border.display = True
            self.border.pinColor = (1.0, 1.0, 1.0, 0.15)
        elif renderState.asRoute:
            self.border.display = True
            self.border.pinColor = (255.0 / 256,
             125.0 / 256,
             0.0 / 256,
             0.15)
        elif renderState.selected:
            pass
        else:
            self.border.display = False
        self.CheckShowNeedsAttentionIndicator()

    def CheckShowNeedsAttentionIndicator(self):
        colony = sm.GetService('planetUI').planet.GetColony(session.charid)
        if colony and colony.colonyData.IsPinNeedingAttention(self.pin.id):
            self.ShowNeedsAttentionIndicator()
        else:
            self.HideNeedsAttentionIndicator()

    def ResetPinData(self, newPin):
        self.pin = newPin
        self.UpdateEditModeColors()

    def GetMenu(self):
        ret = []
        if session.role & ROLE_GML == ROLE_GML:
            ret.append(('GM / WM Extras', self.GetGMMenu()))
        planetUISvc = sm.GetService('planetUI')
        eventManager = planetUISvc.eventManager
        ret.extend([(MenuLabel('UI/PI/Common/CreateLink'), eventManager.BeginCreateLink, [self.pin.id]), (MenuLabel('UI/Commands/ShowInfo'), sm.GetService('info').ShowInfo, [self.pin.typeID, self.pin.id])])
        if len(eventManager.selectedPinIDs) > 1:
            ret += planetUISvc.myPinManager.GetMultiPinMenu(self)
        return ret

    def GetGMMenu(self):
        ret = []
        ret.append(('PinID: %s' % (self.pin.id,), blue.pyos.SetClipboardData, [str(self.pin.id)]))
        return ret

    def OnRefreshPins(self):
        self.UpdateStorageGauge()
        self.SetResourceIcons()
        self.UpdateEditModeColors()
        self.RenderAccordingToState()

    def SetAsRoute(self):
        self.renderState.asRoute = True
        self.RenderAccordingToState()

    def ResetAsRoute(self):
        self.renderState.asRoute = False
        self.RenderAccordingToState()

    def PlacementAnimation(self):
        for pin, radius, expandedRadius in self.pinExpansions:
            pin.pinRadius = RADIUS_LOGO
            animations.MorphScalar(pin, 'pinRadius', endVal=radius, duration=0.25)

    def ConstructHologramModel(self):
        graphic = inventorycommon.typeHelpers.GetGraphic(self.pin.typeID)
        if graphic and graphic.graphicFile:
            graphicFile = str(graphic.graphicFile)
            graphicFile = graphicFile.replace(':/model', ':/dx9/model').replace('.blue', '.red')
            return trinity.Load(graphicFile)
        if not self.hologramModel or self.hologramModel.__bluetype__ != 'trinity.EveTransform':
            return trinity.Load('res:/dx9/model/structure/planetary/terrestrial/command/commt_t1/commt_t1.red')

    def SetSelected(self):
        for pin, radius, expandedRadius in self.pinExpansions:
            animations.MorphScalar(pin, 'pinRadius', endVal=expandedRadius, duration=0.25)

        self.ShowHologramModel()
        self.renderState.selected = True
        self.RenderAccordingToState()

    def SetDeselected(self):
        for pin, radius, expandedRadius in self.pinExpansions:
            animations.MorphScalar(pin, 'pinRadius', endVal=radius, duration=0.25)

        if self.hologramModel:
            self.HideHologramModel()
        self.renderState.selected = False
        self.RenderAccordingToState()

    def SetMultiSelectedDisplay(self, doDisplay):
        self.multiSelected.display = doDisplay

    def OnMouseEnter(self):
        self.renderState.mouseHover = True
        self.RenderAccordingToState()
        sm.GetService('audio').SendUIEvent('msg_pi_pininteraction_mouseover_play')

    def OnMouseExit(self):
        self.renderState.mouseHover = False
        self.RenderAccordingToState()

    def ProcessColonyDataSet(self, planetID):
        if sm.GetService('planetUI').planetID != planetID:
            return
        self.pin = sm.GetService('planetSvc').GetPlanet(planetID).GetPin(self.pin.id)


class CommandCenterPin(BasePlanetPin):
    BasePlanetPin.__notifyevents__.append('OnEditModeBuiltOrDestroyed')

    def __init__(self, surfacePoint, pin, transform):
        BasePlanetPin.__init__(self, surfacePoint, pin, transform)
        gaugeRadius = 0.005
        gaugeRadiusExtended = 0.0082
        powerGauge = self.powerGauge = self.CreateSpherePin(textureName='res:/UI/Texture/Planet/hash15px.dds', layer=11, radius=gaugeRadius, transform=transform, scale=SCALE_PINLIFTED, isGauge=True, color=planetCommonUI.PLANET_COLOR_POWER)
        powerGaugeUnderlay = self.CreateSpherePin(textureName='res:/UI/Texture/Planet/hash15px.dds', layer=10, radius=gaugeRadius, transform=transform, scale=SCALE_PINLIFTED, isGauge=True, color=(0.35, 0, 0))
        powerGauge.name = powerGaugeUnderlay.name = '%s,%s' % (planetCommonUI.PINTYPE_NORMAL, self.pin.id)
        self.pinExpansions.append((powerGauge, gaugeRadius, gaugeRadiusExtended))
        self.pinExpansions.append((powerGaugeUnderlay, gaugeRadius, gaugeRadiusExtended))
        cpuGauge = self.cpuGauge = self.CreateSpherePin(textureName='res:/UI/Texture/Planet/hash15px.dds', layer=11, radius=gaugeRadius, transform=transform, scale=SCALE_PINLIFTED, isGauge=True, color=planetCommonUI.PLANET_COLOR_CPU)
        cpuGaugeUnderlay = self.CreateSpherePin(textureName='res:/UI/Texture/Planet/hash15px.dds', layer=10, radius=gaugeRadius, transform=transform, scale=SCALE_PINLIFTED, isGauge=True, color=(0.0, 0.329, 0.267, 1.0))
        cpuGauge.name = cpuGaugeUnderlay.name = '%s,%s' % (planetCommonUI.PINTYPE_NORMAL, self.pin.id)
        cpuGauge.pinRotation = cpuGaugeUnderlay.pinRotation = math.pi
        self.pinExpansions.append((cpuGauge, gaugeRadius, gaugeRadiusExtended))
        self.pinExpansions.append((cpuGaugeUnderlay, gaugeRadius, gaugeRadiusExtended))
        powerGaugeUnderlay.pinAlphaThreshold = 0.5
        cpuGaugeUnderlay.pinAlphaThreshold = 0.5
        self.AssignIDsToPins()
        self.UpdatePowerCPUGauge()

    def OnRefreshPins(self):
        BasePlanetPin.OnRefreshPins(self)
        self.UpdatePowerCPUGauge()

    def OnEditModeBuiltOrDestroyed(self, planetID):
        if sm.GetService('planetUI').planetID != planetID:
            return
        self.UpdatePowerCPUGauge()

    def UpdatePowerCPUGauge(self):
        colony = sm.GetService('planetUI').GetCurrentPlanet().GetColony(self.pin.ownerID)
        if colony is None or colony.colonyData is None:
            raise RuntimeError('Colony is gone but Command Pin window still open')
        if colony.colonyData.GetColonyPowerSupply() > 0:
            self.powerGauge.pinAlphaThreshold = min(1.0, float(colony.colonyData.GetColonyPowerUsage()) / colony.colonyData.GetColonyPowerSupply()) / 2.0
        else:
            self.powerGauge.pinAlphaThreshold = 0.0
        if colony.colonyData.GetColonyCpuSupply() > 0:
            self.cpuGauge.pinAlphaThreshold = min(1.0, float(colony.colonyData.GetColonyCpuUsage()) / float(colony.colonyData.GetColonyCpuSupply())) / 2.0
        else:
            self.cpuGauge.pinAlphaThreshold = 0.0

    def GetGMMenu(self):
        menu = []
        menu.extend(BasePlanetPin.GetGMMenu(self))
        if session.role & ROLE_GML == ROLE_GML and not sm.GetService('planetUI').GetCurrentPlanet().IsInEditMode():
            menu.append(('Convert Command Center', self.ConvertCommandCenter))
        return menu

    def ConvertCommandCenter(self):
        sm.GetService('planetUI').planet.GMConvertCommandCenter(self.pin.id)


class ProcessorPin(BasePlanetPin):

    def __init__(self, surfacePoint, pin, transform):
        self.hopperGauges = []
        self.hopperGaugeUnderlays = []
        BasePlanetPin.__init__(self, surfacePoint, pin, transform)
        self.gauge.display = self.gaugeUnderlay.display = False
        for i in xrange(3):
            gauge = self.CreateSpherePin(textureName='res:/UI/Texture/Planet/gauge_15px.dds', layer=11, radius=RADIUS_PIN, transform=transform, scale=SCALE_PINLIFTED, isGauge=True, color=planetCommonUI.PLANET_COLOR_USED_PROCESSOR)
            gaugeUnderlay = self.CreateSpherePin(textureName='res:/UI/Texture/Planet/gauge_15px.dds', layer=10, radius=RADIUS_PIN, transform=transform, scale=SCALE_PINLIFTED, isGauge=True, color=self.GetPinColor())
            gauge.display = gaugeUnderlay.display = False
            self.hopperGauges.append(gauge)
            self.hopperGaugeUnderlays.append(gaugeUnderlay)
            self.pinExpansions.append((gauge, RADIUS_PIN, RADIUS_PINEXTENDED))
            self.pinExpansions.append((gaugeUnderlay, RADIUS_PIN, RADIUS_PINEXTENDED))

        self.AssignIDsToPins()
        self.UpdateStorageGauge()

    def GetPinColor(self):
        typeID = self.pin.typeID
        if typeID in planetConst.TYPEIDS_PROCESSORS_HIGHTECH:
            return planetCommonUI.PLANET_COLOR_ICON_PROCESSOR_HIGHTECH
        elif typeID in planetConst.TYPEIDS_PROCESSORS_ADVANCED:
            return planetCommonUI.PLANET_COLOR_ICON_PROCESSOR_ADVANCED
        else:
            return planetCommonUI.PLANET_COLOR_ICON_PROCESSOR

    def UpdateStorageGauge(self):
        if not self.hopperGauges:
            return
        proportions = []
        ingredients = []
        gapConst = 0.04
        for typeID, item in get_schematic_types(self.pin.schematicID, {}).iteritems():
            if item.isInput:
                ingredients.append(utillib.KeyVal(typeID=typeID, quantity=item.quantity))

        numIngredients = len(ingredients)
        for i in xrange(3):
            if i > numIngredients - 1:
                self.hopperGauges[i].display = False
                self.hopperGaugeUnderlays[i].display = False
                continue
            hopperFill = self.pin.contents.get(ingredients[i].typeID, 0) / float(ingredients[i].quantity)
            if hopperFill > 1.0:
                hopperFill = 1.0
            if hopperFill > 0.0:
                self.hopperGauges[i].display = True
            self.hopperGaugeUnderlays[i].display = True
            if numIngredients > 1:
                gaugeThreshold = hopperFill / numIngredients * (1.0 - gapConst * numIngredients)
                underlayThreshold = 1.0 / numIngredients * (1.0 - gapConst * numIngredients)
            else:
                gaugeThreshold = hopperFill
                underlayThreshold = 1.0
            rotation = 2 * math.pi * (float(i) / numIngredients + gapConst / 2.0)
            self.hopperGauges[i].pinAlphaThreshold = gaugeThreshold
            self.hopperGaugeUnderlays[i].pinAlphaThreshold = underlayThreshold
            self.hopperGauges[i].pinRotation = rotation
            self.hopperGaugeUnderlays[i].pinRotation = rotation


class ExtractorPin(BasePlanetPin):
    baseColor = planetCommonUI.PLANET_COLOR_EXTRACTOR

    def __init__(self, surfacePoint, pin, transform):
        BasePlanetPin.__init__(self, surfacePoint, pin, transform)

    def GetMenu(self):
        menu = []
        menu.extend(BasePlanetPin.GetMenu(self))
        return menu

    def GetGMMenu(self):
        menu = []
        menu.extend(BasePlanetPin.GetGMMenu(self))
        return menu


class EcuPin(BasePlanetPin):
    baseColor = planetCommonUI.PLANET_COLOR_EXTRACTOR

    def __init__(self, surfacePoint, pin, transform):
        BasePlanetPin.__init__(self, surfacePoint, pin, transform)
        self.rings = []
        self.extractionHeadsByNum = {}
        self.linksByHeadID = {}
        numRings = 6
        self.transform = transform
        self.isSurveying = False
        self.distanceFactor = 0.0
        for i in xrange(numRings):
            ring = self.CreateSpherePin(textureName='res:/UI/Texture/Planet/gauge_15px.dds', layer=0, radius=0.0, transform=transform, color=Color(*planetCommonUI.PLANET_COLOR_EXTRACTOR).SetAlpha(0.3).GetRGBA())
            self.rings.append(ring)

        self.CreateSpherePin(textureName='res:/UI/Texture/Planet/pin_base.dds', layer=0, radius=RADIUS_PIN * 0.25, scale=SCALE_ONGROUND * 1.0005, transform=transform, color=planetCommonUI.PLANET_COLOR_EXTRACTOR)
        areaOfInfluence = pin.GetAreaOfInfluence()
        self.maxDistanceCircle = self.CreateSpherePin(textureName='res:/UI/Texture/Planet/survey_ghost_512.dds', layer=0, radius=areaOfInfluence, scale=SCALE_ONGROUND * 1.0005, transform=transform, display=False)
        self.maxDistanceCircle.pinMaxRadius = areaOfInfluence
        self.RenderExtractionHeads()
        uthread.new(self.Animate)

    def EnterSurveyMode(self):
        self.isSurveying = True
        self.SetExtractionHeadRadius(self.pin.headRadius)
        self.UpdateMaxDistanceCircle()

    def ExitSurveyMode(self):
        self.isSurveying = False
        self.UpdateMaxDistanceCircle()
        self.ResetOverlapValues()

    def ShowMaxDistanceCircle(self):
        self.isSurveying = True
        self.UpdateMaxDistanceCircle()

    def HideMaxDistanceCircle(self):
        self.isSurveying = False
        self.UpdateMaxDistanceCircle()

    def SetDistanceFactor(self, distanceFactor):
        self.distanceFactor = distanceFactor
        self.UpdateMaxDistanceCircle()

    def UpdateMaxDistanceCircle(self):
        self.maxDistanceCircle.display = self.isSurveying or self.renderState.selected
        if self.maxDistanceCircle.display:
            self._UpdateDistanceCircleOpacity()

    def _UpdateDistanceCircleOpacity(self):
        STARTSHOWVALUE = 0.7
        MINALPHA = 0.15
        MAXALPHA = 0.25
        color = planetCommonUI.GetContrastColorForCurrPlanet()
        x = MINALPHA
        if self.distanceFactor > STARTSHOWVALUE:
            x += (MAXALPHA - MINALPHA) * (self.distanceFactor - STARTSHOWVALUE) / (1.0 - STARTSHOWVALUE)
        self.maxDistanceCircle.pinColor = Color(*color).SetAlpha(x).GetRGBA()

    def GetExtractionHead(self, headID):
        return self.extractionHeadsByNum.get(headID, None)

    def OnHeadsUnlocked(self):
        for head in self.extractionHeadsByNum.values():
            head.ShowUnlocked()

    def OnHeadsLocked(self):
        for head in self.extractionHeadsByNum.values():
            head.ShowLocked()

    def RenderExtractionHeads(self):
        self.RemoveAllHeads()
        for headID, phi, theta in self.pin.heads:
            surfacePoint = SurfacePoint(theta=theta, phi=phi)
            self.AddHead(headID, surfacePoint)

    def AddHead(self, headID, surfacePoint):
        extractionHead = ExtractionHeadPin(surfacePoint, self.transform, self.pin, headID, self.pin.headRadius or planetCommon.RADIUS_DRILLAREAMIN)
        self.extractionHeadsByNum[headID] = extractionHead
        link = LinkBase('linksExtraction', surfacePoint, self.surfacePoint, color=planetCommonUI.PLANET_COLOR_EXTRACTIONLINK)
        self.linksByHeadID[headID] = link

    def RemoveAllHeads(self):
        for headID in self.extractionHeadsByNum.keys():
            self.RemoveHead(headID)

    def RemoveHead(self, headID):
        head = self.extractionHeadsByNum.get(headID, None)
        if head:
            head.Remove()
            self.extractionHeadsByNum.pop(headID)
        link = self.linksByHeadID.get(headID, None)
        if link:
            link.Remove()
            self.linksByHeadID.pop(headID)

    def MoveExtractionHeadTo(self, headID, surfacePoint):
        head = self.extractionHeadsByNum.get(headID, None)
        if head:
            head.SetLocation(surfacePoint)
        link = self.linksByHeadID.get(headID, None)
        if link:
            link.Remove()
            link = LinkBase('linksExtraction', surfacePoint, self.surfacePoint, color=planetCommonUI.PLANET_COLOR_EXTRACTIONLINK)
        self.HideHologramModel()
        for head in self.extractionHeadsByNum.values():
            head.HideHologramModel()

    def ResetPinData(self, newPin):
        oldHeads = [ head for head in self.pin.heads ]
        newHeads = [ head for head in newPin.heads ]
        toRemove = [ head for head in oldHeads if head not in newHeads ]
        for headID, phi, theta in toRemove:
            self.RemoveHead(headID)

        toAdd = [ head for head in newHeads if head not in oldHeads ]
        for headID, phi, theta in toAdd:
            surfacePoint = SurfacePoint(theta=theta, phi=phi)
            self.AddHead(headID, surfacePoint)

        for headUI in self.extractionHeadsByNum.values():
            headUI.pin = self.pin

        BasePlanetPin.ResetPinData(self, newPin)

    def ResetOverlapValues(self):
        for headUI in self.extractionHeadsByNum.values():
            headUI.SetOverlapValue(0)

    def SetOverlapValues(self, overlapVals):
        for headID, overlapVal in overlapVals.iteritems():
            head = self.extractionHeadsByNum.get(headID, None)
            if head:
                head.SetOverlapValue(overlapVal)

    def SetExtractionHeadRadius(self, radius, time = 1000.0):
        uthread.new(self._SetExtractionHeadRadius, radius, time)

    def _SetExtractionHeadRadius(self, radius, time):
        for head in self.extractionHeadsByNum.values():
            head.SetExtractionHeadRadius(radius, time)
            blue.pyos.synchro.SleepWallclock(100)

    def Remove(self):
        self.RemoveAllHeads()
        BasePlanetPin.Remove(self)

    def Animate(self):
        cycleTime = 10.0
        numRings = len(self.rings)
        scaleDiff = SCALE_PINLIFTED - 1.0
        elapsed = 0.0
        color = list(planetCommonUI.PLANET_COLOR_EXTRACTOR)
        while not getattr(self, 'destroyed', False):
            elapsed += 1.0 / blue.os.fps
            t = elapsed % cycleTime
            for i, ring in enumerate(self.rings):
                x = (float(i + 1) / numRings + t / cycleTime) % 1
                scale = x * scaleDiff + 1.0
                ring.scaling = (scale, scale, scale)
                ring.pinRadius = (x * 0.7 + 0.3) * self.mainPin.pinRadius
                color[3] = x
                ring.pinColor = color

            blue.pyos.synchro.Yield()

    def SetSelected(self):
        BasePlanetPin.SetSelected(self)
        self.UpdateMaxDistanceCircle()
        for head in self.extractionHeadsByNum.values():
            head.ShowHologramModel()

    def SetDeselected(self):
        BasePlanetPin.SetDeselected(self)
        self.UpdateMaxDistanceCircle()
        for head in self.extractionHeadsByNum.values():
            head.HideHologramModel()

    def GetMenu(self):
        menu = []
        menu.extend(BasePlanetPin.GetMenu(self))
        return menu

    def GetGMMenu(self):
        menu = []
        menu.extend(BasePlanetPin.GetGMMenu(self))
        if session.role & ROLE_GML == ROLE_GML and not sm.GetService('planetUI').GetCurrentPlanet().IsInEditMode():
            menu.append(('Deposit Designer', self.HotProgramInjection))
        return menu

    def HotProgramInjection(self):
        sm.GetService('planetUI').planet.GMInstallProgram(self.pin.id)


class LaunchpadPin(BasePlanetPin):
    pass


class StorageFacilityPin(BasePlanetPin):

    def __init__(self, surfacePoint, pin, transform):
        BasePlanetPin.__init__(self, surfacePoint, pin, transform)


class BuildIndicatorPin(SpherePinStack):

    def __init__(self, surfacePoint, typeID, groupID, transform):
        areaOfInfluence = sm.GetService('godma').GetTypeAttribute2(typeID, appConst.attributeEcuAreaOfInfluence)
        SpherePinStack.__init__(self, surfacePoint, areaOfInfluence)
        self.surfacePin = self.CreateSpherePin(textureName=GetPinIconPath(typeID), layer=10, radius=RADIUS_LOGO, transform=transform, scale=SCALE_PINBASE, color=(1.0, 1.0, 1.0, 0.4))
        self.cannotBuild = self.CreateSpherePin(textureName='res:/UI/Texture/Planet/pin_base.dds', layer=11, radius=RADIUS_PIN, transform=transform, scale=SCALE_PINBASE, color=(0.3, 0.0, 0.0, 0.5))
        self.cannotBuild.display = False
        self.shadow = self.CreateSpherePin(textureName='res:/UI/Texture/Planet/disc_shadow.dds', layer=12, radius=RADIUS_SHADOW, transform=transform, scale=SCALE_ONGROUND, color=(0.0, 0.0, 0.0, 0.3))
        if groupID == appConst.groupExtractionControlUnitPins:
            color = planetCommonUI.GetContrastColorForCurrPlanet()
            color = Color(*color).SetAlpha(0.2).GetRGBA()
            self.maxDistanceCircle = self.CreateSpherePin(textureName='res:/UI/Texture/Planet/survey_ghost_512.dds', layer=0, radius=areaOfInfluence, scale=SCALE_ONGROUND * 1.0005, transform=transform, color=color)
        sm.GetService('planetUI').planetNav.SetFocus()

    def SetCanBuildIndication(self, canBuild):
        self.cannotBuild.display = not canBuild


class TemplatePins(SpherePinStack):

    def __init__(self, surfacePoint, typeID, groupID, transform):
        areaOfInfluence = sm.GetService('godma').GetTypeAttribute2(typeID, appConst.attributeEcuAreaOfInfluence)
        SpherePinStack.__init__(self, surfacePoint, areaOfInfluence)
        self.typeCircle = self.CreateSpherePin(textureName='res:/UI/Texture/Planet/gauge_15px.dds', layer=10, radius=RADIUS_PIN, transform=transform, scale=SCALE_PINBASE, color=(1.0, 1.0, 1.0, 1.0))
        self.surfacePin = self.CreateSpherePin(textureName=GetPinIconPath(typeID), layer=11, radius=RADIUS_LOGO, transform=transform, scale=SCALE_PINBASE, color=(1.0, 1.0, 1.0, 0.4))
        self.shadow = self.CreateSpherePin(textureName='res:/UI/Texture/Planet/disc_shadow.dds', layer=12, radius=RADIUS_SHADOW, transform=transform, scale=SCALE_ONGROUND, color=(0.0, 0.0, 0.0, 0.3))
        if groupID == appConst.groupExtractionControlUnitPins:
            color = planetCommonUI.GetContrastColorForCurrPlanet()
            color = Color(*color).SetAlpha(0.2).GetRGBA()
            self.maxDistanceCircle = self.CreateSpherePin(textureName='res:/UI/Texture/Planet/survey_ghost_512.dds', layer=0, radius=areaOfInfluence, scale=SCALE_ONGROUND * 1.0005, transform=transform, color=color)
        sm.GetService('planetUI').planetNav.SetFocus()
        self.AssignIDsToPins()

    def SetCircleColor(self, color):
        self.typeCircle.pinColor = color

    def AssignIDsToPins(self):
        counter = 0
        for pin in self.spherePins:
            pinType = planetCommonUI.PINTYPE_NORMAL
            pin.name = '%s,%s,_temp' % (pinType, counter)
            counter += 1


class OtherPlayersPin(SpherePinStack):
    HOVERCOLOR = (1.0, 1.0, 1.0, 0.9)
    DEFAULTCOLOR = (0.0, 1.0, 1.0, 0.3)

    def __init__(self, surfacePoint, pinID, typeID, ownerID, transform, isActive = False):
        SpherePinStack.__init__(self, surfacePoint, RADIUS_PINOTHERS)
        self.pinID = pinID
        self.typeID = typeID
        self.ownerID = ownerID
        groupID = evetypes.GetGroupID(typeID)
        pinIconPath = PINICONPATHS[groupID]
        col = PINCOLORS[groupID]
        self.ACTIVECOLOR = (col[0],
         col[1],
         col[2],
         0.6)
        self.spherePins = []
        if isActive:
            self.currColor = self.ACTIVECOLOR
        else:
            self.currColor = self.DEFAULTCOLOR
        self.surfacePin = self.CreateSpherePin(textureName=pinIconPath, layer=0, radius=RADIUS_PINOTHERS, transform=transform, scale=SCALE_PINOTHERS, color=self.currColor)
        self.surfacePin.name = '%s,%s' % (planetCommonUI.PINTYPE_OTHERS, pinID)

    def OnMouseEnter(self):
        self.surfacePin.pinColor = self.HOVERCOLOR
        sm.GetService('audio').SendUIEvent('msg_pi_pininteraction_mouseover_play')

    def OnMouseExit(self):
        self.surfacePin.pinColor = self.currColor

    def RenderAsActive(self):
        self.surfacePin.pinColor = self.currColor = self.ACTIVECOLOR

    def RenderAsDefault(self):
        self.surfacePin.pinColor = self.currColor = self.DEFAULTCOLOR

    def GetGMMenu(self):
        return None

    def GetMenu(self):
        charTypeID = cfg.eveowners.Get(self.ownerID).typeID
        charName = localization.GetByLabel('UI/PI/Common/OwnerName', ownerName=cfg.eveowners.Get(self.ownerID).name)
        charMenu = GetMenuService().GetMenuFromItemIDTypeID(self.ownerID, charTypeID)
        ret = [(MenuLabel('UI/Commands/ShowInfo'), sm.GetService('info').ShowInfo, [self.typeID, self.pinID]), None, (charName, charMenu)]
        return ret


class ExtractionHeadPin(SpherePinStack):
    NUMWAVES = 2

    def __init__(self, surfacePoint, transform, ecuPin, headID, radius):
        SpherePinStack.__init__(self, surfacePoint, planetCommon.RADIUS_DRILLAREAMAX)
        self.pin = ecuPin
        self.headID = headID
        self.disturbanceVal = 0.0
        self.headRadius = radius
        self.hologramModel = None
        self.transform = transform
        self.surfacePin = self.CreateSpherePin(textureName='res:/UI/Texture/Planet/drill_pin.png', layer=headID * 10 + 2, radius=RADIUS_PIN * 0.4, maxRadius=RADIUS_PIN * 0.4, transform=transform, scale=SCALE_ONGROUND * 1.001, color=planetCommonUI.PLANET_COLOR_EXTRACTOR)
        self.selectionArea = self.CreateSpherePin(textureName='res:/UI/Texture/Planet/arrows_256.dds', layer=headID * 10 + 1, radius=RADIUS_PIN * 1.6, maxRadius=RADIUS_PIN * 1.6, transform=transform, scale=SCALE_ONGROUND * 1.001, color=Color(*planetCommonUI.PLANET_COLOR_EXTRACTOR).SetAlpha(0.7).SetSaturation(0.9).GetRGBA())
        self.selectionArea.display = False
        self.pinColor = Color(*planetCommonUI.PLANET_COLOR_EXTRACTOR).SetSaturation(0.4).GetRGBA()
        self.drillArea = self.CreateSpherePin(textureName='res:/UI/Texture/Planet/drill_area.png', layer=headID * 10, radius=RADIUS_PIN * 0.4, transform=transform, scale=SCALE_ONGROUND, color=self.pinColor)
        self.shadow = self.CreateSpherePin(textureName='res:/UI/Texture/Planet/disc_shadow.dds', layer=0, radius=RADIUS_PIN * 0.4, transform=transform, scale=SCALE_ONGROUND, color=(0.0, 0.0, 0.0, 0.25))
        self.SetExtractionHeadRadius(radius)
        self.waves = []
        for i in xrange(self.NUMWAVES):
            wave = self.CreateSpherePin(textureName='res:/UI/Texture/Planet/donut_512.dds', layer=0, radius=0.0, transform=transform, scale=SCALE_ONGROUND, color=self.pinColor)
            wave.name = ''
            self.waves.append(wave)

        self.noisePin = self.CreateSpherePin(textureName='res:/UI/Texture/Planet/white_noise_256.dds', layer=0, radius=RADIUS_PIN * 1.5, transform=transform, scale=SCALE_ONGROUND, color=Color.WHITE, display=False)
        self.pickArea = self.CreateSpherePin(textureName='res:/UI/Texture/Planet/pin_base.dds', layer=headID * 10 + 2, radius=RADIUS_PIN * 1.9, maxRadius=RADIUS_PIN * 1.9, transform=transform, scale=SCALE_ONGROUND * 1.001, color=(0.0, 0.0, 0.0, 0.01))
        name = '%s,%s,%s' % (planetCommonUI.PINTYPE_EXTRACTIONHEAD, self.pin.id, headID)
        self.selectionArea.name = self.surfacePin.name = self.pickArea.name = name
        uthread.new(self.AnimateDrillArea)
        uthread.new(self.AnimateWaves)
        uthread.new(self.AnimateNoise)

    def ConstructHologramModel(self):
        if sm.GetService('planetUI').planet.planetTypeID == appConst.typePlanetGas:
            id = 20612
        else:
            id = 10097
        return trinity.Load(GetGraphicFile(id))

    def SetExtractionHeadRadius(self, radius, time = 250.0):
        if radius is None:
            return
        self.headRadius = radius
        animations.MorphScalar(self.drillArea, 'pinRadius', self.drillArea.pinRadius, radius, duration=time / 1000)
        animations.MorphScalar(self.shadow, 'pinRadius', self.shadow.pinRadius, radius * 1.1, duration=time / 1000)

    def SetOverlapValue(self, disturbanceVal):
        self.disturbanceVal = min(1.0, max(0.0, disturbanceVal))

    def OnMouseEnter(self):
        self.ShowSelectionArea()
        sm.GetService('audio').SendUIEvent('msg_pi_pininteraction_mouseover_play')

    def OnMouseExit(self):
        self.HideSelectionArea()

    def ShowUnlocked(self):
        self.surfacePin.color = Color(*planetCommonUI.PLANET_COLOR_EXTRACTOR).SetAlpha(2.5).GetRGBA()

    def ShowLocked(self):
        self.surfacePin.color = planetCommonUI.PLANET_COLOR_EXTRACTOR

    def ShowSelectionArea(self):
        self.selectionArea.display = True

    def HideSelectionArea(self):
        self.selectionArea.display = False

    def AnimateDrillArea(self):
        cycleLength = 3.0
        elapsed = 0.0
        while not getattr(self, 'destroyed', False):
            elapsed += 1.0 / blue.os.fps
            x = (math.sin(math.pi * elapsed / cycleLength) + 1.0) / 2.0
            brightness = x * 0.2 + 0.7
            alpha = x * 0.15 + 0.2
            self.drillArea.pinColor = Color(*self.pinColor).SetBrightness(brightness).SetAlpha(alpha).GetRGBA()
            blue.pyos.synchro.Yield()

    def AnimateWaves(self):
        elapsed = 0.0
        cycleLength = self.NUMWAVES * 6.0
        phaseDiff = cycleLength / self.NUMWAVES
        while not getattr(self, 'destroyed', False):
            if self.pin.IsActive():
                elapsed += 1.0 / blue.os.fps
                x = elapsed % cycleLength
                for i, wave in enumerate(self.waves):
                    x = (elapsed + i * phaseDiff) % cycleLength / cycleLength
                    wave.pinColor = Color(*planetCommonUI.PLANET_COLOR_EXTRACTOR).SetHSB(0.5, 0.4, 0.7 + 0.3 * x ** 0.3, 0.5 * x).GetRGBA()
                    wave.pinRadius = (1.0 - x) * self.drillArea.pinRadius

            else:
                for wave in self.waves:
                    wave.pinRadius = 0.0

            blue.pyos.synchro.Yield()

    def AnimateNoise(self):
        while not getattr(self, 'destroyed', False):
            if self.disturbanceVal > 0.0:
                self.noisePin.display = True
                self.noisePin.pinRotation = random.random() * math.pi * 2
                scale = self.drillArea.pinRadius / planetCommon.RADIUS_DRILLAREAMAX
                xVal = random.random() * 0.05 * scale
                yVal = random.random() * 0.05 * scale
                self.noisePin.uvAtlasScaleOffset = (scale,
                 scale,
                 xVal,
                 xVal)
                self.noisePin.pinRadius = self.drillArea.pinRadius * 0.95
                self.noisePin.pinColor = (1.0,
                 1.0,
                 1.0,
                 self.disturbanceVal * 1.0)
            else:
                self.noisePin.display = False
            blue.pyos.synchro.SleepWallclock(10)


class DepletionPin(SpherePinStack):

    def __init__(self, surfacePoint, index, transform):
        self.index = index
        SpherePinStack.__init__(self, surfacePoint, 0.1)
        self.surfacePin = self.CreateSpherePin(textureName='res:/UI/Texture/Planet/drill_pin.png', layer=0, radius=RADIUS_PIN * 0.4, transform=transform, scale=SCALE_ONGROUND * 1.001, color=Color.OLIVE)
        self.pinColor = Color(*planetCommonUI.PLANET_COLOR_EXTRACTOR).SetSaturation(0.4).GetRGBA()
        self.drillArea = self.CreateSpherePin(textureName='res:/UI/Texture/Planet/survey_ghost_512.dds', layer=0, radius=planetCommon.RADIUS_DRILLAREAMAX, transform=transform, scale=SCALE_ONGROUND, color=(0.4, 0.4, 0.9, 0.75))
        self.surfacePin.name = '5,%d' % index

    def GetDuration(self):
        return getattr(self, 'duration', 1440)

    def GetAmount(self):
        return getattr(self, 'amount', 500)

    def GetHeadRadius(self):
        return getattr(self, 'headRadius', planetCommon.RADIUS_DRILLAREAMAX)
