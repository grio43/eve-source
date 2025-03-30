#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\ship\tradingUtil.py
from cosmetics.client.shipSkinTradingSvc import get_ship_skin_trading_svc
from eve.common.script.sys.idCheckers import IsNPCCorporation
from itertoolsext.Enum import Enum
from localization import GetByLabel
DAY_SECONDS = 86400L

@Enum

class SellDuration(object):
    DAY = 1 * DAY_SECONDS
    THREE_DAYS = 3 * DAY_SECONDS
    WEEK = 7 * DAY_SECONDS
    TWO_WEEKS = 14 * DAY_SECONDS
    MONTH = 30 * DAY_SECONDS
    THREE_MONTHS = 90 * DAY_SECONDS


SELL_DURATION_LABELS = {SellDuration.DAY: GetByLabel('UI/Common/DateWords/Day'),
 SellDuration.THREE_DAYS: GetByLabel('UI/Market/MarketQuote/ThreeDays'),
 SellDuration.WEEK: GetByLabel('UI/Common/DateWords/Week'),
 SellDuration.TWO_WEEKS: GetByLabel('UI/Market/MarketQuote/TwoWeeks'),
 SellDuration.MONTH: GetByLabel('UI/Common/DateWords/Month'),
 SellDuration.THREE_MONTHS: GetByLabel('UI/Market/MarketQuote/ThreeMonths')}

@Enum

class SellAvailability(object):
    PUBLIC = 1
    MY_CORPORATION = 2
    MY_ALLIANCE = 3
    SPECIFIC = 4


SELL_AVAILABILITY_LABELS = {SellAvailability.PUBLIC: GetByLabel('UI/Personalization/ShipSkins/SKINR/Collection/SellAvailability/Public'),
 SellAvailability.MY_CORPORATION: GetByLabel('UI/Personalization/ShipSkins/SKINR/Collection/SellAvailability/MyCorporation'),
 SellAvailability.MY_ALLIANCE: GetByLabel('UI/Personalization/ShipSkins/SKINR/Collection/SellAvailability/MyAlliance'),
 SellAvailability.SPECIFIC: GetByLabel('UI/Personalization/ShipSkins/SKINR/Collection/SellAvailability/Specific')}

def get_sell_duration_options():
    listing_durations = get_ship_skin_trading_svc().get_available_listing_durations()
    options = []
    for duration in listing_durations:
        if duration == SellDuration.DAY:
            options.append([SELL_DURATION_LABELS[SellDuration.DAY], SellDuration.DAY])
        elif duration == SellDuration.THREE_DAYS:
            options.append([SELL_DURATION_LABELS[SellDuration.THREE_DAYS], SellDuration.THREE_DAYS])
        elif duration == SellDuration.WEEK:
            options.append([SELL_DURATION_LABELS[SellDuration.WEEK], SellDuration.WEEK])
        elif duration == SellDuration.TWO_WEEKS:
            options.append([SELL_DURATION_LABELS[SellDuration.TWO_WEEKS], SellDuration.TWO_WEEKS])
        elif duration == SellDuration.MONTH:
            options.append([SELL_DURATION_LABELS[SellDuration.MONTH], SellDuration.MONTH])
        elif duration == SellDuration.THREE_MONTHS:
            options.append([SELL_DURATION_LABELS[SellDuration.THREE_MONTHS], SellDuration.THREE_MONTHS])

    return options


def get_sell_availability_options():
    options = [(SELL_AVAILABILITY_LABELS[SellAvailability.PUBLIC], SellAvailability.PUBLIC)]
    if session.corpid and not IsNPCCorporation(session.corpid):
        options.append((SELL_AVAILABILITY_LABELS[SellAvailability.MY_CORPORATION], SellAvailability.MY_CORPORATION))
    if session.allianceid:
        options.append((SELL_AVAILABILITY_LABELS[SellAvailability.MY_ALLIANCE], SellAvailability.MY_ALLIANCE))
    options.append((SELL_AVAILABILITY_LABELS[SellAvailability.SPECIFIC], SellAvailability.SPECIFIC))
    return options
