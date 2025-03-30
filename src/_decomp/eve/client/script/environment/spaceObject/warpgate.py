#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\environment\spaceObject\warpgate.py
from eve.client.script.environment.spaceObject.spaceObject import SpaceObject

class WarpGate(SpaceObject):

    def Assemble(self):
        self.SetStaticDirection()
        self.SetupAmbientAudio()

    def Prepare(self):
        super(WarpGate, self).Prepare()
        self.RestoreAnimationState()

    def RestoreAnimationState(self):
        slimItem = sm.GetService('michelle').GetItem(self.id)
        self.SetControllerVariablesFromSlimItem(slimItem)
