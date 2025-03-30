#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\status.py


class TaskInvalidStatus(object):

    @staticmethod
    def OnUpdated(task):
        raise InvalidStatusError()


class TaskSuccessStatus(object):

    @staticmethod
    def OnUpdated(task):
        task.Exit()


class TaskFailureStatus(TaskSuccessStatus):
    pass


class TaskRunningStatus(object):

    @staticmethod
    def OnUpdated(task):
        task.behaviorTree.StartTaskNextTick(task)


class TaskSuspendedStatus(object):

    @staticmethod
    def OnUpdated(task):
        pass


class TaskBlockingStatus(object):

    @staticmethod
    def OnUpdated(task):
        task.behaviorTree.StartTaskNextTick(task)


class InvalidStatusError(Exception):
    pass
