#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fittingScreen\fittingLayout.py
import math
from carbon.common.script.util.format import FmtAmt
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from carbonui.uicore import uicore
from carbonui.util.color import Color
from eve.client.script.ui.control.gaugeCircular import GaugeCircular
from eve.client.script.ui.control.themeColored import SpriteThemeColored
from eve.client.script.ui.shared.fitting.fittingUtil import GetScaleFactor, GetBaseShapeSize
from eve.client.script.ui.shared.fittingScreen.fittingUtil import GetColoredText
from eve.client.script.ui.station.fitting.fittingTooltipUtils import GetTooltipPathFromTooltipName
from localization import GetByLabel
import trinity
import telemetry

class FittingLayout(Container):
    default_name = 'fittingBase'
    default_width = 640
    default_height = 640
    default_align = uiconst.CENTERLEFT
    default_state = uiconst.UI_HIDDEN

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.scaleFactor = GetScaleFactor()
        self.baseShapeSize = GetBaseShapeSize()
        self.width = self.baseShapeSize
        self.height = self.baseShapeSize
        overlay = Sprite(parent=self, name='overlay', align=uiconst.TOALL, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/Fitting/fittingbase_overlay.png', color=(1.0, 1.0, 1.0, 0.39))
        radius = int(self.baseShapeSize * 0.885 / 2)
        self.calibrationGaugePreview = CalibrationGaugePreview(parent=self, radius=radius, state=uiconst.UI_DISABLED)
        self.powerGaugePreview = PowergridGaugePreview(parent=self, radius=radius, state=uiconst.UI_DISABLED)
        self.cpuGaugePreview = CPUGaugePreview(parent=self, radius=radius, state=uiconst.UI_DISABLED)
        self.calibrationGauge = CalibrationGauge(parent=self, radius=radius)
        self.powerGauge = PowergridGauge(parent=self, radius=radius)
        self.cpuGauge = CPUGauge(parent=self, radius=radius)
        baseDOT = Sprite(parent=self, name='baseDOT', align=uiconst.TOALL, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/Fitting/fittingbase_dotproduct.png', spriteEffect=trinity.TR2_SFX_DOT, blendMode=trinity.TR2_SBM_ADD)
        self.sr.baseColor = SpriteThemeColored(parent=self, name='baseColor', align=uiconst.TOALL, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/Fitting/fittingbase_basecircle.png', colorType=uiconst.COLORTYPE_UIBASE)
        self.sr.baseShape = Sprite(parent=self, name='baseShape', align=uiconst.TOALL, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/Fitting/fittingbase.png', color=(0.0, 0.0, 0.0, 0.86))


class BaseFittingGauge(GaugeCircular):
    gaugeRange = 45
    default_align = uiconst.CENTER
    default_state = uiconst.UI_PICKCHILDREN
    default_colorMarker = (1.0, 1.0, 1.0, 0.0)
    default_colorBg = (1.0, 1.0, 1.0, 0.0)
    default_lineWidth = 11.0
    hintPath = ''

    @telemetry.ZONE_METHOD
    def ApplyAttributes(self, attributes):
        GaugeCircular.ApplyAttributes(self, attributes)
        self.currentValue = 0

    def SetValue(self, value, animate = True):
        if value > 1.0:
            uicore.animations.FadeTo(self, 0.25, 1.0, duration=0.5, loops=uiconst.ANIM_REPEAT)
        else:
            uicore.animations.FadeIn(self, duration=0.5)
        trueValue = max(0.0, value)
        value = min(1.0, trueValue)
        self.currentValue = 100 * value
        self.currentTrueValue = 100 * trueValue
        value *= self.gaugeRange / 360.0
        GaugeCircular.SetValue(self, value, animate)


class FittingGauge(BaseFittingGauge):

    @telemetry.ZONE_METHOD
    def ApplyAttributes(self, attributes):
        BaseFittingGauge.ApplyAttributes(self, attributes)
        self.gauge.OnMouseMove = self.OnMouseMove
        self.bgGauge.OnMouseMove = self.OnMouseMove
        self.gauge.GetTooltipPosition = self.GetTooltipPosition
        self.bgGauge.GetTooltipPosition = self.GetTooltipPosition

    def OnMouseMove(self, *args):
        value = FmtAmt(self.currentTrueValue, showFraction=2)
        if self.currentTrueValue > 100:
            value = GetColoredText(False, value)
        hintText = GetByLabel(self.hintPath, state=value)
        self.gauge.hint = hintText
        self.bgGauge.hint = hintText

    def GetTooltipPosition(self):
        return (uicore.uilib.x - 5,
         uicore.uilib.y - 5,
         10,
         10)


POWER_RANGE = 45
POWER_START_ANGLE = 45
POWER_COLOR = (0.40625, 0.078125, 0.03125, 0.8)

class PowergridGauge(FittingGauge):
    gaugeRange = POWER_RANGE
    default_name = 'powergridGauge'
    default_colorStart = POWER_COLOR
    default_colorEnd = POWER_COLOR
    default_colorMarker = (1.0, 1.0, 1.0, 0.0)
    default_startAngle = math.radians(POWER_START_ANGLE)
    default_bgPortion = gaugeRange / 360.0
    hintPath = 'UI/Fitting/FittingWindow/PowerGridState'


POWER_COLOR2 = Color(*POWER_COLOR).SetBrightness(0.6).SetAlpha(0.8).GetRGBA()

class PowergridGaugePreview(FittingGauge):
    gaugeRange = POWER_RANGE
    default_name = 'powergridGaugePreview'
    default_colorStart = POWER_COLOR2
    default_colorEnd = POWER_COLOR2
    default_colorMarker = (1.0, 1.0, 1.0, 0.0)
    default_startAngle = math.radians(POWER_START_ANGLE)
    default_bgPortion = gaugeRange / 360.0


CPU_RANGE = 45
CPU_COLOR = (0.203125, 0.3828125, 0.37890625, 0.8)
CPU_START_ANGLE = 135

class CPUGauge(FittingGauge):
    gaugeRange = CPU_RANGE
    default_name = 'cpuGauge'
    default_colorStart = CPU_COLOR
    default_colorEnd = CPU_COLOR
    default_startAngle = math.radians(CPU_START_ANGLE)
    default_clockwise = False
    default_bgPortion = gaugeRange / 360.0
    hintPath = 'UI/Fitting/FittingWindow/CpuState'


CPU_COLOR2 = Color(*CPU_COLOR).SetBrightness(0.7).SetAlpha(0.8).GetRGBA()

class CPUGaugePreview(BaseFittingGauge):
    gaugeRange = CPU_RANGE
    default_name = 'cpuGaugePreview'
    default_colorStart = CPU_COLOR2
    default_colorEnd = CPU_COLOR2
    default_startAngle = math.radians(CPU_START_ANGLE)
    default_clockwise = False
    default_bgPortion = gaugeRange / 360.0


CALIBRATION_RANGE = 30
CALIBRATION_COLOR = (0.29296875, 0.328125, 0.33984375, 0.8)
CALIBRATION_START_ANGLE = 318

class CalibrationGauge(FittingGauge):
    gaugeRange = CALIBRATION_RANGE
    default_name = 'calibrationGauge'
    default_colorStart = CALIBRATION_COLOR
    default_colorEnd = CALIBRATION_COLOR
    default_startAngle = math.radians(CALIBRATION_START_ANGLE)
    default_clockwise = False
    default_bgPortion = gaugeRange / 360.0
    hintPath = 'UI/Fitting/FittingWindow/CalibrationState'

    def ApplyAttributes(self, attributes):
        FittingGauge.ApplyAttributes(self, attributes)
        self.calibrationLoad = 0.0
        self.calibrationOutput = 0.0
        self.bgGauge.LoadTooltipPanel = self.LoadTooltipPanel
        self.gauge.LoadTooltipPanel = self.LoadTooltipPanel

    def SetCalibrationNumbers(self, calibrationLoad, calibrationOutput):
        self.calibrationLoad = calibrationLoad
        self.calibrationOutput = calibrationOutput

    def LoadTooltipPanel(self, tooltipPanel, *args, **kwds):
        tooltipPanel.LoadGeneric3ColumnTemplate()
        tooltipPanel.cellSpacing = (10, 4)
        self._LoadTooltipPanel(tooltipPanel)
        self._tooltipUpdateTimer = AutoTimer(250, self._LoadTooltipPanel, tooltipPanel)

    def _LoadTooltipPanel(self, tooltipPanel):
        if tooltipPanel.destroyed:
            self._tooltipUpdateTimer = None
            return
        if not getattr(tooltipPanel, 'initialized', False):
            tooltipPanel.Flush()
            headerLabelPath, descriptionLabelPath = GetTooltipPathFromTooltipName('Calibration')
            tooltipPanel.LoadGeneric1ColumnTemplate()
            tooltipPanel.AddLabelMedium(text=GetByLabel(headerLabelPath), bold=True, colSpan=tooltipPanel.columns - 1)
            tooltipPanel.AddLabelMedium(text=GetByLabel(descriptionLabelPath), align=uiconst.TOPLEFT, wrapWidth=200, colSpan=tooltipPanel.columns, color=(0.6, 0.6, 0.6, 1))
            tooltipPanel.valueLabel = tooltipPanel.AddLabelMedium(text='', colSpan=tooltipPanel.columns, padTop=10)
            tooltipPanel.initialized = True
        calibrationLoadText = FmtAmt(self.calibrationLoad, showFraction=1)
        calibrationOutputText = FmtAmt(self.calibrationOutput, showFraction=1)
        percentage = GetByLabel('UI/Common/Percentage', percentage=self.currentTrueValue)
        if self.currentTrueValue > 100:
            percentage = GetColoredText(False, percentage)
        tooltipPanel.valueLabel.text = '%s / %s = %s' % (calibrationLoadText, calibrationOutputText, percentage)


CALIBRATION_COLOR2 = Color(*CALIBRATION_COLOR).SetBrightness(0.5).SetAlpha(0.8).GetRGBA()

class CalibrationGaugePreview(BaseFittingGauge):
    gaugeRange = CALIBRATION_RANGE
    default_name = 'calibrationGaugePreview'
    default_colorStart = CALIBRATION_COLOR2
    default_colorEnd = CALIBRATION_COLOR2
    default_startAngle = math.radians(CALIBRATION_START_ANGLE)
    default_clockwise = False
    default_bgPortion = gaugeRange / 360.0
