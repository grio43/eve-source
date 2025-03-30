#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\overviewSettings\miscPanel.py
from carbonui.primitives.container import Container
from carbonui import uiconst
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.control.button import Button
from carbonui.control.checkbox import Checkbox
from eve.client.script.ui.control import eveLabel
from carbonui.button.group import ButtonGroup
from eve.client.script.ui.inflight.overviewSettings.panelUtils import ResetCbOnReloadingOverviewProfile
from localization import GetByLabel
import overviewPresets.overviewSettingsConst as oConst

class MiscPanel(Container):
    default_name = 'miscPanel'
    __notifyevents__ = ['OnReloadingOverviewProfile']

    def ApplyAttributes(self, attributes):
        super(MiscPanel, self).ApplyAttributes(attributes)
        self.overviewPresetSvc = sm.GetService('overviewPresetSvc')
        self.settingCheckboxes = []
        self.ConstructCheckboxes()
        sm.RegisterNotify(self)

    def ConstructCheckboxes(self):
        overviewBroadcastsToTop = Checkbox(text=GetByLabel('UI/Overview/MoveBroadcastersToTop'), parent=self, settingsKey=oConst.SETTING_BROADCAST_TO_TOP, checked=self.overviewPresetSvc.GetSettingValueBroadcastToTop(), settingsPath=('user', 'overview'), align=uiconst.TOTOP)
        self.settingCheckboxes.append(overviewBroadcastsToTop)
        self.targetRangeSubCheckboxes = []
        eveLabel.EveCaptionSmall(text=GetByLabel('UI/Overview/BracketAndTargetsHeader'), parent=self, align=uiconst.TOTOP, state=uiconst.UI_DISABLED, padTop=16)
        targetCrosshairCb = Checkbox(text=GetByLabel('UI/SystemMenu/GeneralSettings/Inflight/ShowTargettingCrosshair'), parent=self, settingsKey=oConst.SETTING_TARGET_CROSSHAIR, checked=self.overviewPresetSvc.GetSettingValueOrDefaultFromName(oConst.SETTING_TARGET_CROSSHAIR, True), settingsPath=('user', 'overview'), align=uiconst.TOTOP, callback=self.MiscCheckboxChange)
        self.settingCheckboxes.append(targetCrosshairCb)
        dmgIndicatorCb = Checkbox(text=GetByLabel('UI/Overview/DisplayDamageIndications'), parent=self, settingsKey=oConst.SETTING_BIGGEST_DMG_DEALER, checked=self.overviewPresetSvc.GetSettingValueOrDefaultFromName(oConst.SETTING_BIGGEST_DMG_DEALER, True), settingsPath=('user', 'overview'), align=uiconst.TOTOP, callback=self.MiscCheckboxChange)
        self.settingCheckboxes.append(dmgIndicatorCb)
        moduleHairlineCb = Checkbox(text=GetByLabel('UI/Overview/DisplayModuleLinks'), parent=self, settingsKey=oConst.SETTING_MODULE_HAIRLINES, checked=self.overviewPresetSvc.GetSettingValueOrDefaultFromName(oConst.SETTING_MODULE_HAIRLINES, True), settingsPath=('user', 'overview'), align=uiconst.TOTOP)
        self.settingCheckboxes.append(moduleHairlineCb)
        targetRangeCb = Checkbox(text=GetByLabel('UI/Overview/DisplayRangeBrackets'), parent=self, settingsKey=oConst.SETTING_TARGET_RANGE, checked=self.overviewPresetSvc.GetSettingValueOrDefaultFromName(oConst.SETTING_TARGET_RANGE, True), settingsPath=('user', 'overview'), align=uiconst.TOTOP, callback=self.MiscCheckboxChange)
        self.settingCheckboxes.append(targetRangeCb)
        configName = 'showCategoryInTargetRange_%s' % const.categoryShip
        targetRangeShipsCb = Checkbox(text=GetByLabel('UI/Overview/Ships'), parent=self, settingsKey=configName, checked=self.overviewPresetSvc.GetSettingValueOrDefaultFromName(configName, True), settingsPath=('user', 'overview'), align=uiconst.TOTOP, callback=self.MiscCheckboxChange, padLeft=8)
        self.settingCheckboxes.append(targetRangeShipsCb)
        self.targetRangeSubCheckboxes.append(targetRangeShipsCb)
        configName = 'showCategoryInTargetRange_%s' % const.categoryEntity
        targetRangeNPCsCb = Checkbox(text=GetByLabel('UI/Overview/NPCs'), parent=self, settingsKey=configName, checked=self.overviewPresetSvc.GetSettingValueOrDefaultFromName(configName, True), settingsPath=('user', 'overview'), align=uiconst.TOTOP, callback=self.MiscCheckboxChange, padLeft=8)
        self.settingCheckboxes.append(targetRangeNPCsCb)
        self.targetRangeSubCheckboxes.append(targetRangeNPCsCb)
        configName = 'showCategoryInTargetRange_%s' % const.categoryDrone
        targetRangeDronesCb = Checkbox(text=GetByLabel('UI/Overview/Drones'), parent=self, settingsKey=configName, checked=self.overviewPresetSvc.GetSettingValueOrDefaultFromName(configName, True), settingsPath=('user', 'overview'), align=uiconst.TOTOP, callback=self.MiscCheckboxChange, padLeft=8)
        self.settingCheckboxes.append(targetRangeDronesCb)
        self.targetRangeSubCheckboxes.append(targetRangeDronesCb)
        self.ChangeStateOfSubCheckboxes(targetRangeCb)
        buttonGroup = ButtonGroup(parent=self, align=uiconst.TOBOTTOM)
        buttonGroup.AddButton(GetByLabel('UI/Overview/ImportOverviewSettings'), sm.GetService('tactical').ImportOverviewSettings)
        buttonGroup.AddButton(GetByLabel('UI/Overview/ExportOverviewSettings'), sm.GetService('tactical').ExportOverviewSettings)
        buttonGroup.AddButton(GetByLabel('UI/Overview/ResetOverview'), self.ResetAllOverviewSettings)

    def MiscCheckboxChange(self, cb, *args):
        configName = cb.GetSettingsKey()
        if configName == oConst.SETTING_TARGET_RANGE:
            self.ChangeStateOfSubCheckboxes(cb)
        elif configName == oConst.SETTING_BIGGEST_DMG_DEALER:
            if cb.checked:
                sm.GetService('bracket').EnableShowingDamageDealers()
            else:
                sm.GetService('bracket').DisableShowingDamageDealers()
        elif configName in (oConst.SETTING_TARGET_CROSSHAIR,):
            sm.GetService('bracket').Reload()
        elif cb in self.targetRangeSubCheckboxes:
            sm.GetService('bracket').ShowInTargetRange()

    def ChangeStateOfSubCheckboxes(self, cb):
        if cb.checked:
            sm.GetService('bracket').EnableInTargetRange()
            for subCb in self.targetRangeSubCheckboxes:
                subCb.Enable()
                subCb.opacity = 1.0

        else:
            sm.GetService('bracket').DisableInTargetRange()
            for subCb in self.targetRangeSubCheckboxes:
                subCb.Disable()
                subCb.opacity = 0.3

    def ResetAllOverviewSettings(self, *args):
        self.overviewPresetSvc.ResetOverviewSettingsToDefaultWithPrompt()
        ReloadOverviewSettingsWindow()

    def OnReloadingOverviewProfile(self):
        ResetCbOnReloadingOverviewProfile(self.overviewPresetSvc, self.settingCheckboxes)


def ReloadOverviewSettingsWindow():
    from eve.client.script.ui.inflight.overviewSettings.overviewSettingsWnd import OverviewSettingsWnd
    OverviewSettingsWnd.CloseIfOpen()
    OverviewSettingsWnd.Open()
