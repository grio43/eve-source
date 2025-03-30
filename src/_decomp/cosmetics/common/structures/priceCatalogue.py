#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\common\structures\priceCatalogue.py
from cosmetics.common.structures.const import PAINT_ELIGIBLE_STRUCTURE_TYPE_IDS
from cosmetics.common.structures.exceptions import StructureTypeNotEligibleError

class PriceCatalogue(object):

    def __init__(self):
        self._price_table = {}
        for structure_type_id in PAINT_ELIGIBLE_STRUCTURE_TYPE_IDS:
            self._price_table[structure_type_id] = {}

    def define_price(self, structure_type_id, duration, price):
        if structure_type_id not in self._price_table:
            raise StructureTypeNotEligibleError
        self._price_table[structure_type_id][duration] = price

    def get_available_durations_sorted(self):
        durations = set()
        for structure_type_id, structure_prices in self._price_table.iteritems():
            for stored_duration, price in structure_prices.iteritems():
                durations.add(stored_duration)

        return sorted(list(durations))

    def get_prices_for_structure_type_id(self, structure_type_id):
        if structure_type_id not in self._price_table:
            raise StructureTypeNotEligibleError
        return self._price_table[structure_type_id]

    def get_prices_for_duration(self, duration):
        result = {}
        for structure_type_id, structure_prices in self._price_table.iteritems():
            for stored_duration, price in structure_prices.iteritems():
                if stored_duration == duration:
                    result[structure_type_id] = price

        return result

    def get_price_for_structure_type_id_and_duration(self, structure_type_id, duration):
        if structure_type_id not in self._price_table:
            raise StructureTypeNotEligibleError
        for stored_duration, price in self._price_table[structure_type_id].iteritems():
            if stored_duration == duration:
                return price

        raise KeyError

    def get_all_prices(self):
        result = set()
        for structure_type_id, structure_prices in self._price_table.iteritems():
            for stored_duration, price in structure_prices.iteritems():
                result.add((structure_type_id, stored_duration, price))

        return result

    def __eq__(self, other):
        return len(self.get_all_prices().difference(other.get_all_prices())) == 0
