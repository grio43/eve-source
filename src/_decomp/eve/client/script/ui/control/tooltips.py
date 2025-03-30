#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\tooltips.py
import blue
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui import TextColor, uiconst, TextDetail, TextBody, TextHeader
from carbonui.control.contextMenu.menuUtil import GetContextMenuOwner
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.primitives.sprite import Sprite
from carbonui.uicore import uicore
from eve.client.script.ui import eveColor
from carbonui.control.buttonIcon import ButtonIcon
from eve.client.script.ui.control.infoIcon import InfoIcon
from eve.client.script.ui.control.eveLabel import EveCaptionSmall, EveLabelLarge, EveLabelMedium, EveLabelSmall, EveCaptionMedium, EveCaptionLarge
from eve.client.script.ui.control.pointerPanel import PointerPanel, FrameWithPointer, FadeOutPanelAndClose, RefreshPanelPosition
COLOR_NUMBERVALUE = TextColor.SECONDARY
COLOR_NUMBERVALUE_NEGATIVE = eveColor.HOT_RED
COLOR_NUMBERVALUE_POSITIVE = eveColor.SUCCESS_GREEN
SLEEPTIME_EXTEND = 1000
SLEEPTIME_EXTENDFAST = 10
SLEEPTIME_TIMETOLIVE = 50
SLEEPTIME_TIMETOLIVE_EDITABLE = 300

class ShortcutHint(Container):
    default_align = uiconst.TOPRIGHT

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        bgColor = attributes.get('bgColor', (1, 1, 1, 0.1))
        Fill(bgParent=self, color=bgColor)
        textColor = attributes.get('textColor', TextColor.SECONDARY)
        self.textLabel = EveLabelMedium(align=uiconst.CENTER, parent=self, text=attributes.text, bold=True, color=textColor)
        self.AdjustSize()

    def AdjustSize(self):
        width = self.textLabel.width + 8
        self.width = width - width % 16 + 16
        self.height = self.textLabel.height


class TooltipGeneric(Container):
    pointerSize = 9
    beingDestroyed = None
    scaleTransform = None
    default_pointerDirection = uiconst.POINT_BOTTOM_2
    horizontal_padding = 16
    vertical_padding = 16

    def ApplyAttributes(self, attributes):
        attributes.align = uiconst.NOALIGN
        Container.ApplyAttributes(self, attributes)
        self.pointerDirection = attributes.get('pointerDirection', self.default_pointerDirection)
        self.backgroundFrame = FrameWithPointer(bgParent=self)
        self.textLabel = EveLabelMedium(align=uiconst.TOPLEFT, width=200, autoFitToText=True, parent=self, left=self.horizontal_padding, top=self.vertical_padding)

    def SetTooltipString(self, tooltipString, owner):
        if not tooltipString and self.opacity:
            self.display = False
            return
        self.textLabel.text = tooltipString
        self.owner = owner
        self.pos = (0,
         0,
         uicore.ReverseScaleDpi(self.textLabel.actualTextWidth) + 2 * self.horizontal_padding,
         uicore.ReverseScaleDpi(self.textLabel.actualTextHeight) + 2 * self.vertical_padding)
        RefreshPanelPosition(self)

    @apply
    def left():
        doc = 'x-coordinate of UI element'

        def fget(self):
            return self._left

        def fset(self, value):
            self._left = value
            self.displayX = uicore.ScaleDpiF(self._left)
            ro = self.renderObject
            if ro:
                ro.displayX = self._displayX

        return property(**locals())

    @apply
    def top():
        doc = 'y-coordinate of UI element'

        def fget(self):
            return self._top

        def fset(self, value):
            self._top = value
            self.displayY = uicore.ScaleDpiF(self._top)
            ro = self.renderObject
            if ro:
                ro.displayY = self._displayY

        return property(**locals())

    @apply
    def pos():
        doc = 'Position of UI element'

        def fget(self):
            return (self._left,
             self._top,
             self._width,
             self._height)

        def fset(self, value):
            left, top, width, height = value
            doFlag = self._width != width or self._height != height
            self._left = left
            self._top = top
            self._width = width
            self._height = height
            self.displayX = uicore.ScaleDpiF(self._left)
            self.displayY = uicore.ScaleDpiF(self._top)
            self.displayWidth = uicore.ScaleDpiF(self._width)
            self.displayHeight = uicore.ScaleDpiF(self._height)
            ro = self.renderObject
            if ro:
                ro.displayX = self._displayX
                ro.displayY = self._displayY
                ro.displayWidth = self._displayWidth
                ro.displayHeight = self._displayHeight
                if not self._constructingBase and doFlag:
                    self.FlagAlignmentDirty()

        return property(**locals())

    def _SetDisplay(self, value):
        if value != self._display:
            self._display = value
            ro = self.renderObject
            if ro:
                ro.display = value

    def Close(self, *args):
        if getattr(uicore.uilib, 'tooltipHandler', None):
            now = blue.os.GetWallclockTime()
            uicore.uilib.tooltipHandler.lastCloseTime = now
        Container.Close(self, *args)
        if getattr(self, 'debugFrame', None):
            self.debugFrame.Close()
        if self.scaleTransform:
            self.scaleTransform.Close()
            self.scaleTransform = None


class TooltipPanel(PointerPanel):
    default_state = uiconst.UI_PICKCHILDREN
    default_align = uiconst.TOPLEFT
    default_opacity = 0.0
    default_cellClipChildren = False

    def Close(self, *args):
        if getattr(uicore.uilib, 'tooltipHandler', None) and len(self.children):
            now = blue.os.GetWallclockTime()
            uicore.uilib.tooltipHandler.lastCloseTime = now
        if self.owner and getattr(self.owner, 'OnTooltipPanelClosed', None):
            self.owner.OnTooltipPanelClosed()
        PointerPanel.Close(self, *args)

    def CloseWithFade(self, *args):
        if getattr(uicore.uilib, 'tooltipHandler', None) and len(self.children):
            now = blue.os.GetWallclockTime()
            uicore.uilib.tooltipHandler.lastCloseTime = now
        FadeOutPanelAndClose(self)

    def ShowPanel(self, owner):
        PointerPanel.ShowPanel(self, owner)
        if hasattr(owner, 'LoadExtendedTooltipPanel'):
            alt = uicore.uilib.Key(uiconst.VK_MENU)
            if alt:
                expandSleeptime = SLEEPTIME_EXTENDFAST
            else:
                expandSleeptime = SLEEPTIME_EXTEND
            self.expandTimer = AutoTimer(expandSleeptime, self.ExpandTooltipPanel, owner)
        if self.pickState == uiconst.TR2_SPS_ON:
            timeToLive = SLEEPTIME_TIMETOLIVE_EDITABLE
        else:
            timeToLive = SLEEPTIME_TIMETOLIVE
        if self.owner and getattr(self.owner, 'OnTooltipPanelOpened', None):
            self.owner.OnTooltipPanelOpened()
        self.HoldTillMouseOutside(timeToLive)
        if self.destroyed or self.beingDestroyed:
            return
        if self.opacity:
            FadeOutPanelAndClose(self)
        else:
            self.Close()

    def ExpandTooltipPanel(self, owner):
        self.expandTimer = None
        if self.destroyed or self.beingDestroyed:
            return
        if owner.destroyed:
            return
        owner.LoadExtendedTooltipPanel(self)

    def HoldTillMouseOutside(self, graceTime):
        lastOnTime = blue.os.GetWallclockTime()
        radialMenuSvc = sm.GetService('radialmenu')
        while not self.destroyed:
            now = blue.os.GetWallclockTime()
            if self.pickState == uiconst.TR2_SPS_ON:
                contextMenuOwner = GetContextMenuOwner()
                if contextMenuOwner and contextMenuOwner.IsUnder(self):
                    lastOnTime = now
                    blue.synchro.SleepWallclock(5)
                    continue
                radialMenuOwner = radialMenuSvc.GetRadialMenuOwner()
                if radialMenuOwner and radialMenuOwner.IsUnder(self):
                    lastOnTime = now
                    blue.synchro.SleepWallclock(5)
                    continue
                mouseCapture = uicore.uilib.GetMouseCapture()
                if mouseCapture and mouseCapture.IsUnder(self):
                    lastOnTime = now
                    blue.synchro.SleepWallclock(5)
                    continue
                ownerPickable = self.IsOwnerPickable()
                if not ownerPickable:
                    return False
            mouseInside = self.IsMouseInside()
            if mouseInside:
                lastOnTime = now
                blue.synchro.SleepWallclock(5)
                continue
            blue.synchro.SleepWallclock(1)
            if self.destroyed:
                return False
            if lastOnTime and blue.os.TimeDiffInMs(lastOnTime, now) > graceTime:
                return False

    def IsOwnerPickable(self):
        owner = self.owner
        if not owner:
            return False
        prestate = owner.state
        owner.state = uiconst.UI_NORMAL
        try:
            ol, ot, ow, oh = owner.GetAbsolute()
            ol = uicore.ScaleDpiF(ol)
            ot = uicore.ScaleDpiF(ot)
            ow = uicore.ScaleDpiF(ow)
            oh = uicore.ScaleDpiF(oh)
            renderObject, pyObject = uicore.uilib.PickScreenPosition(int(ol + ow / 2), int(ot + oh / 2))
            if pyObject and pyObject.IsUnder(uicore.layer.menu):
                return True
            if pyObject is not owner:
                pickRadius = uicore.ScaleDpiF(getattr(owner, 'pickRadius', 0.0))
                if pickRadius < 0.0:
                    pickRadius = min(ow, oh) / 2.0
                if pickRadius > 0.0:
                    x_center = ol + ow / 2.0
                    y_center = ot + oh / 2.0
                    tryPick = ((x_center - pickRadius + 1, y_center),
                     (x_center + pickRadius - 1, y_center),
                     (x_center, y_center - pickRadius + 1),
                     (x_center, y_center + pickRadius - 1))
                else:
                    tryPick = ((ol + 1, ot + oh / 2),
                     (ol + ow - 1, ot + oh / 2),
                     (ol + ow / 2, ot + 1),
                     (ol + ow / 2, ot + oh - 1))
                hits = 0
                for x, y in tryPick:
                    renderObject, pyObject = uicore.uilib.PickScreenPosition(int(x), int(y))
                    if pyObject is owner:
                        hits += 1
                        if hits == 2:
                            return True
                    if pyObject and pyObject.IsUnder(uicore.layer.menu):
                        return True

        finally:
            owner.state = prestate

        return pyObject is owner

    def IsMouseInside(self):
        if self.destroyed:
            return False
        owner = self.owner
        if not owner:
            return False
        mouseOver = uicore.uilib.mouseOver
        if mouseOver is owner:
            return True
        if mouseOver is self or mouseOver.IsUnder(self):
            return True
        focus = uicore.registry.GetFocus()
        if focus and focus.IsUnder(self):
            return True
        return False

    def LoadTooltip(self, *args):
        pass

    def ExpandTooltip(self, owner):
        self.expandTimer = None
        if self.destroyed or self.beingDestroyed:
            return
        if owner.destroyed:
            return
        if hasattr(owner, 'LoadExtendedTooltipPanel'):
            owner.LoadExtendedTooltipPanel(self)

    def AddCommandTooltip(self, command):
        label = command.GetName()
        shortcutStr = command.GetShortcutAsString()
        l = self.AddLabelShortcut(label, shortcutStr)
        detailedDescription = command.GetDetailedDescription()
        d = None
        if detailedDescription:
            d = self.AddLabelMedium(text=detailedDescription, align=uiconst.TOPLEFT, wrapWidth=200, colSpan=self.columns, color=TextColor.NORMAL)
        return (l, d)

    def AddShortcutCell(self, shortcut):
        shortcutObj = ShortcutHint(text=shortcut)
        self.AddCell(shortcutObj)
        return shortcutObj

    def AddLabelShortcut(self, label, shortcut, bold = True):
        self.FillRow()
        labelObj = self.AddLabelMedium(text=label, bold=bold, colSpan=self.columns - 1)
        if shortcut:
            shortcutObj = self.AddShortcutCell(shortcut)
        else:
            self.AddCell()
            shortcutObj = None
        return (labelObj, shortcutObj)

    def AddLabelValue(self, label, value, valueColor = COLOR_NUMBERVALUE, wrapWidth = None, opacity = 1.0):
        self.FillRow()
        labelObj = self.AddLabelMedium(text=label, align=uiconst.CENTERLEFT, bold=True, cellPadding=(0, 0, 16, 0), opacity=opacity)
        valueObj = self.AddLabelMedium(text=value, align=uiconst.CENTERRIGHT, color=valueColor, colSpan=self.columns - 1, wrapWidth=wrapWidth, opacity=opacity)
        return (labelObj, valueObj)

    def AddSpriteLabel(self, texturePath, label, iconSize = 32, iconColor = Sprite.default_color, iconOffset = -5, labelOffset = 5, mainAlign = uiconst.CENTERLEFT, align = uiconst.TOLEFT, textAlign = uiconst.CENTERLEFT, **keywords):
        mainContainer = ContainerAutoSize(align=mainAlign, height=iconSize, width=iconSize)
        sprite = Sprite(parent=mainContainer, align=align, width=iconSize, height=iconSize, texturePath=texturePath, left=iconOffset, color=iconColor)
        labelCont = ContainerAutoSize(parent=mainContainer, align=align, height=iconSize)
        label = EveLabelMedium(parent=labelCont, text=label, align=textAlign, left=labelOffset, **keywords)
        self.AddCell(mainContainer, **keywords)
        return (sprite, label)

    def AddIconLabel(self, icon, label, iconSize = 32, padBottom = 0):
        self.FillRow()
        iconObj = Sprite(pos=(0,
         0,
         iconSize,
         iconSize), align=uiconst.CENTERLEFT)
        iconObj.LoadIcon(icon, ignoreSize=True)
        self.AddCell(iconObj, cellPadding=(-3,
         0,
         7,
         padBottom))
        labelObj = self.AddLabelMedium(text=label, align=uiconst.CENTERLEFT, bold=True, cellPadding=(0,
         0,
         7,
         padBottom))
        return (iconObj, labelObj)

    def AddIconLabelValue(self, icon, label, value, valueColor = COLOR_NUMBERVALUE, iconSize = 32):
        self.FillRow()
        iconObj = Sprite(pos=(0,
         0,
         iconSize,
         iconSize), align=uiconst.CENTERLEFT)
        iconObj.LoadIcon(icon, ignoreSize=True)
        self.AddCell(iconObj, cellPadding=(-3, 0, 3, 0))
        labelObj = self.AddLabelMedium(text=label, align=uiconst.CENTERLEFT, bold=True, cellPadding=(0, 0, 7, 0))
        valueObj = self.AddLabelMedium(align=uiconst.CENTERRIGHT, bold=True, color=valueColor, top=1, colSpan=self.columns - 2, cellPadding=(7, 0, 0, 0))
        return (iconObj, labelObj, valueObj)

    def AddButtonLabelValue(self, name, buttonTexturePath, buttonFunc = None, buttonArgs = None, buttonSize = 32, buttonOpacity = 1.0, label = '', valueColor = COLOR_NUMBERVALUE):
        self.FillRow()
        buttonObj = ButtonIcon(name='%s_icon' % name, texturePath=buttonTexturePath, align=uiconst.CENTERLEFT, pos=(0,
         0,
         buttonSize,
         buttonSize), state=uiconst.UI_NORMAL, func=buttonFunc, args=buttonArgs, iconSize=buttonSize, colorType=uiconst.COLORTYPE_UIHILIGHT)
        cell = self.AddCell(buttonObj, cellPadding=(0, 0, 0, 0))
        labelObj = self.AddLabelMedium(text=label, align=uiconst.CENTERLEFT, bold=False, cellPadding=(4, 0, 7, 0))
        valueObj = self.AddLabelMedium(align=uiconst.CENTERRIGHT, bold=True, color=valueColor, top=0, colSpan=self.columns - 2, cellPadding=(7, 0, 0, 0))
        return (cell,
         buttonObj,
         labelObj,
         valueObj)

    def AddDivider(self, color = TextColor.DISABLED, cellPadding = None):
        self.FillRow()
        divider = Fill(align=uiconst.TOTOP, state=uiconst.UI_DISABLED, color=color, height=1, padding=(0, 3, 0, 3))
        self.AddCell(divider, colSpan=self.columns, cellPadding=cellPadding)
        return divider

    def AddSpacer(self, width = 0, height = 0, colSpan = 1, rowSpan = 1):
        spacer = Fill(align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, width=width, height=height, opacity=0.0)
        self.AddCell(spacer, colSpan=colSpan, rowSpan=rowSpan)
        return spacer

    def AddLabelSmall(self, state = uiconst.UI_DISABLED, wrapWidth = None, **keywords):
        if wrapWidth:
            keywords['width'] = wrapWidth
            keywords['autoFitToText'] = True
        label = EveLabelSmall(state=state, **keywords)
        self.AddCell(label, **keywords)
        return label

    def AddLabelMedium(self, state = uiconst.UI_DISABLED, wrapWidth = None, **keywords):
        if wrapWidth:
            keywords['width'] = wrapWidth
            keywords['autoFitToText'] = True
        label = EveLabelMedium(state=state, **keywords)
        self.AddCell(label, **keywords)
        return label

    def AddLabelLarge(self, state = uiconst.UI_DISABLED, wrapWidth = None, **keywords):
        if wrapWidth:
            keywords['width'] = wrapWidth
            keywords['autoFitToText'] = True
        label = EveLabelLarge(state=state, **keywords)
        self.AddCell(label, **keywords)
        return label

    def AddCaptionSmall(self, state = uiconst.UI_DISABLED, wrapWidth = None, **keywords):
        if wrapWidth:
            keywords['width'] = wrapWidth
            keywords['autoFitToText'] = True
        label = EveCaptionSmall(state=state, **keywords)
        self.AddCell(label, **keywords)
        return label

    def AddCaptionMedium(self, state = uiconst.UI_DISABLED, wrapWidth = None, **keywords):
        if wrapWidth:
            keywords['width'] = wrapWidth
            keywords['autoFitToText'] = True
        label = EveCaptionMedium(state=state, **keywords)
        self.AddCell(label, **keywords)
        return label

    def AddCaptionLarge(self, state = uiconst.UI_DISABLED, wrapWidth = None, **keywords):
        if wrapWidth:
            keywords['width'] = wrapWidth
            keywords['autoFitToText'] = True
        label = EveCaptionLarge(state=state, **keywords)
        self.AddCell(label, **keywords)
        return label

    def AddInfoIcon(self, typeID = None, itemID = None, align = uiconst.TOPRIGHT, **keywords):
        infoIcon = InfoIcon(typeID=typeID, itemID=itemID, align=align, left=0, top=0)
        self.AddCell(infoIcon, **keywords)
        return infoIcon

    def AddMediumHeader(self, labelColSpan = None, **keywords):
        row = self.AddHeaderRow()
        label = EveLabelMedium(**keywords)
        row.AddCell(label, colSpan=(labelColSpan or self.columns), **keywords)
        self.FillRow()
        return (row, label)

    def AddTextDetailsLabel(self, state = uiconst.UI_DISABLED, wrapWidth = None, **keywords):
        if wrapWidth:
            keywords['width'] = wrapWidth
            keywords['autoFitToText'] = True
        label = TextDetail(state=state, **keywords)
        self.AddCell(label, **keywords)
        return label

    def AddTextBodyLabel(self, state = uiconst.UI_DISABLED, wrapWidth = None, **keywords):
        if wrapWidth:
            keywords['width'] = wrapWidth
            keywords['autoFitToText'] = True
        label = TextBody(state=state, **keywords)
        self.AddCell(label, **keywords)
        return label

    def AddTextHeaderLabel(self, state = uiconst.UI_DISABLED, wrapWidth = None, **keywords):
        if wrapWidth:
            keywords['width'] = wrapWidth
            keywords['autoFitToText'] = True
        label = TextHeader(state=state, **keywords)
        self.AddCell(label, **keywords)
        return label

    def AddHeaderRow(self):
        self.FillRow()
        row = self.AddRow(cellPadding=(11, 9))
        Fill(bgParent=row, color=(1, 1, 1, 0.1))
        return row

    def LoadGeneric1ColumnTemplate(self):
        self.columns = 1
        self.LoadStandardSpacingOld()

    def LoadGeneric2ColumnTemplate(self):
        self.columns = 2
        self.LoadStandardSpacingOld()

    def LoadGeneric3ColumnTemplate(self):
        self.columns = 3
        self.LoadStandardSpacingOld()

    def LoadGeneric4ColumnTemplate(self):
        self.columns = 4
        self.LoadStandardSpacingOld()

    def LoadGeneric5ColumnTemplate(self):
        self.columns = 5
        self.LoadStandardSpacingOld()

    def LoadStandardSpacingOld(self):
        self.margin = (16, 16, 16, 16)
        self.cellPadding = 0
        self.cellSpacing = (8, 8)

    def LoadStandardSpacing(self):
        self.margin = (16, 16, 16, 16)
        self.cellPadding = (8, 0)
        self.cellSpacing = (0, 8)

    def SetSpacing(self, margin = (16, 16, 16, 16), cellPadding = (8, 0), cellSpacing = (0, 8)):
        self.margin = margin
        self.cellPadding = cellPadding
        self.cellSpacing = cellSpacing


class TooltipPersistentPanel(TooltipPanel):
    picktestEnabled = True
    checkIfBlocked = False

    def ApplyAttributes(self, attributes):
        TooltipPanel.ApplyAttributes(self, attributes)

    def DisablePickTest(self):
        self.picktestEnabled = False

    def HoldTillMouseOutside(self, graceTime):
        while not self.destroyed and self.owner and not self.owner.destroyed:
            if self.picktestEnabled:
                ownerPickable = self.IsOwnerPickable()
                if not ownerPickable:
                    self.opacity = 0.0
                else:
                    self.opacity = 1.0
            blue.synchro.SleepWallclock(5)

    def IsMouseInside(self):
        return True

    def Close(self, *args):
        PointerPanel.Close(self, *args)
