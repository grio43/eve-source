#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dynamicresources\client\ess\state.py
import datetime
from collections import OrderedDict
import codereload
import enum
import gametime
import immutable
import signals
import weakness
UNCHANGED = object()

class EssStateProvider(object):

    def __init__(self, state, on_fetch_request = None):
        self._next_token_id = 1
        self._state = state
        self._subscribers = OrderedDict()
        self._need_fetch = False
        self.on_fetch_request = signals.Signal()
        if on_fetch_request is not None:
            self.on_fetch_request.connect(on_fetch_request)

    @property
    def state(self):
        self._signal_fetch_if_needed()
        return self._state

    @state.setter
    def state(self, state):
        if state != self.state:
            old_state = self.state
            self._state = state
            self.notify_subscribers(old_state, state)

    @property
    def has_subscribers(self):
        return len(self._subscribers) > 0

    def mark_need_fetch(self):
        self._need_fetch = True

    def notify_subscribers(self, old_state, new_state):
        subscribers = self._subscribers
        self._subscribers = OrderedDict()
        for token, (callback, lens) in subscribers.items():
            new_lens_state = lens(new_state)
            if lens(old_state) != new_lens_state:
                try:
                    callback(new_lens_state)
                except ReferenceError:
                    pass

            else:
                self._subscribers[token] = (callback, lens)

    def evolve(self, **kwargs):
        self.state = self.state.evolve(**kwargs)

    def read(self):
        return self.state

    def watch(self, callback):
        return (self.state, self.subscribe(callback))

    def select(self, callback, lens):
        return (lens(self.state), self.subscribe(callback, lens))

    def subscribe(self, callback, lens = None):
        if lens is None:
            lens = lambda s: s
        token_id = self._get_next_token_id()
        self._subscribers[token_id] = (weakness.callable_proxy(callback), lens)
        self._signal_fetch_if_needed()
        return SubscriptionToken(self, token_id)

    def unsubscribe(self, token):
        if isinstance(token, SubscriptionToken):
            token = token.id
        try:
            del self._subscribers[token]
        except (IndexError, KeyError):
            pass

    def _signal_fetch_if_needed(self):
        if self._need_fetch:
            self._need_fetch = False
            self.on_fetch_request()

    def _get_next_token_id(self):
        token_id = self._next_token_id
        self._next_token_id += 1
        return token_id


class SubscriptionToken(object):

    def __init__(self, provider, token_id):
        self.provider = provider
        self.id = token_id

    def __del__(self):
        self.unsubscribe()

    def unsubscribe(self):
        self.provider.unsubscribe(self.id)


@codereload.reloadable_enum

class EssStatus(enum.Enum):
    offline = 1
    loading = 2
    online = 3


class EssState(object):
    __metaclass__ = immutable.Immutable

    def __init__(self, status, ess_item_id, in_range, main_bank, reserve_bank):
        self.status = status
        self.ess_item_id = ess_item_id
        self.in_range = in_range
        self.main_bank = main_bank
        self.reserve_bank = reserve_bank

    @property
    def online(self):
        return self.status == EssStatus.online

    @property
    def offline(self):
        return self.status == EssStatus.offline

    @property
    def loading(self):
        return self.status == EssStatus.loading

    @property
    def out_of_range(self):
        return not self.in_range

    def evolve(self, status = UNCHANGED, ess_item_id = UNCHANGED, in_range = UNCHANGED, main_bank = UNCHANGED, reserve_bank = UNCHANGED):
        return EssState(status=changed(status, self.status), ess_item_id=changed(ess_item_id, self.ess_item_id), in_range=changed(in_range, self.in_range), main_bank=changed(main_bank, self.main_bank), reserve_bank=changed(reserve_bank, self.reserve_bank))

    def __eq__(self, other):
        return self is other or isinstance(other, EssState) and self.status == other.status and self.ess_item_id == other.ess_item_id and self.in_range == other.in_range and self.main_bank == other.main_bank and self.reserve_bank == other.reserve_bank

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.status,
         self.ess_item_id,
         self.in_range,
         self.main_bank,
         self.reserve_bank))

    def __repr__(self):
        return u'EssState(status={!r}, ess_item_id={!r}, in_range={!r}, main_bank={!r}, reserve_bank={!r})'.format(self.status, self.ess_item_id, self.in_range, self.main_bank, self.reserve_bank)


class MainBankState(object):
    __metaclass__ = immutable.Immutable

    def __init__(self, balance, link, link_result):
        self.balance = balance
        self.link = link
        self.link_result = link_result

    def is_hacking(self, character_id):
        return self.link is not None and self.link.character_id == character_id

    def evolve(self, balance = UNCHANGED, link = UNCHANGED, link_result = UNCHANGED):
        return MainBankState(balance=changed(balance, self.balance), link=changed(link, self.link), link_result=changed(link_result, self.link_result))

    def __eq__(self, other):
        return self is other or isinstance(other, MainBankState) and self.balance == other.balance and self.link == other.link and self.link_result == other.link_result

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.balance, self.link, self.link_result))

    def __repr__(self):
        return u'MainBankState(balance={!r}, link={!r}, link_result={!r})'.format(self.balance, self.link, self.link_result)


class MainBankLink(object):
    __metaclass__ = immutable.Immutable

    def __init__(self, link_id, character_id, start, end):
        self.link_id = link_id
        self.character_id = character_id
        self.start = start
        self.end = end

    @property
    def remaining(self):
        remaining = self.end - gametime.now_sim()
        if remaining.total_seconds() < 0.0:
            return datetime.timedelta()
        return remaining

    @property
    def duration(self):
        return self.end - self.start

    def evolve(self, link_id = UNCHANGED, character_id = UNCHANGED, start = UNCHANGED, end = UNCHANGED):
        return MainBankLink(link_id=changed(link_id, self.link_id), character_id=changed(character_id, self.character_id), start=changed(start, self.start), end=changed(end, self.end))

    def __eq__(self, other):
        return self is other or isinstance(other, MainBankLink) and self.link_id == other.link_id and self.character_id == other.character_id and self.start == other.start and self.end == other.end

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.link_id,
         self.character_id,
         self.start,
         self.end))

    def __repr__(self):
        return u'MainBankLink(link_id={!r}, character_id={!r}, start={!r}, end={!r})'.format(self.link_id, self.character_id, self.start, self.end)


class MainBankLinkResult(object):
    __metaclass__ = immutable.Immutable

    def __init__(self, link_id, character_id, successful):
        self.link_id = link_id
        self.character_id = character_id
        self.successful = successful

    def evolve(self, link_id = UNCHANGED, character_id = UNCHANGED, successful = UNCHANGED):
        return MainBankLinkResult(link_id=changed(link_id, self.link_id), character_id=changed(character_id, self.character_id), successful=changed(successful, self.successful))

    def __eq__(self, other):
        return self is other or isinstance(other, MainBankLinkResult) and self.link_id == other.link_id and self.character_id == other.character_id and self.successful == other.successful

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.link_id, self.character_id, self.successful))

    def __repr__(self):
        return u'MainBankLinkResult(link_id={!r}, character_id={!r}, successful={!r})'.format(self.link_id, self.character_id, self.successful)


class ReserveBankState(object):
    __metaclass__ = immutable.Immutable

    def __init__(self, balance, pulses_total, pulses_remaining, last_pulse_start, link_count, linked):
        self.balance = balance
        self.pulses_total = pulses_total
        self.pulses_remaining = pulses_remaining
        self.last_pulse_start = last_pulse_start
        self.link_count = link_count
        self.linked = linked

    @property
    def locked(self):
        return self.pulses_remaining == 0

    @property
    def unlocked(self):
        return self.pulses_remaining > 0

    def evolve(self, balance = UNCHANGED, pulses_total = UNCHANGED, pulses_remaining = UNCHANGED, last_pulse_start = UNCHANGED, link_count = UNCHANGED, linked = UNCHANGED):
        return ReserveBankState(balance=changed(balance, self.balance), pulses_total=changed(pulses_total, self.pulses_total), pulses_remaining=changed(pulses_remaining, self.pulses_remaining), last_pulse_start=changed(last_pulse_start, self.last_pulse_start), link_count=changed(link_count, self.link_count), linked=changed(linked, self.linked))

    def __eq__(self, other):
        return self is other or isinstance(other, ReserveBankState) and self.balance == other.balance and self.pulses_total == other.pulses_total and self.pulses_remaining == other.pulses_remaining and self.last_pulse_start == other.last_pulse_start and self.link_count == other.link_count and self.linked == other.linked

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.balance,
         self.pulses_total,
         self.pulses_remaining,
         self.last_pulse_start,
         self.link_count,
         self.linked))

    def __repr__(self):
        return u'ReserveBankState(balance={!r}, pulses_total={!r}, pulses_remaining={!r}, last_pulse_start={!r}, link_count={!r}, linked={!r})'.format(self.balance, self.pulses_total, self.pulses_remaining, self.last_pulse_start, self.link_count, self.linked)


def changed(value, default):
    if value is not UNCHANGED:
        return value
    return default
