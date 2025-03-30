#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\charsheet\jumpClonesPanel.py
import contextlib
import datetime
import functools
import logging
import math
import random
import caching
import datetimeutils
import dogma.const
import enum
import eveformat.client
import eveicon
import evelink.client
import evetypes
import eveui
import inventorycommon.const
import localization
import signals
import threadutils
import trinity
import uthread2
from carbonui import ButtonStyle, ButtonVariant, TextColor, uiconst
from carbonui.control import scrollContainer
from carbonui.control.button import Button
from carbonui.primitives import container, containerAutoSize, layoutGrid, sprite
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.uianimations import animations
from eve.client.script.ui import eveColor, eveThemeColor
from eve.client.script.ui.control import eveLabel
from eve.client.script.ui.control import eveLoadingWheel
from eve.client.script.ui.control import infoIcon
from eve.client.script.ui.control import itemIcon
from eve.client.script.ui.control import themeColored
from eve.client.script.ui.control import utilMenu
from carbonui.button.group import ButtonGroup
from eve.client.script.ui.shared.shipTree import infoBubble
from eve.client.script.ui.tooltips import tooltipUtil
from eve.client.script.ui.util import utilWindows
from eve.common.script.sys.idCheckers import IsStation
from eve.common.script.util.eveFormat import FmtISK
from eveservices.menu import GetMenuService
from inventorycommon.typeHelpers import GetAveragePrice
from menucheckers.sessionChecker import SessionChecker
log = logging.getLogger(__name__)
CLONE_LIMIT_SKILLS = [inventorycommon.const.typeInfomorphPsychology, inventorycommon.const.typeAdvancedInfomorphPsychology, inventorycommon.const.typeEliteInfomorphPsychology]
CLONE_JUMP_COOLDOWN_SKILLS = [inventorycommon.const.typeInfomorphSynchronizing]
JUMP_CLONE_SKILLS = CLONE_LIMIT_SKILLS + CLONE_JUMP_COOLDOWN_SKILLS
COLOR_WARNING = eveColor.WARNING_ORANGE
COLOR_TEXT_SECONDARY = TextColor.SECONDARY

def jump_clone_label_path(name):
    return 'UI/CharacterSheet/CharacterSheetWindow/JumpCloneScroll/{}'.format(name)


def jump_clone_label(name, **kwargs):
    return localization.GetByLabel(jump_clone_label_path(name), **kwargs)


class OptionEnum(enum.Enum):

    def __new__(cls, value, label):
        obj = object.__new__(cls)
        obj._value_ = value
        obj._label = label
        return obj

    @property
    def label(self):
        return localization.GetByLabel(self._label)

    @classmethod
    def __reload_update__(cls, oldobj):
        return cls


class FilterBy(OptionEnum):
    all = (1, jump_clone_label_path('FilterByAll'))
    station = (2, jump_clone_label_path('FilterByStation'))
    structure = (3, jump_clone_label_path('FilterByStructure'))
    ship = (4, jump_clone_label_path('FilterByShip'))


class ArrangeBy(OptionEnum):
    location = (1, jump_clone_label_path('ArrangeByLocation'))
    name = (2, jump_clone_label_path('ArrangeByName'))
    implant_count = (3, jump_clone_label_path('ArrangeByImplantCount'))


class SortOrder(OptionEnum):
    ascending = (1, jump_clone_label_path('SortOrderAscending'))
    descending = (2, jump_clone_label_path('SortOrderDescending'))


class JumpClonesPanel(container.Container):
    default_name = 'JumpClonesPanel'

    def __init__(self, **kwargs):
        self.controller = JumpClonePanelController()
        self.clone_entries = []
        self.is_refreshing = False
        self.needs_refresh = False
        self.jump_cooldown_banner = None
        self.install_clone_banner = None
        self.no_clones_message = None
        super(JumpClonesPanel, self).__init__(**kwargs)
        self.layout()
        self.controller.on_update.connect(self.refresh)
        self.controller.on_filter_change.connect(self.on_filter_change)

    def on_filter_change(self):
        self.refresh_clone_list()

    def layout(self):
        self.loading_overlay = container.Container(parent=self, align=uiconst.TOALL, state=uiconst.UI_NORMAL, bgColor=(0.0, 0.0, 0.0), opacity=0.5)
        self.main_cont = container.Container(parent=self, align=uiconst.TOALL)
        self.loading_wheel = eveLoadingWheel.LoadingWheel(parent=self.loading_overlay, align=uiconst.CENTER, state=uiconst.UI_DISABLED)
        self.error_message = ErrorMessage(parent=self.loading_overlay, align=uiconst.CENTER)
        self.footer = container.Container(parent=self.main_cont, align=uiconst.TOBOTTOM, height=32)
        self.clone_limit_label = eveLabel.EveLabelMedium(parent=self.footer, align=uiconst.CENTERLEFT, state=uiconst.UI_NORMAL, left=12)
        self.clone_limit_label.LoadTooltipPanel = load_clone_limit_tootltip
        filter_cont = containerAutoSize.ContainerAutoSize(parent=self.main_cont, align=uiconst.TOTOP)
        self.filter_menu = FilterMenu(parent=filter_cont, align=uiconst.TOPLEFT, controller=self.controller)
        self.clone_scroll = scrollContainer.ScrollContainer(parent=self.main_cont, align=uiconst.TOALL, alignMode=uiconst.TOTOP, padding=(0, 4, 0, 0))

    def Close(self):
        self.controller.close()
        super(JumpClonesPanel, self).Close()

    def LoadPanel(self, *args):
        self.refresh()

    def refresh(self):
        if not self.display:
            return
        if not session.charid:
            return
        if self.is_refreshing:
            self.needs_refresh = True
            return
        self.is_refreshing = True
        self.needs_refresh = False
        try:
            with self.loading():
                with self.keep_scroll_position():
                    self.controller.pre_load()
                    self.clear_clone_list()
                    if not self.needs_refresh:
                        self.load_content()
        finally:
            self.is_refreshing = False

        if self.needs_refresh:
            uthread2.start_tasklet(self.refresh)

    def refresh_clone_list(self):
        if not self.display:
            return
        with self.keep_scroll_position():
            self.clear_clone_list()
            self.load_clone_list()

    def clear_clone_list(self):
        if self.no_clones_message:
            self.no_clones_message.Close()
            self.no_clones_message = None
        entries = self.clone_entries
        self.clone_entries = []
        for entry in entries:
            entry.Close()

    @contextlib.contextmanager
    def loading(self):
        self.error_message.Hide()
        self.loading_overlay.Enable()
        animations.FadeIn(self.loading_overlay, endVal=0.5, duration=0.5)
        animations.FadeIn(self.loading_wheel, duration=0.3)
        try:
            yield
        except Exception:
            animations.FadeOut(self.main_cont, duration=0.3)
            animations.FadeOut(self.loading_wheel, duration=0.1)
            self.error_message.Show()
            self.error_message.SetText(jump_clone_label('UnknownErrorMessage'))
            log.exception('Failed to load the jump clones panel in the character sheet')
        else:
            self.loading_overlay.Disable()
            animations.FadeOut(self.loading_overlay, duration=0.3)
            animations.FadeIn(self.main_cont, duration=0.3)

    @contextlib.contextmanager
    def keep_scroll_position(self):
        self.clone_scroll.mainCont.DisableAutoSize()
        try:
            yield
        finally:
            eveui.call_next_frame(self.clone_scroll.mainCont.EnableAutoSize)

    def load_content(self):
        if self.controller.clone_limit == 0:
            text = localization.GetByLabel('UI/Medical/JumpCloneSkillReqNotMet')
            color = COLOR_WARNING
        else:
            text = localization.GetByLabel('UI/Medical/JumpCloneUsageAndCapacity', count=len(self.controller.clones), limit=self.controller.clone_limit)
            if self.controller.clone_count == self.controller.clone_limit:
                color = COLOR_WARNING
            else:
                color = self.clone_limit_label.default_color
        self.clone_limit_label.SetRGBA(*color)
        self.clone_limit_label.SetText(text)
        if not self.jump_cooldown_banner:
            self.jump_cooldown_banner = JumpCooldownBanner(parent=self.clone_scroll, align=uiconst.TOTOP, controller=self.controller)
        if not self.install_clone_banner:
            self.install_clone_banner = InstallCloneBanner(parent=self.clone_scroll, align=uiconst.TOTOP, padTop=4, controller=self.controller)
        self.load_clone_list()

    def load_clone_list(self):
        clones = self.controller.clones_filtered_and_sorted
        for i, clone in enumerate(clones):
            entry = JumpCloneEntry(parent=self.clone_scroll, align=uiconst.TOTOP, padTop=4 if i > 0 else 8, controller=self.controller, clone=clone, jump_errors=self.controller.validate_jump_to(clone), on_expand=self.on_clone_entry_expand)
            self.clone_entries.append(entry)
            animations.FadeTo(entry, startVal=0.0, endVal=1.0, duration=0.25, timeOffset=0.02 * i)

        if not clones and not self.controller.clones:
            self.display_no_clones_message()
        elif not clones:
            self.display_no_clones_match_filter_message()

    @threadutils.threaded
    def on_clone_entry_expand(self, jump_clone_entry):
        eveui.wait_for_next_frame()
        self.clone_scroll.ScrollToRevealChildVertical(jump_clone_entry)

    def display_no_clones_message(self):
        self.no_clones_message = containerAutoSize.ContainerAutoSize(parent=self.clone_scroll, align=uiconst.TOTOP, top=64, padding=(64, 0, 64, 0))
        icon_cont = container.Container(parent=self.no_clones_message, align=uiconst.TOTOP, height=64, width=72)
        sprite.Sprite(parent=icon_cont, align=uiconst.CENTER, height=64, width=64, texturePath='res:/UI/Texture/WindowIcons/jumpclones.png', opacity=0.25)
        infoIcon.MoreInfoIcon(parent=icon_cont, align=uiconst.CENTERTOP, left=42, hint=localization.GetByLabel('UI/Medical/JumpCloneDescription'))
        eveLabel.EveCaptionMedium(parent=self.no_clones_message, align=uiconst.TOTOP, text=eveformat.center(jump_clone_label('NoJumpClonesFound')), opacity=0.5)
        eveLabel.EveLabelMedium(parent=self.no_clones_message, align=uiconst.TOTOP, text=eveformat.center(jump_clone_label('NoJumpClonesFoundDescription')), opacity=0.25)

    def display_no_clones_match_filter_message(self):
        self.no_clones_message = containerAutoSize.ContainerAutoSize(parent=self.clone_scroll, align=uiconst.TOTOP, top=64, padding=(64, 0, 64, 0))
        eveLabel.EveCaptionMedium(parent=self.no_clones_message, align=uiconst.TOTOP, text=eveformat.center(jump_clone_label('NoJumpClonesMatchFilter')), opacity=0.5)
        eveLabel.EveLabelMedium(parent=self.no_clones_message, align=uiconst.TOTOP, text=eveformat.center(jump_clone_label('NoJumpClonesMatchFilterDescription')), opacity=0.25)


def load_clone_limit_tootltip(panel, parent):
    panel.state = uiconst.UI_NORMAL
    panel.LoadGeneric2ColumnTemplate()
    panel.margin = (8, 8, 8, 8)
    for type_id in CLONE_LIMIT_SKILLS:
        panel.AddRow(rowClass=infoBubble.SkillEntry, typeID=type_id, level=0, showLevel=False, skillBarPadding=(24, 8, 0, 8))


class FilterMenu(utilMenu.UtilMenu):
    default_texturePath = eveicon.tune
    default_iconSize = 16
    default_labelAlign = uiconst.CENTERRIGHT

    def __init__(self, controller, **kwargs):
        self.controller = controller
        kwargs['GetUtilMenu'] = self.get_util_menu
        super(FilterMenu, self).__init__(**kwargs)
        self.update_label()

    def on_filter_by_change(self, filter_by):
        self.controller.filter_by = filter_by
        self.update_label()

    def on_arrange_by_change(self, arrange_by):
        self.controller.arrange_by = arrange_by
        self.update_label()

    def on_sort_order_change(self, sort_order):
        self.controller.sort_order = sort_order
        self.update_label()

    def get_util_menu(self, menu):
        menu.AddText(jump_clone_label('FilterHeader'))
        for filter_by in FilterBy:
            menu.AddRadioButton(filter_by.label, checked=self.controller.filter_by == filter_by, callback=functools.partial(self.on_filter_by_change, filter_by=filter_by))

        menu.AddSpace(height=12)
        menu.AddText(jump_clone_label('ArrangeByHeader'))
        for arrange_by in ArrangeBy:
            menu.AddRadioButton(arrange_by.label, checked=self.controller.arrange_by == arrange_by, callback=functools.partial(self.on_arrange_by_change, arrange_by=arrange_by))

        menu.AddSpace(height=12)
        menu.AddText(jump_clone_label('SortHeader'))
        for sort_order in SortOrder:
            menu.AddRadioButton(sort_order.label, checked=self.controller.sort_order == sort_order, callback=functools.partial(self.on_sort_order_change, sort_order=sort_order))

    def update_label(self):
        text = u'{}; {}'.format(self.controller.filter_by.label, self.controller.arrange_by.label)
        self.SetLabel(text)


class SettingsProperty(object):

    def __init__(self, key, default = None, deserialize = None, serialize = None, on_change = None):
        parts = key.split('.')
        if len(parts) > 1:
            group = parts[:-1]
            key = parts[-1]
        else:
            raise ValueError('You must have the settings group in the key, f.ex. "char.ui.some_key"')
        self.key = key
        self.default = default
        self._group = group
        self._deserialize = None
        self._serialize = None
        self._on_change = None
        self._settings = None
        if deserialize:
            self._deserialize = lambda obj, value: deserialize(value)
        if serialize:
            self._serialize = lambda obj, value: serialize(value)
        if on_change:
            self._on_change = lambda obj: on_change()

    @property
    def deserialize(self):

        def deco(func):
            self._deserialize = func
            return self

        return deco

    @property
    def serialize(self):

        def deco(func):
            self._setter = func
            return self

        return deco

    @property
    def on_change(self):

        def deco(func):
            self._on_change = func
            return self

        return deco

    @property
    def settings(self):
        if self._settings is None:
            import __builtin__
            settings = __builtin__.settings
            for group in self._group:
                settings = getattr(settings, group)

            self._settings = settings
        return self._settings

    def __get__(self, obj, obj_type = None):
        if obj is None:
            return self
        value = self.settings.Get(self.key, self.default)
        if self._deserialize:
            value = self._deserialize(obj, value)
        return value

    def __set__(self, obj, value):
        current = self.__get__(obj)
        if value == current:
            return
        if self._serialize:
            value = self._serialize(obj, value)
        self.settings.Set(self.key, value)
        if self._on_change:
            self._on_change(obj)

    def __delete__(self, obj):
        self.settings.Delete(self.key)


def enum_settings_property(enum, key, default):
    return SettingsProperty(key=key, default=default, serialize=lambda e: e.value, deserialize=enum)


class JumpClonePanelController(object):
    __notifyevents__ = ['OnCloneJumpUpdate', 'OnSessionChanged', 'OnSkillsChanged']

    def __init__(self):
        self.on_update = signals.Signal(signalName='on_update')
        self.on_filter_change = signals.Signal(signalName='on_filter_change')
        self.on_expand = signals.Signal(signalName='on_expand')
        self.on_collapse = signals.Signal(signalName='on_collapse')
        sm.RegisterNotify(self)
        if not self.is_jump_available:
            self._jump_cooldown_thread()

    @property
    def clones(self):
        clones = []
        for clone_info in self._clone_jump_service.GetClones():
            implants = self._clone_jump_service.GetImplantsForClone(clone_info.jumpCloneID)
            clone = JumpClone(clone_id=clone_info.jumpCloneID, location_id=clone_info.locationID, name=clone_info.cloneName, implants=[ implant.typeID for implant in implants or [] ])
            clones.append(clone)

        return clones

    @property
    def clones_filtered_and_sorted(self):

        def filter_criteria(clone):
            if self.filter_by == FilterBy.all:
                return True
            elif self.filter_by == FilterBy.station:
                return clone.in_station
            elif self.filter_by == FilterBy.structure:
                return clone.in_structure
            elif self.filter_by == FilterBy.ship:
                return clone.in_ship
            else:
                return False

        def sort_key(clone):
            if self.arrange_by == ArrangeBy.location:
                primary_key = clone.location_name.lower()
                secondary_key = clone.name
            elif self.arrange_by == ArrangeBy.name:
                primary_key = clone.name.lower()
                secondary_key = clone.location_name
            elif self.arrange_by == ArrangeBy.implant_count:
                primary_key = len(clone.implants)
                secondary_key = clone.location_name
            current_location_key = not clone.in_current_location if self.sort_order == SortOrder.ascending else clone.in_current_location
            return (current_location_key, primary_key, secondary_key.lower())

        return sorted(filter(filter_criteria, self.clones), key=sort_key, reverse=self.sort_order == SortOrder.descending)

    @property
    def clone_count(self):
        return len(self.clones)

    @property
    def clone_limit(self):
        dogma_location = sm.GetService('clientDogmaIM').GetDogmaLocation()
        dogma_location.WaitForShip()
        return int(dogma_location.GetAttributeValue(session.charid, dogma.const.attributeMaxJumpClones))

    @property
    def is_jump_available(self):
        return self.remaining_time_until_next_jump.total_seconds() <= 0

    @property
    def last_jump_timestamp(self):
        last_jump_filetime = self._clone_jump_service.LastCloneJumpTime()
        if last_jump_filetime:
            return datetimeutils.filetime_to_datetime(last_jump_filetime)

    @property
    def next_jump_timestamp(self):
        if self.last_jump_timestamp:
            return self.last_jump_timestamp + self.jump_cooldown_duration

    @property
    def remaining_time_until_next_jump(self):
        if self.next_jump_timestamp is None:
            return datetime.timedelta()
        now = datetime.datetime.utcnow()
        if self.next_jump_timestamp < now:
            return datetime.timedelta()
        return self.next_jump_timestamp - now

    @property
    def jump_cooldown_duration(self):
        character = sm.GetService('godma').GetStateManager().GetItem(session.charid, waitForPrime=True)
        return datetime.timedelta(hours=int(round(character.cloneJumpCoolDown)))

    @property
    def clone_count_installed_here(self):
        return len(filter(lambda clone: clone.location_id in (session.stationid, session.structureid), self.clones))

    @property
    def is_clone_installed_here(self):
        return self.clone_count_installed_here > 0

    @property
    def is_docked(self):
        return SessionChecker(session, sm).IsPilotDocked()

    @property
    def location_id(self):
        return session.structureid or session.stationid

    @property
    def _clone_jump_service(self):
        return sm.GetService('clonejump')

    filter_by = enum_settings_property(FilterBy, key='char.ui.jump_clones_panel_filter_by', default=FilterBy.all)

    @filter_by.on_change
    def filter_by(self):
        self.on_filter_change()

    arrange_by = enum_settings_property(ArrangeBy, key='char.ui.jump_clones_panel_arrange_by', default=ArrangeBy.location)

    @arrange_by.on_change
    def arrange_by(self):
        self.on_filter_change()

    sort_order = enum_settings_property(SortOrder, key='char.ui.jump_clones_panel_sort_order', default=SortOrder.ascending)

    @sort_order.on_change
    def sort_order(self):
        self.on_filter_change()

    expanded_clone_ids = SettingsProperty(key='char.ui.jump_clones_panel_expanded_clone_ids', default=None, deserialize=lambda value: (tuple() if value is None else value), serialize=lambda value: tuple(value))

    def is_expanded(self, clone_id):
        return clone_id in self.expanded_clone_ids

    def expand(self, clone_id):
        existing_clone_ids = [ clone.id for clone in self.clones ]
        expanded_clone_ids = set((cid for cid in self.expanded_clone_ids if cid in existing_clone_ids))
        expanded_clone_ids.add(clone_id)
        self.expanded_clone_ids = tuple(expanded_clone_ids)
        self.on_expand(clone_id)

    def collapse(self, clone_id):
        existing_clone_ids = [ clone.id for clone in self.clones ]
        self.expanded_clone_ids = tuple((cid for cid in self.expanded_clone_ids if cid != clone_id and cid in existing_clone_ids))
        self.on_collapse(clone_id)

    def toggle_expanded(self, clone_id):
        if self.is_expanded(clone_id):
            self.collapse(clone_id)
        else:
            self.expand(clone_id)

    def pre_load(self):
        clones = self.clones
        cfg.evelocations.Prime([ clone.location_id for clone in clones ])
        self.clone_limit
        self.is_jump_available

    def close(self):
        sm.UnregisterNotify(self)
        self._jump_cooldown_thread.kill_thread_maybe()

    def can_jump_to(self, clone):
        return len(self.validate_jump_to(clone)) == 0

    def jump(self, clone):
        self._clone_jump_service.CloneJump(clone.location_id, clone.id)

    def destroy(self, clone):
        self._clone_jump_service.DestroyInstalledClone(clone.id)

    def rename(self, clone):
        new_name = utilWindows.NamePopup(localization.GetByLabel('UI/Menusvc/SetName'), localization.GetByLabel('UI/Menusvc/TypeInNewName'), setvalue=clone.name, maxLength=100)
        if new_name:
            self._clone_jump_service.SetJumpCloneName(clone.id, new_name)

    def install(self):
        self._clone_jump_service.InstallCloneInStation()

    def validate_jump_to(self, clone):
        errors = []
        checker = SessionChecker(session, sm)
        should_check_timer = not clone.in_current_location or clone.in_ship
        if should_check_timer and not self.is_jump_available:
            errors.append(jump_clone_label('JumpCooldownError'))
        if not checker.IsPilotDocked() or checker.IsPilotControllingStructure():
            errors.append(jump_clone_label('JumpNotDockedError'))
        if self._clone_jump_service.IsCloneJumping():
            if self._clone_jump_service.IsJumpingIntoClone(clone.id):
                errors.append(jump_clone_label('CurrentlyJumpingToThisCloneError'))
            else:
                errors.append(jump_clone_label('CurrentlyJumpingToAnotherError'))
        return errors

    def validate_install_clone(self):
        checker = SessionChecker(session, sm)
        if not checker.IsPilotDocked():
            return [jump_clone_label('JumpNotDockedError')]
        return self._clone_jump_service.ValidateInstallJumpClone()

    def get_jump_label(self, cloneID):
        if self._clone_jump_service.IsJumpingIntoClone(cloneID):
            return jump_clone_label('Jumping')
        return jump_clone_label('Jump')

    @threadutils.highlander_threaded
    def _jump_cooldown_thread(self):
        while not self.is_jump_available:
            uthread2.sleep(max(1.0, self.remaining_time_until_next_jump.total_seconds()))

        self.on_update()

    def OnCloneJumpUpdate(self):
        uthread2.start_tasklet(self.on_update)

    def OnSessionChanged(self, isRemote, sess, change):
        uthread2.start_tasklet(self.on_update)

    def OnSkillsChanged(self, skillInfos):
        for type_id, skill in skillInfos.iteritems():
            if type_id in JUMP_CLONE_SKILLS:
                uthread2.start_tasklet(self.on_update)
                return


class JumpClone(object):

    def __init__(self, clone_id, location_id, name, implants):
        self.id = clone_id
        self.location_id = location_id
        self._name = name
        self.implants = implants

    @property
    def name(self):
        return self._name or self.default_name

    @name.setter
    def name(self, name):
        self._name = name

    @caching.lazy_property
    def default_name(self):
        alphabet = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        generator = random.Random(self.id)
        identity = u''.join([ generator.choice(alphabet) for x in range(4) ])
        return jump_clone_label('DefaultCloneName', identity=identity)

    @caching.lazy_property
    def location_name(self):
        try:
            return cfg.evelocations.Get(self.location_id).name
        except KeyError:
            return jump_clone_label('DestroyedLocation')

    @caching.lazy_property
    def has_implants(self):
        return len(self.implants) > 0

    @caching.lazy_property
    def in_station(self):
        return IsStation(self.location_id)

    @caching.lazy_property
    def in_structure(self):
        return sm.GetService('structureDirectory').IsStructure(self.location_id)

    @caching.lazy_property
    def in_ship(self):
        return not (self.in_station or self.in_structure)

    @property
    def in_current_location(self):
        return self.location_id in (session.stationid, session.structureid)


class ErrorMessage(containerAutoSize.ContainerAutoSize):

    def __init__(self, **kwargs):
        kwargs.setdefault('width', 300)
        super(ErrorMessage, self).__init__(**kwargs)
        self.icon = sprite.Sprite(parent=container.Container(parent=self, align=uiconst.TOTOP, height=64), align=uiconst.CENTER, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/WindowIcons/aggression.png', width=64, height=64)
        eveLabel.EveCaptionMedium(parent=self, align=uiconst.TOTOP, text=eveformat.center(jump_clone_label('UnknownErrorTitle')))
        self.label = eveLabel.EveLabelMedium(parent=self, align=uiconst.TOTOP)

    def SetText(self, text):
        self.label.SetText(eveformat.center(text))


class JumpCloneEntry(containerAutoSize.ContainerAutoSize):
    default_minHeight = 64
    default_alignMode = uiconst.TOTOP

    def __init__(self, controller, clone, jump_errors, on_expand = None, **kwargs):
        super(JumpCloneEntry, self).__init__(**kwargs)
        self.controller = controller
        self.clone = clone
        self.jump_errors = jump_errors
        self.implant_list = None
        self.on_expand_anim_finished = signals.Signal(signalName='on_expand_anim_finished')
        self.layout()
        if on_expand is not None:
            self.on_expand_anim_finished.connect(on_expand)
        self.controller.on_expand.connect(self.on_expand)
        self.controller.on_collapse.connect(self.on_collapse)

    def layout(self):
        if self.clone.in_current_location:
            in_current_location_cont = containerAutoSize.ContainerAutoSize(parent=self, align=uiconst.TOTOP)
            themeColored.FillThemeColored(bgParent=in_current_location_cont, colorType=uiconst.COLORTYPE_UIHILIGHT, opacity=0.1)
            eveLabel.EveLabelMediumBold(parent=in_current_location_cont, align=uiconst.TOPLEFT, padding=(8, 4, 8, 4), text=jump_clone_label('InCurrentStation'))
            themeColored.FillThemeColored(bgParent=self, colorType=uiconst.COLORTYPE_UIHILIGHT, opacity=0.1)
        else:
            themeColored.FillThemeColored(bgParent=self, colorType=uiconst.COLORTYPE_UIBASECONTRAST)
        jump_clone_icon = JumpCloneIcon(parent=container.Container(parent=self, align=uiconst.TOLEFT, width=64, padRight=8), align=uiconst.CENTERTOP, top=4, clone=self.clone, state=uiconst.UI_NORMAL)
        top_cont = containerAutoSize.ContainerAutoSize(parent=self, align=uiconst.TOTOP, alignMode=uiconst.TOTOP)
        top_right_cont = containerAutoSize.ContainerAutoSize(parent=top_cont, align=uiconst.TORIGHT)
        eveLabel.EveLabelLarge(parent=top_cont, align=uiconst.TOTOP, padTop=4, text=self.clone.name)
        if self.clone.in_ship:
            location_text = self.clone.location_name
        else:
            location_text = evelink.location_link(self.clone.location_id)
        location_text = jump_clone_label('CloneLocationPrefix', location=location_text)
        eveLabel.EveLabelMedium(parent=top_cont, align=uiconst.TOTOP, state=uiconst.UI_NORMAL, text=location_text)
        if len(self.clone.implants) == 0:
            eveLabel.EveLabelMedium(parent=self, align=uiconst.TOTOP, padding=(0, 8, 0, 8), text=jump_clone_label('NoImplantsInstalled'), color=TextColor.DISABLED)
        else:
            ImplantsOverview(parent=containerAutoSize.ContainerAutoSize(parent=self, align=uiconst.TOTOP, padding=(0, 8, 0, 8)), align=uiconst.TOPLEFT, controller=self.controller, clone=self.clone)
        button_cont = ButtonGroup(parent=top_right_cont, align=uiconst.TOPLEFT, padding=8)
        jump_button = Button(parent=button_cont, label=self.controller.get_jump_label(self.clone.id), func=lambda button: self.controller.jump(self.clone))
        if self.jump_errors:
            jump_button.Disable()
            jump_button.LoadTooltipPanel = functools.partial(load_errors_tooltip, errors=self.jump_errors)
        Button(parent=button_cont, label=jump_clone_label('Rename'), variant=ButtonVariant.GHOST, func=lambda button: self.controller.rename(self.clone))
        Button(parent=button_cont, label=jump_clone_label('Destroy'), style=ButtonStyle.DANGER, variant=ButtonVariant.GHOST, func=lambda button: self.controller.destroy(self.clone))
        self.set_clone_value_hint(jump_clone_icon)
        if self.controller.is_expanded(self.clone.id):
            self.create_implant_list()

    def create_implant_list(self):
        self.implant_list = containerAutoSize.ContainerAutoSize(parent=self, align=uiconst.TOTOP, padBottom=8, clipChildren=True)
        self.implant_list.DisableAutoSize()
        for type_id in sorted(self.clone.implants, key=get_implant_slot):
            ImplantEntry(parent=self.implant_list, align=uiconst.TOTOP, type_id=type_id, padBottom=2)

        self.implant_list.EnableAutoSize()

    def on_expand(self, clone_id):
        if clone_id == self.clone.id:
            self.expand_implants()

    def on_collapse(self, clone_id):
        if clone_id == self.clone.id:
            self.collapse_implants()

    def expand_implants(self):
        if not self.clone.has_implants:
            return
        self.create_implant_list()
        self.implant_list.DisableAutoSize()
        self.implant_list.GetAbsoluteSize()

        def after_animation():
            self.implant_list.EnableAutoSize()
            self.on_expand_anim_finished(self)

        _, height = self.implant_list.GetAutoSize()
        animations.FadeTo(self.implant_list, startVal=0.0, endVal=1.0, duration=0.15)
        animations.MorphScalar(self.implant_list, 'height', endVal=height, duration=0.15, callback=after_animation)

    def collapse_implants(self):
        if self.implant_list:
            self.implant_list.DisableAutoSize()
            animations.FadeOut(self.implant_list, duration=0.15)
            animations.MorphScalar(self.implant_list, 'height', startVal=self.implant_list.height, endVal=0, duration=0.15, callback=self.implant_list.Close)
            self.implant_list = None

    def set_clone_value_hint(self, icon):
        if not self.clone.implants:
            icon.hint = jump_clone_label('EstimatedCloneLabel', cloneValue=FmtISK(0, 0))
            return
        total = 0
        for type_id in self.clone.implants:
            price = GetAveragePrice(type_id)
            if price:
                total += price

        if total:
            cloneValue = FmtISK(total, 0)
        else:
            cloneValue = localization.GetByLabel('UI/Common/Unknown')
        icon.hint = jump_clone_label('EstimatedCloneLabel', cloneValue=cloneValue)


class ImplantsOverview(layoutGrid.LayoutGrid):
    default_state = uiconst.UI_NORMAL
    EXPAND_ICON_OPACITY_IDLE = 0.25
    EXPAND_ICON_OPACITY_HOVER = 1.0

    def __init__(self, controller, clone, **kwargs):
        kwargs['columns'] = 2
        kwargs['cellSpacing'] = 4
        super(ImplantsOverview, self).__init__(**kwargs)
        self.controller = controller
        self.clone = clone
        self.expand_icon = None
        self.implant_cont = None
        self.layout()
        self.controller.on_expand.connect(self.on_expand)
        self.controller.on_collapse.connect(self.on_collapse)

    @property
    def is_expanded(self):
        return self.controller.is_expanded(self.clone.id)

    def layout(self):
        self.implant_cont = ContainerAutoSize(parent=self, align=uiconst.TOPLEFT, opacity=self.get_implant_opacity())
        self.expand_icon = themeColored.SpriteThemeColored(parent=container.Container(parent=self, align=uiconst.CENTER, pos=(0, 0, 16, 16)), align=uiconst.CENTER, state=uiconst.UI_DISABLED, width=9, height=9, texturePath='res:/UI/Texture/Shared/arrows/arrowLeft.png', rotation=self.get_icon_rotation(), colorType=uiconst.COLORTYPE_UIHILIGHTGLOW, opacity=self.EXPAND_ICON_OPACITY_IDLE)
        icon_size = 24
        icon_gap = 2
        left = 0
        for type_id in sorted(self.clone.implants, key=get_implant_slot):
            icon = itemIcon.ItemIcon(parent=self.implant_cont, align=uiconst.TOPLEFT, pos=(left,
             0,
             icon_size,
             icon_size), typeID=type_id, showOmegaOverlay=False, showPrice=True)
            icon.techIcon.Disable()
            icon.techIcon.width = 12
            icon.techIcon.height = 12
            icon.OnClick = self.OnClick
            if self.is_expanded:
                icon.Disable()
            left += icon_size + icon_gap

    def on_expand(self, clone_id):
        if clone_id != self.clone.id:
            return
        self._update_implant_icons_state()
        self._anim_update_state()
        tooltipUtil.RefreshTooltipForOwner(self)

    def on_collapse(self, clone_id):
        if clone_id != self.clone.id:
            return
        self._update_implant_icons_state()
        self._anim_update_state()

    def _update_implant_icons_state(self):
        for implant_icon in self.implant_cont.children:
            if self.is_expanded:
                implant_icon.Disable()
            else:
                implant_icon.Enable()

    def _anim_update_state(self):
        animations.MorphScalar(self.expand_icon, 'rotation', startVal=self.expand_icon.rotation, endVal=self.get_icon_rotation(), duration=0.1)
        animations.FadeTo(self.implant_cont, startVal=self.implant_cont.opacity, endVal=self.get_implant_opacity(), duration=0.15)

    def get_icon_rotation(self):
        if self.is_expanded:
            return -math.pi / 2.0
        return math.pi / 2.0

    def get_implant_opacity(self):
        if self.is_expanded:
            return 0.1
        return 1.0

    def OnClick(self, *args):
        self.controller.toggle_expanded(self.clone.id)

    def OnMouseEnter(self):
        animations.FadeIn(self.expand_icon, endVal=self.EXPAND_ICON_OPACITY_HOVER, duration=0.15)

    def OnMouseExit(self):
        animations.FadeTo(self.expand_icon, startVal=self.expand_icon.opacity, endVal=self.EXPAND_ICON_OPACITY_IDLE, duration=0.25)


class ImplantEntry(containerAutoSize.ContainerAutoSize):
    default_alignMode = uiconst.TOPLEFT

    def __init__(self, type_id, **kwargs):
        super(ImplantEntry, self).__init__(**kwargs)
        self.type_id = type_id
        self.info_icon = None
        self.label = None
        self.label_cont = None
        self.layout()

    def layout(self):
        icon = itemIcon.ItemIcon(parent=self, align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED, height=16, width=16, typeID=self.type_id, showOmegaOverlay=False)
        icon.techIcon.width = 6
        icon.techIcon.height = 6
        self.label_cont = containerAutoSize.ContainerAutoSize(parent=self, align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL, left=20, clipChildren=True)
        self.label_cont.GetMenu = self.GetMenu
        self.label_cont.GetHint = self.GetHint
        self.label_cont.tooltipPointer = uiconst.POINT_LEFT_1
        self.label = eveLabel.EveLabelMedium(parent=self.label_cont, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, text=evetypes.GetName(self.type_id), autoFadeSides=16)
        self.info_icon = infoIcon.InfoIcon(parent=self, align=uiconst.CENTERLEFT, typeID=self.type_id)

    def GetMenu(self):
        return sm.GetService('menu').GetMenuFromItemIDTypeID(itemID=None, typeID=self.type_id, includeMarketDetails=True)

    def GetHint(self):
        ret = u'{}<br>{}'.format(eveformat.bold(evetypes.GetName(self.type_id)), evetypes.GetDescription(self.type_id))
        price = GetAveragePrice(self.type_id)
        if price:
            ret += '\n\n%s' % localization.GetByLabel('UI/SkillTrading/EstimatedPrice', price=FmtISK(price, False))
        return ret

    def UpdateAlignment(self, budgetLeft = 0, budgetTop = 0, budgetWidth = 0, budgetHeight = 0, updateChildrenOnly = False):
        self.label_cont.maxWidth = budgetWidth - self.label_cont.left - self.info_icon.width - 4
        budget = super(ImplantEntry, self).UpdateAlignment(budgetLeft=budgetLeft, budgetTop=budgetTop, budgetWidth=budgetWidth, budgetHeight=budgetHeight, updateChildrenOnly=updateChildrenOnly)
        self.info_icon.left = self.label_cont.left + self.label_cont.width + 4
        return budget


class JumpCloneIcon(container.Container):
    default_height = 64
    default_width = 64

    def __init__(self, clone, **kwargs):
        super(JumpCloneIcon, self).__init__(**kwargs)
        self.clone = clone
        self.layout()

    def layout(self):
        sprite.Sprite(parent=self, align=uiconst.TOALL, state=uiconst.UI_DISABLED, texturePath='res:/ui/Texture/Icons/127_64_1.png', spriteEffect=trinity.TR2_SFX_COLOROVERLAY, color=self.generate_clone_color())
        if self.clone.in_ship:
            sprite.Sprite(parent=self, align=uiconst.BOTTOMRIGHT, width=32, height=32, texturePath='res:/UI/Texture/Shared/circularGradient.png', rotation=-math.pi / 2.0, color=(0.0, 0.0, 0.0), idx=0, opacity=0.5)
            sprite.Sprite(parent=self, align=uiconst.BOTTOMRIGHT, width=32, height=32, texturePath='res:/UI/Texture/Icons/9_64_5.png', hint=jump_clone_label('CloneInShipHint'), idx=0)

    def generate_clone_color(self):
        r = random.Random(self.clone.id)
        return (r.random() * 0.4 + 0.4, r.random() * 0.1 + 0.4, r.random() * 0.2 + 0.4)


def load_errors_tooltip(panel, parent, errors):
    if not errors:
        return
    panel.LoadGeneric1ColumnTemplate()
    panel.margin = (8, 8, 8, 8)
    panel.cellSpacing = (0, 4)
    for error in errors:
        label = panel.AddLabelMedium(text=error, wrapWidth=300, padding=(8, 4, 8, 4))
        sprite.Sprite(bgParent=label.parent, texturePath='res:/UI/Texture/Classes/Industry/Output/hatchPattern.png', tileX=True, tileY=True, color=eveColor.DANGER_RED, opacity=0.1)


def load_clone_implants_tooltip(panel, parent, clone):
    panel.LoadGeneric1ColumnTemplate()
    panel.margin = (8, 8, 8, 8)
    if not clone.has_implants:
        panel.AddLabelMedium(text=jump_clone_label('NoImplantsInstalled'))
        return
    list_cont = containerAutoSize.ContainerAutoSize(width=260)
    panel.state = uiconst.UI_NORMAL
    for i, type_id in enumerate(sorted(clone.implants, key=get_implant_slot)):
        ItemEntry(parent=list_cont, align=uiconst.TOTOP, typeID=type_id, padTop=8 if i > 0 else 0)

    panel.AddCell(list_cont)


def get_implant_slot(type_id):
    return getattr(sm.GetService('godma').GetType(type_id), 'implantness', None)


class ItemEntry(containerAutoSize.ContainerAutoSize):
    default_alignMode = uiconst.TOTOP
    default_state = uiconst.UI_NORMAL
    default_minHeight = 32

    def ApplyAttributes(self, attributes):
        super(ItemEntry, self).ApplyAttributes(attributes)
        self.typeID = attributes.typeID
        itemIcon.ItemIcon(parent=container.Container(parent=self, align=uiconst.TOLEFT, width=32), align=uiconst.CENTERTOP, state=uiconst.UI_DISABLED, pos=(0, 0, 32, 32), typeID=self.typeID)
        infoIcon.InfoIcon(parent=container.Container(parent=self, align=uiconst.TORIGHT, width=16), align=uiconst.CENTERTOP, top=8, typeID=self.typeID)
        eveLabel.EveLabelMedium(parent=VerticalCenteredContainer(parent=self, align=uiconst.TOTOP, minHeight=32), align=uiconst.TOTOP, padding=(8, 0, 8, 0), text=evetypes.GetName(self.typeID))

    def GetMenu(self):
        return GetMenuService().GetMenuFromItemIDTypeID(None, self.typeID, includeMarketDetails=True)


class VerticalCenteredContainer(containerAutoSize.ContainerAutoSize):

    def __init__(self, **kwargs):
        kwargs['callback'] = self.on_size_change
        super(VerticalCenteredContainer, self).__init__(**kwargs)

    def on_size_change(self):
        if self.children:
            content_height = 0
            for i, child in enumerate(self.children):
                content_height += child.height + child.padTop + child.padBottom
                if i > 0:
                    content_height += child.top

            adjusted_top = int(round((self.height - content_height) / 2.0))
            self.children[0].top = adjusted_top


class JumpCooldownBanner(containerAutoSize.ContainerAutoSize):
    default_name = 'JumpCooldownBanner'
    default_alignMode = uiconst.TOTOP

    def __init__(self, controller, **kwargs):
        super(JumpCooldownBanner, self).__init__(**kwargs)
        self.controller = controller
        self.layout()
        self.update_state()
        self.controller.on_update.connect(self.update_state)

    def layout(self):
        self.frame = themeColored.FrameThemeColored(bgParent=self, texturePath='res:/UI/Texture/Shared/DarkStyle/panel2Corner_Solid.png', cornerSize=9, colorType=uiconst.COLORTYPE_UIHILIGHT, opacity=0.15)
        self.corner = themeColored.SpriteThemeColored(parent=self, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/Shared/DarkStyle/cornerTriSmall.png', width=5, height=5, colorType=uiconst.COLORTYPE_UIHILIGHT, opacity=0.5)
        self.icon = themeColored.SpriteThemeColored(parent=self, align=uiconst.CENTERLEFT, state=uiconst.UI_HIDDEN, width=32, height=32, left=10, texturePath='res:/UI/Texture/classes/agency/iconExclamation.png', colorType=uiconst.COLORTYPE_UIHILIGHT)
        self.label = eveLabel.EveLabelMedium(parent=self, align=uiconst.TOTOP, state=uiconst.UI_DISABLED, padding=(16, 8, 8, 8))
        more_info = infoIcon.MoreInfoIcon(parent=self, align=uiconst.CENTERRIGHT, left=16)
        more_info.LoadTooltipPanel = self.LoadInfoTooltip

    def update_state(self):
        self._update_state_inner()
        self._auto_update_state()

    def LoadInfoTooltip(self, panel, parent):
        panel.state = uiconst.UI_NORMAL
        panel.LoadGeneric2ColumnTemplate()
        panel.margin = (8, 8, 8, 8)
        cooldown_hours = int(self.controller.jump_cooldown_duration.total_seconds() / 3600)
        panel.AddLabelMedium(text=jump_clone_label('JumpCooldownHint', cooldown=cooldown_hours, color=eveThemeColor.THEME_ACCENT.hex_argb), colSpan=2, width=300)
        panel.AddSpacer(height=8, colSpan=2)
        for type_id in CLONE_JUMP_COOLDOWN_SKILLS:
            panel.AddRow(rowClass=infoBubble.SkillEntry, typeID=type_id, level=0, showLevel=False, skillBarPadding=(24, 8, 0, 8))

    def _update_state_inner(self):
        if not self.controller.is_jump_available:
            self.label.SetText(u'{}\n{}'.format(jump_clone_label('NextCloneJump'), localization.formatters.FormatTimeIntervalShortWritten(datetimeutils.timedelta_to_filetime_delta(self.controller.remaining_time_until_next_jump), showFrom='day', showTo='second')))
            self.label.padLeft = 52
            self.icon.display = True
            self.set_color(eveColor.WARNING_ORANGE)
        else:
            self.label.SetText(jump_clone_label('CloneJumpAvailable'))
            self.label.padLeft = 16
            self.icon.display = False
            self.set_color(None)

    def set_color(self, color):
        self.frame.SetFixedColor(color)
        self.corner.SetFixedColor(color)
        self.icon.SetFixedColor(color)
        if color is None:
            self.label.SetRGBA(*self.label.default_color)
        else:
            self.label.SetRGBA(*color)

    @threadutils.highlander_threaded
    def _auto_update_state(self):
        while not self.destroyed:
            self._update_state_inner()
            if self.controller.is_jump_available:
                return
            uthread2.sleep(1.0)


class InstallCloneBanner(containerAutoSize.ContainerAutoSize):
    default_alignMode = uiconst.TOTOP

    def __init__(self, controller, **kwargs):
        super(InstallCloneBanner, self).__init__(**kwargs)
        self.controller = controller
        self.label = None
        self.install_button = None
        self.layout()
        self.update()
        self.controller.on_update.connect(self.update)

    def layout(self):
        themeColored.FrameThemeColored(parent=self, texturePath='res:/UI/Texture/Shared/DarkStyle/panel2Corner_Solid.png', cornerSize=9, colorType=uiconst.COLORTYPE_UIHILIGHT, opacity=0.15)
        themeColored.SpriteThemeColored(parent=self, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/Shared/DarkStyle/cornerTriSmall.png', width=5, height=5, colorType=uiconst.COLORTYPE_UIHILIGHT, opacity=0.5)
        button_cont = containerAutoSize.ContainerAutoSize(parent=self, align=uiconst.TORIGHT, padding=(16, 8, 16, 8))
        self.install_button = Button(parent=button_cont, align=uiconst.CENTER, label=localization.GetByLabel('UI/Medical/InstallJumpClone'), func=lambda button: self.controller.install())
        self.install_button.Disable()
        self.label = eveLabel.EveLabelMedium(parent=self, align=uiconst.TOTOP, state=uiconst.UI_NORMAL, padding=(16, 8, 0, 8))

    def get_text(self):
        if not self.controller.is_docked:
            return eveformat.color(jump_clone_label('NotDocked'), color=COLOR_TEXT_SECONDARY)
        else:
            docked_in = jump_clone_label('DockedIn', location=evelink.location_link(self.controller.location_id))
            if self.controller.is_clone_installed_here:
                subtext = jump_clone_label('InstalledCloneCount', clone_count=self.controller.clone_count_installed_here)
            else:
                subtext = localization.GetByLabel('UI/Medical/NoJumpCloneInstalled')
            return u'{}<br>{}'.format(docked_in, subtext)

    @threadutils.highlander_threaded
    def update(self):
        self.label.SetText(self.get_text())
        errors = self.controller.validate_install_clone()
        if errors:
            self.install_button.Disable()
            self.install_button.LoadTooltipPanel = functools.partial(load_errors_tooltip, errors=errors)
        else:
            self.install_button.Enable()
            self.install_button.LoadTooltipPanel = None
