#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\control\checkbox.py
import logging
import math
import uthread
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui import fontconst, uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.primitives.frame import Frame
from carbonui.primitives.sprite import Sprite
from carbonui.text.color import TextColor
from carbonui.uianimations import animations
from carbonui.util.various_unsorted import GetAttrs, GetBrowser
from eve.client.script.ui import eveThemeColor
from eve.client.script.ui.control.eveLabel import EveLabelMedium
logger = logging.getLogger(__name__)

class Checkbox(ContainerAutoSize):
    default_enabled = True
    DIODE_SIZE = 16
    DIODE_TEXT_GAP_SIZE = 8
    LABEL_COLOR_IDLE = TextColor.NORMAL
    LABEL_COLOR_HOVER = TextColor.HIGHLIGHT
    LABEL_COLOR_DISABLED = TextColor.DISABLED
    CHECK_MARK_COLOR_DISABLED = TextColor.DISABLED
    CHECK_MARK_COLOR_IDLE = eveThemeColor.THEME_FOCUS
    default_alignMode = uiconst.TOPLEFT
    default_fontsize = fontconst.EVE_MEDIUM_FONTSIZE
    default_width = 0
    default_height = 24
    default_minWidth = 24
    default_minHeight = 24
    default_checkedTexture = 'res:/UI/Texture/classes/checkbox/checked.png'
    default_align = uiconst.TOTOP
    default_text = ''
    default_checked = 0
    default_callback = None
    default_state = uiconst.UI_NORMAL
    default_wrapLabel = True
    default_cursor = uiconst.UICURSOR_SELECT
    default_fontStyle = None
    default_fontFamily = None
    default_fontPath = None
    default_setting = None
    default_settingsPath = ('user', 'ui')
    default_settingsKey = None

    def ApplyAttributes(self, attributes):
        self._callback = None
        if 'callback' in attributes:
            self._callback = attributes.pop('callback')
        super(Checkbox, self).ApplyAttributes(attributes)
        text = attributes.get('text', self.default_text)
        self.checkedTexture = attributes.get('checkedTexture', self.default_checkedTexture)
        self._enabled = attributes.get('enabled', self.default_enabled)
        self.wrapLabel = attributes.get('wrapLabel', self.default_wrapLabel)
        self.fontStyle = attributes.get('fontStyle', self.default_fontStyle)
        self.fontFamily = attributes.get('fontFamily', self.default_fontFamily)
        self.fontPath = attributes.get('fontPath', self.default_fontPath)
        self.fontsize = attributes.get('fontsize', self.default_fontsize)
        isChecked = attributes.get('checked', self.default_checked)
        self.setting = attributes.get('setting', self.default_setting)
        self.settingsKey = attributes.get('settingsKey', self.default_settingsKey)
        self.settingsPath = attributes.get('settingsPath', self.default_settingsPath)
        self.underlay = None
        self._hovered = False
        self._checked = False
        self.isTabStop = 1
        self.checkboxCont = None
        if self.settingsKey is not None:
            self.name = self.settingsKey if isinstance(self.settingsKey, (str, unicode)) else repr(self.settingsKey)
        self.ConstructLayout()
        if self.setting is not None:
            isChecked = self._GetIsCheckedSettingValue()
            self.setting.on_change.connect(self._on_setting_changed)
        self.SetChecked(isChecked, 0)
        self.SetLabelText(text)
        self._update_enabled(animate=False)
        self._update_checkmark_color()

    def Close(self):
        super(Checkbox, self).Close()
        try:
            if self.setting:
                self.setting.on_change.disconnect(self._on_setting_changed)
        except Exception as e:
            logger.exception(e)

    def _on_setting_changed(self, value):
        self.SetChecked(value, report=False)

    @property
    def checked(self):
        return self._checked

    @checked.setter
    def checked(self, value):
        if self._checked != value:
            self.SetChecked(value)

    def ConstructLayout(self):
        self.ConstructLabel()
        self.ConstructCheckboxCont()

    def ConstructLabel(self):
        self.label = EveLabelMedium(name='text', parent=self, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, left=self.DIODE_SIZE + self.DIODE_TEXT_GAP_SIZE, maxLines=1 if not self.wrapLabel else None, color=self._get_label_color())

    def _get_label_color(self):
        if self.hovered:
            return self.LABEL_COLOR_HOVER
        elif self.enabled:
            return self.LABEL_COLOR_IDLE
        else:
            return self.LABEL_COLOR_DISABLED

    def _update_label_color(self, animate = True):
        if self.label:
            if animate:
                duration = uiconst.TIME_ENTRY if self.hovered else uiconst.TIME_EXIT
                animations.SpColorMorphTo(self.label, endColor=self._get_label_color(), duration=duration)
            else:
                self.label.SetRGBA(*self._get_label_color())

    def OnColorThemeChanged(self):
        super(Checkbox, self).OnColorThemeChanged()
        self._update_checkmark_color()

    def Enable(self):
        self.enabled = True

    def Disable(self):
        self.enabled = False

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, value):
        if self._enabled != value:
            self._enabled = value
            self._update_enabled()

    @property
    def disabled(self):
        return not self._enabled

    @disabled.setter
    def disabled(self, value):
        self.enabled = not value

    @property
    def hovered(self):
        return self._hovered

    def _update_enabled(self, animate = True):
        if self.enabled:
            self.underlay.Enable()
        else:
            self.underlay.Disable()
        self._update_checkmark_color()
        self._update_label_color(animate)

    def ToggleState(self):
        self.SetChecked(not self._checked)

    def OnChar(self, char, flag):
        if char == uiconst.VK_SPACE:
            uthread.pool('checkbox::OnChar', self.ToggleState)
            return 1

    def OnSetFocus(self, *args):
        if self and not self.destroyed and self.parent and self.parent.name == 'inlines':
            if self.parent.parent and self.parent.parent.sr.node:
                browser = GetBrowser(self)
                if browser:
                    uthread.new(browser.ShowObject, self)

    def SetValue(self, value):
        self.SetChecked(value)

    def GetValue(self):
        return self._checked

    def SetLabelText(self, labeltext):
        self.label.text = labeltext
        if self.align not in (uiconst.TOTOP, uiconst.TOBOTTOM):
            self.ChangeWidth()

    def ChangeWidth(self, *args):
        self.width = max(20, self.label.padLeft + self.label.left + self.label.textwidth + self.label.padRight) + 1

    def UpdateUIScaling(self, value, oldValue):
        super(Checkbox, self).UpdateUIScaling(value, oldValue)
        self.ChangeWidth()

    def GetLabelText(self):
        return self.label.GetText()

    def SetTextColor(self, color):
        self.label.SetTextColor(color)

    def GetSettingsKey(self):
        if self.setting:
            return self.setting.settings_key
        else:
            return self.settingsKey

    def SetSettingsKey(self, settingsKey):
        self.settingsKey = settingsKey

    def GetSettingsPath(self):
        return self.settingsPath

    def UpdateSettings(self):
        if self.setting:
            if self._checked:
                self.setting.enable()
            else:
                self.setting.disable()
        elif self.settingsPath:
            self._ApplySettingOld(self._checked)

    def _ApplySettingOld(self, value):
        setting = GetAttrs(settings, *self.settingsPath)
        try:
            setting.Set(self.settingsKey, value)
        except:
            logger.error('Failed to assign setting to: %s, %s' % (self.settingsPath, self.settingsKey))

    def _GetSettingValue(self):
        return self.setting.is_enabled()

    def _GetIsCheckedSettingValue(self):
        return self._GetSettingValue()

    def ConstructCheckboxCont(self):
        if self.checkboxCont:
            self.checkboxCont.Close()
        diodeAlign = uiconst.TOPLEFT
        self.checkboxCont = Container(name='diode', parent=self, align=diodeAlign, state=uiconst.UI_DISABLED, pos=(0,
         (self.minHeight - self.DIODE_SIZE) / 2,
         16,
         16))
        self._ConstructCheckmark()

    def _ConstructCheckmark(self):
        self.checkMark = Sprite(name='self_ok', parent=self.checkboxCont, align=uiconst.CENTER, state=uiconst.UI_HIDDEN, pos=(0, 0, 16, 16), texturePath=self.checkedTexture)
        self.underlay = CheckboxUnderlay(parent=self.checkboxCont, enabled=self._enabled)

    def _update_checkmark_color(self):
        color = self.CHECK_MARK_COLOR_IDLE if self._enabled else self.CHECK_MARK_COLOR_DISABLED
        self.checkMark.SetRGBA(*color)

    def IsRightAligned(self):
        return self.GetAlign() in (uiconst.TOPRIGHT, uiconst.CENTERRIGHT)

    def SetChecked(self, isChecked, report = 1):
        isChecked = isChecked or 0
        self._checked = int(isChecked)
        self.checkMark.state = uiconst.UI_DISABLED if self._checked else uiconst.UI_HIDDEN
        if report:
            if isChecked:
                PlaySound(uiconst.SOUND_SETDESELECTED)
            else:
                PlaySound(uiconst.SOUND_SETSELECTED)
            self.UpdateSettings()
            self.OnChange()
        if isChecked:
            self.underlay.Select(animate=report)
        else:
            self.underlay.Deselect(animate=report)

    def OnChange(self):
        if self._callback:
            self._callback(self)

    def SetCallback(self, callback):
        self._callback = callback

    def SetLabel(self, labeltext):
        self.SetLabelText(labeltext)

    def GetTooltipPosition(self, *args, **kwds):
        l, t, w, h = self.GetAbsolute()
        label = self.label
        if label.text:
            return (l,
             t,
             label.padLeft + label.left + label.textwidth,
             h)
        else:
            return (l,
             t,
             w,
             h)

    def OnClick(self, *args):
        if not self.disabled:
            self.ToggleState()

    def OnMouseEnter(self, *args):
        self._hovered = True
        if self.disabled:
            return
        PlaySound(uiconst.SOUND_BUTTON_HOVER)
        self._update_label_color()
        if self.underlay:
            self.underlay.OnMouseEnter()

    def OnMouseExit(self, *args):
        self._hovered = False
        if self.disabled:
            return
        self._update_label_color()
        if self.underlay:
            self.underlay.OnMouseExit()

    def OnMouseDown(self, mouseBtn = None):
        if self.disabled or mouseBtn != uiconst.MOUSELEFT:
            return
        if self.underlay:
            self.underlay.OnMouseDown()

    def OnMouseUp(self, mouseBtn = None):
        super(Checkbox, self).OnMouseUp(mouseBtn)
        if self.disabled or mouseBtn != uiconst.MOUSELEFT:
            return
        if self.underlay:
            self.underlay.OnMouseUp()

    def UpdateAlignment(self, budgetLeft = 0, budgetTop = 0, budgetWidth = 0, budgetHeight = 0, updateChildrenOnly = False):
        budget = super(Checkbox, self).UpdateAlignment(budgetLeft, budgetTop, budgetWidth, budgetHeight, updateChildrenOnly)
        if self.align in uiconst.ALIGNMENTS_WITH_RELEVANT_WIDTH:
            self.label.clear_set_width()
        else:
            width, _ = self.GetCurrentAbsoluteSize()
            self.label.width = width - self.label.left
        measurer = self.label.measurer
        approximateGlyphHeight = int(math.ceil(9.0 / 13.0 * self.ReverseScaleDpi(measurer.fontSize)))
        glyphDistanceFromTop = self.ReverseScaleDpi(measurer.ascender) - approximateGlyphHeight
        self.label.top = round((self.minHeight - approximateGlyphHeight) / 2.0 - glyphDistanceFromTop)
        if self.label._alignmentDirty:
            size_changed = budget[4]
            budget = super(Checkbox, self).UpdateAlignment(budgetLeft, budgetTop, budgetWidth, budgetHeight, updateChildrenOnly=False)
            budget = budget[:4] + (size_changed or budget[4],)
        return budget


class CheckboxUnderlay(Container):
    UNDERLAY_OPACITY_NORMAL = 1.0
    UNDERLAY_OPACITY_DISABLED = 0.5

    def __init__(self, parent = None, bgParent = None, align = uiconst.TOALL, padding = 0, enabled = True):
        self._hover = None
        self._highlight = None
        self._underlay = None
        super(CheckboxUnderlay, self).__init__(parent=parent, bgParent=bgParent, align=align, padding=padding)
        self._hover = Frame(parent=self, align=uiconst.TOALL, texturePath='res:/UI/Texture/classes/checkbox/underlay_hover.png', color=eveThemeColor.THEME_FOCUS, outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, glowBrightness=0.3, cornerSize=8, opacity=0.0)
        self._highlight = Fill(parent=self, align=uiconst.TOALL, padding=1, opacity=0.0)
        self._underlay = Frame(parent=self, align=uiconst.TOALL, texturePath='res:/UI/Texture/classes/checkbox/underlay.png', cornerSize=3, opacity=self.UNDERLAY_OPACITY_NORMAL if enabled else self.UNDERLAY_OPACITY_DISABLED)

    def OnColorThemeChanged(self):
        super(CheckboxUnderlay, self).OnColorThemeChanged()
        self._hover.SetRGBA(*(eveThemeColor.THEME_FOCUS[:3] + (self._hover.opacity,)))

    def Enable(self):
        self._underlay.opacity = self.UNDERLAY_OPACITY_NORMAL

    def Disable(self):
        self._underlay.opacity = self.UNDERLAY_OPACITY_DISABLED

    def Select(self, animate = True):
        pass

    def Deselect(self, animate = True):
        pass

    def OnMouseEnter(self, *args):
        if self._hover is not None:
            animations.FadeIn(self._hover, duration=0.1)

    def OnMouseExit(self, *args):
        if self._hover is not None:
            animations.FadeOut(self._hover, duration=0.3)

    def OnMouseDown(self, *args):
        animations.FadeIn(self._highlight, duration=uiconst.TIME_ENTRY)

    def OnMouseUp(self, *args):
        animations.FadeOut(self._highlight, duration=uiconst.TIME_MOUSEUP)
