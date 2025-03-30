#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\client\ships\skins\live_data\skin_listing_target.py
from itertoolsext.Enum import Enum
from eveProto.generated.eve_public.alliance.alliance_pb2 import Identifier as AllianceIdentifier
from eveProto.generated.eve_public.character.character_pb2 import Identifier as CharacterIdentifier
from eveProto.generated.eve_public.corporation.corporation_pb2 import Identifier as CorporationIdentifier
from eveProto.generated.eve_public.cosmetic.market.skin.listing.listing_pb2 import ListingTarget as ListingTargetIdentifier

@Enum

class ListingTargetType(object):
    PUBLIC = 'Public'
    CORPORATION = 'Corporation'
    ALLIANCE = 'Alliance'
    CHARACTER = 'Character'


@Enum

class SellerMembershipType(object):
    UNSPECIFIED = 0
    BRAND_MANAGER = 1
    MEMBER = 2
    NONE = 3


@Enum

class ListedTo(object):
    PUBLIC = 0
    MY_CORP = 1
    MY_ALLIANCE = 2
    SPECIFIC = 3


class ListingTarget(object):

    def __init__(self, target_type, target_id = None):
        self._target_type = target_type
        self._target_id = target_id

    def __eq__(self, other):
        return self.target_type == other.target_type and self.target_id == other.target_id

    def __str__(self):
        return 'target_type: {target_type}, target_id: {target_id}'.format(target_type=self.target_type, target_id=self.target_id)

    @property
    def target_type(self):
        return self._target_type

    @property
    def target_id(self):
        return self._target_id

    @classmethod
    def from_proto(cls, payload):
        if payload.HasField('public'):
            return cls(ListingTargetType.PUBLIC, payload.public)
        if payload.HasField('corporation'):
            return cls(ListingTargetType.CORPORATION, payload.corporation.sequential)
        if payload.HasField('alliance'):
            return cls(ListingTargetType.ALLIANCE, payload.alliance.sequential)
        if payload.HasField('character'):
            return cls(ListingTargetType.CHARACTER, payload.character.sequential)

    def to_proto(self):
        if self.target_type == ListingTargetType.PUBLIC:
            return ListingTargetIdentifier(public=True)
        if self.target_type == ListingTargetType.CORPORATION:
            return ListingTargetIdentifier(corporation=CorporationIdentifier(sequential=self.target_id))
        if self.target_type == ListingTargetType.CHARACTER:
            return ListingTargetIdentifier(character=CharacterIdentifier(sequential=self.target_id))
        if self.target_type == ListingTargetType.ALLIANCE:
            return ListingTargetIdentifier(alliance=AllianceIdentifier(sequential=self.target_id))
