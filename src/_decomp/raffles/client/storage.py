#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\raffles\client\storage.py
from collections import defaultdict
import signals
import threadutils
from raffles.client.raffle import Raffle

class RaffleStorage(object):
    __notifyevents__ = ['OnRaffleUpdatedServer',
     'OnTicketsUpdatedServer',
     'OnRaffleFinishedServer',
     'OnRaffleCreatedServer']

    def __init__(self):
        sm.RegisterNotify(self)
        self.on_raffle_updated = signals.Signal(signalName='on_raffle_updated')
        self.on_raffle_joined = signals.Signal(signalName='on_raffle_joined')
        self.on_raffle_created = signals.Signal(signalName='on_raffle_created')
        self.on_raffle_finished = signals.Signal(signalName='on_raffle_finished')
        self._raffles = {}
        self._my_tickets_count = defaultdict(int)
        self._fetch_my_tickets()

    def close(self):
        sm.UnregisterNotify(self)

    @threadutils.threaded
    def _fetch_my_tickets(self):
        tickets = sm.GetService('raffleSvc').get_active_tickets()
        for ticket in tickets:
            self._my_tickets_count[ticket.raffle_id] += 1

        for raffle_id, ticket_count in self._my_tickets_count.iteritems():
            raffle = self._get_cached_raffle(raffle_id)
            if raffle:
                raffle.update_my_tickets(ticket_count, send_signal=True)

    def OnRaffleUpdatedServer(self, raffle_id, raffle_data):
        if self.has_raffle(raffle_id):
            self.update_raffle(raffle_data)

    def OnTicketsUpdatedServer(self, ticket_updates):
        for raffle_id, sold_ticket_count in ticket_updates.iteritems():
            raffle = self._get_cached_raffle(raffle_id)
            if raffle:
                raffle.update_sold_ticket_count(sold_ticket_count)

    def OnRaffleFinishedServer(self, raffle_id, winning_ticket):
        raffle = self._get_cached_raffle(raffle_id)
        if raffle:
            raffle.update_winning_ticket(winning_ticket)
            self.on_raffle_finished(raffle)

    def OnRaffleCreatedServer(self, raffle_id, raffle_data):
        self.update_raffle(raffle_data)

    def has_raffle(self, raffle_id):
        return raffle_id in self._raffles

    def get_raffle(self, raffle_id):
        return self._raffles.get(raffle_id, None)

    def update_raffle(self, raffle_data):
        raffle = self._get_cached_raffle(raffle_data.raffle_id)
        if not raffle:
            raffle = Raffle(raffle_data, update_callback=self.update_raffle)
            self._raffles[raffle.raffle_id] = raffle
            if raffle.raffle_id in self._my_tickets_count:
                raffle.update_my_tickets(self._my_tickets_count[raffle.raffle_id])
            if raffle.is_raffle_owner:
                self.on_raffle_created(raffle)
        else:
            was_finished = raffle.is_finished
            was_ticket_owner = raffle.is_ticket_owner
            raffle.update(raffle_data)
            if not was_finished and not was_ticket_owner and raffle.is_ticket_owner:
                self.on_raffle_joined(raffle)
        self.on_raffle_updated(raffle)
        return raffle

    def remove_raffle(self, raffle):
        if raffle.raffle_id in self._raffles:
            del self._raffles[raffle.raffle_id]

    def get_similar_raffles(self, type_id, size):
        result = []
        count = size
        for raffle in self._raffles.itervalues():
            if raffle.type_id == type_id and not raffle.is_finished:
                count -= 1
                result.append(raffle)
                if count == 0:
                    break

        return result

    def _get_cached_raffle(self, raffle_id):
        return self._raffles.get(raffle_id, None)
