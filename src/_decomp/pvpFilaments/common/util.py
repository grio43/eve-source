#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\pvpFilaments\common\util.py
import datetime
from pvpFilaments.common import fsd_loaders
from eveprefs import boot
from gametime import downtime
from utillib import KeyVal

def get_all_events():
    match_types = fsd_loaders.get_match_types()
    all_event_dates = fsd_loaders.get_event_dates()
    result = []
    for schedule_id, event_date in all_event_dates.iteritems():
        region = event_date.region or 'ccp'
        if region != boot.region:
            continue
        result.append(_construct_info(match_types[event_date.matchTypeID], event_date, schedule_id))

    return result


def get_active_events():
    match_types = fsd_loaders.get_match_types()
    all_event_dates = fsd_loaders.get_event_dates()
    result = []
    for schedule_id, event_date in all_event_dates.iteritems():
        if _is_event_active(event_date):
            result.append(_construct_info(match_types[event_date.matchTypeID], event_date, schedule_id))

    return result


def get_past_events():
    match_types = fsd_loaders.get_match_types()
    all_event_dates = fsd_loaders.get_event_dates()
    result = []
    for schedule_id, event_date in all_event_dates.iteritems():
        if _is_event_over(event_date):
            result.append(_construct_info(match_types[event_date.matchTypeID], event_date, schedule_id))

    return result


def get_next_active_event_date():
    all_event_dates = fsd_loaders.get_event_dates().values()
    next_active_date = None
    all_event_dates_sorted = sorted(all_event_dates, key=lambda i: i.startDate)
    for event_date in all_event_dates_sorted:
        next_active_date = _next_date(event_date)
        if next_active_date is not None:
            break

    return next_active_date


def get_most_recent_event():
    match_types = fsd_loaders.get_match_types()
    all_event_dates = fsd_loaders.get_event_dates()
    most_recent_date = None
    all_event_dates_sorted = sorted(all_event_dates.items(), key=lambda i: i[1].endDate, reverse=True)
    for schedule_id, event_date in all_event_dates_sorted:
        if _is_event_over(event_date):
            most_recent_date = _construct_info(match_types[event_date.matchTypeID], event_date, schedule_id)
            break

    return most_recent_date


def get_event_by_filament(filament_type_id):
    match_types = fsd_loaders.get_match_types()
    event_dates = fsd_loaders.get_event_dates()
    for schedule_id, event_date in event_dates.iteritems():
        match_type = match_types[event_date.matchTypeID]
        if match_type.filamentTypeID != filament_type_id:
            continue
        if _is_event_active(event_date):
            return _construct_info(match_type, event_date, schedule_id)


def _next_date(event_date):
    region = event_date.region or 'ccp'
    if region != boot.region:
        return None
    if event_date.QA:
        return None
    start_date = _get_date_from_string(event_date.startDate)
    end_date = _get_date_from_string(event_date.endDate)
    today = datetime.date.today()
    if start_date < today and end_date > today:
        return event_date.startDate
    if start_date > today:
        return event_date.startDate


def _is_event_over(event_date):
    region = event_date.region or 'ccp'
    if region != boot.region:
        return False
    if event_date.QA:
        return False
    end_date = _get_date_from_string(event_date.endDate)
    today = datetime.date.today()
    if end_date < today:
        return True
    if end_date == today and downtime.is_downtime_done_today():
        return True
    return False


def _is_event_active(event_date):
    region = event_date.region or 'ccp'
    if region != boot.region:
        return False
    if event_date.QA:
        return True
    start_date = _get_date_from_string(event_date.startDate)
    end_date = _get_date_from_string(event_date.endDate)
    today = datetime.date.today()
    if start_date > today:
        return False
    if end_date < today:
        return False
    if start_date == today and not downtime.is_downtime_done_today():
        return False
    if end_date == today and downtime.is_downtime_done_today():
        return False
    return True


def _get_date_from_string(date_string):
    if not date_string:
        return None
    year, month, day = date_string.split('-')
    return datetime.date(int(year), int(month), int(day))


def GetEventID(eventInfo):
    return '{}_{}'.format(eventInfo['matchTypeID'], eventInfo['scheduleID'])


def _construct_info(match_type, event_dates, schedule_id):
    rewards = [ KeyVal(typeID=reward.typeID, amount=reward.amount) for reward in match_type.rewards ]
    return KeyVal(matchTypeID=event_dates.matchTypeID, scheduleID=schedule_id, filamentTypeID=match_type.filamentTypeID, numberOfFleets=match_type.numberOfFleets, fleetSize=match_type.fleetSize, shipRestrictions=match_type.shipRestrictions, rewards=rewards, eventNameID=match_type.eventNameID, eventDescriptionID=match_type.eventDescriptionID, filamentDescriptionID=match_type.filamentDescriptionID, restrictionsDescriptionID=match_type.restrictionsDescriptionID, rewardsHintID=match_type.rewardsHintID, shipRestrictionsHintID=match_type.shipRestrictionsHintID, rulesHintID=match_type.rulesHintID, startDate=_get_date_from_string(event_dates.startDate), endDate=_get_date_from_string(event_dates.endDate), QA=event_dates.QA, moduleAndImplantMetaLevelRestrictions=match_type.moduleAndImplantMetaLevelRestrictions, maxOfShipTypeRestriction=match_type.maxOfShipTypeRestriction, maxOfShipGroupRestriction=match_type.maxOfShipGroupRestriction, minimumQueueSizeMultiplier=match_type.minimumQueueSizeMultiplier, provingGroundLootTableID=match_type.provingGroundLootTableID, bannedModulesTypeListID=match_type.bannedModulesTypeListID, limitedAmountOfModulesTypeListID=match_type.limitedAmountOfModulesTypeListID, numberOfLimitedModules=match_type.numberOfLimitedModules)
