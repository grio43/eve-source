#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dbuff\common\aggregators.py
import dbuff.storage

class Aggregator(object):
    __slots__ = ['_sortedInputs', '_continuousInput']

    def __init__(self, expiryTime, outputValue):
        if expiryTime is None:
            self._continuousInput = outputValue
            self._sortedInputs = []
        else:
            self._continuousInput = None
            self._sortedInputs = [(expiryTime, outputValue)]

    def HasInputs(self):
        return len(self._sortedInputs) > 0 or self._continuousInput is not None

    def GetNextExpiryTime(self):
        if self._sortedInputs:
            return self._sortedInputs[0][0]
        if self._continuousInput is None:
            return 0

    def GetFinalExpiryTime(self):
        if self._continuousInput is not None:
            return
        if self._sortedInputs:
            return self._sortedInputs[-1][0]

    def GetCurrentOutputValue(self):
        if self._sortedInputs and self._continuousInput is not None:
            return self._PickValue(self._continuousInput, self._sortedInputs[0][1])
        if self._continuousInput is not None:
            return self._continuousInput
        if self._sortedInputs:
            return self._sortedInputs[0][1]

    def _PickValue(self, *values):
        raise NotImplementedError()

    def MergeNewTimedInput(self, newExpiryTime, newValue):
        raise NotImplementedError()

    def SetContinuousInput(self, newValue):
        if self._continuousInput is None:
            self._continuousInput = newValue
        else:
            self._continuousInput = self._PickValue(self._continuousInput, newValue)

    def ClearContinuousInput(self):
        self._continuousInput = None

    def DiscardExpiredTimedInputs(self, now):
        while self._sortedInputs and self._sortedInputs[0][0] < now:
            self._sortedInputs.pop(0)

    def GetStateForClient(self):
        return (self.GetCurrentOutputValue(), self.GetFinalExpiryTime())


class AggregatorMinimum(Aggregator):
    __slots__ = []

    def MergeNewTimedInput(self, newExpiryTime, newValue):
        for expiryTime, value in self._sortedInputs:
            if expiryTime >= newExpiryTime and value <= newValue:
                return

        result = [ (expiryTime, value) for expiryTime, value in self._sortedInputs if expiryTime < newExpiryTime and value < newValue ]
        result.append((newExpiryTime, newValue))
        result.extend([ (expiryTime, value) for expiryTime, value in self._sortedInputs if expiryTime > newExpiryTime and value > newValue ])
        self._sortedInputs = result

    def _PickValue(self, *values):
        return min(values)


class AggregatorMaximum(Aggregator):
    __slots__ = []

    def MergeNewTimedInput(self, newExpiryTime, newValue):
        for expiryTime, value in self._sortedInputs:
            if expiryTime >= newExpiryTime and value >= newValue:
                return

        result = [ (expiryTime, value) for expiryTime, value in self._sortedInputs if expiryTime < newExpiryTime and value > newValue ]
        result.append((newExpiryTime, newValue))
        result.extend([ (expiryTime, value) for expiryTime, value in self._sortedInputs if expiryTime > newExpiryTime and value < newValue ])
        self._sortedInputs = result

    def _PickValue(self, *values):
        return max(values)


AGGREGATOR_CLASS_BY_MODE = {'Maximum': AggregatorMaximum,
 'Minimum': AggregatorMinimum}

def CreateAggregator(dbuffCollectionID, expiryTime, outputValue):
    dbuffCollection = dbuff.storage.GetDbuffCollection(dbuffCollectionID)
    aggregateMode = dbuffCollection.aggregateMode
    aggregatorClass = AGGREGATOR_CLASS_BY_MODE[aggregateMode]
    return aggregatorClass(expiryTime, outputValue)


if __name__ == '__main__':
    import random
    import timeit

    class AggregatorNull(Aggregator):

        def _PickValue(self, *values):
            pass

        def MergeNewTimedInput(self, newExpiryTime, newValue):
            pass


    for aggregator in [AggregatorNull(555, 1.0), AggregatorMaximum(555, 1.0), AggregatorMinimum(555, 1.0)]:
        rnd = random.Random('aggregators random seed')
        timing = timeit.repeat('\nfor expiryTime, value in samples:\n    aggregator.MergeNewTimedInput(expiryTime, value)\n            ', setup='\nimport random\nfrom __main__ import aggregator, rnd\nnumSamples = 50\nsamples = [(rnd.randint(100, 999), rnd.uniform(0.0, 10.0)) for x in xrange(numSamples)]\n            ', number=10000, repeat=5)
        print '%.3fs [%s]' % (min(timing), aggregator)
