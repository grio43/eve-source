#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\util\profiling.py
import blue
import stackless
import uthread
from carbon.common.script.sys.service import Service
from carbon.common.script.sys.serviceConst import ROLE_ANY
from carbon.common.script.util import timerstuff
from carbon.common.script.util.format import FmtDate
from eve.common.lib import appConst as const
from eveprefs import boot

class TotalProfiler:

    def __init__(self):
        self.file = None
        self.timer = None
        self.startMem = None
        self.snapshotDict = {}

    def Start(self):
        now = blue.os.GetWallclockTime()
        datestr = FmtDate(now, 'sl')
        datestr = datestr.replace('.', '')
        datestr = datestr.replace(':', '')
        datestr = datestr.replace(' ', '')
        import os
        self.file = file(os.path.join(blue.paths.ResolvePath(u'cache:/'), 'prfl' + datestr + '.txt'), 'w')
        self.file.write('<profiling>\r\n')
        self.file.write('<data name="time" type="int">' + datestr[-6:] + '</data>\r\n')
        self.file.write('<data name="date" type="int">' + datestr[:-6] + '</data>\r\n')
        self.file.write('<data name="build" type="int">' + str(boot.build) + '</data>\r\n')
        self.startMem = blue.sysinfo.GetMemory()

    def StartLocation(self, location):
        self.file.write('<locations type="list" name="location">\r\n')
        self.file.write('<location id="TheLocation">\r\n')

    def EndLocation(self):
        self.file.write('</location>\r\n')
        self.file.write('</locations>\r\n')

    def Finish(self):
        endMem = blue.sysinfo.GetMemory()
        self.file.write('<data name="NettoMemory" type="int" signifier="Kb">' + str((endMem.pageFile - self.startMem.pageFile) / 1024) + '</data>\r\n')
        self.file.write('</profiling>\r\n')
        self.file.close()

    def BeginSnapshot(self, name):
        key = uthread.uniqueId()
        snapshot = self.snapshotDict[key] = Snapshot(name)
        tasklets = blue.pyos.taskletTimer.GetTasklets().values()
        snapshot.taskletStart = map(lambda i: (str(i.context), i.switches, i.time), filter(lambda i: i.context != 'Idle Thread' and i.time, tasklets))
        snapshot.memoryStart = blue.sysinfo.GetMemory().pageFile
        return key

    def EndSnapshot(self, key):
        snapshot = self.snapshotDict[key]
        snapshot.end = blue.os.GetWallclockTimeNow()
        tasklets = blue.pyos.taskletTimer.GetTasklets().values()
        snapshot.taskletEnd = map(lambda i: (str(i.context), i.switches, i.time), filter(lambda i: i.context != 'Idle Thread' and i.time, tasklets))
        snapshot.memoryEnd = blue.sysinfo.GetMemory().pageFile

    def ProcessSnapshots(self):
        self.file.write('<snapshots type="list" name="snapshot">\r\n')
        for key, snapshot in self.snapshotDict.iteritems():
            tasklets = snapshot.ProcessTasklets()
            self.file.write('<snapshot name="' + snapshot.name + '" id="' + str(key) + '">\r\n')
            self.file.write('<data name="tasklets" type="list">\r\n')
            for each in tasklets:
                self.file.write(str(each) + '\r\n')

            self.file.write('</data>\r\n')
            self.file.write('<data name="ms" type="int" signifier="ms">' + str(blue.os.TimeDiffInMs(snapshot.start, snapshot.end)) + '</data>\r\n')
            self.file.write('<Memory>\r\n')
            self.file.write('<data name="usage" type="int" signifier="Kb">' + str((snapshot.memoryEnd - snapshot.memoryStart) / 1024) + '</data>\r\n')
            self.file.write('</Memory>\r\n')
            self.file.write('</snapshot>\r\n')

        self.file.write('</snapshots>\r\n')


class FPSProfiler:

    def Start(self, file, ms = 10000):
        self.minValue = 10000000.0
        self.maxValue = -1.0
        self.num = 0
        self.accum = 0.0
        self.run = 1
        self.start = blue.os.GetWallclockTimeNow()
        self.endtimer = timerstuff.AutoTimer(ms, self.Finish, file)
        uthread.new(self.Start_thread).context = 'profiling.FPSProfiler.Start'

    def Start_thread(self):
        while self.run:
            self.num += 1
            fps = blue.os.fps
            if fps > self.maxValue:
                self.maxValue = fps
            elif fps < self.minValue:
                self.minValue = fps
            blue.pyos.synchro.Yield()

    def Finish(self, file):
        self.endtimer = None
        self.run = 0
        end = blue.os.GetWallclockTimeNow()
        totTime = blue.os.TimeDiffInMs(self.start, end)
        FPS = self.num * 1000.0 / totTime
        file.write('<FPS>\r\n')
        file.write('<data name="average" type="float">' + str(FPS) + '</data>\r\n')
        file.write('<data name="max" type="float">' + str(self.maxValue) + '</data>\r\n')
        file.write('<data name="min" type="float">' + str(self.minValue) + '</data>\r\n')
        file.write('</FPS>\r\n')


class DispatchProfiler:

    def __init__(self):
        self.startMem = None
        self.startNet = None
        self.started = 0

    def Start(self):
        self.started = 1
        self.startMem = blue.sysinfo.GetMemory()
        self.startNet = sm.GetService('machoNet').GetConnectionProperties()
        blue.pyos.taskletTimer.Reset()

    def Finish(self, file):
        if not self.started:
            raise RuntimeError('Flush before start')
        self.started = 0
        tasklets = blue.pyos.taskletTimer.GetTasklets().values()
        tasklets = map(lambda i: (str(i.context), i.switches, i.time), filter(lambda i: i.context != 'Idle Thread' and i.time, tasklets))
        blue.pyos.taskletTimer.Reset()
        self.endNet = sm.GetService('machoNet').GetConnectionProperties()
        file.write('<data name="ConnectionProperties" type="dict">\r\n')
        for key in self.startNet.iterkeys():
            file.write(key + ': ' + str(self.endNet[key] - self.startNet[key]) + '\r\n')

        file.write('</data>\r\n')
        file.write('\r\n<data name="tasklets" type="list">\r\n')
        for each in tasklets:
            file.write(str(each) + '\r\n')

        file.write('</data>\r\n')
        tasklets = None
        endMem = blue.sysinfo.GetMemory()
        file.write('<Memory>\r\n')
        file.write('<data name="usage" type="int" signifier="Kb">' + str((endMem.pageFile - self.startMem.pageFile) / 1024) + '</data>\r\n')
        file.write('</Memory>\r\n')


class Snapshot:

    def __init__(self, name = ''):
        self.taskletStart = None
        self.taskletEnd = None
        self.memoryStart = 0
        self.memoryEnd = 0
        self.start = blue.os.GetWallclockTimeNow()
        self.end = self.start
        self.name = name

    def ProcessTasklets(self):
        aDict = {}
        for each in self.taskletEnd:
            aDict[each[0]] = list(each)

        for each in self.taskletStart:
            if each[0] in aDict:
                aDict[each[0]][1] = aDict[each[0]][1] - each[1]
                aDict[each[0]][2] = aDict[each[0]][2] - each[2]

        return aDict.values()


class ProfilingScheduler(Service):
    __guid__ = 'svc.profiling'
    __exportedcalls__ = {'StartDispatching': [ROLE_ANY],
     'StartProfiling': [ROLE_ANY],
     'BeginSnapshot': [ROLE_ANY],
     'EndSnapshot': [ROLE_ANY]}
    __notifyevents__ = ['OnClientEvent_WarpFinished', 'OnSessionChanged']
    __dependencies__ = ['michelle']
    running = 0

    def __init__(self):
        Service.__init__(self)
        self.channel = stackless.channel()
        self.keepAlive = NonniEvent(2000)
        self.totalProfiler = TotalProfiler()
        self.FPSProfiler = FPSProfiler()
        self.dispatchProfiler = DispatchProfiler()
        self.timer = None
        self.snapshotDict = {}

    def Run(self, memstream = None):
        Service.Run(self, memstream)
        if not self.SetUpEnvironment():
            raise RuntimeError('environment not suitable for profiling')

    def StartDispatching(self):
        self.dispatchProfiler.Start()

    def SetUpEnvironment(self):
        if settings.public.generic.Get('memoryMapping', 1):
            print 'memory mapping should be turned off for normal profiling'
            print 'in prefs.ini set'
            print 'memoryMapping=0'
            print 'and restart EVE'
            return 0
        if not eve.session.charid:
            eve.Message('CustomInfo', {'info': 'You have to be in the game to use the profiler'})
            return 0
        return 1

    def StartProfiling(self, start, locationList):
        itemInPark = sm.GetService('michelle').GetBall(start)
        haveToWait = 1
        if itemInPark:
            from eve.client.script.ui.util import uix
            if uix.GetDistanceBetweenBalls(itemInPark, sm.GetService('michelle').GetBall(session.shipid)) > const.minWarpDistance:
                self.WarpTo(start)
            else:
                haveToWait = 0
        else:
            cmdstring = '/tr me %s' % start
            slashRes = sm.RemoteSvc('slash').SlashCmd(cmdstring)
        if haveToWait:
            self.LogInfo('Waiting until in place')
            self.channel.receive()
        self.LogInfo('Ready to run')
        self.LogInfo('Verifying locations')
        blue.pyos.synchro.SleepWallclock(2000)
        for location in locationList:
            inPark = sm.GetService('michelle').GetBall(location)
            if not inPark:
                self.LogError('Location ', location, ' not in ballPark')
                raise RuntimeError('location not found in ballpark')

        self.totalProfiler.Start()
        self.running = 1
        self.LoopThrough(locationList)
        self.WarpTo(start)
        self.channel.receive()
        self.totalProfiler.Finish()
        self.LogInfo('Finished profiling')
        self.running = 0

    def LoopThrough(self, locationList):
        for location in locationList:
            self.dispatchProfiler.Prime()
            self.LogInfo('Trying to warp to ', location)
            self.WarpTo(location)
            self.LogInfo('Waiting for warp to finish')
            self.channel.receive()
            self.LogInfo('Warping finished')
            self.LogInfo('Wait while we gather information, and allow for interupts')
            start = blue.os.GetWallclockTimeNow()
            blue.pyos.synchro.SleepWallclock(1000)
            timer = timerstuff.AutoTimer(60000, self.ShuntEvents)
            self.keepAlive.Wait()
            timer = None
            end = blue.os.GetWallclockTimeNow()
            self.LogInfo('We waited for ', blue.os.TimeDiffInMs(start, end), ' ms')
            self.totalProfiler.ProcessSnapshots()
            self.dispatchProfiler.Flush(self.totalProfiler.file)
            self.LogInfo('Sleeping for good measure')
            blue.pyos.synchro.SleepWallclock(2000)
            FPStime = 10000
            self.LogInfo('FPS profiling for ', FPStime, ' ms')
            self.FPSProfiler.Start(self.totalProfiler.file, FPStime)
            blue.pyos.synchro.SleepWallclock(FPStime + 500)
            self.LogInfo(location, ' done.')

    def WarpTo(self, location):
        uthread.new(self.WarpTo_thread, location).context = 'svc.profiling.WarpTo'

    def WarpTo_thread(self, location):
        bp = sm.GetService('michelle').GetRemotePark()
        if bp is None:
            raise RuntimeError('No park found')
        self.LogInfo('Warping to ', location)
        bp.CmdWarpToStuff('item', location)

    def BeginSnapshot(self, name):
        if not self.dispatchProfiler.primed:
            return
        self.keepAlive.Set()
        return self.totalProfiler.BeginSnapshot(name)

    def EndSnapshot(self, key):
        self.totalProfiler.BeginSnapshot(key)
        self.keepAlive.Release()

    def OnClientEvent_WarpFinished(self, *args):
        self.channel.send(None)

    def OnSessionChanged(self, *args):
        self.channel.send(None)

    def ShuntEvents(self):
        self.LogWarn('We had to kill some events')
        ret = self.keepAlive.ReleaseAll()
        if ret > 0:
            self.LogWarn(ret, ' sends without releases')
        if ret < 0:
            self.LogError(-ret, ' receives without sends?!?')


def Get():
    return ProfilingScheduler.running


def Start():
    if ProfilingScheduler.running:
        sm.GetService('profiling').StartDispatching()


class NonniEvent:

    def __init__(self, sleepingTime = 0):
        self.channel = stackless.channel()
        self.primed = 0
        self.receiving = 0
        self.sleepingTime = sleepingTime

    def Set(self):
        self.primed += 1
        return 1

    def Release(self):
        self.channel.send(None)

    def Wait(self):
        if not self.primed:
            return
        while self.primed:
            self.primed -= 1
            self.channel.receive()

        blue.pyos.synchro.SleepWallclock(self.sleepingTime)
        self.Wait()

    def ReleaseAll(self):
        ret = self.channel.balance
        for i in range(self.channel.balance):
            self.channel.receive()

        for i in range(-self.channel.balance):
            self.channel.send(None)

        self.primed = 0
        return ret
