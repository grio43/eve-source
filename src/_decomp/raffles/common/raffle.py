#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\raffles\common\raffle.py
import caching
from eve.common.script.sys import idCheckers
from eve.common.script.sys.eveCfg import IsBlueprint
import evetypes
from metaGroups import MetaGroup
from raffles.common.const import RaffleStatus, RAFFLE_TAX_PERCENTAGE
from .raffle_score import get_raffle_score
from .ticket import Ticket
from inventorycommon.typeHelpers import GetAveragePrice

class Raffle(object):

    def __init__(self, running_id, raffle_id, owner_id, location_id, solar_system_id, item_id, type_id, ticket_count, ticket_price, restriction_id, creation_time, expiration_time, sold_tickets, winning_ticket = None, raffle_status = RaffleStatus.running, end_date = None, meta_data = None):
        self.running_id = running_id
        self.raffle_id = raffle_id
        self.owner_id = owner_id
        self.location_id = location_id
        self.solar_system_id = solar_system_id
        self.item_id = item_id
        self.type_id = type_id
        self.ticket_count = ticket_count
        self.ticket_price = ticket_price
        self.restriction_id = restriction_id
        self.creation_time = creation_time
        self.expiration_time = expiration_time
        self.sold_ticket_count = sold_tickets
        self.sold_tickets = None
        self.winning_ticket = winning_ticket
        self.raffle_status = RaffleStatus(raffle_status)
        self.end_date = end_date
        self.meta_data = meta_data

    def __getstate__(self):
        sold_tickets = None
        if self.sold_tickets is not None:
            sold_tickets = [ (t.running_id,
             t.raffle_id,
             t.owner_id,
             t.number) for t in self.sold_tickets ]
        return (self.running_id,
         self.raffle_id,
         self.owner_id,
         self.location_id,
         self.solar_system_id,
         self.item_id,
         self.type_id,
         self.ticket_count,
         self.ticket_price,
         self.restriction_id,
         self.creation_time,
         self.expiration_time,
         self.sold_ticket_count,
         sold_tickets,
         self.winning_ticket,
         self.raffle_status.value,
         self.end_date,
         self.meta_data)

    def __setstate__(self, state):
        self.running_id = state[0]
        self.raffle_id = state[1]
        self.owner_id = state[2]
        self.location_id = state[3]
        self.solar_system_id = state[4]
        self.item_id = state[5]
        self.type_id = state[6]
        self.ticket_count = state[7]
        self.ticket_price = state[8]
        self.restriction_id = state[9]
        self.creation_time = state[10]
        self.expiration_time = state[11]
        self.sold_ticket_count = state[12]
        self.sold_tickets = state[13] if state[13] is None else [ Ticket(x[0], x[1], x[2], x[3]) for x in state[13] ]
        self.winning_ticket = state[14]
        self.raffle_status = RaffleStatus(state[15])
        self.end_date = state[16]
        self.meta_data = state[17]

    @caching.lazy_property
    def group_id(self):
        return evetypes.GetGroupID(self.type_id)

    @caching.lazy_property
    def category_id(self):
        return evetypes.GetCategoryIDByGroup(self.group_id)

    @caching.lazy_property
    def meta_group_id(self):
        meta_group_id = evetypes.GetMetaGroupID(self.type_id)
        if meta_group_id is None:
            return MetaGroup.tech_1.id
        else:
            return meta_group_id

    @caching.lazy_property
    def estimated_price(self):
        return GetAveragePrice(self.type_id)

    @property
    def tickets_remaining(self):
        if self.sold_tickets:
            sold_tickets = len(self.sold_tickets)
        else:
            sold_tickets = self.sold_ticket_count
        return self.ticket_count - sold_tickets

    @property
    def tickets_sold(self):
        if self.sold_tickets:
            return len(self.sold_tickets)
        else:
            return self.sold_ticket_count

    @property
    def total_price(self):
        return self.ticket_price * self.ticket_count

    @property
    def sales_tax(self):
        return self.total_price * RAFFLE_TAX_PERCENTAGE

    @property
    def is_blueprint(self):
        return IsBlueprint(self.type_id)

    @property
    def is_blueprint_copy(self):
        return self.is_blueprint and self.meta_data['is_copy']

    def is_ticket_sold(self, ticket_number):
        for ticket in self.get_tickets():
            if ticket.number == ticket_number:
                return True

        return False

    def finalize(self):
        self.raffle_status = RaffleStatus.finished_undelivered

    def get_tickets(self):
        if not self.are_tickets_primed():
            raise RuntimeError('tickets_what_are_they')
        return self.sold_tickets

    def set_tickets(self, tickets):
        self.sold_tickets = tickets

    def are_tickets_primed(self):
        return self.sold_tickets is not None

    def score(self):
        return get_raffle_score(self)

    def __repr__(self):
        return str({'raffle_id': self.raffle_id,
         'owner_id': self.owner_id,
         'location_id': self.location_id,
         'solar_system_id': self.solar_system_id,
         'item_id': self.item_id,
         'ticket_count': self.ticket_count,
         'ticket_price': self.ticket_price,
         'total_price': self.total_price,
         'remaining_tickets': self.tickets_remaining,
         'restriction_id': self.restriction_id,
         'winning_ticket': str(self.winning_ticket),
         'creation_time': self.creation_time,
         'type_id': self.type_id,
         'status': self.raffle_status})

    def should_exclude_from_grab_bag(self):
        if self.restriction_id:
            return True
        if self.winning_ticket is not None:
            return True
        if self.raffle_status >= RaffleStatus.finished_undelivered:
            return True

    def to_notification_data(self):
        return {'type_id': self.type_id,
         'raffle_id': self.raffle_id,
         'ticket_price': self.ticket_price,
         'ticket_count': self.ticket_count,
         'owner_id': self.owner_id,
         'location_id': self.location_id}

    def get_parties(self):
        ret = set()
        if idCheckers.IsEvePlayerCharacter(self.owner_id):
            ret.add(self.owner_id)
        if self.sold_tickets:
            for ticket in self.sold_tickets:
                if idCheckers.IsEvePlayerCharacter(ticket.owner_id):
                    ret.add(ticket.owner_id)

        return ret
