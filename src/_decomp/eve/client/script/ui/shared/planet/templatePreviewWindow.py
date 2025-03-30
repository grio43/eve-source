#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\planet\templatePreviewWindow.py
import math
import random
import blue
import mathext
import monolithconfig
import evetypes
import uthread2
from carbonui import uiconst, TextBody, TextDetail, Align, TextColor, TextHeader
from carbonui.control.button import Button
from carbonui.control.checkbox import Checkbox
from carbonui.control.slider import Slider
from carbonui.control.window import Window
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from carbonui.services.setting import UserSettingNumeric
from carbonui.uicore import uicore
from carbonui.util.color import Color
from eve.client.script.ui.control.infoIcon import MoreInfoIcon
from eve.client.script.ui.control.message import ShowQuickMessage
from eve.client.script.ui.control.eveLoadingWheel import LoadingWheel
from eve.client.script.ui.shared.planet.colonyTemplateLoading import LoadPiTemplate
from eve.client.script.ui.shared.planet.planetConst import *
from eve.client.script.ui.shared.planet.planetUIPins import TemplatePins
from eve.common.script.planet.colonyData import ColonyData
from eve.common.script.planet.surfacePoint import SurfacePoint
from eve.common.script.util.planetCommon import RADIUS_DRILLAREAMIN, RADIUS_DRILLAREAMAX
import inventorycommon.const as invConst
from eveplanet.client.templates.templateConst import ExtractionTypes, ProcessedTypes, RefinedTypes, SpecializedTypes, AdvancedTypes, TemplateDictKeys, TemplatePinDataDictKeys
from localization import GetByLabel
from urllib3.packages.ordered_dict import OrderedDict
EXTRACT_PRODUCTS = set(ExtractionTypes.itervalues())
PRODUCTION_PRODUCTS = set(ProcessedTypes.itervalues()).union(set(RefinedTypes.itervalues())).union(set(SpecializedTypes.itervalues())).union(set(AdvancedTypes.itervalues()))
COMMENT_MAX_WIDTH = 60
DEFAULT_DRILL_RADIUS = (RADIUS_DRILLAREAMIN + RADIUS_DRILLAREAMAX) / 2.0
RING_NAME = 'RotationGizmoRings'
MIN_RING = 2
MAX_RING = 999999
CURSOR_PATH = 'res:/UI/Cursor/cursor32_x2.png'
BASE_MIN_RANGE = 0.012
PI_TEMPLATE_FUSCATION_CONFIG_ID = 'pi_template_fuscation'

class TemplatePreviewWindow(Window):
    default_windowInstanceID = u'TemplatePreviewWindow'
    default_fixedWidth = 400
    default_fixedHeight = 300
    default_caption = localization.GetByLabel('UI/PI/TemplatePreviewWindow')
    default_windowID = u'TemplatePreviewWindow'
    default_analyticID = 'pi_template_preview_window'
    surfacePoints = []

    def ApplyAttributes(self, attributes):
        super(type(self), self).ApplyAttributes(attributes)
        self.contentCont = None
        self.template = attributes.get('template', None)
        self.planet = attributes.get('clientPlanet', None)
        self.verticalReversed = False
        self.compressed = None
        self.buildIndicatorPins = []
        self.pinMover = PinMover()
        uthread2.start_tasklet(self.DoInit)

    def DoInit(self):
        self.lw = LoadingWheel(name='loadingWheel', parent=self.content, align=uiconst.CENTER, state=uiconst.UI_NORMAL, pos=(0, 0, 160, 160), opacity=1.0, idx=0)
        self.lw.Show()
        self.CompressPins(self.template.loadedTemplate[TemplateDictKeys.PinData])
        ShowQuickMessage(localization.GetByLabel('UI/PI/PreprocessDone'))
        self.lw.Hide()
        self.ConstructLayout()
        self.FocusToCmdCtr()

    def ConstructLayout(self):
        self.contentCont = cont = ContainerAutoSize(name='contentCont', parent=self.content, align=uiconst.TOTOP, padding=8, callback=self.OnContSizeChanged)
        comment = self.template.loadedTemplate[TemplateDictKeys.Comments]
        comment = comment if len(comment) < COMMENT_MAX_WIDTH else u'{0}...'.format(comment[:COMMENT_MAX_WIDTH])
        TextHeader(name='commentLabel', parent=cont, text=comment, align=Align.TOTOP, state=uiconst.UI_NORMAL, bold=True)
        TextBody(parent=cont, align=uiconst.TOTOP, text=localization.GetByLabel('UI/PI/PreviewDescription'), top=8)
        ctrlCont = Container(name='ctrlCont', parent=cont, align=Align.TOTOP, top=8)
        btn = Button(name='RefocusButton', parent=ctrlCont, align=uiconst.TOPRIGHT, pos=(0, 0, 32, 32), hint=localization.GetByLabel('UI/PI/FocusToCmdCtr'), func=self.FocusToCmdCtr, texturePath='res:/UI/Texture/Planet/icons/focusIcon.png')
        ctrlCont.height = btn.height
        ReRenderOnReturn = lambda *args: self.InvokeRerenderLines()
        self.doCompressCb = Checkbox(align=uiconst.TOTOP, name='CompressCheckBox', text=localization.GetByLabel('UI/PI/DoCompress'), checked=True, hint=localization.GetByLabel('UI/PI/DoCompressHint'), parent=ctrlCont, enabled=not monolithconfig.enabled(PI_TEMPLATE_FUSCATION_CONFIG_ID), callback=ReRenderOnReturn, padRight=btn.width)
        TextDetail(parent=cont, text=GetByLabel('UI/PI/Horiz'), align=Align.TOTOP, color=TextColor.SECONDARY)
        self.ConstructSliders(cont)
        ReRenderOnReturn()
        self.DrawGizmo()
        bottomCont = ContainerAutoSize(parent=cont, align=Align.TOTOP, alignMode=Align.TOTOP, top=16)
        buttonCont = ContainerAutoSize(parent=bottomCont, align=Align.TORIGHT)
        btn = Button(name='ConfirmButton', parent=buttonCont, align=uiconst.TOPRIGHT, label=localization.GetByLabel('UI/PI/Confirm'), func=self.Confirm)
        bottomCont.minHeight = btn.height

    def ConstructSliders(self, cont):
        ySetting = UserSettingNumeric('pi_template_y', default_value=0.0, min_value=-180.0, max_value=180.0)
        ySetting.set(0)
        ySetting.on_change.connect(self.OnYSettingChanged)
        self.ySlider = Slider(parent=cont, align=uiconst.TOTOP, setting=ySetting, on_dragging=self.OnYDragging)
        TextDetail(parent=cont, text=GetByLabel('UI/PI/AxisA'), align=Align.TOTOP, color=TextColor.SECONDARY)
        xSetting = UserSettingNumeric('pi_template_x', default_value=0.0, min_value=-180.0, max_value=180.0)
        xSetting.set(0)
        xSetting.on_change.connect(self.OnXSettingChanged)
        self.xSlider = Slider(parent=cont, align=uiconst.TOTOP, setting=xSetting, on_dragging=self.OnXDragging)
        TextDetail(parent=cont, text=GetByLabel('UI/PI/AxisB'), align=Align.TOTOP, color=TextColor.SECONDARY)
        zSetting = UserSettingNumeric('pi_template_z', default_value=0.0, min_value=-180.0, max_value=180.0)
        zSetting.set(0)
        zSetting.on_change.connect(self.OnZSettingChanged)
        self.zSlider = Slider(parent=cont, align=uiconst.TOTOP, setting=zSetting, on_dragging=self.OnZDragging)

    def OnContSizeChanged(self, *args, **kwds):
        if self.contentCont:
            height = self.contentCont.height + self.contentCont.padTop + self.contentCont.padBottom
            _, height = self.GetWindowSizeForContentSize(height=height)
            self.SetFixedHeight(height)

    def OnXSettingChanged(self, value, *args):
        self.pinMover.x = value
        self.InvokeRerenderLines()

    def OnXDragging(self, slider, *args):
        self.pinMover.x = slider.GetValue()
        self.InvokeRerenderLines()

    def OnYSettingChanged(self, value, *args):
        self.pinMover.y = value
        self.InvokeRerenderLines()

    def OnYDragging(self, slider, *args):
        self.pinMover.y = slider.GetValue()
        self.InvokeRerenderLines()

    def OnZSettingChanged(self, value, *args):
        self.pinMover.z = value
        self.InvokeRerenderLines()

    def OnZDragging(self, slider, *args):
        self.pinMover.z = slider.GetValue()
        self.InvokeRerenderLines()

    def UpdateSliderValues(self):
        self.xSlider.SetValue(self.pinMover.x)
        self.ySlider.SetValue(self.pinMover.y)
        self.zSlider.SetValue(self.pinMover.z)

    def InvokeRerenderLines(self, *args):
        pinMover = self.pinMover
        degX = 0
        degY = 0
        degZ = 0
        try:
            degX = -float(pinMover.x)
            degY = float(pinMover.y)
            degZ = float(pinMover.z)
        except:
            pass

        self.ReRenderPins(degX, degY, degZ)
        self.ReRenderLines(degX, degY, degZ)

    def FocusToCmdCtr(self, *args):
        sm.GetService('planetUI').planetNav.cameraController.camera.OrbitToSurfacePoint(self.surfacePoints.values()[0][0], newZoom=sm.GetService('planetUI').planetNav.cameraController.camera.zoomLinear, initStartPos=False)

    def ReRenderPins(self, degX, degY, degZ):
        self.surfacePoints = OrderedDict()
        origPinData = self.template.loadedTemplate[TemplateDictKeys.PinData]
        pinData = origPinData
        if self.doCompressCb.checked:
            pinData = self.CompressPins(pinData)
        for pinCount, pin in enumerate(pinData):
            origPin = self.template.loadedTemplate[TemplateDictKeys.PinData][pinCount]
            point = SurfacePoint(theta=pin[TemplatePinDataDictKeys.Longi], phi=pin[TemplatePinDataDictKeys.Lat], radius=1.05)
            self.surfacePoints[str(origPin)] = (point.GetRotatedSurfacePoint(degX, degY, degZ), pin[TemplatePinDataDictKeys.PinTypeID])

        if not self.buildIndicatorPins:
            self.InitPins()
        i = 0
        for point, typeID in self.surfacePoints.values():
            newPoint = SurfacePoint(theta=point.theta, phi=point.phi, radius=1.0)
            self.buildIndicatorPins[i].SetLocation(newPoint)
            i += 1

    def InitPins(self):
        i = 0
        for pin in self.buildIndicatorPins:
            pin.Remove()

        clientPlanet = sm.GetService('planetUI').GetCurrentPlanet()
        colony = clientPlanet.GetColony(session.charid)
        if colony is None:
            colony = clientPlanet.GetNewColony(session.charid)
            colony.SetColonyData(ColonyData(session.charid, None))
        for point, typeID in self.surfacePoints.values():
            newPoint = SurfacePoint(theta=point.theta, phi=point.phi, radius=1.0)
            color = self._GetPinTypeColor(typeID)
            newPin = TemplatePins(newPoint, typeID, evetypes.GetGroupID(typeID), sm.GetService('planetUI').pinOthersTransform)
            newPin.SetCircleColor(color)
            i += 1
            newPin.SetLocation(newPoint)
            self.buildIndicatorPins.append(newPin)

    def ReRenderLines(self, degX, degY, degZ):
        self.surfacePoints = OrderedDict()
        origPinData = self.template.loadedTemplate[TemplateDictKeys.PinData]
        pinData = origPinData
        if self.doCompressCb.checked:
            pinData = self.CompressPins(pinData)
        for pinCount, pin in enumerate(pinData):
            origPin = self.template.loadedTemplate[TemplateDictKeys.PinData][pinCount]
            point = SurfacePoint(theta=pin[TemplatePinDataDictKeys.Longi], phi=pin[TemplatePinDataDictKeys.Lat], radius=1.05)
            pinTypeID = pin[TemplatePinDataDictKeys.PinTypeID]
            color = self._GetPinTypeColor(pinTypeID)
            self.surfacePoints[str(origPin)] = (point.GetRotatedSurfacePoint(degX, degY, degZ), color)

    def _GetPinTypeColor(self, pinTypeID):
        if evetypes.GetGroupID(pinTypeID) in (invConst.groupStoragePins, invConst.groupSpaceportPins):
            color = Color.BLUE
        elif evetypes.GetGroupID(pinTypeID) == invConst.groupExtractionControlUnitPins:
            color = Color.GREEN
        elif pinTypeID in TYPEIDS_PROCESSORS:
            color = Color.ORANGE
        else:
            color = Color.RED
        return color

    def Confirm(self, *args):
        result = LoadPiTemplate(self.surfacePoints, self.template)
        if result:
            ShowQuickMessage(GetByLabel('UI/PI/LoadedFromTemplate'))
        self.Close()

    def CompressPins(self, pinData):
        if self.compressed:
            return self.compressed
        forProcessing = []
        for id, pin in enumerate(pinData):
            forProcessing.append([id, [pin[TemplatePinDataDictKeys.Longi], pin[TemplatePinDataDictKeys.Lat]]])

        minDist = BASE_MIN_RANGE
        doFuscation = 1 if monolithconfig.enabled(PI_TEMPLATE_FUSCATION_CONFIG_ID) else 0
        forProcessing = adjust_coordinates(forProcessing, minDist, 2, doFuscation)
        forProcessing = sorted(forProcessing, key=lambda coord: coord[0])
        self.compressed = []
        for id, pin in enumerate(forProcessing):
            self.compressed.append({TemplatePinDataDictKeys.PinTypeID: pinData[id][TemplatePinDataDictKeys.PinTypeID],
             TemplatePinDataDictKeys.Longi: pin[1][0],
             TemplatePinDataDictKeys.Lat: pin[1][1]})

        return self.compressed

    def DrawGizmo(self, len = 1.1):
        CLD = sm.GetService('planetUI').curveLineDrawer
        try:
            CLD.ClearLines(RING_NAME)
        except:
            pass

        CLD.CreateLineSet(RING_NAME, sm.GetService('planetUI').planetTransform)
        RED = (1, 0.2, 0.2, 5)
        BLUE = (0.2, 1, 0.2, 5)
        GREEN = (0.2, 0.2, 1, 5)
        for i in range(91):
            i = i * 4 + 0.5
            CLD.DrawLine(RING_NAME, SurfacePoint(math.sin(math.radians(i - 1)) * len, 0, math.cos(math.radians(i - 1)) * len), SurfacePoint(math.sin(math.radians(i)) * len, 0, math.cos(math.radians(i)) * len), 3.0, BLUE, BLUE)

        for i in range(91):
            i = i * 4 + 0.5
            CLD.DrawLine(RING_NAME, SurfacePoint(0, math.sin(math.radians(i - 1)) * len, math.cos(math.radians(i - 1)) * len), SurfacePoint(0, math.sin(math.radians(i)) * len, math.cos(math.radians(i)) * len), 3.0, RED, RED)

        for i in range(91):
            i = i * 4 + 0.5
            CLD.DrawLine(RING_NAME, SurfacePoint(math.sin(math.radians(i - 1)) * len, math.cos(math.radians(i - 1)) * len, 0), SurfacePoint(math.sin(math.radians(i)) * len, math.cos(math.radians(i)) * len, 0), 3.0, GREEN, GREEN)

        CLD.SubmitLineset(RING_NAME)

    def Close(self, **kwargs):
        super(TemplatePreviewWindow, self).Close(kwargs)
        self._Close()

    def _Close(self, *args):
        try:
            for pin in self.buildIndicatorPins:
                pin.Remove()

            cld = sm.GetService('planetUI').curveLineDrawer
            cld.ClearLines(RING_NAME)
            cld.SubmitLineset(RING_NAME)
            lineSet = cld.GetLineSet(RING_NAME)
            if lineSet in sm.GetService('planetUI').planetTransform.children:
                sm.GetService('planetUI').planetTransform.children.remove(lineSet)
            cld.RemoveLineSet(RING_NAME)
        except StandardError as e:
            print 'except = ', e


class PinMover(object):

    def __init__(self):
        self._x = 0
        self._y = 0
        self._z = 0
        self._theta = 0

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        if value > 180:
            value -= 360
        elif value < -180:
            value += 360
        self._x = self._ClampValue(value)

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        self._y = self._ClampValue(value)

    @property
    def z(self):
        return self._z

    @z.setter
    def z(self, value):
        self._z = self._ClampValue(value)

    def _ClampValue(self, value):
        if value > 180:
            value -= 360
        elif value < -180:
            value += 360
        return mathext.clamp(value, -180, 180)


def StartDraggingTemplate(x, y):
    wnd = TemplatePreviewWindow.GetIfOpen()
    if not wnd:
        return
    firstPinTheta = wnd.template.loadedTemplate[TemplateDictKeys.PinData][0][TemplatePinDataDictKeys.Longi]
    originalX = wnd.pinMover.x
    originalY = wnd.pinMover.y
    originalZ = wnd.pinMover.z
    uthread2.StartTasklet(UpdateOften, wnd, x, y, originalX, originalY, originalZ, firstPinTheta)


def UpdateOften(wnd, prevX, prevY, originalX, originalY, originalZ, theta = 0):
    isMouseDown = uicore.uilib.leftbtn
    if wnd.destroyed or not isMouseDown:
        return
    zoomLinear = sm.GetService('planetUI').planetNav.cameraController.camera.zoomLinear
    x = uicore.uilib.x
    y = uicore.uilib.y
    pinMover = wnd.pinMover
    newY = (x - prevX) * zoomLinear * 0.2 + originalY
    pinMover.y = newY
    newX = (y - prevY) * -math.sin(theta) * zoomLinear * 0.2 + originalX
    pinMover.x = newX
    newZ = (y - prevY) * -math.cos(theta) * zoomLinear * 0.2 + originalZ
    pinMover.z = newZ
    compareVal = 75 * zoomLinear * 0.75
    if math.fabs(originalX - pinMover.x) > compareVal or math.fabs(originalY - pinMover.y) > compareVal:
        wnd.FocusToCmdCtr()
    wnd.UpdateSliderValues()
    wnd.InvokeRerenderLines()
    uthread2.Yield()
    uthread2.start_tasklet(UpdateOften, wnd, prevX, prevY, originalX, originalY, originalZ, theta)


def scale_away(coord, target, factor):
    x_diff = coord[1][0] - target[1][0]
    y_diff = coord[1][1] - target[1][1]
    return [coord[0], [target[1][0] + factor * x_diff, target[1][1] + factor * y_diff]]


def move_closer(coord, target, step_size):
    x_diff = target[1][0] - coord[1][0]
    y_diff = target[1][1] - coord[1][1]
    distance = (x_diff ** 2 + y_diff ** 2) ** 0.5
    if distance == 0:
        return coord
    return [coord[0], [coord[1][0] + step_size * x_diff / distance, coord[1][1] + step_size * y_diff / distance]]


def distance_between(coord1, coord2):
    SP1 = SurfacePoint(theta=coord1[1][0], phi=coord1[1][1])
    SP2 = SurfacePoint(theta=coord2[1][0], phi=coord2[1][1])
    return SP1.GetDistanceToOther(SP2)


def is_move_valid(coord, other_coords, MinDist):
    for other in other_coords:
        if distance_between(coord, other) < MinDist:
            return False

    return True


def adjust_coordinates(coordList, minDist, expansion_factor, forcedFuscation = 0):
    target = coordList[0]
    expanded_coords = sorted(coordList[1:], key=lambda coord: distance_between(coord, target))
    expanded_coords = [ scale_away(coord, target, expansion_factor + forcedFuscation * expansion_factor * random.random()) for coord in expanded_coords ]
    adjusted_coords = [target] + expanded_coords
    step_size = minDist * 0.01
    max_iterations = 10000
    iteration = 0
    unchangedIterationCount = 0
    ShowQuickMessage(localization.GetByLabel('UI/PI/PreprocessingMsg', pct=0))
    while iteration < max_iterations:
        somethingChanged = False
        for i in range(1, len(adjusted_coords)):
            new_position = move_closer(adjusted_coords[i], target, step_size)
            if is_move_valid(new_position, adjusted_coords[:i] + adjusted_coords[i + 1:], minDist):
                if adjusted_coords[i] != new_position:
                    somethingChanged = True
                adjusted_coords[i] = new_position

        iteration += 1
        if iteration % 30 == 0:
            if not TemplatePreviewWindow.GetIfOpen():
                ShowQuickMessage(localization.GetByLabel('UI/PI/PreprocessTerminated'))
                return
        if iteration % 1000 == 0:
            ShowQuickMessage(localization.GetByLabel('UI/PI/PreprocessingMsg', pct=iteration * 100.0 / max_iterations), flashNewText=False)
        if somethingChanged:
            unchangedIterationCount = 0
        else:
            if unchangedIterationCount > 20:
                break
            unchangedIterationCount += 1
        blue.pyos.BeNice()

    return adjusted_coords
