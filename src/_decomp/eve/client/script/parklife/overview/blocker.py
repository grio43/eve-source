#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\parklife\overview\blocker.py
from eve.client.script.parklife.overview.window import reset_overview_window
from logging import getLogger
logger = getLogger(__name__)
SETTINGS_GROUP_IN_USE = 'overview'
SETTINGS_GROUP_BACKUP = 'overview_overridden'

class OverviewBlocker(object):
    __notifyevents__ = ['OnSessionReset']

    def __init__(self, initialize_function, reset_function, set_read_only_function, default_settings):
        self._is_blocked = False
        self._initialize_function = initialize_function
        self._reset_function = reset_function
        self._set_read_only_function = set_read_only_function
        self._default_settings = default_settings
        if self._is_overridden():
            self._restore_overview_settings()
        sm.RegisterNotify(self)

    def block(self):
        if self._is_blocked:
            return
        self._block()

    def unblock(self):
        if not self._is_blocked:
            return
        self._unblock()

    def _clear(self):
        if self._is_overridden():
            self._unblock()

    @reset_overview_window
    def _block(self):
        self._log_debug('Started blocking')
        self._is_blocked = True
        self._backup_overview_settings()
        self._delete_overview_settings()
        self._reset_function()
        self._make_overview_read_only()
        self._log_debug('Completed blocking')

    @reset_overview_window
    def _unblock(self):
        self._log_debug('Started unblocking')
        self._is_blocked = False
        self._restore_overview_settings()
        self._initialize_function()
        self._make_overview_editable()
        self._log_debug('Completed unblocking')

    def _backup_overview_settings(self):
        user_settings = settings.user
        user_settings.DuplicateGroup(SETTINGS_GROUP_IN_USE, SETTINGS_GROUP_BACKUP)
        user_settings.WriteToDiskImmediate()

    def _delete_overview_settings(self):
        user_settings = settings.user
        user_settings.ClearGroup(SETTINGS_GROUP_IN_USE)
        user_settings.WriteToDiskImmediate()

    def _restore_overview_settings(self):
        user_settings = settings.user
        user_settings.RemoveGroup(SETTINGS_GROUP_IN_USE)
        user_settings.WriteToDiskImmediate()
        user_settings.RenameGroup(SETTINGS_GROUP_BACKUP, SETTINGS_GROUP_IN_USE)
        user_settings.WriteToDiskImmediate()

    def _make_overview_read_only(self):
        self._set_read_only_function(True)

    def _make_overview_editable(self):
        self._set_read_only_function(False)

    def _is_overridden(self):
        user_settings = settings.user
        return user_settings.HasGroup(SETTINGS_GROUP_BACKUP)

    def OnSessionReset(self):
        self._clear()

    def _log_debug(self, text):
        settings_text = self._default_settings.get_settings_report()
        msg = 'Overview Blocker: {text}. \nIs Overriden: {is_overriden} \n{settings_text}'.format(text=text, is_overriden=self._is_overridden(), settings_text=settings_text)
        logger.debug(msg)
