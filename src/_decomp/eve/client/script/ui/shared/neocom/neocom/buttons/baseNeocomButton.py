#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\neocom\buttons\baseNeocomButton.py
import math
import blue
import trinity
import uthread
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui import const as uiconst, fontconst
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.primitives.frame import Frame
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.transform import Transform
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from carbonui.util.color import Color
from eve.client.script.ui import eveColor, eveThemeColor
from eve.client.script.ui.control.glowSprite import GlowSprite
from eve.client.script.ui.control.themeColored import FrameThemeColored, SpriteThemeColored
from eve.client.script.ui.shared.neocom.neocom import neocomConst, highlightState
from eve.client.script.ui.shared.neocom.neocom import neocomTooltips, neocomPanels
from eve.client.script.ui.shared.neocom.neocom.badge import Badge
from eve.client.script.ui.shared.neocom.neocom.buttons.buttonIndicator import ButtonIndicator
from eve.client.script.ui.shared.neocom.neocom.buttons.neocomButtonConst import GLOW_IDLE, GLOW_HOVER, GLOW_MOUSEDOWN, COLOR_IDLE, COLOR_HOVER
from eve.client.script.ui.tooltips.tooltipUtil import RefreshTooltipForOwner
from signals import Signal
BADGE_COLOR_UNSEEN = eveColor.PRIMARY_BLUE[:3]

class BaseNeocomButton(Container):
    default_state = uiconst.UI_NORMAL
    default_align = uiconst.TOPLEFT
    default_isDraggable = True
    default_badgeMaxValue = 7
    default_adjustPositionManually = True

    def ApplyAttributes(self, attributes):
        super(BaseNeocomButton, self).ApplyAttributes(attributes)
        self.btnData = attributes.btnData
        self._isDraggable = attributes.get('isDraggable', self.default_isDraggable)
        self._badgeMaxValue = attributes.get('badgeMaxValue', self.default_badgeMaxValue)
        self._openNeocomPanel = None
        self.isDragging = False
        self.uniqueUiName = attributes.uniqueUiName or getattr(self.btnData, 'uniqueUiName', None)
        self._adjustPositionManually = attributes.get('adjustPositionManually', self.default_adjustPositionManually)
        self.iconLabelCont = None
        self.panel = None
        self.blinkThread = None
        self.realTop = self.top
        self.dragEventCookie = None
        self.disableClick = False
        self.onButtonDragEnter = Signal()
        self.onButtonDragEnd = Signal()
        self.onButtonDragged = Signal()
        self.btnData.on_highlight_state_changed.connect(self.OnHighlightStateChanged)
        self.btnData.on_has_new_activity_changed.connect(self.OnHasNewActivityChanged)
        self.btnData.on_blink.connect(self.OnBlink)
        self.ConstructButtonIndicator()
        self.ConstructIcon()
        self.ConstructBlinkSprite()
        self.ConstructNevActivityFill()
        self.SetCorrectPosition()
        self.dropFrame = Frame(parent=self, name='hoverFrame', color=Color.GetGrayRGBA(1.0, 0.5), state=uiconst.UI_HIDDEN)
        self.UpdateNewActivityState(animate=False)
        self.UpdateHighlightState(animate=False)
        self._UpdateCounter(animate=False)
        self.btnData.on_badge_count_changed.connect(self.OnBadgeCountChanged)

    def OnHasNewActivityChanged(self):
        self.UpdateNewActivityState()

    def UpdateNewActivityState(self, animate = True):
        opacity = 0.3 if self.btnData.hasNewActivity else 0.0
        if animate:
            animations.FadeTo(self.newActivityFill, self.newActivityFill.opacity, opacity, duration=0.6)
        else:
            self.newActivityFill.opacity = opacity

    def OnHighlightStateChanged(self):
        self.UpdateHighlightState()

    def OnBadgeCountChanged(self):
        self._UpdateCounter()

    def _UpdateCounter(self, animate = True):
        self.buttonIndicator.SetCounterValue(self.btnData.GetItemCount(), animate)

    def ConstructButtonIndicator(self):
        self.buttonIndicator = ButtonIndicator(parent=self, align=uiconst.CENTERRIGHT)

    def GetBadgeMaxValue(self):
        return self._badgeMaxValue

    def GetXPosition(self):
        buttons = self.btnData.parent.GetChildrenInScope()
        index = buttons.index(self.btnData)
        return self.height * index

    def SetCorrectPosition(self):
        if self._adjustPositionManually:
            self.top = self.GetXPosition()

    def UpdateIcon(self):
        texturePath = self._GetTexturePath()
        self.SetTexturePath(texturePath)

    def _GetTexturePath(self):
        return self.btnData.iconPath

    def UpdateHighlightState(self, animate = True):
        self.UpdateIcon()
        self.UpdateIconColor(duration=0.6 if animate else None)
        self.blinkSprite.rgba = highlightState.GetPrimaryColor(self.btnData.highlightState)
        self.buttonIndicator.SetHighlightState(self.btnData.highlightState, animate)

    def GetIconPath(self):
        return self.btnData.iconPath

    def IsDraggable(self):
        return self._isDraggable

    def SetDraggable(self, isDraggable):
        self._isDraggable = isDraggable

    def GetMenu(self):
        return self.btnData.GetMenu()

    def LoadTooltipPanel(self, tooltipPanel, *args):
        isOpen = self._openNeocomPanel and not self._openNeocomPanel.destroyed
        if isOpen:
            return
        tooltipPanel.LoadGeneric3ColumnTemplate()
        if getattr(self.btnData, 'cmdName', None):
            cmd = uicore.cmd.commandMap.GetCommandByName(self.btnData.cmdName)
            tooltipPanel.AddCommandTooltip(cmd)
        else:
            label = None
            if self.IsSingleWindow():
                wnd = self.GetWindow()
                if not wnd.destroyed:
                    label = wnd.GetCaption()
            elif self.btnData.children:
                label = self.btnData.children[0].wnd.GetNeocomGroupLabel()
            mainStr = label or self.btnData.label
            tooltipPanel.AddLabelMedium(text=mainStr)
        self.LoadTooltipPanelDetails(tooltipPanel, self.btnData)
        blinkHint = self.btnData.GetBlinkHint()
        if blinkHint:
            tooltipPanel.AddLabelMedium(text=blinkHint, width=200, colSpan=tooltipPanel.columns, color=eveThemeColor.THEME_ALERT)

    def LoadTooltipPanelDetails(cls, tooltipPanel, btnData):
        neocomTooltips.LoadTooltipPanel(tooltipPanel, btnData)

    def IsSingleWindow(self):
        return False

    def ConstructNevActivityFill(self):
        self.newActivityFill = Fill(name='newActivityFill', bgParent=self, color=eveThemeColor.THEME_ALERT, opacity=0.0, padding=(1, 1, 0, 0))

    def ConstructIcon(self):
        self.icon = Sprite(parent=self, name='icon', state=uiconst.UI_DISABLED, align=uiconst.TOALL, outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, glowBrightness=GLOW_IDLE, blendMode=trinity.TR2_SBM_ADD, color=COLOR_IDLE, padding=4)

    def ConstructBlinkSprite(self):
        self.blinkSprite = Sprite(bgParent=self, name='blinkSprite', state=uiconst.UI_HIDDEN, texturePath=self.icon.texturePath, outputMode=uiconst.OUTPUT_GLOW, blendMode=trinity.TR2_SBM_ADD)

    def ConstructActiveFrame(self):
        self.activeFrame = FrameThemeColored(bgParent=self, name='hoverFill', texturePath='res:/UI/Texture/classes/Neocom/buttonActive.png', cornerSize=5, state=uiconst.UI_HIDDEN, colorType=uiconst.COLORTYPE_UIHILIGHTGLOW)

    def SetTexturePath(self, texturePath):
        self.icon.SetTexturePath(texturePath)
        self.blinkSprite.SetTexturePath(texturePath)

    def OnMouseEnter(self, *args):
        PlaySound(uiconst.SOUND_BUTTON_HOVER)
        self._AnimMouseEnter()
        self.UpdateIconColor(uiconst.TIME_ENTRY)
        self.btnData.SetHasNewActivityOff()
        self.btnData.SetBlinkingOff()

    def _AnimMouseEnter(self):
        animations.MorphScalar(self.icon, 'glowBrightness', self.icon.glowBrightness, GLOW_HOVER, duration=uiconst.TIME_ENTRY)

    def OnMouseExit(self, *args):
        self._AnimMouseExit()
        self.UpdateIconColor(uiconst.TIME_EXIT)
        self.btnData.ClearBlinkHint()

    def _AnimMouseExit(self):
        animations.MorphScalar(self.icon, 'glowBrightness', self.icon.glowBrightness, GLOW_IDLE, duration=uiconst.TIME_EXIT)

    def OnMouseDown(self, button):
        if button != uiconst.MOUSELEFT:
            return
        self._AnimMouseDown()
        if self.IsDraggable():
            self.isDragging = False
            self.mouseDownY = uicore.uilib.y
            if self.dragEventCookie is not None:
                uicore.event.UnregisterForTriuiEvents(self.dragEventCookie)
            self.dragEventCookie = uicore.event.RegisterForTriuiEvents(uiconst.UI_MOUSEMOVE, self.OnDrag)

    def _AnimMouseDown(self):
        animations.MorphScalar(self.icon, 'glowBrightness', self.icon.glowBrightness, GLOW_MOUSEDOWN, duration=uiconst.TIME_MOUSEDOWN)

    def OnMouseUp(self, button):
        if button != uiconst.MOUSELEFT:
            return
        self._AnimMouseUp()
        if self.dragEventCookie is not None:
            uicore.event.UnregisterForTriuiEvents(self.dragEventCookie)
            self.dragEventCookie = None

    def _AnimMouseUp(self):
        animations.MorphScalar(self.icon, 'glowBrightness', self.icon.glowBrightness, GLOW_HOVER, duration=uiconst.TIME_MOUSEUP)

    def UpdateIconColor(self, duration = None):
        color = self.GetIconColor()
        if duration:
            animations.SpColorMorphTo(self.icon, self.icon.rgba, color, duration=duration)
        else:
            self.icon.rgba = color

    def GetIconColor(self):
        if uicore.uilib.mouseOver == self:
            return COLOR_HOVER
        else:
            return COLOR_IDLE

    def OnColorThemeChanged(self):
        super(BaseNeocomButton, self).OnColorThemeChanged()
        self.newActivityFill.rgba = eveThemeColor.THEME_ALERT
        self.UpdateNewActivityState(animate=False)
        self.UpdateHighlightState(animate=False)

    def BlinkOnMinimize(self):
        self.blinkSprite.state = uiconst.UI_DISABLED
        uicore.animations.MorphScalar(self.blinkSprite, 'glowBrightness', 2.0, 0.0, duration=0.8, curveType=uiconst.ANIM_SMOOTH)
        uicore.animations.MorphScalar(self.icon, 'glowBrightness', 1.0, 0.0, duration=0.6, curveType=uiconst.ANIM_SMOOTH)

    def BlinkOnce(self):
        self.blinkSprite.state = uiconst.UI_DISABLED
        uicore.animations.MorphScalar(self.blinkSprite, 'glowBrightness', 0.0, 1.0, duration=neocomConst.BLINK_INTERVAL, curveType=uiconst.ANIM_WAVE)
        uicore.animations.MorphScalar(self.icon, 'glowBrightness', 0.0, 2.0, duration=neocomConst.BLINK_INTERVAL, curveType=uiconst.ANIM_WAVE, timeOffset=0.1)

    def GetTooltipPointer(self):
        return uiconst.POINT_LEFT_2

    def OnDragEnd(self, *args):
        uicore.event.UnregisterForTriuiEvents(self.dragEventCookie)
        self.dragEventCookie = None
        self.isDragging = False
        self.onButtonDragEnd(self)
        self.UpdateHighlightState()

    def OnDrag(self, *args):
        if math.fabs(self.mouseDownY - uicore.uilib.y) > 5 or self.isDragging:
            if not self.isDragging:
                uicore.event.RegisterForTriuiEvents(uiconst.UI_MOUSEUP, self.OnDragEnd)
            self.disableClick = True
            self.isDragging = True
            self.onButtonDragged(self)
        return True

    def OnClick(self, *args):
        self.btnData.CheckContinueBlinking()
        if not self.disableClick:
            PlaySound(uiconst.SOUND_BUTTON_CLICK)
            self.OnClickCommand()
        self.disableClick = False
        if self.dragEventCookie:
            uicore.event.UnregisterForTriuiEvents(self.dragEventCookie)

    def OnDblClick(self, *args):
        pass

    def OnClickCommand(self):
        if hasattr(self.btnData, 'cmdName'):
            uicore.cmd.GetCommandAndExecute(self.btnData.cmdName)

    def OnSwitched(self):
        self.SetCorrectPosition()
        self.isDragging = False
        self.disableClick = False

    def GetDragData(self, *args):
        if self.btnData.isDraggable:
            return [self.btnData]

    def OnBlink(self):
        self.BlinkOnce()

    def OnDropData(self, source, dropData):
        if not sm.GetService('neocom').IsValidDropData(dropData):
            return
        index = self.btnData.parent.children.index(self.btnData)
        sm.GetService('neocom').OnBtnDataDropped(dropData[0], index)

    def OnDragEnter(self, panelEntry, dropData):
        if not sm.GetService('neocom').IsValidDropData(dropData):
            return
        self.onButtonDragEnter(self.btnData, dropData[0])
        uthread.new(self.ShowPanelOnMouseHoverThread)

    def OnDragExit(self, *args):
        sm.GetService('neocom').OnButtonDragExit(self.btnData, args)

    def ToggleNeocomPanel(self):
        isOpen = self._openNeocomPanel and not self._openNeocomPanel.destroyed
        sm.GetService('neocom').CloseAllPanels()
        if isOpen:
            self._openNeocomPanel = None
        else:
            self._openNeocomPanel = sm.GetService('neocom').ShowPanel(triggerCont=self, panelClass=self.GetPanelClass(), panelAlign=neocomConst.PANEL_SHOWONSIDE, parent=uicore.layer.abovemain, btnData=self.btnData)
        RefreshTooltipForOwner(self)

    def ShowPanelOnMouseHoverThread(self):
        if len(self.btnData.children) <= 1:
            return
        blue.pyos.synchro.Sleep(500)
        if not self or self.destroyed:
            return
        if uicore.uilib.mouseOver == self:
            self.ToggleNeocomPanel()

    def GetPanelClass(self):
        return neocomPanels.PanelGroup
