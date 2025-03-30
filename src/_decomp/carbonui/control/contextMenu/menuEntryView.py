#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\control\contextMenu\menuEntryView.py
import carbonui
import trinity
import uthread2
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui import uiconst, Align
from carbonui.control.checkbox import Checkbox
from carbonui.control.contextMenu.menuEntryUnderlay import MenuEntryUnderlay
from carbonui.control.contextMenu.menuUtil import FlashEntrySelection
from carbonui.control.radioButton import RadioButton
from carbonui.control.slider import Slider
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.primitives.sprite import Sprite
from carbonui.text.color import TextColor
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from eve.client.script.ui import eveColor
from eve.client.script.ui.services.tutoriallib import TutorialColor
PAD_LEFT = 4
LABELVERTICALPADDING = 4
LABELHORIZONTALPADDING = 8

class BaseMenuEntryView(Container):

    def ApplyAttributes(self, attributes):
        super(BaseMenuEntryView, self).ApplyAttributes(attributes)
        self.iconSize = attributes.iconSize
        self.menuEntryData = attributes.menuEntryData
        self.underlay = None
        self.highlightFrame = None
        self.icon = None
        self.ConstructLayout()
        self.UpdateHeight()
        if not self.menuEntryData.IsEnabled():
            self.SetDisabled()

    def IsInteractable(self):
        return self.menuEntryData.IsEnabled()

    def SetDisabled(self):
        self.label.SetRGBA(0.5, 0.5, 0.5, 1.0)

    def UpdateHeight(self):
        self.height = self._GetHeight()

    def _GetHeight(self):
        return max(self.iconSize, self.label.textheight + LABELVERTICALPADDING)

    def GetRequiredWidth(self):
        width = self.label.textwidth + self.label.left
        if self.menuEntryData.HasSubMenuData():
            width += 16
        return width

    def ConstructLayout(self):
        self.ConstructLabel()

    def ConstructUnderlay(self, *args):
        self.underlay = MenuEntryUnderlay(parent=self, padding=(1, 1, 0, 0))

    def OnMouseEnter(self, *args):
        if not self.IsInteractable():
            return
        if self.underlay is None:
            self.ConstructUnderlay()
        self.underlay.OnMouseEnter()

    def HideHilite(self):
        if self.underlay:
            self.underlay.HideHilite()

    def OnMouseExit(self, *args):
        if self.underlay:
            self.underlay.OnMouseExit()

    def ConstructLabel(self, *args):
        left = self._GetLabelLeft()
        self.label = carbonui.TextBody(parent=self, pos=(left,
         0,
         0,
         0), align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED, text=self.menuEntryData.GetTextDescriptive())

    def _GetLabelLeft(self):
        if self.iconSize and self.menuEntryData:
            return PAD_LEFT + self.iconSize + 8
        else:
            return PAD_LEFT

    def GetHint(self):
        return self.menuEntryData.GetHint()

    def GetTooltipPointer(self):
        return uiconst.POINT_RIGHT_2


class MenuEntryView(BaseMenuEntryView):
    default_cursor = uiconst.UICURSOR_SELECT

    def ApplyAttributes(self, attributes):
        super(MenuEntryView, self).ApplyAttributes(attributes)
        self.subMenuView = None

    def ConstructLayout(self):
        super(MenuEntryView, self).ConstructLayout()
        self.ConstructSubMenuIcon()
        self.CheckConstructIcon()

    def ConstructSubMenuIcon(self, *args):
        if self.menuEntryData.HasSubMenuData():
            self.subMenuIcon = Sprite(parent=self, align=uiconst.CENTERRIGHT, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/Icons/1_16_14.png', color=TextColor.NORMAL, pos=(0, 0, 16, 16), outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, glowBrightness=0.0)
        else:
            self.subMenuIcon = None

    def IsInteractable(self):
        return super(MenuEntryView, self).IsInteractable() and self.menuEntryData.HasFunction()

    def Highlight(self):
        if self.highlightFrame is None:
            self.highlightFrame = Fill(parent=self, color=TutorialColor.HINT_FRAME, opacity=0.0)
            animations.FadeTo(self.highlightFrame, 0.0, 0.8, duration=1.6, curveType=uiconst.ANIM_WAVE, loops=uiconst.ANIM_REPEAT)

    def ClearHighlight(self):
        if self.highlightFrame is not None:
            uicore.animations.StopAllAnimations(self.highlightFrame)
            self.highlightFrame.Close()
            self.pulseThread = None

    def CheckConstructIcon(self):
        if not self.iconSize:
            return
        if self.menuEntryData.HasGroupIcon():
            self.ConstructGroupIcon()
        elif self.menuEntryData.HasIcon():
            self.ConstructIcon()

    def ConstructGroupIcon(self):
        iconTexturePath, bgTexturePath, bgColor = self.menuEntryData.GetGroupIconData()
        self.icon = Container(name='iconCont', parent=self, pos=(PAD_LEFT,
         0,
         self.iconSize,
         self.iconSize), align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED)
        Sprite(name='icon', bgParent=self.icon, texturePath=iconTexturePath)
        if bgTexturePath:
            Sprite(name='iconBG', bgParent=self.icon, texturePath=bgTexturePath, color=bgColor, outputMode=trinity.Tr2SpriteTarget.GLOW, opacity=0.75)
            Sprite(name='iconBG', bgParent=self.icon, texturePath=bgTexturePath, color=bgColor)

    def ConstructIcon(self):
        self.icon = Sprite(name='icon', parent=self, pos=(PAD_LEFT,
         0,
         self.iconSize,
         self.iconSize), align=uiconst.CENTERLEFT, texturePath=self.menuEntryData.GetIcon(), state=uiconst.UI_DISABLED, color=TextColor.NORMAL)

    def SetDisabled(self):
        super(MenuEntryView, self).SetDisabled()
        if self.icon:
            self.icon.opacity = 0.5

    def _OnClose(self):
        if self.subMenuView is not None and not self.subMenuView.destroyed:
            self.subMenuView.Close()
            self.subMenuView = None
        Container._OnClose(self)

    def OnMouseDown(self, *etc):
        if not self.menuEntryData.HasFunction() or not self.menuEntryData.IsEnabled():
            return
        self._AnimMouseDown()
        if self.underlay:
            self.underlay.OnMouseDown()

    def _AnimMouseDown(self):
        animations.SpColorMorphTo(self.label, self.label.GetRGBA(), eveColor.BLACK, duration=uiconst.TIME_MOUSEDOWN)
        if self.icon and isinstance(self.icon, Sprite):
            animations.SpColorMorphTo(self.icon, self.icon.GetRGBA(), eveColor.BLACK, duration=uiconst.TIME_MOUSEDOWN)
        if self.subMenuIcon:
            animations.SpColorMorphTo(self.subMenuIcon, self.subMenuIcon.GetRGBA(), eveColor.BLACK, duration=uiconst.TIME_MOUSEDOWN)

    def OnMouseUp(self, *etc):
        if not self.menuEntryData.IsEnabled():
            return
        if self.underlay:
            self.underlay.OnMouseUp()
        if not self.IsMouseOverEntry():
            return
        if not self.menuEntryData.IsEnabled():
            return
        PlaySound('msg_MenuActivate_play')
        if self.menuEntryData.HasFunction():
            uthread2.start_tasklet(self.menuEntryData.ExecuteFunction)
            uthread2.start_tasklet(self._OnFunctionCalled)

    def _OnFunctionCalled(self):
        from carbonui.control.contextMenu.menuUtil import CloseContextMenus
        pos = self.GetAbsolute()
        CloseContextMenus()
        FlashEntrySelection(pos)

    def OnMouseEnter(self, *args):
        if not self.menuEntryData.IsEnabled():
            return
        super(MenuEntryView, self).OnMouseEnter()
        if self.menuEntryData.IsSubMenuDynamic():
            uthread2.start_tasklet(self._ContinouslyReconstrureSubMenuThread)
        else:
            uthread2.start_tasklet(self.CheckReconstructSubMenu)
        if self.menuEntryData.HasSubMenuData() or self.menuEntryData.HasFunction():
            self._AnimMouseEnter()
        if self.subMenuIcon:
            if not self.subMenuView:
                PlaySound(uiconst.SOUND_EXPAND)
        else:
            PlaySound(uiconst.SOUND_ENTRY_HOVER)

    def _AnimMouseEnter(self):
        animations.SpColorMorphTo(self.label, startColor=self.label.GetRGBA(), endColor=TextColor.HIGHLIGHT, duration=uiconst.TIME_ENTRY)
        if self.icon and isinstance(self.icon, Sprite):
            animations.SpColorMorphTo(self.icon, self.icon.GetRGBA(), TextColor.HIGHLIGHT, duration=uiconst.TIME_ENTRY)
        if self.subMenuIcon:
            animations.SpColorMorphTo(self.subMenuIcon, self.subMenuIcon.GetRGBA(), TextColor.HIGHLIGHT, duration=uiconst.TIME_ENTRY)
            animations.MorphScalar(self.subMenuIcon, 'glowBrightness', self.subMenuIcon.glowBrightness, 0.5, duration=uiconst.TIME_ENTRY)

    def _ContinouslyReconstrureSubMenuThread(self):
        while not self.destroyed and self.IsMouseOverEntry():
            self.CheckReconstructSubMenu()
            uthread2.Sleep(0.5)

    def CheckReconstructSubMenu(self):
        if self.destroyed:
            return
        self._CollapseSiblingSubMenus()
        if self.IsMouseOverEntry() and self.menuEntryData.HasSubMenuData():
            self.ReconstructSubMenuView()

    def HideHilite(self):
        super(MenuEntryView, self).HideHilite()

    def OnMouseExit(self, *args):
        if not self.menuEntryData.IsEnabled():
            return
        self._AnimMouseExit()
        super(MenuEntryView, self).OnMouseExit(*args)

    def _AnimMouseExit(self):
        animations.SpColorMorphTo(self.label, self.label.GetRGBA(), TextColor.NORMAL, duration=uiconst.TIME_EXIT)
        if self.icon and isinstance(self.icon, Sprite):
            animations.SpColorMorphTo(self.icon, self.icon.GetRGBA(), TextColor.NORMAL, duration=uiconst.TIME_EXIT)
        if self.subMenuIcon:
            animations.SpColorMorphTo(self.subMenuIcon, self.subMenuIcon.GetRGBA(), TextColor.NORMAL, duration=uiconst.TIME_EXIT)
            animations.MorphScalar(self.subMenuIcon, 'glowBrightness', self.subMenuIcon.glowBrightness, 0.0, duration=uiconst.TIME_EXIT)

    def Collapse(self):
        if self.subMenuView:
            if not self.subMenuView.destroyed:
                self.subMenuView.Collapse()
            self.subMenuView = None

    def ReconstructSubMenuView(self):
        from carbonui.control.contextMenu.contextMenu import ContextSubMenu
        from carbonui.control.contextMenu.menuUtil import CloseContextMenus
        self._CollapseSiblingSubMenus()
        if not self.IsMouseOverEntry():
            return
        if self.subMenuView:
            self.subMenuView.Close()
        menuData = self.menuEntryData.GetSubMenuData()
        if not menuData:
            return
        menu = ContextSubMenu(parent=uicore.layer.menu, parentEntry=self, menuData=menuData, idx=0)
        if self.destroyed:
            CloseContextMenus()
            return
        self.subMenuView = menu

    def _CollapseSiblingSubMenus(self):
        for menuEntryView in self.parent.children:
            if menuEntryView != self and getattr(menuEntryView, 'subMenuView', None):
                menuEntryView.Collapse()

    def IsMouseOverEntry(self):
        return uicore.uilib.mouseOver in (self, self.label)


class MenuEntryViewCaption(BaseMenuEntryView):

    def UpdateAlignment(self, budgetLeft = 0, budgetTop = 0, budgetWidth = 0, budgetHeight = 0, updateChildrenOnly = False):
        self.padTop = 16 if self.GetOrder() else 0
        return super(MenuEntryViewCaption, self).UpdateAlignment(budgetLeft, budgetTop, budgetWidth, budgetHeight, updateChildrenOnly)

    def ConstructLabel(self, *args):
        self.label = carbonui.TextHeader(parent=self, pos=(PAD_LEFT,
         0,
         0,
         0), align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, text=self.menuEntryData.GetTextDescriptive(), color=TextColor.HIGHLIGHT)

    def SetDisabled(self):
        pass

    def _GetHeight(self):
        return self.label.textheight + 8


class MenuEntryViewLabel(BaseMenuEntryView):

    def UpdateAlignment(self, budgetLeft = 0, budgetTop = 0, budgetWidth = 0, budgetHeight = 0, updateChildrenOnly = False):
        self.padTop = 8 if self.GetOrder() else 0
        return super(MenuEntryViewLabel, self).UpdateAlignment(budgetLeft, budgetTop, budgetWidth, budgetHeight, updateChildrenOnly)

    def ConstructLabel(self, *args):
        self.label = carbonui.TextBody(parent=self, pos=(PAD_LEFT,
         0,
         0,
         0), align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, text=self.menuEntryData.GetTextDescriptive(), color=TextColor.SECONDARY)

    def SetDisabled(self):
        pass

    def _GetHeight(self):
        return self.label.textheight + 8


class MenuEntryViewCheckbox(BaseMenuEntryView):

    def ConstructLayout(self):
        super(MenuEntryViewCheckbox, self).ConstructLayout()
        self.ConstructButton()
        self.menuEntryData.on_enabled_changed.connect(self._on_enabled_changed)

    def ConstructButton(self):
        self.checkbox = Checkbox(parent=self, align=uiconst.CENTERLEFT, setting=self.menuEntryData.setting, minHeight=Checkbox.DIODE_SIZE, padding=0, left=PAD_LEFT, text=self.menuEntryData.GetTextDescriptive(), enabled=self.menuEntryData.IsEnabled(), hint=self.menuEntryData.hint)

    def SetDisabled(self):
        self.checkbox.enabled = False

    def GetRequiredWidth(self):
        return self.checkbox.left + self.checkbox.width

    def ConstructLabel(self, *args):
        pass

    def OnMouseEnter(self, *args):
        super(MenuEntryViewCheckbox, self).OnMouseEnter(*args)
        self.checkbox.OnMouseEnter()

    def OnMouseExit(self, *args):
        super(MenuEntryViewCheckbox, self).OnMouseExit(*args)
        self.checkbox.OnMouseExit()

    def OnClick(self, *args):
        super(MenuEntryViewCheckbox, self).OnClick(*args)
        self.checkbox.OnClick()

    def OnMouseDown(self, *args):
        super(MenuEntryViewCheckbox, self).OnMouseDown(*args)
        self.checkbox.OnMouseDown(*args)

    def OnMouseUp(self, *args):
        super(MenuEntryViewCheckbox, self).OnMouseUp(*args)
        self.checkbox.OnMouseUp(*args)

    def _GetHeight(self):
        return self.checkbox.height

    def _on_enabled_changed(self, menu_entry_data):
        self.checkbox.enabled = menu_entry_data.IsEnabled()


class MenuEntryViewRadioButton(MenuEntryViewCheckbox):

    def ConstructButton(self):
        self.checkbox = RadioButton(parent=self, align=uiconst.CENTERLEFT, minHeight=Checkbox.DIODE_SIZE, padding=0, left=PAD_LEFT, setting=self.menuEntryData.setting, retval=self.menuEntryData.value, text=self.menuEntryData.GetTextDescriptive(), enabled=self.menuEntryData.IsEnabled())


class MenuEntryViewSlider(BaseMenuEntryView):

    def ConstructLayout(self):
        super(MenuEntryViewSlider, self).ConstructLayout()
        self.ConstructSlider()
        self.menuEntryData.on_enabled_changed.connect(self._on_enabled_changed)

    def ConstructSlider(self):
        self.content = ContainerAutoSize(name='content', parent=self, align=uiconst.TOTOP, width=256, padLeft=self._GetLabelLeft())
        labelContainer = ContainerAutoSize(parent=self.content, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, padTop=4)
        self.valueLabel = carbonui.TextBody(parent=labelContainer, align=Align.TORIGHT, text=self._GetValueText(self.menuEntryData.setting.get()))
        self.label = carbonui.TextBody(parent=labelContainer, align=Align.TOTOP, text=self.menuEntryData.GetTextDescriptive())
        self.slider = Slider(parent=self.content, align=Align.TOTOP, setting=self.menuEntryData.setting, enabled=self.menuEntryData.IsEnabled(), minLabel=self.menuEntryData.min_label, maxLabel=self.menuEntryData.max_label, isInteger=self.menuEntryData.isInteger, padTop=2, callback=self._on_value_changed, on_dragging=self._on_value_changed)

    def SetDisabled(self):
        self.slider.enabled = False

    def ConstructLabel(self, *args):
        pass

    def GetRequiredWidth(self):
        return self.content.left + self.content.width

    def _GetHeight(self):
        _, height = self.label.MeasureTextSize(self.menuEntryData.GetTextDescriptive())
        return height + self.slider.height + 10

    def _on_enabled_changed(self, menu_entry_data):
        self.slider.enabled = menu_entry_data.IsEnabled()

    def _on_value_changed(self, slider):
        self.valueLabel.text = self._GetValueText(slider.value)

    def IsInteractable(self):
        return False

    def _GetValueText(self, value):
        import eveformat
        return eveformat.number(value, decimal_places=0 if self.menuEntryData.isInteger else 2)
