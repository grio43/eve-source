#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\dockedUI\offices.py
import logging
import blue
import eveformat
import localization
import threadutils
from carbon.common.lib.const import DAY
from carbonui import AxisAlignment, uiconst
from carbonui.control.button import Button
from carbonui.control.scroll import Scroll
from carbonui.primitives.container import Container
from carbonui.primitives.flowcontainer import FlowContainer
from carbonui.util.sortUtil import SortListOfTuples
from carbonui.button.group import ButtonGroup, ButtonSizeMode
from eve.client.script.ui.control.entries.header import Header
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.shared.dockedUI.officeEntry import OfficeEntry
from eve.common.lib.appConst import corpRoleDirector, rentalPeriodOffice
logger = logging.getLogger(__name__)

class LoadState(object):
    UNLOADED = 1
    LOAD_PENDING = 2
    LOADING = 3
    LOADED = 4


class PanelDestroyedError(Exception):
    pass


class OfficesPanel(Container):
    __notifyevents__ = ('OnCorporationChanged', 'OnCorporationMemberChanged', 'OnOfficeRentalChanged')
    _button_cont = None
    _load_state = LoadState.UNLOADED
    _rent_office_locked = False
    _scroll = None
    _initialized = False

    def __init__(self, station_controller, **kwargs):
        self._station_controller = station_controller
        super(OfficesPanel, self).__init__(**kwargs)

    def LoadPanel(self):
        self._load()

    def _layout(self):
        self._button_cont = ButtonGroup(name='officesButtons', parent=self, align=uiconst.TOBOTTOM, button_alignment=AxisAlignment.START, button_size_mode=ButtonSizeMode.STRETCH)
        self._scroll = Scroll(parent=self)

    @threadutils.threaded
    def _load(self):
        if not self._initialized:
            self._initialized = True
            self._layout()
            sm.RegisterNotify(self)
        is_loading = self._load_state in {LoadState.LOADING, LoadState.LOAD_PENDING}
        self._load_state = LoadState.LOAD_PENDING
        if is_loading:
            return
        try:
            while self._load_state == LoadState.LOAD_PENDING:
                self._load_state = LoadState.LOADING
                self._load_buttons()
                self._load_offices_scroll()
                self._load_state = LoadState.LOADED

        except PanelDestroyedError:
            pass
        except Exception:
            logger.exception('Failed to load the offices panel')

    def ShowOffices(self):
        self._load()

    def _load_offices_scroll(self):
        self._scroll.ShowLoading()
        try:
            corporations_with_office = self._station_controller.CorpsWithOffices()
            cfg.eveowners.Prime(corporations_with_office)
            cfg.corptickernames.Prime(corporations_with_office)
            entries = []
            for corporation_id in corporations_with_office:
                corporation_name = cfg.eveowners.Get(corporation_id).ownerName
                entry = GetFromClass(OfficeEntry, {'corpName': corporation_name,
                 'corpID': corporation_id})
                entries.append((corporation_name.lower(), entry))

            entries = SortListOfTuples(entries)
            available_office_slots = self._station_controller.GetNumberOfUnrentedOffices()
            if available_office_slots is not None:
                entries.insert(0, GetFromClass(Header, {'label': localization.GetByLabel('UI/Station/Lobby/NumAvailableOffices', numOffices=available_office_slots)}))
            if not self._scroll or self._scroll.destroyed:
                return
            self._scroll.Load(contentList=entries)
        finally:
            if self._scroll and not self._scroll.destroyed:
                self._scroll.HideLoading()

    def _load_buttons(self):
        self._button_cont.Flush()
        can_rent = self._station_controller.CanRent()
        office_exists = self._station_controller.GetMyCorpOffice() is not None
        if can_rent and not office_exists:
            self._add_button(text=localization.GetByLabel('UI/Station/Lobby/RentOffice'), callback=self._rent_office)
        can_unrent = self._station_controller.CanUnrent()
        if can_unrent and office_exists:
            self._add_button(text=localization.GetByLabel('UI/Station/Hangar/UnrentOffice'), callback=self._unrent_office)
        can_move_hq = self._station_controller.CanMoveHQ()
        hq_allowed = self._station_controller.IsHqAllowed()
        if can_move_hq and hq_allowed:
            is_hq_here = self._station_controller.IsMyHQ()
            if not is_hq_here:
                self._add_button(text=localization.GetByLabel('UI/Station/Lobby/MoveHeadquartersHere'), callback=self._set_hq)
        has_impounded_items = self._station_controller.HasCorpItemsImpounded()
        is_director = session.corprole & corpRoleDirector
        if not office_exists and has_impounded_items and is_director:
            self._add_button(text=localization.GetByLabel('UI/Inventory/ReleaseItems'), callback=self._release_impounded_items)

    def _add_button(self, text, callback):
        if not self._button_cont or self._button_cont.destroyed:
            raise PanelDestroyedError()
        Button(parent=self._button_cont, align=uiconst.TOPLEFT, label=text, func=callback, args=())

    def _rent_office(self):
        if self._rent_office_locked:
            return
        self._rent_office_locked = True
        try:
            cost = self._station_controller.GetCostForOpeningOffice()
            response = eve.Message('AskPayOfficeRentalFee', {'cost': cost,
             'duration': rentalPeriodOffice * DAY}, uiconst.YESNO)
            if response == uiconst.ID_YES:
                self._station_controller.RentOffice(cost)
        finally:
            self._rent_office_locked = False

    def _unrent_office(self):
        if not self._station_controller.GetMyCorpOffice():
            return
        if not self._station_controller.IsEmptyOffice():
            response = eve.Message('crpUnrentOfficeWithContent', {}, uiconst.YESNO)
            if response != uiconst.ID_YES:
                return
        else:
            station_id = self._station_controller.GetItemID()
            office_name = cfg.evelocations.Get(station_id).name
            response = eve.Message('crpUnrentOffice', {'officeName': office_name}, uiconst.YESNO)
            if response != uiconst.ID_YES:
                return
        self._station_controller.UnrentOffice()

    def _release_impounded_items(self):
        cost = self._station_controller.GetCostForGettingCorpJunkBack()
        if cost is not None:
            if eve.Message('CrpJunkAcceptCost', {'cost': eveformat.number(cost)}, uiconst.YESNO) != uiconst.ID_YES:
                return
            self._station_controller.ReleaseImpoundedItems(cost)
        self._load()

    def _set_hq(self):
        self._station_controller.SetHQ()

    def OnCorporationChanged(self, corpID, change):
        blue.pyos.synchro.Sleep(750)
        self._load()

    def OnCorporationMemberChanged(self, corporationID, memberID, change):
        if memberID == session.charid:
            self._load()

    def OnOfficeRentalChanged(self, corporationID, officeID):
        invalidate_office_inventory_cache(officeID)
        self._load()


def invalidate_office_inventory_cache(office_id):
    sm.GetService('invCache').InvalidateLocationCache(office_id)
