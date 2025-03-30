#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\util\spacescene.py
import carbonui.const as uiconst
from carbonui.util.color import Color
from eve.client.script.ui.control.scenecontainer import SceneContainer
from evegraphics import effects
import trinity

class SpaceScene(SceneContainer):
    __notifyevents__ = SceneContainer.__notifyevents__ + ['OnUIColorsChanged']

    def ApplyAttributes(self, attributes):
        super(SpaceScene, self).ApplyAttributes(attributes)
        self.scene = trinity.EveSpaceScene()
        self.scene.starfield = trinity.Load('res:/dx9/scene/starfield/spritestars.red')
        self.scene.backgroundRenderingEnabled = True
        path = cfg.GetNebula(30005305, 20000776, 10000068)
        scene = trinity.Load(path)
        self.scene.backgroundEffect = scene.backgroundEffect
        effects.SetEffectOption(scene.backgroundEffect, effects.BACKGROUND_VARIATION, effects.BACKGROUND_VARIATION_SCANNING)
        self.OnUIColorsChanged()
        self.DisplaySpaceScene(blendMode=None)

    def OnUIColorsChanged(self):
        if self.scene is None:
            return
        color = sm.GetService('uiColor').GetUIColor(uiconst.COLORTYPE_UIBASE)
        color = Color(*color).SetBrightness(0.015).GetRGBA()
        if self.scene.backgroundEffect:
            effects.SetParameterValue(self.scene.backgroundEffect, effects.BACKGROUND_TINT, color)
