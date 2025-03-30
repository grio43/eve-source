#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evegraphics\environments\nebulaOverrides.py
from evegraphics import effects
from evegraphics.environments import BaseEnvironmentObject

class NebulaOverrides(BaseEnvironmentObject):

    def __init__(self, nebulaOverrideInfo, *args):
        super(NebulaOverrides, self).__init__(*args)
        self.tintColor = tuple(nebulaOverrideInfo.tint or (1, 1, 1, 1))
        self._defaultTintColor = None

    def Setup(self):
        pass

    def ApplyToScene(self):
        if getattr(self.scene, 'backgroundEffect', None):
            self._defaultTintColor = effects.GetParameterValue(self.scene.backgroundEffect, effects.BACKGROUND_TINT)
            effects.SetParameterValue(self.scene.backgroundEffect, effects.BACKGROUND_TINT, self.tintColor)

    def TearDown(self):
        if getattr(self.scene, 'backgroundEffect', None):
            effects.SetParameterValue(self.scene.backgroundEffect, effects.BACKGROUND_TINT, self._defaultTintColor)
        self.scene = None
