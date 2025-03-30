#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\planet\mecDen\mercDenUtil.py


class MercDenEntryInfo(object):

    def __init__(self, itemID, mercDen = None, activities = None):
        self._item_id = itemID
        self._mercDen = mercDen
        self._activities = activities

    @property
    def item_id(self):
        return self._item_id

    @property
    def type_id(self):
        if self._mercDen:
            return self._mercDen.type_id

    @property
    def is_enabled(self):
        if self._mercDen:
            return self._mercDen.is_enabled
        return False

    @property
    def solar_system_id(self):
        if self._mercDen:
            return self._mercDen.solar_system_id

    @property
    def infomorphs_info(self):
        if self._mercDen:
            return self._mercDen.infomorphs_info

    @property
    def owner_id(self):
        if self._mercDen:
            return self._mercDen.owner_id

    @property
    def skyhook_id(self):
        if self._mercDen:
            return self._mercDen.skyhook_id

    @property
    def planet_id(self):
        if self._mercDen:
            return self._mercDen.planet_id

    @property
    def activities(self):
        return self._activities or []

    @property
    def mercenary_den_info(self):
        return self._mercDen

    @property
    def has_complete_info(self):
        if self._mercDen:
            return True
        return False


DEN_COL_NAME = 'name'
DEN_COL_SYSTEM = 'system'
DEN_COL_PLANET = 'planet'
DEN_COL_STATE = 'state'
DEN_COL_INFOM = 'infomorphs'
DEN_COL_MTO = 'mtos'
