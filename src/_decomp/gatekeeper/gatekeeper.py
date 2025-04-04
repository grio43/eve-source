#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\gatekeeper\gatekeeper.py
import logging
from eveexceptions.exceptionEater import ExceptionEater
import functoolsext
CACHE_SIZE = 4096
logger = logging.getLogger(__name__)

class Gatekeeper:

    def __init__(self, ignoreMultipleTeardowns = False, allowMultipleInits = False):
        self.GetCohortFunction = None
        self.tolerantTearDown = ignoreMultipleTeardowns
        self.allowMultipleInits = allowMultipleInits

    def IsInitialized(self):
        return self.GetCohortFunction is not None

    def Initialize(self, getCohortFunction):
        self.__raiseRuntimeErrorIfNone(getCohortFunction)
        if not self.IsInitialized() or self.allowMultipleInits:
            self.GetCohortFunction = getCohortFunction
        else:
            raise RuntimeError('Gatekeeper has already been initialized!')

    def __raiseRuntimeErrorIfNone(self, function):
        if function is None:
            raise RuntimeError('Gatekeeper cohort Function cannot be None')

    def Teardown(self):
        if self.IsInitialized():
            self.GetCohortFunction = None
        elif not self.tolerantTearDown:
            raise RuntimeError('Gatekeeper has not been initialized!')
        self.IsInCohort.cache_clear()
        self.GetCohorts.cache_clear()

    @functoolsext.lru_cache(CACHE_SIZE)
    def IsInCohort(self, cohortID, *args):
        if self.IsInitialized():
            isInCohort = False
            with ExceptionEater('Failed to query the gatekeeper. Returning False for querying entity.'):
                CohortFunction = self.GetCohortFunction(args)
                isInCohort = cohortID in self._GetCohortsForEntityFromService(CohortFunction)
            return isInCohort
        else:
            logger.error('Gatekeeper not initialized')
            return False

    def _GetCohortsForEntityFromService(self, CohortFunction):
        return CohortFunction()

    @functoolsext.lru_cache(CACHE_SIZE)
    def GetCohorts(self, *args):
        self._RaiseErrorIfNotInitialized()
        CohortFunction = self.GetCohortFunction(args)
        return self._GetCohortsForEntityFromService(CohortFunction)

    def _RaiseErrorIfNotInitialized(self):
        if not self.IsInitialized():
            raise RuntimeError('Gatekeeper has not been initialized')
