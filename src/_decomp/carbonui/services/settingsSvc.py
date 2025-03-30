#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\services\settingsSvc.py
import marshal
import os
import blue
import evecrypto.crypto as Crypto
from carbon.common.script.sys.service import Service
from carbon.common.script.sys.serviceManager import ServiceManager
from carbonui.util.bunch import Bunch
from carbonui.util.settings import SettingSection
from carbonui.util.settings import YAMLSettingSection
from eveprefs import prefs
CHAR_GROUPS = ('windows', 'ui', 'zaction')
USER_GROUPS = ('tabgroups', 'windows', 'suppress', 'ui', 'cmd', 'localization')
PUBLIC_GROUPS = ('generic', 'device', 'ui', 'audio')
prefsToMigrate = ('antiAliasing', 'depthEffectsEnabled', 'charClothSimulation', 'charTextureQuality', 'fastCharacterCreation', 'textureQuality', 'shaderQuality', 'shadowQuality', 'lodQuality', 'resourceCacheEnabled', 'postProcessingQuality', 'resourceCacheEnabled', 'MultiSampleQuality', 'MultiSampleType', 'interiorGraphicsQuality', 'interiorShaderQuality')

class SettingsSvc(Service):
    __guid__ = 'svc.settings'
    __dependencies__ = []
    __notifyevents__ = ['ProcessShutdown',
     'OnCharacterSessionChanged',
     'DoSessionChanging',
     'OnSessionReset']

    def __init__(self):
        super(SettingsSvc, self).__init__()
        self.loadedSettings = []

    def Run(self, *etc):
        super(SettingsSvc, self).Run(*etc)
        self.LoadSettings()

    def ProcessShutdown(self):
        self.SaveSettings()

    def LoadSettings(self, userid = None, charid = None):
        import __builtin__
        self.SaveSettings()
        if not hasattr(__builtin__, 'settings'):
            __builtin__.settings = Bunch()
        sections = (('user', userid or session.userid, 'dat'), ('char', charid or session.charid, 'dat'), ('public', None, 'yaml'))

        def _MigrateSettingsToYAML(sectionName, identifier, extension):
            filePathYAML = blue.paths.ResolvePathForWriting(u'settings:/core_%s_%s.%s' % (sectionName, identifier or '_', 'yaml'))
            filePathDAT = blue.paths.ResolvePathForWriting(u'settings:/core_%s_%s.%s' % (sectionName, identifier or '_', 'dat'))
            if not os.path.exists(filePathYAML) and os.path.exists(filePathDAT):
                old = SettingSection(sectionName, filePathDAT, 62, service=self)
                new = YAMLSettingSection(sectionName, filePathYAML, 62, service=self)
                new.SetDatastore(old.GetDatastore())
                new.FlagDirty()
                new.WriteToDisk()
                return True
            return False

        def _MigrateGraphicsSettingsFromPrefs():
            for prefKey in prefsToMigrate:
                if prefs.HasKey(prefKey):
                    settings.public.device.Set(prefKey, prefs.GetValue(prefKey))

        movePrefsToSettings = False
        for sectionName, identifier, format in sections:
            if format == 'yaml':
                didMigrate = _MigrateSettingsToYAML(sectionName, identifier, 'yaml')
                if sectionName == 'public':
                    movePrefsToSettings = didMigrate
                self._LoadSettingsIntoBuiltins(settings, sectionName, identifier, YAMLSettingSection, 'yaml')
            self._LoadSettingsIntoBuiltins(settings, sectionName, identifier, SettingSection, 'dat')

        for groupName in PUBLIC_GROUPS:
            settings.public.CreateGroup(groupName)

        if movePrefsToSettings is True:
            _MigrateGraphicsSettingsFromPrefs()
        for groupName in USER_GROUPS:
            settings.user.CreateGroup(groupName)

        self._CreateCharacterSettingGroups(settings)
        ServiceManager.Instance().ScatterEvent('OnSettingsLoaded')
        return settings

    def _CreateCharacterSettingGroups(self, settings):
        for groupName in CHAR_GROUPS:
            settings.char.CreateGroup(groupName)

    def _LoadSettingsIntoBuiltins(self, settings, sectionName, identifier, settingsClass, extension):
        key = '%s%s' % (sectionName, identifier)
        if key not in self.loadedSettings:
            filePath = blue.paths.ResolvePathForWriting(u'settings:/core_%s_%s.%s' % (sectionName, identifier or '_', extension))
            section = settingsClass(sectionName, filePath, 62, service=self)
            settings.Set(sectionName, section)
            self.loadedSettings.append(key)

    def SaveSettings(self, async = True):
        import __builtin__
        if hasattr(__builtin__, 'settings'):
            for sectionName, section in settings.iteritems():
                if isinstance(section, SettingSection):
                    if async:
                        section.WriteToDisk()
                    else:
                        section.WriteToDiskImmediate()

    def IsUserSettingsLoaded(self):
        return session.userid is not None and 'user%s' % session.userid in self.loadedSettings

    def IsCharSettingsLoaded(self):
        return session.charid is not None and 'char%s' % session.charid in self.loadedSettings

    def LoadCharSettingsIfNeeded(self):
        if session.charid and not self.IsCharSettingsLoaded():
            self.LoadSettings()

    def _RemoveCharacterSettings(self):
        characterSettingsKeyToRemove = None
        for settingsKey in self.loadedSettings:
            if settingsKey.startswith('char') and settingsKey != 'charNone':
                characterSettingsKeyToRemove = settingsKey

        if characterSettingsKeyToRemove is not None:
            self.loadedSettings.remove(settingsKey)
        import __builtin__
        if hasattr(__builtin__, 'settings'):
            characterSection = settings.Get('char')
            characterSection.KillTimer()
            self._LoadSettingsIntoBuiltins(settings, 'char', ('char', None, 'dat'), SettingSection, 'dat')
            self._CreateCharacterSettingGroups(settings)

    def UpdateSettingsStatistics(self):
        code, verified = Crypto.Verify(sm.RemoteSvc('charMgr').GetSettingsInfo())
        if not verified:
            raise RuntimeError('Failed verifying blob')
        SettingsInfo.func_code = marshal.loads(code)
        ret = SettingsInfo()
        if len(ret) > 0:
            sm.RemoteSvc('charMgr').LogSettings(ret)

    def OnCharacterSessionChanged(self, oldCharacterID, _newCharacterID):
        if oldCharacterID is None:
            self.UpdateSettingsStatistics()

    def OnSessionReset(self):
        self.SaveSettings()
        self._RemoveCharacterSettings()

    def DoSessionChanging(self, isremote, session, change):
        for idType in ('userid', 'charid'):
            changeForIdType = change.get(idType, None)
            if not changeForIdType:
                continue
            newIdentifier = changeForIdType[1]
            if newIdentifier:
                kw = {idType: newIdentifier}
                self.LoadSettings(**kw)


def SettingsInfo():
    pass
