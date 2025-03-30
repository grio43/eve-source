#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\control\tab.py
import math
import telemetry
import trinity
import uthread
import uthread2
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui import uiconst, fontconst
from carbonui.primitives.container import Container
from carbonui.primitives.dragdrop import DragDropObject
from carbonui.primitives.fill import Fill
from carbonui.text.color import TextColor
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from carbonui.util.various_unsorted import GetWindowAbove
from eve.client.script.ui import eveThemeColor
from eve.client.script.ui.control import eveLabel
from eve.client.script.ui.control.eveIcon import Icon
from eveexceptions import UserError, EatsExceptions
from logmodule import LogException
from carbonui.loggers.message_bus.tabMessenger import TabMessenger
OPACITY_DEFAULT = 1.0
OPACITY_DISABLED = 0.35
OPACITY_SELECTED = 1.0

class Tab(Container):
    default_enabled = True
    default_fontsize = fontconst.EVE_MEDIUM_FONTSIZE
    default_fontStyle = None
    default_fontFamily = None
    default_fontPath = None
    default_labelPadding = 0
    selectedBG = None

    @telemetry.ZONE_METHOD
    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.enabled = attributes.get('enabled', self.default_enabled)
        self.fontStyle = attributes.get('fontStyle', self.default_fontStyle)
        self.fontFamily = attributes.get('fontFamily', self.default_fontFamily)
        self.fontPath = attributes.get('fontPath', self.default_fontPath)
        self.fontsize = attributes.get('fontsize', self.default_fontsize)
        self.labelPadding = attributes.get('labelPadding', self.default_labelPadding)
        self.tabID = None
        self.selecting = 0
        self.icon = None
        self.headerIconCont = None
        self.sr.LoadTabCallback = None
        self.isTabStop = True
        self._activity_indicator = None
        self._hovered = False
        self._gap_left = 0
        self._gap_right = 0
        self._detachallowed = False
        self.ConstructLayout()
        self.isTabStop = False

    @property
    def gap_left(self):
        return self._gap_left

    @gap_left.setter
    def gap_left(self, value):
        if self._gap_left != value:
            self._gap_left = value
            self._update_activity_indicator_padding()

    @property
    def gap_right(self):
        return self._gap_right

    @gap_right.setter
    def gap_right(self, value):
        if self._gap_right != value:
            self._gap_right = value
            self._update_activity_indicator_padding()

    def _update_activity_indicator_padding(self):
        self._activity_indicator.padding = self._get_activity_indicator_padding()

    def _get_activity_indicator_padding(self):
        pad_left = int(math.floor(max(self._gap_left - 1, 0) / 2.0))
        pad_right = int(math.ceil(max(self._gap_right - 1, 0) / 2.0))
        return (-pad_left,
         0,
         -pad_right,
         0)

    def GetHeight(self):
        if self.icon:
            return self.icon.height
        return self.label.textheight

    @telemetry.ZONE_METHOD
    def ConstructLayout(self):
        self._ConstructClipper()
        self._ConstructLabel()
        self._ConstructActivityIndicator()
        self._ConstructUnderlay()

    def _ConstructActivityIndicator(self):
        self._activity_indicator = ActivityIndicator(parent=self, align=uiconst.TOALL, padding=self._get_activity_indicator_padding())

    def _ConstructClipper(self):
        self.clipper = Container(name='labelClipper', parent=self, align=uiconst.TOALL, clipChildren=True, state=uiconst.UI_PICKCHILDREN)

    def _ConstructLabel(self):
        self.label = eveLabel.EveLabelMedium(parent=self.clipper, align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED, autoFadeSides=8, outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, glowBrightness=0.0, offer_auxiliary_copy_option=False)

    def _ConstructUnderlay(self):
        pass

    @telemetry.ZONE_METHOD
    def Startup(self, tabgroup, data):
        from carbonui.primitives.stretchspritehorizontal import StretchSpriteHorizontal
        self.blinkDrop = StretchSpriteHorizontal(parent=self, align=uiconst.TOTOP_NOPUSH, color=(0.5, 0.5, 0.5, 0.0), name='blinkDrop', height=11, leftEdgeSize=6, rightEdgeSize=6, offset=-2, blendMode=trinity.TR2_SBM_ADD, texturePath='res:/UI/Texture/Lines/BLUR4.png')
        self.sr.args = data.get('args', None)
        self.tabID = self.sr.args
        self.sr.grab = [0, 0]
        self.tabgroup = tabgroup
        self._selected = False
        self.sr.panel = data.get('panel', None)
        self.sr.panelparent = data.get('panelparent', None)
        self.sr.code = data.get('code', None)
        self.sr.LoadTabCallback = data.get('LoadTabCallback', None)
        self.SetLabel(data.get('label', None))
        self.SetIcon(data.get('icon', None))
        self.Deselect(False)
        self.hint = data.get('hint', None)
        if hasattr(self.sr.code, 'GetTabMenu'):
            self.GetMenu = lambda : self.sr.code.GetTabMenu(self)
        if hasattr(self.sr.panel, 'sr'):
            self.sr.panel.sr.tab = self
        self.name = data.name or data.label
        if not self.enabled:
            self.Disable()
        self.callback = data.callback

    def GetPanel(self):
        try:
            return self.sr.panel
        except AttributeError:
            return None

    def Confirm(self, *args):
        self.OnClick()

    def OnSetFocus(self, *args):
        pass

    def OnKillFocus(self, *etc):
        pass

    def SetLabel(self, label, hint = None):
        if self.destroyed:
            return
        self.label.text = label
        self.UpdateTabSize()
        self.label.hint = hint
        self.tabgroup.UpdateSizes()

    def UpdateTabSize(self):
        self.sr.width = self.label.left + self.label.width

    def OnDropData(self, dragObj, nodes):
        if not self.enabled:
            return
        if hasattr(self, 'OnTabDropData'):
            if self.OnTabDropData(dragObj, nodes):
                self.BlinkOnDrop()
        elif isinstance(self.sr.panel, DragDropObject) and hasattr(self.sr.panel, 'OnDropData'):
            if self.sr.panel.OnDropData(dragObj, nodes):
                self.BlinkOnDrop()

    def Blink(self, onoff = 1):
        active = bool(onoff)
        if active and not self.IsSelected():
            self._activity_indicator.mark_new(duration=5.0)
            animations.MorphScalar(self.label, 'glowBrightness', startVal=0.0, endVal=1.0, curveType=uiconst.ANIM_WAVE, loops=3, duration=1.0)
        else:
            self._activity_indicator.activity_level = ActivityLevel.IDLE
        self._update_label_color()

    def BlinkOnDrop(self):
        uicore.animations.FadeTo(self.blinkDrop, 0.0, 1.0, duration=0.25, curveType=uiconst.ANIM_WAVE, loops=2)

    def SetUtilMenu(self, utilMenuFunc):
        from eve.client.script.ui.control.utilMenu import UtilMenu
        self.label.left = 14
        utilMenuIcon = UtilMenu(menuAlign=uiconst.TOPLEFT, parent=self, align=uiconst.TOPLEFT, GetUtilMenu=utilMenuFunc, texturePath='res:/UI/Texture/Icons/73_16_50.png', pos=(uiconst.defaultPadding,
         uiconst.defaultPadding,
         14,
         14))
        self.UpdateTabSize()
        self.tabgroup.UpdateSizes()
        return utilMenuIcon

    def SetIcon(self, iconNo, shiftLabel = 14, hint = None, menufunc = None):
        if self.icon:
            self.icon.Close()
        if self.headerIconCont:
            self.headerIconCont.Close()
            self.headerIconCont = None
        self.sr.hint = hint
        if iconNo is None:
            if self.label:
                self.label.left = 0
        else:
            self.headerIconCont = Container(name='headerIconCont', parent=self, pos=(2, 3, 16, 16), align=uiconst.RELATIVE, ignoreSize=True)
            self.icon = Icon(icon=iconNo, parent=self.headerIconCont, pos=(0, 0, 16, 16), align=uiconst.TOPLEFT, idx=0, state=uiconst.UI_DISABLED)
            if self.label:
                self.label.left = shiftLabel
            if menufunc:
                self.icon.GetMenu = menufunc
                self.icon.expandOnLeft = 1
                self.icon.state = uiconst.UI_NORMAL
        self.sr.hint = hint
        self.UpdateTabSize()
        self.tabgroup.UpdateSizes()

    def OnClick(self, *args):
        if not self.enabled:
            return
        if self.selecting:
            return
        self.tabgroup.state = uiconst.UI_DISABLED
        PlaySound(uiconst.SOUND_BUTTON_CLICK)
        try:
            self.Select()
            uicore.registry.SetFocus(self)
        finally:
            self.tabgroup.state = uiconst.UI_PICKCHILDREN

    def IsSelected(self):
        return self._selected

    @telemetry.ZONE_METHOD
    def Deselect(self, notify = True):
        wasSelected = self._selected
        self._selected = False
        self.ShowDeselected_()
        if self.sr.panel:
            self.sr.panel.display = False
            if notify:
                if wasSelected and hasattr(self.sr.panel, 'OnSelectedTabDeselected'):
                    self.sr.panel.OnSelectedTabDeselected()
                if hasattr(self.sr.panel, 'OnTabDeselect'):
                    self.sr.panel.OnTabDeselect()
                elif hasattr(self.sr.panel, 'UnloadPanel'):
                    self.sr.panel.UnloadPanel()
        if self.sr.panelparent:
            self.sr.panelparent.display = False
            if notify:
                if wasSelected and hasattr(self.sr.panelparent, 'OnSelectedTabDeselected'):
                    self.sr.panelparent.OnSelectedTabDeselected()
                if hasattr(self.sr.panelparent, 'OnTabDeselect'):
                    self.sr.panelparent.OnTabDeselect()
                elif hasattr(self.sr.panelparent, 'UnloadPanel'):
                    self.sr.panelparent.UnloadPanel()

    @telemetry.ZONE_METHOD
    def ShowDeselected_(self):
        if self.selectedBG:
            self.selectedBG.Deselect()
        self._update_label_color()

    @telemetry.ZONE_METHOD
    def ShowSelected_(self):
        if self.selectedBG:
            self.selectedBG.Select()
        self._update_label_color()

    @telemetry.ZONE_METHOD
    def Select(self, silently = 0, useCallback = True, saveSelectedName = True):
        if self.destroyed or self.selecting:
            return
        self.selecting = 1
        self.Blink(0)
        oldTabID = self.tabgroup.GetSelectedID()
        if self is None or self.destroyed:
            self.selecting = 0
            self.tabgroup.state = uiconst.UI_PICKCHILDREN
            return
        if len(self.tabgroup.linkedrows):
            for tabgroup in self.tabgroup.linkedrows:
                if self in tabgroup.mytabs:
                    continue
                tabgroup.SetOrder(0)

        for each in self.tabgroup.sr.tabs:
            if each.IsSelected():
                if hasattr(self.sr.code, 'UnloadTabPanel'):
                    self.sr.code.UnloadTabPanel(each.sr.args, each.sr.panel, each.tabgroup)
            if each == self:
                continue
            notify = True
            if each.sr.panel and each.sr.panel is self.sr.panel or each.sr.panelparent and each.sr.panelparent is self.sr.panelparent:
                notify = False
            each.Deselect(notify)

        self._selected = True
        self.tabgroup._set_selected_tab(self)
        self.ShowSelected_()
        if self.sr.panelparent:
            self.sr.panelparent.display = True
            if hasattr(self.sr.panelparent, 'OnTabSelect'):
                self.sr.panelparent.OnTabSelect()
            elif hasattr(self.sr.panelparent, 'LoadPanel'):
                self.sr.panelparent.LoadPanel()
        if self.sr.panel:
            self.sr.panel.display = True
            if hasattr(self.sr.panel, 'OnTabSelect'):
                self.sr.panel.OnTabSelect()
            elif hasattr(self.sr.panel, 'LoadPanel'):
                self.sr.panel.LoadPanel()
        if useCallback and self.tabgroup.callback:
            self.tabgroup.callback(self.tabgroup.GetSelectedID(), oldTabID)
        err = None
        if self.sr.LoadTabCallback:
            try:
                self.sr.LoadTabCallback(self.sr.args, self.sr.panel, self.tabgroup)
            finally:
                self.selecting = 0

        elif hasattr(self.sr.code, 'LoadTabPanel'):
            try:
                self.sr.code.LoadTabPanel(self.sr.args, self.sr.panel, self.tabgroup)
            finally:
                self.selecting = 0

        elif getattr(self.sr.code, 'Load', None):
            try:
                self.sr.code.Load(self.sr.args)
            except (StandardError,) as err:
                LogException()
                if self.destroyed:
                    return
                wnd = GetWindowAbove(self)
                if wnd and not wnd.destroyed:
                    wnd.HideLoad()

        if not silently:
            par = self.sr.panelparent or self.sr.panel
            wnd = GetWindowAbove(self)
            if par and wnd and wnd == uicore.registry.GetActive():
                uthread.new(uicore.registry.SetFocus, par)
        if self.destroyed:
            return
        self.UpdateSelectedSettings(saveSelectedName)
        if self and not self.destroyed:
            self.tabgroup.UpdateSizes()
            self.selecting = 0
        if err and isinstance(err, UserError):
            raise err
        self._LogProtoEvent()

    def UpdateSelectedSettings(self, saveSelectedName):
        if self.tabgroup.settingsID:
            self.SaveSelectedTabIndex()
            if saveSelectedName:
                self.SaveSelectedTabName()

    def SaveSelectedTabIndex(self):
        settings.user.tabgroups.Set(self.tabgroup.settingsID, self.tabgroup.sr.tabs.index(self))

    def SaveSelectedTabName(self):
        settings.user.tabgroups.Set('%s_names' % self.tabgroup.settingsID, self.label.text if self.label else None)

    def OnMouseDown(self, *args):
        if not self.enabled:
            return
        self._detachallowed = 1
        aL, aT, aW, aH = self.GetAbsolute()
        self.sr.grab = [uicore.uilib.x - aL, uicore.uilib.y - aT]
        if self.selectedBG:
            self.selectedBG.OnMouseDown()

    def OnMouseUp(self, *args):
        if not self.enabled:
            return
        self._detachallowed = 0
        if self.selectedBG:
            self.selectedBG.OnMouseUp()

    def OnMouseMove(self, *args):
        if not self.enabled:
            return
        if self._detachallowed and uicore.uilib.mouseTravel > 24 and hasattr(self.sr.code, 'Detach'):
            uthread.new(self.DoDetach)

    def OnMouseEnter(self, *args):
        if not self.enabled:
            return
        self._hovered = True
        PlaySound(uiconst.SOUND_BUTTON_HOVER)
        if self._selected:
            return
        if self.selectedBG:
            self.selectedBG.OnMouseEnter()
        self._update_label_color()
        self._activity_indicator.mark_seen()

    def OnMouseExit(self, *args):
        if not self.enabled:
            return
        self._hovered = False
        if self.selectedBG:
            self.selectedBG.OnMouseExit()
        self._update_label_color()

    def DoDetach(self, *args):
        if self is not None and not self.destroyed:
            if self.sr.code.Detach(self.sr.panel, self.sr.grab):
                if self is not None and not self.destroyed:
                    self.Close()
            else:
                self._detachallowed = 0

    def GetHint(self):
        if self.hint:
            return self.hint

    @EatsExceptions('protoClientLogs')
    def _LogProtoEvent(self):
        if self.tabgroup.analyticID:
            message_bus = TabMessenger(sm.GetService('publicGatewaySvc'))
            message_bus.tab_selected(self.analyticContext, self._GetAnalyticsTabID(), self.tabgroup.analyticID)

    def _GetAnalyticsTabID(self):
        tab_id = None
        selected_id = self.tabgroup.GetSelectedID()
        if isinstance(selected_id, tuple):
            tab_id = selected_id[0]
        elif isinstance(selected_id, str):
            tab_id = selected_id
        if not tab_id:
            tab_id = self.tabgroup.GetSelectedIdx()
        return str(tab_id)

    def Enable(self, *args):
        super(Tab, self).Enable(*args)
        self.enabled = True
        self.state = uiconst.UI_NORMAL
        self.opacity = OPACITY_DEFAULT

    def Disable(self, *args):
        super(Tab, self).Disable(*args)
        self.enabled = False
        self.state = uiconst.UI_DISABLED
        self.opacity = OPACITY_DISABLED

    def _update_label_color(self):
        if self._hovered:
            duration = 0.1
        else:
            duration = 0.3
        animations.SpColorMorphTo(self.label, endColor=self._get_label_color(), duration=duration)

    def _get_label_color(self):
        if self._selected or self._hovered:
            return TextColor.HIGHLIGHT
        elif self._activity_indicator.activity_level == ActivityLevel.NEW:
            return TextColor.NORMAL
        else:
            return TextColor.SECONDARY


class ActivityLevel(object):
    IDLE = 1
    UNSEEN = 2
    NEW = 3


class ActivityIndicator(Container):
    UNDERLAY_OPACITY_ACTIVE = 0.3
    INDICATOR_OPACITY_ACTIVE = 1.0
    INDICATOR_WIDTH_NEW = 16
    INDICATOR_WIDTH = 8

    def __init__(self, parent = None, align = uiconst.TOALL, activity_level = ActivityLevel.IDLE, padding = 0):
        self._activity_level = activity_level
        self._underlay = None
        self._indicator = None
        self._mark_after_thread = None
        super(ActivityIndicator, self).__init__(parent=parent, align=align, padding=padding)
        self._update()

    @property
    def activity_level(self):
        return self._activity_level

    @activity_level.setter
    def activity_level(self, value):
        if self._activity_level != value:
            previous_activity_level = self._activity_level
            self._activity_level = value
            self._update(previous_activity_level=previous_activity_level)
        if self._mark_after_thread:
            self._mark_after_thread.kill()
            self._mark_after_thread = None

    def mark_seen(self):
        if self._activity_level == ActivityLevel.NEW:
            self.activity_level = ActivityLevel.UNSEEN

    def mark_new(self, duration = None):
        self.activity_level = ActivityLevel.NEW
        if duration is not None:
            self._mark_after_thread = uthread2.StartTasklet(self._mark_after, ActivityLevel.UNSEEN, duration)

    def _mark_after(self, activityLevel, duration):
        uthread2.sleep(duration)
        self.activity_level = activityLevel

    def _update(self, previous_activity_level = None):
        if self._activity_level in (ActivityLevel.IDLE, ActivityLevel.UNSEEN):
            if self._underlay is not None:
                if previous_activity_level is not None:
                    animations.FadeOut(self._underlay, duration=0.6)
                else:
                    self._underlay.opacity = 0.0
        elif self._activity_level == ActivityLevel.NEW:
            if self._underlay is None:
                self._create_underlay()
            if previous_activity_level is not None:
                animations.FadeIn(self._underlay, endVal=self.UNDERLAY_OPACITY_ACTIVE, duration=0.6)
            else:
                self._underlay.opacity = self.UNDERLAY_OPACITY_ACTIVE
        if self._activity_level == ActivityLevel.IDLE:
            if self._indicator is not None:
                if previous_activity_level is not None:
                    animations.FadeOut(self._indicator, duration=0.3)
                    animations.MorphScalar(self._indicator, 'width', startVal=self._indicator.width, endVal=0, duration=0.6)
                else:
                    self._indicator.opacity = 0.0
                    self._indicator.width = 0
        elif self._activity_level in (ActivityLevel.UNSEEN, ActivityLevel.NEW):
            if self._indicator is None:
                self._create_indicator()
            indicator_width = self._get_indicator_width()
            if previous_activity_level is not None:
                animations.FadeIn(self._indicator, duration=0.3)
                animations.MorphScalar(self._indicator, 'width', startVal=self._indicator.width, endVal=indicator_width, duration=0.6)
            else:
                self._indicator.opacity = self.INDICATOR_OPACITY_ACTIVE
                self._indicator.width = indicator_width

    def _create_underlay(self):
        if self._underlay is None:
            self._underlay = Fill(parent=self, align=uiconst.TOALL, color=eveThemeColor.THEME_ALERT, opacity=0.0)

    def _create_indicator(self):
        if self._indicator is None:
            self._indicator = Fill(parent=self, idx=0, align=uiconst.CENTERBOTTOM, width=self._get_indicator_width(), height=1, color=eveThemeColor.THEME_ALERT, outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, opacity=0.0)

    def _get_indicator_width(self):
        if self.activity_level == ActivityLevel.NEW:
            return self.INDICATOR_WIDTH_NEW
        return self.INDICATOR_WIDTH

    def OnColorThemeChanged(self):
        if self._indicator is not None:
            self._indicator.color = tuple(eveThemeColor.THEME_ALERT[:3]) + (self._indicator.opacity,)
        if self._underlay is not None:
            self._underlay.color = tuple(eveThemeColor.THEME_ALERT[:3]) + (self._underlay.opacity,)
