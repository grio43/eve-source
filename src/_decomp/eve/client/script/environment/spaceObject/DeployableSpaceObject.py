#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\environment\spaceObject\DeployableSpaceObject.py
import blue
from eve.client.script.environment.spaceObject.spaceObject import SpaceObject
from eve.client.script.environment.model.turretSet import TurretSet
import evegraphics.settings as gfxsettings
import eve.common.lib.appConst as const
from spacecomponents.client.messages import MSG_ON_ACTIVATE_TIMER_UPDATED
from spacecomponents.common.helper import IsActiveComponent
TURRET_TYPE_ID = {const.groupAutoLooter: 24348}

class DeployableSpaceObject(SpaceObject):

    def __init__(self):
        SpaceObject.__init__(self)
        self.modules = {}
        self.fitted = False

    def Assemble(self):
        if self.ballpark is None:
            return
        registry = self._GetComponentRegistry()
        if not IsActiveComponent(registry, self.typeID, self.id):
            self.SetControllerVariable('IsDeployableActive', False)
            registry.SubscribeToItemMessage(self.id, MSG_ON_ACTIVATE_TIMER_UPDATED, self.ActivateTimerUpdate)
        else:
            self.SetControllerVariable('IsDeployableActive', True)
        if gfxsettings.Get(gfxsettings.UI_TURRETS_ENABLED):
            self.FitHardpoints()
        self.SetupSharedAmbientAudio()

    def ActivateTimerUpdate(self, component, slimItem):
        if component.isActive:
            self.SetControllerVariable('IsDeployableActive', True)

    def FitHardpoints(self, blocking = False):
        if self.fitted:
            return
        if self.model is None:
            self.logger.warning('FitHardpoints - No model')
            return
        if self.typeID is None:
            self.logger.warning('FitHardpoints - No typeID')
            return
        self.fitted = True
        self.modules = {}
        groupID = self.typeData.get('groupID', None)
        if groupID is not None:
            turretTypeID = TURRET_TYPE_ID.get(groupID, None)
            if turretTypeID is not None:
                ts = TurretSet.FitTurret(self.model, turretTypeID, 1, self.typeData.get('sofFactionName', None))
                if ts is not None:
                    self.modules[self.id] = ts

    def LookAtMe(self):
        if not self.model:
            return
        if not self.fitted:
            self.FitHardpoints()

    def Release(self):
        if self.released:
            return
        self.modules = None
        SpaceObject.Release(self)
