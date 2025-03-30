#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evegraphics\settings.py
import platform
import trinity
import logging
import threadutils
from evegraphics.utils import DummyGroup
from yamlext.blueutil import ReadYamlFile
SETTINGS_GROUP_DEVICE = 'settings.public.device'
SETTINGS_GROUP_UI = 'settings.user.ui'
GFX_ANTI_ALIASING = (SETTINGS_GROUP_DEVICE, 'antiAliasing')
GFX_LOD_QUALITY = (SETTINGS_GROUP_DEVICE, 'lodQuality')
GFX_POST_PROCESSING_QUALITY = (SETTINGS_GROUP_DEVICE, 'postProcessingQuality')
GFX_SHADER_QUALITY = (SETTINGS_GROUP_DEVICE, 'shaderQuality')
GFX_SHADOW_QUALITY = (SETTINGS_GROUP_DEVICE, 'shadowQuality')
GFX_TEXTURE_QUALITY = (SETTINGS_GROUP_DEVICE, 'textureQuality')
GFX_REFLECTION_QUALITY = (SETTINGS_GROUP_DEVICE, 'reflectionQuality')
GFX_AO_QUALITY = (SETTINGS_GROUP_DEVICE, 'aoQuality')
GFX_UPSCALING_TECHNIQUE = (SETTINGS_GROUP_DEVICE, 'upscalingTechnique')
GFX_UPSCALING_SETTING = (SETTINGS_GROUP_DEVICE, 'upscalingSetting')
GFX_FRAMEGENERATION_ENABLED = (SETTINGS_GROUP_DEVICE, 'frameGeneration')
GFX_DOF_POSTPROCESS_ENABLED = (SETTINGS_GROUP_DEVICE, 'dofEnabled')
GFX_VOLUMETRIC_QUALITY = (SETTINGS_GROUP_DEVICE, 'volumetricQuality')
GFX_CHAR_TEXTURE_QUALITY = (SETTINGS_GROUP_DEVICE, 'charTextureQuality')
GFX_CHAR_FAST_CHARACTER_CREATION = (SETTINGS_GROUP_DEVICE, 'fastCharacterCreation')
GFX_CHAR_CLOTH_SIMULATION = (SETTINGS_GROUP_DEVICE, 'charClothSimulation')
GFX_UI_SCALE_WINDOWED = (SETTINGS_GROUP_DEVICE, 'UIScaleWindowed')
GFX_UI_SCALE_FULLSCREEN = (SETTINGS_GROUP_DEVICE, 'UIScaleFullscreen')
GFX_UI_SCALE_WINDOWED_SET_AUTOMATICALLY = (SETTINGS_GROUP_DEVICE, 'UIScaleWindowedSetAutomatically')
GFX_UI_SCALE_FULLSCREEN_SET_AUTOMATICALLY = (SETTINGS_GROUP_DEVICE, 'UIScaleFullscreenSetAutomatically')
GFX_RESOLUTION_WINDOWED = (SETTINGS_GROUP_DEVICE, 'WindowedResolution')
GFX_RESOLUTION_FULLSCREEN = (SETTINGS_GROUP_DEVICE, 'FullScreenResolution')
GFX_WINDOW_BORDER_FIXED = (SETTINGS_GROUP_DEVICE, 'FixedWindow')
GFX_DEVICE_SETTINGS = (SETTINGS_GROUP_DEVICE, 'DeviceSettings')
GFX_WINDOWED_MODE_SETTINGS = (SETTINGS_GROUP_DEVICE, 'WindowedSettings')
GFX_FULL_SCREEN_MODE_SETTINGS = (SETTINGS_GROUP_DEVICE, 'FullScreenSettings')
GFX_FIXED_WINDOW_MODE_SETTINGS = (SETTINGS_GROUP_DEVICE, 'FixedWindowSettings')
GFX_WINDOW_MODE = (SETTINGS_GROUP_DEVICE, 'WindowMode')
GFX_BRIGHTNESS = (SETTINGS_GROUP_DEVICE, 'brightness')
UI_TURRETS_ENABLED = (SETTINGS_GROUP_UI, 'turretsEnabled')
UI_EFFECTS_ENABLED = (SETTINGS_GROUP_UI, 'effectsEnabled')
UI_MISSILES_ENABLED = (SETTINGS_GROUP_UI, 'missilesEnabled')
UI_DRONE_MODELS_ENABLED = (SETTINGS_GROUP_UI, 'droneModelsEnabled')
UI_EXPLOSION_EFFECTS_ENABLED = (SETTINGS_GROUP_UI, 'explosionEffectsEnabled')
UI_TRAILS_ENABLED = (SETTINGS_GROUP_UI, 'trailsEnabled')
UI_GPU_PARTICLES_ENABLED = (SETTINGS_GROUP_UI, 'gpuParticlesEnabled')
UI_ASTEROID_ATMOSPHERICS = (SETTINGS_GROUP_UI, 'UI_ASTEROID_ATMOSPHERICS')
UI_ASTEROID_FOG = (SETTINGS_GROUP_UI, 'UI_ASTEROID_FOG')
UI_ASTEROID_CLOUDFIELD = (SETTINGS_GROUP_UI, 'UI_ASTEROID_CLOUDFIELD')
UI_ASTEROID_GODRAYS = (SETTINGS_GROUP_UI, 'UI_ASTEROID_GODRAYS')
UI_ASTEROID_PARTICLES = (SETTINGS_GROUP_UI, 'UI_ASTEROID_PARTICLES')
UI_CAMERA_OFFSET = (SETTINGS_GROUP_UI, 'cameraOffset')
UI_OFFSET_UI_WITH_CAMERA = (SETTINGS_GROUP_UI, 'offsetUIwithCamera')
UI_CAMERA_SHAKE_ENABLED = (SETTINGS_GROUP_UI, 'cameraShakeEnabled')
UI_CAMERA_BOBBING_ENABLED = (SETTINGS_GROUP_UI, 'cameraBobbingEnabled')
UI_CAMERA_DYNAMIC_CAMERA_MOVEMENT = (SETTINGS_GROUP_UI, 'cameraDynamicMovement')
UI_ADVANCED_CAMERA = (SETTINGS_GROUP_UI, 'advancedCamera')
UI_INVERT_CAMERA_ZOOM = (SETTINGS_GROUP_UI, 'invertCameraZoom')
UI_CAMERA_INVERT_Y = (SETTINGS_GROUP_UI, 'cameraInvertY')
UI_CAMERA_INERTIA = (SETTINGS_GROUP_UI, 'cameraInertia')
UI_CAMERA_SENSITIVITY = (SETTINGS_GROUP_UI, 'cameraSensitivity')
UI_CAMERA_SPACEMOUSE_SPEED_COEFFICIENT = (SETTINGS_GROUP_UI, 'spaceMouseSpeedCoefficient')
UI_CAMERA_SPACEMOUSE_ACCELERATION_COEFFICIENT = (SETTINGS_GROUP_UI, 'spaceMouseAccelerationCoefficient')
UI_NCC_GREEN_SCREEN = (SETTINGS_GROUP_UI, 'NCCgreenscreen')
UI_MODELSKINSINSPACE_ENABLED = (SETTINGS_GROUP_UI, 'modelSkinsInSpaceEnabled')
GFX_FSR_MODE = (SETTINGS_GROUP_DEVICE, 'fsrMode')
GFX_REFLECTION_QUALITY_OFF = 0
GFX_REFLECTION_QUALITY_LOW = 1
GFX_REFLECTION_QUALITY_MEDIUM = 2
GFX_REFLECTION_QUALITY_HIGH = 3
GFX_REFLECTION_QUALITY_ULTRA = 4
GFX_AO_QUALITY_OFF = 0
GFX_AO_QUALITY_LOW = 1
GFX_AO_QUALITY_MEDIUM = 2
GFX_AO_QUALITY_HIGH = 3
GFX_VOLUMETRIC_QUALITY_LOW = 0
GFX_VOLUMETRIC_QUALITY_MEDIUM = 1
GFX_VOLUMETRIC_QUALITY_HIGH = 2
GFX_VOLUMETRIC_QUALITY_ULTRA = 3
GFX_UPSCALING_TECHNIQUE_NONE = trinity.UPSCALING_TECHNIQUE.NONE
GFX_UPSCALING_TECHNIQUE_FSR1 = trinity.UPSCALING_TECHNIQUE.FSR1
GFX_UPSCALING_TECHNIQUE_FSR2 = trinity.UPSCALING_TECHNIQUE.FSR2
GFX_UPSCALING_TECHNIQUE_FSR3 = trinity.UPSCALING_TECHNIQUE.FSR3
GFX_UPSCALING_TECHNIQUE_METALFX = trinity.UPSCALING_TECHNIQUE.METALFX
GFX_UPSCALING_TECHNIQUE_DLSS = trinity.UPSCALING_TECHNIQUE.DLSS
GFX_UPSCALING_TECHNIQUE_XESS = trinity.UPSCALING_TECHNIQUE.XESS
GFX_UPSCALING_SETTING_NATIVE = trinity.UPSCALING_SETTING.NATIVE
GFX_UPSCALING_SETTING_ULTRA_PERFORMANCE = trinity.UPSCALING_SETTING.ULTRA_PERFORMANCE
GFX_UPSCALING_SETTING_PERFORMANCE = trinity.UPSCALING_SETTING.PERFORMANCE
GFX_UPSCALING_SETTING_BALANCED = trinity.UPSCALING_SETTING.BALANCED
GFX_UPSCALING_SETTING_QUALITY = trinity.UPSCALING_SETTING.QUALITY
GFX_UPSCALING_SETTING_ULTRA_QUALITY = trinity.UPSCALING_SETTING.ULTRA_QUALITY
GFX_LOD_QUALITY_HIGH = 3
GFX_LOD_QUALITY_MEDIUM = 2
GFX_LOD_QUALITY_LOW = 1
AA_QUALITY_DISABLED = 0
AA_QUALITY_TAA_LOW = 1
AA_QUALITY_TAA_MEDIUM = 2
AA_QUALITY_TAA_HIGH = 3
GFX_SETTINGS = {GFX_ANTI_ALIASING,
 GFX_LOD_QUALITY,
 GFX_POST_PROCESSING_QUALITY,
 GFX_SHADER_QUALITY,
 GFX_SHADOW_QUALITY,
 GFX_TEXTURE_QUALITY,
 GFX_REFLECTION_QUALITY,
 GFX_AO_QUALITY,
 GFX_VOLUMETRIC_QUALITY,
 GFX_UPSCALING_TECHNIQUE,
 GFX_UPSCALING_SETTING,
 GFX_FRAMEGENERATION_ENABLED,
 GFX_CHAR_FAST_CHARACTER_CREATION,
 GFX_CHAR_CLOTH_SIMULATION,
 GFX_UI_SCALE_FULLSCREEN,
 GFX_UI_SCALE_FULLSCREEN_SET_AUTOMATICALLY,
 GFX_RESOLUTION_FULLSCREEN,
 GFX_WINDOW_BORDER_FIXED,
 UI_TRAILS_ENABLED,
 UI_EFFECTS_ENABLED,
 UI_CAMERA_OFFSET}
LOD_SETTINGS = {'eveSpaceSceneVisibilityThreshold': {GFX_LOD_QUALITY_LOW: 15.0,
                                      GFX_LOD_QUALITY_MEDIUM: 6.0,
                                      GFX_LOD_QUALITY_HIGH: 3.0},
 'eveSpaceSceneLowDetailThreshold': {GFX_LOD_QUALITY_LOW: 140.0,
                                     GFX_LOD_QUALITY_MEDIUM: 70.0,
                                     GFX_LOD_QUALITY_HIGH: 35.0},
 'eveSpaceSceneMediumDetailThreshold': {GFX_LOD_QUALITY_LOW: 480.0,
                                        GFX_LOD_QUALITY_MEDIUM: 240.0,
                                        GFX_LOD_QUALITY_HIGH: 120.0},
 'eveSpaceSceneLODFactor': {GFX_LOD_QUALITY_LOW: 4.0,
                            GFX_LOD_QUALITY_MEDIUM: 2.0,
                            GFX_LOD_QUALITY_HIGH: 1.0}}

@threadutils.Memoize
def _LoadDeviceClassifications():
    try:
        data = ReadYamlFile('res:/videoCardCategories.yaml') or []
        result = {tuple(k[0]):k[1] for k in data}
    except:
        logging.exception('Failed to load videoCardCategories.yaml')
        result = {}

    for k, v in result.items():
        if v not in (DEVICE_HIGH_END, DEVICE_MID_RANGE, DEVICE_LOW_END):
            logging.error("Incorrect GPU classification '%s' for %s/%s vendor/device ID", v, k[0], k[1])
            result[k] = DEVICE_HIGH_END

    return result


DEVICE_HIGH_END = 'high'
DEVICE_MID_RANGE = 'medium'
DEVICE_LOW_END = 'low'

class UninitializedSettingsGroupError(Exception):
    pass


class NoAdaptersFoundError(Exception):
    pass


@threadutils.Memoize
def GetDeviceClassification():
    identifier = None
    if trinity.device.deviceType == trinity.TriDeviceType.SOFTWARE:
        return DEVICE_HIGH_END
    if trinity.adapters.GetAdapterCount() > 0:
        identifier = trinity.adapters.GetAdapterInfo(0)
    if identifier is None:
        raise NoAdaptersFoundError()
    vendorID = identifier.vendorID
    deviceID = identifier.deviceID
    log = logging.getLogger(__name__)
    deviceClassifications = _LoadDeviceClassifications()
    found = deviceClassifications.get((vendorID, deviceID), None)
    if found is not None:
        log.warn("Found GPU classification '%s' for %s/%s vendor/device ID", found, vendorID, deviceID)
    else:
        log.warn("Did not find GPU classification for %s/%s vendor/device ID - assuming 'high'", vendorID, deviceID)
        found = DEVICE_HIGH_END
    return found


SECONDARY_LIGHTING_INTENSITY = 3.14
SHADER_MODEL_LOW = 1
SHADER_MODEL_MEDIUM = 2
SHADER_MODEL_HIGH = 3
MAX_SHADER_MODEL = SHADER_MODEL_HIGH
defaultCommonSettings = {SETTINGS_GROUP_DEVICE: {GFX_UI_SCALE_WINDOWED: None,
                         GFX_UI_SCALE_FULLSCREEN: None,
                         GFX_FRAMEGENERATION_ENABLED: False,
                         GFX_UI_SCALE_WINDOWED_SET_AUTOMATICALLY: False,
                         GFX_UI_SCALE_FULLSCREEN_SET_AUTOMATICALLY: False,
                         GFX_RESOLUTION_WINDOWED: None,
                         GFX_RESOLUTION_FULLSCREEN: None,
                         GFX_WINDOW_BORDER_FIXED: 0,
                         GFX_ANTI_ALIASING: AA_QUALITY_TAA_HIGH,
                         GFX_LOD_QUALITY: 3,
                         GFX_TEXTURE_QUALITY: 0,
                         GFX_SHADER_QUALITY: MAX_SHADER_MODEL,
                         GFX_REFLECTION_QUALITY: GFX_REFLECTION_QUALITY_LOW,
                         GFX_AO_QUALITY: GFX_AO_QUALITY_MEDIUM,
                         GFX_VOLUMETRIC_QUALITY: GFX_VOLUMETRIC_QUALITY_HIGH,
                         GFX_UPSCALING_TECHNIQUE: trinity.UPSCALING_TECHNIQUE.NONE,
                         GFX_UPSCALING_SETTING: trinity.UPSCALING_SETTING.NATIVE,
                         GFX_FRAMEGENERATION_ENABLED: False,
                         GFX_CHAR_TEXTURE_QUALITY: 1,
                         GFX_CHAR_FAST_CHARACTER_CREATION: 0,
                         GFX_CHAR_CLOTH_SIMULATION: 1,
                         GFX_DEVICE_SETTINGS: None,
                         GFX_WINDOWED_MODE_SETTINGS: None,
                         GFX_FULL_SCREEN_MODE_SETTINGS: None,
                         GFX_FIXED_WINDOW_MODE_SETTINGS: None,
                         GFX_WINDOW_MODE: 0,
                         GFX_BRIGHTNESS: 1.0,
                         GFX_DOF_POSTPROCESS_ENABLED: False},
 SETTINGS_GROUP_UI: {UI_TURRETS_ENABLED: 1,
                     UI_EFFECTS_ENABLED: 1,
                     UI_MISSILES_ENABLED: 1,
                     UI_DRONE_MODELS_ENABLED: 1,
                     UI_EXPLOSION_EFFECTS_ENABLED: 1,
                     UI_TRAILS_ENABLED: 1,
                     UI_GPU_PARTICLES_ENABLED: 1,
                     UI_ASTEROID_ATMOSPHERICS: 1,
                     UI_ASTEROID_CLOUDFIELD: 1,
                     UI_ASTEROID_FOG: 1,
                     UI_ASTEROID_GODRAYS: 1,
                     UI_ASTEROID_PARTICLES: 1,
                     UI_MODELSKINSINSPACE_ENABLED: 1,
                     UI_CAMERA_OFFSET: 0,
                     UI_OFFSET_UI_WITH_CAMERA: 0,
                     UI_CAMERA_SHAKE_ENABLED: 1,
                     UI_CAMERA_BOBBING_ENABLED: 1,
                     UI_CAMERA_DYNAMIC_CAMERA_MOVEMENT: 1,
                     UI_ADVANCED_CAMERA: 0,
                     UI_INVERT_CAMERA_ZOOM: 0,
                     UI_CAMERA_INVERT_Y: 0,
                     UI_CAMERA_INERTIA: 0.0,
                     UI_CAMERA_SENSITIVITY: 0.0,
                     UI_CAMERA_SPACEMOUSE_ACCELERATION_COEFFICIENT: 0.25,
                     UI_CAMERA_SPACEMOUSE_SPEED_COEFFICIENT: 0.25,
                     UI_NCC_GREEN_SCREEN: 0}}
defaultClassificationSettings = {SETTINGS_GROUP_DEVICE: {DEVICE_HIGH_END: {GFX_ANTI_ALIASING: AA_QUALITY_TAA_HIGH,
                                           GFX_POST_PROCESSING_QUALITY: 2,
                                           GFX_SHADOW_QUALITY: 2,
                                           GFX_REFLECTION_QUALITY: GFX_REFLECTION_QUALITY_HIGH,
                                           GFX_AO_QUALITY: GFX_AO_QUALITY_LOW if platform.system() == 'Darwin' else GFX_AO_QUALITY_HIGH,
                                           GFX_VOLUMETRIC_QUALITY: GFX_VOLUMETRIC_QUALITY_HIGH,
                                           GFX_DOF_POSTPROCESS_ENABLED: platform.system() != 'Darwin'},
                         DEVICE_MID_RANGE: {GFX_ANTI_ALIASING: AA_QUALITY_TAA_MEDIUM,
                                            GFX_POST_PROCESSING_QUALITY: 1,
                                            GFX_SHADOW_QUALITY: 1,
                                            GFX_SHADER_QUALITY: SHADER_MODEL_MEDIUM,
                                            GFX_LOD_QUALITY: 2,
                                            GFX_REFLECTION_QUALITY: GFX_REFLECTION_QUALITY_LOW,
                                            GFX_AO_QUALITY: GFX_AO_QUALITY_LOW,
                                            GFX_VOLUMETRIC_QUALITY: GFX_VOLUMETRIC_QUALITY_MEDIUM},
                         DEVICE_LOW_END: {GFX_ANTI_ALIASING: AA_QUALITY_DISABLED,
                                          GFX_POST_PROCESSING_QUALITY: 0,
                                          GFX_SHADOW_QUALITY: 0,
                                          GFX_SHADER_QUALITY: SHADER_MODEL_LOW,
                                          GFX_LOD_QUALITY: 1,
                                          GFX_CHAR_FAST_CHARACTER_CREATION: 1,
                                          GFX_AO_QUALITY: GFX_AO_QUALITY_OFF,
                                          GFX_VOLUMETRIC_QUALITY: GFX_VOLUMETRIC_QUALITY_LOW}},
 SETTINGS_GROUP_UI: {DEVICE_HIGH_END: {},
                     DEVICE_MID_RANGE: {},
                     DEVICE_LOW_END: {}}}
maxDefaultResolution = {DEVICE_HIGH_END: 2160,
 DEVICE_MID_RANGE: 1080,
 DEVICE_LOW_END: 1080}

def GetSettingKey(setting):
    return setting[1]


def GetSettingGroupName(setting):
    return setting[0]


def GetDefault(setting):
    group, item = setting
    if setting in defaultClassificationSettings[group][GetDeviceClassification()]:
        return defaultClassificationSettings[group][GetDeviceClassification()][setting]
    return defaultCommonSettings[group][setting]


def GetSettingFromSettingKey(key):
    for group in defaultClassificationSettings:
        for setting in defaultClassificationSettings[group][GetDeviceClassification()]:
            if key == GetSettingKey(setting):
                return setting

    for group in defaultCommonSettings:
        for setting in defaultCommonSettings[group]:
            if key == GetSettingKey(setting):
                return setting


def GetMaximumDefaultResolution():
    if platform.system() == 'Darwin':
        return maxDefaultResolution.get(GetDeviceClassification(), None)


def GetDefaultAntiAliasingQuality(width, height):
    resolution = min(width, height)
    if resolution >= 2160:
        aa = AA_QUALITY_DISABLED
    elif resolution >= 1800:
        aa = AA_QUALITY_TAA_MEDIUM
    else:
        aa = AA_QUALITY_TAA_HIGH
    return min(aa, GetDefault(GFX_ANTI_ALIASING))


class GraphicsSettings(object):
    _globalInstance = None

    def __init__(self):
        self.settingsGroups = {}
        self.pendingSettings = {}
        self.storedValues = {}

    def InitializeSettingsGroup(self, groupName, settingsGroup):
        self.pendingSettings[groupName] = {}
        self.settingsGroups[groupName] = settingsGroup
        self._InitializeSettings(groupName, settingsGroup)

    def _GetSettingsGroup(self, group):
        if group not in self.settingsGroups:
            msg = 'GraphicsSettings.Get called on uninitialized settings group, ' + group
            raise UninitializedSettingsGroupError(msg)
        return self.settingsGroups[group]

    def _GetPendingGroup(self, group):
        if group not in self.pendingSettings:
            msg = 'GraphicsSettings.Get called on uninitialized settings group, ' + group
            raise UninitializedSettingsGroupError(msg)
        return self.pendingSettings[group]

    def _InitializeSettings(self, groupName, settingsGroup):

        def _SetSetting(setting):
            key = GetSettingKey(setting)
            settingsGroup.Set(key, settingsGroup.Get(key, GetDefault(setting)))

        for setting in defaultCommonSettings[groupName]:
            _SetSetting(setting)

        for setting in defaultClassificationSettings[groupName][GetDeviceClassification()]:
            _SetSetting(setting)

    def Get(self, setting):
        group = self._GetSettingsGroup(GetSettingGroupName(setting))
        key = GetSettingKey(setting)
        return group.Get(key)

    def Set(self, setting, value):
        group = self._GetSettingsGroup(GetSettingGroupName(setting))
        key = GetSettingKey(setting)
        return group.Set(key, value)

    def SetPending(self, setting, value):
        group = self._GetPendingGroup(GetSettingGroupName(setting))
        group[setting] = value

    def GetPendingOrCurrent(self, setting):
        group = self._GetPendingGroup(GetSettingGroupName(setting))
        if setting in group:
            return group[setting]
        return self.Get(setting)

    def ApplyPendingChanges(self, groupName):
        changes = []
        group = self._GetPendingGroup(groupName)
        for setting in group:
            if group[setting] != self.Get(setting):
                changes.append(setting)
                self.Set(setting, group[setting])

        self.ClearPendingChanges(groupName)
        return changes

    def ClearPendingChanges(self, groupName):
        group = self._GetPendingGroup(groupName)
        group.clear()

    def IsInitialized(self, groupName):
        return groupName in self.settingsGroups

    @staticmethod
    def GetGlobal():
        if GraphicsSettings._globalInstance is None:
            GraphicsSettings._globalInstance = GraphicsSettings()
        return GraphicsSettings._globalInstance


def Get(setting, default = None):
    gfx = GraphicsSettings.GetGlobal()
    value = gfx.Get(setting)
    if value is None:
        return default
    return value


def Set(setting, value, pending = True):
    gfx = GraphicsSettings.GetGlobal()
    if pending:
        gfx.SetPending(setting, value)
    else:
        gfx.Set(setting, value)


def SetDefault(setting, pending = True):
    gfx = GraphicsSettings.GetGlobal()
    if pending:
        gfx.SetPending(setting, GetDefault(setting))
    else:
        gfx.Set(setting, GetDefault(setting))


def GetPendingOrCurrent(setting):
    gfx = GraphicsSettings.GetGlobal()
    return gfx.GetPendingOrCurrent(setting)


def ApplyPendingChanges(groupName):
    gfx = GraphicsSettings.GetGlobal()
    return gfx.ApplyPendingChanges(groupName)


def ClearPendingChanges(groupName):
    gfx = GraphicsSettings.GetGlobal()
    gfx.ClearPendingChanges(groupName)


def IsInitialized(groupName):
    gfx = GraphicsSettings.GetGlobal()
    return gfx.IsInitialized(groupName)


def ValidateSettings():
    aaQuality = Get(GFX_ANTI_ALIASING)
    taaSupported = Get(GFX_SHADER_QUALITY) == SHADER_MODEL_HIGH
    if not taaSupported:
        Set(GFX_ANTI_ALIASING, AA_QUALITY_DISABLED, pending=False)
    ui_scale_windowed = Get(GFX_UI_SCALE_WINDOWED)
    if ui_scale_windowed is None:
        Set(GFX_UI_SCALE_WINDOWED_SET_AUTOMATICALLY, True, pending=False)
    ui_scale_fullscreen = Get(GFX_UI_SCALE_FULLSCREEN)
    if ui_scale_fullscreen is None:
        Set(GFX_UI_SCALE_FULLSCREEN_SET_AUTOMATICALLY, True, pending=False)


def InitializeForJessica():
    for groupName in defaultCommonSettings.keys():
        GraphicsSettings.GetGlobal().InitializeSettingsGroup(groupName, DummyGroup())


def ApplyLodSettings(upscaling = 1.0):
    try:
        lodQuality = Get(GFX_LOD_QUALITY)
    except UninitializedSettingsGroupError:
        lodQuality = GFX_LOD_QUALITY_HIGH

    for lodSettingName, lodSettings in LOD_SETTINGS.iteritems():
        trinity.settings.SetValue(lodSettingName, lodSettings[lodQuality] / upscaling)


def GetLodSettings():
    lodQuality = Get(GFX_LOD_QUALITY)
    settings = {}
    for lodSettingName, lodSettings in LOD_SETTINGS.iteritems():
        settings[lodSettingName] = lodSettings[lodQuality]

    return settings
