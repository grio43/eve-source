#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\industry\activity.py
import math
import operator
import immutable
import industry
import structures

class Activity(industry.Base):
    __metaclass__ = immutable.Immutable
    REQUIRES_ORIGINAL = False
    REQUIRES_COPY = False
    MAX_RUNS = industry.MAX_RUNS_HARD_CAP

    def __new__(cls, *args, **kwargs):
        obj = industry.Base.__new__(cls)
        obj.time = 0
        obj.materials = []
        obj.skills = []
        obj.products = []
        return obj

    def job_modifiers(self, job):
        return []

    def job_probability(self, job):
        return 1.0

    def job_time(self, job):
        return self.time * job.runs

    def job_cost(self, job):
        return 0

    def job_max_runs(self, job):
        modifiers = [ modifier.amount for modifier in job.input_modifiers if isinstance(modifier, industry.TimeModifier) and modifier.activity in (None, job.activityID) ]
        return min(int(math.ceil(industry.MAX_RUN_LENGTH / float(self.time) / reduce(operator.mul, modifiers, 1.0))), self.MAX_RUNS)

    def job_material_runs(self, job):
        return job.runs

    def job_output_products(self, job):
        return []

    def job_output_extras(self, job):
        return []

    def job_validate(self, job):
        pass

    def activity_tax(self, facility):
        if facility.tax is not None:
            return facility.tax
        typeID = None
        if self.activityID in (industry.MANUFACTURING, industry.REACTION):
            typeID = self.products[0].typeID
        serviceID = structures.GetServiceID(self.activityID, typeID)
        return facility.serviceAccess.get(serviceID, 0) or 0

    def is_compatible(self, blueprint):
        if self.REQUIRES_ORIGINAL is True and not blueprint.original:
            return False
        if self.REQUIRES_COPY is True and blueprint.original:
            return False
        return True

    def _get_activityID(self):
        return industry.ACTIVITY_IDS[self.__class__]

    activityID = property(_get_activityID)
