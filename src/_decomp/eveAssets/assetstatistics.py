#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveAssets\assetstatistics.py
import inventorycommon

class AssetStatistics:

    def __init__(self, get_item_type_function, get_item_quantity_function):
        self._type_info = inventorycommon.typeHelpers
        self.get_item_type_function = get_item_type_function
        self.get_item_quantity_function = get_item_quantity_function

    def calculate_items_net_worth(self, items):
        total_net_worth = 0
        for item in items:
            total_net_worth += self.calculate_item_net_worth(item)

        return total_net_worth

    def calculate_item_net_worth(self, item):
        item_net_worth = 0
        type_id = self.get_item_type_function(item)
        average_price_of_type = self._get_average_price_for_type(type_id)
        if average_price_of_type > 0:
            quantity = self.get_item_quantity_function(item)
            item_net_worth = average_price_of_type * quantity
        return item_net_worth

    def _get_average_price_for_type(self, type_id):
        return self._type_info.GetAveragePrice(type_id) or 0.0
