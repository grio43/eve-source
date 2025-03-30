#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\raffles\client\details\controller.py
import logging
import threadutils
from raffles.common.const import RaffleStatus
logger = logging.getLogger(__name__)

class DetailsPageController(object):

    def __init__(self, storage):
        self._storage = storage
        self._is_claiming = False

    def get_raffle(self, raffle_id):
        cached_raffle = self._storage.get_raffle(raffle_id)
        if self._use_cached(cached_raffle):
            return cached_raffle
        raffle_data = sm.GetService('raffleSvc').get_raffle(raffle_id)
        raffle = self._storage.update_raffle(raffle_data)
        return raffle

    def _use_cached(self, cached_raffle):
        if not cached_raffle:
            return False
        elif not cached_raffle.is_finished:
            return False
        elif not cached_raffle.sold_tickets:
            return False
        elif len(cached_raffle.sold_tickets) == cached_raffle.tickets_sold_count:
            return True
        else:
            return False

    def get_similar_raffles(self, raffle, raffle_count):
        result = self._storage.get_similar_raffles(raffle.type_id, raffle_count)
        if not result or len(result) < raffle_count:
            try:
                result = []
                raffle_svc = sm.GetService('raffleSvc')
                raffles_data = raffle_svc.get_similar_raffles(raffle.type_id, raffle_count - len(result))
                if not raffles_data:
                    raffles_data = raffle_svc.grab(None, None)
            except Exception as error:
                logger.exception('get_similar_raffles error')
            else:
                for raffle_data in raffles_data:
                    raffle = self._storage.update_raffle(raffle_data)
                    result.append(raffle)
                    if len(result) >= raffle_count:
                        break

        return result

    def claim_reward(self, raffle):
        if self._is_claiming:
            return
        self._is_claiming = True
        try:
            sm.GetService('raffleSvc').claim_reward(raffle)
        finally:
            self._is_claiming = False
