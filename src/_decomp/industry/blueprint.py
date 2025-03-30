#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\industry\blueprint.py
import fsdlite
import immutable
import industry

class Blueprint(industry.Base):
    __metaclass__ = immutable.Immutable

    def __new__(cls, *args, **kwargs):
        obj = industry.Base.__new__(cls)
        obj.blueprintTypeID = None
        obj.maxProductionLimit = None
        obj.blueprintID = None
        obj.timeEfficiency = 0
        obj.materialEfficiency = 0
        obj.runsRemaining = -1
        obj.quantity = 1
        obj.original = True
        obj.facilityID = None
        obj.facility = None
        obj.locationID = None
        obj.locationTypeID = None
        obj.locationFlagID = None
        obj.flagID = None
        obj.ownerID = None
        obj.jobID = None
        obj.solarSystemID = None
        obj._activities = {}
        return obj

    def __repr__(self):
        return industry.repr(self, exclude=['_activities'])

    def _get_activities(self):
        return {activityID:activity for activityID, activity in self._activities.iteritems() if activity.is_compatible(self)}

    def _set_activities(self, value):
        if isinstance(value, list):
            value = {int(activity.activityID):activity for activity in value}
        self._activities = {int(industry.ACTIVITY_NAME_IDS.get(activityID, activityID)):activity for activityID, activity in (value or {}).iteritems()}

    activities = property(_get_activities, _set_activities)

    def _get_all_activities(self):
        return self._activities

    all_activities = property(_get_all_activities)

    def _get_typeID(self):
        return self.blueprintTypeID

    typeID = property(_get_typeID)

    def _get_itemID(self):
        return self.blueprintID

    itemID = property(_get_itemID)

    def _get_product(self):
        try:
            if industry.MANUFACTURING in self.activities:
                return self.activities[industry.MANUFACTURING].products[0].typeID
            return self.activities[industry.REACTION].products[0].typeID
        except (KeyError, IndexError):
            pass

    productTypeID = property(_get_product)

    def _get_location(self):
        return industry.Location(itemID=self.locationID, flagID=self.locationFlagID, ownerID=self.ownerID, typeID=self.locationTypeID, solarSystemID=self.solarSystemID)

    location = property(_get_location)


def BlueprintStorage():
    return fsdlite.EveStorage(data='blueprints', cache='blueprints.static', mapping=industry.MAPPING, indexes=industry.INDEXES, coerce=int)
