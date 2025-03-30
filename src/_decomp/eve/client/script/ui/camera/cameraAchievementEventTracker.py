#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\camera\cameraAchievementEventTracker.py
import math
import blue
import geo2
from achievements.common.achievementConst import AchievementConsts, AchievementEventConst
from achievements.common.eventExceptionEater import AchievementEventExceptionEater
from carbon.common.script.util import mathCommon
from logmodule import LogException
from operations.client.operationscontroller import operationsController, GetOperationsController
from operations.client.util import are_operations_active
import uthread

class CameraAchievementEventTracker(object):
    cameraStillSpinning = False

    def CameraMove_thread(self, camera_controller, camera):
        try:
            lastYawRad, _, _ = geo2.QuaternionRotationGetYawPitchRoll(camera.GetRotationQuat())
            radDelta = 0
            while self.cameraStillSpinning:
                blue.pyos.synchro.Yield()
                if camera_controller.mouseDownPos is None or camera is None:
                    self.cameraStillSpinning = False
                    return
                curYaw, pitch, roll = geo2.QuaternionRotationGetYawPitchRoll(camera.GetRotationQuat())
                angleBtwYaws = mathCommon.GetLesserAngleBetweenYaws(lastYawRad, curYaw)
                radDelta += math.fabs(angleBtwYaws)
                lastYawRad = curYaw
                if abs(radDelta) > math.pi / 4:
                    sm.ScatterEvent('OnClientMouseSpinInSpace')
                    self.cameraStillSpinning = False

        except Exception as e:
            LogException(e)

    def RecordOrbitForAchievements(self, camera_controller, camera):
        with AchievementEventExceptionEater():
            if self.cameraStillSpinning:
                return
            if self.IsAchievementEventInteresting(AchievementConsts.UI_ROTATE_IN_SPACE, AchievementEventConst.UI_MOUSE_ROTATE_CLIENT):
                self.cameraStillSpinning = True
                uthread.new(self.CameraMove_thread, camera_controller, camera)

    def IsAchievementEventInteresting(self, achievement_const, achievement_event_const):
        return not sm.GetService('achievementSvc').IsAchievementCompleted(achievement_const) or are_operations_active()

    def RecordZoomForAchievements(self, amount):
        with AchievementEventExceptionEater():
            if amount < 0:
                if self.IsAchievementEventInteresting(AchievementConsts.UI_ZOOM_IN_SPACE, AchievementEventConst.UI_MOUSEZOOM_IN_CLIENT):
                    sm.ScatterEvent('OnClientMouseZoomInSpace', amount)
            elif self.IsAchievementEventInteresting(AchievementConsts.UI_ZOOM_IN_SPACE, AchievementEventConst.UI_MOUSEZOOM_OUT_CLIENT):
                sm.ScatterEvent('OnClientMouseZoomOutSpace', amount)

    def StopRecordingOrbitForAchievements(self):
        self.cameraStillSpinning = False
