#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\client\messengers\cosmetics\ship\shipSkinStateNoticeMessenger.py
from cosmetics.client.ships.ship_skin_svc_signals import on_skin_state_set_internal, on_skin_state_set_all_in_bubble_internal
from cosmetics.client.ships.skins.live_data.ship_skin_state import ShipSkinState
from eveprefs import prefs
from eveProto.generated.eve_public.cosmetic.ship.api.notice_pb2 import SetNotice, SetAllInBubbleNotice
from logging import getLogger
logger = getLogger(__name__)

class ShipSkinStateNoticeMessenger(object):

    def __init__(self, public_gateway):
        self._public_gateway = public_gateway
        self._public_gateway.subscribe_to_notice(SetNotice, self._on_set_notice)
        self._public_gateway.subscribe_to_notice(SetAllInBubbleNotice, self._on_set_all_in_bubble_notice)

    @property
    def public_gateway(self):
        return self._public_gateway

    def _on_set_notice(self, notice_payload, _notice_primitive):
        character_id = session.charid
        new_state_proto = notice_payload.state
        skin_state = ShipSkinState.build_from_proto(new_state_proto)
        logger.info('SKIN STATES - SetNotice received by character {character_id} for ship {ship_id} - {skin_type}'.format(character_id=character_id, ship_id=new_state_proto.ship.sequential, skin_type=skin_state.skin_type))
        on_skin_state_set_internal(skin_state)

    def _on_set_all_in_bubble_notice(self, notice_payload, _notice_primitive):
        character_id = session.charid
        skin_states = []
        for proto in notice_payload.state:
            try:
                skin_state = ShipSkinState.build_from_proto(proto)
                skin_states.append(skin_state)
            except Exception as exc:
                logger.exception(exc)

        on_skin_state_set_all_in_bubble_internal(skin_states)
        if self._should_log_details():
            logger.info('SKIN STATES - SetAllInBubbleNotice received by character {character_id} for ships {ship_ids}'.format(character_id=character_id, ship_ids=', '.join([ str(skin_state.ship_instance_id) for skin_state in skin_states ])))
        else:
            logger.info('SKIN STATES - SetAllInBubbleNotice received by character {character_id}'.format(character_id=character_id))

    def _should_log_details(self):
        return prefs.clusterMode != 'LIVE'
