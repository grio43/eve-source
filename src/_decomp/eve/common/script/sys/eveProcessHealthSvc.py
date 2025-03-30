#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\common\script\sys\eveProcessHealthSvc.py
import blue
from eveprefs import boot
from eveservices.dogmaim import GetDogmaIMService
from carbon.common.script.sys.processHealthSvc import ProcessHealthSvc

class EveProcessHealthSvc(ProcessHealthSvc):
    __guid__ = 'svc.eveProcessHealth'
    __replaceservice__ = 'processHealth'
    __servicename__ = 'eveProcessHealth'
    __displayname__ = 'Eve Process Health Service'

    def __init__(self, *args):
        ProcessHealthSvc.__init__(self)
        self.columnNames += ('bytesReceived', 'bytesSent', 'packetsReceived', 'packetsSent')
        if boot.role == 'server':
            self.columnNames += ('dogmaLateness', 'maxModules', 'totalModules', 'sessionCount', 'solCount')
        if boot.role != 'client':
            self.columnNames += ('numEvents',)

    def LogDogma(self):
        if boot.role == 'server':
            maxModules = 0
            totalModules = 0
            count = 0
            totalStopEffects = 0
            dogmaLag = [0]
            for bindparam, dogmaLocation in GetDogmaIMService().boundObjects.items():
                try:
                    nextStopTime = dogmaLocation.GetNextStopEffectTime()
                except AttributeError:
                    continue

                count += 1
                dogmaLag.append(float(nextStopTime - blue.os.GetSimTime()) / const.SEC)
                numModules = dogmaLocation.GetEffectTimerListLength()
                maxModules = max(maxModules, numModules)
                totalModules += numModules
                totalStopEffects += dogmaLocation._stopEffectsRunning

            mostLag = min(dogmaLag)
            self.logLines[-1].update({'solCount': count,
             'maxModules': maxModules,
             'totalModules': totalModules,
             'dogmaLateness': -1 * mostLag,
             'totalStopEffectsThread': totalStopEffects})

    def LogEventCount(self):
        if boot.role != 'client':
            counters = sm.GetService('eventLog').logEventCounter
            num = 0
            for k, v in counters.iteritems():
                num += v[1]

            self.logLines[-1].update({'numEvents': num})

    def DoOnceEvery10Secs(self):
        self.LogCpuMemNet()
        self.LogDogma()
        self.LogEventCount()
