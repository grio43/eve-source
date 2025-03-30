#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\assetholding\client\inventory\utils.py
from inventoryutil.client.inventory import are_types_in_current_location, get_type_quantities_in_current_location

def are_items_available(items, sourceLocationsOptionsList):
    for sourceLocationOptions in sourceLocationsOptionsList:
        item_and_flag, owner_location, owner_home = sourceLocationOptions
        if item_and_flag is not None:
            _item_id, _flag = item_and_flag
            raise NotImplementedError('Not implemented yet: are_items_available support for sourceLocationItemAndFlag')
        elif owner_location:
            if are_types_in_current_location(items):
                return True
        elif owner_home:
            raise NotImplementedError('Not implemented yet: are_items_available support for sourceLocationOwnerHome')
        else:
            raise ValueError('sourceLocationOptions requires exactly one option be set - got {0}'.format(sourceLocationOptions))

    return False


def get_items_available(quantity_by_type_id, sourceLocationOptions):
    item_and_flag, owner_location, owner_home = sourceLocationOptions
    if item_and_flag is not None:
        _item_id, _flag = item_and_flag
        raise NotImplementedError('Not implemented yet: get_items_available support for sourceLocationItemAndFlag')
    else:
        if owner_location:
            return get_type_quantities_in_current_location(quantity_by_type_id)
        if owner_home:
            raise NotImplementedError('Not implemented yet: get_items_available support for sourceLocationOwnerHome')
        else:
            raise ValueError('sourceLocationOptions requires exactly one option be set - got {0}'.format(sourceLocationOptions))
