#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\control\slider.py
import uthread2
from carbon.client.script.environment.AudioUtil import PlaySound
from carbon.common.script.util.mathCommon import FloatCloseEnough
from carbonui.primitives.fill import Fill
from carbonui.primitives.frame import Frame
from carbonui.uianimations import animations
from eve.client.script.ui import eveColor, eveThemeColor
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.control.themeColored import SpriteThemeColored, FrameThemeColored
import carbonui.const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.line import Line
from carbonui.util.various_unsorted import GetAttrs
from carbonui.uicore import uicore
from signals import Signal
MOUSE_WHEEL_SPEED = 0.0005
BAR_PADDING = 5

class Slider(Container):
    default_align = uiconst.TOTOP
    default_height = 16
    default_barHeight = 6
    default_handleSize = 12
    default_minValue = 0.0
    default_maxValue = 1.0
    default_value = None
    default_config = ''
    default_setting = None
    default_label = None
    default_minLabel = None
    default_maxLabel = None
    default_increments = None
    default_snapToIncrements = True
    default_isEvenIncrements = False
    default_getHintFunc = None
    default_mouseWheelEnabled = True
    default_isInteger = False
    default_callback = None
    default_on_dragging = None

    def ApplyAttributes(self, attributes):
        super(Slider, self).ApplyAttributes(attributes)
        self.value = attributes.get('value', self.default_value)
        self.maxValue = attributes.get('maxValue', self.default_maxValue)
        self.minValue = attributes.get('minValue', self.default_minValue)
        self.handle_size = attributes.get('handleSize', self.default_handleSize)
        self._labelText = attributes.get('label', self.default_label)
        self._minLabelText = attributes.get('minLabel', self.default_minLabel)
        self._maxLabelText = attributes.get('maxLabel', self.default_maxLabel)
        self._mouseWheelEnabled = attributes.get('mouseWheelEnabled', self.default_mouseWheelEnabled)
        self.barHeight = attributes.get('barHeight', self.default_barHeight)
        self.isInteger = attributes.get('isInteger', self.default_isInteger)
        self.incrementValues = attributes.get('increments', self.default_increments) or []
        self.snapToIncrements = attributes.get('snapToIncrements', self.default_snapToIncrements)
        self.isEvenIncrementsSlider = attributes.get('isEvenIncrementsSlider', self.default_isEvenIncrements) and bool(self.incrementValues)
        self.config = attributes.get('config', self.default_config)
        self.setting = attributes.get('setting', self.default_setting)
        if self.setting:
            self.minValue = self.setting.min_value
            self.maxValue = self.setting.max_value
        self._getHintFunc = attributes.get('getHintFunc', self.default_getHintFunc)
        callback_func = attributes.get('callback', self.default_callback)
        on_dragging_func = attributes.get('on_dragging', self.default_on_dragging)
        self.isDragging = False
        self._hasMouseMovedOver = False
        self.handle = None
        self.handleOffset = 0
        self.incrementValuesNormalized = []
        self.tickLines = []
        self._ConstructBarCont()
        self._ConstructHandle()
        self.ticksCont = Container(name='ticksCont', parent=self.barCont)
        self._ConstructBackground()
        self._ConstructLabel()
        self._ConstructMinMaxLabels()
        self.SetIncrements(self.incrementValues)
        self._InitializeValue()
        self._ConstructSignals(callback_func, on_dragging_func)

    def _ConstructMinMaxLabels(self):
        if not (self._minLabelText or self._maxLabelText):
            return
        self.maxLabel = EveLabelMedium(parent=self, align=uiconst.BOTTOMLEFT, text=self._minLabelText)
        self.minLabel = EveLabelMedium(parent=self, align=uiconst.BOTTOMRIGHT, text=self._maxLabelText)
        _, textHeight = EveLabelMedium.MeasureTextSize(self._minLabelText or '' + self._maxLabelText or '')
        self.height += textHeight

    def _ConstructSignals(self, callback_func, on_dragging_func):
        self.callback = Signal('Slider.callback')
        if callback_func:
            self.callback.connect(callback_func)
        self.on_dragging = Signal('Slider.on_dragging')
        if on_dragging_func:
            self.on_dragging.connect(on_dragging_func)

    def _InitializeValue(self):
        if self.setting:
            value = self.setting.get()
        elif self.config:
            value = self._GetValueFromSetting()
        elif self.value is not None:
            value = self.value
        else:
            value = self.minValue
        self.SetValue(value)

    def _GetValueFromSetting(self):
        if len(self.config) == 3:
            cfgName, prefsType, defaultValue = self.config
            if prefsType is not None:
                si = GetAttrs(settings, *prefsType)
                if si is not None:
                    value = si.Get(cfgName, defaultValue)
                else:
                    value = defaultValue
            else:
                value = defaultValue
        else:
            value = settings.user.ui.Get(self.config, (self.maxValue - self.minValue) * 0.5)
            if value is None:
                value = 0.0
        return value

    def _ConstructBarCont(self):
        self.barCont = Container(parent=self, name='barCont', align=uiconst.TOTOP, state=uiconst.UI_NORMAL, height=self.barHeight + 2 * BAR_PADDING)
        self.barCont.OnClick = self.OnSliderClicked
        self.barCont.OnMouseMove = self.OnSliderMouseMove
        self.barCont.OnMouseExit = self.OnMouseBarExit
        self.barCont.OnMouseWheel = self.OnMouseWheel
        self.barCont.GetHint = self.GetHint
        self.barCont.GetTooltipPosition = self.GetTooltipPosition

    def _ConstructBackground(self):
        bgCont = Container(name='bgCont', padding=(0,
         BAR_PADDING,
         0,
         BAR_PADDING), parent=self.barCont)
        Frame(bgParent=bgCont, name='bgFrame', texturePath='res:/UI/Texture/Classes/Slider/bgFrame.png', color=eveColor.MATTE_BLACK, cornerSize=3)
        Frame(bgParent=bgCont, name='bgFrame', texturePath='res:/UI/Texture/Classes/Slider/bgFill.png', color=eveColor.BLACK, opacity=0.6, cornerSize=3)

    def OnSliderClicked(self, *args):
        _, newValue = self._FindNewValue()
        self.SetValue(newValue)
        self._OnEndUserAction()

    def _OnEndUserAction(self):
        if self.setting:
            self.setting.set(self.GetValue())
        self._ApplyConfigSetting()
        self.callback(self)

    def OnSliderMouseMove(self, *args):
        self._hasMouseMovedOver = True
        if not self.incrementValues or not self.snapToIncrements:
            return
        _, value = self._FindNewValue()
        if value not in self.incrementValues or not self.tickLines:
            return
        valueIndex = self.incrementValues.index(value)
        self._ApplyTickOpacity(valueIndex)

    def _ApplyTickOpacity(self, valueIndex = None):
        for i, tick in enumerate(self.tickLines):
            isSelected = i == valueIndex
            tick.opacity = self._GetTickOpacity(i, isSelected)

    def _GetTickOpacity(self, i, isSelected = False):
        if isSelected:
            return 1.5
        elif self.incrementValuesNormalized[i] in (0.0, 1.0):
            return 0.0
        else:
            return 1.0

    def _ConstructHandle(self):
        self.handleOffset = 4
        self.handle = Container(name='handle', parent=self.barCont, state=uiconst.UI_NORMAL, align=uiconst.CENTERLEFT, pos=(0,
         0,
         self.handle_size,
         self.handle_size))
        self.handleFill = Fill(name='handleFill', parent=self.handle, align=uiconst.CENTER, pos=(0, 0, 4, 8), outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, glowBrightness=0.0, color=eveThemeColor.THEME_FOCUS)
        self.handle.OnMouseEnter = self.OnHandleMouseEnter
        self.handle.OnMouseDown = self.OnHandleMouseDown
        self.handle.OnMouseUp = self.OnHandleMouseUp
        self.handle.OnMouseMove = self.OnHandleMouseMove
        self.handle.GetHint = self.GetHint

    def _ConstructLabel(self):
        if self._labelText:
            self.label = EveLabelMedium(parent=self, top=13, state=uiconst.UI_NORMAL, hint=self.hint, text=self._labelText)
        else:
            self.label = None

    def ReconstructIncrements(self):
        for tick in self.tickLines:
            tick.Close()

        self.tickLines = []
        if self.incrementValues:
            w, _ = self.GetAbsoluteSize()
            maxX = self._GetMaxX()
            for i, valueNormalized in enumerate(self.incrementValuesNormalized):
                left = valueNormalized
                line = self._ConstructTickLine(i, left)
                self.tickLines.append(line)

    def _ConstructTickLine(self, i, left):
        padding = BAR_PADDING + 2
        return Line(parent=self.ticksCont, name='tickLine', align=uiconst.TOPLEFT_PROP, color=eveColor.SMOKE_BLUE, opacity=self._GetTickOpacity(i), left=left, width=1, top=7, height=self.barHeight - 4)

    def SetIncrements(self, values):
        self.incrementValues = values
        numIncrements = len(self.incrementValues)
        self.incrementValuesNormalized = []
        for idx, value in enumerate(self.incrementValues):
            if self.isEvenIncrementsSlider:
                normalizedValue = float(idx) / (numIncrements - 1)
            else:
                normalizedValue = (value - self.minValue) / float(self.maxValue - self.minValue)
            self.incrementValuesNormalized.append(normalizedValue)

        self.ReconstructIncrements()

    def GetValue(self):
        return self.value

    def _UpdateHandlePosition(self, nValue, useIncrements = True):
        maxX = self._GetMaxX()
        leftPercentage = max(0, nValue)
        if self.incrementValues and useIncrements and self.snapToIncrements:
            leftPercentage = self._FindClosest(leftPercentage, self.incrementValuesNormalized)
        left = leftPercentage * maxX
        self.handle.left = int(left) - self.handleOffset

    def SetValue(self, value):
        self.value = self._GetSanitizedValue(value, useIncrements=False)
        self._UpdateHandlePosition(self.GetNormalizedValue(), useIncrements=False)

    def _GetSanitizedValue(self, value, useIncrements = False):
        if self.incrementValues and useIncrements and self.snapToIncrements:
            value = self._FindClosest(round(value, 2), self.incrementValues)
        value = max(self.minValue, min(self.maxValue, value))
        if self.isInteger:
            value = round(value)
        return value

    def GetNormalizedValue(self):
        if self.isEvenIncrementsSlider:
            valueIndex = self.incrementValues.index(self.value)
            percentage = self.incrementValuesNormalized[valueIndex]
            return percentage
        else:
            return float(self.value - self.minValue) / (-self.minValue + self.maxValue)

    def _FindClosest(self, check, values):
        mindiff = values[-1] - values[0]
        found = mindiff
        for value in values:
            diff = abs(value - check)
            if diff < mindiff:
                mindiff = diff
                found = value

        return found

    def OnColorThemeChanged(self):
        super(Slider, self).OnColorThemeChanged()
        self.handleFill.SetRGBA(*eveThemeColor.THEME_FOCUS)

    def OnMouseWheel(self, delta, *args):
        if not self._hasMouseMovedOver or not self._mouseWheelEnabled:
            return False
        if self.incrementValues and self.snapToIncrements:
            value = self._GetMouseWheelNewValueIncrements(delta)
        else:
            value = self._GetMouseWheelNewValue(delta)
        if value is not None:
            self.SetValue(value)
            self._OnEndUserAction()

    def _GetMouseWheelNewValue(self, delta):
        change = MOUSE_WHEEL_SPEED * delta * (self.maxValue - self.minValue)
        newValue = self._GetSanitizedValue(self.GetValue() + change)
        return newValue

    def _GetMouseWheelNewValueIncrements(self, delta):
        currentValue = self.GetValue()
        if delta < 0:
            if currentValue <= self.incrementValues[0]:
                newValue = None
            else:
                newValue = max((x for x in self.incrementValues if x < currentValue and not FloatCloseEnough(x, currentValue)))
        elif currentValue >= self.incrementValues[-1]:
            newValue = None
        else:
            newValue = min((x for x in self.incrementValues if x > currentValue and not FloatCloseEnough(x, currentValue)))
        return newValue

    def OnMouseBarExit(self):
        self._ApplyTickOpacity(-1)

    def OnMouseEnter(self, *args):
        animations.MorphScalar(self.handleFill, 'glowBrightness', startVal=self.handleFill.glowBrightness, endVal=1.0, duration=0.1)

    def OnMouseExit(self, *args):
        self._hasMouseMovedOver = False
        animations.MorphScalar(self.handleFill, 'glowBrightness', startVal=self.handleFill.glowBrightness, endVal=0.0, duration=0.5)

    def OnHandleMouseEnter(self, *args):
        PlaySound(uiconst.SOUND_BUTTON_HOVER)

    def OnHandleMouseDown(self, *args):
        self.isDragging = True
        self._ApplyTickOpacity(-1)
        uthread2.StartTasklet(self._TooltipUpdateThread)
        animations.SpColorMorphTo(self.handleFill, self.handleFill.GetRGBA(), eveColor.WHITE, duration=0.1)
        animations.MorphScalar(self.handleFill, 'glowBrightness', self.handleFill.glowBrightness, 0.3, duration=0.1)

    def _TooltipUpdateThread(self):
        while self.isDragging:
            uicore.uilib.tooltipHandler.UpdateTooltipHint(self)
            uthread2.Yield()

    def OnHandleMouseUp(self, *args):
        PlaySound(uiconst.SOUND_BUTTON_CLICK)
        uicore.uilib.UnclipCursor()
        self.isDragging = False
        self._OnEndUserAction()
        animations.SpColorMorphTo(self.handleFill, self.handleFill.GetRGBA(), eveThemeColor.THEME_FOCUS, duration=0.3)
        animations.MorphScalar(self.handleFill, 'glowBrightness', self.handleFill.glowBrightness, 1.0, duration=0.3, curveType=uiconst.ANIM_OVERSHOT5)

    def _ApplyConfigSetting(self):
        if self.config:
            if len(self.config) == 3:
                cfgName, prefsType, defaultValue = self.config
                if prefsType:
                    si = GetAttrs(settings, *prefsType)
                    if si is not None:
                        value = si.Set(cfgName, self.value)
            else:
                settings.user.ui.Set(self.config, self.value)

    def OnHandleMouseMove(self, *args):
        if self.isDragging:
            PlaySound(uiconst.SOUND_VALUECHANGE_TICK)
            localMousePos, value = self._FindNewValue()
            if self.handle.left + self.handleOffset == localMousePos:
                return
            self.handle.left = localMousePos - self.handleOffset
            self.value = self._GetSanitizedValue(value, useIncrements=True)
            self._UpdateHandlePosition(self.GetNormalizedValue(), useIncrements=True)
            self.on_dragging(self)

    def _FindNewValue(self):
        l, _, w, _ = self.GetAbsolute()
        hw = self._GetHandleWidth()
        maxX = self._GetMaxX()
        localMousePos = uicore.uilib.x - l - hw / 2
        localMousePos = max(0, min(maxX, localMousePos))
        localMousePercentagePos = min(1, max(0, float(localMousePos) / maxX))
        if self.isEvenIncrementsSlider:
            numIncrements = len(self.incrementValuesNormalized)
            eachStep = float(maxX) / (numIncrements - 1)
            localMousePercentagePos = self._FindClosest(localMousePercentagePos, self.incrementValuesNormalized)
            partIndex = self.incrementValuesNormalized.index(localMousePercentagePos)
            localMousePos = partIndex * eachStep
            value = self.incrementValues[partIndex]
        else:
            if self.incrementValues and self.snapToIncrements:
                localMousePercentagePos = self._FindClosest(localMousePercentagePos, self.incrementValuesNormalized)
                localMousePos = localMousePercentagePos * maxX
            value = self.minValue + localMousePercentagePos * (self.maxValue - self.minValue)
        return (localMousePos, value)

    def _GetMaxX(self):
        w, _ = self.GetAbsoluteSize()
        maxX = w - self._GetHandleWidth()
        return maxX

    def _GetHandleWidth(self):
        return self.handle.width - 2 * self.handleOffset

    def Enable(self, *args):
        self.SetState(uiconst.UI_NORMAL)
        animations.FadeIn(self)

    def Disable(self, *args):
        self.SetState(uiconst.UI_DISABLED)
        animations.FadeTo(self, startVal=self.opacity, endVal=0.5)

    def GetHint(self):
        if self._getHintFunc:
            return self._getHintFunc(self)
        else:
            return super(Slider, self).GetHint()

    def GetTooltipPosition(self):
        return self.handle.GetAbsolute()

    def SetLabel(self, text):
        self._labelText = text
        if not self.label:
            self._ConstructLabel()
        else:
            self.label.SetText(text)

    def UpdateAlignment(self, budgetLeft = 0, budgetTop = 0, budgetWidth = 0, budgetHeight = 0, updateChildrenOnly = False):
        ret = super(Slider, self).UpdateAlignment(budgetLeft, budgetTop, budgetWidth, budgetHeight, updateChildrenOnly)
        if self.value is not None:
            self._UpdateHandlePosition(self.GetNormalizedValue())
        return ret
