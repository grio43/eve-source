#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\conditions\industry.py
from __future__ import absolute_import
from carbonui.control.window import Window
import evetypes
from nodegraph.common.util import get_object_predicate
from nodegraph.client.util import get_item_name
from .base import Condition

class HasIndustryJob(Condition):
    atom_id = 510

    def __init__(self, type_id = None, group_id = None, status = None, **kwargs):
        super(Condition, self).__init__(**kwargs)
        self.type_id = type_id
        self.group_id = group_id
        self.status = self.get_atom_parameter_value('status', status)

    def validate(self, **kwargs):
        if self.type_id:
            predicate = get_object_predicate('blueprintTypeID', self.type_id)
        elif self.group_id:
            group_id = self.group_id

            def predicate_function(item):
                return evetypes.GetGroupID(item.blueprintTypeID) == group_id

            predicate = predicate_function
        else:
            predicate = lambda x: True
        from industry.const import JOB_STATUS_NAME_IDS
        jobs = sm.GetService('industrySvc').GetCharacterJobs(includeCompleted=False, useCached=True)
        for job in jobs:
            if predicate(job) and (self.status == 'any' or job.status == JOB_STATUS_NAME_IDS.get(self.status)):
                return True

        return False

    @classmethod
    def get_subtitle(cls, type_id = None, group_id = None, status = None, **kwargs):
        return u'{} - {}'.format(cls.get_atom_parameter_value('status', status), get_item_name(type_id=type_id, group_id=group_id))


class IndustryJobSelected(Condition):
    atom_id = 514

    def __init__(self, item_id = None, type_id = None, group_id = None, activity_id = None, minimum_runs = None, **kwargs):
        super(Condition, self).__init__(**kwargs)
        self.item_id = item_id
        self.type_id = type_id
        self.group_id = group_id
        self.activity_id = self.get_atom_parameter_value('activity_id', activity_id)
        self.minimum_runs = self.get_atom_parameter_value('minimum_runs', minimum_runs)

    def validate(self, **kwargs):
        from eve.client.script.ui.shared.industry.industryWnd import Industry as IndustryWindow
        industry_window = IndustryWindow.GetIfOpen()
        if not industry_window or not industry_window.jobData:
            return False
        job_data = industry_window.jobData
        from industry.const import ACTIVITY_NAME_IDS
        if self.activity_id != 'any' and job_data.activityID != ACTIVITY_NAME_IDS[self.activity_id]:
            return False
        elif job_data.runs < self.minimum_runs:
            return False
        elif self.item_id:
            return job_data.blueprint.itemID == self.item_id
        elif self.type_id:
            return job_data.blueprint.typeID == self.type_id
        elif self.group_id:
            return evetypes.GetGroupID(job_data.blueprint.typeID) == self.group_id
        else:
            return True

    @classmethod
    def get_subtitle(cls, type_id = None, group_id = None, activity_id = None, **kwargs):
        return u'{} - {}'.format(cls.get_atom_parameter_value('activity_id', activity_id), get_item_name(type_id=type_id, group_id=group_id))


class IndustryJobError(Condition):
    atom_id = 517

    def __init__(self, error_type = None, **kwargs):
        super(Condition, self).__init__(**kwargs)
        self.error_type = self.get_atom_parameter_value('error_type', error_type)

    def validate(self, **kwargs):
        from eve.client.script.ui.shared.industry.industryWnd import Industry as IndustryWindow
        industry_window = IndustryWindow.GetIfOpen()
        if not industry_window or not industry_window.jobData:
            return False
        errors = industry_window.jobData.errors
        if not errors:
            return False
        if self.error_type == 'any':
            return True
        from industry.const import Error
        error_type = getattr(Error, self.error_type, None)
        error_types = set((error[0] for error in errors))
        return error_type in error_types

    @classmethod
    def get_subtitle(cls, error_type = None, **kwargs):
        return cls.get_atom_parameter_value('error_type', error_type)


class ReprocessingMaterial(Condition):
    atom_id = None

    def __init__(self, type_id = None, group_id = None, minimum_amount = None, **kwargs):
        super(Condition, self).__init__(**kwargs)
        self.type_id = type_id
        self.group_id = group_id
        self.minimum_amount = self.get_atom_parameter_value('minimum_amount', minimum_amount)

    def validate(self, **kwargs):
        window = Window.GetIfOpen('reprocessingWindow')
        if not window:
            return False
        if self.type_id:
            predicate = get_object_predicate('typeID', self.type_id)
        elif self.group_id:
            group_id = self.group_id

            def predicate_function(item):
                return evetypes.GetGroupID(item.typeID) == group_id

            predicate = predicate_function
        else:
            return False
        amount = 0
        for output_item in self.get_items(window.controller):
            if predicate(output_item):
                amount += self.get_item_amount(output_item)
                if amount >= self.minimum_amount:
                    return True

        return False

    def get_items(self, controller):
        return []

    def get_item_amount(self, item):
        return 0

    @classmethod
    def get_subtitle(cls, type_id = None, group_id = None, minimum_amount = None, **kwargs):
        return u'{} >= {}'.format(get_item_name(type_id=type_id, group_id=group_id), cls.get_atom_parameter_value('minimum_amount', minimum_amount))


class ReprocessingOutputMaterial(ReprocessingMaterial):
    atom_id = 504

    def get_items(self, controller):
        if not controller.GetInputItems():
            return []
        return controller.GetOutputItems().values()

    def get_item_amount(self, item):
        return item.client


class ReprocessingInputMaterial(ReprocessingMaterial):
    atom_id = 506

    def get_items(self, controller):
        return controller.GetInputItems()

    def get_item_amount(self, item):
        return item.stacksize
