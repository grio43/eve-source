#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\control\label.py
import re
import sys
import types
import blue
import eveLocalization
import localization
import localization.settings
import log
import trinity
from carbon.client.script.environment.AudioUtil import PlaySound
from carbon.common.script.sys import serviceConst
from carbon.common.script.util import mathUtil
from carbon.common.script.util.commonutils import StripTags
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui import fontconst, uiconst
from carbonui.control.link import Link
from carbonui.primitives.base import ScaleDpi, ReverseScaleDpi
from carbonui.primitives.sprite import VisibleBase
from carbonui.text.const import TextAlign
from carbonui.text.settings import check_convert_font_size, font_shadow_enabled_setting
from carbonui.uicore import uicore
from carbonui.util import colorblind
from carbonui.util.bunch import Bunch
from carbonui.util.stringManip import GetAsUnicode
from carbonui.util.various_unsorted import StringColorToHex
from localization.pseudoloc import Pseudolocalize
from menu import MenuLabel
COLORBLIND_MAX_SATURATION = None
layoutCountStat = blue.statistics.Find('CarbonUI/labelLayout')
if not layoutCountStat:
    layoutCountStat = blue.CcpStatisticsEntry()
    layoutCountStat.name = 'CarbonUI/labelLayout'
    layoutCountStat.type = 1
    layoutCountStat.resetPerFrame = True
    layoutCountStat.description = 'The number of calls to LabelCore.Layout per frame'
    blue.statistics.Register(layoutCountStat)
ELLIPSIS = u'\u2026'
SINGLE_LINE_NEWLINE_PATTERN = re.compile('<br>|\r\n|\n')
STOPWRAP = -1
COLOR_WHITE_FULLALPHA = -1

class LabelCore(VisibleBase):
    __renderObject__ = trinity.Tr2Sprite2dTextObject
    isDragObject = True
    busy = False
    linespace = 0
    default_name = 'label'
    default_state = uiconst.UI_DISABLED
    default_fontsize = None
    default_fontStyle = None
    default_fontFamily = None
    default_fontPath = None
    default_linkStyle = uiconst.LINKSTYLE_SUBTLE
    default_textAlign = TextAlign.LEFT
    default_spriteEffect = trinity.TR2_SFX_FONT
    default_color = None
    default_text = ''
    default_tabs = []
    default_tabMargin = uiconst.LABELTABMARGIN
    default_uppercase = False
    default_maxLines = None
    default_maxFontSize = None
    default_wrapMode = uiconst.WRAPMODE_FORCEWORD
    default_lineSpacing = fontconst.DEFAULT_LINESPACING
    default_letterspace = 0
    default_underline = 0
    default_bold = 0
    default_italic = 0
    default_specialIndent = 0
    default_autoDetectCharset = False
    default_showEllipsis = False
    default_autoUpdate = True
    default_shadowOffset = (0, 0)
    default_shadowColor = (0, 0, 0, 0.5)
    default_shadowSpriteEffect = None
    _underline = default_underline
    _bold = default_bold
    _italic = default_italic
    _uppercase = default_uppercase
    _letterspace = default_letterspace
    _lineSpacing = default_lineSpacing
    _wrapMode = default_wrapMode
    _maxLines = default_maxLines
    _tabs = default_tabs
    _setWidth = 0
    _setHeight = 0
    _minCursor = 0
    _shadowOffset = (0, 0)
    _alphaFadeLeft = None
    _alphaFadeRight = None
    _alphaFadeBottom = None
    _fontStyle = default_fontStyle
    _fontPath = default_fontPath
    _fontFamily = default_fontFamily
    _fontsize = default_fontsize
    _setText = ''
    _localizationText = None
    _parseDirty = False
    _layoutDirty = False
    _inlineObjects = None
    _inlineObjectsBuff = None
    _measurerProperties = None
    _lastAddTextData = None
    actualTextHeight = 0
    actualTextWidth = 0
    localizationWrapOn = False
    tooltipPosition = None
    auxTooltipPosition = None
    autoFitToText = False
    autoFadeSides = False
    _resolvingAutoSizing = False
    _hilite = 0
    _mouseOverUrl = None
    _mouseOverUrlID = None
    _mouseOverTextBuff = None
    _lastAbs = None
    _clipWidth = None
    _clipHeight = None
    autoUpdate = None
    _colorInt = -1
    _offer_auxiliary_copy_option = True
    _raw_fontsize = None
    _using_default_shadow = True

    def __init__(self, autoFadeSides = False, shadowOffset = None, **kwargs):
        self.autoFadeSides = autoFadeSides
        if shadowOffset is None:
            shadowOffset = self.get_default_shadow_offset()
        super(LabelCore, self).__init__(shadowOffset=shadowOffset, **kwargs)

    def ApplyAttributes(self, attributes):
        self.busy = True
        VisibleBase.ApplyAttributes(self, attributes)
        if self.default_fontsize is None:
            self.default_fontsize = fontconst.DEFAULT_FONTSIZE
        self.collectWordsInStack = attributes.get('collectWordsInStack', False)
        self.mouseOverWordCallback = attributes.get('mouseOverWordCallback', None)
        self.autoFitToText = attributes.get('autoFitToText', False)
        self.InitMeasurer()
        if self.align != uiconst.TOALL:
            self._setWidth = self.width
            self._setHeight = self.height
        self._textAlign = attributes.get('textAlign', self.default_textAlign)
        self._fontsize = None
        self._clipWidth = attributes.get('clipWidth', self._clipWidth)
        self._clipHeight = attributes.get('clipHeight', self._clipHeight)
        self.InitLocalizationFlag()
        self._tabMargin = attributes.get('tabMargin', self.default_tabMargin)
        self.shadowSpriteEffect = attributes.get('shadowSpriteEffect', self.default_shadowSpriteEffect)
        self.shadowOffset = attributes.get('shadowOffset', self.default_shadowOffset)
        self.shadowColor = attributes.get('shadowColor', self.default_shadowColor)
        self.autoUpdate = attributes.get('autoUpdate', self.default_autoUpdate)
        self.tabs = attributes.get('tabs', self.default_tabs)
        self.fontStyle = attributes.get('fontStyle', self.default_fontStyle)
        self.fontFamily = attributes.get('fontFamily', self.default_fontFamily)
        self.fontPath = attributes.get('fontPath', self.default_fontPath)
        if not self.fontPath and not self.fontFamily:
            self.fontFamily = uicore.font.GetFontFamilyBasedOnClientLanguageID()
        self.linkStyle = attributes.get('linkStyle', self.default_linkStyle)
        self._maxFontSize = attributes.get('maxFontSize', self.default_maxFontSize)
        self.fontsize = attributes.get('fontsize', self.default_fontsize)
        self.underline = attributes.get('underline', self.default_underline)
        self.bold = attributes.get('bold', self.default_bold)
        self.italic = attributes.get('italic', self.default_italic)
        self.uppercase = attributes.get('uppercase', self.default_uppercase)
        self.wrapMode = attributes.get('wrapMode', self.default_wrapMode)
        self.showEllipsis = attributes.get('showEllipsis', self.default_showEllipsis)
        self.lineSpacing = attributes.get('lineSpacing', self.default_lineSpacing)
        self.letterspace = attributes.get('letterspace', self.default_letterspace)
        self.specialIndent = attributes.get('specialIndent', self.default_specialIndent)
        self.autoDetectCharset = attributes.get('autoDetectCharset', self.default_autoDetectCharset)
        if not attributes.get('offer_auxiliary_copy_option', True):
            self._offer_auxiliary_copy_option = False
        if attributes.get('singleline', False):
            maxLines = 1
        else:
            maxLines = attributes.get('maxLines', self.default_maxLines)
        self.maxLines = maxLines
        self._measuringText = attributes.get('measuringText', False)
        self.busy = False
        self.text = attributes.get('text', self.default_text)

    @classmethod
    def get_default_shadow_offset(cls):
        if font_shadow_enabled_setting.is_enabled():
            return cls.default_shadowOffset
        else:
            return (0, 0)

    def InitMeasurer(self):
        self.measurer = trinity.Tr2FontMeasurer()
        self.renderObject.fontMeasurer = self.measurer

    def InitLocalizationFlag(self):
        self.localizationWrapOn = localization.settings.qaSettings.LocWrapSettingsActive()

    def Close(self):
        self._inlineObjects = None
        self._inlineObjectsBuff = None
        self._hiliteResetTimer = None
        if self.renderObject:
            self.renderObject.fontMeasurer = None
        self.measurer = None
        VisibleBase.Close(self)

    def UpdateUIScaling(self, *args):
        if self.destroyed or self.measurer is None:
            return
        self.measurer.fontSize = 0
        self.Layout('OnUIScalingChange')

    def ResolveAutoSizing(self):
        self._resolvingAutoSizing = True
        if self.autoFitToText:
            setWidth = None
            setHeight = None
        else:
            setWidth = self._setWidth
            setHeight = self._setHeight
        if self.clipWidth:
            setWidth = self.clipWidth
        if self.clipHeight:
            setHeight = self.clipHeight
        align = self.align
        width = 0
        height = 0
        if align in uiconst.ALIGNMENTS_WITH_RELEVANT_WIDTH:
            width += setWidth or self.textwidth
        if align in uiconst.ALIGNMENTS_WITH_INCLUDED_HORIZONTAL_PADDING:
            width += self.padLeft + self.padRight
        if align in uiconst.ALIGNMENTS_WITH_RELEVANT_HEIGHT:
            height += setHeight or self.textheight
        if align in uiconst.ALIGNMENTS_WITH_INCLUDED_VERTICAL_PADDING:
            height += self.padTop + self.padBottom
        self.width = width
        self.height = height
        self._resolvingAutoSizing = False

    def SetLeftAlphaFade(self, fadeStart = 0, maxFadeWidth = 0):
        if maxFadeWidth:
            self._alphaFadeLeft = (fadeStart, maxFadeWidth)
            self._UpdateAlphaFade()
        else:
            self._alphaFadeLeft = None
            measurer = self.measurer
            if measurer:
                measurer.fadeLeftStart = 0
                measurer.fadeLeftEnd = 0

    def SetRightAlphaFade(self, fadeEnd = 0, maxFadeWidth = 0):
        if maxFadeWidth:
            self._alphaFadeRight = (fadeEnd, maxFadeWidth)
            self._UpdateAlphaFade()
        else:
            self._alphaFadeRight = None
            measurer = self.measurer
            if measurer:
                measurer.fadeRightStart = sys.maxint
                measurer.fadeRightEnd = sys.maxint

    def SetBottomAlphaFade(self, fadeEnd = 0, maxFadeHeight = 0):
        if maxFadeHeight:
            self._alphaFadeBottom = (fadeEnd, maxFadeHeight)
            self._UpdateAlphaFade()
        else:
            self._alphaFadeBottom = None
            measurer = self.measurer
            if measurer:
                measurer.fadeBottomStart = sys.maxint
                measurer.fadeBottomEnd = sys.maxint

    def _UpdateAlphaFade(self):
        measurer = self.measurer
        if not measurer:
            return
        if self._alphaFadeLeft:
            fadeStart, length = self._alphaFadeLeft
            fadeStart = ScaleDpi(fadeStart - 0.5)
            length = ScaleDpi(length)
            measurer.fadeLeftStart = fadeStart
            measurer.fadeLeftEnd = fadeStart + length
        if self._alphaFadeRight:
            fadeEnd, length = self._alphaFadeRight
            if self.textwidth > fadeEnd:
                diff = self.textwidth - fadeEnd
                length = ScaleDpi(min(length, diff))
                fadeEnd = ScaleDpi(fadeEnd - 0.5)
                measurer.fadeRightStart = max(0, fadeEnd - length)
                measurer.fadeRightEnd = fadeEnd
            else:
                measurer.fadeRightStart = sys.maxint
                measurer.fadeRightEnd = sys.maxint
        if self._alphaFadeBottom:
            fadeEnd, length = self._alphaFadeBottom
            if self.textheight > fadeEnd:
                diff = self.textheight - fadeEnd
                length = ScaleDpi(min(length, diff))
                fadeEnd = ScaleDpi(fadeEnd - 0.5)
                measurer.fadeBottomStart = max(0, fadeEnd - length)
                measurer.fadeBottomEnd = fadeEnd
            else:
                measurer.fadeBottomStart = sys.maxint
                measurer.fadeBottomEnd = sys.maxint

    @property
    def fontsize(self):
        return self._fontsize

    @fontsize.setter
    def fontsize(self, value):
        converted_value = check_convert_font_size(value)
        if self._maxFontSize:
            converted_value = min(converted_value, self._maxFontSize)
        if converted_value != value:
            self._raw_fontsize = value
        self.SetLayoutTriggerProperty('fontsize', converted_value)

    @property
    def mincommitcursor(self):
        if uicore.desktop.dpiScaling != 1.0:
            return ReverseScaleDpi(self._minCursor + 0.5)
        else:
            return self._minCursor

    @property
    def textwidth(self):
        if uicore.desktop.dpiScaling != 1.0:
            return ReverseScaleDpi(self.actualTextWidth + 0.5)
        else:
            return self.actualTextWidth

    @property
    def textheight(self):
        if uicore.desktop.dpiScaling != 1.0:
            return ReverseScaleDpi(self.actualTextHeight + 0.5)
        else:
            return self.actualTextHeight

    @VisibleBase.displayRect.setter
    def displayRect(self, value):
        VisibleBase.displayRect.fset(self, value)
        ro = self.renderObject
        if ro:
            if self.clipWidth:
                ro.textWidth = ScaleDpi(self.clipWidth)
            else:
                ro.textWidth = ro.displayWidth
            if self.clipHeight:
                ro.textHeight = ScaleDpi(self.clipHeight)
            else:
                ro.textHeight = ro.displayHeight

    @VisibleBase.width.setter
    def width(self, value):
        VisibleBase.width.fset(self, value)
        if not getattr(self, '_resolvingAutoSizing', False) and self.align != uiconst.TOALL:
            if value != self._setWidth:
                self._layoutDirty = True
            self._setWidth = value
            if getattr(self, 'autoUpdate', False) and not self.isAffectedByPushAlignment:
                self.Layout('width')

    def clear_set_width(self):
        if self._setWidth is not None:
            self._setWidth = None
            self._layoutDirty = True
            if getattr(self, 'autoUpdate', False) and not self.isAffectedByPushAlignment:
                self.Layout('clear_set_width')

    @VisibleBase.height.setter
    def height(self, value):
        VisibleBase.height.fset(self, value)
        if not getattr(self, '_resolvingAutoSizing', False) and self.align != uiconst.TOALL:
            self._setHeight = value
            if getattr(self, 'autoUpdate', False) and not self.busy and not self.isAffectedByPushAlignment:
                self.Layout('height')

    @VisibleBase.padding.setter
    def padding(self, value):
        if isinstance(value, (tuple, list)):
            padLeft, padTop, padRight, padBottom = value
        else:
            padLeft = padTop = padRight = padBottom = value
        need_to_update_size = self._padLeft != padLeft or self._padTop != padTop or self._padRight != padRight or self._padBottom != padBottom
        VisibleBase.padding.fset(self, value)
        if need_to_update_size and not self._resolvingAutoSizing and not self.busy:
            self.ResolveAutoSizing()

    @VisibleBase.padLeft.setter
    def padLeft(self, value):
        need_to_update_size = self._padLeft != value
        VisibleBase.padLeft.fset(self, value)
        if need_to_update_size and not self._resolvingAutoSizing and not self.busy:
            self.ResolveAutoSizing()

    @VisibleBase.padTop.setter
    def padTop(self, value):
        need_to_update_size = self._padTop != value
        VisibleBase.padTop.fset(self, value)
        if need_to_update_size and not self._resolvingAutoSizing and not self.busy:
            self.ResolveAutoSizing()

    @VisibleBase.padRight.setter
    def padRight(self, value):
        need_to_update_size = self._padRight != value
        VisibleBase.padRight.fset(self, value)
        if need_to_update_size and not self._resolvingAutoSizing and not self.busy:
            self.ResolveAutoSizing()

    @VisibleBase.padBottom.setter
    def padBottom(self, value):
        need_to_update_size = self._padBottom != value
        VisibleBase.padBottom.fset(self, value)
        if need_to_update_size and not self._resolvingAutoSizing and not self.busy:
            self.ResolveAutoSizing()

    @property
    def clipWidth(self):
        return self._clipWidth

    @clipWidth.setter
    def clipWidth(self, value):
        self._clipWidth = value
        self.ResolveAutoSizing()

    @property
    def clipHeight(self):
        return self._clipHeight

    @clipHeight.setter
    def clipHeight(self, value):
        self._clipHeight = value
        self.ResolveAutoSizing()

    @property
    def hint(self):
        return getattr(self, '_hint', None)

    @hint.setter
    def hint(self, value):
        if not getattr(self, '_resolvingInlineHint', False):
            self._objectHint = value
        else:
            VisibleBase.hint.fset(self, value)

    @property
    def shadowSpriteEffect(self):
        return self._shadowSpriteEffect

    @shadowSpriteEffect.setter
    def shadowSpriteEffect(self, value):
        self._shadowSpriteEffect = value
        if self.renderObject:
            if self._shadowSpriteEffect is None:
                self.renderObject.useShadowSpriteEffect = False
            else:
                self.renderObject.useShadowSpriteEffect = True
                self.renderObject.shadowSpriteEffect = self._shadowSpriteEffect

    @property
    def shadowOffset(self):
        return self._shadowOffset

    @shadowOffset.setter
    def shadowOffset(self, value):
        if self._using_default_shadow and value != self.get_default_shadow_offset():
            self._using_default_shadow = False
        self._shadowOffset = value
        ro = self.renderObject
        if ro:
            ro.shadowOffset = value

    @property
    def shadowColor(self):
        return self._shadowColor

    @shadowColor.setter
    def shadowColor(self, value):
        self._shadowColor = value
        ro = self.renderObject
        if ro:
            ro.shadowColor = value

    def SetAlign(self, align):
        if self.align != align:
            layout_dirty = uiconst.is_push_alignment(self.align) != uiconst.is_push_alignment(align) or uiconst.is_affected_by_push_alignment(self.align) != uiconst.is_affected_by_push_alignment(align)
            super(LabelCore, self).SetAlign(align)
            if layout_dirty:
                self._layoutDirty = layout_dirty
                if self.autoUpdate and not self.busy:
                    self.Layout('align')

    def SetText(self, text):
        if self.localizationWrapOn:
            if self._localizationText == text:
                return
            self._localizationText = text
        if self._setText != text:
            self._parseDirty = True
            if self.localizationWrapOn and isinstance(text, basestring):
                if localization.settings.qaSettings.PseudolocSettingsActive() and localization.uiutil.IsLocalizationSafeString(text):
                    text = Pseudolocalize(text)
                try:
                    text = localization.uiutil.WrapStringForDisplay(text)
                except Exception:
                    pass

            self._setText = text
            if self.autoUpdate:
                self.Layout('SetText')

    def GetText(self):
        return self._setText

    text = property(GetText, SetText)

    def SetTextAlign(self, align):
        self._textAlign = align
        if self.autoUpdate:
            self.Layout('SetTextAlign')

    @property
    def singleline(self):
        return self.maxLines == 1

    @singleline.setter
    def singleline(self, value):
        if value:
            self.maxLines = 1
        else:
            self.maxLines = None

    def GetProperty(self, propertyName):
        return getattr(self, '_' + propertyName)

    def SetLayoutTriggerProperty(self, propertyName, value):
        if getattr(self, '_' + propertyName) != value:
            setattr(self, '_' + propertyName, value)
            self._layoutDirty = True
            if self.autoUpdate and not self.busy:
                self.Layout(propertyName)

    fontStyle = property(lambda self: self.GetProperty('fontStyle'), lambda self, value: self.SetLayoutTriggerProperty('fontStyle', value))
    fontFamily = property(lambda self: self.GetProperty('fontFamily'), lambda self, value: self.SetLayoutTriggerProperty('fontFamily', value))
    fontPath = property(lambda self: self.GetProperty('fontPath'), lambda self, value: self.SetLayoutTriggerProperty('fontPath', value))
    letterspace = property(lambda self: self.GetProperty('letterspace'), lambda self, value: self.SetLayoutTriggerProperty('letterspace', value))
    wrapMode = property(lambda self: self.GetProperty('wrapMode'), lambda self, value: self.SetLayoutTriggerProperty('wrapMode', value))
    uppercase = property(lambda self: self.GetProperty('uppercase'), lambda self, value: self.SetLayoutTriggerProperty('uppercase', value))
    lineSpacing = property(lambda self: self.GetProperty('lineSpacing'), lambda self, value: self.SetLayoutTriggerProperty('lineSpacing', value))
    underline = property(lambda self: self.GetProperty('underline'), lambda self, value: self.SetLayoutTriggerProperty('underline', value))
    bold = property(lambda self: self.GetProperty('bold'), lambda self, value: self.SetLayoutTriggerProperty('bold', value))
    italic = property(lambda self: self.GetProperty('italic'), lambda self, value: self.SetLayoutTriggerProperty('italic', value))
    maxLines = property(lambda self: self.GetProperty('maxLines'), lambda self, value: self.SetLayoutTriggerProperty('maxLines', value))
    tabs = property(lambda self: self.GetProperty('tabs'), lambda self, value: self.SetLayoutTriggerProperty('tabs', value))

    def SetTextColor(self, color):
        self.SetRGBA(*color)

    def _ApplyColor(self):
        ro = self.renderObject
        if ro and self._color:
            renderObjectOpacity = max(1.0, self._color.a)
            ro.color = (ro.color[0],
             ro.color[1],
             ro.color[2],
             renderObjectOpacity)
            if self.color.GetBrightness() < 0.2:
                self.renderObject.spriteEffect = trinity.TR2_SFX_COPY
            else:
                self.renderObject.spriteEffect = trinity.TR2_SFX_FONT
        colorInt = self._GetColorAsInt()
        if colorInt == self._colorInt:
            return
        self._colorInt = colorInt
        if self.autoUpdate and not self.busy:
            self.Layout('SetTextColor')

    def _GetColorAsInt(self):
        color = self.GetRGBA()
        tricolor = trinity.TriColor()
        tricolor.SetRGB(*color)
        if len(color) != 4:
            tricolor.a = 1.0
        return tricolor.AsInt()

    SetDefaultColor = SetTextColor

    def SetTabMargin(self, margin, refresh = 1):
        self._tabMargin = margin
        if refresh:
            self.Layout('SetTabMargin')

    def GetTab(self, idx, right = None):
        if len(self.tabs) > idx:
            return self.tabs[idx]
        if right is not None:
            return right

    def Update(self):
        if self._parseDirty or self._layoutDirty:
            self.Layout()

    def Layout(self, hint = 'None', absSize = None):
        if getattr(self, 'busy', 0):
            return
        self.busy = True
        try:
            self._Layout(hint, absSize)
        finally:
            self.busy = False

    def _Layout(self, hint, absSize):
        layoutCountStat.Inc()
        self._layoutDirty = False
        if self.measurer:
            self.measurer.Reset()
        self.actualTextWidth = 0
        self.actualTextHeight = 0
        text = self.text
        if text is None or isinstance(text, basestring) and not text:
            return
        self._urlIDCounter = 0
        if self._parseDirty:
            textToParse = GetAsUnicode(text)
            if self.maxLines == 1:
                textToParse = SINGLE_LINE_NEWLINE_PATTERN.sub(' ', textToParse)
            parsePrepared = trinity.ParseLabelText(textToParse)
            self._parsePrepared = parsePrepared
            self._parseDirty = False
        else:
            parsePrepared = self._parsePrepared
        availableWidth = self._GetAvailableWidth(absSize)
        self._minCursor = None
        self.ResetTagStack()
        self._lastAddTextData = []
        self._inlineObjects = None
        self._inlineObjectsBuff = None
        vScrollshiftX = getattr(self, 'xShift', 0)
        margin = self._tabMargin
        self._numLines = 0
        self._commitCursorYScaled = 0
        self._currTextAlign = self._textAlign
        self._canPushText = True
        maxLines = self.maxLines
        for lineData in parsePrepared:
            left = 0
            isTabbed = len(lineData) > 1
            lineStartCursorYScaled = self._commitCursorYScaled
            lineMaxCommitCursorYScaled = lineStartCursorYScaled
            for tabIndex, tabData in enumerate(lineData):
                self._commitCursorYScaled = lineStartCursorYScaled
                if self.measurer:
                    self.measurer.font = ''
                else:
                    return
                if isTabbed:
                    self._currTextAlign = TextAlign.LEFT
                    self._canPushText = True
                    if availableWidth is None:
                        availableWidth = uicore.desktop.width
                    right = self.GetTab(tabIndex, availableWidth) - margin
                    wrapWidth = right + vScrollshiftX - left
                else:
                    wrapWidth = availableWidth
                self.ProcessLineData(tabData, left, wrapWidth)
                if self._lastAddTextData:
                    self.CommitBuffer(doLineBreak=True)
                    if maxLines and self._numLines >= maxLines:
                        self._canPushText = False
                if isTabbed:
                    left = right + margin * 2 + vScrollshiftX
                lineMaxCommitCursorYScaled = max(lineMaxCommitCursorYScaled, self._commitCursorYScaled)

            self._commitCursorYScaled = lineStartCursorYScaled + (lineMaxCommitCursorYScaled - lineStartCursorYScaled)

        if not self._measuringText:
            self.ResolveAutoSizing()
            self._UpdateAlphaFade()

    def _GetAvailableWidth(self, absSize):
        if not self.isAffectedByPushAlignment:
            if self._setWidth:
                availableWidth = self._setWidth
            else:
                availableWidth = self.maxWidth
        elif absSize:
            availableWidth, _ = absSize
        elif self.align not in uiconst.ALIGNMENTS_WITH_RELEVANT_WIDTH:
            availableWidth, _ = self.GetAbsoluteSize()
        else:
            availableWidth = None
        return availableWidth

    def ResetTagStack(self):
        self._tagStack = {'font': [],
         'file': [],
         'fontsize': [self.fontsize],
         'color': [self._colorInt],
         'letterspace': [self.letterspace],
         'hint': [],
         'link': [],
         'localized': [],
         'localizedQA': [],
         'u': self.underline,
         'b': self.bold,
         'i': self.italic,
         'uppercase': self.uppercase}

    @property
    def maxWidth(self):
        if self._maxWidth is not None:
            return self._maxWidth
        try:
            return trinity.adapters.GetMaxTextureSize(trinity.device.adapter)
        except:
            return 0

    @maxWidth.setter
    def maxWidth(self, width):
        self._maxWidth = width
        self.Layout('maxWidth')

    def PushText(self, text, measurer, oneLiner, wrapModeForceAll, maxLines):
        if not measurer:
            return STOPWRAP
        textAdded = measurer.AddText(text)
        if textAdded >= len(text):
            self._lastAddTextData.append((text, self._measurerProperties))
            return
        if oneLiner:
            if self.showEllipsis:
                sliceBack = 0
                while textAdded > sliceBack:
                    tryFit = text[:textAdded - sliceBack] + ELLIPSIS
                    measurer.CancelLastText()
                    ellipsisFit = measurer.AddText(tryFit)
                    if ellipsisFit == len(tryFit):
                        break
                    sliceBack += 1

            self.CommitBuffer()
            return STOPWRAP
        measurer.CancelLastText()
        hasData = bool(self._lastAddTextData)
        if not hasData:
            if textAdded == 0:
                return STOPWRAP
        if not wrapModeForceAll:
            wrapPointInText = self.FindWrapPointInText(text, textAdded)
            if wrapPointInText is not None:
                textAdded = wrapPointInText
            elif hasData:
                lastText, lastMeasurerProperties = self._lastAddTextData[-1]
                wpl = eveLocalization.WrapPointList(lastText + text, session.languageID)
                combinedResult = wpl.GetLinebreakPoints()
                if len(lastText) in combinedResult:
                    self.CommitBuffer(doLineBreak=True)
                    if maxLines and self._numLines >= maxLines:
                        return STOPWRAP
                    return self.PushText(text, measurer, oneLiner, wrapModeForceAll, maxLines)
                lineText = u''.join([ addedData[0] for addedData in self._lastAddTextData ])
                wpl = eveLocalization.WrapPointList(lineText, session.languageID)
                lineWrapPoints = wpl.GetLinebreakPoints()
                if lineWrapPoints:
                    linePos = len(lineText)
                    moveToNextLine = []
                    breakAt = lineWrapPoints[-1]
                    while self._lastAddTextData:
                        addedData = self._lastAddTextData.pop()
                        addedText, addedMeasurerProperties = addedData
                        addedTextLength = len(addedText)
                        addedTextPos = linePos - addedTextLength
                        measurer.CancelLastText()
                        if addedTextPos <= breakAt <= linePos:
                            self.SetMeasurerProperties(*addedMeasurerProperties)
                            measurer.AddText(addedText[:breakAt - addedTextPos])
                            self._lastAddTextData.append((addedText[:breakAt - addedTextPos], addedMeasurerProperties))
                            rest = addedText[breakAt - addedTextPos:]
                            if rest:
                                moveToNextLine.insert(0, (rest, addedMeasurerProperties))
                            break
                        else:
                            moveToNextLine.insert(0, addedData)
                        linePos -= addedTextLength

                    self.CommitBuffer(doLineBreak=True)
                    if maxLines and self._numLines >= maxLines:
                        return STOPWRAP
                    for nextLineData in moveToNextLine:
                        addedText, addedMeasurerProperties = nextLineData
                        self.SetMeasurerProperties(*addedMeasurerProperties)
                        measurer.AddText(addedText)
                        self._lastAddTextData.append(nextLineData)

                    self.SetMeasurerProperties(*self._measurerProperties)
                    return self.PushText(text, measurer, oneLiner, wrapModeForceAll, maxLines)
        textSlice = text[:textAdded]
        measurer.AddText(textSlice)
        self._lastAddTextData.append((textSlice, self._measurerProperties))
        self.CommitBuffer(doLineBreak=True)
        if maxLines and self._numLines >= maxLines:
            return STOPWRAP
        moveToNext = text[textAdded:]
        return self.PushText(moveToNext, measurer, oneLiner, wrapModeForceAll, maxLines)

    def SetMeasurerProperties(self, fontsize, color, letterspace, underline, fontPath, register = False):
        measurer = self.measurer
        if not measurer:
            return
        measurer.fontSize = fontsize
        try:
            measurer.color = color
        except TypeError as err:
            log.LogError('Invalid color passed to text renderer, error: %s, color: %s' % (err, color))
            measurer.color = COLOR_WHITE_FULLALPHA

        measurer.letterSpace = letterspace
        measurer.underline = underline
        if fontPath is not None:
            measurer.font = str(fontPath)
        else:
            measurer.font = ''
        if register:
            self._measurerProperties = (fontsize,
             color,
             letterspace,
             underline,
             fontPath)

    def ProcessLineData(self, lineData, left, wrapWidth):
        if wrapWidth is not None:
            self._wrapWidthScaled = ScaleDpi(wrapWidth)
        else:
            self._wrapWidthScaled = None
        self._commitCursorXScaled = ScaleDpi(left)
        measurer = self.measurer
        if not measurer:
            return False
        measurer.limit = self._wrapWidthScaled or 0
        measurer.cursorX = 0
        setHeight = self._setHeight
        maxLines = self.maxLines
        oneLiner = maxLines == 1
        wrapMode = self.wrapMode
        wrapModeForceAll = wrapMode == uiconst.WRAPMODE_FORCEALL
        tagStackDirty = True
        tagStack = self._tagStack
        thereWasText = False
        for element in lineData:
            type = element[0]
            if type == 0:
                text = element[1]
                if text:
                    thereWasText = True
                    if getattr(self, 'collectWordsInStack', False):
                        textList = re.split('([\\W]+)', text)
                        for eachWord in textList:
                            if eachWord != ' ':
                                tagStackDirty = self.ParseWordTag(eachWord) or tagStackDirty
                            tagStackDirty = self.DoTextPushing(tagStackDirty, measurer, tagStack, eachWord, oneLiner, wrapModeForceAll, maxLines)
                            if eachWord != ' ':
                                tagStackDirty = self.ParseWordClose() or tagStackDirty

                    else:
                        tagStackDirty = self.DoTextPushing(tagStackDirty, measurer, tagStack, text, oneLiner, wrapModeForceAll, maxLines)
                    linkStack = tagStack.get('link', None)
                    if linkStack:
                        linkStack[-1].textBuff.append(text)
            elif type == 1:
                tagStackDirty = self.tagIDToFunctionMapping[element[1]][0](self, element[2]) or tagStackDirty
            elif type == 2:
                tagStackDirty = self.tagIDToFunctionMapping[element[1]][1](self) or tagStackDirty
            elif type == 3:
                if element[1] != 'loc' and session.role & serviceConst.ROLE_PROGRAMMER:
                    log.LogWarn("Unknown tag '%s' in %s" % (element[1], lineData))
            else:
                log.LogError('Unknown element type ID in ProcessLineData', type)

        if not thereWasText:
            if tagStackDirty:
                self.UpdateMeasurerProperties(measurer, tagStack, u' ')
                tagStackDirty = False
            ret = self.PushText(u' ', measurer, oneLiner, wrapModeForceAll, maxLines)
        return tagStackDirty

    def DoTextPushing(self, tagStackDirty, measurer, tagStack, myText, oneLiner, wrapModeForceAll, maxLines):
        if tagStackDirty:
            self.UpdateMeasurerProperties(measurer, tagStack, myText)
            tagStackDirty = False
        if self._canPushText:
            if tagStack['uppercase']:
                myText = localization.util.UpperCase(myText)
            ret = self.PushText(myText, measurer, oneLiner, wrapModeForceAll, maxLines)
            if ret == STOPWRAP:
                self._canPushText = False
        return tagStackDirty

    def FindWrapPointInText(self, text, fromIndex):
        space = u' '
        if text[fromIndex] != space and text[fromIndex - 1] == space:
            return fromIndex
        totalLength = len(text)
        if text[fromIndex] == space:
            spaceIndex = fromIndex
            while spaceIndex < totalLength:
                if text[spaceIndex] != space:
                    break
                spaceIndex += 1

            return spaceIndex
        wpl = eveLocalization.WrapPointList(unicode(text), session.languageID)
        result = wpl.GetLinebreakPoints()
        if result:
            retIndex = [ each for each in result if each <= fromIndex ]
            if retIndex:
                return retIndex[-1]

    def UpdateMeasurerProperties(self, measurer, tagStack, words):
        fontsize = ScaleDpi(tagStack['fontsize'][-1])
        color = tagStack['color'][-1]
        letterspace = tagStack['letterspace'][-1]
        underline = bool(tagStack['u'])
        italic = bool(tagStack['i'])
        bold = bool(tagStack['b'])
        try:
            fontPath = 'res:/UI/Fonts/%s' % tagStack['file'][-1]
            if not blue.paths.exists(fontPath):
                log.LogWarn('Font file not found:', fontPath)
                fontPath = self.fontPath
        except IndexError:
            fontPath = self.fontPath

        fontFamily = self.fontFamily
        if fontPath is None:
            if self.autoDetectCharset:
                windowsLanguageID = uicore.font.GetWindowsLanguageIDForText(words)
                if windowsLanguageID:
                    fontFamily = uicore.font.GetFontFamilyBasedOnWindowsLanguageID(windowsLanguageID)
            fontPath = uicore.font.GetFontPathFromFontFamily(fontFamily, self.fontStyle, bold, italic)
        if self.localizationWrapOn and localization.settings.qaSettings.GetValue('showHardcodedStrings'):
            if not tagStack['localizedQA']:
                color = localization.uiutil.COLOR_HARDCODED
        self.SetMeasurerProperties(fontsize, color, letterspace, underline, fontPath, register=True)

    def GetIndexUnderPos(self, layoutPosition):
        index = self.measurer.GetIndexAtPos(ScaleDpi(layoutPosition))
        width = ReverseScaleDpi(self.measurer.GetWidthAtIndex(index))
        return (index, width)

    def GetWidthToIndex(self, index):
        if self.destroyed:
            return
        if index == -1:
            maxLength = len(StripTags(self.text))
            index = maxLength
        width = ReverseScaleDpi(self.measurer.GetWidthAtIndex(index))
        return (index, width)

    def CommitBuffer(self, doLineBreak = False):
        measurer = self.measurer
        if not measurer:
            return
        buffWidth = measurer.cursorX
        cursorX = self._commitCursorXScaled
        textAlign = self._currTextAlign
        if textAlign != TextAlign.LEFT:
            lastAddTextData = self._lastAddTextData
            while lastAddTextData:
                lastAddData = lastAddTextData.pop()
                lastText, lastMeasurerProperties = lastAddData
                if not lastText:
                    measurer.CancelLastText()
                    continue
                lastTextStriped = lastText.rstrip()
                if lastText != lastTextStriped:
                    measurer.CancelLastText()
                    self.SetMeasurerProperties(*lastMeasurerProperties)
                    measurer.AddText(lastTextStriped)
                    buffWidth = measurer.cursorX
                break

            if textAlign == TextAlign.RIGHT:
                if self._wrapWidthScaled is None:
                    absWidth, _ = self.GetAbsoluteSize()
                    self._wrapWidthScaled = ScaleDpi(absWidth)
                cursorX += self._wrapWidthScaled - buffWidth
            elif textAlign == TextAlign.CENTER:
                if self._wrapWidthScaled is None:
                    absWidth, _ = self.GetAbsoluteSize()
                    self._wrapWidthScaled = ScaleDpi(absWidth)
                cursorX += int((self._wrapWidthScaled - buffWidth) / 2)
        lineHeight = measurer.ascender - measurer.descender
        lineSpacing = int(self.lineSpacing * lineHeight)
        moveToNextLine = []
        if self._inlineObjectsBuff:
            for object in self._inlineObjectsBuff:
                registerObject = object.Copy()
                if object.inlineXEnd is None:
                    object.inlineX = 0
                    moveToNextLine.append(object)
                    registerObject.inlineXEnd = ReverseScaleDpi(measurer.cursorX)
                registerObject.inlineX += ReverseScaleDpi(cursorX)
                registerObject.inlineXEnd += ReverseScaleDpi(cursorX)
                registerObject.inlineY = ReverseScaleDpi(self._commitCursorYScaled)
                registerObject.inlineHeight = ReverseScaleDpi(lineHeight + lineSpacing)
                if self._inlineObjects is None:
                    self._inlineObjects = []
                self._inlineObjects.append(registerObject)

        measurer.CommitText(cursorX, self._commitCursorYScaled + measurer.ascender)
        if self._minCursor is None:
            self._minCursor = cursorX
        else:
            self._minCursor = min(self._minCursor, cursorX)
        self.actualTextWidth = max(self.actualTextWidth, cursorX + buffWidth)
        self.actualTextHeight = max(self.actualTextHeight, self._commitCursorYScaled + lineHeight)
        self._inlineObjectsBuff = moveToNextLine
        self._lastAddTextData = []
        if doLineBreak:
            self._commitCursorYScaled += lineSpacing + lineHeight
            measurer.cursorX = ScaleDpi(self.specialIndent)
            self._numLines += 1

    def ParseFontOpen(self, attribs):
        try:
            self.ParseColorTag(attribs[u'color'])
        except KeyError:
            pass

        try:
            self.ParseFontsizeTag(attribs[u'size'])
        except KeyError:
            pass

        try:
            self.ParseFontfileTag(attribs[u'file'])
        except KeyError:
            pass

        self._tagStack['font'].append(attribs)
        return True

    def ParseFontClose(self):
        tagStack = self._tagStack['font']
        if tagStack:
            attribs = tagStack.pop()
            if u'color' in attribs:
                self.ParseColorClose()
            if u'size' in attribs:
                self.ParseFontsizeClose()
            if u'file' in attribs:
                self.ParseFontfileClose()
        return True

    def ParseUOpen(self, attribs):
        self._tagStack['u'] += 1
        return self._tagStack['u'] == 1

    def ParseIOpen(self, attribs):
        self._tagStack['i'] += 1
        return self._tagStack['i'] == 1

    def ParseBOpen(self, attribs):
        self._tagStack['b'] += 1
        return self._tagStack['b'] == 1

    def ParseUppercaseOpen(self, attribs):
        self._tagStack['uppercase'] += 1
        return self._tagStack['uppercase'] == 1

    def ParseUClose(self):
        retval = self._tagStack['u'] == 1
        self._tagStack['u'] = max(self._tagStack['u'] - 1, 0)
        return retval

    def ParseIClose(self):
        retval = self._tagStack['i'] == 1
        self._tagStack['i'] = max(self._tagStack['i'] - 1, 0)
        return retval

    def ParseBClose(self):
        retval = self._tagStack['b'] == 1
        self._tagStack['b'] = max(self._tagStack['b'] - 1, 0)
        return retval

    def ParseUppercaseClose(self):
        retval = self._tagStack['uppercase'] == 1
        self._tagStack['uppercase'] = max(self._tagStack['uppercase'] - 1, 0)
        return retval

    def ParseAOpen(self, attribs):
        try:
            url = attribs[u'href'].replace('&amp;', '&')
        except (KeyError, TypeError):
            log.LogError('Anchor tag missing href attribute, I have no idea what to do with this.  Attribs:', attribs)
            return False

        alt = attribs.get('alt', None)
        linkText = 'a href=' + attribs[u'href'] + (" alt='" + alt + "'" if alt is not None else '')
        linkStyle = attribs.get('linkStyle', self.linkStyle)
        try:
            linkStyle = int(linkStyle)
        except ValueError:
            linkStyle = self.linkStyle

        currentTagStackSyntax = self.GetCurrentTagStackFormatSyntax()
        inlineObject = self.StartInline('link', linkText)
        inlineObject.url = url
        inlineObject.urlID = self._urlIDCounter
        inlineObject.alt = alt
        inlineObject.tagStackState = self._tagStack.copy()
        inlineObject.textBuff = [currentTagStackSyntax + '<' + linkText + '>']
        self._tagStack['link'].append(inlineObject)
        linkState = uiconst.LINK_IDLE
        if self._mouseOverUrl and url == self._mouseOverUrl and inlineObject.urlID == self._mouseOverUrlID:
            if uicore.uilib.leftbtn:
                linkState = uiconst.LINK_ACTIVE
            else:
                linkState = uiconst.LINK_HOVER
        linkFmt = self.GetLinkHandler().GetLinkFormat(url, linkState, linkStyle)
        linkColor = None
        if linkState == uiconst.LINK_IDLE:
            try:
                colorSyntax = attribs[u'color'].replace('#', '0x')
                hexColor = StringColorToHex(colorSyntax) or colorSyntax
                if hexColor:
                    linkColor = mathUtil.LtoI(long(hexColor, 0))
            except KeyError:
                pass

        inlineObject.bold = linkFmt.bold
        inlineObject.italic = linkFmt.italic
        inlineObject.underline = linkFmt.underline
        if linkFmt.bold:
            self.ParseBOpen({})
        if linkFmt.italic:
            self.ParseIOpen({})
        if linkFmt.underline:
            self.ParseUOpen({})
        self._tagStack['color'].append(linkColor or linkFmt.color or self._colorInt)
        self._urlIDCounter += 1
        return True

    def ParseLinkClose(self):
        self.EndInline('link')
        if self._tagStack['link']:
            closingLink = self._tagStack['link'].pop()
            if closingLink.bold:
                self.ParseBClose()
            if closingLink.italic:
                self.ParseIClose()
            if closingLink.underline:
                self.ParseUClose()
            self.ParseColorClose()
        return True

    def ParseLocalizedOpen(self, attribs):
        if self.localizationWrapOn:
            self._tagStack['localizedQA'].append(True)
            return True
        try:
            newText = attribs['hint']
            if len(self._tagStack.get('link', [])) < 1:
                self.renderObject.hasAuxiliaryTooltip = True
                inlineObject = self.StartInline('localized', newText)
                self._tagStack['localized'].append(inlineObject)
            else:
                for eachLink in self._tagStack.get('link', []):
                    eachLink['extraAlt'] = newText

        except KeyError:
            log.LogError('Localization tag without tooltip!')

        return True

    def ParseLocalizedClose(self):
        try:
            if self.localizationWrapOn:
                self._tagStack['localizedQA'].pop()
                return True
            self.EndInline('localized')
            if len(self._tagStack['localized']) > 0:
                self._tagStack['localized'].pop()
            return True
        except (KeyError, IndexError):
            pass

        return True

    def ParseLeftOpen(self, attribs):
        self._currTextAlign = TextAlign.LEFT
        return True

    def ParseRightOpen(self, attribs):
        self._currTextAlign = TextAlign.RIGHT
        return True

    def ParseCenterOpen(self, attribs):
        self._currTextAlign = TextAlign.CENTER
        return True

    def ParseColorTag(self, value):
        color = StringColorToHex(value)
        if color is None:
            color = value.replace('#', '0x')
        try:
            color = colorblind.CheckReplaceColorHex(color, maintainBrightness=True, maxSaturation=COLORBLIND_MAX_SATURATION)
            col = mathUtil.LtoI(long(color, 0))
            self._tagStack['color'].append(col)
        except ValueError:
            log.LogWarn('Label got color value it cannot handle', value, self.text)
            return False

        return True

    def ParseColorClose(self):
        try:
            if len(self._tagStack['color']) > 1:
                self._tagStack['color'].pop()
            else:
                log.LogWarn('Label got ParseColorClose but doesnt have color to close', self.text)
                return False
            return True
        except (KeyError, IndexError):
            pass

        return False

    def ParseFontsizeTag(self, value):
        fs = check_convert_font_size(int(value))
        if 'fontsize' not in self._tagStack:
            self._tagStack['fontsize'] = []
        self._tagStack['fontsize'].append(fs)
        return True

    def ParseFontsizeClose(self):
        try:
            if len(self._tagStack['fontsize']) > 1:
                self._tagStack['fontsize'].pop()
            else:
                log.LogWarn('Label got FontsizeClose but doesnt have fontsize to close', self.text)
                return False
            return True
        except (KeyError, IndexError):
            pass

        return False

    def ParseFontfileTag(self, value):
        if 'file' not in self._tagStack:
            self._tagStack['file'] = []
        self._tagStack['file'].append(value)
        return True

    def ParseFontfileClose(self):
        try:
            if len(self._tagStack['file']) > 0:
                x = self._tagStack['file'].pop()
            else:
                log.LogWarn('Label got FontpathClose but doesnt have file to close', self.text)
                return False
            return True
        except (KeyError, IndexError):
            pass

        return False

    def ParseLetterspaceTag(self, value):
        ls = int(value)
        if 'letterspace' not in self._tagStack:
            self._tagStack['letterspace'] = []
        self._tagStack['letterspace'].append(ls)
        return True

    def ParseLetterspaceClose(self):
        try:
            if len(self._tagStack['letterspace']) > 1:
                self._tagStack['letterspace'].pop()
            else:
                log.LogWarn('Label got ParseLetterspaceClose but doesnt have letterspace to close', self.text)
                return False
            return True
        except (KeyError, IndexError):
            pass

        return False

    def ParseHintTag(self, value):
        inlineObject = self.StartInline('hint', value)
        self._tagStack['hint'].append(inlineObject)
        return True

    def ParseHintClose(self):
        self.EndInline('hint')
        try:
            self._tagStack['hint'].pop()
            return True
        except (KeyError, IndexError):
            pass

        return False

    def ParseWordTag(self, value):
        inlineObject = self.StartInline('words', value)
        if 'words' not in self._tagStack:
            self._tagStack['words'] = []
        self._tagStack['words'].append(inlineObject)
        return True

    def ParseWordClose(self):
        self.EndInline('words')
        try:
            self._tagStack['words'].pop()
            return True
        except (KeyError, IndexError):
            pass

        return False

    def ParseEmptyOpen(self, attribs):
        if attribs is None:
            log.LogWarn('Got None attribs into ParseEmptyOpen', self.text)
            return False
        if u'url' in attribs:
            attribs[u'href'] = attribs[u'url']
            del attribs[u'url']
        if u'href' in attribs:
            return self.ParseAOpen(attribs)
        stackDirty = False
        for attrib, value in attribs.iteritems():
            try:
                stackDirty = self.emptyTagHandlers[attrib](self, value) or stackDirty
            except KeyError:
                log.LogWarn('Empty tag attribute', attrib, 'not recognized')

        return stackDirty

    def ParseUnusedClose(self, tag):
        log.LogWarn('Unused close tag:', tag)

    def ParseUnusedOpen(self, tag):
        log.LogWarn('Unused open tag:', tag)

    tagIDToFunctionMapping = {1: (ParseFontOpen, ParseFontClose),
     2: (ParseUOpen, ParseUClose),
     3: (ParseUppercaseOpen, ParseUppercaseClose),
     4: (ParseIOpen, ParseIClose),
     5: (ParseBOpen, ParseBClose),
     6: (ParseAOpen, ParseLinkClose),
     7: (ParseLocalizedOpen, ParseLocalizedClose),
     100: (ParseLeftOpen, lambda self: self.ParseUnusedClose('left')),
     101: (ParseRightOpen, lambda self: self.ParseUnusedClose('right')),
     102: (ParseCenterOpen, lambda self: self.ParseUnusedClose('center')),
     200: (lambda self, attribs: self.ParseUnusedOpen('color'), ParseColorClose),
     201: (lambda self, attribs: self.ParseUnusedOpen('fontsize'), ParseFontsizeClose),
     202: (lambda self, attribs: self.ParseUnusedOpen('letterspace'), ParseLetterspaceClose),
     203: (lambda self, attribs: self.ParseUnusedOpen('hint'), ParseHintClose),
     204: (lambda self, attribs: self.ParseUnusedOpen('url'), ParseLinkClose),
     -48879: (ParseEmptyOpen, lambda self: self.ParseUnusedClose('empty?!?'))}
    emptyTagHandlers = {u'color': ParseColorTag,
     u'fontsize': ParseFontsizeTag,
     u'letterspace': ParseLetterspaceTag,
     u'hint': ParseHintTag,
     u'file': ParseFontfileTag}

    @classmethod
    def ExtractLocalizedTags(cls, text):
        ret = []
        tagID = 7
        parsePrepared = trinity.ParseLabelText(text)
        for lineData in parsePrepared:
            for tabData in lineData:
                for element in tabData:
                    type = element[0]
                    if type == 1 and element[1] == tagID:
                        ret.append(element[2])

        return ret

    def GetCurrentTagStackFormatSyntax(self, ignoreTags = ('link', 'localized', 'letterspace')):
        formatSyntax = ''
        for tag, stack in self._tagStack.iteritems():
            if tag in ignoreTags:
                continue
            if type(stack) == types.ListType:
                if stack:
                    value = stack[-1]
                    if tag == 'color':
                        value = self.IntColorToSyntax(value)
                    formatSyntax += '<%s=%s>' % (tag, value)
            elif stack:
                formatSyntax += '<%s>' % tag

        return formatSyntax

    def IntColorToSyntax(self, intColor):
        c = trinity.TriColor()
        c.FromInt(intColor)
        color = (c.r,
         c.g,
         c.b,
         c.a)
        return '#%02x%02x%02x%02x' % (color[3] * 255,
         color[0] * 255,
         color[1] * 255,
         color[2] * 255)

    def GetTooltipPosition(self):
        if self.tooltipPosition:
            return self.tooltipPosition
        l, t = self.GetAbsolutePosition()
        w, h = self.textwidth, self.textheight
        if self._alphaFadeLeft:
            fadeStart, length = self._alphaFadeLeft
            l += fadeStart
            w -= fadeStart
        if self._alphaFadeRight:
            fadeEnd, length = self._alphaFadeRight
            w = min(w, fadeEnd)
        return (l,
         t,
         w,
         h)

    def GetMouseOverUrl(self):
        return self._mouseOverUrl

    def StartInline(self, inlineType, data):
        inlineObject = Bunch()
        inlineObject.inlineType = inlineType
        inlineObject.data = data
        measurer = self.measurer
        inlineObject.inlineX = ReverseScaleDpi(measurer.cursorX)
        inlineObject.inlineXEnd = None
        if self._inlineObjectsBuff is None:
            self._inlineObjectsBuff = []
        self._inlineObjectsBuff.append(inlineObject)
        return inlineObject

    def EndInline(self, inlineType):
        if inlineType in self._tagStack and self._tagStack[inlineType]:
            inlineObject = self._tagStack[inlineType][-1]
            if inlineObject:
                measurer = self.measurer
                inlineObject.inlineXEnd = ReverseScaleDpi(measurer.cursorX)

    @staticmethod
    def GetLinkHandlerClass():
        return Link

    def GetLinkHandler(self):
        handlerClass = self.GetLinkHandlerClass()
        return handlerClass()

    def GetMenu(self):
        m = []
        if self._mouseOverUrl:
            m = self.GetLinkHandler().GetLinkMenu(self, self._mouseOverUrl)
        m += [(MenuLabel('/Carbon/UI/Controls/Common/Copy'), self.CopyText)]
        if localization.UseImportantTooltip():
            if self.hint:
                m += [(localization.GetByLabel('UI/Common/CopyTooltip'), self.CopyHint, (self.hint,))]
        return m

    def GetAuxiliaryMenuOptions(self):
        m = []
        if self._offer_auxiliary_copy_option:
            m.append((MenuLabel('/Carbon/UI/Controls/Common/Copy'), self.CopyText))
            if localization.UseImportantTooltip():
                locTooltip = self.GetAuxiliaryTooltip()
                if locTooltip:
                    m += [(localization.GetByLabel('UI/Common/CopyTooltip'), self.CopyHint, (locTooltip,))]
        return m

    def GetAuxiliaryTooltip(self):
        if self._inlineObjects:
            mouseX = uicore.uilib.x
            mouseY = uicore.uilib.y
            left, top, width, height = self.GetAbsolute()
            for inline in self._inlineObjects:
                startX = inline.inlineX
                endX = inline.inlineXEnd
                startY = inline.inlineY
                endY = startY + inline.inlineHeight
                if left + startX < mouseX < left + endX and top + startY < mouseY < top + endY:
                    if inline.inlineType == 'localized':
                        self.auxTooltipPosition = (left + startX,
                         top + startY,
                         endX - startX,
                         inline.inlineHeight)
                        return inline.data

        self.auxTooltipPosition = None
        if self.autoFadeSides and self._alphaFadeRight:
            return self.text

    def GetAuxiliaryTooltipPosition(self):
        return self.auxTooltipPosition

    def GetHint(self):
        baseHint = self.hint
        if baseHint:
            return baseHint
        if self.autoFadeSides and self._alphaFadeRight:
            return self.text

    def CopyText(self):
        text = StripTags(self.text, stripOnly=['localized'])
        blue.pyos.SetClipboardData(text)

    def CopyHint(self, hint):
        if isinstance(hint, basestring):
            blue.pyos.SetClipboardData(hint)

    def OnMouseEnter(self, *args):
        self.CheckInlines()

    def OnMouseExit(self, *args):
        self.CheckInlines()

    def OnMouseHover(self, *args):
        self.CheckInlines()

    def CheckInlines(self):
        inlineLinkObj = None
        inlineHintObj = None
        inlineLocalizationHintObj = None
        if self._inlineObjects and uicore.uilib.mouseOver is self:
            mouseX = uicore.uilib.x
            mouseY = uicore.uilib.y
            left, top, width, height = self.GetAbsolute()
            for inline in self._inlineObjects:
                startX = inline.inlineX
                endX = inline.inlineXEnd
                startY = inline.inlineY
                endY = startY + inline.inlineHeight
                if left + startX < mouseX < left + endX and top + startY < mouseY < top + endY:
                    if inline.inlineType == 'link':
                        inlineLinkObj = inline
                    elif inline.inlineType == 'hint':
                        inlineHintObj = inline
                    elif inline.inlineType == 'localized' and isinstance(inline.data, basestring):
                        inlineLocalizationHintObj = inline
                    elif inline.inlineType == 'words':
                        self.MouseOverWordCallback(word=inline.data)

        self._resolvingInlineHint = True
        mouseOverUrl = None
        mouseOverUrlID = None
        mouseOverTextBuff = None
        inlineHint = None
        if inlineLinkObj:
            mouseOverUrl = inlineLinkObj.url
            mouseOverUrlID = inlineLinkObj.urlID
            mouseOverTextBuff = inlineLinkObj.textBuff
            if inlineLinkObj.alt:
                inlineHint = inlineLinkObj.alt
            else:
                standardHint = self.GetLinkHandler().GetStandardLinkHint(mouseOverUrl)
                if standardHint:
                    inlineHint = standardHint
            if inlineLinkObj.extraAlt:
                if inlineHint:
                    inlineHint = inlineHint + '<br>' + inlineLinkObj.extraAlt
                else:
                    inlineHint = inlineLinkObj.extraAlt
            x, y = self.GetAbsolutePosition()
            self.tooltipPosition = (x + inlineLinkObj.inlineX,
             y + inlineLinkObj.inlineY,
             inlineLinkObj.inlineXEnd - inlineLinkObj.inlineX,
             inlineLinkObj.inlineHeight)
        elif inlineHintObj:
            x, y = self.GetAbsolutePosition()
            self.tooltipPosition = (x + inlineHintObj.inlineX,
             y + inlineHintObj.inlineY,
             inlineHintObj.inlineXEnd - inlineHintObj.inlineX,
             inlineHintObj.inlineHeight)
        else:
            self.tooltipPosition = None
        if not inlineHint and inlineHintObj:
            inlineHint = inlineHintObj.data
        if inlineLocalizationHintObj:
            if inlineHint:
                inlineHint += '<br>' + inlineLocalizationHintObj.data
            else:
                inlineHint = inlineLocalizationHintObj.data
        hint = inlineHint or getattr(self, '_objectHint', None)
        if hint != self.hint:
            self.hint = hint
        self._resolvingInlineHint = False
        if mouseOverUrl != self._mouseOverUrl:
            if mouseOverUrl:
                PlaySound(uiconst.SOUND_BUTTON_HOVER)
            self._mouseOverUrl = mouseOverUrl
            self._mouseOverUrlID = mouseOverUrlID
            self._mouseOverTextBuff = mouseOverTextBuff
            self.Layout()
            if mouseOverUrl:
                self._hiliteResetTimer = AutoTimer(50, self._ResetInlineHilite)

    def _ResetInlineHilite(self):
        if uicore.uilib.mouseOver is self:
            return
        self._hiliteResetTimer = None
        self.CheckInlines()

    def OnClick(self, *args):
        if self._mouseOverUrl:
            PlaySound(uiconst.SOUND_BUTTON_CLICK)
            self.GetLinkHandler().ClickLink(self, self._mouseOverUrl.replace('&amp;', '&'))

    def OnMouseDown(self, *args):
        if self._mouseOverUrl:
            self.OnMouseDownWithUrl(self._mouseOverUrl, *args)
        if getattr(self, '_mouseOverTextBuff', None) and self._mouseOverUrl:
            self._dragLinkData = (''.join(self._mouseOverTextBuff), self._mouseOverUrl)
        else:
            self._dragLinkData = None
        VisibleBase.OnMouseDown(self, *args)

    def OnMouseDownWithUrl(self, url, *args):
        pass

    def OnMouseMove(self, *args):
        if not self._hilite:
            self.CheckInlines()
        VisibleBase.OnMouseMove(self, *args)

    def GetDragData(self, *args):
        if getattr(self, '_dragLinkData', None):
            displayText, url = getattr(self, '_dragLinkData', None)
            entry = Bunch()
            entry.__guid__ = 'TextLink'
            entry.url = url
            entry.displayText = StripTags(displayText)
            return [entry]

    def MouseOverWordCallback(self, word, *args):
        if getattr(self, 'mouseOverWordCallback', None):
            self.mouseOverWordCallback(word)

    @classmethod
    def PrepareDrag(cls, *args):
        return cls.GetLinkHandlerClass().PrepareDrag(*args)

    def UpdateAlignment(self, budgetLeft = 0, budgetTop = 0, budgetWidth = 0, budgetHeight = 0, updateChildrenOnly = False):
        preWidth = self.displayWidth
        preHeight = self.displayHeight
        retBudgetLeft, retBudgetTop, retBudgetWidth, retBudgetHeight, sizeChanged = VisibleBase.UpdateAlignment(self, budgetLeft, budgetTop, budgetWidth, budgetHeight)
        if not self._resolvingAutoSizing and self.isAffectedByPushAlignment and sizeChanged:
            self.Layout('UpdateAlignment', absSize=(ReverseScaleDpi(self.displayWidth), ReverseScaleDpi(self.displayHeight)))
            if preWidth != self.displayWidth or preHeight != self.displayHeight:
                retBudgetLeft, retBudgetTop, retBudgetWidth, retBudgetHeight, _sizeChanged = VisibleBase.UpdateAlignment(self, budgetLeft, budgetTop, budgetWidth, budgetHeight)
        if sizeChanged and getattr(self, 'OnSizeChanged', None):
            self.OnSizeChanged()
        if self.autoFadeSides and self.parent:
            length = self.autoFadeSides
            if self.displayX + self.displayWidth > self.parent.displayWidth:
                fadeEnd = self.parent.displayWidth - self.displayX
                self.SetRightAlphaFade(uicore.ReverseScaleDpi(fadeEnd), length)
                self.renderObject.hasAuxiliaryTooltip = True
            else:
                self.SetRightAlphaFade()
        return (retBudgetLeft,
         retBudgetTop,
         retBudgetWidth,
         retBudgetHeight,
         sizeChanged)

    def GetTagStringValue(self, tagtofind, tagstring):
        start = tagstring.find(tagtofind)
        if start != -1:
            tagBegin = tagstring[start + len(tagtofind):]
            for checkQuote in ['"', "'"]:
                if tagBegin.startswith(checkQuote):
                    end = tagBegin.find(checkQuote, 1)
                    if end != -1:
                        return tagBegin[1:end]

    def GetTagValue(self, tagtofind, tagstring):
        start = tagstring.find(tagtofind)
        if start != -1:
            end = tagstring.find(' ', start)
            if end == start:
                end = tagstring.find(' ', start + 1)
            if end == -1:
                end = tagstring.find('>', start)
            if end == -1:
                end = len(tagstring)
            return tagstring[start + len(tagtofind):end]

    @classmethod
    def MeasureTextSize(cls, text, **customAttributes):
        customAttributes['text'] = text
        customAttributes['parent'] = None
        customAttributes['measuringText'] = True
        customAttributes['align'] = uiconst.TOPLEFT
        label = cls(**customAttributes)
        return (label.textwidth, label.textheight)

    def OnGlobalFontSizeChanged(self):
        if self._raw_fontsize is not None:
            self.fontsize = self._raw_fontsize

    def OnGlobalFontShadowChanged(self):
        if self._using_default_shadow:
            self.shadowOffset = self.get_default_shadow_offset()


class LabelOverride(LabelCore):

    @classmethod
    def __reload_update__(cls, old_cls):
        return old_cls
