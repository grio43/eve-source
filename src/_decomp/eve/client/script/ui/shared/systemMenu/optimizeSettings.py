#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\systemMenu\optimizeSettings.py
import carbonui
import carbonui.const as uiconst
import evegraphics.settings as gfxsettings
import localization
from carbonui import IdealSize
from carbonui.button.group import ButtonGroup
from carbonui.control.combo import Combo
from eve.client.script.ui.control.eveEditPlainText import EditPlainText
from carbonui.control.window import Window

class OptimizationModes(object):
    MEMORY_OPTIMIZATION_MODE = 1
    PERFORMANCE_OPTIMIZATION_MODE = 2
    QUALITY_OPTIMIZATION_MODE = 3


OPTIMIZATION_MODES = [OptimizationModes.MEMORY_OPTIMIZATION_MODE, OptimizationModes.PERFORMANCE_OPTIMIZATION_MODE, OptimizationModes.QUALITY_OPTIMIZATION_MODE]
MODE_LABELS = {OptimizationModes.MEMORY_OPTIMIZATION_MODE: 'UI/SystemMenu/DisplayAndGraphics/OptimizeSettings/OptimizeSettingsMemory',
 OptimizationModes.PERFORMANCE_OPTIMIZATION_MODE: 'UI/SystemMenu/DisplayAndGraphics/OptimizeSettings/OptimizeSettingsPerformance',
 OptimizationModes.QUALITY_OPTIMIZATION_MODE: 'UI/SystemMenu/DisplayAndGraphics/OptimizeSettings/OptimizeSettingsQuality'}
MODE_INFO_LABELS = {OptimizationModes.MEMORY_OPTIMIZATION_MODE: 'UI/SystemMenu/DisplayAndGraphics/OptimizeSettings/OptimizeSettingsMemoryInfo',
 OptimizationModes.PERFORMANCE_OPTIMIZATION_MODE: 'UI/SystemMenu/DisplayAndGraphics/OptimizeSettings/OptimizeSettingsPerformanceInfo',
 OptimizationModes.QUALITY_OPTIMIZATION_MODE: 'UI/SystemMenu/DisplayAndGraphics/OptimizeSettings/OptimizeSettingsQualityInfo'}

def SetMemoryOptimization():
    gfxsettings.Set(gfxsettings.GFX_TEXTURE_QUALITY, 2)
    gfxsettings.Set(gfxsettings.GFX_SHADER_QUALITY, 1)
    gfxsettings.Set(gfxsettings.GFX_SHADOW_QUALITY, 0)
    gfxsettings.Set(gfxsettings.GFX_POST_PROCESSING_QUALITY, 0)
    gfxsettings.Set(gfxsettings.GFX_LOD_QUALITY, 2)
    gfxsettings.Set(gfxsettings.GFX_CHAR_FAST_CHARACTER_CREATION, 1)
    gfxsettings.Set(gfxsettings.GFX_CHAR_TEXTURE_QUALITY, 2)
    gfxsettings.Set(gfxsettings.GFX_ANTI_ALIASING, 0)
    gfxsettings.Set(gfxsettings.GFX_DOF_POSTPROCESS_ENABLED, False)
    gfxsettings.Set(gfxsettings.GFX_VOLUMETRIC_QUALITY, gfxsettings.GFX_VOLUMETRIC_QUALITY_LOW)
    if eve.session.userid:
        gfxsettings.Set(gfxsettings.UI_DRONE_MODELS_ENABLED, 0)
        gfxsettings.Set(gfxsettings.UI_EFFECTS_ENABLED, 1)
        gfxsettings.Set(gfxsettings.UI_MISSILES_ENABLED, 1)
        gfxsettings.Set(gfxsettings.UI_EXPLOSION_EFFECTS_ENABLED, 1)
        gfxsettings.Set(gfxsettings.UI_TURRETS_ENABLED, 1)
        gfxsettings.Set(gfxsettings.UI_TRAILS_ENABLED, 0)
        gfxsettings.Set(gfxsettings.UI_GPU_PARTICLES_ENABLED, 0)
        gfxsettings.Set(gfxsettings.UI_ASTEROID_ATMOSPHERICS, 0)
        gfxsettings.Set(gfxsettings.UI_MODELSKINSINSPACE_ENABLED, 1)


def SetPerformanceOptimization():
    gfxsettings.Set(gfxsettings.GFX_TEXTURE_QUALITY, 1)
    gfxsettings.Set(gfxsettings.GFX_SHADER_QUALITY, 1)
    gfxsettings.Set(gfxsettings.GFX_SHADOW_QUALITY, 0)
    gfxsettings.Set(gfxsettings.GFX_POST_PROCESSING_QUALITY, 0)
    gfxsettings.Set(gfxsettings.GFX_LOD_QUALITY, 1)
    gfxsettings.Set(gfxsettings.GFX_CHAR_FAST_CHARACTER_CREATION, 1)
    gfxsettings.Set(gfxsettings.GFX_CHAR_TEXTURE_QUALITY, 1)
    gfxsettings.Set(gfxsettings.GFX_ANTI_ALIASING, 0)
    gfxsettings.Set(gfxsettings.GFX_DOF_POSTPROCESS_ENABLED, False)
    gfxsettings.Set(gfxsettings.GFX_VOLUMETRIC_QUALITY, gfxsettings.GFX_VOLUMETRIC_QUALITY_LOW)
    gfxsettings.Set(gfxsettings.GFX_REFLECTION_QUALITY, gfxsettings.GFX_REFLECTION_QUALITY_ULTRA)
    if eve.session.userid:
        gfxsettings.Set(gfxsettings.UI_DRONE_MODELS_ENABLED, 0)
        gfxsettings.Set(gfxsettings.UI_EFFECTS_ENABLED, 0)
        gfxsettings.Set(gfxsettings.UI_MISSILES_ENABLED, 0)
        gfxsettings.Set(gfxsettings.UI_EXPLOSION_EFFECTS_ENABLED, 0)
        gfxsettings.Set(gfxsettings.UI_TURRETS_ENABLED, 0)
        gfxsettings.Set(gfxsettings.UI_TRAILS_ENABLED, 0)
        gfxsettings.Set(gfxsettings.UI_GPU_PARTICLES_ENABLED, 0)
        gfxsettings.Set(gfxsettings.UI_ASTEROID_ATMOSPHERICS, 0)
        gfxsettings.Set(gfxsettings.UI_MODELSKINSINSPACE_ENABLED, 0)


def SetQualityOptimization():
    gfxsettings.Set(gfxsettings.GFX_TEXTURE_QUALITY, 0)
    gfxsettings.Set(gfxsettings.GFX_SHADER_QUALITY, gfxsettings.MAX_SHADER_MODEL)
    gfxsettings.Set(gfxsettings.GFX_SHADOW_QUALITY, 2)
    gfxsettings.Set(gfxsettings.GFX_POST_PROCESSING_QUALITY, 2)
    gfxsettings.Set(gfxsettings.GFX_LOD_QUALITY, 3)
    gfxsettings.Set(gfxsettings.GFX_CHAR_FAST_CHARACTER_CREATION, 0)
    gfxsettings.Set(gfxsettings.GFX_CHAR_TEXTURE_QUALITY, 0)
    gfxsettings.Set(gfxsettings.GFX_ANTI_ALIASING, gfxsettings.AA_QUALITY_TAA_HIGH)
    gfxsettings.Set(gfxsettings.GFX_AO_QUALITY, gfxsettings.GetDefault(gfxsettings.GFX_AO_QUALITY))
    gfxsettings.Set(gfxsettings.GFX_DOF_POSTPROCESS_ENABLED, True)
    gfxsettings.Set(gfxsettings.GFX_VOLUMETRIC_QUALITY, gfxsettings.GFX_VOLUMETRIC_QUALITY_HIGH)
    if eve.session.userid:
        gfxsettings.Set(gfxsettings.UI_DRONE_MODELS_ENABLED, 1)
        gfxsettings.Set(gfxsettings.UI_EFFECTS_ENABLED, 1)
        gfxsettings.Set(gfxsettings.UI_MISSILES_ENABLED, 1)
        gfxsettings.Set(gfxsettings.UI_EXPLOSION_EFFECTS_ENABLED, 1)
        gfxsettings.Set(gfxsettings.UI_TURRETS_ENABLED, 1)
        gfxsettings.Set(gfxsettings.UI_TRAILS_ENABLED, 1)
        gfxsettings.Set(gfxsettings.UI_GPU_PARTICLES_ENABLED, 1)
        gfxsettings.Set(gfxsettings.UI_ASTEROID_ATMOSPHERICS, 1)
        gfxsettings.Set(gfxsettings.UI_MODELSKINSINSPACE_ENABLED, 1)


FUNC_BY_MODE = {OptimizationModes.MEMORY_OPTIMIZATION_MODE: SetMemoryOptimization,
 OptimizationModes.PERFORMANCE_OPTIMIZATION_MODE: SetPerformanceOptimization,
 OptimizationModes.QUALITY_OPTIMIZATION_MODE: SetQualityOptimization}
