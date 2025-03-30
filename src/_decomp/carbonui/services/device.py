#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\services\device.py
import sys
import time
import blue
import eveformat
import uthread
import trinity
import log
import localization
import monolithsentry
import sentry_sdk
import evegraphics.settings as gfxsettings
from carbonui import uiconst
from carbonui.services import deviceSignals
from carbonui.uicore import uicore, GetWindowName
from carbon.common.script.sys import service
from carbon.common.script.sys.serviceManager import ServiceManager
from carbonui.window.layout import apply_desktop_window_layout, capture_desktop_window_layout
MINIMUM_WINDOW_SIZE = (1024, 700)
SCALE_VALUES = (0.9, 1.0, 1.1, 1.25, 1.5, 1.75, 2.0, 2.5, 3.0, 4.0)

def _GetClientSettings():
    return settings


def _GetWindowModeSettingsKey(windowMode):
    if windowMode == trinity.Tr2WindowMode.FULL_SCREEN:
        return gfxsettings.GFX_FULL_SCREEN_MODE_SETTINGS
    if windowMode == trinity.Tr2WindowMode.WINDOWED:
        return gfxsettings.GFX_WINDOWED_MODE_SETTINGS
    if windowMode == trinity.Tr2WindowMode.FIXED_WINDOW:
        return gfxsettings.GFX_FIXED_WINDOW_MODE_SETTINGS
    raise ValueError()


def _SaveStateSettings(state):
    key = _GetWindowModeSettingsKey(state.windowMode)
    settings = {'adapter': state.adapter,
     'width': state.width,
     'height': state.height,
     'presentInterval': state.presentInterval}
    if state.windowMode == trinity.Tr2WindowMode.WINDOWED:
        settings['left'] = state.left
        settings['top'] = state.top
        settings['showState'] = state.showState
    gfxsettings.Set(key, settings, pending=False)


def _ConstraintResolution(state, maxResolution):
    if maxResolution is None:
        return False
    r = min(state.width, state.height)
    if r > maxResolution:
        if r == state.height:
            state.width = 0
            state.height = maxResolution
        else:
            state.height = 0
            state.width = maxResolution
        return True
    return False


def _LoadStateSettings(windowMode):
    key = _GetWindowModeSettingsKey(windowMode)
    state = trinity.mainWindow.GetDefaultState(windowMode)
    settings = gfxsettings.Get(key, None)
    if settings is None:
        if windowMode == trinity.Tr2WindowMode.FULL_SCREEN:
            res = gfxsettings.GetMaximumDefaultResolution()
            if _ConstraintResolution(state, res):
                trinity.mainWindow.SanitizeState(state)
                log.LogNotice('Constraining default fullscreen resolution to %sx%s' % (state.width, state.height))
        return state
    try:
        _LoadStateSettingsFromDict(state, settings)
    except:
        log.LogException()
        sys.exc_clear()
        return trinity.mainWindow.GetDefaultState(windowMode)

    return state


def _LoadStateSettingsFromDict(state, settings):
    state.adapter = int(settings.get('adapter', 0))
    state.presentInterval = int(settings.get('presentInterval', trinity.PRESENT_INTERVAL.ONE))
    state.width = int(settings.get('width', 0))
    state.height = int(settings.get('height', 0))
    if state.windowMode == trinity.Tr2WindowMode.WINDOWED:
        if 'left' in settings and 'top' in settings:
            state.left = int(settings['left'])
            state.top = int(settings['top'])
        else:
            cm = trinity.adapters.GetCurrentDisplayMode(state.adapter)
            state.left = (cm.width - state.width) / 2
            state.top = (cm.height - state.height) / 2
        state.showState = settings.get('showState', trinity.Tr2WindowShowState.NORMAL)


def _ConvertOldStateSettings(settings):
    return {'adapter': settings.get('Adapter', 0),
     'width': settings.get('BackBufferWidth', 0),
     'height': settings.get('BackBufferHeight', 0),
     'presentInterval': settings.get('PresentationInterval', trinity.PRESENT_INTERVAL.ONE)}


def _HasNewStateSettings():
    if gfxsettings.Get(gfxsettings.GFX_FULL_SCREEN_MODE_SETTINGS, None):
        return True
    if gfxsettings.Get(gfxsettings.GFX_WINDOWED_MODE_SETTINGS, None):
        return True
    if gfxsettings.Get(gfxsettings.GFX_FIXED_WINDOW_MODE_SETTINGS, None):
        return True
    return False


def HasOldUpscaling():
    return gfxsettings.Get(gfxsettings.GFX_FSR_MODE, 0) != 0


class DeviceMgr(service.Service):
    __guid__ = 'svc.device'
    __servicename__ = 'device'
    __displayname__ = 'Device Service'
    __startupdependencies__ = ['settings']
    __exportedcalls__ = {'SetDevice': [],
     'GetSettings': [],
     'ResetMonitor': [],
     'ToggleWindowed': [],
     'CreateDevice': [],
     'GetResolutionOptions': [],
     'GetPresentationIntervalOptions': []}

    def __init__(self):
        super(DeviceMgr, self).__init__()
        self._aaTypes = []
        self._settings = {}

    def _MigrateSettings(self):
        personal = gfxsettings.Get(gfxsettings.GFX_DEVICE_SETTINGS).copy()
        if 'PresentationInterval' in personal and personal['PresentationInterval'] & 16 == 0:
            self.LogInfo('Upgrading PresentationInterval setting')
            if personal['PresentationInterval'] == -2147483648:
                personal['PresentationInterval'] = trinity.PRESENT_INTERVAL.IMMEDIATE
            elif personal['PresentationInterval'] == 0:
                personal['PresentationInterval'] = trinity.PRESENT_INTERVAL.ONE
            else:
                personal['PresentationInterval'] = trinity.PRESENT_INTERVAL.ONE + personal['PresentationInterval'] - 1
        if gfxsettings.Get(gfxsettings.GFX_WINDOW_BORDER_FIXED, False):
            _LoadStateSettingsFromDict(self._settings[trinity.Tr2WindowMode.FIXED_WINDOW], _ConvertOldStateSettings(personal))
            gfxsettings.Set(gfxsettings.GFX_WINDOW_MODE, 2, False)
        elif personal.get('Windowed', False):
            _LoadStateSettingsFromDict(self._settings[trinity.Tr2WindowMode.WINDOWED], _ConvertOldStateSettings(personal))
            gfxsettings.Set(gfxsettings.GFX_WINDOW_MODE, 1, False)
        else:
            _LoadStateSettingsFromDict(self._settings[trinity.Tr2WindowMode.FULL_SCREEN], _ConvertOldStateSettings(personal))
            gfxsettings.Set(gfxsettings.GFX_WINDOW_MODE, 0, False)
        resolution = gfxsettings.Get(gfxsettings.GFX_RESOLUTION_WINDOWED)
        if resolution:
            self._settings[trinity.Tr2WindowMode.WINDOWED].width = resolution[0]
            self._settings[trinity.Tr2WindowMode.WINDOWED].height = resolution[1]
        resolution = gfxsettings.Get(gfxsettings.GFX_RESOLUTION_FULLSCREEN)
        if resolution:
            self._settings[trinity.Tr2WindowMode.FULL_SCREEN].width = resolution[0]
            self._settings[trinity.Tr2WindowMode.FULL_SCREEN].height = resolution[1]

    def Run(self, memStream = None):
        self.LogInfo('Starting DeviceMgr')
        gfx = gfxsettings.GraphicsSettings.GetGlobal()
        gfx.InitializeSettingsGroup(gfxsettings.SETTINGS_GROUP_DEVICE, _GetClientSettings().public.device)
        self._ApplyDeviceIndependentSettings()

    def _ApplyDeviceIndependentSettings(self):
        if not _GetClientSettings().public.generic.Get('resourceUnloading', 1):
            trinity.SetEveSpaceObjectResourceUnloadingEnabled(0)
        blue.classes.maxPendingDeletes = 20000
        blue.classes.maxTimeForPendingDeletes = 4.0
        blue.classes.pendingDeletesEnabled = True
        trinity.device.disableAsyncLoad = not bool(_GetClientSettings().public.generic.Get('asyncLoad', 1))
        gfxsettings.ValidateSettings()
        aaQuality = gfxsettings.Get(gfxsettings.GFX_ANTI_ALIASING)
        brightness = gfxsettings.Get(gfxsettings.GFX_BRIGHTNESS)
        trinity.settings.SetValue('eveSpaceSceneGammaBrightness', brightness)
        trinity.device.mipLevelSkipCount = gfxsettings.Get(gfxsettings.GFX_TEXTURE_QUALITY)
        self.SetResourceCacheSize()
        trinity.SetShaderModel(self._GetAppShaderModel())
        for k, v in self._GetAppSettings().iteritems():
            trinity.settings.SetValue(k, v)

        for path in self._GetAppMipLevelSkipExclusionDirectories():
            trinity.AddMipLevelSkipExclusionDirectory(path)

        try:
            trinity.settings.SetValue('fixFullscreenBehaviorForOldWindows', blue.sysinfo.os.majorVersion < 10)
        except LookupError:
            pass

    def Initialize(self):
        trinity.adapters.Refresh()
        adapters = list(range(trinity.adapters.GetAdapterCount()))
        if not adapters:
            self.LogError('No valid display adapter found')
            blue.os.Terminate(12)
        self.LogInfo('Found valid display adapters: %s' % adapters)
        self._settings = {i:_LoadStateSettings(i) for i in (trinity.Tr2WindowMode.FULL_SCREEN, trinity.Tr2WindowMode.WINDOWED, trinity.Tr2WindowMode.FIXED_WINDOW)}
        if not _HasNewStateSettings():
            if gfxsettings.Get(gfxsettings.GFX_DEVICE_SETTINGS):
                self.LogInfo('No new-style settings found, reading old settings')
                self._MigrateSettings()
            else:
                self.LogInfo('No stored settings found')
                fullscreen = self._settings[trinity.Tr2WindowMode.FULL_SCREEN]
                aa = gfxsettings.GetDefaultAntiAliasingQuality(fullscreen.width, fullscreen.height)
                gfxsettings.Set(gfxsettings.GFX_ANTI_ALIASING, min(gfxsettings.Get(gfxsettings.GFX_ANTI_ALIASING), aa), pending=False)
        if HasOldUpscaling():
            hasNewSettings = gfxsettings.Get(gfxsettings.GFX_UPSCALING_TECHNIQUE, gfxsettings.GFX_UPSCALING_TECHNIQUE_NONE) != gfxsettings.GFX_UPSCALING_TECHNIQUE_NONE
            oldSetting = gfxsettings.Get(gfxsettings.GFX_FSR_MODE, 0)
            if not hasNewSettings and oldSetting != 0:
                gfxsettings.Set(gfxsettings.GFX_UPSCALING_TECHNIQUE, gfxsettings.GFX_UPSCALING_TECHNIQUE_FSR1, False)
                gfxsettings.Set(gfxsettings.GFX_UPSCALING_SETTING, 2 ** oldSetting, False)
            if oldSetting != 0:
                gfxsettings.Set(gfxsettings.GFX_FSR_MODE, 0, False)
        if not trinity.settings.GetValue('newUpscalersEnabled') and gfxsettings.Get(gfxsettings.GFX_UPSCALING_TECHNIQUE, gfxsettings.GFX_UPSCALING_TECHNIQUE_NONE) not in (gfxsettings.GFX_UPSCALING_TECHNIQUE_NONE, gfxsettings.GFX_UPSCALING_TECHNIQUE_FSR1):
            gfxsettings.Set(gfxsettings.GFX_UPSCALING_TECHNIQUE, gfxsettings.GFX_UPSCALING_TECHNIQUE_NONE, False)
        for each in self._settings.values():
            trinity.mainWindow.StoreStateSettings(each)

        self.LogInfo('Using settings: ', ' / '.join((str(x) for x in self._settings.values())))

    def Stop(self, memStream = None):
        self.LogInfo('Stopping DeviceMgr')
        service.Service.Stop(self)

    def GetShaderModelForShaderQuality(self, val):
        if val == 3:
            return 'SM_3_0_DEPTH'
        if val == 2:
            return 'SM_3_0_HI'
        return 'SM_3_0_LO'

    def _SaveSettings(self, window):
        mode = window.GetWindowState()
        windowMode = mode.windowMode
        if windowMode != trinity.Tr2WindowMode.WINDOWED or mode.showState != trinity.Tr2WindowShowState.MINIMIZED:
            self.LogInfo('Saving device settings: ', mode)
            self._settings[windowMode] = mode
            _SaveStateSettings(self._settings[windowMode])
            gfxsettings.Set(gfxsettings.GFX_WINDOW_MODE, windowMode, False)
            self.settings.SaveSettings()
            for each in self._settings.values():
                trinity.mainWindow.StoreStateSettings(each)

    def _OnBeforeSwapChainChange(self, *args):
        ServiceManager.Instance().GetService('window').ProcessDeviceChange()

    def _OnWindowStateChange(self, *args):
        self._SaveSettings(trinity.mainWindow)
        with sentry_sdk.configure_scope() as scope:
            scope.set_tag('window_mode', 'fullscreen' if trinity.mainWindow.GetWindowState().windowMode == trinity.Tr2WindowMode.FULL_SCREEN else 'windowed')
        monolithsentry.set_sentry_crash_key()

    def _OnSwapChainChange(self, *args):
        ServiceManager.Instance().ScatterEvent('OnSetDevice')
        deviceSignals.on_set_device()
        if uicore.uilib:
            uicore.uilib.UpdateRootObjectSizes()
        ServiceManager.Instance().ScatterEvent('OnEndChangeDevice')
        deviceSignals.on_end_change_device()

    def ForceSize(self, width = 512, height = 512):
        trinity.mainWindow.SetMinimumSize(width, height)
        state = trinity.Tr2MainWindowState()
        state.windowMode = trinity.Tr2WindowMode.WINDOWED
        state.width = width
        state.height = height
        uthread.new(self._SetDevice, state)

    def CreateDevice(self):
        self.LogInfo('CreateDevice')
        if '/safemode' in blue.pyos.GetArg():
            self.SetToSafeMode()
        trinity.mainWindow.SetWindowTitle(GetWindowName())
        trinity.mainWindow.SetMinimumSize(*MINIMUM_WINDOW_SIZE)
        trinity.mainWindow.onBeforeSwapChainChange = self._OnBeforeSwapChainChange
        trinity.mainWindow.onWindowStateChange = self._OnWindowStateChange
        trinity.mainWindow.onSwapChainChange = self._OnSwapChainChange
        trinity.settings.SetValue('raytracingEnabled', False)
        trinity.settings.SetValue('newUpscalersEnabled', False)
        trinity.device.UpdateAvailableUpscalingTechniques()
        dev = trinity.device
        while not dev.DoesD3DDeviceExist():
            try:
                self.Initialize()
                dev.SetUpscaling(gfxsettings.Get(gfxsettings.GFX_UPSCALING_TECHNIQUE), gfxsettings.Get(gfxsettings.GFX_UPSCALING_SETTING), gfxsettings.Get(gfxsettings.GFX_FRAMEGENERATION_ENABLED))
                self._SetDevice(self._settings[gfxsettings.Get(gfxsettings.GFX_WINDOW_MODE, 0)])
                if not dev.DoesD3DDeviceExist():
                    blue.os.Pump()
                    time.sleep(0.5)
            except trinity.ALDeviceNotAvailable as e:
                sys.exc_clear()
                trinity.adapters.Refresh()

    def ResetMonitor(self):
        self._SetDevice(trinity.Tr2MainWindowState())

    def IsWindowed(self):
        return trinity.mainWindow.GetWindowState().windowMode != trinity.Tr2WindowMode.FULL_SCREEN

    def GetDefaultResolution(self, windowState):
        if windowState.windowMode != trinity.Tr2WindowMode.FULL_SCREEN or self._settings[windowState.windowMode].adapter == windowState.adapter:
            state = self._settings[windowState.windowMode].CopyTo()
        else:
            state = trinity.Tr2MainWindowState()
            state.windowMode = windowState.windowMode
            state.adapter = windowState.adapter
        trinity.mainWindow.SanitizeState(state)
        return (state.width, state.height)

    def GetPreferedResolution(self, windowed):
        if windowed:
            state = self._settings[trinity.Tr2WindowMode.WINDOWED].CopyTo()
        else:
            state = self._settings[trinity.Tr2WindowMode.FULL_SCREEN].CopyTo()
        trinity.mainWindow.SanitizeState(state)
        return (state.width, state.height)

    def ToggleWindowed(self):
        if trinity.mainWindow.GetWindowState().windowMode != trinity.Tr2WindowMode.WINDOWED:
            windowMode = trinity.Tr2WindowMode.WINDOWED
        else:
            windowMode = trinity.Tr2WindowMode.FULL_SCREEN
        self._SetDevice(self._settings[windowMode])
        ServiceManager.Instance().ScatterEvent('OnToggleWindowed', isWindowed=windowMode != 0)
        deviceSignals.on_toggle_windowed(windowMode != 0)

    def _SetDevice(self, state):
        dev = trinity.device
        dev.viewport.width = state.width
        dev.viewport.height = state.height
        while True:
            try:
                trinity.mainWindow.SetWindowState(state)
                break
            except trinity.ALDeviceLostError:
                blue.pyos.synchro.SleepWallclock(1000)

        return True

    def SetDevice(self, windowState):
        backup = trinity.mainWindow.GetWindowState().CopyTo()
        try:
            self._SetDevice(windowState)
        except:
            self._SetDevice(backup)
            return False

        newState = trinity.mainWindow.GetWindowState()
        if newState.windowMode == trinity.Tr2WindowMode.FULL_SCREEN and (newState.width != backup.width or newState.height != backup.height):
            self._AskForConfirmation(backup)

    def _AskForConfirmation(self, backup):
        loadingSvc = ServiceManager.Instance().GetService('loading')
        if hasattr(loadingSvc, 'CountDownWindow'):
            loadingSvc.CountDownWindow(localization.GetByLabel('/Carbon/UI/Service/Device/KeepDisplayChanges'), 15000, lambda *args: None, lambda *args: self._SetDevice(backup), inModalLayer=1)

    def GetSettings(self):
        return trinity.mainWindow.GetWindowState()

    def GetAdaptersEnumerated(self):
        options = []
        for i in range(trinity.adapters.GetAdapterCount()):
            identifier = trinity.adapters.GetAdapterInfo(i)
            identifierDesc = identifier.description.encode('ascii', 'ignore')
            identifierDesc += ' ' + str(i + 1)
            options.append((identifierDesc, i))

        return options

    def GetResolutionOptions(self, windowState):
        options = []
        for resolution in trinity.mainWindow.GetWindowSizeOptions(windowState.adapter, windowState.windowMode):
            options.append((localization.GetByLabel('/Carbon/UI/Service/Device/ScreenSize', width=resolution[0], height=resolution[1]), resolution))

        return options

    def GetPresentationIntervalOptions(self, windowMode):
        options = [(localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/Common/Off'), trinity.PRESENT_INTERVAL.IMMEDIATE), (localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/Common/On'), trinity.PRESENT_INTERVAL.ONE)]
        return options

    def SetResourceCacheSize(self):
        cacheSize = 128
        self.LogInfo('Setting resource cache size to', cacheSize, 'MB')
        MEG = 1048576
        finalSize = cacheSize * MEG
        blue.motherLode.maxMemUsage = finalSize
        return finalSize

    def SetToSafeMode(self):
        gfxsettings.Set(gfxsettings.GFX_TEXTURE_QUALITY, 2, pending=False)
        gfxsettings.Set(gfxsettings.GFX_SHADER_QUALITY, 1, pending=False)
        gfxsettings.Set(gfxsettings.GFX_POST_PROCESSING_QUALITY, 0, pending=False)
        gfxsettings.Set(gfxsettings.GFX_SHADOW_QUALITY, 0, pending=False)

    def _GetAppShaderModel(self):
        shaderQuality = gfxsettings.Get(gfxsettings.GFX_SHADER_QUALITY)
        return self.GetShaderModelForShaderQuality(shaderQuality)

    def _GetAppSettings(self):
        return gfxsettings.GetLodSettings()

    def _GetAppMipLevelSkipExclusionDirectories(self):
        return ['res:/UI/Texture']

    def RefreshSupportedAATypes(self, deviceSettings, formats, shaderModel = None):
        self._aaTypes = [gfxsettings.AA_QUALITY_DISABLED]
        self._aaTypes.append(gfxsettings.AA_QUALITY_TAA_LOW)
        self._aaTypes.append(gfxsettings.AA_QUALITY_TAA_MEDIUM)
        self._aaTypes.append(gfxsettings.AA_QUALITY_TAA_HIGH)

    def GetAntiAliasingLabel(self, aaQuality):
        aaLabels = {gfxsettings.AA_QUALITY_DISABLED: localization.GetByLabel('/Carbon/UI/Common/Disabled'),
         gfxsettings.AA_QUALITY_TAA_LOW: localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/Common/LowQuality'),
         gfxsettings.AA_QUALITY_TAA_MEDIUM: localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/Common/MediumQuality'),
         gfxsettings.AA_QUALITY_TAA_HIGH: localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/Common/HighQuality')}
        return aaLabels[aaQuality]

    def _GetCommonFormats(self, adapter):
        allFormats = (trinity.PIXEL_FORMAT.R16G16B16A16_FLOAT, trinity.PIXEL_FORMAT.B8G8R8X8_UNORM, trinity.PIXEL_FORMAT.B8G8R8A8_UNORM)
        return [ f for f in allFormats if trinity.adapters.SupportsRenderTargetFormat(adapter, f) ]

    def GetAntiAliasingOptions(self, deviceSettings, shaderModel = None):
        formats = self._GetCommonFormats(deviceSettings.adapter)
        self.RefreshSupportedAATypes(deviceSettings, formats, shaderModel)
        aaOptions = []
        for each in self._aaTypes:
            aaOptions.append((self.GetAntiAliasingLabel(each), each))

        return aaOptions

    def GetUIScalingOptions(self, windowed, height = None):
        if height is None:
            height = uicore.desktop.height
        options = [ (eveformat.percent(scale), scale) for scale in self.GetAllowedScaleValues(height) ]
        auto_scale_value = self.CapUIScaleValue(self._GetFallbackUIScale(windowed))
        auto_option = (localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/DisplaySetup/AutoUIScaleOption', scale=eveformat.percent(auto_scale_value)), uiconst.AUTO_UI_SCALE_OPTION_ID)
        options.insert(0, auto_option)
        return options

    def GetAllowedScaleValues(self, height = None):
        if height is None:
            height = uicore.desktop.height
        maxValue = max(height / float(MINIMUM_WINDOW_SIZE[1]), 1.0)
        allowed_values = [ value for value in SCALE_VALUES if value <= maxValue ]
        return allowed_values

    def CapUIScaleValue(self, checkValue):
        values = self.GetAllowedScaleValues(trinity.device.height)
        minScale = min(values)
        maxScale = max(values)
        return max(minScale, min(maxScale, checkValue))

    def SetupUIScaling(self):
        if not uicore.desktop:
            return
        windowed = self.IsWindowed()
        self.SetUIScaleValue(self.GetUIScaleValue(windowed), windowed)

    def SetUIScaleValue(self, scaleValue, windowed):
        self.LogInfo('SetUIScaleValue', scaleValue, 'windowed', windowed)
        capValue = self.CapUIScaleValue(scaleValue)
        self._SetUIScaleValue(capValue, windowed)
        if capValue != uicore.desktop.dpiScaling:
            PreUIScaleChange_DesktopLayout = capture_desktop_window_layout()
            oldValue = uicore.dpiScaling
            uicore.desktop.UpdateUIScaling(capValue, oldValue)
            self.LogInfo('SetUIScaleValue capValue', capValue)
            ServiceManager.Instance().ScatterEvent('OnUIScalingChange', (oldValue, capValue))
            apply_desktop_window_layout(PreUIScaleChange_DesktopLayout)
        else:
            self.LogInfo('SetUIScaleValue No Change')

    def _SetUIScaleValue(self, value, windowed):
        if windowed:
            gfxsettings.Set(gfxsettings.GFX_UI_SCALE_WINDOWED, value, pending=False)
        else:
            gfxsettings.Set(gfxsettings.GFX_UI_SCALE_FULLSCREEN, value, pending=False)

    def _GetFallbackUIScale(self, windowed):
        if trinity.mainWindow:
            state = trinity.mainWindow.GetWindowState()
            if windowed:
                try:
                    cm = trinity.adapters.GetCurrentDisplayMode(state.adapter)
                except trinity.ALError:
                    return 1.0

                height = cm.height
            else:
                height = state.height
            if height > 2160:
                return 2.0
            if height > 1800:
                return 1.5
            if height > 1440:
                return 1.25
            if height < 900:
                return 0.9
        return 1.0

    def GetUIScaleValue(self, windowed):
        fallback = self._GetFallbackUIScale(windowed)
        auto_ui_scale_setting_key = gfxsettings.GFX_UI_SCALE_WINDOWED_SET_AUTOMATICALLY if windowed else gfxsettings.GFX_UI_SCALE_FULLSCREEN_SET_AUTOMATICALLY
        auto = gfxsettings.Get(auto_ui_scale_setting_key)
        if auto:
            return fallback
        else:
            ui_scale_setting_key = gfxsettings.GFX_UI_SCALE_WINDOWED if windowed else gfxsettings.GFX_UI_SCALE_FULLSCREEN
            return gfxsettings.Get(ui_scale_setting_key, fallback)

    def ApplyTrinityUserSettings(self):
        effectsEnabled = gfxsettings.Get(gfxsettings.UI_EFFECTS_ENABLED)
        trailsEnabled = effectsEnabled and gfxsettings.Get(gfxsettings.UI_TRAILS_ENABLED)
        trinity.settings.SetValue('eveSpaceObjectTrailsEnabled', trailsEnabled)
