#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\parklife\overview\override.py


class OverviewOverride(object):

    def __init__(self):
        self._type = {}
        self._group = {}
        self._category = {}

    def add(self, should_display, type_id = None, group_id = None, category_id = None):
        if type_id:
            self._type[type_id] = should_display
        if group_id:
            self._group[group_id] = should_display
        if category_id:
            self._category[category_id] = should_display
        self._on_change()

    def remove(self, type_id = None, group_id = None, category_id = None):
        self._type.pop(type_id, None)
        self._group.pop(group_id, None)
        self._category.pop(category_id, None)
        self._on_change()

    def _on_change(self):
        sm.ScatterEvent('OnOverviewOverrideChanged')

    def get_state(self, type_id = None, group_id = None, category_id = None):
        if type_id in self._type:
            return self._type[type_id]
        if group_id in self._group:
            return self._group[group_id]
        if category_id in self._category:
            return self._category[category_id]

    def get_state_slim_item(self, slim_item):
        return self.get_state(type_id=slim_item.typeID, group_id=slim_item.groupID, category_id=slim_item.categoryID)
