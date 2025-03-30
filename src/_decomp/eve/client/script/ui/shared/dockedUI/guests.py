#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\dockedUI\guests.py
import eveicon
import logging
import blue
import localization
import signals
import uthread2
import utillib
from bannedwords.client import bannedwords
from carbon.common.script.sys.serviceManager import ServiceManager
from carbonui import Density, uiconst
from carbonui.control.basicDynamicScroll import BasicDynamicScroll
from carbonui.control.contextMenu.menuData import MenuData
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.services.setting import UserSettingBool
from carbonui.util.various_unsorted import SortListOfTuples
from eve.client.script.ui.control.entries.util import GetFromClass
from carbonui.button.menu import MenuButtonIcon
from eve.client.script.ui.quickFilter import QuickFilterEdit
from eve.client.script.ui.shared.userentry import User, UserSimple
from eve.common.script.sys import idCheckers
logger = logging.getLogger(__name__)
guest_list_compact_mode_setting = UserSettingBool('guestCondensedUserList', False)

class LoadState(object):
    UNLOADED = 1
    LOADING = 2
    UNLOAD_PENDING = 3
    LOADED = 4
    ERROR = 5


class GuestsPanelController(object):
    __notifyevents__ = ('OnCharNoLongerInStation', 'OnCharNowInStation', 'OnCharacterEnteredStructure', 'OnCharacterLeftStructure', 'OnSessionChanged')
    _guest_list = None
    _location_id = None

    def __init__(self):
        self._load_state = LoadState.UNLOADED
        self._guests_pending_add = {}
        self._guests_pending_remove = set()
        self.on_guest_list_changed = signals.Signal('{}.on_guest_list_changed'.format(self.__class__.__name__))
        self.on_loading_changed = signals.Signal('{}.on_loading_changed'.format(self.__class__.__name__))
        self.on_guest_count_changed = signals.Signal('{}.on_guest_count_changed'.format(self.__class__.__name__))

    @property
    def guest_list(self):
        if self._load_state == LoadState.LOADED:
            return self._guest_list

    @property
    def guest_count(self):
        if self._load_state == LoadState.LOADED:
            return len(self._guest_list.guests)
        else:
            return 0

    @property
    def loading(self):
        return self._load_state in {LoadState.LOADING, LoadState.UNLOAD_PENDING}

    def load(self):
        if self._load_state == LoadState.UNLOADED:
            ServiceManager.Instance().RegisterNotify(self)
            self._load_guest_list(location_id=self._get_location_id_from_session(session))

    def unload(self):
        if self._load_state == LoadState.LOADING:
            self._set_load_state(LoadState.UNLOAD_PENDING)
        else:
            ServiceManager.Instance().UnregisterNotify(self)
            self._guests_pending_add.clear()
            self._guests_pending_remove.clear()
            self._guest_list = None
            self._set_load_state(LoadState.UNLOADED)
            self.on_guest_list_changed(self)
            self.on_guest_count_changed(self)

    def _set_load_state(self, value):
        if self._load_state != value:
            was_loading = self.loading
            self._load_state = value
            if self.loading != was_loading:
                self.on_loading_changed(self)

    @staticmethod
    def _get_station_guests():
        guests_raw = ServiceManager.Instance().GetService('station').GetGuests()
        return [ Guest(character_id, corporation_id, alliance_id, war_faction_id) for character_id, (corporation_id, alliance_id, war_faction_id) in guests_raw.items() ]

    @staticmethod
    def _get_structure_guests():
        guests_raw = ServiceManager.Instance().GetService('structureGuests').GetGuests()
        return [ Guest(character_id, corporation_id, alliance_id, war_faction_id) for character_id, (corporation_id, alliance_id, war_faction_id) in guests_raw.items() ]

    def _load_guest_list(self, location_id):
        if self._location_id == location_id:
            return
        self._location_id = location_id
        self._guests_pending_add.clear()
        self._guests_pending_remove.clear()
        self._set_load_state(LoadState.LOADING)
        try:
            guest_list = None
            if idCheckers.IsStation(location_id):
                guest_list = GuestList(location_id=session.stationid, guests=self._get_station_guests())
            elif location_id is not None:
                guest_list = GuestList(location_id=session.structureid, guests=self._get_structure_guests())
            if self._location_id != location_id:
                return
            if self._load_state == LoadState.UNLOAD_PENDING:
                self.unload()
                return
            if guest_list is not None:
                for guest in self._guests_pending_add.values():
                    guest_list.add(guest)

                for character_id in self._guests_pending_remove:
                    guest_list.discard(character_id)

            self._guests_pending_add.clear()
            self._guests_pending_remove.clear()
        except Exception:
            logger.exception('Unhandled exception while attempting to load a guest list')
            if self._location_id == location_id:
                self._set_load_state(LoadState.ERROR)
                self.unload()
        else:
            self._guest_list = guest_list
            if guest_list is not None:
                self._set_load_state(LoadState.LOADED)
            else:
                self._set_load_state(LoadState.UNLOADED)
            self.on_guest_list_changed(self)
            self.on_guest_count_changed(self)

    @staticmethod
    def _get_location_id_from_session(session):
        if session.stationid:
            return session.stationid
        elif session.structureid:
            return session.structureid
        else:
            return None

    def _add_guest(self, guest):
        if self.loading:
            self._guests_pending_remove.discard(guest.character_id)
            self._guests_pending_add[guest.character_id] = guest
        elif self._load_state == LoadState.LOADED:
            self._guest_list.add(guest)
            self.on_guest_count_changed(self)

    def _remove_guest(self, character_id):
        if self.loading:
            if character_id in self._guests_pending_add:
                self._guests_pending_add.pop(character_id)
            self._guests_pending_remove.add(character_id)
        elif self._load_state == LoadState.LOADED:
            self._guest_list.discard(character_id)
            self.on_guest_count_changed(self)

    def OnCharNowInStation(self, rec):
        character_id, corporation_id, alliance_id, war_faction_id = rec
        self._add_guest(Guest(character_id, corporation_id, alliance_id, war_faction_id))

    def OnCharNoLongerInStation(self, rec):
        self._remove_guest(character_id=rec[0])

    def OnCharacterEnteredStructure(self, characterID, corporationID, allianceID, factionID):
        self._add_guest(Guest(character_id=characterID, corporation_id=corporationID, alliance_id=allianceID, war_faction_id=factionID))

    def OnCharacterLeftStructure(self, characterID):
        self._remove_guest(character_id=characterID)

    def OnSessionChanged(self, isRemote, session, change):
        if any((name in change for name in ('stationid', 'structureid'))):
            uthread2.start_tasklet(self._load_guest_list, location_id=self._get_location_id_from_session(session))


class GuestsPanel(Container):
    _loaded = False
    _quick_filter = None
    _scroll = None
    _scroll_update_id = 0

    def __init__(self, controller = None, **kwargs):
        self._controller = controller or GuestsPanelController()
        super(GuestsPanel, self).__init__(**kwargs)

    def LoadPanel(self):
        if not self._loaded:
            self._loaded = True
            self._layout()
            self._subscribe()
            uthread2.start_tasklet(self._load)

    def _load(self):
        self._controller.load()
        self._update_scroll_content()

    def _layout(self):
        top_cont = ContainerAutoSize(parent=self, align=uiconst.TOTOP, alignMode=uiconst.TOPLEFT)
        self._quick_filter = QuickFilterEdit(name='quickFilterEdit', parent=top_cont, align=uiconst.TOPLEFT, isCharacterField=True, density=Density.COMPACT)
        self._quick_filter.ReloadFunction = self._update_scroll_filter
        self._scroll = BasicDynamicScroll(parent=self, padTop=8)
        self._update_scroll_loading()
        MenuButtonIcon(parent=top_cont, align=uiconst.CENTERRIGHT, get_menu_func=get_guest_list_settings, texturePath=eveicon.people, hint=localization.GetByLabel('UI/Chat/UserlistSettingButtonHint'), width=16, height=16, iconSize=16)

    def _update_scroll_filter(self):
        filter_query = self._quick_filter.GetValue()
        if len(filter_query):
            bannedwords.check_search_words_allowed(filter_query)
        self._update_scroll_content()

    def _update_scroll_loading(self):
        if self._scroll:
            if self._controller.loading:
                self._scroll.ShowLoading()

    def _update_scroll_content(self):
        if not self._scroll or self._scroll.destroyed:
            return
        scroll_update_id = self._allocate_scroll_update_id()
        guest_list = self._controller.guest_list
        if guest_list is None:
            self._location_id = None
            self._scroll.Clear()
            self._scroll.HideLoading()
        else:
            self._location_id = guest_list.location_id
            guest_list.on_guest_added.connect(self._on_guest_list_guest_added)
            guest_list.on_guest_removed.connect(self._on_guest_list_guest_removed)
            guests = self._get_filtered_guests(guest_list.guests)
            entries = self._get_guest_entries(guests)
            if self._scroll_update_id == scroll_update_id:
                if self._scroll.destroyed:
                    return
                self._scroll.Clear()
                self._scroll.AddNodes(0, entries)
                self._scroll.HideLoading()

    def _allocate_scroll_update_id(self):
        self._scroll_update_id += 1
        return self._scroll_update_id

    def _on_guest_list_guest_added(self, guest):
        self._add_guest_to_scroll(guest)

    def _on_guest_list_guest_removed(self, guest):
        self._remove_guest_from_scroll(guest)

    def _add_guest_to_scroll(self, guest):
        if not self._scroll or self._scroll.destroyed:
            return
        nodes = self._scroll.GetNodes()
        index = bisect_left(nodes, guest.name.lower(), key=lambda node: node.info.name.lower())
        entry = self._get_guest_entry(guest)
        self._scroll.AddNodes(index, [entry])

    def _remove_guest_from_scroll(self, guest):
        if self._scroll and not self._scroll.destroyed:
            for node in self._scroll.GetNodes():
                if node.charID == guest.character_id:
                    self._scroll.RemoveNodes([node])

    def _get_filtered_guests(self, guests):
        cfg.eveowners.Prime([ guest.character_id for guest in guests ])
        filter_query = self._quick_filter.GetValue()
        if len(filter_query):
            filtered_guests = []
            for guest in guests:
                if self._quick_filter.QuickFilter(rec=utillib.KeyVal(name=guest.name.lower())):
                    filtered_guests.append(guest)
                blue.pyos.BeNice()

            return filtered_guests
        else:
            return guests

    def _get_guest_entries(self, guests):
        owner_ids = [ guest.character_id for guest in guests ]
        cfg.eveowners.Prime(owner_ids)
        entries = []
        for guest in guests:
            entries.append((guest.name.lower(), self._get_guest_entry(guest)))
            blue.pyos.BeNice()

        return SortListOfTuples(entries)

    @staticmethod
    def _get_guest_entry(guest):
        return GetFromClass(entryType=get_guest_entry_class(), data={'charID': guest.character_id,
         'info': cfg.eveowners.Get(guest.character_id),
         'label': guest.name,
         'corpID': guest.corporation_id,
         'allianceID': guest.alliance_id,
         'warFactionID': guest.war_faction_id})

    def _subscribe(self):
        guest_list_compact_mode_setting.on_change.connect(self._on_guest_list_compact_mode_changed)
        self._controller.on_guest_list_changed.connect(self._on_guest_list_changed)
        self._controller.on_loading_changed.connect(self._on_loading_changed)

    def _on_loading_changed(self, controller):
        self._update_scroll_loading()

    def _on_guest_list_changed(self, controller):
        uthread2.start_tasklet(self._update_scroll_content)

    def _on_guest_list_compact_mode_changed(self, value):
        uthread2.start_tasklet(self._update_scroll_content)


class GuestList(object):

    def __init__(self, location_id, guests = None):
        self._location_id = location_id
        self._guests = {}
        self.on_guest_added = signals.Signal('{}.on_guest_added'.format(self.__class__.__name__))
        self.on_guest_removed = signals.Signal('{}.on_guest_removed'.format(self.__class__.__name__))
        if guests:
            for guest in guests:
                self._guests[guest.character_id] = guest

    @property
    def guests(self):
        return self._guests.values()

    @property
    def guests_by_character_id(self):
        return self._guests.copy()

    @property
    def location_id(self):
        return self._location_id

    def add(self, guest):
        self._guests[guest.character_id] = guest
        self.on_guest_added(guest)

    def remove(self, character_id):
        guest = self._guests.pop(character_id)
        self.on_guest_removed(guest)
        return guest

    def discard(self, character_id):
        if character_id in self._guests:
            return self.remove(character_id)


class Guest(object):

    def __init__(self, character_id, corporation_id, alliance_id, war_faction_id):
        self.character_id = character_id
        self.corporation_id = corporation_id
        self.alliance_id = alliance_id
        self.war_faction_id = war_faction_id

    @property
    def name(self):
        return cfg.eveowners.Get(self.character_id).name

    @property
    def owner_info(self):
        return cfg.eveowners.Get(self.character_id)

    def __eq__(self, other):
        return isinstance(other, Guest) and self.character_id == other.character_id and self.corporation_id == other.corporation_id and self.alliance_id == other.alliance_id and self.war_faction_id == other.war_faction_id

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return self.character_id


def get_guest_list_settings():
    menu = MenuData()
    menu.AddCheckbox(text=localization.GetByLabel('UI/Chat/ShowCompactMemberList'), setting=guest_list_compact_mode_setting)
    return menu


def get_guest_entry_class():
    if guest_list_compact_mode_setting.is_enabled():
        return UserSimple
    else:
        return User


def bisect_left(a, x, key):
    lo = 0
    hi = len(a)
    while lo < hi:
        mid = (lo + hi) // 2
        if key(a[mid]) < x:
            lo = mid + 1
        else:
            hi = mid

    return lo
