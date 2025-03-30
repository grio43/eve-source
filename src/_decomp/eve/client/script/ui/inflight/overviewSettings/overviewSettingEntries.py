#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\overviewSettings\overviewSettingEntries.py
from carbon.common.script.sys.serviceConst import ROLE_GML
from carbonui import Density, uiconst
from carbonui.control.combo import Combo
from carbonui.control.radioButton import RadioButton
from carbonui.control.scrollentries import SE_BaseClassCore
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.primitives.line import Line
from carbonui.primitives.sprite import Sprite
from carbonui.uicore import uicore
from carbonui.util.various_unsorted import GetAttrs
from carbonui.control.checkbox import Checkbox
from eve.client.script.ui.control.colorPanel import ColorPanel
from eve.client.script.ui.control.entries.checkbox import CheckboxEntry
from eve.client.script.ui.control.entries.generic import Generic
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.control.infoIcon import MoreInfoIcon
from carbonui.fontconst import EVE_SMALL_FONTSIZE
from eve.client.script.ui.inflight.overviewSettings.overviewColorPicker import OverviewColorPickerCont
from eve.client.script.ui.inflight.overview.overviewConst import PRE, POST, LABEL_TYPE, LABEL_COLOR, LABEL_BOLD, LABEL_ITALIC, LABEL_UNDERLINE, LABEL_SIZE, CHAR_LT, CODE_LT, CHAR_GT, CODE_GT
from eve.client.script.ui.shared.stateFlag import FlagIconWithState
from localization import GetByLabel
from localization.formatters import FormatNumeric
from menu import MenuLabel
import blue
DEFAULT_FONTSIZE = EVE_SMALL_FONTSIZE
POS_INDICATOR_HEIGHT = 2

class DraggableOverviewEntry(CheckboxEntry):
    __guid__ = 'listentry.DraggableOverviewEntry'
    isDragObject = True

    def Startup(self, *args):
        CheckboxEntry.Startup(self, args)
        self.sr.posIndicatorCont = Container(name='posIndicator', parent=self, align=uiconst.TOTOP, state=uiconst.UI_DISABLED, height=POS_INDICATOR_HEIGHT)
        self.sr.posIndicator = Fill(parent=self.sr.posIndicatorCont, color=(1.0, 1.0, 1.0, 0.5), state=uiconst.UI_DISABLED)
        self.sr.posIndicator.Hide()
        self.canDrag = False

    def GetDragData(self, *args):
        if not self.sr.node.canDrag:
            return
        self.sr.node.scroll.SelectNode(self.sr.node)
        return [self.sr.node]

    def OnDropData(self, dragObj, nodes, *args):
        self.sr.posIndicator.Hide()
        if not self.IsOfRightTypeForDragging(nodes):
            return
        if GetAttrs(self, 'parent', 'OnDropData'):
            node = nodes[0]
            if GetAttrs(node, 'panel'):
                self.parent.OnDropData(dragObj, nodes, idx=self.sr.node.idx)

    def OnDragEnter(self, dragObj, nodes, *args):
        if self.IsOfRightTypeForDragging(nodes):
            self.sr.posIndicator.Show()

    def IsOfRightTypeForDragging(self, nodes):
        if len(nodes) != 1:
            return False
        myNode = nodes[0]
        panel = getattr(myNode, 'panel', None)
        return isinstance(panel, DraggableOverviewEntry)

    def OnDragExit(self, *args):
        self.sr.posIndicator.Hide()


class OverviewLastDropEntry(SE_BaseClassCore):
    __guid__ = 'OverviewLastDropEntry'
    default_state = uiconst.UI_DISABLED
    default_showHilite = False

    def ApplyAttributes(self, attributes):
        SE_BaseClassCore.ApplyAttributes(self, attributes)
        self.sr.posIndicator = Line(parent=self, state=uiconst.UI_DISABLED, align=uiconst.TOTOP, weight=2)
        self.sr.posIndicator.Hide()

    def Load(self, node):
        pass

    def ShowIndicator(self):
        self.sr.posIndicator.Show()

    def HideIndicator(self):
        self.sr.posIndicator.Hide()

    def GetDynamicHeight(self, width):
        return 10

    def OnDragEnter(self, dragObj, nodes, *args):
        self.ShowIndicator()

    def OnDragExit(self, *args):
        self.HideIndicator()

    def OnDropData(self, dragObj, nodes, *args):
        if GetAttrs(self, 'parent', 'OnDropData'):
            node = nodes[0]
            if GetAttrs(node, 'panel'):
                self.parent.OnDropData(dragObj, nodes, idx=self.sr.node.idx)


class ColumnEntry(DraggableOverviewEntry):
    __guid__ = 'listentry.ColumnEntry'

    def Load(self, args):
        super(ColumnEntry, self).Load(args)
        self.sr.checkbox.state = uiconst.UI_PICKCHILDREN
        checkboxCont = self.sr.checkbox.checkboxCont
        checkboxCont.state = uiconst.UI_NORMAL
        checkboxCont.OnClick = self.ClickDiode

    def CheckBoxChange(self, checkbox, *args):
        self.sr.node.checked = self.sr.checkbox.checked
        self.sr.node.OnChange(checkbox, self.sr.node)

    def ClickDiode(self, *args):
        self.sr.checkbox.ToggleState()


class FlagEntry(DraggableOverviewEntry):
    __guid__ = 'listentry.FlagEntry'

    def Startup(self, *args):
        DraggableOverviewEntry.Startup(self, args)
        self.sr.flag = None

    def Load(self, node):
        CheckboxEntry.Load(self, node)
        self.sr.checkbox.state = uiconst.UI_PICKCHILDREN
        checkboxCont = self.sr.checkbox.checkboxCont
        checkboxCont.state = uiconst.UI_NORMAL
        checkboxCont.OnClick = self.ClickDiode
        if self.sr.flag:
            f = self.sr.flag
            self.sr.flag = None
            f.Close()
        colorPicker = Container(parent=self, pos=(0, 0, 25, 20), name='colorPicker', state=uiconst.UI_NORMAL, align=uiconst.CENTERRIGHT, idx=0)
        if node.cfgname == 'flag':
            flagInfo = sm.GetService('stateSvc').GetStatePropsColorAndBlink(node.flag)
            self.sr.flag = FlagIconWithState(parent=colorPicker, top=4, state=uiconst.UI_DISABLED, align=uiconst.TOPLEFT, flagInfo=flagInfo)
        else:
            backgroundBlink = sm.GetService('stateSvc').GetStateBlink(node.cfgname, node.flag)
            backgroundColor = sm.GetService('stateSvc').GetStateBackgroundColor(node.flag)
            self.sr.flag = Fill(color=backgroundColor, parent=colorPicker, pos=(0, 4, 9, 9), state=uiconst.UI_DISABLED, align=uiconst.TOPLEFT)
            if backgroundBlink:
                uicore.animations.FadeTo(self.sr.flag, startVal=0.0, endVal=1.0, duration=0.5, loops=uiconst.ANIM_REPEAT, curveType=uiconst.ANIM_WAVE)
        arrow = Sprite(parent=colorPicker, pos=(0, 0, 16, 16), name='arrow', align=uiconst.CENTERRIGHT, texturePath='res:/ui/texture/icons/38_16_229.png', color=(1, 1, 1, 0.5), state=uiconst.UI_DISABLED)
        colorPicker.LoadTooltipPanel = self.LoadColorTooltipPanel
        colorPicker.GetTooltipPointer = self.GetColorTooltipPointer
        colorPicker.GetTooltipDelay = self.GetTooltipDelay

    def ClickDiode(self, *args):
        self.sr.checkbox.ToggleState()

    def CheckBoxChange(self, checkbox, *args):
        self.sr.node.checked = self.sr.checkbox.checked
        self.sr.node.OnChange(checkbox, self.sr.node)

    def GetMenu(self):
        if self.sr.node.GetMenu:
            return self.sr.node.GetMenu()
        m = [(MenuLabel('UI/Overview/ToggleBlink'), self.ToggleBlink)]
        return m

    def ToggleBlink(self):
        current = sm.GetService('stateSvc').GetStateBlink(self.sr.node.cfgname, self.sr.node.flag)
        sm.GetService('stateSvc').SetStateBlink(self.sr.node.cfgname, self.sr.node.flag, not current)
        self.Load(self.sr.node)

    def GetColorTooltipPointer(self):
        return uiconst.POINT_LEFT_2

    def GetTooltipDelay(self):
        return 50

    def LoadColorTooltipPanel(self, tooltipPanel, *args):
        tooltipPanel.state = uiconst.UI_NORMAL
        tooltipPanel.LoadStandardSpacing()

        def ChangeColor(color):
            self.ChangeColor(color, tooltipPanel)

        colors = sm.GetService('stateSvc').GetStateColors()
        colorList = [ x[0] for x in colors.values() ]
        currentColor = sm.GetService('stateSvc').GetStateColor(self.sr.node.flag, where=self.sr.node.cfgname)
        colorPanel = ColorPanel(callback=ChangeColor, currentColor=currentColor, colorList=colorList, addClear=False)
        tooltipPanel.AddLabelSmall(text=GetByLabel('UI/Mail/Select Color'))
        tooltipPanel.AddCell(cellObject=colorPanel)

    def ChangeColor(self, color, tooltipPanel):
        sm.GetService('stateSvc').SetStateColor(self.sr.node.cfgname, self.sr.node.flag, color)
        tooltipPanel.Close()
        self.Load(self.sr.node)


class ShipEntry(DraggableOverviewEntry):
    __guid__ = 'listentry.ShipEntry'

    def Startup(self, *args):
        DraggableOverviewEntry.Startup(self, args)
        self.sr.preEdit = SingleLineEditText(name='preEdit', parent=self, align=uiconst.CENTERLEFT, pos=(32, 0, 20, 0), OnFocusLost=self.OnPreChange, OnReturn=self.OnPreChange, density=Density.COMPACT)
        self.postCont = Container(name='postCont', parent=self, align=uiconst.TOLEFT, pos=(140,
         -POS_INDICATOR_HEIGHT,
         50,
         0))
        self.formatCont = Container(name='formatCont', parent=self, padLeft=10)
        self.sr.postEdit = SingleLineEditText(name='postEdit', parent=self.postCont, align=uiconst.CENTERLEFT, pos=(0, 0, 20, 0), OnFocusLost=self.OnPostChange, OnReturn=self.OnPostChange, density=Density.COMPACT)
        self.moreInfoIcon = MoreInfoIcon(parent=self.postCont, align=uiconst.CENTERLEFT, left=28)
        self.BuildFormatCont()

    def BuildFormatCont(self):
        self.colorPicker = OverviewColorPickerCont(parent=self.formatCont, idx=0, callback=self.SetColorForLabel)
        fontSizeCont = ContainerAutoSize(parent=self.formatCont, align=uiconst.TORIGHT, left=30)
        options = [[FormatNumeric(8), 8],
         [FormatNumeric(9), 9],
         [FormatNumeric(10), 10],
         [FormatNumeric(11), 11],
         [FormatNumeric(12), 12],
         [FormatNumeric(14), 14]]
        self.fontSizeCombo = Combo(parent=fontSizeCont, options=options, name='fontsize', callback=self.OnFontSizeChange, align=uiconst.CENTERLEFT, width=56, density=Density.COMPACT)
        underlineCont = Container(parent=self.formatCont, align=uiconst.TORIGHT, width=40)
        self.underlineCb = Checkbox(name='underlineCb', parent=underlineCont, align=uiconst.CENTERLEFT, left=0, height=14, checked=True, callback=self.OnUnderlineChange)
        self.underline = EveLabelMedium(text=GetByLabel('/Carbon/UI/Controls/EditRichText/UnderlineSymbol'), parent=underlineCont, left=16, align=uiconst.CENTERLEFT, color=(1.0, 1.0, 1.0, 0.6), state=uiconst.UI_NORMAL, hint=GetByLabel('/Carbon/UI/Controls/EditRichText/Underline'))
        italicCont = Container(parent=self.formatCont, align=uiconst.TORIGHT, width=30)
        self.italicCb = Checkbox(name='italicCb', parent=italicCont, align=uiconst.CENTERLEFT, left=0, height=14, callback=self.OnItalicChange)
        self.italicIcon = EveLabelMedium(text=GetByLabel('/Carbon/UI/Controls/EditRichText/ItalicSymbol'), parent=italicCont, left=16, align=uiconst.CENTERLEFT, color=(1.0, 1.0, 1.0, 0.6), state=uiconst.UI_NORMAL, hint=GetByLabel('/Carbon/UI/Controls/EditRichText/ItalicSymbol'))
        boldCont = Container(parent=self.formatCont, align=uiconst.TORIGHT, width=30)
        self.boldCb = Checkbox(name='boldCb', parent=boldCont, align=uiconst.CENTERLEFT, left=0, height=14, callback=self.OnBoldChange)
        self.boldIcon = EveLabelMedium(text=GetByLabel('/Carbon/UI/Controls/EditRichText/BoldSymbol'), parent=boldCont, left=16, align=uiconst.CENTERLEFT, color=(1.0, 1.0, 1.0, 0.6), state=uiconst.UI_NORMAL, hint=GetByLabel('/Carbon/UI/Controls/EditRichText/Bold'))

    def Load(self, node):
        CheckboxEntry.Load(self, node)
        self.sr.checkbox.state = uiconst.UI_PICKCHILDREN
        checkboxCont = self.sr.checkbox.checkboxCont
        checkboxCont.state = uiconst.UI_NORMAL
        checkboxCont.OnClick = self.ClickDiode
        self.sr.label.left = 60
        flag = self.sr.node.flag
        self.sr.preEdit.SetValue(flag[PRE])
        self.sr.postEdit.SetValue(flag[POST])
        if flag[LABEL_TYPE] is None:
            self.sr.postEdit.state = uiconst.UI_HIDDEN
        else:
            self.sr.postEdit.state = uiconst.UI_NORMAL
        comment = self.sr.node.comment
        if comment:
            self.moreInfoIcon.display = True
            self.moreInfoIcon.hint = comment
        else:
            self.moreInfoIcon.display = False
        color = flag.get(LABEL_COLOR, None)
        color = tuple(color) if color else color
        self.colorPicker.SetCurrentFill(color)
        isBold = flag.get(LABEL_BOLD, False)
        self.boldCb.SetChecked(isBold, False)
        isBold = flag.get(LABEL_ITALIC, False)
        self.italicCb.SetChecked(isBold, False)
        isUnderlined = flag.get(LABEL_UNDERLINE, False)
        self.underlineCb.SetChecked(isUnderlined, False)
        fontsize = flag.get(LABEL_SIZE, None) or DEFAULT_FONTSIZE
        self.fontSizeCombo.SelectItemByValue(fontsize)

    def CheckBoxChange(self, checkbox, *args):
        self.sr.node.checked = self.sr.checkbox.checked
        self.sr.node.OnChange(checkbox, self.sr.node)

    def ClickDiode(self, *args):
        self.sr.checkbox.ToggleState()

    def OnClick(self, *args):
        Generic.OnClick(self, *args)

    def OnPreChange(self, *args):
        text = self.sr.preEdit.GetValue()
        if self.sr.node.flag[PRE] != text:
            self.sr.node.flag[PRE] = text.replace(CHAR_LT, CODE_LT).replace(CHAR_GT, CODE_GT)
            self.sr.node.OnChange(self.sr.checkbox)

    def OnPostChange(self, *args):
        text = self.sr.postEdit.GetValue()
        if self.sr.node.flag[POST] != text:
            self.sr.node.flag[POST] = text.replace(CHAR_LT, CODE_LT).replace(CHAR_GT, CODE_GT)
            self.sr.node.OnChange(self.sr.checkbox)

    def OnBoldChange(self, *args):
        isChecked = self.boldCb.GetValue()
        formattingType = LABEL_BOLD
        newValue = isChecked
        self.UpdateFormatting(formattingType, newValue)

    def OnItalicChange(self, *args):
        isChecked = self.italicCb.GetValue()
        formattingType = LABEL_ITALIC
        newValue = isChecked
        self.UpdateFormatting(formattingType, newValue)

    def OnUnderlineChange(self, *args):
        isChecked = self.underlineCb.GetValue()
        formattingType = LABEL_UNDERLINE
        newValue = isChecked
        self.UpdateFormatting(formattingType, newValue)

    def SetColorForLabel(self, color, *args):
        formattingType = LABEL_COLOR
        newValue = color
        self.UpdateFormatting(formattingType, newValue)

    def OnFontSizeChange(self, *args):
        formattingType = LABEL_SIZE
        newValue = self.fontSizeCombo.GetValue()
        self.UpdateFormatting(formattingType, newValue)

    def UpdateFormatting(self, formattingType, newValue):
        if self.sr.node.flag.get(formattingType, None) != newValue:
            self.sr.node.flag[formattingType] = newValue
            self.sr.node.OnChange(self.sr.checkbox)

    def IsOfRightTypeForDragging(self, nodes):
        if len(nodes) != 1:
            return False
        myNode = nodes[0]
        panel = getattr(myNode, 'panel', None)
        return isinstance(panel, (DraggableOverviewEntry, ShipEntryLinebreak))

    def GetHeight(self, *args):
        return 32


class StateOverviewEntry(Generic):
    __guid__ = 'listentry.StateOverviewEntry'

    def Startup(self, *args):
        Generic.Startup(self, args)
        self.alwaysCb = RadioButton(parent=self, left=64, width=14, settingsKey='alwaysShow', checked=False, callback=self.OnCheckBoxChange, settingsPath=('user', 'overview'), align=uiconst.CENTERRIGHT)
        self.alwaysCb.OnMouseEnter = self.OnMouseEnter
        self.alwaysCb.OnMouseExit = self.OnMouseExit
        self.alwaysCb.hint = GetByLabel('UI/Overview/FilterStateAlwaysShowShort')
        self.filterOutCb = RadioButton(parent=self, left=34, width=14, settingsKey='filterOut', checked=False, callback=self.OnCheckBoxChange, settingsPath=('user', 'overview'), align=uiconst.CENTERRIGHT)
        self.filterOutCb.OnMouseEnter = self.OnMouseEnter
        self.filterOutCb.OnMouseExit = self.OnMouseExit
        self.filterOutCb.hint = GetByLabel('UI/Overview/FilterStateFilterOutShort')
        self.unfilteredCb = RadioButton(parent=self, left=4, width=14, settingsKey='unfiltered', checked=False, callback=self.OnCheckBoxChange, settingsPath=('user', 'overview'), align=uiconst.CENTERRIGHT)
        self.unfilteredCb.OnMouseEnter = self.OnMouseEnter
        self.unfilteredCb.OnMouseExit = self.OnMouseExit
        self.unfilteredCb.hint = GetByLabel('UI/Overview/FilterStateNotFilterOutShort')

    def Load(self, node):
        Generic.Load(self, node)
        self.onChangeFunc = node.onChangeFunc
        iconCont = Container(parent=self, pos=(3, 0, 9, 9), name='flag', state=uiconst.UI_DISABLED, align=uiconst.CENTERLEFT, idx=0)
        iconRectLeft = (node.props.iconIndex + 1) * 10
        flagIcon = Sprite(parent=iconCont, pos=(0, 0, 10, 10), name='icon', state=uiconst.UI_DISABLED, rectWidth=10, rectHeight=10, texturePath='res:/UI/Texture/classes/Bracket/flagIcons.png', align=uiconst.RELATIVE, color=node.props.iconColor)
        flagIcon.rectLeft = iconRectLeft
        col = sm.GetService('stateSvc').GetStateColor(node.flag, where='flag')
        flagBackground = Fill(parent=iconCont, color=col)
        flagBackground.opacity *= 0.75
        self.sr.label.left = 16
        self.alwaysCb.SetGroup(node.props.label)
        self.filterOutCb.SetGroup(node.props.label)
        self.unfilteredCb.SetGroup(node.props.label)
        self.alwaysCb.width = 14
        self.filterOutCb.width = 14
        self.unfilteredCb.width = 14
        if node.isAlwaysShow:
            self.alwaysCb.SetChecked(True, report=0)
        elif node.isFilterOut:
            self.filterOutCb.SetChecked(True, report=0)
        else:
            self.unfilteredCb.SetChecked(True, report=0)

    def OnCheckBoxChange(self, cb, *args):
        self.onChangeFunc(self.sr.node, cb.GetSettingsKey())


class ShipEntryLinebreak(Generic):
    isDragObject = True

    def Startup(self, *args):
        Generic.Startup(self, args)
        self.sr.posIndicatorCont = Container(name='posIndicator', parent=self, align=uiconst.TOTOP, state=uiconst.UI_DISABLED, height=2)
        self.sr.posIndicator = Fill(parent=self.sr.posIndicatorCont, color=(1.0, 1.0, 1.0, 0.5))
        self.sr.posIndicator.state = uiconst.UI_HIDDEN

    def GetDragData(self, *args):
        if not self.sr.node.canDrag:
            return
        self.sr.node.scroll.SelectNode(self.sr.node)
        return [self.sr.node]

    def OnDropData(self, dragObj, nodes, *args):
        if GetAttrs(self, 'parent', 'OnDropData'):
            node = nodes[0]
            if GetAttrs(node, 'panel'):
                self.parent.OnDropData(dragObj, nodes, idx=self.sr.node.idx)

    def OnDragEnter(self, dragObj, nodes, *args):
        self.sr.posIndicator.state = uiconst.UI_DISABLED

    def OnDragExit(self, *args):
        self.sr.posIndicator.state = uiconst.UI_HIDDEN

    def GetMenu(self):
        data = self.sr.node
        m = []
        if data.removeFunc:
            m += [(MenuLabel('UI/Commands/Remove'), data.removeFunc, (data.idx,))]
        return m


def GetLastEntryToAdd(scrolllist):
    if scrolllist:
        lastDropEntry = GetFromClass(OverviewLastDropEntry)
        return [lastDropEntry]
    else:
        return []


class OverviewTabPresetEntry(CheckboxEntry):

    def Startup(self, *args):
        CheckboxEntry.Startup(self, *args)
        self.bracketSpriteCont = Container(name='bracketSpriteCont', parent=self, align=uiconst.CENTERRIGHT, pos=(6, 0, 16, 16))

    def Load(self, node):
        CheckboxEntry.Load(self, node)
        self.bracketSpriteCont.Flush()
        texturePaths = node.texturePaths
        if texturePaths and len(texturePaths) < 5:
            texturePathList = self.SortTexturePaths(texturePaths)
            for eachPath in texturePathList:
                Sprite(name='bracketSprite', parent=self.bracketSpriteCont, pos=(0, 0, 16, 16), align=uiconst.TORIGHT, state=uiconst.UI_DISABLED, opacity=0.75, texturePath=eachPath)

    def SortTexturePaths(self, texturePaths):
        texturePathList = list(texturePaths)

        def GetSortKey(textureName):
            texturePathLower = textureName.lower()
            if texturePathLower.find('extralarge') > -1:
                return 0
            if texturePathLower.find('large') > -1:
                return 1
            if texturePathLower.find('medium') > -1:
                return 2
            if texturePathLower.find('small') > -1:
                return 3
            return 4

        texturePathList.sort(key=lambda x: GetSortKey(x))
        return texturePathList

    def GetMenu(self):
        node = self.sr.node
        m = CheckboxEntry.GetMenu(self)
        if session.role & ROLE_GML > 0:
            m.append(('GM - groupID: %s' % node.retval, blue.pyos.SetClipboardData, (str(node.retval),)))
        return m
