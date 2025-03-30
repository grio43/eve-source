#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\raffles\common\raffle_data.py
from raffles.common import util

class RaffleCreationData(object):

    def __init__(self, owner_id, location_id, solar_system_id, token_id, token_location_id, item_id, type_id, ticket_count, ticket_price, restriction_id):
        self.owner_id = owner_id
        self.owner_location_id = None
        self.location_id = location_id
        self.solar_system_id = solar_system_id
        self.token_id = token_id
        self.token_location_id = token_location_id
        self.item_id = item_id
        self.type_id = type_id
        self.ticket_count = ticket_count
        self.ticket_price = ticket_price
        self.restriction_id = restriction_id

    def __repr__(self):
        return str({'owner_id': self.owner_id,
         'location_id': self.location_id,
         'solar_system_id': self.solar_system_id,
         'token_id': self.token_id,
         'token_location_id': self.token_location_id,
         'item_id': self.item_id,
         'type_id': self.type_id,
         'ticket_count': self.ticket_count,
         'ticket_price': self.ticket_price,
         'restriction_id': self.restriction_id})

    def tokens_required(self):
        return util.tokens_required(self.ticket_price * self.ticket_count)
