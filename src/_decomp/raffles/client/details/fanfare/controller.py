#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\raffles\client\details\fanfare\controller.py
import random

class FanfareController(object):

    def __init__(self, raffle):
        self._raffle = raffle
        self.winning_hash = self._raffle.get_ticket_display_hash(self._raffle.winning_ticket.number)
        self.owned_hashes = [ raffle.get_ticket_display_hash(ticket.number) for ticket in raffle.tickets_owned ]
        self._total_owned_count = len(self.owned_hashes)

    @property
    def type_id(self):
        return self._raffle.type_id

    @property
    def item_id(self):
        return self._raffle.item_id

    @property
    def is_copy(self):
        return self._raffle.is_blueprint_copy

    @property
    def total_ticket_count(self):
        return self._raffle.ticket_count

    @property
    def total_owned_count(self):
        return self._total_owned_count

    @property
    def active_owned_count(self):
        return len(self.owned_hashes)

    def get_decrypting_order(self):
        owned_ticket_hashes = [ self._raffle.get_ticket_display_hash(ticket.number) for ticket in self._raffle.tickets_owned ]
        highest_score = 0
        highest_ticket_hash = None
        for ticket_hash in owned_ticket_hashes:
            score = self._get_ticket_hash_score(ticket_hash)
            if score >= highest_score:
                highest_score = score
                highest_ticket_hash = ticket_hash

        character_scores = [ [index, character, 0] for index, character in enumerate(self.winning_hash) ]
        for character_score in character_scores:
            index, character, _ = character_score
            if character != highest_ticket_hash[index]:
                continue
            for ticket_hash in owned_ticket_hashes:
                if ticket_hash[index] == character:
                    character_score[2] += 1

        character_scores.sort(key=lambda x: x[2])
        return [ character_score[0] for character_score in reversed(character_scores) ]

    def _get_ticket_hash_score(self, ticket_hash):
        score = 0
        for index, character in enumerate(self.winning_hash):
            if ticket_hash[index] == character:
                score += 1

        return score

    def get_slot_options(self, hash_index):
        options = list(self._raffle.hash_generator.get_available_options(hash_index))
        while len(options) < 9:
            c = random.choice(self._raffle.hash_generator.alphabet)
            if c not in options:
                options.append(c)

        random.shuffle(options)
        highlighted_indexes = [ i for i, character in enumerate(options) if self._has_character(hash_index, character) ]
        return (options, highlighted_indexes)

    def _has_character(self, index, character):
        for ticket_hash in self.owned_hashes:
            if ticket_hash[index] == character:
                return True

        return False

    def decrypt(self, index):
        character = self.winning_hash[index]
        self.owned_hashes = [ ticket_hash for ticket_hash in self.owned_hashes if ticket_hash[index] == character ]

    @property
    def highlighted_ticket_count(self):
        return len(self.owned_hashes)

    @property
    def is_winner(self):
        return self._raffle.is_raffle_winner

    def update_winner_seen(self):
        self._raffle.update_winner_seen(True)
