#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evegraphics\environments\environmentManager.py
import logging
import uthread2
from carbon.common.lib import telemetry
from eveexceptions.exceptionEater import ExceptionEater
from evegraphics.environments.cameraWrapper import CreateCameraWrapper
from evegraphics.environments.environment import Environment
from fsdBuiltData.client.environmentTemplates import GetEnvironmentTemplates, EnvironmentTemplates
from tacticalNavigation.ballparkFunctions import ConvertPositionToGlobalSpace, GetBallpark
log = logging.getLogger(__name__)
from carbon.common.script.util.timerstuff import AutoTimer

class EnvironmentObjectAlreadyEnabled(Exception):

    def __init__(self, environmentType):
        super(EnvironmentObjectAlreadyEnabled).__init__()
        self.environmentType = environmentType

    def __str__(self):
        return "Environment manager already has '%s' set up" % self.environmentType


class EnvironmentManager(object):
    ENABLED = True
    BALLPARK_MODE = True
    __instance__ = None

    @staticmethod
    def GetInstance():
        if EnvironmentManager.__instance__ is None:
            EnvironmentManager.__instance__ = EnvironmentManager()
        return EnvironmentManager.__instance__

    @staticmethod
    def Toggle():
        EnvironmentManager.ENABLED = not EnvironmentManager.ENABLED
        if EnvironmentManager.ENABLED:
            EnvironmentManager.GetInstance()
        else:
            EnvironmentManager.GetInstance().StopUpdates()
            EnvironmentManager.__instance__ = None

    def __init__(self):
        self.environments = []
        self._externalGetCameraFunc = None
        self._externalGetRenderJobFunc = None
        self.updateThread = None
        self.pendingEnvironmentObjects = []
        self.frozen = False
        self.environmentCache = {}
        if self.BALLPARK_MODE:
            EnvironmentTemplates.ConnectToOnReload(self.CreateCache)
            uthread2.start_tasklet(self.CreateCache)
        self.StartUpdates()

    def __del__(self):
        self.StopUpdates()

    def CreateCache(self):
        EnvironmentTemplates.CacheTemplates()
        self.environmentCache.clear()
        for templateID in GetEnvironmentTemplates().keys():
            e = Environment('cache for %s template' % templateID, -1, (0, 0, 0), 0)
            e.CreateFromTemplate(templateID)
            self.environmentCache[templateID] = e

    def StopUpdates(self):
        if self.updateThread:
            self.updateThread.KillTimer()

    def StartUpdates(self):
        self.updateThread = AutoTimer(500, self._UpdateEnvironment)

    def _GetCamera(self):
        camera = CreateCameraWrapper(self._externalGetCameraFunc())
        if camera.viewMatrix is None:
            return
        return camera

    @staticmethod
    def _ExtractCameraPos(camera):
        cameraPos = camera.viewMatrix.transform[3][:3]
        if cameraPos is None:
            return
        if EnvironmentManager.BALLPARK_MODE:
            cameraPos = ConvertPositionToGlobalSpace(cameraPos)
        return cameraPos

    def _UpdateEnvironment(self):
        if self.frozen:
            return
        if self._externalGetRenderJobFunc is None or self._externalGetRenderJobFunc() is None or self._externalGetRenderJobFunc().scene is None:
            return
        if EnvironmentManager.BALLPARK_MODE and (GetBallpark() is None or GetBallpark().ego not in (session.shipid, session.structureid)):
            return
        if self._externalGetCameraFunc is None or self._externalGetCameraFunc() is None:
            return
        with ExceptionEater('Got exception while updating environments'):
            camera = self._GetCamera()
            if camera is None:
                return
            cameraPos = self._ExtractCameraPos(camera)
            if cameraPos is None:
                return
            renderJob = self._externalGetRenderJobFunc()
            refreshSystemWideEnvironment = False
            hasSystemWideEnvironment = False
            environmentsToRemove = []
            environmentsToAdd = []
            for environment in self.environments:
                hasSystemWideEnvironment |= environment.systemWide
                oldIsActive = environment.isActive
                environment.Update(cameraPos)
                newIsActive = environment.isActive
                if oldIsActive != newIsActive:
                    if newIsActive:
                        environmentsToAdd.append(environment)
                    else:
                        environmentsToRemove.append(environment)
                        refreshSystemWideEnvironment = True

            if len(environmentsToAdd) + len(environmentsToRemove) > 0:
                self.MergeEnvironments()
            for environment in environmentsToRemove:
                environment.TearDown()

            for environment in environmentsToAdd:
                environment.Setup(camera, renderJob)

            if refreshSystemWideEnvironment and hasSystemWideEnvironment:
                for systemWideEnvironment in [ e for e in self.environments if e.systemWide ]:
                    systemWideEnvironment.TearDown()
                    systemWideEnvironment.Setup(camera, renderJob)

            if len(self.pendingEnvironmentObjects) > 0:
                environmentObjects = self.pendingEnvironmentObjects[:]
                environmentObjectsAdded = []
                for environment in self.environments:
                    environmentObjectsAdded.extend(environment.AddEnvironmentObjects(environmentObjects))

                for eo in environmentObjectsAdded:
                    if eo in self.pendingEnvironmentObjects:
                        self.pendingEnvironmentObjects.remove(eo)

    def MergeEnvironments(self):
        activeEnvironments = self.GetActiveEnvironments()
        if len(activeEnvironments) > 1:
            activeEnvironments.sort(key=lambda x: x.radius, reverse=True)
            activeEnvironments.sort(key=lambda x: x.systemWide, reverse=True)
            lockedAttributes = {}
            for environment in activeEnvironments:
                environment.SetIgnoredAttributes(lockedAttributes)
                for environmentType, lockedEnvironmentAttributes in environment.GetLockedAttributes():
                    if lockedEnvironmentAttributes:
                        if environmentType not in lockedAttributes:
                            lockedAttributes[environmentType] = []
                        if isinstance(lockedAttributes, dict):
                            lockedAttributes[environmentType] = lockedEnvironmentAttributes
                        else:
                            lockedAttributes[environmentType].extend(lockedEnvironmentAttributes)

    def GetActiveEnvironments(self):
        return [ environment for environment in self.environments if environment.isActive ]

    def GetEnvironmentsForPosition(self, position):
        if position is None:
            return []
        distanceAndEnvironments = [ (env.DistanceSqFrom(position), env) for env in self.environments if env.InRange(position) ]
        distanceAndEnvironments.sort(key=lambda x: x[0])
        return [ env for d, env in distanceAndEnvironments ]

    def GetEnvironmentTemplateInVicinity(self, templateId, position):
        if templateId is None:
            return
        environmentsInPosition = self.GetEnvironmentsForPosition(position)
        if templateId is not None:
            for environment in environmentsInPosition:
                if environment.templateID == templateId:
                    return environment

    @telemetry.ZONE_METHOD
    def AddEnvironment(self, name, position, templateId = None, solarSystemId = None, anchorRadius = 0, anchorTranslationCurve = None, anchorID = None):
        existingEnvironment = self.GetEnvironmentTemplateInVicinity(templateId, position)
        if existingEnvironment is not None:
            existingEnvironment.AddEnvironmentAnchorID(anchorID, anchorTranslationCurve)
            return existingEnvironment
        e = Environment(name, solarSystemId, position, anchorRadius, anchorTranslationCurve)
        if templateId is not None:
            if self.BALLPARK_MODE:
                cacheItem = self.environmentCache.get(templateId, None)
                if cacheItem is not None:
                    e.CreateFromExisting(cacheItem)
                else:
                    log.error('Failed to find environment %s in cache, creating from scratch' % templateId, extra={'template_name': name,
                     'solarSystemId': solarSystemId,
                     'position': position,
                     'anchorRadius': anchorRadius,
                     'anchorTranslationCurve': anchorTranslationCurve,
                     'templateId': templateId})
                    e.CreateFromTemplate(templateId)
            else:
                e.CreateFromTemplate(templateId)
        e.AddEnvironmentAnchorID(anchorID, anchorTranslationCurve)
        self.environments.append(e)
        return e

    def UpdateEnvironment(self, name, templateId, postProcessInstance = None):
        e = next((x for x in self.environments if x.name == name), None)
        if e is None:
            return
        e.TearDown()
        e.CreateFromTemplate(templateId)
        if postProcessInstance and e.postProcess:
            e.postProcess.postProcess = postProcessInstance
        camera = self._GetCamera()
        if camera is None:
            return e
        e.TearDown()
        e.Setup(camera, self._externalGetRenderJobFunc())
        return e

    def IsSubEnvironmentObject(self, position, typeId):
        environments = self.GetEnvironmentsForPosition(position)
        for environment in environments:
            if typeId in environment.subEnvironmentTypeIDs:
                return True

        return False

    def AddObjectsInEnvironment(self, environmentObjects):
        self.pendingEnvironmentObjects.extend(environmentObjects)

    def SetGetCameraFunction(self, func):
        self._externalGetCameraFunc = func

    def SetGetRenderJobFunction(self, func):
        self._externalGetRenderJobFunc = func

    def RefreshEnvironments(self):
        camera = CreateCameraWrapper(self._externalGetCameraFunc())
        renderJob = self._externalGetRenderJobFunc()
        for environment in self.environments:
            if environment.isActive:
                environment.TearDown()
                environment.Setup(camera, renderJob)

    def RefreshEnvironment(self, templateID):
        camera = CreateCameraWrapper(self._externalGetCameraFunc())
        renderJob = self._externalGetRenderJobFunc()
        for environment in self.environments:
            if environment.templateID == templateID:
                environment.TearDown()
                environment.Setup(camera, renderJob)
                return

    def RemoveEnvironment(self, name):
        for environment in self.environments[:]:
            if str(environment.name) != str(name):
                continue
            if environment.isActive:
                environment.TearDown()
            self.environments.remove(environment)

    def RemoveEnvironmentAnchor(self, anchorID):
        for environment in self.environments[:]:
            if anchorID in environment.anchorIDs:
                environment.RemoveEnvironmentAnchorID(anchorID)
                if len(environment.anchorIDs) == 0:
                    self.RemoveEnvironment(environment.name)

    def GetAllAnchorIDs(self):
        anchors = {}
        for environment in self.environments[:]:
            for anchorID in environment.anchorIDs:
                anchors[anchorID] = anchorID

        return anchors

    def ClearAllEnvironments(self):
        for environment in self.environments:
            environment.TearDown()

        del self.environments[:]

    def RemoveEnvironmentForSolarSystem(self, solarSystemID):
        for environment in self.environments[:]:
            if environment.solarsystemId == solarSystemID:
                if environment.isActive:
                    environment.TearDown()
                try:
                    self.environments.remove(environment)
                except ValueError:
                    pass
