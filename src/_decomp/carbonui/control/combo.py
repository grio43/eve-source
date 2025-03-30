#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\control\combo.py
import logging
import random
import weakref
import blue
import eveformat
import eveicon
import localization
import uthread
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui import fontconst, uiconst
from carbonui.button import styling
from carbonui.button.const import HEIGHT_NORMAL
from carbonui.control.comboEntries import ComboCaptionEntry, ComboEntry, ComboSeparatorEntry
from carbonui.control.comboEntryData import BaseComboEntryData, ComboEntryData, ComboEntryDataCaption, ComboEntryDataSeparator, ComboEntryDataText
from carbonui.control.contextMenu.menuUtil import ClearMenuLayer
from carbonui.control.scrollentries import ScrollEntryNode
from carbonui.primitives.container import Container
from carbonui.primitives.frame import Frame
from carbonui.primitives.line import Line
from carbonui.text.color import TextColor
from carbonui.uianimations import animations
from carbonui.uiconst import Density
from carbonui.uicore import uicore
from carbonui.util.color import Color
from carbonui.util.various_unsorted import GetAttrs, GetBrowser
from eve.client.script.ui import eveColor
from eve.client.script.ui.control import eveLabel
from carbonui.decorative.blurredSceneUnderlay import BlurredSceneUnderlay
from carbonui.control.buttonIcon import ButtonIcon
from eve.client.script.ui.control.entries.text import Text
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.control.eveScroll import Scroll
from eve.client.script.ui.control.glowSprite import GlowSprite
log = logging.getLogger(__name__)
OPACITY_TEXT_IDLE = TextColor.NORMAL.opacity
OPACITY_TEXT_HOVER = 1.0
ALIGNMENTS_THAT_DONT_SUPPORT_AUTO_WIDTH = (uiconst.TOTOP,
 uiconst.TOBOTTOM,
 uiconst.TOALL,
 uiconst.TOLEFT_PROP,
 uiconst.TORIGHT_PROP)

class Combo(Container):
    default_adjustWidth = True
    default_align = uiconst.TOPLEFT
    default_callback = None
    default_cursor = uiconst.UICURSOR_SELECT
    default_fontFamily = None
    default_fontPath = None
    default_fontStyle = None
    default_fontsize = fontconst.EVE_MEDIUM_FONTSIZE
    default_hasClearButton = False
    default_iconOnly = False
    default_label = ''
    default_labelleft = None
    default_maxVisibleEntries = 8
    default_name = 'combo'
    default_noChoiceLabel = None
    default_nothingSelectedText = ''
    default_options = []
    default_prefskey = None
    default_select = None
    default_state = uiconst.UI_NORMAL
    default_width = 140
    default_height = HEIGHT_NORMAL
    default_density = Density.NORMAL
    isTabStop = 1
    _hovered = False

    def ApplyAttributes(self, attributes):
        self._comboDropDown = None
        self._disabled = False
        self._expanding = False
        self.clearButton = None
        self.selectedValue = None
        self.sr.label = None
        self._entries = None
        super(Combo, self).ApplyAttributes(attributes)
        self.adjustWidth = attributes.get('adjustWidth', self.default_adjustWidth)
        if self.align not in ALIGNMENTS_THAT_DONT_SUPPORT_AUTO_WIDTH and attributes.get('width', 0) > 0:
            self.adjustWidth = False
        self.prefskey = attributes.get('prefskey', self.default_prefskey)
        self.fontStyle = attributes.get('fontStyle', self.default_fontStyle)
        self.fontFamily = attributes.get('fontFamily', self.default_fontFamily)
        self.fontPath = attributes.get('fontPath', self.default_fontPath)
        self.fontsize = attributes.get('fontsize', self.default_fontsize)
        self.iconOnly = attributes.get('iconOnly', self.default_iconOnly)
        self.density = attributes.get('density', self.default_density)
        options = attributes.get('options', self.default_options)
        select = attributes.get('select', self.default_select)
        self.maxVisibleEntries = attributes.get('maxVisibleEntries', self.default_maxVisibleEntries)
        self.noChoiceLabel = attributes.Get('noChoiceLabel', self.default_noChoiceLabel)
        self.nothingSelectedText = attributes.Get('nothingSelectedText', self.default_nothingSelectedText)
        self.color = attributes.get('color', self.default_bgColor)
        self.hasClearButton = attributes.get('hasClearButton', self.default_hasClearButton)
        self.labelleft = attributes.get('labelleft', self.default_labelleft)
        self.OnChange = attributes.get('callback', self.default_callback)
        self.Prepare_()
        self.SetLabel_(attributes.get('label', self.default_label))
        self.LoadOptions(options, select)
        if self.adjustWidth and self.align not in ALIGNMENTS_THAT_DONT_SUPPORT_AUTO_WIDTH:
            self.AutoAdjustWidth_()
        elif self.align == uiconst.TOALL:
            self.width = 0
        else:
            self.width = attributes.get('width', self.default_width)
        if self.align in (uiconst.TOLEFT, uiconst.TORIGHT, uiconst.TOALL):
            self.height = 0
        else:
            self.height = styling.get_height(self.density)

    def Prepare_(self):
        self.sr.content = Container(parent=self, name='__maincontent')
        self.sr.iconParent = Container(parent=self.sr.content, name='iconParent', align=uiconst.TOLEFT, width=24, state=uiconst.UI_HIDDEN)
        self.sr.selectedIcon = Icon(name='icon', parent=self.sr.iconParent, align=uiconst.CENTERRIGHT, state=uiconst.UI_DISABLED, width=16, height=16)
        self.sr.textclipper = Container(name='__textclipper', parent=self.sr.content, align=uiconst.TOALL, padLeft=8, clipChildren=True)
        self.Prepare_SelectedText_()
        self.Prepare_Expander_()
        self.Prepare_Underlay_()
        self.Prepare_Label_()

    def Prepare_SelectedText_(self):
        self.sr.selected = eveLabel.EveLabelMedium(name='value', parent=self.sr.textclipper, align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED, color=self._get_selected_color(), autoFadeSides=16)

    def Prepare_Underlay_(self):
        self.sr.backgroundFrame = ComboUnderlay(parent=self, align=uiconst.TOALL)

    def Select(self, animate = True):
        self.sr.backgroundFrame.Select()

    def Deselect(self, animate = True):
        self.sr.backgroundFrame.Deselect()

    def Disable(self):
        self._disabled = True
        self.sr.backgroundFrame.SetDisabled()
        self._update_selected_color()

    def Enable(self):
        self._disabled = False
        self.sr.backgroundFrame.SetEnabled()
        self._update_selected_color()

    def Prepare_Expander_(self):
        self.sr.expanderParent = Container(name='__expanderParent', parent=self.sr.content, align=uiconst.TORIGHT, state=uiconst.UI_DISABLED, width=16, padding=(8, 0, 8, 0), idx=0)
        self.sr.expander = GlowSprite(parent=self.sr.expanderParent, align=uiconst.CENTER, texturePath='res:/UI/Texture/Icons/38_16_229.png', pos=(0, 0, 16, 16), opacity=0.8)

    def Prepare_Label_(self):
        self.sr.label = eveLabel.EveLabelSmall(text='', parent=self, name='label', top=-13, left=1, state=uiconst.UI_HIDDEN, idx=1, lineSpacing=-0.1)

    def HideText(self):
        self.sr.textclipper.state = uiconst.UI_HIDDEN

    def Close(self, *args, **kwds):
        self.Cleanup(0)
        super(Combo, self).Close()

    def Confirm(self, setfocus = 1):
        self._TriggerCallback()
        if not self.destroyed:
            self.Cleanup(setfocus)

    def OnUp(self, *args):
        if not self._Expanded():
            self.Expand()
        if self._Expanded():
            self._comboDropDown().sr.scroll.BrowseNodes(1)

    def OnDown(self, *args):
        if not self._Expanded():
            self.Expand()
        if self._Expanded():
            self._comboDropDown().sr.scroll.BrowseNodes(0)

    def SetHint(self, hint):
        self.hint = hint

    def SetLabel_(self, label):
        if self.labelleft is not None:
            self.padLeft = self.labelleft
            self.sr.label.left = -self.labelleft
            self.sr.label.width = self.labelleft - 6
        if label:
            self.sr.label.text = label
            if self.labelleft is not None:
                self.sr.label.top = 0
                self.sr.label.SetAlign(uiconst.CENTERLEFT)
            else:
                self.sr.label.top = -self.sr.label.textheight
            self.sr.label.state = uiconst.UI_DISABLED
        else:
            self.sr.label.state = uiconst.UI_HIDDEN

    def OnSetFocus(self, *args):
        if self and not self.destroyed and self.parent and self.parent.name == 'inlines':
            if self.parent.parent and self.parent.parent.sr.node:
                browser = GetBrowser(self)
                if browser:
                    uthread.new(browser.ShowObject, self)

    def LoadOptions(self, entries, select = None, hints = None):
        self.entries = entries
        screwed = [ each for each in self.entries if not isinstance(each.label, basestring) ]
        if screwed:
            raise RuntimeError('NonStringKeys', repr(screwed))
        if not self.entries:
            self.entries = [ComboEntryDataText(localization.GetByLabel('/Carbon/UI/Controls/Combo/NoChoices'))]
        self.hints = hints
        if not select and self.nothingSelectedText:
            self.SetNothingSelected()
        else:
            self._SelectEntry(select)
        self.AutoAdjustWidth_()

    @property
    def entries(self):
        return self._entries

    @entries.setter
    def entries(self, value):
        self._entries = self._ConvertTuplesToComboEntryData(value)

    def _ConvertTuplesToComboEntryData(self, entries):
        ret = []
        for entry in entries:
            if not isinstance(entry, BaseComboEntryData):
                entry = ComboEntryData(*entry)
            ret.append(entry)

        return ret

    def SetNothingSelected(self):
        self.selectedValue = None
        self.sr.selected.text = self.nothingSelectedText
        self._update_selected_color()

    def _SelectEntry(self, select):
        selectableEntries = self.GetSelectableEntries()
        if not selectableEntries:
            return
        if select == '__random__':
            select = random.choice(selectableEntries).returnValue
        elif select is None:
            select = selectableEntries[0].returnValue
        success = self.SelectItemByValue(select)
        if not success:
            self.SelectItemByValue(selectableEntries[0].returnValue)

    def _UpdateClearButton(self):
        if not self.hasClearButton:
            return
        if self.selectedValue is not None:
            self._CheckConstructClearButton()
            self.clearButton.Show()
        elif self.clearButton:
            self.clearButton.Hide()

    def _CheckConstructClearButton(self):
        if not self.clearButton:
            self.clearButton = ButtonIcon(parent=self, align=uiconst.CENTERRIGHT, left=24, width=24, height=24, iconSize=16, texturePath=eveicon.close, hint=localization.GetByLabel('UI/Calendar/Hints/Clear'), func=self.OnClearButton, idx=0)

    def OnClearButton(self, *args):
        self.SetNothingSelected()
        self._UpdateClearButton()
        self._TriggerCallback()

    def _TriggerCallback(self):
        if self.OnChange:
            uthread.new(self.OnChange, self, self.GetKey(), self.GetValue())

    def AutoAdjustWidth_(self):
        currentAlign = self.GetAlign()
        if self.adjustWidth and self.entries and currentAlign not in ALIGNMENTS_THAT_DONT_SUPPORT_AUTO_WIDTH:
            if self.iconOnly:
                width = self.sr.iconParent.left + self.sr.iconParent.padLeft + self.sr.iconParent.width + self.sr.iconParent.padRight + self.sr.expanderParent.left + self.sr.expanderParent.padLeft + self.sr.expanderParent.width + self.sr.expanderParent.padRight
                if self.hasClearButton:
                    width += self.clearButton.left + self.clearButton.padLeft + self.clearButton.width + self.clearButton.padRight
                self.width = max(width, 32)
            else:
                horizontal_padding = self.sr.textclipper.left + self.sr.textclipper.padLeft + self.sr.textclipper.padRight
                horizontal_padding += self.sr.expanderParent.left + self.sr.expanderParent.padLeft + self.sr.expanderParent.width + self.sr.expanderParent.padRight
                if self.sr.iconParent.display:
                    horizontal_padding += self.sr.iconParent.left + self.sr.iconParent.padLeft + self.sr.iconParent.width + self.sr.iconParent.padRight
                if self.hasClearButton:
                    horizontal_padding += 24
                max_text_width = max((self.GetTextWidth(entry.label) for entry in self.entries))
                self.width = max(32, max_text_width) + horizontal_padding

    def GetKey(self):
        return self.sr.selected.text

    def GetValue(self):
        if self.selectedValue is not None:
            return self.selectedValue
        else:
            return

    def GetIndex(self):
        if self.sr.selected.text:
            i = 0
            for entry in self.GetSelectableEntries():
                if entry.label == self.sr.selected.text:
                    return i
                i += 1

    def GetSelectedEntry(self):
        if self.selectedValue is None:
            return
        for entry in self.GetSelectableEntries():
            if entry.selectedValue == entry.returnValue:
                return entry

    def GetSelectableEntries(self):
        return [ entry for entry in self.entries if isinstance(entry, ComboEntryData) ]

    def SelectItemByIndex(self, i):
        self.SelectItemByLabel(self.GetSelectableEntries()[i].label)

    def SelectItemByLabel(self, label):
        for each in self.GetSelectableEntries():
            if each.label == label:
                self.UpdateSelectedValue(each)
                return

        raise RuntimeError('LabelNotInEntries', label)

    def SelectItemByValue(self, val, triggerCallback = False):
        for each in self.GetSelectableEntries():
            if each.returnValue == val:
                self.UpdateSelectedValue(each)
                if triggerCallback:
                    self._TriggerCallback()
                return True

        log.warn('Combo has no value %s', val)
        return False

    SetValue = SelectItemByValue

    def UpdateSelectedValue(self, entry):
        self.selectedValue = entry.returnValue
        if not self.iconOnly:
            self.sr.selected.text = entry.label
            self._update_selected_color()
        if entry.icon:
            self.sr.selectedIcon.LoadIcon(entry.icon, ignoreSize=True)
            self.sr.selectedIcon.rgba = entry.iconColor
            self.sr.iconParent.state = uiconst.UI_DISABLED
        else:
            self.sr.iconParent.state = uiconst.UI_HIDDEN
        if self.hasClearButton:
            self._UpdateClearButton()

    def UpdateSettings(self):
        prefskey = self.prefskey
        if prefskey is None:
            return
        config = prefskey[-1]
        prefstype = prefskey[:-1]
        s = GetAttrs(settings, *prefstype)
        try:
            s.Set(config, self.GetValue())
        except Exception:
            log.error('Failed to assign setting to: %s, %s' % (prefstype, config))

    def _Expanded(self):
        return bool(self._comboDropDown and self._comboDropDown())

    def OnMouseEnter(self, *args):
        self._hovered = True
        self._update_selected_color(duration=uiconst.TIME_ENTRY)
        if self._disabled:
            return
        self.sr.backgroundFrame.OnMouseEnter()
        self.sr.expander.OnMouseEnter()
        PlaySound(uiconst.SOUND_BUTTON_HOVER)

    def OnMouseExit(self, *args):
        self._hovered = False
        self.sr.backgroundFrame.OnMouseExit()
        self.sr.expander.OnMouseExit()
        self._update_selected_color(duration=uiconst.TIME_EXIT)

    def OnMouseDown(self, *args):
        self.sr.backgroundFrame.OnMouseDown()

    def OnMouseUp(self, *args):
        if self._disabled:
            return
        self.sr.backgroundFrame.OnMouseUp()

    def OnClick(self, *args):
        if self._disabled:
            return
        if not self._Expanded():
            uthread.new(self.Expand)

    def Prepare_OptionMenu_(self):
        ClearMenuLayer()
        self.ConstructOptionMenuContainer()
        self.ConstructOptionMenuScroll()
        self.ConstructOptionMenuBackground()
        return (self.optionMenu, self.optionMenu.sr.scroll)

    def ConstructOptionMenuBackground(self):
        Frame(bgParent=self.optionMenu, texturePath='res:/UI/Texture/classes/combo/underlay_lower_stroke.png', cornerSize=9, color=eveColor.WHITE[:3] + (0.1,))
        BlurredSceneUnderlay(bgParent=self.optionMenu, isInFocus=True, color=Color.HextoRGBA('#ff0b0a12'))

    def ConstructOptionMenuScroll(self):
        self.optionMenu.sr.scroll = self._ConstructOptionMenuScroll()
        self.optionMenu.sr.scroll.OnKillFocus = self.OnScrollFocusLost
        self.optionMenu.sr.scroll.OnSelectionChange = self.OnScrollSelectionChange
        self.optionMenu.sr.scroll.Confirm = self.Confirm
        self.optionMenu.sr.scroll.OnUp = self.OnUp
        self.optionMenu.sr.scroll.OnDown = self.OnDown
        self.optionMenu.sr.scroll.OnRight = self.Confirm
        self.optionMenu.sr.scroll.OnLeft = self.Confirm
        self.optionMenu.sr.scroll.HideBackground()
        self.optionMenu.sr.scroll.padding = (1, 0, 1, 1)

    def _ConstructOptionMenuScroll(self):
        return Scroll(parent=self.optionMenu, pushContent=False)

    def ConstructOptionMenuContainer(self):
        self.optionMenu = Container(parent=uicore.layer.menu, align=uiconst.RELATIVE)

    def GetSelectedIcon(self):
        for each in self.GetSelectableEntries():
            if each.returnValue == self.selectedValue:
                return each.icon

    def GetEntryClass(self):
        return ComboEntry

    def GetTextWidth(self, text):
        width, _ = eveLabel.EveLabelMedium.MeasureTextSize(text)
        return width

    def GetEntryWidth(self, data):
        width = self.GetTextWidth(data['label'])
        if data['icon'] is not None:
            width += 24
        return width

    def GetScrollEntry(self, entryData):
        if isinstance(entryData, ComboEntryData):
            return self._GetScrollEntryData(entryData)
        if isinstance(entryData, ComboEntryDataCaption):
            return self._GetScrollEntryDataCaption(entryData)
        if isinstance(entryData, ComboEntryDataText):
            return self._GetScrollEntryDataText(entryData)
        if isinstance(entryData, ComboEntryDataSeparator):
            return self._GetScrollEntryDataSeparator(entryData)

    def _GetScrollEntryData(self, entryData):
        if not entryData.hint and self.hints:
            hint = self.hints.get(entryData.label, '')
        else:
            hint = entryData.GetHint()
        data = {'OnClick': self.OnEntryClick,
         'data': (entryData.label, entryData.returnValue),
         'label': unicode(entryData.label),
         'fontStyle': self.fontStyle,
         'fontFamily': self.fontFamily,
         'fontPath': self.fontPath,
         'fontsize': self.fontsize,
         'decoClass': self.GetEntryClass(),
         'hideLines': True,
         'icon': entryData.icon,
         'iconColor': entryData.iconColor,
         'indentLevel': entryData.indentLevel,
         'loadTooltipFunc': entryData.GetLoadTooltipFunc(),
         'hint': hint}
        if entryData.returnValue == self.selectedValue:
            data['isSelected'] = True
        return data

    def _GetScrollEntryDataText(self, entryData):
        return {'label': entryData.label,
         'text': entryData.label,
         'icon': entryData.icon,
         'decoClass': Text,
         'hint': entryData.GetHint()}

    def _GetScrollEntryDataCaption(self, entryData):
        return {'label': entryData.label,
         'text': entryData.label,
         'icon': entryData.icon,
         'decoClass': ComboCaptionEntry,
         'hint': entryData.GetHint()}

    def _GetScrollEntryDataSeparator(self, entryData):
        return {'label': entryData.label,
         'text': entryData.label,
         'icon': entryData.icon,
         'decoClass': ComboSeparatorEntry,
         'hint': entryData.GetHint()}

    def GetMaxEntryWidth(self, scrollEntries, w):
        maxWidth = max([ self.GetEntryWidth(entry) for entry in scrollEntries ])
        return max(maxWidth + 24, w)

    def GetScrollList(self):
        scrolllist = []
        if self.noChoiceLabel and len(self.entries) == 1:
            data = {'label': eveformat.color(self.noChoiceLabel, TextColor.SECONDARY),
             'icon': None,
             'selectable': False}
            scrollEntry = ScrollEntryNode(**data)
            scrolllist.append(scrollEntry)
        else:
            for entryData in self.entries:
                label = entryData.label
                if not label:
                    continue
                data = self.GetScrollEntry(entryData)
                scrollEntry = ScrollEntryNode(**data)
                scrolllist.append(scrollEntry)

        return scrolllist

    def Expand(self, position = None):
        if self._expanding:
            return
        try:
            self._expanding = True
            PlaySound(uiconst.SOUND_EXPAND)
            menu, scroll = self.Prepare_OptionMenu_()
            scrolllist = self.GetScrollList()
            scroll.LoadContent(contentList=scrolllist)
            if position:
                l, t, w, h = position
            else:
                l, t, w, h = self.GetAbsolute()
            menu.width = self.GetMaxEntryWidth(scrolllist, w)
            totalHeight = self.GetScrollHeight(scroll)
            menu.height = totalHeight + 2 + scroll.padTop + scroll.padBottom
            menu.left = l
            self.SetMenuTop(menu, t, h)
            self._comboDropDown = weakref.ref(menu)
            uthread.new(self.ShowSelected)
            if hasattr(self.sr.backgroundFrame, 'Expand'):
                self.sr.backgroundFrame.Expand(totalHeight)
            return scroll
        finally:
            self._expanding = False

    def GetScrollHeight(self, scroll):
        return sum([ each.height for each in scroll.sr.nodes[:self.maxVisibleEntries] ])

    def SetMenuTop(self, menu, t, h):
        if t + h + menu.height > uicore.desktop.height:
            menu.top = t - menu.height
        else:
            menu.top = t + h

    def GetExpanderIconWidth(self):
        if self.sr.expanderParent:
            return self.sr.expanderParent.width + self.sr.expanderParent.padLeft + self.sr.expanderParent.padRight
        return 0

    def ShowSelected(self, *args):
        blue.synchro.Yield()
        if self.destroyed or not self._comboDropDown():
            return
        scroll = self._comboDropDown().sr.scroll
        uicore.registry.SetFocus(scroll)
        scroll.ScrollToSelectedNode()

    def OnEntryClick(self, entry, *args):
        PlaySound(uiconst.SOUND_BUTTON_CLICK)
        key, val = entry.sr.node.data
        self.SelectItemByValue(val)
        self.Cleanup()
        if self.OnChange:
            self.OnChange(self, key, val)

    def OnComboClose(self, *args):
        self.Cleanup(0)

    def Cleanup(self, setfocus = 1):
        if self._comboDropDown:
            ClearMenuLayer()
        self._comboDropDown = None
        try:
            self.CollapseBackground()
        except Exception:
            log.exception("Failed to collapse the Combo's background")

        if setfocus:
            uicore.registry.SetFocus(self)

    def OnScrollFocusLost(self, *args):
        self.Confirm(setfocus=False)

    def CollapseBackground(self):
        if hasattr(self.sr.backgroundFrame, 'Collapse'):
            self.sr.backgroundFrame.Collapse()

    def OnScrollSelectionChange(self, selected):
        if selected:
            self.SelectItemByLabel(selected[0].label)

    def OnChar(self, enteredChar, *args):
        if enteredChar < 32 and enteredChar != uiconst.VK_RETURN:
            return False
        if not self._Expanded():
            scroll = self.Expand()
            scroll.OnChar(enteredChar, *args)
        return True

    def Startup(self, *args):
        pass

    def _get_selected_color(self):
        if self._disabled:
            return TextColor.DISABLED
        elif self._hovered:
            return TextColor.HIGHLIGHT
        elif self.selectedValue is None:
            return TextColor.SECONDARY
        else:
            return TextColor.NORMAL

    def _update_selected_color(self, duration = 0.3):
        animations.SpColorMorphTo(self.sr.selected, endColor=self._get_selected_color(), duration=duration)


class SelectCore(Scroll):

    def LoadEntries(self, entries):
        scrolllist = []
        for entryName, entryValue, selected in entries:
            scrolllist.append(ScrollEntryNode(label=entryName, value=entryValue, isSelected=selected))

        self.LoadContent(contentList=scrolllist)

    def GetValue(self):
        return [ node.value for node in self.GetSelected() ] or None

    def SetValue(self, val):
        if type(val) != list:
            val = [val]
        for node in self.GetNodes():
            if node.value in val:
                self._SelectNode(node)


class ComboUnderlay(Container):

    def __init__(self, parent = None, align = uiconst.TOALL):
        super(ComboUnderlay, self).__init__(parent=parent, align=align)
        self.strokeFrame = Frame(parent=self, texturePath='res:/UI/Texture/classes/combo/underlay_stroke.png', cornerSize=9, color=eveColor.WHITE[:3] + (0.1,))
        self.fillFrame = Frame(parent=self, texturePath='res:/UI/Texture/classes/combo/underlay_fill.png', cornerSize=9, color=eveColor.BLACK[:3] + (0.1,))
        self.line = Line(parent=Container(parent=self, padding=(8, 0, 8, 0)), align=uiconst.TOBOTTOM, state=uiconst.UI_HIDDEN, height=1, color=eveColor.WHITE[:3] + (0.1,))
        self.fill = BlurredSceneUnderlay(parent=self, align=uiconst.TOALL, state=uiconst.UI_HIDDEN, isInFocus=True, color=Color.HextoRGBA('#ff0b0a12'))

    def Expand(self, height):
        self.strokeFrame.texturePath = 'res:/UI/Texture/classes/combo/underlay_upper_stroke.png'
        self.fillFrame.Hide()
        self.line.Show()
        self.fill.Show()

    def Collapse(self):
        self.strokeFrame.texturePath = 'res:/UI/Texture/classes/combo/underlay_stroke.png'
        self.fillFrame.Show()
        self.line.Hide()
        self.fill.Hide()

    def SetEnabled(self):
        pass

    def SetDisabled(self):
        pass

    def OnMouseEnter(self):
        pass

    def OnMouseExit(self):
        pass

    def OnMouseDown(self):
        pass

    def OnMouseUp(self):
        pass

    def OnWindowAboveSetActive(self):
        animations.FadeTo(self.fillFrame, startVal=self.fillFrame.opacity, endVal=0.5, duration=uiconst.TIME_ENTRY)

    def OnWindowAboveSetInactive(self):
        animations.FadeTo(self.fillFrame, startVal=self.fillFrame.opacity, endVal=0.1, duration=uiconst.TIME_EXIT)
