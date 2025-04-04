#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\script\net\machoRunTimeStats.py
import sys
import blue
import uthread
import collections
import string
from eveprefs import prefs
BASE_SAMPLE_RATE = 1000
GLOBAL_SAMPLE_PERIODS = 5
SAMPLE_RATE = GLOBAL_SAMPLE_PERIODS * BASE_SAMPLE_RATE
HISTORY_LENGHT = 2000

class MachoRunTimeStats:
    __guid__ = 'macho.MachoRunTimeStats'

    def __init__(self, transportsByID):
        self.stop = False
        self.worker = None
        self.transportsByID = transportsByID
        self.socketStatsEnabled = prefs.GetValue('socketStatsEnabled', False)

    def Enable(self):
        self.stop = False
        self.last = [0,
         0,
         0,
         0,
         0,
         0,
         0,
         0]
        self.maxValues = [0,
         0,
         0,
         0,
         0,
         0,
         0,
         0]
        self.history = collections.deque(maxlen=HISTORY_LENGHT)
        self.packetsSendPerSecond = 0
        self.packetsReceivedPerSecond = 0
        self.totalPacketsPerSecond = 0
        self.KBIn = 0
        self.KBOut = 0
        self.maxPacketsSendPerSecond = 0
        self.maxPacketsReceivedPerSecond = 0
        self.maxTotalPacketsPerSecond = 0
        self.maxKBIn = 0
        self.maxKBOut = 0
        self.lastupdate = blue.os.GetWallclockTime()
        self.worker = uthread.new(self.Worker, self.transportsByID)

    def Disable(self):
        self.stop = True
        if self.worker:
            self.worker.kill()
            self.worker = None

    def Worker(self, transportsByID):
        numSamplePeriods = 0
        while not self.stop:
            delta = blue.os.TimeDiffInMs(self.lastupdate, blue.os.GetWallclockTime()) / 1000L
            self.lastupdate = blue.os.GetWallclockTime()
            if numSamplePeriods % GLOBAL_SAMPLE_PERIODS == 0:
                values = self.last[:]
                mn = sm.services['machoNet']
                self.last[0] = mn.dataSent.Count()
                self.last[1] = mn.dataReceived.Count()
                self.last[2] = mn.dataSent.Current()
                self.last[3] = mn.dataReceived.Current()
                if delta != 0:
                    self.packetsSendPerSecond = float(self.last[0] - values[0]) / delta
                    self.packetsReceivedPerSecond = float(self.last[1] - values[1]) / delta
                    self.totalPacketsPerSecond = self.packetsSendPerSecond + self.packetsReceivedPerSecond
                    self.KBIn = float(self.last[2] - values[2]) / delta
                    self.KBOut = float(self.last[3] - values[3]) / delta
                    self.maxPacketsSendPerSecond = max(self.maxPacketsSendPerSecond, self.packetsSendPerSecond)
                    self.maxPacketsReceivedPerSecond = max(self.maxPacketsReceivedPerSecond, self.packetsReceivedPerSecond)
                    self.maxTotalPacketsPerSecond = max(self.maxTotalPacketsPerSecond, self.totalPacketsPerSecond)
                    self.maxKBIn = max(self.maxKBIn, self.KBIn)
                    self.maxKBOut = max(self.maxKBOut, self.KBOut)
                    self.history.append((blue.os.GetWallclockTime(),
                     self.packetsSendPerSecond,
                     self.packetsReceivedPerSecond,
                     self.KBIn,
                     self.KBOut))
            numSamplePeriods += 1
            if self.socketStatsEnabled:
                for id, machoTransport in transportsByID.iteritems():
                    try:
                        tsp = machoTransport.transport
                        if tsp is not None:
                            tsp.statsBytesRead.Sample()
                            tsp.statsBytesWritten.Sample()
                            tsp.statsPacketsRead.Sample()
                            tsp.statsPacketsWritten.Sample()
                    except AttributeError:
                        sys.exc_clear()

            blue.pyos.synchro.SleepWallclock(BASE_SAMPLE_RATE)


class EWMA(object):
    __guid__ = 'macho.EWMA'

    def __init__(self, factors = None, initialAverage = 0.0, reprFormat = '%.2f'):
        self.factors = factors if factors else [0.1]
        self.averages = [ float(initialAverage) for n in range(0, len(self.factors)) ]
        self.runningTotal = 0
        self.reprFormat = reprFormat

    @classmethod
    def FromSampleCounts(cls, sampleCounts = None, initialAverage = 0.0):
        return EWMA([ 2.0 / (cnt + 1) for cnt in (sampleCounts if sampleCounts else [1]) ], initialAverage)

    def AddSample(self, v = 1):
        self.averages = [ v * f + (1 - f) * avg for f, avg in zip(self.factors, self.averages) ]

    def Add(self, v = 1):
        if self.runningTotal is not None:
            self.runningTotal += v
        else:
            self.runningTotal = v

    def Sample(self, defaultRunningTotal = 0.0):
        if self.runningTotal is not None:
            self.AddSample(self.runningTotal)
            self.runningTotal = None
        elif defaultRunningTotal is not None:
            self.AddSample(defaultRunningTotal)

    def Averages(self):
        return zip(self.averages, self.factors)

    def __repr__(self):
        return string.join([ self.reprFormat % avg for avg in self.averages ], ', ')
