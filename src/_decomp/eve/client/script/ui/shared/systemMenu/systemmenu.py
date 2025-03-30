#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\systemMenu\systemmenu.py
import logging
import sys
import blue
import log
import telemetry
import carbon.client.script.sys.appUtils as appUtils
import carbonui
import eve.common.lib.appConst as const
import eveicon
import evespacemouse
import langutils
import localization
import monolithsentry
import trinity
import uthread
import uthread2
import utillib
from carbon.client.script.environment.AudioUtil import PlaySound
from carbon.common.script.sys.serviceConst import ROLE_QA, ROLEMASK_ELEVATEDPLAYER, ROLE_WORLDMOD
from carbon.common.script.sys.sessions import ThrottlePerSecond
from carbonui import Axis, AxisAlignment, TextColor, uiconst, Align, Density, ButtonVariant, const as uiconst, IdealSize
from carbonui.button.group import ButtonGroup, ButtonSizeMode, OverflowAlign
from carbonui.button.menu import MenuButton
from carbonui.control.button import Button
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.control.checkbox import Checkbox
from carbonui.control.combo import Combo
from carbonui.control.contextMenu.menuData import MenuData
from carbonui.control.layer import LayerCore
from carbonui.control.radioButton import RadioButton
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.decorative.blurredSceneUnderlay import BlurredSceneUnderlay
from carbonui.decorative.panelUnderlay import PanelUnderlay
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.line import Line
from carbonui.primitives.sprite import Sprite
from carbonui.text.settings import set_font_size_setting, is_new_font_size_options_enabled, FontSizeOption, get_default_font_size_setting, font_shadow_enabled_setting
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from carbonui.util import colorblind
from carbonui.util.colorBlindHuePalette import ColorBlindHuePalette
from carbonui.util.colorBlindHuePicker import ColorBlindHuePicker
from carbonui.util.various_unsorted import GetAttrs, SortListOfTuples
from carbonui.window.settings import WindowCompactModeSetting, window_compact_mode_default_setting, only_tint_active_window, WindowMarginModeOption, window_margin_mode
from characterSettingsStorage.characterSettingsConsts import DISABLE_EMERGENCY_WARP
from eve.client.script.ui.camera import cameraUtil
from eve.client.script.ui.control import eveEdit, eveScroll
from eve.client.script.ui.control.entries.button import ButtonEntry
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.eveLabel import Label
from eve.client.script.ui.control.message import QuickMessage
from eve.client.script.ui.control.themeColored import FillThemeColored
from eve.client.script.ui.control.treeData import TreeData
from eve.client.script.ui.control.treeViewEntry import TreeViewEntryHeader
from eve.client.script.ui.quickFilter import QuickFilterEdit
from eve.client.script.ui.services import uiColorSettings
from eve.client.script.ui.services.uiColorSettings import show_window_bg_blur_setting
from eve.client.script.ui.shared.mapView.settings import classic_map_enabled_setting
from eve.client.script.ui.shared.neocom.neocom.neocomUtil import IsInventoryBadgingEnabled, ToggleInventoryBadgingEnabledInClient
from eve.client.script.ui.shared.radialMenu.radialMenuSvc import RADIAL_MENU_EXPAND_DELAY_DEFAULT, RADIAL_MENU_EXPAND_DELAY_MIN, RADIAL_MENU_EXPAND_DELAY_MAX
from eve.client.script.ui.shared.systemMenu import systemMenuConst, optimizeSettings
from eve.client.script.ui.shared.systemMenu.cmdListEntry import CmdListEntry
from eve.client.script.ui.shared.systemMenu.colorTheme import ColorThemeContainer
from eve.client.script.ui.shared.systemMenu.customersatisficationcont import CustomerSatisficationCont
from eve.client.script.ui.shared.systemMenu.feature_preview.data import get_available_feature_previews
from eve.client.script.ui.shared.systemMenu.feature_preview.panel import FeaturePreviewsPanel
from eve.client.script.ui.shared.systemMenu.graphicsOptionsConst import shader_quality_options, texture_quality_options, lod_quality_options, shadow_quality_options, reflection_quality_options, ao_quality_options, post_processing_quality_options, upscaling_technique_options, upscaling_settings_options, volumetric_quality_options, windowed_options
from eve.client.script.ui.shared.systemMenu.systemMenuCombo import SystemMenuCombo
from eve.client.script.ui.shared.systemMenu.systemMenuConst import PANELID_ABOUTEVE, PANELID_AUDIO, PANELID_DISPLAY_AND_GRAPHICS, PANELID_FEATUREPREVIEW, PANELID_USERINTERFACE, PANELID_LANGUAGE, PANELID_RESETSETTINGS, PANELID_SHORTCUTS, LABEL_WIDTH, system_menu_selected_tab_setting, PANEL_IDS_SHORTCUTS, PANELID_GAMEPLAY, PANELID_CAMERA
from eve.client.script.ui.shared.systemMenu.systemMenuHeader import SystemMenuHeader
from eve.client.script.ui.shared.systemMenu.systemMenuSlider import SystemMenuSlider
from eve.client.script.ui.shared.systemMenu.theme.feature_flag import is_only_tint_active_window_setting_enabled
from eve.client.script.ui.tooltips.tooltipHandler import TOOLTIP_SETTINGS_GENERIC, TOOLTIP_SETTINGS_BRACKET, TOOLTIP_DELAY_GENERIC, TOOLTIP_DELAY_MIN, TOOLTIP_DELAY_MAX, TOOLTIP_DELAY_BRACKET
from eve.common.lib import appConst
from eve.common.script.sys import eveCfg
from eve.common.script.sys.eveCfg import IsControllingStructure
from evegraphics import settings as gfxsettings
from evegraphics.gamma import GammaSlider
from eveprefs import prefs, boot
from eveservices.menu import GetMenuService
from globalConfig.getFunctions import AllowCharacterLogoff
from localization import GetByLabel, formatters
from notifications.client.notificationSettings.notificationSettingHandler import NotificationSettingHandler
from storylines.client.airnpe import is_air_npe_focused, skip_air_npe
from trinity.sceneRenderJobSpace import CanSupportSsao
from chat.client.const import CHAT_MESSAGE_MODE_LABEL_PATH
from chat.client.chat_settings import default_compact_member_entries_setting, default_font_size_setting, default_light_background_setting, default_message_mode_setting, default_show_member_list_setting
WIDTH = 1024
logger = logging.getLogger(__name__)

class SystemMenu(LayerCore):
    __guid__ = 'form.SystemMenu'
    __nonpersistvars__ = []
    __notifyevents__ = ['OnEndChangeDevice', 'OnUIScalingChange', 'OnUIRefresh']
    isTopLevelWindow = True
    _suppressed = False
    _was_ui_visible = None

    def __init__(self, *args, **kwargs):
        super(SystemMenu, self).__init__(*args, **kwargs)
        self.windowState = None
        uiColorSettings.show_window_bg_blur_setting.on_change.connect(self.OnWindowBgBlurSetting)
        uiColorSettings.color_theme_by_ship_faction_setting.on_change.connect(self.OnColorThemeByShipFactionSetting)

    def OnColorThemeByShipFactionSetting(self, *args):
        self._RebuildUserInterfacePanel()
        sm.GetService('uiColor').SelectThemeFromShip()

    def OnUIScalingChange(self, change, *args):
        if uicore.layer.systemmenu.isopen:
            self.isAboutEveInited = False
            if self.messageEdit:
                self.messageEdit.Close()
        self._CheckApplyCameraOffset()

    def OnUIRefresh(self):
        self.CloseView()
        uicore.layer.systemmenu.OpenView()

    @telemetry.ZONE_METHOD
    def Reset(self):
        self.isUserInterfaceInited = False
        self.isGameplayInited = False
        self.isDisplayAndGraphicsInited = False
        self.isCameraPanelInited = False
        self.isAudioInited = False
        self.isResetSettingsInited = False
        self.isShortcutsInited = False
        self.isLanguageInited = False
        self.isAboutEveInited = False
        self.colorBlindModeChanged = False
        self.panelsByID = {}
        self.messageEdit = None
        self.fpsThread = None
        self.fpsText = None
        self.menuTreeData = TreeData()
        self.menuTreeData.on_selected.connect(self.OnMenuNodeSelected)
        self.menuTreeData.on_click.connect(self.OnMenuNodeClicked)
        self._experiments_panel = None
        self._suppressed = False
        self._background = None
        self.layerCont = None
        self.genericSysteMenu = None
        self.shortcutsFilterEdit = None
        self.closing = 0
        self.init_language = langutils.get_client_language()
        self.tempStuff = []

    def OnMenuNodeClicked(self, node):
        if node.IsLeaf():
            self.menuTreeData.DeselectAll()
            node.SetSelected()
        else:
            node.ToggleExpanded()

    def OnMenuNodeSelected(self, node, animate = True):
        self.ShowPanel(node.GetID())

    def ShowPanel(self, panel_id):
        panel = self.panelsByID.get(panel_id, None)
        for child in self.panelCont.children:
            if child == panel:
                child.Show()
            else:
                child.Hide()

        self.LoadPanel(panel_id)

    @telemetry.ZONE_METHOD
    def OnCloseView(self):
        sm.ScatterEvent('OnSettingsCloseStarted')
        if eve.session.userid:
            sm.GetService('ui').UnsuppressUI()
        if self.windowState:
            self.ApplyDeviceChanges()
        if getattr(self, 'optimizeWnd', None) is not None:
            self.optimizeWnd.Close()
        self.ApplyGraphicsSettings()
        sm.GetService('settings').SaveSettings()
        if session.userid is not None:
            sm.GetService('sceneManager').UpdateCameraOffset()
        if eve.session.charid:
            if sm.GetService('viewState').IsViewActive('starmap'):
                sm.GetService('starmap').UpdateRoute()
        sm.GetService('settings').LoadSettings()
        if self.fpsThread:
            self.fpsThread.kill()
            self.fpsThread = None
        self.Reset()
        sm.UnregisterNotify(self)

    @telemetry.ZONE_METHOD
    def OnOpenView(self, tabID = None, subTabID = None, **kwargs):
        sm.RegisterNotify(self)
        self.Reset()
        self.InitDeviceSettings()
        self.ReconstructLayout(tabID)
        sm.GetService('ui').SuppressUI(duration=0.1)
        animations.FadeTo(self.layerCont, 0.0, 1.0, duration=0.1)
        sm.ScatterEvent('OnSettingsOpened')
        if self.fpsText:
            self.fpsThread = uthread2.start_tasklet(self._UpdateFPSThread)

    def SelectMenuEntry(self, tabID):
        node = self.menuTreeData.GetChildByID(tabID or system_menu_selected_tab_setting.get())
        if node:
            node.SetSelected(animate=False)

    def _UpdateFPSThread(self):
        while not self.destroyed:
            self.fpsText.text = u'FPS: {:.1f}'.format(blue.os.fps)
            uthread2.Sleep(0.5)

    def ReconstructLayout(self, tabID = None):
        self.Flush()
        self.layerCont = Container(name='layerCont', parent=self)
        self.layerCont.cacheContents = True
        self.ConstructLayout()
        self.SelectMenuEntry(tabID)

    def ConstructBackground(self):
        self._background = BlurredSceneUnderlay(name='systemMenuBackground', bgParent=self.content, isInFocus=True)

    def suppress(self, show_ui = True):
        if not self._suppressed and not getattr(self, 'closing', False) and self.layerCont is not None:
            self._suppressed = True
            self._background.Hide()
            self.layerCont.opacity = 0.0
            self.layerCont.state = uiconst.UI_DISABLED
            if show_ui:
                sm.GetService('ui').UnsuppressUI()

    def unsuppress(self):
        if self._suppressed and not getattr(self, 'closing', False) and self.layerCont is not None:
            self._suppressed = False
            self._background.Show()
            self.layerCont.opacity = 1.0
            self.layerCont.state = uiconst.UI_PICKCHILDREN
            sm.GetService('ui').SuppressUI()

    def GetPanelData(self):
        if session.userid:
            panelData = [(PANELID_DISPLAY_AND_GRAPHICS, self.displayAndGraphicsPanel),
             (PANELID_CAMERA, self.cameraPanel),
             (PANELID_AUDIO, self.audioPanel),
             (PANELID_USERINTERFACE, self.userInterfacePanel),
             (PANELID_GAMEPLAY, self.gameplayPanel),
             (PANELID_SHORTCUTS, self.shortcutsPanel)]
            if get_available_feature_previews():
                panelData.append((PANELID_FEATUREPREVIEW, self.featurePreviewPanel))
            panelData.extend(((PANELID_RESETSETTINGS, self.resetSettingsPanel), (PANELID_LANGUAGE, self.languagePanel), (PANELID_ABOUTEVE, self.aboutEvePanel)))
            return panelData
        else:
            return ((PANELID_DISPLAY_AND_GRAPHICS, self.displayAndGraphicsPanel),
             (PANELID_AUDIO, self.audioPanel),
             (PANELID_USERINTERFACE, self.userInterfacePanel),
             (PANELID_RESETSETTINGS, self.resetSettingsPanel),
             (PANELID_ABOUTEVE, self.aboutEvePanel))

    def ConstructLayout(self):
        self.isElevatedUser = bool(session.role & ROLEMASK_ELEVATEDPLAYER)
        self.scalingCombo = None
        self.layerCont.Hide()
        sm.GetService('settings').LoadSettings()
        self.content = Container(name='content', parent=self.layerCont, align=Align.HORIZONTALLY_CENTERED, width=0.4, minWidth=WIDTH, maxWidth=IdealSize.SIZE_1200)
        self.topCont = Container(name='topCont', parent=self.content, align=uiconst.TOTOP, height=64)
        self.ConstructTopCont()
        self.bottomCont = Container(name='bottomCont', parent=self.content, align=uiconst.TOBOTTOM, height=96)
        FillThemeColored(bgParent=self.bottomCont, opacity=0.5)
        self.ConstructContent()
        self.ConstructBottomCont()
        self.ConstructPanels()
        self.ConstructBackground()
        if self.layerCont:
            self.layerCont.state = uiconst.UI_NORMAL
        self.gammaSlider = None

    def ConstructTopCont(self):
        FillThemeColored(bgParent=self.topCont, opacity=0.5)
        Line(parent=self.topCont, align=uiconst.TOBOTTOM, opacity=0.1)
        Sprite(parent=self.topCont, align=Align.CENTERLEFT, pos=(32, 0, 32, 32), texturePath='res:/UI/Texture/WindowIcons/settings.png')
        carbonui.TextHeadline(parent=self.topCont, align=Align.CENTERLEFT, left=68, text=localization.GetByLabel('UI/Common/Settings'))
        ButtonIcon(parent=self.topCont, align=uiconst.CENTERRIGHT, state=uiconst.UI_NORMAL, pos=(4, 0, 32, 32), iconSize=16, texturePath=eveicon.close, func=self.CloseMenuClick, idx=0)
        if session.userid:
            carbonui.TextDetail(text=GetByLabel('UI/SystemMenu/VersionInfo', version=boot.keyval['version'].split('=', 1)[1], build=boot.build), parent=self.layerCont, align=Align.TOPRIGHT, pos=(8, 8, 0, 0), color=TextColor.SECONDARY)
            self.fpsText = carbonui.TextDetail(parent=self.layerCont, align=Align.TOPLEFT, color=TextColor.SECONDARY, pos=(8, 8, 0, 0))

    def ConstructContent(self):
        self.centerCont = Container(name='centerCont', parent=self.content, padding=(16, 32, 32, 32), state=uiconst.UI_NORMAL)
        self.treeCont = ScrollContainer(name='treeCont', parent=self.centerCont, align=Align.TOLEFT, width=300)
        PanelUnderlay(bgParent=self.treeCont, padding=(-16, -32, 0, -32))
        self.panelCont = Container(name='panelCont', parent=self.centerCont, padLeft=32)
        self._CheckApplyCameraOffset()

    def ConstructPanels(self):
        self.languagePanel = ScrollContainer(name=PANELID_LANGUAGE, parent=self.panelCont, display=False)
        self.aboutEvePanel = Container(name=PANELID_ABOUTEVE, parent=self.panelCont, display=False)
        self.resetSettingsPanel = Container(name=PANELID_RESETSETTINGS, parent=self.panelCont, display=False)
        self.shortcutsPanel = Container(name=PANELID_SHORTCUTS, parent=self.panelCont, display=False)
        self.userInterfacePanel = ScrollContainer(name=PANELID_USERINTERFACE, parent=self.panelCont, display=False)
        self.gameplayPanel = ScrollContainer(name=PANELID_GAMEPLAY, parent=self.panelCont, display=False)
        self.audioPanel = ScrollContainer(name=PANELID_AUDIO, parent=self.panelCont, display=False)
        self.displayAndGraphicsPanel = ScrollContainer(name=PANELID_DISPLAY_AND_GRAPHICS, parent=self.panelCont, display=False)
        self.cameraPanel = ScrollContainer(name=PANELID_CAMERA, parent=self.panelCont, display=False)
        self.featurePreviewPanel = Container(name=PANELID_FEATUREPREVIEW, parent=self.panelCont, display=False)
        self.panelsByID = {PANELID_LANGUAGE: self.languagePanel,
         PANELID_ABOUTEVE: self.aboutEvePanel,
         PANELID_RESETSETTINGS: self.resetSettingsPanel,
         PANELID_SHORTCUTS: self.shortcutsPanel,
         PANELID_USERINTERFACE: self.userInterfacePanel,
         PANELID_GAMEPLAY: self.gameplayPanel,
         PANELID_AUDIO: self.audioPanel,
         PANELID_DISPLAY_AND_GRAPHICS: self.displayAndGraphicsPanel,
         PANELID_CAMERA: self.cameraPanel,
         PANELID_FEATUREPREVIEW: self.featurePreviewPanel}
        for panel_id in PANEL_IDS_SHORTCUTS:
            self.panelsByID[panel_id] = self.shortcutsPanel

        self.ConstructTreeView()

    def ConstructTreeView(self):
        self.ConstructTreeData()
        for node in self.menuTreeData.GetChildren():
            TreeViewEntryHeader(parent=self.treeCont, align=uiconst.TOTOP, data=node, iconColor=TextColor.SECONDARY)

    def ConstructTreeData(self):
        for panel_id, panel in self.GetPanelData():
            label = GetByLabel(systemMenuConst.NAME_BY_PANELID[panel_id])
            icon = systemMenuConst.ICON_BY_PANELID.get(panel_id, None)
            self.menuTreeData.AddNode(label=label, nodeID=panel_id, icon=icon)

        self.ConstructShortcutsTreeBranch()

    def ConstructShortcutsTreeBranch(self):
        shortcutsNode = self.menuTreeData.GetChildByID(PANELID_SHORTCUTS)
        if not shortcutsNode:
            return
        for panel_id in PANEL_IDS_SHORTCUTS:
            label = GetByLabel(systemMenuConst.NAME_BY_PANELID[panel_id])
            shortcutsNode.AddNode(label=label, nodeID=panel_id)

    def ConstructBottomCont(self):
        self.buttonGroup = ButtonGroup(name='mainButtonGroup', parent=ContainerAutoSize(parent=self.bottomCont, align=uiconst.TORIGHT), align=Align.CENTERRIGHT, padRight=16, button_alignment=AxisAlignment.END, button_size_mode=ButtonSizeMode.DYNAMIC, density=Density.EXPANDED, overflow_align=OverflowAlign.LEFT)
        self.ConstructBottomButtons()
        if bool(session.charid):
            CustomerSatisficationCont(parent=self.bottomCont, align=Align.TOALL, padding=(32, 0, 8, 0))

    def ConstructBottomButtons(self):
        if session.charid:
            if is_air_npe_focused():
                self.skipTutorialButton = self.buttonGroup.AddButton(label=GetByLabel('UI/SystemMenu/SkipTutorial'), func=self.SkipTutorial)
        self.buttonGroup.AddButton(label=GetByLabel('UI/SystemMenu/ReturnToGame'), func=self.CloseMenuClick)
        if session.userid:
            if eveCfg.InShipInSpace():
                if not sm.GetService('viewState').SafeLogoffInProgress():
                    label = GetByLabel('UI/Inflight/SafeLogoff')
                    hint = GetByLabel('UI/SystemMenu/SafeLogoffHint')
                    icon = 'res:/UI/Texture/classes/CSAT/logOut.png'
                    if not AllowCharacterLogoff(sm.GetService('machoNet')):
                        label = GetByLabel('UI/Inflight/SafeLogoff/SafeLogoffQuitGame')
                        hint = GetByLabel('UI/SystemMenu/SafeLogoffQuitGameHint')
                        icon = 'res:/UI/Texture/classes/CSAT/quitGame.png'
                    self.buttonGroup.AddButton(label=label, hint=hint, func=self.SafeLogoff, texturePath=icon)
            elif session.charid and AllowCharacterLogoff(sm.GetService('machoNet')):
                self.buttonGroup.AddButton(label=GetByLabel('UI/SystemMenu/LogOff'), hint=GetByLabel('UI/SystemMenu/LogOffHint'), func=self.LogoffBtnClick, texturePath='res:/UI/Texture/classes/CSAT/logOut.png')
        self.buttonGroup.AddButton(label=GetByLabel('UI/SystemMenu/QuitGame'), func=self.QuitBtnClick, texturePath='res:/UI/Texture/classes/CSAT/quitGame.png')

    def _CheckApplyCameraOffset(self):
        offset = sm.GetService('window').GetCameraOffsetSettingValue() / 100.0
        self.content.left = offset

    def SkipTutorial(self, *args):
        skip_air_npe('SkipTutorialOffer')
        if getattr(self, 'skipTutorialButton', None) and not self.skipTutorialButton.destroyed:
            self.skipTutorialButton.Close()
        uicore.cmd.OnEsc()

    def OnWindowBgBlurSetting(self, *args):
        self._RebuildUserInterfacePanel()

    def CloseMenuClick(self, *args):
        PlaySound(uiconst.SOUND_BUTTON_CLICK)
        uicore.cmd.OnEsc()

    def SafeLogoff(self, button, *args):
        if not eveCfg.InShipInSpace():
            button.Close()
        else:
            uicore.cmd.OnEsc()
            if AllowCharacterLogoff(sm.GetService('machoNet')):
                sm.GetService('cmd').CmdLogOff()
            else:
                GetMenuService().SafeLogoff()

    def LogoffBtnClick(self, *args):
        self.CloseMenuClick()
        sm.GetService('cmd').CmdLogOff()

    def LoadPanel(self, panel_id, *args):
        if panel_id == PANELID_DISPLAY_AND_GRAPHICS:
            self.LoadDisplayAndGraphics()
        elif panel_id == PANELID_CAMERA:
            self.LoadCameraPanel()
        elif panel_id == PANELID_AUDIO:
            self.LoadAudio()
        elif panel_id == PANELID_USERINTERFACE:
            self.LoadUserInterface()
        elif panel_id == PANELID_GAMEPLAY:
            self.LoadGameplay()
        elif panel_id == PANELID_SHORTCUTS:
            self.LoadShortcuts(systemMenuConst.PANELID_SHORTCUTS_GENERAL)
        elif panel_id in PANEL_IDS_SHORTCUTS:
            self.LoadShortcuts(panel_id)
        elif panel_id == PANELID_FEATUREPREVIEW:
            self.LoadFeaturePreview()
        elif panel_id == PANELID_RESETSETTINGS:
            self.LoadResetSettings()
        elif panel_id == PANELID_LANGUAGE:
            self.LoadLanguage()
        elif panel_id == PANELID_ABOUTEVE:
            self.LoadAboutEve()
        system_menu_selected_tab_setting.set(panel_id)
        uthread.new(uicore.registry.SetFocus, self.panelCont)

    def InitDeviceSettings(self):
        self.windowState = trinity.mainWindow.GetWindowState()
        self.uiScaleValue = self._GetSelectedUiScaleOption()

    def ConstructDisplaySettings(self, whatChanged = ''):
        deviceSvc = sm.GetService('device')
        windowState = trinity.mainWindow.GetWindowState()
        windowed = self.windowState.windowMode != trinity.Tr2WindowMode.FULL_SCREEN
        isMaximized = windowState.showState == trinity.Tr2WindowShowState.MAXIMIZED
        adapterOps = deviceSvc.GetAdaptersEnumerated()
        resolutionOps = deviceSvc.GetResolutionOptions(self.windowState)
        if (self.windowState.width, self.windowState.height) not in [ x[1] for x in resolutionOps ]:
            self.windowState.width, self.windowState.height = deviceSvc.GetDefaultResolution(self.windowState)
        scalingOps = deviceSvc.GetUIScalingOptions(windowed=windowed, height=self.windowState.height)
        SystemMenuHeader(parent=self.displayAndGraphicsPanel, padTop=0, text=GetByLabel('UI/SystemMenu/DisplayAndGraphics/DisplaySetup/Header'))
        SystemMenuCombo(parent=self.displayAndGraphicsPanel, name='Windowed', select=self.windowState.windowMode, label=GetByLabel('UI/SystemMenu/DisplayAndGraphics/DisplaySetup/WindowedOrFullscreen'), options=windowed_options, hint=GetByLabel('UI/SystemMenu/DisplayAndGraphics/DisplaySetup/WindowedOrFullscreenTooltip'), callback=self.OnWindowedOrFullscreenCombo)
        label = GetByLabel('UI/SystemMenu/DisplayAndGraphics/DisplaySetup/WindowSize') if windowed else GetByLabel('UI/SystemMenu/DisplayAndGraphics/DisplaySetup/AdapterResolution')
        hint = GetByLabel('UI/SystemMenu/DisplayAndGraphics/DisplaySetup/WindowSizeTooltip') if windowed else GetByLabel('UI/SystemMenu/DisplayAndGraphics/DisplaySetup/AdapterResolutionTooltip')
        combo = SystemMenuCombo(parent=self.displayAndGraphicsPanel, name='BackBufferSize', select=(self.windowState.width, self.windowState.height), label=label, options=resolutionOps, hint=hint, callback=self.OnResolutionCombo)
        if isMaximized and windowed:
            combo.Disable()
        SystemMenuCombo(parent=self.displayAndGraphicsPanel, name='UIScaling', select=self.uiScaleValue, label=GetByLabel('UI/SystemMenu/DisplayAndGraphics/DisplaySetup/UIScaling'), options=scalingOps, hint=GetByLabel('UI/SystemMenu/DisplayAndGraphics/DisplaySetup/UIScalingTooltip'), callback=self.OnUIScalingCombo)
        if len(adapterOps) > 1:
            SystemMenuCombo(parent=self.displayAndGraphicsPanel, name='Adapter', select=self.windowState.adapter, label=GetByLabel('UI/SystemMenu/DisplayAndGraphics/DisplaySetup/DisplayAdapter'), options=adapterOps, hint=GetByLabel('UI/SystemMenu/DisplayAndGraphics/DisplaySetup/DisplayAdapterTooltip'), callback=self.OnAdapterCombo)
        options = deviceSvc.GetPresentationIntervalOptions(self.windowState.windowMode)
        SystemMenuCombo(parent=self.displayAndGraphicsPanel, name='VSync', select=self.windowState.presentInterval, label=GetByLabel('UI/SystemMenu/DisplayAndGraphics/DisplaySetup/VSync'), options=options, hint=GetByLabel('UI/SystemMenu/DisplayAndGraphics/DisplaySetup/VSyncTooltip'), callback=self.OnVsyncCombo)
        self.CreateUpscalingMenu()

    def OnAdapterCombo(self, combo, *args):
        self.windowState.adapter = combo.GetValue()
        self.ApplyDeviceChanges()

    def OnUIScalingCombo(self, combo, *args):
        self.uiScaleValue = combo.GetValue()
        self.ApplyDeviceChanges()

    def OnResolutionCombo(self, combo, *args):
        width, height = combo.GetValue()
        self.windowState.width = width
        self.windowState.height = height
        self.ApplyDeviceChanges()

    def OnWindowedOrFullscreenCombo(self, combo, *args):
        self.ChangeWindowMode(combo.GetValue())
        self.ApplyDeviceChanges()

    def OnVsyncCombo(self, combo, *args):
        self.windowState.presentInterval = combo.GetValue()
        self.ApplyDeviceChanges()

    def LoadCameraPanel(self):
        if self.isCameraPanelInited:
            return
        SystemMenuHeader(parent=self.cameraPanel, text=GetByLabel('UI/SystemMenu/DisplayAndGraphics/CameraSettings/InSpaceCameraSettings'), padTop=0)
        self.ConstructSlider(self.cameraPanel, 'cameraSensitivitySlider', ('user', 'ui'), gfxsettings.GetDefault(gfxsettings.UI_CAMERA_SENSITIVITY), 'UI/SystemMenu/DisplayAndGraphics/CameraSettings/CameraSensitivity', (-5.0, 5.0), 120, 10, leftHint=GetByLabel('UI/SystemMenu/DisplayAndGraphics/CameraSettings/CameraSensitivitySlow'), rightHint=GetByLabel('UI/SystemMenu/DisplayAndGraphics/CameraSettings/CameraSensitivityFast'), hint=GetByLabel('UI/SystemMenu/DisplayAndGraphics/CameraSettings/CameraSensitivityTooltip'), increments=[0.0], snapToIncrements=False)
        self.ConstructSlider(self.cameraPanel, 'cameraInertiaSlider', ('user', 'ui'), gfxsettings.GetDefault(gfxsettings.UI_CAMERA_INERTIA), 'UI/SystemMenu/DisplayAndGraphics/CameraSettings/CameraInertia', (-3.0, 3.0), 120, 10, leftHint=GetByLabel('UI/SystemMenu/DisplayAndGraphics/CameraSettings/CameraInertiaSmooth'), rightHint=GetByLabel('UI/SystemMenu/DisplayAndGraphics/CameraSettings/CameraInertiaStiff'), hint=GetByLabel('UI/SystemMenu/DisplayAndGraphics/CameraSettings/CameraInertiaTooltip'), increments=[0.0], snapToIncrements=False)
        SystemMenuSlider(parent=self.cameraPanel, name='cameraOffset', config=('cameraOffset', ('user', 'ui'), gfxsettings.GetDefault(gfxsettings.UI_CAMERA_OFFSET)), minValue=-100, maxValue=100, label='UI/SystemMenu/DisplayAndGraphics/DisplaySetup/CameraCenter', hint=GetByLabel('UI/SystemMenu/DisplayAndGraphics/DisplaySetup/CameraCenterSliderTooltip'), minLabel=GetByLabel('UI/SystemMenu/DisplayAndGraphics/DisplaySetup/CameraCenterSliderLeft'), maxLabel=GetByLabel('UI/SystemMenu/DisplayAndGraphics/DisplaySetup/CameraCenterSliderRight'), increments=[0.0], snapToIncrements=False, callback=self.OnCameraOffsetSlider, getHintFunc=self.GetCameraOffsetHintText, on_dragging=self.OnCameraOffsetSliderDragged)
        self.ConstructCheckbox(self.cameraPanel, gfxsettings.GetSettingKey(gfxsettings.UI_CAMERA_SHAKE_ENABLED), None, gfxsettings.GetPendingOrCurrent(gfxsettings.UI_CAMERA_SHAKE_ENABLED), GetByLabel('UI/SystemMenu/DisplayAndGraphics/Effects/CameraShake'), None, None, GetByLabel('UI/SystemMenu/DisplayAndGraphics/Effects/CameraShakeTooltip'))
        self.ConstructCheckbox(self.cameraPanel, gfxsettings.GetSettingKey(gfxsettings.UI_CAMERA_BOBBING_ENABLED), None, gfxsettings.GetPendingOrCurrent(gfxsettings.UI_CAMERA_BOBBING_ENABLED), GetByLabel('UI/SystemMenu/DisplayAndGraphics/Effects/CameraBobbing'), None, None, GetByLabel('UI/SystemMenu/DisplayAndGraphics/Effects/CameraBobbingTooltip'))
        self.ConstructCheckbox(self.cameraPanel, gfxsettings.GetSettingKey(gfxsettings.UI_INVERT_CAMERA_ZOOM), None, gfxsettings.GetPendingOrCurrent(gfxsettings.UI_INVERT_CAMERA_ZOOM), GetByLabel('UI/SystemMenu/DisplayAndGraphics/Miscellaneous/InvertCameraZoom'), None, None, GetByLabel('UI/SystemMenu/DisplayAndGraphics/Miscellaneous/InvertCameraZoomTooltip'))
        self.ConstructCheckbox(self.cameraPanel, 'offsetUIwithCamera', ('user', 'ui'), gfxsettings.GetDefault(gfxsettings.UI_OFFSET_UI_WITH_CAMERA), GetByLabel('UI/SystemMenu/DisplayAndGraphics/DisplaySetup/OffsetUIWithCamera'), None, None, GetByLabel('UI/SystemMenu/DisplayAndGraphics/DisplaySetup/OffsetUIWithCameraTooltip'))
        self.ConstructCheckbox(self.cameraPanel, 'cameraDynamicMovement', ('user', 'ui'), gfxsettings.GetDefault(gfxsettings.UI_CAMERA_DYNAMIC_CAMERA_MOVEMENT), GetByLabel('UI/SystemMenu/DisplayAndGraphics/CameraSettings/CameraDynamicMovement'), None, None, GetByLabel('UI/SystemMenu/DisplayAndGraphics/CameraSettings/CameraDynamicMovementTooltip'))
        self.ConstructCheckbox(self.cameraPanel, 'cameraInvertY', ('user', 'ui'), gfxsettings.Get(gfxsettings.UI_CAMERA_INVERT_Y), GetByLabel('UI/SystemMenu/DisplayAndGraphics/DisplaySetup/IncarnaCamera/InvertY'), None, None, GetByLabel('UI/SystemMenu/DisplayAndGraphics/DisplaySetup/IncarnaCamera/InvertYTooltip'))
        self.isCameraPanelInited = True

    def ConstructSpaceMouseSettings(self, parent):
        self.ConstructHeader(parent, GetByLabel('UI/SystemMenu/DisplayAndGraphics/CameraSettings/SpaceMouse/Header'))
        self.ConstructSlider(parent, 'spaceMouseSpeed', ('user', 'ui'), gfxsettings.GetDefault(gfxsettings.UI_CAMERA_SPACEMOUSE_SPEED_COEFFICIENT), 'UI/SystemMenu/DisplayAndGraphics/CameraSettings/SpaceMouse/Speed', (0, 1), 120, leftHint=GetByLabel('UI/SystemMenu/DisplayAndGraphics/CameraSettings/SpaceMouse/SpeedMin'), rightHint=GetByLabel('UI/SystemMenu/DisplayAndGraphics/CameraSettings/SpaceMouse/SpeedMax'), hint=GetByLabel('UI/SystemMenu/DisplayAndGraphics/CameraSettings/SpaceMouse/SpeedTooltip'), increments=[0.5], snapToIncrements=False)
        self.ConstructSlider(parent, 'spaceMouseAcceleration', ('user', 'ui'), gfxsettings.GetDefault(gfxsettings.UI_CAMERA_SPACEMOUSE_ACCELERATION_COEFFICIENT), 'UI/SystemMenu/DisplayAndGraphics/CameraSettings/SpaceMouse/Acceleration', (0, 1), 120, leftHint=GetByLabel('UI/SystemMenu/DisplayAndGraphics/CameraSettings/SpaceMouse/AccelerationMin'), rightHint=GetByLabel('UI/SystemMenu/DisplayAndGraphics/CameraSettings/SpaceMouse/AccelerationMax'), hint=GetByLabel('UI/SystemMenu/DisplayAndGraphics/CameraSettings/SpaceMouse/AccelerationTooltip'), increments=[0.5], snapToIncrements=False)

    def ApplyDeviceChanges(self, *args):
        if not self.windowState:
            return
        device_service = sm.GetService('device')
        window_state = trinity.mainWindow.GetWindowState()
        self.windowState.left = window_state.left
        self.windowState.top = window_state.top
        device_service.SetDevice(self.windowState)
        windowed = self.windowState.windowMode != trinity.Tr2WindowMode.FULL_SCREEN
        auto_key = gfxsettings.GFX_UI_SCALE_WINDOWED_SET_AUTOMATICALLY if windowed else gfxsettings.GFX_UI_SCALE_FULLSCREEN_SET_AUTOMATICALLY
        is_auto_scale = self.uiScaleValue == uiconst.AUTO_UI_SCALE_OPTION_ID
        gfxsettings.Set(auto_key, is_auto_scale, pending=False)
        fallback_scale = device_service.GetUIScaleValue(self.windowState.windowMode)
        desired_scale = fallback_scale if is_auto_scale else self.uiScaleValue
        device_service.SetUIScaleValue(desired_scale, self.windowState.windowMode)

    def OnEndChangeDevice(self, *args):
        if not self.destroyed and self.isopen:
            self.windowState = trinity.mainWindow.GetWindowState()
            self._RebuildDisplayAndGraphicsPanel()
            self._CheckApplyCameraOffset()

    def ChangeWindowMode(self, windowed):
        deviceSvc = sm.GetService('device')
        self.uiScaleValue = deviceSvc.GetUIScaleValue(windowed)
        self.windowState.windowMode = windowed
        self.windowState.width, self.windowState.height = deviceSvc.GetDefaultResolution(self.windowState)

    def _GetSelectedUiScaleOption(self):
        windowed = self.windowState.windowMode != trinity.Tr2WindowMode.FULL_SCREEN
        key = gfxsettings.GFX_UI_SCALE_WINDOWED_SET_AUTOMATICALLY if windowed else gfxsettings.GFX_UI_SCALE_FULLSCREEN_SET_AUTOMATICALLY
        auto = gfxsettings.Get(key)
        if auto:
            return uiconst.AUTO_UI_SCALE_OPTION_ID
        else:
            return sm.GetService('device').GetUIScaleValue(windowed)

    def OnComboChange(self, combo, header, value, *args):
        setting_id = combo.name
        if setting_id == 'autoTargetBack':
            settings.user.ui.Set('autoTargetBack', value)
        elif setting_id == 'actionmenuBtn':
            settings.user.ui.Set('actionmenuBtn', value)
        elif setting_id == 'clientFontSize':
            set_font_size_setting(value)
        elif setting_id == 'dblClickUser':
            settings.user.ui.Set('dblClickUser', value)
        elif gfxsettings.GetSettingFromSettingKey(setting_id) is not None:
            setting = gfxsettings.GetSettingFromSettingKey(setting_id)
            gfxsettings.Set(setting, value)
        elif setting_id == 'pseudolocalizationPreset':
            self.SetPseudolocalizationSettingsByPreset(value)
            self.RefreshLanguage(allUI=False)
        elif setting_id == 'characterReplacementMethod':
            self.setCharacterReplacementMethod = value
            if value > 0:
                self.setSimulateTooltip = False
                self.RefreshLanguage(allUI=False)
        elif setting_id == 'localizationImportantNames':
            self.setImpNameSetting = value
            self.RefreshLanguage(allUI=False)

    def OnGraphicsSettingCombo(self, combo, *args):
        setting = gfxsettings.GetSettingFromSettingKey(combo.name)
        gfxsettings.Set(setting, combo.GetValue())
        self.ApplyGraphicsSettings()

    def OnGraphicsSettingComboWithRebuild(self, combo, *args):
        setting = gfxsettings.GetSettingFromSettingKey(combo.name)
        value = combo.GetValue()
        gfxsettings.Set(setting, value)
        self._RebuildDisplayAndGraphicsPanel()
        self.ApplyGraphicsSettings()

    def OnShaderQualityCombo(self, combo, *args):
        setting = gfxsettings.GetSettingFromSettingKey(combo.name)
        value = combo.GetValue()
        gfxsettings.Set(setting, value)
        if value == gfxsettings.SHADER_MODEL_LOW:
            gfxsettings.Set(gfxsettings.GFX_REFLECTION_QUALITY, gfxsettings.GFX_REFLECTION_QUALITY_OFF, pending=False)
            gfxsettings.Set(gfxsettings.GFX_AO_QUALITY, gfxsettings.GFX_AO_QUALITY_OFF, pending=False)
            gfxsettings.Set(gfxsettings.GFX_SHADOW_QUALITY, 0, pending=False)
        else:
            if gfxsettings.Get(gfxsettings.GFX_REFLECTION_QUALITY) == gfxsettings.GFX_REFLECTION_QUALITY_OFF:
                gfxsettings.SetDefault(gfxsettings.GFX_REFLECTION_QUALITY, pending=False)
            if gfxsettings.Get(gfxsettings.GFX_AO_QUALITY) == gfxsettings.GFX_AO_QUALITY_OFF:
                gfxsettings.SetDefault(gfxsettings.GFX_AO_QUALITY, pending=False)
            if gfxsettings.Get(gfxsettings.GFX_SHADOW_QUALITY) == 0:
                gfxsettings.SetDefault(gfxsettings.GFX_SHADOW_QUALITY, pending=False)
        self._RebuildDisplayAndGraphicsPanel()
        self.ApplyGraphicsSettings()

    def _RebuildDisplayAndGraphicsPanel(self):
        self.isDisplayAndGraphicsInited = False
        self.LoadDisplayAndGraphics()

    def __RebuildAudioPanel(self):
        if not self.isAudioInited:
            return
        self.isAudioInited = False
        self.LoadAudio()

    def LoadShortcuts(self, key = None):
        if self.shortcutsFilterEdit:
            self.shortcutsFilterEdit.Clear(docallback=False)
        self._ConstructShortcutsPanel()
        self._PopulateShortcutsScroll(key, filterText='')

    def RefreshShortcutsScroll(self):
        self._PopulateShortcutsScroll(filterText=self.shortcutsFilterEdit.GetValue())

    def _PopulateShortcutsScroll(self, key = None, filterText = ''):
        if key is None and not filterText:
            key = self.GetSelectedPanelID()
        scrolllist = []
        for c in uicore.cmd.commandMap.GetAllCommands():
            if key and c.category and c.category != key:
                continue
            if not uicore.cmd.IsCommandAllowed(c.name):
                continue
            data = utillib.KeyVal()
            data.cmdname = c.name
            hintList = []
            if filterText:
                tabPath = systemMenuConst.NAME_BY_PANELID.get(c.category, '')
                if tabPath:
                    hintList.append(GetByLabel('UI/SystemMenu/TabName', tabName=GetByLabel(tabPath)))
            if c.hint:
                hintList.append(GetByLabel(c.hint))
            if hintList:
                data.hint = '<br>'.join(hintList)
            description = c.GetDescription()
            if filterText and description.lower().find(filterText) < 0:
                continue
            data.context = uicore.cmd.GetCategoryContext(c.category)
            shortcutString = c.GetShortcutAsString() or GetByLabel('UI/SystemMenu/Shortcuts/NoShortcut')
            data.label = description + '<t>' + shortcutString
            data.locked = c.isLocked
            data.refreshcallback = self.RefreshShortcutsScroll
            data.vspace = 8
            scrolllist.append(GetFromClass(CmdListEntry, data))

        if filterText:
            noContentHint = GetByLabel('UI/SystemMenu/Shortcuts/NoShortcutsFoundWithFilter')
        else:
            noContentHint = ''
        self.shortcutsScroll.Load(contentList=scrolllist, headers=[GetByLabel('UI/SystemMenu/Shortcuts/Command'), GetByLabel('UI/SystemMenu/Shortcuts/Shortcut')], scrollTo=self.shortcutsScroll.GetScrollProportion(), noContentHint=noContentHint)

    def GetSelectedPanelID(self):
        selected_nodes = self.menuTreeData.GetSelected()
        if selected_nodes:
            return selected_nodes[0].GetID()

    def RestoreShortcuts(self, *args):
        if uicore.Message('ConfirmResetAllShortcuts', {}, uiconst.YESNO, uiconst.ID_YES) == uiconst.ID_YES:
            uicore.cmd.RestoreDefaults()
            self.LoadShortcuts()

    def ClearCommand(self, cmdName):
        uicore.cmd.ClearMappedCmd(cmdName)
        self.LoadShortcuts()

    def LoadFeaturePreview(self):
        if self._experiments_panel is None:
            if self.featurePreviewPanel:
                self._experiments_panel = FeaturePreviewsPanel(parent=self.featurePreviewPanel)

    def ShowExperimentalFeature(self, experiment_id):
        node = self.menuTreeData.GetChildByID(PANELID_FEATUREPREVIEW)
        if node:
            node.SetSelected()
        self.LoadFeaturePreview()
        uthread2.start_tasklet(self._experiments_panel.select_experiment, experiment_id)

    def LoadAboutEve(self):
        if self.isAboutEveInited:
            return
        self.messageEdit = eveEdit.Edit(parent=self.aboutEvePanel, padLeft=8, padRight=8, readonly=1)
        self.messageEdit.AllowResizeUpdates(0)
        html = GetByLabel('UI/SystemMenu/AboutEve/AboutEve', title=GetByLabel('UI/SystemMenu/AboutEve/ReleaseTitle'), subtitle='', version=boot.keyval['version'].split('=', 1)[1], build=boot.build, currentYear=blue.os.GetTimeParts(blue.os.GetTime())[0], EVECredits=GetByLabel('UI/SystemMenu/AboutEve/EVECredits'), VanguardCredits=GetByLabel('UI/SystemMenu/AboutEve/VanguardCredits'), CCPCredits=GetByLabel('UI/SystemMenu/AboutEve/CCPCredits'))
        self.messageEdit.LoadHTML(html)
        self.isAboutEveInited = 1

    def ValidateData(self, entries):
        valid = []
        for rec in entries:
            if rec[0] not in ('checkbox', 'combo', 'slider', 'button'):
                valid.append(rec)
                continue
            if eve.session.charid:
                valid.append(rec)
            elif len(rec) > 1:
                if rec[1] is None:
                    valid.append(rec)
                    continue
                _, prefsType, _ = rec[1]
                if type(prefsType) is tuple:
                    if prefsType[0] == 'char':
                        if eve.session.charid:
                            valid.append(rec)
                    elif prefsType[0] == 'user':
                        if eve.session.userid:
                            valid.append(rec)
                    else:
                        valid.append(rec)
                else:
                    valid.append(rec)

        return valid

    def ParseData(self, entries, parent, validateEntries = 1):
        if validateEntries:
            validEntries = self.ValidateData(entries)
            if not validEntries:
                return
        for rec in entries:
            if rec[0] == 'topcontainer':
                c = Container(name='container', align=uiconst.TOTOP, height=rec[1], parent=parent)
                if len(rec) > 2:
                    c.name = rec[2]
            elif rec[0] == 'button':
                self.ConstructButton(parent, *rec[1:])
            elif rec[0] == 'header':
                self.ConstructHeader(parent, *rec[1:])
            elif rec[0] == 'text':
                self.ConstructText(parent, *rec[1:])
            elif rec[0] == 'checkbox':
                self.ConstructCheckbox(parent, *(rec[1] + rec[2:]))
            elif rec[0] == 'combo':
                self.ConstructCombo(parent, *rec[1:])
            elif rec[0] == 'slider':
                self.ConstructSlider(parent, *(rec[1] + rec[2:]))
            elif rec[0] == 'element':
                self.AddElement(parent, rec[1])

    def ConstructButton(self, parent, btnName, label, func, hint = None):
        btnpar = ContainerAutoSize(name='buttonpar', parent=parent, align=uiconst.TOTOP, top=4)
        return Button(name=btnName, parent=btnpar, label=label, func=func, hint=hint)

    def ConstructHeader(self, parent, text):
        if len(parent.children) == 0:
            return SystemMenuHeader(parent=parent, text=text, padTop=0)
        else:
            return SystemMenuHeader(parent=parent, text=text)

    def ConstructText(self, parent, text, memberVarName = None):
        t = carbonui.TextBody(name='sysheader', text=text, parent=parent, align=uiconst.TOTOP, padTop=4, padBottom=4, state=uiconst.UI_NORMAL)
        if memberVarName:
            raise ValueError('dafuq: ', memberVarName)
        return t

    def ConstructCheckbox(self, parent, cfgName, prefsType, defaultValue, label, value = None, group = None, hint = None, focus = None, disabled = False, indent = 0):
        checked = int(self.GetSettingsValue(cfgName, prefsType, defaultValue))
        value = None
        if value is not None:
            checked = bool(checked == value)
        if prefsType == 'server_setting':
            prefsType = None
        if group:
            cb = RadioButton(text=label, parent=parent, settingsKey=cfgName, retval=value, checked=checked, groupname=group, callback=self.OnCheckBoxChange, settingsPath=prefsType, padLeft=indent, padBottom=4)
        else:
            cb = Checkbox(text=label, parent=parent, settingsKey=cfgName, checked=checked, callback=self.OnCheckBoxChange, settingsPath=prefsType, padLeft=indent, padBottom=4)
        if disabled:
            cb.Disable()
            cb.opacity = 0.5
        if focus:
            uicore.registry.SetFocus(cb)
        cb.sr.hint = hint
        self.tempStuff.append(cb)
        return cb

    def AddElement(self, parent, element):
        element.SetParent(parent)

    def ConstructSlider(self, parent, cfgName, prefsType, defaultValue, label, minAndMax, labelWidth = 0, step = None, leftHint = None, rightHint = None, disabled = False, height = 10, hint = None, increments = None, snapToIncrements = True):
        minVal, maxVal = minAndMax
        slider = SystemMenuSlider(parent=parent, name=cfgName, config=(cfgName, prefsType, defaultValue), minValue=minVal, maxValue=maxVal, label=label, hint=hint, labelWidth=labelWidth, minLabel=leftHint, maxLabel=rightHint, increments=increments, snapToIncrements=snapToIncrements, callback=self.OnSliderChanged, getHintFunc=self.GetSliderHint, on_dragging=self.OnSliderChanged, state=disabled)
        if disabled:
            slider.Disable()
            slider.opacity = 0.5
            slider.label.Disable()
            slider.label.opacity = 0.5
        return slider

    def ConstructCombo(self, parent, settings, label, options, labelleft = LABEL_WIDTH, hint = None, focus = None, isDisabled = False):
        cfgName, prefsType, defaultValue = settings
        if prefsType:
            defaultValue = self.GetSettingsValue(cfgName, prefsType, defaultValue)
        if cfgName == 'UIScaling':
            newValue = False
            for optionLabel, value in options:
                if defaultValue == value:
                    newValue = True

            if not newValue:
                defaultValue = options[-1][1]
        combo = SystemMenuCombo(label=label, parent=parent, options=options, name=cfgName, select=defaultValue, callback=self.OnComboChange, labelleft=labelleft, align=uiconst.TOTOP, hint=hint)
        if cfgName == 'UIScaling':
            self.scalingCombo = combo
        if focus:
            uicore.registry.SetFocus(combo)
        if isDisabled:
            combo.Disable()
        return combo

    def OnCameraOffsetSliderDragged(self, slider, *args):
        self.SetGfxSetting(gfxsettings.UI_CAMERA_OFFSET, slider.GetValue())

    def OnCameraOffsetSlider(self, slider, *args):
        self.SetGfxSetting(gfxsettings.UI_CAMERA_OFFSET, slider.GetValue())
        self._CheckApplyCameraOffset()

    def OnSetCameraInertiaSliderValue(self, value, *args):
        self.SetGfxSetting(gfxsettings.UI_CAMERA_INERTIA, value)

    def OnSetCameraSensitivitySliderValue(self, value, *args):
        self.SetGfxSetting(gfxsettings.UI_CAMERA_SENSITIVITY, value)

    def SetGfxSetting(self, settingName, value):
        oldValue = gfxsettings.Get(settingName)
        if oldValue != value:
            gfxsettings.Set(settingName, value, pending=False)
            sm.ScatterEvent('OnGraphicSettingsChanged', [settingName])

    def GetCameraOffsetHintText(self, slider):
        value = slider.GetValue()
        if value == 0:
            return GetByLabel('UI/SystemMenu/DisplayAndGraphics/DisplaySetup/CameraCenterSliderCenteredValue')
        elif value < 0:
            return GetByLabel('UI/SystemMenu/DisplayAndGraphics/DisplaySetup/CameraCenterSliderLeftValue', value=abs(int(value)))
        else:
            return GetByLabel('UI/SystemMenu/DisplayAndGraphics/DisplaySetup/CameraCenterSliderRightValue', value=abs(int(value)))

    def GetSettingsValue(self, cfgName, prefsType, defaultValue):
        if not prefsType:
            return defaultValue
        elif prefsType == 'server_setting':
            value = sm.GetService('characterSettings').Get(cfgName)
            return value or defaultValue
        else:
            return GetAttrs(settings, *prefsType).Get(cfgName, defaultValue)

    def _RebuildUserInterfacePanel(self):
        if self.destroyed:
            return
        self.isUserInterfaceInited = False
        self.userInterfacePanel.Flush()
        self.LoadUserInterface()

    def LoadUserInterface(self):
        if self.isUserInterfaceInited:
            return
        self.userInterfacePanel.Flush()
        SystemMenuHeader(parent=self.userInterfacePanel, padTop=0, text=GetByLabel('UI/SystemMenu/GeneralSettings/TextHeader'))
        menudata = self.ConstructColumn1MenuData()
        self.ParseData(entries=menudata, parent=self.userInterfacePanel, validateEntries=True)
        self.ConstructNotificationSection(self.userInterfacePanel)
        if evespacemouse.IsEnabled():
            self.ConstructSpaceMouseSettings(self.userInterfacePanel)
        self.ConstructAndAppendOptionalClientUpdate(self.userInterfacePanel)
        if session.charid:
            self.ConstructWindowAppearanceSection()
            self.ConstructColorThemeSection()
            self.AppendColorBlindnessConfiguration(self.userInterfacePanel)
        self.isUserInterfaceInited = True

    def LoadGameplay(self):
        if self.isGameplayInited:
            return
        self.gameplayPanel.Flush()
        data = self.ConstructInflightMenuData()
        self.ParseData(entries=data, parent=self.gameplayPanel, validateEntries=True)
        menu_data = self.ConstructDuelMenuData()
        self.ParseData(entries=menu_data, parent=self.gameplayPanel, validateEntries=True)
        self.ConstructMapSection(self.gameplayPanel)
        self.ConstructChatSettings(self.gameplayPanel)
        self.ConstructCrashesSection(self.gameplayPanel)
        cinematic_data = self.ConstructBoardingCinematicsMenuData()
        self.ParseData(entries=cinematic_data, parent=self.gameplayPanel, validateEntries=True)
        self.isGameplayInited = True

    def ConstructColorThemeSection(self):
        SystemMenuHeader(parent=self.userInterfacePanel, text=GetByLabel('UI/SystemMenu/GeneralSettings/ColorTheme'))
        if is_only_tint_active_window_setting_enabled():
            Checkbox(parent=self.userInterfacePanel, text=localization.GetByLabel('UI/SystemMenu/GeneralSettings/ColorTheme/OnlyTintActiveWindowSettingTitle'), setting=only_tint_active_window)
        Checkbox(parent=self.userInterfacePanel, setting=uiColorSettings.color_theme_by_ship_faction_setting, text=GetByLabel('UI/SystemMenu/GeneralSettings/General/ShipTheme'))
        self.AppendColorThemeSelection(self.userInterfacePanel)

    def ConstructWindowAppearanceSection(self):
        SystemMenuHeader(parent=self.userInterfacePanel, text=GetByLabel('UI/SystemMenu/GeneralSettings/WindowAppearance'))
        checkbox = Checkbox(parent=self.userInterfacePanel, setting=show_window_bg_blur_setting, text=GetByLabel('UI/SystemMenu/GeneralSettings/General/EnableWindowBlur'))
        shader_quality = gfxsettings.GetPendingOrCurrent(gfxsettings.GFX_SHADER_QUALITY)
        if shader_quality <= gfxsettings.SHADER_MODEL_LOW:
            checkbox.Disable()
            checkbox.hint = GetByLabel('UI/SystemMenu/GeneralSettings/WindowBlurDisabledHint')
        if show_window_bg_blur_setting.is_enabled():
            setting = uiColorSettings.window_transparency_setting
        else:
            setting = uiColorSettings.window_transparency_noblur_setting
        SystemMenuSlider(parent=self.userInterfacePanel, setting=setting, label='UI/SystemMenu/GeneralSettings/Transparency', minLabel=GetByLabel('UI/SystemMenu/DisplayAndGraphics/Common/Off'), maxLabel=GetByLabel('UI/SystemMenu/GeneralSettings/FullTransparency'))
        SystemMenuSlider(parent=self.userInterfacePanel, setting=uiColorSettings.window_transparency_light_mode_setting, label='UI/SystemMenu/GeneralSettings/TransparencyLightMode', minLabel=GetByLabel('UI/SystemMenu/DisplayAndGraphics/Common/Off'), maxLabel=GetByLabel('UI/SystemMenu/GeneralSettings/FullTransparency'))
        self._ConstructWindowMarginCombo(self.userInterfacePanel)
        Checkbox(parent=self.userInterfacePanel, align=uiconst.TOTOP, top=8, setting=window_compact_mode_default_setting, text=GetByLabel('UI/SystemMenu/GeneralSettings/Windows/WindowCompactModeDefaultCheckboxLabel'), hint=GetByLabel('UI/SystemMenu/GeneralSettings/Windows/WindowCompactModeDefaultCheckboxHint'))

    def LoadAudio(self):
        if self.isAudioInited:
            return
        self.audioPanel.Flush()
        audioSvc = sm.GetService('audio')
        enabled = audioSvc.IsActivated()
        turretSuppressed = audioSvc.GetTurretSuppression()
        oldJukeboxOverride = audioSvc.GetOldJukeboxOverride()
        useCombatMusic = audioSvc.GetCombatMusicUsage()
        SystemMenuHeader(parent=self.audioPanel, text=GetByLabel('UI/SystemMenu/AudioAndChat/AudioEngine/Header'), padTop=0)
        audioData = (('checkbox', ('audioEnabled', ('public', 'audio'), enabled), GetByLabel('UI/SystemMenu/AudioAndChat/AudioEngine/AudioEnabled')),
         ('checkbox', ('suppressTurret', ('public', 'audio'), turretSuppressed), GetByLabel('UI/SystemMenu/AudioAndChat/VolumeLevel/SuppressTurretSounds')),
         ('checkbox', ('overrideWithOldJukebox', ('public', 'audio'), oldJukeboxOverride), GetByLabel('UI/SystemMenu/AudioAndChat/AudioEngine/OldJukeboxOverride')),
         ('checkbox', ('useCombatMusic', ('public', 'audio'), useCombatMusic), GetByLabel('UI/SystemMenu/AudioAndChat/AudioEngine/UseCombatMusic')),
         ('header', GetByLabel('UI/SystemMenu/AudioAndChat/VolumeLevel/Header')))
        self.ParseData(audioData, self.audioPanel)
        self.ConstructSlider(self.audioPanel, 'masterVolume', ('public', 'audio'), 0.8, 'UI/SystemMenu/AudioAndChat/VolumeLevel/MasterLevel', (0.0, 1.0))
        self.ConstructSlider(self.audioPanel, 'eveampGain', ('public', 'audio'), 0.5, 'UI/SystemMenu/AudioAndChat/VolumeLevel/MusicLevel', (0.0, 1.0))
        self.ConstructSlider(self.audioPanel, 'uiGain', ('public', 'audio'), 0.5, 'UI/SystemMenu/AudioAndChat/VolumeLevel/UISoundLevel', (0.0, 1.0))
        self.ConstructSlider(self.audioPanel, 'evevoiceGain', ('public', 'audio'), 0.7, 'UI/SystemMenu/AudioAndChat/VolumeLevel/UIVoiceLevel', (0.0, 1.0))
        self.ConstructSlider(self.audioPanel, 'worldVolume', ('public', 'audio'), 0.7, 'UI/SystemMenu/AudioAndChat/VolumeLevel/WorldLevel', (0.0, 1.0))
        if not session.userid:
            self.isAudioInited = True
            return
        self.ConstructHeader(self.audioPanel, GetByLabel('UI/SystemMenu/AudioAndChat/AdvancedHeader'))
        advancedDisabled = not settings.user.audio.Get('soundLevel_advancedSettings', False)
        self.ConstructCheckbox(self.audioPanel, 'soundLevel_advancedSettings', ('user', 'audio'), False, GetByLabel('UI/SystemMenu/AudioAndChat/AudioEngine/AdvancedAudioSettings'), hint=GetByLabel('UI/SystemMenu/AudioAndChat/AudioEngine/AdvancedWarning'))
        advancedCont = ContainerAutoSize(name='advancedCont', parent=self.audioPanel, align=uiconst.TOTOP)
        audioSliderSetting = (('soundLevel_custom_atmosphere', 'UI/SystemMenu/AudioAndChat/AudioEngine/Atmosphere'),
         ('soundLevel_custom_jumpactivation', 'UI/SystemMenu/AudioAndChat/AudioEngine/JumpActivation'),
         ('soundLevel_custom_secondaryinterfaces', 'UI/SystemMenu/AudioAndChat/AudioEngine/SecondaryInterfaces'),
         ('soundLevel_custom_shipeffects', 'UI/SystemMenu/AudioAndChat/AudioEngine/ShipEffects'),
         ('soundLevel_custom_shipsounds', 'UI/SystemMenu/AudioAndChat/AudioEngine/ShipSounds'),
         ('soundLevel_custom_turrets', 'UI/SystemMenu/AudioAndChat/AudioEngine/Turrets'),
         ('soundLevel_custom_uiclick', 'UI/SystemMenu/AudioAndChat/AudioEngine/Uiclick'),
         ('soundLevel_custom_warningsfx', 'UI/SystemMenu/AudioAndChat/AudioEngine/WarningSounds'))
        for settingKey, messageLabel in audioSliderSetting:
            SystemMenuSlider(parent=advancedCont, name=settingKey, config=(settingKey, ('user', 'audio'), 0.5), minValue=0.0, maxValue=1.0, label=messageLabel, callback=self.OnSliderChanged, getHintFunc=self.GetSliderHint, on_dragging=self.OnSliderChanged)

        Container(parent=advancedCont, align=uiconst.TOTOP, height=4)
        if advancedDisabled:
            advancedCont.state = uiconst.UI_DISABLED
            advancedCont.opacity = 0.5
        advancedDisabled = not settings.user.audio.Get('inactiveSounds_advancedSettings', False)
        audioData2 = (('checkbox',
          ('inactiveSounds_advancedSettings', ('user', 'audio'), False),
          GetByLabel('UI/SystemMenu/AudioAndChat/AudioEngine/InactiveClientDampening'),
          None,
          None,
          GetByLabel('UI/SystemMenu/AudioAndChat/AudioEngine/InactiveInfo')),
         ('checkbox',
          ('inactiveSounds_master', ('user', 'audio'), False),
          GetByLabel('UI/SystemMenu/AudioAndChat/AudioEngine/InactiveClientMasterDampening'),
          None,
          None,
          None,
          None,
          advancedDisabled,
          8),
         ('checkbox',
          ('inactiveSounds_music', ('user', 'audio'), False),
          GetByLabel('UI/SystemMenu/AudioAndChat/AudioEngine/InactiveClientMusicDampening'),
          None,
          None,
          None,
          None,
          advancedDisabled,
          8),
         ('checkbox',
          ('inactiveSounds_turrets', ('user', 'audio'), False),
          GetByLabel('UI/SystemMenu/AudioAndChat/AudioEngine/InactiveClientTurretsDampening'),
          None,
          None,
          None,
          None,
          advancedDisabled,
          8),
         ('checkbox',
          ('inactiveSounds_shield', ('user', 'audio'), False),
          GetByLabel('UI/SystemMenu/AudioAndChat/AudioEngine/InactiveClientShieldDampening'),
          None,
          None,
          None,
          None,
          advancedDisabled,
          8),
         ('checkbox',
          ('inactiveSounds_armor', ('user', 'audio'), False),
          GetByLabel('UI/SystemMenu/AudioAndChat/AudioEngine/InactiveClientArmorDampening'),
          None,
          None,
          None,
          None,
          advancedDisabled,
          8),
         ('checkbox',
          ('inactiveSounds_hull', ('user', 'audio'), False),
          GetByLabel('UI/SystemMenu/AudioAndChat/AudioEngine/InactiveClientHullDampening'),
          None,
          None,
          None,
          None,
          advancedDisabled,
          8),
         ('checkbox',
          ('inactiveSounds_shipsound', ('user', 'audio'), False),
          GetByLabel('UI/SystemMenu/AudioAndChat/AudioEngine/InactiveClientShipsoundDampening'),
          None,
          None,
          None,
          None,
          advancedDisabled,
          8),
         ('checkbox',
          ('inactiveSounds_jumpgates', ('user', 'audio'), False),
          GetByLabel('UI/SystemMenu/AudioAndChat/AudioEngine/InactiveClientJumpgateDampening'),
          None,
          None,
          None,
          None,
          advancedDisabled,
          8),
         ('checkbox',
          ('inactiveSounds_wormholes', ('user', 'audio'), False),
          GetByLabel('UI/SystemMenu/AudioAndChat/AudioEngine/InactiveClientWormholeDampening'),
          None,
          None,
          None,
          None,
          advancedDisabled,
          8),
         ('checkbox',
          ('inactiveSounds_jumping', ('user', 'audio'), False),
          GetByLabel('UI/SystemMenu/AudioAndChat/AudioEngine/InactiveClientJumpingDampening'),
          None,
          None,
          None,
          None,
          advancedDisabled,
          8),
         ('checkbox',
          ('inactiveSounds_aura', ('user', 'audio'), False),
          GetByLabel('UI/SystemMenu/AudioAndChat/AudioEngine/InactiveClientAuraDampening'),
          None,
          None,
          None,
          None,
          advancedDisabled,
          8),
         ('checkbox',
          ('inactiveSounds_modules', ('user', 'audio'), False),
          GetByLabel('UI/SystemMenu/AudioAndChat/AudioEngine/InactiveClientModulesDampening'),
          None,
          None,
          None,
          None,
          advancedDisabled,
          8),
         ('checkbox',
          ('inactiveSounds_explosions', ('user', 'audio'), False),
          GetByLabel('UI/SystemMenu/AudioAndChat/AudioEngine/InactiveClientExplosionsDampening'),
          None,
          None,
          None,
          None,
          advancedDisabled,
          8),
         ('checkbox',
          ('inactiveSounds_warping', ('user', 'audio'), False),
          GetByLabel('UI/SystemMenu/AudioAndChat/AudioEngine/InactiveClientWarpingDampening'),
          None,
          None,
          None,
          None,
          advancedDisabled,
          8),
         ('checkbox',
          ('inactiveSounds_locking', ('user', 'audio'), False),
          GetByLabel('UI/SystemMenu/AudioAndChat/AudioEngine/InactiveClientLockingDampening'),
          None,
          None,
          None,
          None,
          advancedDisabled,
          8),
         ('checkbox',
          ('inactiveSounds_planets', ('user', 'audio'), False),
          GetByLabel('UI/SystemMenu/AudioAndChat/AudioEngine/InactiveClientPlanetsDampening'),
          None,
          None,
          None,
          None,
          advancedDisabled,
          8),
         ('checkbox',
          ('inactiveSounds_impacts', ('user', 'audio'), False),
          GetByLabel('UI/SystemMenu/AudioAndChat/AudioEngine/InactiveClientImpactsDampening'),
          None,
          None,
          None,
          None,
          advancedDisabled,
          8),
         ('checkbox',
          ('inactiveSounds_deployables', ('user', 'audio'), False),
          GetByLabel('UI/SystemMenu/AudioAndChat/AudioEngine/InactiveClientDeployablesDampening'),
          None,
          None,
          None,
          None,
          advancedDisabled,
          8),
         ('checkbox',
          ('inactiveSounds_boosters', ('user', 'audio'), False),
          GetByLabel('UI/SystemMenu/AudioAndChat/AudioEngine/InactiveClientBoostersDampening'),
          None,
          None,
          None,
          None,
          advancedDisabled,
          8),
         ('checkbox',
          ('inactiveSounds_stationint', ('user', 'audio'), False),
          GetByLabel('UI/SystemMenu/AudioAndChat/AudioEngine/InactiveClientStationIntDampening'),
          None,
          None,
          None,
          None,
          advancedDisabled,
          8),
         ('checkbox',
          ('inactiveSounds_stationext', ('user', 'audio'), False),
          GetByLabel('UI/SystemMenu/AudioAndChat/AudioEngine/InactiveClientStationExtDampening'),
          None,
          None,
          None,
          None,
          advancedDisabled,
          8),
         ('checkbox',
          ('inactiveSounds_structures', ('user', 'audio'), False),
          GetByLabel('UI/SystemMenu/AudioAndChat/AudioEngine/InactiveClientStructureDampening'),
          None,
          None,
          None,
          None,
          advancedDisabled,
          8))
        self.ParseData(audioData2, self.audioPanel)
        self.isAudioInited = True

    def ConstructChatSettings(self, parent):
        dblClickUserOps = [(GetByLabel('UI/Commands/ShowInfo'), 0), (GetByLabel('UI/Chat/StartConversation'), 1)]
        SystemMenuHeader(parent=parent, text=GetByLabel('UI/SystemMenu/AudioAndChat/Chat/Header'))
        if session.userid:
            self.ConstructCombo(parent=parent, settings=('dblClickUser', ('user', 'ui'), 0), label=GetByLabel('UI/SystemMenu/AudioAndChat/Chat/OnDoubleClick'), options=dblClickUserOps)
            self.ConstructCheckbox(parent, 'logchat', ('user', 'ui'), 1, GetByLabel('UI/SystemMenu/AudioAndChat/Chat/LogChatToFile'))
            self.ConstructCheckbox(parent, 'autoRejectInvitations', ('user', 'ui'), 0, GetByLabel('UI/SystemMenu/AudioAndChat/Chat/AutoRejectInvitations'))
        carbonui.TextBody(parent=parent, align=uiconst.TOTOP, padding=(0, 16, 0, 8), text=GetByLabel('UI/SystemMenu/AudioAndChat/ChatDefaultsSectionDescription'), color=TextColor.SECONDARY)
        Checkbox(parent=parent, align=uiconst.TOTOP, text=GetByLabel('UI/SystemMenu/AudioAndChat/ChatLightBackgroundOption'), setting=default_light_background_setting)
        Checkbox(parent=parent, align=uiconst.TOTOP, text=GetByLabel('UI/SystemMenu/AudioAndChat/ChatShowMemberListOption'), setting=default_show_member_list_setting)
        Checkbox(parent=parent, align=uiconst.TOTOP, text=GetByLabel('UI/SystemMenu/AudioAndChat/ChatCompactMembersOption'), setting=default_compact_member_entries_setting)

        def set_default_font_size(combo, text, value):
            default_font_size_setting.set(value)

        font_size_options = [ (str(x), x) for x in default_font_size_setting.options ]
        font_size_wrap = ContainerAutoSize(parent=parent, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, padding=(0, 8, 0, 8))
        carbonui.TextBody(parent=Container(parent=font_size_wrap, align=uiconst.TOLEFT, width=120, padRight=20), align=uiconst.CENTERLEFT, width=120, text=GetByLabel('UI/SystemMenu/AudioAndChat/ChatFontSizeOption'))
        Combo(parent=font_size_wrap, align=uiconst.TOTOP, options=font_size_options, select=default_font_size_setting.get(), callback=set_default_font_size)

        def set_message_mode(combo, text, value):
            default_message_mode_setting.set(value)

        message_mode_options = [ (localization.GetByLabel(CHAT_MESSAGE_MODE_LABEL_PATH[x]), x) for x in default_message_mode_setting.options ]
        message_mode_wrap = ContainerAutoSize(parent=parent, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, padding=(0, 4, 0, 8))
        carbonui.TextBody(parent=Container(parent=message_mode_wrap, align=uiconst.TOLEFT, width=120, padRight=20), align=uiconst.CENTERLEFT, width=120, text=GetByLabel('UI/SystemMenu/AudioAndChat/ChatMessagePortraitsOption'))
        Combo(parent=message_mode_wrap, align=uiconst.TOTOP, options=message_mode_options, select=default_message_mode_setting.get(), callback=set_message_mode)

    def LoadDisplayAndGraphics(self):
        if self.isDisplayAndGraphicsInited:
            return
        self.InitDeviceSettings()
        scrollPos = self.displayAndGraphicsPanel.GetPositionVertical()
        self.displayAndGraphicsPanel.Flush()
        self.ConstructDisplaySettings()
        self.ConstructGraphicsContentSettings()
        self.ConstructGraphicsButtons()
        if eve.session.userid:
            self.ConstructEffectsSettings()
            self.ConstructCharacterGraphicsSettings()
        uthread2.start_tasklet(self.displayAndGraphicsPanel.ScrollToVertical, scrollPos)
        self.isDisplayAndGraphicsInited = True

    def ConstructGraphicsContentSettings(self):
        deviceSvc = sm.GetService('device')
        SystemMenuHeader(parent=self.displayAndGraphicsPanel, text=GetByLabel('UI/SystemMenu/DisplayAndGraphics/GraphicContentSettings/Header'))
        carbonui.TextBody(parent=self.displayAndGraphicsPanel, align=uiconst.TOTOP, text=GetByLabel('UI/SystemMenu/DisplayAndGraphics/GraphicContentSettings/Description'), padBottom=8, color=TextColor.SECONDARY)
        isLowShaderModel = gfxsettings.GetPendingOrCurrent(gfxsettings.GFX_SHADER_QUALITY) == gfxsettings.SHADER_MODEL_LOW
        options = deviceSvc.GetAntiAliasingOptions(self.windowState, gfxsettings.GetPendingOrCurrent(gfxsettings.GFX_SHADER_QUALITY))
        availableAAQuality = map(lambda x: x[1], options)
        aaQuality = gfxsettings.GetPendingOrCurrent(gfxsettings.GFX_ANTI_ALIASING)
        if aaQuality not in availableAAQuality:
            gfxsettings.Set(gfxsettings.GFX_ANTI_ALIASING, gfxsettings.AA_QUALITY_DISABLED)
        upscalingInfo = trinity.device.GetUpscalingInfo()
        aaDisabled = upscalingInfo['temporal']
        selectedAAOption = gfxsettings.AA_QUALITY_DISABLED if aaDisabled else gfxsettings.GetPendingOrCurrent(gfxsettings.GFX_ANTI_ALIASING)
        aaMenu = SystemMenuCombo(parent=self.displayAndGraphicsPanel, name=gfxsettings.GetSettingKey(gfxsettings.GFX_ANTI_ALIASING), select=selectedAAOption, label=GetByLabel('UI/SystemMenu/DisplayAndGraphics/GraphicContentSettings/AntiAliasing'), options=options, hint=GetByLabel('UI/SystemMenu/DisplayAndGraphics/GraphicContentSettings/AntiAliasingTooltip'), callback=self.OnGraphicsSettingCombo)
        if aaDisabled:
            aaMenu.Disable()
        SystemMenuCombo(parent=self.displayAndGraphicsPanel, name=gfxsettings.GetSettingKey(gfxsettings.GFX_POST_PROCESSING_QUALITY), select=gfxsettings.GetPendingOrCurrent(gfxsettings.GFX_POST_PROCESSING_QUALITY), label=GetByLabel('UI/SystemMenu/DisplayAndGraphics/GraphicContentSettings/PostProcessing'), options=post_processing_quality_options, hint=GetByLabel('UI/SystemMenu/DisplayAndGraphics/GraphicContentSettings/PostProcessingTooltip'), callback=self.OnGraphicsSettingCombo)
        try:
            SystemMenuCombo(parent=self.displayAndGraphicsPanel, name=gfxsettings.GetSettingKey(gfxsettings.GFX_SHADER_QUALITY), select=gfxsettings.GetPendingOrCurrent(gfxsettings.GFX_SHADER_QUALITY), label=GetByLabel('UI/SystemMenu/DisplayAndGraphics/GraphicContentSettings/ShaderQuality'), options=shader_quality_options, hint=GetByLabel('UI/SystemMenu/DisplayAndGraphics/GraphicContentSettings/ShaderQualityTooltip'), callback=self.OnShaderQualityCombo)
        except:
            log.LogException()

        SystemMenuCombo(parent=self.displayAndGraphicsPanel, name=gfxsettings.GetSettingKey(gfxsettings.GFX_TEXTURE_QUALITY), select=gfxsettings.GetPendingOrCurrent(gfxsettings.GFX_TEXTURE_QUALITY), label=GetByLabel('UI/SystemMenu/DisplayAndGraphics/GraphicContentSettings/TextureQuality'), options=texture_quality_options, hint=GetByLabel('UI/SystemMenu/DisplayAndGraphics/GraphicContentSettings/TextureQualityTooltip'), callback=self.OnGraphicsSettingCombo)
        SystemMenuCombo(parent=self.displayAndGraphicsPanel, name=gfxsettings.GetSettingKey(gfxsettings.GFX_LOD_QUALITY), select=gfxsettings.GetPendingOrCurrent(gfxsettings.GFX_LOD_QUALITY), label=GetByLabel('UI/SystemMenu/DisplayAndGraphics/GraphicContentSettings/LODQuality'), options=lod_quality_options, hint=GetByLabel('UI/SystemMenu/DisplayAndGraphics/GraphicContentSettings/LODQualityTooltip'), callback=self.OnGraphicsSettingCombo)
        if isLowShaderModel:
            options = []
        else:
            options = list(shadow_quality_options)
            if not trinity.device.SupportsRaytracing():
                options.pop()
        combo = SystemMenuCombo(parent=self.displayAndGraphicsPanel, name=gfxsettings.GetSettingKey(gfxsettings.GFX_SHADOW_QUALITY), select=gfxsettings.GetPendingOrCurrent(gfxsettings.GFX_SHADOW_QUALITY) if options else None, label=GetByLabel('UI/SystemMenu/DisplayAndGraphics/GraphicContentSettings/ShadowQuality'), options=options, hint=GetByLabel('UI/SystemMenu/DisplayAndGraphics/GraphicContentSettings/ShadowQualityTooltip'), nothingSelectedText=GetByLabel('UI/SystemMenu/DisplayAndGraphics/Common/Disabled'), callback=self.OnGraphicsSettingCombo)
        if not options:
            combo.Disable()
        if not isLowShaderModel and CanSupportSsao():
            options = ao_quality_options
        else:
            options = []
        combo = SystemMenuCombo(parent=self.displayAndGraphicsPanel, name=gfxsettings.GetSettingKey(gfxsettings.GFX_AO_QUALITY), select=gfxsettings.GetPendingOrCurrent(gfxsettings.GFX_AO_QUALITY) if options else None, label=GetByLabel('UI/SystemMenu/DisplayAndGraphics/GraphicContentSettings/AOQuality'), options=options, nothingSelectedText=GetByLabel('UI/SystemMenu/DisplayAndGraphics/Common/Disabled'), hint=GetByLabel('UI/SystemMenu/DisplayAndGraphics/GraphicContentSettings/AOQualityTooltip'), callback=self.OnGraphicsSettingCombo)
        if not options:
            combo.Disable()
        SystemMenuCombo(parent=self.displayAndGraphicsPanel, name=gfxsettings.GetSettingKey(gfxsettings.GFX_VOLUMETRIC_QUALITY), select=gfxsettings.GetPendingOrCurrent(gfxsettings.GFX_VOLUMETRIC_QUALITY), label=GetByLabel('UI/SystemMenu/DisplayAndGraphics/GraphicContentSettings/VolumetricsQuality'), options=volumetric_quality_options, hint=GetByLabel('UI/SystemMenu/DisplayAndGraphics/GraphicContentSettings/VolumetricsQualityTooltip'), callback=self.OnGraphicsSettingCombo)
        if isLowShaderModel:
            options = []
        else:
            options = reflection_quality_options
        combo = SystemMenuCombo(parent=self.displayAndGraphicsPanel, name=gfxsettings.GetSettingKey(gfxsettings.GFX_REFLECTION_QUALITY), select=gfxsettings.GetPendingOrCurrent(gfxsettings.GFX_REFLECTION_QUALITY) if options else None, label=GetByLabel('UI/SystemMenu/DisplayAndGraphics/GraphicContentSettings/ReflectionQuality'), options=options, nothingSelectedText=GetByLabel('UI/SystemMenu/DisplayAndGraphics/Common/Disabled'), hint=GetByLabel('UI/SystemMenu/DisplayAndGraphics/GraphicContentSettings/ReflectionQualityTooltip'), callback=self.OnGraphicsSettingCombo)
        if not options:
            combo.Disable()

    def ConstructGraphicsButtons(self):
        btnGroup = ButtonGroup(name='bottomBtnPar', parent=self.displayAndGraphicsPanel, align=uiconst.TOTOP, padTop=32, orientation=Axis.HORIZONTAL, button_size_mode=ButtonSizeMode.EQUAL, button_alignment=AxisAlignment.START)
        btnGroup.AddButton(label=GetByLabel('UI/SystemMenu/DisplayAndGraphics/GraphicContentSettings/Brightness'), func=self.ChangeBrightness, hint=GetByLabel('UI/SystemMenu/DisplayAndGraphics/GraphicContentSettings/BrightnessToolTip'), texturePath=eveicon.polestar)
        MenuButton(parent=btnGroup, label=GetByLabel('UI/SystemMenu/DisplayAndGraphics/GraphicContentSettings/OptimizeSettings'), get_menu_func=self.GetOptimizeSettingsMenu, texturePath=eveicon.tune)
        btnGroup.AddButton(label=GetByLabel('UI/SystemMenu/DisplayAndGraphics/GraphicContentSettings/ResetGraphicSettings'), func=self.ResetGraphicsSettings, texturePath=eveicon.arrow_rotate_left)

    def GetOptimizeSettingsMenu(self):
        menuData = MenuData()
        for mode in optimizeSettings.OPTIMIZATION_MODES:
            menuData.AddEntry(GetByLabel(optimizeSettings.MODE_LABELS[mode]), func=lambda m = mode: self.ApplyOptimizeSettingsFunc(optimizeSettings.FUNC_BY_MODE[m]), hint=GetByLabel(optimizeSettings.MODE_INFO_LABELS[mode]))

        return menuData

    def ApplyOptimizeSettingsFunc(self, func):
        func()
        self.ApplyGraphicsSettings()
        self._RebuildDisplayAndGraphicsPanel()

    def ConstructCharacterGraphicsSettings(self):
        entries = []
        entries += (('header', GetByLabel('UI/SystemMenu/DisplayAndGraphics/CharacterCreation/Header')),)
        currentFastCharacterCreationValue = gfxsettings.GetPendingOrCurrent(gfxsettings.GFX_CHAR_FAST_CHARACTER_CREATION)
        charTextureQualityOptions = [(GetByLabel('UI/SystemMenu/DisplayAndGraphics/Common/LowQuality'), 2), (GetByLabel('UI/SystemMenu/DisplayAndGraphics/Common/MediumQuality'), 1), (GetByLabel('UI/SystemMenu/DisplayAndGraphics/Common/HighQuality'), 0)]
        entries += [('checkbox',
          (gfxsettings.GetSettingKey(gfxsettings.GFX_CHAR_FAST_CHARACTER_CREATION), None, currentFastCharacterCreationValue),
          GetByLabel('UI/SystemMenu/DisplayAndGraphics/CharacterCreation/LowQualityCharacters'),
          None,
          None,
          GetByLabel('UI/SystemMenu/DisplayAndGraphics/CharacterCreation/LowQualityCharactersTooltip'),
          None,
          False), ('checkbox',
          (gfxsettings.GetSettingKey(gfxsettings.UI_NCC_GREEN_SCREEN), None, gfxsettings.GetPendingOrCurrent(gfxsettings.UI_NCC_GREEN_SCREEN)),
          GetByLabel('UI/SystemMenu/DisplayAndGraphics/Miscellaneous/EnableGreenscreen'),
          None,
          None,
          GetByLabel('UI/SystemMenu/DisplayAndGraphics/Miscellaneous/EnableGreenscreenMenuTooltip')), ('combo',
          (gfxsettings.GetSettingKey(gfxsettings.GFX_CHAR_TEXTURE_QUALITY), None, gfxsettings.GetPendingOrCurrent(gfxsettings.GFX_CHAR_TEXTURE_QUALITY)),
          GetByLabel('UI/SystemMenu/DisplayAndGraphics/CharacterCreation/TextureQuality'),
          charTextureQualityOptions,
          LABEL_WIDTH,
          GetByLabel('UI/SystemMenu/DisplayAndGraphics/CharacterCreation/TextureQualityTooltip'))]
        self.ParseData(entries, self.displayAndGraphicsPanel, validateEntries=0)

    def ConstructEffectsSettings(self):
        entries = [('header', GetByLabel('UI/SystemMenu/DisplayAndGraphics/Effects/Header')),
         ('checkbox',
          (gfxsettings.GetSettingKey(gfxsettings.UI_TURRETS_ENABLED), None, gfxsettings.GetPendingOrCurrent(gfxsettings.UI_TURRETS_ENABLED)),
          GetByLabel('UI/SystemMenu/DisplayAndGraphics/Effects/TurretEffects'),
          None,
          None,
          GetByLabel('UI/SystemMenu/DisplayAndGraphics/Effects/TurretEffectsTooltip')),
         ('checkbox',
          (gfxsettings.GetSettingKey(gfxsettings.UI_EFFECTS_ENABLED), None, gfxsettings.GetPendingOrCurrent(gfxsettings.UI_EFFECTS_ENABLED)),
          GetByLabel('UI/SystemMenu/DisplayAndGraphics/Effects/Effects'),
          None,
          None,
          GetByLabel('UI/SystemMenu/DisplayAndGraphics/Effects/EffectsTooltip')),
         ('checkbox',
          (gfxsettings.GetSettingKey(gfxsettings.UI_MISSILES_ENABLED), None, gfxsettings.GetPendingOrCurrent(gfxsettings.UI_MISSILES_ENABLED)),
          GetByLabel('UI/SystemMenu/DisplayAndGraphics/Effects/MissileEffects'),
          None,
          None,
          GetByLabel('UI/SystemMenu/DisplayAndGraphics/Effects/EffectsTooltip')),
         ('checkbox',
          (gfxsettings.GetSettingKey(gfxsettings.UI_EXPLOSION_EFFECTS_ENABLED), None, gfxsettings.GetPendingOrCurrent(gfxsettings.UI_EXPLOSION_EFFECTS_ENABLED)),
          GetByLabel('UI/SystemMenu/DisplayAndGraphics/Effects/ShipExplosions'),
          None,
          None,
          GetByLabel('UI/SystemMenu/DisplayAndGraphics/Effects/ShipExplosionsTooltip')),
         ('checkbox',
          (gfxsettings.GetSettingKey(gfxsettings.UI_DRONE_MODELS_ENABLED), None, gfxsettings.GetPendingOrCurrent(gfxsettings.UI_DRONE_MODELS_ENABLED)),
          GetByLabel('UI/SystemMenu/DisplayAndGraphics/Effects/DroneModels'),
          None,
          None,
          GetByLabel('UI/SystemMenu/DisplayAndGraphics/Effects/DroneModelsTooltip')),
         ('checkbox',
          (gfxsettings.GetSettingKey(gfxsettings.UI_TRAILS_ENABLED), None, gfxsettings.GetPendingOrCurrent(gfxsettings.UI_TRAILS_ENABLED)),
          GetByLabel('UI/SystemMenu/DisplayAndGraphics/Effects/Trails'),
          None,
          None,
          GetByLabel('UI/SystemMenu/DisplayAndGraphics/Effects/TrailsTooltip')),
         ('checkbox',
          (gfxsettings.GetSettingKey(gfxsettings.UI_GPU_PARTICLES_ENABLED), None, gfxsettings.GetPendingOrCurrent(gfxsettings.UI_GPU_PARTICLES_ENABLED)),
          GetByLabel('UI/SystemMenu/DisplayAndGraphics/Effects/GPUParticles'),
          None,
          None,
          GetByLabel('UI/SystemMenu/DisplayAndGraphics/Effects/GPUParticlesTooltip')),
         ('checkbox',
          (gfxsettings.GetSettingKey(gfxsettings.UI_ASTEROID_ATMOSPHERICS), None, gfxsettings.GetPendingOrCurrent(gfxsettings.UI_ASTEROID_ATMOSPHERICS)),
          GetByLabel('UI/SystemMenu/DisplayAndGraphics/Effects/AsteroidEnvironments'),
          None,
          None,
          GetByLabel('UI/SystemMenu/DisplayAndGraphics/Effects/AsteroidEnvironmentsTooltip')),
         ('checkbox',
          (gfxsettings.GetSettingKey(gfxsettings.UI_MODELSKINSINSPACE_ENABLED), None, gfxsettings.GetPendingOrCurrent(gfxsettings.UI_MODELSKINSINSPACE_ENABLED)),
          GetByLabel('UI/SystemMenu/DisplayAndGraphics/Effects/InSpaceSkinningEffect'),
          None,
          None,
          GetByLabel('UI/SystemMenu/DisplayAndGraphics/Effects/InSpaceSkinningEffectToolTip')),
         ('checkbox',
          (gfxsettings.GetSettingKey(gfxsettings.GFX_DOF_POSTPROCESS_ENABLED), None, gfxsettings.GetPendingOrCurrent(gfxsettings.GFX_DOF_POSTPROCESS_ENABLED)),
          GetByLabel('UI/SystemMenu/DisplayAndGraphics/Effects/DepthOfField'),
          None,
          None,
          GetByLabel('UI/SystemMenu/DisplayAndGraphics/Effects/DepthOfFieldTooltip'))]
        self.ParseData(entries, self.displayAndGraphicsPanel, validateEntries=0)

    def CreateUpscalingMenu(self):
        supportedUpscalingTechniqueInfo = trinity.device.supportedUpscalingTechniques
        supportedUpscalingTechniques = [ info[0] for info in supportedUpscalingTechniqueInfo ] + [trinity.UPSCALING_TECHNIQUE.NONE]
        currentTechnique = gfxsettings.GetPendingOrCurrent(gfxsettings.GFX_UPSCALING_TECHNIQUE)
        currentTechniqueInfo = [ info for info in supportedUpscalingTechniqueInfo if info[0] == currentTechnique ]
        currentTechniqueInfo = currentTechniqueInfo[0] if currentTechniqueInfo else None
        frameGenSupported = False
        techniqueOptions = [ (label, technique) for label, technique in upscaling_technique_options if technique in supportedUpscalingTechniques ]
        if currentTechniqueInfo:
            settingOptions = [ (label, setting) for label, setting in upscaling_settings_options if setting & currentTechniqueInfo[1] == setting ]
            frameGenSupported = currentTechniqueInfo[2]
        else:
            settingOptions = [(GetByLabel('UI/Generic/NotAvailableShort'), 0)]
        SystemMenuCombo(parent=self.displayAndGraphicsPanel, name=gfxsettings.GetSettingKey(gfxsettings.GFX_UPSCALING_TECHNIQUE), select=gfxsettings.GetPendingOrCurrent(gfxsettings.GFX_UPSCALING_TECHNIQUE), label=GetByLabel('UI/SystemMenu/DisplayAndGraphics/GraphicContentSettings/Upscaling/Techniques/Label'), options=techniqueOptions, hint=GetByLabel('UI/SystemMenu/DisplayAndGraphics/GraphicContentSettings/Upscaling/Techniques/Tooltip'), callback=self.OnGraphicsSettingCombo)
        settingCombo = SystemMenuCombo(parent=self.displayAndGraphicsPanel, name=gfxsettings.GetSettingKey(gfxsettings.GFX_UPSCALING_SETTING), select=gfxsettings.GetPendingOrCurrent(gfxsettings.GFX_UPSCALING_SETTING), label=GetByLabel('UI/SystemMenu/DisplayAndGraphics/GraphicContentSettings/Upscaling/Settings/Label'), options=settingOptions, hint=GetByLabel('UI/SystemMenu/DisplayAndGraphics/GraphicContentSettings/Upscaling/Settings/Tooltip'), callback=self.OnGraphicsSettingCombo)
        if currentTechnique == trinity.UPSCALING_TECHNIQUE.NONE:
            settingCombo.Disable()
        if frameGenSupported:
            options = [(localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/Common/Off'), False), (localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/Common/On'), True)]
            SystemMenuCombo(parent=self.displayAndGraphicsPanel, name=gfxsettings.GetSettingKey(gfxsettings.GFX_FRAMEGENERATION_ENABLED), select=gfxsettings.GetPendingOrCurrent(gfxsettings.GFX_FRAMEGENERATION_ENABLED), label=GetByLabel('UI/SystemMenu/DisplayAndGraphics/GraphicContentSettings/Upscaling/FrameGeneration'), options=options, hint=GetByLabel('UI/SystemMenu/DisplayAndGraphics/GraphicContentSettings/Upscaling/FrameGenerationTooltip'), callback=self.OnGraphicsSettingCombo)

    def ResetGraphicsSettings(self, *args):
        gfxsettings.SetDefault(gfxsettings.GFX_POST_PROCESSING_QUALITY)
        gfxsettings.SetDefault(gfxsettings.GFX_TEXTURE_QUALITY)
        gfxsettings.SetDefault(gfxsettings.GFX_SHADER_QUALITY)
        gfxsettings.SetDefault(gfxsettings.GFX_LOD_QUALITY)
        gfxsettings.SetDefault(gfxsettings.GFX_CHAR_FAST_CHARACTER_CREATION)
        gfxsettings.SetDefault(gfxsettings.GFX_CHAR_TEXTURE_QUALITY)
        gfxsettings.SetDefault(gfxsettings.GFX_SHADOW_QUALITY)
        gfxsettings.SetDefault(gfxsettings.GFX_ANTI_ALIASING)
        gfxsettings.SetDefault(gfxsettings.GFX_BRIGHTNESS)
        gfxsettings.SetDefault(gfxsettings.GFX_UPSCALING_SETTING)
        gfxsettings.SetDefault(gfxsettings.GFX_UPSCALING_TECHNIQUE)
        gfxsettings.SetDefault(gfxsettings.GFX_AO_QUALITY)
        gfxsettings.SetDefault(gfxsettings.GFX_VOLUMETRIC_QUALITY)
        gfxsettings.SetDefault(gfxsettings.GFX_REFLECTION_QUALITY)
        if session.userid:
            gfxsettings.SetDefault(gfxsettings.UI_TURRETS_ENABLED)
            gfxsettings.SetDefault(gfxsettings.UI_EFFECTS_ENABLED)
            gfxsettings.SetDefault(gfxsettings.UI_MISSILES_ENABLED)
            gfxsettings.SetDefault(gfxsettings.UI_TRAILS_ENABLED)
            gfxsettings.SetDefault(gfxsettings.UI_ADVANCED_CAMERA)
            gfxsettings.SetDefault(gfxsettings.UI_NCC_GREEN_SCREEN)
            gfxsettings.SetDefault(gfxsettings.UI_CAMERA_OFFSET)
            gfxsettings.SetDefault(gfxsettings.UI_CAMERA_INVERT_Y)
            gfxsettings.SetDefault(gfxsettings.UI_CAMERA_INERTIA)
            gfxsettings.SetDefault(gfxsettings.UI_CAMERA_SENSITIVITY)
            gfxsettings.SetDefault(gfxsettings.UI_ASTEROID_ATMOSPHERICS)
            gfxsettings.SetDefault(gfxsettings.UI_MODELSKINSINSPACE_ENABLED)
        self.ApplyGraphicsSettings()
        self._RebuildDisplayAndGraphicsPanel()

    def ApplyGraphicsSettings(self):
        if not self.windowState:
            return
        deviceSvc = sm.GetService('device')
        dev = trinity.device
        changes = gfxsettings.ApplyPendingChanges(gfxsettings.SETTINGS_GROUP_DEVICE)
        if gfxsettings.IsInitialized(gfxsettings.SETTINGS_GROUP_UI):
            changes.extend(gfxsettings.ApplyPendingChanges(gfxsettings.SETTINGS_GROUP_UI))
        if gfxsettings.GFX_REFLECTION_QUALITY in changes:
            trinity.settings.SetValue('eveReflectionSetting', gfxsettings.Get(gfxsettings.GFX_REFLECTION_QUALITY))
        if gfxsettings.GFX_DOF_POSTPROCESS_ENABLED in changes:
            trinity.settings.SetValue('postprocessDofEnabled', gfxsettings.Get(gfxsettings.GFX_DOF_POSTPROCESS_ENABLED))
        lodChangers = [gfxsettings.GFX_LOD_QUALITY]
        if gfxsettings.GFX_LOD_QUALITY in changes:
            gfxsettings.ApplyLodSettings()
        if gfxsettings.GFX_SHADER_QUALITY in changes:
            message = QuickMessage(className='Message', parent=uicore.layer.modal, name='msgDeviceReset')
            message.ShowMsg(GetByLabel('UI/SystemMenu/DisplayAndGraphics/GraphicContentSettings/ApplyingSettings'))
            blue.synchro.SleepWallclock(200)
            trinity.SetShaderModel(deviceSvc.GetShaderModelForShaderQuality(gfxsettings.Get(gfxsettings.GFX_SHADER_QUALITY)))
            message.Close()
        if gfxsettings.GFX_TEXTURE_QUALITY in changes:
            dev.mipLevelSkipCount = gfxsettings.Get(gfxsettings.GFX_TEXTURE_QUALITY)
            dev.RefreshDeviceResources()
        if gfxsettings.GFX_UPSCALING_TECHNIQUE in changes or gfxsettings.GFX_UPSCALING_SETTING in changes or gfxsettings.GFX_FRAMEGENERATION_ENABLED in changes:
            trinity.device.SetUpscaling(gfxsettings.Get(gfxsettings.GFX_UPSCALING_TECHNIQUE), gfxsettings.Get(gfxsettings.GFX_UPSCALING_SETTING), gfxsettings.Get(gfxsettings.GFX_FRAMEGENERATION_ENABLED))
            if gfxsettings.GFX_UPSCALING_TECHNIQUE in changes:
                while trinity.device.GetUpscalingInfo()['technique'] != gfxsettings.Get(gfxsettings.GFX_UPSCALING_TECHNIQUE) or not trinity.device.DoesD3DDeviceExist():
                    blue.synchro.Yield()

                self._RebuildDisplayAndGraphicsPanel()
        if len(changes) > 0:
            sm.ScatterEvent('OnGraphicSettingsChanged', changes)
        monolithsentry.set_sentry_crash_key()

    def _ConstructShortcutsPanel(self):
        if self.isShortcutsInited:
            return
        self.shortcutsPanel.Flush()
        topCont = ContainerAutoSize(name='topCont', parent=self.shortcutsPanel, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, minHeight=QuickFilterEdit.default_height, padding=(0, 0, 0, 8))
        self.shortcutsFilterEdit = QuickFilterEdit(name='filterInput', parent=topCont, setvalue='', hintText=GetByLabel('UI/Inventory/Filter'), maxLength=64, left=16, width=160, align=uiconst.CENTERLEFT, OnClearFilter=self.LoadShortcuts)
        self.shortcutsFilterEdit.OnReturn = self.FilterCommands
        self.shortcutsFilterEdit.ReloadFunction = self.FilterCommands
        col2 = Container(name='column2', parent=self.shortcutsPanel)
        col2.isTabOrderGroup = 1
        shortcutoptions = Container(name='options', align=uiconst.TOBOTTOM, height=32, parent=col2, padding=(0, 16, 0, 0))
        ButtonGroup(parent=shortcutoptions, align=uiconst.TOTOP, button_alignment=AxisAlignment.START, buttons=[Button(label=GetByLabel('UI/SystemMenu/Shortcuts/EditShortcut'), func=self.OnEditShortcutBtnClicked, variant=ButtonVariant.GHOST), Button(label=GetByLabel('UI/SystemMenu/Shortcuts/ClearShortcut'), func=self.OnClearShortcutBtnClicked, variant=ButtonVariant.GHOST), Button(label=GetByLabel('UI/SystemMenu/Shortcuts/DefaultShortcuts'), func=self.RestoreShortcuts, variant=ButtonVariant.GHOST)])
        self.shortcutsScroll = eveScroll.Scroll(name='shortcutsScroll', align=uiconst.TOALL, parent=col2, multiSelect=False, id='active_cmdscroll', padding=(6, 0, 6, 0))
        self.isShortcutsInited = 1

    def FilterCommands(self):
        filterText = self.shortcutsFilterEdit.GetValue()
        filterText = filterText.strip().lower()
        self._PopulateShortcutsScroll(None, filterText)

    def OnEditShortcutBtnClicked(self, *args):
        selected = self.shortcutsScroll.GetSelected()
        if not selected:
            return
        p = selected[0].panel
        p.Edit()

    def OnClearShortcutBtnClicked(self, *args):
        selected = self.shortcutsScroll.GetSelected()
        if not selected:
            return
        self.ClearCommand(selected[0].cmdname)

    def LoadResetSettings(self, reload = 0):
        if self.isResetSettingsInited:
            return
        self.resetSettingsPanel.Flush()
        SystemMenuHeader(parent=self.resetSettingsPanel, padTop=0, text=GetByLabel('UI/SystemMenu/ResetSettings/ResetToDefault/Header'))
        suppressScroll = eveScroll.Scroll(parent=self.resetSettingsPanel, align=uiconst.TOTOP, name='defaultsResetScroll')
        suppressScroll.HideBackground()
        scrollList = []
        lst = [{'label': GetByLabel('UI/SystemMenu/ResetSettings/ResetToDefault/WindowPosition'),
          'caption': GetByLabel('UI/SystemMenu/ResetSettings/Reset'),
          'OnClick': self.ResetBtnClick,
          'args': 'windows'},
         {'label': GetByLabel('UI/SystemMenu/ResetSettings/ResetToDefault/WindowColors'),
          'caption': GetByLabel('UI/SystemMenu/ResetSettings/Reset'),
          'OnClick': self.ResetBtnClick,
          'args': 'window color'},
         {'label': GetByLabel('UI/SystemMenu/ResetSettings/ResetToDefault/WindowCompactMode'),
          'caption': GetByLabel('UI/SystemMenu/ResetSettings/Reset'),
          'OnClick': lambda button, args: WindowCompactModeSetting.clear_all(),
          'args': ()},
         {'label': GetByLabel('UI/SystemMenu/ResetSettings/ResetToDefault/ClearAllSettings'),
          'caption': GetByLabel('UI/SystemMenu/ResetSettings/Clear'),
          'OnClick': self.ResetBtnClick,
          'args': 'clear settings'},
         {'label': GetByLabel('UI/SystemMenu/ResetSettings/ResetToDefault/ClearAllCacheFiles'),
          'caption': GetByLabel('UI/SystemMenu/ResetSettings/Clear'),
          'OnClick': self.ResetBtnClick,
          'args': 'clear cache'}]
        if session.charid:
            lst.append({'label': GetByLabel('UI/SystemMenu/ResetSettings/ResetToDefault/ClearMailCache'),
             'caption': GetByLabel('UI/SystemMenu/ResetSettings/Clear'),
             'OnClick': self.ResetBtnClick,
             'args': 'clear mail'})
            lst.append({'label': GetByLabel('UI/SystemMenu/ResetSettings/ResetToDefault/NeocomButtons'),
             'caption': GetByLabel('UI/SystemMenu/ResetSettings/Reset'),
             'OnClick': self.ResetBtnClick,
             'args': 'reset neocom'})
            if eveCfg.InShipInSpace() or IsControllingStructure():
                lst.append({'label': GetByLabel('UI/SystemMenu/ResetSettings/ResetToDefault/ReloadHUD'),
                 'caption': GetByLabel('UI/SystemMenu/ResetSettings/ResetToDefault/ReloadHUDBtn'),
                 'OnClick': self.ReloadHUD,
                 'args': None})
        if sm.GetService('chat').has_reported_spammers():
            lst.append({'label': GetByLabel('UI/SystemMenu/ResetSettings/ResetToDefault/ClearISKSpammerList'),
             'caption': GetByLabel('UI/SystemMenu/ResetSettings/Clear'),
             'OnClick': self.ResetBtnClick,
             'args': 'clear iskspammers'})
        for each in lst:
            scrollList.append(GetFromClass(ButtonEntry, {'label': each['label'],
             'caption': each['caption'],
             'OnClick': each['OnClick'],
             'args': (each['args'],),
             'maxLines': None,
             'entryWidth': 600,
             'showHilite': True}))

        suppressScroll.Load(contentList=scrollList)
        suppressScroll.height = suppressScroll.GetEntriesTotalHeight()
        SystemMenuHeader(parent=self.resetSettingsPanel, text=GetByLabel('UI/SystemMenu/ResetSettings/ResetSuppressMessageSettings/Header'))
        suppressScroll = eveScroll.Scroll(name='suppressResetScroll', parent=self.resetSettingsPanel, align=uiconst.TOALL)
        suppressScroll.HideBackground()
        scrollList = []
        for each in settings.user.suppress.GetValues().keys():
            label = self.GetConfigName(each)
            entry = GetFromClass(ButtonEntry, {'label': label,
             'caption': GetByLabel('UI/SystemMenu/ResetSettings/Reset'),
             'OnClick': self.ConfigBtnClick,
             'args': (each,),
             'maxLines': None,
             'entryWidth': 600})
            scrollList.append((label, entry))

        scrollList = SortListOfTuples(scrollList)
        suppressScroll.Load(contentList=scrollList)
        self.isResetSettingsInited = 1

    def RefreshLanguage(self, allUI = True):
        self.isLanguageInited = 0
        if allUI:
            sm.ChainEvent('ProcessUIRefresh')
            sm.ScatterEvent('OnUIRefresh')
        else:
            self.languagePanel.Flush()
            self.isLanguageInited = 0
            self.LoadLanguage()

    def LoadLanguage(self):
        if self.isLanguageInited:
            return
        self._ShowLanguageSelectionOptions()
        self._ShowIMEAndVoiceOptions()
        self._ShowPseudolocOptions()
        self.isLanguageInited = 1

    def _GetLanguageMenuOptionList(self, includeHidden):
        returnSet = langutils.VALID_CLIENT_LANGUAGES
        if includeHidden:
            returnSet |= langutils.SECRET_CLIENT_LANGUAGES
        for l in returnSet:
            l.native = localization.Get('UI/SystemMenu/Language/Language%s' % l.name) or l.native

        return langutils.set_to_sorted_list(returnSet)

    def _ShowLanguageSelectionOptions(self):
        if boot.region == 'optic' and not self.isElevatedUser:
            return
        validLangs = self._GetLanguageMenuOptionList(includeHidden=self.isElevatedUser)
        if len(validLangs) > 1:
            SystemMenuHeader(parent=self.languagePanel, padTop=0, text=GetByLabel('UI/SystemMenu/Language/Header'))
            gameLanguage = langutils.get_client_language()
            selectedLang = langutils.any_to_comfy_language(getattr(self, 'setlanguageID', None), None) or gameLanguage
            for lang in validLangs:
                RadioButton(parent=self.languagePanel, name='languageCheckbox_%s' % lang.cerberus_code(), text=lang.native if lang == langutils.DEFAULT_CLIENT_LANGUAGE else u'%s - %s' % (lang.native, lang.name), retval=lang.mls_language_id(), groupname='languageSelection', checked=lang == selectedLang, fontsize=12, settingsKey='language', callback=self.OnLanguageCheckBoxChange)

            impNameOptions = [(selectedLang.native, 0), (GetByLabel('UI/SystemMenu/Language/EnglishReplacement'), localization.const.IMPORTANT_EN_OVERRIDE)]
            if selectedLang != langutils.LANG_EN:
                bs = localization.settings.bilingualSettings
                if not hasattr(self, 'setImpNameSetting'):
                    self.setImpNameSetting = bs.GetValue('localizationImportantNames')
                if not hasattr(self, 'setLanguageTooltip'):
                    self.setLanguageTooltip = bs.GetValue('languageTooltip')
                if not hasattr(self, 'setLocalizationHighlightImportant'):
                    self.setLocalizationHighlightImportant = bs.GetValue('localizationHighlightImportant')
                if self.setImpNameSetting == localization.const.IMPORTANT_EN_OVERRIDE:
                    checkboxCaption = GetByLabel('UI/SystemMenu/Language/ShowTooltipInLanguage', language=selectedLang.native)
                else:
                    checkboxCaption = GetByLabel('UI/SystemMenu/Language/ShowTooltipInLanguage', language=langutils.LANG_EN.native)
                highlightImportant = GetByLabel('UI/SystemMenu/Language/HighlightImportantNames')
                impNameData = [('header', GetByLabel('UI/SystemMenu/Language/ImportantNames')),
                 ('combo',
                  ('localizationImportantNames', None, self.setImpNameSetting),
                  GetByLabel('UI/SystemMenu/Language/Display'),
                  impNameOptions,
                  LABEL_WIDTH,
                  GetByLabel('UI/SystemMenu/Language/ImportantNamesExplanation')),
                 ('checkbox', ('languageTooltip', None, self.setLanguageTooltip), checkboxCaption),
                 ('checkbox', ('highlightImportant', None, self.setLocalizationHighlightImportant), highlightImportant)]
            else:
                impNameData = []
            self.ParseData(impNameData, self.languagePanel)
            buttonGroup = ButtonGroup(parent=self.languagePanel, align=uiconst.TOTOP, padTop=8, button_alignment=AxisAlignment.START)
            buttonGroup.AddButton(label=GetByLabel('UI/Common/Buttons/Apply'), func=self.ApplyLanguageSettings, variant=ButtonVariant.GHOST)

    def _ShowIMEAndVoiceOptions(self):
        columnData = [('header', GetByLabel('UI/SystemMenu/Language/VoiceOptions/Header')), ('checkbox', ('forceEnglishVoice', ('public', 'audio'), False), GetByLabel('UI/SystemMenu/Language/VoiceOptions/ForceEnglishVoice'))]
        self.ParseData(columnData, self.languagePanel)

    def _ShowPseudolocOptions(self):
        if session and session.charid and session.role & (ROLE_QA | ROLE_WORLDMOD):
            self.DisplayLocalizationQAOptions()
            self.DisplayPseudolocalizationSample()

    def DisplayLocalizationQAOptions(self):
        qaSettings = localization.settings.qaSettings
        if not hasattr(self, 'setShowMessageID'):
            self.setShowMessageID = qaSettings.GetValue('showMessageID')
        if not hasattr(self, 'setEnableBoundaryMarkers'):
            self.setEnableBoundaryMarkers = qaSettings.GetValue('enableBoundaryMarkers')
        if not hasattr(self, 'setShowHardcodedStrings'):
            self.setShowHardcodedStrings = qaSettings.GetValue('showHardcodedStrings')
        if not hasattr(self, 'setSimulateTooltip'):
            self.setSimulateTooltip = qaSettings.GetValue('simulateTooltip')
        if not hasattr(self, 'setEnableTextExpansion'):
            self.setEnableTextExpansion = qaSettings.GetValue('textExpansionAmount') > 0
        if not hasattr(self, 'setCharacterReplacementMethod'):
            self.setCharacterReplacementMethod = qaSettings.GetValue('characterReplacementMethod')
        if not hasattr(self, 'setTextExpansionAmount'):
            self.setTextExpansionAmount = qaSettings.GetValue('textExpansionAmount')
        localizationQAOptions = [('header', 'Localization QA Options'),
         ('checkbox', ('simulateTooltip', None, self.setSimulateTooltip), 'Simulate Tooltip (cancels other options)'),
         ('checkbox', ('showMessageID', None, self.setShowMessageID), 'Show MessageID'),
         ('checkbox', ('enableBoundaryMarkers', None, self.setEnableBoundaryMarkers), 'Show Boundary Markers'),
         ('checkbox', ('showHardcodedStrings', None, self.setShowHardcodedStrings), 'Show Hardcoded Strings')]
        if localization.IsPrimaryLanguage(localization.util.GetLanguageID()):
            conversionMethodOptions = [('&lt; Select &gt;', -1),
             ('No Simulation', 0),
             ('Simulate German', 1),
             ('Simulate Russian', 2),
             ('Simulate Japanese', 3)]
            if not hasattr(self, 'chosenPseudolocPreset'):
                self.chosenPseudolocPreset = -1
            localizationQAOptions += [('combo',
              ('pseudolocalizationPreset', None, self.chosenPseudolocPreset),
              'Simulation Preset',
              conversionMethodOptions,
              LABEL_WIDTH,
              'Simulation presets auto-configure the pseudolocalization settings to test for common localization issues.')]
            replacementMethodOptions = [('No Replacement', localization.settings.qaSettings.NO_REPLACEMENT),
             ('Diacritic Replacement', localization.settings.qaSettings.DIACRITIC_REPLACEMENT),
             ('Cyrillic Replacement', localization.settings.qaSettings.CYRILLIC_REPLACEMENT),
             ('Full-Width Replacement', localization.settings.qaSettings.FULL_WIDTH_REPLACEMENT)]
            localizationQAOptions += [('header', 'Localization QA: Advanced Settings'), ('combo',
              ('characterReplacementMethod', None, self.setCharacterReplacementMethod),
              'Char. Replacement',
              replacementMethodOptions,
              LABEL_WIDTH,
              'The character replacement method allows you to test for specific character rendering issues.'), ('checkbox', ('enableTextExpansion', None, self.setEnableTextExpansion), 'Text Expansion Enabled')]
            self.ParseData(localizationQAOptions, self.languagePanel)
            if self.setEnableTextExpansion:
                self.ConstructSlider(self.languagePanel, 'textExpansionAmount', None, self.setTextExpansionAmount, 'UI/SystemMenu/Language/LocalizationQAAdvanced/TextExpansion', (0.0, 0.5))
        buttonGroup = ButtonGroup(parent=self.languagePanel, align=uiconst.TOTOP, padTop=8, button_alignment=AxisAlignment.START)
        buttonGroup.AddButton(label='Apply QA Settings', func=self.ApplyQALanguageSettings, variant=ButtonVariant.GHOST)

    def DisplayPseudolocalizationSample(self):
        if session.languageID == 'EN':
            pseudolocalizationSample = [('header', 'Localization QA: Sample Text')]
            self.ParseData(pseudolocalizationSample, self.languagePanel, validateEntries=0)
            self.pseudolocalizedSampleTextLabel = carbonui.TextBody(name='pseudolocSample', text=GetByLabel('UI/SystemMenu/SampleText'), parent=self.languagePanel, align=uiconst.TOTOP, padTop=2, padBottom=2, state=uiconst.UI_NORMAL)

    def SetPseudolocalizationSettingsByPreset(self, presetValue):
        self.chosenPseudolocPreset = presetValue
        if presetValue == 0:
            self.setCharacterReplacementMethod = localization.settings.qaSettings.NO_REPLACEMENT
            self.setEnableTextExpansion = 0
            self.setTextExpansionAmount = 0.0
        elif presetValue == 1:
            self.setCharacterReplacementMethod = localization.settings.qaSettings.DIACRITIC_REPLACEMENT
            self.setEnableTextExpansion = True
            self.setTextExpansionAmount = 0.15
            self.setSimulateTooltip = False
        elif presetValue == 2:
            self.setCharacterReplacementMethod = localization.settings.qaSettings.CYRILLIC_REPLACEMENT
            self.setEnableTextExpansion = True
            self.setTextExpansionAmount = 0.05
            self.setSimulateTooltip = False
        elif presetValue == 3:
            self.setCharacterReplacementMethod = localization.settings.qaSettings.FULL_WIDTH_REPLACEMENT
            self.setEnableTextExpansion = False
            self.setTextExpansionAmount = 0.0
            self.setSimulateTooltip = False

    def FindColorFromName(self, findColor, colors):
        for colorName, color in colors:
            if colorName == findColor:
                return color

    def GetSliderHint(self, slider):
        value = slider.GetValue()
        if slider.name.startswith('wnd_'):
            return localization.formatters.FormatNumeric(int(value * 255))
        elif slider.name == 'cameraSensitivitySlider':
            return self.GetCameraSensitivityHintText(value)
        elif slider.name in ('cameraInertiaSlider',
         'actionMenuExpandTime',
         TOOLTIP_SETTINGS_GENERIC,
         TOOLTIP_SETTINGS_BRACKET):
            return ''
        else:
            return localization.formatters.FormatNumeric(int(value * 100))

    def GetCameraSensitivityHintText(self, value):
        return '%.2f' % cameraUtil.GetCameraSensitivityMultiplier()

    def OnSliderChanged(self, slider):
        idname = slider.name
        value = slider.GetValue()
        if idname.startswith('soundLevel_'):
            return self.GetSoundlevelSliderValue(idname, value)
        if idname == 'eveampGain':
            sm.GetService('audio').UserSetAmpVolume(value)
        elif idname == 'masterVolume':
            sm.GetService('audio').SetMasterVolume(value, persist=False)
        elif idname == 'uiGain':
            sm.GetService('audio').SetUIVolume(value, persist=False)
        elif idname == 'worldVolume':
            sm.GetService('audio').SetWorldVolume(value, persist=False)
        elif idname == 'evevoiceGain':
            sm.GetService('audio').SetVoiceVolume(value, persist=False)
        elif idname == 'cameraSensitivitySlider':
            self.OnSetCameraSensitivitySliderValue(value)
        elif idname == 'cameraInertiaSlider':
            self.OnSetCameraInertiaSliderValue(value)
        elif idname == 'textExpansionAmount':
            self.setTextExpansionAmount = value
            localization.settings.qaSettings.SetValue('textExpansionAmount', value)

    def ChangeBrightness(self, *args, **kwargs):
        self.gammaSlider = GammaSlider()

    def GetSoundlevelSliderValue(self, idname, value):
        settingName = idname.replace('soundLevel_', '')
        if self.isAudioInited:
            sm.GetService('audio').SetCustomValue(value, settingName, persist=True)

    def OnInactiveSoundsChange(self, configName, checkbox):
        if configName == 'inactiveSounds_advancedSettings':
            settings.user.audio.Set('inactiveSounds_advancedSettings', checkbox.checked)
            self.__RebuildAudioPanel()
            return
        sm.GetService('audio').SetDampeningValueSetting(configName, setOn=checkbox.checked)

    def OnLanguageCheckBoxChange(self, checkbox):
        if self.isElevatedUser:
            selectedLang = langutils.any_to_comfy_language(checkbox.GetReturnValue())
        else:
            selectedLang = langutils.client_valid_or_default(checkbox.GetReturnValue())
        setattr(self, 'setlanguageID', selectedLang.mls_language_id())
        self.RefreshLanguage(allUI=False)

    def OnCheckBoxChange(self, checkbox):
        if checkbox.GetSettingsPath() is None:
            if checkbox.GetSettingsKey() == const.autoRejectDuelSettingsKey:
                sm.GetService('characterSettings').Save(const.autoRejectDuelSettingsKey, str(int(checkbox.checked)))
            elif checkbox.GetSettingsKey() == DISABLE_EMERGENCY_WARP:
                sm.GetService('characterSettings').Save(DISABLE_EMERGENCY_WARP, str(int(checkbox.checked)))
        if checkbox.GetSettingsKey():
            config = checkbox.GetSettingsKey()
            if config.startswith('inactiveSounds_'):
                return self.OnInactiveSoundsChange(config, checkbox)
            if config == 'offsetUIwithCamera':
                sm.ScatterEvent('OnUIoffsetChanged')
                self._CheckApplyCameraOffset()
            elif config == 'languageTooltip':
                self.setLanguageTooltip = checkbox.checked
            elif config == 'highlightImportant':
                self.setLocalizationHighlightImportant = checkbox.checked
            elif config == 'audioEnabled':
                if checkbox.checked:
                    sm.GetService('audio').Activate()
                else:
                    sm.GetService('audio').Deactivate()
            elif config == 'suppressTurret':
                sm.StartService('audio').SetTurretSuppression(checkbox.checked)
            elif config == 'damageMessages':
                idx = checkbox.parent.children.index(checkbox) + 1
                state = [uiconst.UI_HIDDEN, uiconst.UI_NORMAL][settings.user.ui.Get('damageMessages', 1)]
                for i in range(4):
                    checkbox.parent.children[idx + i].state = state

            elif config == 'invertCameraZoom':
                setting = gfxsettings.GetSettingFromSettingKey(config)
                gfxsettings.Set(setting, checkbox.checked, pending=False)
                sm.ScatterEvent('OnCameraZoomModifierChanged')
            elif gfxsettings.GetSettingFromSettingKey(config) is not None:
                setting = gfxsettings.GetSettingFromSettingKey(config)
                gfxsettings.Set(setting, checkbox.checked)
            elif config == 'enableTextExpansion':
                self.setEnableTextExpansion = checkbox.checked
                if not checkbox.checked:
                    self.setTextExpansionAmount = 0.0
                self.RefreshLanguage(False)
            elif config == 'showMessageID':
                self.setShowMessageID = checkbox.checked
                if checkbox.checked:
                    self.setSimulateTooltip = False
                self.RefreshLanguage(False)
            elif config == 'enableBoundaryMarkers':
                self.setEnableBoundaryMarkers = checkbox.checked
                if checkbox.checked:
                    self.setSimulateTooltip = False
                self.RefreshLanguage(False)
            elif config == 'showHardcodedStrings':
                self.setShowHardcodedStrings = checkbox.checked
                if checkbox.checked:
                    self.setSimulateTooltip = False
                self.RefreshLanguage(False)
            elif config == 'simulateTooltip':
                self.setSimulateTooltip = checkbox.checked
                if checkbox.checked:
                    self.SetPseudolocalizationSettingsByPreset(0)
                    self.setShowMessageID = False
                    self.setEnableBoundaryMarkers = False
                    self.setShowHardcodedStrings = False
                self.RefreshLanguage(False)
            elif config == 'soundLevel_advancedSettings':
                settings.user.audio.Set('soundLevel_advancedSettings', checkbox.checked)
                if checkbox.checked:
                    sm.GetService('audio').EnableAdvancedSettings()
                else:
                    sm.GetService('audio').DisableAdvancedSettings()
                self.__RebuildAudioPanel()
            elif config == 'overrideWithOldJukebox':
                sm.StartService('audio').SetOldJukeboxOverride(checkbox.checked)
            elif config == 'useCombatMusic':
                sm.StartService('audio').SetCombatMusicUsage(checkbox.checked)

    def GetConfigName(self, suppression):
        configTranslation = {'AgtDelayMission': GetByLabel('UI/SystemMenu/ResetSettings/ResetSuppressMessageSettings/DelayMissionOfferDecision'),
         'AgtMissionOfferWarning': GetByLabel('UI/SystemMenu/ResetSettings/ResetSuppressMessageSettings/AgentMissionOfferWarning'),
         'AgtMissionAcceptBigCargo': GetByLabel('UI/SystemMenu/ResetSettings/ResetSuppressMessageSettings/AgentMissionAcceptsBigCargo'),
         'AgtDeclineMission': GetByLabel('UI/SystemMenu/ResetSettings/ResetSuppressMessageSettings/AgentMissionDeclineWarning'),
         'AgtDeclineOnlyMission': GetByLabel('UI/SystemMenu/ResetSettings/ResetSuppressMessageSettings/AgentDeclineOnlyMissionWarning'),
         'AgtDeclineImportantMission': GetByLabel('UI/SystemMenu/ResetSettings/ResetSuppressMessageSettings/AgentDeclineImportantMissionWarning'),
         'AgtDeclineMissionSequence': GetByLabel('UI/SystemMenu/ResetSettings/ResetSuppressMessageSettings/AgentDeclineMissionSequenceWarning'),
         'AgtQuitMission': GetByLabel('UI/SystemMenu/ResetSettings/ResetSuppressMessageSettings/AgentQuitMissionWarning'),
         'AgtQuitImportantMission': GetByLabel('UI/SystemMenu/ResetSettings/ResetSuppressMessageSettings/AgentQuitImportantMissionWarning'),
         'AgtQuitMissionSequence': GetByLabel('UI/SystemMenu/ResetSettings/ResetSuppressMessageSettings/AgentQuitMissionSequenceWarning'),
         'AgtShare': GetByLabel('UI/SystemMenu/ResetSettings/ResetSuppressMessageSettings/AgentShare'),
         'AgtNotShare': GetByLabel('UI/SystemMenu/ResetSettings/ResetSuppressMessageSettings/AgentNotSharing'),
         'AskPartialCargoLoad': GetByLabel('UI/SystemMenu/ResetSettings/ResetSuppressMessageSettings/PartialCargoLoad'),
         'AskUndockInEnemySystem': GetByLabel('UI/SystemMenu/ResetSettings/ResetSuppressMessageSettings/UndockInEnemySystem'),
         'AidWithEnemiesEmpire2': GetByLabel('UI/SystemMenu/ResetSettings/ResetSuppressMessageSettings/AidEnemiesInEmpireSpaceWarning'),
         'AidOutlawEmpire2': GetByLabel('UI/SystemMenu/ResetSettings/ResetSuppressMessageSettings/AidOutlawInEmpireSpaceWarning'),
         'AidGlobalCriminalEmpire2': GetByLabel('UI/SystemMenu/ResetSettings/ResetSuppressMessageSettings/AidCriminalInEmpireSpaceWarning'),
         'AttackInnocentEmpire2': GetByLabel('UI/SystemMenu/ResetSettings/ResetSuppressMessageSettings/AttackInnocentPlayerInEmpireSpaceConfirmation'),
         'AttackInnocentEmpireAbort1': GetByLabel('UI/SystemMenu/ResetSettings/ResetSuppressMessageSettings/AttackInnocentPlayerInEmpireSpaceConfirmation'),
         'AttackGoodNPC2': GetByLabel('UI/SystemMenu/ResetSettings/ResetSuppressMessageSettings/AttackGoodPlayerConfirmation'),
         'AttackGoodNPCAbort1': GetByLabel('UI/SystemMenu/ResetSettings/ResetSuppressMessageSettings/AttackGoodPlayerConfirmation'),
         'AttackAreaEmpire3': GetByLabel('UI/SystemMenu/ResetSettings/ResetSuppressMessageSettings/AreaOfEffectModuleInEmpireSpaceConfirmation'),
         'AttackAreaEmpireAbort1': GetByLabel('UI/SystemMenu/ResetSettings/ResetSuppressMessageSettings/AreaOfEffectModuleInEmpireSpaceConfirmation'),
         'AttackNonEmpire2': GetByLabel('UI/SystemMenu/ResetSettings/ResetSuppressMessageSettings/AttackPlayerOwnedStuffConfirmation'),
         'AttackNonEmpireAbort1': GetByLabel('UI/SystemMenu/ResetSettings/ResetSuppressMessageSettings/AttackPlayerOwnedStuffConfirmation'),
         'ConfirmOneWayItemMove': GetByLabel('UI/SystemMenu/ResetSettings/ResetSuppressMessageSettings/OneWayItemMoveConfirmation'),
         'ConfirmJumpToUnsafeSS': GetByLabel('UI/SystemMenu/ResetSettings/ResetSuppressMessageSettings/JumpToUnsafeSolarSystemConfirmation'),
         'ConfirmJettison': GetByLabel('UI/SystemMenu/ResetSettings/ResetSuppressMessageSettings/JettisonItemsConfirmation'),
         'AskQuitGame': GetByLabel('UI/SystemMenu/ResetSettings/ResetSuppressMessageSettings/QuitGameConfirmation'),
         'facAcceptEjectMaterialLoss': GetByLabel('UI/SystemMenu/ResetSettings/ResetSuppressMessageSettings/EjectBluePrintFromFactoryConformation'),
         'WarnDeleteFromAddressbook': GetByLabel('UI/SystemMenu/ResetSettings/ResetSuppressMessageSettings/DeleteFromAddressBookWarning'),
         'ConfirmDeleteFolder': GetByLabel('UI/SystemMenu/ResetSettings/ResetSuppressMessageSettings/DeleteFoldersConfirmation'),
         'AskCancelContinuation': GetByLabel('UI/SystemMenu/ResetSettings/ResetSuppressMessageSettings/ModifyCharacterConfirmation'),
         'ConfirmClearText': GetByLabel('UI/SystemMenu/ResetSettings/ResetSuppressMessageSettings/ClearTextConfirmation'),
         'ConfirmAbandonDrone': GetByLabel('UI/SystemMenu/ResetSettings/ResetSuppressMessageSettings/AbandonDroneConfirmation'),
         'QueueSaveChangesOnClose': GetByLabel('UI/SystemMenu/ResetSettings/ResetSuppressMessageSettings/TrainingQueueChanges'),
         'PI_Info': GetByLabel('UI/SystemMenu/ResetSettings/ResetSuppressMessageSettings/PlanetaryInteractionInfo'),
         'InvasionWarningUndock': GetByLabel('UI/SystemMenu/ResetSettings/ResetSuppressMessageSettings/InvasionWarningUndockConfirmation'),
         'CloseWindowStackPrompt': GetByLabel('UI/SystemMenu/ResetSettings/ResetSuppressMessageSettings/CloseWindowStackPrompt'),
         'ShipNameChangeOnAssemble': GetByLabel('UI/Ship/NameChange/ResetSuppressSetting')}
        if configTranslation.has_key(suppression[9:]):
            txt = configTranslation[suppression[9:]]
        else:
            txt = cfg.GetRawMessageTitle(suppression[9:])
            if not txt:
                txt = suppression[9:]
            log.LogWarn('Missing system menu config translation', suppression[9:])
        return txt

    def ConfigBtnClick(self, suppress, *args):
        try:
            settings.user.suppress.Delete(suppress)
            self.isResetSettingsInited = 0
            self.LoadResetSettings(1)
        except:
            log.LogException()
            sys.exc_clear()

    def ResetBtnClick(self, reset, *args):
        if reset == 'windows':
            self.isUserInterfaceInited = False
        uicore.cmd.Reset(reset)

    @ThrottlePerSecond()
    def ReloadHUD(self, *args):
        if eveCfg.InShipInSpace() or IsControllingStructure():
            sm.GetService('viewState').UpdateOverlays((uicore.layer.shipui,))
            message = QuickMessage(className='Message', parent=uicore.layer.modal, name='ShipHudReloaded')
            message.ShowMsg(GetByLabel('UI/SystemMenu/ShipHudReloaded'))

    def QuitBtnClick(self, *args):
        uicore.cmd.GetCommandAndExecute('CmdQuitGame')

    def CloseMenu(self, *args):
        self.CheckColorBlindModeChanged()
        if self.gammaSlider and self.gammaSlider.IsOpen():
            self.gammaSlider.Cancel()
            return
        try:
            if getattr(self, 'closing', False):
                return
            self.closing = 1
            if self.layerCont:
                self.layerCont.state = uiconst.UI_DISABLED
            if not getattr(self, 'inited', False):
                blue.pyos.synchro.Yield()
                uicore.layer.systemmenu.CloseView()
                if self and not self.destroyed:
                    self.closing = 0
                return
            if self.layerCont:
                self.layerCont.state = uiconst.UI_HIDDEN
        finally:
            uicore.layer.systemmenu.CloseView()

    def ApplyLanguageSettings(self, *args):
        importantNamesChanged = False
        bs = localization.settings.bilingualSettings
        if getattr(self, 'setImpNameSetting', None) is not None:
            bs.SetValue('localizationImportantNames', self.setImpNameSetting)
            importantNamesChanged = True
        if getattr(self, 'setLanguageTooltip', None) is not None:
            bs.SetValue('languageTooltip', self.setLanguageTooltip)
            importantNamesChanged = True
        if getattr(self, 'setLocalizationHighlightImportant', None) is not None:
            bs.SetValue('localizationHighlightImportant', self.setLocalizationHighlightImportant)
            importantNamesChanged = True
        if importantNamesChanged:
            bs.UpdateAndSaveSettings()
        languageWasChanged = False
        chosenLang = getattr(self, 'setlanguageID', None)
        if chosenLang:
            chosenLang = langutils.any_to_comfy_language(chosenLang)
            if chosenLang != self.init_language:
                languageWasChanged = True
        doReboot = False
        doLanguageSwap = False
        if languageWasChanged:
            ret = eve.Message('ChangeLanguageReboot', {}, uiconst.YESNO)
            if ret == uiconst.ID_YES:
                doLanguageSwap = True
                doReboot = True
            else:
                setattr(self, 'setlanguageID', None)
                self.RefreshLanguage(allUI=False)
                languageWasChanged = False
                return
            if doReboot and self.isElevatedUser:
                ret = eve.Message('CustomWarning', {'warning': 'You have elevated roles and can swap language live (in development). Some UI elements like chat channels might not be updated live. Still want to restart?',
                 'header': 'Still want to restart?'}, uiconst.YESNO)
                if ret == uiconst.ID_NO:
                    doReboot = False
        if doLanguageSwap:
            sm.GetService('gameui').SetLanguage(chosenLang, doReload=True)
            if doReboot:
                appUtils.Reboot('language change')
            else:
                localization.ClearImportantNameSetting()
                self.RefreshLanguage()
        elif importantNamesChanged:
            localization.ClearImportantNameSetting()
            self.RefreshLanguage()

    def ApplyQALanguageSettings(self, *args):

        def _setSetting(settingKey, controlID, defaultValue = False):
            localization.settings.qaSettings.SetValue(settingKey, getattr(self, controlID, defaultValue))

        _setSetting('showMessageID', 'setShowMessageID')
        _setSetting('enableBoundaryMarkers', 'setEnableBoundaryMarkers')
        _setSetting('showHardcodedStrings', 'setShowHardcodedStrings')
        _setSetting('simulateTooltip', 'setSimulateTooltip')
        _setSetting('characterReplacementMethod', 'setCharacterReplacementMethod', localization.settings.qaSettings.NO_REPLACEMENT)
        if not getattr(self, 'setEnableTextExpansion', False):
            localization.settings.qaSettings.SetValue('textExpansionAmount', 0)
        self.chosenPseudolocPreset = -1
        localization.settings.qaSettings.UpdateAndSaveSettings()
        localization.ClearImportantNameSetting()
        self.RefreshLanguage()

    def GetMouseButtonOptions(self):
        actionbtnOps = [(GetByLabel('UI/Common/Input/Mouse/LeftMouseButton'), uiconst.MOUSELEFT),
         (GetByLabel('UI/Common/Input/Mouse/MiddleMouseButton'), uiconst.MOUSEMIDDLE),
         (GetByLabel('UI/Common/Input/Mouse/RightMouseButton'), uiconst.MOUSERIGHT),
         (GetByLabel('UI/Common/Input/Mouse/ExtraMouseButton1'), uiconst.MOUSEXBUTTON1),
         (GetByLabel('UI/Common/Input/Mouse/ExtraMouseButton2'), uiconst.MOUSEXBUTTON2)]
        return actionbtnOps

    def GetSnapOptions(self):
        snapOps = [(GetByLabel('UI/SystemMenu/GeneralSettings/Windows/DontSnap'), 0),
         (formatters.FormatNumeric(3), 3),
         (formatters.FormatNumeric(6), 6),
         (formatters.FormatNumeric(12), 12),
         (formatters.FormatNumeric(24), 24)]
        return snapOps

    def GetFontSizeOptions(self):
        if is_new_font_size_options_enabled():
            return ((GetByLabel('UI/SystemMenu/GeneralSettings/FontSizeExtraSmall'), FontSizeOption.EXTRA_SMALL),
             (GetByLabel('UI/SystemMenu/GeneralSettings/FontSizeSmall'), FontSizeOption.SMALL),
             (GetByLabel('UI/SystemMenu/GeneralSettings/FontSizeMedium'), FontSizeOption.MEDIUM),
             (GetByLabel('UI/SystemMenu/GeneralSettings/FontSizeLarge'), FontSizeOption.LARGE),
             (GetByLabel('UI/SystemMenu/GeneralSettings/FontSizeExtraLarge'), FontSizeOption.EXTRA_LARGE))
        else:
            return ((GetByLabel('UI/SystemMenu/GeneralSettings/FontSizeSmall'), FontSizeOption.SMALL), (GetByLabel('UI/SystemMenu/GeneralSettings/FontSizeMedium'), FontSizeOption.MEDIUM), (GetByLabel('UI/SystemMenu/GeneralSettings/FontSizeLarge'), FontSizeOption.LARGE))

    def GetTooltipSection(self):
        return [('header', GetByLabel('UI/SystemMenu/GeneralSettings/TooltipsHeader')), ('slider',
          (TOOLTIP_SETTINGS_GENERIC, ('user', 'ui'), TOOLTIP_DELAY_GENERIC),
          'UI/SystemMenu/GeneralSettings/Tooltips/GeneralTooltipsDelay',
          (TOOLTIP_DELAY_MIN, TOOLTIP_DELAY_MAX),
          120,
          None,
          GetByLabel('UI/SystemMenu/GeneralSettings/Tooltips/NoTooltipsDelay'),
          GetByLabel('UI/SystemMenu/GeneralSettings/Tooltips/LongTooltipsDelay'))]

    def ConstructSpaceMouseSettings(self, parent):
        SystemMenuHeader(parent=parent, text=GetByLabel('UI/SystemMenu/DisplayAndGraphics/CameraSettings/SpaceMouse/Header'))
        SystemMenuSlider(parent=parent, config=('spaceMouseSpeed', ('user', 'ui'), gfxsettings.GetDefault(gfxsettings.UI_CAMERA_SPACEMOUSE_SPEED_COEFFICIENT)), label='UI/SystemMenu/DisplayAndGraphics/CameraSettings/SpaceMouse/Speed', minValue=0.0, maxValue=1.0, minLabel=GetByLabel('UI/SystemMenu/DisplayAndGraphics/CameraSettings/SpaceMouse/SpeedMin'), maxLabel=GetByLabel('UI/SystemMenu/DisplayAndGraphics/CameraSettings/SpaceMouse/SpeedMax'), hint=GetByLabel('UI/SystemMenu/DisplayAndGraphics/CameraSettings/SpaceMouse/SpeedTooltip'), increments=[0.5], snapToIncrements=False, callback=self.OnSpaceMouseSpeedSliderValue)
        SystemMenuSlider(parent=parent, config=('spaceMouseAcceleration', ('user', 'ui'), gfxsettings.GetDefault(gfxsettings.UI_CAMERA_SPACEMOUSE_ACCELERATION_COEFFICIENT)), label='UI/SystemMenu/DisplayAndGraphics/CameraSettings/SpaceMouse/Acceleration', minValue=0.0, maxValue=1.0, minLabel=GetByLabel('UI/SystemMenu/DisplayAndGraphics/CameraSettings/SpaceMouse/AccelerationMin'), maxLabel=GetByLabel('UI/SystemMenu/DisplayAndGraphics/CameraSettings/SpaceMouse/AccelerationMax'), hint=GetByLabel('UI/SystemMenu/DisplayAndGraphics/CameraSettings/SpaceMouse/AccelerationTooltip'), increments=[0.5], snapToIncrements=False, callback=self.OnSpaceMouseAccelerationSliderValue)

    def OnSpaceMouseSpeedSliderValue(self, slider):
        gfxsettings.Set(gfxsettings.UI_CAMERA_SPACEMOUSE_SPEED_COEFFICIENT, slider.GetValue(), pending=False)
        sm.ScatterEvent('OnSpaceMouseSpeedCoefficientChanged')

    def OnSpaceMouseAccelerationSliderValue(self, slider):
        gfxsettings.Set(gfxsettings.UI_CAMERA_SPACEMOUSE_ACCELERATION_COEFFICIENT, slider.GetValue(), pending=False)
        sm.ScatterEvent('OnSpaceMouseAccelerationCoefficientChanged')

    def _ShouldShowNotificationOptions(self):
        return not sm.GetService('notificationUIService').AreNotificationsAlwaysEnabled()

    def _ShouldShowNeocomNotificationOptions(self):
        return sm.IsServiceRunning('neocom') and sm.GetService('neocom').IsAvailable()

    def ConstructNotificationSection(self, column):
        shouldShowNotificationOptions = self._ShouldShowNotificationOptions()
        shouldShowNeocomOptions = self._ShouldShowNeocomNotificationOptions()
        if not shouldShowNotificationOptions and not shouldShowNeocomOptions:
            return
        SystemMenuHeader(text=GetByLabel('UI/SystemMenu/GeneralSettings/Notifications/Header'), parent=column)
        if shouldShowNotificationOptions:
            Checkbox(text=GetByLabel('UI/SystemMenu/GeneralSettings/Notifications/NotificationsEnabled'), parent=column, checked=NotificationSettingHandler().GetNotificationWidgetEnabled(), callback=self.ToggleNotificationsEnabled)
        if shouldShowNeocomOptions:
            Checkbox(text=GetByLabel('UI/SystemMenu/GeneralSettings/Notifications/InventoryBadgingEnabled'), parent=column, checked=self.IsInventoryBadgingEnabled(), callback=self.ToggleInventoryBadgingEnabled)

    def ToggleNotificationsEnabled(self, *args):
        NotificationSettingHandler().ToggleNotificationWidgetEnabled()

    def IsInventoryBadgingEnabled(self):
        return IsInventoryBadgingEnabled()

    def ToggleInventoryBadgingEnabled(self, *args):
        ToggleInventoryBadgingEnabledInClient()

    def CheckColorBlindModeChanged(self):
        if self.colorBlindModeChanged:
            colorblind.on_colorblind_mode_changed()
            self.colorBlindModeChanged = False

    def _ConstructWindowMarginCombo(self, column):
        options = [ (WindowMarginModeOption.get_name(margin_mode_option), margin_mode_option, WindowMarginModeOption.get_hint(margin_mode_option)) for margin_mode_option in sorted(WindowMarginModeOption.iter(), key=WindowMarginModeOption.get_sort_key) ]

        def set_window_margin_mode(combo, text, value):
            window_margin_mode.setting.set(value)

        carbonui.TextBody(parent=column, align=uiconst.TOTOP, text=GetByLabel('UI/SystemMenu/GeneralSettings/Windows/WindowMarginModeTitle'), padTop=4)
        Combo(name='window_margin_mode', parent=column, align=uiconst.TOTOP, options=options, select=window_margin_mode.setting.get(), callback=set_window_margin_mode, hint=GetByLabel('UI/SystemMenu/GeneralSettings/Windows/WindowMarginModeHint'))

    def AppendColorBlindnessConfiguration(self, column):
        cont = ContainerAutoSize(parent=column, align=uiconst.TOTOP, padding=(0, 6, 0, 6))
        SystemMenuHeader(text=GetByLabel('UI/SystemMenu/GeneralSettings/ColorBlindMode'), parent=cont)
        options = [(GetByLabel('UI/SystemMenu/GeneralSettings/ColorBlindModeOff'), colorblind.MODE_OFF),
         (GetByLabel('UI/SystemMenu/GeneralSettings/ColorBlindModeDeuteranopia'), colorblind.MODE_DEUTERANOPIA),
         (GetByLabel('UI/SystemMenu/GeneralSettings/ColorBlindModeTritonopia'), colorblind.MODE_TRITONOPIA),
         (GetByLabel('UI/SystemMenu/GeneralSettings/ColorBlindModeCustom'), colorblind.MODE_CUSTOM)]
        self.colorBlindModeCombo = Combo(parent=cont, options=options, name='colorBlindModeSetting', select=colorblind.GetMode(), callback=self.OnColorblindCombo, align=uiconst.TOTOP, padTop=2, hint=GetByLabel('UI/SystemMenu/GeneralSettings/ColorBlindComboHint'))
        self.colorBlindCont = ContainerAutoSize(parent=cont, align=uiconst.TOTOP)
        self.colorBlindHuePicker = ColorBlindHuePicker(parent=self.colorBlindCont, align=uiconst.TOTOP, padTop=4, onHueClicked=self.OnColorBlindHueClicked)
        self.colorBlindHuePalette = ColorBlindHuePalette(parent=self.colorBlindCont, align=uiconst.TOTOP, height=20, padTop=10)
        Label(name='betaLabel,', parent=self.colorBlindCont, text=GetByLabel('UI/SystemMenu/GeneralSettings/ColorBlindBetaText'), state=uiconst.UI_NORMAL, align=uiconst.TOTOP, padding=(4, 4, 4, 0))
        self.CheckShowColorBlindOptions()

    def OnColorBlindHueClicked(self, hue):
        if colorblind.GetMode() != colorblind.MODE_CUSTOM:
            currHues = self.colorBlindHuePicker.GetActiveHues()
            colorblind.SetCustomHues(currHues)
        colorblind.ToggleCustomHue(hue)
        mode = colorblind.MODE_CUSTOM
        self.colorBlindModeCombo.SetValue(mode)
        self.SetColorBlindMode(mode)

    def OnColorblindCombo(self, combo, text, value):
        self.SetColorBlindMode(value)

    def SetColorBlindMode(self, value):
        colorblind.SetMode(value)
        self.colorBlindModeChanged = True
        self.CheckShowColorBlindOptions()
        self.colorBlindHuePicker.UpdateHues()
        self.colorBlindHuePalette.Reconstruct()

    def CheckShowColorBlindOptions(self):
        self.colorBlindCont.display = colorblind.GetMode() != colorblind.MODE_OFF

    def AppendColorThemeSelection(self, column):
        colorTheme = ColorThemeContainer(parent=column, align=uiconst.TOTOP, padTop=8, ui_color_service=sm.GetService('uiColor'), height=400)
        colorTheme.on_omega_button_clicked.connect(self.CloseView)

    def ConstructAndAppendOptionalClientUpdate(self, column):
        optionalUpgradeData = [('header', GetByLabel('UI/SystemMenu/GeneralSettings/ClientUpdate/Header'))]
        if len(optionalUpgradeData) > 1:
            self.ParseData(entries=optionalUpgradeData, parent=column, validateEntries=False)

    def ConstructColumn1MenuData(self):
        menufontsizeOps = self.GetFontSizeOptions()
        menusData = [('combo',
          ('clientFontSize', ('public', 'ui'), get_default_font_size_setting(session.languageID)),
          GetByLabel('UI/SystemMenu/GeneralSettings/General/ClientFontSize'),
          menufontsizeOps,
          LABEL_WIDTH), ('element', Checkbox(align=uiconst.TOTOP, text=GetByLabel('UI/SystemMenu/GeneralSettings/TextShadowOption'), setting=font_shadow_enabled_setting))]
        if session.userid:
            menusData += self.GetTooltipSection()
        menusData += [('header', GetByLabel('UI/SystemMenu/GeneralSettings/Windows/Header')), ('checkbox', ('stackwndsonshift', ('user', 'ui'), 0), GetByLabel('UI/SystemMenu/GeneralSettings/Windows/OnlyStackWindowsIfShiftIsPressed')), ('checkbox', ('useexistinginfownd', ('user', 'ui'), 1), GetByLabel('UI/SystemMenu/GeneralSettings/Windows/TryUseExistingInfoWin'))]
        return menusData

    def ConstructDuelMenuData(self):
        menusData = []
        if session.charid:
            menusData += [('header', GetByLabel('UI/Crimewatch/Duel/EscMenuSectionHeader')), ('checkbox', (appConst.autoRejectDuelSettingsKey, 'server_setting', 0), GetByLabel('UI/Crimewatch/Duel/AutoRejectDuelInvites'))]
        return menusData

    def ConstructBoardingCinematicsMenuData(self):
        menusData = []
        if session.charid:
            menusData += [('header', GetByLabel('UI/ShipProgression/EscMenuBoardingCinematicHeader')), ('checkbox', ('show_boarding_cinematic', ('user', 'ui'), 1), GetByLabel('UI/ShipProgression/ShowBoardingCinematic'))]
        return menusData

    def ConstructMapSection(self, parent):
        if not session.userid:
            return
        SystemMenuHeader(text=GetByLabel('UI/SystemMenu/GeneralSettings/Map/Header'), parent=parent)
        Checkbox(text=GetByLabel('UI/SystemMenu/GeneralSettings/Map/ClassicMapToggle'), parent=parent, align=uiconst.TOTOP, setting=classic_map_enabled_setting)

    def ConstructCrashesSection(self, parent):
        column = parent
        SystemMenuHeader(text=GetByLabel('UI/SystemMenu/GeneralSettings/Crashes/Header'), parent=column)
        Checkbox(text=GetByLabel('UI/SystemMenu/GeneralSettings/Crashes/UploadCrashDumpsToCCPEnabled'), parent=column, checked=blue.IsCrashReportingEnabled(), callback=self.EnableDisableCrashReporting)

    def ConstructInflightMenuData(self):
        SystemMenuHeader(parent=self.gameplayPanel, text=GetByLabel('UI/SystemMenu/GeneralSettings/Inflight/Header'), padTop=0)
        inflightData = [('combo',
          ('autoTargetBack', ('user', 'ui'), 0),
          GetByLabel('UI/SystemMenu/GeneralSettings/Inflight/AutoTargetBack'),
          self._GetAutoTargetBackOptions(),
          LABEL_WIDTH), ('combo',
          ('actionmenuBtn', ('user', 'ui'), 0),
          GetByLabel('UI/SystemMenu/GeneralSettings/Inflight/ExpandActionMenu'),
          self.GetMouseButtonOptions(),
          LABEL_WIDTH), ('slider',
          ('actionMenuExpandTime', ('user', 'ui'), RADIAL_MENU_EXPAND_DELAY_DEFAULT),
          'UI/SystemMenu/GeneralSettings/Inflight/RadialMenuDelay',
          (RADIAL_MENU_EXPAND_DELAY_MIN, RADIAL_MENU_EXPAND_DELAY_MAX),
          120,
          75,
          GetByLabel('UI/SystemMenu/GeneralSettings/Inflight/NoBracketListDelay'),
          GetByLabel('UI/SystemMenu/GeneralSettings/Inflight/LongBracketListDelay'))]
        if session.userid:
            inflightData += [('slider',
              (TOOLTIP_SETTINGS_BRACKET, ('user', 'ui'), TOOLTIP_DELAY_BRACKET),
              'UI/SystemMenu/GeneralSettings/Inflight/BracketListDelay',
              (TOOLTIP_DELAY_MIN, TOOLTIP_DELAY_MAX),
              120,
              None,
              GetByLabel('UI/SystemMenu/GeneralSettings/Inflight/NoRadialMenuDelay'),
              GetByLabel('UI/SystemMenu/GeneralSettings/Inflight/LongRadialMenuDelay')), ('checkbox', ('bracketmenu_docked', ('user', 'ui'), False), GetByLabel('UI/SystemMenu/GeneralSettings/Inflight/CompactBracketListWhenSnapped')), ('checkbox', ('bracketmenu_floating', ('user', 'ui'), True), GetByLabel('UI/SystemMenu/GeneralSettings/Inflight/CompactBracketListWhenNotSnapped'))]
        if session.charid:
            inflightData += [('checkbox', (DISABLE_EMERGENCY_WARP, 'server_setting', 0), GetByLabel('UI/SystemMenu/GeneralSettings/Inflight/DisableEmergencyWarp'))]
        return inflightData

    def _GetAutoTargetBackOptions(self):
        atOps = []
        for i in range(13):
            if i == 0:
                atOps.append((GetByLabel('UI/SystemMenu/GeneralSettings/Inflight/ZeroTargets', targetCount=i), i))
            else:
                atOps.append((GetByLabel('UI/SystemMenu/GeneralSettings/Inflight/Targets', targetCount=i), i))

        return atOps

    def EnableDisableCrashReporting(self, checkbox):
        try:
            blue.EnableCrashReporting(checkbox.checked)
        except RuntimeError:
            pass
        finally:
            prefs.SetValue('breakpadUpload', 1 if checkbox.checked else 0)
