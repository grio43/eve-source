#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\raffles\common\ticket.py


class Ticket(object):

    def __init__(self, running_id, raffle_id, owner_id, ticket_number):
        self.running_id = running_id
        self.number = ticket_number
        self.owner_id = owner_id
        self.raffle_id = raffle_id

    def __repr__(self):
        properties = ['running_id',
         'raffle_id',
         'number',
         'owner_id']
        return '<Ticket {}>'.format(' '.join(('{}={!r}'.format(name, getattr(self, name)) for name in properties)))
