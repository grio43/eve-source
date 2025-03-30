#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\primitives\container.py
import weakref
import trinity
from carbonui import uiconst
from carbonui.primitives.backgroundList import BackgroundList
from carbonui.primitives.base import Base
from carbonui.primitives.childrenlist import PyChildrenList
from carbonui.primitives.fill import Fill
from carbonui.primitives.sprite import Sprite
from carbonui.uiconst import PickState
from carbonui.uicore import uicore

class Container(Base):
    __guid__ = 'uiprimitives.Container'
    __renderObject__ = trinity.Tr2Sprite2dContainer
    isDropLocation = True
    default_clipChildren = False
    default_pickRadius = 0
    default_opacity = 1.0
    default_align = uiconst.TOALL
    default_state = uiconst.UI_PICKCHILDREN
    default_pickState = PickState.CHILDREN
    default_depthMin = 0.0
    default_depthMax = 0.0
    default_bgColor = None
    default_bgTexturePath = None
    default_bgRotation = 0.0
    default_bgBlendMode = trinity.TR2_SBM_BLEND
    default_bgSpriteEffect = Sprite.default_spriteEffect
    default_bgOutputMode = Sprite.default_outputMode
    _cacheContents = False
    _containerClosing = False
    _childrenAlignmentDirty = False
    _backgroundlist = None
    _opacity = None

    def ApplyAttributes(self, attributes):
        self.children = self.GetChildrenList()
        Base.ApplyAttributes(self, attributes)
        self.depthMin = attributes.get('depthMin', self.default_depthMin)
        self.depthMax = attributes.get('depthMax', self.default_depthMax)
        self.pickRadius = attributes.get('pickRadius', self.default_pickRadius)
        self.opacity = attributes.get('opacity', self.default_opacity)
        self.clipChildren = attributes.get('clipChildren', self.default_clipChildren)
        self._bgColor = attributes.get('bgColor', self.default_bgColor)
        self._bgTexturePath = attributes.get('bgTexturePath', self.default_bgTexturePath)
        self._bgRotation = attributes.get('bgRotation', self.default_bgRotation)
        self._bgBlendMode = attributes.get('bgBlendMode', self.default_bgBlendMode)
        self._bgSpriteEffect = attributes.get('bgSpriteEffect', self.default_bgSpriteEffect)
        self._bgSpriteOutputMode = attributes.get('bgOutputMode', self.default_bgOutputMode)
        self._bgSprite = None
        self.bgFill = None
        self._SetupBackground()

    def _SetupBackground(self):
        if self._bgSprite is not None:
            self._bgSprite.Close()
        if self.bgFill is not None:
            self.bgFill.Close()
        if self._bgTexturePath:
            self._bgSprite = Sprite(bgParent=self, texturePath=self._bgTexturePath, color=self._bgColor or (1.0, 1.0, 1.0, 1.0), rotation=self._bgRotation, blendMode=self._bgBlendMode, outputMode=self._bgSpriteOutputMode, spriteEffect=self._bgSpriteEffect)
        elif self._bgColor:
            self.bgFill = Fill(bgParent=self, color=self._bgColor, rotation=self._bgRotation, blendMode=self._bgBlendMode)

    def Close(self):
        if getattr(self, 'destroyed', False):
            return
        self._containerClosing = True
        for child in self.children:
            child.Close()

        self.children = []
        if self._backgroundlist:
            for child in self.background[:]:
                child.Close()

        Base.Close(self)

    def UpdateAlignment(self, budgetLeft = 0, budgetTop = 0, budgetWidth = 0, budgetHeight = 0, updateChildrenOnly = False):
        forceUpdate = self._forceUpdateAlignment
        if updateChildrenOnly:
            childrenDirty = True
            sizeChange = False
        else:
            budgetLeft, budgetTop, budgetWidth, budgetHeight, sizeChange = Base.UpdateAlignment(self, budgetLeft, budgetTop, budgetWidth, budgetHeight)
            childrenDirty = self._childrenAlignmentDirty
        self._childrenAlignmentDirty = False
        if childrenDirty or forceUpdate or sizeChange:
            self._update_children_alignment(sizeChange, forceUpdate)
        return (budgetLeft,
         budgetTop,
         budgetWidth,
         budgetHeight,
         sizeChange)

    def _update_children_alignment(self, sizeChange, forceUpdate):
        flagNextChild = False
        cbLeft, cbTop, cbWidth, cbHeight = (0,
         0,
         self.displayWidth,
         self.displayHeight)
        for each in self.children:
            if each.destroyed:
                continue
            if each.display and forceUpdate:
                each._forceUpdateAlignment = True
            isPushAligned = each.isPushAligned
            if isPushAligned and each._forceUpdateAlignment:
                flagNextChild = True
            if each.display:
                if not each._alignmentDirty and (sizeChange or flagNextChild and each.isAffectedByPushAlignment):
                    each._alignmentDirty = True
                if getattr(each, '_childrenAlignmentDirty', False) or each._alignmentDirty or each._forceUpdateAlignment or isPushAligned:
                    preDisplayX = each.displayX
                    preDisplayY = each.displayY
                    cbLeft, cbTop, cbWidth, cbHeight, changedSize = each.UpdateAlignment(cbLeft, cbTop, cbWidth, cbHeight)
                    if not flagNextChild and isPushAligned:
                        flagNextChild = changedSize or preDisplayX != each.displayX or preDisplayY != each.displayY

    def GetChildrenList(self):
        return PyChildrenList(self)

    def GetOpacity(self):
        return self.opacity

    def SetOpacity(self, opacity):
        self.opacity = opacity

    def IsVisibleAndClickable(self):
        if not hasattr(self, 'opacity'):
            return False
        if self.opacity <= 0.5:
            return False
        return super(Container, self).IsVisibleAndClickable()

    def AutoFitToContent(self):
        if self.isAffectedByPushAlignment:
            raise RuntimeError('AutoFitToContent: invalid alignment')
        minWidth = 0
        minHeight = 0
        totalAutoVertical = 0
        totalAutoHorizontal = 0
        for each in self.children:
            if not each.isAffectedByPushAlignment:
                minWidth = max(minWidth, each.left + each.width)
                minHeight = max(minHeight, each.top + each.height)
            elif each.align in (uiconst.TOTOP, uiconst.TOBOTTOM):
                totalAutoVertical += each.padTop + each.height + each.padBottom
            elif each.align in (uiconst.TOLEFT, uiconst.TORIGHT):
                totalAutoHorizontal += each.padLeft + each.width + each.padRight

        self.width = max(minWidth, totalAutoHorizontal)
        self.height = max(minHeight, totalAutoVertical)

    def Flush(self):
        for child in self.children[:]:
            child.Close()

    def FindChild(self, *names, **kwds):
        if self.destroyed:
            return
        ret = None
        searchFrom = self
        for name in names:
            ret = searchFrom._FindChildByName(name)
            if hasattr(ret, 'children'):
                searchFrom = ret

        if not ret or ret.name != names[-1]:
            if kwds.get('raiseError', False):
                raise RuntimeError('ChildNotFound', (self.name, names))
            return
        return ret

    def _FindChildByName(self, name, lvl = 0):
        for child in self.children:
            if child.name == name:
                return child

        for child in self.children:
            if hasattr(child, 'children'):
                ret = child._FindChildByName(name, lvl + 1)
                if ret is not None:
                    return ret

    def iter_children(self):
        for child in self.children:
            yield child

    def iter_descendants_breadth_first(self):
        remaining = list((weakref.ref(child) for child in self.children))
        while remaining:
            element_ref = remaining.pop(0)
            element = element_ref()
            if element is None:
                continue
            yield element
            if hasattr(element, 'children'):
                remaining.extend((weakref.ref(child) for child in element.children))

    def iter_descendants_depth_first(self):
        remaining = list((weakref.ref(child) for child in reversed(self.children)))
        while remaining:
            element_ref = remaining.pop()
            element = element_ref()
            if element is None:
                continue
            yield element
            remaining.extend((weakref.ref(child) for child in reversed(getattr(element, 'children', []))))

    def Find(self, triTypeName):
        return list(filter(lambda element: getattr(element, '__bluetype__', None) == triTypeName, self.iter_descendants_depth_first()))

    def FindByInstance(self, classTypeOrTypeTuple):
        return set(filter(lambda element: isinstance(element, classTypeOrTypeTuple), self.iter_descendants_depth_first()))

    def GetChild(self, *names):
        return self.FindChild(*names, **{'raiseError': True})

    def IsChildClipped(self, child):
        if not self.clipChildren:
            return False
        cdx = child.displayX
        cdw = child.displayWidth
        sdx = self.displayX
        sdw = self.displayWidth
        if cdx >= sdx and cdx <= sdx + sdw or cdx + cdw >= sdx and cdx + cdw <= sdx + sdw:
            cdy = child.displayY
            cdh = child.displayHeight
            sdy = self.displayY
            sdh = self.displayHeight
            if cdy >= sdy and cdy <= sdy + sdh or cdy + cdh >= sdy and cdy + cdh <= sdy + sdh:
                return False
        return True

    @property
    def background(self):
        if not self._backgroundlist:
            self._backgroundlist = BackgroundList(self)
        return self._backgroundlist

    @property
    def depthMin(self):
        return self._depthMin

    @depthMin.setter
    def depthMin(self, value):
        self._depthMin = value
        ro = self.renderObject
        if ro and hasattr(ro, 'depthMin'):
            ro.depthMin = value or 0.0

    @property
    def depthMax(self):
        return self._depthMax

    @depthMax.setter
    def depthMax(self, value):
        self._depthMax = value
        ro = self.renderObject
        if ro and hasattr(ro, 'depthMax'):
            ro.depthMax = value or 0.0

    @property
    def clipChildren(self):
        return self._clipChildren

    @clipChildren.setter
    def clipChildren(self, value):
        self._clipChildren = value
        ro = self.renderObject
        if ro and hasattr(ro, 'clip'):
            ro.clip = value

    @property
    def opacity(self):
        return self._opacity

    @opacity.setter
    def opacity(self, value):
        self._SetOpacity(value)

    def _SetOpacity(self, value):
        if value != self._opacity:
            self._opacity = value
            ro = self.renderObject
            if ro and hasattr(ro, 'opacity'):
                ro.opacity = value or 0.0
            for child in self.children:
                childRenderObject = child.renderObject
                if childRenderObject:
                    childRenderObject.isDirty = True

    @property
    def pickRadius(self):
        return self._pickRadius

    @pickRadius.setter
    def pickRadius(self, value):
        self._pickRadius = value
        ro = self.renderObject
        if ro and hasattr(ro, 'pickRadius'):
            if value < 0:
                ro.pickRadius = value
            else:
                ro.pickRadius = uicore.ScaleDpi(value) or 0.0

    @Base.displayWidth.setter
    def displayWidth(self, value):
        Base.displayWidth.fset(self, value)
        if self._backgroundlist and len(self.background):
            self.UpdateBackgrounds()

    @Base.displayHeight.setter
    def displayHeight(self, value):
        Base.displayHeight.fset(self, value)
        if self._backgroundlist and len(self.background):
            self.UpdateBackgrounds()

    @Base.displayRect.setter
    def displayRect(self, value):
        Base.displayRect.fset(self, value)
        if self._backgroundlist and len(self.background):
            self.UpdateBackgrounds()

    def UpdateBackgrounds(self):
        for each in self.background:
            pl, pt, pr, pb = each.padding
            each.displayRect = (uicore.ScaleDpi(pl),
             uicore.ScaleDpi(pt),
             self._displayWidth - uicore.ScaleDpi(pl + pr),
             self._displayHeight - uicore.ScaleDpi(pt + pb))

    @property
    def cacheContents(self):
        return self._cacheContents

    @cacheContents.setter
    def cacheContents(self, value):
        self._cacheContents = value
        if self.renderObject:
            self.renderObject.cacheContents = value

    def _AppendChildRO(self, child):
        try:
            self.renderObject.children.append(child.renderObject)
        except (AttributeError, TypeError):
            pass

    def _InsertChildRO(self, idx, child):
        try:
            self.renderObject.children.insert(idx, child.renderObject)
        except IndexError:
            self.renderObject.children.append(child.renderObject)
        except (AttributeError, TypeError):
            pass

    def _RemoveChildRO(self, child):
        try:
            self.renderObject.children.remove(child.renderObject)
        except (AttributeError,
         ValueError,
         RuntimeError,
         TypeError):
            pass

    def AppendBackgroundObject(self, child):
        try:
            self.renderObject.background.append(child.renderObject)
        except AttributeError:
            pass

    def InsertBackgroundObject(self, idx, child):
        try:
            self.renderObject.background.insert(idx, child.renderObject)
        except AttributeError:
            pass

    def RemoveBackgroundObject(self, child):
        try:
            self.renderObject.background.remove(child.renderObject)
        except (AttributeError,
         ValueError,
         RuntimeError,
         TypeError):
            pass

    @property
    def background_color(self):
        return self._bgColor

    @background_color.setter
    def background_color(self, value):
        self._bgColor = value
        self._SetupBackground()

    @property
    def background_texture_path(self):
        return self._bgTexturePath

    @background_texture_path.setter
    def background_texture_path(self, value):
        self._bgTexturePath = value
        self._SetupBackground()

    def UpdateUIScaling(self, value, oldValue):
        for child in self.children:
            child.UpdateUIScaling(value, oldValue)

        for bgChild in self.background:
            bgChild.UpdateUIScaling(value, oldValue)

    def OnColorThemeChanged(self):
        for child in self.children:
            child.OnColorThemeChanged()

        for bgChild in self.background:
            bgChild.OnColorThemeChanged()

    def OnWindowAboveSetActive(self):
        for child in self.children:
            child.OnWindowAboveSetActive()

        for bgChild in self.background:
            bgChild.OnWindowAboveSetActive()

    def OnWindowAboveSetInactive(self):
        for child in self.children:
            child.OnWindowAboveSetInactive()

        for bgChild in self.background:
            bgChild.OnWindowAboveSetInactive()

    def OnGlobalFontSizeChanged(self):
        for child in self.children:
            child.OnGlobalFontSizeChanged()

        for bgChild in self.background:
            bgChild.OnGlobalFontSizeChanged()

    def OnGlobalFontShadowChanged(self):
        for child in self.children:
            child.OnGlobalFontShadowChanged()

        for bgChild in self.background:
            bgChild.OnGlobalFontShadowChanged()
