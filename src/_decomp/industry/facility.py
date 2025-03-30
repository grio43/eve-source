#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\industry\facility.py
import industry
import collections

class Facility(industry.Base):

    def __init__(self, facilityID = None, typeID = None, ownerID = None, solarSystemID = None, tax = None, distance = None, modifiers = None, online = True, serviceAccess = {}, sccTaxModifier = 1.0):
        self.facilityID = facilityID
        self.typeID = typeID
        self.ownerID = ownerID
        self.solarSystemID = solarSystemID
        self.tax = tax
        self.distance = distance if distance is not None else None
        self.activities = collections.defaultdict(lambda : {'blueprints': set(),
         'categories': set(),
         'groups': set(),
         'invTypes': set()})
        self.modifiers = modifiers or []
        self.online = online
        self.serviceAccess = serviceAccess
        self.sccTaxModifier = sccTaxModifier

    def __repr__(self):
        return industry.repr(self, exclude=['activities'])

    def update_activity(self, activityID, blueprints = None, categories = None, groups = None, invTypes = None):
        self.activities[activityID]['blueprints'].update(blueprints or [])
        self.activities[activityID]['categories'].update(categories or [])
        self.activities[activityID]['groups'].update(groups or [])
        self.activities[activityID]['invTypes'].update(invTypes or [])
