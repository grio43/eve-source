#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\raffles\client\raffle_service.py
from eveprefs import boot
from carbon.common.script.sys.service import Service
from carbonui.uicore import uicore
from eveexceptions import UserError
import inventorycommon.const
import locks
from raffles.client.window import RaffleWindow
from raffles.common.const import TOKEN_TYPE_ID, RESTRICTED_COUNTRIES, RaffleStatus
from raffles.common.errors import RafflesError
from raffles.common.util import is_kill_switch_enabled

class RaffleService(Service):
    __guid__ = 'svc.raffleSvc'
    __displayname__ = 'Raffle Client Service'
    __notifyevents__ = ['OnGlobalConfigChanged', 'ProcessSessionReset']
    __startupdependencies__ = ['invCache', 'machoNet']
    _is_available = None
    _is_banned = False
    _is_restricted = False
    _is_subscribed = False

    @property
    def proxy(self):
        return sm.ProxySvc('raffleProxy')

    def check_can_open(self):
        if self._is_banned:
            raise UserError('UserBannedRaffleError')
        elif not self.is_available:
            raise UserError('FeatureUnavailable')

    @property
    def is_available(self):
        if not session.countryCode:
            return False
        if self._is_available is None:
            self._available_check()
        return self._is_available

    def _available_check(self):
        if session.countryCode in RESTRICTED_COUNTRIES or boot.region == 'optic':
            self._is_restricted = True
        try:
            self._is_banned = self.proxy.AmIBanned()
        except Exception:
            self.LogException('Failed to check if user is banned')

        if is_kill_switch_enabled(self.machoNet):
            self._is_available = False
        else:
            self._is_available = not self._is_banned and not self._is_restricted

    def toggle_window(self):
        RaffleWindow.ToggleOpenClose()

    def open_link(self, raffle_id):
        RaffleWindow.Open(raffle_id=raffle_id)

    def on_open(self):
        self.subscribe()

    def on_close(self):
        self.unsubscribe()

    def subscribe(self):
        self._is_subscribed = True
        self.proxy.SubscribeToTickets()

    def unsubscribe(self):
        if self._is_subscribed:
            self.proxy.UnSubscribeFromTickets()

    def subscribe_to_raffle(self, raffle_id):
        self.proxy.SubscribeToRaffle(raffle_id)

    def unsubscribe_from_raffle(self, raffle_id):
        if self._is_subscribed:
            self.proxy.UnsubscribeFromRaffle(raffle_id)

    def create_raffle(self, creation_data):
        return self.proxy.CreateRaffle(creation_data)

    def get_character_statistics(self):
        return self.proxy.GetCreatedParticipated()

    def get_type_statistics(self, type_id):
        return self.proxy.GetActiveHistoricPrices(type_id)

    def get_largest_token_stack(self):
        try:
            hangar = self.invCache.GetInventory(inventorycommon.const.containerHangar)
        except Exception:
            return

        flag = inventorycommon.const.flagHangar
        largest = None
        for item in hangar.List(flag):
            if item.typeID != TOKEN_TYPE_ID:
                continue
            if not largest or largest.stacksize < item.stacksize:
                largest = item

        return largest

    def claim_reward(self, raffle):
        if raffle.raffle_status != RaffleStatus.finished_undelivered:
            raise RafflesError()
        self.proxy.AwardItem(raffle.raffle_id)
        raffle.raffle_status = RaffleStatus.finished_delivered

    def grab(self, filters, constraints):
        if filters or constraints:
            return self.proxy.FilteredGrab(filters=filters, constraints=constraints)
        else:
            return self.proxy.Grab()

    def get_similar_raffles(self, type_id, size):
        filters = {'type_id': type_id}
        return self.proxy.FilteredGrab(filters=filters, constraints={}, size=size)

    @locks.SingletonCall
    def get_history(self):
        raffles = []
        page, page_size = self.proxy.GetMyRaffleHistory()
        raffles.extend(page)
        while len(page) == page_size:
            lowest_running_id = min((raffle.running_id for raffle in page))
            page, page_size = self.proxy.GetMyRaffleHistory(running_id=lowest_running_id)
            raffles.extend(page)

        return raffles

    def get_active_tickets(self):
        return self.proxy.GetMyActiveTickets()

    def get_raffle(self, raffle_id):
        return self.proxy.GetRaffle(raffle_id)

    def buy_ticket(self, raffle_id, ticket_number):
        try:
            return self.proxy.BuyTicket(raffle_id, ticket_number)
        except UserError:
            raise
        except Exception:
            self.LogException('Failed to buy ticket due to unexpected error')
            raise RafflesError()

    def buy_random_tickets(self, raffle_id, ticket_count):
        try:
            return self.proxy.BuyRandomTickets(raffle_id, ticket_count)
        except UserError:
            raise
        except Exception:
            self.LogException('Failed to buy ticket due to unexpected error')
            raise RafflesError()

    def OnGlobalConfigChanged(self, configVals):
        if self._is_available is None:
            return
        self._available_check()
        if self.is_available:
            sm.GetService('cmd').Reload()
        elif not self.is_available:
            window = RaffleWindow.GetIfOpen()
            if window:
                window.Maximize()
                uicore.Message('FeatureUnavailable')
                window.CloseByUser()

    def ProcessSessionReset(self):
        self._is_subscribed = False
