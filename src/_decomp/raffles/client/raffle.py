#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\raffles\client\raffle.py
from __future__ import absolute_import
import datetime
import caching
import datetimeutils
from eve.common.script.sys.eveCfg import IsBlueprint
import itertoolsext
import localization
import signals
from raffles.common.const import RaffleStatus, RAFFLE_DURATION, FEW_TICKETS_REMAINING, GOOD_VALUE_FACTOR, BAD_VALUE_FACTOR
from raffles.client.drag_data import RaffleDragData
from raffles.client.hash import HashGenerator
from raffles.client.localization import Text
from raffles.client.util import get_item_name, get_item_group_name, get_group_id, get_market_estimate, get_category_id, get_meta_group_id

class Raffle(object):

    def __init__(self, data, update_callback):
        self._update_callback = update_callback
        self.on_change = signals.Signal(signalName='on_change')
        self.on_tickets_sold = signals.Signal(signalName='on_tickets_sold')
        self.on_tickets_sold.connect(self.on_change)
        self.on_status_changed = signals.Signal(signalName='on_status_changed')
        self.on_status_changed.connect(self.on_change)
        self.on_seen = signals.Signal(signalName='on_seen')
        self._sold_ticket_count = 0
        self._my_ticket_count = 0
        self.is_subscribed = False
        self._update_data(data)

    def _update_data(self, data):
        self.raffle_id = data.raffle_id
        self.owner_id = data.owner_id
        self.location_id = data.location_id
        self.solar_system_id = data.solar_system_id
        self.item_id = data.item_id
        self.type_id = data.type_id
        self.ticket_count = data.ticket_count
        self.ticket_price = data.ticket_price
        self.sold_tickets = data.sold_tickets
        self.update_sold_ticket_count(data.sold_ticket_count)
        self.winning_ticket = data.winning_ticket
        self.expiration_time = datetimeutils.filetime_to_datetime(data.expiration_time)
        if data.end_date:
            self.end_time = datetimeutils.filetime_to_datetime(data.end_date)
        else:
            self.end_time = self.expiration_time
        self.raffle_status = RaffleStatus(data.raffle_status)
        self.is_finished = self._is_status_finished()
        self.restriction_id = data.restriction_id
        self.meta_data = data.meta_data

    def _is_status_finished(self):
        return self.raffle_status in (RaffleStatus.finished_expired, RaffleStatus.finished_undelivered, RaffleStatus.finished_delivered)

    def update(self, raffle_data):
        was_finished = self.is_finished
        last_winning_ticket = self.winning_ticket
        self._update_data(raffle_data)
        if was_finished != self.is_finished or bool(last_winning_ticket) != bool(self.winning_ticket):
            self.on_status_changed(raffle=self)

    def update_my_tickets(self, my_ticket_count, send_signal = False):
        self._my_ticket_count = my_ticket_count
        if send_signal:
            self.on_tickets_sold(raffle=self)

    def update_sold_ticket_count(self, sold_ticket_count):
        if self._sold_ticket_count == sold_ticket_count:
            return
        self._sold_ticket_count = sold_ticket_count
        self.on_tickets_sold(raffle=self)

    def update_winning_ticket(self, winning_ticket):
        self.winning_ticket = winning_ticket
        if self.winning_ticket:
            self.raffle_status = RaffleStatus.finished_undelivered
        else:
            self.raffle_status = RaffleStatus.finished_expired
        self.is_finished = True
        self.on_status_changed(raffle=self)

    def subscribe(self):
        if self.is_subscribed or self.is_finished:
            return
        sm.GetService('raffleSvc').subscribe_to_raffle(self.raffle_id)
        self.is_subscribed = True

    def unsubscribe(self):
        if not self.is_subscribed:
            return
        sm.GetService('raffleSvc').unsubscribe_from_raffle(self.raffle_id)
        self.is_subscribed = False

    def buy_ticket(self, ticket_number):
        raffle_data = sm.GetService('raffleSvc').buy_ticket(self.raffle_id, ticket_number)
        self._update_callback(raffle_data)
        self.update_winner_seen(False)

    def buy_random_tickets(self, amount):
        raffle_data = sm.GetService('raffleSvc').buy_random_tickets(self.raffle_id, amount)
        self._update_callback(raffle_data)
        self.update_winner_seen(False)

    def get_drag_data(self):
        return RaffleDragData(self)

    @caching.lazy_property
    def is_blueprint(self):
        return IsBlueprint(self.type_id)

    @caching.lazy_property
    def is_blueprint_copy(self):
        return self.is_blueprint and self.meta_data['is_copy']

    @property
    def tickets_remaining_count(self):
        return self.ticket_count - self.tickets_sold_count

    @property
    def is_expired(self):
        return self.is_finished and not self.winning_ticket

    @property
    def is_sold_out(self):
        return self.tickets_remaining_count == 0

    def local_expire(self):
        self.is_finished = True
        self.on_status_changed(raffle=self)

    @property
    def tickets_sold_count(self):
        return self._sold_ticket_count

    def get_ticket_owner_id(self, ticket_number):
        ticket = self.get_ticket(ticket_number)
        if ticket:
            return ticket.owner_id

    def get_ticket_display_hash(self, ticket_number):
        return self.hash_generator[ticket_number]

    def get_ticket(self, ticket_number):
        return itertoolsext.first_or_default(self.sold_tickets, lambda x: x.number == ticket_number, None)

    @property
    def winner_id(self):
        if self.winning_ticket:
            return self.winning_ticket.owner_id

    def tickets_owned_by(self, char_id):
        return [ x for x in self.sold_tickets if x.owner_id == char_id ]

    @property
    def tickets_owned(self):
        return self.tickets_owned_by(session.charid)

    def ticket_count_owned_by(self, char_id):
        return itertoolsext.count(self.sold_tickets, lambda x: x.owner_id == char_id)

    @property
    def tickets_owned_count(self):
        if self.sold_tickets:
            return self.ticket_count_owned_by(session.charid)
        return self._my_ticket_count

    @property
    def is_ticket_owner(self):
        return self.tickets_owned_count > 0

    @property
    def is_raffle_owner(self):
        return self.owner_id == session.charid

    @property
    def is_raffle_winner(self):
        return self.winner_id == session.charid

    @property
    def is_involved(self):
        return self.is_raffle_owner or self.is_ticket_owner

    @property
    def is_unclaimed(self):
        return self.is_raffle_winner and self.raffle_status == RaffleStatus.finished_undelivered

    @property
    def is_winner_unseen(self):
        if self.winner_id:
            return settings.char.ui.Get(self._winner_unseen_key, False)

    @property
    def requires_interaction(self):
        return self.is_winner_unseen or self.is_unclaimed

    def update_winner_seen(self, is_seen):
        key = self._winner_unseen_key
        if is_seen:
            settings.char.ui.Delete(key)
            self.on_seen(self)
        else:
            settings.char.ui.Set(key, True)

    @property
    def _winner_unseen_key(self):
        return 'Raffle_Unseen_Winner_{}'.format(self.raffle_id)

    @property
    def time_remaining(self):
        if self.is_finished:
            return 0
        seconds = (self.expiration_time - datetime.datetime.utcnow()).total_seconds()
        time_left = long(max((seconds, 0))) * const.SEC
        if time_left == 0:
            self.local_expire()
        return time_left

    @property
    def time_remaining_text(self):
        return localization.formatters.FormatTimeIntervalShortWritten(self.time_remaining, showFrom='day', showTo='second')

    @property
    def tickets_remaining_ratio(self):
        return self.tickets_remaining_count / float(self.ticket_count)

    @property
    def time_remaining_ratio(self):
        return (RAFFLE_DURATION - self.time_remaining) / float(RAFFLE_DURATION)

    @property
    def few_tickets_remaining(self):
        return self.tickets_remaining_ratio <= FEW_TICKETS_REMAINING

    @property
    def group_id(self):
        return get_group_id(self.type_id)

    @property
    def category_id(self):
        return get_category_id(self.type_id)

    @property
    def meta_group_id(self):
        return get_meta_group_id(self.type_id)

    @caching.lazy_property
    def item_name(self):
        name = get_item_name(self.type_id, item_id=self.item_id)
        if self.is_blueprint:
            if self.is_blueprint_copy:
                return u'{} ({})'.format(name, Text.blueprint_copy())
            else:
                return u'{} ({})'.format(name, Text.blueprint_original())
        return name

    @property
    def item_group_name(self):
        return get_item_group_name(self.type_id)

    @property
    def is_private(self):
        return self.restriction_id == 1

    @property
    def total_price(self):
        return self.ticket_count * self.ticket_price

    @caching.lazy_property
    def _market_estimate(self):
        return get_market_estimate(self.type_id, self.item_id)

    @property
    def good_value(self):
        if self._market_estimate:
            return self.total_price <= self._market_estimate * GOOD_VALUE_FACTOR

    @property
    def bad_value(self):
        if self._market_estimate:
            return self.total_price >= self._market_estimate * BAD_VALUE_FACTOR

    @caching.lazy_property
    def hash_generator(self):
        return HashGenerator(self.raffle_id, self.ticket_count)

    def __repr__(self):
        properties = ['raffle_id',
         'item_id',
         'type_id',
         'ticket_count',
         'tickets_sold_count',
         'total_price',
         'ticket_price',
         'restriction_id',
         'winning_ticket',
         'raffle_status',
         'meta_data']
        return '<Raffle {}>'.format(' '.join(('{}={!r}'.format(name, getattr(self, name)) for name in properties)))
