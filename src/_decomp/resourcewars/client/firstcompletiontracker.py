#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\resourcewars\client\firstcompletiontracker.py
from carbonui.uicore import uicore
from eve.common.script.mgt.appLogConst import eventStandingResourceWarSiteCompleted
from localization import GetByLabel
from resourcewars.common.const import RW_LP_CORPORATIONS
SITE_COMPLETED_SETTING = 'rw_site_completed'

class FirstCompletionTracker(object):
    __notifyevents__ = ['OnWindowOpened']

    def __init__(self, uiHighlightingService, standingSvc):
        self.uiHighlightingService = uiHighlightingService
        self.standingSvc = standingSvc
        self.isPlayingForFirstWin = False
        self.shouldHighlightLPStore = False
        self.highlightActive = False
        sm.RegisterNotify(self)

    def on_rw_dungeon_entered(self):
        if not self._have_completed_rw_site():
            self.isPlayingForFirstWin = True

    def _have_completed_rw_site(self):
        completedSettingValue = settings.char.ui.Get(SITE_COMPLETED_SETTING, None)
        if completedSettingValue is not None:
            return completedSettingValue
        for corpID in RW_LP_CORPORATIONS:
            for standingEvent in self.standingSvc.GetStandingTransactions(corpID, session.charid):
                if standingEvent.eventTypeID == eventStandingResourceWarSiteCompleted:
                    settings.char.ui.Set(SITE_COMPLETED_SETTING, True)
                    return True

        return False

    def on_rw_dungeon_completed(self, isVictory):
        if self.isPlayingForFirstWin and isVictory:
            self.shouldHighlightLPStore = True

    def _should_highlight_lp_store(self):
        return bool(self.shouldHighlightLPStore and uicore.cmd.HasServiceAccess('lpstore') and sm.RemoteSvc('RWManager').solarsystem_contains_rw_instances())

    def OnWindowOpened(self, window):
        if window.windowID == 'lobbyWnd':
            if self._should_highlight_lp_store():
                message = GetByLabel('UI/Station/LPStore')
                self.uiHighlightingService.highlight_ui_element_by_name('lpstore', message, fadeout_seconds=30, title=None, audio_setting=True, default_direction=None, offset=None)
                window.BlinkButton('lpstore')
                self.shouldHighlightLPStore = False
                self.highlightActive = True
        elif self.highlightActive and window.windowID == 'lpstore':
            self.uiHighlightingService.remove_highlight_from_ui_element_by_name('lpstore')
