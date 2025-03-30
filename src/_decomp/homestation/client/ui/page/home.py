#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\homestation\client\ui\page\home.py
import logging
import carbonui.control.button
import signals
import threadutils
from carbon.common.script.sys.serviceManager import ServiceManager
from carbonui import ButtonStyle, uiconst
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.uianimations import animations
from eve.client.script.ui.control import eveLabel, itemIcon
from eve.client.script.ui.control.eveLoadingWheel import LoadingWheel
from homestation.client import text
from homestation.client.augmentation import Augmentations
from homestation.client.error import handle_self_destruct_clone_validation_error
from homestation.client.prompt import prompt_self_destruct_clone
from homestation.client.service import Service
from homestation.client.ui import info_card
from homestation.client.ui.const import TextColor, Padding, PAGE_WIDTH_MAX
from homestation.client.ui.header import Header
from homestation.client.ui.page.base import Page
from homestation.client.ui.tooltip import load_error_tooltip
from homestation.client.ui.vertical_centered_container import VerticalCenteredContainer
from homestation.client.validation import SelfDestructCloneValidator
from homestation.session import get_docked_id, get_global_session
from homestation.validation import SelfDestructCloneValidationError
log = logging.getLogger(__name__)
BUTTON_WIDTH = 140
BUTTON_HEIGHT = 30

class HomePageController(object):

    def __init__(self, godma):
        self.home_station_service = Service.instance()
        self.on_loading = signals.Signal()
        self.on_ready = signals.Signal()
        self.augmentations = Augmentations(character_id=get_global_session().charid, godma=godma)
        self._is_loading = False
        self._is_ready = False
        self._is_load_pending = False
        self._is_closed = False
        self.home_station_service.on_home_station_changed.connect(self.load)

    def close(self):
        if self._is_closed:
            return
        self._is_closed = True
        self.home_station_service.on_home_station_changed.disconnect(self.load)
        self.on_loading.clear()
        self.on_ready.clear()

    @property
    def is_ready(self):
        return self._is_ready

    @property
    def is_loading(self):
        return self._is_loading

    @property
    def home_station(self):
        return self.home_station_service.get_home_station()

    @property
    def on_home_station_changed(self):
        return self.home_station_service.on_home_station_changed

    def load(self):
        if self._is_loading:
            self._is_load_pending = True
            return
        self._is_ready = False
        self._is_loading = True
        try:
            self.on_loading()
            self.home_station_service.get_home_station()
            self.augmentations.load()
        finally:
            self._is_loading = False

        if self._is_load_pending:
            self.load()
        else:
            self._is_ready = True
            self.on_ready()

    def set_destination_to_home_station(self):
        home_station = self.home_station_service.get_home_station()
        star_map_service = ServiceManager.Instance().GetService('starmap')
        star_map_service.SetWaypoint(home_station.id, clearOtherWaypoints=True)


class HomePage(Page):

    def __init__(self):
        super(HomePage, self).__init__()
        self.controller = HomePageController(godma=ServiceManager.Instance().GetService('godma'))
        self.on_select_home_station = signals.Signal()
        self.main_cont = None
        self.loading_indicator = None

    def Close(self):
        self.controller.close()

    def on_loading(self):
        self.show_loading()

    def on_ready(self):
        self.update_page()
        self.hide_loading()

    def load(self):
        self.layout()
        self.controller.on_loading.connect(self.on_loading)
        self.controller.on_ready.connect(self.on_ready)
        if self.controller.is_loading:
            self.show_loading()
        elif self.controller.is_ready:
            self.update_page()
        else:
            self.controller.load()

    def unload(self):
        super(HomePage, self).unload()
        self.controller.on_loading.disconnect(self.on_loading)
        self.controller.on_ready.disconnect(self.on_ready)

    def show_loading(self):
        animations.FadeOut(self.main_cont, duration=0.3)
        animations.FadeIn(self.loading_indicator, duration=0.3)

    def hide_loading(self):
        animations.FadeIn(self.main_cont, duration=0.3)
        animations.FadeOut(self.loading_indicator, duration=0.3)

    def layout(self):
        self.loading_indicator = LoadingWheel(parent=self, align=uiconst.CENTER, opacity=0.0)
        scroll = ScrollContainer(parent=self, align=uiconst.TOALL)
        self.main_cont = ContainerAutoSize(parent=scroll, align=uiconst.CENTERTOP, top=Padding.wide, width=PAGE_WIDTH_MAX)

    @threadutils.highlander_threaded
    def update_page(self):
        self.main_cont.Flush()
        Header(parent=self.main_cont, align=uiconst.TOTOP, text=text.header_current_home_station(), hint=text.hint_home_station_benefits())
        new_home_station_cont = ContainerAutoSize(parent=self.main_cont, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, top=Padding.slim)
        station_icon_size = 48
        station_icon_cont = Container(parent=new_home_station_cont, align=uiconst.TOLEFT, width=station_icon_size)
        itemIcon.ItemIcon(parent=station_icon_cont, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, typeID=self.controller.home_station.type_id, itemID=self.controller.home_station.id, width=station_icon_size, height=station_icon_size)
        home_station_button_cont = ContainerAutoSize(parent=new_home_station_cont, align=uiconst.TORIGHT, padLeft=Padding.normal)
        home_station_button_inner_cont = ContainerAutoSize(parent=home_station_button_cont, align=uiconst.TOPLEFT, minHeight=station_icon_size)
        SetDestinationButton(parent=home_station_button_inner_cont, align=uiconst.CENTERRIGHT, fixedheight=BUTTON_HEIGHT, fixedwidth=BUTTON_WIDTH, home_station_service=self.controller.home_station_service)
        inner_cont = VerticalCenteredContainer(parent=new_home_station_cont, align=uiconst.TOTOP, padLeft=Padding.normal, minHeight=station_icon_size)
        with inner_cont.auto_size_disabled():
            eveLabel.EveLabelMedium(parent=inner_cont, align=uiconst.TOTOP, state=uiconst.UI_NORMAL, text=self.controller.home_station.link)
            eveLabel.EveLabelMedium(parent=inner_cont, align=uiconst.TOTOP, text=self.controller.home_station.trace, color=TextColor.secondary)
        if self.controller.home_station.is_fallback:
            info_card.InfoCard(parent=self.main_cont, align=uiconst.TOTOP, top=Padding.normal, text=text.fallback_station_info_card())
        change_home_station_cont = ContainerAutoSize(parent=self.main_cont, align=uiconst.TOTOP, top=Padding.section, alignMode=uiconst.TOTOP, minHeight=BUTTON_HEIGHT)
        change_home_station_button_cont = ContainerAutoSize(parent=change_home_station_cont, align=uiconst.TORIGHT, padLeft=Padding.wide)
        carbonui.control.button.Button(parent=change_home_station_button_cont, align=uiconst.TOPLEFT, fixedheight=BUTTON_HEIGHT, fixedwidth=BUTTON_WIDTH, top=Padding.slim, label=text.action_select_new_home_station(), func=self.on_select_home_station, args=())
        Header(parent=change_home_station_cont, align=uiconst.TOTOP, text=text.title_change_home_station())
        eveLabel.EveLabelMedium(parent=change_home_station_cont, align=uiconst.TOTOP, top=Padding.slim, text=text.description_change_home_station(), color=TextColor.secondary)
        self_destruct_cont = ContainerAutoSize(parent=self.main_cont, align=uiconst.TOTOP, top=Padding.section, alignMode=uiconst.TOTOP)
        self_destruct_button_cont = ContainerAutoSize(parent=self_destruct_cont, align=uiconst.TORIGHT, padLeft=Padding.wide)
        SelfDestructButton(parent=self_destruct_button_cont, align=uiconst.TOPLEFT, fixedheight=BUTTON_HEIGHT, fixedwidth=BUTTON_WIDTH, top=Padding.slim, home_station_service=self.controller.home_station_service)
        Header(parent=self_destruct_cont, align=uiconst.TOTOP, text=text.header_self_destruct_clone())
        eveLabel.EveLabelMedium(parent=self_destruct_cont, align=uiconst.TOTOP, text=text.description_self_destruct_clone(), color=TextColor.secondary)
        SelfDestructWarning(parent=self.main_cont, align=uiconst.TOTOP, top=Padding.normal, augmentations=self.controller.augmentations)


class Autopilot(object):
    __notifyevents__ = ('OnDestinationSet',)

    def __init__(self):
        self.on_route_update = signals.Signal()
        ServiceManager.Instance().RegisterNotify(self)

    @property
    def destination_id(self):
        return self._star_map_service.GetDestination()

    @property
    def waypoint_count(self):
        return len(self._star_map_service.GetWaypoints())

    def set_destination(self, location_id):
        self._star_map_service.SetWaypoint(location_id, clearOtherWaypoints=True)

    def is_destination_set(self, location_id):
        return self.destination_id == location_id and self.waypoint_count == 1

    @property
    def _star_map_service(self):
        return ServiceManager.Instance().GetService('starmap')

    def OnDestinationSet(self, destination):
        self.on_route_update()


class SetDestinationButton(carbonui.control.button.Button):

    def __init__(self, home_station_service, **kwargs):
        self._autopilot = Autopilot()
        self._home_station_service = home_station_service
        super(SetDestinationButton, self).__init__(func=self._set_destination_to_home_station, args=(), **kwargs)
        self._update()
        self._autopilot.on_route_update.connect(self._update)

    @property
    def _home_station_id(self):
        return self._home_station_service.get_home_station().id

    @property
    def _is_destination_set_home(self):
        return self._autopilot.is_destination_set(self._home_station_id)

    @property
    def _is_at_home(self):
        return self._home_station_id == get_docked_id(get_global_session())

    def _update(self):
        if self._is_destination_set_home or self._is_at_home:
            self.Disable()
        else:
            self.Enable()
        if self._is_destination_set_home:
            self.SetLabel(text.feedback_destination_set())
        else:
            self.SetLabel(text.action_set_destination())

    def _set_destination_to_home_station(self):
        home_station = self._home_station_service.get_home_station()
        self._autopilot.set_destination(home_station.id)

    def LoadTooltipPanel(self, panel, parent):
        if self._is_at_home:
            errors = [text.hint_already_in_home_station()]
            load_error_tooltip(panel, errors)


class SelfDestructWarning(info_card.InfoCard):

    def __init__(self, augmentations, **kwargs):
        super(SelfDestructWarning, self).__init__(text=text.warning_self_destruct_clone(), severity=info_card.Severity.warning, **kwargs)
        self.augmentations = augmentations
        self.update()
        self.augmentations.on_update.connect(self.update)

    @property
    def should_show(self):
        return self.augmentations.has_destructible_augmentations

    @threadutils.threaded
    def update(self):
        if self.should_show:
            self.Show()
        else:
            self.Hide()


class SelfDestructButton(carbonui.control.button.Button):
    default_style = ButtonStyle.WARNING

    def __init__(self, home_station_service, **kwargs):
        self.home_station_service = home_station_service
        self.errors = []
        super(SelfDestructButton, self).__init__(label=text.action_self_destruct_clone(), func=self._self_destruct_clone, args=(), **kwargs)
        self.Disable()
        self.validator = SelfDestructCloneValidator(session=get_global_session(), home_station_service=self.home_station_service, godma_service=ServiceManager.Instance().GetService('godma'))
        self.validate()
        self.validator.on_invalidated.connect(self.validate)

    @threadutils.highlander_threaded
    def validate(self):
        self.Disable()
        self.errors = self.validator.validate()
        if not self.errors:
            self.Enable()

    def _self_destruct_clone(self):
        if not prompt_self_destruct_clone(self.home_station_service.get_home_station().id):
            return
        try:
            self.home_station_service.self_destruct_clone()
        except SelfDestructCloneValidationError as error:
            handle_self_destruct_clone_validation_error(error)

    def LoadTooltipPanel(self, panel, parent):
        errors = [ text.describe_self_destruct_clone_validation_error(error) for error in self.errors ]
        load_error_tooltip(panel, errors)
