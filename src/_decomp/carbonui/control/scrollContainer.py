#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\control\scrollContainer.py
import logging
import mathext
import signals
import uthread2
from carbonui import TextAlign, uiconst, Align
from carbonui.control.baseScrollContEntry import LazyLoadVerticalMixin
from carbonui.control.scrollbar import Scrollbar
from carbonui.decorative.panelUnderlay import PanelUnderlay
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.uianimations import animations
from carbonui.uiconst import Axis
from carbonui.uicore import uicore
from eve.client.script.ui.control.eveLabel import EveCaptionLarge
logger = logging.getLogger(__name__)

class ScrollContainer(Container):
    __guid__ = 'uicls.ScrollContainer'
    default_name = 'scrollContainer'
    default_pushContent = True
    default_state = uiconst.UI_NORMAL
    default_showUnderlay = False
    default_scrollBarColor = None
    default_alignMode = None
    default_scrollBarPadding = 0
    default_innerPadding = None
    default_centerContent = False
    default_scrollBarDisabled = False
    dragHoverScrollAreaSize = 30
    dragHoverScrollSpeed = 60.0
    isTabStop = True
    _scrollbar_vertical = None
    _scrollbar_horizontal = None

    def ApplyAttributes(self, attributes):
        super(ScrollContainer, self).ApplyAttributes(attributes)
        pushContent = attributes.get('pushContent', self.default_pushContent)
        showUnderlay = attributes.Get('showUnderlay', self.default_showUnderlay)
        self.fixedColor = attributes.get('scrollBarColor', self.default_scrollBarColor)
        alignMode = attributes.get('alignMode', self.default_alignMode)
        self.scrollBarPadding = attributes.get('scrollBarPadding', self.default_scrollBarPadding)
        self._innerPadding = attributes.get('innerPadding', self.default_innerPadding)
        self._centerContent = attributes.get('centerContent', self.default_centerContent)
        self.scrollbarsDisabled = self.default_scrollBarDisabled
        self.scrollToVerticalPending = None
        self.scrollToHorizontalPending = None
        self.noResultsContainer = None
        self.noResultsLabel = None
        self.onDownButtonSignal = signals.Signal(__name__ + '_onDownButtonSignal')
        self.onUpButtonSignal = signals.Signal(__name__ + '_onUpButtonSignal')
        self.onDropDataSignal = signals.Signal(__name__ + '_onDropDataSignal')
        self.onDragEnterSignal = signals.Signal(__name__ + '_onDragEnterSignal')
        self.onDragExitSignal = signals.Signal(__name__ + '_onDragExitSignal')
        self.onSizeChangeSignal = signals.Signal(__name__ + '_onSizeChangeSignal')
        self._ConstructVerticalScrollBar(pushContent)
        self._ConstructHorizontalScrollBar(pushContent)
        self.clipCont = Container(name='clipCont', parent=self, clipChildren=True)
        self.mainCont = ContainerAutoSize(name='mainCont', parent=self.clipCont, state=uiconst.UI_NORMAL, alignMode=alignMode, align=alignMode or ContainerAutoSize.default_align, padding=self._innerPadding)
        self.mainCont._OnSizeChange_NoBlock = self._OnMainContSizeChange
        self.mainCont.OnDropData = self.OnDropData
        self.children.insert = self._InsertChild
        self.children.append = self._AppendChild
        self.children.remove = self._RemoveChild
        self._mouseHoverCookie = uicore.uilib.RegisterForTriuiEvents(uiconst.UI_MOUSEHOVER, self.OnGlobalMouseHover)
        self.CheckConstructUnderlay(showUnderlay)

    def _update_children_alignment(self, sizeChange, forceUpdate):
        super(ScrollContainer, self)._update_children_alignment(sizeChange, forceUpdate)
        self._check_lazy_load_entries()

    @property
    def innerPadding(self):
        return self._innerPadding

    @innerPadding.setter
    def innerPadding(self, value):
        if self._innerPadding != value:
            self._innerPadding = value
            self.mainCont.padding = self._innerPadding if self._innerPadding is not None else 0

    def _ConstructHorizontalScrollBar(self, pushContent):
        self._scrollbar_horizontal = Scrollbar(parent=self, align=uiconst.TOBOTTOM, axis=Axis.HORIZONTAL, padTop=8 if pushContent else 0, on_scroll_fraction_changed=self._on_scrollbar_scroll_fraction_changed)

    def _ConstructVerticalScrollBar(self, pushContent):
        self._scrollbar_vertical = Scrollbar(parent=self, align=uiconst.TORIGHT, axis=Axis.VERTICAL, padLeft=8 if pushContent else 0, on_scroll_fraction_changed=self._on_scrollbar_scroll_fraction_changed)

    def _on_scrollbar_scroll_fraction_changed(self, scrollbar):
        if scrollbar.axis == Axis.VERTICAL:
            self._OnVerticalScrollBar(scrollbar.scroll_fraction)
        elif scrollbar.axis == Axis.HORIZONTAL:
            self._OnHorizontalScrollBar(scrollbar.scroll_fraction)

    def CheckConstructUnderlay(self, showUnderlay):
        if showUnderlay:
            self.underlay = PanelUnderlay(bgParent=self)
        else:
            self.underlay = None

    def Close(self, *args):
        try:
            uicore.uilib.UnregisterForTriuiEvents(self._mouseHoverCookie)
        except Exception as e:
            logger.exception(e)
        finally:
            Container.Close(self, *args)

        try:
            del self.mainCont._OnSizeChange_NoBlock
        except AttributeError:
            pass

    def _InsertChild(self, idx, obj):
        self.mainCont.children.insert(idx, obj)
        if not self.mainCont.alignMode:
            self.mainCont.align = obj.align

    def _AppendChild(self, obj):
        self.mainCont.children.append(obj)
        if not self.mainCont.alignMode:
            self.mainCont.align = obj.align

    def _RemoveChild(self, obj):
        self.mainCont.children.remove(obj)

    def OnGlobalMouseHover(self, obj, *args):
        if uicore.IsDragging() and (obj == self or obj.IsUnder(self.mainCont)):
            l, t, w, h = self.GetAbsolute()
            if self.IsVerticalScrollBarVisible() and h > 0:
                fraction = self.dragHoverScrollSpeed / float(h)
                y = uicore.uilib.y - t
                if y <= self.dragHoverScrollAreaSize:
                    self.ScrollMoveVertical(-fraction)
                elif y > h - self.dragHoverScrollAreaSize:
                    self.ScrollMoveVertical(fraction)
            if self.IsHorizontalScrollBarVisible() and w > 0:
                fraction = self.dragHoverScrollSpeed / float(w)
                x = uicore.uilib.x - l
                if x <= self.dragHoverScrollAreaSize:
                    self.ScrollMoveHorizontal(-fraction)
                elif x > w - self.dragHoverScrollAreaSize:
                    self.ScrollMoveHorizontal(fraction)
        return True

    def _OnSizeChange_NoBlock(self, width, height):
        main_cont_width, main_cont_height = self.mainCont.GetCurrentAbsoluteSize()
        self._retain_scroll_position_on_resize(main_cont_width, main_cont_height)
        self._UpdateHandleSizesAndPosition(width, height, updatePos=False)

    def _OnMainContSizeChange(self, width, height):
        self._retain_scroll_position_on_resize(width, height)
        self._UpdateScrollbars()
        self.onSizeChangeSignal(width, height)

    def _check_lazy_load_entries(self):
        any_lazy_loaded = False
        for entry in self.mainCont.children:
            if isinstance(entry, LazyLoadVerticalMixin):
                if entry.check_lazy_load(self.clipCont):
                    any_lazy_loaded = True
                elif any_lazy_loaded:
                    return

    def _retain_scroll_position_on_resize(self, width, height):
        clip_width, clip_height = self.clipCont.GetAbsoluteSize()
        scrollable_size_vertical = height - clip_height
        if scrollable_size_vertical <= 0.0:
            scroll_fraction = 0.0
        else:
            offset = 0
            if self.mainCont.align in (uiconst.CENTER, uiconst.CENTERLEFT, uiconst.CENTERRIGHT):
                offset = scrollable_size_vertical / 2.0
            scroll_fraction = mathext.clamp(value=float(-(self.mainCont.top - offset)) / scrollable_size_vertical, low=0.0, high=1.0)
        if mathext.is_close(scroll_fraction, self._scrollbar_vertical.scroll_fraction):
            self._OnVerticalScrollBar(scroll_fraction)
        else:
            self._scrollbar_vertical.scroll_fraction = scroll_fraction
        scrollable_size_horizontal = width - clip_width
        if scrollable_size_horizontal <= 0.0:
            scroll_fraction = 0.0
        else:
            offset = 0
            if self.mainCont.align in (uiconst.CENTER, uiconst.CENTERTOP, uiconst.CENTERBOTTOM):
                offset = scrollable_size_horizontal / 2.0
            scroll_fraction = mathext.clamp(value=float(-(self.mainCont.left - offset)) / scrollable_size_horizontal, low=0.0, high=1.0)
        if mathext.is_close(scroll_fraction, self._scrollbar_horizontal.scroll_fraction):
            self._OnHorizontalScrollBar(scroll_fraction)
        else:
            self._scrollbar_horizontal.scroll_fraction = scroll_fraction

    def OnDropData(self, dragSource, dragData):
        self.onDropDataSignal(dragSource, dragData)

    def OnDragEnter(self, dragSource, dragData):
        self.onDragEnterSignal(dragSource, dragData)

    def OnDragExit(self, dragSource, dragData):
        self.onDragExitSignal(dragSource, dragData)

    def Flush(self):
        self.mainCont.Flush()
        self.HideNoContentHint()

    def DisableScrollbars(self):
        self.scrollbarsDisabled = True
        self._UpdateScrollbars()

    def EnableScrollbars(self):
        self.scrollbarsDisabled = False
        self._UpdateScrollbars()

    def _UpdateScrollbars(self):
        w, h = self.GetAbsoluteSize()
        self._UpdateHandleSizesAndPosition(w, h)

    def _GetMainContWidth(self):
        width, _ = self.mainCont.GetCurrentAbsoluteSize()
        return width + self.mainCont.padLeft + self.mainCont.padRight

    def _GetMainContHeight(self):
        _, height = self.mainCont.GetCurrentAbsoluteSize()
        return height + self.mainCont.padTop + self.mainCont.padBottom

    def _UpdateHandleSizesAndPosition(self, width, height, updatePos = True):
        mainWidth = self._GetMainContWidth()
        mainHeight = self._GetMainContHeight()
        if mainHeight > 0 and not self.scrollbarsDisabled:
            size = float(height) / mainHeight
        else:
            size = 1.0
        size = mathext.clamp(size, 0.0, 1.0)
        self._scrollbar_vertical.handle_size_fraction = size
        self._scrollbar_vertical.display = not mathext.is_close(size, 1.0)
        if mainWidth != 0 and not self.scrollbarsDisabled:
            size = float(width) / mainWidth
        else:
            size = 1.0
        size = mathext.clamp(size, 0.0, 1.0)
        self._scrollbar_horizontal.handle_size_fraction = size
        self._scrollbar_horizontal.display = not mathext.is_close(size, 1.0)
        if self.IsHorizontalScrollBarVisible() and self.IsVerticalScrollBarVisible():
            self._scrollbar_vertical.padBottom = self._scrollbar_horizontal.height
        else:
            self._scrollbar_vertical.padBottom = 0

    def _OnVerticalScrollBar(self, posFraction):
        w, h = self.clipCont.GetAbsoluteSize()
        posFraction = max(0.0, min(posFraction, 1.0))
        mainHeight = self._GetMainContHeight()
        offset = 0
        if self.mainCont.align in (uiconst.CENTER, uiconst.CENTERLEFT, uiconst.CENTERRIGHT):
            offset = (mainHeight - h) / 2.0
        if mainHeight <= h:
            if self._centerContent:
                self.mainCont.top = int(round((h - mainHeight) / 2.0)) + offset
            else:
                self.mainCont.top = 0
        else:
            self.mainCont.top = -posFraction * (mainHeight - h) + offset
        for c in self.mainCont.children:
            if c.align == Align.TOTOP_STICKY:
                c.FlagAlignmentDirty()

        uthread2.start_tasklet(self._check_lazy_load_entries)
        self.OnScrolledVertical(posFraction)

    def _OnHorizontalScrollBar(self, posFraction):
        w, h = self.clipCont.GetAbsoluteSize()
        posFraction = max(0.0, min(posFraction, 1.0))
        mainWidth = self._GetMainContWidth()
        offset = 0
        if self.mainCont.align in (uiconst.CENTER, uiconst.CENTERTOP, uiconst.CENTERBOTTOM):
            offset = (mainWidth - w) / 2.0
        if mainWidth <= w:
            if self._centerContent:
                self.mainCont.left = int(round((w - mainWidth) / 2.0)) + offset
            else:
                self.mainCont.left = 0
        else:
            self.mainCont.left = -posFraction * (mainWidth - w) + offset
        uthread2.start_tasklet(self._check_lazy_load_entries)
        self.OnScrolledHorizontal(posFraction)

    def OnScrolledHorizontal(self, posFraction):
        pass

    def OnScrolledVertical(self, posFraction):
        pass

    def ScrollToVertical(self, posFraction):
        if posFraction is None:
            return
        if self._alignmentDirty:
            self.scrollToVerticalPending = posFraction
        elif self.IsVerticalScrollBarVisible():
            self._scrollbar_vertical.scroll_to_fraction(posFraction)

    def ScrollToHorizontal(self, posFraction):
        if posFraction is None:
            return
        if self._alignmentDirty:
            self.scrollToHorizontalPending = posFraction
        elif self.IsHorizontalScrollBarVisible():
            self._scrollbar_horizontal.scroll_to_fraction(posFraction)

    def GetPositionVertical(self):
        return self._scrollbar_vertical.scroll_fraction

    def GetPositionHorizontal(self):
        return self._scrollbar_horizontal.scroll_fraction

    def UpdateAlignment(self, *args, **kwds):
        ret = Container.UpdateAlignment(self, *args, **kwds)
        if self.scrollToVerticalPending:
            self._scrollbar_vertical.scroll_fraction = self.scrollToVerticalPending
        self.scrollToVerticalPending = None
        if self.scrollToHorizontalPending:
            self._scrollbar_horizontal.scroll_fraction = self.scrollToHorizontalPending
        self.scrollToHorizontalPending = None
        return ret

    def ScrollMoveVertical(self, moveFraction):
        self._scrollbar_vertical.scroll_to_fraction(mathext.clamp(self._scrollbar_vertical.scroll_fraction + moveFraction, 0.0, 1.0))

    def ScrollMoveHorizontal(self, moveFraction):
        self._scrollbar_horizontal.scroll_to_fraction(mathext.clamp(self._scrollbar_horizontal.scroll_fraction + moveFraction, 0.0, 1.0))

    def OnMouseWheel(self, dz, *args):
        scroll_pixels = -dz * 0.42
        self._scroll_by_pixels(scroll_pixels)

    def _scroll_by_pixels(self, scroll_pixels):
        if self.IsVerticalScrollBarVisible():
            scrollable_height = self._get_scrollable_height()
            scroll_proportion = scroll_pixels / float(scrollable_height)
            self.ScrollMoveVertical(mathext.clamp(scroll_proportion, -1.0, 1.0))
        elif self.IsHorizontalScrollBarVisible():
            scrollable_width = self._get_scrollable_width()
            scroll_proportion = scroll_pixels / float(scrollable_width)
            self.ScrollMoveHorizontal(mathext.clamp(scroll_proportion, -1.0, 1.0))

    def _get_scrollable_height(self):
        _, clip_height = self.clipCont.GetAbsoluteSize()
        return max(0, self._GetMainContHeight() - clip_height)

    def _get_scrollable_width(self):
        clip_width, _ = self.clipCont.GetAbsoluteSize()
        return max(0, self._GetMainContWidth() - clip_width)

    def IsHorizontalScrollBarVisible(self):
        return self._scrollbar_horizontal and self._scrollbar_horizontal.display

    def IsVerticalScrollBarVisible(self):
        return self._scrollbar_vertical and self._scrollbar_vertical.display

    def OnKeyDown(self, key, flag):
        if key == uiconst.VK_PRIOR:
            self.ScrollByPage(up=True)
        elif key == uiconst.VK_NEXT:
            self.ScrollByPage(up=False)

    def ScrollByPage(self, up = True):
        if not self.IsVerticalScrollBarVisible():
            return
        _, h = self.clipCont.GetAbsoluteSize()
        if up:
            h *= -1
        self._scroll_by_pixels(h)

    def ShowNoContentHint(self, hint):
        if not hint:
            if self.noResultsContainer:
                self.noResultsContainer.Hide()
            return
        isNew = self.noResultsLabel is None or self.noResultsLabel.GetText() != hint
        if self.noResultsContainer is None:
            self.ConstructNoContentContainer()
        self.noResultsLabel.SetText(hint)
        self.noResultsContainer.SetState(uiconst.UI_DISABLED)
        if isNew:
            animations.FadeTo(self.noResultsContainer, 0.0, 1.0, duration=0.3)

    def HideNoContentHint(self):
        if self.noResultsContainer:
            self.noResultsContainer.Close()
            self.noResultsContainer = None
            self.noResultsLabel = None

    def ConstructNoContentContainer(self):
        self.noResultsContainer = ContainerAutoSize(name='noResultsContainer', parent=self.clipCont, align=uiconst.TOTOP)
        self.noResultsLabel = EveCaptionLarge(name='noResultsLabel', parent=self.noResultsContainer, align=uiconst.TOTOP, textAlign=TextAlign.CENTER, padding=16, opacity=0.3)

    def OnUp(self):
        self.onUpButtonSignal()

    def OnDown(self):
        self.onDownButtonSignal()

    def ScrollToRevealChildHorizontal(self, child):
        child_left = 0
        for c in self.mainCont.children:
            child_left += c.padLeft
            if c is child:
                break
            w, _ = c.GetCurrentAbsoluteSize()
            child_left += w + c.padRight

        clip_width, _ = self.clipCont.GetCurrentAbsoluteSize()
        overflow_width = self._GetMainContWidth() - clip_width
        if overflow_width == 0:
            return
        child_width, _ = child.GetCurrentAbsoluteSize()
        fraction_scroll_left = abs(self.mainCont.left) / float(overflow_width)
        fraction_child_left = child_left / float(overflow_width)
        fraction_child_bottom = max(0.0, (child_left + child_width - clip_width) / float(overflow_width))
        if fraction_child_left <= fraction_scroll_left:
            self.ScrollToVertical(fraction_child_left)
        elif fraction_child_bottom > fraction_scroll_left:
            self.ScrollToVertical(fraction_child_bottom)

    def ScrollToRevealChildVertical(self, child):
        child_top = 0
        for c in self.mainCont.children:
            child_top += c.padTop
            if c is child:
                break
            _, h = c.GetCurrentAbsoluteSize()
            child_top += h + c.padBottom

        _, clip_height = self.clipCont.GetCurrentAbsoluteSize()
        overflow_height = self._GetMainContHeight() - clip_height
        if overflow_height == 0:
            return
        _, child_height = child.GetCurrentAbsoluteSize()
        fraction_scroll_top = abs(self.mainCont.top) / float(overflow_height)
        fraction_child_top = child_top / float(overflow_height)
        fraction_child_bottom = max(0.0, (child_top + child_height - clip_height) / float(overflow_height))
        if fraction_child_top <= fraction_scroll_top:
            self.ScrollToVertical(fraction_child_top)
        elif fraction_child_bottom > fraction_scroll_top:
            self.ScrollToVertical(fraction_child_bottom)

    def GetPositionVerticalPixels(self):
        return self._scrollbar_vertical.scroll_fraction * self._get_scrollable_height()

    def GetPositionHorizontalPixels(self):
        return self._scrollbar_horizontal.scroll_fraction * self._get_scrollable_width()

    def ScrollToVerticalPixels(self, position):
        scrollable_height = self._get_scrollable_height()
        if scrollable_height > 0:
            fraction = mathext.clamp(position / float(scrollable_height), 0.0, 1.0)
            self.ScrollToVertical(fraction)

    def ScrollToHorizontalPixels(self, position):
        scrollable_width = self._get_scrollable_width()
        if scrollable_width > 0:
            fraction = mathext.clamp(position / float(scrollable_width), 0.0, 1.0)
            self.ScrollToHorizontal(fraction)
