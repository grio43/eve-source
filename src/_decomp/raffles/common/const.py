#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\raffles\common\const.py
from carbon.common.lib.const import DAY
import enum
import inventorycommon.const as invconst
VALIDATION_TYPE_LIST_ID = 133
ALLOWED_SINGLETON_TYPE_LIST_ID = 134
TOKEN_TYPE_ID = invconst.typeRaffleToken
BROKERS_FEE = 0.05
RAFFLE_TAX_PERCENTAGE = 0.05
RAFFLE_DURATION = 3 * DAY
MIN_TOTAL_PRICE = 1000
MAX_TOTAL_PRICE = 10000000000000L
GOOD_VALUE_FACTOR = 1.4
BAD_VALUE_FACTOR = 2.0
FEW_TICKETS_REMAINING = 0.25
TICKET_COUNT_POOL = (8, 16, 48, 512)
RESTRICTED_COUNTRIES = ('KR',)
PKN_CORP_ID = 1000300

class BlueprintType(enum.IntEnum):
    all = 0
    original = 1
    copy = 2


class RaffleStatus(enum.IntEnum):
    created = 1
    inventory_pending = 2
    inventory_received = 3
    token_pending = 4
    token_received = 5
    running = 6
    finished_undelivered = 7
    finished_delivered = 8
    finished_expired = 9


class Tag(enum.IntEnum):
    rare = 0
    high_price = 1
