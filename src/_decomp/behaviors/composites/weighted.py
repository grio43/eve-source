#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\composites\weighted.py
from behaviors.composites import Composite
from evemath import weighted_choice

class WeightsMissingError(Exception):
    pass


class ToManyWeightsError(Exception):
    pass


class WeightedSelector(Composite):

    def GetInitialTask(self):
        num_weights = len(self.attributes.subTaskWeights)
        num_tasks = self.SubTaskCount()
        if num_weights < num_tasks:
            raise WeightsMissingError()
        elif num_tasks < num_weights:
            raise ToManyWeightsError()
        num_tasks = max(len(self.attributes.subTaskWeights), self.SubTaskCount())
        choices = [ (self._subTasks[i], self.attributes.subTaskWeights[i]) for i in xrange(num_tasks) ]
        return weighted_choice(choices)

    def DoSubTaskCompleted(self, task):
        self.status = task.status
