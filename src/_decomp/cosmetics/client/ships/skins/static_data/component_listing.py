#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\client\ships\skins\static_data\component_listing.py
import uuid
import datetime
import time
from cosmetics.client.ships.skins.live_data.component_license import ComponentLicense
from cosmetics.common.ships.skins.live_data.component_license_type import ComponentLicenseType
from cosmetics.common.ships.skins.static_data.component import ComponentsDataLoader
from cosmetics.common.ships.skins.util import Currency, COMPONENT_LIMITED_OFFER_THRESHOLD_DAYS
from eveProto import get_single_value_from_split_precision_message, split_precision
from eveProto.generated.eve_public.isk.isk_pb2 import Currency as IskCurrency
from eveProto.generated.eve_public.plex.plex_pb2 import Currency as PlexCurrency
from eveProto.generated.eve_public.inventory.generic_item_type_pb2 import Identifier as ItemTypeIdentifier
from eveProto.generated.eve_public.cosmetic.market.component.listing.listing_pb2 import Attributes as ListingAttributes
from google.protobuf.timestamp_pb2 import Timestamp

class ComponentListing(object):

    def __init__(self, identifier, valid_until, currency, price, quantity, component_item_type_id, bundle_size):
        self._id = identifier
        self._valid_until = valid_until
        self._currency = currency
        self._price = price
        self._quantity = quantity
        self._component_item_type_id = component_item_type_id
        self._bundle_size = bundle_size

    @property
    def identifier(self):
        return self._id

    @property
    def valid_until(self):
        return self._valid_until

    @property
    def valid_until_seconds(self):
        return time.mktime(self.valid_until.timetuple())

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
    def component_item_type_id(self):
        return self._component_item_type_id

    @property
    def component_id(self):
        return self.get_component_data().component_id

    @property
    def license_type(self):
        item_data = self.get_component_item_data()
        if item_data:
            return item_data.license_type

    def get_component_item_data(self):
        component_data = self.get_component_data()
        item_data = component_data.component_item_data_by_type_id.get(self._component_item_type_id)
        return item_data

    def get_component_data(self):
        return ComponentsDataLoader.get_component_for_component_type(self._component_item_type_id)

    @property
    def bundle_size(self):
        return self._bundle_size

    @property
    def component_license(self):
        return ComponentLicense(owner_character_id=None, component_id=self.component_id, license_type=self.license_type, remaining_license_uses=self.bundle_size)

    @property
    def name(self):
        return self.component_license.name

    @property
    def name_with_quantity(self):
        if self.component_license.license_type == ComponentLicenseType.UNLIMITED:
            return self.name
        else:
            return u'{} x {}'.format(self.component_license.remaining_license_uses, self.name)

    def is_limited_offer(self):
        return self.valid_until < datetime.datetime.now() + datetime.timedelta(days=COMPONENT_LIMITED_OFFER_THRESHOLD_DAYS)

    def __eq__(self, other):
        if other is None:
            return False
        return self.identifier == other.identifier and self.valid_until == other.valid_until and self.currency == other.currency and self.price == other.price and self.quantity == other.quantity and self.component_item_type_id == other.component_item_type_id and self.bundle_size == other.bundle_size

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        result = 'id: {id}\nvalid_until: {valid_until}\nprice: {price} {currency}\noffer: {bundle_size} x {component_type_id}\nquantity: {quantity}'.format(id=self.identifier, valid_until=self.valid_until, price=self.price, quantity=self.quantity, currency=self.currency, bundle_size=self.bundle_size, component_type_id=self.component_item_type_id)
        return result

    @staticmethod
    def build_from_proto(payload, identifier):
        if payload.HasField('isk'):
            currency = Currency.ISK
            price = get_single_value_from_split_precision_message(payload.isk)
        elif payload.HasField('plex'):
            currency = Currency.PLEX
            price = payload.plex.total_in_cents / 100
        else:
            raise Exception('unknown currency type for skin component listing %s' % identifier)
        listing = ComponentListing(identifier=identifier, valid_until=datetime.datetime.fromtimestamp(payload.sale_end.seconds), currency=currency, price=price, quantity=-1, component_item_type_id=payload.component_item.sequential, bundle_size=payload.bundle_size)
        return listing

    @staticmethod
    def build_proto_from_component_listing(component_listing):
        sale_end = Timestamp()
        sale_end.FromDatetime(component_listing.valid_until)
        payload = ListingAttributes(sale_end=sale_end, component_item=ItemTypeIdentifier(sequential=component_listing.component_item_type_id), bundle_size=component_listing.bundle_size)
        if component_listing.currency == Currency.PLEX:
            payload.plex.CopyFrom(PlexCurrency(total_in_cents=component_listing.price * 100))
        elif component_listing.currency == Currency.ISK:
            units, nanos = split_precision(component_listing.price)
            payload.isk.CopyFrom(IskCurrency(units=units, nanos=nanos))
        else:
            raise Exception('unknown currency type for skin component listing %s' % component_listing.identifier)
        return payload
