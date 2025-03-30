#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\overviewSettings\panelUtils.py


def OnContentDragEnter(scroll, dragObj, entries, *args):
    ShowPositionIndicator(scroll)


def ShowPositionIndicator(scroll):
    lastDropEntry = GetLastDropEntry(scroll)
    if lastDropEntry:
        lastDropEntry.ShowIndicator()


def GetLastDropEntry(scroll):
    nodes = scroll.GetNodes()
    if nodes:
        return getattr(nodes[-1], 'panel', None)


def OnContentDragExit(scroll, *args):
    HidePositionIndicator(scroll)


def HidePositionIndicator(scroll):
    lastDropEntry = GetLastDropEntry(scroll)
    if lastDropEntry:
        lastDropEntry.HideIndicator()


def ResetCbOnReloadingOverviewProfile(overviewPresetSvc, settingCheckboxes):
    defaultSettings = overviewPresetSvc.GetSettingsNamesAndDefaults()
    for eachCb in settingCheckboxes:
        configName = eachCb.GetSettingsKey()
        defaultValue = defaultSettings.get(configName, True)
        newValue = overviewPresetSvc.GetSettingValueOrDefaultFromName(configName, defaultValue)
        eachCb.SetChecked(newValue, report=0)
