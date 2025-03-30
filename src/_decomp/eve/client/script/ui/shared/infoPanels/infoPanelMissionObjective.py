#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\infoPanels\infoPanelMissionObjective.py
from eve.client.script.ui.control.statefulButtonController import StatefulButtonController

class MissionObjective(StatefulButtonController, object):
    __notifyevents__ = StatefulButtonController.__notifyevents__
    MISSION_HINT_LABEL_PATH = None
    ICON_TEXTURE_PATH = None
    COMPLETED_ICON_TEXTURE_PATH = 'res:/UI/Texture/classes/MissionTracker/tracker_check.png'
    ICON_COLOR = None
    COMPLETED_ICON_COLOR = None
    ICON_OPACITY = 0.0
    ACTIVE_ICON_OPACITY = 0.6
    COMPLETED_ICON_OPACITY = 0.6
    HEADER_BACKGROUND_COLOR = (0, 0, 0)
    COMPLETED_HEADER_BACKGROUND_COLOR = None
    HEADER_BACKGROUND_OPACITY = 0.0
    COMPLETED_HEADER_BACKGROUND_OPACITY = 0.6
    OBJECTIVE_ICON_SIZE = 48

    def __init__(self, iconItemID = None, iconTypeID = None, missionHint = None, activeIcon = None, completedIcon = None, isActive = False):
        self.activeIcon = activeIcon or self.ICON_TEXTURE_PATH
        self.completedIcon = completedIcon or self.COMPLETED_ICON_TEXTURE_PATH
        self.activeIconOpacity = self.ACTIVE_ICON_OPACITY if activeIcon else self.ICON_OPACITY
        self.iconItemID = iconItemID
        self.iconTypeID = iconTypeID
        self.missionHint = missionHint or ''
        self.isActive = isActive
        StatefulButtonController.__init__(self)

    def IsActive(self):
        return self.isActive

    def SetActive(self):
        self.isActive = True

    def SetInactive(self):
        self.isActive = False

    def GetHeaderBackgroundData(self):
        if self.IsActive():
            return (self.HEADER_BACKGROUND_OPACITY, self.HEADER_BACKGROUND_COLOR)
        return (self.COMPLETED_HEADER_BACKGROUND_OPACITY, self.COMPLETED_HEADER_BACKGROUND_COLOR)

    def GetHeaderIconData(self):
        if self.IsActive():
            return (self.activeIcon, self.activeIconOpacity, self.ICON_COLOR)
        return (self.completedIcon, self.COMPLETED_ICON_OPACITY, self.COMPLETED_ICON_COLOR)

    def GetHeaderText(self):
        raise NotImplementedError('Must implement GetHeaderText in derived class.')

    def GetLocationButtonNamePostfix(self):
        return self.GetHeaderText()

    def GetLocationButtonName(self):
        postFix = self.GetLocationButtonNamePostfix()
        return 'missionObjective_button_location_%s' % postFix

    def HasIcon(self):
        return False

    def GetObjectiveIconSize(self):
        return self.OBJECTIVE_ICON_SIZE

    def BuildIcon(self, name, parent, align, state, opacity, width, height):
        raise NotImplementedError('Must implement BuildIcon in derived class.')

    def HasText(self):
        return bool(self.missionHint)

    def GetText(self):
        return self.missionHint

    def GetLocation(self):
        raise NotImplementedError('Must implement GetLocation in derived class.')

    def HasGuidance(self):
        return False

    def StartGuidance(self):
        raise NotImplementedError('Must implement StartGuidance in derived class.')

    def GetClassName(self):
        return type(self).__name__

    def GetButtonFunction(self):
        return super(MissionObjective, self).GetButtonFunction()
