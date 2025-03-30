#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\utilMenu.py
import weakref
import carbonui.const as uiconst
from carbon.client.script.environment.AudioUtil import PlaySound
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.primitives.line import Line
from carbonui.primitives.sprite import Sprite
from carbonui.util.various_unsorted import IsUnder
from carbonui.control.buttonIcon import ButtonIcon
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from carbonui.decorative.menuUnderlay import MenuUnderlay
from eve.client.script.ui.control.themeColored import FillThemeColored, FrameThemeColored, LineThemeColored, SpriteThemeColored
from eve.client.script.ui.services.tutoriallib import TutorialColor
from eve.common.lib.appConst import defaultPadding
import uthread
from carbonui.uicore import uicore
IDLE_OPACITY = 0.8
MOUSEOVER_OPACITY = 1.0
TOGGLEACTIVE_OPACITY = 0.8
TOGGLEINACTIVE_OPACITY = 0.6
DISABLED_OPACITY = 0.2
OPACITY_LINES = 0.2
OPACITY_BG = 0.8

class UtilMenu(ButtonIcon):
    default_name = 'UtilMenu'
    default_align = uiconst.TOPLEFT
    default_state = uiconst.UI_NORMAL
    default_texturePath = 'res:/UI/Texture/Icons/77_32_30.png'
    default_iconSize = 16
    default_width = 24
    default_height = 24
    default_maxWidth = None
    default_menuAlign = uiconst.TOPLEFT
    default_bgOpacityExpandedIcon = OPACITY_BG
    default_opacityExpandedLines = OPACITY_LINES
    default_labelAlign = uiconst.CENTERLEFT
    _getMenuFunction = None
    _expanded = False
    _menu = None
    _label = None
    _menuButton = None

    def Close(self, *args):
        if self.destroyed:
            return
        self._getMenuFunction = None
        ButtonIcon.Close(self, *args)
        if self.IsExpanded():
            self.CloseMenu()

    def CloseMenu(self, *args):
        if self._menu:
            menu = self._menu()
            if menu:
                menu.Close()

    def OnMenuClosed(self, *args):
        if self._menuButton:
            menuButton = self._menuButton()
            if menuButton:
                menuButton.Close()

    def ApplyAttributes(self, attributes):
        ButtonIcon.ApplyAttributes(self, attributes)
        self._label = None
        self._menu = None
        self._menuButton = None
        if attributes.GetUtilMenu:
            self._getMenuFunction = attributes.GetUtilMenu
        else:
            raise RuntimeError('GetUtilMenu has to be provided in order to use UtilMenu')
        texturePath = attributes.get('texturePath', self.default_texturePath)
        closeTexturePath = attributes.get('closeTexturePath', None)
        iconSize = attributes.get('iconSize', self.default_iconSize)
        self.texturePath = texturePath
        self.iconSize = iconSize
        self.menuAlign = attributes.get('menuAlign', self.default_menuAlign)
        self.closeTexturePath = closeTexturePath or texturePath
        self.maxWidth = attributes.get('maxWidth', self.default_maxWidth)
        self.bgOpacityExpandedIcon = attributes.get('bgOpacityExpandedIcon', self.default_bgOpacityExpandedIcon)
        self.opacityExpandedLines = attributes.get('opacityExpandedLines', self.default_opacityExpandedLines)
        self.labelAlign = attributes.get('labelAlign', self.default_labelAlign)
        if attributes.label:
            self.SetLabel(attributes.label, self.labelAlign)

    def SetLabel(self, label, labelAlign = None):
        if labelAlign is None:
            labelAlign = self.labelAlign
        if labelAlign not in (uiconst.CENTERLEFT, uiconst.CENTERRIGHT):
            raise RuntimeError('SetLabel labelAlign has to be CENTERLEFT or CENTERRIGHT')
        if labelAlign == uiconst.CENTERLEFT:
            iconAlign = uiconst.CENTERRIGHT
        else:
            iconAlign = uiconst.CENTERLEFT
        if self._label is None:
            self._label = EveLabelMedium(parent=self, text=label, align=labelAlign, left=const.defaultPadding * 2)
        else:
            self._label.text = label
        margin = int((self.height - self.iconSize) / 2.0)
        self.width = self.GetFullWidth()
        if self.maxWidth:
            self.width = min(self.maxWidth, self.width)
            self._label.SetRightAlphaFade(self.maxWidth - defaultPadding * 6, 10)
        icon = self.icon
        icon.align = iconAlign
        icon.left = margin
        background = self.bgContainer
        background.align = uiconst.CENTERLEFT
        background.width = self.width
        if self._menuButton:
            buttonCopy = self._menuButton()
            if buttonCopy:
                if not hasattr(buttonCopy, 'label'):
                    buttonCopy.label = EveLabelMedium(parent=buttonCopy, text=label, align=labelAlign, left=self._label.left)
                else:
                    buttonCopy.label.SetText(label)
                    buttonCopy.label.SetAlign(labelAlign)
                buttonCopy.width = self.GetFullWidth()

    def GetFullWidth(self):
        margin = int((self.height - self.iconSize) / 2.0)
        if self._label:
            width = self._label.left + self._label.width + self.iconSize + 2 * margin
        else:
            width = self.iconSize + 2 * margin
        if self.align == uiconst.TOTOP:
            absWidth, _ = self.GetAbsoluteSize()
            width = max(width, absWidth)
        return width

    def GetHint(self):
        if self._label and self._label.text:
            if self.maxWidth and self.maxWidth < self.GetFullWidth():
                return self._label.text
        return self.hint

    def OnClick(self, *args):
        if not self.enabled:
            return
        PlaySound(uiconst.SOUND_EXPAND)
        self.ExpandMenu()

    def IsExpanded(self):
        return bool(self._menu and self._menu() and not self._menu().destroyed)

    def ExpandMenu(self, *args):
        if self.destroyed:
            return
        if self.IsExpanded():
            self.CloseMenu()
            return
        background = self.bgContainer
        icon = self.icon
        l, t, w, h = background.GetAbsolute()
        buttonCopy = Container(name='buttonCopy', parent=uicore.layer.utilmenu, align=uiconst.TOPLEFT, pos=(l,
         t,
         self.GetFullWidth(),
         h), state=uiconst.UI_NORMAL, idx=0)
        buttonCopy.OnMouseDown = self.CloseMenu
        if self._label is not None:
            buttonCopy.label = EveLabelMedium(parent=buttonCopy, text=self._label.text, align=self._label.align, left=self._label.left)
        try:
            expandedPadding = 0 if self.align == uiconst.TOTOP else 16
            menuParent = ExpandedUtilMenu(parent=uicore.layer.utilmenu, controller=self, GetUtilMenu=self._getMenuFunction, minWidth=self.GetFullWidth() + expandedPadding, idx=1, menuAlign=self.menuAlign)
        except StandardError:
            buttonCopy.Close()
            raise

        self._menu = weakref.ref(menuParent)
        self._menuButton = weakref.ref(buttonCopy)
        uicore.animations.MorphScalar(buttonCopy, 'opacity', startVal=0.5, endVal=1.0, duration=0.2)
        uthread.new(uicore.registry.SetFocus, menuParent)
        sm.ScatterEvent('OnUtilMenuOpened')


class ExpandedUtilMenu(ContainerAutoSize):
    __guid__ = 'ExpandedUtilMenu'
    default_name = 'ExpandedUtilMenu'
    default_state = uiconst.UI_NORMAL
    default_opacity = 0
    default_bgOpacity = OPACITY_BG
    default_menuAlign = uiconst.TOPLEFT
    minWidth = 0

    def ApplyAttributes(self, attributes):
        attributes.align = uiconst.TOPLEFT
        attributes.width = 128
        attributes.height = 128
        ContainerAutoSize.ApplyAttributes(self, attributes)
        if attributes.GetUtilMenu:
            self._getMenuFunction = attributes.GetUtilMenu
        else:
            raise RuntimeError('GetUtilMenu has to be provided in order to use UtilMenu')
        self.controller = attributes.controller
        self.isTopLevelWindow = True
        self.menuAlign = attributes.Get('menuAlign', self.default_menuAlign)
        self.minWidth = attributes.minWidth or 0
        self.bgOpacity = attributes.Get('bgOpacity', self.default_bgOpacity)
        MenuUnderlay(bgParent=self, padding=-8)
        uicore.uilib.RegisterForTriuiEvents([uiconst.UI_MOUSEDOWN], self.OnGlobalMouseDown)
        self.ReloadMenu()
        self.AnimFadeIn()
        self.UpdateMenuPosition()

    def OnGlobalMouseDown(self, *args):
        if self.destroyed:
            return False
        for layer in (uicore.layer.utilmenu, uicore.layer.modal, uicore.layer.menu):
            if IsUnder(uicore.uilib.mouseOver, layer):
                return True

        self.Close()
        return False

    def AnimFadeIn(self):
        uicore.animations.FadeIn(self, duration=0.2)

    def Close(self, *args):
        if self.controller and hasattr(self.controller, 'OnMenuClosed'):
            self.controller.OnMenuClosed()
        ContainerAutoSize.Close(self, *args)

    def _OnSizeChange_NoBlock(self, *args, **kwds):
        ContainerAutoSize._OnSizeChange_NoBlock(self, *args, **kwds)
        self.OnSizeChanged()

    def OnSizeChanged(self, *args):
        self.UpdateMenuPosition()

    def SetSizeAutomatically(self):
        width = self.minWidth
        for each in self.children:
            if hasattr(each, 'GetEntryWidth'):
                width = max(width, each.GetEntryWidth())

        self.width = width
        ContainerAutoSize.SetSizeAutomatically(self)

    def ReloadMenu(self):
        self.Flush()
        getMenuFunction = self._getMenuFunction
        if callable(getMenuFunction):
            getMenuFunction(self)
        elif isinstance(getMenuFunction, tuple):
            func = getMenuFunction[0]
            if callable(func):
                func(self, *getMenuFunction[1:])

    def UpdateMenuPosition(self, *args):
        if self.controller.destroyed:
            return
        l, t, w, h = self.controller.GetAbsolute()
        shiftAmount = 0
        if self.menuAlign in (uiconst.TOPRIGHT, uiconst.BOTTOMRIGHT):
            self.left = l - self.width + w - 8
            shiftAmount = -w
        else:
            self.left = l + 8
            shiftAmount = w
        if self.menuAlign in (uiconst.BOTTOMLEFT, uiconst.BOTTOMRIGHT):
            self.top = t - self.height - 8
        else:
            self.top = t + h + 8
        shiftToSide = False
        if self.top < 0:
            self.top = 0
            shiftToSide = True
        elif self.top + self.height > uicore.desktop.height:
            self.top = uicore.desktop.height - self.height
            shiftToSide = True
        if shiftToSide:
            if self.left + self.width + shiftAmount < uicore.desktop.width:
                self.left += shiftAmount
            else:
                self.left = self.left - self.width
        if self.left < 0:
            self.left = l + w
        elif self.left + self.width > uicore.desktop.width:
            self.left = l - self.width

    def VerifyCallback(self, callback):
        if callable(callback):
            return True
        if isinstance(callback, tuple):
            func = callback[0]
            if callable(func):
                return True
        raise RuntimeError('Callback has to be callable or tuple with callable as first argument')

    def AddHeader(self, text, callback = None, hint = None, icon = None):
        if callback:
            self.VerifyCallback(callback)
        return UtilMenuHeader(parent=self, text=text, callback=callback, hint=hint, icon=icon)

    def AddIconEntry(self, icon, text, callback = None, hint = None, toggleMode = None, name = 'UtilMenuIconEntry'):
        if callback:
            self.VerifyCallback(callback)
        return UtilMenuIconEntry(parent=self, icon=icon, text=text, callback=callback, hint=hint, toggleMode=toggleMode, name=name)

    def AddButton(self, text, callback = None, hint = None, toggleMode = None):
        if callback:
            self.VerifyCallback(callback)
        return UtilMenuButton(parent=self, text=text, callback=callback, hint=hint, toggleMode=toggleMode)

    def AddCheckBox(self, text, checked, callback = None, icon = None, hint = None, indentation = None, state = uiconst.UI_NORMAL, uniqueUiName = None):
        if callback:
            self.VerifyCallback(callback)
        return UtilMenuCheckBox(parent=self, text=text, checked=checked, icon=icon, hint=hint, callback=callback, indentation=indentation, state=state, uniqueUiName=uniqueUiName)

    def AddCheckBoxWithSubIcon(self, text, checked, subIcon, callback = None, subIconCallback = None, icon = None, subIconHint = None, hint = None):
        if callback:
            self.VerifyCallback(callback)
        UtilMenuCheckBoxWithButton(parent=self, text=text, checked=checked, icon=icon, hint=hint, callback=callback, subIcon=subIcon, subIconCallback=subIconCallback, subIconHint=subIconHint)

    def AddRadioButton(self, text, checked, callback = None, icon = None, hint = None, uniqueUiName = None):
        if callback:
            self.VerifyCallback(callback)
        return UtilMenuRadioBox(parent=self, text=text, checked=checked, icon=icon, hint=hint, callback=callback, uniqueUiName=uniqueUiName)

    def AddText(self, text, minTextWidth = 100):
        return UtilMenuText(parent=self, text=text, minTextWidth=minTextWidth)

    def AddSpace(self, height = 5):
        return UtilMenuSpace(parent=self, height=height)

    def AddDivider(self, padding = 0):
        return UtilMenuDivider(parent=self, padding=padding)

    def AddContainer(self, *args, **kwargs):
        return UtilMenuContainer(parent=self, *args, **kwargs)

    def AddLayoutGrid(self, *args, **kwargs):
        return UtilMenuLayoutGrid(parent=self, *args, **kwargs)


class UtilMenuEntryBase(Container):
    __guid__ = 'UtilMenuEntryBase'
    default_align = uiconst.TOTOP
    default_state = uiconst.UI_NORMAL
    default_icon = None
    _hiliteSprite = None
    callback = None
    isToggleEntry = False
    uniqueUiName = None

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        labelLeft = 22
        iconLeft = 3
        if attributes.indentation:
            labelLeft += attributes.indentation
            iconLeft += attributes.indentation
        self.label = EveLabelMedium(parent=self, text=attributes.text, align=uiconst.CENTERLEFT, left=labelLeft, state=uiconst.UI_DISABLED)
        icon = attributes.Get('icon', self.default_icon)
        if icon is not None:
            self.icon = SpriteThemeColored(parent=self, texturePath=icon, colorType=uiconst.COLORTYPE_UIHILIGHTGLOW, state=uiconst.UI_DISABLED, left=iconLeft, width=16, height=16, align=uiconst.CENTERLEFT, ignoreSize=True)
        self.ResetOpacity()
        self.TryAddHighlighting()
        self.UpdateEntryHeight()

    def TryAddHighlighting(self):
        if self.uniqueUiName is None:
            return
        isHighlighted = sm.GetService('helpPointer').IsUtilMenuEntryHighlighted(self.uniqueUiName)
        if not isHighlighted:
            return
        self.highlightFrame = Fill(bgParent=self, color=TutorialColor.HINT_FRAME, opacity=0.0)
        uicore.animations.FadeTo(self.highlightFrame, 0.0, 0.4, duration=1.6, curveType=uiconst.ANIM_WAVE, loops=uiconst.ANIM_REPEAT)

    def UpdateEntryHeight(self):
        self.height = self.label.textheight + 4

    def GetEntryWidth(self):
        return self.label.width + self.label.left + 12

    def ResetOpacity(self):
        if not self.callback:
            self.opacity = DISABLED_OPACITY
        elif self.isToggleEntry:
            if self.isChecked:
                self.opacity = TOGGLEACTIVE_OPACITY
            else:
                self.opacity = TOGGLEINACTIVE_OPACITY
        else:
            self.opacity = IDLE_OPACITY

    def OnClick(self, *args):
        callback = self.callback
        if callback:
            PlaySound(uiconst.SOUND_BUTTON_CLICK)
            if callable(callback):
                callback()
            elif isinstance(callback, tuple):
                func = callback[0]
                if callable(func):
                    func(*callback[1:])
        if self.parent:
            if self.isToggleEntry:
                self.parent.ReloadMenu()
            else:
                self.parent.Close()

    def OnMouseEnter(self, *args):
        if not self.callback:
            self.opacity = DISABLED_OPACITY
        else:
            self.opacity = MOUSEOVER_OPACITY
            PlaySound(uiconst.SOUND_ENTRY_HOVER)
            if not self._hiliteSprite:
                self._hiliteSprite = SpriteThemeColored(parent=self, name='hiliteSprite', texturePath='res:/UI/Texture/classes/UtilMenu/entryHilite.png', opacity=0.0, padding=(1, 0, 1, 0), align=uiconst.TOALL, state=uiconst.UI_DISABLED)
            uicore.animations.FadeIn(self._hiliteSprite, 0.2, duration=uiconst.TIME_ENTRY)
            self.hiliteTimer = AutoTimer(1, self._CheckIfStillHilited)

    def OnMouseExit(self, *args):
        if not (IsUnder(uicore.uilib.mouseOver, self) or uicore.uilib.mouseOver is self):
            self.ShowNotHilited()

    def ShowNotHilited(self):
        self.ResetOpacity()
        self.hiliteTimer = None
        if self._hiliteSprite and self._hiliteSprite.display:
            uicore.animations.FadeOut(self._hiliteSprite, duration=uiconst.TIME_EXIT)

    def _CheckIfStillHilited(self):
        if IsUnder(uicore.uilib.mouseOver, self) or uicore.uilib.mouseOver is self:
            return
        self.ShowNotHilited()


class UtilMenuIconEntry(UtilMenuEntryBase):
    __guid__ = 'UtilMenuIconEntry'

    def ApplyAttributes(self, attributes):
        self.callback = attributes.callback
        if self.callback and attributes.toggleMode:
            self.isToggleEntry = True
            self.isChecked = True
        UtilMenuEntryBase.ApplyAttributes(self, attributes)


class UtilMenuButton(UtilMenuIconEntry):
    __guid__ = 'UtilMenuButton'
    default_icon = 'res:/UI/Texture/classes/UtilMenu/BulletIcon.png'


class UtilMenuCheckBox(UtilMenuEntryBase):
    __guid__ = 'UtilMenuCheckBox'
    isToggleEntry = True
    isChecked = False

    def ApplyAttributes(self, attributes):
        self.callback = attributes.callback
        self.isChecked = attributes.checked
        self.isToggleEntry = True
        if attributes.icon is None:
            if attributes.checked:
                attributes.icon = 'res:/UI/Texture/classes/UtilMenu/checkBoxActive.png'
            else:
                attributes.icon = 'res:/UI/Texture/classes/UtilMenu/checkBoxInactive.png'
        UtilMenuEntryBase.ApplyAttributes(self, attributes)


class UtilMenuCheckBoxWithButton(UtilMenuCheckBox):
    __guid__ = 'UtilMenuCheckBoxWithButton'

    def ApplyAttributes(self, attributes):
        UtilMenuCheckBox.ApplyAttributes(self, attributes)
        self.subIcon = Icon(parent=self, icon=attributes.subIcon, state=uiconst.UI_DISABLED, left=3, width=16, height=16, align=uiconst.CENTERRIGHT, ignoreSize=True)
        if attributes.subIconCallback:
            self.subIcon.hint = attributes.subIconHint
            self.subIcon.state = uiconst.UI_NORMAL
            self.subIcon.OnClick = self.OnSubIconClick
            self.subIcon.OnMouseEnter = self.OnMouseEnter
            self.subIconCallback = attributes.subIconCallback

    def OnSubIconClick(self, *args):
        callback = self.subIconCallback
        if callback:
            if callable(callback):
                callback()
            elif isinstance(callback, tuple):
                func = callback[0]
                if callable(func):
                    func(*callback[1:])
        if self.parent:
            if self.isToggleEntry:
                self.parent.ReloadMenu()
            else:
                self.parent.Close()

    def GetEntryWidth(self):
        width = UtilMenuCheckBox.GetEntryWidth(self)
        return (width + 20) / 16 * 16 + 16


class UtilMenuRadioBox(UtilMenuEntryBase):
    __guid__ = 'UtilMenuRadioBox'

    def ApplyAttributes(self, attributes):
        self.callback = attributes.callback
        self.isChecked = attributes.checked
        self.isToggleEntry = True
        if attributes.icon is None:
            if attributes.checked:
                attributes.icon = 'res:/UI/Texture/classes/UtilMenu/radioButtonActive.png'
            else:
                attributes.icon = 'res:/UI/Texture/classes/UtilMenu/radioButtonInactive.png'
        UtilMenuEntryBase.ApplyAttributes(self, attributes)


class UtilMenuHeader(UtilMenuEntryBase):
    __guid__ = 'UtilMenuHeader'
    default_align = uiconst.TOTOP
    default_state = uiconst.UI_DISABLED

    def ApplyAttributes(self, attributes):
        self.callback = attributes.callback
        if self.callback:
            attributes.state = uiconst.UI_NORMAL
            self.isToggleEntry = True
        UtilMenuEntryBase.ApplyAttributes(self, attributes)
        iconLeft = 0
        if attributes.icon:
            self.label.left = 22
        else:
            self.label.left = 6
        self.label.bold = True
        self.label.letterspace = 1
        Sprite(parent=self, align=uiconst.TOALL, texturePath='res:/UI/Texture/classes/UtilMenu/headerGradient.png', color=(1, 1, 1, 0.1), padLeft=1, padRight=1, state=uiconst.UI_DISABLED)
        self.UpdateEntryHeight()

    def ResetOpacity(self):
        pass

    def GetEntryWidth(self):
        return self.label.width + self.label.left * 2


class UtilMenuText(Container):
    __guid__ = 'UtilMenuText'
    default_align = uiconst.TOTOP
    default_height = 22
    default_minTextWidth = 100

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.minTextWidth = attributes.get('minTextWidth', self.default_minTextWidth)
        self.text = EveLabelMedium(parent=self, text=attributes.text, align=uiconst.TOTOP, padding=6, color=(1, 1, 1, 0.8), state=uiconst.UI_DISABLED)
        self.text._OnSizeChange_NoBlock = self.OnTextSizeChange
        self.height = self.text.textheight + 12

    def GetEntryWidth(self):
        return self.minTextWidth + 12

    def OnTextSizeChange(self, newWidth, newHeight):
        EveLabelMedium._OnSizeChange_NoBlock(self.text, newWidth, newHeight)
        self.height = self.text.textheight + 12


class UtilMenuSpace(Container):
    __guid__ = 'UtilMenuSpace'
    default_align = uiconst.TOTOP

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)

    def GetEntryWidth(self):
        return 0


class UtilMenuDivider(ContainerAutoSize):
    __guid__ = 'UtilMenuDivider'
    default_align = uiconst.TOTOP

    def ApplyAttributes(self, attributes):
        padding = attributes.padding or 0
        super(UtilMenuDivider, self).ApplyAttributes(attributes)
        Line(align=uiconst.TOTOP, parent=self, opacity=0.1, padding=(0, 6, 0, 6))

    def GetEntryWidth(self):
        return 0


class UtilMenuLayoutGrid(UtilMenuEntryBase, LayoutGrid):

    def ApplyAttributes(self, attributes):
        LayoutGrid.ApplyAttributes(self, attributes)

    def GetEntryWidth(self):
        return self.gridSize[0]

    def UpdateEntryHeight(self):
        pass

    def ResetOpacity(self):
        pass

    def OnClick(self, *args):
        pass

    def OnMouseEnter(self, *args):
        pass


class UtilMenuContainer(UtilMenuEntryBase, ContainerAutoSize):
    __guid__ = 'UtilMenuContainer'

    def ApplyAttributes(self, attributes):
        ContainerAutoSize.ApplyAttributes(self, attributes)
        self.ResetOpacity()
        self.UpdateEntryHeight()

    def GetEntryWidth(self):
        return 100

    def UpdateEntryHeight(self):
        pass

    def ResetOpacity(self):
        pass

    def OnClick(self, *args):
        pass

    def OnMouseEnter(self, *args):
        pass
