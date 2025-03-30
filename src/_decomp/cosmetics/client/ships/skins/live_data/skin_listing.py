#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\client\ships\skins\live_data\skin_listing.py
import uuid
import datetime
from cosmetics.client.shipSkinDataSvc import get_ship_skin_data_svc
from cosmetics.client.ships.skins.live_data.skin_listing_target import ListingTarget, ListingTargetType
from cosmetics.common.ships.skins.util import Currency
from eve.client.script.ui.control.message import ShowQuickMessage
from eve.common.lib import appConst
from eveProto import get_single_value_from_split_precision_message, split_precision
from eveProto.generated.eve_public.isk.isk_pb2 import Currency as IskCurrency
from eveProto.generated.eve_public.plex.plex_pb2 import Currency as PlexCurrency
from eveProto.generated.eve_public.character.character_pb2 import Identifier as CharacterIdentifier
from eveProto.generated.eve_public.cosmetic.ship.skin.thirdparty.thirdparty_pb2 import Identifier as SkinIdentifier
from eveProto.generated.eve_public.cosmetic.ship.skin.thirdparty.license.license_pb2 import Identifier as LicenseIdentifier
from eveProto.generated.eve_public.cosmetic.market.skin.listing.listing_pb2 import Attributes as ListingAttributes
from google.protobuf.timestamp_pb2 import Timestamp
from localization import GetByLabel
from localization.formatters.timeIntervalFormatters import FormatTimeIntervalShortWritten, TIME_CATEGORY_DAY, TIME_CATEGORY_HOUR, TIME_CATEGORY_MINUTE
from publicGateway.grpc.exceptions import GenericException
from stackless_response_router.exceptions import TimeoutException

class SkinListing(object):

    def __init__(self, identifier, seller_id, created_at, valid_until, currency, price, quantity, skin_hex, target, branded):
        self._id = identifier
        self._seller_id = seller_id
        self._created_at = created_at
        self._valid_until = valid_until
        self._currency = currency
        self._price = price
        self._quantity = quantity
        self._skin_hex = skin_hex
        self._target = target
        self._branded = branded

    @property
    def identifier(self):
        return self._id

    @property
    def seller_id(self):
        return self._seller_id

    @property
    def target(self):
        return self._target

    @property
    def created_at(self):
        return self._created_at

    @property
    def valid_until(self):
        return self._valid_until

    @property
    def currency(self):
        return self._currency

    @property
    def price(self):
        return self._price

    @property
    def quantity(self):
        return self._quantity

    @property
    def skin_hex(self):
        return self._skin_hex

    @property
    def skin_design(self):
        try:
            return get_ship_skin_data_svc().get_skin_data(self.skin_hex)
        except (GenericException, TimeoutException):
            ShowQuickMessage(GetByLabel('UI/Common/CannotConnectToServer'))
            return None

    @property
    def name(self):
        return self.skin_design.name

    @property
    def time_remaining(self):
        if not self.valid_until:
            return None
        time_remaining = self.valid_until - datetime.datetime.now()
        if time_remaining < datetime.timedelta(0):
            return None
        return time_remaining

    @property
    def is_expired(self):
        return self.time_remaining is None

    @property
    def time_remaining_text(self):
        if not self.time_remaining:
            return None
        seconds = int(self.time_remaining.total_seconds() * appConst.SEC)
        if seconds > appConst.MONTH30:
            time_left = FormatTimeIntervalShortWritten(seconds, showTo=TIME_CATEGORY_DAY)
        elif seconds > appConst.DAY:
            time_left = FormatTimeIntervalShortWritten(seconds, showTo=TIME_CATEGORY_HOUR)
        elif seconds > appConst.HOUR:
            time_left = FormatTimeIntervalShortWritten(seconds, showTo=TIME_CATEGORY_MINUTE)
        else:
            time_left = FormatTimeIntervalShortWritten(seconds)
        return GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/TimeLeft', time_left=time_left)

    @property
    def branded(self):
        return self._branded

    @property
    def is_public(self):
        return self.target.target_type == ListingTargetType.PUBLIC

    @property
    def is_targeted_at_any_character(self):
        return self.target.target_type == ListingTargetType.CHARACTER

    @property
    def is_targeted_at_another_character(self):
        if self.target.target_type == ListingTargetType.CHARACTER:
            if self.target.target_id != session.charid:
                return True
        return False

    @property
    def is_targeted_at_any_organization(self):
        return self.target.target_type in [ListingTargetType.CORPORATION, ListingTargetType.ALLIANCE]

    @property
    def is_targeted_at_another_organization(self):
        if self.target.target_type == ListingTargetType.CORPORATION:
            if session.corpid and self.target.target_id != session.corpid:
                return True
        if self.target.target_type == ListingTargetType.ALLIANCE:
            if not session.allianceid or self.target.target_id != session.allianceid:
                return True
        return False

    def __eq__(self, other):
        if other is None:
            return False
        return self.identifier == other.identifier and self.seller_id == other.seller_id and self.created_at == other.created_at and self.valid_until == other.valid_until and self.currency == other.currency and self.price == other.price and self.quantity == other.quantity and self.skin_hex == other.skin_hex and self.target == other.target and self.branded == other.branded

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        result = 'id: {id}\nseller: {seller}\ncreated_at: {created_at}\nvalid_until: {valid_until}\nprice: {price} {currency}\n{quantity} x skin_hex: {skin_hex}\ntarget: {target}\nbranded: {branded}'.format(id=self.identifier, seller=self.seller_id, created_at=self.created_at, valid_until=self.valid_until, price=self.price, quantity=self.quantity, currency=self.currency, skin_hex=self.skin_hex, target=self.target, branded=self.branded)
        return result

    @classmethod
    def build_from_proto(cls, payload, identifier):
        if payload.HasField('isk'):
            currency = Currency.ISK
            price = get_single_value_from_split_precision_message(payload.isk)
        elif payload.HasField('plex'):
            currency = Currency.PLEX
            price = payload.plex.total_in_cents / 100
        else:
            raise Exception('unknown currency type for skin listing %s' % identifier)
        target = ListingTarget.from_proto(payload.target)
        listing = cls(identifier=identifier, seller_id=payload.seller.sequential, created_at=datetime.datetime.fromtimestamp(payload.created.seconds), valid_until=datetime.datetime.fromtimestamp(payload.expires.seconds), currency=currency, price=price, quantity=payload.quantity, skin_hex=payload.skin.skin.hex, target=target, branded=payload.branded)
        return listing

    @staticmethod
    def build_proto_from_skin_listing(skin_listing):
        created = Timestamp()
        created.FromDatetime(skin_listing.created_at)
        expires = Timestamp()
        expires.FromDatetime(skin_listing.valid_until)
        target_proto = skin_listing.target.to_proto()
        payload = ListingAttributes(seller=CharacterIdentifier(sequential=skin_listing.seller_id), created=created, expires=expires, skin=LicenseIdentifier(character=CharacterIdentifier(sequential=skin_listing.seller_id), skin=SkinIdentifier(hex=skin_listing.skin_hex)), quantity=skin_listing.quantity, target=target_proto, branded=skin_listing.branded)
        if skin_listing.currency == Currency.PLEX:
            payload.plex.CopyFrom(PlexCurrency(total_in_cents=skin_listing.price * 100))
        elif skin_listing.currency == Currency.ISK:
            units, nanos = split_precision(skin_listing.price)
            payload.isk.CopyFrom(IskCurrency(units=units, nanos=nanos))
        else:
            raise Exception('unknown currency type for skin listing %s' % skin_listing.identifier)
        return payload
