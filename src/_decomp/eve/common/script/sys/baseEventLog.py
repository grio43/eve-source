#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\common\script\sys\baseEventLog.py
import collections
import json
import os
import sys
import types
import blue
import bluepy
import log
import monolithmetrics
import stacklesslib.util
import uthread
from caching.memoize import Memoize
from carbon.common.script.sys.service import Service
from carbon.common.script.util.format import FmtDateEng, GetTimeParts
from eve.common.lib import appConst
from eve.common.script.sys import idCheckers
from eveprefs import prefs
from utillib import strx
MAX_ITEMS_IN_LOG = 1000

def FmtEventLogDate(date):
    year, month, wd, day, hour, minute, sec, ms = GetTimeParts(date)
    return '%04d.%02d.%02d %02d:%02d:%02d.%03d' % (year,
     month,
     day,
     hour,
     minute,
     sec,
     ms)


class EventLogChannel(object):

    def __init__(self, broker, configOverrides = {}):
        self.broker = broker
        config = {key:getattr(broker, key) for key in broker.GetConfigKeys()}
        config.update(configOverrides)
        self.__dict__.update(config)
        self.logEvents = collections.deque(maxlen=self.maxEvents)
        self.logEventsJson = collections.deque(maxlen=self.maxEvents)
        self.currFileName = ''
        if self.broker.IsEnabled():
            if self.logPath and not os.path.isdir(self.logPath):
                self.broker.LogNotice('Log path', self.logPath, 'does not exist. Creating it')
                os.mkdir(self.logPath)
            uthread.new(self.Worker)

    def Worker(self):
        while 1:
            blue.pyos.synchro.SleepWallclock(self.persistInterval)
            try:
                if self.logEvents:
                    logEvents = self.logEvents
                    self.logEvents = []
                    if self.logPath:
                        stacklesslib.util.call_on_thread(self.PersistToFile_Thread, (logEvents,))
                if self.logEventsJson:
                    logEvents = self.logEventsJson
                    self.logEventsJson = []
                    if self.logPath:
                        stacklesslib.util.call_on_thread(self.PersistToFile_Thread_Json, (logEvents,))
            except:
                log.LogException()
                sys.exc_clear()

    def PersistToFile_Thread(self, logEvents):
        if len(logEvents) > self.numPersistEventsWarningThreshold:
            self.broker.LogWarn('I am going to persist', len(logEvents), 'events which is above the warning threshold')
        maxEventLength = self.maxEventLength
        delimeter = self.delimeter.replace('\\t', '\t')
        nodeID = self.broker.machoNet.GetNodeID()
        try:
            charID = session.charid
        except:
            charID = None

        startTime = blue.os.GetWallclockTimeNow()
        dateAndHour, minutes = FmtDateEng(startTime, 'ss').split(':')
        fileNameDateTime = dateAndHour + '.%02d' % (int(minutes) - int(minutes) % self.logFileCycleMinutes)
        fileNameDatePart = fileNameDateTime.split(' ')[0]
        self.currFileName = fileName = os.path.join(self.logPath, self.logFileNameFormat % {'dateTime': fileNameDateTime,
         'nodeID': nodeID,
         'charID': charID})
        with open(fileName, 'a') as logFile:
            for timestamp, line in logEvents:
                dt = FmtEventLogDate(timestamp)
                if dt.split(' ')[0] != fileNameDatePart:
                    self.broker.LogInfo('Logline falls on a different day than file', dt, 'vs', fileNameDateTime, 'fudging it.')
                    dt = fileNameDatePart + ' 00:00:00.000'
                txt = '%s%s' % (dt, delimeter)
                txt += delimeter.join(map(strx, line))
                txt = txt.replace('\r', '\\r').replace('\n', '\\n')
                if len(txt) > maxEventLength:
                    txt = txt[:maxEventLength]
                    self.broker.LogWarn('Event too long. Cutting it to', self.maxEventLength, 'characters', txt)
                txt += '\n'
                logFile.write(txt)

        duration = (blue.os.GetWallclockTimeNow() - startTime) / appConst.MSEC
        self.broker.LogInfo('Done persisting', len(logEvents), 'events to', fileName, 'in', duration, 'ms')

    def PersistToFile_Thread_Json(self, logEvents):
        if len(logEvents) > self.numPersistEventsWarningThreshold:
            self.broker.LogWarn('I am going to persist', len(logEvents), 'events which is above the warning threshold')
        maxEventLength = self.maxEventLength
        delimeter = self.delimeter.replace('\\t', '\t')
        nodeID = self.broker.machoNet.GetNodeID()
        try:
            charID = session.charid
        except:
            charID = None

        startTime = blue.os.GetWallclockTimeNow()
        dateAndHour, minutes = FmtDateEng(startTime, 'ss').split(':')
        fileNameDateTime = dateAndHour + '.%02d' % (int(minutes) - int(minutes) % self.logFileCycleMinutes)
        fileNameDatePart = fileNameDateTime.split(' ')[0]
        fileName = os.path.join(self.logPath, self.logFileNameFormatJson % {'dateTime': fileNameDateTime,
         'nodeID': nodeID,
         'charID': charID})
        with open(fileName, 'a') as logFile:
            for timestamp, event in logEvents:
                dt = FmtEventLogDate(timestamp)
                if dt.split(' ')[0] != fileNameDatePart:
                    self.broker.LogInfo('Logline falls on a different day than file', dt, 'vs', fileNameDateTime, 'fudging it.')
                    dt = fileNameDatePart + ' 00:00:00.000'
                try:
                    try:
                        txt = json.dumps(event)
                    except:
                        txt = json.dumps(event, ensure_ascii=False)

                except Exception as e:
                    self.broker.LogError('Error dumping to json. Error was ', e, 'Event Skipped', event)
                    continue

                txt = txt.replace('\r', '\\r').replace('\n', '\\n')
                txt += '\n'
                logFile.write(txt)

        duration = (blue.os.GetWallclockTimeNow() - startTime) / appConst.MSEC
        self.broker.LogInfo('Done persisting', len(logEvents), 'events to', fileName, 'in', duration, 'ms')


class BaseEventLogSvc(Service):
    __update_on_reload__ = 1
    __startupdependencies__ = []
    __dependencies__ = ['machoNet']
    __configvalues__ = {'enabled': 0,
     'persistInterval': 1000,
     'logPath': 'c:\\temp',
     'maxEvents': 100000,
     'maxEventLength': 50000,
     'numPersistEventsWarningThreshold': 10000,
     'maxNumArgsFromClient': 32,
     'maxArgLengthFromClient': 255,
     'delimeter': '\\t',
     'logFileNameFormat': 'events_%(dateTime)s_%(nodeID)s.txt',
     'logFileNameFormatJson': 'events_%(dateTime)s_%(nodeID)s.json',
     'maxNumEventCounters': 10000,
     'logFileCycleMinutes': 60}

    def Run(self, *etc):
        Service.Run(self, etc)
        self.logEventCounter = {}
        self.parameterErrors = set()
        self.defaultChannel = EventLogChannel(self)
        self.channels = {}
        self.jsonDisabled = prefs.GetValue('eventLog.jsonDisabled', 0)
        self.tsvDisabled = prefs.GetValue('eventLog.tsvDisabled', 0)

    def SetupChannel(self, chanName, configOverwrites):
        self.channels[chanName] = EventLogChannel(self, configOverwrites)

    def IsChannelOpen(self, chanName):
        return self.enabled and chanName in self.channels

    @Memoize(1)
    def IsEnabled(self):
        return self.enabled

    def GetConfigKeys(self):
        return self.__configvalues__.keys()

    def AddToLogEventCounter(self, eventName, numArgs):
        if len(self.logEventCounter) > self.maxNumEventCounters:
            self.LogError('The maximum number of event counters has been exceeded!', repr(self.logEventCounter.keys())[:1024])
            return False
        if eventName not in self.logEventCounter:
            self.logEventCounter[eventName] = [numArgs, 0]
        c = self.logEventCounter[eventName]
        if numArgs != c[0]:
            if (eventName, numArgs) not in self.parameterErrors:
                self.LogWarn('Event is being called with different number of arguments. This will lead to inconsistent data!', eventName, 'got', numArgs, 'arguments but expected', c[0], 'arguments. Called from', log.WhoCalledMe(4))
                self.parameterErrors.add((eventName, numArgs))
        self.logEventCounter[eventName][1] += 1
        return True

    def AddLogEvent(self, event, eventLogChannel):
        if eventLogChannel is None:
            if isinstance(event, dict):
                logEvents = self.defaultChannel.logEventsJson
            else:
                logEvents = self.defaultChannel.logEvents
        elif eventLogChannel in self.channels:
            if isinstance(event, dict):
                logEvents = self.channels[eventLogChannel].logEventsJson
            else:
                logEvents = self.channels[eventLogChannel].logEvents
        else:
            return
        logEvents.append((blue.os.GetWallclockTimeNow(), event))

    def CollectArgs(self, args):
        lst = []
        for a in args:
            if type(a) in [types.TupleType, types.ListType]:
                for b in a:
                    lst.append(b)

            else:
                lst.append(a)

        return lst

    @bluepy.TimedFunction('BaseEventLogSvc::LogOwnerEvent')
    def LogOwnerEvent(self, eventName, ownerID, *args, **kwargs):
        monolithmetrics.increment('logownerevent', tags=['json:False'])
        if self.tsvDisabled:
            return
        eventLogChannel = kwargs.get('eventLogChannel', None)
        self.LogInfo('LogOwnerEvent', eventName, ownerID)
        try:
            if not self.IsEnabled():
                return
            self._LogOwnerEvent(eventName, ownerID, eventLogChannel, *args)
            if kwargs.get('otherOwnerID', None):
                otherOwnerIDs = kwargs['otherOwnerID']
                if not isinstance(otherOwnerIDs, list):
                    otherOwnerIDs = [otherOwnerIDs]
                for otherOwnerID in set(otherOwnerIDs):
                    if otherOwnerID and otherOwnerID != ownerID and idCheckers.IsPlayerOwner(otherOwnerID):
                        reciprocalArgs = list(args)
                        reciprocalArgs.append(ownerID)
                        self._LogOwnerEvent((eventName + '|R'), otherOwnerID, eventLogChannel, *reciprocalArgs)

        except:
            log.LogException('Error logging owner event')
            sys.exc_clear()

    @bluepy.TimedFunction('BaseEventLogSvc::LogOwnerEventJson')
    def LogOwnerEventJson(self, eventName, ownerID, *args, **kwargs):
        monolithmetrics.increment('logownerevent', tags=['json:True'])
        if self.jsonDisabled:
            return
        eventLogChannel = kwargs.get('eventLogChannel', None)
        try:
            locationID = args[0]
        except:
            self.LogWarn('Event', eventName, 'written without a locationID')
            locationID = 0

        dct = kwargs
        dct['dateTime'] = FmtEventLogDate(blue.os.GetTime())
        dct['locationID'] = locationID
        noArgs = []
        self.LogInfo('LogOwnerEventJson', eventName, ownerID)
        try:
            if not self.IsEnabled():
                return
            self._LogOwnerEvent(eventName, ownerID, eventLogChannel, *noArgs, **dct)
            if kwargs.get('otherOwnerID', None):
                otherOwnerIDs = kwargs['otherOwnerID']
                if not isinstance(otherOwnerIDs, list):
                    otherOwnerIDs = [otherOwnerIDs]
                for otherOwnerID in set(otherOwnerIDs):
                    if otherOwnerID and otherOwnerID != ownerID and idCheckers.IsPlayerOwner(otherOwnerID):
                        self._LogOwnerEvent((eventName + '|R'), otherOwnerID, eventLogChannel, *noArgs, **dct)

        except:
            log.LogException('Error logging owner event')
            sys.exc_clear()

    def _LogOwnerEvent(self, eventName, ownerID, eventLogChannel, *args, **kwargs):
        event = None
        isok = True
        if not args:
            event = {'eventName': eventName,
             'ownerID': ownerID}
            event.update(kwargs)
            isok = self.AddToLogEventCounter(eventName, len(event))
        else:
            event = [eventName, ownerID]
            event.extend(self.CollectArgs(args))
            isok = True
        if isok:
            self.AddLogEvent(event, eventLogChannel)
        else:
            self.LogError('Offending line is', args)

    def GetHtmlState(self, writer, sess = None, request = None):
        if writer is None:
            numEvents = 0
            for k, v in self.logEventCounter.iteritems():
                numEvents += v[1]

            e = 'enabled' if self.IsEnabled() else 'disabled'
            return 'Event logging is %s<br>%s events have been logged<br>Logging to %s' % (e, numEvents, self.defaultChannel.currFileName)
        else:
            return Service.GetHtmlState(self, writer, sess, request)

    def GetHtmlStateDetails(self, k, v, detailed):
        if k == 'logEvents':
            if detailed:
                return self.ViewCounters()
            else:
                return ('Click to view Counters', None)

    def ViewCounters(self):
        result = '<table><tr><th>Counter</th><th>Args</th><th>Count</th></tr>'
        eventNames = self.logEventCounter.keys()
        eventNames.sort()
        for k in eventNames:
            v = self.logEventCounter[k]
            result += '<tr><td>%s</td><td>%s</td><td>%s</td></tr>' % (k, v[0], v[1])

        result += '</table>'
        return ('Counters', result)

    def LogOwnerEventDualNoLocation(self, eventName, ownerID, *args):
        self.LogOwnerEvent(eventName, ownerID, *[ value for key, value in args ])
        self.LogOwnerEventJson(eventName, ownerID, **{key:value for key, value in args})

    def LogOwnerEventDual(self, eventName, ownerID, locationID, *args):
        self.LogOwnerEvent(eventName, ownerID, locationID, *[ value for key, value in args ])
        self.LogOwnerEventJson(eventName, ownerID, locationID, **{key:value for key, value in args})

    def LogOwnerEventDualWithOtherOwnerID(self, eventName, ownerID, otherOwnerID, locationID, *args):
        self.LogOwnerEvent(eventName, ownerID, locationID, otherOwnerID=otherOwnerID, *[ value for key, value in args ])
        self.LogOwnerEventJson(eventName, ownerID, locationID, otherOwnerID=otherOwnerID, **{key:value for key, value in args})


import carbon.common.script.util.autoexport as autoexport
exports = autoexport.AutoExports('baseEventLog', locals())
