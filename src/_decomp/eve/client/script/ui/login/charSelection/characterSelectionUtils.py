#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\login\charSelection\characterSelectionUtils.py
import localization
import trinity
import eve.client.script.ui.login.charSelection.characterSelectionColors as csColors
from carbonui.primitives.fill import Fill
from carbonui.primitives.frame import Frame
from carbonui.uicore import uicore
from carbonui.util.color import Color
from caching.memoize import Memoize
from eve.common.lib import appConst as const
WARNING_TIME = 5 * const.DAY
COLLAPSE_TIME = 0.3
FADE_ANIMATION_TIME = 0.3

def AddFrameWithFillAndGlow(parent, showFill = True, fillColor = None, frameColor = None, glowColor = csColors.FRAME_GLOW_ACTIVE):
    if showFill:
        fillColor = fillColor if fillColor else (0.5, 0.5, 0.5, 0.5)
        fill = Fill(bgParent=parent, color=fillColor)
    else:
        fill = None
    frameColor = frameColor if frameColor else (0.5, 0.5, 0.5, 0.5)
    normalFrame = Frame(parent=parent, color=frameColor)
    glowFrameTexturePath = 'res:/UI/Texture/classes/CharacterSelection/glowDotFrame.png'
    glowFrame = Frame(parent=parent, name='glowFrame', color=glowColor, frameConst=(glowFrameTexturePath,
     5,
     -2,
     0), padding=0)
    return (glowFrame, normalFrame, fill)


def SetColor(uiComponent, newColor, animate = False):
    if animate:
        uicore.animations.SpColorMorphTo(uiComponent, startColor=uiComponent.GetRGBA(), endColor=newColor, duration=FADE_ANIMATION_TIME)
    else:
        uiComponent.SetRGBA(*newColor)


def MakeTransparent(uiComponent, animate = False):
    if animate:
        uicore.animations.MorphScalar(uiComponent, 'opacity', startVal=uiComponent.opacity, endVal=0.0, duration=FADE_ANIMATION_TIME)
    else:
        uiComponent.opacity = 0


def SetEffectOpacity(uiComponent, newOpacity, animate = False):
    if animate:
        uicore.animations.MorphScalar(uiComponent, 'effectOpacity', startVal=uiComponent.effectOpacity, endVal=newOpacity, duration=FADE_ANIMATION_TIME)
    else:
        uiComponent.effectOpacity = newOpacity


def SetSaturation(uiComponent, newSaturation, animate = False):
    if animate:
        uicore.animations.MorphScalar(uiComponent, 'saturation', startVal=uiComponent.saturation, endVal=newSaturation, duration=FADE_ANIMATION_TIME)
    else:
        uiComponent.saturation = newSaturation


def SetMonochromeStyle(uiComponent, animate = False):
    SetColor(uiComponent, Color.GRAY5, animate)
    SetSaturation(uiComponent, 0.0, animate)
    uiComponent.spriteEffect = trinity.TR2_SFX_SOFTLIGHT


@Memoize(5)
def IsMonochromeStyleEnabled():
    if not localization.util.AmOnChineseServer():
        return False
    return sm.RemoteSvc('kiringMgr').IsMonochromeStyleEnabled()
