#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\client\messengers\entitlements\character\ship\noticeMessenger.py
from cosmetics.client.messengers.entitlements.character.ship import new_entitlement
from signals import Signal
from eveProto.generated.eve_public.entitlement.character.ship.corplogo_pb2 import GrantedNotice as GrantedCorp
from eveProto.generated.eve_public.entitlement.character.ship.corplogo_pb2 import RevokedNotice as RevokedCorp
from eveProto.generated.eve_public.entitlement.character.ship.alliancelogo_pb2 import GrantedNotice as GrantedAlliance
from eveProto.generated.eve_public.entitlement.character.ship.alliancelogo_pb2 import RevokedNotice as RevokedAlliance

class NoticeMessenger(object):
    public_gateway = None

    def __init__(self, public_gateway):
        self.public_gateway = public_gateway
        self.public_gateway.subscribe_to_notice(GrantedCorp, self._on_corp_logo_granted)
        self.public_gateway.subscribe_to_notice(RevokedCorp, self._on_corp_logo_revoked)
        self.public_gateway.subscribe_to_notice(GrantedAlliance, self._on_alliance_logo_granted)
        self.public_gateway.subscribe_to_notice(RevokedAlliance, self._on_alliance_logo_revoked)
        self.on_corp_logo_granted = Signal()
        self.on_alliance_logo_granted = Signal()
        self.on_corp_logo_revoked = Signal()
        self.on_alliance_logo_revoked = Signal()

    def _on_corp_logo_granted(self, corp_logo_granted, _notice_primitive):
        self.on_corp_logo_granted(new_entitlement(corp_logo_granted.entitlement))

    def _on_alliance_logo_granted(self, alliance_logo_granted, _notice_primitive):
        self.on_alliance_logo_granted(new_entitlement(alliance_logo_granted.entitlement))

    def _on_corp_logo_revoked(self, corp_logo_revoked, _notice_primitive):
        self.on_corp_logo_revoked(new_entitlement(corp_logo_revoked.entitlement))

    def _on_alliance_logo_revoked(self, alliance_logo_revoked, _notice_primitive):
        self.on_alliance_logo_revoked(new_entitlement(alliance_logo_revoked.entitlement))
