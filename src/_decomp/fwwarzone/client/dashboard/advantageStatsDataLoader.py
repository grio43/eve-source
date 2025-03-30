#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\fwwarzone\client\dashboard\advantageStatsDataLoader.py
import signals
import uthread
import uthread2

class AdvantageStatsDataLoader(object):

    def __init__(self, systemIds):
        self.systemIds = systemIds
        self.onErrorSignal = signals.Signal()
        self.onSuccessSignal = signals.Signal()
        self.fwAdvantageSvc = sm.GetService('fwAdvantageSvc')

    def AsyncLoadAdvantage(self):
        uthread2.StartTasklet(self._LoadAdvantage)

    def _LoadAdvantage(self):
        funcs = []
        for systemId in self.systemIds:
            fun = [self.fwAdvantageSvc.GetAdvantageState, (systemId,)]
            funcs.append(fun)

        try:
            systemIdToAdvantageState = {}
            results = uthread.Parallel(funcs)
            for i, result in enumerate(results):
                systemIdToAdvantageState[self.systemIds[i]] = result

            self.onSuccessSignal(systemIdToAdvantageState)
        except Exception:
            self.onErrorSignal()
