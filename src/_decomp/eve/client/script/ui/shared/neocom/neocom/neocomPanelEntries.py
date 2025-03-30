#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\neocom\neocomPanelEntries.py
import carbonui.const as uiconst
import eve.client.script.ui.shared.pointerTool.pointerToolConst as pConst
import eveicon
import trinity
import uthread
import uthread2
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui import TextColor
from carbonui.control.contextMenu.menuEntryUnderlay import MenuEntryUnderlay
from carbonui.control.contextMenu.menuUtil import FlashEntrySelection
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.primitives.frame import Frame
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from eve.client.script.ui import eveColor, eveThemeColor
from eve.client.script.ui.control import eveIcon, eveLabel
from eve.client.script.ui.control.themeColored import SpriteThemeColored
from eve.client.script.ui.shared.neocom.neocom import neocomConst, neocomTooltips, neocomSettings
from eve.client.script.ui.shared.neocom.neocom.buttons import neocomButtonConst
from eve.client.script.ui.shared.neocom.neocom.buttons.buttonIndicator import ButtonIndicator
from eve.client.script.ui.shared.neocom.neocom.neocomConst import BLINK_INTERVAL
from localization import GetByLabel
COLOR_ICON = eveColor.SILVER_GREY

class PanelEntryBase(Container):
    isDragObject = True
    default_state = uiconst.UI_NORMAL
    default_align = uiconst.TOTOP
    default_icon = None
    default_height = 48
    sound_hover = uiconst.SOUND_BUTTON_HOVER

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.btnData = attributes.btnData
        if hasattr(self.btnData, 'panelEntryHeight'):
            self.height = self.btnData.panelEntryHeight
        self.blinkThread = None
        self._openNeocomPanel = None
        self.func = None
        self.btnData.on_highlight_state_changed.connect(self.UpdateHighlightState)
        self.btnData.on_has_new_activity_changed.connect(self.UpdateHighlightState)
        self.main = Container(parent=self, name='main')
        self.underlay = MenuEntryUnderlay(bgParent=self.main)
        iconSize = self.GetIconSize()
        self.icon = Sprite(parent=self.main, name='icon', state=uiconst.UI_DISABLED, texturePath=self.GetIconPath(), pos=(8,
         0,
         iconSize,
         iconSize), align=uiconst.CENTERLEFT, color=COLOR_ICON, outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, glowBrightness=0.0, blendMode=trinity.TR2_SBM_ADD)
        self.label = eveLabel.EveLabelMedium(parent=self.main, align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED, text=self.GetLabel(), left=self.icon.left + self.icon.width + 12, color=eveColor.TUNGSTEN_GREY)
        self.newActivityFill = Fill(name='newActivityFill', bgParent=self, color=eveColor.DUSKY_ORANGE, opacity=0.0, padBottom=1)
        self.buttonIndicator = ButtonIndicator(parent=self, align=uiconst.CENTERRIGHT)
        self.UpdateHighlightState()
        icon = eveicon.caret_right if neocomSettings.neocom_align_setting.is_equal(uiconst.TOLEFT) else eveicon.caret_left
        self.expanderIcon = Sprite(parent=self, name='expanderIcon', align=uiconst.CENTERRIGHT, pos=(16, 0, 16, 16), texturePath=icon, color=COLOR_ICON)
        self.SetExpanderState()
        self.blinkSprite = SpriteThemeColored(bgParent=self, name='blinkSprite', texturePath='res:/UI/Texture/classes/Neocom/panelEntryBG.png', colorType=uiconst.COLORTYPE_UIHILIGHT, state=uiconst.UI_HIDDEN, opacity=0.0)

    def UpdateHighlightState(self):
        self.buttonIndicator.SetHighlightState(self.btnData.highlightState)
        self.newActivityFill.opacity = 0.4 if self.btnData.HasNewActivity() else 0.0

    def GetIconSize(self):
        return 32

    def AddBetaTag(self):
        SpriteThemeColored(parent=self.main, align=uiconst.TOPLEFT, pos=(10, 2, 11, 29), texturePath='res:/UI/Texture/Shared/betaTag.png', state=uiconst.UI_DISABLED, colorType=uiconst.COLORTYPE_UIHILIGHTGLOW)

    def GetIconPath(self):
        return self.btnData.iconPath or neocomConst.ICONPATH_DEFAULT

    def PrepareDrag(self, dragContainer, dragSource):
        dragContainer.width = dragContainer.height = 48
        eveIcon.Icon(parent=dragContainer, name='icon', state=uiconst.UI_DISABLED, icon=self.GetIconPath(), size=48, ignoreSize=True)
        Frame(parent=dragContainer, offset=-9, cornerSize=13, name='shadow', state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/Shared/bigButtonShadow.png')
        return (0, 0)

    def HasOpenPanel(self):
        return self._openNeocomPanel is not None and not self._openNeocomPanel.destroyed

    def SetExpanderState(self):
        self.HideExpander()

    def ShowExpander(self):
        self.expanderIcon.state = uiconst.UI_DISABLED

    def HideExpander(self):
        self.expanderIcon.state = uiconst.UI_HIDDEN

    def OnClick(self, *args):
        pos = self.GetAbsolute()
        FlashEntrySelection(pos)
        sm.GetService('neocom').CloseAllPanels()
        self.btnData.SetHasNewActivityOff()
        self.btnData.ClearBlinkHint()
        self.btnData.SetBlinkingOff()
        uthread2.start_tasklet(self.OnClickCommand)

    def OnClickCommand(self):
        pass

    def GetLabel(self):
        label = None
        if self.btnData.cmdName:
            cmd = uicore.cmd.commandMap.GetCommandByName(self.btnData.cmdName)
            if cmd and cmd.callback:
                label = cmd.GetName()
        return label or self.btnData.label

    def GetRequiredWidth(self):
        return self.label.width + self.label.left + self.expanderIcon.left + self.expanderIcon.width

    def GetMenu(self):
        m = self.btnData.GetMenu() or []
        m.append((GetByLabel('UI/Neocom/AddShortcut'), sm.GetService('neocom').AddButtonToRoot, (self.btnData,)))
        return m

    def LoadTooltipPanel(self, tooltipPanel, *args):
        tooltipPanel.LoadGeneric3ColumnTemplate()
        if getattr(self.btnData, 'cmdName', None):
            cmd = uicore.cmd.commandMap.GetCommandByName(self.btnData.cmdName)
            tooltipPanel.AddCommandTooltip(cmd)
            neocomTooltips.LoadTooltipPanel(tooltipPanel, self.btnData)
        blinkHint = self.btnData.GetBlinkHint()
        if blinkHint:
            tooltipPanel.AddLabelMedium(text=blinkHint, width=200, colSpan=tooltipPanel.columns, color=eveThemeColor.THEME_ALERT)

    def GetTooltipPointer(self):
        return uiconst.POINT_LEFT_2

    def OnMouseEnter(self, *args):
        PlaySound(self.sound_hover)
        sm.GetService('neocom').CloseChildrenPanels(self.btnData.parent)
        self.underlay.OnMouseEnter()
        animations.MorphScalar(self.icon, 'glowBrightness', self.icon.glowBrightness, neocomButtonConst.GLOW_HOVER, duration=uiconst.TIME_ENTRY)
        animations.SpColorMorphTo(self.icon, self.icon.rgba, eveColor.WHITE, duration=uiconst.TIME_ENTRY)
        animations.SpColorMorphTo(self.label, self.label.rgba, eveColor.WHITE, duration=uiconst.TIME_ENTRY)

    def OnMouseExit(self, *args):
        self.btnData.SetBlinkingOff()
        self.underlay.OnMouseExit()
        self._ResetColor()
        animations.MorphScalar(self.icon, 'glowBrightness', self.icon.glowBrightness, 0.0, duration=uiconst.TIME_EXIT)
        animations.SpColorMorphTo(self.icon, self.icon.rgba, COLOR_ICON, duration=uiconst.TIME_EXIT)
        animations.SpColorMorphTo(self.label, self.label.rgba, eveColor.TUNGSTEN_GREY, duration=uiconst.TIME_EXIT)
        self.btnData.SetHasNewActivityOff()
        self.btnData.ClearBlinkHint()
        self.btnData.SetBlinkingOff()
        self.UpdateHighlightState()

    def OnMouseDown(self, btn):
        if not self.func or btn != uiconst.MOUSELEFT:
            return
        self.underlay.OnMouseDown()
        animations.SpColorMorphTo(self.label, self.label.GetRGBA(), eveColor.BLACK, duration=uiconst.TIME_MOUSEDOWN)
        self.icon.blendMode = trinity.TR2_SBM_BLEND
        animations.SpColorMorphTo(self.icon, self.icon.GetRGBA(), eveColor.BLACK, duration=uiconst.TIME_MOUSEDOWN)
        animations.SpColorMorphTo(self.expanderIcon, self.expanderIcon.GetRGBA(), eveColor.BLACK, duration=uiconst.TIME_MOUSEDOWN)

    def OnMouseUp(self, btn):
        if not self.func or btn != uiconst.MOUSELEFT:
            return
        self._ResetColor()

    def _ResetColor(self):
        self.underlay.OnMouseUp()
        self.icon.blendMode = trinity.TR2_SBM_ADD
        animations.SpColorMorphTo(self.label, self.label.GetRGBA(), TextColor.HIGHLIGHT, duration=uiconst.TIME_MOUSEUP)
        animations.SpColorMorphTo(self.icon, self.icon.GetRGBA(), COLOR_ICON, duration=uiconst.TIME_MOUSEUP)
        animations.SpColorMorphTo(self.expanderIcon, self.expanderIcon.GetRGBA(), COLOR_ICON, duration=uiconst.TIME_MOUSEUP)

    def GetDragData(self, *args):
        if self.btnData.isDraggable:
            return [self.btnData]

    def BlinkOnce(self):
        self.blinkSprite.Show()
        uicore.animations.FadeTo(self.blinkSprite, 0.0, 1.5, duration=BLINK_INTERVAL, curveType=uiconst.ANIM_WAVE)
        uicore.animations.MorphScalar(self.icon, 'glowAmount', 0.0, 1.5, duration=BLINK_INTERVAL, curveType=uiconst.ANIM_WAVE)


class PanelEntryCmd(PanelEntryBase):
    default_name = 'PanelEntryCmd'

    def ApplyAttributes(self, attributes):
        PanelEntryBase.ApplyAttributes(self, attributes)
        self.func = attributes.func
        btnData = attributes.btnData
        if btnData and getattr(btnData, 'uniqueUiName', None):
            self.uniqueUiName = pConst.GetUniquePanelPointerName(btnData.uniqueUiName)

    def OnClickCommand(self, *args):
        self.func()
        PlaySound(uiconst.SOUND_BUTTON_CLICK)


class PanelEntryBookmarks(PanelEntryBase):
    default_name = 'PanelEntryBookmarks'

    def OnClick(self, *args):
        if not self.HasOpenPanel():
            self.ToggleNeocomPanel()

    def ToggleNeocomPanel(self):
        from .neocomPanels import PanelGroup
        sm.GetService('neocom').CloseChildrenPanels(self.btnData.parent)
        if self.HasOpenPanel():
            self._openNeocomPanel = None
        else:
            PlaySound(uiconst.SOUND_EXPAND)
            self._openNeocomPanel = sm.GetService('neocom').ShowPanel(self, PanelGroup, neocomConst.PANEL_SHOWONSIDE, parent=uicore.layer.abovemain, btnData=self.btnData)

    def OnMouseEnter(self, *args):
        PanelEntryBase.OnMouseEnter(self, *args)
        if uicore.uilib.mouseOver == self and not self.HasOpenPanel():
            uthread.new(self.ToggleNeocomPanel)

    def SetExpanderState(self):
        self.ShowExpander()


class PanelEntryBookmark(PanelEntryBase):
    default_name = 'PanelEntryBookmark'
    default_height = 25

    def ApplyAttributes(self, attributes):
        self.bookmark = attributes.btnData.bookmark
        PanelEntryBase.ApplyAttributes(self, attributes)

    def OnClickCommand(self, *args):
        PlaySound(uiconst.SOUND_BUTTON_CLICK)
        uicore.cmd.OpenBrowser(url=self.bookmark.url, newTab=True)

    def GetLabel(self):
        return self.bookmark.name


class PanelEntryText(Container):
    default_name = 'PanelEntryText'
    default_height = 42
    default_align = uiconst.TOTOP

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        label = attributes.label
        self.label = eveLabel.Label(parent=self, state=uiconst.UI_DISABLED, text=label, align=uiconst.CENTERLEFT, left=10)

    def GetRequiredWidth(self):
        return self.label.width + 35


class PanelEntryGroup(PanelEntryBase):
    default_name = 'PanelEntryGroup'
    default_icon = neocomConst.ICONPATH_GROUP
    sound_hover = uiconst.SOUND_EXPAND

    def ApplyAttributes(self, attributes):
        PanelEntryBase.ApplyAttributes(self, attributes)
        if self.btnData.labelAbbrev:
            self.labelAbbrev = eveLabel.Label(parent=self.main, align=uiconst.BOTTOMLEFT, text=self.btnData.labelAbbrev, colorType=uiconst.COLORTYPE_UIHILIGHTGLOW, fontsize=13, opacity=1.0, letterspace=-1, idx=0, bold=True, left=self.height / 2, top=6)

    def OnClick(self, *args):
        if not self.HasOpenPanel():
            self.ToggleNeocomPanel()

    def OnMouseEnter(self, *args):
        PanelEntryBase.OnMouseEnter(self, *args)
        if uicore.uilib.mouseOver == self and not self.HasOpenPanel():
            uthread.new(self.ToggleNeocomPanel)

    def OnDropData(self, source, dropData):
        if not sm.GetService('neocom').IsValidDropData(dropData):
            return
        btnData = dropData[0]
        if btnData.btnType not in neocomConst.FIXED_PARENT_BTNTYPES:
            btnData.MoveTo(self.btnData)

    def ToggleNeocomPanel(self):
        from .neocomPanels import PanelGroup
        if self.HasOpenPanel():
            self._openNeocomPanel = None
            sm.GetService('neocom').CloseChildrenPanels(self.btnData.parent)
        else:
            sm.GetService('neocom').CloseChildrenPanels(self.btnData.parent)
            self._openNeocomPanel = sm.GetService('neocom').ShowPanel(self, PanelGroup, neocomConst.PANEL_SHOWONSIDE, parent=uicore.layer.abovemain, btnData=self.btnData, align=uiconst.TOPLEFT)

    def SetExpanderState(self):
        self.ShowExpander()


class PanelEntryWindow(PanelEntryBase):
    default_name = 'PanelEntryWindow'

    def GetLabel(self):
        if self.IsSingleWindow():
            wnd = self.GetWindow()
            if wnd and not wnd.destroyed:
                return wnd.GetCaption()
        if self.btnData.label:
            return self.btnData.label
        if self.btnData.cmdName:
            cmd = uicore.cmd.commandMap.GetCommandByName(self.btnData.cmdName)
            if cmd:
                return cmd.GetName()
        if self.btnData.children:
            return self.btnData.children[0].wnd.GetNeocomGroupLabel()

    def GetWindow(self):
        if hasattr(self.btnData, 'wnd'):
            return self.btnData.wnd
        if self.btnData.children:
            btnData = self.btnData.children[0]
            return btnData.wnd

    def GetIconPath(self):
        wnd = self.GetWindow()
        if wnd and self.IsSingleWindow():
            return wnd.iconNum
        if len(self.btnData.children) > 1:
            return self.btnData.children[0].wnd.GetNeocomGroupIcon()
        return PanelEntryBase.GetIconPath(self)

    def IsSingleWindow(self):
        return hasattr(self.btnData, 'wnd') or len(self.btnData.children) == 1

    def OnClick(self, *args):
        if hasattr(self.btnData, 'wnd'):
            self.btnData.wnd.ToggleMinimize()
        elif len(self.btnData.children) <= 1:
            self.btnData.children[0].wnd.ToggleMinimize()
        else:
            if self.btnData.children:
                self.ToggleNeocomPanel()
                return
            if hasattr(self.btnData, 'cmdName'):
                uicore.cmd.GetCommandAndExecute(self.btnData.cmdName)
        sm.GetService('neocom').CloseAllPanels()

    def ToggleNeocomPanel(self):
        from .neocomPanels import PanelGroup
        if self.HasOpenPanel():
            sm.GetService('neocom').ClosePanel(self._openNeocomPanel)
            self._openNeocomPanel = None
        else:
            self._openNeocomPanel = sm.GetService('neocom').ShowPanel(triggerCont=self, panelClass=PanelGroup, panelAlign=neocomConst.PANEL_SHOWONSIDE, parent=uicore.layer.abovemain, btnData=self.btnData)

    def OnDragEnter(self, panelEntry, nodes):
        self.OnMouseEnter()

    def OnDragExit(self, *args):
        self.OnMouseExit()

    def OnDropData(self, source, nodes):
        wnd = getattr(self.btnData, 'wnd', None)
        if wnd and hasattr(wnd, 'OnDropData'):
            wnd.OnDropData(source, nodes)
            sm.GetService('neocom').CloseAllPanels()

    def SetExpanderState(self):
        if len(self.btnData.children) > 1:
            self.ShowExpander()
        else:
            self.HideExpander()

    def GetMenu(self):
        return None


class PanelChatChannel(PanelEntryWindow):
    default_name = 'PanelEntryChatChannel'
    default_height = 28

    def GetIconPath(self):
        return eveicon.chat_bubble

    def GetIconSize(self):
        return 16
