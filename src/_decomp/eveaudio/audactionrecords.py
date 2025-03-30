#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveaudio\audactionrecords.py
import logging
import datetimeutils

class AudActionRecord(object):

    def __init__(self, timestamp):
        self._timestamp = timestamp
        self.emitter = None

    @property
    def label(self):
        return self.GetLabel()

    @property
    def timestamp(self):
        return self._timestamp

    def GetDataAsString(self):
        raise NotImplementedError()

    def GetTimestampString(self):
        return self.timestamp.strftime('%H:%M:%S.%f')[:-3]

    def __str__(self):
        return '{} - {} - {}'.format(self.GetTimestampString(), self.label, self.GetDataAsString())

    @classmethod
    def GetLabel(cls):
        raise NotImplementedError()


class AudActionRecordGeneric(AudActionRecord):

    def __init__(self, recordTypename, timestamp, data):
        super(AudActionRecordGeneric, self).__init__(timestamp)
        self.recordTypename = recordTypename
        self.data = data

    def GetDataAsString(self):
        return 'Record Typename: {} - Data: ({})'.format(self.recordTypename, ', '.join([ str(x) for x in self.data ]))

    @classmethod
    def GetLabel(cls):
        return 'Unknown Record Type'


class AudActionRecordPostEvent(AudActionRecord):

    def __init__(self, timestamp, emitterID, playID, eventID, eventName):
        super(AudActionRecordPostEvent, self).__init__(timestamp)
        self.emitterID = emitterID
        self.playID = playID
        self.eventID = eventID
        self.eventName = eventName

    def GetDataAsString(self):
        return 'Emitter ID: {} - Play ID: {} - Event ID: {} - Event Name {}'.format(self.emitterID, self.playID, self.eventID, self.eventName)

    @classmethod
    def GetLabel(cls):
        return 'Post Event'


class AudActionRecordExecuteActionOnPlayingID(AudActionRecord):

    def __init__(self, timestamp, emitterID, playID, action):
        super(AudActionRecordExecuteActionOnPlayingID, self).__init__(timestamp)
        self.emitterID = emitterID
        self.playID = playID
        self.action = action

    def GetDataAsString(self):
        return 'Emitter ID: {} - Play ID: {} - Action: {}'.format(self.emitterID, self.playID, self.action)

    @classmethod
    def GetLabel(cls):
        return 'Execute Action on Playing ID'


class AudActionRecordSetSwitch(AudActionRecord):

    def __init__(self, timestamp, emitterID, groupName, state):
        super(AudActionRecordSetSwitch, self).__init__(timestamp)
        self.emitterID = emitterID
        self.groupName = groupName
        self.state = state

    def GetDataAsString(self):
        return 'Emitter ID: {} - Group: {} - State: {}'.format(self.emitterID, self.groupName, self.state)

    @classmethod
    def GetLabel(cls):
        return 'Set Switch'


class AudActionRecordSetState(AudActionRecord):

    def __init__(self, timestamp, groupName, state):
        super(AudActionRecordSetState, self).__init__(timestamp)
        self.groupName = groupName
        self.state = state

    def GetDataAsString(self):
        return 'Group: {} - State: {}'.format(self.groupName, self.state)

    @classmethod
    def GetLabel(cls):
        return 'Set State'


class AudActionRecordSetRTPC(AudActionRecord):

    def __init__(self, timestamp, emitterID, rtpcName, value, playID):
        super(AudActionRecordSetRTPC, self).__init__(timestamp)
        self.emitterID = emitterID
        self.rtpcName = rtpcName
        self.value = value
        self.playID = playID

    def GetDataAsString(self):
        return 'Emitter ID: {} - RTPC Name: {} - Value: {} - Play ID: {}'.format(self.emitterID, self.rtpcName, self.value, self.playID)

    @classmethod
    def GetLabel(cls):
        return 'Set RTPC'


ALL_ACTION_RECORD_TYPES = [AudActionRecordPostEvent,
 AudActionRecordExecuteActionOnPlayingID,
 AudActionRecordSetSwitch,
 AudActionRecordSetState,
 AudActionRecordSetRTPC]

def AudActionRecordTupleToInstance(record):
    recordTypename, timestamp, recordData = record[0], datetimeutils.filetime_to_datetime(record[1]), record[2:]
    for each in ALL_ACTION_RECORD_TYPES:
        if recordTypename == each.__name__:
            return each(timestamp, *recordData)

    return AudActionRecordGeneric(timestamp, recordTypename, recordData)
