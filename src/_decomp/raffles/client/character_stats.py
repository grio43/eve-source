#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\raffles\client\character_stats.py
import signals
import threadutils

class CharacterStats(object):

    def __init__(self):
        self.created = 0
        self.created_completed = 0
        self.joined = 0
        self._joined_won = 0
        self.created_active = 0
        self.joined_active = 0
        self._unseen = set()
        self._is_fetching = False
        self.fetch_complete = False
        self.on_change = signals.Signal(signalName='on_change')

    @property
    def joined_won(self):
        return self._joined_won - len(self._unseen)

    def start_fetch(self):
        if self._is_fetching:
            return
        self._is_fetching = True
        self._fetch()

    @threadutils.threaded
    def _fetch(self):
        try:
            stats = sm.GetService('raffleSvc').get_character_statistics()
            self.joined = stats['raffles_participated']
            self._joined_won = stats['raffles_won']
            self.created_completed = stats['finished_delivered'] + stats['finished_undelivered']
            self.created = self.created_completed + stats['finished_expired'] + stats['created_running']
        finally:
            self._is_fetching = False
            self.fetch_complete = True

        self.on_change(self)

    def update_active(self, my_raffles):
        for raffle in my_raffles:
            if raffle.is_finished:
                self._add_unseen(raffle)
                continue
            if raffle.is_raffle_owner:
                self.created_active += 1
            if raffle.is_ticket_owner:
                self.joined_active += 1

        self.on_change(self)

    def raffle_joined(self, raffle):
        self.joined += 1
        self.joined_active += 1
        self.on_change(self)

    def raffle_created(self, raffle):
        self.created += 1
        self.created_active += 1
        self.on_change(self)

    def raffle_finished(self, raffle):
        if raffle.is_raffle_owner:
            self.created_active -= 1
            if raffle.winner_id:
                self.created_completed += 1
        if raffle.is_ticket_owner:
            self.joined_active -= 1
            if raffle.is_raffle_winner:
                self._joined_won += 1
                self._add_unseen(raffle)
        self.on_change(self)

    def _add_unseen(self, raffle):
        if not raffle.is_raffle_winner or not raffle.is_winner_unseen:
            return
        self._unseen.add(raffle.raffle_id)
        raffle.on_seen.connect(self._on_raffle_seen)

    def _on_raffle_seen(self, raffle):
        raffle.on_seen.disconnect(self._on_raffle_seen)
        self._unseen.remove(raffle.raffle_id)
        self.on_change(self)
