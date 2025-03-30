#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\primitives\containerAutoSize.py
import telemetry
from carbonui import uiconst, Align
from carbonui.primitives.container import Container
from carbonui.primitives.childrenlist import PyChildrenList as UIChildrenList
from carbonui.uianimations import animations
ALLOWED_ALIGNMENTS = (uiconst.TOLEFT,
 uiconst.TORIGHT,
 uiconst.TOTOP,
 uiconst.TOBOTTOM,
 uiconst.TOPLEFT,
 uiconst.TOPRIGHT,
 uiconst.CENTER,
 uiconst.CENTERTOP,
 uiconst.CENTERBOTTOM,
 uiconst.CENTERLEFT,
 uiconst.CENTERRIGHT,
 uiconst.BOTTOMLEFT,
 uiconst.BOTTOMRIGHT,
 uiconst.NOALIGN,
 uiconst.TOLEFT_NOPUSH,
 uiconst.TOTOP_NOPUSH,
 uiconst.TORIGHT_NOPUSH,
 uiconst.TOBOTTOM_NOPUSH,
 uiconst.TOTOP_STICKY)
ALIGNMENT_MAPPING = {Align.TOTOP_STICKY: Align.TOTOP}

def GetMappedAlignment(align):
    return ALIGNMENT_MAPPING.get(align, align)


class ContainerAutoSize(Container):
    default_align = uiconst.TOPLEFT
    default_alignMode = None
    _childrenAlign = None
    isAutoSizeEnabled = True
    alignMode = None
    callback = None

    def ApplyAttributes(self, attributes):
        self.alignMode = attributes.Get('alignMode', self.default_alignMode)
        self.callback = attributes.Get('callback', None)
        self._only_use_callback_when_size_changes = attributes.Get('only_use_callback_when_size_changes', False)
        self._isCollapsed = False
        Container.ApplyAttributes(self, attributes)

    @property
    def minWidth(self):
        return self._minWidth

    @minWidth.setter
    def minWidth(self, minWidth):
        if minWidth != self._minWidth:
            self._minWidth = minWidth
            if self.width < minWidth:
                self.FlagAlignmentDirty()

    @property
    def minHeight(self):
        return self._minHeight

    @minHeight.setter
    def minHeight(self, minHeight):
        if minHeight != self._minHeight:
            self._minHeight = minHeight
            if self.height < minHeight:
                self.FlagAlignmentDirty()

    @property
    def maxWidth(self):
        return self._maxWidth

    @maxWidth.setter
    def maxWidth(self, maxWidth):
        if maxWidth != self._maxWidth:
            self._maxWidth = maxWidth
            if self.width > maxWidth:
                self.FlagAlignmentDirty()

    @property
    def maxHeight(self):
        return self._maxHeight

    @maxHeight.setter
    def maxHeight(self, maxHeight):
        if maxHeight != self._maxHeight:
            self._maxHeight = maxHeight
            if self.height != maxHeight:
                self.FlagAlignmentDirty()

    @property
    def isCollapsed(self):
        return self._isCollapsed

    @telemetry.ZONE_METHOD
    def SetSizeAutomatically(self):
        if self.align == uiconst.TOALL:
            self.DisableAutoSize()
        if not self.isAutoSizeEnabled:
            return
        size_changed = False
        width, height = self.GetAutoSize()
        if width is not None:
            width_before = self.width
            if self.minWidth is not None:
                self.width = max(width, self.minWidth)
            elif self.maxWidth is not None:
                self.width = min(width, self.maxWidth)
            else:
                self.width = width
            if self.width != width_before:
                size_changed = True
        if height is not None:
            height_before = self.height
            if self.minHeight is not None:
                self.height = max(height, self.minHeight)
            elif self.maxHeight is not None:
                self.height = min(height, self.maxHeight)
            else:
                self.height = height
            if self.height != height_before:
                size_changed = True
        if self.callback and (not self._only_use_callback_when_size_changes or self._only_use_callback_when_size_changes and size_changed):
            self.callback()

    @telemetry.ZONE_METHOD
    def GetAutoSize(self):
        horizontal_padding = 0
        vertical_padding = 0
        if self.align in uiconst.ALIGNMENTS_WITH_INCLUDED_VERTICAL_PADDING:
            vertical_padding = self.padTop + self.padBottom
        if self.align in uiconst.ALIGNMENTS_WITH_INCLUDED_HORIZONTAL_PADDING:
            horizontal_padding = self.padLeft + self.padRight
        if self._childrenAlign in (uiconst.TOLEFT, uiconst.TORIGHT):
            width = 0
            for child in self.children:
                if self._IgnoreChild(child):
                    continue
                width += child.width + child.left + child.padLeft + child.padRight

            width += horizontal_padding
            return (width, None)
        elif self._childrenAlign in (uiconst.TOTOP,
         uiconst.TOBOTTOM,
         uiconst.TOTOP_NOPUSH,
         uiconst.TOBOTTOM_NOPUSH):
            height = 0
            for child in self.children:
                if self._IgnoreChild(child):
                    continue
                height += child.height + child.top + child.padTop + child.padBottom

            height += vertical_padding
            return (None, height)
        elif self._childrenAlign in ALLOWED_ALIGNMENTS:
            width = height = 0
            for child in self.children:
                if self._IgnoreChild(child):
                    continue
                x = child.left + child.width
                if x > width:
                    width = x
                y = child.top + child.height
                if y > height:
                    height = y

            width += horizontal_padding
            height += vertical_padding
            return (width, height)
        else:
            return (vertical_padding, horizontal_padding)

    def _IgnoreChild(self, child):
        if not child.display:
            return True
        if self.alignMode is not None and child.align != self._childrenAlign:
            return True
        return False

    @telemetry.ZONE_METHOD
    def _VerifyNewChild(self, child):
        if self.alignMode is not None:
            self._childrenAlign = GetMappedAlignment(self.alignMode)
            return
        if child.align not in ALLOWED_ALIGNMENTS:
            raise ValueError('ContainerAutoSize only supports TOLEFT, TORIGHT, TOTOP, TOBOTTOM, TOPLEFT, TOPRIGHT or CENTER aligned children')
        if self.children and GetMappedAlignment(child.align) != self._childrenAlign:
            raise ValueError('All children of ContainerAutoSize must have the same alignment (Got %s, expecting %s)' % (child.align, self._childrenAlign))
        if not self.children:
            self._childrenAlign = GetMappedAlignment(child.align)

    def GetChildrenList(self):
        return UIChildrenListAutoSize(self)

    def DisableAutoSize(self):
        self.isAutoSizeEnabled = False

    def EnableAutoSize(self):
        if not self.isAutoSizeEnabled:
            self.isAutoSizeEnabled = True
            self.SetSizeAutomatically()

    def UpdateAlignment(self, *args, **kwds):
        budget = Container.UpdateAlignment(self, *args, **kwds)
        if self._childrenAlign is not None:
            self.SetSizeAutomatically()
        if self._alignmentDirty:
            budget = Container.UpdateAlignment(self, *args, **kwds)
        return budget

    def CollapseHeight(self, duration = 0.2, callback = None):
        _, height = self.GetAutoSize()
        self._CollapseSize(attribute='height', value=height, duration=duration, callback=callback)

    def ExpandHeight(self, duration = 0.2, callback = None):
        _, height = self.GetAutoSize()
        self._ExpandSize(attribute='height', value=height, duration=duration, callback=callback)

    def CollapseWidth(self, duration = 0.2, callback = None):
        width, _ = self.GetAutoSize()
        self._CollapseSize(attribute='width', value=width, duration=duration, callback=callback)

    def ExpandWidth(self, duration = 0.2, callback = None):
        width, _ = self.GetAutoSize()
        self._ExpandSize(attribute='width', value=width, duration=duration, callback=callback)

    def _CollapseSize(self, attribute, value, duration, callback):
        self._isCollapsed = True
        self.DisableAutoSize()
        animations.MorphScalar(self, attribute, startVal=value, endVal=0, duration=duration, callback=callback)

    def _ExpandSize(self, attribute, value, duration, callback):
        self._isCollapsed = False
        self.DisableAutoSize()

        def after_animation():
            self.EnableAutoSize()
            if callback:
                callback()

        animations.MorphScalar(self, attribute, startVal=getattr(self, attribute, 0.0), endVal=value, duration=duration, callback=after_animation)


class UIChildrenListAutoSize(UIChildrenList):

    def append(self, obj):
        owner = self.GetOwner()
        if owner:
            owner._VerifyNewChild(obj)
            UIChildrenList.append(self, obj)

    def insert(self, idx, obj):
        owner = self.GetOwner()
        if owner:
            owner._VerifyNewChild(obj)
            UIChildrenList.insert(self, idx, obj)

    def remove(self, obj):
        owner = self.GetOwner()
        if owner:
            UIChildrenList.remove(self, obj)
            owner.FlagAlignmentDirty()
