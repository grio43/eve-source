#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveui\data_display\table\column\location.py
from .attribute import AttributeColumn

class LocationColumn(AttributeColumn):

    def get_value(self, entry):
        location_id = super(LocationColumn, self).get_value(entry)
        return cfg.evelocations.Get(location_id).locationName
