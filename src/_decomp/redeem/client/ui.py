#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\redeem\client\ui.py
from collections import defaultdict
import localization

def ShowFulfillmentReport(fulfillment, eve):
    report = FulfillmentReport(fulfillment, eve)
    report.show()


class FulfillmentReport(object):

    def __init__(self, fulfillment, eve):
        self.fulfillment = fulfillment
        self.eve = eve
        self.info = []
        self._add_skillpoints()
        self._add_items_created_in_stations()

    def _add_skillpoints(self):
        skillpoints_rewarded = self.fulfillment.get('skillpoints', 0)
        char_id = self.fulfillment['charID']
        if skillpoints_rewarded:
            self.info.append(localization.GetByLabel('UI/Redeem/SkillPointsReport', skillpoints=skillpoints_rewarded, charID=char_id))

    def _add_items_created_in_stations(self):
        station_info = []
        for stationID, item_list in self._iter_items_by_station():
            station_info.append('%s<br>%s' % (localization.GetByLabel('UI/Redeem/ItemReportForStation', stationID=stationID), '<br>'.join(self._iter_items_entries(item_list))))

        if station_info:
            self.info.append('<br><br>'.join(station_info))

    def _iter_items_by_station(self):
        for station_id, item_list in self._get_items_by_station().iteritems():
            yield (station_id, item_list)

    def _get_items_by_station(self):
        items_by_station = defaultdict(list)
        for item in self.fulfillment.get('itemsCreated', []):
            items_by_station[item['stationID']].append((item['typeID'], item['quantity']))

        return items_by_station

    def _iter_items_entries(self, items):
        for type_id, quantity in items:
            yield self._get_item_created_entry(type_id, quantity)

    def _get_item_created_entry(self, type_id, quantity):
        return localization.GetByLabel('UI/Redeem/ItemCreated', typeID=type_id, quantity=quantity)

    def show(self):
        if self.info:
            self.eve.Message('CustomInfo', {'info': '<br><br>'.join(self.info)})
