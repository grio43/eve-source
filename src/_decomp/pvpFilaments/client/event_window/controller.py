#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\pvpFilaments\client\event_window\controller.py
import evetypes
from localization import GetByMessageID
from datetimeutils import datetime_to_filetime

class PVPFilamentEventInfoController(object):

    def __init__(self, filament_type_id):
        self._service = sm.GetService('pvpFilamentSvc')
        self._event_info = None
        if filament_type_id:
            self._event_info = self._service.GetActiveEventByTypeID(filament_type_id)
        else:
            activeEvents = self._service.GetActiveEvents()
            if activeEvents:
                sortedEvents = [ x for x in activeEvents if not x['QA'] ]
                sortedEvents.sort(key=self.sort_event_by_date)
            if sortedEvents:
                self._event_info = sortedEvents[0]
            else:
                self._event_info = self._service.GetMostRecentEvent()

    def sort_event_by_date(self, event):
        return event['startDate']

    def open_market(self, *args):
        sm.GetService('marketutils').ShowMarketDetails(self.filament_type_id)

    @property
    def is_any_event_active(self):
        sortedEvents = [ x for x in self._service.GetActiveEvents() if not x['QA'] ]
        return len(sortedEvents) != 0

    @property
    def data_valid(self):
        return self._event_info is not None

    @property
    def next_event_date(self):
        return self._service.GetNextEventDate()

    @property
    def character_statistics(self):
        return self._service.GetCharacterStatistics(self._event_info)

    @property
    def leaderboard(self):
        return self._service.GetLeaderboard(self._event_info)

    @property
    def ship_restriction_list(self):
        return evetypes.GetTypeIDsByListID(self._event_info['shipRestrictions'])

    @property
    def event_title(self):
        return GetByMessageID(self._event_info['eventNameID'])

    @property
    def event_description(self):
        return GetByMessageID(self._event_info['eventDescriptionID'])

    @property
    def event_start_date(self):
        return datetime_to_filetime(self._event_info['startDate'])

    @property
    def event_end_date(self):
        return datetime_to_filetime(self._event_info['endDate'])

    @property
    def is_qa_filament(self):
        if self._event_info:
            return self._event_info['QA'] != 0
        return False

    @property
    def event_rewards(self):
        return self._event_info['rewards']

    @property
    def filament_type_id(self):
        return self._event_info['filamentTypeID']

    @property
    def filament_name(self):
        return evetypes.GetName(self.filament_type_id)

    @property
    def rewards_hint(self):
        return GetByMessageID(self._event_info['rewardsHintID'])

    @property
    def rules_hint(self):
        return GetByMessageID(self._event_info['rulesHintID'])

    @property
    def ship_restrictions_hint(self):
        return GetByMessageID(self._event_info['shipRestrictionsHintID'])

    @property
    def number_of_fleets(self):
        return self._event_info['numberOfFleets']

    @property
    def fleet_size(self):
        return self._event_info['fleetSize']
