#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\services\eveSettingsSvc.py
import log
from carbonui.services.settingsSvc import SettingsSvc
from carbonui.window.settings import ValidateSettings

class EveSettingsSvc(SettingsSvc):
    __guid__ = 'svc.eveSettings'
    __replaceservice__ = 'settings'

    def LoadSettings(self, userid = None, charid = None):
        if not userid:
            userid = session.userid
        if not charid:
            charid = session.charid
        SettingsSvc.LoadSettings(self, userid, charid)
        settings.user.CreateGroup('audio')
        settings.user.CreateGroup('overview')
        settings.user.CreateGroup('defaultoverview')
        settings.user.CreateGroup('notifications')
        settings.char.CreateGroup('generic')
        settings.char.CreateGroup('autorepeat')
        settings.char.CreateGroup('autoreload')
        settings.char.CreateGroup('inbox')
        settings.char.CreateGroup('notepad')
        settings.char.CreateGroup('notifications')
        try:
            self.FixListgroupSettings()
        except Exception:
            settings.char.ui.Set('listgroups', {})
            log.LogError('Something happened when fixing listgroups settings and they had to be deleted')

        ValidateSettings(userid, charid)
        return settings

    def FixListgroupSettings(self):
        if not session.charid:
            return
        if settings.char.ui.Get('listgroupSettingsUpdated', 0):
            return
        for key, value in settings.char.ui.Get('listgroups', {}).iteritems():
            for key2, value2 in value.iteritems():
                items = value2.pop('items', None)
                if items is not None:
                    value2['groupItems'] = items

        settings.char.ui.Set('listgroupSettingsUpdated', 1)
