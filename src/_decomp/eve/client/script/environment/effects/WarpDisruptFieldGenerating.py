#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\environment\effects\WarpDisruptFieldGenerating.py
from eve.client.script.environment.effects.GenericEffect import ShipEffect

class WarpDisruptFieldGenerating(ShipEffect):
    __guid__ = 'effects.WarpDisruptFieldGenerating'

    def __init__(self, trigger, *args):
        ShipEffect.__init__(self, trigger, *args)
        self.moduleTypeID = trigger.moduleTypeID
        self.radius = 20000.0
        if trigger.graphicInfo is not None:
            self.realRadius = trigger.graphicInfo.range
        else:
            godmaStateManager = sm.GetService('godma').GetStateManager()
            self.realRadius = godmaStateManager.GetType(self.moduleTypeID).warpScrambleRange

    def Prepare(self):
        ShipEffect.Prepare(self)
        radius = self.realRadius
        scale = radius / self.radius
        self.gfxModel.scaling = (scale, scale, scale)

    def Repeat(self, duration):
        pass
