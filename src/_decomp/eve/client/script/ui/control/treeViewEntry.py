#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\treeViewEntry.py
import logging
from math import pi
import blue
import carbonui
from carbon.client.script.environment.AudioUtil import PlaySound
from carbon.common.lib import telemetry
from carbonui import TextColor, uiconst
from carbon.common.script.sys.serviceConst import ROLE_GML, ROLE_PROGRAMMER, ROLE_WORLDMOD
from carbonui.control.dragdrop.dragdata import TypeDragData
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.primitives.sprite import Sprite
from carbonui.uicore import uicore
from carbonui.util.color import Color
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.control.eveLabel import Label
from eve.client.script.ui.control.eveWindowUnderlay import ListEntryUnderlay
from carbonui.decorative.selectionIndicatorLine import SelectionIndicatorLine
from eve.client.script.ui.control.itemIcon import ItemIcon
from eve.client.script.ui.control.themeColored import FillThemeColored, GradientThemeColored
import localization
from eve.client.script.ui.shared.neocom.neocom.buttons.buttonIndicator import ButtonIndicator
from eve.client.script.ui.shared.neocom.neocom.highlightState import HighlightState
from eveservices.menu import GetMenuService

class TreeViewEntry(ContainerAutoSize):
    default_name = 'TreeViewEntry'
    default_align = uiconst.TOTOP
    default_alignMode = uiconst.TOTOP
    default_state = uiconst.UI_NORMAL
    default_settingsID = ''
    default_height = 24
    default_iconColor = eveColor.WHITE
    default_iconGlowBrightness = 0.0
    isDragObject = True
    allow_lazy_construction = True
    default_label_color = TextColor.NORMAL
    LEFTPUSH = 8
    LABEL_PADDING = 4

    @telemetry.ZONE_METHOD
    def ApplyAttributes(self, attributes):
        ContainerAutoSize.ApplyAttributes(self, attributes)
        self.level = attributes.get('level', 0)
        self.data = attributes.get('data')
        self.eventListener = attributes.get('eventListener', None)
        self.parentEntry = attributes.get('parentEntry', None)
        self.settingsID = attributes.get('settingsID', self.default_settingsID)
        self.defaultExpanded = attributes.get('defaultExpanded', self.level < 1)
        self.iconColor = attributes.get('iconColor', self.default_iconColor)
        self.iconGlowBrightness = attributes.get('iconGlowBrightness', self.default_iconGlowBrightness)
        self.label_color = attributes.get('label_color', self.default_label_color)
        if hasattr(self.data, 'uiName'):
            self.name = self.data.uiName
        self.childrenInitialized = False
        self.isToggling = False
        self.canAccess = True
        self.descendantSelectedBG = False
        self.selectedLine = None
        self.icon = None
        self.childCont = None
        self.data.on_selected.connect(self.OnSetSelected)
        self.data.on_deselected.connect(self.OnSetDeselected)
        self.data.on_descendant_selected.connect(self.OnDescendantSelected)
        self.data.on_descendant_deselected.connect(self.OnDescendantDeselected)
        self.data.on_expanded.connect(self.OnExpanded)
        self.data.on_collapsed.connect(self.OnCollapsed)
        self.ConstructContent()
        if self.data.IsSelected():
            self.OnSetSelected(self.data, animate=False)
        self._UpdateDescendantSelectedBG()

    def OnDescendantSelected(self, node, animate = True):
        self._UpdateDescendantSelectedBG()

    def OnDescendantDeselected(self, node, animate = True):
        self._UpdateDescendantSelectedBG()

    def ConstructContent(self):
        self.topRightCont = Container(name='topCont_%s' % self.name, parent=self, align=uiconst.TOTOP, height=self.default_height)
        self.topRightCont.GetDragData = self.GetDragData
        left = self.GetSpacerContWidth()
        if self.data.IsRemovable():
            removeBtn = Sprite(texturePath='res:/UI/Texture/icons/73_16_210.png', parent=self.topRightCont, align=uiconst.CENTERLEFT, width=16, height=16, left=left, hint=localization.GetByLabel('UI/Common/Buttons/Close'))
            left += 20
            removeBtn.OnClick = self.Remove
        left = self.ConstructIcon(left)
        left += self.LABEL_PADDING
        self.ConstructLabel()
        self.label.left = left
        self.UpdateLabel()
        self.hoverBG = None
        self.selectedBG = None
        self.blinkBG = None
        if self.data.HasChildren():
            self.spacerCont = Container(name='spacerCont', parent=self.topRightCont, align=uiconst.TOLEFT, width=self.GetSpacerContWidth())
            self.toggleBtn = Container(name='toggleBtn', parent=self.spacerCont, align=uiconst.CENTERRIGHT, width=16, height=16, state=uiconst.UI_NORMAL)
            self.toggleBtn.OnClick = self.OnToggleBtnClick
            self.toggleBtn.OnDblClick = lambda : None
            self.toggleBtnSprite = Sprite(bgParent=self.toggleBtn, texturePath='res:/UI/Texture/classes/Neocom/arrowDown.png', rotation=pi / 2, padding=(4, 4, 5, 5), color=eveColor.LED_GREY)
            if not self.data.IsForceCollapsed():
                expandChildren = self.GetIsExpandedSetting()
            else:
                expandChildren = False
        else:
            expandChildren = False
            self.spacerCont = None
            self.toggleBtnSprite = None
            self.ShowChildCont(False, animate=False)
        if expandChildren:
            self.ConstructChildren()
            self.data.SetExpanded(animate=False)
        else:
            self.data.SetCollapsed(animate=False)
        if self.eventListener and hasattr(self.eventListener, 'RegisterID'):
            self.eventListener.RegisterID(self, self.data.GetID())
        self.data.on_created(self.data)

    def GetIsExpandedSetting(self):
        toggleSettingsDict = settings.user.ui.Get('invTreeViewEntryToggle_%s' % self.settingsID, {})
        is_expanded_setting = toggleSettingsDict.get(self.data.GetID(), self.defaultExpanded)
        return is_expanded_setting

    def ConstructIcon(self, left):
        icon = self.data.GetIcon()
        if icon:
            iconSize = self.GetIconSize()
            self.icon = Icon(icon=icon, parent=self.topRightCont, pos=(left,
             0,
             iconSize,
             iconSize), align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED, ignoreSize=True, color=self.iconColor, outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, glowBrightness=self.iconGlowBrightness)
            left += iconSize
        return left

    def GetIconSize(self):
        iconSize = self.height - 2
        return iconSize

    def ConstructLabel(self):
        self.label = carbonui.TextBody(parent=self.topRightCont, align=uiconst.CENTERLEFT, text=self.data.GetLabel(), autoFadeSides=16)

    def GetSpacerContWidth(self):
        return (1 + self.level) * self.LEFTPUSH + 16

    def Close(self):
        try:
            if self.eventListener and hasattr(self.eventListener, 'UnregisterID'):
                self.eventListener.UnregisterID(self.data.GetID())
            self.data.on_destroyed(self.data)
            if self.parentEntry and self.data in self.parentEntry.data._children:
                self.parentEntry.data._children.remove(self.data)
        finally:
            ContainerAutoSize.Close(self)

    @telemetry.ZONE_METHOD
    def ConstructChildren(self):
        self.childrenInitialized = True
        children = self.data.GetChildren()
        if self.destroyed:
            return
        if self.childCont is None:
            self.childCont = ContainerAutoSize(parent=self, name='childCont', align=uiconst.TOTOP, clipChildren=True, state=uiconst.UI_HIDDEN)
        if children:
            for child in children:
                cls = self.GetTreeViewEntryClassByTreeData(child)
                child = cls(name=getattr(child, 'clsName', ''), parent=self.childCont, parentEntry=self, level=self.level + 1, eventListener=self.eventListener, data=child, settingsID=self.settingsID, state=uiconst.UI_HIDDEN)
                child.UpdateLabel()
                if self.allow_lazy_construction:
                    blue.pyos.BeNice()

            if self.childCont.children:
                self.childCont.children[-1].padBottom = 8

    def GetTreeViewEntryClassByTreeData(self, treeData):
        return TreeViewEntry

    def ShowChildCont(self, show = True, animate = True):
        if self.childCont is None or self.childCont.display == show or not self.data.HasChildren():
            return
        for child in self.childCont.children:
            self.ShowChild(child, show=show)

        self.isToggling = True
        if animate:
            if show:
                self.childCont.display = True
                uicore.animations.Tr2DRotateTo(self.toggleBtnSprite, pi / 2, 0.0, duration=0.15)
                _, height = self.childCont.GetAutoSize()
                self.childCont.DisableAutoSize()
                uicore.animations.FadeIn(self.childCont, duration=0.15)
                uicore.animations.MorphScalar(self.childCont, 'height', self.childCont.height, height, duration=0.15, callback=self.childCont.EnableAutoSize)
            else:
                uicore.animations.Tr2DRotateTo(self.toggleBtnSprite, 0.0, pi / 2, duration=0.15)
                self.childCont.DisableAutoSize()
                uicore.animations.FadeOut(self.childCont, duration=0.15)
                uicore.animations.MorphScalar(self.childCont, 'height', self.childCont.height, 0, duration=0.15, callback=self._OnEndFadeOut)
            self.toggleBtn.Enable()
        else:
            self.childCont.display = show
            if show:
                self.toggleBtnSprite.rotation = 0.0
                self.childCont.opacity = 1.0
            else:
                self.toggleBtnSprite.rotation = pi / 2
                self.childCont.DisableAutoSize()
                self.childCont.opacity = 0.0
        self.isToggling = False

    def _OnEndFadeOut(self, *args):
        self.childCont.EnableAutoSize()
        self.childCont.Hide()

    def ShowChild(self, child, show = True):
        child.display = show

    def UpdateSelectedState(self, selectedIDs):
        nodeID = self.data.GetID()
        isSelected = selectedIDs[-1] == nodeID
        if isSelected:
            self.SetSelected()
        else:
            self.SetDeselected()

    def SetSelected(self, animate = True):
        self.data.SetSelected(animate)

    def OnSetSelected(self, node, animate = True):
        self.CheckConstructHoverBG()
        self.hoverBG.Select()
        self.CheckConstructSelectedLine()
        self.selectedLine.Select()
        if self.parentEntry:
            self.parentEntry.ExpandFromRoot(animate)
        self.UpdateLabel()
        self.UpdateToggleBtnSpriteColor()

    def _UpdateDescendantSelectedBG(self):
        if self.data.IsAnyDescendantSelected():
            self.CheckConstructChildSelectedGradient()
            self.descendantSelectedBG.Show()
        elif self.descendantSelectedBG:
            self.descendantSelectedBG.Hide()

    def SetDeselected(self, animate = True):
        self.data.SetDeselected(animate)

    def OnSetDeselected(self, node, animate = True):
        if self.hoverBG:
            self.hoverBG.Deselect()
        if self.selectedLine:
            self.selectedLine.Deselect()
        self.UpdateLabel()
        self.UpdateToggleBtnSpriteColor()

    def UpdateToggleBtnSpriteColor(self):
        if not self.toggleBtnSprite:
            return
        if self.data.IsSelected():
            self.toggleBtnSprite.SetRGBA(*eveColor.WHITE)
        else:
            self.toggleBtnSprite.SetRGBA(*eveColor.LED_GREY)

    def CheckConstructSelectedLine(self):
        if not self.selectedLine:
            self.selectedLine = SelectionIndicatorLine(parent=self.topRightCont, align=uiconst.TOLEFT_NOPUSH, idx=0, padding=4)

    def CheckConstructChildSelectedGradient(self):
        if not self.descendantSelectedBG:
            self.descendantSelectedBG = GradientThemeColored(bgParent=self.spacerCont, rotation=0, alphaData=[(0, 0.5), (1.0, 0.0)], colorType=uiconst.COLORTYPE_UIHILIGHT)

    @telemetry.ZONE_METHOD
    def UpdateLabel(self):
        if self.data.IsSelected() and self.canAccess:
            self.label.color = TextColor.HIGHLIGHT
        elif self.canAccess:
            self.label.color = self.label_color
        else:
            self.label.color = TextColor.DISABLED
        if session.role & (ROLE_GML | ROLE_WORLDMOD):
            if settings.user.ui.Get('invPrimingDebugMode', False) and hasattr(self.data, 'invController') and self.data.invController.IsPrimed():
                self.label.color = Color.RED

    def ExpandFromRoot(self, animate = True):
        self.ShowChildren(animate)
        if self.parentEntry:
            self.parentEntry.ExpandFromRoot(animate)

    def OnClick(self, *args):
        PlaySound(uiconst.SOUND_ENTRY_SELECT)
        self.data.on_click(self.data)
        if self.eventListener and hasattr(self.eventListener, 'OnTreeViewClick'):
            self.eventListener.OnTreeViewClick(self, *args)

    def OnDblClick(self, *args):
        self.data.on_dbl_click(self.data)
        if self.eventListener and hasattr(self.eventListener, 'OnTreeViewDblClick'):
            self.eventListener.OnTreeViewDblClick(self, *args)

    def OnToggleBtnClick(self, *args):
        if not self.isToggling:
            self.data.ToggleExpanded()

    def ToggleChildren(self, animate = True):
        self.data.ToggleExpanded(animate)

    def ShowChildren(self, amimate = True):
        self.data.SetExpanded(amimate)

    def HideChildren(self):
        self.data.SetCollapsed()

    def OnExpanded(self, treeData, animate = True):
        self._PersistIsExpandedSetting(True)
        if not self.data.HasChildren():
            return
        if not self.childrenInitialized:
            self.ConstructChildren()
        PlaySound(uiconst.SOUND_EXPAND)
        self.ShowChildCont(True, animate)

    def OnCollapsed(self, treeData, animate = True):
        self._PersistIsExpandedSetting(False)
        if not self.data.HasChildren():
            return
        if not self.childrenInitialized:
            self.ConstructChildren()
        PlaySound(uiconst.SOUND_COLLAPSE)
        self.ShowChildCont(False, animate)

    def _PersistIsExpandedSetting(self, isExpanded):
        toggleSettingsName = 'invTreeViewEntryToggle_%s' % self.settingsID
        toggleSettingsDict = settings.user.ui.Get(toggleSettingsName, {})
        toggleSettingsDict[self.data.GetID()] = isExpanded
        settings.user.ui.Set(toggleSettingsName, toggleSettingsDict)

    def GetMenu(self):
        m = self.data.GetMenu()
        if session.role & ROLE_PROGRAMMER:
            idString = repr(self.data.GetID())
            m.append((u'GM: nodeID={}'.format(idString), blue.pyos.SetClipboardData, (idString,)))
        if self.data.IsRemovable():
            m.append(None)
            m.append((localization.GetByLabel('UI/Common/Buttons/Close'), self.Remove, ()))
        return m

    def GetTooltipPointer(self):
        return self.data.GetTooltipPointer()

    def GetHint(self):
        return self.data.GetHint()

    def GetFullPathLabelList(self):
        labelTuple = [self.data.GetLabel()]
        if self.parentEntry:
            labelTuple = self.parentEntry.GetFullPathLabelList() + labelTuple
        return labelTuple

    def Remove(self, *args):
        self.eventListener.RemoveTreeEntry(self, byUser=True)

    def OnMouseDown(self, *args):
        self.data.on_mouse_down(self.data)
        if self.eventListener and hasattr(self.eventListener, 'OnTreeViewMouseDown'):
            self.eventListener.OnTreeViewMouseDown(self, *args)

    def OnMouseUp(self, *args):
        self.data.on_mouse_up(self.data)
        if self.eventListener and hasattr(self.eventListener, 'OnTreeViewMouseUp'):
            self.eventListener.OnTreeViewMouseUp(self, *args)

    def CheckConstructHoverBG(self):
        if self.hoverBG is None:
            self.hoverBG = ListEntryUnderlay(bgParent=self.topRightCont)

    def CheckConstructSelectedBG(self):
        if self.selectedBG is None:
            self.selectedBG = FillThemeColored(bgParent=self.topRightCont, colorType=uiconst.COLORTYPE_UIHILIGHT, state=uiconst.UI_HIDDEN, opacity=0.5)

    def CheckConstructBlinkBG(self):
        if self.blinkBG is None:
            self.blinkBG = Fill(bgParent=self.topRightCont, color=(1.0, 1.0, 1.0, 0.0))

    def OnMouseEnter(self, *args):
        self.CheckConstructHoverBG()
        self.hoverBG.hovered = True
        PlaySound(uiconst.SOUND_ENTRY_HOVER)
        self.data.on_mouse_enter(self.data)
        if self.eventListener and hasattr(self.eventListener, 'OnTreeViewMouseEnter'):
            self.eventListener.OnTreeViewMouseEnter(self, *args)

    def OnMouseExit(self, *args):
        if self.hoverBG:
            self.hoverBG.hovered = False
        self.data.on_mouse_exit(self.data)
        if self.eventListener and hasattr(self.eventListener, 'OnTreeViewMouseExit'):
            self.eventListener.OnTreeViewMouseExit(self, *args)

    def OnDropData(self, *args):
        self.data.on_drop_data(self.data)
        if self.eventListener and hasattr(self.eventListener, 'OnTreeViewDropData'):
            self.eventListener.OnTreeViewDropData(self, *args)

    def OnDragEnter(self, dragObj, nodes):
        self.CheckConstructHoverBG()
        self.hoverBG.hovered = True
        self.data.on_drag_enter(self.data)
        if self.eventListener and hasattr(self.eventListener, 'OnTreeViewDragEnter'):
            self.eventListener.OnTreeViewDragEnter(self, dragObj, nodes)

    def GetDragData(self):
        if self.data.IsDraggable():
            self.eventListener.OnTreeViewGetDragData(self)
            return [self.data]

    def OnDragExit(self, *args):
        if self.hoverBG:
            self.hoverBG.hovered = False
        self.data.on_drag_exit(self.data)
        if self.eventListener and hasattr(self.eventListener, 'OnTreeViewDragExit'):
            self.eventListener.OnTreeViewDragExit(self, *args)

    def Blink(self):
        self.CheckConstructBlinkBG()
        uicore.animations.FadeTo(self.blinkBG, 0.0, 0.25, duration=0.25, curveType=uiconst.ANIM_WAVE, loops=2)

    @telemetry.ZONE_METHOD
    def SetAccessability(self, canAccess):
        self.canAccess = canAccess
        if self.icon:
            if canAccess:
                self.icon.color = TextColor.NORMAL
            else:
                self.icon.color = TextColor.DISABLED
        self.UpdateLabel()


class TreeViewEntryWithTag(TreeViewEntry):
    default_name = 'TreeViewEntryWithTag'
    __notifyevents__ = ['OnInventoryBadgingUpdated', 'OnInventoryBadgingDestroyed']
    TAG_SIZE = 8
    TAG_PADDING = 4
    TAG_COLOR = (0.97, 0.09, 0.13)
    TAG_TEXTURE_PATH = 'res:/UI/Texture/Shared/smallDot.png'

    def ApplyAttributes(self, attributes):
        onDividerMoved = attributes.get('onDividerMoved', None)
        if onDividerMoved is not None:
            onDividerMoved.connect(self.OnDividerMoved)
        self.shouldShowTag = False
        super(TreeViewEntryWithTag, self).ApplyAttributes(attributes)
        sm.RegisterNotify(self)

    def ConstructContent(self):
        super(TreeViewEntryWithTag, self).ConstructContent()
        self.ConstructTag()

    def ConstructTag(self):
        self.tagContainer = Container(name='tagContainer', parent=self.topRightCont, align=uiconst.TORIGHT, width=ButtonIndicator.default_width, padding=(self.TAG_PADDING,
         0,
         self.TAG_PADDING,
         0), state=uiconst.UI_HIDDEN)
        self.buttonIndicator = ButtonIndicator(parent=self.tagContainer, align=uiconst.CENTER)
        self.buttonIndicator.SetHighlightState(HighlightState.important)
        self.UpdateShouldShowTag()

    def UpdateShouldShowTag(self):
        self.shouldShowTag = sm.GetService('neocom').HasUnseenInventoryItemsInLocation(self.data.invType)
        self.UpdateTagState()

    def UpdateTagState(self):
        self.tagContainer.state = uiconst.UI_DISABLED if self.shouldShowTag else uiconst.UI_HIDDEN
        self.UpdateLabelWidth()

    def ClearTag(self):
        self.tagContainer.state = uiconst.UI_HIDDEN
        self.UpdateLabelWidth()

    def UpdateLabelWidth(self):
        entryWidth, _ = self.GetAbsoluteSize()
        tagWidth = self.TAG_SIZE + 2 * self.TAG_PADDING if self.tagContainer.display else 0
        clipWidth = entryWidth - self.label.left - tagWidth
        if clipWidth > 0 and self.label.textwidth > clipWidth:
            self.label.clipWidth = clipWidth
        else:
            self.label.clipWidth = self.label.textwidth

    def OnDividerMoved(self):
        self.UpdateLabelWidth()

    def OnInventoryBadgingUpdated(self):
        self.UpdateShouldShowTag()

    def OnInventoryBadgingDestroyed(self):
        self.UpdateShouldShowTag()


class TreeViewEntryHeader(TreeViewEntry):
    default_height = 48
    LABEL_PADDING = 8

    def ConstructLabel(self):
        self.label = carbonui.TextHeader(parent=self.topRightCont, align=uiconst.CENTERLEFT, text=self.data.GetLabel(), autoFadeSides=16)

    def GetIconSize(self):
        return 32


class TreeViewEntryShip(TreeViewEntry):
    default_height = 32

    def ConstructIcon(self, left):
        iconSize = self.GetIconSize()
        self.icon = ItemIcon(parent=self.topRightCont, pos=(left,
         0,
         iconSize,
         iconSize), align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED, typeID=self.data.GetID())
        return left + iconSize + 2

    def GetMenu(self):
        m = super(TreeViewEntryShip, self).GetMenu()
        return m + GetMenuService().GetMenuFromItemIDTypeID(itemID=None, typeID=self.data.GetID(), includeMarketDetails=True)

    def OnMouseEnter(self, *args):
        super(TreeViewEntryShip, self).OnMouseEnter(*args)
        self.icon.OnMouseEnter(*args)

    def OnMouseExit(self, *args):
        super(TreeViewEntryShip, self).OnMouseExit(*args)
        self.icon.OnMouseExit(*args)

    def GetDragData(self):
        return [TypeDragData(self.data.GetID())]
