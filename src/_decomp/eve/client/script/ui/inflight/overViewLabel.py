#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\overViewLabel.py
import blue
import telemetry
import carbonui.const as uiconst
import eveicon
import trinity
import uthread
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui import TextColor
from carbonui.primitives.base import Base
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import VisibleBase
from carbonui.text.settings import check_convert_font_size
from carbonui.uicore import uicore
from eve.client.script.ui.control import eveIcon, eveLabel
from eve.client.script.ui.inflight.overview import overviewColumns, overviewConst
from eve.client.script.ui.inflight.overview.overviewConst import *
from localization import GetByLabel
from signals import Signal
FONT_COLOR_INT = trinity.TriColor(*TextColor.HIGHLIGHT).AsInt()

class OverviewLabel(VisibleBase):
    __renderObject__ = trinity.Tr2Sprite2dTextObject
    default_name = 'OverviewLabel'
    default_color = None
    _text = None
    _columnWidth = None
    _columnPosition = 0
    _globalMaxWidth = None
    _columnWidthDirty = False

    def ApplyAttributes(self, attributes):
        VisibleBase.ApplyAttributes(self, attributes)
        self.typeID = attributes.get('typeID', None)
        self.fadeSize = self.ScaleDpi(COLUMNFADESIZE)
        self.rightAligned = False
        measurer = trinity.Tr2FontMeasurer()
        measurer.limit = 0
        measurer.fontSize = uicore.ScaleDpi(check_convert_font_size(attributes.fontSize))
        measurer.font = str(uicore.font.GetFontDefault())
        measurer.letterSpace = 0
        self.renderObject.fontMeasurer = measurer
        self.renderObject.shadowOffset = eveLabel.Label.get_default_shadow_offset()
        self.renderObject.shadowColor = eveLabel.Label.default_shadowColor
        self.measurer = measurer

    def OnGlobalFontShadowChanged(self):
        self.renderObject.shadowOffset = eveLabel.Label.get_default_shadow_offset()

    def UpdateFade(self):
        measurer = self.measurer
        columnWidth = self.columnWidth
        if columnWidth:
            globalFade = False
            globalMaxWidth = self.globalMaxWidth
            if globalMaxWidth and globalMaxWidth - self.left < columnWidth:
                scaledMaxWidth = max(0, self.ScaleDpi(globalMaxWidth - self.left))
                globalFade = True
            elif self.rightAligned:
                scaledMaxWidth = measurer.cursorX
            else:
                scaledMaxWidth = self.ScaleDpi(columnWidth)
            if measurer.cursorX > scaledMaxWidth:
                maxFade = max(2, measurer.cursorX - scaledMaxWidth)
                if globalFade:
                    measurer.fadeRightStart = max(0, scaledMaxWidth - min(maxFade, self.fadeSize))
                    measurer.fadeRightEnd = scaledMaxWidth
                else:
                    measurer.fadeRightStart = measurer.cursorX + 1
                    measurer.fadeRightEnd = measurer.cursorX + 1
            else:
                measurer.fadeRightStart = measurer.cursorX + 1
                measurer.fadeRightEnd = measurer.cursorX + 1

    @apply
    def left():

        def fget(self):
            return self._left

        def fset(self, value):
            if value < 1.0:
                adjustedValue = value
            else:
                adjustedValue = int(round(value))
            if adjustedValue != self._left:
                self._left = adjustedValue
                self.FlagAlignmentDirty()
                self.UpdateFade()

        return property(**locals())

    @apply
    def width():

        def fget(self):
            return self._width

        def fset(self, value):
            if value < 1.0:
                adjustedValue = value
            else:
                adjustedValue = int(round(value))
            if adjustedValue != self._width:
                self._width = adjustedValue
                if self.rightAligned:
                    self.left = self.columnPosition + self.columnWidth - adjustedValue
                self.FlagAlignmentDirty()
                self.UpdateFade()

        return property(**locals())

    @apply
    def text():

        def fget(self):
            return self._text

        def fset(self, value):
            if self._text != value or self._columnWidthDirty:
                self._columnWidthDirty = False
                self._text = value
                if not value:
                    self.texture = None
                    self.spriteEffect = trinity.TR2_SFX_NONE
                    return
                measurer = self.measurer
                measurer.Reset()
                measurer.color = FONT_COLOR_INT
                if self.columnWidth:
                    measurer.limit = self.ScaleDpi(self.columnWidth)
                added = measurer.AddText(unicode(value))
                measurer.CommitText(0, measurer.ascender)
                if self.columnWidth:
                    self.width = min(self.columnWidth, self.ReverseScaleDpi(measurer.cursorX + 0.5))
                    self.renderObject.textWidth = min(self.ScaleDpi(self.columnWidth), measurer.cursorX)
                else:
                    self.width = self.ReverseScaleDpi(measurer.cursorX + 0.5)
                    self.renderObject.textWidth = measurer.cursorX
                self.height = self.ReverseScaleDpi(measurer.ascender - measurer.descender)
                self.renderObject.textHeight = measurer.ascender - measurer.descender

        return property(**locals())

    @apply
    def columnWidth():

        def fget(self):
            return self._columnWidth

        def fset(self, value):
            if self._columnWidth != value:
                self._columnWidth = value
                self._columnWidthDirty = True
                measurer = self.measurer
                self.width = min(value, self.ReverseScaleDpi(measurer.cursorX + 0.5))
                self.renderObject.textWidth = min(self.ScaleDpi(value), measurer.cursorX)
                if self.rightAligned:
                    self.left = self.columnPosition + value - self.width

        return property(**locals())

    @apply
    def columnPosition():

        def fget(self):
            return self._columnPosition

        def fset(self, value):
            if self._columnPosition != value:
                self._columnPosition = value
                if self.rightAligned:
                    self.left = value + self.columnWidth - self.width
                else:
                    self.left = value

        return property(**locals())

    @apply
    def globalMaxWidth():

        def fget(self):
            return self._globalMaxWidth

        def fset(self, value):
            if self._globalMaxWidth != value:
                self._globalMaxWidth = value
                self.UpdateFade()

        return property(**locals())

    @classmethod
    def MeasureTextSize(cls, text, **customAttributes):
        customAttributes['parent'] = None
        customAttributes['align'] = uiconst.TOPLEFT
        label = cls(**customAttributes)
        label.text = text
        return (label.width, label.height)

    def GetMenu(self):
        parent = self.parent
        if parent and hasattr(parent, 'GetMenu'):
            return parent.GetMenu()

    def OnMouseDown(self, *args, **kwds):
        parent = self.parent
        if parent and parent.OnMouseDown.im_func != Base.OnMouseDown.im_func:
            return parent.OnMouseDown(*args, **kwds)

    def OnMouseUp(self, *args, **kwds):
        parent = self.parent
        if parent and parent.OnMouseUp.im_func != Base.OnMouseUp.im_func:
            return parent.OnMouseUp(*args, **kwds)

    def OnClick(self, *args, **kwds):
        parent = self.parent
        if parent and parent.OnClick.im_func != Base.OnClick.im_func:
            return parent.OnClick(*args, **kwds)

    def OnDblClick(self, *args, **kwds):
        parent = self.parent
        if parent and hasattr(parent, 'OnDblClick'):
            return parent.OnDblClick(*args, **kwds)


class Header(Container):

    def ApplyAttributes(self, attributes):
        super(Header, self).ApplyAttributes(attributes)
        showScaler = attributes.showScaler
        self.columnID = attributes.columnID
        self.sortTriangle = None
        self._hovered = False
        self.on_scaler_mouse_down = Signal('on_scaler_mouse_down')
        self.get_menu_func = attributes.get_menu_func
        if showScaler:
            scaler = Container(name='scaler', parent=self, align=uiconst.TORIGHT_NOPUSH, width=4, state=uiconst.UI_NORMAL, cursor=uiconst.UICURSOR_LEFT_RIGHT_DRAG)
            scaler.OnMouseDown = self.OnScalerMouseDown
        self.label = eveLabel.EveLabelSmall(parent=self, text=self.GetLabelText(), align=uiconst.CENTERLEFT, left=uiconst.LABELTABMARGIN, state=uiconst.UI_DISABLED, maxLines=1)
        self._update()

    def GetLabelText(self):
        return overviewColumns.GetColumnLabel(self.columnID, addFormatUnit=True)

    def OnScalerMouseDown(self, *args):
        self.on_scaler_mouse_down(self, *args)

    def OnMouseEnter(self, *args):
        self._hovered = True
        PlaySound(uiconst.SOUND_BUTTON_HOVER)
        self._update()

    def OnMouseExit(self, *args):
        self._hovered = False
        self._update()

    def _update(self):
        self.label.rgba = self._GetLabelColor()
        if self.sortTriangle:
            self.sortTriangle.rgba = self._GetTriangleColor()

    def _GetTriangleColor(self):
        if self._hovered:
            return TextColor.HIGHLIGHT
        else:
            return TextColor.NORMAL

    def _GetLabelColor(self):
        if self._hovered:
            return TextColor.HIGHLIGHT
        else:
            return TextColor.SECONDARY

    def ConstructSortTriangle(self):
        if not self.sortTriangle:
            self.sortTriangle = eveIcon.Icon(align=uiconst.CENTERRIGHT, pos=(3, -1, 16, 16), parent=self, name='directionIcon', shadowOffset=(1, 1), idx=0)
        self._update()

    def GetMenu(self):
        return self.get_menu_func()

    def LoadTooltipPanel(self, tooltipPanel, owner):
        tooltipPanel.LoadStandardSpacing()
        tooltipPanel.columns = 1
        tooltipPanel.AddMediumHeader(text=self.GetLabelText())
        description = self.GetDescription()
        if description:
            tooltipPanel.AddLabelMedium(text=description, wrapWidth=300)

    def GetDescription(self):
        description = overviewConst.COLUMN_DESCRIPTIONS.get(self.columnID, None)
        if description:
            return GetByLabel(description)


class SortHeaders(Container):
    default_name = 'SortHeaders'
    default_align = uiconst.TOTOP
    default_height = 24
    default_state = uiconst.UI_PICKCHILDREN
    default_clipChildren = True
    default_padBottom = 0

    def ApplyAttributes(self, attributes):
        super(SortHeaders, self).ApplyAttributes(attributes)
        self.headerContainer = Container(parent=self)
        self.settingsID = attributes.settingsID
        self.get_menu_func = attributes.get_menu_func
        self.subSettingID = None
        self.customSortIcon = None
        self.columnIDs = []
        self.fixedColumns = None
        self.defaultColumn = None
        self.minSizeByColumnID = {}

    def SetSubSettingID(self, subSettingID):
        self.subSettingID = subSettingID

    def GetSettingKey(self):
        return (self.settingsID, self.subSettingID)

    def SetDefaultColumn(self, columnID, direction):
        self.defaultColumn = (columnID, direction)

    def SetMinSizeByColumnID(self, minSizes):
        self.minSizeByColumnID = minSizes

    def CreateColumns(self, columns, fixedColumns = None):
        self.headerContainer.Flush()
        self.columnIDs = columns
        self.fixedColumns = fixedColumns
        if columns:
            sizes = self.GetCurrentSizes()
            for columnID in columns:
                header = Header(parent=self.headerContainer, align=uiconst.TOLEFT, state=uiconst.UI_NORMAL, showScaler=columnID not in fixedColumns, columnID=columnID, get_menu_func=self.get_menu_func)
                header.OnClick = (self.ClickHeader, header)
                header.OnDblClick = (self.DblClickHeader, header)
                header.on_scaler_mouse_down.connect(self.StartHeaderScale)
                minWidth = self.minSizeByColumnID.get(columnID, COLUMNMINSIZE)
                if fixedColumns and columnID in fixedColumns:
                    header.width = fixedColumns[columnID]
                    if header.width <= 32:
                        header.label.Hide()
                elif columnID in sizes:
                    header.width = max(minWidth, sizes[columnID])
                else:
                    defaultWidth = COLUMN_DEFAULTSIZE.get(columnID, COLUMNMINDEFAULTSIZE)
                    if columnID in COLUMN_DO_NOT_EXPAND_FOR_LABEL:
                        header.width = max(minWidth, defaultWidth)
                    else:
                        requiredWidthForLabel = header.label.textwidth + 24
                        header.width = max(minWidth, max(defaultWidth, requiredWidthForLabel))

            self.UpdateActiveState()

    def SetSortIcon(self, texturePath):
        if self.customSortIcon != texturePath:
            self.customSortIcon = texturePath
            self.UpdateActiveState()

    def UpdateActiveState(self):
        currentActive, currentDirection = self.GetCurrentActive()
        for header in self.headerContainer.children:
            if hasattr(header, 'columnID'):
                if header.columnID == currentActive:
                    if not header.sortTriangle:
                        header.ConstructSortTriangle()
                    if self.customSortIcon:
                        header.sortTriangle.LoadTexture(self.customSortIcon)
                    else:
                        texturePath = eveicon.caret_up if currentDirection else eveicon.caret_down
                        header.sortTriangle.LoadIcon(texturePath)
                    header.sortTriangle.state = uiconst.UI_DISABLED
                    rightMargin = 20
                else:
                    if header.sortTriangle:
                        header.sortTriangle.Hide()
                    rightMargin = 6
                header.label.width = header.width - header.label.left - 4
                if header.sortTriangle and header.sortTriangle.display:
                    header.label.SetRightAlphaFade(header.width - rightMargin - header.label.left, uiconst.SCROLL_COLUMN_FADEWIDTH)
                else:
                    header.label.SetRightAlphaFade()
                if header.width <= 32 or header.width - header.label.left - rightMargin - 6 < header.label.textwidth:
                    header.hint = header.label.text
                else:
                    header.hint = None

    def GetCurrentColumns(self):
        return self.columnIDs

    @telemetry.ZONE_METHOD
    def GetCurrentActive(self):
        all = settings.char.ui.Get('SortHeadersSettings2', {})
        currentActive, currentDirection = None, True
        settingTuple = self.GetSettingKey()
        if settingTuple in all:
            currentActive, currentDirection = all[settingTuple]
            if currentActive not in self.columnIDs:
                return (None, True)
            return (currentActive, currentDirection)
        if self.defaultColumn is not None:
            columnID, direction = self.defaultColumn
            if columnID in self.columnIDs:
                return self.defaultColumn
        if self.columnIDs:
            currentActive, currentDirection = self.columnIDs[0], True
        return (currentActive, currentDirection)

    def SetCurrentActive(self, columnID, doCallback = True):
        currentActive, currentDirection = self.GetCurrentActive()
        if currentActive == columnID:
            sortDirection = not currentDirection
        else:
            sortDirection = currentDirection
        settingTuple = self.GetSettingKey()
        all = settings.char.ui.Get('SortHeadersSettings2', {})
        all[settingTuple] = (columnID, sortDirection)
        settings.char.ui.Set('SortHeadersSettings2', all)
        self.UpdateActiveState()
        if doCallback:
            self.OnSortingChange(currentActive, columnID, currentDirection, sortDirection)

    def DblClickHeader(self, header):
        if not self.ColumnIsFixed(header.columnID):
            self.SetCurrentActive(header.columnID, doCallback=False)
            self.OnColumnSizeReset(header.columnID)

    def ClickHeader(self, header):
        self.SetCurrentActive(header.columnID)

    def StartHeaderScale(self, header, mouseButton, *args):
        if mouseButton == uiconst.MOUSELEFT:
            self.startScaleX = uicore.uilib.x
            self.startScaleWidth = header.width
            uthread.new(self.ScaleHeader, header)

    def ScaleHeader(self, header):
        while not self.destroyed and uicore.uilib.leftbtn:
            diff = self._GetColumnWidthDiff()
            header.width = max(self.minSizeByColumnID.get(header.columnID, COLUMNMINSIZE), self.startScaleWidth + diff)
            self.UpdateActiveState()
            blue.pyos.synchro.Yield()

        currentSizes = self.RegisterCurrentSizes()
        self.UpdateActiveState()
        self.OnColumnSizeChange(header.columnID, header.width, currentSizes)

    def _GetColumnWidthDiff(self):
        diff = uicore.uilib.x - self.startScaleX
        l, t, w, h = self.GetAbsolute()
        maxDiff = w - (self.startScaleX - l) - 2
        return min(diff, maxDiff)

    def GetCurrentSizes(self):
        settingsID = self.GetSettingKey()
        current = settings.char.ui.Get('SortHeadersSizes', {}).get(settingsID, {})
        if self.fixedColumns:
            current.update(self.fixedColumns)
        for each in self.headerContainer.children:
            if hasattr(each, 'columnID') and each.columnID not in current:
                current[each.columnID] = each.width

        return current

    def ColumnIsFixed(self, columnID):
        return columnID in self.fixedColumns

    def SetColumnSize(self, columnID, size):
        if columnID in self.fixedColumns:
            return
        columnSize = max(self.minSizeByColumnID.get(columnID, COLUMNMINSIZE), size)
        for each in self.headerContainer.children:
            if hasattr(each, 'columnID') and each.columnID == columnID:
                each.width = columnSize
                break

        self.UpdateActiveState()
        currentSizes = self.RegisterCurrentSizes()
        self.OnColumnSizeChange(columnID, columnSize, currentSizes)

    def RegisterCurrentSizes(self):
        sizes = {}
        for each in self.headerContainer.children:
            if hasattr(each, 'columnID'):
                sizes[each.columnID] = each.width

        all = settings.char.ui.Get('SortHeadersSizes', {})
        settingsID = self.GetSettingKey()
        all[settingsID] = sizes
        settings.char.ui.Set('SortHeadersSizes', all)
        return sizes

    def OnSortingChange(self, oldColumnID, columnID, oldSortDirection, sortDirection):
        pass

    def OnColumnSizeChange(self, columnID, newSize, currentSizes):
        pass

    def OnColumnSizeReset(self, columnID):
        pass
