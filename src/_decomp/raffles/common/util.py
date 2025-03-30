#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\raffles\common\util.py
from __future__ import absolute_import, division
from eveprefs import prefs
from evetypes import GetTypeIDsByListID
import inventorycommon.const as invconst
import inventorycommon.typeHelpers
from inventoryrestrictions import is_tradable
from raffles.common.const import BROKERS_FEE, VALIDATION_TYPE_LIST_ID
LOCAL_DEFAULT_PLEX_PRICE = 3500000

def tokens_required(total_price):
    return max(1, int(total_price / _get_token_price() * BROKERS_FEE))


def _get_token_price():
    return max(1, _get_plex_price() / 10)


def _get_plex_price():
    plex_price = _get_plex_price_override()
    if not plex_price:
        plex_price = inventorycommon.typeHelpers.GetAveragePrice(invconst.typePlex)
    if not plex_price and prefs.clusterMode == 'LOCAL':
        plex_price = LOCAL_DEFAULT_PLEX_PRICE
    if not plex_price:
        raise RuntimeError('PLEX market price not available')
    return plex_price


def _get_plex_price_override():
    try:
        global_config = sm.GetService('machoNet').GetGlobalConfig()
        return int(global_config.get('HyperNetPlexPriceOverride', 0))
    except Exception:
        return None


def is_kill_switch_enabled(macho_net):
    try:
        return bool(int(macho_net.GetGlobalConfig().get('HyperNetKillSwitch', False)))
    except ValueError:
        return False


def is_type_valid_for_hypernet(type_id):
    return is_tradable(type_id) and type_id not in GetTypeIDsByListID(VALIDATION_TYPE_LIST_ID)
