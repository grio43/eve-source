#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\overview\slimItemDisplayChecker.py
from eve.common.lib import appConst as const
from overviewPresets.overviewSettingsConst import SETTING_OVERVIEW_PRESET_NAME

class SlimItemDisplayChecker(object):

    def __init__(self):
        self.stateSvc = sm.GetService('stateSvc')
        self.tacticalSvc = sm.GetService('tactical')
        self.presetSvc = sm.GetService('overviewPresetSvc')
        self.structureProximityTracker = sm.GetService('structureProximityTracker')
        self.presetName = None

    def UpdateState(self, tabID):
        if tabID is not None:
            tabSettingsByID = self.presetSvc.GetSettingsByTabID()
            self.presetName = tabSettingsByID[tabID][SETTING_OVERVIEW_PRESET_NAME]
        else:
            self.presetName = None
        self.filterGroups = self.presetSvc.GetValidGroups(presetName=self.presetName)
        self.filteredStates = self.tacticalSvc.GetFilteredStatesFunctionNames(presetName=self.presetName)
        self.alwaysShownStates = self.tacticalSvc.GetAlwaysShownStatesFunctionNames(presetName=self.presetName)

    def ShouldDisplayItem(self, slimItem):
        if not slimItem:
            return False
        if slimItem.itemID == session.shipid:
            return False
        overriddenState = self.presetSvc.GetOverrideState(slimItem)
        if overriddenState is not None:
            return overriddenState
        if slimItem.typeID in const.OVERVIEW_IGNORE_TYPES:
            return False
        if slimItem.groupID not in self.filterGroups:
            return False
        if self.stateSvc.CheckIfFilterItem(slimItem) and self.tacticalSvc.CheckFiltered(slimItem, self.filteredStates, self.alwaysShownStates):
            return False
        if slimItem.categoryID == const.categoryStructure and not self.structureProximityTracker.IsStructureVisible(slimItem.itemID):
            return False
        return True
