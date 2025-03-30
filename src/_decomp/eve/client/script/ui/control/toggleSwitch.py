#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\toggleSwitch.py
import math
import carbonui
import threadutils
import trinity
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui.control.button import BusyContext
from carbonui.primitives.container import Container
from carbonui.primitives.frame import Frame
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.stretchspritehorizontal import StretchSpriteHorizontal
from carbonui.primitives.transform import Transform
from carbonui.uianimations import animations
from eve.client.script.ui import eveColor, eveThemeColor
from localization import GetByLabel
import carbonui.const as uiconst
from signals import Signal
ON_FRAME_OPACITY = 0.6

class BaseToggleSwitch(Container):
    default_width = 24
    default_height = 16
    default_minWidth = 24
    default_minHeight = 24
    default_enabled = True
    default_align = carbonui.Align.TOPLEFT
    default_state = carbonui.uiconst.UI_NORMAL
    default_clipChildren = True
    default_checked = False
    default_setting = None
    default_onText = GetByLabel('UI/SystemMenu/DisplayAndGraphics/Common/On')
    default_offText = GetByLabel('UI/SystemMenu/DisplayAndGraphics/Common/Off')
    default_handleSize = 12
    handleLabelOffset = 4
    labelVerticalPadding = 2
    handleTexturePath = 'res:/UI/Texture/classes/toggleSwitch/handle.png'
    handleTextureChecked = handleTexturePath
    __busy_context = None

    def ApplyAttributes(self, attributes):
        self.onFrame = None
        self.offFrame = None
        super(BaseToggleSwitch, self).ApplyAttributes(attributes)
        self.onText = attributes.get('onText', self.default_onText)
        self.offText = attributes.get('offText', self.default_offText)
        handleSize = attributes.get('handleSize', self.default_handleSize)
        setting = attributes.get('setting', self.default_setting)
        enabled = attributes.get('enabled', self.default_enabled)
        self.confirmFunc = attributes.get('confirmFunc', None)
        self.switchController = SwitchController(setting, enabled, handleSize)
        self.switchController.on_set_checked.connect(self.SetChecked)
        self.switchController.on_busy_changed.connect(self.UpdateBusy)
        self.on_switch_changed = Signal(signalName='on_switch_changed')
        isChecked = attributes.get('checked', self.default_checked)
        self.isTabStop = 1
        self.ConstructLayout()
        if self.switchController.HasSettings():
            isChecked = self.switchController.GetIsCheckedSettingValue()
        self.SetChecked(isChecked, 0)
        self.UpdateBusy()

    def ConstructLayout(self):
        self.ConstructSliderHandle()
        self._ConstructFrame()

    def ConstructSliderHandle(self):
        handleSize = self.switchController.handleSize
        self.sliderHandle = Container(name='sliderHandle', parent=self, fillCenter=True, align=carbonui.Align.CENTERLEFT, pos=(self.handleLabelOffset,
         0,
         handleSize,
         handleSize))
        self.sliderHandleSprite = Sprite(parent=self.sliderHandle, pos=(0,
         0,
         handleSize,
         handleSize), align=carbonui.Align.CENTER, texturePath=self.handleTexturePath, state=uiconst.UI_DISABLED)

    def _ConstructFrame(self):
        pass

    def SetChecked(self, isChecked, report = 1):
        isChecked = isChecked or 0
        self.switchController.ForceSetCheckedValue(int(isChecked))
        self.SetCheckLook(bool(report))
        if report:
            if isChecked:
                PlaySound(uiconst.SOUND_SETDESELECTED)
            else:
                PlaySound(uiconst.SOUND_SETSELECTED)
            self.switchController.UpdateSettings()
            self.on_switch_changed(self, self.switchController.checked)

    def SetCheckLook(self, animate = False):
        isChecked = self.switchController.checked
        if isChecked:
            newLeft = self.width - self.switchController.handleSize - self.handleLabelOffset
            handleTexturePath = self.handleTextureChecked
            handleOpacity = 1.0
        else:
            newLeft = self.handleLabelOffset
            handleTexturePath = self.handleTexturePath
            handleOpacity = 0.75
        self.sliderHandleSprite.texturePath = handleTexturePath
        self.sliderHandleSprite.opacity = handleOpacity
        if animate:
            animations.MorphScalar(self.sliderHandle, 'left', startVal=self.sliderHandle.left, endVal=newLeft, duration=0.2)
        else:
            self.sliderHandle.left = newLeft
        self.onFrame.display = bool(isChecked)
        self.offFrame.display = not bool(isChecked)

    def SetValue(self, value, report = True):
        if report:
            self.checked = value
        else:
            self.switchController.ForceSetCheckedValue(value)

    def OnClick(self, *args):
        if not self.switchController.disabled:
            if self.WasConfirmed():
                self.ToggleState()

    def WasConfirmed(self):
        if self.confirmFunc:
            return self.confirmFunc(self.checked)
        return True

    def ToggleState(self):
        self.SetChecked(not self.switchController.checked)

    def OnMouseEnter(self, *args):
        self.switchController.hovered = True
        if self.switchController.disabled:
            return
        self.UpdateHoverLook(True)

    def OnMouseExit(self, *args):
        self.switchController.hovered = False
        if self.switchController.disabled:
            return
        self.UpdateHoverLook(False)

    def UpdateHoverLook(self, on):
        if on:
            self.onFrame.opacity = 0.9
            self.offFrame.opacity = 1.5
        else:
            self.onFrame.opacity = ON_FRAME_OPACITY
            self.offFrame.opacity = 1.0

    def GetHint(self):
        hintList = []
        if self.switchController.checked:
            hintList.append('Current status: %s ' % self.onText)
        else:
            hintList.append('Current status: %s ' % self.offText)
        if not self.switchController.disabled:
            hintList.append('Click to toggle')
        return '<br>'.join(hintList)

    def OnColorThemeChanged(self):
        super(BaseToggleSwitch, self).OnColorThemeChanged()
        self.onFrame.SetRGBA(*(eveThemeColor.THEME_FOCUS[:3] + (self.onFrame.opacity,)))

    @property
    def checked(self):
        return self.switchController.checked

    @checked.setter
    def checked(self, value):
        self.switchController.checked = value

    @property
    def busy(self):
        return self.switchController.busy

    @busy.setter
    def busy(self, value):
        self.switchController.busy = value

    @property
    def busy_context(self):
        if self.__busy_context is None:
            self.__busy_context = BusyContext(self)
        return self.__busy_context

    def UpdateBusy(self):
        if self.destroyed:
            return
        if self.switchController.busy:
            self.Disable()
        else:
            self.Enable()


class ToggleSwitch(BaseToggleSwitch):
    default_adjustSize = True
    _arrowsCont = None
    handleTextureChecked = 'res:/UI/Texture/classes/toggleSwitch/handleCheckedSmall.png'

    def ApplyAttributes(self, attributes):
        super(ToggleSwitch, self).ApplyAttributes(attributes)
        adjustSize = attributes.get('adjustSize', self.default_adjustSize)
        if adjustSize:
            self.AdjustSize(attributes)

    def AdjustSize(self, attributes):
        textwidthOn, textheightOn = self.onLabel.MeasureTextSize(self.onText)
        textwidthOff, textheightOff = self.offLabel.MeasureTextSize(self.offText)
        maxTextheight = max(textheightOn, textheightOff)
        self.switchController.handleSize = max(self.switchController.handleSize, maxTextheight - 4)
        maxLabelWidth = max(textwidthOn, textwidthOff)
        self.width = max(self.width, maxLabelWidth + self.switchController.handleSize + 2.5 * self.handleLabelOffset)
        self.height = max(self.height, maxTextheight + 2 * self.labelVerticalPadding)
        self.UpdateHandleSizes()
        self.SetCheckLook()

    def UpdateHandleSizes(self):
        handleSize = self.switchController.handleSize
        for element in (self.sliderHandle, self.sliderHandleSprite):
            element.width = handleSize
            element.height = handleSize

    def ConstructLayout(self):
        super(ToggleSwitch, self).ConstructLayout()
        self.ConstructLabels()

    def ConstructLabels(self):
        self.onLabel = carbonui.TextDetail(parent=self, text=self.onText, align=carbonui.Align.CENTERLEFT, left=self.handleLabelOffset)
        self.offLabel = carbonui.TextDetail(parent=self, text=self.offText, align=carbonui.Align.CENTERRIGHT, left=self.handleLabelOffset)

    def _ConstructFrame(self):
        self.onFrame = Frame(name='onFrame', bgParent=self, frameConst=('res:/UI/Texture/classes/toggleSwitch/backgroundFill.png', 8, 0), opacity=ON_FRAME_OPACITY, color=eveThemeColor.THEME_FOCUSDARK)
        self.offFrame = Frame(name='offFrame', bgParent=self, frameConst=('res:/UI/Texture/classes/toggleSwitch/backgroundFrame.png', 8, 0), color=eveThemeColor.THEME_FOCUSDARK)

    def SetCheckLook(self, animate = False):
        super(ToggleSwitch, self).SetCheckLook(animate)
        self.onLabel.display = bool(self.switchController.checked)
        self.offLabel.display = not bool(self.switchController.checked)

    def OnColorThemeChanged(self):
        super(ToggleSwitch, self).OnColorThemeChanged()
        self.offFrame.SetRGBA(*(eveThemeColor.THEME_FOCUS[:3] + (self.offFrame.opacity,)))

    def UpdateBusy(self):
        if self.destroyed:
            return
        if self.switchController.busy:
            self.PrepareBusyArrows()
            self._arrowsCont._start_arrow_animation()
            self.Disable()
        else:
            if self._arrowsCont is not None:
                self._arrowsCont._stop_arrow_animation()
            self.Enable()

    def PrepareBusyArrows(self):
        if self._arrowsCont is None:
            self._arrowsCont = ArrowCont(parent=self, switchController=self.switchController)
        return self._arrowsCont


class ToggleSwitchCompact(BaseToggleSwitch):
    default_handleSize = 8
    handleLabelOffset = 0
    default_width = 16
    handleTexturePath = 'res:/UI/Texture/classes/toggleSwitch/handleSmall.png'

    def _ConstructFrame(self):
        cont = Container(name='cont', parent=self, align=uiconst.VERTICALLY_CENTERED, height=4, opacity=0.8)
        self.onFrame = StretchSpriteHorizontal(name='onFrame', parent=cont, align=uiconst.TOTOP_NOPUSH, texturePath='res:/UI/Texture/classes/toggleSwitch/compactBackground.png', height=4, leftEdgeSize=3, rightEdgeSize=3, color=eveThemeColor.THEME_FOCUS)
        self.offFrame = StretchSpriteHorizontal(name='offFrame', parent=cont, align=uiconst.TOTOP_NOPUSH, texturePath='res:/UI/Texture/classes/toggleSwitch/compactBackground.png', height=4, leftEdgeSize=3, rightEdgeSize=3, color=eveColor.MATTE_BLACK)


class SwitchController(object):

    def __init__(self, setting, enabled, handleSize):
        self._setting = setting
        self._enabled = enabled
        self._handleSize = handleSize
        self._hovered = False
        self._checked = False
        self._busy = False
        self.on_set_checked = Signal()
        self.on_busy_changed = Signal()

    def UpdateSettings(self):
        if self._setting:
            if self._checked:
                self._setting.enable()
            else:
                self._setting.disable()

    def _GetSettingValue(self):
        return self._setting.is_enabled()

    def GetIsCheckedSettingValue(self):
        return self._GetSettingValue()

    def HasSettings(self):
        return self._setting is not None

    @property
    def handleSize(self):
        return self._handleSize

    @handleSize.setter
    def handleSize(self, value):
        self._handleSize = value

    @property
    def hovered(self):
        return self._hovered

    @hovered.setter
    def hovered(self, value):
        self._hovered = value

    @property
    def checked(self):
        return self._checked

    @checked.setter
    def checked(self, value):
        if self._checked != value:
            self.SetChecked(value)

    def ForceSetCheckedValue(self, value):
        self._checked = value

    def SetChecked(self, value):
        self.on_set_checked(value)

    @property
    def disabled(self):
        return not self._enabled

    @disabled.setter
    def disabled(self, value):
        self.enabled = not value

    @property
    def busy(self):
        return self._busy

    @busy.setter
    def busy(self, value):
        if value != self._busy:
            self._busy = value
            self.on_busy_changed()


BUSY_ANIMATION_DURATION = 2.0
ARROWS_TEXTURE = 'res:/UI/Texture/Classes/Industry/CenterBar/arrows.png'
ARROWS_TEXTURE_SEGMENT_COUNT = 6
ARROWS_TEXTURE_MASK = 'res:/UI/Texture/Classes/Industry/CenterBar/arrowMask.png'

class ArrowCont(Transform):
    default_name = 'arrowCont'
    default_align = carbonui.Align.TOALL
    default_rotationCenter = (0.5, 0.5)

    def ApplyAttributes(self, attributes):
        super(ArrowCont, self).ApplyAttributes(attributes)
        self.switchController = attributes.switchController
        self._arrows = Sprite(name='arrows', parent=self, texturePath=ARROWS_TEXTURE_MASK, textureSecondaryPath=ARROWS_TEXTURE, spriteEffect=trinity.TR2_SFX_MODULATE, color=eveColor.LED_GREY, idx=0, align=carbonui.Align.TOALL, state=uiconst.UI_DISABLED)
        self._arrows.tileXSecondary = True
        x_translation = 1.0 / float(ARROWS_TEXTURE_SEGMENT_COUNT)
        self._arrows.translationSecondary = (-x_translation, 0)

    @threadutils.threaded
    def _start_arrow_animation(self):
        if self.destroyed:
            return
        self._animate_reset_arrow()
        if self.switchController.busy:
            animations.FadeIn(self._arrows)
            self._loop_arrow_animation()

    def _stop_arrow_animation(self):
        if self.destroyed:
            return
        self._animate_reset_arrow()
        if not self.switchController.busy:
            self._arrows.opacity = 0.0
            animations.StopAnimation(self._arrows, 'translationSecondary')

    def _loop_arrow_animation(self):
        if not self.switchController.busy and not self.destroyed:
            return
        x_translation = 1.0 / float(ARROWS_TEXTURE_SEGMENT_COUNT)
        animations.MorphVector2(self._arrows, 'translationSecondary', (x_translation, 0.0), (-x_translation, 0.0), duration=BUSY_ANIMATION_DURATION, curveType=uiconst.ANIM_LINEAR, loops=uiconst.ANIM_REPEAT)

    def _animate_reset_arrow(self):
        x_translation = 1.0 / float(ARROWS_TEXTURE_SEGMENT_COUNT)
        diff = math.fabs(-x_translation - self._arrows.translationSecondary[0])
        if diff > 0.001:
            duration = diff / x_translation / 2.0 * BUSY_ANIMATION_DURATION
            animations.MorphVector2(self._arrows, 'translationSecondary', self._arrows.translationSecondary, (-x_translation, 0.0), duration=duration, curveType=uiconst.ANIM_LINEAR)
        if self.switchController.checked:
            self.rotation = 0
        else:
            self.rotation = math.pi
