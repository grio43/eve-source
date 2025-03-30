#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\systemMenu\graphicsOptionsConst.py
from evegraphics import settings as gfxsettings
from localization import GetByLabel
windowed_options = [(GetByLabel('/Carbon/UI/Service/Device/WindowMode'), 1), (GetByLabel('/Carbon/UI/Service/Device/FullScreen'), 0), (GetByLabel('/Carbon/UI/Service/Device/FixedWindowMode'), 2)]
shader_quality_options = [(GetByLabel('UI/SystemMenu/DisplayAndGraphics/Common/LowQuality'), 1), (GetByLabel('UI/SystemMenu/DisplayAndGraphics/Common/MediumQuality'), 2), (GetByLabel('UI/SystemMenu/DisplayAndGraphics/Common/HighQuality'), 3)]
texture_quality_options = [(GetByLabel('UI/SystemMenu/DisplayAndGraphics/Common/LowQuality'), 2), (GetByLabel('UI/SystemMenu/DisplayAndGraphics/Common/MediumQuality'), 1), (GetByLabel('UI/SystemMenu/DisplayAndGraphics/Common/HighQuality'), 0)]
lod_quality_options = [(GetByLabel('UI/SystemMenu/DisplayAndGraphics/Common/LowQuality'), gfxsettings.GFX_LOD_QUALITY_LOW), (GetByLabel('UI/SystemMenu/DisplayAndGraphics/Common/MediumQuality'), gfxsettings.GFX_LOD_QUALITY_MEDIUM), (GetByLabel('UI/SystemMenu/DisplayAndGraphics/Common/HighQuality'), gfxsettings.GFX_LOD_QUALITY_HIGH)]
shadow_quality_options = [(GetByLabel('UI/SystemMenu/DisplayAndGraphics/Common/Disabled'), 0),
 (GetByLabel('UI/SystemMenu/DisplayAndGraphics/Common/LowQuality'), 1),
 (GetByLabel('UI/SystemMenu/DisplayAndGraphics/Common/HighQuality'), 2),
 (GetByLabel('UI/SystemMenu/DisplayAndGraphics/GraphicContentSettings/UltraRaytracedShadows'), 3)]
reflection_quality_options = [(GetByLabel('UI/SystemMenu/DisplayAndGraphics/Common/LowQuality'), gfxsettings.GFX_REFLECTION_QUALITY_LOW),
 (GetByLabel('UI/SystemMenu/DisplayAndGraphics/Common/MediumQuality'), gfxsettings.GFX_REFLECTION_QUALITY_MEDIUM),
 (GetByLabel('UI/SystemMenu/DisplayAndGraphics/Common/HighQuality'), gfxsettings.GFX_REFLECTION_QUALITY_HIGH),
 (GetByLabel('UI/SystemMenu/DisplayAndGraphics/Common/UltraQuality'), gfxsettings.GFX_REFLECTION_QUALITY_ULTRA)]
ao_quality_options = [(GetByLabel('UI/SystemMenu/DisplayAndGraphics/Common/Disabled'), gfxsettings.GFX_AO_QUALITY_OFF),
 (GetByLabel('UI/SystemMenu/DisplayAndGraphics/Common/LowQuality'), gfxsettings.GFX_AO_QUALITY_LOW),
 (GetByLabel('UI/SystemMenu/DisplayAndGraphics/Common/MediumQuality'), gfxsettings.GFX_AO_QUALITY_MEDIUM),
 (GetByLabel('UI/SystemMenu/DisplayAndGraphics/Common/HighQuality'), gfxsettings.GFX_AO_QUALITY_HIGH)]
post_processing_quality_options = [(GetByLabel('UI/SystemMenu/DisplayAndGraphics/Common/LowQuality'), 0), (GetByLabel('UI/SystemMenu/DisplayAndGraphics/Common/MediumQuality'), 1), (GetByLabel('UI/SystemMenu/DisplayAndGraphics/Common/HighQuality'), 2)]
upscaling_technique_options = [(GetByLabel('UI/SystemMenu/DisplayAndGraphics/Common/Off'), gfxsettings.GFX_UPSCALING_TECHNIQUE_NONE),
 (GetByLabel('UI/SystemMenu/DisplayAndGraphics/GraphicContentSettings/Upscaling/Techniques/DLSS'), gfxsettings.GFX_UPSCALING_TECHNIQUE_DLSS),
 (GetByLabel('UI/SystemMenu/DisplayAndGraphics/GraphicContentSettings/Upscaling/Techniques/FSR1'), gfxsettings.GFX_UPSCALING_TECHNIQUE_FSR1),
 (GetByLabel('UI/SystemMenu/DisplayAndGraphics/GraphicContentSettings/Upscaling/Techniques/FSR2'), gfxsettings.GFX_UPSCALING_TECHNIQUE_FSR2),
 (GetByLabel('UI/SystemMenu/DisplayAndGraphics/GraphicContentSettings/Upscaling/Techniques/FSR3'), gfxsettings.GFX_UPSCALING_TECHNIQUE_FSR3),
 (GetByLabel('UI/SystemMenu/DisplayAndGraphics/GraphicContentSettings/Upscaling/Techniques/MetalFX'), gfxsettings.GFX_UPSCALING_TECHNIQUE_METALFX),
 (GetByLabel('UI/SystemMenu/DisplayAndGraphics/GraphicContentSettings/Upscaling/Techniques/XESS'), gfxsettings.GFX_UPSCALING_TECHNIQUE_XESS)]
upscaling_settings_options = [(GetByLabel('UI/SystemMenu/DisplayAndGraphics/GraphicContentSettings/Upscaling/Settings/UltraQuality'), gfxsettings.GFX_UPSCALING_SETTING_ULTRA_QUALITY),
 (GetByLabel('UI/SystemMenu/DisplayAndGraphics/GraphicContentSettings/Upscaling/Settings/Quality'), gfxsettings.GFX_UPSCALING_SETTING_QUALITY),
 (GetByLabel('UI/SystemMenu/DisplayAndGraphics/GraphicContentSettings/Upscaling/Settings/Balanced'), gfxsettings.GFX_UPSCALING_SETTING_BALANCED),
 (GetByLabel('UI/SystemMenu/DisplayAndGraphics/GraphicContentSettings/Upscaling/Settings/Performance'), gfxsettings.GFX_UPSCALING_SETTING_PERFORMANCE),
 (GetByLabel('UI/SystemMenu/DisplayAndGraphics/GraphicContentSettings/Upscaling/Settings/UltraPerformance'), gfxsettings.GFX_UPSCALING_SETTING_ULTRA_PERFORMANCE)]
volumetric_quality_options = [(GetByLabel('UI/SystemMenu/DisplayAndGraphics/Common/LowQuality'), gfxsettings.GFX_VOLUMETRIC_QUALITY_LOW),
 (GetByLabel('UI/SystemMenu/DisplayAndGraphics/Common/MediumQuality'), gfxsettings.GFX_VOLUMETRIC_QUALITY_MEDIUM),
 (GetByLabel('UI/SystemMenu/DisplayAndGraphics/Common/HighQuality'), gfxsettings.GFX_VOLUMETRIC_QUALITY_HIGH),
 (GetByLabel('UI/SystemMenu/DisplayAndGraphics/Common/UltraQuality'), gfxsettings.GFX_VOLUMETRIC_QUALITY_ULTRA)]
