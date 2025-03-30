#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\control\singlelineedits\baseSingleLineEdit.py
import weakref
import logging
import sys
import blue
import evetypes
import mathext
import trinity
import uthread
from brennivin.itertoolsext import Bundle
from carbonui.button import styling
from carbonui.button.const import HEIGHT_NORMAL
from carbonui.control.combo import Combo
from carbonui.control.singlelineedits.caret import Caret
from carbonui.control.singlelineedits.singleLineEditHistory import SingleLineEditHistory
from carbonui.fontconst import DEFAULT_FONTSIZE
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from carbonui.text.settings import check_convert_font_size
from eve.client.script.ui import eveThemeColor
from carbon.common.script.util.commonutils import StripTags
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui import Density, uiconst, Align
from carbonui.control.label import LabelOverride as Label
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.text.color import TextColor
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from carbonui.util.various_unsorted import GetBrowser, GetWindowAbove, GetClipboardData
from carbonui.control.buttonIcon import ButtonIcon
from eve.client.script.ui.control.eveLabel import EveLabelMedium, EveLabelSmall
from carbonui.control.window import Window
from carbonui.decorative.inputUnderlay import InputUnderlay
from eve.client.script.ui.shared.market import GetTypeIDFromDragItem
from eve.client.script.ui.tooltips.tooltipUtil import RefreshTooltipForOwner
from eve.client.script.ui.util.linkUtil import GetItemIDFromTextLink
from menu import MenuLabel
from qtyTooltip.tooltip import LoadTooltipForNumber
from carbonui.control.singlelineedits.util import GetDroppedCharCorpOrAllianceName, GetDroppedCharInfo
logger = logging.getLogger(__name__)
CARET_SCROLL_MARGIN = 16

class BaseSingleLineEdit(Container):
    default_name = 'BaseSingleLineEdit'
    default_align = uiconst.TOPLEFT
    default_width = 160
    default_height = HEIGHT_NORMAL
    default_state = uiconst.UI_NORMAL
    default_density = Density.NORMAL
    default_readonly = False
    default_autoselect = False
    default_dynamicHistoryWidth = False
    default_caretcolor = eveThemeColor.THEME_ACCENT
    default_selectioncolor = tuple(eveThemeColor.THEME_FOCUSDARK[:3]) + (0.4,)
    default_fontcolor = TextColor.NORMAL
    default_textLeftMargin = 0
    default_textRightMargin = 0
    default_bold = False
    default_inputType = None
    default_adjustWidth = False
    default_label = ''
    default_setvalue = ''
    default_icon = None
    default_OnChange = None
    default_OnSetFocus = None
    default_OnFocusLost = None
    default_OnReturn = None
    default_OnInsert = None
    default_fontsize = DEFAULT_FONTSIZE
    default_fontStyle = None
    default_fontFamily = None
    default_fontPath = None
    default_fadeOutContent = True
    registerHistory = True

    def ApplyAttributes(self, attributes):
        super(BaseSingleLineEdit, self).ApplyAttributes(attributes)
        self.rightAlignedButtons = weakref.WeakSet()
        self._clearButton = None
        self.caretIndex = (0, 0)
        self.isTabStop = 1
        self.selFrom = None
        self.selTo = None
        self.historyMenu = None
        self.displayHistory = True
        self.caret = None
        self.selectionTimer = None
        self.underlay = None
        self.textLabel = None
        self.hintLabel = None
        self.selectionFill = None
        self.draggedValue = None
        self._textClipperInner = None
        self.iconSprite = None
        self.OnChange = None
        self.OnFocusLost = None
        self.OnReturn = None
        self.OnInsert = None
        self.text = attributes.get('text', '')
        self.hintText = attributes.get('hintText', '')
        self.readonly = attributes.get('readonly', self.default_readonly)
        self.fontStyle = attributes.get('fontStyle', self.default_fontStyle)
        self.fontFamily = attributes.get('fontFamily', self.default_fontFamily)
        self.fontPath = attributes.get('fontPath', self.default_fontPath)
        self.fontsize = attributes.get('fontsize', self.default_fontsize)
        self.bold = attributes.get('bold', self.default_bold)
        self.textLeftMargin = attributes.get('textLeftMargin', self.default_textLeftMargin)
        self.textRightMargin = attributes.get('textRightMargin', self.default_textRightMargin)
        self.icon = attributes.get('icon', self.default_icon)
        self.CaretColor = attributes.get('caretColor', self.default_caretcolor)
        self.SelectColor = attributes.get('selectColor', self.default_selectioncolor)
        self.fontcolor = attributes.get('fontcolor', self.default_fontcolor)
        self.autoselect = attributes.get('autoselect', self.default_autoselect)
        self.dynamicHistoryWidth = attributes.get('dynamicHistoryWidth', self.default_dynamicHistoryWidth)
        self.inputType = attributes.get('inputType', self.default_inputType)
        self.isTypeField = attributes.get('isTypeField', False)
        self.isCharacterField = attributes.get('isCharacterField', False)
        self.isCharCorpOrAllianceField = attributes.get('isCharCorpOrAllianceField', False)
        self.isLocationField = attributes.get('isLocationField', False)
        self.OnAnyChar = attributes.get('OnAnyChar', self.OnAnyChar)
        self.adjustWidth = attributes.get('adjustWidth', self.default_adjustWidth)
        self.fadeOutContent = attributes.get('fadeOutContent', self.default_fadeOutContent)
        self.ConstructIcon()
        self.ConstructTextClipper()
        self.ConstructBackground()
        self.ConstructLabels()
        self.SetTextColor(self.fontcolor)
        self.SetLabel(attributes.get('label', self.default_label))
        self.SetValue(attributes.get('setvalue', self.default_setvalue))
        self.CheckHintText()
        self.OnChange = attributes.get('OnChange', self.default_OnChange)
        self.__OnSetFocus = attributes.get('OnSetFocus', self.default_OnSetFocus)
        self.OnFocusLost = attributes.get('OnFocusLost', self.default_OnFocusLost)
        self.OnReturn = attributes.get('OnReturn', self.default_OnReturn)
        self.OnInsert = attributes.get('OnInsert', self.default_OnInsert)
        self.sendSelfAsArgument = attributes.get('sendSelfAsArgument', False)
        self.density = attributes.get('density', self.default_density)
        if self.GetAlign() == uiconst.TOALL:
            self.height = self.width = 0
        else:
            self.height = styling.get_height(self.density)
        uicore.event.RegisterForTriuiEvents(uiconst.UI_MOUSEDOWN, self.OnGlobalMouseDownCallback)

    def ConstructIcon(self):
        if self.icon:
            if not self.iconSprite:
                iconCont = ContainerAutoSize(name='iconCont', parent=self, align=uiconst.TOLEFT, padLeft=8)
                self.iconSprite = Sprite(name='iconSprite', parent=iconCont, align=Align.CENTERLEFT, color=TextColor.SECONDARY, pos=(0, 0, 16, 16))
            self.iconSprite.SetTexturePath(self.icon)
        else:
            self.iconSprite = None

    def ConstructTextClipper(self):
        self._textClipper = Container(name='_textClipper', parent=self, clipChildren=False, padding=(8, 0, 8, 0))
        self._textClipperInner = Container(parent=self._textClipper, align=uiconst.TOALL, clipChildren=True)
        self._textClipper._OnSizeChange_NoBlock = self.OnClipperSizeChange

    def ConstructBackground(self):
        if self.underlay:
            return
        self.underlay = InputUnderlay(bgParent=self)

    def ConstructLabels(self):
        self.textLabel = EveLabelMedium(name='textLabel', parent=self._textClipperInner, align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED, left=self.textLeftMargin, text='', maxLines=1)
        self.hintLabel = Label(name='hintTextLabel', parent=self._textClipperInner, align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED, left=self.textLeftMargin, text='', maxLines=1, color=TextColor.SECONDARY)

    def ConstructCaret(self):
        if self.caret or not hasattr(self, 'caret'):
            return
        self.caret = Caret(name='caret', parent=self._textClipper, align=uiconst.CENTERLEFT, idx=0, state=uiconst.UI_HIDDEN, left=self.textLeftMargin, height=1)

    def ConstructSelectionFill(self):
        _, h = self.GetAbsoluteSize()
        order = self.textLabel.GetOrder()
        if self.selectionFill:
            return
        self.selectionFill = Fill(name='selectionFill', parent=self._textClipperInner, align=uiconst.CENTERLEFT, idx=order + 1, color=self.SelectColor)

    def SetLabel(self, text):
        self.label = EveLabelSmall(parent=self, name='__caption', text=text, state=uiconst.UI_DISABLED, align=uiconst.TOPLEFT, idx=0)
        self.label.top = -self.label.textheight
        if self.adjustWidth:
            self.width = max(self.width, self.label.textwidth)

    def SetHistoryVisibility(self, status):
        self.displayHistory = status

    def SetTextColor(self, color):
        if not color:
            return
        self.textLabel.SetRGBA(*color)

    def SetHintText(self, hint):
        self.hintText = hint
        self.CheckHintText()

    def OnClipperSizeChange(self, newWidth, newHeight):
        if newWidth:
            self.RefreshCaretPosition()
            self.RefreshSelectionDisplay()
            self.RefreshTextClipper()

    def RefreshCaretPosition(self):
        if self.destroyed:
            return
        self.ConstructCaret()
        w, h = self._textClipper.GetAbsoluteSize()
        self.caret.left = self.textLabel.left + self.caretIndex[1]
        if self.textLabel.textwidth < w - self.textLeftMargin - self.textRightMargin:
            self.textLabel.left = self.textLeftMargin
        else:
            if self.textLabel.left + self.textLabel.textwidth < w - self.textLeftMargin - self.textRightMargin:
                self.textLabel.left = w - self.textLeftMargin - self.textRightMargin - self.textLabel.textwidth
            if self.caret.left > w - self.textRightMargin - CARET_SCROLL_MARGIN:
                diff = self.caret.left - w + self.textRightMargin + CARET_SCROLL_MARGIN
                self.textLabel.left = max(self.textLabel.left - diff, w - self.textLabel.textwidth)
            elif self.caret.left < self.textLeftMargin + CARET_SCROLL_MARGIN:
                diff = -self.caret.left + self.textLeftMargin + CARET_SCROLL_MARGIN
                self.textLabel.left = min(self.textLabel.left + diff, 0)
        self.caret.left = mathext.clamp(value=self.textLabel.left + self.caretIndex[1], low=0, high=w - self.caret.width)

    def RefreshSelectionDisplay(self):
        selection = self.GetSelectionBounds()
        if selection != (None, None):
            self.ConstructSelectionFill()
            f, t = selection
            self.selectionFill.left = self.textLabel.left + f[1]
            self.selectionFill.width = t[1] - f[1]
            self.selectionFill.state = uiconst.UI_DISABLED
            fontSize = check_convert_font_size(self.fontsize)
            self.selectionFill.height = fontSize + 4
        elif self.selectionFill:
            self.selectionFill.state = uiconst.UI_HIDDEN

    def GetSelectionBounds(self):
        if self.selFrom and self.selTo and self.selFrom[0] != self.selTo[0]:
            return (min(self.selFrom, self.selTo), max(self.selFrom, self.selTo))
        return (None, None)

    def RefreshTextClipper(self):
        if self._clearButton:
            if len(self.text) >= self._clearButton.showOnLetterCount:
                self._clearButton.Show()
            else:
                self._clearButton.Hide()
        visible_button_count = 0
        left = 5
        for each in self.rightAlignedButtons:
            if not each.destroyed and each.display:
                visible_button_count += 1
                each.left = left
                left += each.width

        if visible_button_count > 0:
            left += 4
        left = max(left, 8)
        self._textClipper.padRight = left
        if self.fadeOutContent:
            w, h = self._textClipper.GetAbsoluteSize()
            if self.textLabel.left + self.textLabel.textwidth > w:
                self.textLabel.SetRightAlphaFade(-self.textLabel.left + w, 8)
            else:
                self.textLabel.SetRightAlphaFade(0, 0)
            if self.textLabel.left < self.textLeftMargin:
                self.textLabel.SetLeftAlphaFade(-self.textLabel.left + self.textLeftMargin, 8)
            else:
                self.textLabel.SetLeftAlphaFade(0, 0)

    def ShowClearButton(self, icon = None, hint = None, showOnLetterCount = True):
        if self._clearButton:
            self._clearButton.Close()
        icon = icon or 'res:/UI/Texture/Icons/73_16_210.png'
        clearButton = self.AddIconButton(icon, hint)
        clearButton.OnClick = self.OnClearButtonClick
        clearButton.Hide()
        clearButton.showOnLetterCount = showOnLetterCount
        self._clearButton = clearButton
        return clearButton

    def OnGlobalMouseDownCallback(self, uiObject, *args, **kwds):
        if self.destroyed:
            return False
        if uiObject is not self and self.historyMenu:
            historyMenu = self.historyMenu()
            if historyMenu and not historyMenu.destroyed:
                if not uiObject.IsUnder(historyMenu):
                    self.CloseHistoryMenu()
        return True

    def AutoFitToText(self, text = None, minWidth = None):
        if self.align in (uiconst.TOTOP, uiconst.TOBOTTOM, uiconst.TOALL):
            raise RuntimeError('Incorrect alignment for SingleLine.AutoFitToText')
        if text is not None:
            textwidth, textheight = self.textLabel.MeasureTextSize(text)
            autoWidth = textwidth + self.textLeftMargin * 2 + 2
        else:
            autoWidth = self.textLabel.textwidth + self.textLeftMargin * 2 + 2
        if minWidth:
            autoWidth = max(minWidth, autoWidth)
        self.width = autoWidth
        self.textLabel.left = self.textLeftMargin

    def CloseHistoryMenu(self):
        if self.historyMenu:
            historyMenu = self.historyMenu()
            if historyMenu and not historyMenu.destroyed:
                self.active = None
                historyMenu.Close()
                self.historyMenu = None

    def GetValid(self):
        current = self.GetValue(registerHistory=False)
        id, mine = self.GetHistory()
        valid = [ each for each in mine if each.lower().startswith(unicode(current).lower()) and each != current ]
        valid.sort(key=lambda x: len(x))
        return valid

    def ClearHistory(self, *args):
        id, mine, all = self.GetHistory(getAll=True)
        if id in all:
            del all[id]
            settings.user.ui.Set('editHistory', all)

    def RegisterHistory(self, value = None):
        if not self.registerHistory:
            return
        id, mine, all = self.GetHistory(getAll=True)
        current = (value or self.text).rstrip()
        if current not in mine:
            mine.append(current)
        all[id] = mine
        settings.user.ui.Set('editHistory', all)

    def AddIconButton(self, texturePath, hint = None):
        rightAlignedButton = self._ConstructIconButton(hint, texturePath)
        self.rightAlignedButtons.add(rightAlignedButton)
        return rightAlignedButton

    def _ConstructIconButton(self, hint, texturePath):
        return ButtonIcon(texturePath=texturePath, pos=(0, 0, 16, 16), align=uiconst.CENTERRIGHT, parent=self, hint=hint, idx=0)

    def OnChar(self, char, flag):
        if self.OnAnyChar(char):
            fontFamily = uicore.font.GetFontFamilyBasedOnClientLanguageID()
            if fontFamily != self.textLabel.fontFamily:
                self.textLabel.fontFamily = fontFamily
                self.hintLabel.fontFamily = fontFamily
            if char in [127, uiconst.VK_BACK]:
                if self.GetSelectionBounds() != (None, None):
                    self.DeleteSelected()
                else:
                    self.Delete(direction=False)
                self.CheckHistory()
                if self.OnInsert:
                    self.OnInsert(char, flag)
                return True
            if char != uiconst.VK_RETURN:
                self.Insert(char)
                self.CheckHistory()
                if self.OnInsert:
                    self.OnInsert(char, flag)
                return True
        return False

    def Confirm(self, *args):
        if self.OnReturn:
            self.CloseHistoryMenu()
            if self.sendSelfAsArgument:
                return uthread.new(self.OnReturn, self)
            else:
                return uthread.new(self.OnReturn)
        searchFrom = GetWindowAbove(self)
        if searchFrom:
            wnds = [ w for w in searchFrom.Find('trinity.Tr2Sprite2dContainer') + searchFrom.Find('trinity.Tr2Sprite2d') if getattr(w, 'btn_default', 0) == 1 ]
            if len(wnds):
                for wnd in wnds:
                    if self == wnd:
                        continue
                    if wnd.IsVisible():
                        if hasattr(wnd, 'OnClick'):
                            uthread.new(wnd.OnClick, wnd)
                        return True

        return False

    def OnKeyDown(self, vkey, flag):
        isMac = sys.platform.startswith('darwin')

        def k(win, mac):
            if isMac:
                return mac
            return win

        HOME = uiconst.VK_HOME
        END = uiconst.VK_END
        CTRL = uicore.uilib.Key(uiconst.VK_CONTROL)
        ALT = uicore.uilib.Key(uiconst.VK_MENU)
        CMD = uicore.uilib.Key(uiconst.VK_LWIN)
        SHIFT = uicore.uilib.Key(uiconst.VK_SHIFT)
        if self.destroyed:
            return
        oldCaretIndex = self.caretIndex
        selection = self.GetSelectionBounds()
        index = oldCaretIndex[0]
        if SHIFT and vkey == uiconst.VK_DELETE:
            wasDeleted = self.TryDeleteFromHistory()
            if wasDeleted:
                return
        if vkey == uiconst.VK_LEFT and (not isMac or not CMD):
            if k(win=CTRL, mac=ALT):
                index = self.text.rfind(' ', 0, max(index - 1, 0)) + 1 or 0
            else:
                index = self.MoveIndexToLeft(index)
        elif vkey == uiconst.VK_RIGHT and (not isMac or not CMD):
            if k(win=CTRL, mac=ALT):
                index = self.text.find(' ', index) + 1 or len(self.textLabel.text)
            else:
                index = self.MoveIndexToRight(index)
            index = min(index, len(self.textLabel.text))
        elif vkey == HOME or isMac and vkey == uiconst.VK_LEFT and CMD:
            index = 0
        elif vkey == END or isMac and vkey == uiconst.VK_RIGHT and CMD:
            index = len(self.textLabel.text)
        elif vkey == uiconst.VK_DELETE:
            if self.GetSelectionBounds() != (None, None):
                self.DeleteSelected()
                return
            else:
                self.Delete(direction=True)
                return
        else:
            if vkey == uiconst.VK_UP:
                self.OnUpKeyPressed()
            elif vkey == uiconst.VK_DOWN:
                self.OnDownKeyPressed()
            else:
                self.OnUnusedKeyDown(self, vkey, flag)
            return
        self.caretIndex = self.GetCursorFromIndex(index)
        if vkey in (uiconst.VK_LEFT,
         uiconst.VK_RIGHT,
         HOME,
         END):
            if SHIFT:
                if self.selTo is not None:
                    self.selTo = self.caretIndex
                elif self.selTo is None:
                    self.selFrom = oldCaretIndex
                    self.selTo = self.caretIndex
            elif selection != (None, None):
                if vkey == uiconst.VK_LEFT:
                    index = selection[0][0]
                elif vkey == uiconst.VK_RIGHT:
                    index = selection[1][0]
                self.caretIndex = self.GetCursorFromIndex(index)
            if not SHIFT or self.selFrom == self.selTo:
                self.selFrom = self.selTo = None
            self.CloseHistoryMenu()
        self.RefreshCaretPosition()
        self.RefreshSelectionDisplay()
        self.RefreshTextClipper()

    def TryDeleteFromHistory(self):
        if not self.historyMenu:
            return False
        historyMenu = self.historyMenu()
        if not historyMenu:
            return False
        selectedEntry = historyMenu.GetSelectedEntry()
        if not selectedEntry:
            return False
        currentText = historyMenu.GetTextEntered()
        return self.DeleteFromHistory(currentText, selectedEntry.string)

    def OnDownKeyPressed(self):
        self.BrowseHistory(down=True)

    def OnUpKeyPressed(self):
        self.BrowseHistory(down=False)

    def OnUnusedKeyDown(self, *args):
        pass

    def MoveIndexToRight(self, index):
        index += 1
        return index

    def MoveIndexToLeft(self, index):
        index = max(index - 1, 0)
        return index

    def _GetSizeForHistoryMenu(self):
        return self.GetAbsolute()

    def OnSetFocus(self, *args):
        if self.pickState != uiconst.TR2_SPS_ON:
            return
        if not self.readonly and uicore.imeHandler:
            uicore.imeHandler.SetFocus(self)
        if self and not self.destroyed and self.parent and self.parent.name == 'inlines':
            if self.parent.parent and getattr(self.parent.parent.sr, 'node', None):
                browser = GetBrowser(self)
                if browser:
                    uthread.new(browser.ShowObject, self)
        self._OnSetFocus()
        self.ShowCaret()
        self.CheckHintText()
        if self.autoselect:
            self.SelectAll()
        else:
            self.RefreshSelectionDisplay()
        if hasattr(self, '__OnSetFocus') and self.__OnSetFocus:
            self.__OnSetFocus(*args)

    def _OnSetFocus(self):
        pass

    def Cut(self, *args):
        if self.GetSelectionBounds() != (None, None):
            self.Copy()
            self.DeleteSelected()

    def Copy(self, selectStart = None, selectEnd = None):
        if selectStart is not None and selectEnd is not None:
            blue.pyos.SetClipboardData(self.text[selectStart:selectEnd])
        else:
            start, end = self.GetSelectionBounds()
            if not start and not end:
                blue.pyos.SetClipboardData(self.text)
            else:
                blue.pyos.SetClipboardData(self.text[start[0]:end[0]])

    def Paste(self, paste, deleteStart = None, deleteEnd = None, forceFocus = False):
        if deleteStart is None or deleteEnd is None:
            start, end = self.GetSelectionBounds()
            if start is not None and end is not None:
                self.DeleteSelected()
        else:
            text = self.text
            self.SetText(text[:deleteStart] + text[deleteEnd:])
            self.caretIndex = self.GetCursorFromIndex(deleteStart)
            self.OnTextChange()
        self.Insert(paste)
        hadFocus = uicore.registry.GetFocus() is self
        if (hadFocus or forceFocus) and not uicore.registry.GetFocus() == self:
            uicore.registry.SetFocus(self)

    def SelectAll(self):
        self.selFrom = self.GetCursorFromIndex(0)
        self.selTo = self.GetCursorFromIndex(-1)
        self.RefreshSelectionDisplay()

    def ShowCaret(self):
        self.ConstructCaret()
        self.RefreshCaretPosition()
        fontSize = check_convert_font_size(self.fontsize)
        self.caret.height = fontSize + 4
        self.caret.state = uiconst.UI_DISABLED
        self.caretTimer = AutoTimer(interval=uiconst.CARET_BLINK_INTERVAL_MS, method=self.BlinkCaret)
        self.caret.SetRGBA(*self.CaretColor)

    def HideCaret(self):
        self.caretTimer = None
        if self.caret:
            self.caret.state = uiconst.UI_HIDDEN

    def BlinkCaret(self):
        if self.destroyed:
            self.caretTimer = None
            return
        if self.caret:
            if not trinity.app.IsActive():
                self.caret.state = uiconst.UI_HIDDEN
                return
            self.caret.state = [uiconst.UI_HIDDEN, uiconst.UI_DISABLED][self.caret.state == uiconst.UI_HIDDEN]

    def SelectNone(self):
        self.selFrom = (None, None)
        self.selTo = (None, None)
        self.RefreshSelectionDisplay()

    def OnAnyChar(self, char, *args):
        return True

    def OnKillFocus(self, *args):
        if not self.readonly and uicore.imeHandler:
            uicore.imeHandler.KillFocus(self)
        if self.autoselect:
            self.SelectNone()
        self.HideCaret()
        self.CheckHintText()
        self.CloseHistoryMenu()
        self.ClearSelection()
        if self.OnFocusLost:
            uthread.new(self.OnFocusLost, self)

    def Insert(self, text):
        if self.readonly or text is None:
            return
        if not isinstance(text, basestring):
            text = unichr(text)
        text = text.replace(u'\r', u' ').replace(u'\n', u'')
        if self.GetSelectionBounds() != (None, None):
            self.DeleteSelected()
        caretIndex = self.caretIndex[0] if self.caretIndex else 0
        before = self.text[:caretIndex]
        after = self.text[caretIndex:]
        become = before + text + after
        become = self._ValidateInsert(become)
        self.autoselect = False
        self.SetText(become)
        if become != before:
            newCaretIndex = caretIndex + max(len(text), 1)
            self.caretIndex = self.GetCursorFromIndex(newCaretIndex)
        self.OnTextChange()

    def _ValidateInsert(self, insert):
        return insert

    def ShowHistoryMenu(self, history):
        hadMenu = 0
        if self.historyMenu and self.historyMenu():
            hadMenu = 1
        self.CloseHistoryMenu()
        if not history:
            return
        currentText = self.GetValue(registerHistory=False)
        l, t, w, h = self._GetSizeForHistoryMenu()
        mp = SingleLineEditHistory(parent=uicore.layer.menu, pos=(l,
         t + h + 2,
         w,
         0), dynamicHistoryWidth=self.dynamicHistoryWidth, mouseDownFunc=self.HEMouseDown, mouseUpFunc=self.HEMouseUp, currentText=currentText)
        if not hadMenu:
            mp.opacity = 0.0
        self.PopulateHistoryMenu(mp, history)
        self.historyMenu = weakref.ref(mp)
        if not hadMenu:
            animations.FadeIn(mp, duration=0.25)

    def OnDblClick(self, *args):
        self.caretIndex = self.GetIndexUnderCursor()
        self.selFrom = self.GetCursorFromIndex(0)
        self.selTo = self.caretIndex = self.GetCursorFromIndex(-1)
        self.RefreshCaretPosition()
        self.RefreshSelectionDisplay()
        self.RefreshTextClipper()

    def GetIndexUnderCursor(self):
        l, t = self.textLabel.GetAbsolutePosition()
        cursorXpos = uicore.uilib.x - l
        return self.textLabel.GetIndexUnderPos(cursorXpos)

    def PopulateHistoryMenu(self, menuParent, history):
        historyFormatted = []
        for historyEntry in history:
            if isinstance(historyEntry, tuple):
                displayText = historyEntry[0]
                editText = historyEntry[1]
            else:
                displayText = editText = historyEntry
            b = Bundle(displayText=displayText, editText=editText, info=None, historyEntry=historyEntry)
            historyFormatted.append(b)

        menuParent.PopulateHistoryMenu(historyFormatted)

    def BrowseHistory(self, down):
        justopened = 0
        if not (self.historyMenu and self.historyMenu()):
            if not self.CheckHistory():
                return
            justopened = 1
        hm = self.historyMenu()
        currentIdx = None
        i = 0
        for entry in hm.sr.entries.children:
            if entry.selected:
                currentIdx = i
            entry.sr.hilite.state = uiconst.UI_HIDDEN
            entry.selected = 0
            i += 1

        if justopened:
            return
        if currentIdx is None:
            if down:
                currentIdx = 0
            else:
                currentIdx = len(hm.sr.entries.children) - 1
        elif down:
            currentIdx += 1
            if currentIdx >= len(hm.sr.entries.children):
                currentIdx = 0
        else:
            currentIdx -= 1
            if currentIdx < 0:
                currentIdx = len(hm.sr.entries.children) - 1
        self.active = active = hm.sr.entries.children[currentIdx]
        active.sr.hilite.state = uiconst.UI_DISABLED
        active.selected = 1
        if not getattr(self, 'blockSetValue', 0):
            self.SetValue(active.string)

    def HEMouseDown(self, entry, mouseButton, *args):
        if mouseButton == uiconst.MOUSELEFT:
            self.SetValue(entry.string)
            self.OnHistoryClick(entry.string)

    def HEMouseUp(self, entry, mouseButton, *args):
        if mouseButton == uiconst.MOUSELEFT:
            self.CloseHistoryMenu()

    def OnHistoryClick(self, clickedString, *args):
        pass

    def OnMouseUp(self, *args):
        self.mouseDownCaretIndex = None
        self.selectionTimer = None

    def OnMouseDown(self, button, *etc):
        if uicore.uilib.mouseTravel > 10:
            return
        gettingFocus = uicore.registry.GetFocus() != self
        if gettingFocus:
            uicore.registry.SetFocus(self)
        leftClick = button == uiconst.MOUSELEFT
        if uicore.uilib.Key(uiconst.VK_SHIFT):
            if self.selFrom is None:
                self.selFrom = self.caretIndex
            self.selTo = self.caretIndex = self.GetIndexUnderCursor()
            self.RefreshCaretPosition()
            self.RefreshSelectionDisplay()
            self.RefreshTextClipper()
        elif leftClick:
            self.caretIndex = self.mouseDownCaretIndex = self.GetIndexUnderCursor()
            self.selFrom = None
            self.selTo = None
            self.RefreshCaretPosition()
            self.RefreshSelectionDisplay()
            self.RefreshTextClipper()
            if self.autoselect and gettingFocus:
                self.SelectAll()
            else:
                self.selectionTimer = AutoTimer(50, self.UpdateSelection)

    def UpdateSelection(self):
        oldCaretIndex = self.mouseDownCaretIndex
        newCaretIndex = self.GetIndexUnderCursor()
        self.selFrom = oldCaretIndex
        self.selTo = newCaretIndex
        self.caretIndex = newCaretIndex
        self.RefreshCaretPosition()
        self.RefreshSelectionDisplay()
        self.RefreshTextClipper()

    def CheckHistory(self):
        if not self.displayHistory:
            return
        if self.readonly:
            return
        validHistoryEntries = self.GetValid()
        if validHistoryEntries:
            self.ShowHistoryMenu(validHistoryEntries[:5])
            return 1
        self.CloseHistoryMenu()
        return 0

    def GetHistory(self, getAll = False):
        historyID = self.GetHistoryID()
        editHistory = settings.user.ui.Get('editHistory', {})
        suggestions = self.GetSuggestions()
        if suggestions is None:
            suggestions = editHistory.get(historyID, [])
        if getAll:
            return (historyID, suggestions, editHistory)
        return (historyID, suggestions)

    def GetHistoryID(self):
        id = ''
        item = self
        while item.parent:
            id = '/' + item.name + id
            if isinstance(item, Window):
                break
            item = item.parent

        return id

    def GetSuggestions(self):
        return None

    def DeleteFromHistory(self, currentText, historyEntry):
        _, history = self.GetHistory()
        if historyEntry in history:
            history.remove(historyEntry)
            self.CloseHistoryMenu()
            if not getattr(self, 'blockSetValue', 0):
                self.SetValue(currentText)
            self.CheckHistory()
            return True
        return False

    def SetReadOnly(self, state):
        self.readonly = state

    def Delete(self, direction = True):
        if self.readonly or self.text is None:
            return
        if not self.caretIndex:
            logger.exception('BaseSingleLineEdit::Delete failed, caretIndex is None')
            return
        caretIndex = self.caretIndex[0] if self.caretIndex else 0
        if direction:
            begin = caretIndex
            end = min(caretIndex + 1, len(self.textLabel.text))
        else:
            begin = max(caretIndex - 1, 0)
            end = caretIndex
        newText = self.text[:begin] + self.text[end:]
        self.SetText(newText)
        newCaretIndex = begin
        self.caretIndex = self.GetCursorFromIndex(newCaretIndex)
        self.OnTextChange()

    def DeleteSelected(self, inserting = False):
        if self.readonly:
            return
        start, end = self.GetSelectionBounds()
        self.ClearSelection()
        text = self.text
        newText = text[:start[0]] + text[end[0]:]
        self.SetText(newText)
        self.caretIndex = self.GetCursorFromIndex(start[0])
        self.OnTextChange()

    def OnClearButtonClick(self):
        self.Clear()

    def OnClear(self):
        pass

    def SetValue(self, text, docallback = True):
        self.draggedValue = None
        if text is None:
            return
        text = self.SanitizeText(text)
        self.SetText(text)
        self.SendCaretToEnd()
        self.ClearSelection()
        self.OnTextChange(docallback)

    def Clear(self, docallback = True):
        self.SetText('')
        self.SendCaretToEnd()
        self.ClearSelection()
        self.OnTextChange(docallback)
        self.OnClear()

    def SanitizeText(self, text):
        isString = isinstance(text, basestring)
        if isString:
            text = StripTags(text, stripOnly=['localized'])
        return text

    def ClearSelection(self):
        self.selFrom = self.selTo = None
        self.RefreshSelectionDisplay()

    def GetCursorFromIndex(self, index):
        return self.textLabel.GetWidthToIndex(index)

    def SendCaretToEnd(self):
        self.caretIndex = self.GetCursorFromIndex(-1)

    def SetText(self, text):
        if not isinstance(text, basestring):
            text = str(text)
        text = StripTags(text, stripOnly=['localized'])
        self.SetDisplayText(text.replace('<', '&lt;').replace('>', '&gt;'))
        self.text = text
        self.CheckHintText()

    def SetDisplayText(self, text):
        self.textLabel.SetText(text)

    def OnTextChange(self, docallback = True):
        self.CheckHintText()
        self.RefreshCaretPosition()
        self.RefreshTextClipper()
        if docallback and self.OnChange:
            self.OnChange(self.GetText())
        RefreshTooltipForOwner(self)

    def CheckHintText(self):
        if self.text:
            self.hintLabel.display = False
        elif uicore.registry.GetFocus() is self:
            self.hintLabel.color = TextColor.DISABLED
            self.hintLabel.display = True
        else:
            self.hintLabel.color = TextColor.SECONDARY
            self.hintLabel.display = True
        self.hintLabel.SetText(self.hintText)

    def GetText(self):
        return self.text

    def GetValue(self, registerHistory = True):
        if registerHistory:
            self.RegisterHistory()
        return self.text

    def GetMenu(self):
        m = []
        start, end = self.GetSelectionBounds()
        if start is not None:
            start = start[0]
        if end is not None:
            end = end[0]
        m += [(MenuLabel('/Carbon/UI/Controls/Common/Copy'), self.Copy, (start, end))]
        if not self.readonly:
            paste = GetClipboardData()
            if paste:
                m += [(MenuLabel('/Carbon/UI/Controls/Common/Paste'), self.Paste, (paste,
                   start,
                   end,
                   True))]
        return m

    def OnDropData(self, dragObj, nodes):
        if self.isTypeField:
            self.OnDropType(dragObj, nodes)
        elif self.isLocationField:
            self.OnDropLocation(dragObj, nodes)
        elif self.isCharCorpOrAllianceField:
            self.OndDropCharCorpOrAlliance(dragObj, nodes)
        elif self.isCharacterField:
            self.OnDropCharacter(dragObj, nodes)
        else:
            super(BaseSingleLineEdit, self).OnDropData(dragObj, nodes)

    def OnDropType(self, dragObj, nodes):
        node = nodes[0]
        guid = getattr(node, '__guid__', None)
        if guid in ('xtriui.ShipUIModule', 'xtriui.InvItem', 'listentry.InvItem', 'listentry.InvAssetItem'):
            typeID = getattr(node.item, 'typeID', None)
        elif guid in ('listentry.GenericMarketItem', 'listentry.QuickbarItem', 'listentry.Item'):
            typeID = getattr(node, 'typeID', None)
        else:
            typeID = GetTypeIDFromDragItem(node)
        if typeID and evetypes.IsPublished(typeID):
            typeName = evetypes.GetName(typeID)
            self.SetValueAfterDragging(typeName, draggedValue=typeID)

    def OnDropLocation(self, dragObj, nodes):
        node = nodes[0]
        guid = node.Get('__guid__', None)
        locationItemID = None
        itemID = GetItemIDFromTextLink(node, None)
        if self._IsLocation(itemID):
            locationItemID = itemID
        elif guid in ('xtriui.ListSurroundingsBtn', 'listentry.LocationTextEntry', 'listentry.LabelLocationTextTop', 'listentry.LocationGroup', 'listentry.LocationSearchItem'):
            if self._IsLocation(node.itemID):
                locationItemID = node.itemID
        if locationItemID:
            self.SetValueAfterDragging(cfg.evelocations.Get(locationItemID).name, locationItemID)

    def _IsLocation(self, itemID):
        if not itemID:
            return False
        try:
            cfg.evelocations.Get(itemID)
            return True
        except KeyError:
            return False

    def OnDropCharacter(self, dragObj, nodes):
        charInfo = GetDroppedCharInfo(nodes[0])
        if charInfo is not None:
            self.SetValueAfterDragging(charInfo.charName, charInfo.charID)

    def OndDropCharCorpOrAlliance(self, dragObj, nodes):
        itemInfo = GetDroppedCharCorpOrAllianceName(nodes[0])
        if itemInfo is not None:
            self.SetValueAfterDragging(itemInfo.itemName, itemInfo.itemID)

    def SetValueAfterDragging(self, name, draggedValue):
        self.SetValue(name)
        self.draggedValue = draggedValue

    def LoadTooltipPanel(self, tooltipPanel, *args):
        normalHint = self.hint
        if self.inputType:
            return LoadTooltipForNumber(tooltipPanel, normalHint, self.text, self.inputType)

    def Disable(self):
        super(BaseSingleLineEdit, self).Disable()
        self.opacity = 0.3

    def Enable(self):
        super(BaseSingleLineEdit, self).Enable()
        self.opacity = 1.0

    def SetMaxLength(self, newMaxLength):
        pass

    def LoadCombo(self, id, options, callback = None, setvalue = None, comboIsTabStop = True):
        for each in self.children[:]:
            if each.name == 'combo':
                each.Close()

        combo = Combo(parent=self, label='', options=options, name=id, select=setvalue, callback=self.OnComboChange, pos=(0, 0, 16, 16), align=uiconst.BOTTOMRIGHT)
        combo.sr.inputCallback = callback
        combo.isTabStop = comboIsTabStop
        combo.name = 'combo'
        combo.Confirm = self.ComboConfirm
        combo.Hide()
        self.sr.combo = combo
        comboButton = self.AddIconButton('res:/UI/Texture/Icons/38_16_229.png')
        comboButton.name = 'combo'
        comboButton.OnMouseDown = (self.ExpandCombo, combo)

    def ExpandCombo(self, combo, *args, **kwds):
        if not combo._Expanded():
            uthread.new(combo.Expand, self.GetAbsolute())

    def ComboConfirm(self, *args, **kwargs):
        if self.sr.combo and not self.sr.combo.destroyed:
            self.OnComboChange(self.sr.combo, self.sr.combo.GetKey(), self.sr.combo.GetValue())
        self.sr.combo.Cleanup(setfocus=False)

    def GetComboValue(self):
        if self.sr.combo:
            return self.sr.combo.GetValue()

    def OnComboChange(self, combo, label, value, *args):
        self.SetValue(label)
        if combo.sr.inputCallback:
            combo.sr.inputCallback(combo, label, value)

    def Close(self):
        self.CloseHistoryMenu()
        super(BaseSingleLineEdit, self).Close()

    def get_absolute_caret_position(self):
        y = self.absoluteTop + 2
        x = self.absoluteLeft + self.caretIndex[1] - 1 + self.textLabel.left
        return (x, y)
