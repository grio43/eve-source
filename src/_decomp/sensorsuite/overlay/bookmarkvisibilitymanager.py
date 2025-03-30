#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sensorsuite\overlay\bookmarkvisibilitymanager.py
import logging
import yaml
from carbon.common.script.util.timerstuff import AutoTimer
logger = logging.getLogger(__name__)
FOLDER_VISIBILITY_SETTING = 'sensor_overlay_bookmark_folder_visibility'
FOLDER_VISIBILITY_SETTING_NEW = 'sensor_overlay_acl_bookmark_folder_visibility'

class BookmarkFolderVisibilityManager:

    def __init__(self):
        self.bookmarkFolderKeysHiddenFromSensorOverlay = None

    def LoadFolderVisibility(self):
        logger.debug('Loading folder visibility settings')
        settingsYaml = sm.GetService('characterSettings').Get(FOLDER_VISIBILITY_SETTING_NEW) or ''
        tempSettings = yaml.safe_load(settingsYaml) or []
        try:
            self.bookmarkFolderKeysHiddenFromSensorOverlay = set(((f, s) for f, s in tempSettings))
        except StandardError:
            logger.exception('Failed to load folder visibility settings')
            self.bookmarkFolderKeysHiddenFromSensorOverlay = set()

    def PersistVisibleFolders(self):
        logger.debug('Persisting folder visibility settings')
        settingsYaml = yaml.safe_dump(list(self.bookmarkFolderKeysHiddenFromSensorOverlay))
        sm.GetService('characterSettings').Save(FOLDER_VISIBILITY_SETTING_NEW, settingsYaml)
        self.persistVisibleFoldersTimer = None

    def IsFolderVisible(self, folderKey):
        if self.bookmarkFolderKeysHiddenFromSensorOverlay is None:
            self.LoadFolderVisibility()
        return folderKey not in self.bookmarkFolderKeysHiddenFromSensorOverlay

    def SetFolderVisibility(self, folderKey, isVisible):
        logger.debug('Setting bookmark folder %s visibility to %s', folderKey, isVisible)
        if isVisible:
            self.bookmarkFolderKeysHiddenFromSensorOverlay.discard(folderKey)
        else:
            self.bookmarkFolderKeysHiddenFromSensorOverlay.add(folderKey)
        self.persistVisibleFoldersTimer = AutoTimer(5000, self.PersistVisibleFolders)


_bookmarkVisibilityManager = None

def GetBookmarkFolderVisibilityManager():
    global _bookmarkVisibilityManager
    if _bookmarkVisibilityManager is None:
        _bookmarkVisibilityManager = BookmarkFolderVisibilityManager()
    return _bookmarkVisibilityManager


def ReleaseBookmarkFolderVisibilityManager():
    global _bookmarkVisibilityManager
    if _bookmarkVisibilityManager is not None:
        del _bookmarkVisibilityManager
        _bookmarkVisibilityManager = None
