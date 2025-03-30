#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\raffles\client\create\controller.py
import logging
import math
import enum
from eve.common.lib.appConst import factionTriglavian
from eve.common.script.sys.idCheckers import IsStation, IsTriglavianSystem
import eveformat
import evetypes
import inventorycommon.const
import inventorycommon.typeHelpers
from menucheckers.itemCheckers import ItemChecker
import signals
import threadutils
from raffles.common import util
from raffles.common.const import ALLOWED_SINGLETON_TYPE_LIST_ID, GOOD_VALUE_FACTOR, RAFFLE_TAX_PERCENTAGE, TICKET_COUNT_POOL, TOKEN_TYPE_ID, MAX_TOTAL_PRICE, MIN_TOTAL_PRICE
from raffles.common.errors import CreateErrorReason, RafflesError
from raffles.common.raffle_data import RaffleCreationData
logger = logging.getLogger(__name__)

class CreationStatus(enum.IntEnum):
    none = 0
    creating = 1
    success = 2
    failure = 3


class CreatePageController(object):

    def __init__(self, storage, focus_window):
        sm.RegisterForNotifyEvent(self, 'OnRaffleCreationFailedServer')
        sm.RegisterForNotifyEvent(self, 'OnMultipleItemChange')
        self._storage = storage
        self.focus_window = focus_window
        self._ticket_options = [ (str(x), x) for x in TICKET_COUNT_POOL ]
        self._item = None
        self._token = None
        self._solar_system_id = None
        self._total_price = 0
        self._ticket_count = TICKET_COUNT_POOL[0]
        self.is_private = False
        self.raffle_id = None
        self.statistics = None
        self.statistics_fetched = False
        self.status = CreationStatus.none
        self.on_item_changed = signals.Signal(signalName='on_item_changed')
        self.on_token_changed = signals.Signal(signalName='on_token_changed')
        self.on_price_changed = signals.Signal(signalName='on_price_changed')
        self.on_statistics_changed = signals.Signal(signalName='on_statistics_changed')
        self.on_creation_success = signals.Signal(signalName='on_creation_success')
        self.on_creation_failure = signals.Signal(signalName='on_creation_failure')
        self.on_drop_item = signals.Signal(signalName='on_drop_item')
        self.on_drag_enter = signals.Signal(signalName='on_drag_enter')
        self.on_drag_exit = signals.Signal(signalName='on_drag_exit')
        self.on_token_error = signals.Signal(signalName='on_token_error')
        self.on_item_error = signals.Signal(signalName='on_item_error')
        self._storage.on_raffle_created.connect(self._on_raffle_created)
        self.on_drop_item.connect(self._on_drop_item)

    def close(self):
        sm.UnregisterForNotifyEvent(self, 'OnRaffleCreationFailedServer')
        sm.UnregisterForNotifyEvent(self, 'OnMultipleItemChange')
        self._storage.on_raffle_created.disconnect(self._on_raffle_created)
        self.on_item_changed.clear()
        self.on_token_changed.clear()
        self.on_price_changed.clear()
        self.on_statistics_changed.clear()
        self.on_creation_success.clear()
        self.on_creation_failure.clear()
        self.on_drop_item.clear()
        self.on_drag_enter.clear()
        self.on_drag_exit.clear()
        self.on_token_error.clear()
        self.on_item_error.clear()

    def drop_data(self, data):
        item = getattr(data[0], 'item', None)
        if item:
            self.on_drop_item(item)

    def OnMultipleItemChange(self, items, changes):
        if not self.token:
            return
        for item in items:
            if item.itemID == self.token.itemID:
                if item.stacksize == 0 or item.locationID != self.token.locationID:
                    self._set_default_token_stack()
                else:
                    self.token = item
                return

    def OnRaffleCreationFailedServer(self, raffle_id, creation_error):
        if raffle_id != self.raffle_id:
            return
        self._on_raffle_failure(creation_error)

    def _on_raffle_created(self, raffle):
        if raffle.raffle_id != self.raffle_id:
            return
        self.status = CreationStatus.success
        self.on_creation_success(raffle)

    def _on_raffle_failure(self, error):
        self.status = CreationStatus.failure
        error_kwargs = self._get_error_kwargs(error)
        self.on_creation_failure(error, error_kwargs)

    def _get_error_kwargs(self, error):
        if error == CreateErrorReason.ticket_price:
            return {'min_price': eveformat.isk_readable(MIN_TOTAL_PRICE),
             'max_price': eveformat.isk_readable(MAX_TOTAL_PRICE)}
        if error == CreateErrorReason.item_triglavian_system:
            return {'factionID': factionTriglavian}

    def validate_create(self):
        item_error = self.validate_item(self.item)
        if item_error:
            return item_error
        token_error = self.validate_token(self.token)
        if token_error:
            return token_error
        if self.total_price < MIN_TOTAL_PRICE or self.total_price > MAX_TOTAL_PRICE:
            return CreateErrorReason.ticket_price
        if self.ticket_count not in TICKET_COUNT_POOL:
            return CreateErrorReason.ticket_count

    @threadutils.threaded
    def create(self):
        self.status = CreationStatus.creating
        validate_error = self.validate_create()
        if validate_error:
            self._on_raffle_failure(validate_error)
            return
        creation_data = RaffleCreationData(owner_id=session.charid, token_id=self._token.itemID, token_location_id=self._token.locationID, item_id=self._item.itemID, type_id=self._item.typeID, location_id=self._item.locationID, solar_system_id=None, ticket_count=self.ticket_count, ticket_price=self.ticket_price, restriction_id=1 if self.is_private else None)
        raffle_svc = sm.GetService('raffleSvc')
        try:
            self.raffle_id = raffle_svc.create_raffle(creation_data)
        except RafflesError as error:
            self._on_raffle_failure(error.msg)
        except Exception as error:
            logger.exception('Unknown error when creating raffle')
            self._on_raffle_failure(CreateErrorReason.unknown)

    def _update_type_statistics(self):
        self.statistics_fetched = False
        self.statistics = None
        if not self.item:
            return
        self._fetch_type_statistics()

    @threadutils.threaded
    def _fetch_type_statistics(self):
        self.statistics = sm.GetService('raffleSvc').get_type_statistics(self.item.typeID)
        self.statistics_fetched = True
        self.on_statistics_changed()

    def confirm_create_error(self):
        self.status = CreationStatus.none
        self.raffle_id = None
        self.on_item_changed()

    def open_market(self, *args):
        sm.GetService('marketutils').ShowMarketDetails(self.token_type_id)

    def open_nes(self, *args):
        sm.GetService('vgsService').OpenStore(typeIds=[self.token_type_id])

    @property
    def ticket_price(self):
        return long(round(self._total_price / float(self._ticket_count)))

    @property
    def is_low_price(self):
        return self.market_estimate is not None and self.earnings < self.market_estimate

    @ticket_price.setter
    def ticket_price(self, ticket_price):
        self.total_price = ticket_price * self.ticket_count

    @property
    def total_price(self):
        return self._total_price

    @total_price.setter
    def total_price(self, total_price):
        total_price = self._clamp_price(total_price)
        if self._total_price == total_price:
            return
        self._total_price = total_price
        self.on_price_changed()

    def _clamp_price(self, total_price):
        total_price = max(min(total_price, MAX_TOTAL_PRICE), MIN_TOTAL_PRICE)
        ticket_price = long(math.ceil(float(total_price) / self.ticket_count))
        price = ticket_price * self.ticket_count
        if price > MAX_TOTAL_PRICE:
            price = (ticket_price - 1) * self.ticket_count
        return price

    @property
    def ticket_count(self):
        return self._ticket_count

    @ticket_count.setter
    def ticket_count(self, ticket_count):
        self._ticket_count = ticket_count
        self.total_price = self.total_price
        self.on_price_changed()

    @property
    def ticket_options(self):
        return self._ticket_options

    @property
    def sales_tax(self):
        return self.total_price * RAFFLE_TAX_PERCENTAGE

    @property
    def earnings(self):
        return self.total_price - self.sales_tax

    @property
    def item(self):
        return self._item

    @item.setter
    def item(self, item):
        if self.status == CreationStatus.creating:
            return
        if item == self.item:
            return
        if item is not None:
            error = self.validate_item(item)
            if error:
                self.on_item_error(error, self._get_error_kwargs(error))
                return
        self.status = CreationStatus.none
        self.raffle_id = None
        self._solar_system_id = None
        self._item = item
        self._total_price = 0
        self._update_type_statistics()
        if item:
            if not self.token:
                self._set_default_token_stack()
            self._total_price = self._get_default_total_price(item)
        self.on_item_changed()

    @property
    def market_estimate(self):
        if self.item is None:
            return
        if self.item.quantity == -2:
            return
        return inventorycommon.typeHelpers.GetAveragePrice(self.item.typeID)

    def _get_default_total_price(self, item):
        if self.market_estimate is not None:
            return self._clamp_price(self.market_estimate * GOOD_VALUE_FACTOR)
        else:
            return self._clamp_price(MIN_TOTAL_PRICE)

    def clear(self):
        self.item = None

    def validate_item(self, item):
        if item.ownerID != session.charid:
            return CreateErrorReason.item_owner
        if not util.is_type_valid_for_hypernet(item.typeID):
            return CreateErrorReason.item_type
        if not self._validate_singleton(item):
            return CreateErrorReason.item_singleton
        if item.flagID != inventorycommon.const.flagHangar:
            return CreateErrorReason.item_inventory
        if not IsStation(item.locationID):
            return CreateErrorReason.item_location
        solar_system_id = cfg.evelocations.Get(item.locationID).solarSystemID
        if IsTriglavianSystem(solar_system_id):
            return CreateErrorReason.item_triglavian_system

    def _validate_singleton(self, item):
        if not ItemChecker(item).IsSingleton():
            return True
        if evetypes.IsDynamicType(item.typeID):
            return True
        if item.typeID in evetypes.GetTypeIDsByListID(ALLOWED_SINGLETON_TYPE_LIST_ID):
            return True
        return False

    @property
    def type_id(self):
        return self.item.typeID

    @property
    def item_id(self):
        return self.item.itemID

    @property
    def solar_system_id(self):
        if not self._solar_system_id:
            self._solar_system_id = cfg.evelocations.Get(self.item.locationID).solarSystemID
        return self._solar_system_id

    @property
    def location_id(self):
        return self.item.locationID

    @property
    def token(self):
        return self._token

    @token.setter
    def token(self, token):
        error = self.validate_token(token)
        if error:
            self.on_token_error(error)
            return
        self._token = token
        self.on_token_changed()

    def validate_token(self, token):
        if not token:
            return None
        if token.typeID != self.token_type_id:
            return CreateErrorReason.token_type
        if token.ownerID != session.charid:
            return CreateErrorReason.token_owner
        if not IsStation(token.locationID):
            return CreateErrorReason.token_location
        if token.flagID != inventorycommon.const.flagHangar:
            return CreateErrorReason.token_inventory

    @property
    def token_type_id(self):
        return TOKEN_TYPE_ID

    @property
    def token_location_name(self):
        if not self._token:
            return ''
        return cfg.evelocations.Get(self._token.locationID).locationName

    @property
    def tokens_required(self):
        return util.tokens_required(self.total_price)

    @property
    def has_enough_tokens(self):
        if not self._token:
            return False
        return self._token.stacksize >= self.tokens_required

    @property
    def token_amount(self):
        if not self._token:
            return 0
        return self._token.stacksize

    @property
    def enable_create_button(self):
        if not self.token:
            return False
        return True

    def _set_default_token_stack(self):
        token = sm.GetService('raffleSvc').get_largest_token_stack()
        self.token = token

    def _on_drop_item(self, item):
        if item.typeID == self.token_type_id:
            self.token = item
        else:
            self.item = item
        self.focus_window()
