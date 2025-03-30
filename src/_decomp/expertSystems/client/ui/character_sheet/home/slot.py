#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\expertSystems\client\ui\character_sheet\home\slot.py
import chroma
import datetimeutils
import eveformat
import localization.formatters
import signals
import threadutils
import uthread2
from carbon.client.script.environment.AudioUtil import PlaySound
from carbon.common.script.sys.serviceManager import ServiceManager
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control.donutSegment import DonutSegment
from eve.client.script.ui.control.itemIcon import ItemIcon
from eve.client.script.ui.control.themeColored import SpriteThemeColored
from expertSystems.client import texture
from expertSystems.client.const import Color

class SlotController(object):

    def __init__(self, expert_system = None, is_selected = False):
        self._is_selected = is_selected
        self._expert_system = expert_system
        self.on_add = signals.Signal()
        self.on_expert_system_changed = signals.Signal()
        self.on_selected_changed = signals.Signal()

    @property
    def expert_system(self):
        return self._expert_system

    @expert_system.setter
    def expert_system(self, expert_system):
        if self._expert_system != expert_system:
            self.is_selected = False
            self._expert_system = expert_system
            self.on_expert_system_changed(self)

    @property
    def is_selected(self):
        return self._is_selected

    @is_selected.setter
    def is_selected(self, is_selected):
        if self._is_selected != is_selected:
            self._is_selected = is_selected
            self.on_selected_changed(self)

    def select(self):
        if self.expert_system is not None:
            self.is_selected = True

    def add(self):
        if self.expert_system is None:
            self.on_add(self)


class ExpertSystemSlot(ContainerAutoSize):

    def __init__(self, controller = None, **kwargs):
        if controller is None:
            controller = SlotController()
        self.controller = controller
        self.slot_container = None
        self.empty_slot = None
        self.type_icon = None
        self.timer = None
        self.hover_indicator = None
        self.selected_indicator = None
        super(ExpertSystemSlot, self).__init__(alignMode=uiconst.TOTOP, width=64, **kwargs)
        self.layout()
        self.update()
        self.controller.on_selected_changed.connect(self._handle_slot_updated)
        self.controller.on_expert_system_changed.connect(self._handle_slot_updated)

    def layout(self):
        self.slot_container = Container(parent=self, align=uiconst.TOTOP, height=64)
        self.empty_slot = EmptySlotIcon(parent=self.slot_container, align=uiconst.CENTERTOP, width=64, height=64, on_click=self.controller.add)
        self.hover_indicator = Sprite(parent=self, align=uiconst.CENTERTOP, state=uiconst.UI_DISABLED, top=-2, width=60, height=69, texturePath=texture.slot_hovered_indicator, opacity=0.0)
        self.selected_indicator = Sprite(parent=self, align=uiconst.CENTERTOP, state=uiconst.UI_DISABLED, top=-2, width=60, height=69, texturePath=texture.slot_selected_indicator, opacity=0.0)

    def update(self):
        self.empty_slot.display = self.controller.expert_system is None
        if self.controller.expert_system is not None:
            if self.type_icon is None:
                self.type_icon = ExpertSystemIcon(parent=self.slot_container, align=uiconst.CENTER, expert_system=self.controller.expert_system, on_click=self._handle_on_expert_system_icon_clicked)
            else:
                self.type_icon.expert_system = self.controller.expert_system
            if self.timer is None:
                self.timer = Timer(parent=self.slot_container, align=uiconst.CENTER, top=24, left=16, expert_system=self.controller.expert_system, idx=0)
            else:
                self.timer.expert_system = self.controller.expert_system
            if self.controller.is_selected:
                self.hover_indicator.opacity = 0.0
                self.selected_indicator.opacity = 0.7
            else:
                self.selected_indicator.opacity = 0.0
        else:
            if self.type_icon:
                self.type_icon.Close()
                self.type_icon = None
            if self.timer:
                self.timer.Close()
                self.timer = None
            self.selected_indicator.opacity = 0.0

    def _handle_slot_updated(self, slot):
        self.update()

    def _handle_on_expert_system_icon_clicked(self):
        if not self.controller.is_selected:
            PlaySound(uiconst.SOUND_ENTRY_SELECT)
            self.controller.select()

    def OnMouseEnter(self, *args):
        PlaySound(uiconst.SOUND_BUTTON_HOVER)
        if self.controller.expert_system and not self.controller.is_selected:
            self.hover_indicator.opacity = 0.7

    def OnMouseExit(self, *args):
        self.hover_indicator.opacity = 0.0


class EmptySlotIcon(Container):
    default_state = uiconst.UI_NORMAL
    default_width = 64
    default_height = 64
    default_pickRadius = 30

    def __init__(self, on_click = None, **kwargs):
        self._on_click = on_click
        self.icon_plus = None
        self.icon_background = None
        super(EmptySlotIcon, self).__init__(**kwargs)
        self.layout()

    def layout(self):
        self.icon_plus = Sprite(parent=self, align=uiconst.TOALL, state=uiconst.UI_DISABLED, texturePath=texture.empty_slot_plus, color=Color.white)
        Sprite(parent=self, align=uiconst.CENTER, state=uiconst.UI_DISABLED, top=24, left=16, width=24, height=24, texturePath=texture.badge_24)
        self.icon_background = SpriteThemeColored(parent=self, align=uiconst.TOALL, state=uiconst.UI_DISABLED, texturePath=texture.empty_slot_background, colorType=uiconst.COLORTYPE_UIBASECONTRAST, opacity=0.8)

    def GetHint(self):
        return localization.GetByLabel('UI/ExpertSystem/BrowseExpertSystems')

    def OnMouseEnter(self, *args):
        self.icon_plus.SetRGB(*Color.base)
        self.icon_background.SetColorType(uiconst.COLORTYPE_UIHILIGHT)

    def OnMouseExit(self, *args):
        self.icon_plus.SetRGB(*Color.white)
        self.icon_background.SetColorType(uiconst.COLORTYPE_UIBASECONTRAST)

    def OnClick(self):
        if self._on_click:
            PlaySound(uiconst.SOUND_BUTTON_CLICK)
            self._on_click()


class ExpertSystemIcon(ItemIcon):
    default_width = 64
    default_height = 64
    default_showOmegaOverlay = False
    default_pickRadius = 30

    def __init__(self, expert_system, on_click = None, **kwargs):
        self._expert_system = expert_system
        self._on_click = on_click
        super(ExpertSystemIcon, self).__init__(typeID=expert_system.type_id, **kwargs)

    @property
    def expert_system(self):
        return self._expert_system

    @expert_system.setter
    def expert_system(self, expert_system):
        if self._expert_system != expert_system:
            self._expert_system = expert_system
            self.SetTypeID(expert_system.type_id)

    def OnClick(self, *args):
        if self._on_click:
            self._on_click()

    def GetMenu(self):
        menu_service = ServiceManager.Instance().GetService('menu')
        return menu_service.GetMenuFromItemIDTypeID(itemID=None, typeID=self.typeID)

    def LoadTooltipPanel(self, tooltipPanel, *args):
        tooltipPanel.LoadGeneric1ColumnTemplate()
        tooltipPanel.AddLabelLarge(text=self.expert_system.name)
        tooltipPanel.AddLabelMedium(text=localization.GetByLabel('UI/ExpertSystem/ExpiresIn', time=eveformat.color(format_timespan_short(self.expert_system.expires_in), color=Color.warning if self.expert_system.expires_soon else Color.base)))


class Timer(ContainerAutoSize):

    def __init__(self, expert_system = None, **kwargs):
        self._expert_system = expert_system
        self._donut = None
        self._donut_background = None
        super(Timer, self).__init__(**kwargs)
        self.layout()
        self._start_timer_thread_maybe()

    @property
    def expert_system(self):
        return self._expert_system

    @expert_system.setter
    def expert_system(self, expert_system):
        if self._expert_system != expert_system:
            self._expert_system = expert_system
            self._start_timer_thread_maybe()

    def layout(self):
        self._donut = DonutSegment(parent=self, align=uiconst.CENTER, state=uiconst.UI_DISABLED, lineWidth=2, radius=10)
        self._donut_background = DonutSegment(parent=self, align=uiconst.CENTER, state=uiconst.UI_DISABLED, lineWidth=2, radius=10)
        DonutSegment(parent=self, align=uiconst.CENTER, state=uiconst.UI_DISABLED, lineWidth=6, radius=12, colorStart=(0.05, 0.05, 0.05), colorEnd=(0.05, 0.05, 0.05))
        self._update_color()

    def _get_donut_color(self):
        if self.expert_system is None:
            return Color.base
        elif self.expert_system.expires_soon:
            return Color.warning
        else:
            return Color.base

    def _get_donut_background_color(self):
        return chroma.Color.from_any(self._get_donut_color()).with_brightness(0.2).rgba

    def _update_color(self):
        donut_color = chroma.Color.from_any(self._get_donut_color()).rgba
        self._donut.SetColor(start=donut_color, end=donut_color)
        donut_background_color = self._get_donut_background_color()
        self._donut_background.SetColor(start=donut_background_color, end=donut_background_color)

    @threadutils.highlander_threaded
    def _start_timer_thread_maybe(self):
        while self._expert_system:
            self._update_color()
            self._donut.SetValue(self.expert_system.remaining_time_proportion)
            uthread2.sleep(1.0)


def format_timespan_short(timespan, show_from = 'year', show_to = 'second'):
    filetime_delta = datetimeutils.timedelta_to_filetime_delta(timespan)
    return localization.formatters.FormatTimeIntervalShortWritten(filetime_delta, showFrom=show_from, showTo=show_to)
