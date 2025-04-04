#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\svc_gridload.py
import blue
import uthread
import log
from carbon.common.script.sys.service import Service
from carbon.common.script.sys.serviceConst import SERVICE_RUNNING, SERVICE_START_PENDING, SERVICE_STOP_PENDING, SERVICE_STOPPED

class GridLoadSimulationTool(Service):
    __guid__ = 'svc.GridLoadSimulationTool'
    __servicename__ = 'GridLoadSimulationTool'
    __displayname__ = 'Grid Load Simulation Tool'
    __exportedcalls__ = {}

    def Run(self, memStream = None):
        self.state = SERVICE_START_PENDING
        super(GridLoadSimulationTool, self).Run(memStream)
        self.numInQueue = 0
        self.pcQueue = uthread.Queue(0)
        self.semaphore = uthread.Semaphore('spawnTestSema', 1, True)
        self.go = False
        self.hasStarted = False
        self.state = SERVICE_RUNNING

    def Stop(self, memStream = None):
        self.state = SERVICE_STOP_PENDING
        Service.Stop(self, memStream)
        self.state = SERVICE_STOPPED

    def StartTest(self, initNumObjsToSpawn, spawnCountPerTick, unspawnCountPerTick, spawnTickIntervalInMS, unspawnTickIntervalInMS, spawningCharID = 0):
        self.numInQueue = 0
        self.go = True
        self.hasStarted = False
        self.prodThread = uthread.new(self.spawnRunner, spawningCharID, initNumObjsToSpawn, spawnCountPerTick, unspawnCountPerTick, spawnTickIntervalInMS)
        self.consumeThread = uthread.new(self.unspawnRunner, unspawnCountPerTick, unspawnTickIntervalInMS)

    def StopTest(self):
        uthread.new(self.StopRunner)

    def spawnRunner(self, spawningCharID, initNumObjs, spawnCountPerTick, unspawnCountPerTick, tickIntervalInMS):
        typeIDtoSpawn = 638
        baseName = 'spawnLoadTestObj_'
        itemIDList = []
        stdDev = 0.0
        self.semaphore.acquire()
        for i in xrange(initNumObjs):
            cmdStr = '/spawn %s stddev=%s name="%s%s" ' % (typeIDtoSpawn,
             stdDev,
             baseName,
             i)
            id = sm.GetService('slash').SlashCmd(cmdStr)
            itemIDList.append(id)
            if len(itemIDList) == unspawnCountPerTick:
                self.pcQueue.non_blocking_put(itemIDList)
                self.numInQueue = self.numInQueue + unspawnCountPerTick
                itemIDList = []

        self.hasStarted = True
        self.semaphore.release()
        log.LogInfo('Finished setting up the, feel free to call StopTest().')
        while True:
            blue.pyos.synchro.SleepWallclock(tickIntervalInMS)
            if not self.go:
                for id in itemIDList:
                    cmdStr = '/unspawn %s' % id
                    sm.GetService('slash').SlashCmd(cmdStr)

                return
            self.semaphore.acquire()
            for i in xrange(spawnCountPerTick):
                cmdStr = '/spawn %s stddev=%s name="%s%s" ' % (typeIDtoSpawn,
                 stdDev,
                 baseName,
                 i)
                id = sm.GetService('slash').SlashCmd(cmdStr)
                itemIDList.append(id)
                if len(itemIDList) == unspawnCountPerTick:
                    self.pcQueue.non_blocking_put(itemIDList)
                    self.numInQueue = self.numInQueue + unspawnCountPerTick
                    itemIDList = []

            self.semaphore.release()

    def unspawnRunner(self, unspawnCountPerTick, tickIntervalInMS):
        while True:
            blue.pyos.synchro.SleepWallclock(tickIntervalInMS)
            if not self.hasStarted:
                continue
            if not self.go:
                while True:
                    cleanUpList = self.pcQueue.get()
                    self.semaphore.acquire()
                    for id in cleanUpList:
                        cmdStr = '/unspawn %s' % id
                        sm.GetService('slash').SlashCmd(cmdStr)

                    self.numInQueue = self.numInQueue - len(cleanUpList)
                    self.semaphore.release()

            else:
                listToDespawn = self.pcQueue.get()
                self.semaphore.acquire()
                for id in listToDespawn:
                    cmdStr = '/unspawn %s' % id
                    sm.GetService('slash').SlashCmd(cmdStr)

                self.numInQueue = self.numInQueue - len(listToDespawn)
                self.semaphore.release()

    def StopRunner(self):
        while True:
            self.semaphore.acquire()
            if not self.hasStarted:
                self.semaphore.release()
                blue.pyos.synchro.SleepWallclock(1000)
                continue
            self.go = False
            self.semaphore.release()
            blue.pyos.synchro.SleepWallclock(1000)
            if self.consumeThread.alive:
                if self.consumeThread.blocked:
                    self.semaphore.acquire()
                    if self.numInQueue == 0:
                        self.semaphore.release()
                        self.consumeThread.kill()
                        return
                    self.semaphore.release()
                    blue.pyos.synchro.SleepWallclock(1000)
            else:
                return
