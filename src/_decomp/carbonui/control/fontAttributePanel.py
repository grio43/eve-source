#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\control\fontAttributePanel.py
import localization
import telemetry
from carbon.client.script.environment.AudioUtil import PlaySound
from carbon.common.script.util.commonutils import StripTags
from carbonui import uiconst
from carbonui.control.combo import Combo
from carbonui.control.editPlainText import EditPlainTextCore
from carbonui.control.label import LabelOverride as Label
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.text.color import TextColor
from carbonui.uicore import uicore
from eve.client.script.ui.shared.dropdownColorPicker import DropdownColorPicker

class FontAttributePanel(Container):
    __guid__ = 'uicontrols.FontAttribPanel'
    default_height = 32

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.counterMax = attributes.counterMax
        self.countWithTags = attributes.countWithTags
        self.boldBtn = LabelButton(text=localization.GetByLabel('/Carbon/UI/Controls/EditRichText/BoldSymbol'), parent=self, width=12, align=uiconst.TOLEFT, fontsize=14, padLeft=4, state=uiconst.UI_NORMAL, func=self.ToggleBold, hint=localization.GetByLabel('/Carbon/UI/Controls/EditRichText/Bold'))
        self.italicBtn = LabelButton(text=localization.GetByLabel('/Carbon/UI/Controls/EditRichText/ItalicSymbol'), parent=self, pos=(0, 0, 12, 0), align=uiconst.TOLEFT, fontsize=14, state=uiconst.UI_NORMAL, func=self.ToggleItalic, minWidth=10, hint=localization.GetByLabel('/Carbon/UI/Controls/EditRichText/Italic'))
        self.underlineBtn = LabelButton(text=localization.GetByLabel('/Carbon/UI/Controls/EditRichText/UnderlineSymbol'), parent=self, pos=(0, 0, 12, 0), align=uiconst.TOLEFT, fontsize=14, state=uiconst.UI_NORMAL, func=self.ToggleUnderline, hint=localization.GetByLabel('/Carbon/UI/Controls/EditRichText/Underline'))
        self.colorPicker = EditTextColorPickerCont(parent=self, pos=(0, 0, 12, 12), callback=self.SetColorForLabel, align=uiconst.TOLEFT, padLeft=4)
        options = [[localization.formatters.FormatNumeric(8), 8],
         [localization.formatters.FormatNumeric(9), 9],
         [localization.formatters.FormatNumeric(10), 10],
         [localization.formatters.FormatNumeric(11), 11],
         [localization.formatters.FormatNumeric(12), 12],
         [localization.formatters.FormatNumeric(13), 13],
         [localization.formatters.FormatNumeric(14), 14],
         [localization.formatters.FormatNumeric(18), 18],
         [localization.formatters.FormatNumeric(24), 24],
         [localization.formatters.FormatNumeric(30), 30],
         [localization.formatters.FormatNumeric(36), 36]]
        self.fontSizeCombo = Combo(parent=self, options=options, name='fontsize', select=12, callback=self.OnFontSizeChange, align=uiconst.TOLEFT, width=56, padding=(8, 4, 0, 4), hint=localization.GetByLabel('/Carbon/UI/Controls/EditRichText/FontSize'))
        self.urlBtn = LabelButton(name='anchor', text=localization.GetByLabel('/Carbon/UI/Controls/EditRichText/LinkSymbol'), parent=self, align=uiconst.TOLEFT, fontsize=10, state=uiconst.UI_NORMAL, func=self.OnAnchorBtn, padding=(4, 0, 4, 0), hint=localization.GetByLabel('/Carbon/UI/Controls/EditRichText/AddLink'))
        self.clearBtn = LabelButton(name='clearnote', text=localization.GetByLabel('/Carbon/UI/Controls/EditRichText/ClearTextSymbol'), parent=self, width=12, align=uiconst.TOLEFT, hint=localization.GetByLabel('/Carbon/UI/Controls/EditRichText/ClearText'), fontsize=14, state=uiconst.UI_NORMAL, func=self.ClearNote)
        self.clearBtn.hint = localization.GetByLabel('/Carbon/UI/Controls/EditRichText/ClearText')
        if self.counterMax is not None:
            self.charCounter = Label(text='0/%s' % self.counterMax, parent=self, color=(1.0, 1.0, 1.0, 0.6), fontsize=12, left=4, align=uiconst.CENTERRIGHT, state=uiconst.UI_NORMAL)
        self.expanding = 0
        self.expanded = 0

    def OnAnchorBtn(self):
        PlaySound(uiconst.SOUND_BUTTON_CLICK)
        return self.AddAnchor()

    def ClearNote(self, *args):
        PlaySound(uiconst.SOUND_BUTTON_CLICK)
        response = uicore.Message('ConfirmClearText', {}, uiconst.YESNO, uiconst.ID_YES)
        if response == uiconst.ID_YES:
            self.parent.SetValue('')
        uicore.registry.SetFocus(self.parent)

    def ToggleBold(self, *args):
        self.parent.ToggleBold()

    def ToggleUnderline(self, *args):
        self.parent.ToggleUnderline()

    def ToggleItalic(self, *args):
        self.parent.ToggleItalic()

    def AddAnchor(self, *args):
        self.parent.AddAnchor()

    def OnFontSizeChange(self, entry, header, value, *args):
        self.parent.ChangeFontSize(value)

    def AttribStateChange(self, bold, italic, underline, size, color, url, *args):
        self.boldBtn.SetHighlighted(bold)
        self.italicBtn.SetHighlighted(italic)
        self.underlineBtn.SetHighlighted(underline)
        self.colorPicker.SetCurrentFill(color)
        self.fontSizeCombo.SelectItemByValue(size)
        self.urlBtn.SetHighlighted(bool(url))

    def ShowOrHideCharacterCounter(self, showCounter = True):
        if getattr(self, 'charCounter', None) is None:
            return
        self.charCounter.display = showCounter

    @telemetry.ZONE_METHOD
    def UpdateCounter(self, currentCount = None, *args):
        if getattr(self, 'charCounter', None) is None or self.parent is None:
            return
        parent = self.parent
        if currentCount is not None:
            currentLen = currentCount
        elif self.countWithTags:
            currentLen = len(parent.GetValue())
            self._currentLen = currentLen
        elif isinstance(parent, EditPlainTextCore):
            currentLen = len(parent.GetAllText())
        else:
            currentLen = len(StripTags(parent.GetSelectedText(getAll=True)))
        currentLenText = currentLen
        hint = ''
        if currentLen > self.counterMax:
            currentLenText = '<color=red>%s</color>' % currentLenText
            hint = localization.GetByLabel('UI/Notepad/TooLongText')
        self.charCounter.text = '%s/%s' % (currentLenText, self.counterMax)
        self.charCounter.hint = hint

    def SetColorForLabel(self, color, *args):
        if color:
            newColor = color + (1.0,)
        else:
            newColor = TextColor.NORMAL
        self.parent.ChangeFontColor(newColor)

    def HideEditOptions(self):
        for eachElement in [self.boldBtn,
         self.italicBtn,
         self.underlineBtn,
         self.colorPicker,
         self.fontSizeCombo,
         self.urlBtn,
         self.clearBtn]:
            eachElement.display = False

        charCounter = getattr(self, 'charCounter', None)
        if charCounter:
            charCounter.left = 0


class LabelButton(ContainerAutoSize):
    default_padLeft = 1
    default_padRight = 1
    default_minWidth = 10

    def ApplyAttributes(self, attributes):
        super(LabelButton, self).ApplyAttributes(attributes)
        self.isHighlited = False
        self.label = Label(parent=self, align=uiconst.CENTER, text=attributes.text, fontsize=attributes.fontsize, uppercase=attributes.uppercase, opacity=1.0)
        self.func = attributes.func
        self.hint = attributes.hint

    def OnMouseEnter(self):
        self.UpdateOpacity()
        PlaySound(uiconst.SOUND_BUTTON_HOVER)

    def OnMouseExit(self):
        self.UpdateOpacity()

    def OnClick(self):
        PlaySound(uiconst.SOUND_BUTTON_CLICK)
        self.func()

    def SetHighlighted(self, isHighlighted):
        self.isHighlited = isHighlighted
        self.UpdateOpacity()

    def UpdateOpacity(self):
        if self.isHighlited:
            self.SetOpacity(1.0)
        elif uicore.uilib.mouseOver == self:
            self.SetOpacity(0.8)
        else:
            self.SetOpacity(0.6)


class EditTextColorPickerCont(DropdownColorPicker):
    __guid__ = 'editTextColorPickerCont'
    default_height = 14
    default_width = 14
    default_colorPos = (0, 0, 16, 16)
    default_numColumns = 4
    COLOR_LIST = [(1.0, 1.0, 1.0),
     (0.7, 0.7, 0.7),
     (0.3, 0.3, 0.3),
     (0.0, 0.0, 0.0),
     (1.0, 1.0, 0.0),
     (0.0, 1.0, 0.0),
     (1.0, 0.0, 0.0),
     (0.0, 0.0, 1.0),
     (0.5, 0.5, 0.0),
     (0.0, 0.5, 0.0),
     (0.5, 0.0, 0.0),
     (0.0, 0.0, 0.5),
     (0.5, 0.0, 0.5),
     (0.0, 1.0, 1.0),
     (1.0, 0.0, 1.0),
     (0.0, 0.5, 1.0)]

    def ApplyAttributes(self, attributes):
        DropdownColorPicker.ApplyAttributes(self, attributes)
        self.arrowSprite.display = False
        self.colorCont.width = self.width - 2
        self.colorCont.height = self.height - 2
