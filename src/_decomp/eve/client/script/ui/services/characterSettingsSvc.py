#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\services\characterSettingsSvc.py
from carbon.common.script.sys.service import Service

class CharacterSettingsSvc(Service):
    __guid__ = 'svc.characterSettings'
    __update_on_reload__ = 1
    __notifyevents__ = ['OnSessionReset']

    def __init__(self):
        super(CharacterSettingsSvc, self).__init__()
        self._charMgr = None
        self._settings = None

    @property
    def charMgr(self):
        if self._charMgr is None:
            self._charMgr = session.ConnectToRemoteService('charMgr')
        return self._charMgr

    def OnSessionReset(self):
        self._charMgr = None
        self._settings = None

    def _GetSettings(self):
        if self._settings is None:
            self._settings = self.charMgr.GetCharacterSettings()
        return self._settings

    def Get(self, settingKey):
        try:
            return self._GetSettings()[settingKey]
        except KeyError:
            return None

    def Save(self, settingKey, value):
        if value is None or value == '':
            self.Delete(settingKey)
        else:
            if len(value) > 102400:
                raise RuntimeError("We don't want to send too large character settings to the server", settingKey, len(value))
            self.charMgr.SaveCharacterSetting(settingKey, value)
            self._GetSettings()[settingKey] = value

    def Delete(self, settingKey):
        settings = self._GetSettings()
        if settingKey in settings:
            self.charMgr.DeleteCharacterSetting(settingKey)
            del settings[settingKey]
