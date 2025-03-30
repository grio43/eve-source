#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\careerPortal\uiSettings.py
SELECTED_PAGE = 'careerPortal_selectedPage'
SELECTED_CAREER = 'careerPortal_selectedCareerPathID'
SELECTED_GROUP = 'careerPortal_selectedGroup'
TRACKED_GOALS = 'careerPortal_trackedGoals'

def GetSettingsSection():
    return settings.char.ui


def GetTrackedGoalsFromSettings(defaultValue = None):
    defaultValue = set() if defaultValue is None else defaultValue
    return GetSettingsSection().Get(TRACKED_GOALS, defaultValue)


def StoreTrackedGoalsInSettings(groupID):
    return GetSettingsSection().Set(TRACKED_GOALS, groupID)
