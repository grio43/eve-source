#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\talecommon\errors.py


class TaleStartErrorFailedRequirement(Exception):

    def __str__(self):
        return 'failed to start tale, template could not be placed here'


class TaleStartErrorLocationInUse(Exception):

    def __str__(self):
        return 'failed to start tale, a tale of the same template type is already running in this location'


class TaleStartErrorHardKill(Exception):

    def __str__(self):
        return "failed to start tale, the hard kill flag is set, you can't start tales"


class TaleStartErrorUnknown(Exception):

    def __str__(self):
        return 'unknown reason'


class TaleStartCannotEndBeforeStart(Exception):

    def __str__(self):
        return 'failed to start tale, end time is before start time'
