#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\primitives\base.py
import signals
import types
import telemetry
import trinity
from carbonui import uiconst
from carbonui.uiconst import PUSHALIGNMENTS, AFFECTEDBYPUSHALIGNMENTS, PickState, Align
from carbonui.primitives.dragdrop import DragDropObject
from carbonui.uicore import uicore
from carbonui.util.bunch import Bunch
from carbonui.util.dpi import ScaleDpi, ScaleDpiF, ReverseScaleDpi
DELEGATE_EVENTNAMES = ('OnMouseUp',
 'OnMouseDown',
 'OnMouseEnter',
 'OnMouseExit',
 'OnMouseHover',
 'OnMouseMove',
 'OnMouseWheel',
 'OnClick',
 'OnDblClick',
 'GetMenu',
 'OnMouseMoveDrag',
 'OnMouseDownDrag')

class Base(DragDropObject):
    __guid__ = 'uiprimitives.Base'
    __renderObject__ = None
    default_name = ''
    default_parent = None
    default_idx = -1
    default_state = uiconst.UI_NORMAL
    default_display = True
    default_pickState = PickState.ON
    default_align = uiconst.TOPLEFT
    default_hint = None
    default_left = 0
    default_top = 0
    default_width = 0
    default_height = 0
    default_padding = None
    default_padLeft = 0
    default_padTop = 0
    default_padRight = 0
    default_padBottom = 0
    default_cursor = None
    default_minWidth = None
    default_minHeight = None
    default_maxWidth = None
    default_maxHeight = None
    default_pickingMaskTexturePath = None
    default_aspectRatio = 1.0
    _left = 0
    _top = 0
    _width = 0
    _height = 0
    _align = None
    _display = True
    _minWidth = None
    _minHeight = None
    _maxWidth = None
    _maxHeight = None
    _sr = None
    _name = default_name
    _cursor = default_cursor
    _parentRef = None
    _alignmentDirty = False
    _forceUpdateAlignment = False
    _displayX = 0
    _displayY = 0
    _displayWidth = 0
    _displayHeight = 0
    _padLeft = 0
    _padTop = 0
    _padRight = 0
    _padBottom = 0
    _pickState = uiconst.TR2_SPS_ON
    _hint = None
    _tooltipPanelClassInfo = None
    _delegatingEvents = False
    _constructingBase = True
    __on_display_changed = None
    __on_size_changed = None
    destroyed = False
    renderObject = None
    auxiliaryHint = None
    isPushAligned = False
    isAffectedByPushAlignment = False
    isTransformed = False
    isAnimated = False
    uniqueUiName = None

    @telemetry.ZONE_METHOD
    def __init__(self, **kw):
        if self.__renderObject__:
            self.renderObject = RO = self.__renderObject__()
            uicore.uilib.RegisterObject(self, RO)
            RO.display = True
            RO.name = self.name
        attributesBunch = Bunch(**kw)
        self.ApplyAttributes(attributesBunch)

    @property
    def on_display_changed(self):
        if self.__on_display_changed is None:
            self.__on_display_changed = signals.Signal('{}.on_display_changed'.format(self.__class__.__name__))
        return self.__on_display_changed

    @property
    def on_size_changed(self):
        if self.__on_size_changed is None:
            self.__on_size_changed = signals.Signal('{}.__on_size_changed'.format(self.__class__.__name__))
        return self.__on_size_changed

    def _emit_on_size_changed(self, new_width, new_height):
        if self.__on_size_changed:
            self.on_size_changed(new_width, new_height)

    def __repr__(self):
        return '<{klass} object at {address:#016X}, name={name}, destroyed={destroyed}>'.format(klass=self.__class__.__name__, address=id(self), name=self._get_ui_element_name(), destroyed=self.destroyed)

    def _get_ui_element_name(self):
        if self.name:
            try:
                return self.name.encode('utf8')
            except UnicodeDecodeError:
                try:
                    return '{name}'.format(name=self.name)
                except Exception:
                    pass

        return 'None'

    @telemetry.ZONE_METHOD
    def ApplyAttributes(self, attributes):
        self._cursor = attributes.get('cursor', self.default_cursor)
        self._hint = attributes.get('hint', self.default_hint)
        if 'name' in attributes and attributes.name is not None:
            self.name = attributes.name
        if 'uniqueUiName' in attributes:
            self.uniqueUiName = attributes.uniqueUiName
        self.SetAlign(attributes.get('align', self.default_align))
        pos = attributes.pos
        if pos is not None:
            self.pos = pos
        else:
            left = attributes.get('left', self.default_left)
            top = attributes.get('top', self.default_top)
            width = attributes.get('width', self.default_width)
            height = attributes.get('height', self.default_height)
            self.pos = (left,
             top,
             width,
             height)
        padding = attributes.get('padding', self.default_padding)
        if padding is not None:
            self.padding = padding
        else:
            padLeft = attributes.get('padLeft', self.default_padLeft)
            padTop = attributes.get('padTop', self.default_padTop)
            padRight = attributes.get('padRight', self.default_padRight)
            padBottom = attributes.get('padBottom', self.default_padBottom)
            self.padding = (padLeft,
             padTop,
             padRight,
             padBottom)
        self._aspectRatio = float(attributes.get('aspectRatio', self.default_aspectRatio))
        self._minWidth = attributes.get('minWidth', self.default_minWidth)
        self._minHeight = attributes.get('minHeight', self.default_minHeight)
        self._maxWidth = attributes.get('maxWidth', self.default_maxWidth)
        self._maxHeight = attributes.get('maxHeight', self.default_maxHeight)
        pickingMaskTexturePath = attributes.get('pickingMaskTexturePath', self.default_pickingMaskTexturePath)
        if pickingMaskTexturePath:
            self.pickingMaskTexturePath = pickingMaskTexturePath
        if 'pickState' in attributes or 'display' in attributes:
            self.display = attributes.get('display', self.default_display)
            self.pickState = attributes.get('pickState', self.default_pickState)
        else:
            self.SetState(attributes.get('state', self.default_state))
        if attributes.get('bgParent', None):
            idx = attributes.get('idx', self.default_idx)
            if idx is None:
                idx = -1
            attributes.bgParent.background.insert(idx, self)
        else:
            parent = attributes.get('parent', self.default_parent)
            if parent and not parent.destroyed:
                self.SetParent(parent, attributes.get('idx', self.default_idx))
        self._constructingBase = False
        self.FlagAlignmentDirty()

    def Close(self):
        if getattr(self, 'destroyed', False):
            return
        self.destroyed = True
        uicore.uilib.ReleaseObject(self)
        notifyevents = getattr(self, '__notifyevents__', None)
        if notifyevents:
            sm.UnregisterNotify(self)
        self._OnClose()
        parent = self.parent
        if parent and not parent._containerClosing:
            parent.children.remove(self)
            parent.background.remove(self)
        if self.isAnimated:
            self.StopAnimations()
        self.renderObject = None
        self._alignFunc = None
        if self._delegatingEvents:
            for eventName in DELEGATE_EVENTNAMES:
                setattr(self, eventName, None)

    def _GetSR(self):
        if self._sr is None:
            self._sr = Bunch()
        return self._sr

    sr = property(_GetSR)

    def HasEventHandler(self, handlerName):
        handlerArgs, handler = self.FindEventHandler(handlerName)
        if not handler:
            return False
        baseHandler = getattr(Base, handlerName, None)
        if baseHandler and getattr(handler, 'im_func', None) is baseHandler.im_func:
            return False
        return bool(handler)

    def FindEventHandler(self, handlerName):
        handler = getattr(self, handlerName, None)
        if not handler:
            return (None, None)
        if type(handler) == types.TupleType:
            handlerArgs = handler[1:]
            handler = handler[0]
        else:
            handlerArgs = ()
        return (handlerArgs, handler)

    def StopAnimations(self):
        uicore.animations.StopAllAnimations(self)

    def HasAnimation(self, attrName):
        curveSet = uicore.animations.GetAnimationCurveSet(self, attrName)
        return curveSet is not None

    def GetRenderObject(self):
        return self.renderObject

    def SetParent(self, parent, idx = None):
        currentParent = self.parent
        if currentParent:
            if self in currentParent.children:
                currentParent.children.remove(self)
        if parent is not None:
            self.isTransformed = parent.isTransformed or self.isTransformed
            if idx is None:
                idx = -1
            parent.children.insert(idx, self)

    def GetParent(self):
        if self._parentRef:
            return self._parentRef()

    parent = property(GetParent)

    def SetOrder(self, idx):
        parent = self.parent
        if parent:
            currentIndex = self.GetOrder()
            if currentIndex != idx:
                self.SetParent(parent, idx)

    def GetOrder(self):
        parent = self.parent
        if parent:
            return parent.children.index(self)

    @property
    def pos(self):
        return (self._left,
         self._top,
         self._width,
         self._height)

    @pos.setter
    def pos(self, value):
        left, top, width, height = value
        if left < 1.0:
            adjustedLeft = left
        else:
            adjustedLeft = int(round(left))
        if top < 1.0:
            adjustedTop = top
        else:
            adjustedTop = int(round(top))
        if width < 1.0:
            adjustedWidth = width
        else:
            adjustedWidth = int(round(width))
        if height < 1.0:
            adjustedHeight = height
        else:
            adjustedHeight = int(round(height))
        if self._left != adjustedLeft or self._top != adjustedTop or self._width != adjustedWidth or self._height != adjustedHeight:
            self._left = adjustedLeft
            self._top = adjustedTop
            self._width = adjustedWidth
            self._height = adjustedHeight
            self.FlagAlignmentDirty()

    @property
    def left(self):
        return self._left

    @left.setter
    def left(self, value):
        if value < 1.0:
            adjustedValue = value
        else:
            adjustedValue = int(round(value))
        if adjustedValue != self._left:
            self._left = adjustedValue
            self.FlagAlignmentDirty()

    @property
    def top(self):
        return self._top

    @top.setter
    def top(self, value):
        if value < 1.0:
            adjustedValue = value
        else:
            adjustedValue = int(round(value))
        if adjustedValue != self._top:
            self._top = adjustedValue
            self.FlagAlignmentDirty()

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, value):
        if value < 1.0:
            adjustedValue = value
        else:
            adjustedValue = int(round(value))
        if adjustedValue != self._width:
            self._width = adjustedValue
            self.FlagAlignmentDirty()

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, value):
        if value < 1.0:
            adjustedValue = value
        else:
            adjustedValue = int(round(value))
        if adjustedValue != self._height:
            self._height = adjustedValue
            self.FlagAlignmentDirty()

    @property
    def maxWidth(self):
        return self._maxWidth

    @maxWidth.setter
    def maxWidth(self, value):
        if value != self._maxWidth:
            self._maxWidth = value
            self.FlagAlignmentDirty()

    @property
    def maxHeight(self):
        return self._maxHeight

    @maxHeight.setter
    def maxHeight(self, value):
        if value != self._maxHeight:
            self._maxHeight = value
            self.FlagAlignmentDirty()

    @property
    def minWidth(self):
        return self._minWidth

    @minWidth.setter
    def minWidth(self, value):
        if value != self._minWidth:
            self._minWidth = value
            self.FlagAlignmentDirty()

    @property
    def minHeight(self):
        return self._minHeight

    @minHeight.setter
    def minHeight(self, value):
        if value != self._minHeight:
            self._minHeight = value
            self.FlagAlignmentDirty()

    @property
    def padding(self):
        return (self._padLeft,
         self._padTop,
         self._padRight,
         self._padBottom)

    @padding.setter
    def padding(self, value):
        if isinstance(value, (tuple, list)):
            padLeft, padTop, padRight, padBottom = value
        else:
            padLeft = padTop = padRight = padBottom = value
        if self._padLeft != padLeft or self._padTop != padTop or self._padRight != padRight or self._padBottom != padBottom:
            self._padLeft = padLeft
            self._padTop = padTop
            self._padRight = padRight
            self._padBottom = padBottom
            self.FlagAlignmentDirty()

    @property
    def padLeft(self):
        return self._padLeft

    @padLeft.setter
    def padLeft(self, value):
        if value != self._padLeft:
            self._padLeft = value
            self.FlagAlignmentDirty()

    @property
    def padRight(self):
        return self._padRight

    @padRight.setter
    def padRight(self, value):
        if value != self._padRight:
            self._padRight = value
            self.FlagAlignmentDirty()

    @property
    def padTop(self):
        return self._padTop

    @padTop.setter
    def padTop(self, value):
        if value != self._padTop:
            self._padTop = value
            self.FlagAlignmentDirty()

    @property
    def padBottom(self):
        return self._padBottom

    @padBottom.setter
    def padBottom(self, value):
        if value != self._padBottom:
            self._padBottom = value
            self.FlagAlignmentDirty()

    @property
    def display(self):
        return self._GetDisplay()

    @display.setter
    def display(self, value):
        self._SetDisplay(value)

    def _GetDisplay(self):
        return self._display

    def _SetDisplay(self, value):
        if value != self._display:
            RO = self.renderObject
            if RO:
                RO.display = value
            if value:
                self._display = value
            self.FlagAlignmentDirty()
            self._display = value
            self.FlagForceUpdateAlignment()
            self._emit_on_display_changed()

    def _emit_on_display_changed(self):
        if self.__on_display_changed is not None:
            self.__on_display_changed(self)

    def FlagForceUpdateAlignment(self):
        self.FlagAlignmentDirty()
        self._forceUpdateAlignment = True

    def SetAlign(self, align):
        if align == self._align:
            return
        if hasattr(self.renderObject, 'absoluteCoordinates'):
            if align == uiconst.ABSOLUTE:
                self.renderObject.absoluteCoordinates = True
            else:
                self.renderObject.absoluteCoordinates = False
        self._alignFunc, self.isPushAligned, self.isAffectedByPushAlignment = ALIGN_AND_CONSUME_FUNCTIONS[align]
        oldAlign = self._align
        self._align = align
        self.FlagAlignmentDirty()
        if uiconst.is_push_alignment(oldAlign) != uiconst.is_push_alignment(align):
            parent = self.parent
            if parent is not None and not parent.destroyed:
                siblings = getattr(parent, 'children', [])
                found_self = False
                for sibling in siblings:
                    if sibling == self:
                        found_self = True
                    elif found_self and sibling.isAffectedByPushAlignment:
                        sibling._alignmentDirty = True

    def GetAlign(self):
        return self._align

    @property
    def align(self):
        return self.GetAlign()

    @align.setter
    def align(self, value):
        self.SetAlign(value)

    @property
    def name(self):
        return self._name or self.default_name or self.__class__.__name__

    @name.setter
    def name(self, value):
        self._name = value
        ro = self.renderObject
        if ro:
            ro.name = value

    @property
    def translation(self):
        return (self._displayX, self._displayY)

    @translation.setter
    def translation(self, value):
        self._displayX = value[0]
        self._displayY = value[1]
        ro = self.renderObject
        if ro:
            ro.displayX = self._displayX
            ro.displayY = self._displayY

    @property
    def displayRect(self):
        return (self._displayX,
         self._displayY,
         self._displayWidth,
         self._displayHeight)

    @displayRect.setter
    def displayRect(self, value):
        displayX, displayY, displayWidth, displayHeight = value
        self._displayX = int(round(displayX))
        self._displayY = int(round(displayY))
        self._displayWidth = int(round(displayX + displayWidth)) - self._displayX
        self._displayHeight = int(round(displayY + displayHeight)) - self._displayY
        if self._displayWidth == 0 and round(displayWidth) > 0:
            self._displayWidth = 1
        if self._displayHeight == 0 and round(displayHeight) > 0:
            self._displayHeight = 1
        ro = self.renderObject
        if ro:
            ro.displayX = self._displayX
            ro.displayY = self._displayY
            ro.displayWidth = self._displayWidth
            ro.displayHeight = self._displayHeight

    @property
    def displayX(self):
        return self._displayX

    @displayX.setter
    def displayX(self, value):
        self._displayX = int(round(value))
        ro = self.renderObject
        if ro:
            ro.displayX = self._displayX

    @property
    def displayY(self):
        return self._displayY

    @displayY.setter
    def displayY(self, value):
        self._displayY = int(round(value))
        ro = self.renderObject
        if ro:
            ro.displayY = self._displayY

    @property
    def displayWidth(self):
        return self._displayWidth

    @displayWidth.setter
    def displayWidth(self, value):
        self._displayWidth = int(round(value))
        ro = self.renderObject
        if ro:
            ro.displayWidth = self._displayWidth

    @property
    def displayHeight(self):
        return self._displayHeight

    @displayHeight.setter
    def displayHeight(self, value):
        self._displayHeight = int(round(value))
        ro = self.renderObject
        if ro:
            ro.displayHeight = self._displayHeight

    @property
    def pickState(self):
        return self._pickState

    @pickState.setter
    def pickState(self, value):
        self._pickState = value
        ro = self.renderObject
        if ro:
            ro.pickState = value

    def Disable(self, *args):
        self.pickState = uiconst.TR2_SPS_OFF

    def Enable(self, *args):
        self.pickState = uiconst.TR2_SPS_ON

    def IsEnabled(self):
        return self.pickState == uiconst.TR2_SPS_ON

    def SetFocus(self, *args):
        pass

    def SetHint(self, hint):
        self.hint = hint

    def GetHint(self):
        return self.hint

    @property
    def hint(self):
        return self._hint

    @hint.setter
    def hint(self, value):
        if value != self._hint:
            self._hint = value
            if self is uicore.uilib.mouseOver:
                uicore.uilib.UpdateTooltip(instant=True)

    @property
    def tooltipPanelClassInfo(self):
        return self._tooltipPanelClassInfo

    @tooltipPanelClassInfo.setter
    def tooltipPanelClassInfo(self, value):
        if value != self._tooltipPanelClassInfo:
            self._tooltipPanelClassInfo = value
            if self is uicore.uilib.mouseOver:
                uicore.uilib.RefreshTooltipForOwner(owner=self)

    def SetDisplayRect(self, displayRect):
        align = self.GetAlign()
        if align != uiconst.NOALIGN:
            return
        self.displayRect = displayRect

    def SetPosition(self, left, top):
        self.left = left
        self.top = top

    def GetPosition(self):
        return (self.left, self.top)

    def IsClickable(self):
        if self.destroyed or not hasattr(self, 'state') or not hasattr(self, 'parent'):
            return False
        if self.state not in (uiconst.UI_NORMAL, uiconst.UI_PICKCHILDREN):
            return False
        dad = self.parent
        if dad is uicore.desktop:
            return True
        return dad.IsClickable()

    def IsVisibleAndClickable(self):
        if self.destroyed or not hasattr(self, 'state') or not hasattr(self, 'display') or not hasattr(self, 'parent'):
            return False
        if self.state != uiconst.UI_NORMAL or not self.display:
            return False
        dad = self.parent
        if dad is uicore.desktop:
            return True
        return dad.IsVisibleAndClickable()

    def IsUnder(self, ancestor_maybe, retfailed = False):
        dad = self.parent
        if not dad:
            if retfailed:
                return self
            return False
        if dad is ancestor_maybe:
            return True
        return dad.IsUnder(ancestor_maybe, retfailed)

    def IsUnderClass(self, parentClass, returnParent = False):
        dad = self.parent
        if not dad:
            if returnParent:
                return None
            return False
        if isinstance(dad, parentClass):
            if returnParent:
                return dad
            return True
        return dad.IsUnderClass(parentClass, returnParent)

    def IsVisible(self):
        if self.destroyed or not hasattr(self, 'state') or not hasattr(self, 'parent'):
            return False
        if self.state == uiconst.UI_HIDDEN:
            return False
        dad = self.parent
        if not dad:
            return False
        if dad.state == uiconst.UI_HIDDEN:
            return False
        if dad is uicore.desktop:
            return True
        return dad.IsVisible()

    def IsClippedBy(self, clipper):
        return self.IsCompletelyClipped(clipper) or self.IsPartiallyClipped(clipper)

    def IsCompletelyClipped(self, clipper):
        if self.GetAbsoluteTop() >= clipper.GetAbsoluteBottom():
            return True
        elif self.GetAbsoluteBottom() <= clipper.GetAbsoluteTop():
            return True
        elif self.GetAbsoluteRight() <= clipper.GetAbsoluteLeft():
            return True
        elif self.GetAbsoluteLeft() >= clipper.GetAbsoluteRight():
            return True
        else:
            return False

    def IsPartiallyClipped(self, clipper):
        if self.GetAbsoluteTop() < clipper.GetAbsoluteTop():
            return True
        elif self.GetAbsoluteBottom() > clipper.GetAbsoluteBottom():
            return True
        elif self.GetAbsoluteRight() > clipper.GetAbsoluteRight():
            return True
        elif self.GetAbsoluteLeft() < clipper.GetAbsoluteLeft():
            return True
        else:
            return False

    def GetClipper(self):
        if not self.parent:
            return None
        elif self.parent.clipChildren:
            return self.parent
        else:
            return self.parent.GetClipper()

    def SetSize(self, width, height):
        self.width = width
        self.height = height

    def GetSize(self):
        return (self.width, self.height)

    def GetAbsoluteViewport(self):
        if not self.display:
            return (0, 0, 0, 0)
        w, h = self.GetAbsoluteSize()
        l, t = self.GetAbsolutePosition()
        return (l,
         t,
         w,
         h)

    def GetAbsolute(self):
        if not self.display:
            return (0, 0, 0, 0)
        w, h = self.GetAbsoluteSize()
        l, t = self.GetAbsolutePosition()
        return (l,
         t,
         w,
         h)

    @telemetry.ZONE_METHOD
    def GetAbsoluteSize(self):
        if self.destroyed or not self.display:
            return (0, 0)
        if self.isTransformed:
            scaleX, scaleY = self._GetAbsoluteScale()
        else:
            scaleX, scaleY = (1.0, 1.0)
        self._AssureAlignmentUpdated()
        return (ReverseScaleDpi(scaleX * self.displayWidth), ReverseScaleDpi(scaleY * self.displayHeight))

    def _GetAbsoluteScale(self):
        if hasattr(self, '_GetScale'):
            scaleX, scaleY = self._GetScale()
        else:
            scaleX, scaleY = (1.0, 1.0)
        parent = self.parent
        if parent:
            parScaleX, parScaleY = parent._GetAbsoluteScale()
            scaleX *= parScaleX
            scaleY *= parScaleY
        return (scaleX, scaleY)

    def _GetScale(self):
        return (1.0, 1.0)

    def GetCurrentAbsolutePosition(self):
        if self.destroyed or not self.display:
            return (0, 0)
        left, top = self._GetAbsolutePosition(0, 0)
        return (ReverseScaleDpi(left), ReverseScaleDpi(top))

    def GetCurrentAbsoluteSize(self):
        if self.destroyed or not self.display:
            return (0, 0)
        return (ReverseScaleDpi(self.displayWidth), ReverseScaleDpi(self.displayHeight))

    def _AssureAlignmentUpdated(self):
        if self._alignmentDirty or self._forceUpdateAlignment:
            parent = self.parent
            if parent:
                prevParent = None
                while parent:
                    if not parent.isAffectedByPushAlignment and not parent._alignmentDirty:
                        break
                    if not parent._childrenAlignmentDirty and not parent._forceUpdateAlignment:
                        break
                    if not parent.display:
                        break
                    prevParent = parent
                    parent = parent.parent

                parent = parent or prevParent
                if not parent.isAffectedByPushAlignment:
                    oldDisplayWidth = parent.displayWidth
                    oldDisplayHeight = parent.displayHeight
                    parent.displayWidth = ScaleDpiF(parent.width)
                    parent.displayHeight = ScaleDpiF(parent.height)
                    sizeChanged = oldDisplayWidth != parent.displayWidth or oldDisplayHeight != parent.displayHeight
                    if sizeChanged:
                        for each in parent.children:
                            each.FlagAlignmentDirty()

                parent.UpdateAlignment(updateChildrenOnly=True)

    @telemetry.ZONE_METHOD
    def GetAbsolutePosition(self):
        if self.destroyed or not self.display:
            return (0, 0)
        self._AssureAlignmentUpdated()
        l, t = self._GetAbsolutePosition(0, 0)
        return (ReverseScaleDpi(l), ReverseScaleDpi(t))

    def _GetAbsolutePosition(self, childLeft, childTop):
        parent = self.GetParent()
        left, top = self._GetRelativePosition()
        left += childLeft
        top += childTop
        if parent and self.align != uiconst.ABSOLUTE:
            left, top = parent._GetAbsolutePosition(left, top)
        return (left, top)

    def _GetRelativePosition(self):
        if self.renderObject:
            return (self.renderObject.displayX, self.renderObject.displayY)
        else:
            return (self.displayX, self.displayY)

    def GetAbsoluteLeft(self):
        l, t = self.GetAbsolutePosition()
        return l

    absoluteLeft = property(GetAbsoluteLeft)

    def GetAbsoluteTop(self):
        l, t = self.GetAbsolutePosition()
        return t

    absoluteTop = property(GetAbsoluteTop)

    def GetAbsoluteBottom(self):
        l, t = self.GetAbsolutePosition()
        w, h = self.GetAbsoluteSize()
        return t + h

    absoluteBottom = property(GetAbsoluteBottom)

    def GetAbsoluteRight(self):
        l, t = self.GetAbsolutePosition()
        w, h = self.GetAbsoluteSize()
        return l + w

    absoluteRight = property(GetAbsoluteRight)

    def GetUniqueName(self):
        return self.uniqueUiName

    def SetState(self, state):
        if state == uiconst.UI_NORMAL:
            self.display = True
            self.pickState = uiconst.TR2_SPS_ON
        elif state == uiconst.UI_DISABLED:
            self.display = True
            self.pickState = uiconst.TR2_SPS_OFF
        elif state == uiconst.UI_HIDDEN:
            self.display = False
        elif state == uiconst.UI_PICKCHILDREN:
            self.display = True
            self.pickState = uiconst.TR2_SPS_CHILDREN

    def GetState(self):
        if not self.display:
            return uiconst.UI_HIDDEN
        if self.pickState == uiconst.TR2_SPS_CHILDREN:
            return uiconst.UI_PICKCHILDREN
        if self.pickState == uiconst.TR2_SPS_ON:
            return uiconst.UI_NORMAL
        if self.pickState == uiconst.TR2_SPS_OFF:
            return uiconst.UI_DISABLED

    @property
    def state(self):
        return self.GetState()

    @state.setter
    def state(self, newState):
        self.SetState(newState)

    @property
    def pickingMaskTexturePath(self):
        if self.renderObject and self.renderObject.pickingMask:
            return self.renderObject.pickingMask.maskPath

    @pickingMaskTexturePath.setter
    def pickingMaskTexturePath(self, pickingMaskTexturePath):
        if self.renderObject:
            if pickingMaskTexturePath:
                self.renderObject.pickingMask = trinity.Tr2Sprite2dPickingMask()
                self.renderObject.pickingMask.maskPath = unicode(pickingMaskTexturePath)
            else:
                self.renderObject.pickingMask = None

    @property
    def pickingMaskLeftEdgeSize(self):
        if self.pickingMaskTexturePath:
            return self.renderObject.pickingMask.leftEdge

    @pickingMaskLeftEdgeSize.setter
    def pickingMaskLeftEdgeSize(self, value):
        if self.pickingMaskTexturePath:
            self.renderObject.pickingMask.leftEdge = value

    @property
    def pickingMaskRightEdgeSize(self):
        if self.pickingMaskTexturePath:
            return self.renderObject.pickingMask.rightEdge

    @pickingMaskRightEdgeSize.setter
    def pickingMaskRightEdgeSize(self, value):
        if self.pickingMaskTexturePath:
            self.renderObject.pickingMask.rightEdge = value

    @property
    def pickingMaskTopEdgeSize(self):
        if self.pickingMaskTexturePath:
            return self.renderObject.pickingMask.topEdge

    @pickingMaskTopEdgeSize.setter
    def pickingMaskTopEdgeSize(self, value):
        if self.pickingMaskTexturePath:
            self.renderObject.pickingMask.topEdge = value

    @property
    def pickingMaskBottomEdgeSize(self):
        if self.pickingMaskTexturePath:
            return self.renderObject.pickingMask.bottomEdge

    @pickingMaskBottomEdgeSize.setter
    def pickingMaskBottomEdgeSize(self, value):
        if self.pickingMaskTexturePath:
            self.renderObject.pickingMask.bottomEdge = value

    def FlagAlignmentDirty(self, hint = None):
        if not self.display or self._constructingBase:
            return
        self._alignmentDirty = True
        flagObj = self.parent
        if flagObj and (flagObj._childrenAlignmentDirty or not flagObj._display):
            return
        while flagObj:
            flagObj._childrenAlignmentDirty = True
            if flagObj.align == uiconst.NOALIGN:
                uicore.uilib.alignIslands.add(flagObj)
                return
            flagObj = flagObj.parent
            if flagObj and (flagObj._childrenAlignmentDirty or not flagObj._display):
                return

    @telemetry.ZONE_METHOD
    def UpdateToLeftAlignment(self, budgetOnly, budgetLeft, budgetTop, budgetWidth, budgetHeight):
        padLeft, padTop, padRight, padBottom = self.padding
        left, top, width, height = self.pos
        if not budgetOnly:
            displayX = budgetLeft + ScaleDpiF(padLeft + left)
            displayY = budgetTop + ScaleDpiF(padTop + top)
            displayHeight = budgetHeight - ScaleDpiF(padTop + padBottom)
            displayWidth = ScaleDpiF(width)
            self.displayRect = (displayX,
             displayY,
             displayWidth,
             displayHeight)
        widthUsed = ScaleDpiF(padLeft + width + left + padRight)
        budgetLeft += widthUsed
        budgetWidth -= widthUsed
        return (budgetLeft,
         budgetTop,
         budgetWidth,
         budgetHeight)

    @telemetry.ZONE_METHOD
    def UpdateToLeftAlignmentNoPush(self, budgetOnly, budgetLeft, budgetTop, budgetWidth, budgetHeight):
        padLeft, padTop, padRight, padBottom = self.padding
        left, top, width, height = self.pos
        if not budgetOnly:
            displayX = budgetLeft + ScaleDpiF(padLeft + left)
            displayY = budgetTop + ScaleDpiF(padTop + top)
            displayHeight = budgetHeight - ScaleDpiF(padTop + padBottom)
            displayWidth = ScaleDpiF(width)
            self.displayRect = (displayX,
             displayY,
             displayWidth,
             displayHeight)
        return (budgetLeft,
         budgetTop,
         budgetWidth,
         budgetHeight)

    @telemetry.ZONE_METHOD
    def UpdateToRightAlignment(self, budgetOnly, budgetLeft, budgetTop, budgetWidth, budgetHeight):
        padLeft, padTop, padRight, padBottom = self.padding
        left, top, width, height = self.pos
        if not budgetOnly:
            displayX = budgetLeft + budgetWidth - ScaleDpiF(width + padRight + left)
            displayY = budgetTop + ScaleDpiF(padTop + top)
            displayHeight = budgetHeight - ScaleDpiF(padTop + padBottom)
            displayWidth = ScaleDpiF(width)
            self.displayRect = (displayX,
             displayY,
             displayWidth,
             displayHeight)
        widthUsed = ScaleDpiF(padLeft + width + padRight + left)
        budgetWidth -= widthUsed
        return (budgetLeft,
         budgetTop,
         budgetWidth,
         budgetHeight)

    @telemetry.ZONE_METHOD
    def UpdateToRightAlignmentNoPush(self, budgetOnly, budgetLeft, budgetTop, budgetWidth, budgetHeight):
        padLeft, padTop, padRight, padBottom = self.padding
        left, top, width, height = self.pos
        if not budgetOnly:
            displayX = budgetLeft + budgetWidth - ScaleDpiF(width + padRight + left)
            displayY = budgetTop + ScaleDpiF(padTop + top)
            displayHeight = budgetHeight - ScaleDpiF(padTop + padBottom)
            displayWidth = ScaleDpiF(width)
            self.displayRect = (displayX,
             displayY,
             displayWidth,
             displayHeight)
        return (budgetLeft,
         budgetTop,
         budgetWidth,
         budgetHeight)

    @telemetry.ZONE_METHOD
    def UpdateToBottomAlignment(self, budgetOnly, budgetLeft, budgetTop, budgetWidth, budgetHeight):
        padLeft, padTop, padRight, padBottom = self.padding
        left, top, width, height = self.pos
        if not budgetOnly:
            displayX = budgetLeft + ScaleDpiF(padLeft + left)
            displayY = budgetTop + budgetHeight - ScaleDpiF(height + padBottom + top)
            displayWidth = budgetWidth - ScaleDpiF(padLeft + padRight)
            displayHeight = ScaleDpiF(height)
            self.displayRect = (displayX,
             displayY,
             displayWidth,
             displayHeight)
        heightUsed = ScaleDpiF(padTop + height + top + padBottom)
        budgetHeight -= heightUsed
        return (budgetLeft,
         budgetTop,
         budgetWidth,
         budgetHeight)

    @telemetry.ZONE_METHOD
    def UpdateToBottomAlignmentNoPush(self, budgetOnly, budgetLeft, budgetTop, budgetWidth, budgetHeight):
        padLeft, padTop, padRight, padBottom = self.padding
        left, top, width, height = self.pos
        if not budgetOnly:
            displayX = budgetLeft + ScaleDpiF(padLeft + left)
            displayY = budgetTop + budgetHeight - ScaleDpiF(height + padBottom + top)
            displayWidth = budgetWidth - ScaleDpiF(padLeft + padRight)
            displayHeight = ScaleDpiF(height)
            self.displayRect = (displayX,
             displayY,
             displayWidth,
             displayHeight)
        return (budgetLeft,
         budgetTop,
         budgetWidth,
         budgetHeight)

    @telemetry.ZONE_METHOD
    def UpdateToTopAlignment(self, budgetOnly, budgetLeft, budgetTop, budgetWidth, budgetHeight):
        padLeft, padTop, padRight, padBottom = self.padding
        left, top, width, height = self.pos
        if not budgetOnly:
            displayX = budgetLeft + ScaleDpiF(padLeft + left)
            displayY = budgetTop + ScaleDpiF(padTop + top)
            displayWidth = budgetWidth - ScaleDpiF(padLeft + padRight)
            displayHeight = ScaleDpiF(height)
            self.displayRect = (displayX,
             displayY,
             displayWidth,
             displayHeight)
        heightUsed = ScaleDpiF(padTop + height + top + padBottom)
        budgetTop += heightUsed
        budgetHeight -= heightUsed
        return (budgetLeft,
         budgetTop,
         budgetWidth,
         budgetHeight)

    @telemetry.ZONE_METHOD
    def UpdateToTopAlignmentNoPush(self, budgetOnly, budgetLeft, budgetTop, budgetWidth, budgetHeight):
        padLeft, padTop, padRight, padBottom = self.padding
        left, top, width, height = self.pos
        if not budgetOnly:
            displayX = budgetLeft + ScaleDpiF(padLeft + left)
            displayY = budgetTop + ScaleDpiF(padTop + top)
            displayWidth = budgetWidth - ScaleDpiF(padLeft + padRight)
            displayHeight = ScaleDpiF(height)
            self.displayRect = (displayX,
             displayY,
             displayWidth,
             displayHeight)
        return (budgetLeft,
         budgetTop,
         budgetWidth,
         budgetHeight)

    @telemetry.ZONE_METHOD
    def UpdateToAllAlignment(self, budgetOnly, budgetLeft, budgetTop, budgetWidth, budgetHeight):
        if not budgetOnly:
            padLeft, padTop, padRight, padBottom = self.padding
            left, top, width, height = self.pos
            displayX = budgetLeft + ScaleDpiF(padLeft + left)
            displayY = budgetTop + ScaleDpiF(padTop + top)
            displayWidth = budgetWidth - ScaleDpiF(padLeft + padRight + left + width)
            displayHeight = budgetHeight - ScaleDpiF(padTop + padBottom + top + height)
            self.displayRect = (displayX,
             displayY,
             displayWidth,
             displayHeight)
        return (budgetLeft,
         budgetTop,
         budgetWidth,
         budgetHeight)

    @telemetry.ZONE_METHOD
    def UpdateAbsoluteAlignment(self, budgetOnly, budgetLeft, budgetTop, budgetWidth, budgetHeight):
        if not budgetOnly:
            left, top, width, height = self.pos
            displayX = ScaleDpiF(left)
            displayY = ScaleDpiF(top)
            displayWidth = ScaleDpiF(width)
            displayHeight = ScaleDpiF(height)
            self.displayRect = (displayX,
             displayY,
             displayWidth,
             displayHeight)
        return (budgetLeft,
         budgetTop,
         budgetWidth,
         budgetHeight)

    @telemetry.ZONE_METHOD
    def UpdateTopLeftAlignment(self, budgetOnly, *budget):
        if not budgetOnly:
            padLeft, padTop, padRight, padBottom = self.padding
            left, top, width, height = self.pos
            displayX = ScaleDpiF(left + padLeft)
            displayY = ScaleDpiF(top + padTop)
            displayWidth = ScaleDpiF(width - padLeft - padRight)
            displayHeight = ScaleDpiF(height - padTop - padBottom)
            self.displayRect = (displayX,
             displayY,
             displayWidth,
             displayHeight)
        return budget

    @telemetry.ZONE_METHOD
    def UpdateTopRightAlignment(self, budgetOnly, *budget):
        if not budgetOnly:
            padLeft, padTop, padRight, padBottom = self.padding
            left, top, width, height = self.pos
            parent = self.parent
            budgetWidth, budgetHeight = parent.displayWidth, parent.displayHeight
            displayX = budgetWidth + ScaleDpiF(padLeft - width - left)
            displayY = ScaleDpiF(top + padTop)
            displayWidth = ScaleDpiF(width - padLeft - padRight)
            displayHeight = ScaleDpiF(height - padTop - padBottom)
            self.displayRect = (displayX,
             displayY,
             displayWidth,
             displayHeight)
        return budget

    @telemetry.ZONE_METHOD
    def UpdateBottomRightAlignment(self, budgetOnly, *budget):
        if not budgetOnly:
            padLeft, padTop, padRight, padBottom = self.padding
            left, top, width, height = self.pos
            parent = self.parent
            budgetWidth, budgetHeight = parent.displayWidth, parent.displayHeight
            displayX = budgetWidth + ScaleDpiF(padLeft - width - left)
            displayY = budgetHeight + ScaleDpiF(padTop - height - top)
            displayWidth = ScaleDpiF(width - padLeft - padRight)
            displayHeight = ScaleDpiF(height - padTop - padBottom)
            self.displayRect = (displayX,
             displayY,
             displayWidth,
             displayHeight)
        return budget

    @telemetry.ZONE_METHOD
    def UpdateBottomLeftAlignment(self, budgetOnly, *budget):
        if not budgetOnly:
            padLeft, padTop, padRight, padBottom = self.padding
            left, top, width, height = self.pos
            parent = self.parent
            budgetWidth, budgetHeight = parent.displayWidth, parent.displayHeight
            displayX = ScaleDpiF(left + padLeft)
            displayY = budgetHeight + ScaleDpiF(padTop - height - top)
            displayWidth = ScaleDpiF(width - padLeft - padRight)
            displayHeight = ScaleDpiF(height - padTop - padBottom)
            self.displayRect = (displayX,
             displayY,
             displayWidth,
             displayHeight)
        return budget

    @telemetry.ZONE_METHOD
    def UpdateCenterAlignment(self, budgetOnly, *budget):
        if not budgetOnly:
            padLeft, padTop, padRight, padBottom = self.padding
            left, top, width, height = self.pos
            parent = self.parent
            budgetWidth, budgetHeight = parent.displayWidth, parent.displayHeight
            displayX = (budgetWidth - ScaleDpiF(width)) / 2 + ScaleDpiF(left + padLeft)
            displayY = (budgetHeight - ScaleDpiF(height)) / 2 + ScaleDpiF(top + padTop)
            displayWidth = ScaleDpiF(width - padLeft - padRight)
            displayHeight = ScaleDpiF(height - padTop - padBottom)
            self.displayRect = (displayX,
             displayY,
             displayWidth,
             displayHeight)
        return budget

    @telemetry.ZONE_METHOD
    def UpdateCenterPreserveAspectAlignment(self, budgetOnly, *budget):
        if not budgetOnly:
            padLeft, padTop, padRight, padBottom = self.padding
            left, top, _, _ = self.pos
            parent = self.parent
            budgetWidth, budgetHeight = parent.displayWidth, parent.displayHeight
            displayWidth = budgetWidth - ScaleDpiF(padLeft + padRight)
            displayHeight = budgetHeight - ScaleDpiF(padTop + padBottom)
            if displayWidth / self._aspectRatio > displayHeight:
                displayWidth = displayHeight * self._aspectRatio
            else:
                displayHeight = displayWidth / self._aspectRatio
            displayX = (budgetWidth - displayWidth + ScaleDpiF(padLeft - padRight)) / 2 + ScaleDpiF(left)
            displayY = (budgetHeight - displayHeight + ScaleDpiF(padTop - padBottom)) / 2 + ScaleDpiF(top)
            self.displayRect = (displayX,
             displayY,
             displayWidth,
             displayHeight)
        return budget

    @telemetry.ZONE_METHOD
    def UpdateCenterBottomAlignment(self, budgetOnly, *budget):
        if not budgetOnly:
            padLeft, padTop, padRight, padBottom = self.padding
            left, top, width, height = self.pos
            parent = self.parent
            budgetWidth, budgetHeight = parent.displayWidth, parent.displayHeight
            displayX = (budgetWidth - ScaleDpiF(width)) / 2 + ScaleDpiF(left + padLeft)
            displayY = budgetHeight - ScaleDpiF(height + top - padTop)
            displayWidth = ScaleDpiF(width - padLeft - padRight)
            displayHeight = ScaleDpiF(height - padTop - padBottom)
            self.displayRect = (displayX,
             displayY,
             displayWidth,
             displayHeight)
        return budget

    @telemetry.ZONE_METHOD
    def UpdateCenterTopAlignment(self, budgetOnly, *budget):
        if not budgetOnly:
            padLeft, padTop, padRight, padBottom = self.padding
            left, top, width, height = self.pos
            parent = self.parent
            budgetWidth, budgetHeight = parent.displayWidth, parent.displayHeight
            displayX = (budgetWidth - ScaleDpiF(width)) / 2 + ScaleDpiF(left + padLeft)
            displayY = ScaleDpiF(top + padTop)
            displayWidth = ScaleDpiF(width - padLeft - padRight)
            displayHeight = ScaleDpiF(height - padTop - padBottom)
            self.displayRect = (displayX,
             displayY,
             displayWidth,
             displayHeight)
        return budget

    @telemetry.ZONE_METHOD
    def UpdateCenterLeftAlignment(self, budgetOnly, *budget):
        if not budgetOnly:
            padLeft, padTop, padRight, padBottom = self.padding
            left, top, width, height = self.pos
            parent = self.parent
            budgetWidth, budgetHeight = parent.displayWidth, parent.displayHeight
            displayX = ScaleDpiF(left + padLeft)
            displayY = (budgetHeight - ScaleDpiF(height)) / 2 + ScaleDpiF(top + padTop)
            displayWidth = ScaleDpiF(width - padLeft - padRight)
            displayHeight = ScaleDpiF(height - padTop - padBottom)
            self.displayRect = (displayX,
             displayY,
             displayWidth,
             displayHeight)
        return budget

    @telemetry.ZONE_METHOD
    def UpdateCenterRightAlignment(self, budgetOnly, *budget):
        if not budgetOnly:
            padLeft, padTop, padRight, padBottom = self.padding
            left, top, width, height = self.pos
            parent = self.parent
            budgetWidth, budgetHeight = parent.displayWidth, parent.displayHeight
            displayX = budgetWidth - ScaleDpiF(width + left - padLeft)
            displayY = (budgetHeight - ScaleDpiF(height)) / 2 + ScaleDpiF(top + padTop)
            displayWidth = ScaleDpiF(width - padLeft - padRight)
            displayHeight = ScaleDpiF(height - padTop - padBottom)
            self.displayRect = (displayX,
             displayY,
             displayWidth,
             displayHeight)
        return budget

    @telemetry.ZONE_METHOD
    def UpdateNoAlignment(self, budgetOnly, *budget):
        left, top, width, height = self.pos
        displayWidth = ScaleDpi(width)
        displayHeight = ScaleDpi(height)
        self.displayWidth = displayWidth
        self.displayHeight = displayHeight
        return budget

    @telemetry.ZONE_METHOD
    def UpdateToLeftProportionalAlignment(self, budgetOnly, budgetLeft, budgetTop, budgetWidth, budgetHeight):
        padLeft, padTop, padRight, padBottom = self.padding
        left, top, width, height = self.pos
        if not budgetOnly:
            width = int(float(self.parent.displayWidth) * width)
            width = self._CheckClampDisplayWidth(width)
            left = int(float(self.parent.displayWidth) * left)
            displayX = budgetLeft + ScaleDpiF(padLeft) + left
            displayY = budgetTop + ScaleDpiF(padTop + top)
            displayHeight = budgetHeight - ScaleDpiF(padTop + padBottom)
            displayWidth = width - ScaleDpiF(padLeft + padRight)
            self.displayRect = (displayX,
             displayY,
             displayWidth,
             displayHeight)
        widthUsed = left + ScaleDpiF(padLeft + padRight) + self.displayWidth
        budgetLeft += widthUsed
        budgetWidth -= widthUsed
        return (budgetLeft,
         budgetTop,
         budgetWidth,
         budgetHeight)

    def _CheckClampValue(self, value, min_val, max_val):
        if min_val is not None:
            value = max(min_val, value)
        if max_val is not None:
            value = min(max_val, value)
        return value

    def _CheckClampDisplayWidth(self, width):
        if self.minWidth == self.maxWidth == None:
            return width
        min_val = ScaleDpiF(self.minWidth) if self.minWidth else None
        max_val = ScaleDpiF(self.maxWidth) if self.maxWidth else None
        return self._CheckClampValue(width, min_val, max_val)

    def _CheckClampDisplayHeight(self, height):
        if self.minHeight == self.maxHeight == None:
            return height
        min_val = ScaleDpiF(self.minHeight) if self.minHeight else None
        max_val = ScaleDpiF(self.maxHeight) if self.maxHeight else None
        return self._CheckClampValue(height, min_val, max_val)

    def _CheckClampWidth(self, width):
        if self.minWidth == self.maxWidth == None:
            return width
        return self._CheckClampValue(width, self.minWidth, self.maxWidth)

    def _CheckClampHeight(self, height):
        if self.minHeight == self.maxHeight == None:
            return height
        return self._CheckClampValue(height, self.minHeight, self.maxHeight)

    @telemetry.ZONE_METHOD
    def UpdateToRightProportionalAlignment(self, budgetOnly, budgetLeft, budgetTop, budgetWidth, budgetHeight):
        padLeft, padTop, padRight, padBottom = self.padding
        left, top, width, height = self.pos
        if not budgetOnly:
            width = int(float(self.parent.displayWidth) * width)
            width = self._CheckClampDisplayWidth(width)
            left = int(float(self.parent.displayWidth) * left)
            displayX = budgetLeft + budgetWidth - width - ScaleDpiF(padRight - padLeft) - left
            displayY = budgetTop + ScaleDpiF(padTop + top)
            displayHeight = budgetHeight - ScaleDpiF(padTop + padBottom)
            displayWidth = width - ScaleDpiF(padLeft + padRight)
            self.displayRect = (displayX,
             displayY,
             displayWidth,
             displayHeight)
        widthUsed = left + ScaleDpiF(padLeft + padRight) + self.displayWidth
        budgetWidth -= widthUsed
        return (budgetLeft,
         budgetTop,
         budgetWidth,
         budgetHeight)

    @telemetry.ZONE_METHOD
    def UpdateToTopProportionalAlignment(self, budgetOnly, budgetLeft, budgetTop, budgetWidth, budgetHeight):
        padLeft, padTop, padRight, padBottom = self.padding
        left, top, width, height = self.pos
        if not budgetOnly:
            height = int(float(self.parent.displayHeight) * height)
            height = self._CheckClampDisplayHeight(height)
            top = int(float(self.parent.displayHeight) * top)
            displayX = budgetLeft + ScaleDpiF(padLeft + left)
            displayY = budgetTop + ScaleDpiF(padTop) + top
            displayWidth = budgetWidth - ScaleDpiF(padLeft + padRight)
            displayHeight = height - ScaleDpiF(padTop + padBottom)
            self.displayRect = (displayX,
             displayY,
             displayWidth,
             displayHeight)
        heightUsed = top + ScaleDpiF(padTop + padBottom) + self.displayHeight
        budgetTop += heightUsed
        budgetHeight -= heightUsed
        return (budgetLeft,
         budgetTop,
         budgetWidth,
         budgetHeight)

    @telemetry.ZONE_METHOD
    def UpdateToBottomProportionalAlignment(self, budgetOnly, budgetLeft, budgetTop, budgetWidth, budgetHeight):
        padLeft, padTop, padRight, padBottom = self.padding
        left, top, width, height = self.pos
        if not budgetOnly:
            height = int(float(self.parent.displayHeight) * height)
            height = self._CheckClampDisplayHeight(height)
            top = int(float(self.parent.displayHeight) * top)
            displayX = budgetLeft + ScaleDpiF(padLeft + left)
            displayY = budgetTop + budgetHeight - height - ScaleDpiF(padBottom) + top
            displayWidth = budgetWidth - ScaleDpiF(padLeft + padRight)
            displayHeight = height - ScaleDpiF(padTop + padBottom)
            self.displayRect = (displayX,
             displayY,
             displayWidth,
             displayHeight)
        heightUsed = top + ScaleDpiF(padTop + padBottom) + self.displayHeight
        budgetHeight -= heightUsed
        return (budgetLeft,
         budgetTop,
         budgetWidth,
         budgetHeight)

    @telemetry.ZONE_METHOD
    def UpdateTopLeftProportionalAlignment(self, budgetOnly, *budget):
        padLeft, padTop, padRight, padBottom = self.padding
        left, top, width, height = self.pos
        if not budgetOnly:
            parent = self.parent
            budgetWidth, budgetHeight = parent.displayWidth, parent.displayHeight
            if self._width < 1.0:
                displayWidth = width * budgetWidth - ScaleDpiF(padLeft + padRight)
                displayWidth = self._CheckClampDisplayWidth(displayWidth)
            else:
                displayWidth = ScaleDpiF(width - padLeft - padRight)
            if self._height < 1.0:
                displayHeight = height * budgetHeight - ScaleDpiF(padTop + padBottom)
                displayHeight = self._CheckClampDisplayHeight(displayHeight)
            else:
                displayHeight = ScaleDpiF(height - padTop - padBottom)
            if self._left <= 1.0:
                displayX = (budgetWidth - displayWidth) * (left + padLeft)
            else:
                displayX = ScaleDpiF(left + padLeft)
            if self._top <= 1.0:
                displayY = (budgetHeight - displayHeight) * (top + padTop)
            else:
                displayY = ScaleDpiF(top + padTop)
            self.displayRect = (displayX,
             displayY,
             displayWidth,
             displayHeight)
        return budget

    @telemetry.ZONE_METHOD
    def UpdateHorizontalCenteredAlignment(self, budgetOnly, budgetLeft, budgetTop, budgetWidth, budgetHeight):
        _, padTop, _, padBottom = self.padding
        left, top, width, height = self.pos
        if not budgetOnly:
            displayY = budgetTop + ScaleDpiF(padTop + top)
            displayHeight = budgetHeight - ScaleDpiF(padTop + padBottom)
            if width < 1:
                displayWidth = self._CheckClampDisplayWidth(width * budgetWidth)
            else:
                displayWidth = ScaleDpiF(width)
            displayX = budgetLeft + (budgetWidth - displayWidth) * 0.5 * (1.0 + left)
            self.displayRect = (displayX,
             displayY,
             displayWidth,
             displayHeight)
        return (budgetLeft,
         budgetTop,
         budgetWidth,
         budgetHeight)

    @telemetry.ZONE_METHOD
    def UpdateVerticalCenteredAlignment(self, budgetOnly, budgetLeft, budgetTop, budgetWidth, budgetHeight):
        padLeft, _, padRight, _ = self.padding
        left, top, width, height = self.pos
        if not budgetOnly:
            displayX = budgetLeft + ScaleDpiF(padLeft + left)
            displayWidth = budgetWidth - ScaleDpiF(padLeft + padRight)
            if height < 1:
                displayHeight = self._CheckClampDisplayHeight(ScaleDpiF(height * budgetHeight))
            else:
                displayHeight = ScaleDpiF(height)
            displayY = budgetTop + (budgetHeight - displayHeight) * 0.5 * (1.0 + top)
            self.displayRect = (displayX,
             displayY,
             displayWidth,
             displayHeight)
        return (budgetLeft,
         budgetTop,
         budgetWidth,
         budgetHeight)

    def UpdateTotopStickyAlignment(self, budgetOnly, budgetLeft, budgetTop, budgetWidth, budgetHeight):
        padLeft, padTop, padRight, padBottom = self.padding
        left, top, width, height = self.pos
        if not budgetOnly:
            displayX = budgetLeft + ScaleDpiF(padLeft + left)
            clipper = self.GetClipper()
            displayY = budgetTop + ScaleDpiF(padTop + top)
            parent_absolute_top = ScaleDpiF(self.parent.GetAbsoluteTop())
            clipper_absolute_top = ScaleDpiF(clipper.GetAbsoluteTop())
            if clipper and clipper_absolute_top > parent_absolute_top + displayY:
                displayY = clipper_absolute_top - parent_absolute_top
            displayWidth = budgetWidth - ScaleDpiF(padLeft + padRight)
            displayHeight = ScaleDpiF(height)
            self.displayRect = (displayX,
             displayY,
             displayWidth,
             displayHeight)
        heightUsed = ScaleDpiF(padTop + height + top + padBottom)
        budgetTop += heightUsed
        budgetHeight -= heightUsed
        return (budgetLeft,
         budgetTop,
         budgetWidth,
         budgetHeight)

    @telemetry.ZONE_METHOD
    def UpdateAlignmentAsRoot(self, caller = None):
        if self.destroyed or not self.display:
            return
        if self.align == uiconst.NOALIGN:
            self.UpdateAlignment(0, 0, ScaleDpi(self.width), ScaleDpi(self.height))
        else:
            self.UpdateAlignment(0, 0, self.displayWidth, self.displayHeight)

    def UpdateAlignment(self, budgetLeft = 0, budgetTop = 0, budgetWidth = 0, budgetHeight = 0, updateChildrenOnly = False):
        if self.destroyed:
            return (budgetLeft,
             budgetTop,
             budgetWidth,
             budgetHeight,
             False)
        forceUpdate = self._forceUpdateAlignment
        alignmentDirty = self._alignmentDirty
        self._alignmentDirty = False
        self._forceUpdateAlignment = False
        fullUpdate = alignmentDirty or forceUpdate
        sizeChange = False
        preDX, preDY, preDWidth, preDHeight = self.displayRect
        budgetLeft, budgetTop, budgetWidth, budgetHeight = self._alignFunc(self, not fullUpdate, budgetLeft, budgetTop, budgetWidth, budgetHeight)
        if fullUpdate:
            newDX, newDY, newDWidth, newDHeight = self.displayRect
            sizeChange = preDWidth != newDWidth or preDHeight != newDHeight
            posChange = preDX != newDX or preDY != newDY
            if sizeChange or posChange:
                if self._OnResize.im_func != Base._OnResize.im_func:
                    self._OnResize()
            if sizeChange:
                newWidth = ReverseScaleDpi(newDWidth)
                newHeight = ReverseScaleDpi(newDHeight)
                self._OnSizeChange_NoBlock(newWidth, newHeight)
                self._emit_on_size_changed(newWidth, newHeight)
        return (budgetLeft,
         budgetTop,
         budgetWidth,
         budgetHeight,
         sizeChange)

    def ScaleDpi(self, value):
        return ScaleDpi(value)

    def ReverseScaleDpi(self, value):
        return ReverseScaleDpi(value)

    def Toggle(self, *args):
        if self.IsHidden():
            self.Show()
        else:
            self.Hide()

    def Hide(self, *args):
        self.display = False

    def Show(self, *args):
        self.display = True

    def IsHidden(self):
        return not self.display

    def FindParentByName(self, parentName):
        parent = self.GetParent()
        while parent:
            if parent.name == parentName:
                return parent
            parent = parent.GetParent()

    @property
    def cursor(self):
        return self._cursor

    @cursor.setter
    def cursor(self, value):
        self._cursor = value
        uicore.CheckCursor()

    def _OnClose(self, *args, **kw):
        pass

    def _OnResize(self, *args):
        pass

    def _OnSizeChange_NoBlock(self, width, height):
        pass

    def OnMouseUp(self, *args):
        pass

    def OnMouseDown(self, *args):
        pass

    def OnMouseEnter(self, *args):
        pass

    def OnMouseExit(self, *args):
        pass

    def OnMouseHover(self, *args):
        pass

    def OnClick(self, *args):
        pass

    def OnMouseMove(self, *args):
        pass

    def UpdateUIScaling(self, value, oldValue):
        pass

    def OnColorThemeChanged(self):
        pass

    def OnWindowAboveSetActive(self):
        pass

    def OnWindowAboveSetInactive(self):
        pass

    def OnGlobalFontSizeChanged(self):
        pass

    def OnGlobalFontShadowChanged(self):
        pass

    def DelegateEvents(self, delegateTo):
        self._delegatingEvents = True
        for eventName in DELEGATE_EVENTNAMES:
            toHandler = getattr(delegateTo, eventName, None)
            if toHandler:
                setattr(self, eventName, toHandler)

    def DelegateEventsNotImplemented(self, delegateTo):
        self._delegatingEvents = True
        for eventName in DELEGATE_EVENTNAMES:
            haveLocal = self.HasEventHandler(eventName)
            if not haveLocal:
                toHandler = getattr(delegateTo, eventName, None)
                if toHandler:
                    setattr(self, eventName, toHandler)

    @property
    def analyticContext(self):
        contextParts = []
        parent = self.parent
        while parent is not None:
            context = getattr(parent, 'analyticID', None)
            if context:
                contextParts.append(context)
            parent = parent.parent

        return '.'.join(reversed(contextParts))

    @property
    def __bluetype__(self):
        if self.__renderObject__:
            return self.__renderObject__().__bluetype__

    @property
    def __typename__(self):
        if self.__renderObject__:
            return self.__renderObject__().__typename__


ALIGN_AND_CONSUME_FUNCTIONS = {Align.TOPLEFT: (Base.UpdateTopLeftAlignment, uiconst.TOPLEFT in PUSHALIGNMENTS, uiconst.TOPLEFT in AFFECTEDBYPUSHALIGNMENTS),
 Align.TOALL: (Base.UpdateToAllAlignment, uiconst.TOALL in PUSHALIGNMENTS, uiconst.TOALL in AFFECTEDBYPUSHALIGNMENTS),
 Align.NOALIGN: (Base.UpdateNoAlignment, uiconst.NOALIGN in PUSHALIGNMENTS, uiconst.NOALIGN in AFFECTEDBYPUSHALIGNMENTS),
 Align.TOLEFT: (Base.UpdateToLeftAlignment, uiconst.TOLEFT in PUSHALIGNMENTS, uiconst.TOLEFT in AFFECTEDBYPUSHALIGNMENTS),
 Align.TORIGHT: (Base.UpdateToRightAlignment, uiconst.TORIGHT in PUSHALIGNMENTS, uiconst.TORIGHT in AFFECTEDBYPUSHALIGNMENTS),
 Align.TOTOP: (Base.UpdateToTopAlignment, uiconst.TOTOP in PUSHALIGNMENTS, uiconst.TOTOP in AFFECTEDBYPUSHALIGNMENTS),
 Align.TOBOTTOM: (Base.UpdateToBottomAlignment, uiconst.TOBOTTOM in PUSHALIGNMENTS, uiconst.TOBOTTOM in AFFECTEDBYPUSHALIGNMENTS),
 Align.TOLEFT_NOPUSH: (Base.UpdateToLeftAlignmentNoPush, uiconst.TOLEFT_NOPUSH in PUSHALIGNMENTS, uiconst.TOLEFT_NOPUSH in AFFECTEDBYPUSHALIGNMENTS),
 Align.TORIGHT_NOPUSH: (Base.UpdateToRightAlignmentNoPush, uiconst.TORIGHT_NOPUSH in PUSHALIGNMENTS, uiconst.TORIGHT_NOPUSH in AFFECTEDBYPUSHALIGNMENTS),
 Align.TOTOP_NOPUSH: (Base.UpdateToTopAlignmentNoPush, uiconst.TOTOP_NOPUSH in PUSHALIGNMENTS, uiconst.TOTOP_NOPUSH in AFFECTEDBYPUSHALIGNMENTS),
 Align.TOBOTTOM_NOPUSH: (Base.UpdateToBottomAlignmentNoPush, uiconst.TOBOTTOM_NOPUSH in PUSHALIGNMENTS, uiconst.TOBOTTOM_NOPUSH in AFFECTEDBYPUSHALIGNMENTS),
 Align.TOLEFT_PROP: (Base.UpdateToLeftProportionalAlignment, uiconst.TOLEFT_PROP in PUSHALIGNMENTS, uiconst.TOLEFT_PROP in AFFECTEDBYPUSHALIGNMENTS),
 Align.TORIGHT_PROP: (Base.UpdateToRightProportionalAlignment, uiconst.TORIGHT_PROP in PUSHALIGNMENTS, uiconst.TORIGHT_PROP in AFFECTEDBYPUSHALIGNMENTS),
 Align.TOTOP_PROP: (Base.UpdateToTopProportionalAlignment, uiconst.TOTOP_PROP in PUSHALIGNMENTS, uiconst.TOTOP_PROP in AFFECTEDBYPUSHALIGNMENTS),
 Align.TOBOTTOM_PROP: (Base.UpdateToBottomProportionalAlignment, uiconst.TOBOTTOM_PROP in PUSHALIGNMENTS, uiconst.TOBOTTOM_PROP in AFFECTEDBYPUSHALIGNMENTS),
 Align.ABSOLUTE: (Base.UpdateAbsoluteAlignment, uiconst.ABSOLUTE in PUSHALIGNMENTS, uiconst.ABSOLUTE in AFFECTEDBYPUSHALIGNMENTS),
 Align.TOPLEFT_PROP: (Base.UpdateTopLeftProportionalAlignment, uiconst.TOPLEFT_PROP in PUSHALIGNMENTS, uiconst.TOPLEFT_PROP in AFFECTEDBYPUSHALIGNMENTS),
 Align.TOPRIGHT: (Base.UpdateTopRightAlignment, uiconst.TOPRIGHT in PUSHALIGNMENTS, uiconst.TOPRIGHT in AFFECTEDBYPUSHALIGNMENTS),
 Align.BOTTOMRIGHT: (Base.UpdateBottomRightAlignment, uiconst.BOTTOMRIGHT in PUSHALIGNMENTS, uiconst.BOTTOMRIGHT in AFFECTEDBYPUSHALIGNMENTS),
 Align.BOTTOMLEFT: (Base.UpdateBottomLeftAlignment, uiconst.BOTTOMLEFT in PUSHALIGNMENTS, uiconst.BOTTOMLEFT in AFFECTEDBYPUSHALIGNMENTS),
 Align.CENTER: (Base.UpdateCenterAlignment, uiconst.CENTER in PUSHALIGNMENTS, uiconst.CENTER in AFFECTEDBYPUSHALIGNMENTS),
 Align.CENTERBOTTOM: (Base.UpdateCenterBottomAlignment, uiconst.CENTERBOTTOM in PUSHALIGNMENTS, uiconst.CENTERBOTTOM in AFFECTEDBYPUSHALIGNMENTS),
 Align.CENTERTOP: (Base.UpdateCenterTopAlignment, uiconst.CENTERTOP in PUSHALIGNMENTS, uiconst.CENTERTOP in AFFECTEDBYPUSHALIGNMENTS),
 Align.CENTERLEFT: (Base.UpdateCenterLeftAlignment, uiconst.CENTERLEFT in PUSHALIGNMENTS, uiconst.CENTERLEFT in AFFECTEDBYPUSHALIGNMENTS),
 Align.CENTERRIGHT: (Base.UpdateCenterRightAlignment, uiconst.CENTERRIGHT in PUSHALIGNMENTS, uiconst.CENTERRIGHT in AFFECTEDBYPUSHALIGNMENTS),
 Align.CENTER_PRESERVE_ASPECT: (Base.UpdateCenterPreserveAspectAlignment, uiconst.CENTER_PRESERVE_ASPECT in PUSHALIGNMENTS, uiconst.CENTER_PRESERVE_ASPECT in AFFECTEDBYPUSHALIGNMENTS),
 Align.VERTICALLY_CENTERED: (Base.UpdateVerticalCenteredAlignment, uiconst.VERTICALLY_CENTERED in PUSHALIGNMENTS, uiconst.VERTICALLY_CENTERED in AFFECTEDBYPUSHALIGNMENTS),
 Align.HORIZONTALLY_CENTERED: (Base.UpdateHorizontalCenteredAlignment, uiconst.HORIZONTALLY_CENTERED in PUSHALIGNMENTS, uiconst.HORIZONTALLY_CENTERED in AFFECTEDBYPUSHALIGNMENTS),
 Align.TOTOP_STICKY: (Base.UpdateTotopStickyAlignment, Align.TOTOP_STICKY in PUSHALIGNMENTS, Align.TOTOP_STICKY in AFFECTEDBYPUSHALIGNMENTS)}
