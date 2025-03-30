#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dogma\effects\remoteEffect.py
import logging
import ccpProfile
from dogma.effects import Effect
from dogma.effects.tracker import DogmaEffectTracker
from logging import getLogger
logger = logging.getLogger(__name__)

class RemoteEffect(Effect):

    def _LogTryRemoteEffect(self, dogma_lm, event_class, actor_id, item_id, target_ship_id, change_amount = None):
        with ccpProfile.Timer('RemoteEffect::_LogTryRemoteEffect'):
            if not event_class:
                return
            if not actor_id:
                return
            actor_ship_id = dogma_lm.GetShipForPilot(actor_id)
            if not actor_ship_id or not target_ship_id:
                return
            target_id = dogma_lm.GetPilot(target_ship_id)
            if not target_id:
                return
            actor_ship_type_id = getattr(dogma_lm.inventory2.GetItem(actor_ship_id), 'typeID', None)
            target_ship_type_id = getattr(dogma_lm.inventory2.GetItem(target_ship_id), 'typeID', None)
            if not actor_ship_type_id or not target_ship_type_id:
                return
            module_type_id = getattr(dogma_lm.inventory2.GetItem(item_id), 'typeID', None)
            if not module_type_id:
                return
            target_corp_id, target_alliance_id, target_faction_id = dogma_lm.GetCharacterOrganization(target_id)
            solar_system_id = dogma_lm.locationID
            try:
                DogmaEffectTracker.track_remote_support_effect(event_class, actor_id, actor_ship_id, actor_ship_type_id, target_id, target_ship_id, target_ship_type_id, target_corp_id, target_alliance_id, target_faction_id, change_amount, module_type_id, solar_system_id)
            except Exception as exc:
                logger.exception('Failed to track remote support effect {}: {}'.format(event_class, exc))
